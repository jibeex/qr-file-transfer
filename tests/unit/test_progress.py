"""Unit tests for ProgressTracker."""
import io
import pytest
from qr_transfer.utils.progress import ProgressTracker


def test_quiet_false_emits_progress_with_percent(monkeypatch):
    """UT-PRG-001: quiet=False creates tqdm bar that includes % in output."""
    buf = io.StringIO()
    monkeypatch.setattr(
        "qr_transfer.utils.progress.tqdm",
        lambda *a, **kw: __import__("tqdm").tqdm(*a, **{**kw, "file": buf}),
    )
    with ProgressTracker(total=10, description="test", quiet=False) as pt:
        pt.update(5)
    assert "%" in buf.getvalue()


def test_quiet_true_suppresses_output():
    """quiet=True sets _pbar to None and update is a no-op."""
    with ProgressTracker(total=10, quiet=True) as pt:
        assert pt._pbar is None
        pt.update(5)  # must not raise


def test_context_manager_enter_returns_self():
    pt = ProgressTracker(total=5, quiet=True)
    assert pt.__enter__() is pt
    pt.__exit__(None, None, None)


def test_context_manager_calls_close(monkeypatch):
    pt = ProgressTracker(total=5, quiet=True)
    closed = []
    monkeypatch.setattr(pt, "close", lambda: closed.append(True))
    with pt:
        pass
    assert closed == [True]
