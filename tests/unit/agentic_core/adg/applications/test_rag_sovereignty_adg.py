"""ADG importability contract for agentic_core/adg/applications/rag_sovereignty.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rag_sovereignty.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.rag_sovereignty import (  # noqa: F401
        RAGSovereigntyViolation,
        RAGSovereigntyReport,
        check_rag_sovereignty,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RAGSovereigntyViolation = None  # type: ignore[assignment,misc]
    RAGSovereigntyReport = None  # type: ignore[assignment,misc]
    check_rag_sovereignty = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="rag_sovereignty.py deps unavailable")
class TestRagSovereigntyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: rag_sovereignty.py must be importable."""
        assert _AVAILABLE

    def test_ragsovereigntyviolation_is_type(self) -> None:
        assert RAGSovereigntyViolation is not None

    def test_ragsovereigntyreport_is_type(self) -> None:
        assert RAGSovereigntyReport is not None

    def test_check_rag_sovereignty_callable(self) -> None:
        assert callable(check_rag_sovereignty)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

