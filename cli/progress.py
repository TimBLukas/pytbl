"""Simple terminal progress indicators for CLI tools."""

from __future__ import annotations

import sys
from typing import Iterable, Iterator, Optional, TextIO


class ProgressBar:
    """Display incremental progress to the terminal."""

    def __init__(
        self,
        *,
        total: Optional[int] = None,
        width: int = 30,
        prefix: str = "",
        stream: Optional[TextIO] = None,
        enabled: bool = True,
    ) -> None:
        self.total = total
        self.width = max(1, width)
        self.prefix = prefix
        self.stream = stream if stream is not None else sys.stdout
        self.enabled = enabled
        self.current = 0
        self.last_message = ""

    def reset(self, *, total: Optional[int] = None) -> None:
        if total is not None:
            self.total = total
        self.current = 0
        self.last_message = ""

    def update(self, current: Optional[int] = None, *, message: Optional[str] = None) -> None:
        if current is not None:
            self.current = current
        if message is not None:
            self.last_message = message
        if not self.enabled:
            return
        if self.total is None:
            value = f"{self.current}"
            rendered = f"{self.prefix}{value}"
            if self.last_message:
                rendered = f"{rendered} {self.last_message}"
            self.stream.write(f"\r{rendered}")
            self.stream.flush()
            return

        done = min(self.current, self.total)
        ratio = 0.0 if self.total == 0 else done / self.total
        filled = int(ratio * self.width)
        bar = "#" * filled + "-" * (self.width - filled)
        percent = int(ratio * 100)
        rendered = f"{self.prefix}[{bar}] {percent}% ({done}/{self.total})"
        if self.last_message:
            rendered = f"{rendered} {self.last_message}"
        self.stream.write(f"\r{rendered}")
        self.stream.flush()

    def finish(self, *, message: Optional[str] = None) -> None:
        if not self.enabled:
            return
        final_message = self.last_message if message is None else message
        if self.total is None:
            suffix = f" {final_message}" if final_message else ""
            self.stream.write(f"\r{self.prefix}{self.current}{suffix}\n")
        else:
            suffix = f" {final_message}" if final_message else ""
            self.stream.write(f"\r{self.prefix}[{'#' * self.width}] 100% ({self.total}/{self.total}){suffix}\n")
        self.stream.flush()

    def __enter__(self) -> "ProgressBar":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.finish()


def progress_iterable(
    iterable: Iterable[object],
    *,
    total: Optional[int] = None,
    prefix: str = "",
    stream=None,
    enabled: bool = True,
) -> Iterator[object]:
    """Yield items while updating a progress bar for each iteration."""

    progress = ProgressBar(total=total, prefix=prefix, stream=stream, enabled=enabled)
    iterator = iter(iterable)
    count = 0
    for item in iterator:
        count += 1
        progress.update(count)
        yield item
    progress.finish()
