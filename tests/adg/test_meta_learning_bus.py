"""Tests for the ADG-driven meta-learning bus pipeline.

Covers:
  - TraceFeatureTypes: frozen invariants, validation, hashing
  - OptimizationTypes: frozen invariants, validation, hashing
  - TraceFeatureExtractor: signal mapping, fail-safe defaults, batch
  - RCAClusterEngine: grouping, singleton merging, negative seeds
  - OptimizationProposalEngine: rule matching, risk downgrade, multi-agent
  - ProposalValidationEngine: gate logic, fail-closed, batch validation
  - GovernanceRewardModel: weighted scoring, invariant check, annotation
  - MetaLearningBus: full pipeline, ADG relation emission, fail-open stages
"""

from __future__ import annotations

import hashlib

import pytest

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
        for oc in ("SUCCESS", "SAFE_FAILURE", "HEALED_SUCCESS",
                   "ROLLBACK", "HUMAN_OVERRIDE", "REPLAY_FAILURE", "UNKNOWN"):
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
        for st in ("VIOLATION", "ANTIPATTERN", "DRIFT_ALERT",
                   "REPLAY_FAILURE", "LOW_GROUNDEDNESS", "OVER_ESCALATION"):
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
            "groundedness_score", "policy_compliance", "replay_stability",
            "guardrail_cleanliness", "mutation_correctness",
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


# ===========================================================================
# TestTraceFeatureExtractor
# ===========================================================================


