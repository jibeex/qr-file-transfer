# QR Code File Transfer System - Requirements Specification

## Document Information
- **Project Name**: QR File Transfer
- **Version**: 1.0.0
- **Date**: 2026-06-27
- **Document Type**: Requirements Specification (SRS)
- **Status**: Draft

## Purpose

This document describes **WHAT** the system should do from a user perspective. It contains requirements, constraints, and acceptance criteria, but **NOT** implementation details or technical design decisions.

**Intended Audience**:
- Product Owner (approval authority)
- Security Team (security requirements review)
- IT Operations (operational requirements review)
- QA Team (test planning and validation)
- Development Team (implementation reference)
- Compliance Officer (regulatory review)

For technical design, see: [DESIGN.md](./DESIGN.md)

---

## 1. Introduction

### 1.1 Product Overview

A software tool that enables users to transfer files between computers that have no network connection (air-gapped), using only a display and a camera. The system encodes files into visual QR codes that can be captured and decoded back to the original file.

### 1.2 Target Users

**Primary Users**:
- Security professionals working with air-gapped systems
- IT administrators in high-security environments
- Researchers with isolated networks
- Individuals needing secure offline file transfer

**User Characteristics**:
- Comfortable with command-line tools
- Basic understanding of file systems
- Access to: computer with display + device with camera

### 1.3 Use Cases

**UC-001: Transfer Configuration File**
- **Actor**: System Administrator
- **Goal**: Transfer a 5KB config file from secure workstation to air-gapped server
- **Preconditions**:
  - Source system has qr-transfer installed and operational
  - Destination system has qr-transfer installed and operational
  - Admin has camera device available (phone, webcam)
  - Both systems have sufficient disk space
- **Main Success Scenario**:
  1. Admin runs: `qr-transfer encode config.yaml output video file`
  2. System compresses and encodes file, displays progress
  3. System displays "Encoding complete" with video file path
  4. Admin displays video fullscreen on source system
  5. Admin records video with camera device at 20-40cm distance
  6. Admin transfers video file to destination via physical media (USB, SD card)
  7. Admin runs: `qr-transfer decode recorded.mov config.yaml`
  8. System decodes, verifies integrity, displays progress
  9. System displays "Transfer successful" with file details
- **Postconditions**:
  - config.yaml exists on destination with verified integrity
  - Video files can be securely deleted from both systems
  - Transfer logged (if audit logging enabled)
- **Alternative Flows**:
  - 7a. Video corrupted/incomplete → System reports missing chunks → Admin re-records specific sections
  - 7b. Wrong video file → System detects format mismatch → Error with file info
  - 8a. Integrity check fails → System reports corruption → Do not use file, retry transfer
- **Exception Flows**:
  - 1a. Source file > 1 GB → Error: "File exceeds 1 GB limit"
  - 4a. Display resolution < 1080p → Warning: "Low resolution may affect reliability"
  - 7a. Destination disk space insufficient → Error before attempting decode
- **Frequency**: Weekly
- **Priority**: High

**UC-002: Transfer Cryptographic Keys**
- **Actor**: Security Engineer
- **Goal**: Transfer private key (1KB) to cold storage system
- **Preconditions**:
  - Source system has qr-transfer and private key file
  - Destination is air-gapped cold storage system
  - Security protocols for key handling are followed
- **Main Success Scenario**:
  1. Engineer encodes private key to video
  2. Engineer verifies encoding successful
  3. Engineer displays video, records with dedicated secure camera
  4. Engineer transfers to cold storage via secure physical media
  5. Engineer decodes on cold storage system
  6. System verifies integrity
  7. Engineer securely deletes source video and intermediate files
- **Postconditions**:
  - Private key on cold storage with verified integrity
  - Source video securely wiped (not just deleted)
  - Transfer audited and logged
- **Alternative Flows**:
  - 5a. Decode fails → Engineer retries with fresh recording
  - 6a. Integrity fails → Abort, investigate, retry from step 1
- **Security Considerations**:
  - Video displays sensitive key material on screen
  - Recording device must be in secure location
  - All intermediate files must be securely wiped
- **Frequency**: Monthly
- **Priority**: Critical

**UC-003: Transfer Document Package**
- **Actor**: Researcher
- **Goal**: Transfer 10MB research document with images
- **Preconditions**:
  - Source and destination systems operational
  - Adequate lighting conditions (300-700 lux)
  - Camera capable of 1080p video recording
- **Main Success Scenario**:
  1. Researcher encodes PDF to video (~15 second video for 10MB)
  2. System displays encoding complete
  3. Researcher plays video fullscreen, records with phone
  4. Researcher transfers via USB to air-gapped analysis system
  5. Researcher decodes video
  6. System verifies integrity, researcher confirms content
- **Postconditions**:
  - Document on analysis system, integrity verified
  - Researcher can open and view document normally
- **Alternative Flows**:
  - 3a. Recording interrupted → Researcher restarts recording
  - 5a. Some frames missing → System reports specific missing chunks, researcher re-records those sections only
- **Performance Requirements**:
  - Total time < 2 minutes for 10MB file
- **Frequency**: Daily
- **Priority**: Medium

**UC-004: Emergency Credential Transfer**
- **Actor**: IT Support
- **Goal**: Transfer emergency access credentials when network is down
- **Preconditions**:
  - Network outage preventing normal credential distribution
  - IT support has qr-transfer on accessible system
  - Technician on-site with camera device
- **Main Success Scenario**:
  1. Support generates one-time credentials (text file)
  2. Support encodes credentials to video
  3. Support shares video via screen share to technician's personal device
  4. Technician records video from screen
  5. Technician transfers to on-site system
  6. Technician decodes credentials
  7. Technician uses credentials for emergency access
  8. Credentials expire/revoked after use
- **Postconditions**:
  - Emergency access granted
  - Temporary credentials used then revoked
  - Incident logged
- **Alternative Flows**:
  - 4a. Screen share quality poor → Support sends video file via alternative channel
  - 6a. Decode fails → Support regenerates credentials, repeats process
- **Time Constraints**:
  - Process must complete < 5 minutes (emergency scenario)
- **Frequency**: Rare (emergency only)
- **Priority**: High

**UC-005: Misuse Scenario - Unauthorized Data Exfiltration (Negative Use Case)**
- **Threat Actor**: Malicious insider
- **Goal**: Exfiltrate sensitive data from air-gapped system
- **Scenario**:
  1. Insider encodes sensitive file to video
  2. Insider displays video on screen
  3. Insider records video with personal phone
  4. Insider carries video out on personal device
- **Mitigations**:
  - System cannot prevent this misuse (physical security required)
  - Detection: Video encoding creates system logs (if logging enabled)
  - Prevention: Physical security (camera monitoring, device restrictions)
  - Deterrence: Audit trails, access logging, policy enforcement
- **Security Recommendations**:
  - Deploy in environments with appropriate physical security controls
  - Enable audit logging to detect encoding operations
  - Consider metadata anonymization for sensitive environments
  - Document security considerations in deployment guide
- **Priority**: High (security consideration)

### 1.4 Out of Scope

- Real-time bidirectional communication
- File transfer over networks (use standard protocols)
- Mobile app with camera integration (future enhancement)
- GUI application (future enhancement)
- Batch/directory transfer (future enhancement)

### 1.5 Document Scope

**This document covers**:
- Functional requirements for CLI-based file transfer system
- Non-functional requirements (performance, security, reliability, usability)
- User interface specifications for command-line interface
- System constraints and assumptions
- Quality attributes and success metrics

**This document does NOT cover**:
- Implementation details and technical architecture (see DESIGN.md)
- Test plans and test cases (see TEST_PLAN.md - to be created)
- Deployment procedures and operations guide (see OPS_GUIDE.md - to be created)
- Developer documentation and API specifications (see DESIGN.md)


### 1.5.1 System Context Diagram

```
                              ┌──────────┐
                              │   User   │
                              └─────┬────┘
                                    │
                    Commands        │        Results/Errors
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌─────────────────────────────────────────────┐
            │                                             │
            │       QR File Transfer System               │
            │                                             │
            │   (Accepts files, generates QR videos,      │
            │    decodes QR videos, verifies integrity)   │
            │                                             │
            └─────────────────────────────────────────────┘
                    │               ▲               │
                    │               │               │
         Input File │               │ Video File   │ Output File
                    │               │               │
                    ▼               │               ▼
            ┌──────────────┐  ┌─────┴──────┐  ┌──────────────┐
            │   Source     │  │  Physical  │  │ Destination  │
            │  Computer    │──│  Transfer  │─▶│  Computer    │
            │  (Display)   │  │  Medium    │  │ (Air-gapped) │
            └──────────────┘  └────────────┘  └──────────────┘
                    │                                  ▲
                    │         QR Video                 │
                    │         on Screen                │
                    │                                  │
                    └─────────┐         ┌──────────────┘
                              │         │
                              ▼         │
                        ┌─────────────────┐
                        │ Camera Device   │
                        │ (Records video) │
                        └─────────────────┘

External Entities:
- User: Person operating the system (admin, engineer, researcher)
- Source Computer: Computer with display where file originates
- Destination Computer: Air-gapped computer receiving the file
- Camera Device: Device that captures QR video from screen
- Physical Transfer Medium: USB drive, SD card for video file
- Display: Screen showing QR video
```

