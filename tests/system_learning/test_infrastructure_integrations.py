"""Comprehensive Test Suite for System Learning Infrastructure Integrations"""
from __future__ import annotations

import agentic_core.embeddings.embedding_input_guard  # noqa: F401


def test_module_importable():
    """Module embedding_input_guard must be importable."""
    assert agentic_core.embeddings.embedding_input_guard is not None