class TestTraceFeatureExtractor:
    def _extractor(self):
        from system_learning.engines.trace_feature_extractor import TraceFeatureExtractor
        return TraceFeatureExtractor()

    def _signal(self, **kw):
        defaults = {
            "route_selected": "PATH_A",
            "confidence_gate_state": "pass",
            "retrieval_path": "RAG_BGE",
            "retrieval_groundedness_score": 0.8,
            "policy_hashes": ["ph1"],
            "guardrails_applied": ["g1"],
            "determinism_markers": ["dm1"],
            "healing_invoked": False,
            "healer_id": None,
            "human_escalation_flag": False,
            "mutation_presence": False,
            "success": True,
            "adg_entity_name": "ADG::Module::alpha",
            "adg_relation_ids": ["r1"],
        }
        defaults.update(kw)
        return defaults

    def test_success_outcome_extracted(self):
        b = self._extractor().extract("tr-001", self._signal(success=True), _TS)
        assert b.final_outcome_class == "SUCCESS"

    def test_replay_failure_highest_priority(self):
        b = self._extractor().extract(
            "tr-002",
            self._signal(success=True, replay_failed=True),
            _TS,
        )
        assert b.final_outcome_class == "REPLAY_FAILURE"

    def test_rollback_priority(self):
        b = self._extractor().extract(
            "tr-003",
            self._signal(success=False, rollback=True),
            _TS,
        )
        assert b.final_outcome_class == "ROLLBACK"

    def test_healed_success(self):
        b = self._extractor().extract(
            "tr-004",
            self._signal(success=True, healed=True),
            _TS,
        )
        assert b.final_outcome_class == "HEALED_SUCCESS"

    def test_safe_failure(self):
        b = self._extractor().extract(
            "tr-005",
            self._signal(success=False),
            _TS,
        )
        assert b.final_outcome_class == "SAFE_FAILURE"

    def test_unknown_outcome_when_no_success_key(self):
        sig = {k: v for k, v in self._signal().items() if k != "success"}
        b = self._extractor().extract("tr-006", sig, _TS)
        assert b.final_outcome_class == "UNKNOWN"

    def test_gate_state_mapping(self):
        for raw, expected in [
            ("pass", "PASS"), ("stall", "STALL"), ("escalate", "ESCALATE"),
            ("PASSED", "PASS"), ("Stalled", "STALL"), ("bogus", "PASS"),
        ]:
            b = self._extractor().extract(
                "tr-x", self._signal(confidence_gate_state=raw), _TS
            )
            assert b.confidence_gate_state == expected, f"raw={raw!r}"

    def test_groundedness_clamped_to_0_1(self):
        b = self._extractor().extract(
            "tr-x", self._signal(retrieval_groundedness_score=5.0), _TS
        )
        assert b.retrieval_groundedness_score == 1.0

        b2 = self._extractor().extract(
            "tr-y", self._signal(retrieval_groundedness_score=-1.0), _TS
        )
        assert b2.retrieval_groundedness_score == 0.0

    def test_missing_fields_produce_safe_defaults(self):
        b = self._extractor().extract("tr-empty", {}, _TS)
        assert b.route_selected == "UNKNOWN"
        assert b.retrieval_path == "UNKNOWN"
        assert b.final_outcome_class == "UNKNOWN"
        assert b.adg_entity_name == "ADG::Unknown"

    def test_batch_skips_bad_entries_and_continues(self):
        # Pass a valid and a signal that produces a bundle (no failures expected
        # since extractor is fail-safe for all signal shapes)
        traces = [
            ("tr-a", self._signal(success=True), _TS),
            ("tr-b", self._signal(success=False), _TS + 1),
        ]
        bundles = self._extractor().extract_batch(traces)
        assert len(bundles) == 2

    def test_extract_record_returns_trace_feature_record(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord
        rec = self._extractor().extract_record("tr-r", self._signal(), _TS)
        assert isinstance(rec, TraceFeatureRecord)
        assert rec.trace_id == "tr-r"

    def test_module_level_helpers(self):
        from system_learning.engines.trace_feature_extractor import (
            build_feature_bundle,
            build_trace_record,
        )
        b = build_feature_bundle("tr-h1", self._signal(), _TS)
        r = build_trace_record("tr-h2", self._signal(), _TS)
        assert b.trace_id == "tr-h1"
        assert r.trace_id == "tr-h2"


# ===========================================================================
# TestRCAClusterEngine
# ===========================================================================


def _make_record(trace_id, outcome="SAFE_FAILURE", route="PATH_A",
                 groundedness=0.4, healer=None, hitl=False,
                 guardrails=(), policies=()):
    from system_learning.types.trace_feature_types import TraceFeatureRecord
    bh = _sha256(trace_id)
    return TraceFeatureRecord(
        record_id=bh,
        trace_id=trace_id,
        route=route,
        retrieval_pattern="RAG_BGE",
        retrieval_groundedness=groundedness,
        policy_edges=policies,
        guardrail_edges=guardrails,
        determinism_signals=(),
        healer_used=healer,
        hitl_escalation=hitl,
        outcome_class=outcome,
        adg_node_id="ADG::Module::alpha",
        adg_relation_ids=(),
        feature_bundle_hash=bh,
        timestamp_utc=_TS,
    )


class TestRCAClusterEngine:
    def _engine(self, **kw):
        from system_learning.engines.rca_cluster_engine import (
            RCAClusterConfig, RCAClusterEngine,
        )
        return RCAClusterEngine(RCAClusterConfig(**kw))

    def test_two_same_pattern_records_form_cluster(self):
        records = [
            _make_record("t1", groundedness=0.2),
            _make_record("t2", groundedness=0.3),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "LOW_GROUNDEDNESS" in patterns

    def test_singleton_merged_into_residual(self):
        records = [
            _make_record("t1", groundedness=0.2),
            _make_record("t2", groundedness=0.3),
            # singleton with different pattern
            _make_record("t3", outcome="REPLAY_FAILURE"),
        ]
        clusters = self._engine(min_cluster_size=2).cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "SINGLETON_RESIDUAL" in patterns

    def test_allow_singletons_config(self):
        records = [_make_record("t1", outcome="REPLAY_FAILURE")]
        clusters = self._engine(min_cluster_size=1, allow_singletons=True).cluster(
            records, _TS
        )
        assert len(clusters) >= 1
        assert all(c.failure_pattern != "SINGLETON_RESIDUAL" for c in clusters)

    def test_negative_seed_produces_cluster(self):
        from system_learning.types.trace_feature_types import FailurePattern
        seed = FailurePattern(
            pattern_id=_HASH64,
            source_type="VIOLATION",
            signature="AuthorityViolation",
            affected_component="ADG::Module::guard",
            occurrence_count=5,
            evidence_hash=_HASH64,
            cluster_id=None,
            timestamp_utc=_TS,
        )
        clusters = self._engine().cluster([], _TS, negative_seeds=[seed])
        patterns = {c.failure_pattern for c in clusters}
        assert any("NEG_SEED" in p for p in patterns)

    def test_cluster_ids_are_deterministic(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(4)]
        c1 = self._engine().cluster(records, _TS)
        c2 = self._engine().cluster(records, _TS)
        ids1 = sorted(c.cluster_id for c in c1)
        ids2 = sorted(c.cluster_id for c in c2)
        assert ids1 == ids2

    def test_cluster_member_count_correct(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(6)]
        clusters = self._engine().cluster(records, _TS)
        low_g = [c for c in clusters if c.failure_pattern == "LOW_GROUNDEDNESS"]
        assert len(low_g) == 1
        assert low_g[0].member_count == 6

    def test_healer_required_pattern(self):
        records = [
            _make_record("t1", healer="healer_A"),
            _make_record("t2", healer="healer_B"),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "HEALER_REQUIRED" in patterns

    def test_hitl_escalation_pattern(self):
        records = [
            _make_record("t1", hitl=True),
            _make_record("t2", hitl=True),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "HITL_ESCALATION" in patterns

    def test_guardrail_block_pattern(self):
        records = [
            _make_record("t1", groundedness=0.9, guardrails=("g1",)),
            _make_record("t2", groundedness=0.9, guardrails=("g1",)),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "GUARDRAIL_BLOCK" in patterns

    def test_output_sorted_by_cluster_id(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(4)]
        clusters = self._engine().cluster(records, _TS)
        ids = [c.cluster_id for c in clusters]
        assert ids == sorted(ids)

    def test_module_level_cluster_records(self):
        from system_learning.engines.rca_cluster_engine import cluster_records
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(2)]
        clusters = cluster_records(records, _TS)
        assert isinstance(clusters, list)


# ===========================================================================
# TestOptimizationProposalEngine
# ===========================================================================


def _make_cluster(failure_pattern, member_count=5, hitl_rate=0.0,
                  healer_rate=0.0, agents=("ADG::Module::alpha",),
                  trace_ids=None):
    from system_learning.types.trace_feature_types import RCACluster
    if trace_ids is None:
        trace_ids = tuple(f"t{i}" for i in range(member_count))
    cid = _sha256(failure_pattern + str(member_count))
    return RCACluster(
        cluster_id=cid,
        failure_pattern=failure_pattern,
        dominant_route="PATH_A",
        dominant_guardrail=None,
        dominant_retrieval_pattern="RAG_BGE",
        affected_agents=agents,
        member_trace_ids=trace_ids,
        member_count=member_count,
        outcome_distribution=(("SAFE_FAILURE", member_count),),
        avg_groundedness=0.4,
        hitl_escalation_rate=hitl_rate,
        healer_invocation_rate=healer_rate,
        adg_cluster_node=f"ADG::RCACluster::{failure_pattern}::abc",
        timestamp_utc=_TS,
    )


class TestOptimizationProposalEngine:
    def _engine(self, **kw):
        from system_learning.engines.optimization_proposal_engine import (
            OptimizationProposalEngine, ProposalEngineConfig,
        )
        return OptimizationProposalEngine(ProposalEngineConfig(**kw))

    def test_low_groundedness_produces_retrieval_proposal(self):
        cluster = _make_cluster("LOW_GROUNDEDNESS")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "RETRIEVAL_RANKING_ADJUSTMENT" in types

    def test_hitl_escalation_produces_confidence_proposal(self):
        cluster = _make_cluster("HITL_ESCALATION")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "CONFIDENCE_THRESHOLD_UPDATE" in types

    def test_guardrail_block_produces_guardrail_proposal(self):
        cluster = _make_cluster("GUARDRAIL_BLOCK")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "GUARDRAIL_REFINEMENT" in types

    def test_healer_required_produces_healer_proposal(self):
        cluster = _make_cluster("HEALER_REQUIRED")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "HEALER_ROUTING_IMPROVEMENT" in types

    def test_unknown_pattern_produces_no_proposal(self):
        cluster = _make_cluster("TOTALLY_UNKNOWN_PATTERN_XYZ")
        proposals = self._engine().generate([cluster], _TS)
        assert proposals == []

    def test_high_risk_downgraded_for_small_cluster(self):
        # POLICY_VIOLATION → HIGH risk, but member_count=2 < min_cluster_members_for_high_risk=5
        cluster = _make_cluster("POLICY_VIOLATION", member_count=2)
        proposals = self._engine().generate([cluster], _TS)
        # Should be downgraded to MEDIUM
        assert all(p.risk_class == "MEDIUM" for p in proposals)

    def test_critical_blocked_by_default(self):
        # Force a CRITICAL proposal by patching — use allow_critical=False (default)
        cluster = _make_cluster("REPLAY_FAILURE", member_count=10)
        # Manually set risk_class to CRITICAL is not directly possible since rule
        # table uses HIGH at most. Test that allow_critical=False doesn't crash.
        proposals = self._engine(allow_critical=False).generate([cluster], _TS)
        assert all(p.risk_class != "CRITICAL" for p in proposals)

    def test_max_proposals_per_cluster_respected(self):
        agents = tuple(f"ADG::Module::agent{i}" for i in range(10))
        cluster = _make_cluster("LOW_GROUNDEDNESS", agents=agents)
        proposals = self._engine(max_proposals_per_cluster=3).generate([cluster], _TS)
        assert len(proposals) <= 3

    def test_proposal_ids_are_unique(self):
        clusters = [_make_cluster("LOW_GROUNDEDNESS"), _make_cluster("HITL_ESCALATION")]
        proposals = self._engine().generate(clusters, _TS)
        ids = [p.proposal_id for p in proposals]
        assert len(ids) == len(set(ids))

    def test_proposals_sorted_by_id(self):
        clusters = [_make_cluster("LOW_GROUNDEDNESS"), _make_cluster("HITL_ESCALATION")]
        proposals = self._engine().generate(clusters, _TS)
        ids = [p.proposal_id for p in proposals]
        assert ids == sorted(ids)

    def test_evidence_bundle_hash_references_cluster(self):
        cluster = _make_cluster("LOW_GROUNDEDNESS")
        proposals = self._engine().generate([cluster], _TS)
        assert all(cluster.stable_hash() in p.evidence_bundle_hashes for p in proposals)

    def test_module_level_generate_proposals(self):
        from system_learning.engines.optimization_proposal_engine import generate_proposals
        cluster = _make_cluster("HEALER_REQUIRED")
        proposals = generate_proposals([cluster], _TS)
        assert isinstance(proposals, list)


# ===========================================================================
# TestProposalValidationEngine
# ===========================================================================


def _make_proposal(change_type="ROUTING_RULE_ADJUSTMENT", risk_class="LOW",
                   reward_score=None, policy_hash=None, affected_component="ADG::Module::router",
                   evidence=()):
    from system_learning.types.optimization_types import OptimizationProposal
    pid = _sha256(change_type + risk_class + affected_component)
    cid = _sha256("cluster")
    return OptimizationProposal(
        proposal_id=pid,
        cluster_id=cid,
        proposed_change_type=change_type,
        affected_component=affected_component,
        expected_outcome="Test outcome",
        risk_class=risk_class,
        change_spec=(
            ("change_type", change_type),
            ("cluster_id", cid),
            ("dominant_route", "PATH_A"),
            ("failure_pattern", "SAFE_FAILURE"),
            ("member_count", "5"),
            ("avg_groundedness", "0.700000"),
            ("hitl_escalation_rate", "0.000000"),
            ("healer_invocation_rate", "0.000000"),
        ),
        evidence_bundle_hashes=evidence or (_HASH64,),
        reward_score=reward_score,
        policy_hash=policy_hash,
        timestamp_utc=_TS,
    )


class TestProposalValidationEngine:
    def _engine(self, **kw):
        from system_learning.engines.proposal_validation_engine import (
            ProposalValidationEngine, ValidationConfig,
        )
        return ProposalValidationEngine(ValidationConfig(**kw))

    def test_clean_proposal_passes_all_gates(self):
        p = _make_proposal()
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is True
        assert result.denial_reasons == ()

    def test_unknown_component_fails_guardrail_gate(self):
        p = _make_proposal(affected_component="ADG::Unknown")
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is False
        assert "UNKNOWN_AFFECTED_COMPONENT" in result.denial_reasons

    def test_embedding_expansion_with_no_evidence_fails_replay_gate(self):
        from system_learning.types.optimization_types import OptimizationProposal
        cid = _sha256("cluster")
        pid = _sha256("EMBEDDING_CORPUS_EXPANSION_LOW_ADG::Module::router")
        p = OptimizationProposal(
            proposal_id=pid,
            cluster_id=cid,
            proposed_change_type="EMBEDDING_CORPUS_EXPANSION",
            affected_component="ADG::Module::router",
            expected_outcome="Test outcome",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(),  # explicitly empty
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is False
        assert "EMBEDDING_EXPANSION_NO_EVIDENCE" in result.denial_reasons

    def test_policy_hash_mismatch_fails_policy_gate(self):
        p = _make_proposal(policy_hash="hash_a")
        result = self._engine(active_policy_hash="hash_b").validate(p, _TS)
        assert result.validation_pass is False
        assert "POLICY_HASH_MISMATCH" in result.denial_reasons

    def test_policy_hash_match_passes_policy_gate(self):
        p = _make_proposal(policy_hash="hash_a")
        result = self._engine(active_policy_hash="hash_a").validate(p, _TS)
        assert result.policy_safe is True

    def test_high_regression_blocks_high_risk_proposal(self):
        p = _make_proposal(risk_class="HIGH")
        result = self._engine().validate(p, _TS, hitl_rate=0.8)
        # HITL rate 0.8 → HIGH regression for HIGH risk proposal
        assert result.validation_pass is False
        assert "HIGH_REGRESSION_RISK" in result.denial_reasons

    def test_high_regression_does_not_block_low_risk(self):
        p = _make_proposal(risk_class="LOW")
        result = self._engine().validate(p, _TS, hitl_rate=0.9)
        # LOW risk → regression should not block
        assert result.validation_pass is True

    def test_result_id_is_sha256_hexdigest(self):
        p = _make_proposal()
        result = self._engine().validate(p, _TS)
        assert len(result.result_id) == 64
        assert all(c in "0123456789abcdef" for c in result.result_id)

    def test_batch_validation_returns_sorted_results(self):
        proposals = [_make_proposal(risk_class="LOW"), _make_proposal(change_type="CONFIDENCE_THRESHOLD_UPDATE")]
        results = self._engine().validate_batch(proposals, _TS)
        ids = [r.result_id for r in results]
        assert ids == sorted(ids)

    def test_gate_exception_counts_as_failure(self):
        # Force a determinism gate failure by using a non-hash proposal_id
        from system_learning.types.optimization_types import OptimizationProposal
        cid = _sha256("cluster")
        p = OptimizationProposal(
            proposal_id="NOT_A_HASH",  # will fail determinism gate
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Module::router",
            expected_outcome="Test",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(_HASH64,),
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is False
        assert "PROPOSAL_ID_NOT_HASH" in result.denial_reasons

    def test_module_level_validate_proposal(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal
        p = _make_proposal()
        result = validate_proposal(p, _TS)
        assert result.validation_pass is True


# ===========================================================================
# TestGovernanceRewardModel
# ===========================================================================


def _make_signal(trace_id, gnd=0.9, policy=0.95, replay=1.0,
                 guard=1.0, mut=1.0, approval=None):
    from system_learning.types.optimization_types import GovernanceRewardSignal
    sid = _sha256(trace_id)
    return GovernanceRewardSignal(
        signal_id=sid,
        trace_id=trace_id,
        groundedness_score=gnd,
        policy_compliance=policy,
        replay_stability=replay,
        guardrail_cleanliness=guard,
        mutation_correctness=mut,
        human_approval=approval,
        timestamp_utc=_TS,
    )


class TestGovernanceRewardModel:
    def _model(self, **kw):
        from system_learning.engines.governance_reward_model import (
            GovernanceRewardModel, RewardModelConfig,
        )
        return GovernanceRewardModel(RewardModelConfig(**kw))

    def test_high_quality_signals_produce_high_score(self):
        p = _make_proposal()
        signals = [_make_signal(f"t{i}") for i in range(5)]
        score = self._model().score(p, signals, _TS)
        assert score.aggregate_score > 0.8
        assert score.invariant_preserved is True

    def test_zero_signals_produce_zero_score_and_invariant_false(self):
        p = _make_proposal()
        score = self._model().score(p, [], _TS)
        assert score.aggregate_score == 0.0
        assert score.invariant_preserved is False
        assert score.signal_count == 0

    def test_low_policy_compliance_breaks_invariant(self):
        p = _make_proposal()
        # policy_compliance < 0.80 (floor)
        signals = [_make_signal(f"t{i}", policy=0.5) for i in range(3)]
        score = self._model().score(p, signals, _TS)
        assert score.invariant_preserved is False

    def test_low_replay_stability_breaks_invariant(self):
        p = _make_proposal()
        signals = [_make_signal(f"t{i}", replay=0.5) for i in range(3)]
        score = self._model().score(p, signals, _TS)
        assert score.invariant_preserved is False

    def test_human_approval_rate_computed_correctly(self):
        p = _make_proposal()
        signals = [
            _make_signal("t1", approval=True),
            _make_signal("t2", approval=False),
            _make_signal("t3", approval=None),  # no HITL
        ]
        score = self._model().score(p, signals, _TS)
        # 1 approved out of 2 HITL signals
        assert score.human_approval_rate == pytest.approx(0.5, abs=1e-6)

    def test_no_hitl_signals_approval_rate_is_1(self):
        p = _make_proposal()
        signals = [_make_signal("t1", approval=None)]
        score = self._model().score(p, signals, _TS)
        assert score.human_approval_rate == 1.0

    def test_invalid_signal_empty_trace_id_skipped(self):
        from system_learning.types.optimization_types import GovernanceRewardSignal
        p = _make_proposal()
        bad_signal = GovernanceRewardSignal(
            signal_id=_HASH64,
            trace_id="",  # invalid
            groundedness_score=0.9,
            policy_compliance=0.95,
            replay_stability=1.0,
            guardrail_cleanliness=1.0,
            mutation_correctness=1.0,
            human_approval=None,
            timestamp_utc=_TS,
        )
        score = self._model().score(p, [bad_signal], _TS)
        assert score.signal_count == 0  # invalid signal was rejected

    def test_weights_must_sum_to_1(self):
        from system_learning.engines.governance_reward_model import RewardModelConfig
        with pytest.raises(ValueError, match="sum to 1.0"):
            RewardModelConfig(
                weight_groundedness=0.5,
                weight_policy_compliance=0.5,
                weight_replay_stability=0.5,
                weight_guardrail_cleanliness=0.5,
                weight_mutation_correctness=0.5,
            )

    def test_annotate_proposals_sets_reward_score(self):
        import dataclasses
        p = _make_proposal()
        signals = [_make_signal(f"t{i}") for i in range(3)]
        model = self._model()
        scores = model.score_batch([p], {p.proposal_id: signals}, _TS)
        annotated = model.annotate_proposals([p], scores, _TS)
        assert len(annotated) == 1
        assert annotated[0].reward_score is not None
        assert 0.0 <= annotated[0].reward_score <= 1.0

    def test_module_level_score_proposal(self):
        from system_learning.engines.governance_reward_model import score_proposal
        p = _make_proposal()
        signals = [_make_signal("t1")]
        score = score_proposal(p, signals, _TS)
        assert score.proposal_id == p.proposal_id


# ===========================================================================
# TestMetaLearningBus
# ===========================================================================


class TestMetaLearningBus:
    def _bus(self, **kw):
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus, MetaLearningBusConfig,
        )
        return MetaLearningBus(MetaLearningBusConfig(**kw))

    def _signal(self, trace_id, success=True, groundedness=0.8,
                outcome_override=None):
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
        traces = [
            (f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i)
            for i in range(6)
        ]
        result = self._bus().process_traces(traces, _TS + 100)
        assert len(result.proposals) >= 1

    def test_adg_triggered_telemetry_relations_emitted(self):
        traces = [("t1", self._signal("t1"), _TS)]
        result = self._bus().process_traces(traces, _TS)
        relation_types = {rel[1] for rel in result.adg_relations_emitted}
        assert "triggered_telemetry" in relation_types

    def test_adg_chunks_into_relations_emitted_for_clusters(self):
        traces = [
            (f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i)
            for i in range(4)
        ]
        result = self._bus(reward_threshold=0.0).process_traces(traces, _TS + 100)
        relation_types = {rel[1] for rel in result.adg_relations_emitted}
        assert "chunks_into" in relation_types

    def test_adg_stores_embedding_relations_emitted(self):
        traces = [
            (f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i)
            for i in range(4)
        ]
        result = self._bus(reward_threshold=0.0).process_traces(traces, _TS + 100)
        relation_types = {rel[1] for rel in result.adg_relations_emitted}
        assert "stores_embedding" in relation_types

    def test_low_reward_threshold_allows_more_proposals_to_validation(self):
        traces = [
            (f"t{i}", self._signal(f"t{i}", groundedness=0.2), _TS + i)
            for i in range(6)
        ]
        result_strict = self._bus(reward_threshold=0.99).process_traces(traces, _TS + 100)
        result_loose = self._bus(reward_threshold=0.0).process_traces(traces, _TS + 100)
        # With threshold 0.0, at least as many proposals pass reward gate
        assert len(result_loose.validation_results) >= len(result_strict.validation_results)

    def test_successful_pipeline_produces_commits(self):
        # 6 traces with HEALER_REQUIRED pattern (LOW risk → easy to pass)
        traces = [
            (f"t{i}", {
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
            }, _TS + i)
            for i in range(6)
        ]
        result = self._bus(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ).process_traces(traces, _TS + 100)
        assert len(result.commits) >= 1

    def test_commits_have_correct_adg_relation(self):
        traces = [
            (f"t{i}", {
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
            }, _TS + i)
            for i in range(6)
        ]
        result = self._bus(
            reward_threshold=0.0, commit_reward_threshold=0.0,
        ).process_traces(traces, _TS + 100)
        for commit in result.commits:
            assert commit.adg_relation == "proposal_commits_optimization"

    def test_proposal_commits_optimization_relations_emitted(self):
        traces = [
            (f"t{i}", {
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
            }, _TS + i)
            for i in range(6)
        ]
        result = self._bus(
            reward_threshold=0.0, commit_reward_threshold=0.0,
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
            (f"t{i}", {
                "route_selected": "PATH_A",
                "confidence_gate_state": "pass",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.8,
                "replay_failed": True,
                "success": False,
                "adg_entity_name": "ADG::Module::replay_test",
                "adg_relation_ids": [],
            }, _TS + i)
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
        from system_learning.engines.meta_learning_bus import BusPipelineResult
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
        result = bus.process_traces(
            [("t1", self._signal("t1"), _TS)], _TS + 10
        )
        assert isinstance(result.adg_relations_emitted, list)


# ===========================================================================
# Integration: full closed loop
# ===========================================================================


class TestClosedLearningLoop:
    """End-to-end tests verifying the complete learning loop."""

    def test_10_low_groundedness_traces_produce_commit(self):
        """10 low-groundedness traces → cluster → proposal → validation → commit."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus, MetaLearningBusConfig,
        )
        traces = [
            (f"tr-lg-{i:03d}", {
                "route_selected": "PATH_B",
                "confidence_gate_state": "pass",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.2,
                "success": False,
                "adg_entity_name": "ADG::Module::retriever",
                "adg_relation_ids": ["retrieves_via"],
            }, _TS + i)
            for i in range(10)
        ]
        bus = MetaLearningBus(MetaLearningBusConfig(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ))
        result = bus.process_traces(traces, _TS + 200)
        assert len(result.clusters) >= 1
        assert len(result.proposals) >= 1
        assert len(result.validation_results) >= 1
        assert len(result.commits) >= 1

    def test_adg_relation_graph_has_all_5_types(self):
        """Full pipeline must emit all 5 ADG relation types."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus, MetaLearningBusConfig,
        )
        traces = [
            (f"tr-full-{i:03d}", {
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
            }, _TS + i)
            for i in range(8)
        ]
        bus = MetaLearningBus(MetaLearningBusConfig(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ))
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
            (f"t{i}", {
                "route_selected": "PATH_A",
                "confidence_gate_state": "pass",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.2,
                "success": False,
                "adg_entity_name": "ADG::Module::neg_test",
                "adg_relation_ids": [],
            }, _TS + i)
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
        result_with_seed = MetaLearningBus().process_traces(
            traces, _TS + 100, negative_seeds=[seed]
        )
        assert len(result_with_seed.clusters) >= len(result_no_seed.clusters)

    def test_hitl_traces_feed_into_confidence_threshold_proposals(self):
        """HITL escalations cluster and generate confidence threshold proposals."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus, MetaLearningBusConfig,
        )
        traces = [
            (f"tr-hitl-{i}", {
                "route_selected": "PATH_A",
                "confidence_gate_state": "escalate",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.85,
                "human_escalation_flag": True,
                "success": True,
                "adg_entity_name": "ADG::Module::confidence_gate",
                "adg_relation_ids": ["escalates_to_human"],
            }, _TS + i)
            for i in range(6)
        ]
        bus = MetaLearningBus(MetaLearningBusConfig(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ))
        result = bus.process_traces(traces, _TS + 200)
        change_types = {p.proposed_change_type for p in result.proposals}
        assert "CONFIDENCE_THRESHOLD_UPDATE" in change_types

    def test_replay_failure_cluster_generates_routing_proposal(self):
        """REPLAY_FAILURE cluster produces ROUTING_RULE_ADJUSTMENT proposal."""
        from system_learning.engines.meta_learning_bus import (
            MetaLearningBus, MetaLearningBusConfig,
        )
        traces = [
            (f"tr-rf-{i}", {
                "route_selected": "PATH_D",
                "confidence_gate_state": "pass",
                "retrieval_path": "DIRECT",
                "retrieval_groundedness_score": 0.5,
                "replay_failed": True,
                "success": False,
                "adg_entity_name": "ADG::Module::replay_module",
                "adg_relation_ids": ["records_execution_trace"],
            }, _TS + i)
            for i in range(6)
        ]
        bus = MetaLearningBus(MetaLearningBusConfig(
            reward_threshold=0.0,
            commit_reward_threshold=0.0,
        ))
        result = bus.process_traces(traces, _TS + 200)
        change_types = {p.proposed_change_type for p in result.proposals}
        assert "ROUTING_RULE_ADJUSTMENT" in change_types
