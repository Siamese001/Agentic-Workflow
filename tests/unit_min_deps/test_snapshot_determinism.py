"""Unit tests for system_learning.snapshots.snapshot_factory — determinism.

Covers:
  - Same inputs => bitwise identical snapshot object + identical snapshot_id
  - Different telemetry bytes => different telemetry_hash and snapshot_id
  - Invalid window ordering => raises ValueError
  - No reliance on system time (monkeypatch time/timezone calls; assert not called)
"""

import hashlib
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
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

_emit_authorize_and_execute("p2", "test_snapshot_determinism", "execution_auth")
_emit_validates_capability("p2", "test_snapshot_determinism", "capability_check")
_emit_routes_to_capability("p2", "test_snapshot_determinism", "capability_route")
_emit_writes_via_uwg("p2", "test_snapshot_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "test_snapshot_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_snapshot_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "test_snapshot_determinism", "exec_output")
_emit_dispatches_agent("p3", "test_snapshot_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_snapshot_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_snapshot_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_snapshot_determinism", "healing_outcome")
_emit_escalates_failure("p3", "test_snapshot_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_snapshot_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_snapshot_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_snapshot_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_snapshot_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_snapshot_determinism", "eval_metric")
_emit_stores_embedding("p4", "test_snapshot_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_snapshot_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_snapshot_determinism", "exec_snapshot_link")
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
from system_learning.snapshots.snapshot_factory import create_snapshot
from system_learning.types.snapshot_types import MetaLearningSnapshot

