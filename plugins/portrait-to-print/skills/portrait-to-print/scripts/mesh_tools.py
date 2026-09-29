#!/usr/bin/env python3
"""Inspect or scale an already oriented STL without repairing its geometry.

Requires numpy, scipy, and trimesh. PyMeshLab is optional and is used only
when --intersections is explicitly requested. STL coordinates are interpreted
as millimeters; +Z is up. This tool does not infer which direction a face looks.

Exit codes: 0 = requested checks passed; 1 = geometry/size validation failed;
2 = usage, dependency, filesystem, or source-preservation error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile

try:
    import numpy as np
    import scipy
    import trimesh
except ImportError as exc:
    print("Install numpy, scipy, and trimesh before running mesh_tools.py", file=sys.stderr)
    raise SystemExit(2) from exc


class MeshToolError(Exception):
    """An operational error, not a failed geometry check."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def positive_number(value: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a finite positive number") from exc
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return result


def require_new_path(path: Path) -> None:
    # is_symlink also rejects dangling links; exists alone does not.
    if path.exists() or path.is_symlink():
        raise MeshToolError(f"Refusing to overwrite existing path: {path}")
    if not path.parent.is_dir():
        raise MeshToolError(f"Output parent directory must already exist: {path.parent}")


def load_stl_exact(path: Path) -> tuple[trimesh.Trimesh, dict]:
    if path.suffix.lower() != ".stl":
        raise MeshToolError("Only STL input is supported; units must already be understood as mm")
    try:
        raw = trimesh.load_mesh(str(path), file_type="stl", process=False)
    except Exception as exc:
        raise MeshToolError(f"Could not parse input as STL: {exc}") from exc
    if not isinstance(raw, trimesh.Trimesh):
        raise MeshToolError("Input did not load as one triangle-mesh container")
    vertices = np.asarray(raw.vertices, dtype=np.float64)
    faces = np.asarray(raw.faces, dtype=np.int64)
    if not len(vertices) or not len(faces):
        raise MeshToolError("Input did not contain any readable STL triangles")
    info = {
        "raw_vertices": len(vertices),
        "raw_triangles": len(faces),
        "indexing": "Only exactly equal coordinate duplicates are indexed together; no tolerance welding, face removal, hole filling, or winding repair",
    }
    # STL is normally an unindexed triangle soup. Build connectivity without
    # process=True, which can silently discard invalid data or weld by tolerance.
    if len(vertices) and np.isfinite(vertices).all():
        unique, inverse = np.unique(vertices, axis=0, return_inverse=True)
        faces = inverse[faces]
        info["exact_duplicate_vertex_records_indexed"] = len(vertices) - len(unique)
        vertices = unique
    else:
        info["exact_duplicate_vertex_records_indexed"] = 0
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False), info


def intersection_check(mesh: trimesh.Trimesh, requested: bool) -> dict:
    result = {
        "requested": requested,
        "status": "not_checked",
        "flagged_faces": None,
        "caveat": "Face flags are not intersection-pair counts. This floating-point checker can miss coplanar/shared-edge overlaps; zero flags are not an exhaustive geometric proof.",
    }
    if not requested:
        return result
    try:
        import pymeshlab
    except ImportError as exc:
        raise MeshToolError("--intersections requires PyMeshLab; install it or omit the option") from exc
    try:
        meshset = pymeshlab.MeshSet()
        meshset.add_mesh(pymeshlab.Mesh(vertex_matrix=np.asarray(mesh.vertices), face_matrix=np.asarray(mesh.faces, dtype=np.int32)))
        meshset.apply_filter("compute_selection_by_self_intersections_per_face")
        count = int(meshset.current_mesh().selected_face_number())
        result.update(status="checked", flagged_faces=count)
    except Exception as exc:
        raise MeshToolError(f"Requested intersection check could not run: {exc}") from exc
    return result


