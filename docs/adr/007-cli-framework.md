# ADR-007: CLI Framework (argparse)

**Date**: 2026-06-28  
**Status**: Accepted  
**Decided by**: Tech Lead

---

## Context

The CLI is the only user interface for v1.0. It needs subcommands (`encode`, `decode`, `verify`, `info`, `secure-delete`), typed arguments, help text, and reliable exit codes. Two mainstream Python CLI frameworks were considered.

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **argparse** (stdlib) | Zero extra dependency; already in Python; predictable exit code behavior | Verbose boilerplate; less elegant subcommand support |
| click | Decorator-based; minimal boilerplate; automatic help | Extra dependency; click's `sys.exit` wrapping can interfere with exit code testing |

## Decision

**argparse** — Python standard library, zero dependency.

The exit code contract (IR-002) is security-critical: every error condition must map to a specific code. `argparse`'s behavior is fully predictable and testable via subprocess. `click` wraps `sys.exit` in ways that complicate contract testing (CT-009).

## Consequences

- **Good**: No additional dependency; consistent with zero-external-dependency philosophy for security tools
- **Good**: Exit codes fully controllable — no framework interception
- **Bad**: More boilerplate per subcommand (acceptable for 5 commands)

## Related

- REQUIREMENTS.md: IR-001, IR-002, FR-002
- DESIGN.md §1.2 (CLI component), specs/cli-reference.md
