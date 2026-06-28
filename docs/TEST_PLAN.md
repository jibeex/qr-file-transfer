# Test Design Specification

**Owner**: QA Lead  
**Status**: Draft — test cases defined; implementation pending POC  
**Review trigger**: Before each milestone; when REQUIREMENTS.md acceptance criteria change  
**Standard**: IEEE 829 / ISO 29119-3  
**Reference**: [REQUIREMENTS.md](./REQUIREMENTS.md), [DESIGN.md §9.6](./DESIGN.md)

---

## 1. Scope

Covers all requirements in REQUIREMENTS.md: functional (FR-001–FR-013), non-functional (NFR-001–NFR-024), data (DR-001–DR-003), interface (IR-001–IR-002), compliance (CR-001–CR-002), UI (UI-001–UI-008), and constraints (CON-001–CON-014).

**Out of scope**: GUI, mobile app, network testing, hardware procurement.

---

## 2. Test Environments

| Environment | Purpose | Hardware |
|---|---|---|
| Unit / CI | Fast isolated tests | Any Python 3.9+ machine |
| Integration | Full pipeline, no camera | Mac with display |
| E2E simulation | Encode → decode via synthetic video | Mac with display |
| Hardware acceptance | Real-world transfer | iPhone 16 + MacBook Pro 16" Retina, 300–700 lux, 30 cm |
| Cross-platform | OS compatibility | macOS 14+, Ubuntu 22.04, Windows 11 |

---

## 3. Requirements Traceability Matrix

Every requirement maps to at least one test. `UT` = unit test, `IT` = integration, `PT` = performance, `ST` = security, `CT` = CLI contract, `E2E` = end-to-end, `HW` = hardware acceptance, `MAN` = manual inspection.

### 3.1 Functional Requirements

| Req | Description | Test ID(s) | Layer |
|---|---|---|---|
| FR-001 | Encode any file type | IT-004, UT-ENC-001 | IT, UT |
| FR-002 | Simple encoding command | CT-001 | CT |
| FR-003 | Transfer speed targets | IT-002, IT-003, PT-001, PT-002 | IT, PT |
| FR-004 | Progress visibility | UT-PRG-001, CT-002 | UT, CT |
| FR-005 | Customizable grid size | UT-ENC-002, IT-009 | UT, IT |
| FR-006 | Decode video to file | IT-001–IT-004 | IT |
| FR-007 | Verify file integrity | IT-008, UT-INT-001 | IT, UT |
| FR-008 | Handle imperfect captures | IT-005, IT-006, IT-007, HW-001 | IT, HW |
| FR-009 | Clear error messages | CT-003, UT-ERR-001 | CT, UT |
| FR-010 | Report missing chunks | IT-005, UT-DEC-001 | IT, UT |
| FR-011 | Verify command | CT-004, IT-010 | CT, IT |
| FR-012 | Info command | CT-005 | CT |
| FR-013 | Help documentation | CT-006 | CT |

### 3.2 Non-Functional Requirements

| Req | Description | Test ID(s) | Layer |
|---|---|---|---|
| NFR-001 | ≥ 400 KB/s transfer rate | PT-001, PT-002 | PT |
| NFR-002 | Encode 10 MB in < 5s | PT-003 | PT |
| NFR-003 | < 1 GB RAM for 500 MB file | PT-004 | PT |
| NFR-004 | Startup < 2s | PT-005 | PT |
| NFR-005 | 100% data integrity | IT-001–IT-004, IT-008 | IT |
| NFR-006 | > 95% success rate | HW-001 | HW |
| NFR-007 | Graceful degradation | ST-002, IT-011 | ST, IT |
| NFR-008 | New user succeeds in < 5 min | MAN-001 | MAN |
| NFR-009 | Error messages Grade 8 reading | MAN-002 | MAN |
| NFR-010 | README covers common use cases | MAN-003 | MAN |
| NFR-011 | macOS, Linux, Windows | CT-007 (CI matrix) | CT |
| NFR-012 | Python 3.9+ | CT-007 (CI matrix) | CT |
| NFR-013 | Video playable on VLC/QT/WMP | IT-012 | IT |
| NFR-014 | Camera ≥ 720p | HW-001 | HW |
| NFR-015 | Cryptographic integrity | IT-008, UT-INT-001 | IT, UT |
| NFR-016 | Zero network access | ST-003 | ST |
| NFR-017 | Input validation | ST-001, UT-VAL-001 | ST, UT |
| NFR-018 | No telemetry | ST-003 | ST |
| NFR-023 | pip installable | CT-008 | CT |
| NFR-024 | Pinned dependencies | MAN-004 | MAN |

