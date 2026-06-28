"""Secure file I/O: atomic writes and secure deletion."""

import os
from pathlib import Path

from qr_transfer.errors import QRTransferIOError


class FileOps:
    """Atomic writes and secure deletion."""

    @staticmethod
    def atomic_write(path: Path, data: bytes) -> None:
        """Write data atomically: write to .tmp, fsync, rename to target."""
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            with open(tmp, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            tmp.rename(path)
        except OSError as exc:
            tmp.unlink(missing_ok=True)
            raise QRTransferIOError(str(exc)) from exc

    @staticmethod
    def secure_delete(path: Path, passes: int = 1) -> None:
        """Overwrite file with random bytes (passes times), then unlink."""
        if not path.exists():
            return
        size = path.stat().st_size
        with open(path, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        path.unlink()
