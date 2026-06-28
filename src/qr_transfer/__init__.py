"""
QR File Transfer - Air-gapped file transfer using animated QR codes
"""

__version__ = "0.1.0"
__author__ = "QR Transfer Team"

from .encoder import FileEncoder
from .decoder import FileDecoder

__all__ = ["FileEncoder", "FileDecoder"]
