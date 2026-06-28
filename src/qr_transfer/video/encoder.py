import cv2
import numpy as np

from qr_transfer.constants import DEFAULT_FPS
from qr_transfer.errors import VideoCreationError
from qr_transfer.core.protocols import VideoInfo


class VideoEncoder:
    def __init__(self, fps: int = DEFAULT_FPS):
        self.fps = fps

    def create(self, frames: list, output_path: str, width: int, height: int) -> VideoInfo:
        """Create MP4 video from frames. Tries avc1 (H.264) first, falls back to mp4v."""
        writer = None
        for codec in ("avc1", "mp4v"):
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
            if writer.isOpened():
                break
            writer.release()
            writer = None
        else:
            raise VideoCreationError(f"Failed to open video writer for {output_path!r}")

        frame_count = 0
        try:
            for frame in frames:
                writer.write(self._pil_to_cv(frame))
                frame_count += 1
        except Exception as e:
            raise VideoCreationError(f"Failed to write video frames: {e}") from e
        finally:
            writer.release()

        return VideoInfo(
            path=output_path,
            frame_count=frame_count,
            fps=float(self.fps),
            duration=frame_count / self.fps if frame_count else 0.0,
        )

    def _pil_to_cv(self, img) -> np.ndarray:
        """Convert PIL Image to OpenCV BGR ndarray."""
        return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
