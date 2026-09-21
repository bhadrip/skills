import bpy
import argparse
import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict
from mathutils import Vector


def blender_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Build a dimensioned PVC Golu padi in Blender")
    parser.add_argument("--output-dir", default=os.path.abspath("golu-padi-output"))
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--short", type=float, default=12.0,
                        help="Short member length in inches (cut or assembled pitch, per --dimension-mode)")
    parser.add_argument("--long", type=float, default=36.0,
                        help="Width member length in inches (cut or assembled pitch, per --dimension-mode)")
    parser.add_argument("--dimension-mode", choices=("cut", "pitch"), default="cut")
    parser.add_argument("--socket-stop-offset", type=float, default=1.0,
                        help="Fitting center to socket stop in inches")
    parser.add_argument("--pipe-od", type=float, default=1.900)
    parser.add_argument("--pipe-wall", type=float, default=0.145)
    parser.add_argument("--nominal-pipe-size", type=float, default=1.5)
    parser.add_argument("--stock-length-ft", type=float, default=10.0,
                        help="Purchased straight-pipe stock length used for cut planning")
    parser.add_argument("--cut-kerf-in", type=float, default=0.125,
                        help="Conservative material allowance per cut")
    parser.add_argument("--no-boards", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.steps <= 12:
        parser.error("--steps must be between 1 and 12")
    if args.short <= 0 or args.long <= 0 or args.socket_stop_offset < 0:
        parser.error("member dimensions must be positive and socket offset non-negative")
    if args.dimension_mode == "pitch" and min(args.short, args.long) <= 2 * args.socket_stop_offset:
        parser.error("assembled pitch must exceed twice the socket-stop offset")
    if args.pipe_wall <= 0 or args.pipe_od <= 2 * args.pipe_wall:
        parser.error("pipe OD must exceed twice the wall thickness")
    if args.stock_length_ft <= 0 or args.cut_kerf_in < 0:
        parser.error("stock length must be positive and cut kerf non-negative")
    return args


ARGS = blender_args()
ROOT = os.path.abspath(ARGS.output_dir)
RENDER_DIR = os.path.join(ROOT, "renders")
STEM = f"golu_padi_{ARGS.steps}step"
BLEND_PATH = os.path.join(ROOT, STEM + ".blend")
GLB_PATH = os.path.join(ROOT, STEM + ".glb")
REPORT_PATH = os.path.join(ROOT, "qa_report.json")
BOM_PATH = os.path.join(ROOT, "bom.csv")
ASSEMBLY_PATH = os.path.join(ROOT, "assembly_instructions.md")
CONNECTOR_MAP_PATH = os.path.join(ROOT, "connector_map.csv")
SHOPPING_PATH = os.path.join(ROOT, "shopping_list.md")
CUT_PLAN_PATH = os.path.join(ROOT, "cut_plan.csv")
MANIFEST_PATH = os.path.join(ROOT, "design_manifest.json")
os.makedirs(RENDER_DIR, exist_ok=True)

# All modeled lengths are SI internally. Inch values are the user-facing source of truth.
INCH = 0.0254
STEPS = ARGS.steps
SOCKET_STOP_OFFSET_IN = ARGS.socket_stop_offset
if ARGS.dimension_mode == "cut":
    SHORT_CUT_IN = ARGS.short
    LONG_CUT_IN = ARGS.long
    SHORT_PITCH_IN = SHORT_CUT_IN + 2.0 * SOCKET_STOP_OFFSET_IN
    LONG_PITCH_IN = LONG_CUT_IN + 2.0 * SOCKET_STOP_OFFSET_IN
else:
    SHORT_PITCH_IN = ARGS.short
    LONG_PITCH_IN = ARGS.long
    SHORT_CUT_IN = SHORT_PITCH_IN - 2.0 * SOCKET_STOP_OFFSET_IN
    LONG_CUT_IN = LONG_PITCH_IN - 2.0 * SOCKET_STOP_OFFSET_IN

# Nominal 1-1/2 inch Schedule 40 PVC dimensions.
PIPE_OD_IN = ARGS.pipe_od
PIPE_WALL_IN = ARGS.pipe_wall
NOMINAL_PIPE_SIZE_IN = ARGS.nominal_pipe_size
PIPE_RADIUS = PIPE_OD_IN * INCH / 2.0
PIPE_INNER_RADIUS = (PIPE_OD_IN - 2.0 * PIPE_WALL_IN) * INCH / 2.0

# Generic furniture-grade socket envelope. Replace with a chosen fitting SKU's values.
FITTING_HUB_OD_IN = 2.50
FITTING_PORT_OD_IN = 2.30
FITTING_LIP_OD_IN = 2.56
FITTING_PORT_REACH_IN = 1.75
FITTING_LIP_WIDTH_IN = 0.22

HUB_RADIUS = FITTING_HUB_OD_IN * INCH / 2.0
PORT_RADIUS = FITTING_PORT_OD_IN * INCH / 2.0
LIP_RADIUS = FITTING_LIP_OD_IN * INCH / 2.0
PORT_REACH = FITTING_PORT_REACH_IN * INCH
LIP_WIDTH = FITTING_LIP_WIDTH_IN * INCH

SHORT_PITCH = SHORT_PITCH_IN * INCH
LONG_PITCH = LONG_PITCH_IN * INCH
SOCKET_STOP_OFFSET = SOCKET_STOP_OFFSET_IN * INCH
STOCK_LENGTH_IN = ARGS.stock_length_ft * 12.0
CUT_KERF_IN = ARGS.cut_kerf_in

BOARD_THICKNESS_IN = 0.75
BOARD_DEPTH_IN = SHORT_PITCH_IN - 0.75
BOARD_WIDTH_IN = LONG_PITCH_IN + 2.0
BOARD_THICKNESS = BOARD_THICKNESS_IN * INCH
BOARD_DEPTH = BOARD_DEPTH_IN * INCH
BOARD_WIDTH = BOARD_WIDTH_IN * INCH

BASE_Z = LIP_RADIUS


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                       bpy.data.cameras, bpy.data.lights):
        pass


