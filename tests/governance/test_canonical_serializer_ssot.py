"""
Tests for CanonicalJSON SSOT enforcement.

Verifies that CanonicalJSON produces deterministic, byte-stable output
and that the SSOT module exists and exports the correct interface.

Phase 0.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.governance

from agentic_core.utils.canonical_json import CanonicalJSON


class TestCanonicalJSONSerialize:
    def test_sorted_keys(self) -> None:
        result = CanonicalJSON.serialize({"b": 2, "a": 1})
        assert result == '{"a":1,"b":2}'

    def test_nested_sorted_keys(self) -> None:
        result = CanonicalJSON.serialize({"z": {"y": 3, "x": 2}, "a": 1})
        assert result == '{"a":1,"z":{"x":2,"y":3}}'

    def test_compact_separators(self) -> None:
        result = CanonicalJSON.serialize({"k": "v"})
        assert " " not in result

    def test_ensure_ascii(self) -> None:
        result = CanonicalJSON.serialize({"key": "caf\u00e9"})
        assert "\\u" in result or all(ord(c) < 128 for c in result)

    def test_deterministic_across_calls(self) -> None:
        data = {"c": [3, 1, 2], "a": True, "b": None}
        assert CanonicalJSON.serialize(data) == CanonicalJSON.serialize(data)

    def test_serialize_bytes_type(self) -> None:
        result = CanonicalJSON.serialize_bytes({"k": "v"})
        assert isinstance(result, bytes)

    def test_serialize_bytes_utf8(self) -> None:
        result = CanonicalJSON.serialize_bytes({"k": "v"})
        assert result == b'{"k":"v"}'

    def test_serialize_hash_length(self) -> None:
        digest = CanonicalJSON.serialize_hash({"k": "v"})
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_serialize_hash_stable(self) -> None:
        data = {"x": 42}
        assert CanonicalJSON.serialize_hash(data) == CanonicalJSON.serialize_hash(data)

    def test_serialize_hash_matches_manual(self) -> None:
        data = {"k": "v"}
        expected = hashlib.sha256(b'{"k":"v"}').hexdigest()
        assert CanonicalJSON.serialize_hash(data) == expected

    def test_empty_dict(self) -> None:
        assert CanonicalJSON.serialize({}) == "{}"

    def test_list_preserved(self) -> None:
        result = CanonicalJSON.serialize({"items": [1, 2, 3]})
        assert result == '{"items":[1,2,3]}'

    def test_none_value(self) -> None:
        result = CanonicalJSON.serialize({"key": None})
        assert result == '{"key":null}'

    def test_bool_values(self) -> None:
        result = CanonicalJSON.serialize({"t": True, "f": False})
        assert "true" in result
        assert "false" in result
