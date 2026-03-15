"""
Seam for canonical truth utilities - approved L0→L5 interface.

This seam provides a controlled interface for L0 utilities to access
L5 canonical truth functions without direct L5 imports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class CanonicalTruthProvider(Protocol):
    """Protocol for canonical truth operations."""

    def get_layer(self, file_path: Path) -> int:
        """Get the canonical layer for a file path."""
        ...

    def categorize_agent(self, class_name: str, base_classes: list[str], docstring: str | None) -> str:
        """Categorize an agent based on its characteristics."""
        ...


def get_canonical_truth_provider() -> CanonicalTruthProvider:
    """Get the canonical truth provider implementation.

    This function uses dynamic import to avoid static L0→L5 dependency
    while providing runtime access to L5 canonical truth logic.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_canonical_truth_provider", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_canonical_truth_provider", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_canonical_truth_provider")
    import importlib

    try:
        module = importlib.import_module("agentic_core.L5_safety.utils.canonical_truth_util")
        return module
    except ImportError as e:
        raise RuntimeError(f"Failed to load canonical truth provider: {e}")


def get_canonical_layer(file_path: Path) -> int:
    """Get the canonical layer for a file path."""
    provider = get_canonical_truth_provider()
    return provider.get_layer(file_path)


def categorize_agent(class_name: str, base_classes: list[str], docstring: str | None) -> str:
    """Categorize an agent based on its characteristics."""
    provider = get_canonical_truth_provider()
    return provider.categorize_agent(class_name, base_classes, docstring)
