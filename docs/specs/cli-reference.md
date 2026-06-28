# CLI Reference

**Owner**: Development Team  
**Review trigger**: When any command, flag, or exit code changes  
**Conforms to**: POSIX conventions (IR-001), exit codes (IR-002)

---

## Commands

### `qr-transfer encode`

```
qr-transfer encode <input_file> <output_video> [OPTIONS]
```

Encodes a file into a QR code video.

**Arguments**

| Argument | Required | Description |
|---|---|---|
| `input_file` | ✅ | Path to the file to encode |
| `output_video` | ✅ | Path for the output video file |

**Options**

| Flag | Default | Range | Description |
|---|---|---|---|
| `-g`, `--grid-size SIZE` | `800` | 177–1000 | QR code grid size in modules |
| `-f`, `--fps RATE` | `10` | 5–30 | Video frame rate |
| `--no-compress` | off | — | Skip gzip compression |
| `--anonymize-metadata` | off | — | Strip filename from metadata frame |
| `-q`, `--quiet` | off | — | Suppress all progress output |
| `-v`, `--verbose` | off | — | Enable verbose debug logging |
| `-h`, `--help` | — | — | Show this help |

**Examples**

```bash
qr-transfer encode document.pdf output.mp4
qr-transfer encode file.zip output.mp4 --grid-size 600
qr-transfer encode secret.key output.mp4 --anonymize-metadata
qr-transfer encode large.bin output.mp4 --no-compress --fps 15
```

---

### `qr-transfer decode`

```
qr-transfer decode <input_video> <output_file> [OPTIONS]
```

Decodes a QR video back to the original file.

**Arguments**

| Argument | Required | Description |
|---|---|---|
| `input_video` | ✅ | Path to the recorded video |
| `output_file` | ✅ | Path for the decoded output file |

**Options**

| Flag | Default | Description |
|---|---|---|
| `--force` | off | Overwrite `output_file` if it already exists |
| `--partial` | off | Write partial file even if some chunks are missing |
| `-q`, `--quiet` | off | Suppress all progress output |
| `-v`, `--verbose` | off | Enable verbose debug logging |
| `-h`, `--help` | — | Show this help |

**Examples**

```bash
qr-transfer decode recorded.mov document.pdf
qr-transfer decode video.mp4 output.bin --force
qr-transfer decode video.mp4 output.bin --partial --verbose
```

---

### `qr-transfer verify`

```
qr-transfer verify <input_video> [OPTIONS]
```

Verifies a QR video without decoding. Checks metadata frame and chunk count. Completes in < 5 seconds for any video size.

**Arguments**

| Argument | Required | Description |
|---|---|---|
| `input_video` | ✅ | Path to the QR video to verify |

**Options**

| Flag | Default | Description |
|---|---|---|
| `-d`, `--detailed` | off | Show per-chunk information |
| `-h`, `--help` | — | Show this help |

**Examples**

```bash
qr-transfer verify output.mp4
qr-transfer verify output.mp4 --detailed
```

---

### `qr-transfer info`

```
qr-transfer info <input_video>
```

Displays metadata embedded in a QR video: original filename, file size, grid size, frame count, estimated transfer time, creation timestamp.

**Examples**

```bash
qr-transfer info output.mp4
```

---

### `qr-transfer secure-delete`

```
qr-transfer secure-delete <file> [<file> ...]
```

Overwrites file contents with random data before deleting. Use after sensitive transfers to prevent recovery of video files containing plaintext data.

> Note: Not forensically secure on SSDs (wear leveling); better than standard delete for most environments.

**Examples**

```bash
qr-transfer secure-delete output.mp4 recorded.mov
```

---

## Exit Codes

| Code | Constant | Meaning |
|---|---|---|
| `0` | `ERROR_SUCCESS` | Operation completed successfully |
| `1` | `ERROR_GENERAL` | Unspecified error |
| `2` | `ERROR_FILE_NOT_FOUND` | Input file or video not found |
| `3` | `ERROR_INVALID_INPUT` | Invalid parameter or argument |
| `4` | `ERROR_ENCODING_FAILED` | Encoding pipeline error |
| `5` | `ERROR_DECODING_FAILED` | Decoding pipeline error |
| `6` | `ERROR_INTEGRITY_FAILED` | SHA-256 hash mismatch |
| `7` | `ERROR_PERMISSION_DENIED` | Cannot read/write file |
| `8` | `ERROR_DISK_SPACE` | Insufficient disk space |

---

## Output Streams

- **stdout**: Normal output (progress, results, metadata display)
- **stderr**: Error messages only

Scripts should redirect stderr separately when capturing output:

```bash
qr-transfer decode video.mp4 output.bin 2>error.log
```
