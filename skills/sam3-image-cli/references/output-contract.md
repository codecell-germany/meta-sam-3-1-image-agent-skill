# Output contract

Every successful `sam3-cli image` run is expected to produce a result bundle.

## Files

- overlay PNG
- JSON metadata file
- crop directory

## JSON fields

Top-level fields:

- `image`
- `prompt`
- `device`
- `checkpoint`
- `overlay`
- `crops_dir`
- `resolution`
- `threshold`
- `mask_threshold`
- `top_k`
- `crop_padding`
- `detections`

Per-detection fields:

- `index`
- `score`
- `bbox_xyxy`
- `bbox_wh`
- `crop_padding`
- `crop_path`
- `mask_pixels`

## Operational meaning

- Overlay is best for quick visual validation.
- JSON is the machine-readable source of truth.
- Crops are the preferred payload for OCR or component-level follow-up analysis.

## Non-overwrite behavior

If a result bundle with the same target name already exists, the CLI should create a new version with ` (1)`, ` (2)` and so on instead of overwriting prior results.
