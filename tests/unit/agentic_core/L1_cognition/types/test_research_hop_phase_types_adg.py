"""Behavioral tests for research_hop_phase_types_adg."""

from __future__ import annotations

from agentic_core.research_hop_phase_types_adg import ResearchHopPhase


def test_research_hop_phase_enum_contains_expected_values():
    assert {phase.value for phase in ResearchHopPhase} == {"discover", "retrieve", "synthesize"}
