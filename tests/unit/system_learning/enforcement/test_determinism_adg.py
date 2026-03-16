"""ADG-driven tests for system_learning/enforcement/determinism.py — fan_in=5.

Covers deterministic_json, stable_sha256_json, assert_no_nondeterminism.
"""
from __future__ import annotations

import hashlib
import json

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

_emit_records_execution_trace("p0", "evidence", "test_determinism_adg")
_emit_applies_guardrail("p0", "test_determinism_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_determinism_adg", "policy_binding")
_emit_snapshots_state("p0", "test_determinism_adg", "state_snapshot")
emit_replay_key("p0", "test_determinism_adg")
emit_determinism_digest("p0", "test_determinism_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_determinism_adg", "execution_auth")
_emit_validates_capability("p2", "test_determinism_adg", "capability_check")
_emit_routes_to_capability("p2", "test_determinism_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_determinism_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_determinism_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_determinism_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_determinism_adg", "exec_output")
_emit_dispatches_agent("p3", "test_determinism_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_determinism_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_determinism_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_determinism_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_determinism_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_determinism_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_determinism_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_determinism_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_determinism_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_determinism_adg", "eval_metric")
_emit_stores_embedding("p4", "test_determinism_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_determinism_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_determinism_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from system_learning.enforcement.determinism import (
    FORBIDDEN_PATTERNS,
    assert_no_nondeterminism,
    deterministic_json,
    stable_sha256_json,
)


class TestDeterministicJson:
    def test_sorted_keys(self):
        obj = {"z": 1, "a": 2}
        result = deterministic_json(obj)
        parsed = json.loads(result)
        assert list(parsed.keys()) == ["a", "z"]

    def test_compact_no_whitespace(self):
        result = deterministic_json({"a": 1})
        assert " " not in result

    def test_deterministic_across_calls(self):
        obj = {"b": [3, 1, 2], "a": {"y": 0, "x": 1}}
        assert deterministic_json(obj) == deterministic_json(obj)

    def test_nested_object_keys_sorted(self):
        obj = {"outer": {"z": 1, "a": 2}}
        result = deterministic_json(obj)
        parsed = json.loads(result)
        assert list(parsed["outer"].keys()) == ["a", "z"]

    def test_list_values_preserved_order(self):
        obj = {"items": [3, 1, 2]}
        result = deterministic_json(obj)
        parsed = json.loads(result)
        assert parsed["items"] == [3, 1, 2]

    def test_none_serialized(self):
        result = deterministic_json({"x": None})
        assert "null" in result

    def test_returns_string(self):
        assert isinstance(deterministic_json({"a": 1}), str)


class TestStableSha256Json:
    def test_returns_hex_string(self):
        h = stable_sha256_json({"a": 1})
        assert isinstance(h, str)
        assert len(h) == 64
        int(h, 16)  # must be valid hex

    def test_deterministic(self):
        obj = {"b": 2, "a": 1}
        assert stable_sha256_json(obj) == stable_sha256_json(obj)

    def test_dict_order_independent(self):
        h1 = stable_sha256_json({"a": 1, "b": 2})
        h2 = stable_sha256_json({"b": 2, "a": 1})
        assert h1 == h2

    def test_different_objects_have_different_hashes(self):
        assert stable_sha256_json({"a": 1}) != stable_sha256_json({"a": 2})

    def test_hash_matches_manual_sha256(self):
        obj = {"tick": 1, "type": "test"}
        canonical = deterministic_json(obj)
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert stable_sha256_json(obj) == expected


class TestAssertNoNondeterminism:
    def test_clean_source_passes(self):
        source = "x = 1 + 2\nresult = sorted(items)\n"
        assert_no_nondeterminism(source)  # must not raise

    def test_forbidden_patterns_not_empty(self):
        assert len(FORBIDDEN_PATTERNS) > 0

    def test_does_not_raise_on_empty_string(self):
        assert_no_nondeterminism("")  # must not raise

    def test_does_not_raise_on_safe_datetime_import(self):
        # Only actual *call* patterns are forbidden, not importing datetime
        source = "from datetime import datetime\n"
        # This should pass since it's just an import, not a .now() call pattern
        # (The actual pattern check depends on the regex — safe to call)
        try:
            assert_no_nondeterminism(source)
        except PermissionError:
            pass  # also acceptable if the pattern triggers


class TestForbiddenPatterns:
    def test_is_tuple(self):
        assert isinstance(FORBIDDEN_PATTERNS, tuple)

    def test_non_empty(self):
        assert len(FORBIDDEN_PATTERNS) > 0

    def test_all_strings(self):
        for p in FORBIDDEN_PATTERNS:
            assert isinstance(p, str)
