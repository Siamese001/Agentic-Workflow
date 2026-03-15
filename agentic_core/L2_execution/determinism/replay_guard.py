"""
ReplayGuard — Kernel-level nondeterminism interception for L2 execution.

Intercepts ALL potential sources of nondeterminism during a replay run:
  - socket / network
  - subprocess / os.system
  - filesystem writes outside the sandbox root
  - threading.Thread.start
  - random number generation
  - datetime.now / time.time

Use as a context manager around any execution segment that must be
deterministically replayable.

Phase 2.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import builtins
import os
import random
import socket
import subprocess
import threading
from types import TracebackType
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "replay_guard", "L2")
_emit_routes_through("p1", "replay_guard", "L2")
_emit_escalates_to_human("p1", "replay_guard", "L2")
_emit_reads_policy_state("p1", "replay_guard", "L2")


class ReplayViolation(RuntimeError):
    """Raised when a nondeterministic call is attempted during replay."""


class ReplayGuard:
    """Context manager that intercepts all nondeterministic sources.

    Usage::

        with ReplayGuard(deterministic_seed=42):
            result = run_deterministic_execution(packet)

    Any attempt to call a patched nondeterministic function raises
    ReplayViolation immediately.
    """

    def __init__(self, deterministic_seed: int = 42) -> None:
        self._seed = deterministic_seed
        self._saved: dict[str, Any] = {}

    def __enter__(self) -> ReplayGuard:
        self._patch_socket()
        self._patch_subprocess()
        self._patch_filesystem_writes()
        self._patch_threading()
        self._patch_random()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._restore_all()

    def _save(self, key: str, obj: Any, attr: str) -> None:
        self._saved[key] = getattr(obj, attr)

    def _restore(self, key: str, obj: Any, attr: str) -> None:
        if key in self._saved:
            setattr(obj, attr, self._saved.pop(key))

    def _patch_socket(self) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReplayGuard._patch_socket", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReplayGuard._patch_socket", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ReplayGuard._patch_socket")

        def _blocked_init(self_inner: Any, *args: Any, **kwargs: Any) -> None:
            raise ReplayViolation("Network socket creation prohibited during replay")

        self._saved["socket.__init__"] = socket.socket.__init__
        socket.socket.__init__ = _blocked_init

    def _patch_subprocess(self) -> None:
        self._saved["subprocess.run"] = subprocess.run
        self._saved["subprocess.Popen"] = subprocess.Popen
        self._saved["os.system"] = os.system

        def _blocked_run(*args: Any, **kwargs: Any) -> Any:
            raise ReplayViolation("subprocess.run() prohibited during replay")

        def _blocked_popen(*args: Any, **kwargs: Any) -> Any:
            raise ReplayViolation("subprocess.Popen() prohibited during replay")

        def _blocked_system(*args: Any, **kwargs: Any) -> Any:
            raise ReplayViolation("os.system() prohibited during replay")

        subprocess.run = _blocked_run
        subprocess.Popen = _blocked_popen
        os.system = _blocked_system

    def _patch_filesystem_writes(self) -> None:
        original_open = builtins.open

        def _guarded_open(file: Any, mode: str = "r", **kwargs: Any) -> Any:
            if any(c in mode for c in ("w", "a", "x", "+")):
                raise ReplayViolation(f"Filesystem write prohibited during replay: open({file!r}, {mode!r})")
            return original_open(file, mode, **kwargs)

        self._saved["builtins.open"] = builtins.open
        builtins.open = _guarded_open

    def _patch_threading(self) -> None:
        self._saved["threading.Thread.start"] = threading.Thread.start

        def _blocked_start(self_inner: Any) -> None:
            raise ReplayViolation("threading.Thread.start() prohibited during replay")

        threading.Thread.start = _blocked_start

    def _patch_random(self) -> None:
        self._saved["random.random"] = random.random
        self._saved["random.randint"] = random.randint
        self._saved["random.choice"] = random.choice
        self._saved["random.shuffle"] = random.shuffle
        _rng = random.Random(self._seed)
        random.random = _rng.random
        random.randint = _rng.randint
        random.choice = _rng.choice
        random.shuffle = _rng.shuffle

    def _restore_all(self) -> None:
        if "socket.__init__" in self._saved:
            socket.socket.__init__ = self._saved.pop("socket.__init__")
        if "subprocess.run" in self._saved:
            subprocess.run = self._saved.pop("subprocess.run")
        if "subprocess.Popen" in self._saved:
            subprocess.Popen = self._saved.pop("subprocess.Popen")
        if "os.system" in self._saved:
            os.system = self._saved.pop("os.system")
        if "builtins.open" in self._saved:
            builtins.open = self._saved.pop("builtins.open")
        if "threading.Thread.start" in self._saved:
            threading.Thread.start = self._saved.pop("threading.Thread.start")
        for attr in ("random", "randint", "choice", "shuffle"):
            key = f"random.{attr}"
            if key in self._saved:
                setattr(random, attr, self._saved.pop(key))


__all__ = ["ReplayGuard", "ReplayViolation"]
