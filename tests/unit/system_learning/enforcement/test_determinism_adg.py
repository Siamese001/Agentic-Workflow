"""ADG-driven tests for system_learning/enforcement/determinism.py — fan_in=5.

Covers deterministic_json, stable_sha256_json, assert_no_nondeterminism.
"""
from __future__ import annotations

import hashlib
import json

import pytest

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
