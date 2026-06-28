"""QR code image generation."""

from __future__ import annotations

import qrcode
import qrcode.exceptions
from PIL import Image

from qr_transfer.constants import DEFAULT_GRID_SIZE, MAX_GRID_SIZE, MIN_GRID_SIZE
from qr_transfer.errors import QRGenerationError


class QRGenerator:
    """Generates QR code images with configurable grid size."""

    def __init__(self, grid_size: int = DEFAULT_GRID_SIZE) -> None:
        if not MIN_GRID_SIZE <= grid_size <= MAX_GRID_SIZE:
            raise ValueError(f"Grid size must be {MIN_GRID_SIZE}-{MAX_GRID_SIZE}")
        self.grid_size = grid_size

    def generate(self, data: bytes) -> Image.Image:
        """Generate a QR code image resized to grid_size×grid_size."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=4,
        )
        try:
            qr.add_data(data)
            qr.make(fit=True)
        except qrcode.exceptions.DataOverflowError as exc:
            raise QRGenerationError(f"Data too large for QR code: {exc}") from exc
        img = qr.make_image(fill_color="black", back_color="white").get_image()
        return img.resize((self.grid_size, self.grid_size), Image.Resampling.NEAREST)
