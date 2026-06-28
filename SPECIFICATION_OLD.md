# QR Code File Transfer System - Technical Specification

## Document Information
- **Project Name**: QR File Transfer
- **Version**: 1.0.0
- **Date**: 2026-06-27
- **Author**: System Specification
- **Status**: Draft

## Executive Summary

A visual data transmission system enabling file transfers between air-gapped computers using animated QR codes. The system encodes files into sequential QR code frames displayed as video, which can be captured by camera and decoded back to the original file.

**Key Value Proposition**: Secure, network-free file transfer for air-gapped environments using only a display and camera.

## 1. Requirements

### 1.1 Functional Requirements

#### FR-001: File Encoding
- **Priority**: MUST
- **Description**: System shall encode any binary file into an animated video containing sequential QR codes
- **Acceptance Criteria**:
  - Accept any file format (binary or text)
  - Compress data before encoding (gzip)
  - Split into chunks with metadata headers
  - Generate QR code frames with configurable grid size (177-1000 modules)
  - Output MP4 video file with configurable frame rate (5-30 fps)
  - Default grid size: 800×800 modules
  - Default frame rate: 10 fps

#### FR-002: File Decoding
- **Priority**: MUST
- **Description**: System shall decode video file back to original file
- **Acceptance Criteria**:
  - Extract frames from video file
  - Detect and decode QR codes at any grid size
  - Handle frames out of order
  - Verify chunk integrity (CRC32)
  - Reconstruct original file
  - Decompress data
  - Output identical file to original

#### FR-003: Error Detection & Correction
- **Priority**: MUST
- **Description**: System shall detect and report errors during transfer
- **Acceptance Criteria**:
  - Detect missing chunks
  - Report corrupted chunks (CRC mismatch)
  - Identify duplicate frames
  - Provide detailed error report with missing chunk indices
  - Calculate transfer success rate

#### FR-004: Grid Size Customization
- **Priority**: MUST
- **Description**: Users shall be able to customize QR code grid size
- **Acceptance Criteria**:
  - Support grid sizes from 177×177 to 1000×1000
  - Auto-detect grid size during decoding
  - Validate grid size parameters
  - Default to 800×800 for optimal speed on iPhone 16 + Mac

#### FR-005: Progress Monitoring
- **Priority**: SHOULD
- **Description**: System shall display encoding/decoding progress
- **Acceptance Criteria**:
  - Show percentage complete
  - Display estimated time remaining
  - Show current chunk number / total chunks
  - Display transfer speed (KB/sec)

#### FR-006: Metadata Frame
- **Priority**: MUST
- **Description**: First frame shall contain file metadata
- **Acceptance Criteria**:
  - Original filename
  - Original file size (bytes)
  - Compression algorithm used
  - Grid size used
  - Total number of data frames
  - Protocol version
  - Checksum of entire file

#### FR-007: CLI Interface
- **Priority**: MUST
- **Description**: Provide command-line interface for all operations
- **Acceptance Criteria**:
  - `encode` command: file → video
  - `decode` command: video → file
  - `verify` command: check video integrity
  - Support for optional parameters (grid size, fps, compression level)
  - Help documentation

#### FR-008: Batch Processing
- **Priority**: MAY
- **Description**: Support encoding/decoding multiple files
- **Acceptance Criteria**:
  - Accept directory as input
  - Process all files in directory
  - Generate separate video per file OR single archive
  - Report summary statistics

### 1.2 Non-Functional Requirements

#### NFR-001: Performance
- **Priority**: MUST
- **800×800 Grid**: Minimum 500 KB/sec transfer rate under ideal conditions
- **177×177 Grid**: Minimum 20 KB/sec transfer rate
- **Encoding Speed**: Process minimum 5 MB/sec during encoding
- **Decoding Speed**: Process minimum 10 frames/sec during decoding
- **Memory Usage**: Maximum 500 MB RAM for files up to 100 MB

