import ctypes
import os

"""Shared pytest fixtures and configuration."""
import os
import struct
import zlib
from pathlib import Path
import pytest

# ---------------------------------------------------------------------------
# Fixtures: test data
# ---------------------------------------------------------------------------

@pytest.fixture
def small_data() -> bytes:
    return b"hello qr-transfer world " * 10

@pytest.fixture
def binary_1kb() -> bytes:
    import secrets
    return secrets.token_bytes(1024)

@pytest.fixture
def binary_1mb() -> bytes:
    import secrets
    return secrets.token_bytes(1024 * 1024)

@pytest.fixture
def tmp_file(tmp_path, small_data) -> Path:
    p = tmp_path / "input.bin"
    p.write_bytes(small_data)
    return p

@pytest.fixture
def tmp_output(tmp_path) -> Path:
    return tmp_path / "output.bin"

# ---------------------------------------------------------------------------
# Fixtures: pre-built chunks (no QR/video needed)
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_chunk_bytes():
    """One valid packed chunk."""
    magic = b'QRFT'
    version = 1
    chunk_index = 0
    total_chunks = 1
    data = b"chunk payload"
    data_length = len(data)
    crc = zlib.crc32(data) & 0xFFFFFFFF
    reserved = 0
    header = struct.pack(">4sBIIHIB", magic, version, chunk_index, total_chunks, data_length, crc, reserved)
    return header + data

# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "hardware: requires iPhone + Mac hardware (manual)")
    config.addinivalue_line("markers", "slow: integration tests that encode/decode real QR")
    config.addinivalue_line("markers", "network: tests that check network isolation")
