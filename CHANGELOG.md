# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Requirements specification (IEEE 29148) — `docs/REQUIREMENTS.md`
- Technical design (arc42) — `docs/DESIGN.md` with quality scenarios, cross-cutting concerns, accessibility
- Architecture Decision Records (ADR-001–009) — `docs/adr/`
- Wire format, CLI reference, and algorithms specs — `docs/specs/`
- Test design spec with requirements traceability matrix and E2E suite — `docs/TEST_PLAN.md`
- Operations guide — `docs/OPS_GUIDE.md`
- Glossary — `docs/GLOSSARY.md`
- ROADMAP.md — implementation phases and risk register
- `pyproject.toml` — package metadata and `qr-transfer` entry point (NFR-023)
- `.github/dependabot.yml` — automated dependency updates (SEC-004)
- CONTRIBUTING.md, CHANGELOG.md, SECURITY.md, LICENSE (MIT)

### Changed
- Restructured docs following Divio/arc42/ADR best practices
- Moved decision log from REQUIREMENTS.md to individual ADR files
- Extracted glossary, algorithms, wire format to standalone files
- Resolved all 47 GAP_ANALYSIS.md items; file removed
- Fixed chunk header size (16 → 20 bytes) across DESIGN.md and specs/
- Updated `mp4v` codec documentation to reflect MPEG-4/H.264 dual support

### Removed
- `docs/GAP_ANALYSIS.md` — all gaps resolved or tracked
- `requirements.txt` — superseded by `pyproject.toml`

---

## [0.1.0] — 2026-06-28

### Added
- Initial project documentation (requirements, design, gap analysis)
- Project structure and dependencies (`requirements.txt`)

[Unreleased]: https://github.com/jibeex/qr-file-transfer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jibeex/qr-file-transfer/releases/tag/v0.1.0
