"""Integration tests: full encode→decode pipeline (IT-001 – IT-009).

Real QR generation (qrcode) and real video creation (OpenCV). No mocking.
"""

from __future__ import annotations

import hashlib
import random
from pathlib import Path

import cv2
import pytest

from qr_transfer.core.decoder import FileDecoder
from qr_transfer.core.encoder import FileEncoder
from qr_transfer.errors import FileIntegrityError, IncompleteTransferError


# ---------------------------------------------------------------------------
# pyzbar availability
# ---------------------------------------------------------------------------

def _check_pyzbar() -> bool:
    try:
        from pyzbar import pyzbar  # noqa: F401
        return True
    except (ImportError, OSError):
        return False


pyzbar_available = pytest.mark.skipif(
    not _check_pyzbar(),
    reason="libzbar not installed",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _roundtrip(data: bytes, tmp_path: Path, suffix: str = ".bin", grid_size: int | None = None) -> bytes:
    src = tmp_path / f"input{suffix}"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"
    out = tmp_path / f"decoded{suffix}"

    kw: dict = {"quiet": True}
    if grid_size is not None:
        kw["grid_size"] = grid_size
    FileEncoder(**kw).encode(str(src), str(video))
    FileDecoder().decode(str(video), str(out), force=True)
    return out.read_bytes()


def _rewrite_video(src: Path, dst: Path, transform) -> None:
    """Read all frames, apply transform(frames) -> list[frame], write to dst."""
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 10
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    out = cv2.VideoWriter(str(dst), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for f in transform(frames):
        out.write(f)
    out.release()


# ---------------------------------------------------------------------------
# IT-001: Round-trip 1 byte
# ---------------------------------------------------------------------------

@pyzbar_available
@pytest.mark.slow
def test_it001_roundtrip_1_byte(tmp_path):
    data = b"X"
    assert _sha256(_roundtrip(data, tmp_path)) == _sha256(data)


# ---------------------------------------------------------------------------
# IT-004: Round-trip 20 file extensions
# ---------------------------------------------------------------------------

_EXTENSIONS = [
    ".txt", ".pdf", ".bin", ".jpg", ".png", ".zip", ".gz",
    ".csv", ".json", ".xml", ".mp3", ".wav", ".avi", ".mov",
    ".docx", ".xlsx", ".pptx", ".log", ".yaml", ".toml",
]

@pyzbar_available
@pytest.mark.slow
@pytest.mark.parametrize("suffix", _EXTENSIONS)
def test_it004_file_extensions(tmp_path, suffix):
    data = b"hello integration" * 8
    assert _sha256(_roundtrip(data, tmp_path, suffix=suffix)) == _sha256(data)


# ---------------------------------------------------------------------------
# IT-005: 5% frames removed → IncompleteTransferError with missing_chunks
# ---------------------------------------------------------------------------

@pyzbar_available
@pytest.mark.slow
def test_it005_frames_removed(tmp_path):
    data = b"frame removal test" * 20
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = tmp_path / "full.mp4"
    trimmed = tmp_path / "trimmed.mp4"
    out = tmp_path / "decoded.bin"

    FileEncoder(quiet=True).encode(str(src), str(video))

    def drop_5pct(frames):
        # Frame 0 is metadata; only drop data frames (index 1+)
        n = max(1, int((len(frames) - 1) * 0.05))
        drop = set(random.sample(range(1, len(frames)), min(n, len(frames) - 1)))
        return [f for i, f in enumerate(frames) if i not in drop]

    _rewrite_video(video, trimmed, drop_5pct)

    with pytest.raises(IncompleteTransferError) as exc_info:
        FileDecoder().decode(str(trimmed), str(out), force=True)

    assert exc_info.value.missing_chunks


# ---------------------------------------------------------------------------
# IT-006: Duplicate frames — decoder deduplicates, output identical
# ---------------------------------------------------------------------------

@pyzbar_available
@pytest.mark.slow
def test_it006_duplicate_frames(tmp_path):
    data = b"duplicate frame test" * 16
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = tmp_path / "full.mp4"
    duped = tmp_path / "duped.mp4"
    out = tmp_path / "decoded.bin"

    FileEncoder(quiet=True).encode(str(src), str(video))

    def duplicate_10pct(frames):
        n = max(1, int(len(frames) * 0.10))
        indices = sorted(random.sample(range(len(frames)), min(n, len(frames))), reverse=True)
        result = list(frames)
        for i in indices:
            result.insert(i, frames[i])
        return result

    _rewrite_video(video, duped, duplicate_10pct)
    FileDecoder().decode(str(duped), str(out), force=True)
    assert out.read_bytes() == data


# ---------------------------------------------------------------------------
# IT-008: Bit flip in video binary → FileIntegrityError, no output written
# ---------------------------------------------------------------------------

@pyzbar_available
@pytest.mark.slow
def test_it008_integrity_tamper(tmp_path):
    data = b"integrity tamper test " * 30
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = tmp_path / "full.mp4"
    tampered = tmp_path / "tampered.mp4"
    out = tmp_path / "decoded.bin"

    FileEncoder(quiet=True).encode(str(src), str(video))

    raw = bytearray(video.read_bytes())
    # Flip a byte in the last quarter — away from MP4 headers, likely in QR pixel data
    pos = len(raw) * 3 // 4
    raw[pos] ^= 0xFF
    tampered.write_bytes(bytes(raw))

    with pytest.raises((FileIntegrityError, IncompleteTransferError)):
        FileDecoder().decode(str(tampered), str(out), force=True)

    assert not out.exists()


# ---------------------------------------------------------------------------
# IT-009: Custom grid size 400 — encode and decode succeed
# ---------------------------------------------------------------------------

@pyzbar_available
@pytest.mark.slow
def test_it009_custom_grid_size_400(tmp_path):
    data = b"grid size 400 round-trip"
    assert _roundtrip(data, tmp_path, grid_size=400) == data
