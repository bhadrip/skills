#!/usr/bin/env python3
"""Deterministic, local geometry review and explicitly approved export in Blender.

Run with Blender (tested on 5.2), not ordinary Python:
  blender --background --factory-startup --python blender_review.py -- \
    --source model.stl --units mm --front-axis=-Y --out /private/review-01
For a changed mesh in the same imported coordinate frame, add:
    --reference-review /private/review-01
This reuses placement, all six cameras, resolution and studio light exactly. It
does not recenter, reground or zoom the candidate; out-of-frame edits stay visible
as clipping rather than silently changing the comparison.
After inspecting all six PNGs and the editable scene:
  blender --background --factory-startup --python blender_review.py -- \
    --export --review /private/review-01 --approve-reviewed-geometry \
    --out /private/export-01

Every output directory must be new. Imported coordinates must be Z-up; front-axis
describes the imported model, not the native glTF coordinate system. STL/PLY/OBJ
and BLEND units are explicit. GLB/GLTF import produces meters: use --units m.
The review copies evaluated render-visible meshes and discards textures/rigs.
Without --reference-review, it rotates the supplied front to -Y, centers XY and
grounds Z=0. It does not sculpt or repair.
No network, add-ons, model weights, or personal sample assets are required.
"""

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

import bpy
from mathutils import Matrix, Vector


SCHEMA = "portrait-to-print.blender-review.v1"
VIEWS = {
    "front": (0, -1, 0),
    "three_quarter": (1, -1, 0),
    "three_quarter_other": (-1, -1, 0),
    "profile": (1, 0, 0),
    "back": (0, 1, 0),
    "top": (0, 0, 1),
}
LIMITATIONS = [
    "No likeness, expression, anatomical accuracy, or unseen-surface claim.",
    "No self-intersection, coplanar-overlap, wall-thickness, or support analysis.",
    "Edge-manifold checks do not test vertex-manifold singularities or nested shells.",
    "A closed mesh and correct dimensions do not establish printability.",
    "STL has no unit metadata: exported coordinates must be interpreted as mm.",
    "Materials, animation, rigs, cameras and textures from the source are omitted.",
    "External dependencies of BLEND/GLTF/OBJ are not covered by the source hash.",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def fresh_directory(path):
    path = Path(path).expanduser().absolute()
    if path.exists() or path.is_symlink():
        raise ValueError(f"Refusing existing output: {path}")
    path.mkdir(parents=True, exist_ok=False)
    return path.resolve()


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    # Importers receive an unambiguous unit-scale scene. Source conversion is ours.
    bpy.context.scene.unit_settings.scale_length = 1.0


def import_source(path):
    clear_scene()
    suffix = path.suffix.lower()
    if suffix == ".blend":
        # Never execute embedded startup scripts in an input scene.
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    elif suffix == ".stl":
        bpy.ops.wm.stl_import(filepath=str(path), use_scene_unit=False,
                              forward_axis="Y", up_axis="Z")
    elif suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path), forward_axis="Y", up_axis="Z")
    elif suffix == ".ply":
        bpy.ops.wm.ply_import(filepath=str(path), use_scene_unit=False)
    else:
        raise ValueError("Supported sources: .blend, .stl, .glb, .gltf, .obj, .ply")


def evaluated_snapshot():
    """Return geometry in imported world coordinates, retaining separate parts."""
    vertices, faces, objects = [], [], []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for instance in depsgraph.object_instances:
        obj = instance.object
        if obj.type != "MESH" or obj.hide_render or not instance.show_self:
            continue
        mesh = obj.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
        try:
            offset = len(vertices)
            world = instance.matrix_world.copy()
            vertices.extend(tuple(world @ vertex.co) for vertex in mesh.vertices)
            reverse = world.determinant() < 0
            for polygon in mesh.polygons:
                indices = list(polygon.vertices)
                if reverse:
                    indices.reverse()
                faces.append(tuple(index + offset for index in indices))
            objects.append({"name": obj.name, "vertices": len(mesh.vertices),
                            "polygons": len(mesh.polygons), "instance": instance.is_instance})
        finally:
            obj.to_mesh_clear()
    if not vertices or not faces:
        raise ValueError("No render-visible mesh surface found in the source scene")
    if not all(math.isfinite(value) for vertex in vertices for value in vertex):
        raise ValueError("Source contains nonfinite coordinates")
    return vertices, faces, objects


