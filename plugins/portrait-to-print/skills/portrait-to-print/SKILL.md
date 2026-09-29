---
name: portrait-to-print
description: Create or refine a locally generated portrait bust from existing photographs using a bounded sculpt-render-review loop, an experiment ledger, and validated 3D-print exports. Use for photo-to-face/head/bust projects and portrait print preparation, not generic CAD, biometric measurement, model training, or automatic printer submission.
---

# Portrait to Print

Produce a recognizable sculptural portrait, not a claim of an exact scan.
Work from the user's existing photographs and strongest accepted mesh. A paid
service, new photographs, a learned critic, or a freshly trained model is not a
default prerequisite. This plugin provides workflow and geometry helpers; it
does not bundle an image-to-3D model or guarantee likeness.

## Start from the actual state

1. Establish the requested deliverable: head, bust, figurine or relief; likeness
   tolerance; expression/hairstyle changes; deadline; physical size and printer.
   Reuse known answers. Label nozzle/material/plate assumptions if unconfirmed.
2. Inspect the existing experiment ledger, accepted/rejected meshes, source
   photos and actual multi-angle renders. Do not restart generation merely
   because a new model or tool is available.
3. Discover local runtimes and cached weights before installing or downloading
   anything. Read [local-generation.md](references/local-generation.md) when a
   base mesh is still needed. Read [sculpt-loop.md](references/sculpt-loop.md)
   before changing facial geometry or hairstyle.
4. Keep a private job directory **outside this plugin and source repositories**.
   Use `scripts/project_log.py init --help` to create it without copying photos.
   Photographs, derivatives, masks, landmarks, facial measurements, geometry,
   renders, private filenames, hashes and logs belong there—not in a release.
   Run inference locally. Do not upload inputs or derivatives, publish a job,
   pay for a service, or send a printer job without separate user authorization.

## The working loop

- Preserve the accepted source and its content hash. Record axes and units;
  STL has no units, and GLB import may already apply the Y-up/Z-up conversion.
- State **one visible hypothesis**: for example, lower-tip pinching, lip
  overfullness, or a hairstyle with no deliberate comb direction. Compare with
  actual front and oblique photographs, not an invented clay reference.
- Make a staged, regional change with protected neighboring anatomy. Test a
  baseline and two meaningfully different strengths when useful—not an endless
  grid of barely distinguishable variants.
- Render the same front, both obliques, profile and back views; add top for hair
  and a close-up for the edited region. Inspect real mesh renders with fixed
  cameras/material/lighting and no photographic texture. A separately labeled
  soft-light control may reveal lighting artifacts, but cannot substitute for
  the same-light comparison.
  With the included Blender helper, pass `--reference-review BASELINE_DIRECTORY`
  for variants to retain the baseline placement matrix and camera framing.
  Independent auto-fit runs are not an exact paired-camera comparison.
- Keep a change only when it visibly improves the whole head without damaging
  another view. Metrics constrain regressions; they do not certify recognition.
  Preserve the user's authority over likeness and artistic taste.
- Append what changed, what happened, why it was accepted/rejected and the next
  stopping condition using `scripts/project_log.py append --help`. Keep failed
  attempts. After two unhelpful variants of a hypothesis, reconsider the
  mechanism or stop that branch instead of shrinking the parameter indefinitely.
  A numeric retry budget is a practical default, not permission for unrelated
  work or a requirement to abandon a clearly useful correction.
- Give brief progress updates during long work. At a visual milestone, show
  actual previews. Once the requested result passes review, stop sculpting and
  prepare the handoff; do not reopen the entire likeness problem.

## Prepare, review, then export

Read [print-handoff.md](references/print-handoff.md) for mesh repairs, unit
conversion, slicing and physical-test limitations. Helpers are deliberately
separate so a valid mesh cannot silently become an approved portrait:

- `scripts/mesh_tools.py check`: read-only topology and scale report.
- `scripts/mesh_tools.py prepare`: ground and uniformly resize an already
  oriented, valid STL, export and re-import. It does not repair or sculpt.
- `scripts/blender_review.py`: fixed neutral views and editable `.blend`;
  separate explicit export after review, with STL/GLB scale checks. Run its
  `--help` through Blender for the current interface.
- `scripts/project_log.py`: private workspace and append-only experiment log.

Use each script's `--help`; retain reports beside the private artifacts. New
outputs must not overwrite an accepted checkpoint. A failed check is evidence,
not an invitation to lower its threshold. If a broad anatomical mask includes
intentionally removed hair, preserve the original failing figures, locate the
outliers in the render, and justify any refined region explicitly.

Hand off the actual mesh preview, editable scene, checked geometry, and any
printer-specific project that was really sliced. Separate **visual acceptance,
topology validity, successful slicing and physical print success**. State what
was not tested. Read [failure-patterns.md](references/failure-patterns.md) before
repeating a stalled experiment family.
