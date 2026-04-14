"""Foundational behavioral tests for agentic_core/L4_state/memory/semantic_cache_manager.py."""

from __future__ import annotations

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
semantic_cache_manager = import_or_skip(
    "agentic_core.L4_state.utils.memory.semantic_cache_manager",
    reason="semantic_cache_manager module unavailable for foundational cache-manager tests",
)


def test_module_importable() -> None:
    """Module semantic_cache_manager must be importable."""
    assert semantic_cache_manager is not None
