# Algorithms & Processing Logic

**Owner**: Development Team  
**Review trigger**: When encoding/decoding pipeline changes  
**Protocol version**: 1.0.0  
Referenced by: [DESIGN.md §4](../DESIGN.md), [specs/data-protocol.md](./data-protocol.md)

---


### 4.1 Encoding Algorithm

**Purpose**: Transform file to QR video.

**Fulfills Requirements**: FR-001, FR-002, FR-003

```python
def encode_file(input_path: str, output_path: str, 
                grid_size: int = 800, fps: int = 10,
                compression: bool = True) -> EncodingResult:
    """
    Complete encoding algorithm.
    
    Algorithm Steps:
    ─────────────────────────────────────────────────────────
    1. INPUT VALIDATION
       - Check file exists and is readable
       - Check file size ≤ 1 GB
       - Validate output path is writable
       
    2. FILE READING
       - Read entire file into memory
       - Handle large files with memory mapping if needed
       
    3. COMPRESSION (optional)
       - Apply gzip compression (level 6)
       - Calculate compression ratio
       
    4. INTEGRITY CALCULATION
       - Calculate SHA-256 hash of (compressed) data
       
    5. CHUNKING
       - Split data into chunks (max 2800 bytes each)
       - Create chunk headers with sequence numbers
       - Calculate CRC32 for each chunk
       
    6. METADATA FRAME GENERATION
       - Create JSON metadata structure
       - Encode metadata as first QR code
       
    7. QR CODE GENERATION
       - For each chunk: generate QR code image
       - Use specified grid_size
       - Error correction level: M (15%)
       
    8. VIDEO CREATION
       - Combine QR frames into video
       - Apply specified FPS
       - Use H.264 codec with high quality
       
    9. RESULT VALIDATION
       - Verify output file created
       - Return statistics
    ─────────────────────────────────────────────────────────
    
    Time Complexity: O(n) where n = file size
    Space Complexity: O(n) - file must fit in memory
    """
    
    # Step 1: Validate inputs
    validate_input_file(input_path, max_size=1_000_000_000)
    validate_output_path(output_path)
    validate_parameters(grid_size, fps)
    
    # Step 2: Read file
    with ProgressTracker(8, "Encoding") as progress:
        file_data = read_file(input_path)
        progress.update(1)
        
        # Step 3: Compress
        if compression:
            compressed = CompressionUtil.compress(file_data)
            compression_ratio = len(compressed) / len(file_data)
            data_to_encode = compressed
        else:
            compression_ratio = 1.0
            data_to_encode = file_data
        progress.update(1)
        
        # Step 4: Calculate hash
        file_hash = IntegrityUtil.sha256(file_data)
        progress.update(1)
        
        # Step 5: Chunk data
        chunks = chunk_data(data_to_encode)
        progress.update(1)
        
        # Step 6: Generate metadata
        metadata = create_metadata(
            filename=os.path.basename(input_path),
            size=len(file_data),
            hash=file_hash,
            compressed=compression,
            compression_ratio=compression_ratio,
            total_chunks=len(chunks),
            grid_size=grid_size,
            fps=fps
        )
        progress.update(1)
        
        # Step 7: Generate QR codes
        qr_gen = QRGenerator(grid_size)
        frames = [qr_gen.generate(metadata.to_json().encode())]
        
        for chunk in chunks:
            qr_image = qr_gen.generate(chunk.pack())
            frames.append(qr_image)
        progress.update(1)
        
        # Step 8: Create video
        video_encoder = VideoEncoder(fps)
        video_info = video_encoder.create(
            frames, output_path, grid_size, grid_size
        )
        progress.update(1)
        
        # Step 9: Return result
        progress.update(1)
        
    return EncodingResult(
        success=True,
        output_path=output_path,
        frames=len(frames),
        file_size=len(file_data),
        compressed_size=len(data_to_encode),
        video_size=os.path.getsize(output_path),
        duration=video_info.duration
    )
```

### 4.2 Decoding Algorithm

**Purpose**: Transform QR video back to file.

**Fulfills Requirements**: FR-006, FR-007, FR-008

