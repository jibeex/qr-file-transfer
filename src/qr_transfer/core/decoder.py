"""QR file transfer decoder — FileDecoder, GracefulDegradation."""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qr_transfer.constants import CHUNK_HEADER_SIZE, CHUNK_MAGIC
from qr_transfer.core.protocols import Chunk, QRData
from qr_transfer.errors import (
    DecodingError,
    FileIntegrityError,
    IncompleteTransferError,
)
from qr_transfer.qr.detector import QRDetector
from qr_transfer.utils.compression import CompressionUtil
from qr_transfer.utils.file_ops import FileOps
from qr_transfer.utils.integrity import IntegrityUtil
from qr_transfer.utils.validation import InputValidator
from qr_transfer.video.decoder import VideoDecoder


# ---------------------------------------------------------------------------
# Result / metadata types
# ---------------------------------------------------------------------------

@dataclass
class Metadata:
    version: str
    filename: str
    file_size: int
    sha256: str
    total_chunks: int
    compressed: bool

    @classmethod
    def from_json(cls, raw: bytes) -> "Metadata":
        d = json.loads(raw)
        f = d["file"]
        t = d["transfer"]
        return cls(
            version=d.get("version", "1.0.0"),
            filename=f["name"],
            file_size=f["size"],
            sha256=f.get("hash", ""),
            total_chunks=t["total_chunks"],
            compressed=f.get("compressed", False),
        )


@dataclass
class DecodingResult:
    output_path: Path
    filename: str
    file_size: int
    total_chunks: int
    sha256: str


@dataclass
class VerifyResult:
    valid: bool
    total_chunks: int
    decoded_chunks: int
    missing: list[int] = field(default_factory=list)
    metadata: Metadata | None = None


# ---------------------------------------------------------------------------
# Chunk parsing helpers
# ---------------------------------------------------------------------------

def _is_metadata(data: bytes) -> bool:
    return data.startswith(b"{")





# ---------------------------------------------------------------------------
# GracefulDegradation (§8.3)
# ---------------------------------------------------------------------------

class GracefulDegradation:
    """Two-pass QR detection: normal pass, then aggressive preprocessing on failures."""

    @staticmethod
    def decode_with_fallback(
        frames: list[np.ndarray],
        detector: QRDetector,
    ) -> list[tuple[int, list[QRData]]]:
        results: list[tuple[int, list[QRData]]] = []
        failed: list[int] = []

        for i, frame in enumerate(frames):
            qrs = detector.detect(frame)
            if qrs:
                results.append((i, qrs))
            else:
                failed.append(i)

        if failed:
            import cv2 as _cv2
            for i in failed:
                gray = _cv2.cvtColor(frames[i], _cv2.COLOR_BGR2GRAY)
                denoised = _cv2.bilateralFilter(gray, 9, 75, 75)
                _, thresh = _cv2.threshold(denoised, 0, 255, _cv2.THRESH_BINARY + _cv2.THRESH_OTSU)
                qrs = detector.detect(_cv2.cvtColor(thresh, _cv2.COLOR_GRAY2BGR))
                if qrs:
                    results.append((i, qrs))

        return results


# ---------------------------------------------------------------------------
# FileDecoder
# ---------------------------------------------------------------------------

class FileDecoder:
    """Decode a QR-transfer video back into the original file."""

    def __init__(self) -> None:
        self._video = VideoDecoder()
        self._detector: QRDetector | None = None

    def _get_detector(self) -> QRDetector:
        if self._detector is None:
            self._detector = QRDetector()
        return self._detector

    def decode(
        self,
        input_path: str | Path,
        output_path: str | Path,
        force: bool = False,
    ) -> DecodingResult:
        src = InputValidator.validate_file_path(str(input_path))
        dst = InputValidator.validate_output_path(str(output_path), force=force)

        frames = self._video.extract_frames(str(src))
        if not frames:
            raise DecodingError("No frames extracted from video.")

        metadata, chunks = self._collect(
            GracefulDegradation.decode_with_fallback(frames, self._get_detector())
        )
        if metadata is None:
            raise DecodingError("Metadata frame not found in video.")

        missing = [i for i in range(metadata.total_chunks) if i not in chunks]
        if missing:
            raise IncompleteTransferError(
                f"Transfer incomplete: {len(missing)}/{metadata.total_chunks} chunks missing.",
                missing_chunks=missing,
                total_chunks=metadata.total_chunks,
            )

        file_data = self._reconstruct(chunks, metadata)
        FileOps.atomic_write(dst, file_data)

        return DecodingResult(
            output_path=dst,
            filename=metadata.filename,
            file_size=metadata.file_size,
            total_chunks=metadata.total_chunks,
            sha256=metadata.sha256,
        )

    def verify(self, input_path: str | Path, detailed: bool = False) -> VerifyResult:
        src = InputValidator.validate_file_path(str(input_path))
        frames = self._video.extract_frames(str(src))
        metadata, chunks = self._collect(
            GracefulDegradation.decode_with_fallback(frames, self._get_detector())
        )
        if metadata is None:
            return VerifyResult(valid=False, total_chunks=0, decoded_chunks=0)

        missing = [i for i in range(metadata.total_chunks) if i not in chunks]
        return VerifyResult(
            valid=not missing,
            total_chunks=metadata.total_chunks,
            decoded_chunks=len(chunks),
            missing=missing,
            metadata=metadata if detailed else None,
        )

    def get_info(self, input_path: str | Path) -> Metadata:
        src = InputValidator.validate_file_path(str(input_path))
        for frame in self._video.extract_frames(str(src)):
            for qr in self._get_detector().detect(frame):
                if _is_metadata(qr.data):
                    try:
                        return Metadata.from_json(qr.data)
                    except (KeyError, json.JSONDecodeError):
                        pass
        raise DecodingError("Metadata frame not found in video.")

    # ------------------------------------------------------------------

    def _collect(
        self,
        frame_qr_pairs: list[tuple[int, list[QRData]]],
    ) -> tuple[Metadata | None, dict[int, bytes]]:
        metadata: Metadata | None = None
        chunks: dict[int, bytes] = {}

        for _idx, qrs in frame_qr_pairs:
            for qr in qrs:
                if _is_metadata(qr.data):
                    if metadata is None:
                        try:
                            metadata = Metadata.from_json(qr.data)
                        except (KeyError, json.JSONDecodeError):
                            pass
                    continue
                try:
                    chunk = Chunk.unpack(qr.data)
                    if chunk.header.chunk_index not in chunks:
                        chunks[chunk.header.chunk_index] = chunk.data
                except (ValueError, Exception):
                    pass

        return metadata, chunks

    def _reconstruct(self, chunks: dict[int, bytes], metadata: Metadata) -> bytes:
        raw = b"".join(chunks[i] for i in range(metadata.total_chunks))
        if metadata.compressed:
            raw = CompressionUtil.decompress(raw)
        if not IntegrityUtil.verify_hash(raw, metadata.sha256):
            raise FileIntegrityError(
                "SHA-256 verification failed — file is corrupted.",
                expected=metadata.sha256,
                actual=IntegrityUtil.sha256(raw),
            )
        return raw
