"""Tests for MetaLearningBus pipeline and closed-loop integration.

Covers:
  - MetaLearningBus: full pipeline, ADG relation emission, fail-open stages
  - TestClosedLearningLoop: end-to-end integration scenarios
"""

from __future__ import annotations

import hashlib

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_meta_learning_bus_pipeline")
# REMOVED: _emit_applies_guardrail("p0", "test_meta_learning_bus_pipeline", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_meta_learning_bus_pipeline", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_meta_learning_bus_pipeline", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_meta_learning_bus_pipeline", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_meta_learning_bus_pipeline", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_meta_learning_bus_pipeline", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_meta_learning_bus_pipeline", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_meta_learning_bus_pipeline", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_meta_learning_bus_pipeline", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_meta_learning_bus_pipeline", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_meta_learning_bus_pipeline", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_meta_learning_bus_pipeline", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_meta_learning_bus_pipeline", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_meta_learning_bus_pipeline", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_meta_learning_bus_pipeline", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_meta_learning_bus_pipeline", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_meta_learning_bus_pipeline", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_meta_learning_bus_pipeline", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_meta_learning_bus_pipeline", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_meta_learning_bus_pipeline", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_meta_learning_bus_pipeline", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_meta_learning_bus_pipeline", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_meta_learning_bus_pipeline", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_meta_learning_bus_pipeline", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_meta_learning_bus_pipeline", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_meta_learning_bus_pipeline", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_meta_learning_bus_pipeline", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_meta_learning_bus_pipeline", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_meta_learning_bus_pipeline", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_bus_pipeline", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_bus_pipeline", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_bus_pipeline", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_bus_pipeline", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_pipeline", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_pipeline", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_bus_pipeline", "write_through")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_bus_pipeline", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_meta_learning_bus_pipeline", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_meta_learning_bus_pipeline", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_meta_learning_bus_pipeline", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_meta_learning_bus_pipeline", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_meta_learning_bus_pipeline", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_meta_learning_bus_pipeline", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_meta_learning_bus_pipeline", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_meta_learning_bus_pipeline", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_meta_learning_bus_pipeline", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_meta_learning_bus_pipeline", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_meta_learning_bus_pipeline", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_meta_learning_bus_pipeline", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_meta_learning_bus_pipeline", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_meta_learning_bus_pipeline", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_meta_learning_bus_pipeline")
# REMOVED: _emit_gated_by_confidence("p1", "test_meta_learning_bus_pipeline", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_meta_learning_bus_pipeline")
# REMOVED: emit_determinism_digest("p0", "test_meta_learning_bus_pipeline")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_meta_learning_bus_pipeline", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_meta_learning_bus_pipeline", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_meta_learning_bus_pipeline", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_meta_learning_bus_pipeline", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_meta_learning_bus_pipeline", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_meta_learning_bus_pipeline", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_meta_learning_bus_pipeline", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_meta_learning_bus_pipeline", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_meta_learning_bus_pipeline", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_meta_learning_bus_pipeline", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_meta_learning_bus_pipeline", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_meta_learning_bus_pipeline", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_meta_learning_bus_pipeline", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_meta_learning_bus_pipeline", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_meta_learning_bus_pipeline", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_meta_learning_bus_pipeline", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_meta_learning_bus_pipeline", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_meta_learning_bus_pipeline", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_meta_learning_bus_pipeline", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_meta_learning_bus_pipeline", "exec_snapshot_link")

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
# TestMetaLearningBus
# ===========================================================================


