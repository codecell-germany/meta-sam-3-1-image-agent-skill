# sam3-image-cli command cheat sheet

## Verify the CLI

```bash
sam3-cli --help
```

## Show setup guidance

```bash
sam3-cli setup --language de
sam3-cli setup --language en
sam3-cli setup --platform macos-apple-silicon --language de
sam3-cli setup --platform windows-cuda --language en
```

## Check the environment

```bash
sam3-cli doctor
```

## Download the model weights

```bash
sam3-cli download --version sam3.1
```

## Minimal image segmentation

```bash
sam3-cli image --version sam3.1 --device cpu --image /absolute/path/image.jpg --prompt "object of interest"
```

## More controlled image segmentation

```bash
sam3-cli image \
  --version sam3.1 \
  --device cpu \
  --threshold 0.5 \
  --mask-threshold 0.5 \
  --resolution 1008 \
  --top-k 0 \
  --crop-padding 5 \
  --overlap-filter outer \
  --overlap-threshold 0.9 \
  --alpha 120 \
  --image /absolute/path/image.jpg \
  --prompt "object of interest"
```

## Important parameters

- `--device cpu|cuda|mps|auto`
- `--threshold`
- `--mask-threshold`
- `--resolution`
- `--top-k`
- `--crop-padding`
- `--overlap-filter off|outer`
- `--overlap-threshold`
- `--alpha`
- `--checkpoint`
- `--json-only`
