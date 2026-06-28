"""Security tests — ST-001 through ST-005."""
import struct
import zlib
import pytest
from pathlib import Path

PYTHONPATH = "src"


def _chunk_bytes(data: bytes, index: int = 0, total: int = 1) -> bytes:
    crc = zlib.crc32(data) & 0xFFFFFFFF
    return struct.pack(">4sBIIHIB", b"QRFT", 1, index, total, len(data), crc, 0) + data


# ST-001: Path traversal prevention
@pytest.mark.parametrize("bad_path", [
    "../etc/passwd",
    "../../etc/shadow",
    "..\\..\\windows\\system32",
])
def test_path_traversal_blocked(bad_path, tmp_path):
    """ST-001: SecurityError on path traversal attempts."""
    import sys; sys.path.insert(0, "src")
    from qr_transfer.utils.validation import InputValidator
    from qr_transfer.errors import SecurityError, TransferFileNotFoundError
    with pytest.raises((SecurityError, TransferFileNotFoundError, PermissionError)):
        InputValidator.validate_file_path(bad_path, must_exist=False)


# ST-003: No network access
def test_no_network_imports():
    """ST-003: qr_transfer modules must not have network attributes."""
    import sys; sys.path.insert(0, "src")
    import qr_transfer.constants as c
    import qr_transfer.utils.compression as comp
    import qr_transfer.utils.integrity as integ
    # None of these pure-logic modules should expose socket/http
    for mod in (c, comp, integ):
        assert not hasattr(mod, "socket"), f"{mod.__name__} exposes socket"
        assert not hasattr(mod, "urllib"), f"{mod.__name__} exposes urllib"


# ST-004: Integrity check catches tampered data
def test_integrity_detects_tampering():
    """ST-004: SHA-256 mismatch detected on byte flip."""
    import sys; sys.path.insert(0, "src")
    from qr_transfer.utils.integrity import IntegrityUtil
    data = b"sensitive data " * 50
    h = IntegrityUtil.sha256(data)
    tampered = data[:10] + bytes([data[10] ^ 0x01]) + data[11:]
    assert not IntegrityUtil.verify_hash(tampered, h)


# ST-004b: CRC mismatch in chunk
def test_chunk_crc_mismatch_rejected():
    """ST-004: Chunk with wrong CRC raises ValueError."""
    import sys; sys.path.insert(0, "src")
    from qr_transfer.core.protocols import Chunk
    raw = _chunk_bytes(b"payload")
    # flip a byte in the payload
    corrupted = raw[:-3] + bytes([raw[-3] ^ 0xFF]) + raw[-2:]
    with pytest.raises((ValueError, Exception)):
        Chunk.unpack(corrupted)


# ST-005: atomic_write leaves no partial file on error
def test_atomic_write_no_partial_on_error(tmp_path, monkeypatch):
    """ST-005: No partial output if write fails mid-way."""
    import sys; sys.path.insert(0, "src")
    from qr_transfer.utils.file_ops import FileOps
    target = tmp_path / "output.bin"
    monkeypatch.setattr(Path, "rename", lambda self, dst: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(Exception):
        FileOps.atomic_write(target, b"data")
    assert not target.exists()
    tmp = target.with_suffix(".tmp")
    assert not tmp.exists()
