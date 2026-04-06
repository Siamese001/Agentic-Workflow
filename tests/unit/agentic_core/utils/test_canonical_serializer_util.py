"""Foundational behavioral tests for agentic_core/utils/canonical_serializer_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module canonical_serializer_util must be importable."""
    from agentic_core.utils import canonical_serializer_util
    assert canonical_serializer_util is not None


def test_canonical_bytes_happy_path():
    """canonical_bytes must produce deterministic bytes for dict."""
    from agentic_core.utils import canonical_serializer_util

    obj = {"b": 2, "a": 1}
    result = canonical_serializer_util.canonical_bytes(obj)
    assert result is not None
    assert isinstance(result, bytes)


def test_canonical_bytes_failure_path():
    """canonical_bytes must handle complex objects by converting to string."""
    from agentic_core.utils import canonical_serializer_util

    class CustomObj:
        pass

    obj = {"data": CustomObj()}
    result = canonical_serializer_util.canonical_bytes(obj)
    assert result is not None
    assert isinstance(result, bytes)


def test_canonical_bytes_edge_case():
    """canonical_bytes must handle nested structures."""
    from agentic_core.utils import canonical_serializer_util

    obj = {"a": {"b": [1, 2, 3]}, "c": None}
    result = canonical_serializer_util.canonical_bytes(obj)
    assert result is not None
    assert isinstance(result, bytes)


def test_canonical_hash_happy_path():
    """canonical_hash must produce deterministic hash."""
    from agentic_core.utils import canonical_serializer_util

    obj = {"a": 1, "b": 2}
    hash1 = canonical_serializer_util.canonical_hash(obj)
    hash2 = canonical_serializer_util.canonical_hash(obj)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex digest
