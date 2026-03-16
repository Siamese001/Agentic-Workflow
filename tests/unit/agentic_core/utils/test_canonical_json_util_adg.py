"""ADG-driven tests for agentic_core/utils/canonical_json_util.py — fan_in=2.

Contract tests: CanonicalJSON serialize, serialize_bytes, serialize_hash determinism.
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

_emit_records_execution_trace("p0", "evidence", "test_canonical_json_util_adg")
_emit_applies_guardrail("p0", "test_canonical_json_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_canonical_json_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_canonical_json_util_adg", "state_snapshot")
emit_replay_key("p0", "test_canonical_json_util_adg")
emit_determinism_digest("p0", "test_canonical_json_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_canonical_json_util_adg", "execution_auth")
_emit_validates_capability("p2", "test_canonical_json_util_adg", "capability_check")
_emit_routes_to_capability("p2", "test_canonical_json_util_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_canonical_json_util_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_canonical_json_util_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_canonical_json_util_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_canonical_json_util_adg", "exec_output")
_emit_dispatches_agent("p3", "test_canonical_json_util_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_canonical_json_util_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_canonical_json_util_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_canonical_json_util_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_canonical_json_util_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_canonical_json_util_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_canonical_json_util_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_canonical_json_util_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_canonical_json_util_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_canonical_json_util_adg", "eval_metric")
_emit_stores_embedding("p4", "test_canonical_json_util_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_canonical_json_util_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_canonical_json_util_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.utils.canonical_json_util import CanonicalJSON


class TestCanonicalJSONImport:
    def test_class_importable(self):
        assert callable(CanonicalJSON)


class TestCanonicalJSONSerialize:
    def test_returns_string(self):
        result = CanonicalJSON.serialize({"a": 1})
        assert isinstance(result, str)

    def test_sorted_keys(self):
        result = CanonicalJSON.serialize({"z": 1, "a": 2})
        assert result.index('"a"') < result.index('"z"')

    def test_compact_separators_no_spaces(self):
        result = CanonicalJSON.serialize({"key": "val"})
        assert " " not in result

    def test_deterministic_on_same_input(self):
        a = CanonicalJSON.serialize({"b": 2, "a": 1})
        b = CanonicalJSON.serialize({"a": 1, "b": 2})
        assert a == b

    def test_nested_sorted(self):
        result = CanonicalJSON.serialize({"z": {"b": 2, "a": 1}})
        inner = result[result.index("{", 1):]
        assert inner.index('"a"') < inner.index('"b"')

    def test_list_preserved(self):
        result = CanonicalJSON.serialize([1, 2, 3])
        assert result == "[1,2,3]"

    def test_ascii_only(self):
        result = CanonicalJSON.serialize({"key": "héllo"})
        assert all(ord(c) < 128 for c in result)


class TestCanonicalJSONSerializeBytes:
    def test_returns_bytes(self):
        result = CanonicalJSON.serialize_bytes({"x": 1})
        assert isinstance(result, bytes)

    def test_utf8_encoding(self):
        obj = {"a": 1}
        bs = CanonicalJSON.serialize_bytes(obj)
        assert bs == CanonicalJSON.serialize(obj).encode("utf-8")

    def test_deterministic(self):
        a = CanonicalJSON.serialize_bytes({"b": 2, "a": 1})
        b = CanonicalJSON.serialize_bytes({"a": 1, "b": 2})
        assert a == b


class TestCanonicalJSONSerializeHash:
    def test_returns_string(self):
        result = CanonicalJSON.serialize_hash({"x": 1})
        assert isinstance(result, str)

    def test_is_sha256_hex(self):
        result = CanonicalJSON.serialize_hash({"x": 1})
        assert len(result) == 64
        int(result, 16)  # must parse as hex

    def test_deterministic(self):
        a = CanonicalJSON.serialize_hash({"b": 2, "a": 1})
        b = CanonicalJSON.serialize_hash({"a": 1, "b": 2})
        assert a == b

    def test_different_inputs_different_hash(self):
        a = CanonicalJSON.serialize_hash({"x": 1})
        b = CanonicalJSON.serialize_hash({"x": 2})
        assert a != b