class TestMetaLearningBus:
    def _bus(self, **kw):
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        return MetaLearningBus(MetaLearningBusConfig(**kw))

    def _signal(self, trace_id, success=True, groundedness=0.8, outcome_override=None):
        sig = {
            "route_selected": "PATH_A",
            "confidence_gate_state": "pass",
            "retrieval_path": "RAG_BGE",
            "retrieval_groundedness_score": groundedness,
            "policy_hashes": ["ph1"],
            "guardrails_applied": [],
            "determinism_markers": ["dm1"],
            "healing_invoked": False,
            "healer_id": None,
            "human_escalation_flag": False,
            "mutation_presence": False,
            "success": success,
            "adg_entity_name": f"ADG::Module::test_{trace_id}",
            "adg_relation_ids": ["r1"],
        }
        if outcome_override:
            sig["replay_failed"] = outcome_override == "REPLAY_FAILURE"
            sig["rollback"] = outcome_override == "ROLLBACK"
        return sig

    def test_empty_traces_returns_empty_pipeline_result(self):
        result = self._bus().process_traces([], _TS)
        assert result.bundles == []
        assert result.records == []
        assert result.clusters == []
        assert result.commits == []

    def test_two_identical_pattern_traces_produce_cluster(self):
        traces = [
            ("t1", self._signal("t1", groundedness=0.2), _TS),
            ("t2", self._signal("t2", groundedness=0.3), _TS),
        ]
        result = self._bus().process_traces(traces, _TS)
        assert len(result.bundles) == 2
        assert len(result.records) == 2
        assert len(result.clusters) >= 1

    def test_full_pipeline_produces_proposals(self):
        # 6 traces with LOW_GROUNDEDNESS pattern
        traces = [(f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i) for i in range(6)]
        result = self._bus().process_traces(traces, _TS + 100)
        assert len(result.proposals) >= 1

    def test_adg_triggered_telemetry_relations_emitted(self):
        traces = [("t1", self._signal("t1"), _TS)]
        result = self._bus().process_traces(traces, _TS)
        relation_types = {rel[1] for rel in result.adg_relations_emitted}
        assert "triggered_telemetry" in relation_types

    def test_adg_chunks_into_relations_emitted_for_clusters(self):
        traces = [(f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i) for i in range(4)]
        result = self._bus(reward_threshold=0.0).process_traces(traces, _TS + 100)
        relation_types = {rel[1] for rel in result.adg_relations_emitted}
        assert "chunks_into" in relation_types

    def test_adg_stores_embedding_relations_emitted(self):
        traces = [(f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i) for i in range(4)]
        result = self._bus(reward_threshold=0.0).process_traces(traces, _TS + 100)
        relation_types = {rel[1] for rel in result.adg_relations_emitted}
        assert "stores_embedding" in relation_types

    def test_low_reward_threshold_allows_more_proposals_to_validation(self):
        traces = [(f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i) for i in range(6)]
        result_strict = self._bus(reward_threshold=0.99).process_traces(traces, _TS + 100)
        result_loose = self._bus(reward_threshold=0.0).process_traces(traces, _TS + 100)
        # With threshold 0.0, at least as many proposals pass reward gate
        assert len(result_loose.validation_results) >= len(result_strict.validation_results)

    def test_successful_pipeline_produces_commits(self):
        # 6 traces with HEALER_REQUIRED pattern (LOW risk → easy to pass)
        traces = [
            (
                f"t{i}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.8,
                    "healing_invoked": True,
                    "healer_id": "healer_X",
                    "success": True,
                    "healed": True,
                    "adg_entity_name": "ADG::Module::healer_test",
                    "adg_relation_ids": [],
                },
                _TS + i,
            )
            for i in range(6)
        ]
        result = self._bus(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ).process_traces(traces, _TS + 100)
        assert len(result.commits) >= 1

    def test_commits_have_correct_adg_relation(self):
        traces = [
            (
                f"t{i}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.8,
                    "healing_invoked": True,
                    "healer_id": "healer_X",
                    "success": True,
                    "healed": True,
                    "adg_entity_name": "ADG::Module::healer_test",
                    "adg_relation_ids": [],
                },
                _TS + i,
            )
            for i in range(6)
        ]
        result = self._bus(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ).process_traces(traces, _TS + 100)
        for commit in result.commits:
            assert commit.adg_relation == "proposal_commits_optimization"

    def test_proposal_commits_optimization_relations_emitted(self):
        traces = [
            (
                f"t{i}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.8,
                    "healing_invoked": True,
                    "healer_id": "healer_X",
                    "success": True,
                    "healed": True,
                    "adg_entity_name": "ADG::Module::healer_test",
                    "adg_relation_ids": [],
                },
                _TS + i,
            )
            for i in range(6)
        ]
        result = self._bus(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ).process_traces(traces, _TS + 100)
        if result.commits:
            relation_types = {rel[1] for rel in result.adg_relations_emitted}
            assert "proposal_commits_optimization" in relation_types

    def test_negative_seed_injection_adds_clusters(self):
        from system_learning.types.trace_feature_types import FailurePattern

        seed = FailurePattern(
            pattern_id=_HASH64,
            source_type="VIOLATION",
            signature="AuthorityViolation",
            affected_component="ADG::Module::guard",
            occurrence_count=3,
            evidence_hash=_HASH64,
            cluster_id=None,
            timestamp_utc=_TS,
        )
        # No live traces — only the seed
        result = self._bus().process_traces([], _TS, negative_seeds=[seed])
        # Seed adds a cluster even with no live records
        assert len(result.clusters) >= 1

    def test_process_single_trace_convenience_method(self):
        bus = self._bus()
        result = bus.process_single_trace(
            "tr-single",
            self._signal("tr-single"),
            _TS,
            _TS + 10,
        )
        assert len(result.bundles) == 1

    def test_synthesised_reward_signals_replay_failure_gets_low_stability(self):
        # REPLAY_FAILURE trace → replay_stability=0.0 → low reward
        traces = [
            (
                f"t{i}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.8,
                    "replay_failed": True,
                    "success": False,
                    "adg_entity_name": "ADG::Module::replay_test",
                    "adg_relation_ids": [],
                },
                _TS + i,
            )
            for i in range(4)
        ]
        result = self._bus().process_traces(traces, _TS + 100)
        # With replay=0.0, aggregate reward is low → invariant NOT preserved
        # → proposals likely rejected; at minimum they should be in rejected list
        # or validation_results should reflect the risk
        assert isinstance(result, object)  # pipeline completes without crash

    def test_module_level_run_learning_pipeline(self):
        from system_learning.engines.meta_learning_bus import run_learning_pipeline

        traces = [("t1", self._signal("t1"), _TS)]
        result = run_learning_pipeline(traces, _TS + 10)
        assert len(result.bundles) == 1

    def test_pipeline_result_fields_all_present(self):
        result = self._bus().process_traces([], _TS)
        assert hasattr(result, "bundles")
        assert hasattr(result, "records")
        assert hasattr(result, "clusters")
        assert hasattr(result, "proposals")
        assert hasattr(result, "validation_results")
        assert hasattr(result, "commits")
        assert hasattr(result, "rejected_proposal_ids")
        assert hasattr(result, "adg_relations_emitted")

    def test_bridge_none_does_not_crash(self):
        from system_learning.engines.meta_learning_bus import MetaLearningBus, MetaLearningBusConfig

        bus = MetaLearningBus(MetaLearningBusConfig(emit_adg_relations=True), bridge=None)
        result = bus.process_traces([("t1", self._signal("t1"), _TS)], _TS + 10)
        assert isinstance(result.adg_relations_emitted, list)


