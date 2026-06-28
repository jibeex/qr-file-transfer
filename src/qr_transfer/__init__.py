"""QR File Transfer - Air-gapped file transfer using animated QR codes."""

__version__ = "0.1.0"
__author__ = "jibeex"
__all__ = ["FileEncoder", "FileDecoder"]


def __getattr__(name: str):
    if name == "FileEncoder":
        from qr_transfer.core.encoder import FileEncoder
        return FileEncoder
    if name == "FileDecoder":
        from qr_transfer.core.decoder import FileDecoder
        return FileDecoder
    raise AttributeError(f"module 'qr_transfer' has no attribute {name!r}")
