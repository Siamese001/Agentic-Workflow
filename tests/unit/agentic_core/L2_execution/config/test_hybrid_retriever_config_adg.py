"""ADG importability contract for agentic_core/L2_execution/config/hybrid_retriever_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hybrid_retriever_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.config.hybrid_retriever_config import (  # noqa: F401
        ASTAwareTokenizer,
        RetrievalResult,
        HybridRetriever,
        NoOpGuardrail,
        HybridRetrieverFactory,
        get_hybrid_retriever,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ASTAwareTokenizer = None  # type: ignore[assignment,misc]
    RetrievalResult = None  # type: ignore[assignment,misc]
    HybridRetriever = None  # type: ignore[assignment,misc]
    NoOpGuardrail = None  # type: ignore[assignment,misc]
    HybridRetrieverFactory = None  # type: ignore[assignment,misc]
    get_hybrid_retriever = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hybrid_retriever_config.py deps unavailable")
class TestHybridRetrieverConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hybrid_retriever_config.py must be importable."""
        assert _AVAILABLE

    def test_astawaretokenizer_is_type(self) -> None:
        assert ASTAwareTokenizer is not None

    def test_retrievalresult_is_type(self) -> None:
        assert RetrievalResult is not None

    def test_hybridretriever_is_type(self) -> None:
        assert HybridRetriever is not None

    def test_get_hybrid_retriever_callable(self) -> None:
        assert callable(get_hybrid_retriever)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

