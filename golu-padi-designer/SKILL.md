---
name: golu-padi-designer
description: Create or edit PVC Golu/Kolu/Bommai Golu step designs in Blender, or plan a build with a shopping list, optimized pipe cut plan, connector map, required tools, and tailored assembly instructions. Use for visual design changes and practical purchase/assembly planning; do not present the result as structural certification.
---

# Golu Padi Designer

Support exactly two capabilities. Use either one independently or both from the same design manifest.

## Capability 1 — Create or edit the Blender design

Use this mode when the user wants a new 3D design, changes to an existing Golu model, different step count or width, different boards/materials, or revised inspection renders.

Read [references/blender-editing.md](references/blender-editing.md) before editing an existing `.blend` or generated design.

For a new or dimensionally changed design, run Blender with the deterministic generator:

```shell
blender --background --python scripts/build_golu_padi.py -- \
  --output-dir /absolute/path/to/output \
  --steps 4 \
  --dimension-mode cut \
  --short 12 \
  --long 36 \
  --socket-stop-offset 1
```

For edits to a generated design, read its `design_manifest.json`, preserve the source, change only the requested parameters, and rebuild into a new versioned output directory. Use direct Blender edits for appearance or one-off geometry changes that are not represented by generator parameters; keep those edits in a new `.blend` and rerender all inspection views.

The generated structure must route fittings from the actual incident pipe directions. Do not substitute planar crosses or tees at nodes that require ports on multiple axes.

## Capability 2 — Plan purchases and assembly

Use this mode when the user wants help deciding dimensions, planning what to buy, calculating pipe stock and cuts, identifying tools, or following build instructions.

Read [references/procurement-and-assembly.md](references/procurement-and-assembly.md). Resolve or reasonably infer the step count, width meaning, rise/run, PVC size, fitting socket allowance, tread boards, purchasable stock length, and saw/cutter kerf.

The generated plan must include:

- `shopping_list.md` with PVC stock, fittings, boards, retention/safety supplies, and tools such as a correctly sized PVC cutter;
- `cut_plan.csv` packing the required cuts into the chosen stock length with kerf allowance;
- `bom.csv`, `connector_map.csv`, and level-specific `assembly_instructions.md`;
- explicit assumptions and manufacturer/SKU checks.

Only add current prices when the user requests pricing and provides or allows a location/vendor search. Keep price estimates separate from geometric quantities.

## Shared dimensional rules

Read [references/dimensional-model.md](references/dimensional-model.md) whenever converting between tube cuts, assembled center pitches, board width, or overall envelope.

Interpret “3 padi, 3 ft wide” or “5 padi, 5 ft wide” as an assembled center-to-center frame width unless the user explicitly means overall envelope, board width, or tube cut length. If the user says “use 3 ft pipes,” use cut mode. Always report both the interpretation and resulting overall bounding box.

If no fitting SKU is supplied, use clearly labeled generic dimensions and state that its socket allowance must be replaced with measured manufacturer data before cutting. Never claim structural, load, seismic, or child-safety certification.

## Validate both modes

Inspect all canonical renders. Reopen the saved `.blend`, re-import the GLB with `scripts/verify_exports.py`, and require both QA JSON files to report `PASS`. Confirm the design manifest, BOM, shopping list, cut plan, connector map, and assembly instructions agree on dimensions and quantities.

## Deliver

For Blender work, provide the edited `.blend`, GLB, and inspection renders. For planning work, provide the manifest, shopping list, cut plan, BOM, tools list, connector map, and assembly instructions. When both capabilities are used, deliver the complete set and summarize:

- cut lengths and assembled pitches;
- pipe and connector counts;
- assumed fitting allowance;
- overall bounding box;
- any manufacturer data still required before fabrication.
