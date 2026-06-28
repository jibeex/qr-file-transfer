# ADR-006: Maximum Input File Size (1 GB)

**Date**: 2026-06-28  
**Status**: Accepted  
**Decided by**: Product Owner

---

## Context

The v1.0 architecture loads the entire file into memory for compression and chunking. Setting an upper bound on file size prevents out-of-memory conditions and runaway video generation.

Memory usage scales roughly as `2× file size` (original + compressed copy in memory simultaneously).

## Options Considered

| Limit | Memory peak | Transfer time @ 640 KB/s | Notes |
|---|---|---|---|
| 100 MB | ~200 MB RAM | ~2.5 min | Too restrictive for some use cases |
| 500 MB | ~1 GB RAM | ~13 min | Tight on low-memory systems |
| **1 GB** | **~2 GB RAM** | **~26 min** | Workable on modern hardware; acceptable limit |
| Unlimited | Unbounded | Unbounded | Risk of OOM crashes |

## Decision

**Maximum input file size: 1 GB (configurable via constant `MAX_FILE_SIZE`).**

Rationale: 1 GB is the practical upper limit for the in-memory architecture of v1.0. Modern workstations have 16–32 GB RAM, making 2 GB peak usage acceptable.

## Consequences

- **Good**: Prevents OOM crashes on typical hardware (NFR-003: < 1 GB RAM for 500 MB file)
- **Good**: Clear error message when exceeded (`FR-009`, exit code `ERROR_FILE_NOT_FOUND`)
- **Bad**: Users with files > 1 GB must split manually (documented as workaround in CON-001)
- **Risk**: A streaming architecture in v2.0 would remove this limit entirely

## Future

v2.0 should replace in-memory buffering with a streaming pipeline, eliminating the file size limit. This is tracked as OQ-006 (resume/checkpoint for large files).

## Related

- REQUIREMENTS.md: CON-001, NFR-003, OQ-006
- DESIGN.md §6 (Performance Architecture — memory management)
