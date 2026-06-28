"""Unit tests for FileOps."""
from pathlib import Path
import pytest
from qr_transfer.utils.file_ops import FileOps
from qr_transfer.errors import QRTransferIOError


def test_atomic_write_writes_correctly(tmp_path):
    target = tmp_path / "output.bin"
    data = b"hello atomic world"
    FileOps.atomic_write(target, data)
    assert target.read_bytes() == data
    assert not target.with_suffix(target.suffix + ".tmp").exists()


def test_atomic_write_cleans_up_tmp_on_error(tmp_path, monkeypatch):
    target = tmp_path / "output.bin"

    def bad_rename(self, dst):
        raise OSError("rename failed")

    monkeypatch.setattr(Path, "rename", bad_rename)

    with pytest.raises(QRTransferIOError):
        FileOps.atomic_write(target, b"data")

    tmp = target.with_suffix(target.suffix + ".tmp")
    assert not tmp.exists()


def test_secure_delete_removes_file(tmp_path):
    f = tmp_path / "secret.bin"
    f.write_bytes(b"sensitive")
    FileOps.secure_delete(f)
    assert not f.exists()


def test_secure_delete_noop_if_missing(tmp_path):
    f = tmp_path / "nonexistent.bin"
    FileOps.secure_delete(f)  # must not raise
