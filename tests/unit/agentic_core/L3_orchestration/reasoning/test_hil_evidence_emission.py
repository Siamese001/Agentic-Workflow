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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_hil_evidence_emission")
# REMOVED: _emit_applies_guardrail("p0", "test_hil_evidence_emission", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_hil_evidence_emission", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_hil_evidence_emission", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_hil_evidence_emission", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_hil_evidence_emission", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_hil_evidence_emission", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_hil_evidence_emission", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_hil_evidence_emission", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_hil_evidence_emission", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_hil_evidence_emission", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_hil_evidence_emission", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_hil_evidence_emission", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_hil_evidence_emission", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_hil_evidence_emission", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_hil_evidence_emission", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_hil_evidence_emission", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_hil_evidence_emission", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_hil_evidence_emission", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_hil_evidence_emission", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_hil_evidence_emission", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_hil_evidence_emission", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_hil_evidence_emission", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_hil_evidence_emission", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_hil_evidence_emission", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_hil_evidence_emission", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_hil_evidence_emission", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_hil_evidence_emission", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_hil_evidence_emission", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_hil_evidence_emission", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_hil_evidence_emission", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_hil_evidence_emission", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_hil_evidence_emission", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hil_evidence_emission", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hil_evidence_emission", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_hil_evidence_emission", "write_through")
# REMOVED: _emit_writes_through("p1", "test_hil_evidence_emission", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_hil_evidence_emission", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_hil_evidence_emission", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_hil_evidence_emission", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_hil_evidence_emission", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_hil_evidence_emission", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_hil_evidence_emission", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_hil_evidence_emission", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_hil_evidence_emission", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_hil_evidence_emission", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_hil_evidence_emission", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_hil_evidence_emission", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_hil_evidence_emission", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_hil_evidence_emission", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_hil_evidence_emission", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_hil_evidence_emission")
# REMOVED: _emit_gated_by_confidence("p1", "test_hil_evidence_emission", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_hil_evidence_emission")
# REMOVED: emit_determinism_digest("p0", "test_hil_evidence_emission")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_hil_evidence_emission", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_hil_evidence_emission", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_hil_evidence_emission", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_hil_evidence_emission", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_hil_evidence_emission", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_hil_evidence_emission", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_hil_evidence_emission", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_hil_evidence_emission", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_hil_evidence_emission", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_hil_evidence_emission", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_hil_evidence_emission", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_hil_evidence_emission", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_hil_evidence_emission", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_hil_evidence_emission", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_hil_evidence_emission", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_hil_evidence_emission", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_hil_evidence_emission", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_hil_evidence_emission", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_hil_evidence_emission", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_hil_evidence_emission", "exec_snapshot_link")

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
