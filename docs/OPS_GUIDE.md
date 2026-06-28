# Operations Guide

**Owner**: IT Operations  
**Status**: Draft  
**Review trigger**: Before each release; update when install steps or dependencies change

---

## Installation

### macOS

```bash
# System dependency (one-time)
brew install zbar

# Install qr-transfer
pip install qr-transfer

# Verify
qr-transfer --version
```

### Linux (Ubuntu/Debian)

```bash
# System dependency (one-time)
sudo apt-get install libzbar0

# Install qr-transfer
pip install qr-transfer

# Verify
qr-transfer --version
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install zbar

pip install qr-transfer
qr-transfer --version
```

### Windows

```bash
# No system dependencies required (pyzbar includes DLL)
pip install qr-transfer
qr-transfer --version
```

### Install in virtualenv (recommended)

```bash
python -m venv qr-env
source qr-env/bin/activate    # Windows: qr-env\Scripts\activate
pip install qr-transfer
```

---

## Environment Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| Python | 3.9 | 3.12+ |
| Display resolution | 1920×1080 | Retina/HiDPI |
| Display brightness | 80% | 100% |
| Camera | 1280×720 (720p) | 1920×1080+ (1080p) |
| Lighting | 300 lux | 500 lux |
| Camera distance | 20–40 cm | 30 cm |

---

## Basic Usage

```bash
# Encode a file
qr-transfer encode document.pdf output.mp4

# Play the video fullscreen on source system
# Record with phone camera at 20-40cm distance
# Transfer video file to destination via USB/SD card

# Decode on destination
qr-transfer decode recorded.mov document.pdf

# Verify before decoding
qr-transfer verify recorded.mov

# Inspect metadata
qr-transfer info output.mp4
```

---

## Troubleshooting

### Decode fails: "Missing N chunks"

1. **Re-record the video** — keep camera steady, perpendicular to screen
2. **Check lighting** — office lighting (300–700 lux); avoid direct sunlight glare
3. **Reduce grid size** — retry with `qr-transfer encode ... --grid-size 600` for better reliability
4. **Check distance** — optimal 20–40 cm between camera and display
5. **Verify video plays** — confirm the video file is not corrupted: open in VLC

### Decode fails: "Integrity check failed"

The file data was corrupted during decode. Do **not** use the output file.

1. Check the video file was not corrupted during USB transfer (copy again)
2. Re-record and retry

### Encoding is very slow

- Enable progress with `-v` to identify the bottleneck
- For already-compressed files (zip, jpg, mp4), add `--no-compress`
- Reduce grid size to decrease frame count: `--grid-size 600`

### `ImportError: Unable to find zbar shared library`

- macOS: `brew install zbar`
- Linux: `sudo apt-get install libzbar0`
- Then reinstall: `pip install --force-reinstall pyzbar`

### Permission denied on output file

```bash
# Check permissions
ls -l output_file

# Fix
chmod +w output_file
# or specify a different output path
```

### Out of disk space (exit code 8)

The encoder estimates required space before starting. Free disk space equal to at least `3×` the input file size before encoding.

---

## Security Operations

### After a sensitive transfer

Delete video files from both systems:

```bash
# Standard delete (sufficient for most use cases)
rm output.mp4 recorded.mov

# Secure overwrite (for high-security environments; note: not forensically secure on SSDs)
qr-transfer secure-delete output.mp4
```

### Air-gap compliance verification

Verify the tool makes no network calls:

```bash
# macOS/Linux — run while encoding, check for network traffic
sudo lsof -i -n -P | grep qr-transfer   # should return nothing
```

---

## Logging

By default, no persistent logs are written (NFR-018 — no telemetry).

Enable verbose output to stdout:
```bash
qr-transfer decode video.mp4 output.bin --verbose
```

Capture to file:
```bash
qr-transfer decode video.mp4 output.bin --verbose > transfer.log 2>&1
```
