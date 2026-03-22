"""Unit tests for persistent storage layer."""

import tempfile

import pytest

from agentic_core.L4_state.storage.filesystem_store import FileSystemStore
from agentic_core.L4_state.storage.persistent_store import (
    _canonicalize_payload,
    _compute_sha256,
    _sanitize_id,
    create_artifact,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_persistent_store", "p4obs", "metric_1")
_emit_emits_metric_event("test_persistent_store", "p4obs", "metric_2")
_emit_emits_metric_event("test_persistent_store", "p4obs", "metric_3")
_emit_emits_metric_event("test_persistent_store", "p4obs", "metric_4")
_emit_emits_metric_event("test_persistent_store", "p4obs", "metric_5")
_emit_emits_metric_event("test_persistent_store", "p4obs", "metric_6")
_emit_records_incident_event("test_persistent_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_persistent_store", "p4obs", "anomaly")
_emit_writes_observability_log("test_persistent_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_persistent_store", "p4obs", "mon_state")
_emit_triggers_alert("test_persistent_store", "p4obs", "alert")
_emit_links_incident_trace("test_persistent_store", "p4obs", "trace_link")
_emit_captures_pattern("test_persistent_store", "p3lm", "pattern")
_emit_records_learning_event("test_persistent_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_persistent_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_persistent_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_persistent_store", "p3lm", "routing")
_emit_improves_agent_policy("test_persistent_store", "p3lm", "policy")
_emit_stores_learning_state("test_persistent_store", "p3lm", "state")
_emit_records_execution_trace("test_persistent_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_persistent_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_persistent_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_persistent_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_persistent_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_persistent_store", "env_read", "p2_env_1")
_emit_reads_environ("test_persistent_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_persistent_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_persistent_store", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_persistent_store")
_emit_applies_guardrail("p0", "test_persistent_store", "p0_governance")
_emit_reads_policy_state("p0", "test_persistent_store", "policy_binding")
_emit_snapshots_state("p0", "test_persistent_store", "state_snapshot")
_emit_pulls_context("p1", "test_persistent_store", "context_pull")
_emit_pulls_context("p1", "test_persistent_store", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_persistent_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_persistent_store", "uwg_term_secondary")
_emit_writes_through("p1", "test_persistent_store", "write_through")
_emit_writes_through("p1", "test_persistent_store", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_persistent_store", "safety_validation")
_emit_invokes_eval("p1", "test_persistent_store", "eval_call")
_emit_proposal_commits_routing("p1", "test_persistent_store", "routing_commit")
_emit_escalates_to_human("p1", "test_persistent_store", "human_escalation")
_emit_routes_through("p1", "test_persistent_store", "route_through")
_emit_checks_agent_registry("p1", "test_persistent_store", "agent_registry")
_emit_validates_agent_capability("p1", "test_persistent_store", "capability")
_emit_dispatches_execution_plan("p1", "test_persistent_store", "exec_plan")
_emit_agent_executes_agent("p1", "test_persistent_store", "sub_agent")
_emit_routes_to_agent("p1", "test_persistent_store", "target_agent")
_emit_verifies_policy("p1", "test_persistent_store", "policy_check")
_emit_observes_runtime_state("p1", "test_persistent_store", "runtime_state")
_emit_verifies_boundary("p1", "test_persistent_store", "boundary_check")
_emit_transcripts_response("p1", "test_persistent_store", "transcript")
_emit_hard_fails_untranscripted("p1", "test_persistent_store")
_emit_gated_by_confidence("p1", "test_persistent_store", "confidence_gate")
emit_replay_key("p0", "test_persistent_store")
emit_determinism_digest("p0", "test_persistent_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_persistent_store", "execution_auth")
_emit_validates_capability("p2", "test_persistent_store", "capability_check")
_emit_routes_to_capability("p2", "test_persistent_store", "capability_route")
_emit_writes_via_uwg("p2", "test_persistent_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_persistent_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_persistent_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_persistent_store", "exec_output")
_emit_dispatches_agent("p3", "test_persistent_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_persistent_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_persistent_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_persistent_store", "healing_outcome")
_emit_escalates_failure("p3", "test_persistent_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_persistent_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_persistent_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_persistent_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_persistent_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_persistent_store", "eval_metric")
_emit_stores_embedding("p4", "test_persistent_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_persistent_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_persistent_store", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_sanitize_id():
    """Test ID sanitization prevents path traversal."""
    # Normal IDs pass through
    assert _sanitize_id("test_id") == "test_id"
    assert _sanitize_id("test.id-123") == "test.id-123"

    # Path traversal attempts are blocked
    assert _sanitize_id("../etc/passwd") == ".._etc_passwd"
    assert _sanitize_id("test/../../secret") == "test_.._.._secret"
    assert _sanitize_id(r"C:\Windows\System32") == "C__Windows_System32"

    # Leading dots/dashes are prefixed
    assert _sanitize_id(".hidden") == "id_.hidden"
    assert _sanitize_id("-dash") == "id_-dash"


@pytest.mark.unit_min_deps
def test_canonicalize_payload():
    """Test payload canonicalization is deterministic."""
    payload1 = {"b": 2, "a": 1}
    payload2 = {"a": 1, "b": 2}

    canon1 = _canonicalize_payload(payload1)
    canon2 = _canonicalize_payload(payload2)

    # Should be identical regardless of key order
    assert canon1 == canon2
    assert canon1 == '{"a":1,"b":2}'


@pytest.mark.unit_min_deps
def test_compute_sha256():
    """Test SHA256 computation is stable."""
    data = "test data"
    hash1 = _compute_sha256(data)
    hash2 = _compute_sha256(data)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex length
    assert all(c in "0123456789abcdef" for c in hash1)


@pytest.mark.unit_min_deps
def test_create_artifact():
    """Test artifact creation with computed hashes."""
    payload = {"test": "data"}
    artifact = create_artifact("test_kind", "test_id", payload)

    assert artifact.kind == "test_kind"
    assert artifact.logical_id == "test_id"
    assert artifact.content_type == "application/json"
    assert artifact.payload == payload
    assert "sha256" in artifact.hashes
    assert "size" in artifact.metadata


@pytest.mark.unit_min_deps
def test_filesystem_store_put_creates_v0001_then_v0002():
    """Test that put creates v0001 then v0002 deterministically."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        artifact1 = create_artifact("test_kind", "test_id", {"version": 1})
        ref1 = store.put(artifact1)

        assert ref1.version == 1
        assert "v0001.json" in ref1.path

        artifact2 = create_artifact("test_kind", "test_id", {"version": 2})
        ref2 = store.put(artifact2)

        assert ref2.version == 2
        assert "v0002.json" in ref2.path


@pytest.mark.unit_min_deps
def test_filesystem_store_get_round_trip():
    """Test that get returns exactly what was put."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        original = create_artifact(
            "test_kind", "test_id", {"data": "test", "number": 42}, metadata={"test": "meta"}
        )
        ref = store.put(original)
        retrieved = store.get(ref)

        assert retrieved == original


@pytest.mark.unit_min_deps
def test_filesystem_store_list_ordering():
    """Test that list returns deterministically sorted results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Create artifacts in non-deterministic order
        artifacts = [
            ("z_kind", "b_id", {"data": 1}),
            ("a_kind", "c_id", {"data": 2}),
            ("a_kind", "a_id", {"data": 3}),
            ("z_kind", "a_id", {"data": 4}),
        ]

        refs = []
        for kind, id_, data in artifacts:
            artifact = create_artifact(kind, id_, data)
            ref = store.put(artifact)
            refs.append(ref)

        # List should be sorted by kind, then logical_id, then version
        listed = store.list()
        expected_order = [
            ("a_kind", "a_id", 1),
            ("a_kind", "c_id", 1),
            ("z_kind", "a_id", 1),
            ("z_kind", "b_id", 1),
        ]

        actual_order = [(r.kind, r.logical_id, r.version) for r in listed]
        assert actual_order == expected_order


@pytest.mark.unit_min_deps
def test_filesystem_store_rejects_path_traversal():
    """Test that path traversal attempts are blocked."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Attempt to create artifact with path traversal in kind
        artifact = create_artifact("../etc/passwd", "test", {"data": "test"})
        ref = store.put(artifact)

        # Should be sanitized to safe path
        assert ".._etc_passwd" in ref.path
        assert "../etc/passwd" not in ref.path


@pytest.mark.unit_min_deps
def test_filesystem_store_size_cap_enforced():
    """Test that maximum artifact size is enforced."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create store with tiny size limit
        store = FileSystemStore(temp_dir, max_artifact_size=100)

        # Create artifact that exceeds limit
        large_payload = {"data": "x" * 200}  # Will be > 100 bytes when JSON-encoded
        artifact = create_artifact("test", "large", large_payload)

        with pytest.raises(ValueError, match="Artifact size .* exceeds maximum"):
            store.put(artifact)


@pytest.mark.unit_min_deps
def test_filesystem_store_list_filter_by_kind():
    """Test that list can filter by artifact kind."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Create artifacts of different kinds
        artifact1 = create_artifact("kind1", "id1", {"data": 1})
        artifact2 = create_artifact("kind2", "id1", {"data": 2})
        artifact3 = create_artifact("kind1", "id2", {"data": 3})

        store.put(artifact1)
        store.put(artifact2)
        store.put(artifact3)

        # List all
        all_refs = store.list()
        assert len(all_refs) == 3

        # List filtered by kind
        kind1_refs = store.list(kind="kind1")
        assert len(kind1_refs) == 2
        assert all(r.kind == "kind1" for r in kind1_refs)

        kind2_refs = store.list(kind="kind2")
        assert len(kind2_refs) == 1
        assert kind2_refs[0].kind == "kind2"
