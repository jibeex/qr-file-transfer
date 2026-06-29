"""Integration tests: IT-001 – IT-009 — simulated camera, no pyzbar/iPhone needed."""
from __future__ import annotations

import random
import secrets
from pathlib import Path

import pytest

from qr_transfer.core.encoder import FileEncoder
from qr_transfer.errors import FileIntegrityError, IncompleteTransferError


from qr_transfer.utils.integrity import IntegrityUtil as _I
_sha256 = _I.sha256


def _roundtrip(data: bytes, tmp_path: Path, sim, suffix: str = ".bin", **enc_kw) -> bytes:
    src = tmp_path / f"input{suffix}"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / f"decoded{suffix}")
    payloads = sim.capture(str(src), video, **enc_kw)
    sim.decode(payloads, video, dst)
    return Path(dst).read_bytes()


@pytest.mark.slow
def test_it001_roundtrip_1_byte(tmp_path, sim):
    data = b"X"
    assert _roundtrip(data, tmp_path, sim) == data


@pytest.mark.slow
@pytest.mark.parametrize("suffix", [
    ".txt", ".pdf", ".bin", ".jpg", ".png", ".zip", ".gz",
    ".csv", ".json", ".xml", ".mp3", ".wav", ".avi", ".mov",
    ".docx", ".xlsx", ".pptx", ".log", ".yaml", ".toml",
])
def test_it004_file_extensions(tmp_path, sim, suffix):
    data = b"hello integration" * 8
    assert _roundtrip(data, tmp_path, sim, suffix=suffix) == data


@pytest.mark.slow
def test_it005_frames_removed(tmp_path, sim):
    """IT-005: Drop 5% of data payloads → IncompleteTransferError with missing_chunks."""
    data = b"frame removal test" * 20
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.bin")

    payloads = sim.capture(str(src), video)
    # payload[0] is metadata; drop ALL copies of at least one chunk
    # With redundancy=3: payloads are [meta, c0m0, c0m1, c0m2, c1m0, c1m1, c1m2, ...]
    # Drop ALL payloads for the last chunk (last 3 entries)
    reduced = payloads[:-3]  # remove last chunk's 3 copies

    with pytest.raises(IncompleteTransferError) as exc_info:
        sim.decode(reduced, video, dst)
    assert exc_info.value.missing_chunks


@pytest.mark.slow
def test_it006_duplicate_frames(tmp_path, sim):
    """IT-006: Duplicate 10% of payloads → decoder deduplicates, output identical."""
    data = b"duplicate frame test" * 16
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.bin")

    payloads = sim.capture(str(src), video)
    # Duplicate every 10th data payload
    duped = list(payloads)
    for i in range(len(payloads) - 1, 0, -10):
        duped.insert(i, payloads[i])

    sim.decode(duped, video, dst)
    assert Path(dst).read_bytes() == data


@pytest.mark.slow
def test_it008_integrity_tamper(tmp_path, sim):
    """IT-008: Corrupt one chunk payload → FileIntegrityError or IncompleteTransferError."""
    data = b"integrity tamper test " * 30
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.bin")

    payloads = sim.capture(str(src), video)
    # Corrupt ALL 3 copies of the last chunk (last 3 payloads)
    for idx in range(1, min(4, len(payloads))):
        bad = bytearray(payloads[-idx])
        bad[20] ^= 0xFF  # flip byte in data region (after 20-byte header)
        payloads[-idx] = bytes(bad)

    with pytest.raises((FileIntegrityError, IncompleteTransferError)):
        sim.decode(payloads, video, dst)
    assert not Path(dst).exists()


@pytest.mark.slow
def test_it009_custom_grid_size_400(tmp_path, sim):
    """IT-009: Custom grid_size=400 → encode and decode succeed."""
    data = b"grid size 400 round-trip"
    assert _roundtrip(data, tmp_path, sim, grid_size=400) == data
