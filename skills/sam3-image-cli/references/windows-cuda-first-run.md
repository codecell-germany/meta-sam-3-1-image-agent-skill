# Windows CUDA first run

Use this guide for Windows machines with NVIDIA GPUs.

## Goal

Set up the preferred high-performance Meta-SAM-3.1 image segmentation path.

## Recommended order

```powershell
git clone https://github.com/codecell-germany/meta-sam-3-1-image-agent-skill.git
cd meta-sam-3-1-image-agent-skill
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -e .
pip install einops
sam3-cli doctor
sam3-cli download --version sam3.1
sam3-cli image --version sam3.1 --device cuda --image C:\absolute\path\image.jpg --prompt "object of interest"
```

## Expectations

- `cuda` should be the preferred execution device
- the model weights still come from the gated Hugging Face repo
- the result bundle should still be overlay + JSON + crops
