# Platform support

## Verified path

### macOS Apple Silicon

Verified locally:

- Python 3.12 virtual environment
- PyTorch 2.10.0
- `torchvision 0.25.0`
- Meta SAM 3.1 image segmentation
- stable execution via `cpu`
- result bundle with overlay, JSON, and crops

Important rule:

- `cpu` is the stable default path on Apple Silicon

## Intended path

### Windows with NVIDIA/CUDA

Target support:

- Python 3.12
- CUDA-enabled PyTorch
- Meta SAM 3.1 image segmentation via `cuda`
- `npx` installer creates `sam3-cli.cmd` and `sam3-cli.ps1` in addition to the POSIX shim

This path follows Meta's documented CUDA-first direction and should be the preferred performance mode once verified on a real Windows/CUDA machine.

## Not part of the default promise

- video segmentation as the normal path for Apple Silicon
- SAM 3.1 multiplex video on macOS
- `mps` as a reliable production default
