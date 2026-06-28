# ADR-001: Default QR Grid Size

**Date**: 2026-06-27  
**Status**: Accepted  
**Decided by**: Tech Lead

---

## Context

The QR grid size (number of modules per side) determines how much data fits in one frame and therefore the overall transfer speed. A larger grid size means more data per frame but requires higher camera resolution to decode reliably.

The primary target hardware is iPhone 16 camera + Mac Retina display.

Standard QR codes (ISO/IEC 18004) max out at 177×177 (Version 40), yielding ~2.8 KB/frame. This is insufficient for practical transfer speeds.

## Options Considered

| Grid Size | Data/Frame | Speed @ 10fps | Trade-off |
|---|---|---|---|
| 177×177 (standard max) | ~2.8 KB | 28 KB/sec | Maximum compatibility, very slow |
| 600×600 | ~36 KB | 360 KB/sec | Balanced |
| **800×800** | **~64 KB** | **640 KB/sec** | Optimal for iPhone 16 + Mac |
| 1000×1000 | ~100 KB | 1 MB/sec | Fast but reliability unvalidated |

## Decision

**Default grid size: 800×800 modules.**

800×800 is approximately 20× the standard QR maximum, achieves ~640 KB/sec at 10fps, and is validated (via hardware testing assumption ASM-007) as reliably decodable by iPhone 16 at 20–40cm distance.

## Consequences

- **Good**: ~640 KB/sec effective transfer rate exceeds the 400 KB/sec requirement (NFR-001)
- **Good**: Configurable via `--grid-size` flag for users with older hardware
- **Bad**: Non-standard; requires custom QR library configuration (not ISO/IEC 18004 compliant above Version 40)
- **Risk**: ASM-007 and ASM-008 must be validated by POC testing before implementation begins

## Related

- REQUIREMENTS.md: NFR-001, CON-002, ASM-007, ASM-008, ASM-010
- ADR-003 (video format), ADR-005 (integrity algorithm)
