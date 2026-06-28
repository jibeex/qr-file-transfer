# ADR-003: Video Output Format (MP4 container, codec auto-selection)

**Date**: 2026-06-27  
**Status**: Accepted (revised 2026-06-28)  
**Decided by**: Product Owner / Tech Lead

---

## Context

The encoded QR animation must be saved as a video file that:
1. Plays on the source computer (to display for camera capture)
2. Can be transferred via USB/SD card
3. Preserves QR code clarity (no lossy compression artifacts that obscure modules)

**Clarification (2026-06-28)**: OpenCV's `mp4v` FourCC produces MPEG-4 Part 2, **not** H.264. True H.264 requires `avc1` (available natively on macOS via VideoToolbox, and on Linux/Windows when OpenCV is built with FFmpeg). Both are valid; the decision is which to default to and whether to support both.

## Options Considered

| Format | Pros | Cons |
|---|---|---|
| **MP4 (`mp4v`, MPEG-4 Part 2)** | Works with any OpenCV pip install; no extra deps | Slightly lower compatibility than H.264 on some players |
| **MP4 (`avc1`, H.264)** | Industry-standard; best player compatibility | Requires VideoToolbox (macOS) or FFmpeg backend (Linux/Windows) |
| MP4 (H.265/HEVC) | Better compression | Limited hardware support |
| AVI (MJPEG) | Lossless per-frame | Large files; limited player support |
| WebM (VP9) | Open codec | Poor Windows support without extra codecs |

## Decision

**MP4 container. Codec: auto-select with user override.**

- Default codec: `avc1` (H.264) — try first; best player compatibility
- Fallback codec: `mp4v` (MPEG-4 Part 2) — if `avc1` is unavailable on the current platform
- User override: `--codec [avc1|mp4v]` flag for explicit control
- All-keyframe encoding (no inter-frame compression) — ensures every frame is independently decodable
- High quality / high bitrate — preserves QR module clarity

Platform behavior:
- macOS: `avc1` works natively via VideoToolbox (OpenCV uses hardware H.264 encoder)
- Linux: `avc1` requires OpenCV+FFmpeg; `mp4v` is the safe fallback for standard pip install
- Windows: `avc1` works in most OpenCV builds; `mp4v` as fallback

Both codecs produce files playable in VLC, QuickTime, and Windows Media Player.

## Consequences

- **Good**: Best-effort H.264 output where supported; graceful MPEG-4 fallback elsewhere
- **Good**: Both formats playable on all major video players
- **Good**: `--codec` flag gives users explicit control
- **Bad**: Platform-dependent default behavior requires POC validation on all three OSes
- **Risk**: Must validate `avc1` availability during Week 0 POC; if unavailable, `mp4v` becomes the effective default

## Related

- REQUIREMENTS.md: DR-001, CON-004, NFR-013
- DESIGN.md §3.3 (Video Format Specification)
- ADR-001 (grid size affects frame dimensions)
