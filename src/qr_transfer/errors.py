"""Exception hierarchy for qr-transfer (IR-002 exit codes)."""

from __future__ import annotations
from typing import List, Optional


class QRTransferError(Exception):
    """Base exception for all QR transfer errors."""

    def __init__(
        self,
        message: str,
        error_code: int = 1,
        suggestions: Optional[List[str]] = None,
        details: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.details = details
        super().__init__(message)

    def format_user_message(self) -> str:
        parts = [f"✗ {self.message}"]
        if self.details:
            parts.append(f"\nDetails:\n  {self.details}")
        if self.suggestions:
            parts.append("\nSuggestions:")
            for s in self.suggestions:
                parts.append(f"  • {s}")
        parts.append(f"\nError code: {self.error_code}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# ValidationError branch
# ---------------------------------------------------------------------------

class ValidationError(QRTransferError):
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, error_code=3, suggestions=suggestions, details=details)


class InvalidParameterError(ValidationError):
    pass


class FileValidationError(ValidationError):
    pass


class SecurityError(ValidationError):
    pass


# ---------------------------------------------------------------------------
# EncodingError branch
# ---------------------------------------------------------------------------

class EncodingError(QRTransferError):
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, error_code=4, suggestions=suggestions, details=details)


class CompressionError(EncodingError):
    pass


class QRGenerationError(EncodingError):
    pass


class VideoCreationError(EncodingError):
    pass


# ---------------------------------------------------------------------------
# DecodingError branch
# ---------------------------------------------------------------------------

class DecodingError(QRTransferError):
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, error_code=5, suggestions=suggestions, details=details)


class VideoReadError(DecodingError):
    pass


class QRDetectionError(DecodingError):
    pass


class IncompleteTransferError(DecodingError):
    def __init__(self, message: str, missing_chunks: List[int], total_chunks: int):
        self.missing_chunks = missing_chunks
        self.total_chunks = total_chunks
        self.decoded_chunks = total_chunks - len(missing_chunks)
        self.completion_percent = (self.decoded_chunks / total_chunks * 100) if total_chunks else 0.0

        suggestions = [
            "Re-record the video with better lighting",
            "Keep camera steady at 20-40cm distance",
            "Ensure display brightness is at maximum",
            "Try with --grid-size 600 for easier scanning",
        ]
        missing_preview = missing_chunks[:20]
        details = (
            f"Total chunks: {total_chunks}\n"
            f"  Decoded: {self.decoded_chunks} ({self.completion_percent:.1f}%)\n"
            f"  Missing: {len(missing_chunks)}\n"
            f"  Missing chunk IDs: {missing_preview}"
            + ("..." if len(missing_chunks) > 20 else "")
        )
        # Bypass DecodingError.__init__ to set error_code directly via base
        QRTransferError.__init__(self, message, error_code=5, suggestions=suggestions, details=details)


class DecompressionError(DecodingError):
    pass


# ---------------------------------------------------------------------------
# IntegrityError branch
# ---------------------------------------------------------------------------

class IntegrityError(QRTransferError):
    def __init__(
        self,
        message: str,
        expected: Optional[str] = None,
        actual: Optional[str] = None,
    ):
        self.expected = expected
        self.actual = actual
        suggestions = [
            "DO NOT USE the decoded file - it is corrupted",
            "Retry the entire transfer from encoding",
            "If problem persists, check hardware (display, camera)",
            "Report issue if reproducible",
        ]
        details = (
            f"Expected hash: {expected}\nActual hash:   {actual}"
            if expected and actual
            else None
        )
        super().__init__(message, error_code=6, suggestions=suggestions, details=details)


class ChunkIntegrityError(IntegrityError):
    pass


class FileIntegrityError(IntegrityError):
    pass


# ---------------------------------------------------------------------------
# IOError branch  (QRTransferIOError avoids shadowing the builtin IOError)
# ---------------------------------------------------------------------------

class QRTransferIOError(QRTransferError):
    pass


class TransferFileNotFoundError(QRTransferIOError):
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, error_code=2, suggestions=suggestions, details=details)


class PermissionError(QRTransferIOError):  # noqa: A001
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, error_code=7, suggestions=suggestions, details=details)


class DiskSpaceError(QRTransferIOError):
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None):
        super().__init__(message, error_code=8, suggestions=suggestions, details=details)
