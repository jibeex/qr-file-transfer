"""QR code detection from video frames."""
from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from qr_transfer.core.protocols import QRData

if TYPE_CHECKING:
    pass


class QRDetector:
    """Detects and decodes QR codes from video frames using pyzbar."""

    def __init__(self) -> None:
        import cv2
        self._cv2 = cv2
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        from pyzbar import pyzbar as _pyzbar
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

