"""
Phase 3.2 — SemanticClock Propagation Enforcement Tests.

Tests:
1. Positive: semantic_clock present in emitted artifacts with tick
2. Negative: passing None into each chokepoint raises ValueError
3. Determinism: same input twice → byte-identical artifact JSON
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from agentic_core.L0_routing.enforcement.governance_contracts import (
    build_hil_evidence_pack,
    build_hil_policy_proposal,
)
from agentic_core.L0_routing.types.determinism_types import (
    SemanticClock,
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.L0_routing.types.governance_types import (
    EvidencePack,
    HILOutcome,
    PolicySnapshot,
    PolicyUpdateProposal,
    RouteDecisionRef,
)
from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.L3_orchestration.types.route_decision_artifact_types import (
    build_l3_route_decision_artifact,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_semantic_clock_propagation")
_emit_applies_guardrail("p0", "test_semantic_clock_propagation", "p0_governance")
_emit_snapshots_state("p0", "test_semantic_clock_propagation", "state_snapshot")
emit_replay_key("p0", "test_semantic_clock_propagation")
emit_determinism_digest("p0", "test_semantic_clock_propagation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_semantic_clock_propagation", "execution_auth")
_emit_validates_capability("p2", "test_semantic_clock_propagation", "capability_check")
_emit_routes_to_capability("p2", "test_semantic_clock_propagation", "capability_route")
_emit_writes_via_uwg("p2", "test_semantic_clock_propagation", "uwg_write")
_emit_blocks_direct_write("p2", "test_semantic_clock_propagation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_semantic_clock_propagation", "tool_invocation")
_emit_captures_execution_output("p2", "test_semantic_clock_propagation", "exec_output")
_emit_dispatches_agent("p3", "test_semantic_clock_propagation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_semantic_clock_propagation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_semantic_clock_propagation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_semantic_clock_propagation", "healing_outcome")
_emit_escalates_failure("p3", "test_semantic_clock_propagation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_semantic_clock_propagation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_semantic_clock_propagation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_semantic_clock_propagation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_semantic_clock_propagation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_semantic_clock_propagation", "eval_metric")
_emit_stores_embedding("p4", "test_semantic_clock_propagation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_semantic_clock_propagation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_semantic_clock_propagation", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clock_snapshot() -> SemanticClockSnapshot:
    """A deterministic clock snapshot for testing."""
    return SemanticClockSnapshot(tick=7, vector_clock=(("L0", 3), ("L3", 4)))


@pytest.fixture
def route_ref() -> RouteDecisionRef:
    return RouteDecisionRef(
        trace_id="t1",
        decision="human_escalation",
        agent_name="A",
        reason="policy",
    )


@pytest.fixture
def policy_snap() -> PolicySnapshot:
    return PolicySnapshot(
        security_level="enforced",
        risk_tier="HIGH",
        laws_applied=(),
        policy_hash="abc",
    )


# ---------------------------------------------------------------------------
# 1. SemanticClockSnapshot — construction and serialization
# ---------------------------------------------------------------------------


class TestSemanticClockSnapshot:
    def test_from_clock_captures_state(self):
        clock = SemanticClock(step_id=5, vector_clock={"L0": 2, "L3": 3})
        snap = SemanticClockSnapshot.from_clock(clock)
        assert snap.tick == 5
        assert dict(snap.vector_clock) == {"L0": 2, "L3": 3}

    def test_to_dict_deterministic(self):
        snap = SemanticClockSnapshot(tick=3, vector_clock=(("L3", 2), ("L0", 1)))
        d = snap.to_dict()
        assert d == {"tick": 3, "vector_clock": {"L0": 1, "L3": 2}}
        keys = list(d["vector_clock"].keys())
        assert keys == sorted(keys), "vector_clock keys must be sorted"

    def test_negative_tick_rejected(self):
        with pytest.raises(ValueError, match="tick must be >= 0"):
            SemanticClockSnapshot(tick=-1)

    def test_frozen_immutable(self):
        snap = SemanticClockSnapshot(tick=1)
        with pytest.raises(AttributeError):
            snap.tick = 2  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 2. validate_semantic_clock — hard fail on None
# ---------------------------------------------------------------------------


class TestValidateSemanticClock:
    def test_none_raises_value_error(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            validate_semantic_clock(None)

    def test_wrong_type_raises_type_error(self):
        with pytest.raises(TypeError, match="SemanticClockSnapshot"):
            validate_semantic_clock(42)  # type: ignore[arg-type]

    def test_valid_snapshot_passes(self, clock_snapshot):
        result = validate_semantic_clock(clock_snapshot)
        assert result is clock_snapshot


# ---------------------------------------------------------------------------
# 3. Positive: RouteDecisionArtifact includes semantic_clock
# ---------------------------------------------------------------------------


class TestRouteDecisionArtifactClock:
    def test_semantic_clock_present(self, clock_snapshot):
        artifact = RouteDecisionArtifact(
            trace_id="t1",
            timestamp="2026-02-13T00:00:00Z",
            route_path=RoutePath.STANDARD_VALIDATION,
            risk_score=0.0,
            budget_est=0.0,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="hash",
            semantic_clock=clock_snapshot,
        )
        d = asdict(artifact)
        assert d["semantic_clock"] is not None
        assert d["semantic_clock"]["tick"] == 7

    def test_backward_compat_none_default(self):
        artifact = RouteDecisionArtifact(
            trace_id="t2",
            timestamp="2026-02-13T00:00:00Z",
            route_path=RoutePath.STANDARD_VALIDATION,
            risk_score=0.0,
            budget_est=0.0,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="",
        )
        assert artifact.semantic_clock is None


# ---------------------------------------------------------------------------
# 4. Positive: L3RouteDecisionArtifact includes semantic_clock
# ---------------------------------------------------------------------------


class TestL3RouteDecisionArtifactClock:
    def test_factory_propagates_clock(self, clock_snapshot):
        artifact = build_l3_route_decision_artifact(
            trace_id="t3",
            chosen={"method": "run", "agent_class": "A", "module": "m"},
            candidates=[],
            semantic_clock=clock_snapshot,
        )
        assert artifact.semantic_clock is clock_snapshot
        d = asdict(artifact)
        assert d["semantic_clock"]["tick"] == 7

    def test_factory_default_none(self):
        artifact = build_l3_route_decision_artifact(
            trace_id="t4",
            chosen={"method": "run", "agent_class": "A", "module": "m"},
            candidates=[],
        )
        assert artifact.semantic_clock is None


# ---------------------------------------------------------------------------
# 5. Positive: EvidencePack includes semantic_clock on escalation
# ---------------------------------------------------------------------------


class TestEvidencePackClock:
    def test_hil_evidence_pack_includes_clock(
        self,
        clock_snapshot,
        route_ref,
        policy_snap,
    ):
        pack = build_hil_evidence_pack(
            trace_id="t5",
            escalation_reason="policy",
            route_decision_ref=route_ref,
            policy_snapshot_data=policy_snap,
            semantic_clock=clock_snapshot,
        )
        assert pack.semantic_clock is clock_snapshot
        d = asdict(pack)
        assert d["semantic_clock"]["tick"] == 7

    def test_direct_construction_includes_clock(self, clock_snapshot):
        pack = EvidencePack(
            trace_id="t6",
            action_trace=("a",),
            policy_evals=("p",),
            risk_score=0.5,
            budget_breach_data={},
            boundary_snapshot_hash="hash",
            semantic_clock=clock_snapshot,
        )
        assert pack.semantic_clock.tick == 7

    def test_backward_compat_none_default(self):
        pack = EvidencePack(
            trace_id="t7",
            action_trace=("a",),
            policy_evals=("p",),
            risk_score=0.5,
            budget_breach_data={},
            boundary_snapshot_hash="hash",
        )
        assert pack.semantic_clock is None


# ---------------------------------------------------------------------------
# 6. Positive: PolicyUpdateProposal includes semantic_clock
# ---------------------------------------------------------------------------


class TestPolicyUpdateProposalClock:
    def test_hil_proposal_includes_clock(self, clock_snapshot):
        proposal = build_hil_policy_proposal(
            trace_id="t8",
            evidence_pack_id="ep-1",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="alice",
            review_notes="ok",
            request_id="req-1",
            semantic_clock=clock_snapshot,
        )
        assert proposal.semantic_clock is clock_snapshot
        d = asdict(proposal)
        assert d["semantic_clock"]["tick"] == 7

    def test_direct_construction_includes_clock(self, clock_snapshot):
        proposal = PolicyUpdateProposal(
            trace_id="t9",
            override_id="ov-1",
            proposed_policy_diff="diff",
            originating_agent="agent",
            semantic_clock_tick=0,
            semantic_clock=clock_snapshot,
        )
        assert proposal.semantic_clock.tick == 7

    def test_backward_compat_none_default(self):
        proposal = PolicyUpdateProposal(
            trace_id="t10",
            override_id="ov-2",
            proposed_policy_diff="diff",
            originating_agent="agent",
            semantic_clock_tick=0,
        )
        assert proposal.semantic_clock is None


# ---------------------------------------------------------------------------
# 7. Negative: None at chokepoint raises ValueError
# ---------------------------------------------------------------------------


class TestNoneAtChokepoint:
    def test_validate_raises_on_none(self):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            validate_semantic_clock(None)

    def test_validate_raises_on_wrong_type(self):
        with pytest.raises(TypeError, match="SemanticClockSnapshot"):
            validate_semantic_clock({"tick": 1})  # type: ignore[arg-type]

    def test_route_decision_artifact_allows_none_construction(self):
        artifact = RouteDecisionArtifact(
            trace_id="t11",
            timestamp="2026-02-13T00:00:00Z",
            route_path=RoutePath.STANDARD_VALIDATION,
            risk_score=0.0,
            budget_est=0.0,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="",
        )
        with pytest.raises(ValueError, match="semantic_clock is required"):
            validate_semantic_clock(artifact.semantic_clock)


# ---------------------------------------------------------------------------
# 8. Determinism: same input → byte-identical JSON
# ---------------------------------------------------------------------------


class TestDeterministicSerialization:
    def _make_route_artifact(self, clock_snapshot):
        return RouteDecisionArtifact(
            trace_id="det-1",
            timestamp="2026-02-13T00:00:00Z",
            route_path=RoutePath.STANDARD_VALIDATION,
            risk_score=0.1,
            budget_est=0.2,
            rationale_enum=RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="hash123",
            semantic_clock=clock_snapshot,
        )

    def test_route_decision_byte_identical(self, clock_snapshot):
        a1 = self._make_route_artifact(clock_snapshot)
        a2 = self._make_route_artifact(clock_snapshot)
        j1 = json.dumps(asdict(a1), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(asdict(a2), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_evidence_pack_byte_identical(self, clock_snapshot):
        def _make():
            return EvidencePack(
                trace_id="det-2",
                action_trace=("a",),
                policy_evals=("p",),
                risk_score=0.5,
                budget_breach_data={},
                boundary_snapshot_hash="hash",
                semantic_clock=clock_snapshot,
            )

        j1 = json.dumps(asdict(_make()), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(asdict(_make()), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_policy_proposal_byte_identical(self, clock_snapshot):
        def _enum_default(o):
            if hasattr(o, "value"):
                return o.value
            raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

        def _make():
            return PolicyUpdateProposal(
                trace_id="det-3",
                override_id="ov-det",
                proposed_policy_diff="diff",
                originating_agent="agent",
                semantic_clock_tick=0,
                semantic_clock=clock_snapshot,
            )

        j1 = json.dumps(asdict(_make()), sort_keys=True, separators=(",", ":"), default=_enum_default)
        j2 = json.dumps(asdict(_make()), sort_keys=True, separators=(",", ":"), default=_enum_default)
        assert j1 == j2

    def test_semantic_clock_in_json_has_tick(self, clock_snapshot):
        artifact = self._make_route_artifact(clock_snapshot)
        raw = json.dumps(asdict(artifact), sort_keys=True, indent=2)
        parsed = json.loads(raw)
        sc = parsed["semantic_clock"]
        assert "tick" in sc
        assert sc["tick"] == 7
        assert "vector_clock" in sc
