"""ADG-driven tests for agentic_core/knowledge/document_loaders/source_document_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.knowledge.document_loaders.source_document_types  # noqa: F401


def test_module_importable():
    """Module source_document_types must be importable."""
    assert agentic_core.knowledge.document_loaders.source_document_types is not None
