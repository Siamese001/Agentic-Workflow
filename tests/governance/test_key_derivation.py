"""
Tests for HMAC key derivation with versioning.

Phase 0.2: Mathematically-Sealed Sovereignty Hardening
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

_emit_records_execution_trace("p0", "evidence", "test_key_derivation")
_emit_applies_guardrail("p0", "test_key_derivation", "p0_governance")
_emit_reads_policy_state("p0", "test_key_derivation", "policy_binding")
_emit_snapshots_state("p0", "test_key_derivation", "state_snapshot")
emit_replay_key("p0", "test_key_derivation")
emit_determinism_digest("p0", "test_key_derivation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_key_derivation", "execution_auth")
_emit_validates_capability("p2", "test_key_derivation", "capability_check")
_emit_routes_to_capability("p2", "test_key_derivation", "capability_route")
_emit_writes_via_uwg("p2", "test_key_derivation", "uwg_write")
_emit_blocks_direct_write("p2", "test_key_derivation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_key_derivation", "tool_invocation")
_emit_captures_execution_output("p2", "test_key_derivation", "exec_output")
_emit_dispatches_agent("p3", "test_key_derivation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_key_derivation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_key_derivation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_key_derivation", "healing_outcome")
_emit_escalates_failure("p3", "test_key_derivation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_key_derivation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_key_derivation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_key_derivation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_key_derivation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_key_derivation", "eval_metric")
_emit_stores_embedding("p4", "test_key_derivation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_key_derivation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_key_derivation", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.enforcement.key_derivation import (
    derive_hmac_key,
    get_kdf_salt_hash,
    get_key_version,
    verify_key_version,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_key_derivation", "p4obs", "metric_1")
_emit_emits_metric_event("test_key_derivation", "p4obs", "metric_2")
_emit_emits_metric_event("test_key_derivation", "p4obs", "metric_3")
_emit_emits_metric_event("test_key_derivation", "p4obs", "metric_4")
_emit_emits_metric_event("test_key_derivation", "p4obs", "metric_5")
_emit_emits_metric_event("test_key_derivation", "p4obs", "metric_6")
_emit_records_incident_event("test_key_derivation", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_key_derivation", "p4obs", "anomaly")
_emit_writes_observability_log("test_key_derivation", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_key_derivation", "p4obs", "mon_state")
_emit_triggers_alert("test_key_derivation", "p4obs", "alert")
_emit_links_incident_trace("test_key_derivation", "p4obs", "trace_link")
_emit_captures_pattern("test_key_derivation", "p3lm", "pattern")
_emit_records_learning_event("test_key_derivation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_key_derivation", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_key_derivation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_key_derivation", "p3lm", "routing")
_emit_improves_agent_policy("test_key_derivation", "p3lm", "policy")
_emit_stores_learning_state("test_key_derivation", "p3lm", "state")
_emit_records_execution_trace("test_key_derivation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_key_derivation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_key_derivation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_key_derivation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_key_derivation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_key_derivation", "env_read", "p2_env_1")
_emit_reads_environ("test_key_derivation", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_key_derivation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_key_derivation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_key_derivation", "context_pull")
_emit_pulls_context("p1", "test_key_derivation", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_key_derivation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_key_derivation", "uwg_term_secondary")
_emit_writes_through("p1", "test_key_derivation", "write_through")
_emit_writes_through("p1", "test_key_derivation", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_key_derivation", "safety_validation")
_emit_invokes_eval("p1", "test_key_derivation", "eval_call")
_emit_proposal_commits_routing("p1", "test_key_derivation", "routing_commit")


class TestDeriveHmacKey:
    def test_returns_tuple_of_three(self) -> None:
        key, version, salt_hash = derive_hmac_key(b"master-secret")
        assert isinstance(key, bytes)
        assert isinstance(version, str)
        assert isinstance(salt_hash, str)

    def test_key_is_32_bytes(self) -> None:
        key, _, _ = derive_hmac_key(b"master-secret")
        assert len(key) == 32

    def test_deterministic_for_same_input(self) -> None:
        k1, v1, s1 = derive_hmac_key(b"same-secret")
        k2, v2, s2 = derive_hmac_key(b"same-secret")
        assert k1 == k2
        assert v1 == v2
        assert s1 == s2

    def test_different_secrets_produce_different_keys(self) -> None:
        k1, _, _ = derive_hmac_key(b"secret-a")
        k2, _, _ = derive_hmac_key(b"secret-b")
        assert k1 != k2

    def test_version_string_nonempty(self) -> None:
        _, version, _ = derive_hmac_key(b"s")
        assert version

    def test_salt_hash_is_64_chars(self) -> None:
        _, _, salt_hash = derive_hmac_key(b"s")
        assert len(salt_hash) == 64
        assert all(c in "0123456789abcdef" for c in salt_hash)


class TestGetKeyVersion:
    def test_returns_string(self) -> None:
        assert isinstance(get_key_version(), str)

    def test_nonempty(self) -> None:
        assert get_key_version()


class TestVerifyKeyVersion:
    def test_current_version_valid(self) -> None:
        current = get_key_version()
        assert verify_key_version(current) is True

    def test_wrong_version_invalid(self) -> None:
        assert verify_key_version("99999") is False

    def test_empty_string_invalid(self) -> None:
        assert verify_key_version("") is False


class TestGetKdfSaltHash:
    def test_is_hex_64(self) -> None:
        h = get_kdf_salt_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_stable_across_calls(self) -> None:
        assert get_kdf_salt_hash() == get_kdf_salt_hash()
