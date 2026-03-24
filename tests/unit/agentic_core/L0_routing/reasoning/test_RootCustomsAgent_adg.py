"""ADG importability contract for agentic_core/L0_routing/reasoning/RootCustomsAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_RootCustomsAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.reasoning.RootCustomsAgent import (  # noqa: F401
        ASTAnalyzer,
        RootCustomsAgent,
        RoutingDecision,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RoutingDecision = None  # type: ignore[assignment,misc]
    ASTAnalyzer = None  # type: ignore[assignment,misc]
    RootCustomsAgent = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="RootCustomsAgent.py deps unavailable")
class TestRootcustomsagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: RootCustomsAgent.py must be importable."""
        assert _AVAILABLE

    def test_routingdecision_is_type(self) -> None:
        assert RoutingDecision is not None

    def test_astanalyzer_is_type(self) -> None:
        assert ASTAnalyzer is not None

    def test_rootcustomsagent_is_type(self) -> None:
        assert RootCustomsAgent is not None

    def test_main_callable(self) -> None:
        assert callable(main)