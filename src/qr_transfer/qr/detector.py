"""QR code detection from video frames — uses cv2 QRCodeDetectorAruco (opencv>=4.8)."""
from __future__ import annotations
import base64
import numpy as np
from qr_transfer.core.protocols import QRData


class QRDetector:
    """Detects QR codes using cv2.QRCodeDetectorAruco. Payloads are base64-encoded."""

    def __init__(self) -> None:
        import cv2
        self._cv2 = cv2
        self._detector = cv2.QRCodeDetectorAruco()

    def detect(self, frame: np.ndarray) -> list[QRData]:
        gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
        for img in (gray, self._cv2.threshold(gray, 0, 255,
                    self._cv2.THRESH_BINARY + self._cv2.THRESH_OTSU)[1]):
            ok, decoded_list, *_ = self._detector.detectAndDecodeMulti(img)
            if ok and any(decoded_list):
                results = []
                for s in decoded_list:
                    if not s:
                        continue
                    try:
                        results.append(QRData(
                            data=base64.b64decode(s.encode("latin-1")),
                            type="QRCODE", rect=None,
                        ))
                    except Exception:
                        pass
                if results:
                    return results
        return []
