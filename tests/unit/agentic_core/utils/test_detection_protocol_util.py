"""Foundational behavioral tests for agentic_core/utils/detection_protocol_util.py."""
from __future__ import annotations


def test_module_importable():
    """Module detection_protocol_util must be importable."""
    from agentic_core.utils import detection_protocol_util
    assert detection_protocol_util is not None
