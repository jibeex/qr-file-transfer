# Test Plan

**Owner**: QA Lead  
**Status**: Draft — awaiting POC completion  
**Review trigger**: Before each milestone; update when acceptance criteria change  
**Reference**: REQUIREMENTS.md acceptance criteria

---

## 1. Scope

This plan covers functional, non-functional, and security testing for the QR File Transfer CLI (`qr-transfer`).

**In scope**: encode, decode, verify, info commands; integrity, performance, error handling, security  
**Out of scope**: GUI (future), mobile app (future), network testing (system has no network access)

---

## 2. Test Environments

| Environment | Purpose | Hardware |
|---|---|---|
| Unit / CI | Fast isolated tests | Any Python 3.9+ machine |
| Integration | End-to-end pipeline | Mac with display |
| Hardware acceptance | Real-world transfer | iPhone 16 + MacBook Pro 16" Retina |
| Cross-platform | OS compatibility | macOS, Ubuntu 22.04, Windows 11 |

**Reference hardware** (for performance tests): iPhone 16, MacBook Pro 16" Retina, office lighting 300–700 lux, 30cm camera distance.

---

## 3. Test Categories

### 3.1 Unit Tests (`tests/unit/`)

- Component isolation with mocked dependencies
- Target: ≥ 80% code coverage
- Execution time: < 30 seconds total

Key areas: `ChunkHeader.pack/unpack`, `IntegrityUtil.sha256/crc32`, `CompressionUtil.compress/decompress`, `InputValidator.*`, `ErrorMessages.*`

### 3.2 Integration Tests (`tests/integration/`)

Full encode → decode pipeline without hardware.

| Test ID | Description | Pass Criteria |
|---|---|---|
| IT-001 | Round-trip: 1 byte file | Hash matches exactly |
| IT-002 | Round-trip: 1 MB random binary | Hash matches, time < 5s |
| IT-003 | Round-trip: 10 MB file | Hash matches, time < 30s |
| IT-004 | Round-trip: 20 file types | All 20 succeed |
| IT-005 | Decode with 5% frames removed | Reports missing chunks, no crash |
| IT-006 | Decode duplicate frames | No chunk duplication in output |
| IT-007 | Decode corrupted frame | Skip frame, continue |
| IT-008 | Integrity mismatch injected | Exit code 6, no output file written |

### 3.3 Performance Tests (`tests/performance/`)

Run on reference hardware. See REQUIREMENTS.md AC-003-1 and AC-003-2.

| Test ID | Description | Pass Criteria |
|---|---|---|
| PT-001 | 1 MB end-to-end, 10 trials | Average ≤ 5.0s, no trial > 7s |
| PT-002 | 10 MB end-to-end, 5 trials | Average ≤ 30s, no trial > 40s |
| PT-003 | Encoding 10 MB file | < 5 seconds (NFR-002) |
| PT-004 | Memory usage, 500 MB file | Peak RAM < 1 GB (NFR-003) |
| PT-005 | Startup time | First output < 2s (NFR-004) |

### 3.4 Security Tests (`tests/security/`)

| Test ID | Description | Pass Criteria |
|---|---|---|
| ST-001 | Path traversal inputs | `SecurityError` raised, no file access |
| ST-002 | 1000 malformed videos (fuzz) | No crash, exit code 1–255, no data written |
| ST-003 | Network monitoring during operation | Zero outbound connections |
| ST-004 | Tampered file (flipped bit) | Exit code 6, clear error message |
| ST-005 | Disk full during write | Exit code 8, no partial output |

### 3.5 Hardware Acceptance Tests

Manual tests on reference hardware (see REQUIREMENTS.md NFR-006).

- 100 transfers of 10 MB file
- 5 different operators, 2 office environments
- Pass: ≥ 95 successful decodes with 100% data integrity

---

## 4. Test Data

| Dataset | Size | Format | Purpose |
|---|---|---|---|
| `random_1b.bin` | 1 byte | Binary | Boundary case |
| `random_1kb.bin` | 1 KB | Binary | Small file |
| `random_1mb.bin` | 1 MB | Binary | Performance baseline |
| `random_10mb.bin` | 10 MB | Binary | Acceptance criterion |
| `text_sample.txt` | 50 KB | Text | Compression test |
| `photo_sample.jpg` | 2 MB | JPEG | Already-compressed file |
| `malformed/*.mp4` | Various | Corrupted | Fuzz/error injection |

---

## 5. Open Items

- [ ] Establish baseline measurements (POC phase — see REQUIREMENTS.md §9.3)
- [ ] Acquire reference hardware (iPhone 16)
- [ ] Define CI pipeline (GitHub Actions)
- [ ] Add cross-platform test matrix to CI
