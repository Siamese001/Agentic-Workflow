"""
Wave 4 Phase 10 — Apps_* Integration Tests

§4-compliant test suite covering:
- ContactSafetyEngine: SSN detection, credit card detection, PII guards
- HallucinationDetector.check_batch: score calculation, threshold, suspicious patterns
- SkillScoreNormalizer: min-max normalisation, all-equal scores, empty input
- HopStageRegistry: stage registration, lookup, all 9 stages present, missing stage
"""

from __future__ import annotations

from unittest.mock import MagicMock

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "test_apps_integration", "execution_auth")
_emit_validates_capability("p2", "test_apps_integration", "capability_check")
_emit_routes_to_capability("p2", "test_apps_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_apps_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_apps_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_apps_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_apps_integration", "exec_output")
_emit_dispatches_agent("p3", "test_apps_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_apps_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_apps_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_apps_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_apps_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_apps_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_apps_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_apps_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_apps_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_apps_integration", "eval_metric")
_emit_stores_embedding("p4", "test_apps_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_apps_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_apps_integration", "exec_snapshot_link")
from apps_lic.engines.hop_stage_registry import (
    _REGISTRY,
    get_stage_handler,
    register_stage,
)
from apps_rg.engines.contact_safety_engine import ContactSafetyEngine
from apps_rg.engines.hallucination_detector import HallucinationDetector
from apps_rg.engines.skill_score_normalizer import SkillScoreNormalizer

_emit_records_execution_trace("p0", "evidence", "test_apps_integration")
_emit_applies_guardrail("p0", "test_apps_integration", "p0_governance")
_emit_reads_policy_state("p0", "test_apps_integration", "policy_binding")
_emit_snapshots_state("p0", "test_apps_integration", "state_snapshot")
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

