"""QR code detection from video frames."""
from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from qr_transfer.core.protocols import QRData

if TYPE_CHECKING:
    pass


def _ensure_zbar() -> None:
    """Patch ctypes.util.find_library to find zbar on Apple Silicon (Homebrew)."""
    import ctypes.util as _cu, os
    if _cu.find_library("zbar") is not None:
        return
    _orig = _cu.find_library
    def _patched(name):
        if name == "zbar":
            for p in ["/opt/homebrew/lib/libzbar.dylib", "/usr/local/lib/libzbar.dylib"]:
                if os.path.exists(p):
                    return p
        return _orig(name)
    _cu.find_library = _patched


class QRDetector:
    """Detects and decodes QR codes from video frames using pyzbar."""

    def __init__(self) -> None:
        import cv2
        _ensure_zbar()
        from pyzbar import pyzbar as _pyzbar
        self._cv2 = cv2
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self._pyzbar = _pyzbar

    def detect(self, frame: np.ndarray) -> list[QRData]:
        gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
        enhanced = self._enhance_contrast(gray)
        return [
            QRData(data=obj.data, type=obj.type, rect=obj.rect)
            for obj in self._pyzbar.decode(enhanced)
        ]

    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        return self._clahe.apply(img)
