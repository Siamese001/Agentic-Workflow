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

_emit_records_execution_trace("p0", "evidence", "test_trace_feature_routing_fields")
_emit_applies_guardrail("p0", "test_trace_feature_routing_fields", "p0_governance")
_emit_reads_policy_state("p0", "test_trace_feature_routing_fields", "policy_binding")
_emit_snapshots_state("p0", "test_trace_feature_routing_fields", "state_snapshot")
emit_replay_key("p0", "test_trace_feature_routing_fields")
emit_determinism_digest("p0", "test_trace_feature_routing_fields")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_trace_feature_routing_fields", "execution_auth")
_emit_validates_capability("p2", "test_trace_feature_routing_fields", "capability_check")
_emit_routes_to_capability("p2", "test_trace_feature_routing_fields", "capability_route")
_emit_writes_via_uwg("p2", "test_trace_feature_routing_fields", "uwg_write")
_emit_blocks_direct_write("p2", "test_trace_feature_routing_fields", "direct_write_block")
_emit_records_tool_invocation("p2", "test_trace_feature_routing_fields", "tool_invocation")
_emit_captures_execution_output("p2", "test_trace_feature_routing_fields", "exec_output")
_emit_dispatches_agent("p3", "test_trace_feature_routing_fields", "agent_dispatch")
_emit_coordinates_agents("p3", "test_trace_feature_routing_fields", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_trace_feature_routing_fields", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_trace_feature_routing_fields", "healing_outcome")
_emit_escalates_failure("p3", "test_trace_feature_routing_fields", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_trace_feature_routing_fields", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_trace_feature_routing_fields", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_trace_feature_routing_fields", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_trace_feature_routing_fields", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_trace_feature_routing_fields", "eval_metric")
_emit_stores_embedding("p4", "test_trace_feature_routing_fields", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_trace_feature_routing_fields", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_trace_feature_routing_fields", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from system_learning.engines.trace_feature_extractor import TraceFeatureExtractor
from system_learning.types.trace_feature_types import FeatureBundle

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