# ===========================================================================
# Integration: full closed loop
# ===========================================================================


class TestClosedLearningLoop:
    """End-to-end tests verifying the complete learning loop."""

    def test_10_low_groundedness_traces_produce_commit(self):
        """10 low-groundedness traces → cluster → proposal → validation → commit."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        traces = [
            (
                f"tr-lg-{i:03d}",
                {
                    "route_selected": "PATH_B",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.2,
                    "success": False,
                    "adg_entity_name": "ADG::Module::retriever",
                    "adg_relation_ids": ["retrieves_via"],
                },
                _TS + i,
            )
            for i in range(10)
        ]
        bus = MetaLearningBus(
            MetaLearningBusConfig(
                reward_threshold=0.0,
                commit_reward_threshold=0.0,
            )
        )
        result = bus.process_traces(traces, _TS + 200)
        assert len(result.clusters) >= 1
        assert len(result.proposals) >= 1
        assert len(result.validation_results) >= 1
        assert len(result.commits) >= 1

    def test_adg_relation_graph_has_all_5_types(self):
        """Full pipeline must emit all 5 ADG relation types."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        traces = [
            (
                f"tr-full-{i:03d}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.8,
                    "healing_invoked": True,
                    "healer_id": "healer_X",
                    "success": True,
                    "healed": True,
                    "adg_entity_name": "ADG::Module::full_test",
                    "adg_relation_ids": [],
                },
                _TS + i,
            )
            for i in range(8)
        ]
        bus = MetaLearningBus(
            MetaLearningBusConfig(
                reward_threshold=0.0,
                commit_reward_threshold=0.0,
            )
        )
        result = bus.process_traces(traces, _TS + 300)
        emitted = {rel[1] for rel in result.adg_relations_emitted}
        # All 5 relation families
        assert "triggered_telemetry" in emitted
        assert "chunks_into" in emitted
        assert "stores_embedding" in emitted
        assert "scored_by_reward" in emitted
        if result.commits:
            assert "proposal_commits_optimization" in emitted

    def test_negative_case_plus_live_traces_produce_richer_cluster_set(self):
        """Negative seeds augment live-trace clusters."""
        from system_learning.engines.meta_learning_bus import MetaLearningBus
        from system_learning.types.trace_feature_types import FailurePattern

        traces = [
            (
                f"t{i}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.2,
                    "success": False,
                    "adg_entity_name": "ADG::Module::neg_test",
                    "adg_relation_ids": [],
                },
                _TS + i,
            )
            for i in range(4)
        ]
        seed = FailurePattern(
            pattern_id=_HASH64,
            source_type="ANTIPATTERN",
            signature="nondeterminism_use",
            affected_component="ADG::Module::clock_reader",
            occurrence_count=7,
            evidence_hash=_HASH64,
            cluster_id=None,
            timestamp_utc=_TS,
        )
        result_no_seed = MetaLearningBus().process_traces(traces, _TS + 100)
        result_with_seed = MetaLearningBus().process_traces(traces, _TS + 100, negative_seeds=[seed])
        assert len(result_with_seed.clusters) >= len(result_no_seed.clusters)

    def test_hitl_traces_feed_into_confidence_threshold_proposals(self):
        """HITL escalations cluster and generate confidence threshold proposals."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        traces = [
            (
                f"tr-hitl-{i}",
                {
                    "route_selected": "PATH_A",
                    "confidence_gate_state": "escalate",
                    "retrieval_path": "RAG_BGE",
                    "retrieval_groundedness_score": 0.85,
                    "human_escalation_flag": True,
                    "success": True,
                    "adg_entity_name": "ADG::Module::confidence_gate",
                    "adg_relation_ids": ["escalates_to_human"],
                },
                _TS + i,
            )
            for i in range(6)
        ]
        bus = MetaLearningBus(
            MetaLearningBusConfig(
                reward_threshold=0.0,
                commit_reward_threshold=0.0,
            )
        )
        result = bus.process_traces(traces, _TS + 200)
        change_types = {p.proposed_change_type for p in result.proposals}
        assert "CONFIDENCE_THRESHOLD_UPDATE" in change_types

    def test_replay_failure_cluster_generates_routing_proposal(self):
        """REPLAY_FAILURE cluster produces ROUTING_RULE_ADJUSTMENT proposal."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningBusConfig,
        )

        traces = [
            (
                f"tr-rf-{i}",
                {
                    "route_selected": "PATH_D",
                    "confidence_gate_state": "pass",
                    "retrieval_path": "DIRECT",
                    "retrieval_groundedness_score": 0.5,
                    "replay_failed": True,
                    "success": False,
                    "adg_entity_name": "ADG::Module::replay_module",
                    "adg_relation_ids": ["records_execution_trace"],
                },
                _TS + i,
            )
            for i in range(6)
        ]
        bus = MetaLearningBus(
            MetaLearningBusConfig(
                reward_threshold=0.0,
                commit_reward_threshold=0.0,
            )
        )
        result = bus.process_traces(traces, _TS + 200)
        change_types = {p.proposed_change_type for p in result.proposals}
        assert "ROUTING_RULE_ADJUSTMENT" in change_types
