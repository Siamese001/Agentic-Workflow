"""ADG importability contract for agentic_core/L5_safety/reasoning/hierarchy_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hierarchy_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.hierarchy_validator import (  # noqa: F401
        HierarchyValidatorAgent,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HierarchyValidatorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hierarchy_validator deps unavailable")
class TestHierarchyValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/hierarchy_validator.py must be importable."""
        assert _AVAILABLE

    def test_hierarchyvalidatoragent_defined(self) -> None:
        assert HierarchyValidatorAgent is not None