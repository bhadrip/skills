# Regional sculpting that changes the relevant shape

## Start with a concrete observation

Inspect original photos and fixed mesh views side by side. Distinguish camera,
expression, lighting and surface geometry. Prioritize head silhouette and
feature relationships before fine skin texture. A mesh can be manifold while
having the wrong facial character.

Use project-local Blender/Open3D/PyMeshLab or an equivalent available local
geometry tool. Reuse an installed automation skill when available, but do not
assume a particular plugin, bridge, machine path or optional paid tool exists.
An editable local mesh is required; an image-generator mockup is not a 3D edit.

## Regional operations

- **Nose:** compare tip fullness, underside/columella, alar width and profile
  projection independently. For a pinched tip, test bounded dome rounding and
  restrained underside lift before shortening the entire bridge. Dark photo
  nostrils do not justify arbitrary deep holes. Lock the smile and eyes.
- **Mouth:** shape upper/lower lip volume and curvature, not only posterior
  translation. Uniform setbacks can leave horizontal shelves. Preserve the
  seam and naturally full lips; repeated smoothing can erase identity.
- **Smile:** lift corners with compatible cheek/lip deformation. A closed-mouth
  smile is often simpler to print than invented teeth and an open cavity.
  Label this as artistic expression, not reconstruction of an unobserved smile.
- **Eyes:** adjust aperture/rim geometry relative to the photos, preserving
  canthi and neighboring anatomy. Do not keep enlarging eyes to compensate for
  missing iris contrast in a monochrome sculpture. Avoid floating iris discs
  or disconnected generic eyeballs as an automatic fix.
- **Combed hair:** use a coherent scalp mass, modest part and a few separately
  curved broad locks with deliberate flow, tapered sides/nape and a readable
  fringe. Scale their relief and width to the selected print size/nozzle.
  Periodic ripples around an angular coordinate tend to make a corrugated cap;
  radial relief can become a crown starburst. Neither is a combed hairstyle.
  Protect the actual pinna, not an oversized box that also protects bad hair.

Set the target shape and local coordinate frame from the current subject.
Do not reuse a previous person's landmark positions, masks, dimensions or
displacement arrays. No such biometric data is bundled with this plugin.

## Integrate without mixing incompatible sources

If edits are represented as displacement arrays, store the source mesh hash,
vertex count/order hash, active region and maximum move. Combine only when
hashes/order match and overlaps are either absent or explicitly reconciled.
After any remesh, those indices are invalid: do not add an old displacement
array to the new topology. Preserve intermediate checkpoints.

When a final voxel stitch is needed, choose a resolution meaningfully smaller
than the smallest intentional printable feature. Measure before/after surface
distances in protected regions and inspect silhouette and facial detail.
Exact vertex preservation is not always the goal, but no hidden whole-face
smoothing or undocumented topology replacement is acceptable.

## Repair the mechanism, not just the shading

If local smoothing does not remove a hair ring, torn web or hanging strip:

1. Locate it in actual 3D coordinates by ray picking/projected inspection.
   Verify whether it lies outside the edit mask or inside an ear protection
   mask. Do not keep guessing a coordinate boundary from the image.
2. Inspect its topology. Vertex projection can collapse a handle onto a surface
   while retaining folded triangles, an attached cavity or self-overlap.
3. For a small corrupted region, fit a smooth replacement from its intact
   surrounding annulus, excluding the corrupted center. A **closed volumetric
   patch** with a feathered transition may be needed to replace the shell;
   surface fairing alone cannot reliably remove topology.
4. Keep the operation local. Recheck ears, face and the untouched crown. If the
   join leaves a visible circular seam, one narrow seam-fairing pass after
   topology replacement is more relevant than another hairstyle overhaul.
5. Verify the exported surface, not just the boolean operation's return code.
   If it still fails, retain the failed control and change the mechanism or
   report the limitation. Never call a defect removed while it is still visible.

Remove disconnected components only under an explicit semantic/size rule;
report counts, size/volume and retain the pre-removal mesh. An ear or accessory
is not debris merely because it is not the largest component.

## Acceptance boundary

Review front, both obliques, profile, back and top; inspect feature close-ups
without losing the whole-head judgment. Avoid a photorealistic texture that
makes an incorrect underlying printable face look convincing.

Preserve original mask statistics even when a supposedly anatomical region
includes deliberately removed hair. Locate outliers, justify the new semantic
region and report both sets. Do not change a threshold merely to turn red into
green. A clean regional pass still requires a visual check and, eventually,
the user's judgment of resemblance.
