"""Cross-process negative controls for file-backed L6 index synchronization."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
from pathlib import Path

import pytest

from agentic_core.L6_system_learning.stores.index_file_lock import (
    RuntimeADGIndexLockTimeout,
    runtime_adg_index_lock,
)


class _Payload:
    def __init__(self, raw: bytes) -> None:
        self._raw = raw

    def canonical_bytes(self) -> bytes:
        return self._raw


def _hold_lock(base_dir: str, ready, release) -> None:  # noqa: ANN001
    with runtime_adg_index_lock(Path(base_dir), timeout_seconds=5.0):
        ready.set()
        if not release.wait(10.0):
            raise TimeoutError("parent did not release lock holder")


def _crash_while_holding_lock(base_dir: str, ready) -> None:  # noqa: ANN001
    with runtime_adg_index_lock(Path(base_dir), timeout_seconds=5.0):
        ready.set()
        os._exit(23)


def _commit_from_preinitialized_writer(
    base_dir: str,
    payload: bytes,
    ready,
    start,
) -> None:  # noqa: ANN001
    from agentic_core.L6_system_learning.stores import version_store

    class _NullBridge:
        def persist_active_version(self, *_args, **_kwargs) -> None:
            return None

    version_store.get_sl_memory_bridge = lambda: _NullBridge()
    store = version_store.FileBackedVersionStore(Path(base_dir))
    ready.set()
    if not start.wait(10.0):
        raise TimeoutError("parent did not release competing writers")
    store.commit_change_package(_Payload(payload))


def _spawn_context():
    return multiprocessing.get_context("spawn")


def test_cross_process_holder_forces_bounded_timeout(tmp_path: Path) -> None:
    context = _spawn_context()
    ready = context.Event()
    release = context.Event()
    process = context.Process(target=_hold_lock, args=(str(tmp_path), ready, release))
    process.start()
    try:
        assert ready.wait(10.0)
        with pytest.raises(RuntimeADGIndexLockTimeout, match="timed out acquiring runtime ADG index lock"):
            with runtime_adg_index_lock(tmp_path, timeout_seconds=0.05):
                pass
    finally:
        release.set()
        process.join(10.0)
        if process.is_alive():
            process.terminate()
            process.join(5.0)
    assert process.exitcode == 0


@pytest.mark.parametrize("timeout_seconds", [float("inf"), float("nan"), -0.01])
def test_nonfinite_or_negative_timeout_is_rejected(
    tmp_path: Path,
    timeout_seconds: float,
) -> None:
    with pytest.raises(ValueError, match="finite and nonnegative"):
        with runtime_adg_index_lock(tmp_path, timeout_seconds=timeout_seconds):
            pass


def test_process_exit_releases_lock_without_stale_file_cleanup(tmp_path: Path) -> None:
    context = _spawn_context()
    ready = context.Event()
    process = context.Process(target=_crash_while_holding_lock, args=(str(tmp_path), ready))
    process.start()
    assert ready.wait(10.0)
    process.join(10.0)
    if process.is_alive():
        process.terminate()
        process.join(5.0)
        pytest.fail("crash worker did not exit")
    assert process.exitcode == 23

    with runtime_adg_index_lock(tmp_path, timeout_seconds=0.5):
        pass
    assert (tmp_path / "_runtime_adg_indexes.lock").exists()


def test_competing_preinitialized_version_writers_preserve_both_entries(tmp_path: Path) -> None:
    context = _spawn_context()
    start = context.Event()
    ready_a = context.Event()
    ready_b = context.Event()
    payload_a = b"concurrent-version-a"
    payload_b = b"concurrent-version-b"
    process_a = context.Process(
        target=_commit_from_preinitialized_writer,
        args=(str(tmp_path), payload_a, ready_a, start),
    )
    process_b = context.Process(
        target=_commit_from_preinitialized_writer,
        args=(str(tmp_path), payload_b, ready_b, start),
    )
    process_a.start()
    process_b.start()
    try:
        assert ready_a.wait(10.0)
        assert ready_b.wait(10.0)
        start.set()
        process_a.join(15.0)
        process_b.join(15.0)
    finally:
        start.set()
        for process in (process_a, process_b):
            if process.is_alive():
                process.terminate()
                process.join(5.0)
    assert process_a.exitcode == 0
    assert process_b.exitcode == 0

    observed = json.loads((tmp_path / "_index.json").read_text(encoding="utf-8"))
    expected = {
        f"v_{hashlib.sha256(payload).hexdigest()[:16]}": hashlib.sha256(payload).hexdigest()
        for payload in (payload_a, payload_b)
    }
    assert observed.items() >= expected.items()
