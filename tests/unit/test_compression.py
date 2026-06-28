"""Unit tests for compression.py."""

import gzip

import pytest

from qr_transfer.errors import DecompressionError
from qr_transfer.utils.compression import CompressionUtil


def test_compress_decompress_roundtrip():
    data = b"hello world" * 100
    assert CompressionUtil.decompress(CompressionUtil.compress(data)) == data


def test_compress_empty():
    assert CompressionUtil.decompress(CompressionUtil.compress(b"")) == b""


def test_compress_binary_data():
    data = bytes(range(256)) * 10
    assert CompressionUtil.decompress(CompressionUtil.compress(data)) == data


def test_compress_produces_gzip():
    compressed = CompressionUtil.compress(b"test data")
    # gzip magic bytes
    assert compressed[:2] == b"\x1f\x8b"


def test_compress_level_1():
    data = b"x" * 10000
    result = CompressionUtil.decompress(CompressionUtil.compress(data, level=1))
    assert result == data


def test_compress_level_9():
    data = b"x" * 10000
    result = CompressionUtil.decompress(CompressionUtil.compress(data, level=9))
    assert result == data


def test_decompress_bad_data_raises():
    with pytest.raises(DecompressionError):
        CompressionUtil.decompress(b"not gzip data")


def test_decompress_truncated_raises():
    compressed = CompressionUtil.compress(b"some data")
    with pytest.raises(DecompressionError):
        CompressionUtil.decompress(compressed[:5])