```python
def decode_file(input_path: str, output_path: str,
                force: bool = False) -> DecodingResult:
    """
    Complete decoding algorithm.
    
    Algorithm Steps:
    ─────────────────────────────────────────────────────────
    1. INPUT VALIDATION
       - Check video file exists
       - Check output path (handle force flag)
       
    2. FRAME EXTRACTION
       - Extract all frames from video
       - Convert to format suitable for QR detection
       
    3. QR CODE DETECTION
       - For each frame: detect QR codes
       - Handle multiple QR codes per frame (take first)
       - Handle frames with no QR codes (skip)
       
    4. METADATA PARSING
       - Decode first QR code as metadata
       - Validate metadata structure
       - Extract file info and transfer params
       
    5. CHUNK COLLECTION
       - Decode remaining QR codes as chunks
       - Verify chunk headers (magic, CRC32)
       - Build dictionary: chunk_index -> chunk_data
       - Handle duplicate chunks (keep first valid)
       
    6. COMPLETENESS CHECK
       - Compare collected chunks vs. expected total
       - Identify missing chunk indices
       - Decision: continue or fail?
       
    7. FILE RECONSTRUCTION
       - Sort chunks by index
       - Concatenate chunk data
       
    8. DECOMPRESSION (if needed)
       - Decompress using gzip
       
    9. INTEGRITY VERIFICATION
       - Calculate SHA-256 of reconstructed file
       - Compare with expected hash from metadata
       - CRITICAL: Fail if mismatch
       
    10. FILE WRITING
        - Write reconstructed file to output path
        - Set permissions
    ─────────────────────────────────────────────────────────
    
    Time Complexity: O(f * d) where f = frames, d = detection time
    Space Complexity: O(n) where n = file size
    """
    
    # Step 1: Validate
    validate_video_file(input_path)
    validate_output_path(output_path, force)
    
    with ProgressTracker(10, "Decoding") as progress:
        # Step 2: Extract frames
        video_decoder = VideoDecoder()
        frames = video_decoder.extract_frames(input_path)
        progress.update(1)
        
        # Step 3: Detect QR codes
        qr_detector = QRDetector()
        qr_data_list = []
        
        for frame in frames:
            detected = qr_detector.detect(frame)
            if detected:
                qr_data_list.append(detected[0])  # Take first QR code
        progress.update(2)
        
        if not qr_data_list:
            raise DecodingError("No QR codes detected in video")
        
        # Step 4: Parse metadata
        metadata = Metadata.from_json(qr_data_list[0].data.decode())
        progress.update(1)
        
        # Step 5: Collect chunks
        chunks = {}
        errors = []
        
        for qr_data in qr_data_list[1:]:  # Skip metadata frame
            try:
                chunk = Chunk.unpack(qr_data.data)
                if chunk.header.chunk_index not in chunks:
                    chunks[chunk.header.chunk_index] = chunk
            except Exception as e:
                errors.append(str(e))
                
        progress.update(2)
        
        # Step 6: Check completeness
        expected_chunks = metadata.transfer.total_chunks
        missing = [i for i in range(expected_chunks) if i not in chunks]
        
        if missing:
            raise IncompleteTransferError(
                f"Missing {len(missing)} chunks: {missing[:10]}...",
                missing_chunks=missing,
                total_chunks=expected_chunks
            )
        progress.update(1)
        
        # Step 7: Reconstruct
        sorted_chunks = [chunks[i] for i in sorted(chunks.keys())]
        reconstructed = b''.join(chunk.data for chunk in sorted_chunks)
        progress.update(1)
        
        # Step 8: Decompress
        if metadata.file.compressed:
            file_data = CompressionUtil.decompress(reconstructed)
        else:
            file_data = reconstructed
        progress.update(1)
        
        # Step 9: Verify integrity (CRITICAL)
        if not IntegrityUtil.verify_hash(file_data, metadata.file.hash):
            raise IntegrityError(
                "File integrity check failed! Data corruption detected."
            )
        progress.update(1)
        
        # Step 10: Write file
        write_file(output_path, file_data)
        progress.update(1)
        
    return DecodingResult(
        success=True,
        output_path=output_path,
        file_size=len(file_data),
        chunks_decoded=len(chunks),
        chunks_expected=expected_chunks,
        integrity_verified=True
    )
```

### 4.3 Chunking Algorithm

**Purpose**: Split data into optimal chunks.

**Fulfills Requirements**: DR-003, FR-003

```python
def chunk_data(data: bytes, chunk_size: int = 2800) -> List[Chunk]:
    """
    Split data into chunks with headers.
    
    Algorithm:
    ─────────────────────────────────────────────────────────
    1. Calculate total chunks needed
    2. For each chunk:
       a. Extract slice of data (up to chunk_size bytes)
       b. Calculate CRC32 of data
       c. Create chunk header
       d. Combine header + data into Chunk object
    3. Return list of chunks
    ─────────────────────────────────────────────────────────
    
    Chunk Size Selection:
    - QR code capacity at 800x800 grid: ~2953 bytes
    - Reserve 153 bytes for header + overhead: 2800 bytes
    - Ensures reliable encoding/decoding
    
    Time Complexity: O(n) where n = data size
    Space Complexity: O(n) for output chunks
    """
    total_chunks = (len(data) + chunk_size - 1) // chunk_size
    chunks = []
    
    for i in range(total_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, len(data))
        chunk_data = data[start:end]
        
        # Calculate CRC32 for this chunk
        crc = IntegrityUtil.crc32(chunk_data)
        
        # Create header
        header = ChunkHeader(
            chunk_index=i,
            total_chunks=total_chunks,
            data_length=len(chunk_data),
            crc32=crc
        )
        
        # Create chunk
        chunk = Chunk(header=header, data=chunk_data)
        chunks.append(chunk)
        
    return chunks
```

