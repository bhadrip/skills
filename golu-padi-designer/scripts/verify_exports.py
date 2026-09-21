import argparse
import bpy
import json
import os
import sys
from mathutils import Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Reopen and validate a generated Golu padi Blend/GLB pair")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--steps", type=int, required=True)
    return parser.parse_args(argv)


ARGS = parse_args()
ROOT = os.path.abspath(ARGS.output_dir)
STEM = f"golu_padi_{ARGS.steps}step"
GLB_PATH = os.path.join(ROOT, STEM + ".glb")
OUT_PATH = os.path.join(ROOT, "reopen_validation.json")
INCH = 0.0254


def bounds(objects):
    points = []
    for obj in objects:
        if obj.type == 'MESH':
            points.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return [round((hi[i] - lo[i]) / INCH, 4) for i in range(3)]


# Launch Blender with the generated .blend open before running this script.
pipe_objects = [o for o in bpy.data.objects if o.name.startswith("PIPE_")]
board_objects = [o for o in bpy.data.objects if o.name.startswith("TREAD_BOARD_STEP_")]
expected_steps = int(bpy.context.scene.get("steps", ARGS.steps))
blend_checks = {
    "pipe_count": len(pipe_objects),
    "board_count": len(board_objects),
    "steps": expected_steps,
    "saved_scene_short_cut_in": bpy.context.scene.get("short_cut_in"),
    "saved_scene_long_cut_in": bpy.context.scene.get("long_cut_in"),
    "all_pipes_have_cut_length": all(o.get("cut_length_in") for o in pipe_objects),
}

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=GLB_PATH)
imported = list(bpy.context.scene.objects)
glb_meshes = [o for o in imported if o.type == 'MESH']

checks_pass = (
    bool(pipe_objects)
    and blend_checks["all_pipes_have_cut_length"]
    and expected_steps == ARGS.steps
    and bool(glb_meshes)
)
result = {
    "status": "PASS" if checks_pass else "FAIL",
    "blend_reopen": blend_checks,
    "glb_reimport": {
        "mesh_object_count": len(glb_meshes),
        "bounding_box_inches_xyz": bounds(imported),
    },
}
with open(OUT_PATH, "w", encoding="utf-8") as handle:
    json.dump(result, handle, indent=2)
print(json.dumps(result, indent=2))
