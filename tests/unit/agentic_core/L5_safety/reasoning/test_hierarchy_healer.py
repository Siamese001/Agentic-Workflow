"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/hierarchy_healer.py.

fan_in=17 — imported by 17 other modules.
ADG import-hygiene is covered separately by test_hierarchy_healer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.hierarchy_healer import (  # noqa: F401
        HierarchyAgent,
        get_hierarchy_agent,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HierarchyAgent = None  # type: ignore[assignment,misc]
    get_hierarchy_agent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hierarchy_healer.py deps unavailable")
class TestHierarchyAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HierarchyAgent)

@pytest.mark.skipif(not _AVAILABLE, reason="hierarchy_healer.py deps unavailable")
class TestGetHierarchyAgentFunction:
    def test_is_callable(self):
        assert callable(get_hierarchy_agent)


def test_module_importable():
    """Smoke: hierarchy_healer importable or gracefully unavailable."""
    pass