"""Foundational behavioral tests for system_learning/engines/retrieval_profile.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.retrieval_profile  # noqa: F401


def test_module_importable():
    """Module retrieval_profile must be importable."""
    assert system_learning.engines.retrieval_profile is not None
