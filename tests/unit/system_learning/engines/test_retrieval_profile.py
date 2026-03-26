"""Foundational behavioral tests for system_learning/engines/retrieval_profile.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module retrieval_profile must be importable."""
    import system_learning.engines.retrieval_profile  # noqa: F401

    assert system_learning.engines.retrieval_profile is not None
