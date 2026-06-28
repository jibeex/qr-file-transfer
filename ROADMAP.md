# Implementation Roadmap

**Owner**: Tech Lead  
**Review trigger**: After each phase completes; update sprint tasks weekly  
See also: [docs/DESIGN.md](./docs/DESIGN.md), [docs/TEST_PLAN.md](./docs/TEST_PLAN.md)

---


### 10.1 Development Phases

**Fulfills Requirements**: CON-011 (6-week timeline)

```
Timeline Overview:
─────────────────────────────────────────────────────────
Week 0: Requirements & POC          [CRITICAL]
Week 1-2: Core Implementation       [Foundation]
Week 3-4: Features & Integration    [Build]
Week 5: Testing & Polish            [Quality]
Week 6: Documentation & Release     [Delivery]
```

### 10.2 Week 0: Requirements Validation & POC

**Duration**: 3-5 days
**Status**: MANDATORY before Week 1
**Owner**: Tech Lead

**Critical Assumptions to Validate** (from REQUIREMENTS.md Appendix):
- ASM-007: 800×800 QR codes scannable with iPhone 16
- ASM-008: iPhone 16 can decode reliably at 10fps
- ASM-010: System shall support QR grid sizes up to 1000×1000

**POC Objectives**:
1. Validate hardware capabilities
2. Test QR code generation/detection at target sizes
3. Measure actual performance vs. targets
4. Identify technical blockers

**Deliverables**:
- [ ] Hardware test report (iPhone 16 + MacBook Pro)
- [ ] QR capacity validation (bytes per QR at 800×800)
- [ ] Performance baseline measurements
- [ ] Go/No-Go decision document

**POC Script**:
```python
# poc_test.py - Hardware validation script

import qrcode
import pyzbar.pyzbar
import cv2
import time
from PIL import Image

def test_qr_capacity(grid_size=800):
    """Test QR code capacity at specified grid size."""
    data_sizes = [500, 1000, 1500, 2000, 2500, 2800, 3000]
    
    for size in data_sizes:
        test_data = b'X' * size
        
        try:
            # Generate QR
            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(test_data)
            qr.make(fit=True)
            img = qr.make_image()
            
            # Decode QR
            decoded = pyzbar.pyzbar.decode(img)
            
            if decoded and decoded[0].data == test_data:
                print(f"✓ {size} bytes: SUCCESS")
            else:
                print(f"✗ {size} bytes: DECODE FAILED")
        except Exception as e:
            print(f"✗ {size} bytes: ERROR - {e}")
            break
    
    # Conclusion: Maximum reliable size
    print(f"\nRecommended max chunk size: 2800 bytes")

def test_detection_speed():
    """Test QR detection performance."""
    # Create test QR code
    qr = qrcode.QRCode()
    qr.add_data(b'Test data' * 100)
    qr.make()
    img = qr.make_image()
    
    # Convert to OpenCV format
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Benchmark detection
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        decoded = pyzbar.pyzbar.decode(cv_img)
    
    elapsed = time.time() - start
    avg_time = elapsed / iterations
    
    print(f"Average detection time: {avg_time*1000:.2f} ms")
    print(f"Max FPS: {1/avg_time:.1f}")

if __name__ == '__main__':
    test_qr_capacity()
    test_detection_speed()
```

**Exit Criteria**:
- [ ] All critical assumptions validated OR
- [ ] Alternative parameters identified (e.g., grid_size=600 if 800 fails)
- [ ] Performance targets achievable OR
- [ ] Revised targets documented

### 10.3 Week 1-2: Core Implementation

**Duration**: 10 working days
**Goal**: Functional encode/decode pipeline

**Week 1 Tasks**:

**Day 1-2: Foundation**
- [ ] Project structure setup
- [ ] Dependencies installation and testing
- [ ] Constants and configuration (constants.py)
- [ ] Data structures (protocols.py: Chunk, Metadata)
- [ ] Error hierarchy (errors.py)