### 1.5.2 System Boundary Definition

**Inside System Boundary** (what the system controls):
- File encoding logic
- QR code generation (any grid size 177-1000)
- Video creation (industry-standard format)
- File decoding logic
- QR code detection and decoding
- Data integrity verification
- Error reporting and handling
- Command-line interface
- Progress tracking
- Compression/decompression

**Outside System Boundary** (external dependencies):
- Source computer display hardware
- Destination computer hardware
- Camera device (for capturing QR codes)
- Video recording software (native to camera device)
- Physical transfer medium (USB, SD card)
- File system (where files are stored)
- Operating system (macOS, Linux, Windows)
- Python runtime environment
- Third-party libraries (see DESIGN.md for details)

**System Interfaces**:

| Interface | Type | Direction | Protocol/Format |
|-----------|------|-----------|-----------------|
| File Input | File | User → System | Any binary/text file |
| Video Output | File | System → User | Standard video file |
| Video Input | File | User → System | Standard video file |
| File Output | File | System → User | Original file format |
| CLI Commands | Text | User → System | Command-line arguments |
| Console Output | Text | System → User | stdout/stderr |
| Display | Visual | System → User (via display) | Video playback |
| Camera | Visual | User → System (via camera) | Video recording |

### 1.5.3 Operating Environment

**Source System Environment**:
- Computer with display (1920×1080 minimum)
- Python 3.9+ installed
- qr-transfer software installed
- Sufficient disk space for video output
- Read access to source files

**Destination System Environment**:
- Computer (air-gapped, no network)
- Python 3.9+ installed
- qr-transfer software installed
- Sufficient disk space for decoded files
- Write access to output directory

**Transfer Environment**:
- Camera device capable of 1080p video recording
- Adequate lighting (300-700 lux)
- Physical transfer medium (USB, SD card)

**Assumptions About Environment**:
- Display can show video clearly at specified resolution
- Camera can focus at 20-40cm distance
- Lighting conditions are controllable
- Physical access to both systems is available
- Physical security controls prevent unauthorized transfers


### 1.6 References

- **ISO/IEC 18004:2015** - QR Code bar code symbology specification


- **IEEE 29148-2018** - Systems and software engineering - Life cycle processes - Requirements engineering


- **WCAG 2.1** - Web Content Accessibility Guidelines

---

## 2. Stakeholders

| Stakeholder | Interest | Priority | Role | Approval Required |
|-------------|----------|----------|------|-------------------|
| End Users | Usability, reliability | High | Primary users | User acceptance testing sign-off |
| Security Team | Data integrity, audit trail | High | Security review | Security requirements (§4.5) approval |
| IT Operations | Installation, support | Medium | Operational review | Installability requirements (§4.7) approval |
| Development Team | Maintainability, extensibility | Medium | Implementation | Technical feasibility review |
| Compliance Officer | Regulatory requirements | Low | Legal review | Privacy & compliance approval |
| Product Owner | Vision, scope, budget | Critical | Final authority | All requirements approval |
| QA Team | Quality assurance | High | Testing | Testability review |

### 2.1 Approval Process

1. Security Team reviews §4.5 (Security requirements) and §5.1.5 (Data requirements)
2. IT Operations reviews §4.7 (Installability requirements)
3. Development Team reviews technical feasibility of all requirements
4. QA Team reviews testability of acceptance criteria
5. Product Owner conducts final approval
6. All stakeholders sign Section 13 (Approval)

### 2.2 Conflict Resolution

- **Priority 1**: Product Owner has final decision authority
- **Priority 2**: Security requirements cannot be downgraded without Security Team approval
- **Priority 3**: Technical feasibility concerns veto unrealistic requirements

---

## 3. Functional Requirements

### 3.1 File Encoding

**FR-001: Encode Any File Type**
- **ID**: FR-001
- **Priority**: MUST-1 (Critical)
- **Source**: Product requirements
- **Owner**: Product Owner
- **Status**: Draft
- **Stability**: Stable
- **Dependencies**: None
- **Related**: FR-002, FR-006
- **Verification Method**: Test (TC-FR-001)
- **Description**: Users shall be able to encode any file (text, binary, any format) into a video
- **Rationale**: System must be file-agnostic for maximum utility
- **Risk if not implemented**: Critical - Core functionality blocked
- **Acceptance Criteria**:
  - AC-001-1: System shall accept files with any extension (.txt, .pdf, .zip, .bin, .jpg, etc.)
    - Test: Encode 20 different file types from standard test suite
    - Pass: All 20 files encode without error
  - AC-001-2: System shall preserve binary data without corruption
    - Test: Encode/decode random binary file (10 MB), compare cryptographic hash
    - Pass: Hash matches exactly (100% integrity)
  - AC-001-3: System shall support files from 1 byte to 1 GB
    - Test: Encode files of sizes: 1B, 1KB, 100KB, 1MB, 10MB, 100MB, 1GB
    - Pass: All files encode successfully, memory usage < 2× file size
- **User Story**: "As a user, I want to encode any type of file so that I'm not limited by format"

**FR-002: Simple Encoding Command**
- **ID**: FR-002
- **Priority**: MUST-1 (Critical)
- **Source**: Usability requirements
- **Owner**: Product Owner
- **Status**: Draft
- **Stability**: Stable
- **Dependencies**: FR-001
- **Related**: FR-006, UI-001
- **Verification Method**: Demo (user testing)
- **Description**: Users shall encode a file with a single, simple command
- **Rationale**: Reduce friction and errors
- **Risk if not implemented**: Critical - Poor user adoption
- **Acceptance Criteria**:
  - AC-002-1: Command syntax shall be: `qr-transfer encode <input_file> <output_video>`
    - Test: Execute command with valid inputs
    - Pass: Command completes successfully with exit code 0
  - AC-002-2: Command shall work with default settings requiring no additional configuration
    - Test: Run command without optional flags
    - Pass: Video generated successfully with sensible defaults
  - AC-002-3: Output shall be standard standard video format video file
    - Test: Verify output file format with `file` command and video player
    - Pass: File identified as "standard video format", playable in VLC/QuickTime
  - AC-002-4: Progress shall be displayed during encoding
    - Test: Observe console output during encoding
    - Pass: Progress percentage displayed, updates at least every second
- **User Story**: "As a user, I want to encode with one command so that I don't need to configure complex options"

**FR-003: Fast Transfer Speed**
- **ID**: FR-003
- **Priority**: MUST-2 (High)
- **Source**: Performance requirements
- **Owner**: Product Owner
- **Status**: Draft
- **Stability**: Moderate (performance targets may adjust after POC)
- **Dependencies**: FR-001, FR-002, NFR-001
- **Related**: NFR-001, NFR-002
- **Verification Method**: Test (automated performance benchmark)
- **Description**: Users shall experience fast transfer speeds suitable for typical file sizes
- **Rationale**: User patience is limited; slow transfers reduce usability
- **Risk if not implemented**: High - Poor user experience, low adoption
- **Acceptance Criteria**:
  - AC-003-1: Transfer 1 MB file in < 5 seconds (end-to-end)
    - Test environment: iPhone 16 Pro, MacBook Pro 16" Retina, office lighting (300-700 lux)
    - Test procedure: Encode → display fullscreen → record at 30cm → decode
    - Test data: Randomly generated 1 MB binary file
    - Measurement: 10 trials, calculate average
    - Pass: Average time ≤ 5.0 seconds, no trial > 7 seconds
  - AC-003-2: Transfer 10 MB file in < 30 seconds (end-to-end)
    - Test environment: Same as AC-003-1
    - Test procedure: Same as AC-003-1
    - Test data: Randomly generated 10 MB binary file
    - Measurement: 5 trials, calculate average
    - Pass: Average time ≤ 30 seconds, no trial > 40 seconds
  - AC-003-3: Estimated time remaining shall be displayed
    - Test: Monitor console output during encoding
    - Pass: Time estimate shown, updates at least every 2 seconds, accuracy within ±20%
- **User Story**: "As a user, I want fast transfers so that I don't wait unnecessarily"

**FR-004: Progress Visibility**
- **Priority**: SHOULD
- **Description**: Users shall see encoding progress in real-time
- **Acceptance Criteria**:
  - ✓ Display percentage complete (0-100%)
  - ✓ Show current chunk / total chunks
  - ✓ Estimate time remaining
  - ✓ Option to suppress progress output (--quiet flag)
- **User Story**: "As a user, I want to see progress so that I know the system is working"

