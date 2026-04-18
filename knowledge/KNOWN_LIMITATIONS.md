# Known limitations

## Checkpoint access is gated

Meta SAM 3.1 weights are not bundled in this repository.
The user must have approved access to `facebook/sam3.1` on Hugging Face before checkpoint download succeeds.

## Apple Silicon uses a conservative default

On Apple Silicon, the stable default path is currently `cpu`.
The repository does not promise `mps` as a reliable production default for SAM 3.1 image segmentation.

## Video and multiplex are not the default product story here

This repository is positioned around image segmentation for downstream agent workflows.
Video and multiplex tracking remain CUDA-centric in the current upstream state.

## Checkpoint load warning

The SAM 3.1 image path can emit `missing_keys` warnings while still completing a successful image segmentation run.
This should be tracked and documented, but it is not the same as a hard runtime failure.

## Overlap filtering is CLI-level policy

`sam3-cli image --overlap-filter outer` is a deterministic post-filter for nested boxes.
It is not the same as generic upstream NMS:

- NMS usually keeps the higher-scored detection
- the CLI overlap filter intentionally keeps the larger outer box when containment is strong
