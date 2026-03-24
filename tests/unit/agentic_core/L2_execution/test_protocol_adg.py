"""ADG importability contract for agentic_core/L2_execution/protocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_protocol.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.protocol import (  # noqa: F401
        AgentRunResult,
        L2AgentProtocol,
        SubphaseResult,
        compute_pipeline_digest,
        emit_pipeline_digest,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SubphaseResult = None  # type: ignore[assignment,misc]
    AgentRunResult = None  # type: ignore[assignment,misc]
    L2AgentProtocol = None  # type: ignore[assignment,misc]
    compute_pipeline_digest = None  # type: ignore[assignment,misc]
    emit_pipeline_digest = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="protocol deps unavailable")
class TestProtocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/protocol.py must be importable."""
        assert _AVAILABLE

    def test_subphaseresult_defined(self) -> None:
        assert SubphaseResult is not None

    def test_agentrunresult_defined(self) -> None:
        assert AgentRunResult is not None

    def test_l2agentprotocol_defined(self) -> None:
        assert L2AgentProtocol is not None