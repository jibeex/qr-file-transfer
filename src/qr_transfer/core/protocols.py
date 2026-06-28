"""Shared data structures used across modules."""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from typing import Any

from qr_transfer.constants import CHUNK_HEADER_SIZE, CHUNK_MAGIC, PROTOCOL_VERSION
from qr_transfer.utils.integrity import IntegrityUtil


@dataclass
class VideoInfo:
    path: str
    frame_count: int
    fps: float
    duration: float
    width: int = 0
    height: int = 0


@dataclass
class QRData:
    data: bytes
    type: str
    rect: Any


# ---------------------------------------------------------------------------
# Wire protocol: Chunk
# Header: magic(4)|version(1)|chunk_index(4)|total_chunks(4)|data_length(2)|crc32(4)|reserved(1)
# Format: '>4sBIIHIB' = 20 bytes
# ---------------------------------------------------------------------------

_HEADER_STRUCT = struct.Struct(">4sBIIHIB")
assert _HEADER_STRUCT.size == CHUNK_HEADER_SIZE, f"struct={_HEADER_STRUCT.size}, constant={CHUNK_HEADER_SIZE}"


@dataclass
class ChunkHeader:
    chunk_index: int
    total_chunks: int
    data_length: int
    crc32: int


@dataclass
class Chunk:
    header: ChunkHeader
    data: bytes

    def pack(self) -> bytes:
        crc = IntegrityUtil.crc32(self.data)
        return _HEADER_STRUCT.pack(
            CHUNK_MAGIC,
            1,  # version
            self.header.chunk_index,
            self.header.total_chunks,
            len(self.data),
            crc,
            0,  # reserved
        ) + self.data

    @classmethod
    def unpack(cls, raw: bytes) -> "Chunk":
        if len(raw) < CHUNK_HEADER_SIZE:
            raise ValueError("Chunk too short")
        magic, version, chunk_index, total_chunks, data_length, crc32, _ = _HEADER_STRUCT.unpack_from(raw)
        if magic != CHUNK_MAGIC:
            raise ValueError(f"Invalid magic: expected {CHUNK_MAGIC!r}, got {magic!r}")
        if version != 1:
            raise ValueError(f"Unsupported version: {version}")
        data = raw[CHUNK_HEADER_SIZE:CHUNK_HEADER_SIZE + data_length]
        if len(data) != data_length:
            raise ValueError("Truncated chunk payload")
        actual_crc = IntegrityUtil.crc32(data)
        if actual_crc != crc32:
            raise ValueError(f"CRC mismatch: expected {crc32:#010x}, got {actual_crc:#010x}")
        return cls(
            header=ChunkHeader(
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                data_length=data_length,
                crc32=crc32,
            ),
            data=data,
        )


# ---------------------------------------------------------------------------
# Metadata (first QR frame)
# ---------------------------------------------------------------------------

@dataclass
class FileMetadata:
    name: str
    size: int
    hash: str
    compressed: bool
    compression_ratio: float


@dataclass
class TransferMetadata:
    total_chunks: int
    grid_size: int
    fps: int
    protocol_version: str
    timestamp: str


@dataclass
class Metadata:
    file: FileMetadata
    transfer: TransferMetadata

    def to_json(self) -> str:
        return json.dumps({
            "file": {
                "name": self.file.name,
                "size": self.file.size,
                "hash": self.file.hash,
                "compressed": self.file.compressed,
                "compression_ratio": self.file.compression_ratio,
            },
            "transfer": {
                "total_chunks": self.transfer.total_chunks,
                "grid_size": self.transfer.grid_size,
                "fps": self.transfer.fps,
                "protocol_version": self.transfer.protocol_version,
                "timestamp": self.transfer.timestamp,
            },
        })

    @classmethod
    def from_json(cls, data: str) -> "Metadata":
        d = json.loads(data)
        return cls(
            file=FileMetadata(**d["file"]),
            transfer=TransferMetadata(**d["transfer"]),
        )


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

@dataclass
class EncodingResult:
    success: bool
    output_path: str
    frames: int
    file_size: int
    compressed_size: int
    video_size: int
    duration: float