**FR-005: Customizable Transfer Speed**
- **Priority**: SHOULD
- **Description**: Users shall be able to adjust transfer speed vs. compatibility
- **Rationale**: Different hardware has different capabilities
- **Acceptance Criteria**:
  - ✓ Option to specify grid size (e.g., --grid-size 800)
  - ✓ Sensible default optimized for modern hardware
  - ✓ Clear documentation of trade-offs
  - ✓ System validates chosen size is supported
- **User Story**: "As a user with older hardware, I want to reduce grid size so that scanning is more reliable"

### 3.2 File Decoding

**FR-006: Decode Video to File**
- **Priority**: MUST
- **Description**: Users shall decode a video back to the original file
- **Acceptance Criteria**:
  - ✓ Command: `qr-transfer decode <input_video> <output_file>`
  - ✓ Reconstruct exact original file (byte-for-byte identical)
  - ✓ Support video recorded at any angle/orientation (within reason)
  - ✓ Display progress during decoding
- **User Story**: "As a user, I want to decode easily so that I can retrieve my file"

**FR-007: Verify File Integrity**
- **Priority**: MUST
- **Description**: Users shall receive confirmation that the file transferred correctly
- **Rationale**: Data integrity is critical in secure environments
- **Acceptance Criteria**:
  - ✓ Automatic integrity check after decoding
  - ✓ Clear success/failure message
  - ✓ If failure: report which parts are missing/corrupted
  - ✓ Exit code indicates success (0) or failure (non-zero)
- **User Story**: "As a user, I want verification so that I know my file is intact"

**FR-008: Handle Imperfect Captures**
- **ID**: FR-008
- **Priority**: MUST-2 (High)
- **Source**: Usability requirements, user feedback
- **Owner**: Product Owner
- **Status**: Draft
- **Stability**: Moderate (thresholds may adjust after real-world testing)
- **Dependencies**: FR-006
- **Related**: NFR-006, NFR-007
- **Verification Method**: Test (induced error conditions)
- **Description**: System shall work with typical real-world video captures
- **Rationale**: Users cannot perfectly stabilize cameras in practical environments
- **Risk if not implemented**: High - System unusable in real-world conditions
- **Acceptance Criteria**:
  - AC-008-1: Tolerate minor camera shake
    - Test environment: Handheld recording (not tripod), normal hand tremor
    - Quantification: ±5° angular deviation from perpendicular, ±2cm positional movement
    - Test procedure: Record video with intentional minor shake within specified range
    - Pass: Successfully decode ≥ 95% of chunks
  - AC-008-2: Work with various lighting conditions
    - Test environment: Office lighting range 300-700 lux (not extreme darkness < 50 lux)
    - Test procedure: Record videos at 300, 500, 700 lux
    - Pass: Successfully decode ≥ 95% of chunks at all three lighting levels
  - AC-008-3: Handle duplicate frames in video
    - Test: Create video with 10% duplicate consecutive frames
    - Pass: Decoder identifies and skips duplicates, no chunk duplication in output
  - AC-008-4: Skip frames that cannot be decoded
    - Test: Inject 3 corrupted/unreadable frames into 50-frame video
    - Pass: Decoder reports missing 3 chunks, continues processing remaining frames
  - AC-008-5: Recover if some frames are missing
    - Test: Remove up to 5% of frames from encoded video
    - Pass: Decoder reports specific missing chunks, provides clear error message
- **User Story**: "As a user, I want reliable decoding so that minor imperfections don't fail the transfer"

### 3.3 Error Handling & Recovery

**FR-009: Clear Error Messages**
- **Priority**: MUST
- **Description**: Users shall receive actionable error messages when something goes wrong
- **Acceptance Criteria**:
  - ✓ Errors explain what went wrong in plain language
  - ✓ Errors suggest how to fix the problem
  - ✓ Include error codes for support/debugging
  - ✓ No technical jargon in user-facing messages
- **User Story**: "As a user, I want helpful errors so that I can fix problems myself"

**FR-010: Report Missing Data**
- **Priority**: MUST
- **Description**: If transfer is incomplete, users shall know exactly what is missing
- **Acceptance Criteria**:
  - ✓ Report number of missing chunks
  - ✓ Calculate percentage of file successfully transferred
  - ✓ Suggest retry or re-recording
  - ✓ Option to retry only missing chunks (future: not MVP)
- **User Story**: "As a user, I want to know what's missing so that I can retry efficiently"

**FR-011: Verify Without Full Decode**
- **Priority**: SHOULD
- **Description**: Users shall be able to check video integrity without full decode
- **Rationale**: Quick validation before starting full transfer
- **Acceptance Criteria**:
  - ✓ Command: `qr-transfer verify <video>`
  - ✓ Check metadata frame is readable
  - ✓ Report expected vs. actual frame count
  - ✓ Complete in < 5 seconds for any video size
- **User Story**: "As a user, I want to verify before decoding so that I don't waste time on bad videos"

### 3.4 Information & Inspection

**FR-012: Display File Metadata**
- **Priority**: SHOULD
- **Description**: Users shall view information about an encoded video
- **Acceptance Criteria**:
  - ✓ Command: `qr-transfer info <video>`
  - ✓ Display: original filename, file size, grid size, frame count
  - ✓ Display: estimated transfer time, creation date
  - ✓ Human-readable format
- **User Story**: "As a user, I want to see metadata so that I know what's in a video"

**FR-013: Help Documentation**
- **Priority**: MUST
- **Description**: Users shall access help from the command line
- **Acceptance Criteria**:
  - ✓ Command: `qr-transfer --help` shows all commands
  - ✓ Command: `qr-transfer encode --help` shows encode options
  - ✓ Help text is clear and includes examples
  - ✓ Version info: `qr-transfer --version`
- **User Story**: "As a user, I want built-in help so that I don't need to search documentation"


### 3.5 Data Requirements

**DR-001: Video Output Format**
- **ID**: DR-001
- **Priority**: MUST-1 (Critical)
- **Owner**: Product Owner
- **Verification Method**: Test
- **Description**: System shall output videos in a widely-compatible format
- **Rationale**: Videos must be playable on standard video players and recordable by standard cameras
- **Acceptance Criteria**:
  - AC-DR-001: Generated videos shall be playable on VLC, QuickTime, and Windows Media Player without additional codecs
  - AC-DR-001: Videos shall maintain sufficient quality to preserve QR code readability
  - AC-DR-001: Video format shall be industry-standard (not proprietary)

**DR-002: File Metadata**
- **ID**: DR-002
- **Priority**: MUST-1 (Critical)
- **Owner**: Product Owner
- **Verification Method**: Test
- **Description**: System shall embed file metadata for verification and validation
- **Rationale**: Metadata enables integrity checking and ensures correct file reconstruction
- **Acceptance Criteria**:
  - AC-DR-002: Metadata shall include original filename
  - AC-DR-002: Metadata shall include original file size
  - AC-DR-002: Metadata shall include integrity verification information
  - AC-DR-002: Metadata shall indicate total expected data chunks
  - AC-DR-002: Decoder shall detect missing or corrupted metadata

**DR-003: Data Chunking**
- **ID**: DR-003
- **Priority**: MUST-1 (Critical)
- **Owner**: Product Owner
- **Verification Method**: Test
- **Description**: System shall divide files into discrete, verifiable chunks
- **Rationale**: Chunking enables error detection, progress tracking, and partial recovery
- **Acceptance Criteria**:
  - AC-DR-003: Each chunk shall be independently verifiable for integrity
  - AC-DR-003: Chunks shall include sequencing information (chunk number, total chunks)
  - AC-DR-003: Malformed or corrupted chunks shall be detectable
  - AC-DR-003: System shall report which specific chunks are missing or corrupt

### 3.6 Interface Requirements

**IR-001: Command-Line Interface Contract**
- **ID**: IR-001
- **Priority**: MUST-1 (Critical)
- **Owner**: Development Team
- **Verification Method**: Test
- **Description**: CLI shall follow POSIX conventions and provide consistent interface
- **Specification**:
  - Exit codes: 0 = success, 1-255 = error (specific codes documented)
  - Output: stdout for normal output, stderr for errors
  - Arguments: POSIX-style flags (-g, --grid-size)
  - Help: --help and -h for all commands
- **Acceptance Criteria**:
  - AC-IR-001: All commands return appropriate exit codes
  - AC-IR-001: Error messages output to stderr, normal output to stdout

**IR-002: Error Code Specification**
- **ID**: IR-002
- **Priority**: SHOULD-1
- **Owner**: Development Team
- **Verification Method**: Inspection
- **Description**: System shall use standardized error codes
- **Specification**:
  - 0: Success
  - 1: General error
  - 2: File not found
  - 3: Invalid input
  - 4: Encoding failed
  - 5: Decoding failed
  - 6: Integrity check failed
  - 7: Insufficient permissions
  - 8: Out of disk space
