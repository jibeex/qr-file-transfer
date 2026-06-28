"""Unit tests for protocols.py — UT-CHK-001, UT-META-001."""

import json
import struct
import zlib

import pytest

from qr_transfer.constants import CHUNK_HEADER_SIZE, CHUNK_MAGIC
from qr_transfer.core.protocols import (
    Chunk,
    ChunkHeader,
    FileMetadata,
    Metadata,
    TransferMetadata,
)


# ---------------------------------------------------------------------------
# UT-CHK-001: Chunk pack / unpack
# ---------------------------------------------------------------------------

def _make_chunk(data: bytes, index: int = 0, total: int = 1) -> Chunk:
    crc = zlib.crc32(data) & 0xFFFFFFFF
    return Chunk(header=ChunkHeader(chunk_index=index, total_chunks=total, data_length=len(data), crc32=crc), data=data)


def test_chunk_pack_magic_and_header_size():
    chunk = _make_chunk(b"hello")
    packed = chunk.pack()
    assert packed[:4] == CHUNK_MAGIC
    assert len(packed) >= CHUNK_HEADER_SIZE


def test_chunk_pack_version():
    packed = _make_chunk(b"test").pack()
    version = struct.unpack_from(">B", packed, 4)[0]
    assert version == 1


def test_chunk_pack_crc_correct():
    data = b"some data for crc"
    packed = _make_chunk(data).pack()
    # CRC is at offset 4+1+4+4+2 = 15, 4 bytes big-endian
    crc_in_header = struct.unpack_from(">I", packed, 15)[0]
    assert crc_in_header == zlib.crc32(data) & 0xFFFFFFFF


def test_chunk_roundtrip():
    data = b"\x00\xff\xab\xcd" * 100
    chunk = _make_chunk(data, index=3, total=10)
    unpacked = Chunk.unpack(chunk.pack())
    assert unpacked.data == data
    assert unpacked.header.chunk_index == 3
    assert unpacked.header.total_chunks == 10


def test_chunk_unpack_too_short():
    with pytest.raises(ValueError, match="too short"):
        Chunk.unpack(b"\x00" * (CHUNK_HEADER_SIZE - 1))


def test_chunk_unpack_bad_magic():
    data = b"payload"
    packed = bytearray(_make_chunk(data).pack())
    packed[0] = ord('X')  # corrupt magic
    with pytest.raises(ValueError, match="magic"):
        Chunk.unpack(bytes(packed))


def test_chunk_unpack_bad_version():
    data = b"payload"
    packed = bytearray(_make_chunk(data).pack())
    packed[4] = 99  # corrupt version byte
    with pytest.raises(ValueError, match="version"):
        Chunk.unpack(bytes(packed))


def test_chunk_unpack_crc_mismatch():
    data = b"payload"
    packed = bytearray(_make_chunk(data).pack())
    packed[-1] ^= 0xFF  # flip last byte of payload
    with pytest.raises(ValueError, match="CRC"):
        Chunk.unpack(bytes(packed))


def test_chunk_unpack_truncated_payload():
    data = b"enough data here"
    packed = _make_chunk(data).pack()
    # Drop last 5 bytes — payload becomes shorter than data_length says
    with pytest.raises(ValueError, match="[Tt]runcated"):
        Chunk.unpack(packed[:-5])


def test_chunk_empty_data():
    chunk = _make_chunk(b"")
    unpacked = Chunk.unpack(chunk.pack())
    assert unpacked.data == b""


# ---------------------------------------------------------------------------
# UT-META-001: Metadata JSON roundtrip
# ---------------------------------------------------------------------------

def _make_metadata() -> Metadata:
    return Metadata(
        file=FileMetadata(name="file.bin", size=1024, hash="abc123", compressed=True, compression_ratio=0.75),
        transfer=TransferMetadata(total_chunks=10, grid_size=800, fps=10, protocol_version="1.0.0", timestamp="2026-06-28T00:00:00Z"),
    )


def test_metadata_roundtrip_all_fields():
    m = _make_metadata()
    restored = Metadata.from_json(m.to_json())
    assert restored.file.name == m.file.name
    assert restored.file.size == m.file.size
    assert restored.file.hash == m.file.hash
    assert restored.file.compressed == m.file.compressed
    assert restored.file.compression_ratio == m.file.compression_ratio
    assert restored.transfer.total_chunks == m.transfer.total_chunks
    assert restored.transfer.grid_size == m.transfer.grid_size
    assert restored.transfer.fps == m.transfer.fps
    assert restored.transfer.protocol_version == m.transfer.protocol_version
    assert restored.transfer.timestamp == m.transfer.timestamp


def test_metadata_to_json_is_valid_json():
    raw = _make_metadata().to_json()
    parsed = json.loads(raw)
    assert "file" in parsed and "transfer" in parsed


def test_metadata_compressed_false():
    m = _make_metadata()
    m.file.compressed = False
    restored = Metadata.from_json(m.to_json())
    assert restored.file.compressed is False
