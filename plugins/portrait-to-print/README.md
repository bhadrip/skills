# Portrait to Print

A local-first agent workflow for turning existing photographs into a recognizable
3D-printable portrait through **generation → bounded sculpting → visual review →
checked export → printer-specific slicing**. It can also start from an existing
mesh and refine a nose, smile, hairstyle or print defect without regenerating
the entire head.

This is a **workflow plugin plus executable helpers**, not a trained model or a
one-click likeness guarantee. Image-to-3D generation needs a separately installed
local backend and weights. Sculpting needs an agent with local shell/file access
and Blender or equivalent geometry tools. No paid service is required by this
plugin. No model weights, inference runtime, or personal portrait is bundled.

## Privacy boundary

**No real-person photos, masks, landmarks, facial measurements, portrait meshes,
renders, source filenames, personal experiment logs, or weights are included.**
Tests create only synthetic primitives/text in temporary directories outside
the repository. Private job data must stay outside the plugin and all source
repositories. The workspace initializer copies no input files and blocks
Git/plugin-tree destinations; a package-content test rejects binary/media/model
payloads. These safeguards complement, not replace, a manual staged-diff review.

The helpers do not use the network or submit prints. External generation/slicer
applications have their own behavior: offline environment flags are not an
OS firewall. Uploading source data or derivatives, downloading large model
assets, publishing a job or starting a printer requires its own authorization.

## Package and use

Version **0.1.0** includes the `portrait-to-print` skill and three local helpers.
The root `plugin.json` is the portable Agent Plugins manifest. The synchronized
`.codex-plugin/plugin.json` supports the repository's Codex-compatible packaging.
The repository also supplies `.agents/plugins/marketplace.json`, whose source
entry points to `./plugins/portrait-to-print`. Publishing this source does not
install or activate the plugin in a user's account.

An agent can read [the skill](skills/portrait-to-print/SKILL.md) directly, or the
`skills/portrait-to-print` directory can be used independently in a compatible
agent skill installation. The helpers and references live inside that directory
so the standalone skill does not depend on paths elsewhere in this repository.

Example requests:

> Use $portrait-to-print with my existing photographs. Keep everything local,
> record failed experiments, and aim for a recognizable birthday bust rather
> than an exact scan.

> Refine this mesh's hairstyle and nose. Show actual front and oblique renders
> before preparing a new print project. Preserve my previous version.

> Prepare the reviewed portrait for my printer. Verify units, topology and
> actual sliced supports, but do not send a print job.

## Local prerequisites

- Python 3.10+ for the helpers; NumPy, trimesh and SciPy for mesh checks.
- Blender 4.2+ API family for the review/export script; the included smoke test
  is tested on Blender 5.2. Other versions must pass the test before assuming
  compatibility.
- Optional PyMeshLab for the mesh helper's self-intersection selector.
- A separately installed local shape-generation runtime/checkpoint when no
  base mesh exists. See [local generation](skills/portrait-to-print/references/local-generation.md).
- A locally installed slicer and matching printer profiles for an actual 3MF/
  toolpath handoff. Slicing is guided by the skill, not bundled as a universal
  preset or printer-control integration.

Install Python dependencies in a dedicated environment using `requirements.txt`
from this plugin. Keep the environment outside the public source tree if practical.
No helper installs dependencies or downloads checkpoints automatically.

## Helpers

Run from the plugin directory. Replace the illustrative absolute paths with
private paths outside any Git checkout; all new output paths must be unused.

```sh
python3 skills/portrait-to-print/scripts/project_log.py init /absolute/private-job

python3 skills/portrait-to-print/scripts/project_log.py append /absolute/private-job \
  --id E001 --hypothesis 'A local tip correction may improve the profile' \
  --changed 'Tested a bounded regional edit against the unchanged baseline' \
  --observed 'No clear improvement in the two oblique reviews' \
  --decision reject --stop-reason 'Change the hypothesis; do not repeat the same edit'

python3 skills/portrait-to-print/scripts/project_log.py verify /absolute/private-job
```

The logger records append-only JSONL plus readable Markdown, parent links and
optional artifact/source hashes. Artifact files are referenced, never copied.
Hash chaining detects accidental record drift; it is not a cryptographic
signature against a person who can rewrite the whole directory. POSIX workspace
permissions are owner-only; Windows users must also check filesystem ACLs.

The mesh helper expects an already oriented STL in **millimeters, Z up**:

```sh
python3 skills/portrait-to-print/scripts/mesh_tools.py check \
  --input /absolute/private-job/candidates/reviewed.stl \
  --out /absolute/private-job/reports/mesh-check.json

python3 skills/portrait-to-print/scripts/mesh_tools.py prepare \
  --input /absolute/private-job/candidates/reviewed.stl \
  --out /absolute/private-job/selected/portrait-120mm.stl --height-mm 120
```

`prepare` only grounds and uniformly scales a valid solid, then checks the
re-imported output. It neither repairs nor sculpts. Use `--intersections` only
with PyMeshLab installed; its known shared-edge/coplanar blind spot is reported.

Blender review and export are intentionally separate:

```sh
blender --background --factory-startup --python-exit-code 7 \
  --python skills/portrait-to-print/scripts/blender_review.py -- \
  --source /absolute/private-job/selected/portrait-120mm.stl \
  --units mm --front-axis=-Y --out /absolute/private-job/review-01

# Inspect all six actual mesh renders first; this flag records your approval.
blender --background --factory-startup --python-exit-code 7 \
  --python skills/portrait-to-print/scripts/blender_review.py -- \
  --export --review /absolute/private-job/review-01 \
  --approve-reviewed-geometry --out /absolute/private-job/export-01
```

Review produces front, both obliques, profile, back and top PNGs, `review.blend`
and a hashed manifest. Imported geometry must already be Z-up; front direction
is explicit. The script centers XY and grounds Z but does not resize or repair.
GLB imports require `--units m`; Blender already applies their up-axis conversion.
For a changed candidate, add `--reference-review /absolute/private-job/review-01`
to its review command with a new output directory. This reuses the baseline's
placement matrix, all six cameras, image resolution and lighting: the candidate
is **not** independently recentered, grounded or zoomed. Its imported units and
front axis must match. Without this option, each new review auto-fits its own
geometry, so two independent runs are not an exact fixed-camera comparison.
Export checks the reviewed source/scene/images have not changed and produces
`portrait_mm.stl` and `portrait_m.glb`, with re-imported scale validation.
Use each helper's `--help` for options and failure conditions.

## Why the loop is bounded

The skill preserves source meshes, separates image conditioning from sculpting,
protects neighboring anatomy, and logs failed edit families. It includes
specific lessons about pinched nose tips, mouth shelves, corrugated hair,
misleading Portrait depth, failed topology smoothing, and support warnings.
Those lessons are generalized; no subject-specific masks or displacement
arrays are reusable or published.

Visual likeness, manifold geometry, successful slicing, and physical print
success are four different gates. The workflow never promotes one as proof of
the others. A physical sample and the user's recognition judgment remain
important before a larger batch.

## Tests

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tests/blender_smoke.py --blender /absolute/path/to/blender
```

Tests generate synthetic inputs only. No reference photographs or portrait
models are needed. The Blender smoke test is separate because Blender is an
external application, not a Python package. It verifies rendering/export
mechanics, not photographic likeness. Generation quality and physical printer
success are not claimed by these tests.

## License

MIT for this plugin's original code and instructions; see [LICENSE](LICENSE).
Blender, Hunyuan3D, model checkpoints, and other optional tools retain their
own licenses and hardware requirements. They are not redistributed here.