#### NFR-002: Reliability
- **Priority**: MUST
- **Data Integrity**: 100% accuracy with error detection (CRC32)
- **Chunk Recovery**: Handle up to 5% missing frames with clear reporting
- **Error Rate**: Fail gracefully with informative error messages
- **Robustness**: Handle malformed input without crashes

#### NFR-003: Compatibility
- **Priority**: MUST
- **OS Support**: macOS, Linux, Windows
- **Python Version**: Python 3.9+
- **Video Format**: MP4 (H.264 codec)
- **Camera Input**: Support iPhone 16 (48MP) recording at 1080p or 4K
- **Display Output**: Optimized for Mac Retina displays (220 PPI)

#### NFR-004: Usability
- **Priority**: SHOULD
- **CLI Simplicity**: Single command for common operations
- **Error Messages**: Clear, actionable error messages
- **Documentation**: Comprehensive README with examples
- **Installation**: Single command install via pip
- **Defaults**: Sensible defaults requiring no configuration

#### NFR-005: Maintainability
- **Priority**: SHOULD
- **Code Quality**: PEP 8 compliant Python code
- **Test Coverage**: Minimum 80% unit test coverage
- **Documentation**: Inline docstrings for all public functions
- **Modularity**: Loosely coupled components
- **Logging**: Structured logging at appropriate levels

#### NFR-006: Security
- **Priority**: SHOULD
- **Input Validation**: Validate all user inputs
- **Path Traversal**: Prevent directory traversal attacks
- **Resource Limits**: Prevent DoS via excessive resource consumption
- **No Network**: System shall not make any network requests
- **Data Privacy**: No telemetry or analytics

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface (CLI)                    │
└───────────────┬──────────────────────────────┬──────────────────┘
                │                              │
                ├─────── encode ───────────────┤
                │                              │
        ┌───────▼────────┐            ┌────────▼────────┐
        │                │            │                 │
        │    Encoder     │            │     Decoder     │
        │   Module       │            │     Module      │
        │                │            │                 │
        └───────┬────────┘            └────────┬────────┘
                │                              │
                │                              │
        ┌───────▼────────┐            ┌────────▼────────┐
        │  QR Generator  │            │   QR Detector   │
        │                │            │   & Decoder     │
        └───────┬────────┘            └────────┬────────┘
                │                              │
        ┌───────▼────────┐            ┌────────▼────────┐
        │ Video Encoder  │            │ Video Decoder   │
        │   (OpenCV)     │            │   (OpenCV)      │
        └───────┬────────┘            └────────┬────────┘
                │                              │
                ▼                              ▼
           video.mp4                       file.bin
```

### 2.2 Component Specifications

#### 2.2.1 Encoder Module (`qr_encoder.py`)

**Responsibilities**:
- Read input file
- Compress data (gzip)
- Split into chunks
- Generate metadata frame
- Create QR code images
- Encode video file

**Key Classes/Functions**:

```python
class FileEncoder:
    def __init__(self, grid_size=800, fps=10, compression_level=6):
        """Initialize encoder with configuration"""
        
    def encode_file(self, input_path: str, output_video: str) -> EncodingResult:
        """Main encoding pipeline"""
        
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        
    def _create_chunks(self, data: bytes, chunk_size: int) -> List[Chunk]:
        """Split data into chunks with headers"""
        
    def _generate_metadata_frame(self, metadata: FileMetadata) -> np.ndarray:
        """Create first frame with file metadata"""
        
    def _generate_qr_frame(self, chunk: Chunk) -> np.ndarray:
        """Generate QR code image for chunk"""
        
    def _encode_video(self, frames: List[np.ndarray], output_path: str):
        """Encode frames into MP4 video"""
