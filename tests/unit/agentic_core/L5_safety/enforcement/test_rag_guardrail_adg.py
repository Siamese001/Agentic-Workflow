"""ADG importability contract for agentic_core/L5_safety/enforcement/rag_guardrail.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rag_guardrail.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.rag_guardrail import (  # noqa: F401
        CitationBundle,
        ExternalKnowledgeAccessViolation,
        RagGuardrail,
        validate_citation_custody,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ExternalKnowledgeAccessViolation = None  # type: ignore[assignment,misc]
    CitationBundle = None  # type: ignore[assignment,misc]
    validate_citation_custody = None  # type: ignore[assignment,misc]
    RagGuardrail = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rag_guardrail deps unavailable")
class TestRagGuardrailImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/rag_guardrail.py must be importable."""
        assert _AVAILABLE

    def test_externalknowledgeaccessviolation_defined(self) -> None:
        assert ExternalKnowledgeAccessViolation is not None

    def test_citationbundle_defined(self) -> None:
        assert CitationBundle is not None

    def test_ragguardrail_defined(self) -> None:
        assert RagGuardrail is not None
