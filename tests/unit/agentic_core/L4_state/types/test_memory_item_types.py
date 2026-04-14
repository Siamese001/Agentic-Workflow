"""Foundational behavioral tests for agentic_core/L4_state/types/memory_item_types.py."""

from __future__ import annotations

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
memory_item_types = import_or_skip(
    "agentic_core.L4_state.types.memory_item_types",
    reason="memory_item_types module unavailable for foundational type tests",
)


def test_module_importable() -> None:
    """Module memory_item_types must be importable."""
    assert memory_item_types is not None
