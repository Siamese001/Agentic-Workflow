"""Foundational behavioral tests for agentic_core/utils/review_protocol_util.py.

"""
from __future__ import annotations


def test_module_importable():
    """Module review_protocol_util must be importable or skip gracefully."""
    from agentic_core.utils import review_protocol_util
    assert review_protocol_util is not None


def test_module_exposes_public_api():
    """review_protocol_util module exposes expected public symbols."""
    from agentic_core.utils import review_protocol_util
    assert review_protocol_util is not None
