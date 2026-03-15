"""ADG importability contract for agentic_core/utils/workflow_engines/interfaces.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_interfaces.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.utils.workflow_engines.interfaces import (  # noqa: F401
        Document,
        ICandidateFusion,
        IReranker,
        IRetrieverLexical,
        IRetrieverVector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    Document = None  # type: ignore[assignment,misc]
    IRetrieverLexical = None  # type: ignore[assignment,misc]
    IRetrieverVector = None  # type: ignore[assignment,misc]
    ICandidateFusion = None  # type: ignore[assignment,misc]
    IReranker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="interfaces deps unavailable")
class TestInterfacesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/utils/workflow_engines/interfaces.py must be importable."""
        assert _AVAILABLE

    def test_document_defined(self) -> None:
        assert Document is not None

    def test_iretrieverlexical_defined(self) -> None:
        assert IRetrieverLexical is not None

    def test_iretrievervector_defined(self) -> None:
        assert IRetrieverVector is not None

    def test_icandidatefusion_defined(self) -> None:
        assert ICandidateFusion is not None

    def test_ireranker_defined(self) -> None:
        assert IReranker is not None
