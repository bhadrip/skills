# Dimensional and connector model

## Cut length versus assembled pitch

Let `C` be the tube cut length and `S` the fitting center-to-socket-stop distance at each end. The model uses:

`assembled center pitch = C + 2S`

Conversely, for a required assembled center pitch `P`:

`tube cut length = P - 2S`

Do not label the same dimension as both an exact tube cut and exact assembled pitch unless `S = 0`. Commercial fittings vary; measure the selected SKU.

## Stair grid

For `N` steps, the frame uses `N + 1` depth stations. Their maximum module heights are:

`1, 2, ..., N, N`

The script fills the volume beneath the stepped profile with:

- short vertical members between adjacent height nodes;
- short depth members between adjacent depth stations wherever both nodes exist;
- long width members joining the two side frames at every node elevation.

This produces a complete orthogonal lattice instead of the disconnected or under-supported geometry common in generated concept images.

## Connector routing

At each node, collect every incident direction from `+X`, `-X`, `+Y`, `-Y`, `+Z`, and `-Z`. The connector port count and orientation must exactly match that set. A connector with the correct number of ports but the wrong axes is still invalid.

The bundled model uses generic 3-, 4-, and 5-port furniture-style fitting envelopes. Actual part availability and socket geometry must be checked against a manufacturer catalog before fabrication.

## Scope

The output is suitable for visualization, dimension review, BOM planning, and discussion with a fabricator. It is not a calculation of PVC deflection, buckling, joint pullout, shelf capacity, seismic stability, or child safety.
