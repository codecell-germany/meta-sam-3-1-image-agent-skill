# Release checklist

## Repo hygiene

- no private images in Git
- no generated crops in Git
- no model weights in Git
- `Plans/` stays private
- `for_segmentation/` stays private
- `.venv/` stays private

## Public docs

- README is product-first and bilingual
- `skills/sam3-image-cli/SKILL.md` exists
- onboarding references exist
- known limitations are documented

## Runtime

- `sam3-cli --help` works
- `sam3-cli setup --language en` works
- `sam3-cli setup --language de` works
- `sam3-cli doctor` works
- overlap-filter path verified:
  - `sam3-cli image --overlap-filter outer --overlap-threshold 0.9 ...`
- `npm run test:unit` works
- `npm run test:release` works
- the installer creates `sam3-cli`, `sam3-cli.cmd`, and `sam3-cli.ps1`

## Platform verification

- macOS Apple Silicon image segmentation verified
- Windows/CUDA installation path at least documented and reviewed

## GitHub skill readiness

- `skills/sam3-image-cli/` is complete
- repository can be listed by `skills add owner/repo -l`
