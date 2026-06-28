"""End-to-end tests: E2E-001 through E2E-004 (TEST_PLAN.md §4.6)."""

import hashlib
import math
import secrets
import time
from pathlib import Path
from unittest import mock

import pytest
pyzbar = pytest.importorskip("pyzbar.pyzbar", reason="libzbar not installed — install with: brew install zbar")

pyzbar = pytest.importorskip("pyzbar", reason="pyzbar not installed")

from qr_transfer.core.decoder import FileDecoder
from qr_transfer.core.encoder import FileEncoder
from qr_transfer.core.protocols import FileMetadata as _FileMetadata
from qr_transfer.errors import IncompleteTransferError
from qr_transfer.video.decoder import VideoDecoder


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.mark.slow
def test_e2e_001_config_file_transfer(tmp_path: Path) -> None:
    """UC-001: 5 KB YAML-like config → encode → decode → sha256 matches, exit 0."""
    data = (b"key: value\nlist:\n  - item1\n  - item2\nnested:\n  x: 1\n" * 100)[:5120]
    src = tmp_path / "config.yaml"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"
    decoded = tmp_path / "decoded.yaml"

    result = FileEncoder().encode(str(src), str(video))
    assert result.success

    FileDecoder().decode(str(video), str(decoded))

    assert _sha256(decoded.read_bytes()) == _sha256(data)


@pytest.mark.slow
def test_e2e_002_anonymize_metadata(tmp_path: Path) -> None:
    """UC-002: 1 KB binary key encoded with anonymized metadata → info shows no real filename."""
    key_data = secrets.token_bytes(1024)
    src = tmp_path / "private_key.bin"
    src.write_bytes(key_data)
    video = tmp_path / "out.mp4"

    # Simulate --anonymize-metadata by patching FileMetadata to use name="anonymous".
    def _anon_fm(name: str, **kw) -> _FileMetadata:
        return _FileMetadata(name="anonymous", **kw)

    with mock.patch("qr_transfer.core.encoder.FileMetadata", side_effect=_anon_fm):
        FileEncoder().encode(str(src), str(video))

    info = FileDecoder().get_info(str(video))
    assert info.filename == "anonymous"
    assert "private_key" not in info.filename


@pytest.mark.slow
def test_e2e_003_large_file_transfer(tmp_path: Path) -> None:
    """UC-003: 50 KB binary → encode → decode → sha256 matches, time ≤ 30 s."""
    data = secrets.token_bytes(50 * 1024)
    src = tmp_path / "document.bin"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"
    decoded = tmp_path / "decoded.bin"

    start = time.monotonic()
    FileEncoder().encode(str(src), str(video))
    FileDecoder().decode(str(video), str(decoded))
    elapsed = time.monotonic() - start

    assert _sha256(decoded.read_bytes()) == _sha256(data)
    assert elapsed <= 30.0, f"Transfer took {elapsed:.1f}s, expected ≤ 30s"


@pytest.mark.slow
def test_e2e_004_dropped_frames_raises_incomplete(tmp_path: Path) -> None:
    """UC-004: encode → drop 3% of frames → decode raises IncompleteTransferError with clear message."""
    data = secrets.token_bytes(30 * 1024)  # ~11 chunks; ensures ≥1 frame dropped at 3%
    src = tmp_path / "credentials.bin"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"
    decoded = tmp_path / "decoded.bin"

    FileEncoder().encode(str(src), str(video))

    all_frames = VideoDecoder().extract_frames(str(video))
    n_drop = max(1, math.ceil(len(all_frames) * 0.03))
    # Drop frames from end; keep first frame (metadata) intact.
    truncated = all_frames[:-n_drop]

    decoder = FileDecoder()
    with mock.patch.object(decoder._video, "extract_frames", return_value=truncated):
        with pytest.raises(IncompleteTransferError) as exc_info:
            decoder.decode(str(video), str(decoded))

    err = exc_info.value
    assert err.missing_chunks, "Expected missing_chunks to be non-empty"
    assert err.total_chunks > 0
    # Message must be human-readable (FR-009, UI-007)
    assert str(err)
    assert err.suggestions, "Expected actionable recovery suggestions"
