"""ADG-driven tests for agentic_core/knowledge/document_loaders/pdf_document_loader_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.knowledge.document_loaders.pdf_document_loader_config  # noqa: F401


def test_module_importable():
    """Module pdf_document_loader_config must be importable."""
    assert agentic_core.knowledge.document_loaders.pdf_document_loader_config is not None
