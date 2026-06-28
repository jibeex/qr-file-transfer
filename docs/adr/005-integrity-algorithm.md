# ADR-005: Integrity Verification (SHA-256 + CRC32)

**Date**: 2026-06-28  
**Status**: Accepted  
**Decided by**: Security Lead

---

## Context

Data integrity is critical (NFR-005: 100% accuracy, zero tolerance). The system must detect both accidental corruption and deliberate tampering. Two levels of checking are needed:

1. **File level**: Verify the complete reconstructed file matches the original
2. **Chunk level**: Detect corrupted individual chunks during decoding

## Options Considered

### File-level integrity

| Algorithm | Security | Performance | Notes |
|---|---|---|---|
| MD5 | ❌ Broken | Fast | Collision-vulnerable; not suitable |
| SHA-1 | ❌ Weak | Fast | Deprecated for security use |
| **SHA-256** | ✅ Strong | Good | Python stdlib `hashlib`; industry standard |
| SHA-3-256 | ✅ Strongest | Slower | Overkill for this use case |
| HMAC-SHA-256 | ✅ Strong + auth | Good | Requires shared secret; adds complexity |

### Chunk-level integrity

| Algorithm | Security | Performance | Notes |
|---|---|---|---|
| **CRC32** | Error detection only | Very fast | Python `zlib` stdlib; standard for checksums |
| Adler-32 | Weaker than CRC32 | Very fast | Not recommended |
| MD5 | Cryptographic | Slower | Overkill for per-chunk checks |

## Decision

- **File level**: SHA-256 (cryptographic; Python stdlib `hashlib`)
- **Chunk level**: CRC32 (error detection; Python stdlib `zlib`)

SHA-256 is computed on the original uncompressed file data and embedded in the metadata frame. This ensures the decoded output is byte-for-byte identical to the input.

CRC32 is computed on each chunk's data payload and embedded in the 16-byte chunk header. It detects transmission errors per chunk.

## Consequences

- **Good**: SHA-256 at file level provides cryptographic integrity assurance
- **Good**: Both algorithms are Python stdlib — zero extra dependencies
- **Good**: Two-level checking catches both chunk-level and file-level corruption
- **Bad**: CRC32 is not cryptographically secure — a determined attacker can forge a matching CRC32. SHA-256 at file level is the authoritative check
- **Risk**: v2.0 should consider upgrading to HMAC-SHA-256 for both levels to add authentication (detect intentional tampering with a known key)

## Known Gap

The GAP_ANALYSIS identified that using HMAC-SHA-256 instead of plain SHA-256 would add authentication (verify the file came from the expected sender). This is deferred to v2.0.

## Related

- REQUIREMENTS.md: NFR-005, NFR-015, DR-002
- DESIGN.md §7 (Security Implementation), §3.1 (Chunk Binary Format)
- ADR-004 (compression — hash is over uncompressed data)
