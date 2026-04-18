# Architecture

This repository combines three layers:

1. Meta's upstream SAM 3.1 codebase and model implementation
2. a hardened local CLI surface in `sam3_cli.py` plus the `sam3-cli` wrapper
3. an agent-facing skill payload in `skills/sam3-image-cli/`

The product idea is simple:

- segment the image locally with Meta SAM 3.1
- convert the raw model output into stable downstream artifacts
- teach agents to use those artifacts instead of operating on the full image every time

## Current public surface

- CLI:
  `sam3-cli`
- Skill:
  `skills/sam3-image-cli/`

## Main runtime flow

1. `sam3-cli doctor` inspects the local runtime.
2. `sam3-cli download --version sam3.1` ensures the checkpoint exists.
3. `sam3-cli image ...` builds the model, applies text-prompt segmentation, and writes the output bundle.

The image command can now also apply a CLI-level overlap filter for nested detections:

- `--overlap-filter outer`
- `--overlap-threshold 0.9`

This path is intentionally deterministic for agent workflows that want to keep the larger outer region instead of relying only on raw model score suppression.

## Why this matters for agents

Agents often do better when a large image is reduced into smaller, semantically relevant regions.
This repository turns Meta SAM 3.1 into that reduction layer.
