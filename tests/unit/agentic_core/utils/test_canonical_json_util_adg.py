"""ADG-driven tests for agentic_core/utils/canonical_json_util.py — fan_in=2.

Contract tests: CanonicalJSON serialize, serialize_bytes, serialize_hash determinism.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