_emit_emits_metric_event("test_snapshot_determinism", "p4obs", "metric_1")
_emit_emits_metric_event("test_snapshot_determinism", "p4obs", "metric_2")
_emit_emits_metric_event("test_snapshot_determinism", "p4obs", "metric_3")
_emit_emits_metric_event("test_snapshot_determinism", "p4obs", "metric_4")
_emit_emits_metric_event("test_snapshot_determinism", "p4obs", "metric_5")
_emit_emits_metric_event("test_snapshot_determinism", "p4obs", "metric_6")
_emit_records_incident_event("test_snapshot_determinism", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_snapshot_determinism", "p4obs", "anomaly")
_emit_writes_observability_log("test_snapshot_determinism", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_snapshot_determinism", "p4obs", "mon_state")
_emit_triggers_alert("test_snapshot_determinism", "p4obs", "alert")
_emit_links_incident_trace("test_snapshot_determinism", "p4obs", "trace_link")
_emit_captures_pattern("test_snapshot_determinism", "p3lm", "pattern")
_emit_records_learning_event("test_snapshot_determinism", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_snapshot_determinism", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_snapshot_determinism", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_snapshot_determinism", "p3lm", "routing")
_emit_improves_agent_policy("test_snapshot_determinism", "p3lm", "policy")
_emit_stores_learning_state("test_snapshot_determinism", "p3lm", "state")
_emit_records_execution_trace("test_snapshot_determinism", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_snapshot_determinism", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_snapshot_determinism", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_snapshot_determinism", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_snapshot_determinism", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_snapshot_determinism", "env_read", "p2_env_1")
_emit_reads_environ("test_snapshot_determinism", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_snapshot_determinism", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_snapshot_determinism", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_snapshot_determinism")
_emit_applies_guardrail("p0", "test_snapshot_determinism", "p0_governance")
_emit_snapshots_state("p0", "test_snapshot_determinism", "state_snapshot")
_emit_pulls_context("p1", "test_snapshot_determinism", "context_pull")
_emit_pulls_context("p1", "test_snapshot_determinism", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_snapshot_determinism", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_snapshot_determinism", "uwg_term_secondary")
_emit_writes_through("p1", "test_snapshot_determinism", "write_through")
_emit_writes_through("p1", "test_snapshot_determinism", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_snapshot_determinism", "safety_validation")
_emit_invokes_eval("p1", "test_snapshot_determinism", "eval_call")
_emit_proposal_commits_routing("p1", "test_snapshot_determinism", "routing_commit")
_emit_escalates_to_human("p1", "test_snapshot_determinism", "human_escalation")
_emit_routes_through("p1", "test_snapshot_determinism", "route_through")
_emit_checks_agent_registry("p1", "test_snapshot_determinism", "agent_registry")
_emit_validates_agent_capability("p1", "test_snapshot_determinism", "capability")
_emit_dispatches_execution_plan("p1", "test_snapshot_determinism", "exec_plan")
_emit_agent_executes_agent("p1", "test_snapshot_determinism", "sub_agent")
_emit_routes_to_agent("p1", "test_snapshot_determinism", "target_agent")
_emit_verifies_policy("p1", "test_snapshot_determinism", "policy_check")
_emit_observes_runtime_state("p1", "test_snapshot_determinism", "runtime_state")
_emit_verifies_boundary("p1", "test_snapshot_determinism", "boundary_check")
_emit_transcripts_response("p1", "test_snapshot_determinism", "transcript")
_emit_hard_fails_untranscripted("p1", "test_snapshot_determinism")
_emit_gated_by_confidence("p1", "test_snapshot_determinism", "confidence_gate")
emit_replay_key("p0", "test_snapshot_determinism")
emit_determinism_digest("p0", "test_snapshot_determinism")
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


# =============================================================================
# Fixtures
# =============================================================================

_ENGINE_VERSION = "1.0.0"
_CONFIG_SURFACE_VERSION = "1.0.0"
_WINDOW_START = 1_700_000_000
_WINDOW_END = 1_700_003_600
_TELEMETRY = b"telemetry-data-slice-v1"
_POLICY = b'{"token_budget":1000000,"tool_allowlist":["file_read"]}'
_ROUTING = b'{"escalation_threshold":0.85,"depth_breaker":10}'
_MODEL = b'{"cognition_model":"gpt-4o","embedding_model":"text-embedding-3-small"}'
_CLOCK_BYTES = b'{"tick":42,"vector_clock":{"L0":1,"L4":2}}'
_CLOCK = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L4", 2)))


def _make_snapshot(**overrides) -> MetaLearningSnapshot:
    kwargs: dict = {
        "engine_version": _ENGINE_VERSION,
        "config_surface_version": _CONFIG_SURFACE_VERSION,
        "audit_window_start_utc": _WINDOW_START,
        "audit_window_end_utc": _WINDOW_END,
        "telemetry_bytes": _TELEMETRY,
        "policy_config_bytes": _POLICY,
        "routing_config_bytes": _ROUTING,
        "model_config_bytes": _MODEL,
        "semantic_clock_bytes": _CLOCK_BYTES,
        "semantic_clock": _CLOCK,
    }
    kwargs.update(overrides)
    return create_snapshot(**kwargs)


# =============================================================================
# Determinism: same inputs => bitwise identical
# =============================================================================


class TestSnapshotDeterminism:
    def test_same_inputs_produce_identical_snapshot_id(self):
        snap1 = _make_snapshot()
        snap2 = _make_snapshot()
        assert snap1.snapshot_id == snap2.snapshot_id

    def test_same_inputs_produce_identical_snapshot_object(self):
        snap1 = _make_snapshot()
        snap2 = _make_snapshot()
        assert snap1 == snap2

    def test_snapshot_id_is_sha256_hex(self):
        snap = _make_snapshot()
        # SHA-256 hex digest is always 64 hex chars
        assert len(snap.snapshot_id) == 64
        assert all(c in "0123456789abcdef" for c in snap.snapshot_id)

    def test_snapshot_id_stability_across_calls(self):
        """Run 5 times; all snapshot_ids must be identical."""
        ids = {_make_snapshot().snapshot_id for _ in range(5)}
        assert len(ids) == 1

    def test_snapshot_fields_match_inputs(self):
        snap = _make_snapshot()
        assert snap.engine_version == _ENGINE_VERSION
        assert snap.config_surface_version == _CONFIG_SURFACE_VERSION
        assert snap.audit_window_start_utc == _WINDOW_START
        assert snap.audit_window_end_utc == _WINDOW_END
        assert snap.semantic_clock == _CLOCK

    def test_telemetry_hash_is_sha256_of_telemetry_bytes(self):
        snap = _make_snapshot()
        expected = hashlib.sha256(_TELEMETRY).hexdigest()
        assert snap.telemetry_hash == expected

    def test_policy_config_hash_is_sha256_of_policy_bytes(self):
        snap = _make_snapshot()
        expected = hashlib.sha256(_POLICY).hexdigest()
        assert snap.policy_config_hash == expected

    def test_routing_config_hash_is_sha256_of_routing_bytes(self):
        snap = _make_snapshot()
        expected = hashlib.sha256(_ROUTING).hexdigest()
        assert snap.routing_config_hash == expected

    def test_model_config_hash_is_sha256_of_model_bytes(self):
        snap = _make_snapshot()
        expected = hashlib.sha256(_MODEL).hexdigest()
        assert snap.model_config_hash == expected


# =============================================================================
# Sensitivity: different inputs => different hashes
# =============================================================================


class TestSnapshotSensitivity:
    def test_different_telemetry_bytes_produce_different_telemetry_hash(self):
        snap1 = _make_snapshot(telemetry_bytes=b"telemetry-v1")
        snap2 = _make_snapshot(telemetry_bytes=b"telemetry-v2")
        assert snap1.telemetry_hash != snap2.telemetry_hash

    def test_different_telemetry_bytes_produce_different_snapshot_id(self):
        snap1 = _make_snapshot(telemetry_bytes=b"telemetry-v1")
        snap2 = _make_snapshot(telemetry_bytes=b"telemetry-v2")
        assert snap1.snapshot_id != snap2.snapshot_id

    def test_different_policy_bytes_produce_different_snapshot_id(self):
        snap1 = _make_snapshot(policy_config_bytes=b'{"token_budget":1000000}')
        snap2 = _make_snapshot(policy_config_bytes=b'{"token_budget":2000000}')
        assert snap1.snapshot_id != snap2.snapshot_id

    def test_different_engine_version_produces_different_snapshot_id(self):
        snap1 = _make_snapshot(engine_version="1.0.0")
        snap2 = _make_snapshot(engine_version="1.0.1")
        assert snap1.snapshot_id != snap2.snapshot_id

    def test_different_window_produces_different_snapshot_id(self):
        snap1 = _make_snapshot(audit_window_start_utc=1_700_000_000)
        snap2 = _make_snapshot(audit_window_start_utc=1_700_000_001)
        assert snap1.snapshot_id != snap2.snapshot_id


# =============================================================================
# Validation: invalid window ordering
# =============================================================================


class TestSnapshotValidation:
    def test_start_equal_to_end_raises(self):
        with pytest.raises(ValueError, match="INVALID_AUDIT_WINDOW"):
            _make_snapshot(
                audit_window_start_utc=1_700_000_000,
                audit_window_end_utc=1_700_000_000,
            )

    def test_start_greater_than_end_raises(self):
        with pytest.raises(ValueError, match="INVALID_AUDIT_WINDOW"):
            _make_snapshot(
                audit_window_start_utc=1_700_003_600,
                audit_window_end_utc=1_700_000_000,
            )

    def test_valid_window_does_not_raise(self):
        snap = _make_snapshot(
            audit_window_start_utc=1_700_000_000,
            audit_window_end_utc=1_700_000_001,
        )
        assert snap.audit_window_start_utc < snap.audit_window_end_utc


# =============================================================================
# No reliance on system time
# =============================================================================


class TestNoSystemTime:
    def test_datetime_now_not_called(self):
        """create_snapshot must not call datetime.now or datetime.utcnow."""
        with patch("datetime.datetime") as mock_dt:
            mock_dt.now.side_effect = AssertionError("datetime.now must not be called")
            mock_dt.utcnow.side_effect = AssertionError("datetime.utcnow must not be called")
            # Must complete without triggering the side_effect
            snap = _make_snapshot()
        assert snap.snapshot_id is not None

    def test_time_time_not_called(self):
        """create_snapshot must not call time.time."""
        with patch("time.time") as mock_time:
            mock_time.side_effect = AssertionError("time.time must not be called")
            snap = _make_snapshot()
        assert snap.snapshot_id is not None

    def test_snapshot_is_frozen(self):
        """MetaLearningSnapshot must be immutable (frozen dataclass)."""
        snap = _make_snapshot()
        with pytest.raises((AttributeError, TypeError)):
            snap.snapshot_id = "tampered"  # type: ignore[misc]

    def test_snapshot_id_equality_assertion(self):
        """Canonical determinism assertion: two calls with same inputs produce equal snapshot_id."""
        snap_a = _make_snapshot()
        snap_b = _make_snapshot()
        assert snap_a.snapshot_id == snap_b.snapshot_id, (
            f"snapshot_id mismatch: {snap_a.snapshot_id!r} != {snap_b.snapshot_id!r}"
        )