- **Rationale**: Standardized codes enable automation and scripting
- **Acceptance Criteria**:
  - AC-IR-002: Each error condition returns documented code

### 3.7 Compliance Requirements

**CR-001: Privacy Compliance (GDPR)**
- **ID**: CR-001
- **Priority**: SHOULD-1 (High for EU users)
- **Owner**: Compliance Officer
- **Verification Method**: Inspection + Privacy audit
- **Description**: System shall comply with GDPR data protection requirements
- **Requirements**:
  - Filenames in metadata are PII - shall provide option to anonymize
  - No telemetry or data collection
  - No network access (verifiable)
  - User data processed locally only
- **Acceptance Criteria**:
  - AC-CR-001: Option --anonymize-metadata strips filename from QR video
  - AC-CR-001: Network monitoring confirms zero external communication
  - AC-CR-001: Privacy audit passes with no PII leakage

**CR-002: Accessibility Compliance (WCAG 2.1 Level A)**
- **ID**: CR-002
- **Priority**: SHOULD-2
- **Owner**: Development Team
- **Verification Method**: Inspection + Accessibility audit
- **Description**: CLI output shall be accessible to users with disabilities
- **Requirements**:
  - Screen reader compatible (structured output)
  - Progress indicators do not rely on color alone
  - Error messages readable by screen readers
  - Help text written at Grade 8 reading level
- **Acceptance Criteria**:
  - AC-CR-002: Output tested with VoiceOver/NVDA screen readers
  - AC-CR-002: Help text passes Flesch-Kincaid readability test (Grade 8)
  - AC-CR-002: Color not used as sole indicator for any status

**CR-003: Export Control Compliance**
- **ID**: CR-003
- **Priority**: MAY (if encryption added in future)
- **Owner**: Compliance Officer
- **Verification Method**: Legal review
- **Description**: If encryption is added, comply with export control regulations
- **Note**: Current version has no encryption, this is placeholder for v2.0
- **Requirements**:
  - Document encryption algorithms used
  - Verify export control classification
  - Include required notices in documentation



---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-001: Transfer Speed**
- **Priority**: MUST
- **Target**: Minimum 400 KB/sec effective transfer rate under typical conditions
- **Measurement**: 10 MB file transfers in ≤ 25 seconds (encode + display + capture + decode)
- **Rationale**: Users need practical transfer speeds for productivity
- **Acceptance Test**: Transfer 10 MB test file on reference hardware (iPhone 16 + Mac) in < 25 seconds

**NFR-002: Encoding Performance**
- **Priority**: SHOULD
- **Target**: Encode 10 MB file in < 5 seconds
- **Rationale**: Encoding should not be the bottleneck
- **Acceptance Test**: Measure encoding time for various file sizes

**NFR-003: Memory Efficiency**
- **Priority**: MUST
- **Target**: Use no more than 1 GB RAM for 500 MB file
- **Rationale**: Run on typical workstations without resource exhaustion
- **Acceptance Test**: Memory profiling during encode/decode of large files

**NFR-004: Startup Time**
- **Priority**: SHOULD
- **Target**: Command execution starts in < 2 seconds
- **Rationale**: Responsive CLI improves user experience
- **Acceptance Test**: Measure time from command invocation to first output

### 4.2 Reliability

**NFR-005: Data Integrity**
- **Priority**: MUST (CRITICAL)
- **Target**: 100% data accuracy (zero tolerance for data corruption)
- **Rationale**: Incorrect data could have severe consequences
- **Acceptance Test**: Encode/decode 1000 random files, verify cryptographic hashes match

**NFR-006: Transfer Success Rate**
- **ID**: NFR-006
- **Priority**: MUST-1 (Critical)
- **Owner**: Product Owner
- **Verification Method**: Test (automated + field testing)
- **Description**: System shall achieve high success rate under typical conditions
- **Target**: > 95% success rate
- **Typical Conditions Specification**:
  - **Lighting**: 300-700 lux (office lighting, not extreme darkness < 50 lux or direct sunlight glare)
  - **Distance**: 20-40 cm between camera and display
  - **Angle**: ±10° from perpendicular (not extreme angles > 30°)
  - **Camera**: 1080p minimum resolution, 30 fps recording
  - **Display**: 1920×1080 minimum, 80-100% brightness
  - **Stability**: Handheld camera (not tripod-mounted, normal hand tremor)
  - **Environment**: Indoor, stable (not moving vehicle)
- **Rationale**: System must work in realistic user environments
- **Acceptance Test**:
  - Test protocol: 100 transfers of 10 MB file
  - Test conditions: Within "typical conditions" specification above
  - Operators: 5 different users (varied experience levels)
  - Locations: 2 different office environments
  - Pass criteria: ≥ 95 successful decodes with 100% data integrity
  - Measurement: Track success rate, identify failure patterns

**NFR-007: Graceful Degradation**
- **ID**: NFR-007
- **Priority**: MUST-1 (Critical)
- **Owner**: Development Team
- **Verification Method**: Test (fuzz testing, error injection)
- **Description**: System shall fail safely without crashes or data corruption
- **Target Specifications**:
  - **No segmentation faults** or unhandled exceptions
  - **No data corruption** - partial writes shall be prevented or detected
  - **Exit codes 1-255** with descriptive error message for all failure modes
  - **No process hangs** - timeout > 30 seconds for any operation
  - **Resource cleanup** - temp files deleted even on error paths
- **Rationale**: System should fail safely, never corrupt data or leave orphaned processes
- **Acceptance Test**:
  - Fuzz testing with 1000 malformed videos
  - Error injection: corrupted files, invalid parameters, disk full, permission denied
  - Resource exhaustion: extremely large files, low memory, no disk space
  - Pass criteria: No crashes (exit code 0-255 only), no data corruption, clear error messages
  - Verification: valgrind for memory leaks, strace for system call errors

### 4.3 Usability

**NFR-008: Ease of Use**
- **Priority**: MUST
- **Target**: New user successfully transfers first file within 5 minutes of installation
- **Rationale**: Low barrier to entry increases adoption
- **Acceptance Test**: User testing with 5 new users, measure time to first successful transfer

**NFR-009: Error Message Quality**
- **ID**: NFR-009
- **Priority**: SHOULD-1 (High)
- **Owner**: UX/Development Team
- **Verification Method**: Demo (user testing with induced errors)
- **Description**: Error messages shall be clear, actionable, and user-friendly
- **Target**: 80% of users can resolve errors without external help
- **Error Message Standards**:
  - **Plain language**: Flesch reading ease score > 60 (Grade 8 level)
  - **Action-oriented**: Include specific recovery steps ("Try X" not "Error code Y")
  - **No jargon**: Avoid technical terms or explain them in parentheses
  - **Concise**: Maximum 200 characters for error summary
  - **Structured**: Error code + summary + details + suggestions
- **Rationale**: Self-service reduces support burden, improves user experience
- **Acceptance Test**:
  - User study: 10 participants, 5 induced error scenarios each
  - Measure: Time to resolution, need for external help
  - Pass criteria: ≥ 8 participants resolve ≥ 4 errors without help
  - Readability: All error messages pass Flesch-Kincaid test (Grade 8)

**NFR-010: Documentation Quality**
- **Priority**: MUST
- **Target**: README covers 100% of common use cases (encode, decode, verify)
- **Rationale**: Users shouldn't need to ask basic questions
- **Acceptance Test**: Documentation review against user questions

### 4.4 Compatibility

**NFR-011: Operating System Support**
- **Priority**: MUST
- **Target**: Works on macOS, Linux, Windows
- **Rationale**: Maximize reach across platforms
- **Acceptance Test**: Install and run on each OS, verify functionality

**NFR-012: Python Version**
- **Priority**: MUST
- **Target**: Python 3.9+ (support current and 2 previous major releases)
- **Rationale**: Balance modernity with compatibility
- **Acceptance Test**: Test on Python 3.9, 3.10, 3.11, 3.12

**NFR-013: Video Format Compatibility**
- **Priority**: MUST
- **Target**: Output videos playable on all major video players
- **Rationale**: Users need to verify videos visually
- **Acceptance Test**: Test playback on VLC, QuickTime, Windows Media Player

**NFR-014: Camera Compatibility**
- **Priority**: SHOULD
- **Target**: Work with any camera ≥ 1080p resolution
- **Minimum**: 720p with reduced grid size
- **Acceptance Test**: Test with various cameras and devices

### 4.5 Security

**NFR-015: Data Integrity Verification**
- **Priority**: MUST
- **Target**: Cryptographic verification of file integrity (cryptographic hash)
- **Rationale**: Detect any data tampering or corruption
- **Acceptance Test**: Verify tampered files are detected

**NFR-016: No Network Access**
- **Priority**: MUST
- **Target**: Zero network requests or external communication
- **Rationale**: Air-gapped security requirement
- **Acceptance Test**: Network monitoring during operation, verify no traffic

