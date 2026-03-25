"""Behavioral tests for routing_confidence / routing_target fields added to
FeatureBundle (trace_feature_types.py) and TraceFeatureExtractor.

Covers:
- FeatureBundle defaults to 0.0 / '' for new fields
- FeatureBundle accepts explicit routing_confidence and routing_target
- __post_init__ rejects routing_confidence outside [0.0, 1.0]
- stable_hash includes routing_confidence and routing_target
- Two bundles differing only in routing_confidence have different hashes
- TraceFeatureExtractor.extract() populates routing_confidence from signal
- TraceFeatureExtractor.extract() populates routing_target from signal
- TraceFeatureExtractor clamps out-of-range routing_confidence to [0,1]
- TraceFeatureExtractor handles missing routing fields gracefully (defaults)
- to_dict() includes routing_confidence and routing_target keys
"""

from __future__ import annotations

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_trace_feature_routing_fields")
# REMOVED: _emit_applies_guardrail("p0", "test_trace_feature_routing_fields", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_trace_feature_routing_fields", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_trace_feature_routing_fields", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_trace_feature_routing_fields")
# REMOVED: emit_determinism_digest("p0", "test_trace_feature_routing_fields")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_trace_feature_routing_fields", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_trace_feature_routing_fields", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_trace_feature_routing_fields", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_trace_feature_routing_fields", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_trace_feature_routing_fields", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_trace_feature_routing_fields", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_trace_feature_routing_fields", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_trace_feature_routing_fields", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_trace_feature_routing_fields", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_trace_feature_routing_fields", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_trace_feature_routing_fields", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_trace_feature_routing_fields", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_trace_feature_routing_fields", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_trace_feature_routing_fields", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_trace_feature_routing_fields", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_trace_feature_routing_fields", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_trace_feature_routing_fields", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_trace_feature_routing_fields", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_trace_feature_routing_fields", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_trace_feature_routing_fields", "exec_snapshot_link")

pytestmark = pytest.mark.unit

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
from system_learning.engines.trace_feature_extractor import TraceFeatureExtractor
from system_learning.types.trace_feature_types import FeatureBundle

# REMOVED: _emit_emits_metric_event("test_trace_feature_routing_fields", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_trace_feature_routing_fields", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_trace_feature_routing_fields", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_trace_feature_routing_fields", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_trace_feature_routing_fields", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_trace_feature_routing_fields", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_trace_feature_routing_fields", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_trace_feature_routing_fields", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_trace_feature_routing_fields", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_trace_feature_routing_fields", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_trace_feature_routing_fields", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_trace_feature_routing_fields", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_trace_feature_routing_fields", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_trace_feature_routing_fields", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_trace_feature_routing_fields", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_trace_feature_routing_fields", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_trace_feature_routing_fields", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_trace_feature_routing_fields", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_trace_feature_routing_fields", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_trace_feature_routing_fields", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_trace_feature_routing_fields", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_trace_feature_routing_fields", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_trace_feature_routing_fields", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_trace_feature_routing_fields", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_trace_feature_routing_fields", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_trace_feature_routing_fields", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_trace_feature_routing_fields", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_trace_feature_routing_fields", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_trace_feature_routing_fields", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_trace_feature_routing_fields", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_trace_feature_routing_fields", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_trace_feature_routing_fields", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_trace_feature_routing_fields", "write_through")
# REMOVED: _emit_writes_through("p1", "test_trace_feature_routing_fields", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_trace_feature_routing_fields", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_trace_feature_routing_fields", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_trace_feature_routing_fields", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_trace_feature_routing_fields", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_trace_feature_routing_fields", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_trace_feature_routing_fields", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_trace_feature_routing_fields", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_trace_feature_routing_fields", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_trace_feature_routing_fields", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_trace_feature_routing_fields", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_trace_feature_routing_fields", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_trace_feature_routing_fields", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_trace_feature_routing_fields", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_trace_feature_routing_fields", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_trace_feature_routing_fields")
# REMOVED: _emit_gated_by_confidence("p1", "test_trace_feature_routing_fields", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE = {
    "trace_id": "t1",
    "route_selected": "PATH_A",
    "confidence_gate_state": "PASS",
    "retrieval_path": "DIRECT",
    "retrieval_groundedness_score": 0.8,
    "policy_state_accessed": (),
    "guardrails_applied": (),
    "determinism_markers": (),
    "healing_invoked": False,
    "healer_id": None,
    "human_escalation_flag": False,
    "mutation_presence": False,
    "final_outcome_class": "SUCCESS",
    "timestamp_utc": 1000,
    "adg_entity_name": "ADG::Test",
    "adg_relation_ids": (),
}


def _make_bundle(**overrides) -> FeatureBundle:
    kwargs = dict(_BASE)
    kwargs.update(overrides)
    return FeatureBundle(**kwargs)


# ---------------------------------------------------------------------------
# FeatureBundle field defaults
# ---------------------------------------------------------------------------


class TestFeatureBundleRoutingFieldDefaults:
    def test_routing_confidence_defaults_to_zero(self):
        fb = _make_bundle()
        assert fb.routing_confidence == 0.0

    def test_routing_target_defaults_to_empty_string(self):
        fb = _make_bundle()
        assert fb.routing_target == ""

    def test_routing_confidence_explicit_value(self):
        fb = _make_bundle(routing_confidence=0.75)
        assert fb.routing_confidence == 0.75

    def test_routing_target_explicit_value(self):
        fb = _make_bundle(routing_target="code_reviewer")
        assert fb.routing_target == "code_reviewer"


