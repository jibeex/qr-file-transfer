"""Unit tests for validation.py — UT-VAL-001 through UT-VAL-004."""

import pytest

from qr_transfer.constants import MAX_FILE_SIZE, MAX_FPS, MAX_GRID_SIZE, MIN_FPS, MIN_GRID_SIZE
from qr_transfer.errors import (
    FileValidationError,
    InvalidParameterError,
    SecurityError,
    TransferFileNotFoundError,
)
from qr_transfer.utils.validation import InputValidator


# ---------------------------------------------------------------------------
# UT-VAL-001: Path traversal — validate_file_path
# ---------------------------------------------------------------------------

def test_path_traversal_blocked():
    with pytest.raises(SecurityError):
        InputValidator.validate_file_path("../../etc/passwd")


def test_path_traversal_middle_blocked():
    with pytest.raises(SecurityError):
        InputValidator.validate_file_path("/tmp/../etc/passwd")


def test_valid_path_existing_file(tmp_path):
    f = tmp_path / "file.bin"
    f.write_bytes(b"data")
    result = InputValidator.validate_file_path(str(f))
    assert result == f.resolve()


def test_valid_path_must_exist_false(tmp_path):
    p = tmp_path / "new_file.bin"
    result = InputValidator.validate_file_path(str(p), must_exist=False)
    assert result == p.resolve()


def test_missing_file_raises():
    with pytest.raises(TransferFileNotFoundError):
        InputValidator.validate_file_path("/nonexistent/path/file.bin")


# ---------------------------------------------------------------------------
# UT-VAL-002: File size — validate_file_size
# ---------------------------------------------------------------------------

def test_file_size_zero_raises():
    with pytest.raises(FileValidationError):
        InputValidator.validate_file_size(0)


def test_file_size_negative_raises():
    with pytest.raises(FileValidationError):
        InputValidator.validate_file_size(-1)


def test_file_size_min_valid():
    assert InputValidator.validate_file_size(1) == 1


def test_file_size_max_valid():
    assert InputValidator.validate_file_size(MAX_FILE_SIZE) == MAX_FILE_SIZE


def test_file_size_over_max_raises():
    with pytest.raises(FileValidationError):
        InputValidator.validate_file_size(MAX_FILE_SIZE + 1)


# ---------------------------------------------------------------------------
# UT-VAL-003: Grid size — validate_grid_size
# ---------------------------------------------------------------------------

def test_grid_size_min_valid():
    assert InputValidator.validate_grid_size(MIN_GRID_SIZE) == MIN_GRID_SIZE


def test_grid_size_max_valid():
    assert InputValidator.validate_grid_size(MAX_GRID_SIZE) == MAX_GRID_SIZE


def test_grid_size_below_min_raises():
    with pytest.raises(InvalidParameterError):
        InputValidator.validate_grid_size(MIN_GRID_SIZE - 1)


def test_grid_size_above_max_raises():
    with pytest.raises(InvalidParameterError):
        InputValidator.validate_grid_size(MAX_GRID_SIZE + 1)


def test_grid_size_wrong_type_raises():
    with pytest.raises(InvalidParameterError):
        InputValidator.validate_grid_size(500.0)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# UT-VAL-004: FPS — validate_fps
# ---------------------------------------------------------------------------

def test_fps_min_valid():
    assert InputValidator.validate_fps(MIN_FPS) == MIN_FPS


def test_fps_max_valid():
    assert InputValidator.validate_fps(MAX_FPS) == MAX_FPS


def test_fps_below_min_raises():
    with pytest.raises(InvalidParameterError):
        InputValidator.validate_fps(MIN_FPS - 1)


def test_fps_above_max_raises():
    with pytest.raises(InvalidParameterError):
        InputValidator.validate_fps(MAX_FPS + 1)


def test_fps_wrong_type_raises():
    with pytest.raises(InvalidParameterError):
        InputValidator.validate_fps(10.0)  # type: ignore[arg-type]
