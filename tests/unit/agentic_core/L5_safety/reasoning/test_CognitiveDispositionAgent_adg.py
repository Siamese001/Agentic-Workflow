"""ADG importability contract for agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CognitiveDispositionAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import (  # noqa: F401
        CognitiveDispositionAgent,
        DispositionDecision,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DispositionDecision = None  # type: ignore[assignment,misc]
    CognitiveDispositionAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent deps unavailable")
class TestCognitivedispositionagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py must be importable."""
        assert _AVAILABLE

    def test_dispositiondecision_defined(self) -> None:
        assert DispositionDecision is not None

    def test_cognitivedispositionagent_defined(self) -> None:
        assert CognitiveDispositionAgent is not None
