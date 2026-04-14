"""Foundational behavioral tests for agentic_core/L4_state/config/versioned_configs.py."""

from __future__ import annotations

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
versioned_configs = import_or_skip(
    "agentic_core.L4_state.config.versioned_configs",
    reason="versioned_configs module unavailable for foundational config tests",
)


def test_module_importable() -> None:
    """Module versioned_configs must be importable."""
    assert versioned_configs is not None
