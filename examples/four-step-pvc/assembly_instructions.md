# Assembly instructions — 4-padi PVC Golu display

These instructions are generated from the same node graph as the Blender model and BOM.

## Design summary

- Levels: **4 padi**
- Width requirement: **36 in width-tube cuts producing a 38 in center pitch**
- Rise/run requirement: **12 in short-tube cuts producing a 14 in rise/run pitch**
- Exact short tube cut: **12 in**
- Exact width tube cut: **36 in**
- Assumed fitting center-to-socket-stop distance: **1 in per end**
- Modeled overall bounding box: **58.56 × 40.56 × 59.41 in** (depth × width × height)

## Parts to prepare

- **56** short PVC members at **12 in**: 28 depth rails and 28 verticals
- **19** width PVC members at **36 in**
- **14** generic multi-axis **3-port** fittings
- **12** generic multi-axis **4-port** fittings
- **12** generic multi-axis **5-port** fittings
- **4** removable tread boards at **40 × 13.25 × 0.75 in**

## Labeling system

- Mark depth stations **D0** at the front through **D4** at the rear.
- Mark height levels **H0** at the floor through **H4** at the top.
- `L` and `R` are the model's negative-Y and positive-Y side frames.
- Label each fitting by side, station, and height—for example, `L-D2-H1`.
- Use `connector_map.csv` to orient every fitting. Port count alone is insufficient; the port axes must also match.

## Assembly sequence

1. **Cut, deburr, and label all members.** Keep short depth rails, short verticals, and width members in separate bundles. Mark the socket insertion depth from the selected fitting manufacturer on every tube end.

2. **Dry-build the H0 base.** On both L and R sides, connect D0 through D4 with 8 short depth rails total. Join the two sides with 5 width members at D0 through D4. Keep every joint unglued and only hand-tight at this stage.

3. **Add level H1.**
   - Install **10 short vertical members** at stations D0 through D4, counting both sides.
   - Install **8 short depth rails** across bays D0–D1, D1–D2, D2–D3, D3–D4 on the L and R sides.
   - Bridge L to R with **5 width members** at H1, stations D0 through D4.
   - Match each H1 fitting to its exact row in `connector_map.csv`; check that every unused-looking port is actually absent, not merely hidden or rotated away.

4. **Add level H2.**
   - Install **8 short vertical members** at stations D1 through D4, counting both sides.
   - Install **6 short depth rails** across bays D1–D2, D2–D3, D3–D4 on the L and R sides.
   - Bridge L to R with **4 width members** at H2, stations D1 through D4.
   - Match each H2 fitting to its exact row in `connector_map.csv`; check that every unused-looking port is actually absent, not merely hidden or rotated away.

5. **Add level H3.**
   - Install **6 short vertical members** at stations D2 through D4, counting both sides.
   - Install **4 short depth rails** across bays D2–D3, D3–D4 on the L and R sides.
   - Bridge L to R with **3 width members** at H3, stations D2 through D4.
   - Match each H3 fitting to its exact row in `connector_map.csv`; check that every unused-looking port is actually absent, not merely hidden or rotated away.

6. **Add level H4.**
   - Install **4 short vertical members** at stations D3 through D4, counting both sides.
   - Install **2 short depth rails** across bays D3–D4 on the L and R sides.
   - Bridge L to R with **2 width members** at H4, stations D3 through D4.
   - Match each H4 fitting to its exact row in `connector_map.csv`; check that every unused-looking port is actually absent, not merely hidden or rotated away.

7. **Square and seat the frame.** Place it on a flat floor. Measure both base diagonals and adjust until equal. Seat every tube to the same insertion-depth mark, then recheck plumb, level, and all diagonals.

8. **Install the tread boards only after the frame is square.**
   - Board 1: place over bay D0–D1 at height H1.
   - Board 2: place over bay D1–D2 at height H2.
   - Board 3: place over bay D2–D3 at height H3.
   - Board 4: place over bay D3–D4 at height H4.
   - Use removable straps/clips or the user's chosen fastening system; the model does not assume screws through PVC.

9. **Final check before loading.** Confirm every connector orientation against the map, every joint insertion mark, board retention, floor contact, and anti-tip restraint. Follow the chosen fitting manufacturer's joining instructions; do not solvent-weld furniture fittings unless the manufacturer permits it.

## Important limitations

- The fitting envelope and socket offset are generic until replaced with manufacturer/SKU measurements.
- This guide is an assembly plan derived from geometry, not structural, load, seismic, or child-safety certification.
- Dry-fit the complete frame before making any irreversible joint.
