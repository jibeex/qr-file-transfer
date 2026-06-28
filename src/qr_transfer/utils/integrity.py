import hashlib
import zlib

from qr_transfer.constants import ERROR_INTEGRITY_FAILED  # noqa: F401


class IntegrityUtil:
    """Handles cryptographic hashing and verification."""

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def crc32(data: bytes) -> int:
        return zlib.crc32(data) & 0xFFFFFFFF

    @staticmethod
    def verify_hash(data: bytes, expected_hash: str) -> bool:
        return IntegrityUtil.sha256(data) == expected_hash