**NFR-017: Input Validation**
- **Priority**: MUST
- **Target**: All user inputs validated and sanitized
- **Rationale**: Prevent injection attacks and crashes
- **Acceptance Test**: Security testing with malicious inputs

**NFR-018: Privacy**
- **Priority**: SHOULD
- **Target**: No telemetry, analytics, or data collection
- **Rationale**: Users expect privacy in security tools
- **Acceptance Test**: Code review and network monitoring

**NFR-019: Confidentiality (Future)**
- **Priority**: MAY (Future Enhancement)
- **Target**: Optional encryption before encoding
- **Rationale**: Data is visible on screen during transfer
- **Note**: Not in MVP, but architecture should allow addition

### 4.6 Maintainability

### 4.7 Installability

**NFR-023: Easy Installation**
- **Priority**: MUST
- **Target**: Single command install via pip
- **Rationale**: Reduce installation friction
- **Acceptance Test**: Fresh virtual environment, measure steps to working install

**NFR-024: Dependency Management**
- **Priority**: MUST
- **Target**: All dependencies specified with version constraints
- **Rationale**: Reproducible installs
- **Acceptance Test**: Install in isolated environment

---

## 5. User Interface Requirements

### 5.1 Command-Line Interface

**UI-001: Encode Command**
```bash
qr-transfer encode <input_file> <output_video> [OPTIONS]

Required Arguments:
  input_file      Path to file to encode
  output_video    Path to output video ( video file)

Options:
  -g, --grid-size SIZE    QR code size: 177-1000 [default: 800]
  -f, --fps RATE          Frame rate: 5-30 fps [default: 10]
  --no-compress           Skip compression
  -q, --quiet             Suppress progress output
  -v, --verbose           Verbose logging
  -h, --help              Show this help

Examples:
  qr-transfer encode document.pdf video video file
  qr-transfer encode file.zip video video file -g 600
```

**UI-002: Decode Command**
```bash
qr-transfer decode <input_video> <output_file> [OPTIONS]

Required Arguments:
  input_video     Path to recorded video
  output_file     Path to output file

Options:
  --force             Overwrite existing output file
  --partial           Write partial file if incomplete
  -q, --quiet         Suppress progress output
  -v, --verbose       Verbose logging
  -h, --help          Show this help

Examples:
  qr-transfer decode video.mov document.pdf
  qr-transfer decode video video file output.bin --force
```

**UI-003: Verify Command**
```bash
qr-transfer verify <input_video> [OPTIONS]

Required Arguments:
  input_video     Path to video to verify

Options:
  -d, --detailed      Show detailed chunk information
  -h, --help          Show this help

Examples:
  qr-transfer verify video video file
```

**UI-004: Info Command**
```bash
qr-transfer info <input_video>

Required Arguments:
  input_video     Path to video

Examples:
  qr-transfer info video video file
```

### 5.2 Progress Display

**UI-005: Encoding Progress**
```
Encoding: document.pdf → video video file
Compressing... [OK] 1.2 MB → 890 KB (26% reduction)
Generating QR codes: [████████████████----] 80% (12/15 chunks)
Creating video... [OK]
✓ Encoded successfully in 2.3 seconds
  Grid size: 800×800 | Frame rate: 10 fps | File size: 4.5 MB
```

**UI-006: Decoding Progress**
```
Decoding: video video file → output.pdf
Extracting frames... [OK] 15 frames
Decoding QR codes: [████████████████----] 80% (12/15 chunks)
Reconstructing file... [OK]
Verifying integrity... [OK]
✓ Decoded successfully in 3.1 seconds
  Original size: 1.2 MB | Transfer speed: 387 KB/sec
```

**UI-007: Error Display**
```
✗ Decoding failed: Incomplete transfer

Details:
  Total chunks: 15
  Decoded: 12 (80%)
  Missing: 3 (chunks #4, #8, #12)

Suggestions:
  • Re-record the video with better lighting
  • Keep camera steady and at 20-40cm distance
  • Ensure display brightness is at maximum
  • Try with --grid-size 600 for easier scanning

Error code: INCOMPLETE_TRANSFER
```

### 5.3 Help & Documentation

**UI-008: Main Help**
```bash
$ qr-transfer --help

QR File Transfer - Air-gapped file transfer using animated QR codes

Usage: qr-transfer <command> [options]

Commands:
  encode    Encode a file into QR code video
  decode    Decode a video back to the original file
  verify    Verify video integrity without decoding
  info      Display video metadata

Options:
  -h, --help        Show this help
  -v, --version     Show version

Examples:
  qr-transfer encode document.pdf video video file
  qr-transfer decode video.mov document.pdf
  qr-transfer verify video video file

For more help: qr-transfer <command> --help
Documentation: https://github.com/jibeex/qr-file-transfer
```

---

## 6. System Constraints

### 6.1 Technical Constraints

**CON-001: File Size Limits**
- Maximum input file size: 1 GB (configurable)
- Rationale: Memory and processing time constraints
- Workaround: Split large files manually

**CON-002: Grid Size Limits**
- Minimum: 177×177 modules (QR Version 40 equivalent)
- Maximum: 1000×1000 modules (hardware scanning limit)
- Rationale: Below minimum = too slow, above maximum = unreliable scanning

**CON-003: Frame Rate Limits**
- Minimum: 5 fps (human readable)
- Maximum: 30 fps (camera capture limit)
- Rationale: Balance between speed and reliability

**CON-004: Video Compatibility**
- Output format: Industry-standard video format compatible with common video players
- Rationale: Universal playback compatibility required
- Note: High quality/lossless to avoid artifacts

### 6.2 Environmental Constraints

**CON-005: Display Requirements**
- Minimum resolution: 1920×1080 (Full HD)
- Recommended: Retina/High-DPI display
- Brightness: 80-100%
- Rationale: QR codes must be clearly visible

**CON-006: Camera Requirements**
- Minimum resolution: 1280×720 (720p)
- Recommended: 1920×1080+ (1080p or higher)
- Reference: iPhone 16 (48MP) is excellent
- Rationale: Must resolve individual QR modules

**CON-007: Lighting Requirements**
- Indoor lighting: Normal office lighting sufficient
- Avoid: Direct sunlight causing glare, very dim lighting
- Rationale: Camera must clearly capture QR codes

**CON-008: Scanning Distance**
- Optimal: 20-40 cm between camera and display
- Rationale: Balance between field of view and resolution

### 6.3 Operational Constraints

**CON-009: Platform Dependencies**
- Requires Python 3.9+ with pip
- Requires video and QR processing libraries
- May require system libraries (libzbar on Linux)

**CON-010: No Internet Required**
- System must function completely offline
- Installation may require internet for initial pip install

### 6.4 Business Constraints

**CON-011: Development Timeline**
- MVP must be ready within 6 weeks from requirements approval
- Rationale: Project deadline and resource availability

**CON-012: Budget Constraints**
- Zero budget for paid third-party libraries (open source only)
- No paid infrastructure or services
- Rationale: Project is open source, community-driven

**CON-013: Resource Constraints**
- Single full-time developer
- Part-time QA support (20% allocation)
- No dedicated UX designer (use best practices and community feedback)

**CON-014: Technology Constraints**
- Must use Python (no other languages for core functionality)
- Must work without GPU acceleration (CPU-only)
- Cannot require specialized hardware (no dedicated QR scanners)

---

## 7. Quality Attributes

### 7.1 Acceptance Criteria Summary

For the system to be considered complete and acceptable:

**Critical (Must Pass)**:
- ✓ Encode and decode any file type with 100% data integrity
- ✓ Transfer 10 MB file in < 30 seconds (end-to-end)
- ✓ Success rate > 95% under typical conditions
- ✓ No crashes or data corruption with any input
- ✓ Works on macOS, Linux, Windows
- ✓ Zero network access
- ✓ Comprehensive README with examples

**Important (Should Pass)**:
- ✓ New user successful within 5 minutes
- ✓ 80% of errors resolvable without support
- ✓ Encode 10 MB in < 5 seconds
- ✓ Memory usage < 1 GB for 500 MB file

**Nice-to-Have (May Pass)**:
- ✓ Batch processing support
- ✓ GUI application
- ✓ Mobile apps

---

## 8. Assumptions & Dependencies

### 8.1 Assumptions

1. Users have physical access to both source and destination systems
2. Users can record video (phone, webcam, camera)
3. Displays are capable of showing high-resolution video clearly
4. Users operate in reasonably lit environments
5. Users have basic command-line proficiency
6. Python and pip are available for installation

### 8.2 Dependencies

**External Systems**: None (fully self-contained)

**Third-Party Libraries**:
- Video processing library (third-party)
- QR code generation library (third-party)
- QR code decoding library (third-party)
- Image handling library (third-party)
- Numerical computing library (third-party)

