"""Unit tests for integrity.py — UT-INT-001."""

import hashlib
import zlib

from qr_transfer.utils.integrity import IntegrityUtil


def test_sha256_known_value():
    data = b"hello"
    assert IntegrityUtil.sha256(data) == hashlib.sha256(data).hexdigest()


def test_sha256_empty():
    assert IntegrityUtil.sha256(b"") == hashlib.sha256(b"").hexdigest()


def test_sha256_returns_hex_string():
    result = IntegrityUtil.sha256(b"data")
    assert isinstance(result, str)
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_sha256_different_data_different_hash():
    assert IntegrityUtil.sha256(b"a") != IntegrityUtil.sha256(b"b")


def test_crc32_known_value():
    data = b"hello"
    assert IntegrityUtil.crc32(data) == zlib.crc32(data) & 0xFFFFFFFF


def test_crc32_empty():
    assert IntegrityUtil.crc32(b"") == zlib.crc32(b"") & 0xFFFFFFFF


def test_crc32_returns_unsigned_int():
    result = IntegrityUtil.crc32(b"\xff" * 100)
    assert isinstance(result, int)
    assert 0 <= result <= 0xFFFFFFFF


def test_verify_hash_match():
    data = b"some bytes"
    h = IntegrityUtil.sha256(data)
    assert IntegrityUtil.verify_hash(data, h) is True


def test_verify_hash_mismatch():
    data = b"some bytes"
    wrong = "a" * 64
    assert IntegrityUtil.verify_hash(data, wrong) is False


def test_verify_hash_empty_data():
    h = IntegrityUtil.sha256(b"")
    assert IntegrityUtil.verify_hash(b"", h) is True
    assert IntegrityUtil.verify_hash(b"x", h) is False
