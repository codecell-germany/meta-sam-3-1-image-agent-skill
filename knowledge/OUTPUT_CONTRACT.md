# Output contract

The CLI is useful because it creates a stable output contract instead of just a visual overlay.

## Bundle layout

For each successful `sam3-cli image` run:

- one overlay image is written
- one JSON file is written
- one crop directory is written

For machine callers:

- `sam3-cli image --json-only ...` keeps stdout reserved for the final result JSON
- upstream or model-loading chatter is redirected to stderr in that mode
- if `--overlap-filter outer` is active, the JSON also records which detections were removed

## Why the bundle matters

- the overlay helps a human validate the run quickly
- the JSON preserves the detections in a stable structured form
- the crops let later OCR or image-analysis tools work on reduced image regions
- if the next step is Uni-Elektro product matching, the crops are also the preferred source before handing structured search terms to `unielektro-suche`
- nested-box removal is explicit and inspectable through `removed_detections`

## Downstream recommendation

When another agent continues the workflow, prefer this order:

1. inspect the JSON
2. use the crops as primary visual inputs
3. fall back to the overlay only for quick visual confirmation