_emit_emits_metric_event("test_apps_integration", "p4obs", "metric_1")
_emit_emits_metric_event("test_apps_integration", "p4obs", "metric_2")
_emit_emits_metric_event("test_apps_integration", "p4obs", "metric_3")
_emit_emits_metric_event("test_apps_integration", "p4obs", "metric_4")
_emit_emits_metric_event("test_apps_integration", "p4obs", "metric_5")
_emit_emits_metric_event("test_apps_integration", "p4obs", "metric_6")
_emit_records_incident_event("test_apps_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_apps_integration", "p4obs", "anomaly")
_emit_writes_observability_log("test_apps_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_apps_integration", "p4obs", "mon_state")
_emit_triggers_alert("test_apps_integration", "p4obs", "alert")
_emit_links_incident_trace("test_apps_integration", "p4obs", "trace_link")
_emit_captures_pattern("test_apps_integration", "p3lm", "pattern")
_emit_records_learning_event("test_apps_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_apps_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_apps_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_apps_integration", "p3lm", "routing")
_emit_improves_agent_policy("test_apps_integration", "p3lm", "policy")
_emit_stores_learning_state("test_apps_integration", "p3lm", "state")
_emit_records_execution_trace("test_apps_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_apps_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_apps_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_apps_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_apps_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_apps_integration", "env_read", "p2_env_1")
_emit_reads_environ("test_apps_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_apps_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_apps_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_apps_integration", "context_pull")
_emit_pulls_context("p1", "test_apps_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_apps_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_apps_integration", "uwg_term_2")
_emit_writes_through("p1", "test_apps_integration", "write_through")
_emit_writes_through("p1", "test_apps_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_apps_integration", "safety_validation")
_emit_invokes_eval("p1", "test_apps_integration", "eval_call")
_emit_proposal_commits_routing("p1", "test_apps_integration", "routing_commit")
_emit_escalates_to_human("p1", "test_apps_integration", "human_escalation")
_emit_routes_through("p1", "test_apps_integration", "route_through")
_emit_checks_agent_registry("p1", "test_apps_integration", "agent_registry")
_emit_validates_agent_capability("p1", "test_apps_integration", "capability")
_emit_dispatches_execution_plan("p1", "test_apps_integration", "exec_plan")
_emit_agent_executes_agent("p1", "test_apps_integration", "sub_agent")
_emit_routes_to_agent("p1", "test_apps_integration", "target_agent")
_emit_verifies_policy("p1", "test_apps_integration", "policy_check")
_emit_observes_runtime_state("p1", "test_apps_integration", "runtime_state")
_emit_verifies_boundary("p1", "test_apps_integration", "boundary_check")
_emit_transcripts_response("p1", "test_apps_integration", "transcript")
_emit_hard_fails_untranscripted("p1", "test_apps_integration")
_emit_gated_by_confidence("p1", "test_apps_integration", "confidence_gate")
emit_replay_key("p0", "test_apps_integration")
emit_determinism_digest("p0", "test_apps_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers — minimal context stub so engines can construct without a real ctx
# ---------------------------------------------------------------------------


def _make_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.buffer = MagicMock()
    ctx.buffer.read.return_value = None
    ctx.config = None
    return ctx


def _contact_safety() -> ContactSafetyEngine:
    return ContactSafetyEngine(ctx=_make_ctx())


def _hallucination_detector() -> HallucinationDetector:
    return HallucinationDetector(ctx=_make_ctx())


def _skill_normalizer() -> SkillScoreNormalizer:
    return SkillScoreNormalizer(ctx=_make_ctx())


# ===========================================================================
# 1. ContactSafetyEngine — SSN detection
# ===========================================================================


class TestContactSafetySSNDetection:
    @pytest.mark.governance
    def test_detects_standard_ssn_format(self):
        engine = _contact_safety()
        assert engine._contains_ssn("SSN: 123-45-6789") is True

    @pytest.mark.governance
    def test_no_false_positive_for_phone_number(self):
        engine = _contact_safety()
        assert engine._contains_ssn("555-867-5309") is False

    @pytest.mark.governance
    def test_no_false_positive_for_date(self):
        engine = _contact_safety()
        assert engine._contains_ssn("2026-01-15") is False

    @pytest.mark.governance
    def test_no_detection_in_empty_string(self):
        engine = _contact_safety()
        assert engine._contains_ssn("") is False

    @pytest.mark.governance
    def test_detects_ssn_embedded_in_longer_text(self):
        engine = _contact_safety()
        assert engine._contains_ssn("Patient SSN is 987-65-4321 for records") is True

    @pytest.mark.governance
    def test_no_detection_for_non_ssn_hyphenated_numbers(self):
        engine = _contact_safety()
        # 3-2-5 format but wrong length groups
        assert engine._contains_ssn("12-345-6789") is False

    @pytest.mark.governance
    def test_ssn_detection_does_not_mutate_input(self):
        engine = _contact_safety()
        original = "SSN: 123-45-6789"
        engine._contains_ssn(original)
        assert original == "SSN: 123-45-6789"


# ===========================================================================
# 2. ContactSafetyEngine — credit card detection
# ===========================================================================


class TestContactSafetyCreditCardDetection:
    @pytest.mark.governance
    def test_detects_standard_16_digit_card_with_dashes(self):
        engine = _contact_safety()
        assert engine._contains_credit_card("4111-1111-1111-1111") is True

    @pytest.mark.governance
    def test_detects_16_digit_card_with_spaces(self):
        engine = _contact_safety()
        assert engine._contains_credit_card("4111 1111 1111 1111") is True

    @pytest.mark.governance
    def test_detects_16_digit_card_no_separator(self):
        engine = _contact_safety()
        assert engine._contains_credit_card("4111111111111111") is True

    @pytest.mark.governance
    def test_no_false_positive_for_short_number(self):
        engine = _contact_safety()
        assert engine._contains_credit_card("1234 5678") is False

    @pytest.mark.governance
    def test_no_detection_in_empty_string(self):
        engine = _contact_safety()
        assert engine._contains_credit_card("") is False

    @pytest.mark.governance
    def test_no_false_positive_for_ssn_format(self):
        engine = _contact_safety()
        assert engine._contains_credit_card("123-45-6789") is False


# ===========================================================================
# 3. HallucinationDetector — check_batch
# ===========================================================================


class TestHallucinationDetectorCheckBatch:
    @pytest.mark.governance
    def test_empty_batch_returns_zero_score(self):
        engine = _hallucination_detector()
        result = engine.check_batch([])
        assert result["score"] == 0.0

    @pytest.mark.governance
    def test_clean_text_returns_valid_true(self):
        engine = _hallucination_detector()
        result = engine.check_batch(["Managed a team of 5 engineers successfully."])
        assert result["valid"] is True

    @pytest.mark.governance
    def test_suspicious_100_percent_pattern_adds_to_issues(self):
        engine = _hallucination_detector()
        result = engine.check_batch(["Improved performance by 100%"])
        assert any("Suspicious metric" in issue for issue in result["issues"])

    @pytest.mark.governance
    def test_1000_percent_pattern_flagged_as_suspicious(self):
        engine = _hallucination_detector()
        result = engine.check_batch(["Increased revenue by 1000%"])
        assert len(result["issues"]) > 0

    @pytest.mark.governance
    def test_text_too_short_adds_issue(self):
        engine = _hallucination_detector()
        result = engine.check_batch(["short"])
        assert any("too short" in issue.lower() for issue in result["issues"])

    @pytest.mark.governance
    def test_score_is_average_of_all_texts(self):
        engine = _hallucination_detector()
        # Two clean texts → avg score 1.0
        result = engine.check_batch(
            [
                "Led a development team through an agile transformation.",
                "Architected a distributed microservices platform.",
            ]
        )
        assert result["score"] == 1.0

    @pytest.mark.governance
    def test_valid_threshold_at_07(self):
        engine = _hallucination_detector()
        # 1 suspicious (0.3) + 1 clean (1.0) → avg 0.65 → invalid
        result = engine.check_batch(
            [
                "Improved by 100%",
                "Managed core infrastructure services effectively.",
            ]
        )
        # avg = (0.3 + 1.0) / 2 = 0.65 < 0.7
        assert result["valid"] is False

    @pytest.mark.governance
    def test_result_contains_valid_score_issues_keys(self):
        engine = _hallucination_detector()
        result = engine.check_batch(["A normal enough description of work."])
        assert "valid" in result
        assert "score" in result
        assert "issues" in result

    @pytest.mark.governance
    def test_does_not_mutate_input_list(self):
        engine = _hallucination_detector()
        texts = ["Normal text here is good enough."]
        original = list(texts)
        engine.check_batch(texts)
        assert texts == original


# ===========================================================================
# 4. SkillScoreNormalizer — normalisation math
# ===========================================================================


class TestSkillScoreNormalizer:
    @pytest.mark.governance
    def test_empty_scores_returns_empty_dict(self):
        engine = _skill_normalizer()
        import asyncio

        result = asyncio.run(engine.execute({}))
        assert result == {}

    @pytest.mark.governance
    def test_normalised_scores_all_in_0_to_1_range(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"python": 80.0, "java": 60.0, "sql": 40.0}
        result = asyncio.run(engine.execute(raw))
        for v in result.values():
            assert 0.0 <= v <= 1.0

    @pytest.mark.governance
    def test_max_score_normalises_to_1(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"python": 80.0, "java": 40.0}
        result = asyncio.run(engine.execute(raw))
        assert result["python"] == 1.0

    @pytest.mark.governance
    def test_min_score_normalises_to_0(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"python": 80.0, "java": 40.0}
        result = asyncio.run(engine.execute(raw))
        assert result["java"] == 0.0

    @pytest.mark.governance
    def test_all_equal_scores_normalise_to_1(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"python": 70.0, "java": 70.0, "sql": 70.0}
        result = asyncio.run(engine.execute(raw))
        for v in result.values():
            assert v == 1.0

    @pytest.mark.governance
    def test_single_skill_normalises_to_1(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"python": 55.0}
        result = asyncio.run(engine.execute(raw))
        assert result["python"] == 1.0

    @pytest.mark.governance
    def test_preserves_all_skill_keys(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"a": 1.0, "b": 2.0, "c": 3.0}
        result = asyncio.run(engine.execute(raw))
        assert set(result.keys()) == set(raw.keys())

    @pytest.mark.governance
    def test_normalisation_deterministic_for_same_input_twice(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"x": 10.0, "y": 50.0, "z": 90.0}
        r1 = asyncio.run(engine.execute(raw))
        r2 = asyncio.run(engine.execute(raw))
        assert r1 == r2

    @pytest.mark.governance
    def test_normalisation_does_not_mutate_input(self):
        engine = _skill_normalizer()
        import asyncio

        raw = {"x": 10.0, "y": 90.0}
        original = dict(raw)
        asyncio.run(engine.execute(raw))
        assert raw == original


# ===========================================================================
# 5. HopStageRegistry — registration, lookup, all 9 stages
# ===========================================================================


class TestHopStageRegistry:
    @pytest.mark.governance
    def test_all_nine_stages_registered(self):
        for stage_id in range(1, 10):
            assert get_stage_handler(stage_id) is not None, f"Stage {stage_id} not registered"

    @pytest.mark.governance
    def test_get_stage_handler_returns_none_for_unknown_stage(self):
        assert get_stage_handler(99) is None

    @pytest.mark.governance
    def test_get_stage_handler_returns_none_for_stage_0(self):
        assert get_stage_handler(0) is None

    @pytest.mark.governance
    def test_stage_1_handler_returns_profile_analysis_stage(self):
        handler = get_stage_handler(1)
        result = handler(executor=None, context={"k": "v"})
        assert result["stage"] == 1
        assert result["name"] == "profile_analysis"

    @pytest.mark.governance
    def test_stage_5_handler_returns_generation_stage(self):
        handler = get_stage_handler(5)
        result = handler(executor=None, context={})
        assert result["stage"] == 5
        assert result["name"] == "generation"

    @pytest.mark.governance
    def test_stage_9_handler_returns_integration_stage(self):
        handler = get_stage_handler(9)
        result = handler(executor=None, context={})
        assert result["stage"] == 9
        assert result["name"] == "integration"

    @pytest.mark.governance
    def test_all_stages_return_status_processed(self):
        for stage_id in range(1, 10):
            handler = get_stage_handler(stage_id)
            result = handler(executor=None, context={})
            assert result["status"] == "processed"

    @pytest.mark.governance
    def test_context_passed_through_to_stage_output(self):
        ctx = {"mission": "test-mission"}
        handler = get_stage_handler(3)
        result = handler(executor=None, context=ctx)
        assert result["context"] == ctx

    @pytest.mark.governance
    def test_register_stage_decorator_stores_in_registry(self):
        @register_stage(42)
        def _test_stage(executor, context, **kwargs):
            return {"stage": 42}

        assert get_stage_handler(42) is not None
        # Cleanup
        _REGISTRY.pop(42, None)

    @pytest.mark.governance
    def test_registered_handler_is_callable(self):
        for stage_id in range(1, 10):
            handler = get_stage_handler(stage_id)
            assert callable(handler)
