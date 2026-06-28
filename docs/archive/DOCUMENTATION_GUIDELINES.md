> ⚠️ **Superseded** — Documentation standards have been consolidated into [CONTRIBUTING.md](../CONTRIBUTING.md) at the repo root. Kept for historical reference only.

# QR File Transfer - Documentation Guidelines

## Document Structure

This project maintains strict separation between requirements and design to ensure clarity, maintainability, and compliance with IEEE 29148 standards.

---

## REQUIREMENTS.md - What Should Be Included

### ✅ INCLUDE (Requirements - "WHAT" the system does)

**Functional Requirements**:
- What the system must do from a user perspective
- User-visible behaviors and features
- Input/output specifications (from user's view)
- Error handling from user perspective

**Non-Functional Requirements**:
- Performance targets (speed, throughput, latency)
- Reliability requirements (uptime, success rates)
- Security requirements (what must be protected)
- Usability requirements (ease of use, learnability)
- Compatibility requirements (platforms, formats)

**Constraints**:
- Business constraints (budget, timeline, resources)
- Technical constraints (language, platforms)
- Environmental constraints (hardware, operating conditions)
- Legal/regulatory constraints (compliance requirements)

**Use Cases**:
- Who uses the system
- What they want to accomplish
- Preconditions and postconditions
- Success and failure scenarios

**Acceptance Criteria**:
- Measurable, testable criteria
- Pass/fail conditions
- Verification methods

**System Boundaries**:
- External entities (users, systems, devices)
- Data flows (what goes in, what comes out)
- Black-box view of the system

---

## ❌ EXCLUDE from REQUIREMENTS.md (Implementation - "HOW")

**Never Include These in REQUIREMENTS.md**:

1. **Specific Libraries**:
   - ❌ "Use opencv-python for video processing"
   - ❌ "Use pyzbar for QR decoding"
   - ✅ "System requires video processing capabilities"

2. **Specific Algorithms**:
   - ❌ "Use SHA-256 for hashing"
   - ❌ "Use gzip compression"
   - ❌ "Implement CRC32 checksums"
   - ✅ "System shall verify data integrity cryptographically"

3. **Specific Codecs/Formats** (internal):
   - ❌ "Encode video using H.264 codec"
   - ❌ "Store metadata as JSON with fields X, Y, Z"
   - ❌ "Use 20-byte binary header with layout..."
   - ✅ "Output shall be industry-standard video format"

4. **Data Structures**:
   - ❌ "Use a dictionary with keys: {name, size, hash}"
   - ❌ "Store chunks in array of structs"
   - ✅ "System shall store chunk metadata"

5. **Class/Module Names**:
   - ❌ "FileEncoder class handles encoding"
   - ❌ "QRGenerator module creates QR codes"
   - ✅ "System shall encode files"

6. **Code-Level Details**:
   - ❌ "Call compress() then chunk() then encode()"
   - ❌ "Use multithreading for parallel processing"
   - ✅ "System shall compress data to reduce size"

7. **Internal Architecture**:
   - ❌ "MVC pattern with Controller, Model, View"
   - ❌ "Pipeline: Input → Compress → Chunk → QR → Video"
   - ✅ "System shall process files for transfer"

---

## 📋 Gray Areas - When to Include

Some items are borderline - here's how to decide:

### User-Visible Formats (INCLUDE if user-facing)
- ✅ "Output shall be playable in standard video players"
- ✅ "CLI shall follow POSIX conventions"
- ✅ "Exit codes: 0=success, 1-255=error"
- ⚠️ Acceptable: "Output shall be MP4 format" (if it's a compatibility requirement)

### Standards References (INCLUDE if compliance requirement)
- ✅ "System shall comply with ISO/IEC 18004 (QR Code standard)"
- ✅ "System shall meet WCAG 2.1 Level A accessibility"
- ❌ "Implement according to RFC 1952 (gzip)"

### Technology Constraints (INCLUDE if business constraint)
- ✅ "System must be written in Python" (business decision)
- ✅ "System must run on Python 3.9+" (compatibility requirement)
- ❌ "Use numpy arrays for performance" (implementation choice)

---

## 🎯 The Key Test: "WHAT vs HOW"

When writing a requirement, ask:

**"Does this describe WHAT the system must do, or HOW it does it?"**

- **WHAT** (requirement) → REQUIREMENTS.md
- **HOW** (implementation) → DESIGN.md

### Examples:

| Statement | WHAT or HOW? | Goes In |
|-----------|--------------|---------|
| "System shall transfer files between air-gapped computers" | WHAT | REQUIREMENTS.md |
| "System shall encode files using H.264 codec" | HOW | DESIGN.md |
| "System shall verify data integrity" | WHAT | REQUIREMENTS.md |
| "System shall use SHA-256 for hashing" | HOW | DESIGN.md |
| "Transfer speed shall exceed 400 KB/sec" | WHAT (measurable target) | REQUIREMENTS.md |
| "Use 800×800 grid size for performance" | HOW | DESIGN.md |
| "Video must play in VLC/QuickTime" | WHAT (compatibility) | REQUIREMENTS.md |
| "Generate QR using qrcode library" | HOW | DESIGN.md |

---

## 🔄 Where Implementation Details Go

All "HOW" items belong in **DESIGN.md**:

- System architecture (components, modules, layers)
- Technology choices (libraries, frameworks, tools)
- Algorithms and data structures
- Binary formats and protocols
- Class/module/function designs
- Database schemas
- API implementations
- Performance optimization techniques

---

## ✅ Compliance Checklist

Before finalizing REQUIREMENTS.md, verify:

- [ ] No specific library names (opencv, pyzbar, etc.)
- [ ] No specific algorithms (SHA-256, gzip, CRC32, etc.)
- [ ] No internal data structures (JSON fields, binary layouts)
- [ ] No class/module/function names
- [ ] No implementation steps (compress → chunk → encode)
- [ ] System shown as black box (external view only)
- [ ] All requirements are testable and measurable
- [ ] All requirements state WHAT, not HOW

---

## 📚 Document Roles

### REQUIREMENTS.md
- **Purpose**: Define WHAT the system must do
- **Audience**: Product owners, stakeholders, users, QA
- **Content**: Requirements, constraints, use cases, acceptance criteria
- **Perspective**: External, black-box view
- **Question it answers**: "What do we need to build?"

### DESIGN.md
- **Purpose**: Define HOW the system works
- **Audience**: Developers, architects, technical reviewers
- **Content**: Architecture, algorithms, data structures, technology choices
- **Perspective**: Internal, white-box view
- **Question it answers**: "How do we build it?"

---

## 🚨 Enforcement

When reviewing changes to REQUIREMENTS.md:

1. **Check for implementation leaks**:
   ```bash
   grep -i "library\|algorithm\|class\|module\|function\|json\|struct" REQUIREMENTS.md
   ```

2. **Ask these questions**:
   - Is this describing WHAT or HOW?
   - Could this be implemented differently without changing the requirement?
   - Is this visible to the user?
   - Is this a business decision or technical choice?

3. **If implementation detail found**:
   - Move it to DESIGN.md
   - Rephrase as high-level requirement if needed
   - Document the decision in DESIGN.md decision log

---

## 📖 Examples from This Project

### ✅ Good Requirements (WHAT)
```
FR-001: System shall encode any file type into a video
NFR-001: Transfer speed shall exceed 400 KB/sec
NFR-005: Data integrity shall be 100% (verified cryptographically)
CON-004: Output shall be playable in standard video players
```

### ❌ Bad Requirements (HOW - should be in DESIGN.md)
```
FR-001: System shall use opencv-python to encode H.264 video
NFR-001: Use 800×800 QR grid to achieve 640 KB/sec
NFR-005: Calculate SHA-256 hash and CRC32 checksum
CON-004: Output shall be MP4 with H.264 High Profile Level 4.0
```

---

## 🎓 Summary

**Golden Rule**: REQUIREMENTS.md describes the **problem space** (what needs to be solved), not the **solution space** (how to solve it).

- ✅ Focus on user needs, not technical solutions
- ✅ Describe outcomes, not methods
- ✅ Specify constraints, not implementations
- ✅ Keep it black-box, not white-box

**When in doubt**: If a developer could choose a different approach to meet the requirement, it's a good requirement. If it specifies exactly how to implement, it belongs in DESIGN.md.

---

**Last Updated**: 2026-06-28  
**Maintained By**: Project team  
**Standard**: IEEE 29148-2018
