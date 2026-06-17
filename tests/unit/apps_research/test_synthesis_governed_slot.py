"""Tests for RH6B.2 synthesis bridge adoption.

Plan: prompt-reception-followups-a7b3c4.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
)
from apps_research.services.synthesis_engine_service import SynthesisEngineService


def _sample_synthesis() -> dict[str, Any]:
    return {
        "synthesis_id": "synth_abc",
        "mode": "thematic",
        "target_audience": "technical",
        "insight_count": 3,
        "theme_count": 2,
        "findings": [
            {
                "theme": "performance",
                "summary": "Synthesis of 2 insights on performance",
                "key_points": ["p50 latency", "throughput"],
                "confidence": 0.8,
                "source_count": 2,
            },
            {
                "theme": "security",
                "summary": "Synthesis of 1 insights on security",
                "key_points": ["mTLS required"],
                "confidence": 0.9,
                "source_count": 1,
            },
        ],
    }


class TestSynthesisEngineServiceGovernedSlot:
    """RH6B.2 — SynthesisEngineService.build_governed_slot."""

    def test_returns_c0_authority_slot(self) -> None:
        service = SynthesisEngineService()
        slot = service.build_governed_slot(_sample_synthesis())
        assert isinstance(slot, AuthoritySlot)
        assert slot.slot_type == "C0"
        assert slot.authority_level is AuthorityLevel.INFO

    def test_renders_themes_and_key_points_into_content(self) -> None:
        service = SynthesisEngineService()
        slot = service.build_governed_slot(_sample_synthesis())
        assert "performance" in slot.content
        assert "mTLS required" in slot.content
        assert "thematic" in slot.content
        # Token counts from the input synthesis make it into the header line.
        assert "Insights: 3" in slot.content
        assert "Themes: 2" in slot.content

    def test_attaches_synthesis_producer_provenance(self) -> None:
        service = SynthesisEngineService()
        slot = service.build_governed_slot(
            _sample_synthesis(),
            source_trace_ids=("upstream-1",),
            model="gemini-2.5-flash",
        )
        assert slot.metadata["synthesis_producer"] == "apps_research.services.synthesis_engine_service"
        assert slot.metadata["synthesis_source_trace_ids"] == ["upstream-1"]
        assert slot.metadata["synthesis_model"] == "gemini-2.5-flash"
        assert slot.metadata["synthesis_kind"] == "knowledge"

    def test_handles_empty_findings(self) -> None:
        service = SynthesisEngineService()
        empty: dict[str, Any] = {
            "mode": "thematic",
            "insight_count": 0,
            "theme_count": 0,
            "findings": [],
        }
        slot = service.build_governed_slot(empty)
        assert slot.slot_type == "C0"
        assert "Insights: 0" in slot.content