**Hardware**:
- Source system: Computer with display (1920×1080 minimum)
- Destination system: Computer with video file capability
- Transfer medium: Camera/phone capable of 1080p video recording (iPhone 16 recommended)

### 8.3 Assumption Validation Status

| ID | Assumption | Risk if Wrong | Validation Status | Mitigation |
|----|------------|---------------|-------------------|------------|
| ASM-001 | Users have physical access to both systems | High - core use case blocked | ✓ Verified (inherent to air-gapped scenario) | None needed |
| ASM-002 | Users can record video | High - core functionality blocked | ✓ Verified (smartphones ubiquitous) | Document camera requirements |
| ASM-003 | Displays show high-res video clearly | Medium - affects reliability | ⚠️ Assumed (need testing) | Test with various display types |
| ASM-004 | Users operate in reasonably lit environments | Medium - affects success rate | ⚠️ Assumed (need testing) | Document lighting requirements, add troubleshooting |
| ASM-005 | Users have basic CLI proficiency | Low - training can address | ✓ Verified (target users are IT/security professionals) | Provide good documentation and examples |
| ASM-006 | Python 3.9+ available | Medium - installation blocker | ⚠️ Assumed (varies by environment) | Document installation for older systems, provide troubleshooting |
| ASM-007 | **800×800 QR codes scannable with iPhone 16** | **Critical - performance targets depend on this** | 🔲 **NOT VALIDATED - POC REQUIRED** | **Week 0: Hardware testing mandatory before implementation** |
| ASM-008 | **iPhone 16 can decode reliably at 10fps** | **Critical - transfer speed depends on this** | 🔲 **NOT VALIDATED - POC REQUIRED** | **Week 0: Performance testing mandatory** |
| ASM-009 | compression reduces file sizes meaningfully | Low - worst case no compression | ⚠️ Assumed (typical 20-40% reduction) | Make compression optional |
| ASM-010 | System shall support QR grid sizes up to 1000×1000 | High - limits maximum performance | 🔲 **NOT VALIDATED - POC REQUIRED** | **Week 0: Library capability testing** |

**Critical Assumptions Requiring Immediate Validation**:
- ASM-007, ASM-008, ASM-010 must be validated via POC before proceeding to implementation

---

## 9. Success Metrics

### 9.1 User Success Metrics

| Metric | Target | Measurement Method | Frequency | Owner | Action if Below Target |
|--------|--------|-------------------|-----------|-------|------------------------|
| Time to first successful transfer | < 5 minutes | User testing with new users | End of each sprint | UX Lead | Simplify docs, improve error messages |
| Transfer success rate | > 95% | Automated testing + user feedback | Weekly (dev), Monthly (prod) | QA Lead | Investigate failures, investigate and resolve failures |
| User satisfaction (ease of use) | > 4/5 rating | User survey | Monthly | Product Owner | UX improvements, feature refinement |
| Support request rate | < 10% of users | Support ticket tracking | Weekly | Support Lead | Improve documentation, add troubleshooting |

### 9.2 Technical Success Metrics

| Metric | Target | Measurement Method | Frequency | Owner | Action if Below Target |
|--------|--------|-------------------|-----------|-------|------------------------|
| Data integrity | 100% accuracy | Automated hash verification | Every build (CI/CD) | Dev Lead | Block release until fixed |
| Performance (10MB file) | < 25 seconds | Performance testing suite | Daily | Dev Lead | Profile and optimize bottlenecks |
| Memory efficiency | < 1GB for 500MB file | Memory profiling | Weekly | Dev Lead | Optimize memory usage, add streaming |
| Test coverage | > 80% | coverage.py in CI | Every commit | Dev Lead | No merge until threshold met |
| Bug escape rate | < 1 critical bug per release | Issue tracking | Per release | QA Lead | Improve test coverage, add regression tests |

### 9.3 Baseline Measurements

(To be established during POC phase)

| Metric | Expected Baseline | Actual Baseline | Notes |
|--------|-------------------|-----------------|-------|
| Encoding speed (10MB) | 3-5 seconds | TBD | Measure during POC |
| Decoding speed (10MB) | 10-15 seconds | TBD | Measure during POC |
| QR detection success | > 98% | TBD | Measure during POC |
| Transfer success (ideal conditions) | > 99% | TBD | Measure during POC |

---

## 10. Open Questions & Decisions

### 10.1 Open Questions

| ID | Question | Impact | Options | Decision Criteria | Owner | Due Date | Status |
|----|----------|--------|---------|-------------------|-------|----------|--------|
| OQ-001 | Should filenames be encrypted/anonymized in metadata? | Privacy vs usability | 1) Always anonymize 2) Optional flag 3) Never anonymize | User feedback + security review + GDPR compliance | Security Lead | Week 0 | **Resolved → Optional flag (`--anonymize-metadata`); see CR-001** |
| OQ-002 | Should we support partial file recovery? | Complexity vs UX | 1) Yes (retry missing chunks) 2) No (full retry only) 3) Defer to v2 | Development effort vs user benefit analysis | Product Owner | Design phase | Open |
| OQ-003 | What should happen if video contains multiple files? | Error handling | 1) Error immediately 2) Support multi-file 3) Warn but decode first | Technical feasibility + scope | Tech Lead | Design phase | Open |
| OQ-004 | Should system support streaming (display while encoding)? | Architecture complexity | 1) Yes (real-time) 2) No (file-based) 3) v2 feature | Memory constraints + complexity | Tech Lead | Design phase | Open |
| OQ-005 | What compression level should be default? | Speed vs size tradeoff | 1) None 2) Fast (level 1) 3) Balanced (level 6) 4) Best (level 9) | Performance testing results | Dev Lead | Implementation | **Resolved → [ADR-004](./adr/004-compression.md)** |
| OQ-006 | Should we support resume/checkpoint for large files? | Reliability vs complexity | 1) Yes (checkpoint every N chunks) 2) No (restart on failure) | User feedback on large file transfers | Product Owner | After MVP | Open |

### 10.2 Architecture Decision Records

Implementation decisions (why each technical choice was made) are recorded in individual ADR files. ADRs are immutable once accepted — superseded by a new ADR, never edited.

| ADR | Title | Status |
|----|-------|--------|
| [ADR-001](./adr/001-default-grid-size.md) | Default QR Grid Size (800×800) | Accepted |
| [ADR-002](./adr/002-cli-only-mvp.md) | CLI-Only Interface for MVP | Accepted |
| [ADR-003](./adr/003-video-format.md) | Video Output Format (MP4/H.264) | Accepted |
| [ADR-004](./adr/004-compression.md) | Data Compression (gzip, Level 6) | Accepted |
| [ADR-005](./adr/005-integrity-algorithm.md) | Integrity Verification (SHA-256 + CRC32) | Accepted |
| [ADR-006](./adr/006-max-file-size.md) | Maximum Input File Size (1 GB) | Accepted |

### 10.3 Pending Decisions (Require Input)

**High Priority**:
- OQ-001: Privacy/anonymization strategy - **Blocks security review**
- OQ-005: Compression level - **Affects performance testing**

**Medium Priority**:
- OQ-002: Partial recovery support - **Affects architecture design**
- OQ-004: Streaming support - **Affects memory architecture**

**Low Priority**:
- OQ-003: Multi-file handling - **Edge case, can defer**
- OQ-006: Resume/checkpoint - **Future enhancement**

---

## 11. Future Enhancements (Not in MVP)

**v2.0 - Enhanced Features**:
- FR-014: Batch processing (encode multiple files)
- FR-015: Resume capability (continue interrupted transfers)
- FR-016: Selective chunk retransmission
- FR-017: 4-color QR codes (2× capacity)

**v3.0 - Platform Expansion**:
- FR-018: GUI application (desktop)
- FR-019: Mobile apps (iOS/Android with camera integration)
- FR-020: Real-time mode (instant display → scan → decode)

**v4.0 - Security Enhancements**:
- FR-021: Optional encryption (AES-256-GCM)
- FR-022: Digital signatures for authenticity
- FR-023: Metadata anonymization

---

## 12. Glossary

See [docs/GLOSSARY.md](./GLOSSARY.md) for all term definitions. Key terms used in this document: air-gapped, chunk, grid size, module, frame, metadata frame, encode, decode, integrity.

---

## 13. Approval

### 13.1 Approval Criteria

Before approval, each stakeholder role must verify the following:

**Product Owner**:
- [ ] All functional requirements align with product vision and scope
- [ ] Success metrics are achievable and meaningful
- [ ] Open questions have resolution plans or timeline
- [ ] Business constraints are realistic
- [ ] Out of scope items are clearly documented

**Technical Lead**:
- [ ] All requirements are technically feasible
- [ ] Constraints are realistic and achievable
- [ ] Dependencies are identified and manageable
- [ ] Critical assumptions (ASM-007, ASM-008, ASM-010) have validation plan
- [ ] Architecture can support all MUST requirements

