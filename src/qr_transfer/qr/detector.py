"""QR code detection from video frames — uses cv2 (no zbar/pyzbar needed)."""
from __future__ import annotations
import base64
import numpy as np
from qr_transfer.core.protocols import QRData


class QRDetector:
    """Detects QR codes using cv2.QRCodeDetector. Payloads are base64-encoded."""

    def __init__(self) -> None:
        import cv2
        self._cv2 = cv2
        self._detector = cv2.QRCodeDetector()
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def detect(self, frame: np.ndarray) -> list[QRData]:
        gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
        enhanced = self._enhance_contrast(gray)
        # Try multiple scales — cv2 QRCodeDetector struggles with large QR codes
        for scale in (0.4, 0.25, 0.6, 1.0):
            h, w = enhanced.shape
            resized = self._cv2.resize(enhanced, (int(w * scale), int(h * scale)))
            ok, decoded_list, *_ = self._detector.detectAndDecodeMulti(resized)
            if ok and any(decoded_list):
                results = []
                for s in decoded_list:
                    if not s:
                        continue
                    try:
                        raw = base64.b64decode(s.encode("latin-1"))
                        results.append(QRData(data=raw, type="QRCODE", rect=None))
                    except Exception:
                        pass
                if results:
                    return results
        return []

    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        return self._clahe.apply(img)
