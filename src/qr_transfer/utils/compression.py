"""Gzip compression utility."""

import gzip
import zlib

from qr_transfer.constants import DEFAULT_COMPRESSION_LEVEL
from qr_transfer.errors import DecompressionError


class CompressionUtil:
    """Handles data compression using gzip."""

    @staticmethod
    def compress(data: bytes, level: int = DEFAULT_COMPRESSION_LEVEL) -> bytes:
        return gzip.compress(data, compresslevel=level)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        try:
            return gzip.decompress(data)
        except (gzip.BadGzipFile, EOFError, zlib.error) as e:
            raise DecompressionError(f"Invalid gzip data: {e}") from e
