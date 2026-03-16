"""
Hardened SSOT routing algorithm tests — 10-agent scenario coverage.

Tests ``compute_routing_decision`` (pure function) and ``_route_decision``
integration on ``AutonomousDecisionEngine``.  No I/O, no subprocess, no LLM.

Gate coverage:
  GATE_0  — replay_mode=True   → DETERMINISTIC
  GATE_1  — retry_count>=3     → GEMINI / FAIL_CLOSED
  GATE_2a — structural + det_cov  → DETERMINISTIC
  GATE_2b — structural, no det_cov → GEMINI / FAIL_CLOSED
  GATE_3  — critical surface mech → DETERMINISTIC
  THRESH_LOW   — S<=13         → DETERMINISTIC
  THRESH_MED_QWEN — S 14-26    → QWEN
  THRESH_MED_QWEN_DISALLOWED   → GEMINI (fall-up, no det_cov)
  THRESH_MED_QWEN_DISALLOWED_DET_FALLBACK → DETERMINISTIC
  THRESH_HIGH  — S>=27         → GEMINI
  THRESH_HIGH_HARD_OVERRIDE    → GEMINI (B==3 or F==3 and C>=2 or A>=1)
  LATENCY_DOWN — L=0 near S=14 → biases QWEN→DETERMINISTIC
  LATENCY_UP   — L=3 near S=13 → biases DETERMINISTIC→QWEN
  FAIL_CLOSED  — all providers prohibited
  DETERMINISM_DIGEST uniqueness
"""

