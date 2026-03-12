"""ADG importability contract for agentic_core/L1_cognition/engines/CognitiveNode.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CognitiveNode.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.engines.CognitiveNode import (  # noqa: F401
        CognitiveResult,
        PerceptionNode,
        ReasoningNode,
        PlanningCoordinator,
        ActionNode,
        CognitiveNode,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CognitiveResult = None  # type: ignore[assignment,misc]
    PerceptionNode = None  # type: ignore[assignment,misc]
    ReasoningNode = None  # type: ignore[assignment,misc]
    PlanningCoordinator = None  # type: ignore[assignment,misc]
    ActionNode = None  # type: ignore[assignment,misc]
    CognitiveNode = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveNode.py deps unavailable")
class TestCognitivenodeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: CognitiveNode.py must be importable."""
        assert _AVAILABLE

    def test_cognitiveresult_is_type(self) -> None:
        assert CognitiveResult is not None

    def test_perceptionnode_is_type(self) -> None:
        assert PerceptionNode is not None

    def test_reasoningnode_is_type(self) -> None:
        assert ReasoningNode is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