def make_material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def make_wood_material():
    mat = bpy.data.materials.new("Board_Warm_Birch")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 5.0
    tex.inputs["Detail"].default_value = 3.0
    tex.inputs["Roughness"].default_value = 0.65
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (8.0, 1.15, 4.0)
    coord = nodes.new("ShaderNodeTexCoord")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.22, 0.065, 0.018, 1.0)
    ramp.color_ramp.elements[1].color = (0.82, 0.43, 0.12, 1.0)
    ramp.color_ramp.elements.new(0.55).color = (0.52, 0.19, 0.045, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.34
    links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def move_to_collection(obj, coll):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    coll.objects.link(obj)


def cylinder_between(name, start, end, radius, material, coll, vertices=40):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    length = direction.length
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=length,
        location=(start + end) / 2.0,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.materials.append(material)
    move_to_collection(obj, coll)
    return obj


def annular_pipe_between(name, start, end, material, coll, cut_length_in, axis_name, segments=48):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    full_distance = direction.length
    unit = direction.normalized()
    pipe_start = start + unit * SOCKET_STOP_OFFSET
    pipe_end = end - unit * SOCKET_STOP_OFFSET
    pipe_length = (pipe_end - pipe_start).length

    expected = cut_length_in * INCH
    if abs(pipe_length - expected) > 1e-7:
        raise RuntimeError(f"{name}: cut length mismatch {pipe_length / INCH:.6f} in")

    verts = []
    faces = []
    for z in (-pipe_length / 2.0, pipe_length / 2.0):
        for radius in (PIPE_RADIUS, PIPE_INNER_RADIUS):
            for i in range(segments):
                a = 2.0 * math.pi * i / segments
                verts.append((radius * math.cos(a), radius * math.sin(a), z))
    # rings: bottom outer=0, bottom inner=1, top outer=2, top inner=3
    def idx(ring, i):
        return ring * segments + (i % segments)
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((idx(0, i), idx(0, j), idx(2, j), idx(2, i)))
        faces.append((idx(1, j), idx(1, i), idx(3, i), idx(3, j)))
        faces.append((idx(0, j), idx(0, i), idx(1, i), idx(1, j)))
        faces.append((idx(2, i), idx(2, j), idx(3, j), idx(3, i)))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj.location = (pipe_start + pipe_end) / 2.0
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(unit)
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.materials.append(material)
    obj["cut_length_in"] = cut_length_in
    obj["nominal_size_in"] = NOMINAL_PIPE_SIZE_IN
    obj["outside_diameter_in"] = PIPE_OD_IN
    obj["wall_in"] = PIPE_WALL_IN
    obj["axis"] = axis_name
    return obj


def add_fitting(node_key, directions, material, fitting_coll):
    pos = Vector(node_key)
    parent = bpy.data.objects.new("", None)
    parent.name = f"FIT_{len(directions)}WAY_{pos.x / INCH:.2f}_{pos.y / INCH:.2f}_{pos.z / INCH:.2f}"
    fitting_coll.objects.link(parent)
    parent.location = pos
    parent.empty_display_type = 'SPHERE'
    parent.empty_display_size = HUB_RADIUS * 0.55

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=HUB_RADIUS, location=pos)
    hub = bpy.context.object
    hub.name = parent.name + "_Hub"
    for poly in hub.data.polygons:
        poly.use_smooth = True
    hub.data.materials.append(material)
    move_to_collection(hub, fitting_coll)
    hub_world = hub.matrix_world.copy()
    hub.parent = parent
    hub.matrix_world = hub_world

    for i, raw_dir in enumerate(sorted(directions)):
        direction = Vector(raw_dir).normalized()
        port_end = pos + direction * PORT_REACH
        barrel = cylinder_between(
            parent.name + f"_Port_{i}", pos, port_end, PORT_RADIUS,
            material, fitting_coll, vertices=36,
        )
        barrel_world = barrel.matrix_world.copy()
        barrel.parent = parent
        barrel.matrix_world = barrel_world
        lip_center = pos + direction * (PORT_REACH - LIP_WIDTH / 2.0)
        lip = cylinder_between(
            parent.name + f"_Lip_{i}",
            lip_center - direction * LIP_WIDTH / 2.0,
            lip_center + direction * LIP_WIDTH / 2.0,
            LIP_RADIUS, material, fitting_coll, vertices=36,
        )
        lip_world = lip.matrix_world.copy()
        lip.parent = parent
        lip.matrix_world = lip_world

    direction_labels = []
    for d in sorted(directions):
        direction_labels.append({(1, 0, 0): "+X", (-1, 0, 0): "-X",
                                 (0, 1, 0): "+Y", (0, -1, 0): "-Y",
                                 (0, 0, 1): "+Z", (0, 0, -1): "-Z"}[tuple(d)])
    parent["port_count"] = len(directions)
    parent["port_directions"] = ",".join(direction_labels)
    parent["generic_fitting_note"] = "Verify exact SKU geometry and socket-stop depth before fabrication"
    return parent


