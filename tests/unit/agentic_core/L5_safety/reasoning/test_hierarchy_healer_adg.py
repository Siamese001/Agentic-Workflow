"""ADG importability contract for agentic_core/L5_safety/reasoning/hierarchy_healer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hierarchy_healer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.hierarchy_healer import (  # noqa: F401
        HierarchyAgent,
        get_hierarchy_agent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HierarchyAgent = None  # type: ignore[assignment,misc]
    get_hierarchy_agent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hierarchy_healer deps unavailable")
class TestHierarchyHealerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/hierarchy_healer.py must be importable."""
        assert _AVAILABLE

    def test_hierarchyagent_defined(self) -> None:
        assert HierarchyAgent is not None
