# ADR-002: CLI-Only Interface for MVP

**Date**: 2026-06-27  
**Status**: Accepted  
**Decided by**: Product Owner

---

## Context

The system needs a user interface. Options range from a simple CLI to a full GUI application or mobile app with integrated camera.

The target users (security professionals, IT administrators, researchers) have stated CLI proficiency as a baseline. Development timeline is 6 weeks for MVP with a single developer.

## Options Considered

1. **CLI only** — `argparse`/`click`-based terminal commands
2. **CLI + TUI** — terminal UI with interactive display (e.g., `rich`, `textual`)
3. **Desktop GUI** — cross-platform GUI (e.g., `tkinter`, `PyQt`)
4. **Mobile app** — integrated camera capture (iOS/Android)

## Decision

**CLI only for MVP. GUI and mobile app deferred to v3.0.**

## Consequences

- **Good**: Fastest to implement; aligns with target user expertise
- **Good**: Scriptable, automatable, composable with other Unix tools
- **Good**: Keeps MVP scope achievable within 6-week timeline (CON-011)
- **Bad**: Limits audience — non-CLI users cannot use the tool
- **Bad**: No integrated camera capture; user must record video separately

## Future

- v3.0: Desktop GUI (`FR-018`)
- v3.0: Mobile app with camera integration (`FR-019`)

## Related

- REQUIREMENTS.md: CON-011, CON-013, FR-018, FR-019, §1.4 Out of Scope
