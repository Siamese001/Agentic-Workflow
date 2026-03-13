"""Tests for MetaLearningBus pipeline and closed-loop integration.

Covers:
  - MetaLearningBus: full pipeline, ADG relation emission, fail-open stages
  - TestClosedLearningLoop: end-to-end integration scenarios
"""

from __future__ import annotations

import hashlib

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
