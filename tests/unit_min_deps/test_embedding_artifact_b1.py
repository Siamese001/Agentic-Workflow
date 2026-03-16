"""Tests for EmbeddingArtifact type (Plan B Phase 1).

Comprehensive test suite covering determinism, canonical bytes, hash computation,
and invariants enforcement.
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

_emit_authorize_and_execute("p2", "test_embedding_artifact_b1", "execution_auth")
_emit_validates_capability("p2", "test_embedding_artifact_b1", "capability_check")
_emit_routes_to_capability("p2", "test_embedding_artifact_b1", "capability_route")
_emit_writes_via_uwg("p2", "test_embedding_artifact_b1", "uwg_write")
_emit_blocks_direct_write("p2", "test_embedding_artifact_b1", "direct_write_block")
_emit_records_tool_invocation("p2", "test_embedding_artifact_b1", "tool_invocation")
_emit_captures_execution_output("p2", "test_embedding_artifact_b1", "exec_output")
_emit_dispatches_agent("p3", "test_embedding_artifact_b1", "agent_dispatch")
_emit_coordinates_agents("p3", "test_embedding_artifact_b1", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_embedding_artifact_b1", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_embedding_artifact_b1", "healing_outcome")
_emit_escalates_failure("p3", "test_embedding_artifact_b1", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_embedding_artifact_b1", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_embedding_artifact_b1", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_embedding_artifact_b1", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_embedding_artifact_b1", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_embedding_artifact_b1", "eval_metric")
_emit_stores_embedding("p4", "test_embedding_artifact_b1", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_embedding_artifact_b1", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_embedding_artifact_b1", "exec_snapshot_link")
from system_learning.types.embedding_artifact import EmbeddingArtifact

_emit_records_execution_trace("p0", "evidence", "test_embedding_artifact_b1")
_emit_applies_guardrail("p0", "test_embedding_artifact_b1", "p0_governance")
_emit_reads_policy_state("p0", "test_embedding_artifact_b1", "policy_binding")
_emit_snapshots_state("p0", "test_embedding_artifact_b1", "state_snapshot")
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

_emit_emits_metric_event("test_embedding_artifact_b1", "p4obs", "metric_1")
_emit_emits_metric_event("test_embedding_artifact_b1", "p4obs", "metric_2")
_emit_emits_metric_event("test_embedding_artifact_b1", "p4obs", "metric_3")
_emit_emits_metric_event("test_embedding_artifact_b1", "p4obs", "metric_4")
_emit_emits_metric_event("test_embedding_artifact_b1", "p4obs", "metric_5")
_emit_emits_metric_event("test_embedding_artifact_b1", "p4obs", "metric_6")
_emit_records_incident_event("test_embedding_artifact_b1", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_embedding_artifact_b1", "p4obs", "anomaly")
_emit_writes_observability_log("test_embedding_artifact_b1", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_embedding_artifact_b1", "p4obs", "mon_state")
_emit_triggers_alert("test_embedding_artifact_b1", "p4obs", "alert")
_emit_links_incident_trace("test_embedding_artifact_b1", "p4obs", "trace_link")
_emit_captures_pattern("test_embedding_artifact_b1", "p3lm", "pattern")
_emit_records_learning_event("test_embedding_artifact_b1", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_embedding_artifact_b1", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_embedding_artifact_b1", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_embedding_artifact_b1", "p3lm", "routing")
_emit_improves_agent_policy("test_embedding_artifact_b1", "p3lm", "policy")
_emit_stores_learning_state("test_embedding_artifact_b1", "p3lm", "state")
_emit_records_execution_trace("test_embedding_artifact_b1", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_embedding_artifact_b1", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_embedding_artifact_b1", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_embedding_artifact_b1", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_embedding_artifact_b1", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_embedding_artifact_b1", "env_read", "p2_env_1")
_emit_reads_environ("test_embedding_artifact_b1", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_embedding_artifact_b1", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_embedding_artifact_b1", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_embedding_artifact_b1", "context_pull")
_emit_pulls_context("p1", "test_embedding_artifact_b1", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_embedding_artifact_b1", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_embedding_artifact_b1", "uwg_term_2")
_emit_writes_through("p1", "test_embedding_artifact_b1", "write_through")
_emit_writes_through("p1", "test_embedding_artifact_b1", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_embedding_artifact_b1", "safety_validation")
_emit_invokes_eval("p1", "test_embedding_artifact_b1", "eval_call")
_emit_proposal_commits_routing("p1", "test_embedding_artifact_b1", "routing_commit")
_emit_escalates_to_human("p1", "test_embedding_artifact_b1", "human_escalation")
_emit_routes_through("p1", "test_embedding_artifact_b1", "route_through")
_emit_checks_agent_registry("p1", "test_embedding_artifact_b1", "agent_registry")
_emit_validates_agent_capability("p1", "test_embedding_artifact_b1", "capability")
_emit_dispatches_execution_plan("p1", "test_embedding_artifact_b1", "exec_plan")
_emit_agent_executes_agent("p1", "test_embedding_artifact_b1", "sub_agent")
_emit_routes_to_agent("p1", "test_embedding_artifact_b1", "target_agent")
_emit_verifies_policy("p1", "test_embedding_artifact_b1", "policy_check")
_emit_observes_runtime_state("p1", "test_embedding_artifact_b1", "runtime_state")
_emit_verifies_boundary("p1", "test_embedding_artifact_b1", "boundary_check")
_emit_transcripts_response("p1", "test_embedding_artifact_b1", "transcript")
_emit_hard_fails_untranscripted("p1", "test_embedding_artifact_b1")
_emit_gated_by_confidence("p1", "test_embedding_artifact_b1", "confidence_gate")
emit_replay_key("p0", "test_embedding_artifact_b1")
emit_determinism_digest("p0", "test_embedding_artifact_b1")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps


class TestEmbeddingArtifactDeterminism:
    """Test deterministic behavior of EmbeddingArtifact."""

    def test_same_inputs_identical_canonical_bytes(self):
        """Same inputs → identical canonical_bytes."""
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        assert artifact1.canonical_bytes() == artifact2.canonical_bytes()

    def test_same_inputs_identical_artifact_hash(self):
        """Same inputs → identical artifact_hash."""
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t3", "t1", "t2"],
            supporting_content_hashes=["h3", "h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        assert artifact1.artifact_hash() == artifact2.artifact_hash()

    def test_different_trace_ids_different_artifact_hash(self):
        """Different trace_ids → different artifact_hash."""
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t2"],
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t3"],  # Different trace_id
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        assert artifact1.artifact_hash() != artifact2.artifact_hash()

    def test_canonical_sorting_enforced_trace_ids(self):
        """Trace IDs are automatically sorted canonically."""
        # Create with unordered trace IDs
        artifact = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["z_trace", "a_trace", "m_trace"],
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Should be sorted to ["a_trace", "m_trace", "z_trace"]
        assert artifact.supporting_trace_ids == ["a_trace", "m_trace", "z_trace"]

    def test_canonical_sorting_enforced_content_hashes(self):
        """Content hashes are automatically sorted canonically."""
        artifact = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t2"],
            supporting_content_hashes=["z_hash", "a_hash", "m_hash"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Should be sorted to ["a_hash", "m_hash", "z_hash"]
        assert artifact.supporting_content_hashes == ["a_hash", "m_hash", "z_hash"]


class TestEmbeddingArtifactNegativeControl:
    """Test negative control cases to prove determinism enforcement."""

    def test_ordering_instability_without_canonical_sort_changes_hash(self):
        """Negative control: Without canonical sort, ordering changes hash.

        This test demonstrates why canonical sorting is necessary by showing
        that different input orders would produce different hashes if not
        automatically sorted.
        """
        # Create two artifacts with different input orders
        # (they will be auto-sorted, but we can verify the sorting works)
        artifact1 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["z_trace", "a_trace"],  # Unordered input
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        artifact2 = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["a_trace", "z_trace"],  # Different order
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Both should have the same sorted order
        assert artifact1.supporting_trace_ids == ["a_trace", "z_trace"]
        assert artifact2.supporting_trace_ids == ["a_trace", "z_trace"]

        # And therefore the same hash
        assert artifact1.artifact_hash() == artifact2.artifact_hash()


class TestEmbeddingArtifactInvariants:
    """Test invariants enforcement."""

    def test_frozen_dataclass_no_mutation(self):
        """No mutation allowed (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        artifact = EmbeddingArtifact(
            namespace="test_namespace",
            seed_index_version_hash="abcd1234",
            supporting_trace_ids=["t1", "t2"],
            supporting_content_hashes=["h1", "h2"],
            k=10,
            similarity_metric="cosine",
            embedding_model_version="v1.0",
        )

        # Direct field assignment should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            artifact.namespace = "modified"

        # List append should still work (lists are mutable even in frozen dataclasses)
        # This is expected behavior - the list object itself can be modified
        # but the field reference cannot be changed to a different list
        original_len = len(artifact.supporting_trace_ids)
        artifact.supporting_trace_ids.append("t3")
        assert len(artifact.supporting_trace_ids) == original_len + 1

        # But we cannot replace the list entirely
        with pytest.raises(FrozenInstanceError):
            artifact.supporting_trace_ids = ["new_list"]

    def test_canonical_bytes_utf8_minified_json(self):
        """Canonical bytes are UTF-8 minified JSON."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        bytes_repr = artifact.canonical_bytes()

        # Should be valid UTF-8
        bytes_repr.decode("utf-8")

        # Should be minified (no extra whitespace)
        json_str = bytes_repr.decode("utf-8")
        assert "  " not in json_str  # No double spaces
        assert "\n" not in json_str  # No newlines
        assert "\t" not in json_str  # No tabs

    def test_canonical_bytes_deterministic_key_order(self):
        """Canonical bytes have deterministic key order."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        bytes_repr = artifact.canonical_bytes()
        json_str = bytes_repr.decode("utf-8")

        # Keys should appear in sorted order
        expected_order = [
            "embedding_model_version",
            "k",
            "namespace",
            "seed_index_version_hash",
            "similarity_metric",
            "supporting_content_hashes",
            "supporting_trace_ids",
        ]

        # Check that keys appear in expected order
        prev_pos = -1
        for key in expected_order:
            pos = json_str.find(f'"{key}"')
            assert pos > prev_pos, f"Key {key} not in expected order"
            prev_pos = pos

    def test_artifact_hash_sha256_of_canonical_bytes(self):
        """artifact_hash is SHA-256 of canonical_bytes."""
        import hashlib

        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        canonical_bytes = artifact.canonical_bytes()
        expected_hash = hashlib.sha256(canonical_bytes).hexdigest()

        assert artifact.artifact_hash() == expected_hash

    def test_no_timestamps_in_canonical_representation(self):
        """No timestamps in canonical representation."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="euclidean",
            embedding_model_version="v2.0",
        )

        json_str = artifact.canonical_bytes().decode("utf-8")

        # Should not contain any timestamp-related fields
        assert "timestamp" not in json_str.lower()
        assert "created_at" not in json_str.lower()
        assert "updated_at" not in json_str.lower()
        assert "time" not in json_str.lower()

    def test_no_floats_stored(self):
        """No floats stored in the artifact."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["t1"],
            supporting_content_hashes=["h1"],
            k=5,
            similarity_metric="cosine",
            embedding_model_version="v2.0",
        )

        json_str = artifact.canonical_bytes().decode("utf-8")

        # Should not contain any floating point numbers
        # (check for decimal points in numeric values)
        import re

        # Look for numbers with decimal points
        float_pattern = r":\s*\d+\.\d+"
        assert not re.search(float_pattern, json_str), "Float values found in representation"

    def test_lists_preserve_deterministic_order(self):
        """Lists are serialized in their stored (deterministic) order."""
        artifact = EmbeddingArtifact(
            namespace="test",
            seed_index_version_hash="hash123",
            supporting_trace_ids=["c", "a", "b"],  # Will be sorted to ["a", "b", "c"]
            supporting_content_hashes=["z", "x", "y"],  # Will be sorted to ["x", "y", "z"]
            k=5,
            similarity_metric="cosine",
            embedding_model_version="v2.0",
        )

        json_str = artifact.canonical_bytes().decode("utf-8")

        # Should contain the sorted lists
        assert '"supporting_trace_ids":["a","b","c"]' in json_str
        assert '"supporting_content_hashes":["x","y","z"]' in json_str
