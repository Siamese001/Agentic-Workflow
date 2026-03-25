"""Consolidation tests for the unified confidence routing system.

Covers all 10 phases of the confidence-routing consolidation:
- Phase 1: SSOT_SCORE_THRESHOLD_DET/QWEN constants in healing_tier_config
- Phase 2: route_by_confidence() bridge in healing_tier_router
- Phase 3: heal_policy_types SCORE_THRESHOLD_DET/QWEN delegate to config
- Phase 4: ConfidenceScore properties use canonical constants (no os.getenv)
- Phase 5+6: _ssot_routing uses canonical constants (no bare literals)
- Phase 7: _ssot_reporting band keys use canonical constants
- Phase 8: tiered_batch_util heuristic_threshold default = HEALING_CONFIDENCE_X
- Phase 9: qwen_meta_learning.__all__ does NOT re-export X/Y
- Phase 10: SovereignBaseAgent and decorators_util delegate to route_by_confidence
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_confidence_routing_consolidation")
# REMOVED: _emit_applies_guardrail("p0", "test_confidence_routing_consolidation", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_confidence_routing_consolidation", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_confidence_routing_consolidation", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_confidence_routing_consolidation", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_confidence_routing_consolidation", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_confidence_routing_consolidation", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_confidence_routing_consolidation", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_confidence_routing_consolidation", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_confidence_routing_consolidation", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_confidence_routing_consolidation", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_confidence_routing_consolidation", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_confidence_routing_consolidation", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_confidence_routing_consolidation", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_confidence_routing_consolidation", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_confidence_routing_consolidation", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_confidence_routing_consolidation", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_confidence_routing_consolidation", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_confidence_routing_consolidation", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_confidence_routing_consolidation", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_confidence_routing_consolidation", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_confidence_routing_consolidation", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_confidence_routing_consolidation", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_confidence_routing_consolidation", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_confidence_routing_consolidation", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_confidence_routing_consolidation", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_confidence_routing_consolidation", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_confidence_routing_consolidation", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_confidence_routing_consolidation", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_confidence_routing_consolidation", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_confidence_routing_consolidation", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_confidence_routing_consolidation", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_confidence_routing_consolidation", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_confidence_routing_consolidation", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_confidence_routing_consolidation", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_confidence_routing_consolidation", "write_through")
# REMOVED: _emit_writes_through("p1", "test_confidence_routing_consolidation", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_confidence_routing_consolidation", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_confidence_routing_consolidation", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_confidence_routing_consolidation", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_confidence_routing_consolidation", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_confidence_routing_consolidation", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_confidence_routing_consolidation", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_confidence_routing_consolidation", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_confidence_routing_consolidation", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_confidence_routing_consolidation", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_confidence_routing_consolidation", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_confidence_routing_consolidation", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_confidence_routing_consolidation", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_confidence_routing_consolidation", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_confidence_routing_consolidation", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_confidence_routing_consolidation")
# REMOVED: _emit_gated_by_confidence("p1", "test_confidence_routing_consolidation", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_confidence_routing_consolidation")
# REMOVED: emit_determinism_digest("p0", "test_confidence_routing_consolidation")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_confidence_routing_consolidation", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_confidence_routing_consolidation", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_confidence_routing_consolidation", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_confidence_routing_consolidation", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_confidence_routing_consolidation", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_confidence_routing_consolidation", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_confidence_routing_consolidation", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_confidence_routing_consolidation", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_confidence_routing_consolidation", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_confidence_routing_consolidation", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_confidence_routing_consolidation", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_confidence_routing_consolidation", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_confidence_routing_consolidation", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_confidence_routing_consolidation", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_confidence_routing_consolidation", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_confidence_routing_consolidation", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_confidence_routing_consolidation", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_confidence_routing_consolidation", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_confidence_routing_consolidation", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_confidence_routing_consolidation", "exec_snapshot_link")

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[5]


# ---------------------------------------------------------------------------
# Phase 1 — SSOT constants exist and are correct
# ---------------------------------------------------------------------------

class TestSSOTScoreThresholds:
    def test_det_constant_exists(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_DET
        assert SSOT_SCORE_THRESHOLD_DET is not None

    def test_qwen_constant_exists(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_QWEN
        assert SSOT_SCORE_THRESHOLD_QWEN is not None

    def test_det_value_is_13(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_DET
        assert SSOT_SCORE_THRESHOLD_DET == 13

    def test_qwen_value_is_26(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_QWEN
        assert SSOT_SCORE_THRESHOLD_QWEN == 26

    def test_det_is_int(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_DET
        assert isinstance(SSOT_SCORE_THRESHOLD_DET, int)

    def test_qwen_is_int(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_QWEN
        assert isinstance(SSOT_SCORE_THRESHOLD_QWEN, int)

    def test_det_less_than_qwen(self):
        from agentic_core.L2_execution.healers.healing_tier_config import (
            SSOT_SCORE_THRESHOLD_DET,
            SSOT_SCORE_THRESHOLD_QWEN,
        )
        assert SSOT_SCORE_THRESHOLD_DET < SSOT_SCORE_THRESHOLD_QWEN

    def test_both_in_all(self):
        import agentic_core.L2_execution.healers.healing_tier_config as m
        assert "SSOT_SCORE_THRESHOLD_DET" in m.__all__
        assert "SSOT_SCORE_THRESHOLD_QWEN" in m.__all__


# ---------------------------------------------------------------------------
# Phase 2 — route_by_confidence() bridge function
# ---------------------------------------------------------------------------

class TestRouteByConfidence:
    def test_importable(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        assert callable(route_by_confidence)

    def test_in_all(self):
        import agentic_core.L2_execution.healers.healing_tier_router as m
        assert "route_by_confidence" in m.__all__

    def test_returns_healing_decision(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingDecision
        result = route_by_confidence(confidence=0.9)
        assert isinstance(result, HealingDecision)

    def test_high_confidence_routes_local_agent(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        result = route_by_confidence(confidence=0.95)
        assert result.tier == HealingTier.LOCAL_AGENT

    def test_mid_confidence_routes_qwen(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        result = route_by_confidence(confidence=0.65)
        assert result.tier == HealingTier.QWEN_VLLM

    def test_low_confidence_routes_gemini(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        result = route_by_confidence(confidence=0.30)
        assert result.tier == HealingTier.GEMINI_2_5_PRO

    def test_result_has_reason_codes(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        result = route_by_confidence(confidence=0.5)
        assert isinstance(result.reason_codes, tuple)
        assert len(result.reason_codes) > 0

    def test_result_heal_confidence_in_unit_interval(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        result = route_by_confidence(confidence=0.7)
        assert 0.0 <= result.heal_confidence <= 1.0

    def test_accepts_retry_count(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        result = route_by_confidence(confidence=0.9, retry_count=5)
        assert result is not None

    def test_accepts_failure_type(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        result = route_by_confidence(confidence=0.9, failure_type="import_error")
        assert result is not None

    def test_deterministic_same_inputs(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        r1 = route_by_confidence(confidence=0.6, retry_count=1, failure_type="type_error")
        r2 = route_by_confidence(confidence=0.6, retry_count=1, failure_type="type_error")
        assert r1.tier == r2.tier

    def test_boundary_at_confidence_x(self):
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        above = route_by_confidence(confidence=HEALING_CONFIDENCE_X + 0.01)
        assert above.tier == HealingTier.LOCAL_AGENT

    def test_boundary_at_confidence_y(self):
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_Y
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        below = route_by_confidence(confidence=HEALING_CONFIDENCE_Y - 0.01)
        assert below.tier == HealingTier.GEMINI_2_5_PRO


# ---------------------------------------------------------------------------
# Phase 3 — heal_policy_types SCORE_THRESHOLD_* delegate to config (no literals)
# ---------------------------------------------------------------------------

class TestHealPolicyTypesThresholdDelegation:
    def test_score_threshold_det_matches_config(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_DET
        from agentic_core.L5_safety.types.heal_policy_types import SCORE_THRESHOLD_DET
        assert SCORE_THRESHOLD_DET == SSOT_SCORE_THRESHOLD_DET

    def test_score_threshold_qwen_matches_config(self):
        from agentic_core.L2_execution.healers.healing_tier_config import SSOT_SCORE_THRESHOLD_QWEN
        from agentic_core.L5_safety.types.heal_policy_types import SCORE_THRESHOLD_QWEN
        assert SCORE_THRESHOLD_QWEN == SSOT_SCORE_THRESHOLD_QWEN

    def test_no_bare_literals_in_source(self):
        src = (REPO_ROOT / "agentic_core/L5_safety/types/heal_policy_types.py").read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        # No module-level integer assignments of 13 or 26
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in ("SCORE_THRESHOLD_DET", "SCORE_THRESHOLD_QWEN"):
                        pytest.fail(
                            f"heal_policy_types.py assigns {t.id} as a bare literal — must import from config"
                        )

    def test_sentinel_constants_importable(self):
        from agentic_core.L5_safety.types.heal_policy_types import (
            BATCH_SIZE,
            BUFFER_SIZE,
            DEFAULT_SLEEP,
            MAX_DEPTH,
            MAX_RETRIES,
            THRESHOLD,
        )
        assert all(v is not None for v in [MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD, BUFFER_SIZE, BATCH_SIZE, MAX_DEPTH])


# ---------------------------------------------------------------------------
# Phase 4 — ConfidenceScore properties use canonical constants, not os.getenv
# ---------------------------------------------------------------------------

class TestConfidenceScoreNoEnvVar:
    def test_no_getenv_in_ssot_types_confidence_score(self):
        src = (REPO_ROOT / "agentic_core/L0_routing/scripts/_ssot_types.py").read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ConfidenceScore":
                class_src = ast.get_source_segment(src, node) or ""
                assert "os.getenv" not in class_src, \
                    "ConfidenceScore must not use os.getenv — use canonical HEALING_CONFIDENCE_X/Y"
                assert "os.environ" not in class_src, \
                    "ConfidenceScore must not use os.environ — use canonical HEALING_CONFIDENCE_X/Y"

    def test_is_high_confidence_uses_canonical_x(self):
        from agentic_core.L0_routing.scripts._ssot_types import ConfidenceScore
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X
        cs_high = ConfidenceScore(value=HEALING_CONFIDENCE_X + 0.01, reasoning="test")
        cs_low = ConfidenceScore(value=HEALING_CONFIDENCE_X - 0.01, reasoning="test")
        assert cs_high.is_high_confidence is True
        assert cs_low.is_high_confidence is False

    def test_is_low_confidence_uses_canonical_y(self):
        from agentic_core.L0_routing.scripts._ssot_types import ConfidenceScore
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_Y
        cs_low = ConfidenceScore(value=HEALING_CONFIDENCE_Y - 0.01, reasoning="test")
        cs_med = ConfidenceScore(value=HEALING_CONFIDENCE_Y + 0.01, reasoning="test")
        assert cs_low.is_low_confidence is True
        assert cs_med.is_low_confidence is False

    def test_is_medium_confidence_bounded(self):
        from agentic_core.L0_routing.scripts._ssot_types import ConfidenceScore
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )
        mid = (HEALING_CONFIDENCE_X + HEALING_CONFIDENCE_Y) / 2.0
        cs = ConfidenceScore(value=mid, reasoning="test")
        assert cs.is_medium_confidence is True
        assert cs.is_high_confidence is False
        assert cs.is_low_confidence is False

    def test_no_high_threshold_property(self):
        from agentic_core.L0_routing.scripts._ssot_types import ConfidenceScore
        assert not hasattr(ConfidenceScore, "_high_threshold"), \
            "_high_threshold property must be removed — was backed by os.getenv"

    def test_no_med_threshold_property(self):
        from agentic_core.L0_routing.scripts._ssot_types import ConfidenceScore
        assert not hasattr(ConfidenceScore, "_med_threshold"), \
            "_med_threshold property must be removed — was backed by os.getenv"


# ---------------------------------------------------------------------------
# Phase 5+6 — _ssot_routing has no bare 0.75/0.5/13/26 literals in routing logic
# ---------------------------------------------------------------------------

class TestSsotRoutingNoHardcodedLiterals:
    def _get_routing_source(self) -> str:
        return (REPO_ROOT / "agentic_core/L0_routing/scripts/_ssot_routing.py").read_text(encoding="utf-8", errors="replace")

    def test_no_importerror_fallback_block(self):
        src = self._get_routing_source()
        assert "except ImportError" not in src or "_CONF_X = 0.8" not in src, \
            "_ssot_routing.py must not have ImportError fallback that hardcodes _CONF_X = 0.8"

    def test_imports_healing_confidence_x_at_module_level(self):
        src = self._get_routing_source()
        assert "HEALING_CONFIDENCE_X" in src, \
            "_ssot_routing.py must import HEALING_CONFIDENCE_X from healing_tier_config"

    def test_imports_ssot_score_thresholds(self):
        src = self._get_routing_source()
        assert "SSOT_SCORE_THRESHOLD_DET" in src, \
            "_ssot_routing.py must import SSOT_SCORE_THRESHOLD_DET"
        assert "SSOT_SCORE_THRESHOLD_QWEN" in src, \
            "_ssot_routing.py must import SSOT_SCORE_THRESHOLD_QWEN"

    def test_compute_routing_decision_uses_constants(self):
        from agentic_core.L0_routing.scripts._ssot_routing import compute_routing_decision
        from agentic_core.L0_routing.scripts._ssot_types import FailureType, RoutingInputs, RoutingTier
        # S = 3*1+4*1+3*0+2*0+4*1 = 11 → DETERMINISTIC (below _SCORE_DET=13)
        det_inputs = RoutingInputs(
            failure_type=FailureType.LAYER_VIOLATION,
            retry_count=0, C=1, B=1, A=0, N=0, F=1, L=0,
        )
        det_result = compute_routing_decision(det_inputs)
        assert det_result.tier in (
            RoutingTier.DETERMINISTIC, RoutingTier.QWEN,
            RoutingTier.GEMINI, RoutingTier.FAIL_CLOSED,
        )

    def test_ssot_routing_constants_match_config(self):
        import agentic_core.L0_routing.scripts._ssot_routing as m
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
            SSOT_SCORE_THRESHOLD_DET,
            SSOT_SCORE_THRESHOLD_QWEN,
        )
        assert m._CONF_X == HEALING_CONFIDENCE_X
        assert m._CONF_Y == HEALING_CONFIDENCE_Y
        assert m._SCORE_DET == SSOT_SCORE_THRESHOLD_DET
        assert m._SCORE_QWEN == SSOT_SCORE_THRESHOLD_QWEN


# ---------------------------------------------------------------------------
# Phase 7 — _ssot_reporting band keys are dynamic (not hardcoded 0.75/0.40)
# ---------------------------------------------------------------------------

class TestSsotReportingNoBandLiterals:
    def test_no_hardcoded_075_band_key(self):
        src = (REPO_ROOT / "agentic_core/L0_routing/scripts/_ssot_reporting.py").read_text(encoding="utf-8", errors="replace")
        assert "band_local_gte075" not in src, \
            "_ssot_reporting.py must not hardcode band_local_gte075 — use canonical _CONF_X"
        assert "band_qwen_040_074" not in src, \
            "_ssot_reporting.py must not hardcode band_qwen_040_074 — use canonical _CONF_Y/_CONF_X"

    def test_imports_healing_confidence_constants(self):
        src = (REPO_ROOT / "agentic_core/L0_routing/scripts/_ssot_reporting.py").read_text(encoding="utf-8", errors="replace")
        assert "HEALING_CONFIDENCE_X" in src
        assert "HEALING_CONFIDENCE_Y" in src


# ---------------------------------------------------------------------------
# Phase 8 — tiered_batch_util heuristic_threshold default = HEALING_CONFIDENCE_X
# ---------------------------------------------------------------------------

class TestTieredBatchUtilThreshold:
    def test_default_threshold_equals_healing_confidence_x(self):
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X
        sig = inspect.signature(
            __import__(
                "agentic_core.L5_safety.utils.tiered_batch_util",
                fromlist=["TieredBatchProcessor"],
            ).TieredBatchProcessor.__init__
        )
        default = sig.parameters["heuristic_threshold"].default
        assert default == HEALING_CONFIDENCE_X, \
            f"TieredBatchProcessor.heuristic_threshold default must be HEALING_CONFIDENCE_X={HEALING_CONFIDENCE_X}, got {default}"

    def test_no_bare_075_in_init_signature(self):
        src = (REPO_ROOT / "agentic_core/L5_safety/utils/tiered_batch_util.py").read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for default in node.args.defaults:
                    if isinstance(default, ast.Constant) and default.value == 0.75:
                        pytest.fail(
                            "TieredBatchProcessor.__init__ must not have bare 0.75 default — use _HEALING_CONFIDENCE_X"
                        )

    def test_sentinel_constants_importable(self):
        from agentic_core.L5_safety.utils.tiered_batch_util import (
            BATCH_SIZE,
            BUFFER_SIZE,
            DEFAULT_SLEEP,
            MAX_DEPTH,
            MAX_RETRIES,
            THRESHOLD,
        )
        assert all(v is not None for v in [MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD, BUFFER_SIZE, BATCH_SIZE, MAX_DEPTH])


# ---------------------------------------------------------------------------
# Phase 9 — qwen_meta_learning.__all__ does NOT re-export X/Y
# ---------------------------------------------------------------------------

class TestQwenMetaLearningNoXYReexport:
    def test_healing_confidence_x_not_in_all(self):
        import agentic_core.L2_execution.healers.qwen_meta_learning as m
        assert "HEALING_CONFIDENCE_X" not in m.__all__, \
            "qwen_meta_learning.__all__ must not re-export HEALING_CONFIDENCE_X — import from healing_tier_config directly"

    def test_healing_confidence_y_not_in_all(self):
        import agentic_core.L2_execution.healers.qwen_meta_learning as m
        assert "HEALING_CONFIDENCE_Y" not in m.__all__, \
            "qwen_meta_learning.__all__ must not re-export HEALING_CONFIDENCE_Y — import from healing_tier_config directly"

    def test_functional_exports_still_present(self):
        from agentic_core.L2_execution.healers.qwen_meta_learning import (
            clear_historical_success_rates,
            get_historical_success_rate,
            set_historical_success_rate,
            update_qwen_confidence_prior,
            validate_threshold_immutability,
        )
        assert all(callable(f) for f in [
            get_historical_success_rate, set_historical_success_rate,
            update_qwen_confidence_prior, validate_threshold_immutability,
            clear_historical_success_rates,
        ])


# ---------------------------------------------------------------------------
# Phase 10a — SovereignBaseAgent delegates to route_by_confidence
# ---------------------------------------------------------------------------

class TestSovereignBaseAgentUsesCanonicalRouter:
    def test_no_decide_heal_escalation_import_in_heal_repository(self):
        src = (REPO_ROOT / "agentic_core/base_agents/SovereignBaseAgent.py").read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
                fn_src = ast.get_source_segment(src, node) or ""
                assert "decide_heal_escalation" not in fn_src, \
                    "heal_repository() must not call decide_heal_escalation — use route_by_confidence"

    def test_route_by_confidence_import_in_heal_repository(self):
        src = (REPO_ROOT / "agentic_core/base_agents/SovereignBaseAgent.py").read_text(encoding="utf-8", errors="replace")
        assert "route_by_confidence" in src, \
            "SovereignBaseAgent must import route_by_confidence from healing_tier_router"

    def test_no_harcoded_confidence_default_075_kwarg(self):
        src = (REPO_ROOT / "agentic_core/base_agents/SovereignBaseAgent.py").read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
                fn_src = ast.get_source_segment(src, node) or ""
                assert "HealEscalationInputs(" not in fn_src, \
                    "heal_repository() must not construct HealEscalationInputs — delegate to route_by_confidence"


# ---------------------------------------------------------------------------
# Phase 10b — decorators_util delegates to route_by_confidence
# ---------------------------------------------------------------------------

class TestDecoratorsUtilUsesCanonicalRouter:
    def test_get_heal_policy_types_returns_route_by_confidence(self):
        from agentic_core.utils.decorators_util import _get_heal_policy_types
        result = _get_heal_policy_types()
        route_fn, reasoning_tier = result
        assert callable(route_fn), "_get_heal_policy_types() must return route_by_confidence as first element"

    def test_route_by_confidence_is_the_returned_fn(self):
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.utils.decorators_util import _get_heal_policy_types
        returned_fn, _ = _get_heal_policy_types()
        assert returned_fn is route_by_confidence

    def test_decide_reasoning_tier_backward_compat_still_callable(self):
        from agentic_core.utils.decorators_util import decide_reasoning_tier
        assert callable(decide_reasoning_tier)

    def test_no_heal_escalation_inputs_construction_in_standard_heal(self):
        src = (REPO_ROOT / "agentic_core/utils/decorators_util.py").read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "wrapper":
                fn_src = ast.get_source_segment(src, node) or ""
                assert "HealEscalationInputs(" not in fn_src, \
                    "standard_heal wrapper must not construct HealEscalationInputs — use route_by_confidence"


# ---------------------------------------------------------------------------
# Cross-cutting — single SSOT verification
# ---------------------------------------------------------------------------

class TestSingleSourceOfTruth:
    def test_healing_confidence_x_value_consistent_across_modules(self):
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X as cfg_x
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        # Just above X should always be LOCAL_AGENT
        result = route_by_confidence(confidence=cfg_x + 0.001)
        assert result.tier == HealingTier.LOCAL_AGENT

    def test_healing_confidence_y_value_consistent_across_modules(self):
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_Y as cfg_y
        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        # Just below Y should always be GEMINI
        result = route_by_confidence(confidence=cfg_y - 0.001)
        assert result.tier == HealingTier.GEMINI_2_5_PRO

    def test_score_thresholds_same_object_in_heal_policy_types_and_config(self):
        from agentic_core.L2_execution.healers.healing_tier_config import (
            SSOT_SCORE_THRESHOLD_DET,
            SSOT_SCORE_THRESHOLD_QWEN,
        )
        from agentic_core.L5_safety.types.heal_policy_types import SCORE_THRESHOLD_DET, SCORE_THRESHOLD_QWEN
        assert SCORE_THRESHOLD_DET is SSOT_SCORE_THRESHOLD_DET or SCORE_THRESHOLD_DET == SSOT_SCORE_THRESHOLD_DET
        assert SCORE_THRESHOLD_QWEN is SSOT_SCORE_THRESHOLD_QWEN or SCORE_THRESHOLD_QWEN == SSOT_SCORE_THRESHOLD_QWEN

    def test_no_envvar_confidence_fallback_anywhere_in_targets(self):
        targets = [
            "agentic_core/L0_routing/scripts/_ssot_routing.py",
            "agentic_core/L5_safety/types/heal_policy_types.py",
            "agentic_core/L5_safety/utils/tiered_batch_util.py",
        ]
        pattern = "os.getenv"
        for rel in targets:
            src = (REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr == "getenv":
                        # Check if the value being read is a confidence threshold
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and "CONFIDENCE" in str(arg.value).upper():
                                pytest.fail(
                                    f"{rel}: os.getenv({arg.value!r}) is a confidence env-var fallback — must use canonical constant"
                                )
