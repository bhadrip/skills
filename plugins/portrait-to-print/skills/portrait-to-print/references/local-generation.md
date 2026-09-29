# Local generation: obtain a useful foundation

## Choose the source rather than restarting blindly

An accepted local head is usually a better start for a small nose/hair request
than a new generation. When the whole face remains visibly wrong, more tiny
deformations of the same restricted identity space can waste time. Test a
different complete-head foundation once, with a concrete comparison, instead
of polishing indefinitely.

Inventory the GPU/backend, available memory, local repositories, environment
and cached checkpoint. Keep weights and third-party runtimes outside this
plugin and outside public source control. Download/setup is a separate step;
respect its license, size and the user's offline/network constraints. No model
weights or third-party inference implementation is redistributed here.

## Real multiview inputs

Prefer a clear front view plus genuinely different oblique/profile views of
the same person. Keep originals immutable, use alpha mattes/cutouts to reduce
background confusion, and document the crop and view assignment privately.
Removing food, occluders or background must not replace facial anatomy with a
generated guess. Do not remove interior light features as if they were background.

Check the model's expected views and coordinate conventions. A left/right slot
may expect canonical profiles rather than arbitrary camera angles. An oblique
photo can be a useful controlled experiment, but is not a calibrated profile.
Do not invent a rear photo to satisfy an optional view slot. Do not insert a
generated clay portrait between the real photos and the geometry unless the
user deliberately wants that stylization and accepts the identity drift.

## A proven backend family, not a bundled dependency

The local Hunyuan3D-2 multiview shape pipeline is a practical starting candidate.
Its official sources are [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)
and [the 2mv checkpoint](https://huggingface.co/tencent/Hunyuan3D-2mv).
Inspect the installed revision/API rather than copying commands from a different
runtime: PyTorch multiview and MLX single-view implementations are not interchangeable.

For the official Python shape API, an already installed/cached environment can
use `Hunyuan3DDiTFlowMatchingPipeline` with `image` keyed by supported view names
such as `front`, `left` and `right`, then request `output_type="trimesh"`.
Load an explicit local configuration and safetensors checkpoint with the
installed `from_single_file` API when available. Never silently fall back from
a missing local weight to a network model identifier. Optional conditioner
assets must also already be cached for offline execution.

Set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` and
`HF_HUB_DISABLE_TELEMETRY=1` before importing the runtime. These are application
settings, not an operating-system network sandbox. If strict offline execution
is required, use the host's supported network-denial mechanism as well and
record whether it was actually applied. Do not claim all dependencies are
network-isolated merely because the flags are set.

An illustrative multiview quality configuration is 50 inference steps,
octree resolution 512 and chunk size 8000, with a fixed recorded seed and an
appropriate backend/dtype. These are starting parameters, not universal memory
or quality guarantees. MPS/float16 has worked in a compatible installation;
validate runtime support on the current machine. No unrequested training,
texture/PBR stage, CUDA extension rebuild or large seed sweep is necessary.

Record the repository revision, checkpoint/config hashes, inputs, view mapping,
seed, steps, octree, chunks, dtype/device, quantization, measured wall time and
peak memory if available. Check for missing model keys, incomplete inference,
empty/non-finite geometry and errors. Successful inference is not likeness.

If uncertain whether extra photographs help, run one same-checkpoint,
same-seed front-only control versus the available multiview condition. Judge
untextured whole-head views, not a scalar identity score alone. Keep the
winning raw mesh unchanged before cleaning it.

## Portrait depth and geometry uncertainty

HEIC Portrait disparity, portrait mattes and front TrueDepth are different
data products. Inspect actual image metadata/auxiliary data instead of inferring
the camera from AirDrop or Portrait mode. Relative disparity may support broad
form but does not establish metric depth or fine nostril/eyelid anatomy.
Do not invert it and call the result an accurate facial scan.

Casual photographs with subject motion are not a rigid calibrated
photogrammetry orbit. If cross-view registration fails, record that evidence
and use the images as sculpting constraints rather than repeating fusion with
the same assumptions. Unseen back-of-head geometry remains inferred.
