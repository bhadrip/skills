# Procurement and assembly planning

## Inputs

Resolve the step count, dimensional interpretation, PVC specifications, socket-stop distance, tread requirements, stock length, and cut kerf. Defaults must be disclosed. The generator defaults to 10-foot straight stock and a conservative 0.125-inch allowance per cut.

## Shopping plan

The shopping list must separate:

- straight PVC stock quantities and nominal/actual diameter;
- multi-axis fittings by exact port count and orientation map;
- tread boards and retention hardware;
- anti-tip hardware and optional joining consumables;
- tools already owned versus items that must be purchased.

The tools section should include a ratcheting PVC cutter rated for the modeled outside diameter or a fine-tooth saw and miter box, deburring/chamfering tool, tape measure, marker, labels, framing square, level, rubber mallet, tapping block, safety glasses, work gloves, and clamps or a helper.

Do not recommend solvent cement for furniture fittings unless the selected manufacturer permits it.

## Cut plan

The bundled generator uses deterministic dynamic programming to minimize the number of equal-length stock pipes for the two required cut lengths. Each planned cut consumes its finished length plus the configured kerf allowance. Treat the result as a conservative purchase estimate and preserve useful remnants. Reject a plan when the longest cut plus kerf exceeds the chosen stock length.

## Assembly plan

Instructions must come from the same node graph as the Blender model. Build H0 first, then H1 through HN, square the completed frame, and add boards last. Every connector is labeled by side, depth station, and height level and must match both port count and port axes.

Quantities in the shopping list, BOM, cut plan, connector map, and assembly guide must reconcile before delivery.
