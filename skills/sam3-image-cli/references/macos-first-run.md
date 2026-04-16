# macOS Apple Silicon first run

Use this guide for Macs with Apple Silicon.

## Goal

Set up a stable local Meta-SAM-3.1 image segmentation path for agent workflows.

## Important rule

Use `cpu` as the default execution device.
Do not treat `mps` as the standard production path yet.

## Recommended order

```bash
git clone https://github.com/codecell-germany/meta-sam-3-1-image-agent-skill.git
cd meta-sam-3-1-image-agent-skill
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install torch==2.10.0 torchvision==0.25.0
pip install -e .
pip install einops
sam3-cli doctor
sam3-cli download --version sam3.1
sam3-cli image --version sam3.1 --device cpu --image /absolute/path/image.jpg --prompt "object of interest"
```

## If checkpoint download fails

- confirm the user has access to the gated Hugging Face model `facebook/sam3.1`
- confirm the current shell is authenticated
- if the error is `401`, treat it as an access issue first
