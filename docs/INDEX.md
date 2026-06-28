# Documentation Index

**Owner**: Development Team  
**Review trigger**: When any document is added, removed, or renamed

---

## Core Documents

| Document | Purpose | Audience | Status |
|---|---|---|---|
| [REQUIREMENTS.md](./REQUIREMENTS.md) | **WHAT** — user requirements (IEEE 29148) | Product owners, QA, stakeholders | ✅ Draft complete |
| [DESIGN.md](./DESIGN.md) | **HOW** — architecture and component design (arc42) | Developers, architects | ⚠️ In progress |
| [GLOSSARY.md](./GLOSSARY.md) | Shared term definitions | All | ✅ Complete |
| [TEST_PLAN.md](./TEST_PLAN.md) | Test strategy and acceptance criteria | QA, developers | ✅ Draft complete |
| [OPS_GUIDE.md](./OPS_GUIDE.md) | Install, configure, troubleshoot | IT Operations, users | ✅ Draft complete |

---

## Project Management

| Document | Purpose |
|---|---|
| [ROADMAP.md](../ROADMAP.md) | Week-by-week implementation plan, risk register, success criteria |

---

## Architecture Decision Records (`adr/`)

One immutable file per architecture decision. Written when a choice is made; never edited — superseded instead.

| ADR | Title | Status |
|---|---|---|
| [001](./adr/001-default-grid-size.md) | Default QR Grid Size (800×800) | Accepted |
| [002](./adr/002-cli-only-mvp.md) | CLI-Only Interface for MVP | Accepted |
| [003](./adr/003-video-format.md) | Video Output Format (MP4/H.264) | Accepted |
| [004](./adr/004-compression.md) | Data Compression (gzip, Level 6) | Accepted |
| [005](./adr/005-integrity-algorithm.md) | Integrity Verification (SHA-256 + CRC32) | Accepted |
| [006](./adr/006-max-file-size.md) | Maximum Input File Size (1 GB) | Accepted |

---

## Reference Specifications (`specs/`)

Stable, lookup-oriented reference docs. Updated only when the contract changes.

| Spec | Contents |
|---|---|
| [cli-reference.md](./specs/cli-reference.md) | All commands, flags, exit codes |
| [data-protocol.md](./specs/data-protocol.md) | Chunk binary format, metadata JSON schema |
| [algorithms.md](./specs/algorithms.md) | Encoding/decoding pipeline, chunking, QR capacity |

---

## Archive (`archive/`)

Superseded documents kept for history.

| Document | Reason archived |
|---|---|
| [REQUIREMENTS_GAP_ANALYSIS.md](./archive/REQUIREMENTS_GAP_ANALYSIS.md) | All gaps resolved |
| [DOCUMENTATION_GUIDELINES.md](./archive/DOCUMENTATION_GUIDELINES.md) | Superseded by [CONTRIBUTING.md](../CONTRIBUTING.md) |
| [PROJECT_SUMMARY.md](./archive/PROJECT_SUMMARY.md) | Superseded by [README.md](../README.md) |

---

## Reading Guide

**New to the project?** → `README.md` at repo root → `REQUIREMENTS.md` → `DESIGN.md`  
**Setting up dev environment?** → `CONTRIBUTING.md` at repo root → `OPS_GUIDE.md`  
**Understanding a design choice?** → `docs/adr/`  
**Looking up a command or field?** → `docs/specs/`  
**Writing requirements or design?** → `CONTRIBUTING.md` §Documentation Standards  
**Reporting a security issue?** → `SECURITY.md` at repo root
