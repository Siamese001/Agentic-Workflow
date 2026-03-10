"""REQ-414: SovereignLLMGateway egress audit enforcement.

Every route_generation call MUST append to the HashChainAuditLog.
Enforcement layers: Runtime + CI (REQ-416 dual-layer contract).
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.governance


def test_gateway_has_egress_audit_log():
    """Gateway must expose a HashChainAuditLog as _egress_audit_log."""
    from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()
    assert hasattr(gw, "_egress_audit_log"), "Gateway missing _egress_audit_log"
    assert isinstance(gw._egress_audit_log, HashChainAuditLog), (
        "Gateway._egress_audit_log must be a HashChainAuditLog instance"
    )
    SovereignLLMGateway.reset_instance()


def test_route_generation_writes_egress_audit():
    """route_generation must append to the egress audit log on each call."""
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()

    req = GenerationRequest(
        agent_id="test_egress_agent",
        provider="openai",
        model="gpt-4o",
        prompt="test egress audit",
    )

    mock_profile = MagicMock()
    mock_profile.execution_mode.value = "LLM_API"
    mock_profile.allowed_models = {"gpt-4o"}
    mock_profile.allowed_providers = {"openai"}
    mock_profile.reasoning_intensity.value = "HIGH"

    sentinel = object()
    mock_em = MagicMock()
    mock_em.DETERMINISTIC = sentinel  # distinct from mock_profile.execution_mode

    with (
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.get_profile",
            return_value=mock_profile,
        ),
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.ExecutionMode",
            mock_em,
        ),
        patch.object(
            gw,
            "_call_provider",
            return_value={"content": "ok", "tokens": 1},
        ),
        patch.object(gw._egress_audit_log, "append") as mock_append,
    ):
        asyncio.run(gw.route_generation(req))
        assert mock_append.called, "Egress audit log.append must be called by route_generation"

    SovereignLLMGateway.reset_instance()


def test_route_generation_egress_payload_contains_agent_id():
    """Egress audit payload must include agent_id and provider."""
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
    )
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest

    SovereignLLMGateway.reset_instance()
    gw = SovereignLLMGateway()

    req = GenerationRequest(
        agent_id="test_payload_agent",
        provider="openai",
        model="gpt-4o",
        prompt="payload check",
    )

    mock_profile = MagicMock()
    mock_profile.execution_mode.value = "LLM_API"
    mock_profile.allowed_models = {"gpt-4o"}
    mock_profile.allowed_providers = {"openai"}
    mock_profile.reasoning_intensity.value = "HIGH"

    sentinel = object()
    mock_em = MagicMock()
    mock_em.DETERMINISTIC = sentinel

    captured: list[dict] = []

    def _capture(**kwargs):
        captured.append(kwargs)

    with (
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.get_profile",
            return_value=mock_profile,
        ),
        patch(
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway.ExecutionMode",
            mock_em,
        ),
        patch.object(
            gw,
            "_call_provider",
            return_value={"content": "ok", "tokens": 1},
        ),
        patch.object(gw._egress_audit_log, "append", side_effect=_capture),
    ):
        asyncio.run(gw.route_generation(req))

    assert len(captured) >= 1, "Egress audit log must be written at least once"
    payload = captured[0].get("payload", {})
    assert payload.get("agent_id") == "test_payload_agent", "Egress audit payload must contain agent_id"
    assert "provider" in payload, "Egress audit payload must contain provider"

    SovereignLLMGateway.reset_instance()
