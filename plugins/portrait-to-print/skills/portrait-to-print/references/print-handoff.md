# Prepare and verify the actual deliverable

## Geometry and units

Preserve an editable scene and the reviewed source. Establish coordinate units,
up axis and face-forward direction before adding a base or resizing. Blender
normally converts glTF's Y-up convention on import; do not apply that rotation
twice. STL does not encode units. The mesh helper expects already oriented
millimeter STL with Z up; it does not guess anatomy or orientation.

Check finite/nonempty geometry, component count with component statistics,
watertightness, winding, positive volume, degenerate/duplicate triangles,
unreferenced vertices, dimensions and Z minimum. Do not silently repair at the
validation stage. A single solid is appropriate for a fused monochrome bust;
intentional multi-part assemblies need explicit per-part validation instead.

Self-intersection checks must name the checker and its limitations. PyMeshLab's
triangle selector can miss shared-edge/coplanar overlaps; zero selected faces
are not an exact-arithmetic proof. State when it was not run. Never describe
watertightness as synonymous with printable, or likeness as a topology metric.

Ground and uniformly size the approved geometry, then render it again if
normalization or repair could affect interpretation. Export STL in mm and
GLB in meters with correct axis conversion. Re-import **the exported files**
to verify scale, bounds, components and topology, rather than checking only
the working scene. Preserve the full-size editable `.blend` before creating a
smaller draft. Renders must show the mesh that was actually exported.

## Printer-specific gate

Record confirmed printer, nozzle, material, plate, print orientation and any
color/assembly choice. Distinguish confirmed settings from assumptions. An AMS
does not automatically turn a texture or sculpt into a multicolor print;
material boundaries or painting need an explicit user choice and extra work.

Use the locally installed slicer's actual profiles/API for its version.
Do not invent profile IDs or carry timing/filament estimates from a predecessor
whose geometry changed. Retain the command, complete resolved settings, input
mesh hash, slicer version, raw log, output files and estimates.

For an installed Bambu Studio CLI, useful lessons are:

- Resolve stock machine/process/filament inheritance and preserve stock system
  identity metadata. Relabeling a system profile as a user profile can break
  otherwise valid slicing. Do not edit the user's installed presets in place.
- Use a separate configuration directory. Use the host's supported network
  isolation for offline slicing; launching the normal UI is not proof of
  network isolation. Slicing must not connect to or submit to a printer.
- Check the current CLI help. Some builds prepend the output directory even
  to an absolute `--export-3mf` argument: use a basename with the explicit
  output-directory option when that behavior is verified.
- For a typical 0.4 mm PLA portrait test, 0.12 mm layers, 2 walls, 15% gyroid,
  automatic tree supports and a brim are starting choices—not universal
  approved settings. Thin features, contact gaps, overhang threshold and
  supports must match the actual model and machine. Do not assume support
  contacts must be build-plate-only.
- Inspect the raw log as well as the UI/plate warning field. A successful exit
  and empty summary can coexist with an internal tree-support warning. Record
  any reported fallback and inspect the affected adjacent toolpaths. Internal
  support-layer indices may differ from emitted G-code indices. A successful
  fallback is not evidence that a physical print has succeeded.

Verify actual layer/extrusion output. Inspect support contacts at chin, nose,
ear undersides, nape and rear bust/base edges; look for fragile high trees that
are only supporting a remnant that should have been sculpted away. Analyze
positive extrusion moves rather than travel moves. Arc endpoint plots are an
approximation, not a full overhang coverage or load-bearing proof.

Reopen/re-import a packaged 3MF without re-slicing where supported. Confirm
correct model count/height, editable geometry/settings, intended material
assignment and no unexplained automatic repairs. If it embeds G-code, compare
that member's hash with the checked external G-code. A GLB is a viewing copy,
not a substitute for a slicer-specific multicolor project.

## Handoff

Show the actual updated mesh and a same-light before/after when relevant.
Provide checked files, printer settings, estimated time/material, remaining
warnings and the local experiment-log location. A small draft can test likeness,
layer visibility and support removal before committing to a batch. Larger
prints may retain more facial detail. Do not claim exhaustive thickness or
overhang checking unless it was actually performed.

Separate these four outcomes explicitly: visual acceptance, valid mesh,
successful slice, successful physical print. Sending a print job requires
specific authorization beyond preparing a model or project.
