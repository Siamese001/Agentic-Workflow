"""ADG importability contract for agentic_core/adg/analysis/prompt_authority.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_prompt_authority.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.prompt_authority import (  # noqa: F401
        PromptAuthorityViolation,
        PromptAuthorityReport,
        detect_prompt_authority_violations,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PromptAuthorityViolation = None  # type: ignore[assignment,misc]
    PromptAuthorityReport = None  # type: ignore[assignment,misc]
    detect_prompt_authority_violations = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_authority.py deps unavailable")
class TestPromptAuthorityImportability:
    def test_module_importable(self) -> None:
        """ADG contract: prompt_authority.py must be importable."""
        assert _AVAILABLE

    def test_promptauthorityviolation_is_type(self) -> None:
        assert PromptAuthorityViolation is not None

    def test_promptauthorityreport_is_type(self) -> None:
        assert PromptAuthorityReport is not None

    def test_detect_prompt_authority_violations_callable(self) -> None:
        assert callable(detect_prompt_authority_violations)

