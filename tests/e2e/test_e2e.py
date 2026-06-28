"""End-to-end tests: E2E-001 – E2E-004 — simulated camera, no pyzbar/iPhone needed."""
import hashlib
import math
import secrets
import time
from pathlib import Path
from unittest import mock

import pytest

from qr_transfer.core.decoder import FileDecoder
from qr_transfer.core.encoder import FileEncoder
from qr_transfer.errors import IncompleteTransferError


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.mark.slow
def test_e2e_001_config_file_transfer(tmp_path, sim):
    """UC-001: 5 KB YAML-like config → encode → decode → sha256 matches."""
    data = (b"key: value\nlist:\n  - item1\n  - item2\n" * 100)[:5120]
    src = tmp_path / "config.yaml"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.yaml")

    payloads = sim.capture(str(src), video)
    sim.decode(payloads, video, dst)

    assert _sha256(Path(dst).read_bytes()) == _sha256(data)


@pytest.mark.slow
def test_e2e_002_anonymize_metadata(tmp_path, sim):
    """UC-002: --anonymize-metadata → info shows no real filename."""
    key_data = secrets.token_bytes(1024)
    src = tmp_path / "private_key.bin"
    src.write_bytes(key_data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.bin")

    payloads = sim.capture(str(src), video, anonymize_metadata=True)
    sim.decode(payloads, video, dst)

    # Verify anonymization: metadata payload is first, parse its name field
    import json
    meta_json = json.loads(payloads[0].decode("utf-8"))
    assert meta_json["file"]["name"] == "anonymous"
    assert "private_key" not in meta_json["file"]["name"]


@pytest.mark.slow
def test_e2e_003_large_file_transfer(tmp_path, sim):
    """UC-003: 50 KB binary → encode → decode → sha256 matches, time ≤ 30 s."""
    data = secrets.token_bytes(50 * 1024)
    src = tmp_path / "document.bin"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.bin")

    start = time.monotonic()
    payloads = sim.capture(str(src), video)
    sim.decode(payloads, video, dst)
    elapsed = time.monotonic() - start

    assert _sha256(Path(dst).read_bytes()) == _sha256(data)
    assert elapsed <= 30.0, f"Transfer took {elapsed:.1f}s, expected ≤ 30s"


@pytest.mark.slow
def test_e2e_004_dropped_frames_raises_incomplete(tmp_path, sim):
    """UC-004: Drop 3% of data payloads → IncompleteTransferError with actionable message."""
    data = secrets.token_bytes(30 * 1024)
    src = tmp_path / "credentials.bin"
    src.write_bytes(data)
    video = str(tmp_path / "out.mp4")
    dst = str(tmp_path / "decoded.bin")

    payloads = sim.capture(str(src), video)
    # Keep metadata (index 0), drop 3% of data frames from the tail
    data_payloads = payloads[1:]
    n_drop = max(1, math.ceil(len(data_payloads) * 0.03))
    trimmed = [payloads[0]] + data_payloads[:-n_drop]

    with pytest.raises(IncompleteTransferError) as exc_info:
        sim.decode(trimmed, video, dst)

    err = exc_info.value
    assert err.missing_chunks
    assert err.total_chunks > 0
    assert str(err)
