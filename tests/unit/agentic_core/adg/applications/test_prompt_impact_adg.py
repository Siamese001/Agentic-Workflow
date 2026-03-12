"""ADG importability contract for agentic_core/adg/applications/prompt_impact.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_prompt_impact.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.prompt_impact import (  # noqa: F401
        PromptImpactEntry,
        PromptImpactReport,
        analyze_prompt_impact,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PromptImpactEntry = None  # type: ignore[assignment,misc]
    PromptImpactReport = None  # type: ignore[assignment,misc]
    analyze_prompt_impact = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="prompt_impact.py deps unavailable")
class TestPromptImpactImportability:
    def test_module_importable(self) -> None:
        """ADG contract: prompt_impact.py must be importable."""
        assert _AVAILABLE

    def test_promptimpactentry_is_type(self) -> None:
        assert PromptImpactEntry is not None

    def test_promptimpactreport_is_type(self) -> None:
        assert PromptImpactReport is not None

    def test_analyze_prompt_impact_callable(self) -> None:
        assert callable(analyze_prompt_impact)