```

**Data Structures**:

```python
@dataclass
class Chunk:
    magic: bytes            # 4 bytes: b'QRFT' (QR File Transfer)
    version: int            # 2 bytes: protocol version
    index: int              # 4 bytes: chunk index (0-based)
    total: int              # 4 bytes: total chunks
    data_length: int        # 2 bytes: payload size
    crc32: int              # 4 bytes: CRC of payload
    payload: bytes          # variable: actual data
    
@dataclass
class FileMetadata:
    filename: str
    original_size: int
    compressed_size: int
    compression: str        # "gzip"
    grid_size: int
    total_frames: int
    protocol_version: int
    file_hash: str          # SHA256 of original file
```

#### 2.2.2 Decoder Module (`qr_decoder.py`)

**Responsibilities**:
- Extract frames from video
- Detect QR codes in frames
- Decode QR payloads
- Validate chunks
- Reconstruct file
- Decompress data

**Key Classes/Functions**:

```python
class FileDecoder:
    def __init__(self):
        """Initialize decoder"""
        
    def decode_video(self, input_video: str, output_path: str) -> DecodingResult:
        """Main decoding pipeline"""
        
    def _extract_frames(self, video_path: str) -> Generator[np.ndarray]:
        """Extract frames from video"""
        
    def _detect_qr(self, frame: np.ndarray) -> Optional[bytes]:
        """Detect and decode QR code in frame"""
        
    def _parse_chunk(self, data: bytes) -> Optional[Chunk]:
        """Parse chunk structure and validate CRC"""
        
    def _reconstruct_file(self, chunks: List[Chunk]) -> bytes:
        """Assemble chunks in order"""
        
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress gzip data"""
        
    def _verify_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Verify file hash"""
```

**Data Structures**:

```python
@dataclass
class DecodingResult:
    success: bool
    output_file: str
    total_chunks: int
    decoded_chunks: int
    missing_chunks: List[int]
    corrupted_chunks: List[int]
    duplicate_frames: int
    transfer_speed: float   # KB/sec
    error_message: Optional[str]
```

#### 2.2.3 QR Code Module (`qr_code.py`)

**Responsibilities**:
- Generate QR codes at arbitrary grid sizes
- Encode binary data into QR format
- Handle error correction levels

**Key Functions**:

```python
def generate_qr(data: bytes, grid_size: int, error_correction: str = 'M') -> np.ndarray:
    """Generate QR code image at specified grid size"""
    
def calculate_capacity(grid_size: int, error_correction: str = 'M') -> int:
    """Calculate data capacity for given grid size"""
    
def render_qr_frame(qr_data: np.ndarray, frame_size: Tuple[int, int]) -> np.ndarray:
    """Render QR code with border and progress indicator"""
```

#### 2.2.4 Utilities Module (`utils.py`)

**Responsibilities**:
- CRC calculation
- Compression/decompression
- File I/O helpers
- Progress tracking

**Key Functions**:

```python
def calculate_crc32(data: bytes) -> int:
    """Calculate CRC32 checksum"""
    
def compress_data(data: bytes, level: int = 6) -> bytes:
    """Compress data with gzip"""
    
def decompress_data(data: bytes) -> bytes:
    """Decompress gzip data"""
    