**Security Lead**:
- [ ] Security requirements (§4.5, NFR-015 to NFR-019) are sufficient
- [ ] Privacy requirements comply with regulations (CR-001)
- [ ] No security gaps or vulnerabilities identified
- [ ] Data requirements (DR-001 to DR-003) are secure
- [ ] Negative use case (UC-005) mitigations are documented

**QA Lead**:
- [ ] All requirements are testable (have measurable acceptance criteria)
- [ ] Acceptance criteria are clear and unambiguous
- [ ] Test approach is feasible with available resources
- [ ] Verification methods specified for all requirements
- [ ] Success metrics are measurable

**IT Operations**:
- [ ] Installability requirements (§4.7) are achievable
- [ ] Operational constraints are documented
- [ ] Support and troubleshooting considerations addressed
- [ ] No operational blockers identified

**Compliance Officer** (if applicable):
- [ ] Regulatory requirements identified and addressed
- [ ] Privacy compliance (GDPR) requirements met (CR-001)
- [ ] Accessibility compliance planned (CR-002)
- [ ] No legal or compliance blockers

### 13.2 Approval Process

**Timeline**: 2 weeks from draft completion to final sign-off

1. **Draft Review** (Week 1, Days 1-3):
   - Stakeholders review draft independently
   - Provide feedback via comments or review meetings
   - Focus areas: completeness, feasibility, testability

2. **Revision** (Week 1, Days 4-5):
   - Requirements team addresses feedback
   - Update document with changes
   - Resolve open questions where possible

3. **Final Review** (Week 2, Days 1-2):
   - Stakeholders verify changes address feedback
   - Confirm approval criteria met
   - Raise any final concerns

4. **Sign-off** (Week 2, Day 3):
   - Formal approval signatures collected
   - Document status changed from "Draft" to "Approved"

5. **Baseline** (Week 2, Day 3):
   - Requirements baselined in version control
   - Future changes require formal change request process

### 13.3 Change Request Process

After requirements are approved and baselined, any changes require:

**Change Request Procedure**:
1. Submitter creates change request (CR) with:
   - Requirement ID(s) affected
   - Proposed change description
   - Rationale for change
   - Impact assessment (schedule, resources, dependencies)

2. Product Owner reviews CR:
   - Assess business impact
   - Prioritize against other work
   - Accept, reject, or defer decision

3. If accepted, stakeholder review:
   - Technical Lead: feasibility and design impact
   - QA Lead: testing impact
   - Security Lead: security implications (if applicable)

4. Approval and implementation:
   - Product Owner grants final approval
   - Requirements document updated with revision history
   - Traceability updated (design, code, tests impacted)
   - All stakeholders notified of change

**Change Request Template**:
```
CR-ID: CR-[YYYY]-[NNN]
Date: [Date]
Submitter: [Name/Role]
Affected Requirements: [FR-XXX, NFR-YYY]
Type: [Addition | Modification | Deletion]
Priority: [Critical | High | Medium | Low]

Description:
[What needs to change and why]

Impact Analysis:
- Schedule: [X days/weeks delay or no impact]
- Resources: [Additional resources needed]
- Dependencies: [Other requirements affected]
- Risk: [Risks introduced by this change]

Approval:
[ ] Product Owner: __________ Date: ____
[ ] Technical Lead: _________ Date: ____
[ ] Security Lead: __________ Date: ____ (if security-related)
```


### 13.3.1 Change Tracking System

**Selected Tool**: GitHub Issues with Custom Labels

**Configuration**:
- Repository: qr-file-transfer
- Labels:
  - `requirement-change`: Change to existing requirement
  - `requirement-new`: New requirement proposed
  - `requirement-delete`: Requirement removal
  - `priority-critical`: Urgent change needed
  - `priority-high`: Important change
  - `priority-medium`: Standard change
  - `priority-low`: Nice-to-have change
  - `impact-high`: Affects multiple components
  - `impact-medium`: Affects single component
  - `impact-low`: Documentation or minor change
  - `status-proposed`: Awaiting review
  - `status-approved`: Approved, ready for implementation
  - `status-rejected`: Not approved
  - `status-implemented`: Change completed

**Custom Fields** (GitHub Project):
- Affected Requirements: [FR-XXX, NFR-YYY]
- Impact Analysis: [Schedule, Resources, Dependencies]
- Approval Status: [Pending, Approved, Rejected]
- Implementation Status: [Not Started, In Progress, Complete]

### 13.3.2 Change Impact Analysis Template

```markdown
# Change Request: [Title]

## CR Information
- **CR-ID**: CR-YYYY-NNN
- **Date Submitted**: YYYY-MM-DD
- **Submitter**: [Name/Role]
- **Type**: [Addition | Modification | Deletion]
- **Priority**: [Critical | High | Medium | Low]

## Affected Requirements
- Primary: [REQ-ID]
- Related: [REQ-ID, REQ-ID]

## Change Description
### Current State
[What exists now]

### Proposed Change
[What should change]

### Rationale
[Why this change is needed]

## Impact Analysis

### Schedule Impact
- Estimated effort: [X hours/days]
- Delay to milestone: [X days] or [No impact]
- Critical path affected: [Yes/No]

### Resource Impact
- Developer time: [X hours]
- QA time: [X hours]
- Additional resources needed: [None / List]

### Technical Impact
- Design changes required: [Yes/No - describe]
- Components affected: [List]
- Test cases affected: [List]
- Documentation affected: [List]

### Dependency Impact
- Other requirements affected: [List]
- External dependencies: [List]
- Integration points: [List]

### Risk Assessment
- Technical risk: [Low/Medium/High - describe]
- Schedule risk: [Low/Medium/High - describe]
- Business risk: [Low/Medium/High - describe]
- Mitigation plan: [Describe]

## Traceability Update Required
- [ ] Requirements document (REQUIREMENTS.md)
- [ ] Design document (DESIGN.md)
- [ ] Implementation (source code)
- [ ] Test cases
- [ ] RTM (Appendix A)
- [ ] Documentation (README, etc.)

## Approval

### Reviews Required
- [ ] Product Owner: __________ Date: ____
- [ ] Technical Lead: __________ Date: ____
- [ ] Security Lead: ___________ Date: ____ (if security-related)
- [ ] QA Lead: ________________ Date: ____

### Decision
- [ ] Approved - Proceed with implementation
- [ ] Approved with conditions - [List conditions]
- [ ] Rejected - [Reason]
- [ ] Deferred - [Reason and future review date]

### Implementation Plan
- Assigned to: [Developer name]
- Target completion: [Date]
- Verification method: [How to verify change is complete]
```

### 13.3.3 Change Control Board (if needed)

**For this project size (1 developer), formal CCB not required.**

If project scales beyond 5 people, establish CCB:
- **Chair**: Product Owner
- **Members**: Technical Lead, Security Lead, QA Lead
- **Meeting frequency**: Weekly or as-needed
- **Quorum**: 3 of 4 members
- **Decision authority**: Chair has final say on ties

### 13.3.4 Change Request Workflow

```
┌──────────────────┐
│  Change Request  │
│    Submitted     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Product Owner   │
│   Initial Review │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
   Reject   Accept
    │         │
    ▼         ▼
  Close  ┌──────────────────┐
         │  Impact Analysis │
         │  by Tech Lead    │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Stakeholder      │
         │ Review           │
         └────────┬─────────┘
                  │
         ┌────────┴────────┐
         │                 │
      Approve           Reject
         │                 │
         ▼                 ▼
┌──────────────────┐    Close
│  Update RTM      │
│  & Documents     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Implementation  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Verification    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Close CR        │
└──────────────────┘
```

### 13.3.5 Emergency Changes

For critical security or production issues:

**Fast-track Process**:
1. Security/Production issue identified
2. Technical Lead assesses severity
3. If CRITICAL: Implement immediately, document retroactively
4. If HIGH: Product Owner verbal approval, formal CR within 24h
5. Notify all stakeholders within 24 hours
6. Formal CR and impact analysis completed post-implementation
7. Lessons learned documented

**Criteria for Emergency Change**:
- Security vulnerability actively exploited
- Data integrity compromised
- Complete system failure
- Cannot wait for normal CR process

### 13.3.6 Change Metrics

Track the following metrics:

| Metric | Target | Purpose |
|--------|--------|---------|
| Average CR turnaround time | < 5 days | Measure efficiency |
| CR approval rate | 60-80% | Balance quality vs. agility |
| Requirements volatility | < 10% per sprint | Measure stability |
| Impact of changes | < 20% high-impact | Minimize disruption |
| Emergency changes | < 5% of total | Process effectiveness |

**Review quarterly**: If metrics outside targets, adjust process.


### 13.4 Approval Sign-off

