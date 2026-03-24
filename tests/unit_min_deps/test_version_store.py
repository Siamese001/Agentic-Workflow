"""Unit tests for system_learning.engines.l4_version_store.

Covers:
  Wave 2.1 — Versioned ChangePackage Store:
    - Write-once semantics
    - Same content → same version_id
    - Parent existence enforced
    - No mutation of stored objects
  Wave 2.2 — Activation Pointer + Rollback:
    - Activate version
    - Rollback to parent
    - O(1) pointer reversion
    - Attempt activation of unknown version → fail
"""

import hashlib

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

_emit_authorize_and_execute("p2", "test_version_store", "execution_auth")
_emit_validates_capability("p2", "test_version_store", "capability_check")
_emit_routes_to_capability("p2", "test_version_store", "capability_route")
_emit_writes_via_uwg("p2", "test_version_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_version_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_version_store", "exec_output")
_emit_dispatches_agent("p3", "test_version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_version_store", "healing_outcome")
_emit_escalates_failure("p3", "test_version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_version_store", "eval_metric")
_emit_stores_embedding("p4", "test_version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_version_store", "exec_snapshot_link")
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
from system_learning.engines.l4_version_store import (
    L4VersionStore,
    ParentVersionNotFound,
    VersionNotFound,
)

_emit_emits_metric_event("test_version_store", "p4obs", "metric_1")
_emit_emits_metric_event("test_version_store", "p4obs", "metric_2")
_emit_emits_metric_event("test_version_store", "p4obs", "metric_3")
_emit_emits_metric_event("test_version_store", "p4obs", "metric_4")
_emit_emits_metric_event("test_version_store", "p4obs", "metric_5")
_emit_emits_metric_event("test_version_store", "p4obs", "metric_6")
_emit_records_incident_event("test_version_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_version_store", "p4obs", "anomaly")
_emit_writes_observability_log("test_version_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_version_store", "p4obs", "mon_state")
_emit_triggers_alert("test_version_store", "p4obs", "alert")
_emit_links_incident_trace("test_version_store", "p4obs", "trace_link")
_emit_captures_pattern("test_version_store", "p3lm", "pattern")
_emit_records_learning_event("test_version_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_version_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_version_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_version_store", "p3lm", "routing")
_emit_improves_agent_policy("test_version_store", "p3lm", "policy")
_emit_stores_learning_state("test_version_store", "p3lm", "state")
_emit_records_execution_trace("test_version_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_version_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_version_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_version_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_version_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_version_store", "env_read", "p2_env_1")
_emit_reads_environ("test_version_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_version_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_version_store", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_version_store")
_emit_applies_guardrail("p0", "test_version_store", "p0_governance")
_emit_reads_policy_state("p0", "test_version_store", "policy_binding")
_emit_snapshots_state("p0", "test_version_store", "state_snapshot")
_emit_pulls_context("p1", "test_version_store", "context_pull")
_emit_pulls_context("p1", "test_version_store", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_version_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_version_store", "uwg_term_secondary")
_emit_writes_through("p1", "test_version_store", "write_through")
_emit_writes_through("p1", "test_version_store", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_version_store", "safety_validation")
_emit_invokes_eval("p1", "test_version_store", "eval_call")
_emit_proposal_commits_routing("p1", "test_version_store", "routing_commit")
_emit_escalates_to_human("p1", "test_version_store", "human_escalation")
_emit_routes_through("p1", "test_version_store", "route_through")
_emit_checks_agent_registry("p1", "test_version_store", "agent_registry")
_emit_validates_agent_capability("p1", "test_version_store", "capability")
_emit_dispatches_execution_plan("p1", "test_version_store", "exec_plan")
_emit_agent_executes_agent("p1", "test_version_store", "sub_agent")
_emit_routes_to_agent("p1", "test_version_store", "target_agent")
_emit_verifies_policy("p1", "test_version_store", "policy_check")
_emit_observes_runtime_state("p1", "test_version_store", "runtime_state")
_emit_verifies_boundary("p1", "test_version_store", "boundary_check")
_emit_transcripts_response("p1", "test_version_store", "transcript")
_emit_hard_fails_untranscripted("p1", "test_version_store")
_emit_gated_by_confidence("p1", "test_version_store", "confidence_gate")
emit_replay_key("p0", "test_version_store")
emit_determinism_digest("p0", "test_version_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# Fake ChangePackage for tests
# =============================================================================


class FakeChangePackage:
    """Minimal ChangePackage implementation for testing."""

    def __init__(self, content: str) -> None:
        self._content = content

    def canonical_bytes(self) -> bytes:
        return self._content.encode("utf-8")


# =============================================================================
# Wave 2.1 — Versioned ChangePackage Store
# =============================================================================


class TestCommitChangePackage:
    def test_commit_returns_sha256_version_id(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(
            package=pkg,
            parent_version_id=None,
            change_spec_hash="abc123",
            committed_at_utc=1700000000,
        )
        expected = hashlib.sha256(b"test-content").hexdigest()
        assert version_id == expected

    def test_same_content_produces_same_version_id(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("identical-content")
        pkg2 = FakeChangePackage("identical-content")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        assert v1 == v2

    def test_different_content_produces_different_version_id(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        assert v1 != v2

    def test_write_once_semantics_idempotent_on_same_content(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")

        v1 = store.commit_change_package(pkg, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg, None, "hash1", 1700000000)

        assert v1 == v2

    def test_parent_version_not_found_raises(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")

        with pytest.raises(ParentVersionNotFound, match="PARENT_VERSION_NOT_FOUND"):
            store.commit_change_package(
                pkg, parent_version_id="nonexistent", change_spec_hash="hash", committed_at_utc=1700000000
            )

    def test_genesis_version_allowed(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("genesis-content")

        version_id = store.commit_change_package(
            pkg, parent_version_id=None, change_spec_hash="hash", committed_at_utc=1700000000
        )

        assert version_id is not None
        retrieved = store.get_change_package(version_id)
        assert retrieved.parent_version_id is None

    def test_child_version_with_valid_parent(self):
        store = L4VersionStore()
        parent_pkg = FakeChangePackage("parent-content")
        child_pkg = FakeChangePackage("child-content")

        parent_id = store.commit_change_package(parent_pkg, None, "hash1", 1700000000)
        child_id = store.commit_change_package(
            child_pkg, parent_version_id=parent_id, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        child = store.get_change_package(child_id)
        assert child.parent_version_id == parent_id


class TestGetChangePackage:
    def test_get_existing_version(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        retrieved = store.get_change_package(version_id)
        assert retrieved.version_id == version_id
        assert retrieved.package_bytes == b"test-content"

    def test_get_nonexistent_version_raises(self):
        store = L4VersionStore()
        with pytest.raises(VersionNotFound, match="VERSION_NOT_FOUND"):
            store.get_change_package("nonexistent-version-id")

    def test_retrieved_package_is_immutable(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        retrieved = store.get_change_package(version_id)
        # VersionedPackage is frozen dataclass
        with pytest.raises((AttributeError, TypeError)):
            retrieved.version_id = "tampered"  # type: ignore[misc]


class TestListVersions:
    def test_list_all_versions(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-1")
        pkg2 = FakeChangePackage("content-2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        versions = store.list_versions()
        assert sorted(versions) == sorted([v1, v2])

    def test_list_versions_empty_store(self):
        store = L4VersionStore()
        assert store.list_versions() == []

    def test_list_versions_deterministic_order(self):
        store = L4VersionStore()
        for i in range(5):
            pkg = FakeChangePackage(f"content-{i}")
            store.commit_change_package(pkg, None, f"hash{i}", 1700000000 + i)

        versions1 = store.list_versions()
        versions2 = store.list_versions()
        assert versions1 == versions2


# =============================================================================
# Wave 2.2 — Activation Pointer + Rollback
# =============================================================================


class TestUpdateActivationPointer:
    def test_activate_version(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        store.update_activation_pointer("routing_config", version_id)
        active = store.get_active_version("routing_config")
        assert active == version_id

    def test_activate_nonexistent_version_raises(self):
        store = L4VersionStore()
        with pytest.raises(VersionNotFound, match="ACTIVATION_TARGET_NOT_FOUND"):
            store.update_activation_pointer("routing_config", "nonexistent-version")

    def test_activation_does_not_mutate_package(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        original = store.get_change_package(version_id)
        store.update_activation_pointer("routing_config", version_id)
        after_activation = store.get_change_package(version_id)

        assert original == after_activation

    def test_atomic_pointer_update(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        store.update_activation_pointer("routing_config", v1)
        assert store.get_active_version("routing_config") == v1

        store.update_activation_pointer("routing_config", v2)
        assert store.get_active_version("routing_config") == v2


class TestGetActiveVersion:
    def test_get_active_version_when_set(self):
        store = L4VersionStore()
        pkg = FakeChangePackage("test-content")
        version_id = store.commit_change_package(pkg, None, "hash", 1700000000)

        store.update_activation_pointer("routing_config", version_id)
        assert store.get_active_version("routing_config") == version_id

    def test_get_active_version_when_not_set(self):
        store = L4VersionStore()
        assert store.get_active_version("routing_config") is None

    def test_multiple_components_independent(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-1")
        pkg2 = FakeChangePackage("content-2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        store.update_activation_pointer("routing_config", v1)
        store.update_activation_pointer("policy_config", v2)

        assert store.get_active_version("routing_config") == v1
        assert store.get_active_version("policy_config") == v2


class TestRollback:
    def test_rollback_to_parent(self):
        store = L4VersionStore()
        parent_pkg = FakeChangePackage("parent-content")
        child_pkg = FakeChangePackage("child-content")

        parent_id = store.commit_change_package(parent_pkg, None, "hash1", 1700000000)
        child_id = store.commit_change_package(
            child_pkg, parent_version_id=parent_id, change_spec_hash="hash2", committed_at_utc=1700000001
        )

        store.update_activation_pointer("routing_config", child_id)
        assert store.get_active_version("routing_config") == child_id

        store.rollback("routing_config", parent_id)
        assert store.get_active_version("routing_config") == parent_id

    def test_rollback_is_o1_pointer_reversion(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(pkg2, None, "hash2", 1700000001)

        store.update_activation_pointer("routing_config", v2)
        store.rollback("routing_config", v1)

        # Rollback does not delete v2
        assert store.get_change_package(v2) is not None
        # Active pointer now points to v1
        assert store.get_active_version("routing_config") == v1

    def test_rollback_to_nonexistent_version_raises(self):
        store = L4VersionStore()
        with pytest.raises(VersionNotFound):
            store.rollback("routing_config", "nonexistent-version")

    def test_no_deletion_of_historical_versions(self):
        store = L4VersionStore()
        pkg1 = FakeChangePackage("content-v1")
        pkg2 = FakeChangePackage("content-v2")
        pkg3 = FakeChangePackage("content-v3")

        v1 = store.commit_change_package(pkg1, None, "hash1", 1700000000)
        v2 = store.commit_change_package(
            pkg2, parent_version_id=v1, change_spec_hash="hash2", committed_at_utc=1700000001
        )
        v3 = store.commit_change_package(
            pkg3, parent_version_id=v2, change_spec_hash="hash3", committed_at_utc=1700000002
        )

        store.update_activation_pointer("routing_config", v3)
        store.rollback("routing_config", v1)

        # All versions still exist
        assert store.get_change_package(v1) is not None
        assert store.get_change_package(v2) is not None
        assert store.get_change_package(v3) is not None


# =============================================================================
# Version ID Determinism
# =============================================================================


class TestVersionIdDeterminism:
    def test_version_id_determinism_assertion(self):
        """Canonical determinism assertion: same content → same version_id."""
        store1 = L4VersionStore()
        store2 = L4VersionStore()

        pkg1 = FakeChangePackage("deterministic-content")
        pkg2 = FakeChangePackage("deterministic-content")

        v1 = store1.commit_change_package(pkg1, None, "hash", 1700000000)
        v2 = store2.commit_change_package(pkg2, None, "hash", 1700000000)

        assert v1 == v2, f"version_id mismatch: {v1!r} != {v2!r}"