def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file"""
    
class ProgressTracker:
    """Track and display progress"""
    def update(self, current: int, total: int):
        """Update progress"""
```

#### 2.2.5 CLI Module (`qr_transfer.py`)

**Responsibilities**:
- Parse command-line arguments
- Invoke encoder/decoder
- Display results
- Handle errors

**Commands**:

```python
def cmd_encode(args):
    """Encode file to video"""
    
def cmd_decode(args):
    """Decode video to file"""
    
def cmd_verify(args):
    """Verify video integrity without full decode"""
    
def cmd_info(args):
    """Display video metadata"""
```

### 2.3 Data Flow

#### 2.3.1 Encoding Flow

```
Input File
    ↓
Read entire file into memory / stream in chunks
    ↓
Compress with gzip
    ↓
Calculate total chunks based on grid size capacity
    ↓
Generate metadata frame (frame 0)
    ↓
For each chunk:
    ├─ Create chunk header
    ├─ Add payload
    ├─ Calculate CRC32
    ├─ Encode as QR code image (grid_size × grid_size)
    └─ Add to frame list
    ↓
Encode all frames as MP4 video (fps)
    ↓
Output video file
```

#### 2.3.2 Decoding Flow

```
Input Video
    ↓
Open video file
    ↓
Extract frame 0 → parse metadata
    ↓
Extract remaining frames sequentially
    ↓
For each frame:
    ├─ Detect QR code region
    ├─ Decode QR payload
    ├─ Parse chunk structure
    ├─ Validate CRC32
    ├─ Store chunk by index (handle duplicates)
    └─ Update progress
    ↓
Check for missing chunks
    ↓
If complete:
    ├─ Reconstruct data in order
    ├─ Decompress
    ├─ Verify file hash
    └─ Write output file
Else:
    └─ Report missing chunks
```

## 3. Technical Design

### 3.1 Chunk Structure (Binary Layout)

```
Offset  Size    Field           Description
------  ----    -----           -----------
0       4       magic           b'QRFT' (0x51524654)
4       2       version         Protocol version (0x0001)
6       4       chunk_index     Current chunk number (0-based)
10      4       total_chunks    Total number of chunks
14      2       data_length     Size of payload in this chunk
16      4       crc32           CRC32 of payload
20      N       payload         Actual data (N = data_length)
```

**Total header size**: 20 bytes per chunk

### 3.2 Metadata Frame Structure (JSON)

```json
{
  "magic": "QRFT",
  "version": 1,
  "filename": "document.pdf",
  "original_size": 1048576,
  "compressed_size": 524288,
  "compression": "gzip",
  "grid_size": 800,
  "total_frames": 10,
  "file_hash": "sha256:abcd1234..."
}
```

Encoded as JSON, compressed, then encoded as QR code.

### 3.3 Grid Size vs. Capacity Calculation

For black/white QR codes with medium error correction:

```
Capacity (bytes) ≈ (grid_size²  × 0.12) - overhead

Examples:
- 177×177 = 31,329 modules × 0.12 ≈ 3,759 bytes - overhead ≈ 2,900 bytes
- 400×400 = 160,000 modules × 0.12 ≈ 19,200 bytes - overhead ≈ 16,000 bytes
- 600×600 = 360,000 modules × 0.12 ≈ 43,200 bytes - overhead ≈ 36,000 bytes
- 800×800 = 640,000 modules × 0.12 ≈ 76,800 bytes - overhead ≈ 64,000 bytes
- 1000×1000 = 1,000,000 modules × 0.12 ≈ 120,000 bytes - overhead ≈ 100,000 bytes
```

Note: Actual capacity depends on QR encoding mode and error correction level.

### 3.4 Video Encoding Parameters

- **Codec**: H.264 (libx264)
- **Container**: MP4
- **Frame Rate**: 10 fps (configurable 5-30 fps)
- **Resolution**: Based on grid size + border
  - For 800×800: 1920×1920 (with border and padding)
- **Bitrate**: Lossless or very high quality to prevent artifacts
- **Color Space**: RGB (future: support for 4-color codes)

### 3.5 Error Correction Strategy

#### Level 1: QR Code Built-in Error Correction
- Use medium (M) or high (H) error correction
- Corrects up to 15% (M) or 30% (H) damage per QR code

#### Level 2: CRC32 Chunk Validation
- Detect corrupted chunks immediately
- Report which specific chunks failed

#### Level 3: Duplicate Frame Handling
- If same chunk decoded multiple times, keep first valid instance
- Increases reliability when video has duplicate frames

#### Level 4: Missing Chunk Reporting (Future: FEC)
- Report exact chunk indices missing
- User can retry transfer for specific chunks only
- Future: Add Reed-Solomon FEC across chunks

## 4. API Specification

### 4.1 Command Line Interface

#### 4.1.1 Encode Command

```bash
qr-transfer encode <input_file> <output_video> [OPTIONS]

Arguments:
  input_file      Path to file to encode
  output_video    Path to output MP4 video

Options:
  --grid-size, -g     QR code grid size (177-1000) [default: 800]
  --fps, -f           Video frame rate (5-30) [default: 10]
  --compression, -c   Compression level (0-9) [default: 6]
  --no-compress       Skip compression
  --quiet, -q         Suppress progress output
  --verbose, -v       Verbose logging

Examples:
  qr-transfer encode document.pdf output.mp4
  qr-transfer encode large.zip output.mp4 -g 1000 -f 15
  qr-transfer encode secret.key output.mp4 -g 177
```

#### 4.1.2 Decode Command

```bash
qr-transfer decode <input_video> <output_file> [OPTIONS]

Arguments:
  input_video     Path to encoded video
  output_file     Path to output file

Options:
  --force, -f         Overwrite existing file
  --partial           Write partial file even if chunks missing
  --quiet, -q         Suppress progress output
  --verbose, -v       Verbose logging

Examples:
  qr-transfer decode recorded.mp4 document.pdf
  qr-transfer decode video.mov output.bin -f
```

#### 4.1.3 Verify Command

```bash
qr-transfer verify <input_video> [OPTIONS]

Arguments:
  input_video     Path to encoded video

Options:
  --detailed, -d      Show detailed chunk information

Examples:
  qr-transfer verify output.mp4
  qr-transfer verify output.mp4 --detailed
```

#### 4.1.4 Info Command

```bash
qr-transfer info <input_video>

Arguments:
  input_video     Path to encoded video

Examples:
  qr-transfer info output.mp4
```

### 4.2 Python API (Programmatic Usage)

```python
from qr_transfer import FileEncoder, FileDecoder

# Encoding
encoder = FileEncoder(grid_size=800, fps=10)
result = encoder.encode_file('input.pdf', 'output.mp4')
print(f"Encoded {result.total_chunks} chunks")

# Decoding
decoder = FileDecoder()
result = decoder.decode_video('output.mp4', 'output.pdf')
if result.success:
    print(f"Successfully decoded {result.decoded_chunks}/{result.total_chunks} chunks")
else:
    print(f"Failed: {result.error_message}")
    print(f"Missing chunks: {result.missing_chunks}")
```

## 5. Implementation Plan

### 5.1 Development Phases

#### Phase 1: Core Encoder (Week 1)
- [ ] Project setup, dependencies
- [ ] File I/O utilities
- [ ] Compression module
- [ ] Chunking logic with header structure
- [ ] QR code generation (basic, 800×800)
- [ ] Video encoding
- [ ] Basic CLI for encoding
- [ ] Unit tests for chunking and encoding

**Deliverable**: Working encoder that can create QR videos

#### Phase 2: Core Decoder (Week 2)
- [ ] Video frame extraction
- [ ] QR detection and decoding
- [ ] Chunk parsing and validation
- [ ] File reconstruction
- [ ] Decompression
- [ ] Basic CLI for decoding
- [ ] Unit tests for decoding

**Deliverable**: Working decoder that can reconstruct files

#### Phase 3: Error Handling & Robustness (Week 3)
- [ ] Missing chunk detection and reporting
- [ ] Duplicate frame handling
- [ ] CRC validation and error reporting
- [ ] Graceful failure modes
- [ ] Integration tests (roundtrip)
- [ ] Error injection tests

**Deliverable**: Reliable encoder/decoder with error handling

#### Phase 4: Polish & Optimization (Week 4)
- [ ] Progress tracking UI
- [ ] Performance optimization
- [ ] Memory efficiency for large files
- [ ] Comprehensive CLI with all commands
- [ ] Documentation (README, examples)
- [ ] Performance benchmarks

**Deliverable**: Production-ready system

#### Phase 5: Advanced Features (Future)
- [ ] Variable grid size support (177-1000)
- [ ] 4-color QR codes
- [ ] Reed-Solomon FEC across chunks
- [ ] Batch processing
- [ ] GUI application
- [ ] Mobile apps (iOS/Android)

### 5.2 Testing Strategy

#### Unit Tests
- Chunk creation and parsing
- CRC calculation
- Compression/decompression
- QR encoding (mock)
- Video encoding (mock)

#### Integration Tests
- Full encode → decode roundtrip
- Various file types (text, binary, PDF, images)
- Various file sizes (1KB, 10KB, 100KB, 1MB, 10MB, 100MB)
- Edge cases (empty file, very large file)

#### Error Handling Tests
- Corrupted video
- Missing frames
- Invalid chunk headers
- CRC mismatches
- Malformed QR codes

#### Performance Tests
- Encoding speed (MB/sec)
- Decoding speed (frames/sec)
- Memory usage profiling
- Large file handling (1GB+)

#### Real-World Tests
- iPhone 16 camera recording Mac display
- Various lighting conditions
- Camera shake and movement
- Different Mac display brightnesses
- Different scanning distances

### 5.3 Dependencies

```
# Core dependencies
opencv-python>=4.8.0      # Video encoding/decoding, image processing
qrcode>=7.4.0             # QR code generation
pyzbar>=0.1.9             # QR code decoding
Pillow>=10.0.0            # Image handling
numpy>=1.24.0             # Array operations

# Optional dependencies
tqdm>=4.65.0              # Progress bars
click>=8.1.0              # CLI framework (alternative to argparse)

# Development dependencies
pytest>=7.4.0             # Testing framework
pytest-cov>=4.1.0         # Coverage reporting
black>=23.0.0             # Code formatting
flake8>=6.0.0             # Linting
mypy>=1.5.0               # Type checking
```

## 6. Deployment

### 6.1 Installation

```bash
# Via pip (future)
pip install qr-file-transfer

# From source
git clone https://github.com/username/qr-file-transfer.git
cd qr-file-transfer
pip install -e .
```

### 6.2 System Requirements

- **Python**: 3.9 or higher
- **RAM**: 512 MB minimum, 2 GB recommended
- **Disk**: 100 MB for installation
- **Camera**: 720p minimum, 1080p+ recommended (iPhone 16: excellent)
- **Display**: 1080p minimum, Retina recommended

### 6.3 Platform-Specific Notes

#### macOS
- Use native camera app or third-party video capture
- Maximize screen brightness for QR display
- Disable auto-sleep during transfer

#### Linux
- May require `libzbar0` system package for pyzbar
- `apt-get install libzbar0` (Debian/Ubuntu)

#### Windows
- May require Visual C++ redistributables
- Use Windows Camera app for recording

## 7. Security Considerations

### 7.1 Threat Model

**In Scope**:
- Air-gapped file transfer
- Data integrity verification
- Prevention of malicious file injection

**Out of Scope**:
- Confidentiality (data is visible on screen)
- Authentication (no verification of sender/receiver)
- Encryption (files transferred in cleartext)

### 7.2 Security Measures

1. **Input Validation**
   - Validate file paths (prevent directory traversal)
   - Validate grid size (177-1000)
   - Validate FPS (5-30)
   - Limit file size to prevent memory exhaustion

2. **Data Integrity**
   - CRC32 for each chunk
   - SHA256 hash for complete file
   - Verify reconstructed file matches original hash

3. **Resource Limits**
   - Maximum video file size: 10 GB
   - Maximum source file size: 1 GB (configurable)
   - Timeout limits for long-running operations

4. **No Network Access**
   - System makes zero network requests
   - No telemetry or phone-home
   - Fully offline operation

5. **Future: Optional Encryption**
   - Add encryption layer before QR encoding
   - User-provided key or passphrase
   - AES-256-GCM recommended

### 7.3 Privacy

- No analytics or telemetry
- No cloud services
- Files never leave local machine during encoding
- Metadata (filename) is included in QR video - users should be aware

## 8. Documentation

### 8.1 User Documentation

- **README.md**: Quick start guide
- **INSTALL.md**: Installation instructions
- **USAGE.md**: Detailed usage examples
- **FAQ.md**: Common questions and troubleshooting
- **PERFORMANCE.md**: Performance characteristics and optimization tips

### 8.2 Developer Documentation

- **SPECIFICATION.md**: This document
- **ARCHITECTURE.md**: System architecture details
- **API.md**: Python API documentation
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history

## 9. Success Metrics

### 9.1 Technical Metrics

- **Transfer Speed**: > 500 KB/sec (800×800 grid)
- **Reliability**: > 99% chunk success rate under ideal conditions
- **Accuracy**: 100% data integrity (CRC verified)
- **Performance**: Encode 10 MB file in < 2 seconds
- **Memory**: < 500 MB RAM for 100 MB file

### 9.2 Usability Metrics

- **Time to First Transfer**: < 5 minutes from installation
- **CLI Simplicity**: Single command for basic use
- **Error Recovery**: Clear instructions when transfer fails
- **Documentation**: All common use cases covered

## 10. Future Enhancements

### 10.1 Near-Term (v1.1 - v1.3)

- **Variable grid sizes**: Full support for 177-1000 grid sizes
- **Improved error correction**: Reed-Solomon FEC across chunks
- **Streaming mode**: Start displaying QR codes before entire file is chunked
- **Resume capability**: Resume interrupted transfers
- **Verification mode**: Verify integrity without full decode

### 10.2 Medium-Term (v2.0)

- **4-color QR codes**: 2x capacity increase
- **Bidirectional transfer**: Request retransmission of missing chunks
- **GUI application**: Desktop app for non-technical users
- **Real-time mode**: Display → capture → decode in one flow
- **Batch processing**: Multiple files in one video

### 10.3 Long-Term (v3.0+)

- **Mobile apps**: Native iOS/Android apps
- **Encryption**: Built-in file encryption
- **Compression**: Better algorithms (zstd, brotli)
- **Forward error correction**: Fountain codes for maximum reliability
- **Protocol negotiation**: Auto-negotiate best settings based on hardware

## 11. Open Questions & Decisions

### 11.1 Resolved
- ✅ Default grid size: 800×800 (optimized for iPhone 16)
- ✅ Video format: MP4 (H.264)
- ✅ Primary language: Python
- ✅ Error correction: CRC32 per chunk

### 11.2 To Be Decided
- ❓ Should we use click or argparse for CLI?
- ❓ Maximum file size limit? (suggest 1 GB)
- ❓ Should metadata frame include thumbnail/preview?
- ❓ Support for multi-part videos (split large files across multiple videos)?
- ❓ Should we compress metadata frame separately?

## 12. References

### 12.1 Technical Standards
- ISO/IEC 18004:2015 - QR Code bar code symbology specification
- RFC 1952 - GZIP file format specification
- ITU-T H.264 - Advanced Video Coding

### 12.2 Related Projects
- **QRStream**: Animated QR code file transfer (inspiration)
- **TxQR/RxQR**: Blockchain transaction signing via QR
- **JAB Code**: High Capacity Color Barcode
- **SQRL**: Secure QR Login (different use case, relevant tech)

### 12.3 Libraries
- OpenCV: https://opencv.org/
- qrcode: https://github.com/lincolnloop/python-qrcode
- pyzbar: https://github.com/NaturalHistoryMuseum/pyzbar
- Pillow: https://python-pillow.org/

## Revision History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0.0   | 2026-06-27 | System | Initial specification |
