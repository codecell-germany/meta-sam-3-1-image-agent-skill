---
name: sam3-image-cli
description: "Use when an agent must reduce an image to the most relevant regions with Meta SAM 3.1, then continue with OCR or image analysis using overlays, bounding boxes, JSON metadata, and crops. Covers setup detection, platform-specific installation guidance for macOS Apple Silicon and Windows/CUDA, checkpoint download, and reliable image segmentation via the public `sam3-cli`."
---

# sam3-image-cli

## When to use

Use this skill when an agent should improve downstream image understanding by segmenting an image into the most relevant regions first.

Use it especially when the task benefits from:

- reducing visual noise before OCR
- isolating components or objects into separate crops
- turning an image into a JSON-documented set of regions
- comparing multiple segmentation runs without overwriting prior results
- working with Meta SAM 3.1 through a stable terminal flow instead of ad-hoc notebooks
- preparing cleaner downstream input for product lookup or replacement-part matching on Uni Elektro

## Preconditions

- Treat `sam3-cli` as the public product surface.
- First verify that it exists:
  - `sam3-cli --help`
- The skill payload can be installed through:
  - `sam3-image-skill install --force`
- If the repo-local wrapper is being used during development, the same command should still work from the repo root.
- Do not start with notebooks, hidden Python entry points, or direct model-builder calls when the CLI already supports the workflow.
- Meta SAM 3.1 requires approved access to the gated Hugging Face repo `facebook/sam3.1`.

## First-run detection

Run this before any real segmentation work:

```bash
sam3-cli doctor
```

Treat the environment as not ready if:

- `sam3-cli` is missing
- Python or PyTorch is missing
- the checkpoint has not been downloaded yet
- the user says this is the first setup
- the user is on macOS Apple Silicon and expects `mps` to be the default path

If setup is incomplete, switch into onboarding mode immediately.

## Onboarding mode

This is the correct first-run order:

1. Verify the public CLI:
   - `sam3-cli --help`
2. Detect the current environment:
   - `sam3-cli doctor`
3. If setup is incomplete, print the setup guide:
   - German: `sam3-cli setup --language de`
   - English: `sam3-cli setup --language en`
4. If the platform is known, prefer the explicit setup variant:
   - macOS Apple Silicon:
     `sam3-cli setup --platform macos-apple-silicon --language en|de`
   - Windows with CUDA:
     `sam3-cli setup --platform windows-cuda --language en|de`
5. Only then install the runtime and dependencies.
6. Download the model weights:
   - `sam3-cli download --version sam3.1`
7. Rerun:
   - `sam3-cli doctor`
8. Only then run real segmentation.

## Core workflow

1. Validate setup:
   - `sam3-cli doctor`
2. Make sure the checkpoint is available:
   - `sam3-cli download --version sam3.1`
3. Segment the image:
   - `sam3-cli image --version sam3.1 --device cpu --image /absolute/path/image.jpg --prompt "object of interest"`
   - if nested detections should be suppressed, use:
     `sam3-cli image ... --overlap-filter outer --overlap-threshold 0.9`
4. Continue with the generated outputs:
   - overlay PNG for quick inspection
   - JSON file for agentic routing and structured follow-up
   - crop directory for OCR, classification, or finer visual inspection
5. If the next step is product identification or replacement search on Uni Elektro:
   - use the companion skill `unielektro-suche`
   - prefer OCR or structured extraction from the crops first
   - then use the cleaned identifiers, names, article hints, or Hager candidates against the Uni-Elektro suggest API

## Platform rules

- On macOS Apple Silicon, `cpu` is currently the stable default path.
- Do not assume that `mps` is production-safe for SAM 3.1 image segmentation.
- On Windows with NVIDIA/CUDA, `cuda` is the preferred performance path.
- Do not present video or multiplex tracking as the standard path for Apple Silicon.

## Guardrails

- Never assume the checkpoint is available just because the repo is cloned.
- If checkpoint download fails with `401`, treat it as an access or authentication issue against the gated Hugging Face model.
- Do not overwrite previous result bundles on purpose unless the user explicitly asks for that.
- Prefer JSON plus crops over the overlay alone for any serious downstream workflow.
- If nested or almost fully contained detections should not survive, prefer `--overlap-filter outer`.
- Do not commit model weights, private images, or generated crops into Git.

## How to use the outputs

- Use the overlay PNG for quick human validation.
- Use the JSON file as the machine-readable source of truth.
- Use the crops when OCR or object-specific analysis should run on reduced image areas instead of the full original image.
- If the end goal is a Uni-Elektro product hit, run OCR or label extraction on the crops first and then hand the structured terms to `unielektro-suche`.
- When multiple runs exist, compare the distinct result bundles rather than reusing only the latest file name.

## References

- Main overview: `references/overview.md`
- Agent onboarding: `references/agent-onboarding.md`
- Command cheat sheet: `references/command-cheatsheet.md`
- macOS first run: `references/macos-first-run.md`
- Windows/CUDA first run: `references/windows-cuda-first-run.md`
- Output contract: `references/output-contract.md`
- Architecture notes: `knowledge/ARCHITECTURE.md`
- Platform support: `knowledge/PLATFORM_SUPPORT.md`
- Known limitations: `knowledge/KNOWN_LIMITATIONS.md`
- Release checklist: `knowledge/RELEASE_CHECKLIST.md`
