"""Progress tracking utility wrapping tqdm. CR-002: quiet=True disables output."""

from tqdm import tqdm


class ProgressTracker:
    """Tracks operation progress with tqdm. Context manager."""

    def __init__(self, total: int, description: str = "", quiet: bool = False) -> None:
        self.quiet = quiet
        self._pbar = (
            None
            if quiet
            else tqdm(
                total=total,
                desc=description,
                unit="chunks",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            )
        )

    def update(self, n: int = 1) -> None:
        """Advance progress by n steps."""
        if self._pbar is not None:
            self._pbar.update(n)

    def close(self) -> None:
        """Close the progress bar."""
        if self._pbar is not None:
            self._pbar.close()

    def __enter__(self) -> "ProgressTracker":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