def make_geometry(vertices, faces):
    clear_scene()
    mesh = bpy.data.meshes.new("ReviewGeometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("ReviewGeometry", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    material = bpy.data.materials.new("NeutralClay")
    material.diffuse_color = (0.62, 0.62, 0.62, 1.0)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.62, 0.62, 0.62, 1.0)
    principled.inputs["Roughness"].default_value = 0.85
    mesh.materials.append(material)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 0.001
    bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
    return obj


def mesh_stats(mesh):
    """Topology/signed-volume checks only; deliberately not an intersection test."""
    points = [vertex.co.copy() for vertex in mesh.vertices]
    if not points:
        raise ValueError("Empty mesh")
    lower = [min(point[i] for point in points) for i in range(3)]
    upper = [max(point[i] for point in points) for i in range(3)]
    parent = array("I", range(len(points)))

    def root(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for edge in mesh.edges:
        a, b = edge.vertices
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[rb] = ra
    edge_uses = array("I", [0]) * len(mesh.edges)
    edge_directions = array("i", [0]) * len(mesh.edges)
    referenced = bytearray(len(points))
    for polygon in mesh.polygons:
        loops = list(polygon.loop_indices)
        for index, loop_index in enumerate(loops):
            loop = mesh.loops[loop_index]
            next_loop = mesh.loops[loops[(index + 1) % len(loops)]]
            referenced[loop.vertex_index] = 1
            edge_uses[loop.edge_index] += 1
            edge_directions[loop.edge_index] += (1 if loop.vertex_index < next_loop.vertex_index else -1)
    mesh.calc_loop_triangles()
    component_volumes = {}
    area, degenerate = 0.0, 0
    for triangle in mesh.loop_triangles:
        indices = triangle.vertices
        a, b, c = (points[i] for i in indices)
        triangle_area = (b - a).cross(c - a).length / 2
        area += triangle_area
        degenerate += triangle_area <= 1e-12
        key = root(indices[0])
        component_volumes[key] = component_volumes.get(key, 0.0) + a.dot(b.cross(c)) / 6
    component_counts = {}
    for vertex in range(len(points)):
        key = root(vertex)
        component_counts[key] = component_counts.get(key, 0) + 1
    return {
        "vertices": len(points), "polygons": len(mesh.polygons),
        "triangles": len(mesh.loop_triangles), "edges": len(mesh.edges),
        "bounds_mm": [lower, upper], "dimensions_mm": [upper[i] - lower[i] for i in range(3)],
        "minimum_z_mm": lower[2], "surface_area_mm2": area,
        "signed_volume_mm3": sum(component_volumes.values()),
        "components": len(component_counts),
        "component_vertices": sorted(component_counts.values(), reverse=True),
        "component_signed_volumes_mm3": sorted(component_volumes.values(), reverse=True),
        "boundary_edges": sum(uses == 1 for uses in edge_uses),
        "nonmanifold_edges": sum(uses != 2 for uses in edge_uses),
        "inconsistent_winding_edges": sum(uses == 2 and direction != 0
                                           for uses, direction in zip(edge_uses, edge_directions)),
        "watertight_edge_manifold": bool(edge_uses) and all(uses == 2 for uses in edge_uses),
        "unreferenced_vertices": referenced.count(0),
        "zero_length_edges": sum((points[a] - points[b]).length <= 1e-12 for a, b in (edge.vertices for edge in mesh.edges)),
        "degenerate_triangles_area_le_1e_minus12_mm2": degenerate,
        "finite_vertices": all(math.isfinite(value) for point in points for value in point),
        "finite_normals": all(math.isfinite(value) for polygon in mesh.polygons for value in polygon.normal),
        "self_intersections": "not tested", "wall_thickness": "not tested",
    }


def load_reference_review(args):
    if not args.reference_review:
        return None, None
    directory = Path(args.reference_review).expanduser().resolve(strict=True)
    path = directory / "manifest.json"
    reference = json.loads(path.read_text())
    if (reference.get("schema") != SCHEMA or reference.get("mode") != "review"
            or reference.get("status") != "review_ready_not_approved"):
        raise ValueError("Reference must be a completed same-schema review, not an export or partial run")
    source = reference["source"]
    if source["imported_units"] != args.units or source["imported_front_axis"] != args.front_axis:
        raise ValueError("Reference review has incompatible imported units/front axis")
    if (source.get("imported_up_axis") != "+Z"
            or reference.get("units", {}).get("mesh_coordinates") != "millimeters"
            or reference["units"].get("up_axis") != "+Z"
            or reference["units"].get("front_axis") != "-Y"):
        raise ValueError("Reference review has incompatible coordinate conventions")
    transform = reference["source_to_review_matrix"]
    if (len(transform) != 4 or any(len(row) != 4 for row in transform)
            or not all(math.isfinite(value) for row in transform for value in row)
            or abs(Matrix(transform).determinant()) < 1e-12):
        raise ValueError("Reference placement matrix is invalid")
    render = reference["render"]
    resolution = render["resolution"]
    if (render.get("engine") != "BLENDER_WORKBENCH" or render.get("camera_projection") != "ORTHO"
            or render.get("textures") is not False or render.get("cavity") is not False
            or len(resolution) != 2 or resolution[0] != resolution[1]
            or not isinstance(resolution[0], int) or not 64 <= resolution[0] <= 8192):
        raise ValueError("Reference review has incompatible render settings")
    if args.resolution is not None and args.resolution != resolution[0]:
        raise ValueError("--resolution must match the reference; omit it to inherit the baseline resolution")
    if set(reference["cameras"]) != set(VIEWS):
        raise ValueError("Reference review must contain all six canonical cameras")
    for name, camera in reference["cameras"].items():
        required = {"location_mm", "rotation_euler_radians", "ortho_scale_mm", "clip_start_mm", "clip_end_mm", "shift_xy"}
        if not required.issubset(camera):
            raise ValueError("Reference lacks complete camera metadata; create a fresh baseline review")
        if len(camera["location_mm"]) != 3 or len(camera["rotation_euler_radians"]) != 3 or len(camera["shift_xy"]) != 2:
            raise ValueError("Reference camera transform is malformed")
        values = [*camera["location_mm"], *camera["rotation_euler_radians"], *camera["shift_xy"],
                  camera["ortho_scale_mm"], camera["clip_start_mm"], camera["clip_end_mm"]]
        if (not all(math.isfinite(value) for value in values) or camera["ortho_scale_mm"] <= 0
                or not 0 < camera["clip_start_mm"] < camera["clip_end_mm"]):
            raise ValueError("Reference camera contains invalid framing values")
        if sha256(directory / f"{name}.png") != camera["image_sha256"]:
            raise ValueError(f"Reference image changed: {name}")
    if sha256(directory / "review.blend") != reference["editable_scene"]["sha256"]:
        raise ValueError("Reference scene changed; create a new baseline review")
    return reference, {"manifest_path": str(path), "manifest_sha256": sha256(path),
                       "reuses": ["source_to_review_matrix", "all_six_camera_transforms_and_framing",
                                  "resolution", "studio_light"],
                       "recenters_or_regrounds_candidate": False}


def setup_review_scene(obj, resolution, reference=None):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    shading = scene.display.shading
    shading.light = "STUDIO"
    studios = [light.name for light in bpy.context.preferences.studio_lights if light.type == "STUDIO"]
    studio = (reference["render"]["studio_light"] if reference else
              ("paint.sl" if "paint.sl" in studios else (studios[0] if studios else None)))
    if studio not in studios:
        raise RuntimeError("Required built-in studio light is unavailable; do not substitute lighting in a comparison")
    shading.studio_light = studio
    shading.color_type = "SINGLE"
    shading.single_color = (0.62, 0.62, 0.62)
    shading.show_shadows = False
    shading.show_cavity = False
    shading.show_specular_highlight = False
    shading.show_object_outline = False
    shading.background_type = "WORLD"
    scene.world = bpy.data.worlds.new("ReviewWorld")
    scene.world.color = (0.055, 0.055, 0.055)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    stats = mesh_stats(obj.data)
    if reference is not None:
        cameras = {}
        for name in VIEWS:
            framing = reference["cameras"][name]
            data = bpy.data.cameras.new(f"Review_{name}")
            data.type = "ORTHO"
            data.ortho_scale = framing["ortho_scale_mm"]
            data.clip_start, data.clip_end = framing["clip_start_mm"], framing["clip_end_mm"]
            data.shift_x, data.shift_y = framing["shift_xy"]
            camera = bpy.data.objects.new(f"Review_{name}", data)
            scene.collection.objects.link(camera)
            camera.location = framing["location_mm"]
            camera.rotation_euler = framing["rotation_euler_radians"]
            cameras[name] = camera
        return cameras, studio, stats
    lower, upper = (Vector(bound) for bound in stats["bounds_mm"])
    center = (lower + upper) / 2
    diagonal = (upper - lower).length
    if diagonal <= 1e-8:
        raise ValueError("Geometry has no useful extent")
    corners = [Vector((x, y, z)) for x in (lower.x, upper.x)
               for y in (lower.y, upper.y) for z in (lower.z, upper.z)]
    # One scale for all six cameras: comparisons do not silently zoom each pose.
    cameras, extent = {}, 0.0
    for name, direction in VIEWS.items():
        data = bpy.data.cameras.new(f"Review_{name}")
        data.type = "ORTHO"
        data.clip_start = max(diagonal / 10000, 0.0001)
        data.clip_end = diagonal * 10
        camera = bpy.data.objects.new(f"Review_{name}", data)
        scene.collection.objects.link(camera)
        camera.location = center + Vector(direction).normalized() * diagonal * 3
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        rotation = camera.rotation_euler.to_matrix().transposed()
        projected = [rotation @ (point - center) for point in corners]
        extent = max(extent, *(max(point[i] for point in projected) - min(point[i] for point in projected)
                               for i in (0, 1)))
        cameras[name] = camera
    for camera in cameras.values():
        camera.data.ortho_scale = extent * 1.16
    return cameras, studio, stats


def prepare_review(args, out):
    source = Path(args.source).expanduser().resolve(strict=True)
    source_hash = sha256(source)
    if source.suffix.lower() in {".glb", ".gltf"} and args.units != "m":
        raise ValueError("GLB/GLTF coordinates import in meters; explicitly use --units m")
    reference, reference_record = load_reference_review(args)
    resolution = reference["render"]["resolution"][0] if reference else (args.resolution or 900)
    import_source(source)
    vertices, faces, source_objects = evaluated_snapshot()
    if reference is not None:
        transform = Matrix(reference["source_to_review_matrix"])
    else:
        scale = 1000 if args.units == "m" else 1
        angle = {"-Y": 0, "+Y": math.pi, "+X": -math.pi / 2, "-X": math.pi / 2}[args.front_axis]
        transform = Matrix.Rotation(angle, 4, "Z") @ Matrix.Scale(scale, 4)
        points = [transform @ Vector(vertex) for vertex in vertices]
        lower = Vector([min(point[i] for point in points) for i in range(3)])
        upper = Vector([max(point[i] for point in points) for i in range(3)])
        translation = Vector((-(lower.x + upper.x) / 2, -(lower.y + upper.y) / 2, -lower.z))
        transform = Matrix.Translation(translation) @ transform
    vertices = [tuple(transform @ Vector(vertex)) for vertex in vertices]
    obj = make_geometry(vertices, faces)
    cameras, studio, stats = setup_review_scene(obj, resolution, reference)
    manifest = {
        "schema": SCHEMA, "status": "preparing", "mode": "review",
        "source": {"path": str(source), "sha256": source_hash, "imported_units": args.units,
                   "imported_up_axis": "+Z", "imported_front_axis": args.front_axis,
                   "render_visible_meshes": source_objects},
        "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode("ascii", errors="replace"),
        "script_sha256": sha256(__file__),
        "units": {"mesh_coordinates": "millimeters", "scene_scale_length": 0.001,
                  "up_axis": "+Z", "front_axis": "-Y"},
        "source_to_review_matrix": [list(row) for row in transform],
        "reference_review": reference_record,
        "geometry": stats, "geometry_changes": "Rigid axis rotation, unit scaling and placement only; no repair or sculpt.",
        "render": {"engine": "BLENDER_WORKBENCH", "studio_light": studio,
                   "resolution": [resolution, resolution], "textures": False,
                   "cavity": False, "cast_shadows": False, "smooth_shading": True,
                   "camera_projection": "ORTHO", "common_scale_all_views": True},
        "cameras": {}, "limitations": LIMITATIONS,
    }
    write_json(out / "manifest.json", manifest)
    for name, camera in cameras.items():
        bpy.context.scene.camera = camera
        bpy.context.scene.render.filepath = str(out / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        manifest["cameras"][name] = {
            "location_mm": list(camera.location), "rotation_euler_radians": list(camera.rotation_euler),
            "ortho_scale_mm": camera.data.ortho_scale,
            "clip_start_mm": camera.data.clip_start, "clip_end_mm": camera.data.clip_end,
            "shift_xy": [camera.data.shift_x, camera.data.shift_y], "image": f"{name}.png",
            "image_sha256": sha256(out / f"{name}.png"),
        }
    bpy.context.scene.camera = cameras["front"]
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "review.blend"))
    if sha256(source) != source_hash:
        raise RuntimeError("Source hash changed during review")
    if reference_record and sha256(reference_record["manifest_path"]) != reference_record["manifest_sha256"]:
        raise RuntimeError("Reference manifest changed during review")
    manifest["editable_scene"] = {"file": "review.blend", "sha256": sha256(out / "review.blend")}
    manifest["status"] = "review_ready_not_approved"
    write_json(out / "manifest.json", manifest)


