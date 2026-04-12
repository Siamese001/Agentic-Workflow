"""§Wave5.0.6 — Robust filesystem helpers for Windows batch test stability.

Provides:
- ``robust_rmtree``: shutil.rmtree with bounded immediate retry on Windows
  file-lock / stale-handle errors (PermissionError, FileNotFoundError,
  OSError winerror 2|32).
- ``robust_subprocess_run``: subprocess.run with bounded immediate retry
  on transient WinError 2 (FileNotFoundError).
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_MAX_RETRIES: int = 3

# Windows error codes that indicate transient file-lock / stale-handle races
_WIN_TRANSIENT_ERRNOS: frozenset[int] = frozenset({2, 32})


def _force_writable(func, path, exc_info):  # noqa: ANN001
    """on_error handler: chmod +w then retry the failing operation."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def robust_rmtree(path: Path | str, *, retries: int = _MAX_RETRIES) -> None:
    """Remove *path* tree, retrying on transient Windows errors.

    On each failure the handler first clears read-only bits.  If the
    error is a known transient Windows race (winerror 2 or 32), it
    retries immediately up to *retries* times.  No sleep.
    """
    target = Path(path)
    if not target.exists():
        return

    last_exc: Exception | None = None
    for _ in range(retries):
        try:
            shutil.rmtree(target, onerror=_force_writable)
            return
        except (
            PermissionError,
            FileNotFoundError,
            OSError,
        ) as exc:  # guardian: Multiple exceptions (PermissionError, FileNotFoundError) need specific handling
            last_exc = exc
            winerr = getattr(exc, "winerror", None)
            if winerr is not None and winerr in _WIN_TRANSIENT_ERRNOS:
                continue
            if isinstance(exc, (PermissionError, FileNotFoundError)):
                continue
            raise
    if last_exc is not None and Path(path).exists():
        raise last_exc


def robust_subprocess_run(
    cmd: list[str],
    **kwargs: object,
) -> subprocess.CompletedProcess[str]:
    """subprocess.run with bounded immediate retry on WinError 2.

    On Windows, subprocess.run can transiently fail with
    FileNotFoundError (WinError 2) when many processes are spawned
    concurrently during batch test runs.
    """
    last_exc: FileNotFoundError | None = None
    for _ in range(_MAX_RETRIES):
        try:
            return subprocess.run(cmd, **kwargs)  # type: ignore[arg-type]
        except FileNotFoundError as exc:  # guardian: File operations should check existence before access
            last_exc = exc
    raise last_exc  # type: ignore[misc]
