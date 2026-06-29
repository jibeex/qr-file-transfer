"""Shared pytest fixtures and configuration."""
import struct
import zlib
from collections import deque
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Camera-simulation utilities
#
# Simulates the iPhone recording step without pyzbar/libzbar.
# The encoder captures each raw QR payload as it's generated; the decoder
# replays those payloads directly — a perfect-fidelity software simulation.
# ---------------------------------------------------------------------------

class SimulatedDetector:
    """Fake QRDetector that replays pre-captured payloads in sequence."""

    def __init__(self, payloads: list[bytes]):
        self._queue = deque(payloads)

    def detect(self, frame):
        from qr_transfer.core.protocols import QRData
        if not self._queue:
            return []
        return [QRData(data=self._queue.popleft(), type="QRCODE", rect=None)]


def capture_payloads(src: str, video: str,
                     grid_size: int = 800, fps: int = 10, compression: bool = True,
                     anonymize_metadata: bool = False) -> list[bytes]:
    """Run encoder, return list of raw QR payloads (metadata + chunks) in order."""
    from qr_transfer.core.encoder import FileEncoder
    captured: list[bytes] = []

    import qr_transfer.qr.generator as _gen_mod
    OrigQRGen = _gen_mod.QRGenerator

    class CapturingQRGen(OrigQRGen):
        def generate(self, data: bytes, **kw):
            captured.append(data)
            return super().generate(data, **kw)

    with mock.patch.object(_gen_mod, "QRGenerator", CapturingQRGen), \
         mock.patch("qr_transfer.core.encoder.QRGenerator", CapturingQRGen):
        FileEncoder(grid_size=grid_size, fps=fps, compression=compression).encode(
            src, video, anonymize_metadata=anonymize_metadata
        )

    return captured


def decode_with_payloads(payloads: list[bytes], video: str, dst: str, **dec_kwargs) -> object:
    """Run decoder using simulated payloads instead of real QR detection."""
    from qr_transfer.core.decoder import FileDecoder
    decoder = FileDecoder()
    detector = SimulatedDetector(payloads)
    decoder._detector = detector
    return decoder.decode(video, dst, **dec_kwargs)


@pytest.fixture
def sim():
    """Expose capture_payloads / decode_with_payloads as a fixture namespace."""
    class _Sim:
        capture = staticmethod(capture_payloads)
        decode = staticmethod(decode_with_payloads)
        Detector = SimulatedDetector
    return _Sim()


# ---------------------------------------------------------------------------
# Basic data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_data() -> bytes:
    return b"hello qr-transfer world " * 10


@pytest.fixture
def binary_1kb() -> bytes:
    import secrets
    return secrets.token_bytes(1024)


@pytest.fixture
def tmp_file(tmp_path, small_data) -> Path:
    p = tmp_path / "input.bin"
    p.write_bytes(small_data)
    return p


@pytest.fixture
def tmp_output(tmp_path) -> Path:
    return tmp_path / "output.bin"


@pytest.fixture
def raw_chunk_bytes():
    magic = b"QRFT"
    data = b"chunk payload"
    crc = zlib.crc32(data) & 0xFFFFFFFF
    return struct.pack(">4sBIIHIB", magic, 1, 0, 1, len(data), crc, 0) + data


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "hardware: requires iPhone + Mac hardware (manual)")
    config.addinivalue_line("markers", "slow: integration/E2E tests")
    config.addinivalue_line("markers", "network: tests that check network isolation")
