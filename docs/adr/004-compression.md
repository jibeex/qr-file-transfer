# ADR-004: Data Compression (gzip, Level 6)

**Date**: 2026-06-27  
**Status**: Accepted  
**Decided by**: Product Owner

---

## Context

Before chunking and QR encoding, the file can optionally be compressed to reduce the number of QR frames needed and improve transfer speed. Compression adds encoding/decoding time but reduces total frame count.

## Options Considered

| Option | Ratio | Speed | Notes |
|---|---|---|---|
| None | 1.0× | Fastest | No CPU overhead; worst for compressible files |
| **gzip level 6** | ~1.3–2×  | Fast | Built-in Python stdlib; balanced default |
| gzip level 9 | ~1.35–2.1× | Slow | Marginal gain over level 6; notable CPU cost |
| zstd | ~1.4–2.5× | Very fast | Better ratio + speed but requires external dependency |
| lzma/xz | ~1.5–3× | Very slow | Best ratio; unacceptable latency for large files |

## Decision

**gzip compression enabled by default at level 6. Disable via `--no-compress` flag.**

Rationale:
- Python `gzip` stdlib — zero additional dependencies
- Level 6 is Python's documented balanced default (speed/ratio)
- Typical 20–40% reduction on text/config files reduces frame count proportionally
- Binary/already-compressed files (zip, jpg, mp4) see minimal benefit; `--no-compress` available

## Consequences

- **Good**: Reduces frame count and transfer time for typical use cases (config files, PDFs, source code)
- **Good**: No extra dependencies
- **Bad**: Adds latency for large already-compressed files (workaround: `--no-compress`)
- **Bad**: Compression is applied to the whole file in memory; not streaming-compatible for v1.0

## Related

- REQUIREMENTS.md: NFR-002, OQ-005 (compression level — resolved by this ADR)
- DESIGN.md §2.7 (CompressionUtil)
- ADR-005 (integrity algorithm — hash computed pre/post-compression)
