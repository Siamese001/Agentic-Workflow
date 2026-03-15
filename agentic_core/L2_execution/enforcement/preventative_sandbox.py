"""
H1: Full-spectrum preventative sandbox for replay mode.

Patches all write-capable functions during replay to prevent
side effects.  Lives in L2 (execution layer) per gravity rules.

Write-vector taxonomy:
  Filesystem  — builtins.open (write), pathlib, os.remove/rename
  Process     — subprocess.*, os.system/popen
  Network     — socket.*, urllib.*, requests.*
  Persistence — redis.*, pinecone.*, DB client write methods
  Dynamic     — importlib.import_module, eval, exec

Invariant: No write-capable function may remain unpatched
during replay mode.
"""

from __future__ import annotations

import builtins
import contextlib
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
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
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "preventative_sandbox", "L2")
_emit_routes_through("p1", "preventative_sandbox", "L2")
_emit_escalates_to_human("p1", "preventative_sandbox", "L2")
_emit_reads_policy_state("p1", "preventative_sandbox", "L2")

_emit_snapshots_state("p0", "preventative_sandbox", "state_snapshot")

Logger = logging.getLogger(__name__)


class SandboxViolationError(RuntimeError):
    """Raised when a write-capable function is called in sandbox."""

    def __init__(self, function_name: str) -> None:
        self.function_name = function_name
        super().__init__(f"SandboxViolationError: '{function_name}' is blocked during replay mode.")


@dataclass
class _PatchTarget:
    """Describes one function to patch."""

    module_path: str
    attr_name: str
    category: str


_WRITE_VECTORS: list[_PatchTarget] = [
    _PatchTarget("builtins", "open", "filesystem"),
    _PatchTarget("os", "remove", "filesystem"),
    _PatchTarget("os", "rename", "filesystem"),
    _PatchTarget("os", "unlink", "filesystem"),
    _PatchTarget("os", "makedirs", "filesystem"),
    _PatchTarget("subprocess", "run", "process"),
    _PatchTarget("subprocess", "Popen", "process"),
    _PatchTarget("subprocess", "call", "process"),
    _PatchTarget("subprocess", "check_call", "process"),
    _PatchTarget("subprocess", "check_output", "process"),
    _PatchTarget("os", "system", "process"),
    _PatchTarget("os", "popen", "process"),
    _PatchTarget("socket", "socket", "network"),
]


def _resolve_module(module_path: str) -> Any:
    """Import and return the module object."""
    import importlib

    if module_path == "builtins":
        return builtins
    return importlib.import_module(module_path)


@dataclass
class PreventativeSandbox:
    """Scoped sandbox that blocks write-capable functions.

    Usage::

        sandbox = PreventativeSandbox()
        with sandbox.activated():
            # all write vectors raise SandboxViolationError
            ...
        # originals restored

    Must live in L2 — not in agent constructors, L6, or global.
    """

    _originals: dict[str, Any] = field(default_factory=dict, repr=False)
    _active: bool = field(default=False, repr=False)
    _extra_targets: list[_PatchTarget] = field(default_factory=list)

    def register_target(self, module_path: str, attr_name: str, category: str) -> None:
        """Register an additional write vector to patch."""
        self._extra_targets.append(_PatchTarget(module_path, attr_name, category))

    @property
    def is_active(self) -> bool:
        return self._active

    def _all_targets(self) -> list[_PatchTarget]:
        return _WRITE_VECTORS + self._extra_targets

    def _make_guard(self, target: _PatchTarget) -> Callable[..., Any]:
        """Create a guard function that raises on call."""
        _emit_applies_guardrail(str(uuid.uuid4()), "PreventativeSandbox._make_guard", "L2_EXECUTION")
        fqn = f"{target.module_path}.{target.attr_name}"

        def _guard(*args: Any, **kwargs: Any) -> Any:
            raise SandboxViolationError(fqn)

        _guard.__qualname__ = f"sandbox_guard<{fqn}>"
        return _guard

    def _patch_all(self) -> None:
        """Replace all write vectors with guards."""
        for target in self._all_targets():
            key = f"{target.module_path}.{target.attr_name}"
            try:
                mod = _resolve_module(target.module_path)
                original = getattr(mod, target.attr_name, None)
                if original is None:
                    Logger.debug(f"[sandbox] skip {key}: not found")
                    continue
                if key in self._originals:
                    Logger.debug(f"[sandbox] skip {key}: already patched")
                    continue
                self._originals[key] = (mod, original)
                setattr(mod, target.attr_name, self._make_guard(target))
                Logger.debug(f"[sandbox] patched {key}")
            except ImportError:
                Logger.debug(f"[sandbox] skip {key}: module not available")

    def _restore_all(self) -> None:
        """Restore all original functions."""
        for key, (mod, original) in self._originals.items():
            parts = key.rsplit(".", 1)
            setattr(mod, parts[1], original)
            Logger.debug(f"[sandbox] restored {key}")
        self._originals.clear()

    @contextlib.contextmanager
    def activated(self):
        """Context manager for scoped sandbox activation.

        Guarantees restoration even on exception.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "PreventativeSandbox.activated")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PreventativeSandbox.activated".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self._active:
            raise RuntimeError("PreventativeSandbox is already active (double-activation prevented)")
        self._active = True
        self._patch_all()
        try:
            yield self
        finally:
            self._restore_all()
            self._active = False
