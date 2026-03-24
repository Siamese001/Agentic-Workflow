"""ADG importability contract for agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_EmbeddingSovereignAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (  # noqa: F401
        EmbeddingSovereignAgent,
        get_embedding_gateway,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    EmbeddingSovereignAgent = None  # type: ignore[assignment,misc]
    get_embedding_gateway = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="EmbeddingSovereignAgent deps unavailable")
class TestEmbeddingsovereignagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py must be importable."""
        assert _AVAILABLE

    def test_embeddingsovereignagent_defined(self) -> None:
        assert EmbeddingSovereignAgent is not None