"""Cross-process synchronization for file-backed L6 index mappings.

The version and runtime-ADG stores persist complete JSON mappings. Every
writer, including offline recovery tools, must hold the same operating-system
lock and reload the mapping before it merges an update. The lock file is
persistent; process exit releases the byte-range lock without stale-file
cleanup or a missing canonical-index window.
"""

from __future__ import annotations

import errno
import json
import math
import os
import tempfile
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path

RUNTIME_ADG_INDEX_LOCK_NAME = "_runtime_adg_indexes.lock"
DEFAULT_INDEX_LOCK_TIMEOUT_SECONDS = 30.0
_LOCK_POLL_SECONDS = 0.05
_RETRYABLE_LOCK_ERRNOS = {errno.EACCES, errno.EAGAIN, errno.EDEADLK}


class RuntimeADGIndexLockTimeout(ValueError):
    """Bounded lock acquisition failed without mutating an index."""


def _try_lock(descriptor: int) -> bool:
    os.lseek(descriptor, 0, os.SEEK_SET)
    if os.name == "nt":
        import msvcrt

        try:
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            if exc.errno in _RETRYABLE_LOCK_ERRNOS:
                return False
            raise
        return True

    import fcntl

    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        if exc.errno in _RETRYABLE_LOCK_ERRNOS:
            return False
        raise
    return True


def _unlock(descriptor: int) -> None:
    os.lseek(descriptor, 0, os.SEEK_SET)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(descriptor, fcntl.LOCK_UN)


@contextmanager
def runtime_adg_index_lock(
    base_dir: Path,
    *,
    timeout_seconds: float = DEFAULT_INDEX_LOCK_TIMEOUT_SECONDS,
) -> Iterator[None]:
    """Acquire the shared, crash-released lock for both runtime ADG indexes."""
    if not math.isfinite(timeout_seconds) or timeout_seconds < 0:
        raise ValueError("index lock timeout must be finite and nonnegative")
    base_dir.mkdir(parents=True, exist_ok=True)
    lock_path = base_dir / RUNTIME_ADG_INDEX_LOCK_NAME
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    locked = False
    try:
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b"\0")
            os.fsync(descriptor)
        deadline = time.monotonic() + timeout_seconds
        while not locked:
            locked = _try_lock(descriptor)
            if locked:
                break
            if time.monotonic() >= deadline:
                raise RuntimeADGIndexLockTimeout(
                    f"timed out acquiring runtime ADG index lock after {timeout_seconds:.3f}s: {lock_path}"
                )
            time.sleep(min(_LOCK_POLL_SECONDS, max(0.0, deadline - time.monotonic())))
        yield
    finally:
        if locked:
            _unlock(descriptor)
        os.close(descriptor)


def atomic_write_json_mapping(path: Path, payload: Mapping[str, str]) -> None:
    """Atomically replace one complete JSON mapping with durable temp bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(dict(payload), handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


__all__ = [
    "DEFAULT_INDEX_LOCK_TIMEOUT_SECONDS",
    "RUNTIME_ADG_INDEX_LOCK_NAME",
    "RuntimeADGIndexLockTimeout",
    "atomic_write_json_mapping",
    "runtime_adg_index_lock",
]