def inspect_mesh(mesh: trimesh.Trimesh, *, expected_height_mm: float | None = None,
                 height_tolerance_mm: float = 0.01, intersections: bool = False) -> dict:
    """Read-only geometry audit. In particular, component splitting never repairs."""
    if expected_height_mm is not None and (not math.isfinite(expected_height_mm) or expected_height_mm <= 0):
        raise MeshToolError("Expected height must be finite and positive")
    if not math.isfinite(height_tolerance_mm) or height_tolerance_mm <= 0:
        raise MeshToolError("Height tolerance must be finite and positive")
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    failures: list[str] = []
    report = {
        "vertices": len(vertices), "triangles": len(faces),
        "coordinates_assumed_mm": True, "up_axis_assumed": "+Z",
        "face_forward_direction": "not inferred or changed",
        "finite_vertices": bool(np.isfinite(vertices).all()),
        "failure_reasons": failures,
        "expected_height_mm": expected_height_mm,
        "height_tolerance_mm": height_tolerance_mm,
        "intersection_check": intersection_check(mesh, False),
        "unperformed_checks": ["visual likeness/orientation approval", "minimum wall and feature thickness", "slicer supports and overhangs", "physical print"],
    }
    if len(vertices) == 0 or len(faces) == 0:
        failures.append("empty_mesh")
    if not report["finite_vertices"]:
        failures.append("nonfinite_vertices")
    if faces.ndim != 2 or faces.shape[1:] != (3,) or (faces.size and (faces.min() < 0 or faces.max() >= len(vertices))):
        failures.append("invalid_triangle_indices")
    if failures:
        if intersections:
            report["intersection_check"].update(requested=True, status="not_run_invalid_geometry")
        report["structural_gate_passed"] = False
        return report

    triangles = vertices[faces]
    with np.errstate(over="ignore", invalid="ignore"):
        cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        areas = np.linalg.norm(cross, axis=1) * 0.5
    if not np.isfinite(areas).all():
        failures.append("nonfinite_derived_triangle_areas")
        if intersections:
            report["intersection_check"].update(requested=True, status="not_run_invalid_geometry")
        report["structural_gate_passed"] = False
        return report
    canonical_faces = np.sort(faces, axis=1)
    duplicate_count = len(faces) - len(np.unique(canonical_faces, axis=0))
    unreferenced_count = len(vertices) - len(np.unique(faces))
    degenerate_count = int(np.count_nonzero(areas <= 1e-12))
    edge_lengths = np.asarray(mesh.edges_unique_length)
    # repair=False is essential: trimesh's split default may fill small holes.
    parts = mesh.split(only_watertight=False, repair=False)
    component_stats = []
    for index, part in enumerate(sorted(parts, key=lambda part: len(part.faces), reverse=True)):
        component_stats.append({
            "index": index, "vertices": len(part.vertices), "triangles": len(part.faces),
            "bounds_mm": part.bounds.tolist(), "area_mm2": float(part.area),
            "signed_volume_mm3": float(part.volume),
            "watertight": bool(part.is_watertight),
            "winding_consistent": bool(part.is_winding_consistent),
        })
    dimensions = mesh.extents
    volume = float(mesh.volume)
    face_normals = np.asarray(mesh.face_normals)
    vertex_normals = np.asarray(mesh.vertex_normals)
    report.update({
        "dimensions_mm": dimensions.tolist(), "bounds_mm": mesh.bounds.tolist(),
        "z_min_mm": float(mesh.bounds[0, 2]), "z_max_mm": float(mesh.bounds[1, 2]),
        "height_mm": float(dimensions[2]), "area_mm2": float(mesh.area),
        "signed_volume_mm3": volume, "component_count": len(parts), "components": component_stats,
        "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "euler_number": int(mesh.euler_number), "unreferenced_vertices": unreferenced_count,
        "duplicate_triangles_ignoring_winding": duplicate_count,
        "degenerate_triangles_area_le_1e_12_mm2": degenerate_count,
        "minimum_triangle_area_mm2": float(areas.min()),
        "zero_length_edges": int(np.count_nonzero(edge_lengths == 0)),
        "edge_length_min_median_max_mm": [float(edge_lengths.min()), float(np.median(edge_lengths)), float(edge_lengths.max())],
        "finite_computed_face_normals": bool(np.isfinite(face_normals).all()),
        "finite_computed_vertex_normals": bool(np.isfinite(vertex_normals).all()),
        "normal_basis": "Computed from triangle winding; stored STL normal vectors are not trusted as topology evidence",
        "repairs_performed": [],
    })
    for condition, reason in [
        (len(parts) != 1, "requires_exactly_one_connected_component"),
        (not mesh.is_watertight, "not_watertight"),
        (not mesh.is_winding_consistent, "inconsistent_winding"),
        (not math.isfinite(volume) or volume <= 0, "nonpositive_or_nonfinite_signed_volume"),
        (degenerate_count > 0, "degenerate_triangles"),
        (duplicate_count > 0, "duplicate_triangles"),
        (unreferenced_count > 0, "unreferenced_vertices"),
        (not report["finite_computed_face_normals"] or not report["finite_computed_vertex_normals"], "nonfinite_computed_normals"),
        (not np.isfinite(dimensions).all() or dimensions[2] <= 0, "invalid_z_height"),
        (expected_height_mm is not None and abs(float(dimensions[2]) - expected_height_mm) > height_tolerance_mm, "unexpected_height"),
    ]:
        if condition:
            failures.append(reason)
    report["intersection_check"] = intersection_check(mesh, intersections)
    if report["intersection_check"]["flagged_faces"]:
        failures.append("self_intersection_flags")
    report["structural_gate_passed"] = not failures
    return report