### 3.3 Data, Interface, Compliance, UI, Constraint Requirements

| Req | Test ID(s) | Layer |
|---|---|---|
| DR-001 (video format) | IT-012 | IT |
| DR-002 (metadata frame) | UT-META-001 | UT |
| DR-003 (chunking) | UT-CHK-001 | UT |
| IR-001 (POSIX CLI) | CT-001–CT-006 | CT |
| IR-002 (exit codes) | CT-009 | CT |
| CR-001 (GDPR anonymize) | CT-010, UT-META-002 | CT, UT |
| CR-002 (WCAG a11y) | MAN-005 | MAN |
| UI-001 encode cmd | CT-001 | CT |
| UI-002 decode cmd | CT-011 | CT |
| UI-003 verify cmd | CT-004 | CT |
| UI-004 info cmd | CT-005 | CT |
| UI-005–UI-007 progress/errors | UT-PRG-001, CT-002, CT-003 | UT, CT |
| UI-008 help | CT-006 | CT |
| CON-001 (1 GB file limit) | UT-VAL-002 | UT |
| CON-002 (grid 177–1000) | UT-VAL-003 | UT |
| CON-003 (fps 5–30) | UT-VAL-004 | UT |

---

## 4. Test Cases

### 4.1 Unit Tests (`tests/unit/`)

| Test ID | Given / When / Then | Requirement |
|---|---|---|
| UT-ENC-001 | File with `.bin`/`.pdf`/`.jpg` extension **when** encoded **then** no error, hash preserved | FR-001 |
| UT-ENC-002 | `FileEncoder(grid_size=600)` **when** encode **then** output QR images are 600×600 | FR-005 |
| UT-DEC-001 | Chunk dict missing indices 2,5,8 **when** `_verify_completeness` **then** returns `[2,5,8]` | FR-010 |
| UT-INT-001 | Random 1 KB bytes **when** compress→chunk→reconstruct→decompress **then** sha256 matches | FR-007, NFR-005 |
| UT-CHK-001 | Chunk with known data **when** `ChunkHeader.pack()` **then** magic=`QRFT`, header=20 bytes, CRC32 correct | DR-003 |
| UT-META-001 | `Metadata(file=…, transfer=…)` **when** `to_json()→from_json()` **then** all fields preserved | DR-002 |
| UT-META-002 | `--anonymize-metadata` flag **when** encode **then** `metadata.file.name == "anonymous"` | CR-001 |
| UT-VAL-001 | Path `../../etc/passwd` **when** `validate_file_path` **then** raises `SecurityError` | NFR-017 |
| UT-VAL-002 | File > 1 GB **when** `validate_input_file` **then** raises `ValidationError` with exit code 3 | CON-001 |
| UT-VAL-003 | `grid_size=176` or `grid_size=1001` **when** `validate_grid_size` **then** raises `ValidationError` | CON-002 |
| UT-VAL-004 | `fps=4` or `fps=31` **when** `validate_fps` **then** raises `ValidationError` | CON-003 |
| UT-PRG-001 | `ProgressTracker(total=10)` **when** `update(5)` **then** internal state = 50%; output contains `%` not color alone | FR-004, CR-002 |
| UT-ERR-001 | `FileNotFoundError` **when** `ErrorMessages.file_not_found(path)` **then** message contains path, actionable suggestion, no jargon | FR-009 |

### 4.2 Integration Tests (`tests/integration/`)

Full encode → decode without camera hardware. Video is generated by `encode`, then fed directly to `decode`.

