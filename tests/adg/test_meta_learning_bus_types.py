"""Tests for TraceFeatureTypes and OptimizationTypes in the meta-learning bus pipeline.

Covers:
  - TraceFeatureTypes: frozen invariants, validation, hashing
  - OptimizationTypes: frozen invariants, validation, hashing
"""

from __future__ import annotations

import hashlib

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_bus_types")
_emit_applies_guardrail("p0", "test_meta_learning_bus_types", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_bus_types", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_bus_types", "state_snapshot")
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_meta_learning_bus_types", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_bus_types", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_bus_types", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_bus_types", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_bus_types", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_bus_types", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_bus_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_bus_types", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_bus_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_bus_types", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_bus_types", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_bus_types", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_bus_types", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_bus_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_bus_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_bus_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_bus_types", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_bus_types", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_bus_types", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_bus_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_bus_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_bus_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_bus_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_bus_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_bus_types", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_bus_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_bus_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_bus_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_meta_learning_bus_types", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_bus_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_types", "uwg_term_2")
_emit_writes_through("p1", "test_meta_learning_bus_types", "write_through")
_emit_writes_through("p1", "test_meta_learning_bus_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_meta_learning_bus_types", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_bus_types", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_bus_types", "routing_commit")
_emit_escalates_to_human("p1", "test_meta_learning_bus_types", "human_escalation")
_emit_routes_through("p1", "test_meta_learning_bus_types", "route_through")
_emit_checks_agent_registry("p1", "test_meta_learning_bus_types", "agent_registry")
_emit_validates_agent_capability("p1", "test_meta_learning_bus_types", "capability")
_emit_dispatches_execution_plan("p1", "test_meta_learning_bus_types", "exec_plan")
_emit_agent_executes_agent("p1", "test_meta_learning_bus_types", "sub_agent")
_emit_routes_to_agent("p1", "test_meta_learning_bus_types", "target_agent")
_emit_verifies_policy("p1", "test_meta_learning_bus_types", "policy_check")
_emit_observes_runtime_state("p1", "test_meta_learning_bus_types", "runtime_state")
_emit_verifies_boundary("p1", "test_meta_learning_bus_types", "boundary_check")
_emit_transcripts_response("p1", "test_meta_learning_bus_types", "transcript")
_emit_hard_fails_untranscripted("p1", "test_meta_learning_bus_types")
_emit_gated_by_confidence("p1", "test_meta_learning_bus_types", "confidence_gate")
emit_replay_key("p0", "test_meta_learning_bus_types")
emit_determinism_digest("p0", "test_meta_learning_bus_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_learning_bus_types", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_bus_types", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_bus_types", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_bus_types", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_bus_types", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_bus_types", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_bus_types", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_bus_types", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_bus_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_bus_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_bus_types", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_bus_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_bus_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_bus_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_bus_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_bus_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_bus_types", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_bus_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_bus_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_bus_types", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_TS = 1_700_000_000
_HASH64 = "a" * 64  # valid-looking SHA-256 hexdigest for tests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ===========================================================================
# TestTraceFeatureTypes
# ===========================================================================


class TestFeatureBundle:
    def _make(self, **kw):
        from system_learning.types.trace_feature_types import FeatureBundle

        defaults = {
            "trace_id": "tr-001",
            "route_selected": "PATH_A",
            "confidence_gate_state": "PASS",
            "retrieval_path": "RAG_BGE",
            "retrieval_groundedness_score": 0.8,
            "policy_state_accessed": (),
            "guardrails_applied": (),
            "determinism_markers": (),
            "healing_invoked": False,
            "healer_id": None,
            "human_escalation_flag": False,
            "mutation_presence": False,
            "final_outcome_class": "SUCCESS",
            "timestamp_utc": _TS,
            "adg_entity_name": "ADG::Module::foo",
            "adg_relation_ids": (),
        }
        defaults.update(kw)
        return FeatureBundle(**defaults)

    def test_frozen(self):
        b = self._make()
        with pytest.raises((AttributeError, TypeError)):
            b.route_selected = "NEW"  # type: ignore[misc]

    def test_invalid_outcome_class_raises(self):
        with pytest.raises(ValueError, match="final_outcome_class"):
            self._make(final_outcome_class="GARBAGE")

    def test_groundedness_out_of_range_raises(self):
        with pytest.raises(ValueError, match="retrieval_groundedness_score"):
            self._make(retrieval_groundedness_score=1.5)

    def test_influence_class_must_be_c0(self):
        with pytest.raises(ValueError, match="C0_INFORMATIONAL"):
            self._make(influence_class="C1_ROUTING")

    def test_stable_hash_deterministic(self):
        b = self._make()
        assert b.stable_hash() == b.stable_hash()

    def test_stable_hash_changes_with_outcome(self):
        b1 = self._make(final_outcome_class="SUCCESS")
        b2 = self._make(final_outcome_class="SAFE_FAILURE")
        assert b1.stable_hash() != b2.stable_hash()

    def test_to_json_is_string(self):
        b = self._make()
        j = b.to_json()
        assert isinstance(j, str)
        assert '"trace_id"' in j

    def test_all_outcome_classes_valid(self):
        for oc in (
            "SUCCESS",
            "SAFE_FAILURE",
            "HEALED_SUCCESS",
            "ROLLBACK",
            "HUMAN_OVERRIDE",
            "REPLAY_FAILURE",
            "UNKNOWN",
        ):
            b = self._make(final_outcome_class=oc)
            assert b.final_outcome_class == oc

    def test_adg_relation_ids_preserved_in_canonical_dict(self):
        b = self._make(adg_relation_ids=("rel-z", "rel-a"))
        d = b.to_dict()
        # canonical dict sorts them
        assert d["adg_relation_ids"] == ["rel-a", "rel-z"]


class TestTraceFeatureRecord:
    def _make_bundle(self, trace_id="tr-001", outcome="SUCCESS"):
        from system_learning.types.trace_feature_types import FeatureBundle

        return FeatureBundle(
            trace_id=trace_id,
            route_selected="PATH_A",
            confidence_gate_state="PASS",
            retrieval_path="RAG_BGE",
            retrieval_groundedness_score=0.75,
            policy_state_accessed=("ph1",),
            guardrails_applied=("g1",),
            determinism_markers=("dm1",),
            healing_invoked=False,
            healer_id=None,
            human_escalation_flag=False,
            mutation_presence=False,
            final_outcome_class=outcome,
            timestamp_utc=_TS,
            adg_entity_name="ADG::Module::bar",
            adg_relation_ids=("r1", "r2"),
        )

    def test_from_bundle_sets_record_id(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord

        bundle = self._make_bundle()
        record = TraceFeatureRecord.from_bundle(bundle)
        assert record.record_id == bundle.stable_hash()

    def test_from_bundle_maps_fields(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord

        bundle = self._make_bundle()
        record = TraceFeatureRecord.from_bundle(bundle)
        assert record.trace_id == bundle.trace_id
        assert record.route == bundle.route_selected
        assert record.retrieval_pattern == bundle.retrieval_path
        assert record.outcome_class == bundle.final_outcome_class
        assert record.adg_node_id == bundle.adg_entity_name

    def test_stable_hash_deterministic(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord

        bundle = self._make_bundle()
        r = TraceFeatureRecord.from_bundle(bundle)
        assert r.stable_hash() == r.stable_hash()

    def test_invalid_outcome_raises(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord

        with pytest.raises(ValueError, match="outcome_class"):
            TraceFeatureRecord(
                record_id=_HASH64,
                trace_id="t",
                route="R",
                retrieval_pattern="P",
                retrieval_groundedness=0.5,
                policy_edges=(),
                guardrail_edges=(),
                determinism_signals=(),
                healer_used=None,
                hitl_escalation=False,
                outcome_class="BOGUS",
                adg_node_id="ADG::X",
                adg_relation_ids=(),
                feature_bundle_hash=_HASH64,
                timestamp_utc=_TS,
            )

    def test_empty_trace_id_raises(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord

        with pytest.raises(ValueError, match="trace_id"):
            TraceFeatureRecord(
                record_id=_HASH64,
                trace_id="",
                route="R",
                retrieval_pattern="P",
                retrieval_groundedness=0.5,
                policy_edges=(),
                guardrail_edges=(),
                determinism_signals=(),
                healer_used=None,
                hitl_escalation=False,
                outcome_class="SUCCESS",
                adg_node_id="ADG::X",
                adg_relation_ids=(),
                feature_bundle_hash=_HASH64,
                timestamp_utc=_TS,
            )


class TestRCACluster:
    def _make(self, **kw):
        from system_learning.types.trace_feature_types import RCACluster

        defaults = {
            "cluster_id": _HASH64,
            "failure_pattern": "LOW_GROUNDEDNESS",
            "dominant_route": "PATH_B",
            "dominant_guardrail": None,
            "dominant_retrieval_pattern": "RAG_BGE",
            "affected_agents": ("ADG::Module::alpha",),
            "member_trace_ids": ("tr-001", "tr-002"),
            "member_count": 2,
            "outcome_distribution": (("SAFE_FAILURE", 2),),
            "avg_groundedness": 0.3,
            "hitl_escalation_rate": 0.0,
            "healer_invocation_rate": 0.0,
            "adg_cluster_node": "ADG::RCACluster::LOW_GROUNDEDNESS::abc123",
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return RCACluster(**defaults)

    def test_frozen(self):
        c = self._make()
        with pytest.raises((AttributeError, TypeError)):
            c.failure_pattern = "NEW"  # type: ignore[misc]

    def test_empty_failure_pattern_raises(self):
        with pytest.raises(ValueError, match="failure_pattern"):
            self._make(failure_pattern="")

    def test_zero_member_count_raises(self):
        with pytest.raises(ValueError, match="member_count"):
            self._make(member_count=0)

    def test_stable_hash_deterministic(self):
        c = self._make()
        assert c.stable_hash() == c.stable_hash()

    def test_stable_hash_differs_by_cluster_id(self):
        c1 = self._make(cluster_id=_HASH64)
        c2 = self._make(cluster_id="b" * 64)
        assert c1.stable_hash() != c2.stable_hash()

    def test_to_dict_sorts_affected_agents(self):
        c = self._make(affected_agents=("ADG::Z", "ADG::A"))
        d = c.to_dict()
        assert d["affected_agents"] == ["ADG::A", "ADG::Z"]


class TestFailurePattern:
    def _make(self, **kw):
        from system_learning.types.trace_feature_types import FailurePattern

        defaults = {
            "pattern_id": _HASH64,
            "source_type": "VIOLATION",
            "signature": "AuthorityViolation",
            "affected_component": "ADG::Module::guard",
            "occurrence_count": 3,
            "evidence_hash": _HASH64,
            "cluster_id": None,
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return FailurePattern(**defaults)

    def test_invalid_source_type_raises(self):
        with pytest.raises(ValueError, match="source_type"):
            self._make(source_type="BOGUS")

    def test_zero_occurrence_count_raises(self):
        with pytest.raises(ValueError, match="occurrence_count"):
            self._make(occurrence_count=0)

    def test_all_source_types_valid(self):
        for st in (
            "VIOLATION",
            "ANTIPATTERN",
            "DRIFT_ALERT",
            "REPLAY_FAILURE",
            "LOW_GROUNDEDNESS",
            "OVER_ESCALATION",
        ):
            fp = self._make(source_type=st)
            assert fp.source_type == st

    def test_stable_hash_deterministic(self):
        fp = self._make()
        assert fp.stable_hash() == fp.stable_hash()


# ===========================================================================
# TestOptimizationTypes
# ===========================================================================


class TestOptimizationProposal:
    def _make(self, **kw):
        from system_learning.types.optimization_types import OptimizationProposal

        defaults = {
            "proposal_id": _HASH64,
            "cluster_id": _HASH64,
            "proposed_change_type": "ROUTING_RULE_ADJUSTMENT",
            "affected_component": "ADG::Module::router",
            "expected_outcome": "Improve routing accuracy",
            "risk_class": "LOW",
            "change_spec": (("dominant_route", "PATH_A"),),
            "evidence_bundle_hashes": (_HASH64,),
            "reward_score": None,
            "policy_hash": None,
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return OptimizationProposal(**defaults)

    def test_frozen(self):
        p = self._make()
        with pytest.raises((AttributeError, TypeError)):
            p.risk_class = "HIGH"  # type: ignore[misc]

    def test_invalid_change_type_raises(self):
        with pytest.raises(ValueError, match="proposed_change_type"):
            self._make(proposed_change_type="TELEPORT")

    def test_invalid_risk_class_raises(self):
        with pytest.raises(ValueError, match="risk_class"):
            self._make(risk_class="EXTREME")

    def test_reward_score_out_of_range_raises(self):
        with pytest.raises(ValueError, match="reward_score"):
            self._make(reward_score=1.5)

    def test_stable_hash_deterministic(self):
        p = self._make()
        assert p.stable_hash() == p.stable_hash()

    def test_all_change_types_valid(self):
        for ct in (
            "ROUTING_RULE_ADJUSTMENT",
            "CONFIDENCE_THRESHOLD_UPDATE",
            "RETRIEVAL_RANKING_ADJUSTMENT",
            "EMBEDDING_CORPUS_EXPANSION",
            "GUARDRAIL_REFINEMENT",
            "HEALER_ROUTING_IMPROVEMENT",
            "PROMPT_TUNING",
            "DPO_DATASET_GENERATION",
        ):
            p = self._make(proposed_change_type=ct)
            assert p.proposed_change_type == ct


class TestValidationResult:
    def _make(self, **kw):
        from system_learning.types.optimization_types import ValidationResult

        defaults = {
            "result_id": _HASH64,
            "proposal_id": _HASH64,
            "validation_pass": True,
            "replay_safe": True,
            "policy_safe": True,
            "guardrail_safe": True,
            "determinism_verified": True,
            "regression_risk": "NONE",
            "gate_results": (("REPLAY_VALIDATION", True),),
            "denial_reasons": (),
            "policy_hash": None,
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return ValidationResult(**defaults)

    def test_pass_with_denial_reasons_raises(self):
        with pytest.raises(ValueError, match="denial_reasons"):
            self._make(validation_pass=True, denial_reasons=("GATE_FAIL",))

    def test_fail_without_denial_reasons_raises(self):
        with pytest.raises(ValueError, match="denial_reasons"):
            self._make(validation_pass=False, denial_reasons=())

    def test_invalid_regression_risk_raises(self):
        with pytest.raises(ValueError, match="regression_risk"):
            self._make(regression_risk="CATASTROPHIC")

    def test_stable_hash_deterministic(self):
        r = self._make()
        assert r.stable_hash() == r.stable_hash()

    def test_failing_result_consistent(self):
        r = self._make(
            validation_pass=False,
            denial_reasons=("REPLAY_VALIDATION",),
            gate_results=(("REPLAY_VALIDATION", False),),
            regression_risk="HIGH",
        )
        assert not r.validation_pass
        assert "REPLAY_VALIDATION" in r.denial_reasons


class TestOptimizationCommit:
    def _make(self, **kw):
        from system_learning.types.optimization_types import OptimizationCommit

        defaults = {
            "commit_id": _HASH64,
            "proposal_id": _HASH64,
            "validation_result_id": _HASH64,
            "affected_rules": ("rule:ROUTING_RULE_ADJUSTMENT",),
            "affected_routes": ("PATH_A",),
            "affected_retrieval_policy": (),
            "affected_components": ("ADG::Module::router",),
            "policy_hash": None,
            "change_type": "ROUTING_RULE_ADJUSTMENT",
            "risk_class": "LOW",
            "adg_relation": "proposal_commits_optimization",
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return OptimizationCommit(**defaults)

    def test_wrong_adg_relation_raises(self):
        with pytest.raises(ValueError, match="adg_relation"):
            self._make(adg_relation="wrong_relation")

    def test_frozen(self):
        c = self._make()
        with pytest.raises((AttributeError, TypeError)):
            c.commit_id = "new"  # type: ignore[misc]

    def test_stable_hash_deterministic(self):
        c = self._make()
        assert c.stable_hash() == c.stable_hash()

    def test_canonical_dict_sorts_components(self):
        c = self._make(affected_components=("ADG::Z", "ADG::A"))
        d = c.to_dict()
        assert d["affected_components"] == ["ADG::A", "ADG::Z"]


class TestGovernanceRewardSignal:
    def _make(self, **kw):
        from system_learning.types.optimization_types import GovernanceRewardSignal

        defaults = {
            "signal_id": _HASH64,
            "trace_id": "tr-001",
            "groundedness_score": 0.9,
            "policy_compliance": 0.95,
            "replay_stability": 1.0,
            "guardrail_cleanliness": 1.0,
            "mutation_correctness": 1.0,
            "human_approval": None,
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return GovernanceRewardSignal(**defaults)

    def test_out_of_range_groundedness_raises(self):
        with pytest.raises(ValueError, match="groundedness_score"):
            self._make(groundedness_score=1.1)

    def test_all_scores_in_range(self):
        s = self._make()
        for attr in (
            "groundedness_score",
            "policy_compliance",
            "replay_stability",
            "guardrail_cleanliness",
            "mutation_correctness",
        ):
            val = getattr(s, attr)
            assert 0.0 <= val <= 1.0

    def test_stable_hash_deterministic(self):
        s = self._make()
        assert s.stable_hash() == s.stable_hash()


class TestGovernanceRewardScore:
    def _make(self, **kw):
        from system_learning.types.optimization_types import GovernanceRewardScore

        defaults = {
            "score_id": _HASH64,
            "proposal_id": _HASH64,
            "aggregate_score": 0.85,
            "groundedness_contrib": 0.225,
            "policy_compliance_contrib": 0.2375,
            "replay_stability_contrib": 0.2,
            "guardrail_cleanliness_contrib": 0.15,
            "mutation_correctness_contrib": 0.15,
            "human_approval_rate": 1.0,
            "invariant_preserved": True,
            "signal_count": 5,
            "timestamp_utc": _TS,
        }
        defaults.update(kw)
        return GovernanceRewardScore(**defaults)

    def test_aggregate_out_of_range_raises(self):
        with pytest.raises(ValueError, match="aggregate_score"):
            self._make(aggregate_score=-0.1)

    def test_negative_signal_count_raises(self):
        with pytest.raises(ValueError, match="signal_count"):
            self._make(signal_count=-1)

    def test_stable_hash_deterministic(self):
        s = self._make()
        assert s.stable_hash() == s.stable_hash()
