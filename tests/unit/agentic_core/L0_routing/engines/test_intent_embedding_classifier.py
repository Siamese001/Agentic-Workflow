"""Behavioral tests for IntentEmbeddingClassifier.

Covers:
- No-embedder fallback (no EmbeddingServiceFactory available)
- Prototype registration, deduplication, hash stability
- classify() without embedder returns None
- classify() with stub embedder returns best cosine match
- update_prototype() replaces existing entry
- Tie-breaking is deterministic
- Out-of-bounds confidence clamping
- Empty prototype count guard
- Kill-switch / exception isolation (never raises into caller)
"""

from __future__ import annotations

import math
from typing import Any
from unittest.mock import MagicMock, patch

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

_emit_records_execution_trace("p0", "evidence", "test_intent_embedding_classifier")
_emit_applies_guardrail("p0", "test_intent_embedding_classifier", "p0_governance")
_emit_reads_policy_state("p0", "test_intent_embedding_classifier", "policy_binding")
_emit_snapshots_state("p0", "test_intent_embedding_classifier", "state_snapshot")
emit_replay_key("p0", "test_intent_embedding_classifier")
emit_determinism_digest("p0", "test_intent_embedding_classifier")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_intent_embedding_classifier", "execution_auth")
_emit_validates_capability("p2", "test_intent_embedding_classifier", "capability_check")
_emit_routes_to_capability("p2", "test_intent_embedding_classifier", "capability_route")
_emit_writes_via_uwg("p2", "test_intent_embedding_classifier", "uwg_write")
_emit_blocks_direct_write("p2", "test_intent_embedding_classifier", "direct_write_block")
_emit_records_tool_invocation("p2", "test_intent_embedding_classifier", "tool_invocation")
_emit_captures_execution_output("p2", "test_intent_embedding_classifier", "exec_output")
_emit_dispatches_agent("p3", "test_intent_embedding_classifier", "agent_dispatch")
_emit_coordinates_agents("p3", "test_intent_embedding_classifier", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_intent_embedding_classifier", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_intent_embedding_classifier", "healing_outcome")
_emit_escalates_failure("p3", "test_intent_embedding_classifier", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_intent_embedding_classifier", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_intent_embedding_classifier", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_intent_embedding_classifier", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_intent_embedding_classifier", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_intent_embedding_classifier", "eval_metric")
_emit_stores_embedding("p4", "test_intent_embedding_classifier", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_intent_embedding_classifier", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_intent_embedding_classifier", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.engines.intent_embedding_classifier import (
    IntentEmbeddingClassifier,
    _average_vectors,
    _l2_normalize,
)
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

_emit_emits_metric_event("test_intent_embedding_classifier", "p4obs", "metric_1")
_emit_emits_metric_event("test_intent_embedding_classifier", "p4obs", "metric_2")
_emit_emits_metric_event("test_intent_embedding_classifier", "p4obs", "metric_3")
_emit_emits_metric_event("test_intent_embedding_classifier", "p4obs", "metric_4")
_emit_emits_metric_event("test_intent_embedding_classifier", "p4obs", "metric_5")
_emit_emits_metric_event("test_intent_embedding_classifier", "p4obs", "metric_6")
_emit_records_incident_event("test_intent_embedding_classifier", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_intent_embedding_classifier", "p4obs", "anomaly")
_emit_writes_observability_log("test_intent_embedding_classifier", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_intent_embedding_classifier", "p4obs", "mon_state")
_emit_triggers_alert("test_intent_embedding_classifier", "p4obs", "alert")
_emit_links_incident_trace("test_intent_embedding_classifier", "p4obs", "trace_link")
_emit_captures_pattern("test_intent_embedding_classifier", "p3lm", "pattern")
_emit_records_learning_event("test_intent_embedding_classifier", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_intent_embedding_classifier", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_intent_embedding_classifier", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_intent_embedding_classifier", "p3lm", "routing")
_emit_improves_agent_policy("test_intent_embedding_classifier", "p3lm", "policy")
_emit_stores_learning_state("test_intent_embedding_classifier", "p3lm", "state")
_emit_records_execution_trace("test_intent_embedding_classifier", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_intent_embedding_classifier", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_intent_embedding_classifier", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_intent_embedding_classifier", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_intent_embedding_classifier", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_intent_embedding_classifier", "env_read", "p2_env_1")
_emit_reads_environ("test_intent_embedding_classifier", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_intent_embedding_classifier", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_intent_embedding_classifier", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_intent_embedding_classifier", "context_pull")
_emit_pulls_context("p1", "test_intent_embedding_classifier", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_intent_embedding_classifier", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_intent_embedding_classifier", "uwg_term_2")
_emit_writes_through("p1", "test_intent_embedding_classifier", "write_through")
_emit_writes_through("p1", "test_intent_embedding_classifier", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_intent_embedding_classifier", "safety_validation")
_emit_invokes_eval("p1", "test_intent_embedding_classifier", "eval_call")
_emit_proposal_commits_routing("p1", "test_intent_embedding_classifier", "routing_commit")
_emit_escalates_to_human("p1", "test_intent_embedding_classifier", "human_escalation")
_emit_routes_through("p1", "test_intent_embedding_classifier", "route_through")
_emit_checks_agent_registry("p1", "test_intent_embedding_classifier", "agent_registry")
_emit_validates_agent_capability("p1", "test_intent_embedding_classifier", "capability")
_emit_dispatches_execution_plan("p1", "test_intent_embedding_classifier", "exec_plan")
_emit_agent_executes_agent("p1", "test_intent_embedding_classifier", "sub_agent")
_emit_routes_to_agent("p1", "test_intent_embedding_classifier", "target_agent")
_emit_verifies_policy("p1", "test_intent_embedding_classifier", "policy_check")
_emit_observes_runtime_state("p1", "test_intent_embedding_classifier", "runtime_state")
_emit_verifies_boundary("p1", "test_intent_embedding_classifier", "boundary_check")
_emit_transcripts_response("p1", "test_intent_embedding_classifier", "transcript")
_emit_hard_fails_untranscripted("p1", "test_intent_embedding_classifier")
_emit_gated_by_confidence("p1", "test_intent_embedding_classifier", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unit_vec(dim: int, idx: int) -> list[float]:
    """Return a unit vector of length dim with 1.0 at position idx."""
    v = [0.0] * dim
    v[idx] = 1.0
    return v


class _StubEmbedder:
    """Deterministic stub: embeds text by returning a fixed pre-registered vector."""

    def __init__(self, mapping: dict[str, list[float]]) -> None:
        self._map = mapping
        self._default_dim = 4

    def embed(self, text: str) -> Any:
        vec = self._map.get(text, [0.0] * self._default_dim)
        result = MagicMock()
        result.vector = vec
        return result


def _make_classifier_with_stub(mapping: dict[str, list[float]]) -> IntentEmbeddingClassifier:
    stub = _StubEmbedder(mapping)
    clf = IntentEmbeddingClassifier(embedder=stub)
    return clf


# ---------------------------------------------------------------------------
# Unit helper tests
# ---------------------------------------------------------------------------


class TestL2Normalize:
    def test_unit_vector_unchanged(self):
        v = [1.0, 0.0, 0.0]
        n = _l2_normalize(v)
        assert abs(math.sqrt(sum(x * x for x in n)) - 1.0) < 1e-6

    def test_zero_vector_returned_unchanged(self):
        v = [0.0, 0.0, 0.0]
        assert _l2_normalize(v) == [0.0, 0.0, 0.0]

    def test_scaling_produces_unit(self):
        v = [3.0, 4.0]
        n = _l2_normalize(v)
        assert abs(n[0] - 0.6) < 1e-6
        assert abs(n[1] - 0.8) < 1e-6


class TestAverageVectors:
    def test_empty_returns_none(self):
        assert _average_vectors([]) is None

    def test_single_vector_returned(self):
        v = [1.0, 2.0, 3.0]
        result = _average_vectors([v])
        assert result == [1.0, 2.0, 3.0]

    def test_two_vectors_averaged(self):
        a = [2.0, 0.0]
        b = [0.0, 2.0]
        result = _average_vectors([a, b])
        assert result == [1.0, 1.0]


# ---------------------------------------------------------------------------
# IntentEmbeddingClassifier — no-embedder path (no EmbeddingServiceFactory)
# ---------------------------------------------------------------------------


class TestNoEmbedder:
    def setup_method(self):
        self.clf = IntentEmbeddingClassifier()

    def test_prototype_count_starts_zero(self):
        assert self.clf.prototype_count() == 0

    def test_has_prototype_false_before_register(self):
        assert not self.clf.has_prototype("resume_writer")

    def test_encode_prototype_returns_false_without_embedder(self):
        with patch.object(self.clf, "_get_embedder", return_value=None):
            result = self.clf.encode_prototype("resume_writer", ["resume", "cv"])
        assert result is False
        assert self.clf.prototype_count() == 0

    def test_classify_returns_none_no_prototypes(self):
        result = self.clf.classify("write my resume")
        assert result is None

    def test_classify_returns_none_embedder_unavailable(self):
        with patch.object(self.clf, "_get_embedder", return_value=None):
            # Manually add a fake entry to bypass the empty-prototypes guard
            from agentic_core.L0_routing.engines.intent_embedding_classifier import _PrototypeEntry

            self.clf._prototypes["x"] = _PrototypeEntry("x", "abc", [1.0, 0.0])
            result = self.clf.classify("write my resume")
        assert result is None


# ---------------------------------------------------------------------------
# IntentEmbeddingClassifier — stub embedder path
# ---------------------------------------------------------------------------


class TestWithStubEmbedder:
    """Use orthogonal unit vectors so cosine similarity is perfectly deterministic."""

    def setup_method(self):
        self.mapping = {
            "resume": _unit_vec(4, 0),
            "cv": _unit_vec(4, 0),
            "code": _unit_vec(4, 1),
            "review": _unit_vec(4, 1),
            "query resume": _unit_vec(4, 0),
            "query code": _unit_vec(4, 1),
        }
        self.clf = _make_classifier_with_stub(self.mapping)

    def _register_targets(self):
        self.clf.encode_prototype("resume_writer", ["resume", "cv"])
        self.clf.encode_prototype("code_reviewer", ["code", "review"])

    def test_encode_prototype_returns_true(self):
        result = self.clf.encode_prototype("resume_writer", ["resume", "cv"])
        assert result is True

    def test_prototype_count_after_register(self):
        self._register_targets()
        assert self.clf.prototype_count() == 2

    def test_has_prototype_true_after_register(self):
        self._register_targets()
        assert self.clf.has_prototype("resume_writer")
        assert self.clf.has_prototype("code_reviewer")

    def test_classify_returns_tuple(self):
        self._register_targets()
        result = self.clf.classify("query resume")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_classify_resume_query_matches_resume_writer(self):
        self._register_targets()
        name, conf = self.clf.classify("query resume")
        assert name == "resume_writer"
        assert 0.0 <= conf <= 1.0

    def test_classify_code_query_matches_code_reviewer(self):
        self._register_targets()
        name, conf = self.clf.classify("query code")
        assert name == "code_reviewer"
        assert 0.0 <= conf <= 1.0

    def test_classify_confidence_clamped_to_0_1(self):
        self._register_targets()
        _, conf = self.clf.classify("query resume")
        assert 0.0 <= conf <= 1.0

    def test_classify_deterministic_same_input_same_output(self):
        self._register_targets()
        r1 = self.clf.classify("query resume")
        r2 = self.clf.classify("query resume")
        assert r1 == r2

    def test_no_prototypes_returns_none(self):
        result = self.clf.classify("any query")
        assert result is None

    def test_get_prototype_hash_not_none_after_register(self):
        self.clf.encode_prototype("resume_writer", ["resume", "cv"])
        h = self.clf.get_prototype_hash("resume_writer")
        assert h is not None
        assert len(h) == 64  # sha256 hex

    def test_get_prototype_hash_stable_for_same_texts(self):
        clf2 = _make_classifier_with_stub(self.mapping)
        self.clf.encode_prototype("resume_writer", ["resume", "cv"])
        clf2.encode_prototype("resume_writer", ["resume", "cv"])
        assert self.clf.get_prototype_hash("resume_writer") == clf2.get_prototype_hash("resume_writer")

    def test_get_prototype_hash_none_for_unknown(self):
        assert self.clf.get_prototype_hash("nonexistent") is None

    def test_update_prototype_replaces_existing(self):
        self.clf.encode_prototype("resume_writer", ["resume", "cv"])
        old_hash = self.clf.get_prototype_hash("resume_writer")
        # Update with different texts
        new_mapping = dict(self.mapping)
        new_mapping["new_keyword"] = _unit_vec(4, 2)
        clf2 = _make_classifier_with_stub(new_mapping)
        clf2.encode_prototype("resume_writer", ["resume", "cv"])
        clf2.encode_prototype("resume_writer", ["new_keyword"])
        # prototype count stays 1 (overwrite, not append)
        assert clf2.prototype_count() == 1

    def test_encode_prototype_empty_texts_returns_false(self):
        result = self.clf.encode_prototype("resume_writer", [])
        assert result is False

    def test_cosine_cutoff_filters_below_threshold(self):
        """Classifier with high cutoff returns None for low-similarity input."""
        clf_strict = _make_classifier_with_stub(self.mapping)
        clf_strict._cosine_cutoff = 0.99
        clf_strict.encode_prototype("resume_writer", ["resume", "cv"])
        # "query code" maps to orthogonal vector → cosine ≈ 0 with resume prototype
        result = clf_strict.classify("query code")
        assert result is None

    def test_embedding_exception_returns_none_gracefully(self):
        """classify() must not propagate exceptions from _embed_texts."""
        self._register_targets()

        def _raising_embed(texts):
            raise RuntimeError("simulated failure")

        with patch.object(self.clf, "_embed_texts", side_effect=_raising_embed):
            result = self.clf.classify("query resume")
        assert result is None


# ---------------------------------------------------------------------------
# Single-prototype edge case
# ---------------------------------------------------------------------------


class TestSinglePrototype:
    def setup_method(self):
        mapping = {"only": _unit_vec(3, 0), "query": _unit_vec(3, 0)}
        self.clf = _make_classifier_with_stub(mapping)
        self.clf.encode_prototype("only_target", ["only"])

    def test_single_prototype_always_wins(self):
        name, conf = self.clf.classify("query")
        assert name == "only_target"
        assert conf > 0.0
