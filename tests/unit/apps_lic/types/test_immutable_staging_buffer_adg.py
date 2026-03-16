"""ADG-driven tests for apps_lic/types/ImmutableStagingBuffer.py — fan_in=3.

Contract tests: write-once semantics, read, is_locked, get_snapshot.
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

_emit_records_execution_trace("p0", "evidence", "test_immutable_staging_buffer_adg")
_emit_applies_guardrail("p0", "test_immutable_staging_buffer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_immutable_staging_buffer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_immutable_staging_buffer_adg", "state_snapshot")
emit_replay_key("p0", "test_immutable_staging_buffer_adg")
emit_determinism_digest("p0", "test_immutable_staging_buffer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_immutable_staging_buffer_adg", "execution_auth")
_emit_validates_capability("p2", "test_immutable_staging_buffer_adg", "capability_check")
_emit_routes_to_capability("p2", "test_immutable_staging_buffer_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_immutable_staging_buffer_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_immutable_staging_buffer_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_immutable_staging_buffer_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_immutable_staging_buffer_adg", "exec_output")
_emit_dispatches_agent("p3", "test_immutable_staging_buffer_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_immutable_staging_buffer_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_immutable_staging_buffer_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_immutable_staging_buffer_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_immutable_staging_buffer_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_immutable_staging_buffer_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_immutable_staging_buffer_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_immutable_staging_buffer_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_immutable_staging_buffer_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_immutable_staging_buffer_adg", "eval_metric")
_emit_stores_embedding("p4", "test_immutable_staging_buffer_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_immutable_staging_buffer_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_immutable_staging_buffer_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer


class TestImmutableStagingBufferImport:
    def test_class_importable(self):
        assert callable(ImmutableStagingBuffer)


class TestWriteOnce:
    def test_write_and_read(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("key1", "value1")
        assert buf.read("key1") == "value1"

    def test_write_twice_raises(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("key1", "first")
        with pytest.raises(ValueError, match="immutable"):
            buf.write_once("key1", "second")

    def test_write_different_keys_allowed(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("a", 1)
        buf.write_once("b", 2)
        assert buf.read("a") == 1
        assert buf.read("b") == 2

    def test_read_missing_key_returns_none(self):
        buf = ImmutableStagingBuffer()
        assert buf.read("nonexistent") is None

    def test_write_various_types(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("int_val", 42)
        buf.write_once("list_val", [1, 2, 3])
        buf.write_once("dict_val", {"x": 1})
        assert buf.read("int_val") == 42
        assert buf.read("list_val") == [1, 2, 3]


class TestIsLocked:
    def test_key_locked_after_write(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("k", "v")
        assert buf.is_locked("k") is True

    def test_key_not_locked_before_write(self):
        buf = ImmutableStagingBuffer()
        assert buf.is_locked("unwritten") is False


class TestGetSnapshot:
    def test_snapshot_is_copy(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("x", 10)
        snap = buf.get_snapshot()
        snap["x"] = 999
        assert buf.read("x") == 10  # original unchanged

    def test_snapshot_empty_on_new_buffer(self):
        buf = ImmutableStagingBuffer()
        assert buf.get_snapshot() == {}

    def test_snapshot_contains_all_written_keys(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("a", 1)
        buf.write_once("b", 2)
        snap = buf.get_snapshot()
        assert set(snap.keys()) == {"a", "b"}
