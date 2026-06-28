"""QR code detection from video frames."""
from __future__ import annotations
import ctypes
import ctypes.util
import os
from typing import Optional
import numpy as np
from qr_transfer.core.protocols import QRData


# ---------------------------------------------------------------------------
# Low-level zbar ctypes wrapper — bypasses pyzbar's pre-built binary
# which segfaults on Apple Silicon when loaded against Homebrew libzbar.
# ---------------------------------------------------------------------------

def _find_libzbar() -> Optional[str]:
    name = ctypes.util.find_library("zbar")
    if name:
        return name
    for p in ["/opt/homebrew/lib/libzbar.dylib", "/usr/local/lib/libzbar.dylib"]:
        if os.path.exists(p):
            return p
    return None


class _ZbarScanner:
    """Minimal ctypes wrapper around the zbar C library."""

    def __init__(self, libpath: str):
        lib = ctypes.cdll.LoadLibrary(libpath)

        lib.zbar_image_scanner_create.restype = ctypes.c_void_p
        lib.zbar_image_scanner_destroy.argtypes = [ctypes.c_void_p]
        lib.zbar_image_scanner_set_config.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.zbar_image_create.restype = ctypes.c_void_p
        lib.zbar_image_destroy.argtypes = [ctypes.c_void_p]
        lib.zbar_image_set_format.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        lib.zbar_image_set_size.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
        lib.zbar_image_set_data.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]
        lib.zbar_scan_image.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.zbar_scan_image.restype = ctypes.c_int
        lib.zbar_image_first_symbol.argtypes = [ctypes.c_void_p]
        lib.zbar_image_first_symbol.restype = ctypes.c_void_p
        lib.zbar_symbol_next.argtypes = [ctypes.c_void_p]
        lib.zbar_symbol_next.restype = ctypes.c_void_p
        lib.zbar_symbol_get_data.argtypes = [ctypes.c_void_p]
        lib.zbar_symbol_get_data.restype = ctypes.c_char_p
        lib.zbar_symbol_get_data_length.argtypes = [ctypes.c_void_p]
        lib.zbar_symbol_get_data_length.restype = ctypes.c_uint

        self._lib = lib
        self._scanner = lib.zbar_image_scanner_create()
        # Enable QR only (type 64), enable all configs (0=CFG_ENABLE, value=1)
        lib.zbar_image_scanner_set_config(self._scanner, 64, 0, 1)

    def decode(self, gray: np.ndarray) -> list[bytes]:
        lib = self._lib
        h, w = gray.shape
        img = lib.zbar_image_create()
        try:
            lib.zbar_image_set_format(img, 0x30303859)  # Y800 (grayscale)
            lib.zbar_image_set_size(img, w, h)
            buf = gray.tobytes()
            lib.zbar_image_set_data(img, buf, len(buf), None)
            lib.zbar_scan_image(self._scanner, img)

            results = []
            sym = lib.zbar_image_first_symbol(img)
            while sym:
                n = lib.zbar_symbol_get_data_length(sym)
                raw_ptr = lib.zbar_symbol_get_data(sym)
                results.append(ctypes.string_at(raw_ptr, n))
                sym = lib.zbar_symbol_next(sym)
            return results
        finally:
            lib.zbar_image_destroy(img)


class QRDetector:
    """Detects and decodes QR codes from video frames."""

    def __init__(self) -> None:
        import cv2
        self._cv2 = cv2
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        libpath = _find_libzbar()
        if libpath is None:
            raise ImportError(
                "Cannot find zbar shared library.\n"
                "  macOS: brew install zbar\n"
                "  Linux: sudo apt-get install libzbar0"
            )
        self._scanner = _ZbarScanner(libpath)

    def detect(self, frame: np.ndarray) -> list[QRData]:
        gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
        enhanced = self._enhance_contrast(gray)
        return [QRData(data=raw, type="QRCODE", rect=None) for raw in self._scanner.decode(enhanced)]

    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        return self._clahe.apply(img)
