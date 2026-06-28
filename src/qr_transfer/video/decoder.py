import cv2
import numpy as np

from qr_transfer.errors import VideoReadError
from qr_transfer.core.protocols import VideoInfo


class VideoDecoder:
    def extract_frames(self, video_path: str, sample_rate: int = 1) -> list[np.ndarray]:
        """Extract frames from video, returning every sample_rate-th frame."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path!r}")

        frames = []
        frame_idx = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % sample_rate == 0:
                    frames.append(frame)
                frame_idx += 1
        finally:
            cap.release()

        return frames

    def get_video_info(self, video_path: str) -> VideoInfo:
        """Return video metadata without extracting frames."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path!r}")

        try:
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            return VideoInfo(
                path=video_path,
                frame_count=frame_count,
                fps=fps,
                width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                duration=frame_count / fps if fps else 0.0,
            )
        finally:
            cap.release()
