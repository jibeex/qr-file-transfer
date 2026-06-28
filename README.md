# qr-file-transfer

Transfer files between air-gapped computers using animated QR codes — no network required.

```bash
qr-transfer encode document.pdf output.mp4
# play output.mp4 fullscreen → record with phone → copy via USB
qr-transfer decode recorded.mov document.pdf
```

---

## How it works

1. **Encode** — file is compressed, split into chunks, each chunk becomes a QR code frame in an MP4 video
2. **Display** — play the video fullscreen on the source system
3. **Capture** — record the screen with any 1080p camera (phone, webcam)
4. **Transfer** — move the video to the destination via USB or SD card
5. **Decode** — extract frames, decode QR codes, reconstruct file, verify SHA-256 integrity

Default throughput: **~640 KB/sec** (800×800 grid, 10 fps, iPhone 16 + Mac Retina)

---

## Install

```bash
# macOS
brew install zbar && pip install qr-transfer

# Linux
sudo apt-get install libzbar0 && pip install qr-transfer

# Windows
pip install qr-transfer
```

> **Note**: Not yet published to PyPI. Install from source until v1.0 release:
> ```bash
> git clone git@github.com:jibeex/qr-file-transfer.git && cd qr-file-transfer
> pip install -e ".[dev]"
> ```

Requires Python 3.9+.

---

## Usage

```bash
# Encode (default 800×800 grid, 10 fps)
qr-transfer encode file.zip output.mp4

# Encode with reduced grid size for older hardware
qr-transfer encode file.zip output.mp4 --grid-size 600

# Decode
qr-transfer decode recorded.mov file.zip

# Verify video before decoding
qr-transfer verify recorded.mov

# Inspect metadata
qr-transfer info output.mp4

# Help
qr-transfer --help
```

---

## Performance

| Grid size | Data/frame | Speed @ 10 fps | Use when |
|---|---|---|---|
| 177×177 | ~2.8 KB | 28 KB/sec | Maximum compatibility |
| 600×600 | ~36 KB | 360 KB/sec | Older cameras |
| **800×800** | **~64 KB** | **640 KB/sec** | **Default (iPhone 16 + Mac)** |
| 1000×1000 | ~100 KB | 1 MB/sec | Experimental |

---

## Requirements

- Source system: display ≥ 1920×1080, brightness 80–100%
- Camera: ≥ 1080p recommended (720p minimum with `--grid-size 600`)
- Distance: 20–40 cm from screen
- Lighting: 300–700 lux (normal office)

---

## Documentation

| Document | Purpose |
|---|---|
| [ROADMAP.md](./ROADMAP.md) | Implementation plan (phases, risk register) |
| [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md) | What the system must do (IEEE 29148) |
| [docs/DESIGN.md](./docs/DESIGN.md) | How it works (arc42 architecture) |
| [docs/adr/](./docs/adr/) | Architecture decisions (why each choice was made) |
| [docs/specs/cli-reference.md](./docs/specs/cli-reference.md) | All commands and exit codes |
| [docs/specs/data-protocol.md](./docs/specs/data-protocol.md) | Wire format (chunk binary + metadata JSON) |
| [docs/OPS_GUIDE.md](./docs/OPS_GUIDE.md) | Install, troubleshoot, operations |
| [docs/TEST_PLAN.md](./docs/TEST_PLAN.md) | Test strategy and acceptance criteria |
| [docs/GLOSSARY.md](./docs/GLOSSARY.md) | Term definitions |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Development setup and contribution guide |
| [SECURITY.md](./SECURITY.md) | Threat model and vulnerability reporting |

---

## Development

```bash
# Run tests (no hardware and no system dependencies needed)
PYTHONPATH=src pytest tests/ -q

# All 120 tests pass using software simulation — no iPhone, no libzbar required
```

---

## Status

**Implementation**: ✅ Complete — 15 source modules, 120 tests passing  
**Version**: 0.1.0 (pre-release, not yet on PyPI)  
**License**: [MIT](./LICENSE)
