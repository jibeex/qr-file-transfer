"""FileEncoder: orchestrates the full file-to-QR-video encoding pipeline."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from qr_transfer.constants import DEFAULT_FPS, DEFAULT_GRID_SIZE, MAX_CHUNK_SIZE, PROTOCOL_VERSION
from qr_transfer.core.protocols import (
    Chunk,
    ChunkHeader,
    EncodingResult,
    FileMetadata,
    Metadata,
    TransferMetadata,
)
from qr_transfer.errors import EncodingError
from qr_transfer.qr.generator import QRGenerator
from qr_transfer.utils.compression import CompressionUtil
from qr_transfer.utils.integrity import IntegrityUtil
from qr_transfer.utils.progress import ProgressTracker
from qr_transfer.utils.validation import InputValidator
from qr_transfer.video.encoder import VideoEncoder


def chunk_data(data: bytes, chunk_size: int = MAX_CHUNK_SIZE) -> list[Chunk]:
    """Split data into chunks with headers and CRC32 checksums."""
    if not data:
        raise ValueError("Cannot chunk empty data")
    total_chunks = (len(data) + chunk_size - 1) // chunk_size
    chunks: list[Chunk] = []
    for i in range(total_chunks):
        start = i * chunk_size
        payload = data[start: start + chunk_size]
        chunks.append(Chunk(
            header=ChunkHeader(
                chunk_index=i,
                total_chunks=total_chunks,
                data_length=len(payload),
                crc32=IntegrityUtil.crc32(payload),
            ),
            data=payload,
        ))
    return chunks


class FileEncoder:
    """Encodes a file into a QR code video using a streaming pipeline."""

    def __init__(
        self,
        grid_size: int = DEFAULT_GRID_SIZE,
        fps: int = DEFAULT_FPS,
        compression: bool = True,
        quiet: bool = False,
    ) -> None:
        self.grid_size = InputValidator.validate_grid_size(grid_size)
        self.fps = InputValidator.validate_fps(fps)
        self.compression = compression
        self.quiet = quiet
        self.qr_generator = QRGenerator(grid_size)
        self.video_encoder = VideoEncoder(fps)

    def encode(self, input_path: str, output_path: str, anonymize_metadata: bool = False) -> EncodingResult:
        """Run the full encoding pipeline and return an EncodingResult."""
        # 1. Validate inputs
        in_path = InputValidator.validate_file_path(input_path, must_exist=True)
        InputValidator.validate_file_size(in_path.stat().st_size)
        InputValidator.validate_output_path(output_path)

        with ProgressTracker(5, "Encoding", quiet=self.quiet) as progress:
            # 2. Read file, hash, compress
            file_data = in_path.read_bytes()
            file_size = len(file_data)
            file_hash = IntegrityUtil.sha256(file_data)

            if self.compression:
                compressed = CompressionUtil.compress(file_data)
                compression_ratio = len(compressed) / file_size
            else:
                compressed = file_data
                compression_ratio = 1.0

            compressed_size = len(compressed)
            del file_data  # free original file data from memory (§6.3)
            progress.update()

            # 3. Chunk
            chunks = chunk_data(compressed)
            del compressed  # chunks hold independent byte slices
            progress.update()

            # 4. Build metadata
            metadata = Metadata(
                file=FileMetadata(
                    name=Path(input_path).name,
                    size=file_size,
                    hash=file_hash,
                    compressed=self.compression,
                    compression_ratio=compression_ratio,
                ),
                transfer=TransferMetadata(
                    total_chunks=len(chunks),
                    grid_size=self.grid_size,
                    fps=self.fps,
                    protocol_version=PROTOCOL_VERSION,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ),
            )
            progress.update()

            # 5 & 6. Stream QR frames: metadata frame first, then one frame per chunk
            try:
                video_info = self.video_encoder.create(
                    self._frame_stream(metadata, chunks),
                    output_path,
                    self.grid_size,
                    self.grid_size,
                )
            except Exception as exc:
                raise EncodingError(f"Video creation failed: {exc}") from exc
            progress.update()

        # 7. Return result
        return EncodingResult(
            success=True,
            output_path=output_path,
            frames=video_info.frame_count,
            file_size=file_size,
            compressed_size=compressed_size,
            video_size=os.path.getsize(output_path),
            duration=video_info.duration,
        )

    def _frame_stream(self, metadata: Metadata, chunks: list[Chunk]) -> Generator:
        """Yield QR frames one at a time: metadata frame first, then data chunk frames."""
        yield self.qr_generator.generate(metadata.to_json().encode())
        for chunk in chunks:
            yield self.qr_generator.generate(chunk.pack())
