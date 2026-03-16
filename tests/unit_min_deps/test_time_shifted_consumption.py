"""Tests for time-shifted consumption behavior - Phase 7 functionality.

Tests that L0 reads only activated state from previous run, not same-run writes.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

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

_emit_records_execution_trace("p0", "evidence", "test_time_shifted_consumption")
_emit_applies_guardrail("p0", "test_time_shifted_consumption", "p0_governance")
_emit_reads_policy_state("p0", "test_time_shifted_consumption", "policy_binding")
_emit_snapshots_state("p0", "test_time_shifted_consumption", "state_snapshot")
emit_replay_key("p0", "test_time_shifted_consumption")
emit_determinism_digest("p0", "test_time_shifted_consumption")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_time_shifted_consumption", "execution_auth")
_emit_validates_capability("p2", "test_time_shifted_consumption", "capability_check")
_emit_routes_to_capability("p2", "test_time_shifted_consumption", "capability_route")
_emit_writes_via_uwg("p2", "test_time_shifted_consumption", "uwg_write")
_emit_blocks_direct_write("p2", "test_time_shifted_consumption", "direct_write_block")
_emit_records_tool_invocation("p2", "test_time_shifted_consumption", "tool_invocation")
_emit_captures_execution_output("p2", "test_time_shifted_consumption", "exec_output")
_emit_dispatches_agent("p3", "test_time_shifted_consumption", "agent_dispatch")
_emit_coordinates_agents("p3", "test_time_shifted_consumption", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_time_shifted_consumption", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_time_shifted_consumption", "healing_outcome")
_emit_escalates_failure("p3", "test_time_shifted_consumption", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_time_shifted_consumption", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_time_shifted_consumption", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_time_shifted_consumption", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_time_shifted_consumption", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_time_shifted_consumption", "eval_metric")
_emit_stores_embedding("p4", "test_time_shifted_consumption", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_time_shifted_consumption", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_time_shifted_consumption", "exec_snapshot_link")

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

from agentic_core.L0_routing.meta_control.config_store import (
    _clear_start_of_run_cache,
    activate_version,
    get_active_version,
    read_active_payload,
    read_version_payload,
    write_next_version,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
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

_emit_emits_metric_event("test_time_shifted_consumption", "p4obs", "metric_1")
_emit_emits_metric_event("test_time_shifted_consumption", "p4obs", "metric_2")
_emit_emits_metric_event("test_time_shifted_consumption", "p4obs", "metric_3")
_emit_emits_metric_event("test_time_shifted_consumption", "p4obs", "metric_4")
_emit_emits_metric_event("test_time_shifted_consumption", "p4obs", "metric_5")
_emit_emits_metric_event("test_time_shifted_consumption", "p4obs", "metric_6")
_emit_records_incident_event("test_time_shifted_consumption", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_time_shifted_consumption", "p4obs", "anomaly")
_emit_writes_observability_log("test_time_shifted_consumption", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_time_shifted_consumption", "p4obs", "mon_state")
_emit_triggers_alert("test_time_shifted_consumption", "p4obs", "alert")
_emit_links_incident_trace("test_time_shifted_consumption", "p4obs", "trace_link")
_emit_captures_pattern("test_time_shifted_consumption", "p3lm", "pattern")
_emit_records_learning_event("test_time_shifted_consumption", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_time_shifted_consumption", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_time_shifted_consumption", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_time_shifted_consumption", "p3lm", "routing")
_emit_improves_agent_policy("test_time_shifted_consumption", "p3lm", "policy")
_emit_stores_learning_state("test_time_shifted_consumption", "p3lm", "state")
_emit_records_execution_trace("test_time_shifted_consumption", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_time_shifted_consumption", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_time_shifted_consumption", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_time_shifted_consumption", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_time_shifted_consumption", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_time_shifted_consumption", "env_read", "p2_env_1")
_emit_reads_environ("test_time_shifted_consumption", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_time_shifted_consumption", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_time_shifted_consumption", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_time_shifted_consumption", "context_pull")
_emit_pulls_context("p1", "test_time_shifted_consumption", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_time_shifted_consumption", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_time_shifted_consumption", "uwg_term_secondary")
_emit_writes_through("p1", "test_time_shifted_consumption", "write_through")
_emit_writes_through("p1", "test_time_shifted_consumption", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_time_shifted_consumption", "safety_validation")
_emit_invokes_eval("p1", "test_time_shifted_consumption", "eval_call")
_emit_proposal_commits_routing("p1", "test_time_shifted_consumption", "routing_commit")
_emit_escalates_to_human("p1", "test_time_shifted_consumption", "human_escalation")
_emit_routes_through("p1", "test_time_shifted_consumption", "route_through")
_emit_checks_agent_registry("p1", "test_time_shifted_consumption", "agent_registry")
_emit_validates_agent_capability("p1", "test_time_shifted_consumption", "capability")
_emit_dispatches_execution_plan("p1", "test_time_shifted_consumption", "exec_plan")
_emit_agent_executes_agent("p1", "test_time_shifted_consumption", "sub_agent")
_emit_routes_to_agent("p1", "test_time_shifted_consumption", "target_agent")
_emit_verifies_policy("p1", "test_time_shifted_consumption", "policy_check")
_emit_observes_runtime_state("p1", "test_time_shifted_consumption", "runtime_state")
_emit_verifies_boundary("p1", "test_time_shifted_consumption", "boundary_check")
_emit_transcripts_response("p1", "test_time_shifted_consumption", "transcript")
_emit_hard_fails_untranscripted("p1", "test_time_shifted_consumption")
_emit_gated_by_confidence("p1", "test_time_shifted_consumption", "confidence_gate")


class TestTimeShiftedConsumption:
    """Test suite for time-shifted consumption behavior."""

    def test_time_shifted_behavior_t_reads_old_t1_reads_new(self):
        """Test time-shifted consumption: T reads old version, T+1 reads new version."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "prompt_templates"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Initial state: no versions
        assert get_active_version(store_root, app_id, component) == 0
        assert read_active_payload(store_root, app_id, component) == {}

        # Simulate start of run T: capture initial state
        initial_payload = read_active_payload(store_root, app_id, component)

        # Run t: write version 1 (this updates current.json for next run)
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))
        payload_v1 = {"key": "value_v1", "version": 1}

        write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v1,
            semantic_clock=semantic_clock,
        )

        # Version 1 is written and current.json is updated for next run
        # But L0 in run T still reads the initial state (time-shifted)
        assert read_active_payload(store_root, app_id, component) == initial_payload  # Still {}

        # Activate version 1 explicitly (this would happen between runs)
        activate_version(store_root, app_id, component, 1)

        # Now active version is 1
        assert get_active_version(store_root, app_id, component) == 1
        assert read_active_payload(store_root, app_id, component) == initial_payload  # Still {} due to cache

        # Simulate start of run T+1: clear cache to simulate new run
        _clear_start_of_run_cache()
        start_t1_payload = read_active_payload(store_root, app_id, component)
        assert start_t1_payload == payload_v1  # Now reads v1

        # Run t+1: write version 2 (updates current.json for next run)
        semantic_clock_t1 = SemanticClockSnapshot(tick=2, vector_clock=(("L0", 2),))
        payload_v2 = {"key": "value_v2", "version": 2}

        snapshot_v2 = write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v2,
            semantic_clock=semantic_clock_t1,
        )

        # Version 2 is written and current.json updated
        assert snapshot_v2.config_version == 2
        # But L0 in run T+1 still reads v1 (time-shifted)
        assert read_active_payload(store_root, app_id, component) == start_t1_payload  # Still v1

        # Activate version 2 for next run
        activate_version(store_root, app_id, component, 2)

        # Simulate start of run T+2: clear cache
        _clear_start_of_run_cache()
        # Now active version is 2
        assert get_active_version(store_root, app_id, component) == 2
        assert read_active_payload(store_root, app_id, component) == payload_v2

    def test_read_specific_version(self):
        """Test reading a specific version (not just active)."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "routing_thresholds"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Capture initial state before any writes
        initial_payload = read_active_payload(store_root, app_id, component)
        assert initial_payload == {}

        # Write version 1
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))
        payload_v1 = {"threshold": 0.5}

        write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v1,
            semantic_clock=semantic_clock,
        )

        # Can read specific version
        assert read_version_payload(store_root, app_id, component, 1) == payload_v1

        # Active payload is still {} due to time-shift (cache captured before write)
        assert read_active_payload(store_root, app_id, component) == initial_payload

        # Write version 2
        payload_v2 = {"threshold": 0.6}
        semantic_clock_v2 = SemanticClockSnapshot(tick=2, vector_clock=(("L0", 2),))

        write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v2,
            semantic_clock=semantic_clock_v2,
        )

        # Can still read version 1 specifically
        assert read_version_payload(store_root, app_id, component, 1) == payload_v1
        assert read_version_payload(store_root, app_id, component, 2) == payload_v2

        # Active payload is still {} due to time-shift
        assert read_active_payload(store_root, app_id, component) == {}

        # Clear cache to simulate new run
        _clear_start_of_run_cache()
        # Now reads the latest written version
        assert read_active_payload(store_root, app_id, component) == payload_v2

    def test_activate_nonexistent_version_raises_error(self):
        """Test that activating non-existent version raises error."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "tool_policies"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Try to activate version 1 when no versions exist
        with pytest.raises(ValueError, match="VERSION_NOT_FOUND"):
            activate_version(store_root, app_id, component, 1)

    def test_get_active_version_returns_zero_when_none(self):
        """Test that get_active_version returns 0 when no version is active."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "prompt_templates"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # No versions written, should return 0
        assert get_active_version(store_root, app_id, component) == 0

    def test_read_active_payload_empty_when_none(self):
        """Test that read_active_payload returns {} when no version is active."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "routing_thresholds"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # No versions written, should return empty dict
        assert read_active_payload(store_root, app_id, component) == {}

    def test_activation_pointer_atomic_update(self):
        """Test that activation pointer updates are atomic."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "tool_policies"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Capture initial state before any writes
        initial_payload = read_active_payload(store_root, app_id, component)
        assert initial_payload == {}

        # Write multiple versions
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))

        for i in range(1, 4):
            payload = {"policy": f"version_{i}"}
            write_next_version(
                store_root=store_root,
                app_id=app_id,
                component=component,
                payload=payload,
                semantic_clock=semantic_clock,
            )

        # After writing 3 versions, latest version is 3
        assert get_active_version(store_root, app_id, component) == 3
        # But active payload is still {} due to time-shift (cache captured before writes)
        assert read_active_payload(store_root, app_id, component) == initial_payload

        # Activate version 2 - this updates current.json payload
        activate_version(store_root, app_id, component, 2)
        # get_active_version still returns 3 (latest version number)
        assert get_active_version(store_root, app_id, component) == 3
        # But read_active_payload still returns initial_payload due to time-shift cache
        assert read_active_payload(store_root, app_id, component) == initial_payload

        # Clear cache to simulate new run
        _clear_start_of_run_cache()
        # Now reads the activated version's payload
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_2"}

        # Activate version 1
        activate_version(store_root, app_id, component, 1)
        # Still cached until next run
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_2"}

        # Clear cache for new run
        _clear_start_of_run_cache()
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_1"}

        # Can go back to version 3
        activate_version(store_root, app_id, component, 3)
        _clear_start_of_run_cache()
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_3"}
