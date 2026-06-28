# ADR-009: Progress Display Library (tqdm)

**Date**: 2026-06-28  
**Status**: Accepted  
**Decided by**: Tech Lead

---

## Context

The CLI must display real-time progress (FR-004): percentage complete, chunk count, and ETA. The library must be screen-reader compatible (CR-002) — no color-only indicators — and support `--quiet` suppression.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **tqdm** | Lightweight; widely used; `disable` flag for quiet mode; character-based fill (no color-only) | Limited styling |
| rich | Beautiful output; color + spinners | Color-heavy by default; requires careful accessibility configuration; heavier dependency |
| Manual `\r` writes | No dependency | Error-prone; no ETA calculation |

## Decision

**`tqdm`** — lightweight, accessible by default.

`tqdm` uses `[████░░░]` fill characters that convey progress without relying on color (satisfies CR-002). The `disable=True` flag cleanly suppresses all output for `--quiet` mode. ETA is built-in.

`rich` was rejected because its default progress display relies heavily on ANSI color and spinner animations that require extra configuration for screen reader compatibility.

## Consequences

- **Good**: Progress is character-based — accessible without color
- **Good**: `ProgressTracker(quiet=True)` wraps `tqdm(disable=True)` cleanly
- **Good**: Built-in ETA satisfies FR-004 acceptance criteria
- **Bad**: Less visually polished than `rich`

## Related

- REQUIREMENTS.md: FR-004, CR-002
- DESIGN.md §2.7 (ProgressTracker), §13.6 (Accessibility)
