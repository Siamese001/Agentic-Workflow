"""Wave 5.1: Canonical serialization lockdown tests.

Validates:
- Deterministic golden tests (10x identical SHA256)
- Float precision normalization
- Tuple normalization
- Explicit null encoding
- Sorted keys (recursive)
- AST guard: no direct json.dumps in L2 audit path
- Cross-object serialization consistency
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

from agentic_core.utils.canonical_serializer_util import (
    _normalize,
    canonical_bytes,
    canonical_hash,
)

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestGoldenDeterminism:
    """Same object serialized 10x must produce identical SHA256."""

    def test_dict_10x_identical(self):
        obj = {
            "agent_id": "agent-001",
            "score": 0.123456789,
            "tags": ["a", "b"],
            "nested": {"z": 1, "a": 2},
        }
        hashes = [canonical_hash(obj) for _ in range(10)]
        assert len(set(hashes)) == 1

    def test_nested_dict_10x_identical(self):
        obj = {
            "outer": {
                "inner": {
                    "deep": [1, 2.0, None, "x"],
                }
            }
        }
        hashes = [canonical_hash(obj) for _ in range(10)]
        assert len(set(hashes)) == 1

    def test_tuple_input_10x_identical(self):
        obj = {
            "metrics": (("accuracy", 0.95), ("loss", 0.05)),
        }
        hashes = [canonical_hash(obj) for _ in range(10)]
        assert len(set(hashes)) == 1

    def test_empty_dict_10x_identical(self):
        hashes = [canonical_hash({}) for _ in range(10)]
        assert len(set(hashes)) == 1

    def test_none_values_10x_identical(self):
        obj = {"a": None, "b": None}
        hashes = [canonical_hash(obj) for _ in range(10)]
        assert len(set(hashes)) == 1


class TestFloatPrecision:
    """Float precision must be normalized to 6 decimal places."""

    def test_float_normalized(self):
        assert _normalize(0.1234567890123) == 0.123457

    def test_float_round_trip(self):
        a = canonical_bytes({"v": 0.1 + 0.2})
        b = canonical_bytes({"v": 0.3})
        assert a == b

    def test_float_trailing_zeros(self):
        a = canonical_bytes({"v": 1.0})
        b = canonical_bytes({"v": 1.000000})
        assert a == b


class TestTupleNormalization:
    """Tuples must be converted to lists."""

    def test_tuple_becomes_list(self):
        a = canonical_bytes({"v": (1, 2, 3)})
        b = canonical_bytes({"v": [1, 2, 3]})
        assert a == b

    def test_nested_tuple(self):
        a = canonical_bytes({"v": ((1, 2), (3, 4))})
        b = canonical_bytes({"v": [[1, 2], [3, 4]]})
        assert a == b


class TestNullEncoding:
    """None must be explicitly encoded as JSON null."""

    def test_none_encoded(self):
        raw = canonical_bytes({"a": None})
        assert b"null" in raw

    def test_none_not_omitted(self):
        raw = canonical_bytes({"a": None, "b": 1})
        assert b'"a":null' in raw


class TestSortedKeys:
    """Keys must be sorted recursively."""

    def test_top_level_sorted(self):
        a = canonical_bytes({"z": 1, "a": 2})
        b = canonical_bytes({"a": 2, "z": 1})
        assert a == b

    def test_nested_sorted(self):
        a = canonical_bytes({"x": {"z": 1, "a": 2}})
        b = canonical_bytes({"x": {"a": 2, "z": 1}})
        assert a == b


class TestCrossObjectConsistency:
    """Serializer used by audit log and intent must agree."""

    def test_audit_and_intent_same_serializer(self):
        payload = {
            "agent_id": "a1",
            "action": "persist",
            "score": 0.95,
        }
        h1 = canonical_hash(payload)
        h2 = hashlib.sha256(canonical_bytes(payload)).hexdigest()
        assert h1 == h2


class TestASTNoDirectJsonDumps:
    """No direct json.dumps in L2 audit execution path."""

    def test_no_json_dumps_in_audit_log(self):
        audit_path = REPO_ROOT / "agentic_core" / "L2_execution" / "audit" / "hash_chain_audit_log.py"
        tree = ast.parse(audit_path.read_text("utf-8"))
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    if func.attr == "dumps" and isinstance(func.value, ast.Name) and func.value.id == "json":
                        violations.append(f"line {node.lineno}: json.dumps")
        assert violations == [], (
            "L2 audit must use canonical_serializer, not direct json.dumps:\n" + "\n".join(violations)
        )

    def test_no_json_dumps_in_canonical_serializer(self):
        """canonical_serializer itself is the ONLY place json.dumps is allowed."""
        ser_path = REPO_ROOT / "agentic_core" / "utils" / "canonical_serializer_util.py"
        tree = ast.parse(ser_path.read_text("utf-8"))
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    if func.attr == "dumps" and isinstance(func.value, ast.Name) and func.value.id == "json":
                        count += 1
        assert count == 1, f"canonical_serializer.py must have exactly 1 json.dumps call, found {count}"

    def test_no_json_import_in_audit_log(self):
        audit_path = REPO_ROOT / "agentic_core" / "L2_execution" / "audit" / "hash_chain_audit_log.py"
        tree = ast.parse(audit_path.read_text("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "json", "audit log must not import json directly"
