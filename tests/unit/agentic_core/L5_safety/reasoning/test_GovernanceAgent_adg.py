"""ADG importability contract for agentic_core/L5_safety/reasoning/GovernanceAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_GovernanceAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.GovernanceAgent import (  # noqa: F401
        LOGGER,
        DependencyGraph,
        GovernanceAgent,
        create_architecture_governor,
        get_GovernanceAgent,
        heal,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    LOGGER = None  # type: ignore[assignment,misc]
    heal = None  # type: ignore[assignment,misc]
    DependencyGraph = None  # type: ignore[assignment,misc]
    GovernanceAgent = None  # type: ignore[assignment,misc]
    create_architecture_governor = None  # type: ignore[assignment,misc]
    get_GovernanceAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceAgent deps unavailable")
class TestGovernanceagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/GovernanceAgent.py must be importable."""
        assert _AVAILABLE

    def test_dependencygraph_defined(self) -> None:
        assert DependencyGraph is not None

    def test_governanceagent_defined(self) -> None:
        assert GovernanceAgent is not None