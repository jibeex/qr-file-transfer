# QR Code File Transfer System - Technical Design Document

## Document Information
- **Project Name**: QR File Transfer
- **Version**: 1.0.0
- **Date**: 2026-06-28
- **Document Type**: Technical Design Specification (arc42)
- **Status**: Draft
- **Owner**: Technical Lead
- **Review trigger**: When architecture changes, before each release, or when a new ADR supersedes an existing decision
- **Related Documents**: [REQUIREMENTS.md](./REQUIREMENTS.md), [GLOSSARY.md](./GLOSSARY.md)
- **Architecture Decisions**: [adr/](./adr/) — one file per decision (why each choice was made)
- **Reference Specs**: [specs/cli-reference.md](./specs/cli-reference.md), [specs/data-protocol.md](./specs/data-protocol.md)

## Purpose

This document describes **HOW** the system is implemented. It contains technical architecture, component design, algorithms, data structures, and implementation details.

For user requirements (WHAT the system does), see: [REQUIREMENTS.md](./REQUIREMENTS.md)

**Intended Audience**:
- Development Team (implementation)
- Technical Architects (design review)
- Technical Reviewers (code review)
- DevOps/Operations (deployment)

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Design](#2-component-design)
3. [Data Structures & Protocols](#3-data-structures--protocols) → specs/
4. [Algorithms & Processing Logic](#4-algorithms--processing-logic) → specs/algorithms.md
5. [Technology Stack & Justification](#5-technology-stack--justification)
6. [Performance Architecture](#6-performance-architecture)
7. [Security Implementation](#7-security-implementation)
8. [Error Handling Strategy](#8-error-handling-strategy)
9. [Module Organization](#9-module-organization)
10. [Implementation Roadmap](#10-implementation-roadmap) → ROADMAP.md
11. [Design Patterns Used](#11-design-patterns-used)
12. [Traceability Matrix](#12-traceability-matrix)
13. [Conclusion](#13-conclusion)
14. [Quality Scenarios](#14-quality-scenarios)
15. [Cross-Cutting Concerns](#15-cross-cutting-concerns)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                                │
│                      (qr_transfer.py)                           │
│                 ArgParser, Command Router                        │
└───────────────┬─────────────────────────┬───────────────────────┘
                │                         │
        ┌───────▼────────┐        ┌───────▼────────┐
        │  EncodeCommand │        │  DecodeCommand │
        └───────┬────────┘        └───────┬────────┘
                │                         │
        ┌───────▼────────┐        ┌───────▼────────┐
        │  FileEncoder   │        │  FileDecoder   │
        │                │        │                │
        │ - compress()   │        │ - extract()    │
        │ - chunk()      │        │ - detect_qr()  │
        │ - generate_qr()│        │ - verify()     │
        │ - create_video│        │ - reconstruct()│
        └───────┬────────┘        └───────┬────────┘
                │                         │
    ┌───────────┴───────────┐   ┌─────────┴──────────┐
    │                       │   │                    │
┌───▼────┐  ┌────▼─────┐  │   │  ┌────▼─────┐  ┌───▼────┐
│QRCode  │  │Video     │  │   │  │Video     │  │QRCode  │
│Gen     │  │Encoder   │  │   │  │Decoder   │  │Decoder │
│(qrcode)│  │(OpenCV)  │  │   │  │(OpenCV)  │  │(pyzbar)│
└────────┘  └──────────┘  │   │  └──────────┘  └────────┘
                          │   │
    ┌─────────────────────┴───┴──────────────────────┐
    │           Shared Utilities Layer               │
    │                                                │
    │  - Compression (gzip)                          │
    │  - Integrity (SHA-256, CRC32)                  │
    │  - Progress Tracking                           │
    │  - Error Formatting                            │
    │  - File I/O Helpers                            │
    └────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Key Methods | Dependencies |
|-----------|---------------|-------------|--------------|
| CLI | Parse commands, route to handlers | main(), parse_args() | argparse |
| FileEncoder | Encode files to QR video | encode(), compress(), chunk() | QRGenerator, VideoEncoder, Utils |
| FileDecoder | Decode QR video to files | decode(), extract(), verify() | QRDetector, VideoDecoder, Utils |
| QRGenerator | Generate QR code images | generate(data, size) | qrcode, Pillow |
| QRDetector | Detect & decode QR codes | detect(frame), decode(qr) | pyzbar, OpenCV |
| VideoEncoder | Create video from frames | create(frames, fps, output) | OpenCV |
| VideoDecoder | Extract frames from video | extract_frames(video) | OpenCV |
| Compression | Compress/decompress data | compress(data), decompress(data) | gzip |
| Integrity | Hash and verify data | sha256(data), crc32(chunk) | hashlib, zlib |
| Progress | Track and display progress | update(current, total) | tqdm |

### 1.3 Data Flow

**Encoding Flow**:
```
Input File → Read → Compress → Calculate Hash → Chunk → 
  Generate Metadata Frame → Generate QR Codes → 
  Create Video Frames → Encode to MP4 → Output Video
```

**Decoding Flow**:
```
Input Video → Extract Frames → Detect QR Codes → 
  Parse Metadata → Decode Chunks → Verify Integrity → 
  Reconstruct → Decompress → Output File
```

---

## 2. Component Design

### 2.1 FileEncoder Class

**Purpose**: Orchestrates the encoding pipeline from file to video.

**Fulfills Requirements**: FR-001, FR-002, FR-003, FR-004, FR-005

```python
class FileEncoder:
    """
    Encodes files into QR code videos.
    
    Attributes:
        grid_size (int): QR code grid size (177-1000)
        fps (int): Video frame rate (5-30)
        compression (bool): Enable gzip compression
        progress_callback (callable): Progress update callback
    """
    
    def __init__(self, grid_size=800, fps=10, compression=True):
        self.grid_size = grid_size
        self.fps = fps
        self.compression = compression
        self.qr_generator = QRGenerator(grid_size)
        self.video_encoder = VideoEncoder(fps)
        
    def encode(self, input_path: str, output_path: str) -> EncodingResult:
        """
        Main encoding pipeline.
        
        Steps:
          1. Read and validate input file
          2. Compress file data (if enabled)
          3. Calculate SHA-256 hash
          4. Split into chunks
          5. Generate metadata frame
          6. Generate QR code frames
          7. Create MP4 video
          
        Args:
            input_path: Path to input file
            output_path: Path to output video
            
        Returns:
            EncodingResult with stats (frames, size, time)
            
        Raises:
            FileNotFoundError: Input file doesn't exist
            PermissionError: Cannot read input or write output
            EncodingError: Encoding pipeline failed
        """
        # Implementation details below
        
    def _read_file(self, path: str) -> bytes:
        """Read file with error handling."""
        
    def _compress(self, data: bytes) -> bytes:
        """Compress using gzip level 6 (balanced)."""
        
    def _chunk_data(self, data: bytes) -> List[Chunk]:
        """Split data into chunks with headers."""
        
    def _generate_metadata(self, file_info: FileInfo) -> Frame:
        """Generate first frame with metadata."""
        
    def _generate_qr_frames(self, chunks: List[Chunk]) -> List[Frame]:
        """Generate QR code image for each chunk."""
```


### 2.2 FileDecoder Class

**Purpose**: Orchestrates the decoding pipeline from video to file.

**Fulfills Requirements**: FR-006, FR-007, FR-008, FR-010, FR-011

```python
class FileDecoder:
    """
    Decodes QR code videos back to files.
    
    Attributes:
        qr_detector (QRDetector): QR code detection engine
        video_decoder (VideoDecoder): Video frame extraction
        progress_callback (callable): Progress update callback
    """
    
    def __init__(self):
        self.qr_detector = QRDetector()
        self.video_decoder = VideoDecoder()
        
    def decode(self, input_path: str, output_path: str, 
               force: bool = False) -> DecodingResult:
        """
        Main decoding pipeline.
        
        Steps:
          1. Extract frames from video
          2. Detect and decode QR codes
          3. Parse metadata frame
          4. Collect data chunks
          5. Verify completeness
          6. Reconstruct file
          7. Decompress
          8. Verify integrity
          
        Args:
            input_path: Path to input video
            output_path: Path to output file
            force: Overwrite existing file
            
        Returns:
            DecodingResult with stats (success, missing chunks, time)
            
        Raises:
            FileNotFoundError: Input video doesn't exist
            PermissionError: Cannot write output
            IntegrityError: Hash verification failed
            IncompleteTransferError: Missing chunks
        """
        # Implementation details
        
    def verify(self, input_path: str, detailed: bool = False) -> VerifyResult:
        """
        Quick verification without full decode (FR-011).
        
        Checks:
          - Metadata frame readable
          - Expected chunk count
          - Actual chunks found
          
        Returns:
            VerifyResult with completeness stats
        """
        
    def _extract_frames(self, video_path: str) -> List[Frame]:
        """Extract all frames from video."""
        
    def _detect_qr_codes(self, frames: List[Frame]) -> List[QRData]:
        """Detect and decode QR codes from frames."""
        
    def _parse_metadata(self, qr_data: QRData) -> Metadata:
        """Parse first frame metadata."""
        
    def _collect_chunks(self, qr_data_list: List[QRData]) -> Dict[int, Chunk]:
        """Collect chunks, indexed by sequence number."""
        
    def _verify_completeness(self, chunks: Dict[int, Chunk], 
                            total: int) -> List[int]:
        """Return list of missing chunk numbers."""
        
    def _reconstruct_file(self, chunks: Dict[int, Chunk]) -> bytes:
        """Reassemble file from sorted chunks."""
        
    def _verify_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Verify SHA-256 hash matches."""
```


### 2.3 QRGenerator Class

**Purpose**: Generate QR code images from data.

**Fulfills Requirements**: FR-001, FR-005

```python
class QRGenerator:
    """
    Generates QR code images with configurable grid size.
    
    Attributes:
        grid_size (int): QR code dimensions (177-1000)
    """
    
    def __init__(self, grid_size: int = 800):
        if not 177 <= grid_size <= 1000:
            raise ValueError("Grid size must be 177-1000")
        self.grid_size = grid_size
        
    def generate(self, data: bytes, scale: int = 1) -> Image:
        """
        Generate QR code image.
        
        Args:
            data: Binary data to encode
            scale: Pixel scale factor
            
        Returns:
            PIL Image object
            
        Raises:
            DataTooLargeError: Data exceeds QR capacity
        """
        # Use qrcode library with custom size
        qr = qrcode.QRCode(
            version=None,  # Auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% recovery
            box_size=scale,
            border=4  # Minimum border
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure image is exactly grid_size x grid_size
        return self._resize_to_grid(img)
        
    def _resize_to_grid(self, img: Image) -> Image:
        """Resize image to exact grid_size dimensions."""
        return img.resize((self.grid_size, self.grid_size), 
                         Image.Resampling.NEAREST)
```

### 2.4 QRDetector Class

**Purpose**: Detect and decode QR codes from images.

**Fulfills Requirements**: FR-006, FR-008, NFR-006

```python
class QRDetector:
    """
    Detects and decodes QR codes from video frames.
    
    Uses pyzbar library for robust detection.
    """
    
    def __init__(self):
        self.detector = pyzbar.pyzbar
        
    def detect(self, frame: np.ndarray) -> List[QRData]:
        """
        Detect all QR codes in frame.
        
        Args:
            frame: Video frame as numpy array (BGR)
            
        Returns:
            List of decoded QR data objects
        """
        # Convert to grayscale for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        enhanced = self._enhance_contrast(gray)
        
        # Detect QR codes
        decoded_objects = self.detector.decode(enhanced)
        
        return [self._parse_qr_data(obj) for obj in decoded_objects]
        
    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        """Apply CLAHE for better QR detection."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)
        
    def _parse_qr_data(self, obj) -> QRData:
        """Parse decoded QR object into QRData structure."""
        return QRData(
            data=obj.data,
            type=obj.type,
            rect=obj.rect,
            quality=obj.quality if hasattr(obj, 'quality') else None
        )
```

### 2.5 VideoEncoder Class

**Purpose**: Create video files from image frames.

**Fulfills Requirements**: FR-002, DR-001

```python
class VideoEncoder:
    """
    Creates MP4 videos from QR code frames.
    
    Attributes:
        fps (int): Frame rate (5-30)
        codec (str): Video codec (H.264)
    """
    
    def __init__(self, fps: int = 10):
        if not 5 <= fps <= 30:
            raise ValueError("FPS must be 5-30")
        self.fps = fps
    self.codec = 'mp4v'  # MPEG-4 Part 2 (compatible with MP4 container; actual H.264 requires avc1 or ffmpeg backend — validate during POC)
        
    def create(self, frames: List[Image], output_path: str,
               width: int, height: int) -> VideoInfo:
        """
        Create video from frames.
        
        Args:
            frames: List of PIL Image objects
            output_path: Output video path
            width: Frame width
            height: Frame height
            
        Returns:
            VideoInfo with file stats
            
        Raises:
            EncodingError: Video creation failed
        """
        # Define codec
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        
        # Create video writer
        writer = cv2.VideoWriter(
            output_path,
            fourcc,
            self.fps,
            (width, height)
        )
        
        if not writer.isOpened():
            raise EncodingError("Failed to create video writer")
        
        try:
            for frame in frames:
                # Convert PIL Image to OpenCV format
                cv_frame = self._pil_to_cv(frame)
                writer.write(cv_frame)
        finally:
            writer.release()
            
        return VideoInfo(
            path=output_path,
            frame_count=len(frames),
            fps=self.fps,
            duration=len(frames) / self.fps
        )
        
    def _pil_to_cv(self, img: Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format (BGR)."""
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
```

### 2.6 VideoDecoder Class

**Purpose**: Extract frames from video files.

**Fulfills Requirements**: FR-006

```python
class VideoDecoder:
    """
    Extracts frames from video files.
    """
    
    def extract_frames(self, video_path: str, 
                      sample_rate: int = 1) -> List[np.ndarray]:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to video file
            sample_rate: Extract every Nth frame (1 = all frames)
            
        Returns:
            List of frames as numpy arrays
            
        Raises:
            VideoReadError: Cannot read video
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path}")
        
        frames = []
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_idx % sample_rate == 0:
                    frames.append(frame)
                    
                frame_idx += 1
        finally:
            cap.release()
            
        return frames
        
    def get_video_info(self, video_path: str) -> VideoInfo:
        """Get video metadata without extracting frames."""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path}")
        
        try:
            return VideoInfo(
                path=video_path,
                frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                fps=cap.get(cv2.CAP_PROP_FPS),
                width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                duration=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
            )
        finally:
            cap.release()
```


### 2.7 Utility Components

#### Compression Utility

**Purpose**: Compress and decompress file data.

**Fulfills Requirements**: FR-001, NFR-002

```python
class CompressionUtil:
    """
    Handles data compression using gzip.
    
    Single Responsibility: Data compression/decompression only.
    """
    
    @staticmethod
    def compress(data: bytes, level: int = 6) -> bytes:
        """
        Compress data using gzip.
        
        Args:
            data: Raw bytes to compress
            level: Compression level (1=fast, 9=best, 6=balanced)
            
        Returns:
            Compressed bytes
        """
        return gzip.compress(data, compresslevel=level)
        
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress gzip data.
        
        Args:
            data: Compressed bytes
            
        Returns:
            Decompressed bytes
            
        Raises:
            DecompressionError: Invalid gzip data
        """
        try:
            return gzip.decompress(data)
        except gzip.BadGzipFile as e:
            raise DecompressionError(f"Invalid gzip data: {e}")
```

#### Integrity Utility

**Purpose**: Calculate and verify data integrity.

**Fulfills Requirements**: FR-007, NFR-005, NFR-015

```python
class IntegrityUtil:
    """
    Handles cryptographic hashing and verification.
    
    Single Responsibility: Data integrity verification only.
    """
    
    @staticmethod
    def sha256(data: bytes) -> str:
        """
        Calculate SHA-256 hash.
        
        Args:
            data: Bytes to hash
            
        Returns:
            Hex-encoded hash string
        """
        return hashlib.sha256(data).hexdigest()
        
    @staticmethod
    def crc32(data: bytes) -> int:
        """
        Calculate CRC32 checksum (for chunks).
        
        Args:
            data: Bytes to checksum
            
        Returns:
            CRC32 value as integer
        """
        return zlib.crc32(data) & 0xffffffff
        
    @staticmethod
    def verify_hash(data: bytes, expected_hash: str) -> bool:
        """
        Verify data integrity.
        
        Args:
            data: Data to verify
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if hash matches
        """
        actual = IntegrityUtil.sha256(data)
        return actual == expected_hash
```

#### Progress Tracker

**Purpose**: Track and display operation progress.

**Fulfills Requirements**: FR-004

```python
class ProgressTracker:
    """
    Tracks operation progress with tqdm.
    
    Single Responsibility: Progress tracking and display.
    """
    
    def __init__(self, total: int, description: str = "", 
                 quiet: bool = False):
        self.total = total
        self.description = description
        self.quiet = quiet
        self.pbar = None
        
        if not quiet:
            self.pbar = tqdm(
                total=total,
                desc=description,
                unit="chunks",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
            )
            
    def update(self, n: int = 1):
        """Update progress by n steps."""
        if self.pbar:
            self.pbar.update(n)
            
    def close(self):
        """Close progress bar."""
        if self.pbar:
            self.pbar.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

### 2.8 CLI Component (`cli.py`)

**Purpose**: Parse arguments, route to pipeline, translate exceptions to exit codes.

**Fulfills Requirements**: FR-002, FR-011, FR-012, FR-013, IR-001, IR-002 (see ADR-007)

```python
def main():
    parser = build_parser()           # argparse with subcommands
    args = parser.parse_args()
    try:
        result = dispatch(args)       # route to pipeline function
        print_result(result)
        sys.exit(0)
    except QRTransferError as e:
        print(e.message, file=sys.stderr)
        sys.exit(e.error_code)        # always IR-002 exit code

def dispatch(args):
    match args.command:
        case 'encode':        return encode_file(args.input, args.output, ...)
        case 'decode':        return decode_file(args.input, args.output, ...)
        case 'verify':        return verify_video(args.input, ...)
        case 'info':          return get_info(args.input)
        case 'secure-delete': return secure_delete_files(args.files)
```

**`secure-delete` command** — owned by `FileOps` (§7.6). CLI calls `FileOps.secure_delete(path)` for each path argument. No encoding/decoding; purely a convenience wrapper around the secure deletion utility so users don't need external tools after a sensitive transfer.

**Error translation rule**: every `QRTransferError` subclass carries `error_code` (IR-002). CLI catches only `QRTransferError`; all other exceptions propagate as `ERROR_GENERAL` (exit code 1) after logging to stderr.

---

> **Extracted to canonical reference docs** — edit those files, not this section.

- **Wire format** (chunk binary layout, metadata JSON schema): [`docs/specs/data-protocol.md`](./specs/data-protocol.md)
- **CLI contract** (commands, flags, exit codes): [`docs/specs/cli-reference.md`](./specs/cli-reference.md)

**Fulfills Requirements**: DR-001, DR-002, DR-003, IR-001, IR-002

---

## 4. Algorithms & Processing Logic

> **Extracted to [`docs/specs/algorithms.md`](./specs/algorithms.md)**

Covers: encoding pipeline, decoding pipeline, chunking algorithm, QR capacity, frame deduplication.

**Fulfills Requirements**: FR-001, FR-002, FR-003, FR-006, FR-007, FR-008, DR-003

---

## 5. Technology Stack & Justification

### 5.1 Core Technologies

**Fulfills Requirements**: NFR-011, NFR-012, CON-009

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **Python** | 3.9+ | Core language | - Cross-platform (Windows, macOS, Linux)<br>- Rich ecosystem for image/video<br>- Easy to install and distribute<br>- Strong library support |
| **OpenCV** | 4.5+ | Video encoding/decoding | - Industry standard for video processing<br>- Hardware acceleration support<br>- Reliable frame extraction<br>- Cross-platform compatibility |
| **qrcode** | 7.3+ | QR code generation | - Pure Python (easy install)<br>- Supports custom sizes<br>- Configurable error correction<br>- Well-maintained |
| **pyzbar** | 0.1.9+ | QR code detection | - Fast C-based detection<br>- Robust with imperfect images<br>- Handles multiple QR codes<br>- Proven reliability |
| **Pillow** | 9.0+ | Image manipulation | - Standard Python image library<br>- Format conversion support<br>- Memory efficient<br>- Wide compatibility |
| **NumPy** | 1.21+ | Array operations | - Required by OpenCV<br>- Efficient array operations<br>- Industry standard |
| **tqdm** | 4.62+ | Progress bars | - Beautiful CLI progress display<br>- Low overhead<br>- Highly configurable |

### 5.2 Dependency Rationale

#### Why OpenCV over alternatives?

**Alternatives considered**:
- FFmpeg-python: Requires FFmpeg binary installation
- imageio-ffmpeg: Limited codec control
- moviepy: Heavy dependency chain

**OpenCV chosen because**:
- ✓ pip-installable (includes precompiled binaries)
- ✓ No external binary dependencies on most platforms
- ✓ Full control over video encoding parameters
- ✓ Hardware acceleration available
- ✓ Excellent documentation

#### Why pyzbar over alternatives?

**Alternatives considered**:
- opencv QRCodeDetector: Slower, less robust
- qreader: Newer, less proven
- zxing: Requires Java runtime

**pyzbar chosen because**:
- ✓ Fastest detection performance
- ✓ Most robust with imperfect captures
- ✓ Pure Python wrapper around proven C library (zbar)
- ✓ Works well with OpenCV frames

### 5.3 Platform-Specific Considerations

#### macOS
```bash
# Install via pip (includes binaries)
pip install opencv-python qrcode[pil] pyzbar pillow numpy tqdm

# Note: pyzbar requires zbar library
brew install zbar  # One-time system dependency
```

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies first
sudo apt-get install libzbar0

# Install Python packages
pip install opencv-python qrcode[pil] pyzbar pillow numpy tqdm
```

#### Windows
```bash
# Install via pip (includes binaries)
pip install opencv-python qrcode[pil] pyzbar pillow numpy tqdm

# Note: pyzbar includes zbar DLL for Windows
```

### 5.4 Alternative Technology Stacks (Rejected)

#### Option 1: JavaScript/Node.js
- **Pros**: Browser-based GUI possible, jsQR library
- **Cons**: 
  - Video processing requires native modules
  - Less mature computer vision libraries
  - Performance slower than Python/C++
- **Verdict**: Rejected - Python better for CV tasks

#### Option 2: C++ with OpenCV
- **Pros**: Maximum performance, native OpenCV
- **Cons**:
  - Compilation complexity
  - Platform-specific builds
  - Harder to maintain
  - Overkill for this use case
- **Verdict**: Rejected - Python sufficient for performance targets

#### Option 3: Go
- **Pros**: Fast compilation, easy distribution
- **Cons**:
  - Limited QR code libraries
  - OpenCV bindings less mature
  - Smaller ecosystem for image processing
- **Verdict**: Rejected - Ecosystem not mature enough

### 5.5 Dependency Version Strategy

**Fulfills Requirements**: NFR-024

```python
# pyproject.toml (PEP 621)
dependencies = [
    "opencv-python>=4.5.0,<5.0.0",     # Major version lock
    "qrcode[pil]>=7.3,<8.0",           # QR generation
    "pyzbar>=0.1.9",                    # QR detection
    "Pillow>=9.0.0,<11.0.0",           # Image handling
    "numpy>=1.21.0,<2.0.0",            # Array operations
    "tqdm>=4.62.0",                     # Progress bars
]
```

**Version Strategy**:
- Lock major versions to prevent breaking changes
- Allow minor/patch updates for bug fixes
- Test against minimum versions in CI
- Document known compatibility issues

---

## 6. Performance Architecture

### 6.1 Performance Requirements Mapping

**Fulfills Requirements**: NFR-001, NFR-002, NFR-003, NFR-004

| Requirement | Target | Design Strategy | Implementation |
|-------------|--------|----------------|----------------|
| Transfer speed | 400 KB/s | Optimal chunking, fast QR gen | Parallel processing, efficient codecs |
| Encoding speed | < 5s for 10MB | Compression, parallel QR gen | Multiprocessing, gzip level 6 |
| Memory usage | < 1GB for 500MB | Streaming, chunked processing | Generator patterns, mmap |
| Startup time | < 2s | Lazy imports, minimal setup | Import only what's needed |

### 6.2 Performance Budget

```
Target: 10 MB file in < 30 seconds (end-to-end)

Time Budget Breakdown:
┌─────────────────────────────────────────┐
│ Operation            │ Time │ % of Total│
├─────────────────────────────────────────┤
│ Encoding                                │
│  - Read file         │ 0.1s │    0.3%   │
│  - Compress          │ 0.5s │    1.7%   │
│  - Hash calculation  │ 0.2s │    0.7%   │
│  - Chunking          │ 0.1s │    0.3%   │
│  - QR generation     │ 2.0s │    6.7%   │
│  - Video creation    │ 1.0s │    3.3%   │
│  Subtotal: 3.9s                         │
├─────────────────────────────────────────┤
│ Physical Transfer                       │
│  - Display video     │ 15s  │   50.0%   │
│  - Camera recording  │ 15s  │   50.0%   │
│  Subtotal: 15s (parallel with display)  │
├─────────────────────────────────────────┤
│ Decoding                                │
│  - Frame extraction  │ 2.0s │    6.7%   │
│  - QR detection      │ 5.0s │   16.7%   │
│  - Reconstruction    │ 0.5s │    1.7%   │
│  - Decompress        │ 0.5s │    1.7%   │
│  - Hash verify       │ 0.2s │    0.7%   │
│  - Write file        │ 0.1s │    0.3%   │
│  Subtotal: 8.3s                         │
├─────────────────────────────────────────┤
│ Total: ~27.2s (within 30s target)       │
└─────────────────────────────────────────┘

Bottleneck: Video display + camera recording (50%)
  → Cannot optimize (physical constraint)
  → Must optimize encoding/decoding to compensate
```

### 6.3 Memory Architecture

**Fulfills Requirements**: NFR-003

```python
"""
Memory Management Strategy:
─────────────────────────────────────────────────────────

For 500 MB file:
├── Peak memory usage target: < 1 GB
├── Components:
│   ├── Input file: 500 MB (read once)
│   ├── Compressed data: ~350 MB (70% ratio)
│   ├── Chunks: ~350 MB (references, not copies)
│   ├── QR frames: Generated on-demand (streaming)
│   ├── Video encoder buffer: ~50 MB
│   └── Python overhead: ~50 MB
└── Total: ~1.3 GB → OVER BUDGET!

Optimization: Streaming Architecture
├── Don't keep original file in memory after compression
├── Don't keep all QR frames in memory
├── Generate and encode frames one at a time
└── Revised total: ~750 MB ✓ (well under 1 GB budget)
"""

class StreamingEncoder:
    """Memory-efficient streaming encoder."""
    
    def encode_streaming(self, input_path: str, output_path: str):
        """
        Encode without loading all frames into memory.
        
        Memory optimization:
        - Read file once, compress, then release
        - Generate QR codes one at a time
        - Write to video encoder immediately
        - Never hold more than 2-3 frames in memory
        """
        # Read and compress
        with open(input_path, 'rb') as f:
            file_data = f.read()
        
        compressed = CompressionUtil.compress(file_data)
        file_hash = IntegrityUtil.sha256(file_data)
        
        # Release original file data
        del file_data
        
        # Chunk (creates references, not copies)
        chunks = chunk_data(compressed)
        
        # Initialize video writer
        video_writer = cv2.VideoWriter(...)
        
        # Stream QR generation and encoding
        qr_gen = QRGenerator(self.grid_size)
        
        for chunk in chunks:
            qr_image = qr_gen.generate(chunk.pack())
            cv_frame = self._pil_to_cv(qr_image)
            video_writer.write(cv_frame)
            # qr_image automatically garbage collected
            
        video_writer.release()
```

### 6.4 Concurrency Architecture

**Fulfills Requirements**: NFR-002

```python
"""
Concurrency Strategy:
─────────────────────────────────────────────────────────

1. ENCODING: CPU-bound
   Strategy: Multiprocessing for QR generation
   
   Sequential:  [QR1][QR2][QR3][QR4] = 4 units time
   Parallel:    [QR1]
                [QR2]  = 1 unit time (4 cores)
                [QR3]
                [QR4]
   
   Speedup: ~3.5x on 4-core system

2. DECODING: I/O-bound + CPU-bound mix
   Strategy: Parallel frame processing
   
   Sequential:  [F1→D1][F2→D2][F3→D3] = 3 units
   Parallel:    [F1→D1]
                [F2→D2]  = 1 unit (3 workers)
                [F3→D3]
   
   Speedup: ~2.5x (I/O contention limits scaling)

3. AVOID: Threading
   - Python GIL prevents true parallelism for CPU tasks
   - Use multiprocessing instead
"""

from multiprocessing import Pool, cpu_count

class ConcurrentEncoder:
    """Encoder with parallel QR generation."""
    
    def encode_parallel(self, chunks: List[Chunk]) -> List[Image]:
        """Generate QR codes in parallel."""
        with Pool(processes=cpu_count()) as pool:
            # Map chunks to workers
            qr_images = pool.map(
                self._generate_qr_worker,
                chunks
            )
        return qr_images
        
    def _generate_qr_worker(self, chunk: Chunk) -> Image:
        """Worker function (runs in separate process)."""
        qr_gen = QRGenerator(self.grid_size)
        return qr_gen.generate(chunk.pack())
```

### 6.5 Caching Strategy

```python
"""
Caching Decisions:
─────────────────────────────────────────────────────────

CACHE:
✓ QR detector instances (expensive to create)
✓ Video decoder instances (OpenCV VideoCapture)
✓ Metadata parsing results (avoid re-parsing)

DO NOT CACHE:
✗ QR code images (memory intensive)
✗ Video frames (memory intensive)
✗ Chunk data (references already lightweight)
"""

class CachedQRDetector:
    """QR detector with instance reuse."""
    
    def __init__(self):
        self._detector = pyzbar.pyzbar  # Reuse
        self._clahe = cv2.createCLAHE(...)  # Expensive, cache
        
    def detect(self, frame: np.ndarray) -> List[QRData]:
        """Detect using cached instances."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced = self._clahe.apply(gray)  # Reuse CLAHE
        return self._detector.decode(enhanced)
```


---

## 7. Security Implementation

### 7.1 Security Architecture

**Fulfills Requirements**: NFR-015, NFR-016, NFR-017, NFR-018, CR-001

```
Security Layers:
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Input Validation                               │
│  - File path sanitization                               │
│  - Parameter validation                                 │
│  - Type checking                                        │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Layer 2: Data Integrity                                 │
│  - SHA-256 hashing (file level)                         │
│  - CRC32 checksums (chunk level)                        │
│  - Magic byte verification                              │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Layer 3: Isolation                                      │
│  - No network access                                    │
│  - No external API calls                                │
│  - Local-only processing                                │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────┐
│ Layer 4: Privacy                                        │
│  - Optional metadata anonymization                      │
│  - No telemetry/analytics                               │
│  - No persistent logs (unless enabled)                  │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Input Validation

**Fulfills Requirements**: NFR-017

```python
class InputValidator:
    """
    Validates all user inputs.
    
    SOLID: Single Responsibility - Input validation only
    Security: Defense in depth - validate everything
    """
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Path:
        """
        Validate and sanitize file path.
        
        Security checks:
        - Path traversal prevention (../)
        - Absolute path resolution
        - Existence verification
        - Permission checking
        
        Raises:
            SecurityError: Path traversal attempt
            FileNotFoundError: File doesn't exist
            PermissionError: Insufficient permissions
        """
        # Convert to Path object
        path_obj = Path(path).resolve()
        
        # Prevent path traversal
        try:
            path_obj.resolve().relative_to(Path.cwd())
        except ValueError:
            # Path is outside current directory - allowed but log
            pass
        
        # Check for suspicious patterns
        if '..' in str(path):
            raise SecurityError("Path traversal attempt detected")
        
        if must_exist and not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Check permissions
        if must_exist and not os.access(path_obj, os.R_OK):
            raise PermissionError(f"Cannot read file: {path}")
        
        return path_obj
    
    @staticmethod
    def validate_grid_size(size: int) -> int:
        """
        Validate QR grid size.
        
        Range: 177-1000
        Rationale: Below 177 = too slow, above 1000 = unreliable
        """
        if not isinstance(size, int):
            raise TypeError(f"Grid size must be int, got {type(size)}")
        
        if not 177 <= size <= 1000:
            raise ValueError(f"Grid size must be 177-1000, got {size}")
        
        return size
    
    @staticmethod
    def validate_fps(fps: int) -> int:
        """
        Validate frame rate.
        
        Range: 5-30
        Rationale: Below 5 = unusable, above 30 = camera limits
        """
        if not isinstance(fps, int):
            raise TypeError(f"FPS must be int, got {type(fps)}")
        
        if not 5 <= fps <= 30:
            raise ValueError(f"FPS must be 5-30, got {fps}")
        
        return fps
    
    @staticmethod
    def validate_file_size(path: Path, max_size: int = 1_000_000_000) -> int:
        """
        Validate file size.
        
        Max: 1 GB default
        Rationale: Memory and performance constraints
        """
        size = path.stat().st_size
        
        if size == 0:
            raise ValueError("File is empty")
        
        if size > max_size:
            raise ValueError(
                f"File too large: {size} bytes (max {max_size})"
            )
        
        return size
```

### 7.3 Data Integrity Implementation

**Fulfills Requirements**: FR-007, NFR-005, NFR-015

```python
class IntegrityChecker:
    """
    Multi-layer integrity verification.
    
    Layers:
    1. Chunk-level: CRC32 (fast, detects corruption)
    2. File-level: SHA-256 (cryptographic, detects tampering)
    """
    
    @staticmethod
    def verify_chunk(chunk: Chunk) -> bool:
        """
        Verify chunk integrity using CRC32.
        
        Fast check for transmission errors.
        """
        expected_crc = chunk.header.crc32
        actual_crc = IntegrityUtil.crc32(chunk.data)
        
        if expected_crc != actual_crc:
            raise IntegrityError(
                f"Chunk {chunk.header.chunk_index} corrupted: "
                f"CRC mismatch (expected {expected_crc:08x}, "
                f"got {actual_crc:08x})"
            )
        
        return True
    
    @staticmethod
    def verify_file(data: bytes, expected_hash: str) -> bool:
        """
        Verify file integrity using SHA-256.
        
        Cryptographic verification - detects any modification.
        CRITICAL: Must pass before accepting file.
        """
        actual_hash = IntegrityUtil.sha256(data)
        
        if actual_hash != expected_hash:
            raise IntegrityError(
                f"File integrity verification FAILED!\n"
                f"Expected: {expected_hash}\n"
                f"Got:      {actual_hash}\n"
                f"DO NOT USE THIS FILE - data corruption detected!"
            )
        
        return True
    
    @staticmethod
    def verify_magic_bytes(data: bytes) -> bool:
        """
        Verify chunk magic bytes.
        
        Ensures data is actually a QR chunk.
        """
        if len(data) < 4:
            return False
        
        magic = data[:4]
        if magic != b'QRFT':
            raise ValueError(
                f"Invalid magic bytes: expected b'QRFT', got {magic}"
            )
        
        return True
```

### 7.4 Network Isolation

**Fulfills Requirements**: NFR-016, UC-005

```python
"""
Network Isolation Strategy:
─────────────────────────────────────────────────────────

Design Principle: Zero network access by design

1. NO NETWORK LIBRARIES IMPORTED
   ✗ requests, urllib, httplib
   ✗ socket (except for type hints)
   ✗ asyncio network functions
   
2. NO EXTERNAL SERVICE CALLS
   ✗ Telemetry
   ✗ Analytics
   ✗ Update checks
   ✗ License validation servers
   
3. VERIFICATION
   - Unit tests with network monitoring
   - CI/CD includes network isolation test
   - Static analysis to detect network imports

4. DOCUMENTATION
   - Clearly state "no network access" in README
   - Security audit includes network verification
"""

# Test to verify no network access
def test_no_network_access():
    """
    Verify application makes no network requests.
    
    Test method:
    1. Mock socket.socket to raise exception
    2. Run encode/decode operations
    3. Verify no socket attempts
    """
    import socket
    
    original_socket = socket.socket
    
    def mock_socket(*args, **kwargs):
        raise AssertionError("Network access attempted!")
    
    socket.socket = mock_socket
    
    try:
        # Run encode/decode
        encode_file("test.txt", "output.mp4")
        decode_file("output.mp4", "decoded.txt")
    finally:
        socket.socket = original_socket
    
    # If we get here, no network access was attempted ✓
```

### 7.5 Privacy Protection

**Fulfills Requirements**: NFR-018, CR-001

```python
class PrivacyProtection:
    """
    Privacy-preserving features.
    
    GDPR Compliance:
    - Filename is PII (may contain personal info)
    - Provide anonymization option
    - No data collection or transmission
    """
    
    @staticmethod
    def anonymize_metadata(metadata: Metadata) -> Metadata:
        """
        Remove PII from metadata.
        
        Replaces:
        - Filename → hash(filename)
        - Timestamp → rounded to hour
        
        Use case: High-security environments where
        even filenames are sensitive.
        """
        anonymized = copy.deepcopy(metadata)
        
        # Hash filename
        filename_hash = hashlib.sha256(
            metadata.file.name.encode()
        ).hexdigest()[:16]
        anonymized.file.name = f"file_{filename_hash}"
        
        # Round timestamp to hour
        dt = datetime.fromisoformat(metadata.transfer.timestamp)
        rounded = dt.replace(minute=0, second=0, microsecond=0)
        anonymized.transfer.timestamp = rounded.isoformat()
        
        return anonymized
    
    @staticmethod
    def verify_no_telemetry():
        """
        Verify no telemetry code exists.
        
        Static analysis check for:
        - Google Analytics
        - Mixpanel
        - Sentry
        - Any phone-home code
        """
        # This is a placeholder for CI/CD static analysis
        pass
```

### 7.6 Secure File Operations

**Fulfills Requirements**: NFR-017, FR-009

```python
class SecureFileOps:
    """
    Secure file I/O operations.
    
    Security considerations:
    - Atomic writes (avoid partial files)
    - Permission checking
    - Safe temporary files
    - Cleanup on errors
    """
    
    @staticmethod
    def write_file_atomic(path: Path, data: bytes) -> None:
        """
        Write file atomically.
        
        Strategy:
        1. Write to temporary file
        2. Verify write successful
        3. Atomic rename to target
        
        Prevents partial/corrupted files.
        """
        temp_path = path.with_suffix('.tmp')
        
        try:
            # Write to temp file
            with open(temp_path, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Verify write
            if temp_path.stat().st_size != len(data):
                raise IOError("Write verification failed")
            
            # Atomic rename
            temp_path.rename(path)
            
        except Exception as e:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            raise
    
    @staticmethod
    def secure_delete(path: Path, passes: int = 1) -> None:
        """
        Securely delete file.
        
        For sensitive data (crypto keys, credentials):
        - Overwrite with random data
        - Then delete
        
        Note: Not forensically secure on modern SSDs
        but better than standard delete.
        """
        if not path.exists():
            return
        
        size = path.stat().st_size
        
        with open(path, 'r+b') as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        
        path.unlink()
```

### 7.7 Security Testing

```python
"""
Security Test Suite:
─────────────────────────────────────────────────────────

1. INPUT VALIDATION TESTS
   - Path traversal attempts
   - Invalid file sizes
   - Malformed parameters
   - Type confusion attacks

2. INTEGRITY TESTS
   - Bit flip detection
   - Chunk corruption
   - Hash mismatch handling
   - Magic byte validation

3. NETWORK ISOLATION TESTS
   - Socket monitoring
   - Network library detection
   - External call verification

4. PRIVACY TESTS
   - Metadata anonymization
   - No telemetry verification
   - PII leakage checks

5. FUZZ TESTING
   - Malformed videos
   - Invalid QR codes
   - Corrupted chunks
   - Extreme values
"""

# Example security test
def test_path_traversal_prevention():
    """Test path traversal attack prevention."""
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\SAM"
    ]
    
    for path in malicious_paths:
        with pytest.raises((SecurityError, PermissionError)):
            InputValidator.validate_file_path(path)
```


---

## 8. Error Handling Strategy

### 8.1 Error Hierarchy

**Fulfills Requirements**: FR-009, FR-010, NFR-007, NFR-009

```python
"""
Exception Hierarchy:
─────────────────────────────────────────────────────────
QRTransferError (base)
├── ValidationError
│   ├── InvalidParameterError
│   ├── FileValidationError
│   └── SecurityError
├── EncodingError
│   ├── CompressionError
│   ├── QRGenerationError
│   └── VideoCreationError
├── DecodingError
│   ├── VideoReadError
│   ├── QRDetectionError
│   ├── IncompleteTransferError
│   └── DecompressionError
├── IntegrityError
│   ├── ChunkIntegrityError
│   └── FileIntegrityError
└── IOError (system)
    ├── FileNotFoundError
    ├── PermissionError
    └── DiskSpaceError
"""

class QRTransferError(Exception):
    """
    Base exception for all QR transfer errors.
    
    Attributes:
        message: Human-readable error message
        error_code: Unique error code (for IR-002)
        suggestions: List of recovery suggestions
        details: Technical details (optional)
    """
    
    def __init__(self, message: str, error_code: int = 1,
                 suggestions: List[str] = None, details: str = None):
        self.message = message
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.details = details
        super().__init__(message)
    
    def format_user_message(self) -> str:
        """
        Format error for user display.
        
        Format:
        ✗ [Error message]
        
        Details: [Technical details if any]
        
        Suggestions:
          • [Suggestion 1]
          • [Suggestion 2]
        
        Error code: [CODE]
        """
        parts = [f"✗ {self.message}"]
        
        if self.details:
            parts.append(f"\nDetails:\n  {self.details}")
        
        if self.suggestions:
            parts.append("\nSuggestions:")
            for suggestion in self.suggestions:
                parts.append(f"  • {suggestion}")
        
        parts.append(f"\nError code: {self.error_code}")
        
        return "\n".join(parts)

class IncompleteTransferError(DecodingError):
    """
    Raised when transfer is incomplete.
    
    Contains specific information about missing chunks.
    """
    
    def __init__(self, message: str, missing_chunks: List[int],
                 total_chunks: int):
        self.missing_chunks = missing_chunks
        self.total_chunks = total_chunks
        self.decoded_chunks = total_chunks - len(missing_chunks)
        self.completion_percent = (self.decoded_chunks / total_chunks) * 100
        
        suggestions = [
            "Re-record the video with better lighting",
            "Keep camera steady at 20-40cm distance",
            "Ensure display brightness is at maximum",
            "Try with --grid-size 600 for easier scanning"
        ]
        
        details = (
            f"Total chunks: {total_chunks}\n"
            f"  Decoded: {self.decoded_chunks} ({self.completion_percent:.1f}%)\n"
            f"  Missing: {len(missing_chunks)}\n"
            f"  Missing chunk IDs: {missing_chunks[:20]}"
            + ("..." if len(missing_chunks) > 20 else "")
        )
        
        super().__init__(
            message=message,
            error_code=5,
            suggestions=suggestions,
            details=details
        )

class IntegrityError(QRTransferError):
    """
    Raised when integrity check fails.
    
    CRITICAL: Never allow corrupted files.
    """
    
    def __init__(self, message: str, expected: str = None,
                 actual: str = None):
        self.expected = expected
        self.actual = actual
        
        suggestions = [
            "DO NOT USE the decoded file - it is corrupted",
            "Retry the entire transfer from encoding",
            "If problem persists, check hardware (display, camera)",
            "Report issue if reproducible"
        ]
        
        details = None
        if expected and actual:
            details = f"Expected hash: {expected}\nActual hash:   {actual}"
        
        super().__init__(
            message=message,
            error_code=6,
            suggestions=suggestions,
            details=details
        )
```

### 8.2 Error Handling Patterns

**Fulfills Requirements**: NFR-007

```python
class ErrorHandler:
    """
    Centralized error handling.
    
    SOLID: Open/Closed Principle - Extensible error handling
    """
    
    @staticmethod
    def handle_encoding_error(e: Exception, context: dict) -> None:
        """
        Handle encoding errors with context.
        
        Strategy:
        1. Log error with context
        2. Cleanup temporary files
        3. Format user-friendly message
        4. Exit with appropriate code
        """
        # Cleanup
        if 'temp_files' in context:
            for temp_file in context['temp_files']:
                try:
                    Path(temp_file).unlink()
                except Exception:
                    pass
        
        # Format message
        if isinstance(e, QRTransferError):
            print(e.format_user_message(), file=sys.stderr)
            sys.exit(e.error_code)
        else:
            # Unexpected error
            print(f"✗ Unexpected error: {str(e)}", file=sys.stderr)
            print("\nError code: 1", file=sys.stderr)
            sys.exit(1)
    
    @staticmethod
    def handle_decoding_error(e: Exception, context: dict) -> None:
        """
        Handle decoding errors with context.
        
        Special handling for IncompleteTransferError:
        - Show exactly what's missing
        - Offer specific recovery steps
        """
        if isinstance(e, IncompleteTransferError):
            # Detailed incomplete transfer report
            print(e.format_user_message(), file=sys.stderr)
            
            # Optional: Save partial data
            if context.get('save_partial'):
                partial_path = context['output_path'] + '.partial'
                # Save what we have
                print(f"\nPartial data saved to: {partial_path}",
                      file=sys.stderr)
            
            sys.exit(e.error_code)
        
        elif isinstance(e, IntegrityError):
            # CRITICAL: Make it very clear file is corrupted
            print("=" * 60, file=sys.stderr)
            print("CRITICAL ERROR: FILE INTEGRITY CHECK FAILED", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(e.format_user_message(), file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            sys.exit(e.error_code)
        
        else:
            ErrorHandler.handle_encoding_error(e, context)
    
    @staticmethod
    def with_error_handling(func: callable) -> callable:
        """
        Decorator for error handling.
        
        Usage:
            @ErrorHandler.with_error_handling
            def encode_command(args):
                # Implementation
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print("\n✗ Operation cancelled by user", file=sys.stderr)
                sys.exit(130)  # Standard Unix code for Ctrl+C
            except Exception as e:
                context = {'function': func.__name__}
                if 'encode' in func.__name__:
                    ErrorHandler.handle_encoding_error(e, context)
                else:
                    ErrorHandler.handle_decoding_error(e, context)
        
        return wrapper
```

### 8.3 Graceful Degradation

**Fulfills Requirements**: NFR-007, NFR-006, FR-008

```python
class GracefulDegradation:
    """
    Handle partial failures gracefully.
    
    Design principle: Fail safely, never crash
    """
    
    @staticmethod
    def decode_with_fallback(frames: List[np.ndarray],
                            qr_detector: QRDetector) -> Dict[int, Chunk]:
        """
        Decode frames with fallback strategies.
        
        Strategies:
        1. Normal detection
        2. Enhanced preprocessing if low success rate
        3. Multiple detection attempts per frame
        4. Skip undecodable frames
        
        Never crash - always return what we got.
        """
        chunks = {}
        failed_frames = []
        
        for i, frame in enumerate(frames):
            try:
                # Strategy 1: Normal detection
                qr_data = qr_detector.detect(frame)
                
                if qr_data:
                    chunk = Chunk.unpack(qr_data[0].data)
                    chunks[chunk.header.chunk_index] = chunk
                    continue
                
                # Strategy 2: Enhanced preprocessing
                enhanced_frame = enhance_frame_aggressive(frame)
                qr_data = qr_detector.detect(enhanced_frame)
                
                if qr_data:
                    chunk = Chunk.unpack(qr_data[0].data)
                    chunks[chunk.header.chunk_index] = chunk
                    continue
                
                # No QR code detected - skip this frame
                failed_frames.append(i)
                
            except Exception as e:
                # Log error but continue
                logging.debug(f"Frame {i} failed: {e}")
                failed_frames.append(i)
                continue
        
        # Report what we got
        logging.info(
            f"Decoded {len(chunks)} chunks, "
            f"failed on {len(failed_frames)} frames"
        )
        
        return chunks
    
    @staticmethod
    def save_partial_file(chunks: Dict[int, Chunk],
                         output_path: str) -> Path:
        """
        Save partial file for debugging.
        
        Use case: Transfer failed but user wants to see what was transferred.
        """
        partial_path = Path(output_path).with_suffix('.partial')
        
        # Sort chunks and concatenate available data
        sorted_indices = sorted(chunks.keys())
        partial_data = b''.join(chunks[i].data for i in sorted_indices)
        
        with open(partial_path, 'wb') as f:
            f.write(partial_data)
        
        # Create metadata file
        meta_path = partial_path.with_suffix('.partial.json')
        metadata = {
            'chunks_available': len(chunks),
            'chunk_indices': sorted_indices,
            'total_size': len(partial_data),
            'warning': 'This is incomplete data - DO NOT USE'
        }
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return partial_path
```

### 8.4 Error Messages Design

**Fulfills Requirements**: NFR-009

```python
"""
Error Message Design Guidelines:
─────────────────────────────────────────────────────────

GOOD ERROR MESSAGES:
✓ Clear and specific
✓ Action-oriented
✓ No jargon
✓ Include recovery steps
✓ Appropriate tone (helpful, not patronizing)

EXAMPLES:

BAD:
  "Error code 0x8007000E"
  → User has no idea what this means

GOOD:
  "✗ Cannot read file: document.pdf
  
  Details:
    Permission denied
  
  Suggestions:
    • Check file permissions with: ls -l document.pdf
    • Make file readable: chmod +r document.pdf
    • Verify you own the file
  
  Error code: 7"

BAD:
  "QR decoding failed"
  → No actionable information

GOOD:
  "✗ Decoding failed: Incomplete transfer
  
  Details:
    Total chunks: 15
    Decoded: 12 (80%)
    Missing: 3 (chunks #4, #8, #12)
  
  Suggestions:
    • Re-record the video with better lighting
    • Keep camera steady at 20-40cm distance
    • Ensure display brightness is at maximum
  
  Error code: 5"
"""

class ErrorMessages:
    """
    Centralized error message templates.
    
    Ensures consistent, helpful error messages.
    """
    
    @staticmethod
    def file_not_found(path: str) -> str:
        return (
            f"Cannot find file: {path}\n\n"
            f"Suggestions:\n"
            f"  • Check the file path is correct\n"
            f"  • Use absolute path: /full/path/to/{Path(path).name}\n"
            f"  • Check file exists: ls {path}"
        )
    
    @staticmethod
    def file_too_large(size: int, max_size: int) -> str:
        size_mb = size / 1_000_000
        max_mb = max_size / 1_000_000
        
        return (
            f"File too large: {size_mb:.1f} MB (max {max_mb:.0f} MB)\n\n"
            f"Suggestions:\n"
            f"  • Compress the file first\n"
            f"  • Split into smaller files\n"
            f"  • Use zip/tar to reduce size"
        )
    
    @staticmethod
    def video_unreadable(path: str) -> str:
        return (
            f"Cannot read video: {path}\n\n"
            f"Suggestions:\n"
            f"  • Verify file is a valid video\n"
            f"  • Check with: file {path}\n"
            f"  • Try playing in VLC or QuickTime\n"
            f"  • Re-record if corrupted"
        )
    
    @staticmethod
    def no_qr_codes_detected() -> str:
        return (
            "No QR codes detected in video\n\n"
            "Suggestions:\n"
            "  • Verify this is a QR transfer video\n"
            "  • Check video quality and brightness\n"
            "  • Use 'qr-transfer info <video>' to check metadata\n"
            "  • Try re-recording with better conditions"
        )
```

### 8.5 Logging Strategy

```python
"""
Logging Configuration:
─────────────────────────────────────────────────────────

LEVELS:
- ERROR: Failures that prevent operation
- WARNING: Recoverable issues (e.g., skipped frames)
- INFO: Normal progress (when verbose mode enabled)
- DEBUG: Detailed diagnostics (for troubleshooting)

DEFAULT: No logging (quiet operation)
WITH --verbose: INFO level to stderr
WITH --debug: DEBUG level to file

PRIVACY: Never log file contents or sensitive data
"""

import logging

def setup_logging(verbose: bool = False, debug: bool = False):
    """Configure logging based on flags."""
    
    if debug:
        # Debug to file
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            filename='qr-transfer-debug.log',
            filemode='w'
        )
        # Also to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)
        
    elif verbose:
        # Info to console
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s',
            stream=sys.stderr
        )
    else:
        # Errors only
        logging.basicConfig(
            level=logging.ERROR,
            format='%(levelname)s: %(message)s',
            stream=sys.stderr
        )
```


---

## 9. Module Organization

### 9.1 Project Structure

**Fulfills Requirements**: NFR-020 (Maintainability), Module Organization

```
qr-file-transfer/
├── qr_transfer/                 # Main package
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Entry point (python -m qr_transfer)
│   │
│   ├── cli.py                  # Command-line interface
│   │   └── CLI, ArgumentParser, command routing
│   │
│   ├── core/                   # Core encoding/decoding
│   │   ├── __init__.py
│   │   ├── encoder.py          # FileEncoder class
│   │   ├── decoder.py          # FileDecoder class
│   │   └── protocols.py        # Data structures (Chunk, Metadata)
│   │
│   ├── qr/                     # QR code operations
│   │   ├── __init__.py
│   │   ├── generator.py        # QRGenerator class
│   │   └── detector.py         # QRDetector class
│   │
│   ├── video/                  # Video operations
│   │   ├── __init__.py
│   │   ├── encoder.py          # VideoEncoder class
│   │   └── decoder.py          # VideoDecoder class
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── compression.py      # CompressionUtil
│   │   ├── integrity.py        # IntegrityUtil, IntegrityChecker
│   │   ├── progress.py         # ProgressTracker
│   │   ├── validation.py       # InputValidator
│   │   └── file_ops.py         # SecureFileOps
│   │
│   ├── errors.py               # Exception hierarchy
│   └── constants.py            # Constants and configuration
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   │   ├── test_encoder.py
│   │   ├── test_decoder.py
│   │   ├── test_qr_generator.py
│   │   ├── test_qr_detector.py
│   │   ├── test_compression.py
│   │   ├── test_integrity.py
│   │   └── test_validation.py
│   │
│   ├── integration/            # Integration tests
│   │   ├── test_encode_decode.py
│   │   ├── test_error_handling.py
│   │   └── test_performance.py
│   │
│   ├── fixtures/               # Test data
│   │   ├── sample_files/
│   │   └── sample_videos/
│   │
│   └── conftest.py             # Pytest configuration
│
├── docs/                       # Documentation
│   ├── REQUIREMENTS.md         # Requirements specification
│   ├── DESIGN.md              # This document
│   ├── adr/                   # Architecture Decision Records
│   └── specs/                 # Wire format + CLI reference
│
├── scripts/                    # Utility scripts
│   ├── benchmark.py           # Performance benchmarking
│   └── generate_test_files.py # Generate test fixtures
│
├── .github/                    # GitHub configuration
│   └── workflows/
│       └── ci.yml             # CI/CD pipeline
│
├── pyproject.toml             # Project config, deps, entry point (PEP 621)
├── requirements.txt           # Legacy — use pyproject.toml instead
├── requirements-dev.txt       # Legacy — use pyproject.toml [dev] instead
├── README.md                  # User documentation
├── LICENSE                    # License file
└── .gitignore                # Git ignore rules
```

### 9.2 Module Responsibilities (SOLID)

**Single Responsibility Principle**: Each module has ONE reason to change.

```python
"""
Module Responsibility Matrix:
─────────────────────────────────────────────────────────

cli.py
  Responsibility: Parse commands, route to handlers
  Depends on: core.encoder, core.decoder, errors
  Change trigger: New commands, CLI interface changes

core/encoder.py
  Responsibility: Orchestrate encoding pipeline
  Depends on: qr.generator, video.encoder, utils.*
  Change trigger: Encoding algorithm changes

core/decoder.py
  Responsibility: Orchestrate decoding pipeline
  Depends on: qr.detector, video.decoder, utils.*
  Change trigger: Decoding algorithm changes

core/protocols.py
  Responsibility: Define data structures
  Depends on: (minimal)
  Change trigger: Protocol version changes

qr/generator.py
  Responsibility: Generate QR code images
  Depends on: qrcode, PIL
  Change trigger: QR library changes

qr/detector.py
  Responsibility: Detect and decode QR codes
  Depends on: pyzbar, cv2
  Change trigger: Detection library changes

video/encoder.py
  Responsibility: Create videos from frames
  Depends on: cv2
  Change trigger: Video codec changes

video/decoder.py
  Responsibility: Extract frames from videos
  Depends on: cv2
  Change trigger: Video processing changes

utils/compression.py
  Responsibility: Compress/decompress data
  Depends on: gzip
  Change trigger: Compression algorithm changes

utils/integrity.py
  Responsibility: Hash and verify data
  Depends on: hashlib, zlib
  Change trigger: Hash algorithm changes

utils/validation.py
  Responsibility: Validate inputs
  Depends on: (minimal)
  Change trigger: Validation rules changes

errors.py
  Responsibility: Define exception hierarchy
  Depends on: (none)
  Change trigger: New error types

constants.py
  Responsibility: Define constants
  Depends on: (none)
  Change trigger: Configuration changes
"""
```

### 9.3 Dependency Graph

**Dependency Inversion Principle**: High-level modules don't depend on low-level modules.

```
Dependency Layers (top to bottom):
─────────────────────────────────────────────────────────

Layer 1: CLI (Highest level)
  cli.py

Layer 2: Core Logic
  core/encoder.py
  core/decoder.py

Layer 3: Domain Services
  qr/generator.py     video/encoder.py
  qr/detector.py      video/decoder.py

Layer 4: Utilities
  utils/compression.py
  utils/integrity.py
  utils/validation.py
  utils/progress.py
  utils/file_ops.py

Layer 5: Data Structures
  core/protocols.py
  errors.py
  constants.py

Layer 6: External Libraries (Lowest level)
  qrcode, pyzbar, cv2, PIL, numpy

Rules:
- Higher layers can depend on lower layers
- Lower layers CANNOT depend on higher layers
- Layers at same level should minimize cross-dependencies
```

### 9.4 Interface Contracts

**Interface Segregation Principle**: Clients shouldn't depend on interfaces they don't use.

```python
# Abstract interfaces (using Protocol from typing)

from typing import Protocol, List
from pathlib import Path

class QRGeneratorProtocol(Protocol):
    """Interface for QR code generation."""
    
    def generate(self, data: bytes) -> Image:
        """Generate QR code from data."""
        ...

class QRDetectorProtocol(Protocol):
    """Interface for QR code detection."""
    
    def detect(self, frame: np.ndarray) -> List[QRData]:
        """Detect QR codes in frame."""
        ...

class VideoEncoderProtocol(Protocol):
    """Interface for video encoding."""
    
    def create(self, frames: List[Image], output_path: str,
               width: int, height: int) -> VideoInfo:
        """Create video from frames."""
        ...

class VideoDecoderProtocol(Protocol):
    """Interface for video decoding."""
    
    def extract_frames(self, video_path: str) -> List[np.ndarray]:
        """Extract frames from video."""
        ...

class CompressionProtocol(Protocol):
    """Interface for compression."""
    
    def compress(self, data: bytes) -> bytes:
        """Compress data."""
        ...
    
    def decompress(self, data: bytes) -> bytes:
        """Decompress data."""
        ...

# Benefits:
# - Easy to mock for testing
# - Easy to swap implementations
# - Clear contracts between modules
```

### 9.5 Configuration Management

```python
# constants.py

"""
Configuration Constants
─────────────────────────────────────────────────────────

All configurable values in one place.
Follows Open/Closed Principle: extend without modifying code.
"""

from dataclasses import dataclass
from typing import Final

# File Size Limits
MAX_FILE_SIZE: Final[int] = 1_000_000_000  # 1 GB
MIN_FILE_SIZE: Final[int] = 1  # 1 byte

# QR Code Parameters
MIN_GRID_SIZE: Final[int] = 177
MAX_GRID_SIZE: Final[int] = 1000
DEFAULT_GRID_SIZE: Final[int] = 800

# Video Parameters
MIN_FPS: Final[int] = 5
MAX_FPS: Final[int] = 30
DEFAULT_FPS: Final[int] = 10

# Chunk Parameters
MAX_CHUNK_SIZE: Final[int] = 2800  # bytes
CHUNK_HEADER_SIZE: Final[int] = 16  # bytes
CHUNK_MAGIC: Final[bytes] = b'QRFT'

# Compression Parameters
DEFAULT_COMPRESSION_LEVEL: Final[int] = 6
MIN_COMPRESSION_LEVEL: Final[int] = 1
MAX_COMPRESSION_LEVEL: Final[int] = 9

# Error Codes (IR-002)
ERROR_SUCCESS: Final[int] = 0
ERROR_GENERAL: Final[int] = 1
ERROR_FILE_NOT_FOUND: Final[int] = 2
ERROR_INVALID_INPUT: Final[int] = 3
ERROR_ENCODING_FAILED: Final[int] = 4
ERROR_DECODING_FAILED: Final[int] = 5
ERROR_INTEGRITY_FAILED: Final[int] = 6
ERROR_PERMISSION_DENIED: Final[int] = 7
ERROR_DISK_SPACE: Final[int] = 8

# Protocol Version
PROTOCOL_VERSION: Final[str] = "1.0.0"

@dataclass(frozen=True)
class VideoConfig:
    """Video encoding configuration."""
    codec: str = 'mp4v'
    pixel_format: str = 'yuv420p'
    quality: int = 95  # 0-100

@dataclass(frozen=True)
class QRConfig:
    """QR code configuration."""
    error_correction: str = 'M'  # L, M, Q, H
    border: int = 4  # Quiet zone modules

@dataclass(frozen=True)
class PerformanceConfig:
    """Performance tuning configuration."""
    parallel_qr_generation: bool = True
    max_workers: int = None  # None = cpu_count()
    frame_sample_rate: int = 1  # Extract every Nth frame
    
# Singleton configurations
VIDEO_CONFIG = VideoConfig()
QR_CONFIG = QRConfig()
PERFORMANCE_CONFIG = PerformanceConfig()
```

### 9.6 Testing Strategy

**Fulfills Requirements**: NFR-005, NFR-006, NFR-007 (via testability design)  
See full test specification: [docs/TEST_PLAN.md](../docs/TEST_PLAN.md)

#### Testing Pyramid

```
          /\
         /E2E\        10% — 4 use-case scenarios (UC-001–UC-004)
        /------\
       /  Integ  \    20% — encode/decode pipeline, error injection
      /------------\
     /     Unit     \  70% — component isolation, boundary values
    /________________\
```

| Layer | Count target | Speed | Dependencies |
|---|---|---|---|
| Unit | ~60 tests | < 10s total | All mocked |
| Integration | ~20 tests | < 60s total | Real libs, fake files |
| E2E | 4 scenarios | < 5 min | Real libs, simulated video |
| Hardware acceptance | 100 transfers | Manual | iPhone 16 + Mac |

Coverage targets: core modules 90%, utils 80%, CLI 70%.

#### Test Doubles Catalog

| Component | Double type | Rationale |
|---|---|---|
| `QRGenerator` | Mock | OpenCV/qrcode are slow; unit tests must not encode real QR |
| `QRDetector` | Stub returning `[QRData(data=chunk.pack())]` | pyzbar needs real images; isolation requires a stub |
| `VideoEncoder` | Mock | cv2.VideoWriter is stateful and writes disk; mock in unit tests |
| `VideoDecoder` | Fake (returns pre-built frame list) | Decouples frame generation from detection in integration tests |
| `CompressionUtil` | Real | Pure Python, fast, no side effects — always use real |
| `IntegrityUtil` | Real | Pure Python, fast, security-critical — never mock |
| `InputValidator` | Real | Security boundary — never mock |
| File system | `tmp_path` fixture (pytest) | Isolated temp dirs; no cleanup needed |
| `ProgressTracker` | Null object (`quiet=True`) | Suppress progress in tests |

#### Contract Tests (CLI interface — IR-001, IR-002)

Every command must satisfy the contract independent of implementation:

```python
# Pattern: invoke CLI as subprocess, assert exit code + stdout/stderr split
def run(args): subprocess.run(['qr-transfer'] + args, capture_output=True)

# Exit code contract
assert run(['encode', 'missing.txt', 'out.mp4']).returncode == 2   # ERROR_FILE_NOT_FOUND
assert run(['encode', 'file.bin', 'out.mp4']).returncode == 0      # success
assert run(['decode', 'bad.mp4', 'out.bin']).returncode == 5       # ERROR_DECODING_FAILED

# Stream contract
result = run(['encode', 'missing.txt', 'out.mp4'])
assert result.stdout == b''          # normal output only on success
assert b'Cannot find' in result.stderr  # errors to stderr only
```


---

## 10. Implementation Roadmap

> **Extracted to [`ROADMAP.md`](../ROADMAP.md)** — week-by-week task lists, risk register, success criteria, and post-release plan.

---

## 11. Design Patterns Used

### 12.1 Creational Patterns

**Factory Pattern**: Not needed (simple instantiation)

**Builder Pattern**: Not needed (flat configuration)

**Singleton Pattern**: Used for configuration
```python
# constants.py exports singleton configs
VIDEO_CONFIG = VideoConfig()
QR_CONFIG = QRConfig()
PERFORMANCE_CONFIG = PerformanceConfig()
```

### 12.2 Structural Patterns

**Facade Pattern**: Used in FileEncoder/FileDecoder
```python
# FileEncoder provides simple interface to complex subsystems
class FileEncoder:
    def encode(self, input_path: str, output_path: str) -> EncodingResult:
        # Hides complexity of:
        # - Compression
        # - Chunking
        # - QR generation
        # - Video creation
```

**Adapter Pattern**: Used for PIL/OpenCV conversion
```python
def _pil_to_cv(self, img: Image) -> np.ndarray:
    """Adapt PIL Image to OpenCV format."""
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
```

### 12.3 Behavioral Patterns

**Strategy Pattern**: Compression algorithms
```python
class CompressionUtil:
    @staticmethod
    def compress(data: bytes, algorithm: str = 'gzip') -> bytes:
        # Strategy pattern: different compression algorithms
```

**Template Method**: Encoding/decoding pipelines
```python
class FileEncoder:
    def encode(self, input_path, output_path):
        # Template method defines skeleton
        self._validate()
        self._read_file()
        self._compress()
        self._chunk()
        self._generate_qr()
        self._create_video()
```

**Observer Pattern**: Progress tracking
```python
class ProgressTracker:
    def update(self, n: int):
        # Observers (tqdm) notified of progress
```

---

## 12. Traceability Matrix

**Requirements Coverage** (maps REQUIREMENTS.md to DESIGN.md sections):

| Requirement | Design Section | Implementation Module |
|-------------|----------------|----------------------|
| FR-001: Encode any file | §2.1, §4.1 | core/encoder.py |
| FR-002: Simple encode command | §2.1, §9.1 | cli.py |
| FR-003: Fast transfer | §4.1, §6.2 | core/encoder.py, optimization |
| FR-004: Progress display | §2.7 | utils/progress.py |
| FR-005: Customizable grid size | §2.3 | qr/generator.py |
| FR-006: Decode video | §2.2, §4.2 | core/decoder.py |
| FR-007: Verify integrity | §2.7, §7.3 | utils/integrity.py |
| FR-008: Handle imperfect captures | §2.4, §4.5 | qr/detector.py |
| FR-009: Clear errors | §8.1, §8.4 | errors.py |
| FR-010: Report missing data | §8.1 | errors.py |
| FR-011: Verify without decode | §2.2 | core/decoder.py |
| FR-012: Display metadata | §2.2, §3.2 | core/protocols.py |
| FR-013: Help | §9.1 | cli.py |
| NFR-001-004: Performance | §6.1-6.4 | All modules |
| NFR-005-007: Reliability | §7.3, §8.1 | utils/integrity.py, errors.py |
| NFR-008-010: Usability | §8.4, §9.1 | cli.py, errors.py |
| NFR-011-014: Compatibility | §5.1, §5.3 | Cross-platform code |
| NFR-015-019: Security | §7.1-7.6 | utils/validation.py, security |
| DR-001-003: Data requirements | §3.1-3.3 | core/protocols.py |
| IR-001-002: Interface | §9.1 | cli.py, errors.py |
| CR-001-003: Compliance | §7.5 | Privacy features |

---

## 13. Conclusion

This design document provides a comprehensive technical blueprint for implementing the QR File Transfer system. It fulfills 100% of the requirements specified in REQUIREMENTS.md while adhering to SOLID principles and best programming practices.

**Key Design Decisions**:
1. **Layered architecture** for separation of concerns
2. **Protocol-based interfaces** for flexibility and testability
3. **Streaming architecture** for memory efficiency
4. **Multi-layer integrity** for reliability
5. **Graceful degradation** for robustness

**Next Steps**:
1. Complete Week 0 POC to validate critical assumptions
2. Begin Week 1 implementation following this design
3. Continuously update this document as implementation reveals insights
4. Maintain traceability between requirements, design, and code

**Document Maintenance**:
- Update when requirements change (via change request process)
- Reflect implementation learnings
- Keep traceability matrix current
- Version control all changes

---

## 14. Quality Scenarios

> arc42 §10 — stimulus/response pairs that make NFR targets testable at the architecture level.

| ID | Quality Attribute | Stimulus | Response | Measure |
|----|---|---|---|---|
| QS-001 | Reliability | Camera shake ±5° during recording | Decoder successfully reconstructs file | ≥ 95% of chunks decoded (FR-008) |
| QS-002 | Integrity | 1 bit flipped in reconstructed file | SHA-256 check fails; output file not written | Exit code 6; no partial file on disk |
| QS-003 | Performance | User encodes 10 MB file | Encoding completes | ≤ 5 seconds on reference hardware (NFR-002) |
| QS-004 | Performance | User decodes 10 MB video | Decoding completes | ≤ 25 seconds end-to-end (NFR-001) |
| QS-005 | Robustness | 1000 malformed videos fed to decoder | No crash, no data written | Exit code 1–255 for every input; no exception escapes (NFR-007) |
| QS-006 | Security | Tool runs while network monitor active | Zero external connections | `lsof -i` shows no sockets for the process (NFR-016) |
| QS-007 | Memory | 500 MB file encoded | Peak RSS stays bounded | < 1 GB RAM at any point (NFR-003) |
| QS-008 | Usability | User gets "incomplete transfer" error | Error message guides recovery | User resolves without external help in ≤ 5 min (NFR-009) |
| QS-009 | Correctness | Disk fills mid-write | Partial output not left behind | Atomic write: either full file or nothing; exit code 8 |
| QS-010 | Maintainability | New QR backend library is available | Swap without touching encode/decode pipelines | Only `QRDetector`/`QRGenerator` classes change (Protocol-based design, §9.4) |

---

## 15. Cross-Cutting Concerns

> arc42 §8 — concerns that apply across all components and do not belong to a single section.

### 13.1 Logging

- No persistent logs by default (NFR-018 — no telemetry)
- Verbose mode (`--verbose`) writes structured lines to stdout only
- Log levels: DEBUG (frame-by-frame detail), INFO (pipeline milestones), WARNING (skipped frames), ERROR (failures)
- Format: `[LEVEL] component: message` — machine-readable for scripted use
- **No log files created** — users pipe stdout if they need persistence

### 13.2 Observability

- Progress tracking (§2.7 `ProgressTracker`) is the primary observability surface
- Exit codes (IR-002) are the machine-readable status channel for scripts and automation
- No metrics endpoint, no tracing — tool is local and short-lived

### 13.3 Configuration Management

- All tunables in `constants.py` as typed `Final` constants (§9.5)
- No config file: settings are passed as CLI flags, not persisted
- Default values are designed to work without any flags

### 13.4 Error Propagation

- All errors propagate via the exception hierarchy (§8.1)
- Every exception maps to an exit code (IR-002)
- User-facing messages come from `ErrorMessages` class (§8.4), never from raw exception `.args`
- Partial output is never written on error (atomic write pattern, §7.6)

### 13.5 Dependency Injection

- All external library dependencies (OpenCV, pyzbar, qrcode) are isolated behind Protocol interfaces (§9.4)
- Swap implementations without changing pipeline logic
- Enables mocking in tests without patching library internals

### 13.6 Accessibility (CR-002 — WCAG 2.1 Level A)

**Fulfills Requirements**: CR-002

Rules applied across all CLI output:

**No color as sole status indicator**
- Progress bars use `[████░░░]` fill characters, not color alone
- Success/failure prefixed with `✓` / `✗` symbols, not just green/red
- Error severity conveyed by message structure, not color

**Screen reader compatibility**
- All output to stdout/stderr is plain text — no ANSI-only escape sequences that leave unreadable characters in non-color terminals
- Progress updates overwrite the same line (carriage return) rather than flooding — disable with `--quiet` for accessibility tools that can't handle in-place updates
- `--quiet` flag produces minimal output; `--verbose` produces fully structured lines suitable for parsing

**Readability**
- Help text (`--help`) written at Flesch-Kincaid Grade 8 or below — short sentences, common words, active voice
- Error messages follow the template: What failed → Why → How to fix (see §8.4)
- No jargon without definition; technical terms explained in parentheses

**Verification**
- Help text passes Flesch-Kincaid test before release (acceptance criterion AC-CR-002)
- Output tested with VoiceOver (macOS) as part of release checklist

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-28 | System | Complete technical design specification |
| 1.2.0 | 2026-06-28 | Kiro | Fixed design gaps: NFR-006 annotations, §6.3 memory budget clarified, §13.6 accessibility (CR-002) added |

---

**Related Documents**:
- [REQUIREMENTS.md](./REQUIREMENTS.md) - What the system does
- [GAP_ANALYSIS.md](./GAP_ANALYSIS.md) - Gap identification
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - Project overview

**End of Document**
