"""
Unit tests for apps_shared.utils.determinism_util.

Verifies:
- Excluded fields are stripped at top level.
- Excluded fields are stripped recursively in nested dicts.
- Lists are recursed and order is preserved.
- file_hash returns stable sha256 of file bytes.

No network, wall-clock, or randomness used.
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.unit_min_deps

from apps_shared.utils.determinism_util import (
    DETERMINISM_EXCLUDED_FIELDS,
    canonical_hash,
    file_hash,
    strip_nondeterministic,
)


def test_exclusion_top_level():
    """duration_ms value must not affect canonical_hash."""
    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash({"a": 1, "duration_ms": 0})


def test_exclusion_nested_recursive():
    """timestamp inside a nested dict must not affect canonical_hash."""
    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
        {"a": {"timestamp": "y", "b": 2}}
    )


def test_list_recursive_preserves_order_and_strips():
    """trace_id inside list elements must not affect canonical_hash; order preserved."""
    assert canonical_hash([{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]) == canonical_hash(
        [{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}]
    )


def test_list_order_matters():
    """Different element order must produce different hashes."""
    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash([{"v": 2}, {"v": 1}])


def test_file_hash_stable(tmp_path):
    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
    content = b"deterministic content"
    f = tmp_path / "sample.bin"
    f.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert file_hash(f) == expected

    f.write_bytes(b"different content")
    assert file_hash(f) != expected


def test_strip_nondeterministic_dict_top_level():
    """All excluded fields are removed from a flat dict."""
    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
    result = strip_nondeterministic(obj)
    for excluded in DETERMINISM_EXCLUDED_FIELDS:
        assert excluded not in result
    assert result["a"] == 1
    assert result["b"] == 2


def test_strip_nondeterministic_preserves_non_excluded():
    """Non-excluded fields survive stripping unchanged."""
    obj = {"x": 42, "y": [1, 2, 3]}
    assert strip_nondeterministic(obj) == obj


def test_strip_nondeterministic_tuple_preserved():
    """Tuples are recursed and returned as tuples."""
    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
    result = strip_nondeterministic(obj)
    assert isinstance(result, tuple)
    assert result == ({"v": 1}, {"v": 2})


def test_canonical_hash_deterministic_multiple_calls():
    """Same input always produces same hash across multiple calls."""
    obj = {"key": "value", "nested": {"a": 1}}
    h1 = canonical_hash(obj)
    h2 = canonical_hash(obj)
    assert h1 == h2


def test_canonical_hash_different_content_differs():
    """Different meaningful content produces different hashes."""
    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
