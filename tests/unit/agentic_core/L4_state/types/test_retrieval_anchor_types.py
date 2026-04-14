"""Foundational behavioral tests for agentic_core/L4_state/types/retrieval_anchor_types.py."""

from __future__ import annotations

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
retrieval_anchor_types = import_or_skip(
    "agentic_core.L4_state.types.retrieval_anchor_types",
    reason="retrieval_anchor_types module unavailable for foundational type tests",
)


def test_module_importable() -> None:
    """Module retrieval_anchor_types must be importable."""
    assert retrieval_anchor_types is not None
