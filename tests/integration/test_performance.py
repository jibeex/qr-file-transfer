"""Performance integration tests: PT-003, PT-004, PT-005 (TEST_PLAN.md §4.3)."""

import secrets
import time
import tracemalloc
from pathlib import Path
from unittest import mock

import pytest

from qr_transfer.core.encoder import FileEncoder
from qr_transfer.utils.progress import ProgressTracker


@pytest.mark.slow
def test_pt_003_encode_10kb_under_5s(tmp_path: Path) -> None:
    """PT-003 (NFR-002): encode 10 KB file completes in < 5 seconds."""
    data = secrets.token_bytes(10 * 1024)
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"

    start = time.monotonic()
    FileEncoder(quiet=True).encode(str(src), str(video))
    elapsed = time.monotonic() - start

    assert elapsed < 5.0, f"Encoding took {elapsed:.2f}s, expected < 5s"


@pytest.mark.slow
def test_pt_004_encode_50kb_memory(tmp_path: Path) -> None:
    """PT-004 (NFR-003): encode 50 KB file — peak memory stays reasonable (< 50 MB)."""
    data = secrets.token_bytes(50 * 1024)
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"

    tracemalloc.start()
    try:
        FileEncoder(quiet=True).encode(str(src), str(video))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    peak_mb = peak / (1024 ** 2)
    assert peak_mb < 50, f"Peak memory {peak_mb:.1f} MB exceeded 50 MB for 50 KB input"


@pytest.mark.slow
def test_pt_005_first_progress_update_under_2s(tmp_path: Path) -> None:
    """PT-005 (NFR-004): time from encode() start to first progress update < 2 seconds."""
    data = secrets.token_bytes(10 * 1024)
    src = tmp_path / "input.bin"
    src.write_bytes(data)
    video = tmp_path / "out.mp4"

    first_update: list[float] = []
    start = time.monotonic()

    original_update = ProgressTracker.update

    def capturing_update(self: ProgressTracker, n: int = 1) -> None:
        if not first_update:
            first_update.append(time.monotonic())
        original_update(self, n)

    with mock.patch.object(ProgressTracker, "update", capturing_update):
        FileEncoder(quiet=True).encode(str(src), str(video))

    assert first_update, "encode() never called progress.update()"
    elapsed = first_update[0] - start
    assert elapsed < 2.0, f"First progress update arrived after {elapsed:.2f}s, expected < 2s"
