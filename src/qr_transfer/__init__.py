"""QR File Transfer - Air-gapped file transfer using animated QR codes."""
import importlib

__version__ = "0.1.0"
__author__ = "jibeex"
__all__ = ["FileEncoder", "FileDecoder"]

_LAZY = {
    "FileEncoder": ("qr_transfer.core.encoder", "FileEncoder"),
    "FileDecoder": ("qr_transfer.core.decoder", "FileDecoder"),
}


def __getattr__(name: str):
    if name in _LAZY:
        mod, attr = _LAZY[name]
        return getattr(importlib.import_module(mod), attr)
    raise AttributeError(f"module 'qr_transfer' has no attribute {name!r}")
