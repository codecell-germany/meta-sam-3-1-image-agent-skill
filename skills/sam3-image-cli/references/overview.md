# sam3-image-cli overview

`sam3-image-cli` gives an agent a stable terminal-first way to use Meta SAM 3.1 for image reduction and region extraction.

The main value is not only the segmentation itself.
The real value is that the CLI turns one complex image into a structured result bundle that later tools and agents can process much more accurately.

## What the CLI is for

Use it to:

- reduce large or cluttered images to the most relevant regions
- generate crops that can be fed into OCR or visual classification
- preserve a structured JSON description of detections
- compare multiple segmentation runs without overwriting earlier output

## Public CLI surface

- `sam3-cli setup --language en|de [--platform ...]`
- `sam3-cli doctor`
- `sam3-cli download --version sam3.1`
- `sam3-cli image --version sam3.1 --image <path> --prompt <text>`

## What it produces

Each image run produces a result bundle:

- an overlay PNG
- a JSON file
- a crop directory

The JSON and crops are the most useful downstream artifacts for agents.

## Platform model

- macOS Apple Silicon:
  stable image segmentation path via `cpu`
- Windows with NVIDIA/CUDA:
  preferred performance path via `cuda`

## Important operational truth

Meta SAM 3.1 code can run locally, but the official model weights do not live in this Git repo.
The agent still needs approved access to the gated Hugging Face model `facebook/sam3.1` before checkpoint download works.
