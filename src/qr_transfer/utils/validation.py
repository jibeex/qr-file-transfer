"""Input validation utilities."""

import os
from pathlib import Path

from qr_transfer.constants import MAX_FILE_SIZE, MAX_FPS, MAX_GRID_SIZE, MIN_FPS, MIN_GRID_SIZE
from qr_transfer.errors import (
    FileValidationError,
    InvalidParameterError,
    PermissionError,
    SecurityError,
    TransferFileNotFoundError,
)


class InputValidator:
    """Validates all user inputs. Single Responsibility: input validation only."""

    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Path:
        if ".." in path:
            raise SecurityError(f"Path traversal attempt detected: {path}")

        path_obj = Path(path).resolve()

        if must_exist and not path_obj.exists():
            raise TransferFileNotFoundError(f"File not found: {path}")

        if must_exist and not os.access(path_obj, os.R_OK):
            raise PermissionError(f"Cannot read file: {path}")

        return path_obj

    @staticmethod
    def validate_output_path(path: str, force: bool = False) -> Path:
        if ".." in path:
            raise SecurityError(f"Path traversal attempt detected: {path}")

        path_obj = Path(path).resolve()
        parent = path_obj.parent

        if not parent.exists():
            raise FileValidationError(f"Output directory does not exist: {parent}")

        if not os.access(parent, os.W_OK):
            raise PermissionError(f"Cannot write to directory: {parent}")

        if path_obj.exists() and not force:
            raise FileValidationError(
                f"Output file already exists: {path}",
                suggestions=["Use --force to overwrite the existing file"],
            )

        return path_obj

    @staticmethod
    def validate_grid_size(size: int) -> int:
        if not isinstance(size, int):
            raise InvalidParameterError(f"Grid size must be int, got {type(size).__name__}")
        if not MIN_GRID_SIZE <= size <= MAX_GRID_SIZE:
            raise InvalidParameterError(
                f"Grid size must be {MIN_GRID_SIZE}-{MAX_GRID_SIZE}, got {size}"
            )
        return size

    @staticmethod
    def validate_fps(fps: int) -> int:
        if not isinstance(fps, int):
            raise InvalidParameterError(f"FPS must be int, got {type(fps).__name__}")
        if not MIN_FPS <= fps <= MAX_FPS:
            raise InvalidParameterError(f"FPS must be {MIN_FPS}-{MAX_FPS}, got {fps}")
        return fps

    @staticmethod
    def validate_file_size(size: int) -> int:
        if size <= 0:
            raise FileValidationError("File is empty")
        if size > MAX_FILE_SIZE:
            raise FileValidationError(
                f"File too large: {size} bytes (max {MAX_FILE_SIZE})",
                suggestions=[
                    "Compress the file first",
                    "Split into smaller files",
                ],
            )
        return size