**Day 3-4: Encoding Pipeline**
- [ ] FileEncoder class (core/encoder.py)
- [ ] Compression utility (utils/compression.py)
- [ ] Integrity utility (utils/integrity.py)
- [ ] Chunking algorithm
- [ ] Basic unit tests

**Day 5: QR Generation**
- [ ] QRGenerator class (qr/generator.py)
- [ ] Grid size configuration
- [ ] Test with various data sizes
- [ ] Unit tests

**Week 2 Tasks**:

**Day 6-7: Video Encoding**
- [ ] VideoEncoder class (video/encoder.py)
- [ ] MP4/H.264 output
- [ ] Frame generation pipeline
- [ ] Test video playback

**Day 8-9: Decoding Pipeline**
- [ ] FileDecoder class (core/decoder.py)
- [ ] QRDetector class (qr/detector.py)
- [ ] VideoDecoder class (video/decoder.py)
- [ ] Reconstruction algorithm
- [ ] Unit tests

**Day 10: Integration**
- [ ] End-to-end encode/decode test
- [ ] Integrity verification
- [ ] Bug fixes
- [ ] Code review

**Deliverables**:
- [ ] Working encode/decode pipeline
- [ ] Unit tests (60%+ coverage)
- [ ] Basic CLI (encode/decode commands only)
- [ ] Demo video successful

### 10.4 Week 3-4: Features & Integration

**Duration**: 10 working days
**Goal**: Complete feature set

**Week 3 Tasks**:

**Day 11-12: CLI Enhancement**
- [ ] Full CLI implementation (cli.py)
- [ ] Argument parsing
- [ ] Help system
- [ ] Progress tracking (utils/progress.py)
- [ ] Error messages

**Day 13-14: Additional Commands**
- [ ] Verify command
- [ ] Info command
- [ ] Input validation (utils/validation.py)
- [ ] File operations (utils/file_ops.py)

**Day 15: Error Handling**
- [ ] Exception handling throughout
- [ ] User-friendly error messages
- [ ] Exit codes
- [ ] Recovery suggestions

**Week 4 Tasks**:

**Day 16-17: Performance Optimization**
- [ ] Parallel QR generation
- [ ] Memory optimization
- [ ] Streaming architecture
- [ ] Performance benchmarks

**Day 18-19: Edge Cases & Robustness**
- [ ] Handle imperfect captures
- [ ] Duplicate frame detection
- [ ] Missing chunk handling
- [ ] Partial file recovery

**Day 20: Integration Testing**
- [ ] End-to-end test suite
- [ ] Error injection testing
- [ ] Performance validation
- [ ] Cross-platform testing

**Deliverables**:
- [ ] Complete feature set
- [ ] Full CLI with all commands
- [ ] Performance targets met
- [ ] Integration tests (70%+ coverage)

### 10.5 Week 5: Testing & Polish

**Duration**: 5 working days
**Goal**: Production-ready quality

**Day 21-22: Comprehensive Testing**
- [ ] Unit test completion (80%+ coverage)
- [ ] Integration test expansion
- [ ] Security testing
- [ ] Fuzz testing
- [ ] Real-world scenario testing

**Day 23: Cross-Platform Validation**
- [ ] macOS testing (primary)
- [ ] Linux testing (Ubuntu, Debian)
- [ ] Windows testing (Windows 10/11)
- [ ] Installation verification
- [ ] Dependency validation

**Day 24: Performance Tuning**
- [ ] Profile encoding/decoding
- [ ] Optimize bottlenecks
- [ ] Memory profiling
- [ ] Benchmark against targets
- [ ] Adjust parameters if needed

**Day 25: Bug Fixes & Polish**
- [ ] Fix all critical bugs
- [ ] Fix high-priority bugs
- [ ] UX improvements
- [ ] Error message refinement
- [ ] Code cleanup

