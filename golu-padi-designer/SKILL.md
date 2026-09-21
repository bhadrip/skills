---
name: golu-padi-designer
description: Design dimensioned modular Golu/Kolu/Bommai Golu display steps from PVC pipe, generate an editable Blender model, connector-aware BOM, inspection renders, and GLB export. Use when users want to plan, visualize, resize, or validate a stepped PVC festival display; do not present the result as structural certification.
---

# Golu Padi Designer

Create a buildable-looking, dimensionally explicit PVC step display while keeping tube cut lengths distinct from assembled spacing.

## Before building

Resolve or reasonably infer:

- number of steps;
- whether the supplied short/long dimensions are **tube cut lengths** or **assembled center-to-center pitches**;
- PVC nominal size, outside diameter, and wall thickness;
- fitting center-to-socket-stop distance;
- whether removable tread boards are wanted.

If the user intends physical fabrication and has not selected a fitting manufacturer/SKU, use clearly labeled generic fitting dimensions. State that the socket allowance must be replaced with measured SKU data before cutting. Never claim structural or load certification.

Read [references/dimensional-model.md](references/dimensional-model.md) when converting between cut lengths and assembled dimensions or reviewing connector requirements.

## Generate the model

Use Blender in background mode with `scripts/build_golu_padi.py`. The script accepts arguments after `--`:

```sh
blender --background --python scripts/build_golu_padi.py -- \
  --output-dir /absolute/path/to/output \
  --steps 4 \
  --dimension-mode cut \
  --short 12 \
  --long 36 \
  --socket-stop-offset 1
```

Use `--dimension-mode pitch` when the user's dimensions describe assembled center spacing. Add `--no-boards` only when the user wants a pipe-only frame. Run `--help` through Blender for all pipe geometry options.

The generated structure must route fittings from the actual incident pipe directions. Do not substitute planar crosses or tees at nodes that require ports on multiple axes.

## Validate and inspect

The generator writes an editable `.blend`, `.glb`, BOM, QA JSON, and four canonical renders. Inspect the perspective, side, front, and rear three-quarter renders before delivery.

Reopen the saved Blend and re-import the GLB:

```sh
blender --background /absolute/path/to/output/golu_padi_4step.blend \
  --python scripts/verify_exports.py -- \
  --output-dir /absolute/path/to/output --steps 4
```

Treat a successful command as incomplete until `qa_report.json` and `reopen_validation.json` both report `PASS` and the renders show every board, pipe, and fitting at the intended node.

## Deliver

Provide the `.blend`, GLB, BOM, QA files, and at least the perspective render. Summarize:

- cut lengths and assembled pitches;
- pipe and connector counts;
- assumed fitting allowance;
- overall bounding box;
- any manufacturer data still required before fabrication.
