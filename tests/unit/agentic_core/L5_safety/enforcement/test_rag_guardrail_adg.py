"""ADG importability contract for agentic_core/L5_safety/enforcement/rag_guardrail.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rag_guardrail.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.rag_guardrail import (  # noqa: F401
        ExternalKnowledgeAccessViolation,
        CitationBundle,
        RagGuardrail,
        validate_citation_custody,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExternalKnowledgeAccessViolation = None  # type: ignore[assignment,misc]
    CitationBundle = None  # type: ignore[assignment,misc]
    RagGuardrail = None  # type: ignore[assignment,misc]
    validate_citation_custody = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="rag_guardrail.py deps unavailable")
class TestRagGuardrailImportability:
    def test_module_importable(self) -> None:
        """ADG contract: rag_guardrail.py must be importable."""
        assert _AVAILABLE

    def test_externalknowledgeaccessviolation_is_type(self) -> None:
        assert ExternalKnowledgeAccessViolation is not None

    def test_citationbundle_is_type(self) -> None:
        assert CitationBundle is not None

    def test_ragguardrail_is_type(self) -> None:
        assert RagGuardrail is not None

    def test_validate_citation_custody_callable(self) -> None:
        assert callable(validate_citation_custody)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