| Role | Name | Signature | Date | Comments |
|------|------|-----------|------|----------|
| Product Owner | | | | Final authority on all requirements |
| Technical Lead | | | | Technical feasibility confirmed |
| Security Lead | | | | Security requirements adequate |
| QA Lead | | | | All requirements testable |
| IT Operations Lead | | | | Operational requirements feasible |
| Compliance Officer | | | | Regulatory compliance addressed |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-27 | System | Initial requirements specification (separated from design) |

---

**Next Document**: See [DESIGN.md](./DESIGN.md) for technical architecture and implementation details.

## Appendix A: Requirements Traceability Matrix

The Requirements Traceability Matrix (RTM) links each requirement to its design specification, implementation, and test cases. This enables forward and backward traceability throughout the development lifecycle.

**Status Legend**:
- Draft: Requirement defined, not yet approved
- Approved: Stakeholder sign-off complete
- Designed: Design specification completed
- Implemented: Code complete
- Tested: Test cases pass
- Verified: Acceptance criteria validated

### A.1 Functional Requirements Traceability

| Req ID | Requirement Summary | Design Ref | Implementation | Test Case | Status | Notes |
|--------|---------------------|------------|----------------|-----------|--------|-------|
| FR-001 | Encode any file type | DESIGN.md §2.1 | src/encoder.py | TC-FR-001 | Draft | Core encoding functionality |
| FR-002 | Simple encoding command | DESIGN.md §4.1 | src/cli.py | TC-FR-002 | Draft | CLI entry point |
| FR-003 | Fast transfer speed | DESIGN.md §2.1, §3.2 | src/encoder.py | TC-FR-003 | Draft | Performance critical |
| FR-004 | Progress visibility | DESIGN.md §2.1 | src/progress.py | TC-FR-004 | Draft | UX requirement |
| FR-005 | Customizable grid size | DESIGN.md §2.1 | src/qr_generator.py | TC-FR-005 | Draft | Flexibility requirement |
| FR-006 | Decode video to file | DESIGN.md §2.2 | src/decoder.py | TC-FR-006 | Draft | Core decoding functionality |
| FR-007 | Verify file integrity | DESIGN.md §2.2, §2.4 | src/integrity.py | TC-FR-007 | Draft | Security critical |
| FR-008 | Handle imperfect captures | DESIGN.md §2.2 | src/decoder.py | TC-FR-008 | Draft | Reliability requirement |
| FR-009 | Clear error messages | DESIGN.md §4.2 | src/errors.py | TC-FR-009 | Draft | UX requirement |
| FR-010 | Report missing data | DESIGN.md §2.2 | src/decoder.py | TC-FR-010 | Draft | Error handling |
| FR-011 | Verify without decode | DESIGN.md §2.2 | src/verify.py | TC-FR-011 | Draft | Quick validation |
| FR-012 | Display file metadata | DESIGN.md §2.2 | src/metadata.py | TC-FR-012 | Draft | Information display |
| FR-013 | Help documentation | DESIGN.md §4.1 | src/cli.py | TC-FR-013 | Draft | User assistance |

### A.2 Non-Functional Requirements Traceability

| Req ID | Requirement Summary | Design Ref | Implementation | Test Case | Status | Notes |
|--------|---------------------|------------|----------------|-----------|--------|-------|
| NFR-001 | Transfer speed 400KB/s | DESIGN.md §3.2 | src/encoder.py, src/decoder.py | TC-NFR-001 | Draft | Performance target |
| NFR-002 | Encoding performance | DESIGN.md §2.1 | src/encoder.py | TC-NFR-002 | Draft | Encoding optimization |
| NFR-003 | Memory efficiency | DESIGN.md §2.5 | All modules | TC-NFR-003 | Draft | Resource management |
| NFR-004 | Startup time < 2s | DESIGN.md §4.1 | src/cli.py | TC-NFR-004 | Draft | Responsiveness |
| NFR-005 | Data integrity 100% | DESIGN.md §2.4 | src/integrity.py | TC-NFR-005 | Draft | Security critical |
| NFR-006 | Success rate > 95% | DESIGN.md §2.2 | src/decoder.py | TC-NFR-006 | Draft | Reliability target |
| NFR-007 | Graceful degradation | DESIGN.md §4.2 | All modules | TC-NFR-007 | Draft | Error handling |
| NFR-008 | Ease of use | DESIGN.md §4.1 | src/cli.py | TC-NFR-008 | Draft | UX validation |
| NFR-009 | Error message quality | DESIGN.md §4.2 | src/errors.py | TC-NFR-009 | Draft | UX requirement |
| NFR-010 | Documentation quality | N/A | README.md | TC-NFR-010 | Draft | Documentation review |
| NFR-011 | OS support (Mac/Linux/Win) | DESIGN.md §5.1 | All modules | TC-NFR-011 | Draft | Cross-platform |
| NFR-012 | Python 3.9+ support | DESIGN.md §5.1 | All modules | TC-NFR-012 | Draft | Version compatibility |
| NFR-013 | Video format compatibility | DESIGN.md §2.3 | src/video_encoder.py | TC-NFR-013 | Draft | Format compliance |
| NFR-014 | Camera compatibility | N/A | N/A | TC-NFR-014 | Draft | Hardware testing |
| NFR-015 | Data integrity verification | DESIGN.md §2.4 | src/integrity.py | TC-NFR-015 | Draft | Security requirement |
| NFR-016 | No network access | DESIGN.md §5.2 | All modules | TC-NFR-016 | Draft | Security requirement |
| NFR-017 | Input validation | DESIGN.md §4.2 | All modules | TC-NFR-017 | Draft | Security requirement |
| NFR-018 | Privacy (no telemetry) | DESIGN.md §5.2 | All modules | TC-NFR-018 | Draft | Privacy requirement |
| NFR-019 | Confidentiality (future) | TBD | N/A | N/A | Deferred | v2.0 feature |
### A.3 Data Requirements Traceability

| Req ID | Requirement Summary | Design Ref | Implementation | Test Case | Status | Notes |
|--------|---------------------|------------|----------------|-----------|--------|-------|
| DR-001 | Video file format spec | DESIGN.md §3.1 | src/video_encoder.py | TC-DR-001 | Draft | standard video format H.264 specification |
| DR-002 | Metadata frame structure | DESIGN.md §3.3 | src/metadata.py | TC-DR-002 | Draft | JSON metadata format |
| DR-003 | Chunk binary format | DESIGN.md §3.4 | src/chunking.py | TC-DR-003 | Draft | Binary protocol |

### A.4 Interface Requirements Traceability

| Req ID | Requirement Summary | Design Ref | Implementation | Test Case | Status | Notes |
|--------|---------------------|------------|----------------|-----------|--------|-------|
| IR-001 | CLI interface contract | DESIGN.md §4.1 | src/cli.py | TC-IR-001 | Draft | POSIX conventions |
| IR-002 | Error code specification | DESIGN.md §4.2 | src/errors.py | TC-IR-002 | Draft | Exit code standards |

### A.5 Compliance Requirements Traceability

| Req ID | Requirement Summary | Design Ref | Implementation | Test Case | Status | Notes |
|--------|---------------------|------------|----------------|-----------|--------|-------|
| CR-001 | Privacy compliance (GDPR) | DESIGN.md §5.2 | src/metadata.py | TC-CR-001 | Draft | Anonymization option |
| CR-002 | Accessibility (WCAG 2.1) | DESIGN.md §4.1 | src/cli.py | TC-CR-002 | Draft | Screen reader support |
| CR-003 | Export control (future) | TBD | N/A | N/A | Deferred | If encryption added |

### A.6 Use Case Traceability

| Use Case | Related Requirements | Design Ref | Test Scenario | Status |
|----------|---------------------|------------|---------------|--------|
| UC-001: Config file transfer | FR-001, FR-002, FR-006, FR-007 | DESIGN.md §6.1 | TS-UC-001 | Draft |
| UC-002: Crypto key transfer | FR-001, FR-007, NFR-015 | DESIGN.md §6.2 | TS-UC-002 | Draft |
| UC-003: Document package | FR-001, FR-003, FR-006 | DESIGN.md §6.3 | TS-UC-003 | Draft |
| UC-004: Emergency credentials | FR-001, FR-002, FR-003 | DESIGN.md §6.4 | TS-UC-004 | Draft |
| UC-005: Misuse scenario | CR-001, NFR-016, NFR-018 | DESIGN.md §5.2 | N/A | Draft |

### A.7 Traceability Maintenance

**Ownership**: Development Team Lead

**Update Frequency**: 
- Weekly during active development
- After each requirement change (via CR process)
- Before each release

**Process**:
1. Developer updates RTM when implementing requirement
2. Tester updates RTM when test case created
3. QA verifies RTM completeness during sprint review
4. Tech Lead reviews RTM completeness during release preparation

**Tools**:
- Current: Markdown table (simple, version controlled)
- Future: Consider JIRA/GitHub Issues with custom fields for larger project

---

**Document Complete**: All identified gaps from gap analysis have been addressed.
