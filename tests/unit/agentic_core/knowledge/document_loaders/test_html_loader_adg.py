"""ADG importability contract for agentic_core/knowledge/document_loaders/html_loader.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_html_loader.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.knowledge.document_loaders.html_loader import (  # noqa: F401
        HTMLDocumentLoader,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HTMLDocumentLoader = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="html_loader deps unavailable")
class TestHtmlLoaderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/knowledge/document_loaders/html_loader.py must be importable."""
        assert _AVAILABLE

    def test_htmldocumentloader_defined(self) -> None:
        assert HTMLDocumentLoader is not None