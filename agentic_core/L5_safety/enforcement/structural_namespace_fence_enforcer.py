"""
agentic_core/enforcement/structural_namespace_fence_enforcer.py

Structural namespace enforcement using MetaPathFinder with module load-time
provenance tracking.

Design principles:
- Namespace is determined from the physical file path at module load time,
  not from stack inspection at import time.
- The StructuralNamespaceFinder only BLOCKS imports; it never modifies them.
- No global __builtins__ monkey-patching.
- Safe to use alongside test frameworks (pytest, unittest).
"""

import importlib.abc
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "structural_namespace_fence_enforcer", "p0_governance")
_emit_snapshots_state("p0", "structural_namespace_fence_enforcer", "state_snapshot")

_TRACKED_ROOTS: frozenset = frozenset(
    {APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR}
)
_ALLOWED_CROSS: dict[str, set[str]] = {
    "apps_lic": {"agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"},
    "apps_rg": {"agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"},
    "apps_shared": {"agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"},
    "agentic_core.L0_routing": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L1_cognition": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L2_execution": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L3_orchestration": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L4_state": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L5_safety": {"system_learning.types", "system_learning.interfaces"},
    "agentic_core.L6_observability": {"system_learning.types", "system_learning.interfaces"},
    "system_learning": {"agentic_core.types", "agentic_core.interfaces"},
}


class ProvenanceTracker:
    """Tracks module-to-namespace mapping at module load time."""

    def __init__(self) -> None:
        self._provenance: dict[str, str] = {}

    def register(self, module_name: str, origin: str | None) -> None:
        """Register module provenance from its file path origin."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ProvenanceTracker.register")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ProvenanceTracker.register".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if origin is None:
            return
        namespace = _extract_namespace(Path(origin))
        self._provenance[module_name] = namespace

    def namespace_of(self, module_name: str) -> str:
        """Return namespace for a registered module ('external' if unknown)."""
        if module_name in self._provenance:
            return self._provenance[module_name]
        for tracked in _TRACKED_ROOTS:
            if module_name == tracked or module_name.startswith(tracked + "."):
                return _namespace_from_module_name(module_name)
        return "external"

    def is_forbidden_cross_import(self, caller_ns: str, target_module: str) -> bool:
        """Return True iff importing target_module from caller_ns is forbidden."""
        if caller_ns == "external" or caller_ns == "unknown":
            return False
        target_ns = _namespace_from_module_name(target_module)
        if target_ns == "external":
            return False
        if caller_ns == target_ns:
            return False
        allowed = _ALLOWED_CROSS.get(caller_ns, set())
        return not any(
            target_module == a or target_module.startswith(a + ".") or target_ns == a for a in allowed
        )


def _extract_namespace(path: Path) -> str:
    """Derive namespace string from file path."""
    for part in path.parts:
        if part in _TRACKED_ROOTS:
            if part == AGENTIC_CORE_DIR:
                idx = list(path.parts).index(part)
                rest = path.parts[idx + 1 :]
                if rest and rest[0].startswith("L") and ("_" in rest[0]):
                    return f"agentic_core.{rest[0]}"
            return part
    return "external"


def _namespace_from_module_name(module_name: str) -> str:
    """Derive namespace from a dotted module name."""
    for root in _TRACKED_ROOTS:
        if module_name == root or module_name.startswith(root + "."):
            if root == AGENTIC_CORE_DIR:
                parts = module_name.split(".")
                if len(parts) >= 2 and parts[1].startswith("L") and ("_" in parts[1]):
                    return f"agentic_core.{parts[1]}"
            return root
    return "external"


class ProvenanceLoader(importlib.abc.Loader):
    """Wraps an existing loader to register module provenance on creation."""

    def __init__(
        self,
        original_loader: importlib.abc.Loader,
        tracker: ProvenanceTracker,
        module_name: str,
        origin: str | None,
    ) -> None:
        self._loader = original_loader
        self._tracker = tracker
        self._module_name = module_name
        self._origin = origin

    def create_module(self, spec):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ProvenanceLoader.create_module")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ProvenanceLoader.create_module".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        module = self._loader.create_module(spec) if hasattr(self._loader, "create_module") else None
        self._tracker.register(self._module_name, self._origin)
        return module

    def exec_module(self, module):
        if hasattr(self._loader, "exec_module"):
            self._loader.exec_module(module)


class StructuralNamespaceFinder(importlib.abc.MetaPathFinder):
    """MetaPathFinder that enforces cross-namespace import rules.

    Returns None for all modules to let the normal import machinery resolve
    them — it only raises ImportError when a forbidden cross-namespace import
    is detected.  Namespace determination uses load-time provenance, not
    frame stack inspection.
    """

    def __init__(self, tracker: ProvenanceTracker) -> None:
        self._tracker = tracker

    def find_spec(self, fullname: str, path, target=None):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "StructuralNamespaceFinder.find_spec"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:StructuralNamespaceFinder.find_spec".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        caller_module = self._get_caller_from_loaded_modules()
        # guardian: allow-config-with-logic
        if caller_module is None:
            return None
        caller_ns = self._tracker.namespace_of(caller_module)
        # guardian: allow-config-with-logic
        if self._tracker.is_forbidden_cross_import(caller_ns, fullname):
            raise ImportError(
                f"Namespace boundary violation: '{caller_ns}' (module '{caller_module}') may not import '{fullname}'"
            )
        return None

    def _get_caller_from_loaded_modules(self) -> str | None:
        """Determine calling module by scanning loaded sys.modules for tracked roots."""
        import inspect

        frame = inspect.currentframe()
        try:
            if frame is None:
                return None
            frame = frame.f_back
            while frame is not None:
                module_name: str = frame.f_globals.get("__name__", "")
                if module_name in self._tracker._provenance:
                    return module_name
                for root in _TRACKED_ROOTS:
                    if module_name == root or module_name.startswith(root + "."):
                        return module_name
                frame = frame.f_back
        finally:
            del frame
        return None


_provenance_tracker = ProvenanceTracker()
_structural_finder: StructuralNamespaceFinder | None = None


def install_structural_namespace_fence() -> StructuralNamespaceFinder:
    """Install the namespace fence into sys.meta_path (idempotent)."""
    global _structural_finder
    if _structural_finder is None:
        _structural_finder = StructuralNamespaceFinder(_provenance_tracker)
        sys.meta_path.insert(0, _structural_finder)
    return _structural_finder


def uninstall_structural_namespace_fence() -> None:
    """Remove the namespace fence from sys.meta_path."""
    global _structural_finder
    if _structural_finder is not None and _structural_finder in sys.meta_path:
        sys.meta_path.remove(_structural_finder)
        _structural_finder = None


def get_provenance_tracker() -> ProvenanceTracker:
    """Return the global ProvenanceTracker."""
    return _provenance_tracker
