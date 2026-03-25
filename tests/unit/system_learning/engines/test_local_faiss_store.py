"""Foundational behavioral tests for system_learning/engines/local_faiss_store.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.local_faiss_store  # noqa: F401


def test_module_importable():
    """Module local_faiss_store must be importable."""
    assert system_learning.engines.local_faiss_store is not None