# ---------------------------------------------------------------------------
# FeatureBundle __post_init__ validation
# ---------------------------------------------------------------------------


class TestFeatureBundleRoutingFieldValidation:
    def test_routing_confidence_zero_valid(self):
        fb = _make_bundle(routing_confidence=0.0)
        assert fb.routing_confidence == 0.0

    def test_routing_confidence_one_valid(self):
        fb = _make_bundle(routing_confidence=1.0)
        assert fb.routing_confidence == 1.0

    def test_routing_confidence_above_one_raises(self):
        with pytest.raises(ValueError, match="routing_confidence"):
            _make_bundle(routing_confidence=1.001)

    def test_routing_confidence_below_zero_raises(self):
        with pytest.raises(ValueError, match="routing_confidence"):
            _make_bundle(routing_confidence=-0.001)

    def test_influence_class_still_enforced(self):
        with pytest.raises(ValueError, match="C0_INFORMATIONAL"):
            _make_bundle(influence_class="C1_MUTATION")


# ---------------------------------------------------------------------------
# FeatureBundle stable_hash includes routing fields
# ---------------------------------------------------------------------------


class TestFeatureBundleHashIncludesRoutingFields:
    def test_different_routing_confidence_different_hash(self):
        fb1 = _make_bundle(routing_confidence=0.5)
        fb2 = _make_bundle(routing_confidence=0.6)
        assert fb1.stable_hash() != fb2.stable_hash()

    def test_different_routing_target_different_hash(self):
        fb1 = _make_bundle(routing_target="resume_writer")
        fb2 = _make_bundle(routing_target="code_reviewer")
        assert fb1.stable_hash() != fb2.stable_hash()

    def test_same_fields_same_hash(self):
        fb1 = _make_bundle(routing_confidence=0.77, routing_target="rg")
        fb2 = _make_bundle(routing_confidence=0.77, routing_target="rg")
        assert fb1.stable_hash() == fb2.stable_hash()

    def test_to_dict_includes_routing_confidence(self):
        fb = _make_bundle(routing_confidence=0.55)
        d = fb.to_dict()
        assert "routing_confidence" in d
        assert abs(d["routing_confidence"] - 0.55) < 1e-6

    def test_to_dict_includes_routing_target(self):
        fb = _make_bundle(routing_target="rfp_agent")
        d = fb.to_dict()
        assert "routing_target" in d
        assert d["routing_target"] == "rfp_agent"

    def test_routing_confidence_rounded_to_6dp_in_dict(self):
        fb = _make_bundle(routing_confidence=0.123456789)
        d = fb.to_dict()
        assert d["routing_confidence"] == round(0.123456789, 6)


# ---------------------------------------------------------------------------
# TraceFeatureExtractor populates routing fields
# ---------------------------------------------------------------------------


class TestTraceFeatureExtractorRoutingFields:
    def setup_method(self):
        self.extractor = TraceFeatureExtractor()

    def _extract(self, signal: dict) -> FeatureBundle:
        return self.extractor.extract("trace-x", signal, timestamp_utc=42)

    def test_routing_confidence_populated_from_signal(self):
        fb = self._extract({"success": True, "routing_confidence": 0.88})
        assert abs(fb.routing_confidence - 0.88) < 1e-6

    def test_routing_target_populated_from_signal(self):
        fb = self._extract({"success": True, "routing_target": "resume_writer"})
        assert fb.routing_target == "resume_writer"

    def test_routing_confidence_defaults_when_absent(self):
        fb = self._extract({"success": True})
        assert fb.routing_confidence == 0.0

    def test_routing_target_defaults_when_absent(self):
        fb = self._extract({"success": True})
        assert fb.routing_target == ""

    def test_routing_confidence_clamped_above_one(self):
        fb = self._extract({"routing_confidence": 1.5})
        assert fb.routing_confidence == 1.0

    def test_routing_confidence_clamped_below_zero(self):
        fb = self._extract({"routing_confidence": -0.5})
        assert fb.routing_confidence == 0.0

    def test_routing_confidence_invalid_type_defaults_to_zero(self):
        fb = self._extract({"routing_confidence": "not_a_float"})
        assert fb.routing_confidence == 0.0

    def test_routing_confidence_none_defaults_to_zero(self):
        fb = self._extract({"routing_confidence": None})
        assert fb.routing_confidence == 0.0

    def test_routing_target_none_defaults_to_empty(self):
        fb = self._extract({"routing_target": None})
        assert fb.routing_target == ""

    def test_both_fields_set_simultaneously(self):
        fb = self._extract({"routing_confidence": 0.65, "routing_target": "eval_agent"})
        assert abs(fb.routing_confidence - 0.65) < 1e-6
        assert fb.routing_target == "eval_agent"

    def test_stable_hash_deterministic_with_routing_fields(self):
        sig = {"success": True, "routing_confidence": 0.72, "routing_target": "rg"}
        fb1 = self._extract(sig)
        fb2 = self._extract(sig)
        assert fb1.stable_hash() == fb2.stable_hash()
