"""ADG-driven tests for system_learning/engines/retrieval_profile_replay_check.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.retrieval_profile_replay_check  # noqa: F401


def test_module_importable():
    """Module retrieval_profile_replay_check must be importable."""
    assert system_learning.engines.retrieval_profile_replay_check is not None
