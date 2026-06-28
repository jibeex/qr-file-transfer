# ADR-008: QR Code Generation Library (qrcode)

**Date**: 2026-06-28  
**Status**: Accepted  
**Decided by**: Tech Lead

---

## Context

The encoder needs to generate QR code images from binary chunk data at custom grid sizes up to 1000×1000 modules. The library must support `pip install` with no compiled extensions and allow control over error correction level, border size, and output as a PIL Image.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **qrcode** | Pure Python; pip-installable; PIL Image output; well-maintained | Slower than C-based alternatives |
| segno | Faster; more output formats | Less community usage; less proven at non-standard sizes |
| python-qrcode | Alias for qrcode | Same library |
| zxing-cpp bindings | Fastest | Requires compiled C extension; complex install |

## Decision

**`qrcode[pil]`** — pure Python, pip-installable, PIL Image output.

Matches the project's constraint that all dependencies install via `pip` with no compiled extensions required (except OpenCV which provides precompiled wheels). The slower speed is acceptable: QR generation is parallelised in §6.4, and encoding 10 MB meets NFR-002 (< 5s) with parallel generation.

## Consequences

- **Good**: `pip install qrcode[pil]` — no system dependencies
- **Good**: Returns `PIL.Image` directly, compatible with OpenCV frame pipeline
- **Bad**: Slower per-QR than C-based libs; mitigated by multiprocessing (§6.4)
- **Risk**: ASM-010 (supports grids up to 1000×1000) must be validated in POC

## Related

- REQUIREMENTS.md: CON-002, ASM-010
- DESIGN.md §2.3 (QRGenerator), ADR-001 (default grid size)
