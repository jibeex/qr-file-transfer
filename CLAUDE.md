# Project Instructions for AI Assistants

## Documentation Standards

### Key Principle: Separation of Requirements and Design

**REQUIREMENTS.md** = **WHAT** the system must do (user perspective)  
**DESIGN.md** = **HOW** the system works (implementation)

### Critical Rule for REQUIREMENTS.md

**Never include implementation details**:
- ❌ Specific libraries (opencv, pyzbar, qrcode)
- ❌ Specific algorithms (SHA-256, gzip, CRC32, H.264)
- ❌ Data structures (JSON schemas, binary layouts)
- ❌ Class/module names (Encoder, Decoder)
- ❌ Internal architecture (components, pipelines)

**Always include requirements**:
- ✅ What the system does (functional requirements)
- ✅ How well it performs (non-functional requirements)
- ✅ User-visible behaviors (use cases, interfaces)
- ✅ Constraints (business, technical, environmental)

### The Test

Ask: **"Does this describe WHAT or HOW?"**
- WHAT → REQUIREMENTS.md
- HOW → DESIGN.md

### Quick Check

```bash
# Verify no implementation leaks before committing
grep -i "sha-256\|h.264\|mp4\|gzip\|crc32\|opencv\|pyzbar" docs/REQUIREMENTS.md
```

If found: move to DESIGN.md and rephrase as high-level requirement.

---

**Full guidelines**: See [docs/DOCUMENTATION_GUIDELINES.md](./docs/DOCUMENTATION_GUIDELINES.md)

**Last Updated**: 2026-06-28