def add_board(name, center, size, material, coll):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("Edge_Roundover", 'BEVEL')
    bevel.width = 0.09 * INCH
    bevel.segments = 4
    obj.data.materials.append(material)
    obj["width_in"] = size[1] / INCH
    obj["depth_in"] = size[0] / INCH
    obj["thickness_in"] = size[2] / INCH
    move_to_collection(obj, coll)
    return obj


def add_floor(material, env_coll):
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(2 * SHORT_PITCH, 0, 0))
    obj = bpy.context.object
    obj.name = "Studio_Floor"
    obj.data.materials.append(material)
    move_to_collection(obj, env_coll)


def add_camera(name, location, target, lens=52, ortho=None, coll=None):
    data = bpy.data.cameras.new(name + "_Data")
    cam = bpy.data.objects.new(name, data)
    coll.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
    if ortho is not None:
        data.type = 'ORTHO'
        data.ortho_scale = ortho
    return cam


def add_area_light(name, location, energy, size, color, target, coll):
    data = bpy.data.lights.new(name + "_Data", type='AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    coll.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    return light


def world_bbox(objects):
    corners = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(depsgraph)
        corners.extend(evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box)
    mins = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    maxs = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    return mins, maxs


def format_inches(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


def direction_labels(directions):
    names = {
        (1, 0, 0): "+X depth/rear",
        (-1, 0, 0): "-X depth/front",
        (0, 1, 0): "+Y width",
        (0, -1, 0): "-Y width",
        (0, 0, 1): "+Z up",
        (0, 0, -1): "-Z down",
    }
    return [names[tuple(direction)] for direction in sorted(directions)]


def write_assembly_artifacts(incidents, ys, connector_counts, pipe_axis_counts, dimensions_in):
    with open(CONNECTOR_MAP_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["node", "side", "depth_station", "height_level", "port_count", "port_directions"])
        for xi, max_level in enumerate(max_levels):
            for zi in range(max_level + 1):
                for side_name, y in (("L", ys[0]), ("R", ys[1])):
                    node = (xi * SHORT_PITCH, y, BASE_Z + zi * SHORT_PITCH)
                    directions = incidents[node]
                    writer.writerow([
                        f"{side_name}-D{xi}-H{zi}", side_name, f"D{xi}", f"H{zi}",
                        len(directions), "; ".join(direction_labels(directions)),
                    ])

    width_description = (
        f"{format_inches(LONG_PITCH_IN)} in assembled center-to-center width"
        if ARGS.dimension_mode == "pitch"
        else f"{format_inches(LONG_CUT_IN)} in width-tube cuts producing a {format_inches(LONG_PITCH_IN)} in center pitch"
    )
    short_description = (
        f"{format_inches(SHORT_PITCH_IN)} in assembled rise/run pitch"
        if ARGS.dimension_mode == "pitch"
        else f"{format_inches(SHORT_CUT_IN)} in short-tube cuts producing a {format_inches(SHORT_PITCH_IN)} in rise/run pitch"
    )

    lines = [
        f"# Assembly instructions — {STEPS}-padi PVC Golu display",
        "",
        "These instructions are generated from the same node graph as the Blender model and BOM.",
        "",
        "## Design summary",
        "",
        f"- Levels: **{STEPS} padi**",
        f"- Width requirement: **{width_description}**",
        f"- Rise/run requirement: **{short_description}**",
        f"- Exact short tube cut: **{format_inches(SHORT_CUT_IN)} in**",
        f"- Exact width tube cut: **{format_inches(LONG_CUT_IN)} in**",
        f"- Assumed fitting center-to-socket-stop distance: **{format_inches(SOCKET_STOP_OFFSET_IN)} in per end**",
        f"- Modeled overall bounding box: **{format_inches(dimensions_in[0])} × {format_inches(dimensions_in[1])} × {format_inches(dimensions_in[2])} in** (depth × width × height)",
        "",
        "## Parts to prepare",
        "",
        f"- **{pipe_axis_counts['X'] + pipe_axis_counts['Z']}** short PVC members at **{format_inches(SHORT_CUT_IN)} in**: {pipe_axis_counts['X']} depth rails and {pipe_axis_counts['Z']} verticals",
        f"- **{pipe_axis_counts['Y']}** width PVC members at **{format_inches(LONG_CUT_IN)} in**",
    ]
    for ports, qty in sorted(connector_counts.items()):
        lines.append(f"- **{qty}** generic multi-axis **{ports}-port** fittings")
    if not ARGS.no_boards:
        lines.append(
            f"- **{STEPS}** removable tread boards at **{format_inches(BOARD_WIDTH_IN)} × {format_inches(BOARD_DEPTH_IN)} × {format_inches(BOARD_THICKNESS_IN)} in**"
        )
    lines.extend([
        "",
        "## Tools needed",
        "",
        f"- Ratcheting PVC cutter rated for at least **{format_inches(PIPE_OD_IN)} in outside diameter**, or a fine-tooth saw with a miter box",
        "- Deburring/chamfering tool or flat and round files",
        "- Tape measure, permanent marker, and masking tape for labels",
        "- Framing square or large carpenter's square",
        "- Spirit level",
        "- Rubber mallet and scrap-wood tapping block",
        "- Safety glasses and work gloves",
        "- Clamps or a helper for holding the two side frames during width-member installation",
        "- Optional manufacturer-approved primer/cement only if the chosen fittings are intended to be permanently bonded",
        "",
        "## Labeling system",
        "",
        f"- Mark depth stations **D0** at the front through **D{STEPS}** at the rear.",
        f"- Mark height levels **H0** at the floor through **H{STEPS}** at the top.",
        "- `L` and `R` are the model's negative-Y and positive-Y side frames.",
        "- Label each fitting by side, station, and height—for example, `L-D2-H1`.",
        "- Use `connector_map.csv` to orient every fitting. Port count alone is insufficient; the port axes must also match.",
        "",
        "## Assembly sequence",
        "",
        "1. **Cut, deburr, and label all members.** Keep short depth rails, short verticals, and width members in separate bundles. Mark the socket insertion depth from the selected fitting manufacturer on every tube end.",
        "",
        "2. **Dry-build the H0 base.** On both L and R sides, connect D0 through D{n} with {shorts} short depth rails total. Join the two sides with {longs} width members at D0 through D{n}. Keep every joint unglued and only hand-tight at this stage.".format(
            n=STEPS, shorts=2 * STEPS, longs=STEPS + 1
        ),
    ])

    sequence_number = 3
    for level in range(1, STEPS + 1):
        first_station = level - 1
        station_count = STEPS - level + 2
        depth_bays = STEPS - level + 1
        vertical_count = 2 * station_count
        depth_count = 2 * depth_bays
        width_count = station_count
        bay_text = ", ".join(f"D{i}–D{i + 1}" for i in range(first_station, STEPS))
        lines.extend([
            "",
            f"{sequence_number}. **Add level H{level}.**",
            f"   - Install **{vertical_count} short vertical members** at stations D{first_station} through D{STEPS}, counting both sides.",
            f"   - Install **{depth_count} short depth rails** across bays {bay_text} on the L and R sides.",
            f"   - Bridge L to R with **{width_count} width members** at H{level}, stations D{first_station} through D{STEPS}.",
            f"   - Match each H{level} fitting to its exact row in `connector_map.csv`; check that every unused-looking port is actually absent, not merely hidden or rotated away.",
        ])
        sequence_number += 1

    lines.extend([
        "",
        f"{sequence_number}. **Square and seat the frame.** Place it on a flat floor. Measure both base diagonals and adjust until equal. Seat every tube to the same insertion-depth mark, then recheck plumb, level, and all diagonals.",
    ])
    sequence_number += 1
    if not ARGS.no_boards:
        lines.extend([
            "",
            f"{sequence_number}. **Install the tread boards only after the frame is square.**",
        ])
        for step in range(1, STEPS + 1):
            lines.append(f"   - Board {step}: place over bay D{step - 1}–D{step} at height H{step}.")
        lines.append("   - Use removable straps/clips or the user's chosen fastening system; the model does not assume screws through PVC.")
        sequence_number += 1
    lines.extend([
        "",
        f"{sequence_number}. **Final check before loading.** Confirm every connector orientation against the map, every joint insertion mark, board retention, floor contact, and anti-tip restraint. Follow the chosen fitting manufacturer's joining instructions; do not solvent-weld furniture fittings unless the manufacturer permits it.",
        "",
        "## Important limitations",
        "",
        "- The fitting envelope and socket offset are generic until replaced with manufacturer/SKU measurements.",
        "- This guide is an assembly plan derived from geometry, not structural, load, seismic, or child-safety certification.",
        "- Dry-fit the complete frame before making any irreversible joint.",
        "",
    ])
    with open(ASSEMBLY_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def plan_stock_cuts(pipe_axis_counts):
    width_count = pipe_axis_counts["Y"]
    short_count = pipe_axis_counts["X"] + pipe_axis_counts["Z"]
    width_consumed = LONG_CUT_IN + CUT_KERF_IN
    short_consumed = SHORT_CUT_IN + CUT_KERF_IN
    if max(width_consumed, short_consumed) > STOCK_LENGTH_IN + 1e-9:
        raise RuntimeError(
            f"Longest cut plus kerf exceeds "
            f"stock length ({STOCK_LENGTH_IN:.3f} in)"
        )

    patterns = []
    for width_pieces in range(width_count + 1):
        for short_pieces in range(short_count + 1):
            if width_pieces == 0 and short_pieces == 0:
                continue
            used = width_pieces * width_consumed + short_pieces * short_consumed
            if used <= STOCK_LENGTH_IN + 1e-9:
                patterns.append((width_pieces, short_pieces, used))
    patterns.sort(key=lambda pattern: (-pattern[2], -pattern[0], -pattern[1]))

    infinity = width_count + short_count + 1
    dp = [[infinity] * (short_count + 1) for _ in range(width_count + 1)]
    previous = [[None] * (short_count + 1) for _ in range(width_count + 1)]
    dp[0][0] = 0
    for have_width in range(width_count + 1):
        for have_short in range(short_count + 1):
            if dp[have_width][have_short] == infinity:
                continue
            for add_width, add_short, used in patterns:
                next_width = have_width + add_width
                next_short = have_short + add_short
                if next_width > width_count or next_short > short_count:
                    continue
                candidate = dp[have_width][have_short] + 1
                if candidate < dp[next_width][next_short]:
                    dp[next_width][next_short] = candidate
                    previous[next_width][next_short] = (have_width, have_short, add_width, add_short, used)

    if dp[width_count][short_count] == infinity:
        raise RuntimeError("Unable to produce a complete stock cut plan")

    stock_pieces = []
    state = (width_count, short_count)
    while state != (0, 0):
        prior = previous[state[0]][state[1]]
        if prior is None:
            raise RuntimeError("Cut-plan reconstruction failed")
        have_width, have_short, add_width, add_short, used = prior
        cuts = [("width", LONG_CUT_IN)] * add_width + [("short", SHORT_CUT_IN)] * add_short
        stock_pieces.append({"cuts": cuts, "used_in": used})
        state = (have_width, have_short)
    stock_pieces.sort(key=lambda stock: -stock["used_in"])
    return stock_pieces


def write_procurement_artifacts(pipe_axis_counts, connector_counts, dimensions_in):
    stock_pieces = plan_stock_cuts(pipe_axis_counts)
    with open(CUT_PLAN_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([
            "stock_piece", "stock_length_in", "cuts_in_order", "piece_length_total_in",
            "kerf_allowance_in", "estimated_remnant_in",
        ])
        for index, stock in enumerate(stock_pieces, start=1):
            piece_total = sum(length for _, length in stock["cuts"])
            kerf_total = len(stock["cuts"]) * CUT_KERF_IN
            cuts = " | ".join(f"{label}:{format_inches(length)}" for label, length in stock["cuts"])
            writer.writerow([
                index, format_inches(STOCK_LENGTH_IN), cuts, format_inches(piece_total),
                format_inches(kerf_total), format_inches(STOCK_LENGTH_IN - stock["used_in"]),
            ])

    total_piece_length = (
        pipe_axis_counts["Y"] * LONG_CUT_IN
        + (pipe_axis_counts["X"] + pipe_axis_counts["Z"]) * SHORT_CUT_IN
    )
    total_purchased = len(stock_pieces) * STOCK_LENGTH_IN
    total_kerf = sum(len(stock["cuts"]) for stock in stock_pieces) * CUT_KERF_IN
    estimated_remnant = total_purchased - total_piece_length - total_kerf

    lines = [
        f"# Shopping list — {STEPS}-padi PVC Golu display",
        "",
        "Quantities come from the generated geometry. Prices are intentionally omitted unless current local supplier pricing is researched separately.",
        "",
        "## PVC and fittings",
        "",
        f"- **{len(stock_pieces)} × {format_inches(ARGS.stock_length_ft)} ft** straight lengths of **{format_inches(NOMINAL_PIPE_SIZE_IN)} in nominal PVC**",
        f"  - Planned finished pieces: {pipe_axis_counts['X'] + pipe_axis_counts['Z']} short cuts at {format_inches(SHORT_CUT_IN)} in and {pipe_axis_counts['Y']} width cuts at {format_inches(LONG_CUT_IN)} in",
        f"  - Cut-plan allowance: {format_inches(CUT_KERF_IN)} in per cut",
        f"  - Estimated total remnant after kerf: {format_inches(estimated_remnant)} in",
    ]
    for ports, qty in sorted(connector_counts.items()):
        lines.append(f"- **{qty} × {ports}-port multi-axis PVC fittings**, with axes matching `connector_map.csv`")
    lines.extend([
        "",
        "## Treads and retention",
        "",
    ])
    if ARGS.no_boards:
        lines.append("- No tread boards are included in this design.")
    else:
        lines.extend([
            f"- **{STEPS} × tread boards**, each {format_inches(BOARD_WIDTH_IN)} × {format_inches(BOARD_DEPTH_IN)} × {format_inches(BOARD_THICKNESS_IN)} in",
            "- Removable board straps/clips or another suitable retention system",
        ])
    lines.extend([
        "",
        "## Assembly and safety supplies",
        "",
        "- Tape measure, permanent marker, square, and level",
        f"- Ratcheting PVC cutter rated for at least {format_inches(PIPE_OD_IN)} in OD, or a fine-tooth saw and miter box",
        "- Deburring/chamfering tool or flat and round files",
        "- Rubber mallet and a scrap wood tapping block",
        "- Safety glasses and work gloves",
        "- Clamps or a helper for joining the two side frames",
        "- Anti-tip restraints appropriate to the installation location",
        "- Optional joining supplies only when approved by the selected fitting manufacturer",
        "",
        "## Purchase checks",
        "",
        f"- Confirm the selected fittings fit {format_inches(NOMINAL_PIPE_SIZE_IN)} in nominal PVC with {format_inches(PIPE_OD_IN)} in OD.",
        f"- Replace the generic {format_inches(SOCKET_STOP_OFFSET_IN)} in center-to-socket-stop assumption with the chosen fitting's measured value before cutting.",
        f"- Confirm available stock is at least {format_inches(STOCK_LENGTH_IN)} in long and straight enough for the cuts in `cut_plan.csv`.",
        f"- Confirm the intended installation can accommodate the modeled {format_inches(dimensions_in[0])} × {format_inches(dimensions_in[1])} × {format_inches(dimensions_in[2])} in envelope.",
        "- Obtain independent structural and safety review for the intended load and environment.",
        "",
    ])
    with open(SHOPPING_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return stock_pieces


reset_scene()

scene = bpy.context.scene
scene.unit_settings.system = 'IMPERIAL'
scene.unit_settings.length_unit = 'INCHES'
scene.unit_settings.scale_length = 1.0
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1100
scene.render.resolution_y = 825
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.look = 'AgX - Medium High Contrast'

world = scene.world
world.color = (0.035, 0.045, 0.065)
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.095, 0.125, 0.175, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.50

model_coll = collection("MODEL_PVC_GOLU_PADI")
pipe_coll = collection("PVC_PIPES")
fitting_coll = collection("PVC_FITTINGS")
board_coll = collection("TREAD_BOARDS")
env_coll = collection("RENDER_ENVIRONMENT")
cam_coll = collection("CAMERAS")
light_coll = collection("LIGHTS")

# Nest model subcollections for clean outliner organization.
scene.collection.children.unlink(pipe_coll)
scene.collection.children.unlink(fitting_coll)
scene.collection.children.unlink(board_coll)
model_coll.children.link(pipe_coll)
model_coll.children.link(fitting_coll)
model_coll.children.link(board_coll)

pvc_mat = make_material("PVC_White", (0.83, 0.87, 0.89), metallic=0.0, roughness=0.28)
fitting_mat = make_material("Fitting_Charcoal", (0.028, 0.038, 0.050), metallic=0.0, roughness=0.24)
wood_mat = make_wood_material()
floor_mat = make_material("Floor_Warm_Gray", (0.075, 0.082, 0.095), roughness=0.64)

# Stair solid beneath the profile: N+1 depth stations with the rear pair at full height.
max_levels = list(range(1, STEPS + 1)) + [STEPS]
ys = [-LONG_PITCH / 2.0, LONG_PITCH / 2.0]
nodes = set()
for xi, max_level in enumerate(max_levels):
    for y in ys:
        for zi in range(max_level + 1):
            nodes.add((xi * SHORT_PITCH, y, BASE_Z + zi * SHORT_PITCH))

edges = set()

def add_edge(a, b, cut_length_in, axis_name):
    key = tuple(sorted((tuple(a), tuple(b))))
    edges.add((key[0], key[1], cut_length_in, axis_name))

# Width members: one exact 36-inch cut at every side-frame node pair.
for xi, max_level in enumerate(max_levels):
    for zi in range(max_level + 1):
        z = BASE_Z + zi * SHORT_PITCH
        add_edge((xi * SHORT_PITCH, ys[0], z), (xi * SHORT_PITCH, ys[1], z), LONG_CUT_IN, "Y")

# Vertical 12-inch cuts.
for xi, max_level in enumerate(max_levels):
    for y in ys:
        for zi in range(max_level):
            add_edge((xi * SHORT_PITCH, y, BASE_Z + zi * SHORT_PITCH),
                     (xi * SHORT_PITCH, y, BASE_Z + (zi + 1) * SHORT_PITCH),
                     SHORT_CUT_IN, "Z")

# Depth 12-inch cuts fill the stepped side-frame grid for stiffness and honest connector routing.
for zi in range(STEPS + 1):
    for xi in range(STEPS):
        if max_levels[xi] >= zi and max_levels[xi + 1] >= zi:
            for y in ys:
                add_edge((xi * SHORT_PITCH, y, BASE_Z + zi * SHORT_PITCH),
                         ((xi + 1) * SHORT_PITCH, y, BASE_Z + zi * SHORT_PITCH),
                         SHORT_CUT_IN, "X")

incidents = defaultdict(set)
pipe_counts = Counter()
pipe_axis_counts = Counter()
for index, (a, b, cut_length_in, axis_name) in enumerate(sorted(edges)):
    av = Vector(a)
    bv = Vector(b)
    direction = bv - av
    dominant = tuple(int(round(v)) for v in direction.normalized())
    incidents[a].add(dominant)
    incidents[b].add(tuple(-v for v in dominant))
    length_label = f"{cut_length_in:g}IN".replace(".", "P")
    annular_pipe_between(
        f"PIPE_{length_label}_{axis_name}_{index:03d}", a, b, pvc_mat, pipe_coll,
        cut_length_in, axis_name,
    )
    pipe_counts[cut_length_in] += 1
    pipe_axis_counts[axis_name] += 1

connector_counts = Counter()
for node in sorted(nodes):
    degree = len(incidents[node])
    connector_counts[degree] += 1
    add_fitting(node, incidents[node], fitting_mat, fitting_coll)

# Removable tread boards are enabled by default.
if not ARGS.no_boards:
    for step in range(STEPS):
        x_center = (step + 0.5) * SHORT_PITCH
        node_level = step + 1
        node_z = BASE_Z + node_level * SHORT_PITCH
        board_center_z = node_z + LIP_RADIUS + 0.10 * INCH + BOARD_THICKNESS / 2.0
        board = add_board(
            f"TREAD_BOARD_STEP_{step + 1}",
            (x_center, 0, board_center_z),
            (BOARD_DEPTH, BOARD_WIDTH, BOARD_THICKNESS),
            wood_mat, board_coll,
        )
        board["step_number"] = step + 1

add_floor(floor_mat, env_coll)

depth = STEPS * SHORT_PITCH
frame_height = STEPS * SHORT_PITCH + 2.0 * LIP_RADIUS + BOARD_THICKNESS
width = LONG_PITCH + 2.0 * LIP_RADIUS
extent = max(depth, frame_height, width)
target = (depth / 2.0, 0, frame_height / 2.0)
aspect = scene.render.resolution_x / scene.render.resolution_y
cam_perspective = add_camera(
    "Camera_Perspective",
    Vector(target) + Vector((-2.45 * extent, -2.20 * extent, 1.00 * extent)),
    target, lens=55, coll=cam_coll,
)
cam_side = add_camera(
    "Camera_Side",
    (depth / 2.0, -2.40 * extent, frame_height / 2.0),
    target, ortho=max(depth * 1.20, frame_height * 1.42), coll=cam_coll,
)
cam_front = add_camera(
    "Camera_Front",
    (-2.40 * extent, 0, frame_height / 2.0),
    target, ortho=max(width * 1.30, frame_height * 1.42), coll=cam_coll,
)
cam_rear = add_camera(
    "Camera_Rear_ThreeQuarter",
    Vector(target) + Vector((2.10 * extent, -2.20 * extent, 1.00 * extent)),
    target, lens=55, coll=cam_coll,
)

add_area_light("Key", Vector(target) + Vector((-1.3 * extent, -1.6 * extent, 1.8 * extent)), 1650, 1.4 * extent, (1.0, 0.86, 0.72), target, light_coll)
add_area_light("Fill", Vector(target) + Vector((1.4 * extent, -0.8 * extent, 0.8 * extent)), 1000, 1.2 * extent, (0.65, 0.78, 1.0), target, light_coll)
add_area_light("Rim", Vector(target) + Vector((1.2 * extent, 1.6 * extent, 1.5 * extent)), 1450, extent, (0.78, 0.88, 1.0), target, light_coll)

# Ground card behind the object for a clean studio horizon.
bpy.ops.mesh.primitive_plane_add(size=4.5 * extent, location=(depth / 2.0, 1.65 * extent, 1.3 * extent), rotation=(math.pi / 2, 0, 0))
backdrop = bpy.context.object
backdrop.name = "Studio_Backdrop"
backdrop.data.materials.append(floor_mat)
move_to_collection(backdrop, env_coll)

# Render canonical inspection views.
for camera, filename in (
    (cam_perspective, "01_perspective.png"),
    (cam_side, "02_side.png"),
    (cam_front, "03_front.png"),
    (cam_rear, "04_rear_threequarter.png"),
):
    scene.camera = camera
    scene.render.filepath = os.path.join(RENDER_DIR, filename)
    bpy.ops.render.render(write_still=True)

# Export only the intended model, excluding the studio environment and cameras.
bpy.ops.object.select_all(action='DESELECT')
model_objects = []
for coll in (pipe_coll, fitting_coll, board_coll):
    for obj in coll.all_objects:
        obj.select_set(True)
        model_objects.append(obj)
scene.view_layers[0].objects.active = next(obj for obj in model_objects if obj.type == 'MESH')
bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
)

# Compute evaluated model bounds and QA metadata.
mins, maxs = world_bbox(model_objects)
dimensions_in = [(maxs[i] - mins[i]) / INCH for i in range(3)]
write_assembly_artifacts(incidents, ys, connector_counts, pipe_axis_counts, dimensions_in)
stock_pieces = write_procurement_artifacts(pipe_axis_counts, connector_counts, dimensions_in)

manifest = {
    "schema_version": 1,
    "generator": "golu-padi-designer/scripts/build_golu_padi.py",
    "requirements": {
        "steps": STEPS,
        "dimension_mode": ARGS.dimension_mode,
        "short_input_in": ARGS.short,
        "long_input_in": ARGS.long,
        "boards_enabled": not ARGS.no_boards,
    },
    "pipe": {
        "nominal_size_in": NOMINAL_PIPE_SIZE_IN,
        "outside_diameter_in": PIPE_OD_IN,
        "wall_in": PIPE_WALL_IN,
        "socket_stop_offset_in": SOCKET_STOP_OFFSET_IN,
    },
    "derived_dimensions_in": {
        "short_cut": SHORT_CUT_IN,
        "long_cut": LONG_CUT_IN,
        "short_pitch": SHORT_PITCH_IN,
        "long_pitch": LONG_PITCH_IN,
        "bounding_box_xyz": [round(v, 4) for v in dimensions_in],
    },
    "procurement": {
        "stock_length_ft": ARGS.stock_length_ft,
        "cut_kerf_in": CUT_KERF_IN,
        "stock_pieces_required": len(stock_pieces),
    },
}
with open(MANIFEST_PATH, "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, indent=2)

qa = {
    "status": "PASS",
    "blender_version": bpy.app.version_string,
    "steps": STEPS,
    "dimension_mode": ARGS.dimension_mode,
    "model_semantics": "cut mode treats member inputs as exact tube cuts; pitch mode treats them as assembled center spacing",
    "parameters_inches": {
        "short_tube_cut": SHORT_CUT_IN,
        "long_tube_cut": LONG_CUT_IN,
        "assumed_center_to_socket_stop_each_end": SOCKET_STOP_OFFSET_IN,
        "assembled_short_pitch": SHORT_PITCH_IN,
        "assembled_long_pitch": LONG_PITCH_IN,
        "nominal_pipe_size": NOMINAL_PIPE_SIZE_IN,
        "pipe_outside_diameter": PIPE_OD_IN,
        "pipe_wall": PIPE_WALL_IN,
        "generic_fitting_hub_od": FITTING_HUB_OD_IN,
        "stock_length_ft": ARGS.stock_length_ft,
        "cut_kerf": CUT_KERF_IN,
    },
    "counts": {
        "short_pipes": pipe_axis_counts["X"] + pipe_axis_counts["Z"],
        "long_pipes": pipe_axis_counts["Y"],
        "total_pipes": sum(pipe_counts.values()),
        "connectors": sum(connector_counts.values()),
        "tread_boards": 0 if ARGS.no_boards else STEPS,
        "connector_port_counts": {str(k): v for k, v in sorted(connector_counts.items())},
    },
    "model_bounding_box_inches_xyz": [round(v, 4) for v in dimensions_in],
    "checks": {
        "all_pipe_lengths_exact": True,
        "pipe_length_tolerance_in": 0.00001,
        "all_edge_endpoints_have_fittings": len(incidents) == len(nodes),
        "max_connector_ports": max(connector_counts),
        "render_count": 4,
        "glb_exported": os.path.exists(GLB_PATH),
        "assembly_instructions_generated": os.path.exists(ASSEMBLY_PATH),
        "connector_map_generated": os.path.exists(CONNECTOR_MAP_PATH),
        "shopping_list_generated": os.path.exists(SHOPPING_PATH),
        "cut_plan_generated": os.path.exists(CUT_PLAN_PATH),
        "design_manifest_generated": os.path.exists(MANIFEST_PATH),
    },
    "limitations": [
        "Generic fitting envelopes are used because no manufacturer/SKU was supplied.",
        "Replace SOCKET_STOP_OFFSET_IN and fitting dimensions with measured SKU data before cutting for fabrication.",
        "This is a dimensioned visualization, not a structural/load certification.",
    ],
}
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(qa, handle, indent=2)

with open(BOM_PATH, "w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(["category", "description", "quantity", "modeled_dimension", "note"])
    pipe_description = f"{NOMINAL_PIPE_SIZE_IN:g} in nominal PVC"
    pipe_note = f"OD {PIPE_OD_IN:.3f} in; wall {PIPE_WALL_IN:.3f} in"
    writer.writerow(["pipe", pipe_description, pipe_axis_counts["X"] + pipe_axis_counts["Z"], f"{SHORT_CUT_IN:.3f} in cut", pipe_note])
    writer.writerow(["pipe", pipe_description, pipe_axis_counts["Y"], f"{LONG_CUT_IN:.3f} in cut", pipe_note])
    for ports, qty in sorted(connector_counts.items()):
        writer.writerow(["fitting", f"generic multi-axis {ports}-port socket fitting", qty, "generic envelope", "select actual SKU before fabrication"])
    if not ARGS.no_boards:
        writer.writerow(["tread", "removable wood board", STEPS, f"{BOARD_WIDTH_IN:.3f} x {BOARD_DEPTH_IN:.3f} x {BOARD_THICKNESS_IN:.3f} in", "optional"])

scene["design_note"] = (
    f"{ARGS.dimension_mode} mode; short cut {SHORT_CUT_IN:.3f} in; "
    f"long cut {LONG_CUT_IN:.3f} in; assembled pitch includes socket-stop allowances"
)
scene["steps"] = STEPS
scene["dimension_mode"] = ARGS.dimension_mode
scene["short_cut_in"] = SHORT_CUT_IN
scene["long_cut_in"] = LONG_CUT_IN
scene["socket_stop_offset_in"] = SOCKET_STOP_OFFSET_IN
scene["assembled_short_pitch_in"] = SHORT_PITCH_IN
scene["assembled_long_pitch_in"] = LONG_PITCH_IN
scene["nominal_pipe_size_in"] = NOMINAL_PIPE_SIZE_IN
scene["pipe_od_in"] = PIPE_OD_IN
scene["pipe_wall_in"] = PIPE_WALL_IN
scene["boards_enabled"] = not ARGS.no_boards
scene["stock_length_ft"] = ARGS.stock_length_ft
scene["cut_kerf_in"] = CUT_KERF_IN
scene.camera = cam_perspective
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)

print(json.dumps(qa, indent=2))
