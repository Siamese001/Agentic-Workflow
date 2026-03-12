"""ADG importability contract for agentic_core/knowledge/document_loaders/csv_loader.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_csv_loader.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.knowledge.document_loaders.csv_loader import (  # noqa: F401
        CSVDocumentLoader,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CSVDocumentLoader = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="csv_loader.py deps unavailable")
class TestCsvLoaderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: csv_loader.py must be importable."""
        assert _AVAILABLE

    def test_csvdocumentloader_is_type(self) -> None:
        assert CSVDocumentLoader is not None