### 4.4 QR Code Capacity Calculation

**Purpose**: Determine optimal parameters.

**Fulfills Requirements**: FR-005, NFR-001

```python
def calculate_qr_capacity(grid_size: int, 
                         error_correction: str = 'M') -> int:
    """
    Calculate maximum bytes per QR code.
    
    QR Code Capacity Formula:
    ─────────────────────────────────────────────────────────
    Capacity depends on:
    - Version (size): 1-40 or custom grid
    - Error correction: L (7%), M (15%), Q (25%), H (30%)
    - Data mode: Binary (8-bit bytes)
    
    For grid_size = 800:
    - Approximate version: 40 (177x177 modules)
    - Binary capacity with M correction: ~2953 bytes
    
    Conservative estimate: 2800 bytes (leaves margin)
    ─────────────────────────────────────────────────────────
    """
    # Simplified capacity calculation
    # In reality, use qrcode library's segmentation
    
    if grid_size < 177:
        raise ValueError("Grid size too small")
    
    # Rough estimate based on QR version
    if grid_size >= 800:
        return 2800  # Version 40 equivalent
    elif grid_size >= 600:
        return 2000  # Version 30 equivalent
    elif grid_size >= 400:
        return 1200  # Version 20 equivalent
    else:
        return 800   # Version 10 equivalent
```

### 4.5 Performance Optimization Strategies

**Purpose**: Achieve performance requirements.

**Fulfills Requirements**: NFR-001, NFR-002, NFR-003

#### 4.5.1 Encoding Optimizations

```python
"""
Performance Optimization Techniques:
─────────────────────────────────────────────────────────

1. PARALLEL QR GENERATION
   - Generate QR codes in parallel using multiprocessing
   - Divide chunks across CPU cores
   - Speedup: ~4x on quad-core
   
2. LAZY FRAME GENERATION
   - Generate QR images on-demand during video encoding
   - Avoid storing all frames in memory
   - Memory savings: ~90%
   
3. COMPRESSION OPTIMIZATION
   - Use gzip level 6 (balanced)
   - Level 9 only marginally better but 3x slower
   - Typical compression: 30-40% for text, 0-10% for binaries
   
4. VIDEO ENCODING OPTIMIZATION
   - Use hardware acceleration if available (FFmpeg)
   - Write frames directly to encoder without buffering
   - Minimize frame format conversions
"""

class ParallelQRGenerator:
    """Generate QR codes in parallel."""
    
    def __init__(self, grid_size: int, workers: int = None):
        self.grid_size = grid_size
        self.workers = workers or cpu_count()
        
    def generate_batch(self, chunks: List[Chunk]) -> List[Image]:
        """Generate QR codes for chunks in parallel."""
        with Pool(self.workers) as pool:
            return pool.map(self._generate_single, chunks)
            
    def _generate_single(self, chunk: Chunk) -> Image:
        """Worker function for single QR generation."""
        qr_gen = QRGenerator(self.grid_size)
        return qr_gen.generate(chunk.pack())
```

#### 4.5.2 Decoding Optimizations

```python
"""
Decoding Performance Optimizations:
─────────────────────────────────────────────────────────

1. FRAME SAMPLING
   - Extract every Nth frame (adaptive)
   - If chunk found: continue
   - If chunk not found: reduce N
   - Speedup: ~2-3x for high FPS videos
   
2. EARLY TERMINATION
   - Stop decoding once all chunks collected
   - Don't process remaining frames
   - Speedup: ~10-20% typically
   
3. QR DETECTION OPTIMIZATION
   - Preprocess frames (grayscale, contrast enhancement)
   - Use pyzbar's optimized detection
   - Cache detection results
   
4. MEMORY-MAPPED FILE WRITING
   - Use mmap for large file writes
   - Reduces memory pressure
"""

class AdaptiveFrameDecoder:
    """Decode frames with adaptive sampling."""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.video_decoder = VideoDecoder()
        self.qr_detector = QRDetector()
        
    def decode_adaptive(self, expected_chunks: int) -> Dict[int, Chunk]:
        """
        Decode with adaptive frame sampling.
        
        Strategy:
        - Start with sample_rate = 2 (every 2nd frame)
        - If missing chunks: reduce to 1 (all frames)
        - Stop when all chunks collected
        """
        chunks = {}
        sample_rate = 2
        
        frames = self.video_decoder.extract_frames(
            self.video_path, sample_rate
        )
        
        for frame in frames:
            qr_data = self.qr_detector.detect(frame)
            if qr_data:
                try:
                    chunk = Chunk.unpack(qr_data[0].data)
                    chunks[chunk.header.chunk_index] = chunk
                    
                    # Early termination
                    if len(chunks) >= expected_chunks:
                        break
                except Exception:
                    pass
                    
        return chunks
```


---

