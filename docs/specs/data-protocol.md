# Wire Format Specification

**Owner**: Development Team  
**Review trigger**: When protocol version changes (breaking change = new ADR required)  
**Current protocol version**: `1.0.0` (magic `QRFT`)

---

## 1. Chunk Binary Format

Every data frame in the QR video encodes exactly one chunk.

```
┌──────────────────────────────────────────────────────┐
│ Header (20 bytes)                                    │
├──────────────────────────────────────────────────────┤
│ Magic       4 bytes  0x51524654  ("QRFT")            │
│ Version     1 byte   0x01                            │
│ Chunk Index 4 bytes  uint32, big-endian, 0-based     │
│ Total Chunks 4 bytes uint32, big-endian              │
│ Data Length 2 bytes  uint16, big-endian (max 2800)   │
│ CRC32       4 bytes  uint32, big-endian (data only)  │
│ Reserved    1 byte   0x00                            │
├──────────────────────────────────────────────────────┤
│ Data (variable, max 2800 bytes)                      │
└──────────────────────────────────────────────────────┘

struct format: '>4sBIIHIB'
Total max chunk size: 20 + 2800 = 2820 bytes
```

**Field details**

| Field | Offset | Size | Description |
|---|---|---|---|
| Magic | 0 | 4 | Identifies QR transfer data; reject frames without this |
| Version | 4 | 1 | Protocol version; `0x01` for v1.0 |
| Chunk Index | 5 | 4 | Zero-based position of this chunk |
| Total Chunks | 9 | 4 | Total expected chunks for this transfer |
| Data Length | 13 | 2 | Byte count of the data payload |
| CRC32 | 15 | 4 | CRC32 of data payload only (not header) |
| Reserved | 19 | 1 | Set to `0x00`; reserved for future use |
| Data | 20 | ≤2800 | Raw payload (compressed file data slice) |

**Integrity rules**

1. Reject if magic ≠ `QRFT`
2. Reject if version ≠ `0x01` (unknown version)
3. Reject if `len(data) != data_length`
4. Reject if `crc32(data) != header.crc32`

---

## 2. Metadata Frame Format

The first frame in every QR video is a metadata frame. It is encoded as a JSON string (UTF-8), **not** as a binary chunk.

```json
{
  "version": "1.0.0",
  "type": "metadata",
  "file": {
    "name": "document.pdf",
    "size": 1048576,
    "hash": "sha256:e3b0c44298fc1c149afbf4c8996fb924...",
    "compressed": true,
    "compression_ratio": 0.74
  },
  "transfer": {
    "total_chunks": 375,
    "chunk_size": 2800,
    "grid_size": 800,
    "fps": 10,
    "timestamp": "2026-06-28T10:00:00Z"
  }
}
```

**Field semantics**

| Field | Type | Description |
|---|---|---|
| `version` | string | Protocol version matching chunk header version |
| `type` | string | Always `"metadata"` for the first frame |
| `file.name` | string | Original filename (may be anonymized with `--anonymize-metadata`) |
| `file.size` | integer | Original uncompressed file size in bytes |
| `file.hash` | string | `"sha256:<hex>"` of the original **uncompressed** file |
| `file.compressed` | boolean | Whether gzip compression was applied |
| `file.compression_ratio` | float | `compressed_size / original_size`; 1.0 if not compressed |
| `transfer.total_chunks` | integer | Expected chunk count; decoder fails if this count is not reached |
| `transfer.chunk_size` | integer | Max bytes per chunk payload (default 2800) |
| `transfer.grid_size` | integer | QR module count per side used for encoding |
| `transfer.fps` | integer | Video frame rate used for encoding |
| `transfer.timestamp` | string | ISO 8601 UTC timestamp of encoding time |

**Identification rule**: A QR frame is a metadata frame if its decoded content is valid JSON with `"type": "metadata"`. All other successfully decoded frames are treated as binary chunks.

---

## 3. Frame Ordering

```
Frame 0:  metadata frame (JSON)
Frame 1:  chunk index 0
Frame 2:  chunk index 1
  ...
Frame N:  chunk index N-1
```

The decoder **does not rely on frame order**. It identifies each frame type by content:
- JSON with `type=metadata` → metadata frame
- Binary with magic `QRFT` → data chunk at `chunk_index`

Duplicate chunks (same index) are deduplicated; the first valid occurrence is kept.

---

## 4. Protocol Versioning

| Version | Status | Notes |
|---|---|---|
| `1.0.0` | Current | Initial protocol |

Breaking changes (new magic, new header layout, incompatible metadata schema) require a new ADR and a version bump. Non-breaking additions (new optional metadata fields) may be made without a new ADR.
