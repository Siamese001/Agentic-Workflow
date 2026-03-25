"""ADG importability contract for agentic_core/knowledge/document_loaders/csv_loader.py."""
from __future__ import annotations

import agentic_core.knowledge.document_loaders.csv_loader  # noqa: F401


def test_module_importable():
    """Module csv_loader must be importable."""
    assert agentic_core.knowledge.document_loaders.csv_loader is not None
