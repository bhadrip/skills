# Four-step PVC Golu padi — corrected 3D model

This Blender model corrects the impossible connector logic in the supplied concept image. Every fitting is generated from the actual pipe directions that meet at that node, including the required multi-axis 4-port and 5-port junctions.

## Dimensional interpretation

- Short tube cut: **12.000 in**
- Long tube cut: **36.000 in**
- Pipe: nominal **1-1/2 in Schedule 40 PVC** (1.900 in OD, 0.145 in wall)
- Generic assumed fitting center-to-socket-stop offset: **1.000 in per end**
- Resulting assembled short pitch: **14.000 in**
- Resulting assembled width pitch: **38.000 in**

The distinction matters: a 12-inch cut tube inserted into two fittings does not produce a 12-inch assembled center-to-center step. The fitting allowance in this model is deliberately a top-level parameter in `build_pvc_golu_padi.py`.

## Deliverables

- `pvc_golu_padi_4step.blend` — editable, organized Blender source
- `pvc_golu_padi_4step.glb` — portable model export
- `build_pvc_golu_padi.py` — deterministic rebuild script
- `bom.csv` — modeled bill of materials
- `qa_report.json` — dimensional and object-count checks
- `reopen_validation.json` — saved Blend reopen and GLB re-import checks
- `renders/` — perspective, side, front, and rear three-quarter inspection views

## Important fabrication note

The connector bodies are accurate to the declared generic envelope, not to a specific commercial fitting. Before buying or cutting material, choose a manufacturer/SKU and replace the socket-stop offset and connector envelope with its measured dimensions. This model is a dimensioned visualization, not structural/load certification.

Rebuild with Blender 5.2+ from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python golu-padi-designer/scripts/build_golu_padi.py -- \
  --output-dir ./golu-padi-output --steps 4 \
  --dimension-mode cut --short 12 --long 36 --socket-stop-offset 1
```