def validate_closed_export(stats):
    failures = []
    if not stats["finite_vertices"] or not stats["finite_normals"] or not stats["triangles"]:
        failures.append("missing/nonfinite geometry")
    if not stats["watertight_edge_manifold"]:
        failures.append("open or nonmanifold edges")
    if stats["inconsistent_winding_edges"]:
        failures.append("inconsistent winding")
    if stats["degenerate_triangles_area_le_1e_minus12_mm2"] or stats["zero_length_edges"]:
        failures.append("degenerate geometry")
    if not stats["component_signed_volumes_mm3"] or any(v <= 0 for v in stats["component_signed_volumes_mm3"]):
        failures.append("nonpositive component signed volume")
    if abs(stats["minimum_z_mm"]) > 0.001:
        failures.append("base not on Z=0")
    if failures:
        raise ValueError("Export geometry gate failed: " + "; ".join(failures))


def prepare_export(args, out):
    review = Path(args.review).expanduser().resolve(strict=True)
    manifest_path = review / "manifest.json"
    approved = json.loads(manifest_path.read_text())
    if approved.get("schema") != SCHEMA or approved.get("status") != "review_ready_not_approved":
        raise ValueError("Expected a complete review manifest from this script")
    scene = review / "review.blend"
    if sha256(scene) != approved["editable_scene"]["sha256"]:
        raise ValueError("Reviewed scene changed; create and inspect a new review")
    for name in VIEWS:
        image = review / f"{name}.png"
        if sha256(image) != approved["cameras"][name]["image_sha256"]:
            raise ValueError(f"Review image changed: {name}")
    original = Path(approved["source"]["path"])
    if sha256(original) != approved["source"]["sha256"]:
        raise ValueError("Original source changed; create a new review")
    import_source(scene)
    vertices, faces, _ = evaluated_snapshot()
    obj = make_geometry(vertices, faces)
    expected = mesh_stats(obj.data)
    bpy.ops.wm.stl_export(filepath=str(out / "portrait_mm.stl"),
                          export_selected_objects=True, use_scene_unit=False,
                          global_scale=1.0, forward_axis="Y", up_axis="Z")
    # glTF is meters. Set a real object scale, not just Blender's display units.
    obj.scale = (0.001, 0.001, 0.001)
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.ops.export_scene.gltf(filepath=str(out / "portrait_m.glb"), export_format="GLB",
                              use_selection=True, export_yup=True, export_apply=True,
                              export_animations=False, export_cameras=False, export_lights=False)
    checks = {}
    for filename, factor in (("portrait_mm.stl", 1.0), ("portrait_m.glb", 1000.0)):
        path = out / filename
        import_source(path)
        points, polygons, _ = evaluated_snapshot()
        obj = make_geometry([tuple(value * factor for value in point) for point in points], polygons)
        stats = mesh_stats(obj.data)
        error = max(abs(a - b) for actual, wanted in zip(stats["bounds_mm"], expected["bounds_mm"])
                    for a, b in zip(actual, wanted))
        tolerance = max(0.001, max(expected["dimensions_mm"]) * 1e-5)
        if error > tolerance:
            raise ValueError(f"{filename}: reimport scale/axis error {error:.6g} mm exceeds {tolerance:.6g}")
        # STL is welded by Blender's importer. glTF may split vertices at normals
        # or material seams, so its raw edge-manifold result is reported, not hidden.
        if filename.endswith(".stl"):
            validate_closed_export(stats)
            if stats["components"] != 1 and not args.allow_multiple_components:
                raise ValueError("Multiple parts after STL reimport: use --allow-multiple-components only if intentional and reviewed")
        checks[filename] = {"sha256": sha256(path), "reimport_geometry_mm": stats,
                            "max_bounds_error_mm": error, "bounds_tolerance_mm": tolerance}
    if sha256(original) != approved["source"]["sha256"]:
        raise RuntimeError("Source hash changed during export")
    write_json(out / "manifest.json", {
        "schema": SCHEMA, "status": "export_geometry_checks_passed_not_print_certified",
        "mode": "export", "explicit_review_approval": True,
        "review_manifest": str(manifest_path), "review_manifest_sha256": sha256(manifest_path),
        "reviewed_scene_sha256": approved["editable_scene"]["sha256"],
        "source": approved["source"], "blender_version": bpy.app.version_string,
        "script_sha256": sha256(__file__), "geometry": expected, "exports": checks,
        "units": {"STL_coordinates": "millimeters", "GLB_coordinates": "meters",
                  "GLB_format_up": "+Y", "reimported_review_up": "+Z", "review_front": "-Y"},
        "multiple_components_explicitly_allowed": args.allow_multiple_components,
        "limitations": LIMITATIONS,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", help="Local source geometry; never overwritten")
    parser.add_argument("--out", required=True, help="New local output directory; existing paths are refused")
    parser.add_argument("--units", choices=("mm", "m"), help="Units of imported coordinates; GLB/GLTF requires m")
    parser.add_argument("--front-axis", choices=("-Y", "+Y", "-X", "+X"), help="Imported model's forward axis; always Z-up")
    parser.add_argument("--reference-review", help="Completed baseline review; reuse its placement, six cameras, lighting and resolution exactly")
    parser.add_argument("--resolution", type=int, help="Square image size; default 900, or inherited from --reference-review")
    parser.add_argument("--export", action="store_true", help="Separate export phase; no new shaping or repair")
    parser.add_argument("--review", help="Previously rendered review directory")
    parser.add_argument("--approve-reviewed-geometry", action="store_true", help="Explicit acknowledgement that all views were inspected")
    parser.add_argument("--allow-multiple-components", action="store_true", help="Export intentionally separate parts after review")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    if args.export:
        if not args.review or not args.approve_reviewed_geometry:
            parser.error("--export requires --review and --approve-reviewed-geometry")
        if args.source or args.units or args.front_axis or args.reference_review:
            parser.error("Export uses the reviewed scene; do not supply --source/--units/--front-axis/--reference-review")
    else:
        if not args.source or not args.units or not args.front_axis:
            parser.error("Review requires --source, --units and --front-axis (use --front-axis=-Y)")
        if args.review or args.approve_reviewed_geometry or args.allow_multiple_components:
            parser.error("Review cannot include export-only flags")
    if args.resolution is not None and not 64 <= args.resolution <= 8192:
        parser.error("--resolution must be between 64 and 8192")
    out = fresh_directory(args.out)
    try:
        (prepare_export if args.export else prepare_review)(args, out)
    except Exception as error:
        write_json(out / "FAILED.json", {"status": "failed_do_not_use_outputs", "error": str(error),
                                         "traceback": traceback.format_exc()})
        raise
    print(f"PORTRAIT_TO_PRINT_RESULT {out / 'manifest.json'}", flush=True)


if __name__ == "__main__":
    main()
