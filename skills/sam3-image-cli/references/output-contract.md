# Output contract

Every successful `sam3-cli image` run is expected to produce a result bundle.

## Files

- overlay PNG
- JSON metadata file
- crop directory

## Machine mode

- `sam3-cli image --json-only ...` is the preferred contract for wrappers and other CLIs.
- In that mode stdout is reserved for the final result JSON.
- Progress or loader chatter is redirected to stderr.

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
- `overlap_filter`
- `overlap_threshold`
- `detections_before_filters`
- `removed_detections`
- `detections`

Per-detection fields:

- `index`
- `score`
- `bbox_xyxy`
- `bbox_wh`
- `crop_padding`
- `crop_path`
- `mask_pixels`

Removed-detection fields:

- `removed_index`
- `kept_index`
- `relation`
- `overlap_ratio_of_smaller`

## Operational meaning

- Overlay is best for quick visual validation.
- JSON is the machine-readable source of truth.
- Crops are the preferred payload for OCR or component-level follow-up analysis.
- If the next step is Uni-Elektro product matching, crops should be the preferred extraction source before handing terms to `unielektro-suche`.

## Non-overwrite behavior

If a result bundle with the same target name already exists, the CLI should create a new version with ` (1)`, ` (2)` and so on instead of overwriting prior results.