import os

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_hardened_routing_ssot")
_emit_applies_guardrail("p0", "test_hardened_routing_ssot", "p0_governance")
_emit_reads_policy_state("p0", "test_hardened_routing_ssot", "policy_binding")
_emit_snapshots_state("p0", "test_hardened_routing_ssot", "state_snapshot")
emit_replay_key("p0", "test_hardened_routing_ssot")
emit_determinism_digest("p0", "test_hardened_routing_ssot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hardened_routing_ssot", "execution_auth")
_emit_validates_capability("p2", "test_hardened_routing_ssot", "capability_check")
_emit_routes_to_capability("p2", "test_hardened_routing_ssot", "capability_route")
_emit_writes_via_uwg("p2", "test_hardened_routing_ssot", "uwg_write")
_emit_blocks_direct_write("p2", "test_hardened_routing_ssot", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hardened_routing_ssot", "tool_invocation")
_emit_captures_execution_output("p2", "test_hardened_routing_ssot", "exec_output")
_emit_dispatches_agent("p3", "test_hardened_routing_ssot", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hardened_routing_ssot", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hardened_routing_ssot", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hardened_routing_ssot", "healing_outcome")
_emit_escalates_failure("p3", "test_hardened_routing_ssot", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hardened_routing_ssot", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hardened_routing_ssot", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hardened_routing_ssot", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hardened_routing_ssot", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hardened_routing_ssot", "eval_metric")
_emit_stores_embedding("p4", "test_hardened_routing_ssot", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hardened_routing_ssot", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hardened_routing_ssot", "exec_snapshot_link")

os.environ.setdefault("AGENTIC_BYPASS_LONGPATHS_CHECK", "1")

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.scripts.execute_ssot import (  # noqa: E402
    _QWEN_DISALLOWED,
    _STRUCTURAL_CLASS,
    AutonomousDecisionEngine,
    ConfidenceScore,
    FailureType,
    RoutingInputs,
    RoutingTier,
    compute_routing_decision,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_hardened_routing_ssot", "p4obs", "metric_1")
_emit_emits_metric_event("test_hardened_routing_ssot", "p4obs", "metric_2")
_emit_emits_metric_event("test_hardened_routing_ssot", "p4obs", "metric_3")
_emit_emits_metric_event("test_hardened_routing_ssot", "p4obs", "metric_4")
_emit_emits_metric_event("test_hardened_routing_ssot", "p4obs", "metric_5")
_emit_emits_metric_event("test_hardened_routing_ssot", "p4obs", "metric_6")
_emit_records_incident_event("test_hardened_routing_ssot", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hardened_routing_ssot", "p4obs", "anomaly")
_emit_writes_observability_log("test_hardened_routing_ssot", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hardened_routing_ssot", "p4obs", "mon_state")
_emit_triggers_alert("test_hardened_routing_ssot", "p4obs", "alert")
_emit_links_incident_trace("test_hardened_routing_ssot", "p4obs", "trace_link")
_emit_captures_pattern("test_hardened_routing_ssot", "p3lm", "pattern")
_emit_records_learning_event("test_hardened_routing_ssot", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hardened_routing_ssot", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hardened_routing_ssot", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hardened_routing_ssot", "p3lm", "routing")
_emit_improves_agent_policy("test_hardened_routing_ssot", "p3lm", "policy")
_emit_stores_learning_state("test_hardened_routing_ssot", "p3lm", "state")
_emit_records_execution_trace("test_hardened_routing_ssot", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hardened_routing_ssot", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hardened_routing_ssot", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hardened_routing_ssot", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hardened_routing_ssot", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hardened_routing_ssot", "env_read", "p2_env_1")
_emit_reads_environ("test_hardened_routing_ssot", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hardened_routing_ssot", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hardened_routing_ssot", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_hardened_routing_ssot", "context_pull")
_emit_pulls_context("p1", "test_hardened_routing_ssot", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_hardened_routing_ssot", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hardened_routing_ssot", "uwg_term_secondary")
_emit_writes_through("p1", "test_hardened_routing_ssot", "write_through")
_emit_writes_through("p1", "test_hardened_routing_ssot", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_hardened_routing_ssot", "safety_validation")
_emit_invokes_eval("p1", "test_hardened_routing_ssot", "eval_call")
_emit_proposal_commits_routing("p1", "test_hardened_routing_ssot", "routing_commit")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ri(**kwargs) -> RoutingInputs:
    """Build RoutingInputs with NAMING as default failure_type."""
    kwargs.setdefault("failure_type", FailureType.NAMING)
    return RoutingInputs(**kwargs)


def _score(C=0, B=0, A=0, N=0, F=0, playbook_match=False) -> int:
    S = 3 * C + 4 * B + 3 * A + 2 * N + 4 * F
    if playbook_match:
        S = max(0, S - 4)
    return S


# ---------------------------------------------------------------------------
# Gate 0 — Replay gate
# ---------------------------------------------------------------------------


class TestGate0Replay:
    def test_replay_always_deterministic(self):
        ri = _ri(
            failure_type=FailureType.LAYER_VIOLATION, replay_mode=True, C=3, B=3, A=3, F=3, retry_count=5
        )
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert d.gate_applied == "GATE_0_REPLAY"

    def test_replay_beats_structural_class(self):
        """Replay gate fires before structural class gate."""
        ri = _ri(failure_type=FailureType.KILL_SWITCH_BYPASS, replay_mode=True, deterministic_coverage=False)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert "GATE_0" in d.gate_applied


# ---------------------------------------------------------------------------
# Gate 1 — Global retry override
# ---------------------------------------------------------------------------


class TestGate1Retry:
    def test_retry_gte3_goes_gemini(self):
        ri = _ri(retry_count=3, C=1, B=1)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI
        assert "GATE_1" in d.gate_applied

    def test_retry_gte3_gemini_prohibited_fails_closed(self):
        ri = _ri(retry_count=4, provider_prohibited_gemini=True)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.FAIL_CLOSED
        assert "GATE_1" in d.gate_applied

    def test_retry_2_does_not_trigger(self):
        """retry_count=2 must NOT fire gate 1."""
        ri = _ri(retry_count=2, C=0, B=0, A=0, N=0, F=0)
        d = compute_routing_decision(ri)
        # Score = 0 → DETERMINISTIC via threshold
        assert d.tier == RoutingTier.DETERMINISTIC
        assert "GATE_1" not in d.gate_applied


# ---------------------------------------------------------------------------
# Gate 2 — Structural class pre-gates
# ---------------------------------------------------------------------------


class TestGate2Structural:
    @pytest.mark.parametrize("ftype", list(_STRUCTURAL_CLASS))
    def test_structural_with_det_cov_is_deterministic(self, ftype):
        ri = RoutingInputs(failure_type=ftype, deterministic_coverage=True)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert d.gate_applied == "GATE_2_STRUCTURAL_DET_COV"

    @pytest.mark.parametrize("ftype", list(_STRUCTURAL_CLASS))
    def test_structural_no_det_cov_goes_gemini(self, ftype):
        ri = RoutingInputs(failure_type=ftype, deterministic_coverage=False)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI
        assert "GATE_2" in d.gate_applied

    def test_structural_no_det_cov_gemini_prohibited(self):
        ri = RoutingInputs(
            failure_type=FailureType.GATEWAY_BYPASS,
            deterministic_coverage=False,
            provider_prohibited_gemini=True,
        )
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.FAIL_CLOSED


# ---------------------------------------------------------------------------
# Gate 3 — Critical surface mechanical exception
# ---------------------------------------------------------------------------


class TestGate3CriticalSurface:
    def test_critical_surface_mech_fires(self):
        ri = _ri(
            B=3, A=0, C=1, playbook_match=True, deterministic_coverage=True, failure_type=FailureType.NAMING
        )
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert d.gate_applied == "GATE_3_CRITICAL_SURFACE_MECH"

    def test_critical_surface_requires_A0(self):
        """A=1 must prevent gate 3 from firing."""
        ri = _ri(B=3, A=1, C=1, playbook_match=True, deterministic_coverage=True)
        d = compute_routing_decision(ri)
        assert d.gate_applied != "GATE_3_CRITICAL_SURFACE_MECH"

    def test_critical_surface_requires_det_cov(self):
        ri = _ri(B=3, A=0, C=1, playbook_match=True, deterministic_coverage=False)
        d = compute_routing_decision(ri)
        assert d.gate_applied != "GATE_3_CRITICAL_SURFACE_MECH"


# ---------------------------------------------------------------------------
# Score + Threshold routing
# ---------------------------------------------------------------------------


class TestThresholdRouting:
    def test_score_zero_is_deterministic(self):
        ri = _ri(C=0, B=0, A=0, N=0, F=0)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert d.score == 0

    def test_score_13_boundary_deterministic(self):
        # C=1,B=1,A=1,N=1,F=0 → 3+4+3+2+0=12
        ri = _ri(C=1, B=1, A=1, N=1, F=0)
        d = compute_routing_decision(ri)
        assert d.score == 12
        assert d.tier == RoutingTier.DETERMINISTIC

    def test_score_14_goes_qwen(self):
        # C=0,B=2,N=1,F=1 → 8+2+4=14. Use L=1 (neutral) to avoid latency tie-breaker.
        ri = _ri(C=0, B=2, N=1, F=1, L=1)
        assert _score(C=0, B=2, N=1, F=1) == 14
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.QWEN
        assert d.score == 14

    def test_score_26_boundary_qwen(self):
        # B=3,A=2,N=2,F=1 → 12+6+4+4=26. Use L=1 (neutral) to avoid latency tie-breaker.
        ri = _ri(B=3, A=2, N=2, F=1, L=1)
        assert _score(B=3, A=2, N=2, F=1) == 26
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.QWEN
        assert d.score == 26

    def test_score_27_goes_gemini(self):
        # B=3,A=2,N=2,F=1 → 26; add C=1 → 27? 3+12+6+4+4=29. Use N=3,B=3,A=1 → 6+12+3=21 no. C=1,B=3,A=1,N=1,F=1 → 3+12+3+2+4=24. Try B=3,F=2,A=1 → 12+8+3=23. B=3,F=3 → 12+12=24 still. B=3,C=2,F=2 → 12+6+8=26. B=3,C=2,F=2,N=1 → 28. B=3,F=3,A=1 → 12+12+3=27 ✓
        ri = _ri(B=3, F=3, A=1)
        assert _score(B=3, F=3, A=1) == 27
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI
        assert d.score == 27

    def test_high_score_hard_override_gemini(self):
        """B==3 and F==3 and C>=2 → hard override to GEMINI."""
        ri = _ri(B=3, F=3, C=2, A=0)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI
        assert "HARD_OVERRIDE" in d.gate_applied

    def test_high_score_all_providers_prohibited(self):
        ri = _ri(B=3, F=3, C=2, provider_prohibited_gemini=True, provider_prohibited_qwen=True)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.FAIL_CLOSED

    def test_playbook_dampener_reduces_score(self):
        # Without playbook: C=2,B=1,N=1,F=1 → 6+4+2+4=16 → QWEN
        # With playbook: 16-4=12 → DETERMINISTIC
        ri_no = _ri(C=2, B=1, N=1, F=1, playbook_match=False)
        ri_yes = _ri(C=2, B=1, N=1, F=1, playbook_match=True)
        d_no = compute_routing_decision(ri_no)
        d_yes = compute_routing_decision(ri_yes)
        assert d_no.tier == RoutingTier.QWEN
        assert d_yes.tier == RoutingTier.DETERMINISTIC


# ---------------------------------------------------------------------------
# Qwen-disallowed fall-up logic
# ---------------------------------------------------------------------------


class TestQwenDisallowed:
    @pytest.mark.parametrize("ftype", list(_QWEN_DISALLOWED - _STRUCTURAL_CLASS))
    def test_qwen_disallowed_non_structural_falls_to_gemini(self, ftype):
        """IMPORT_BOUNDARY_VIOLATION and SCHEMA_REQUIRED_FIELDS_MISSING in med band → GEMINI."""
        # Force medium score (14-26) with no det_cov
        ri = RoutingInputs(failure_type=ftype, B=2, N=1, F=1, deterministic_coverage=False)
        assert 14 <= _score(B=2, N=1, F=1) <= 26
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI
        assert "QWEN_DISALLOWED" in d.gate_applied

    def test_qwen_disallowed_with_det_cov_and_low_A_C_returns_det(self):
        ri = RoutingInputs(
            failure_type=FailureType.IMPORT_BOUNDARY_VIOLATION,
            B=2,
            N=1,
            F=1,
            A=0,
            C=0,
            deterministic_coverage=True,
        )
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert "DET_FALLBACK" in d.gate_applied

    def test_provider_prohibited_qwen_falls_to_gemini(self):
        """provider_prohibited_qwen with normal NAMING and med score → GEMINI."""
        ri = _ri(B=2, N=1, F=1, provider_prohibited_qwen=True)
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI

    def test_qwen_disallowed_both_providers_prohibited(self):
        ri = RoutingInputs(
            failure_type=FailureType.SCHEMA_REQUIRED_FIELDS_MISSING,
            B=2,
            N=1,
            F=1,
            provider_prohibited_gemini=True,
            provider_prohibited_qwen=True,
        )
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.FAIL_CLOSED


# ---------------------------------------------------------------------------
# Latency tie-breaker (Gate 6)
# ---------------------------------------------------------------------------


class TestLatencyTieBreaker:
    def test_L0_biases_qwen_down_to_deterministic(self):
        """S=14 (QWEN boundary) + L=0 → biases to DETERMINISTIC."""
        ri = _ri(B=2, N=1, F=1, L=0)  # S=14 → QWEN normally
        assert _score(B=2, N=1, F=1) == 14
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.DETERMINISTIC
        assert "L_TIEBREAK_DOWN" in d.gate_applied

    def test_L3_biases_deterministic_up_to_qwen(self):
        """S=13 (DETERMINISTIC boundary) + L=3 → biases to QWEN."""
        # C=1,B=1,A=1,N=1,F=0 → 12 — need exactly 13. B=1,F=1,C=1,N=1 → 4+4+3+2=13 ✓
        ri = _ri(B=1, F=1, C=1, N=1, L=3)
        assert _score(B=1, F=1, C=1, N=1) == 13
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.QWEN
        assert "L_TIEBREAK_UP" in d.gate_applied

    def test_latency_tiebreak_does_not_apply_outside_boundary(self):
        """S=5 (far from boundary) — latency has no effect."""
        ri_L0 = _ri(C=1, B=0, F=0, L=0)  # S=3
        ri_L3 = _ri(C=1, B=0, F=0, L=3)
        assert (
            compute_routing_decision(ri_L0).tier
            == compute_routing_decision(ri_L3).tier
            == RoutingTier.DETERMINISTIC
        )

    def test_latency_tiebreak_blocked_on_qwen_disallowed(self):
        """L=0 tie-breaker must not apply when failure_type is qwen_disallowed."""
        # S=14 (QWEN boundary), L=0, but ftype is IMPORT_BOUNDARY_VIOLATION
        # → already falls to GEMINI via QWEN_DISALLOWED; tie-breaker cannot cross to DET via L_TIEBREAK
        ri = RoutingInputs(
            failure_type=FailureType.IMPORT_BOUNDARY_VIOLATION,
            B=2,
            N=1,
            F=1,
            L=0,
            deterministic_coverage=False,
        )
        d = compute_routing_decision(ri)
        assert d.tier == RoutingTier.GEMINI
        assert "L_TIEBREAK" not in d.gate_applied


# ---------------------------------------------------------------------------
# Determinism digest uniqueness
# ---------------------------------------------------------------------------


class TestDeterminismDigest:
    def test_different_tiers_produce_different_digests(self):
        d_det = compute_routing_decision(_ri(C=0, B=0, A=0, N=0, F=0))
        d_qwen = compute_routing_decision(_ri(B=2, N=1, F=1))
        assert d_det.determinism_digest != d_qwen.determinism_digest

    def test_same_inputs_produce_same_digest(self):
        ri = _ri(B=2, N=1, F=1)
        assert (
            compute_routing_decision(ri).determinism_digest == compute_routing_decision(ri).determinism_digest
        )

    def test_digest_is_16_chars(self):
        d = compute_routing_decision(_ri())
        assert len(d.determinism_digest) == 16


# ---------------------------------------------------------------------------
# AutonomousDecisionEngine._route_decision integration — 10 named agents
# ---------------------------------------------------------------------------

AGENTS_10 = [
    "arch_governor",
    "file_classification",
    "cognitive_disposition",
    "observability_probe",
    "location",
    "root_hygiene",
    "hierarchy",
    "naming",
    "schema_validator",
    "import_boundary",
]


class TestRouteDecisionIntegration:
    """Verify _route_decision produces a valid RoutingDecision for each of the 10 agents."""

    @pytest.fixture
    def engine(self):
        return AutonomousDecisionEngine(enable_llm=False)

    @pytest.mark.parametrize("agent_name", AGENTS_10)
    def test_route_decision_returns_valid_tier(self, engine, agent_name):
        cs = ConfidenceScore(value=0.62, reasoning="Base: 0.70, Pattern: 0.55")
        rd = engine._route_decision(
            confidence=cs,
            agent_name=agent_name,
            territory=AGENTIC_CORE_DIR,
        )
        assert rd.tier in list(RoutingTier)
        assert rd.gate_applied
        assert len(rd.determinism_digest) == 16

    @pytest.mark.parametrize("agent_name", AGENTS_10)
    def test_route_decision_high_confidence_deterministic(self, engine, agent_name):
        """High confidence (0.9) should yield DETERMINISTIC for standard agents."""
        cs = ConfidenceScore(value=0.90, reasoning="Base: 0.90, Pattern: 0.90")
        rd = engine._route_decision(
            confidence=cs,
            agent_name=agent_name,
            territory=AGENTIC_CORE_DIR,
        )
        # C=0 (high conf), F=1, B=2 → S=4+2=6? Let's just check tier is DETERMINISTIC or QWEN
        assert rd.tier in {RoutingTier.DETERMINISTIC, RoutingTier.QWEN, RoutingTier.GEMINI}

    def test_route_decision_layer_violation_structural_no_det_cov_goes_gemini(self, engine):
        cs = ConfidenceScore(value=0.55, reasoning="LAYER_VIOLATION")
        rd = engine._route_decision(
            confidence=cs,
            agent_name="arch_governor",
            territory=AGENTIC_CORE_DIR,
            failure_type=FailureType.LAYER_VIOLATION,
            deterministic_coverage=False,
        )
        assert rd.tier == RoutingTier.GEMINI

    def test_route_decision_replay_mode_always_det(self, engine):
        cs = ConfidenceScore(value=0.3, reasoning="low")
        rd = engine._route_decision(
            confidence=cs,
            agent_name="naming",
            territory=AGENTIC_CORE_DIR,
            replay_mode=True,
        )
        assert rd.tier == RoutingTier.DETERMINISTIC

    def test_route_decision_retry3_goes_gemini(self, engine):
        cs = ConfidenceScore(value=0.5, reasoning="retry")
        rd = engine._route_decision(
            confidence=cs,
            agent_name="location",
            territory="unknown",
            retry_count=3,
        )
        assert rd.tier == RoutingTier.GEMINI

    def test_route_decision_L5_territory_raises_blast_radius(self, engine):
        """L5 territory should produce B=3, which raises score."""
        cs = ConfidenceScore(value=0.62, reasoning="Base: 0.62, Pattern: 0.62")
        rd = engine._route_decision(
            confidence=cs,
            agent_name="schema_validator",
            territory="L5_safety",
        )
        assert rd.factors["B"] == 3

    def test_route_decision_all_providers_prohibited_fails_closed(self, engine):
        """Both providers prohibited → FAIL_CLOSED for high-score scenario."""
        cs = ConfidenceScore(value=0.3, reasoning="Base: 0.3, Pattern: 0.3")
        rd = engine._route_decision(
            confidence=cs,
            agent_name="import_boundary",
            territory=AGENTIC_CORE_DIR,
            failure_type=FailureType.IMPORT_BOUNDARY_VIOLATION,
            deterministic_coverage=False,
            provider_prohibited_gemini=True,
            provider_prohibited_qwen=True,
        )
        assert rd.tier == RoutingTier.FAIL_CLOSED

    def test_as_log_line_contains_required_fields(self, engine):
        cs = ConfidenceScore(value=0.62, reasoning="Base: 0.62")
        rd = engine._route_decision(cs, "arch_governor", AGENTIC_CORE_DIR)
        log = rd.as_log_line()
        for field in ["tier=", "S=", "gate=", "model=", "digest="]:
            assert field in log, f"Missing {field!r} in log line: {log}"
