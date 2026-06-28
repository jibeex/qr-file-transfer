"""Unit tests for the error hierarchy (IR-002 exit codes)."""
import pytest
from qr_transfer.errors import (
    QRTransferError,
    ValidationError,
    EncodingError,
    DecodingError,
    IntegrityError,
    TransferFileNotFoundError,
    PermissionError as QRPermissionError,
    DiskSpaceError,
    IncompleteTransferError,
)
from qr_transfer import constants


@pytest.mark.parametrize("factory,expected_code", [
    (lambda: QRTransferError("e"),           constants.ERROR_GENERAL),
    (lambda: ValidationError("e"),           constants.ERROR_INVALID_INPUT),
    (lambda: EncodingError("e"),             constants.ERROR_ENCODING_FAILED),
    (lambda: DecodingError("e"),             constants.ERROR_DECODING_FAILED),
    (lambda: IntegrityError("e"),            constants.ERROR_INTEGRITY_FAILED),
    (lambda: TransferFileNotFoundError("e"), constants.ERROR_FILE_NOT_FOUND),
    (lambda: QRPermissionError("e"),         constants.ERROR_PERMISSION_DENIED),
    (lambda: DiskSpaceError("e"),            constants.ERROR_DISK_SPACE),
])
def test_error_codes(factory, expected_code):
    assert factory().error_code == expected_code


def test_qrtransfer_error_str_includes_message():
    err = QRTransferError("something went wrong")
    assert "something went wrong" in str(err)


def test_incomplete_transfer_carries_missing_chunks():
    missing = [2, 5, 7]
    err = IncompleteTransferError("incomplete", missing_chunks=missing, total_chunks=10)
    assert err.missing_chunks == missing