| Test ID | Scenario | Pass Criteria | Requirement |
|---|---|---|---|
| IT-001 | Round-trip: 1 byte file | sha256 matches exactly | FR-006, NFR-005 |
| IT-002 | Round-trip: 1 MB random binary, 10 trials | avg ≤ 5.0s, no trial > 7s | FR-003, NFR-001 |
| IT-003 | Round-trip: 10 MB random binary, 5 trials | avg ≤ 30s, no trial > 40s | FR-003, NFR-001 |
| IT-004 | Round-trip: 20 different file types | all 20 succeed, hashes match | FR-001 |
| IT-005 | Decode with 5% frames removed from video | decoder reports missing chunk indices, no crash, exit code 5 | FR-008, FR-010 |
| IT-006 | Decode video with 10% duplicate frames | no chunk duplication, output identical to original | FR-008 |
| IT-007 | Decode video with 3 corrupted (unreadable) frames | those 3 skipped, remaining decoded, reports missing | FR-008 |
| IT-008 | Decode with 1 bit flipped in reconstructed data | exit code 6, no output file written | FR-007, NFR-005 |
| IT-009 | Encode with `--grid-size 400`, decode | round-trip succeeds with 400×400 QR codes | FR-005 |
| IT-010 | `verify` command on valid video | reports expected chunk count, exit code 0, completes < 5s | FR-011 |
| IT-011 | Feed 1000 malformed video files to decoder | no crash (exit code 1–255 only), no partial output | NFR-007 |
| IT-012 | Encoded video opened in VLC, QuickTime | file command identifies as MP4; plays without error | NFR-013, DR-001 |

### 4.3 Performance Tests (`tests/performance/`) — reference hardware only

| Test ID | Scenario | Pass Criteria | Requirement |
|---|---|---|---|
| PT-001 | 1 MB end-to-end, 10 trials | avg ≤ 5.0s, no trial > 7s | NFR-001, FR-003 |
| PT-002 | 10 MB end-to-end, 5 trials | avg ≤ 30s, no trial > 40s | NFR-001, FR-003 |
| PT-003 | Encode-only: 10 MB file | < 5 seconds | NFR-002 |
| PT-004 | Memory profiling: 500 MB file | peak RSS < 1 GB | NFR-003 |
| PT-005 | Time from CLI invocation to first output line | < 2 seconds | NFR-004 |

### 4.4 CLI Contract Tests (`tests/contract/`)

Invoked as subprocess. Assert exact exit codes and stdout/stderr routing per IR-001, IR-002.

| Test ID | Command | Expected exit code | Expected stream | Requirement |
|---|---|---|---|---|
| CT-001 | `encode <file> <out.mp4>` (valid) | 0 | stdout: progress; stderr: empty | FR-002, UI-001 |
| CT-002 | `encode <file> <out.mp4>` | stdout contains `%` progress during encode | stdout | FR-004, UI-005 |
| CT-003 | `encode missing.txt out.mp4` | 2 | stderr: `Cannot find`; stdout: empty | FR-009, IR-002 |
| CT-004 | `verify <valid video>` | 0 | stdout: chunk count + expected count | FR-011, UI-003 |
| CT-005 | `info <valid video>` | 0 | stdout: filename, size, grid, fps, timestamp | FR-012, UI-004 |
| CT-006 | `--help`, `-h`, `encode --help` | 0 | stdout: usage text | FR-013, UI-008 |
| CT-007 | Full test suite on Python 3.9, 3.10, 3.11, 3.12 × macOS/Ubuntu/Windows | all pass | — | NFR-011, NFR-012 |
| CT-008 | `pip install -e .` in fresh venv, then `qr-transfer --version` | 0 | stdout: version string | NFR-023 |
| CT-009 | All 8 error conditions triggered | exit codes 1–8 match IR-002 spec exactly | stderr | IR-002 |
| CT-010 | `encode <file> <out> --anonymize-metadata` then `info <out>` | 0 | stdout: filename = `anonymous` or absent | CR-001 |
| CT-011 | `decode <video> <out>` (valid) | 0 | stdout: progress + "✓ Decoded successfully" | FR-006, UI-002 |

### 4.5 Security Tests (`tests/security/`)

| Test ID | Scenario | Pass Criteria | Requirement |
|---|---|---|---|
| ST-001 | Path traversal inputs (`../etc/passwd`, null bytes, absolute paths) | `SecurityError` raised, no file access | NFR-017 |
| ST-002 | 1000 malformed video files (fuzz corpus) | no crash; exit code always in [1–255] | NFR-007 |
| ST-003 | Monitor network during `encode` + `decode` | zero outbound connections (`lsof -i` empty) | NFR-016, NFR-018 |
| ST-004 | Tampered file (single bit flip in payload, hash unchanged) | exit code 6; message: "integrity check failed" | NFR-015 |
| ST-005 | Disk full simulation during `decode` write | exit code 8; no partial output file; temp file cleaned up | NFR-007 |

