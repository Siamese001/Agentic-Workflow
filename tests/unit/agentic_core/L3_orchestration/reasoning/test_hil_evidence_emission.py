"""Wave 2.2 — HIL EvidencePack emission tests.

Tests prove:
1) Positive: HUMAN_ESCALATION path emits EvidencePack with required fields.
2) Negative: non-escalation path (STANDARD_VALIDATION, no routing) does NOT emit.

These tests WILL FAIL if emission code is removed from delegate_task().
"""

from __future__ import annotations

import sys
import types
from dataclasses import asdict
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.governance_contracts import (
    build_hil_evidence_pack,
)
from agentic_core.L0_routing.types.governance_types import (
    EvidencePack,
    PolicySnapshot,
    RouteDecisionRef,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hil_evidence_emission")
_emit_applies_guardrail("p0", "test_hil_evidence_emission", "p0_governance")
_emit_snapshots_state("p0", "test_hil_evidence_emission", "state_snapshot")
emit_replay_key("p0", "test_hil_evidence_emission")
emit_determinism_digest("p0", "test_hil_evidence_emission")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =========================================================================
# Unit tests — EvidencePack construction with Wave 2.2 fields
# =========================================================================


class TestEvidencePackConstruction:
    """Unit: build_hil_evidence_pack produces valid, typed EvidencePack."""

    def test_hil_pack_has_required_fields(self):
        ref = RouteDecisionRef(
            trace_id="t1",
            decision="human_escalation",
            agent_name="A",
            reason="policy",
        )
        snap = PolicySnapshot(
            security_level="enforced",
            risk_tier="HIGH",
            laws_applied=(),
            policy_hash="abc",
        )
        pack = build_hil_evidence_pack(
            trace_id="t1",
            escalation_reason="policy requires human review",
            route_decision_ref=ref,
            policy_snapshot_data=snap,
        )
        assert isinstance(pack, EvidencePack)
        assert pack.trace_id == "t1"
        assert pack.evidence_id  # non-empty uuid4
        assert pack.timestamp_utc  # non-empty ISO8601
        assert pack.escalation_reason == "policy requires human review"
        assert pack.route_decision_ref is ref
        assert pack.policy_snapshot_data is snap
        assert pack.risk_score == 0.8

    def test_hil_pack_is_frozen(self):
        ref = RouteDecisionRef(trace_id="t2", decision="d", agent_name="A", reason="r")
        snap = PolicySnapshot(
            security_level="s",
            risk_tier="t",
            laws_applied=(),
            policy_hash="h",
        )
        pack = build_hil_evidence_pack(
            trace_id="t2",
            escalation_reason="r",
            route_decision_ref=ref,
            policy_snapshot_data=snap,
        )
        with pytest.raises(AttributeError):
            pack.escalation_reason = "changed"  # type: ignore[misc]

    def test_hil_pack_serializable(self):
        ref = RouteDecisionRef(trace_id="t3", decision="d", agent_name="A", reason="r")
        snap = PolicySnapshot(
            security_level="s",
            risk_tier="HIGH",
            laws_applied=("GDPR",),
            policy_hash="h",
        )
        pack = build_hil_evidence_pack(
            trace_id="t3",
            escalation_reason="test",
            route_decision_ref=ref,
            policy_snapshot_data=snap,
        )
        d = asdict(pack)
        assert d["trace_id"] == "t3"
        assert d["escalation_reason"] == "test"
        assert d["route_decision_ref"]["decision"] == "d"
        assert d["policy_snapshot_data"]["risk_tier"] == "HIGH"

    def test_backward_compat_old_style_still_works(self):
        pack = EvidencePack(
            trace_id="old",
            action_trace=("a",),
            policy_evals=("p",),
            risk_score=0.5,
            budget_breach_data={},
            boundary_snapshot_hash="hash",
        )
        assert pack.trace_id == "old"
        assert pack.evidence_id == ""
        assert pack.route_decision_ref is None
        assert pack.policy_snapshot_data is None


# =========================================================================
# Integration tests — delegate_task HIL escalation path
#
# Stub missing leaf modules before importing OrchestrationHandshakeAgent.
# =========================================================================

_STUBS_INSTALLED = False


def _install_module_stubs():
    """Idempotent: stub missing/broken leaf modules so Python never loads their source."""
    global _STUBS_INSTALLED
    if _STUBS_INSTALLED:
        return
    _STUBS_INSTALLED = True

    _stub_cls = type("Stub", (), {"__init__": lambda self, *a, **k: None})

    def _make_stub(name, attrs):
        if name not in sys.modules:
            mod = types.ModuleType(name)
            for k, v in attrs.items():
                setattr(mod, k, v)
            sys.modules[name] = mod

    _make_stub(
        "agentic_core.L3_orchestration.unified",
        {
            "CoreOrchestrationAgent": _stub_cls,
        },
    )
    _make_stub(
        "agentic_core.L3_orchestration.unified.CoreOrchestrationAgent",
        {
            "CoreOrchestrationAgent": _stub_cls,
        },
    )
    from datetime import datetime, timezone

    class _RoutingRequestStub:
        def __init__(self, *a, **k):
            self.timestamp = datetime.now(timezone.utc)
            for key, val in k.items():
                setattr(self, key, val)

    _make_stub(
        "agentic_core.runtime.config.contextual_router_config",
        {
            "RoutingRequest": _RoutingRequestStub,
            "get_router": MagicMock(return_value=MagicMock()),
        },
    )


def _import_oha_module():
    """Import OrchestrationHandshakeAgent module with stubs in place."""
    _install_module_stubs()
    import agentic_core.L3_orchestration.reasoning.OrchestrationHandshakeAgent as mod

    return mod


def _make_handshake_agent():
    """Build a minimally-mocked OrchestrationHandshakeAgent for routing tests."""
    oha_mod = _import_oha_module()
    cls = oha_mod.OrchestrationHandshakeAgent
    agent = object.__new__(cls)
    agent.__dict__["requesting_agent"] = "test_caller"
    agent.__dict__["redis"] = None
    registry = MagicMock()
    registry.invoke_method = MagicMock(return_value={"ok": True})
    agent.__dict__["registry"] = registry
    return agent, oha_mod


def _mock_routing_result(oha_mod, decision_value, reason="policy requires human review"):
    """Create a mock RoutingResult with the given RoutePath decision."""
    RoutePath = oha_mod.RoutePath
    mock_result = MagicMock()
    mock_result.decision = RoutePath(decision_value)
    mock_result.reason = reason
    mock_result.risk_level = "HIGH"
    return mock_result


class TestHILEscalationEmission:
    """Integration: HUMAN_ESCALATION path emits EvidencePack."""

    def test_positive_evidence_pack_emitted_on_escalation(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.cache_routing_decision = MagicMock()
        agent.discover_capable_agents = MagicMock(
            return_value=[
                {
                    "agent_class": "TestAgent",
                    "method": "run",
                    "confidence": 0.95,
                    "docstring": "test agent",
                },
            ],
        )

        mock_result = _mock_routing_result(oha_mod, "human_escalation")
        mock_router = MagicMock()
        mock_router.route = MagicMock(return_value=mock_result)

        with (
            patch.object(oha_mod, "is_v15_enforced", return_value=True),
            patch.object(oha_mod, "get_router", return_value=mock_router),
        ):
            result = agent.delegate_task("escalation test task")

        assert result["status"] == "route_blocked"
        assert result["route_path"] == "human_escalation"
        assert "hil_evidence_pack" in result
        pack = result["hil_evidence_pack"]
        assert pack is not None
        assert pack["trace_id"]  # non-empty
        assert pack["escalation_reason"]  # non-empty
        assert pack["evidence_id"]  # uuid4
        assert pack["timestamp_utc"]  # ISO8601
        assert pack["route_decision_ref"] is not None
        assert pack["route_decision_ref"]["decision"] == "human_escalation"
        assert pack["policy_snapshot_data"] is not None
        assert pack["policy_snapshot_data"]["security_level"] == "enforced"

    def test_positive_evidence_pack_contains_action_trace(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.cache_routing_decision = MagicMock()
        agent.discover_capable_agents = MagicMock(
            return_value=[
                {
                    "agent_class": "EscAgent",
                    "method": "analyze",
                    "confidence": 0.92,
                    "docstring": "esc",
                },
            ],
        )

        mock_result = _mock_routing_result(oha_mod, "human_escalation", "critical signal")
        mock_router = MagicMock()
        mock_router.route = MagicMock(return_value=mock_result)

        with (
            patch.object(oha_mod, "is_v15_enforced", return_value=True),
            patch.object(oha_mod, "get_router", return_value=mock_router),
        ):
            result = agent.delegate_task("critical operation")

        pack = result["hil_evidence_pack"]
        assert pack["escalation_reason"] == "critical signal"
        assert len(pack["action_trace"]) >= 1


class TestHILEscalationBypass:
    """Negative: non-escalation paths do NOT emit EvidencePack."""

    def test_no_evidence_pack_on_standard_validation(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.cache_routing_decision = MagicMock()
        agent.discover_capable_agents = MagicMock(
            return_value=[
                {
                    "agent_class": "NormalAgent",
                    "method": "run",
                    "confidence": 0.95,
                    "docstring": "normal",
                },
            ],
        )

        mock_result = _mock_routing_result(
            oha_mod,
            "standard_validation",
            "standard path",
        )
        mock_router = MagicMock()
        mock_router.route = MagicMock(return_value=mock_result)

        with (
            patch.object(oha_mod, "is_v15_enforced", return_value=True),
            patch.object(oha_mod, "get_router", return_value=mock_router),
        ):
            result = agent.delegate_task("normal task")

        assert result["status"] == "success"
        assert "hil_evidence_pack" not in result

    def test_no_evidence_pack_when_v15_not_enforced(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.cache_routing_decision = MagicMock()
        agent.discover_capable_agents = MagicMock(
            return_value=[
                {
                    "agent_class": "SimpleAgent",
                    "method": "run",
                    "confidence": 0.90,
                    "docstring": "simple",
                },
            ],
        )

        with patch.object(oha_mod, "is_v15_enforced", return_value=False):
            result = agent.delegate_task("non-v15 task")

        assert result["status"] == "success"
        assert "hil_evidence_pack" not in result

    def test_no_evidence_pack_on_no_candidates(self):
        agent, oha_mod = _make_handshake_agent()
        agent.get_cached_routing = MagicMock(return_value=None)
        agent.discover_capable_agents = MagicMock(return_value=[])

        with patch.object(oha_mod, "is_v15_enforced", return_value=False):
            result = agent.delegate_task("no agents task")

        assert result["status"] == "no_capable_agent"
        assert "hil_evidence_pack" not in result
