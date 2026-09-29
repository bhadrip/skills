#!/usr/bin/env python3
"""Synthetic-only Blender integration smoke test; all assets stay in OS temp.

  python3 tests/blender_smoke.py --blender /path/to/blender

No project photos, portrait geometry, network, or model dependencies are used.
Tested with Blender 5.2 and a working background Workbench renderer. Artifacts are
removed by TemporaryDirectory unless --keep is supplied for manual inspection.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender")
    parser.add_argument("--keep", action="store_true", help="Keep synthetic artifacts in the OS temporary directory")
    args = parser.parse_args()
    script = Path(__file__).resolve().parents[1] / "skills/portrait-to-print/scripts/blender_review.py"
    blender = shutil.which(args.blender)
    if not blender:
        raise SystemExit(f"Blender executable not found: {args.blender}")
    temporary = tempfile.TemporaryDirectory(prefix="portrait-plugin-smoke-") if not args.keep else None
    root = Path(temporary.name if temporary else tempfile.mkdtemp(prefix="portrait-plugin-smoke-"))
    commands = []

    def run(arguments, expected_success=True, log_name="run"):
        command = [blender, "--background", "--factory-startup", "--python-exit-code", "7", *arguments]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=240)
        (root / f"{log_name}.log").write_text(result.stdout)
        commands.append({"label": log_name, "exit_code": result.returncode})
        if (result.returncode == 0) != expected_success:
            raise AssertionError(f"{log_name} unexpected exit {result.returncode}:\n{result.stdout[-7000:]}")
        return result

    try:
        source = root / "synthetic_block.blend"
        # Deliberately nonuniform scale, off-center translation, wrong source
        # material and a unit-display scale. The resulting dimensions are known.
        fixture = (
            "import bpy; "
            "bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False); "
            "bpy.ops.mesh.primitive_cube_add(size=2, location=(13, 17, 47)); "
            "o=bpy.context.object; o.name='SyntheticBlock'; o.scale=(20, 15, 40); "
            "bpy.context.scene.unit_settings.system='METRIC'; "
            "bpy.context.scene.unit_settings.scale_length=0.001; "
            f"bpy.ops.wm.save_as_mainfile(filepath={str(source)!r})"
        )
        run(["--python-expr", fixture], log_name="fixture")
        original_hash = digest(source)
        review = root / "review"
        review_args = ["--source", str(source), "--units", "mm", "--front-axis=+X",
                       "--out", str(review), "--resolution", "128"]
        run(["--python", str(script), "--", *review_args], log_name="review")
        manifest = json.loads((review / "manifest.json").read_text())
        assert manifest["status"] == "review_ready_not_approved"
        assert all(abs(a - b) < 0.001 for a, b in zip(manifest["geometry"]["dimensions_mm"], (30, 40, 80))), manifest["geometry"]
        assert manifest["geometry"]["minimum_z_mm"] == 0.0
        assert set(manifest["cameras"]) == {"front", "three_quarter", "three_quarter_other", "profile", "back", "top"}
        assert len({camera["ortho_scale_mm"] for camera in manifest["cameras"].values()}) == 1
        for name in manifest["cameras"]:
            assert (review / f"{name}.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert not list(review.glob("*.stl")) and not list(review.glob("*.glb"))
        assert digest(source) == original_hash
        stable_manifest = digest(review / "manifest.json")
        # Fixed-camera comparisons must not hide an offset/size change by fitting
        # the new candidate's bounds. Reuse both placement and camera transforms.
        variant_source = root / "synthetic_offset_variant.blend"
        variant_fixture = (
            "import bpy; "
            f"bpy.ops.wm.open_mainfile(filepath={str(source)!r}, use_scripts=False); "
            "o=bpy.data.objects['SyntheticBlock']; o.location=(18,20,54); o.scale=(22,15,40); "
            f"bpy.ops.wm.save_as_mainfile(filepath={str(variant_source)!r})"
        )
        run(["--python-expr", variant_fixture], log_name="variant_fixture")
        fixed_review = root / "fixed_review"
        run(["--python", str(script), "--", "--source", str(variant_source), "--units", "mm",
             "--front-axis=+X", "--reference-review", str(review), "--out", str(fixed_review)],
            log_name="fixed_reference_review")
        fixed = json.loads((fixed_review / "manifest.json").read_text())
        assert fixed["source_to_review_matrix"] == manifest["source_to_review_matrix"]
        for name, camera in manifest["cameras"].items():
            fields = set(camera) - {"image_sha256"}
            assert {key: fixed["cameras"][name][key] for key in fields} == {key: camera[key] for key in fields}
        assert fixed["render"] == manifest["render"]
        assert fixed["reference_review"]["manifest_sha256"] == stable_manifest
        assert abs(fixed["geometry"]["minimum_z_mm"] - 7) < 0.001  # deliberately NOT regrounded
        assert all(abs(a - b) < 0.001 for a, b in zip(fixed["geometry"]["dimensions_mm"], (30, 44, 80)))
        center = [(a + b) / 2 for a, b in zip(*fixed["geometry"]["bounds_mm"])]
        assert all(abs(a - b) < 0.001 for a, b in zip(center, (3, -5, 47))), center
        assert digest(review / "manifest.json") == stable_manifest
        for label, units, front in (("units", "m", "+X"), ("front", "mm", "-Y")):
            run(["--python", str(script), "--", "--source", str(variant_source), "--units", units,
                 f"--front-axis={front}", "--reference-review", str(review),
                 "--out", str(root / f"incompatible_{label}")], False, f"refuse_reference_{label}")
        run(["--python", str(script), "--", "--export", "--review", str(fixed_review),
             "--approve-reviewed-geometry", "--out", str(root / "off_ground_export")],
            False, "refuse_off_ground_export")
        run(["--python", str(script), "--", *review_args], False, "refuse_existing")
        assert digest(review / "manifest.json") == stable_manifest
        run(["--python", str(script), "--", "--export", "--review", str(review),
             "--out", str(root / "unapproved")], False, "refuse_unapproved")
        assert not (root / "unapproved").exists()
        exports = root / "exports"
        run(["--python", str(script), "--", "--export", "--review", str(review),
             "--approve-reviewed-geometry", "--out", str(exports)], log_name="export")
        exported = json.loads((exports / "manifest.json").read_text())
        for filename in ("portrait_mm.stl", "portrait_m.glb"):
            stats = exported["exports"][filename]["reimport_geometry_mm"]
            assert all(abs(a - b) < 0.001 for a, b in zip(stats["dimensions_mm"], (30, 40, 80))), stats
            assert stats["minimum_z_mm"] >= -0.001
            assert exported["exports"][filename]["max_bounds_error_mm"] < 0.001
        stl_stats = exported["exports"]["portrait_mm.stl"]["reimport_geometry_mm"]
        assert stl_stats["watertight_edge_manifold"] and stl_stats["components"] == 1
        assert abs(stl_stats["signed_volume_mm3"] - 96000) < 0.01
        assert digest(source) == original_hash
        # A GLB source round trip exercises the import-unit contract too.
        glb_review = root / "glb_review"
        run(["--python", str(script), "--", "--source", str(exports / "portrait_m.glb"),
             "--units", "m", "--front-axis=-Y", "--out", str(glb_review), "--resolution", "128"],
            log_name="glb_source_review")
        glb_stats = json.loads((glb_review / "manifest.json").read_text())["geometry"]
        assert all(abs(a - b) < 0.001 for a, b in zip(glb_stats["dimensions_mm"], (30, 40, 80))), glb_stats
        # Wrong glTF unit declarations must fail instead of producing a 1000x error.
        run(["--python", str(script), "--", "--source", str(exports / "portrait_m.glb"),
             "--units", "mm", "--front-axis=-Y", "--out", str(root / "wrong_units")],
            False, "refuse_wrong_glb_units")
        # Open geometry may be reviewed, but the export gate must reject it.
        open_source = root / "synthetic_open.blend"
        open_fixture = (
            "import bpy; bpy.ops.object.select_all(action='SELECT'); "
            "bpy.ops.object.delete(use_global=False); bpy.ops.mesh.primitive_plane_add(size=10); "
            f"bpy.ops.wm.save_as_mainfile(filepath={str(open_source)!r})"
        )
        run(["--python-expr", open_fixture], log_name="open_fixture")
        open_review = root / "open_review"
        run(["--python", str(script), "--", "--source", str(open_source), "--units", "mm",
             "--front-axis=-Y", "--out", str(open_review), "--resolution", "128"], log_name="open_review")
        open_export = root / "open_export"
        run(["--python", str(script), "--", "--export", "--review", str(open_review),
             "--approve-reviewed-geometry", "--out", str(open_export)], False, "refuse_open_export")
        assert (open_export / "FAILED.json").exists() and not (open_export / "manifest.json").exists()
        # A tampered approved scene cannot be silently exported.
        with (review / "review.blend").open("ab") as stream:
            stream.write(b"synthetic-smoke-test-tamper")
        run(["--python", str(script), "--", "--export", "--review", str(review),
             "--approve-reviewed-geometry", "--out", str(root / "tampered")], False, "refuse_tampered_scene")
        summary = {"status": "passed", "synthetic_only": True, "tests": commands,
                   "verified_stl_mm": [30, 40, 80], "verified_glb_m": [0.03, 0.04, 0.08],
                   "reference_matrix_and_all_six_cameras_exactly_reused": True,
                   "source_unchanged": digest(source) == original_hash}
        (root / "smoke_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
        if args.keep:
            print(f"Synthetic artifacts retained outside plugin: {root}")
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    main()
