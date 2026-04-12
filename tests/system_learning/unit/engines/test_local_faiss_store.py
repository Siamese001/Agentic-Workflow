"""Foundational behavioral tests for system_learning/engines/local_faiss_store.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module local_faiss_store must be importable."""
    import system_learning.engines.local_faiss_store

    assert system_learning.engines.local_faiss_store is not None
