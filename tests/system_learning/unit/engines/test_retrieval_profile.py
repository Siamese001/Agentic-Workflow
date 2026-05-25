"""Foundational behavioral tests for system_learning/engines/retrieval_profile.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module retrieval_profile must be importable."""
    import agentic_core.L6_system_learning.retrieval_profile

    assert system_learning.engines.retrieval_profile is not None
