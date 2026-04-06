"""Foundational behavioral tests for agentic_core/utils/canonical_serializer_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module canonical_serializer_util must be importable."""
    from agentic_core.utils import canonical_serializer_util
    assert canonical_serializer_util is not None