### 4.6 End-to-End Suite (`tests/e2e/`)

Simulates the full user journey: encode → synthetic video file → decode. No physical camera; the QR video is generated by encode and fed directly to decode (IT-layer approach), but the scenarios map 1:1 to REQUIREMENTS.md use cases.

| Test ID | Use Case | Scenario | Pass Criteria |
|---|---|---|---|
| E2E-001 | UC-001: Config file transfer | 5 KB YAML → encode → decode | sha256 matches, `"Transfer successful"` output, exit 0 |
| E2E-002 | UC-002: Cryptographic key transfer | 1 KB binary key → encode with `--anonymize-metadata` → decode | sha256 matches; metadata contains no filename |
| E2E-003 | UC-003: Document package | 10 MB PDF → encode → decode (verify < 30s) | sha256 matches, transfer time ≤ 30s |
| E2E-004 | UC-004: Emergency credential | Encode → introduce 3% frame corruption → decode | Decoder reports missing chunks, exit code 5, clear recovery message |

These four scenarios are the acceptance gate: **all must pass before v1.0 release**.

### 4.7 Hardware Acceptance Tests (manual, reference hardware)

Per REQUIREMENTS.MD NFR-006 acceptance test:
- 100 transfers of 10 MB file
- 5 different operators, 2 office environments (300–700 lux)
- iPhone 16 camera, MacBook Pro 16" Retina display, 30 cm distance
- Pass: ≥ 95 successful decodes with 100% data integrity

### 4.8 Manual Inspection Tests

| Test ID | What to verify | Requirement |
|---|---|---|
| MAN-001 | New user installs and completes first transfer in < 5 min | NFR-008 |
| MAN-002 | All error messages pass Flesch-Kincaid Grade 8 readability tool | NFR-009 |
| MAN-003 | README covers encode, decode, verify, troubleshoot without gaps | NFR-010 |
| MAN-004 | `pyproject.toml` has upper-bound pins on all deps | NFR-024 |
| MAN-005 | CLI output tested with VoiceOver (macOS); no color-only indicators; `--help` at Grade 8 | CR-002 |

---

## 5. Test Data

| Dataset | Size | Format | Used by |
|---|---|---|---|
| `random_1b.bin` | 1 byte | Binary | IT-001, UT-ENC-001 |
| `random_1kb.bin` | 1 KB | Binary | E2E-002 |
| `random_1mb.bin` | 1 MB | Binary | IT-002, PT-001 |
| `random_10mb.bin` | 10 MB | Binary | IT-003, PT-002, HW-001 |
| `config_5kb.yaml` | 5 KB | YAML | E2E-001 |
| `document_10mb.pdf` | 10 MB | PDF | E2E-003 |
| `text_sample.txt` | 50 KB | Text | UT-ENC-001 |
| `photo_sample.jpg` | 2 MB | JPEG | UT-ENC-001 |
| `malformed/*.mp4` | Various | Corrupted | ST-002, IT-011 |
| 20-type suite | Varied | Mixed | IT-004 |

All binary test files generated deterministically with `secrets.token_bytes(n)` and fixed seed for reproducibility.

---

## 6. CI Pipeline

```yaml
# .github/workflows/ci.yml  (to be created)
jobs:
  unit:          # runs on every commit — pytest tests/unit/
  integration:   # runs on every commit — pytest tests/integration/
  contract:      # runs on every commit — pytest tests/contract/
  security:      # runs weekly and on release — pytest tests/security/
  cross-platform:  # matrix: [ubuntu, macos, windows] × [py3.9, py3.10, py3.11, py3.12]
  performance:   # runs on release branch only — requires reference hardware or self-hosted runner
```

---

## 7. Open Items

- [ ] Establish baseline measurements during Week 0 POC (see REQUIREMENTS.md §9.3)
- [ ] Acquire reference hardware (iPhone 16) for PT and HW tests
- [ ] Create fuzz corpus of malformed videos for ST-002/IT-011
- [ ] Set up CI pipeline (`.github/workflows/ci.yml`)
- [ ] Add cross-platform matrix to CI (CT-007)