def write_json_new(path: Path, report: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("check", "prepare"):
        command = commands.add_parser(name)
        command.add_argument("--input", required=True, type=Path, help="Already oriented STL; coordinates interpreted as millimeters")
        command.add_argument("--out", required=True, type=Path, help="New JSON report for check; new STL for prepare")
        command.add_argument("--intersections", action="store_true", help="Require optional PyMeshLab self-intersection face-flag check")
        command.add_argument("--height-tolerance-mm", type=positive_number, default=0.01)
        if name == "check":
            command.add_argument("--expected-height-mm", type=positive_number)
        else:
            command.add_argument("--height-mm", required=True, type=positive_number)
            command.add_argument("--report", type=Path, help="New JSON report path; default is OUT.stl.json")
    return result


def run(args: argparse.Namespace) -> tuple[dict, int]:
    source = args.input.expanduser().resolve(strict=True)
    # Do not resolve away a dangling output symlink before rejecting it.
    output = args.out.expanduser().absolute()
    require_new_path(output)
    output = output.resolve()
    report_path = output if args.command == "check" else (args.report.expanduser().absolute() if args.report else Path(str(output) + ".json"))
    require_new_path(report_path)
    report_path = report_path.resolve()
    if args.command == "prepare" and (output.suffix.lower() != ".stl" or output == report_path):
        raise MeshToolError("Prepare requires a new .stl output and a different JSON report path")
    before = sha256(source)
    mesh, indexing = load_stl_exact(source)
    report = {
        "schema_version": 1, "operation": args.command,
        "source": {"path": str(source), "sha256": before, **indexing},
        "software": {"numpy": np.__version__, "scipy": scipy.__version__, "trimesh": trimesh.__version__},
        "report_path": str(report_path),
        "warning": "A structural pass is not likeness approval or a complete printability certificate. Inputs and runtime reports may be private; this tool does not upload them.",
    }
    source_check = inspect_mesh(mesh, expected_height_mm=getattr(args, "expected_height_mm", None), height_tolerance_mm=args.height_tolerance_mm, intersections=args.intersections)
    report["input_check"] = source_check
    code = 0 if source_check["structural_gate_passed"] else 1
    if args.command == "prepare" and code == 0:
        scale = args.height_mm / source_check["height_mm"]
        prepared = mesh.copy()
        prepared.vertices = np.asarray(mesh.vertices) * scale
        ground_shift = -float(prepared.bounds[0, 2])
        prepared.vertices[:, 2] += ground_shift
        report["transform"] = {"uniform_scale": scale, "z_translation_mm_after_scale": ground_shift, "rotation": "none", "xy_recentering": "none"}
        # Export and inspect a private staged file before publishing anything.
        with tempfile.TemporaryDirectory(prefix="mesh-tools-", dir=output.parent) as staging:
            candidate = Path(staging) / "candidate.stl"
            prepared.export(candidate, file_type="stl")
            reimported, reindexing = load_stl_exact(candidate)
            output_check = inspect_mesh(reimported, expected_height_mm=args.height_mm, height_tolerance_mm=args.height_tolerance_mm, intersections=args.intersections)
            if abs(output_check.get("z_min_mm", math.inf)) > args.height_tolerance_mm:
                output_check["failure_reasons"].append("export_not_grounded")
                output_check["structural_gate_passed"] = False
            report["output_check"] = output_check
            report["output_indexing"] = reindexing
            if not output_check["structural_gate_passed"]:
                code = 1
                report["output_published"] = False
            elif sha256(source) != before:
                raise MeshToolError("Source changed during processing; output was not published")
            else:
                # Exclusive creation also protects against a race after preflight.
                with candidate.open("rb") as reader, output.open("xb") as writer:
                    shutil.copyfileobj(reader, writer)
                if sha256(output) != sha256(candidate):
                    raise MeshToolError("Published file differs from the validated staged export")
                report["output"] = {"path": str(output), "sha256": sha256(output)}
                report["output_published"] = True
                report["reimport_verified"] = True
    elif args.command == "prepare":
        report["output_published"] = False
        report["note"] = "Input failed validation. No repair, scaling, or STL publication was performed."
    report["source_unchanged"] = sha256(source) == before
    if not report["source_unchanged"]:
        raise MeshToolError("Source changed during processing; review concurrent writers")
    report["exit_code"] = code
    write_json_new(report_path, report)
    return report, code


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report, code = run(args)
    except (MeshToolError, OSError, ValueError, RuntimeError, ImportError) as exc:
        print(json.dumps({"error": str(exc), "exit_code": 2}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