**Deliverables**:
- [ ] 80%+ test coverage
- [ ] All tests passing
- [ ] Performance targets met
- [ ] Zero critical bugs
- [ ] Cross-platform verified

### 10.6 Week 6: Documentation & Release

**Duration**: 5 working days
**Goal**: Public release

**Day 26-27: Documentation**
- [ ] README.md (user guide)
- [ ] API.md (developer docs)
- [ ] CONTRIBUTING.md
- [ ] Installation guide
- [ ] Troubleshooting guide
- [ ] Examples and tutorials

**Day 28: Package Preparation**
- [ ] setup.py / pyproject.toml
- [ ] requirements.txt
- [ ] PyPI metadata
- [ ] LICENSE file
- [ ] CHANGELOG.md

**Day 29: Release Process**
- [ ] Version tagging (v1.0.0)
- [ ] PyPI upload (test.pypi.org first)
- [ ] GitHub release
- [ ] Installation verification
- [ ] Announcement preparation

**Day 30: Launch & Support**
- [ ] PyPI release
- [ ] Documentation live
- [ ] Community announcement
- [ ] Monitor feedback
- [ ] Issue triage process

**Deliverables**:
- [ ] Complete documentation
- [ ] PyPI package published
- [ ] GitHub release v1.0.0
- [ ] Public announcement
- [ ] Support process established

### 10.7 Risk Mitigation

**Technical Risks**:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| QR capacity insufficient | Medium | High | POC validation in Week 0; fallback to smaller chunks |
| Camera detection unreliable | Low | High | Enhanced preprocessing; multiple detection attempts |
| Performance targets missed | Medium | Medium | Parallel processing; optimize critical path |
| Cross-platform issues | Medium | Medium | Early multi-platform testing; CI/CD |
| Dependency conflicts | Low | Low | Pin versions; virtual environment |

**Schedule Risks**:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Week 0 POC fails | Low | Critical | Have fallback parameters ready |
| Integration issues | Medium | High | Continuous integration; daily builds |
| Testing reveals major bugs | Medium | High | Buffer time in Week 5; prioritize critical |
| Documentation delay | Low | Low | Write docs alongside code |

**Resource Risks**:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Single developer constraint | High | Medium | Clear priorities; ruthless scope management |
| Hardware availability | Low | Medium | Use cloud VMs for testing |
| Library breaking changes | Low | High | Pin dependency versions |

### 10.8 Success Criteria

**Mandatory** (Must have for v1.0):
- [ ] Encode any file type ≤ 1 GB (FR-001)
- [ ] Decode with 100% data integrity (NFR-005)
- [ ] Transfer 10 MB in < 30 seconds (FR-003)
- [ ] Success rate > 95% under typical conditions (NFR-006)
- [ ] Works on macOS, Linux, Windows (NFR-011)
- [ ] Zero network access (NFR-016)
- [ ] Clear error messages (FR-009)
- [ ] Complete README (NFR-010)

**Important** (Should have for v1.0):
- [ ] 80%+ test coverage (NFR-020)
- [ ] Memory < 1 GB for 500 MB file (NFR-003)
- [ ] Pip-installable (NFR-023)
- [ ] New user successful in < 5 min (NFR-008)

**Nice to have** (Can defer to v1.1):
- [ ] GUI application (out of scope)
- [ ] Batch processing (FR-014)
- [ ] Partial recovery (FR-016)
- [ ] Encryption support (NFR-019)

### 10.9 Post-Release Roadmap (v1.1+)

**v1.1** (4 weeks after v1.0):
- Enhanced error recovery
- Partial file reconstruction
- Performance optimizations based on user feedback
- Additional platform testing

**v1.2** (8 weeks after v1.0):
- Batch processing support
- Resume capability
- 4-color QR codes (2× capacity)

**v2.0** (6 months after v1.0):
- GUI application (desktop)
- Optional encryption
- Mobile app integration
- Real-time mode

---

