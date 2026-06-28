"""
Configuration Constants
─────────────────────────────────────────────────────────

All configurable values in one place.
Follows Open/Closed Principle: extend without modifying code.
"""

from dataclasses import dataclass
from typing import Final

# File Size Limits
MAX_FILE_SIZE: Final[int] = 1_000_000_000  # 1 GB
MIN_FILE_SIZE: Final[int] = 1  # 1 byte

# QR Code Parameters
MIN_GRID_SIZE: Final[int] = 177
MAX_GRID_SIZE: Final[int] = 1000
DEFAULT_GRID_SIZE: Final[int] = 800

# Video Parameters
MIN_FPS: Final[int] = 5
MAX_FPS: Final[int] = 30
DEFAULT_FPS: Final[int] = 10

# Chunk Parameters
MAX_CHUNK_SIZE: Final[int] = 500   # bytes (cv2 QRCodeDetector reliable up to QR v15)
CHUNK_HEADER_SIZE: Final[int] = 20  # bytes: 4+1+4+4+2+4+1 ('>4sBIIHIB')
CHUNK_MAGIC: Final[bytes] = b'QRFT'

# Compression Parameters
DEFAULT_COMPRESSION_LEVEL: Final[int] = 6
MIN_COMPRESSION_LEVEL: Final[int] = 1
MAX_COMPRESSION_LEVEL: Final[int] = 9

# Error Codes (IR-002)
ERROR_SUCCESS: Final[int] = 0
ERROR_GENERAL: Final[int] = 1
ERROR_FILE_NOT_FOUND: Final[int] = 2
ERROR_INVALID_INPUT: Final[int] = 3
ERROR_ENCODING_FAILED: Final[int] = 4
ERROR_DECODING_FAILED: Final[int] = 5
ERROR_INTEGRITY_FAILED: Final[int] = 6
ERROR_PERMISSION_DENIED: Final[int] = 7
ERROR_DISK_SPACE: Final[int] = 8

# Protocol Version
PROTOCOL_VERSION: Final[str] = "1.0.0"


@dataclass(frozen=True)
class VideoConfig:
    """Video encoding configuration."""
    codec: str = 'mp4v'
    pixel_format: str = 'yuv420p'
    quality: int = 95  # 0-100


@dataclass(frozen=True)
class QRConfig:
    """QR code configuration."""
    error_correction: str = 'M'  # L, M, Q, H
    border: int = 4  # Quiet zone modules


@dataclass(frozen=True)
class PerformanceConfig:
    """Performance tuning configuration."""
    parallel_qr_generation: bool = True
    max_workers: int = None  # None = cpu_count()
    frame_sample_rate: int = 1  # Extract every Nth frame


# Singleton configurations
VIDEO_CONFIG = VideoConfig()
QR_CONFIG = QRConfig()
PERFORMANCE_CONFIG = PerformanceConfig()
