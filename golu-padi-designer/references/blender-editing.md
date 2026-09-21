# Blender create/edit mode

## Generated designs

Treat `design_manifest.json` as the source of dimensional intent and the `.blend` as the editable visual artifact. For structural changes such as step count, width, rise/run, pipe size, or board inclusion:

1. Read the manifest and existing QA report.
2. Preserve the original output directory.
3. Rerun `scripts/build_golu_padi.py` with the existing values plus the requested overrides into a new versioned directory.
4. Inspect all four renders and run `scripts/verify_exports.py` against the new output.
5. Compare the new manifest and BOM with the old ones and explain the material impact.

This rebuild approach prevents stale fittings, BOM entries, connector maps, or assembly steps when the frame topology changes.

## Direct Blender edits

Use direct Blender edits for material, color, lighting, camera, annotation, board profile, decorative treatment, or one-off geometry not represented by generator parameters. Work on a copy and record reproducible changes in a project-local script when they are substantial.

Do not directly stretch pipe meshes to represent a dimensional change. That leaves cut lengths, sockets, fittings, and planning artifacts inconsistent; rebuild parametrically instead.

## Existing non-generated files

Inspect units, axes, object names, collections, modifiers, cameras, and bounding boxes before editing. Never assume an arbitrary file follows the generated naming scheme. Save a new file and retain the original.
