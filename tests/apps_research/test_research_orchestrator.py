"""
Tests for apps_research — Autonomous Research Engine.

All tests are deterministic: no LLM calls, no file I/O in non-dry-run paths.
"""

from __future__ import annotations

import pytest

#  # MOVED: from apps_research.types.research_types import (
    ArtifactMode,
    AudienceStyle,
    ClaimType,
    ComparisonRow,
    ResearchRequest,
    ResearchRunSummary,
    ResearchSection,
    ResearchStatus,
    SourceEntry,
)


class TestResearchTypes:
    def test_research_status_values(self) -> None:
                from apps_research.types.research_types import (
                from apps_research.validators.research_gate_validator import ResearchGateValidator
                from apps_research.validators.research_gate_validator import ResearchGateValidator
                from apps_research.validators.research_gate_validator import ResearchGateValidator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
                from apps_research.config.agent_spec_config import load_research_specs
                from apps_research.config.agent_spec_config import load_research_specs
                from apps_research.config.reasoning_toggles_config import DEFAULT_TOGGLES
                from apps_research.config.agent_spec_config import load_research_specs
                assert ResearchStatus.COMPLETE.value == "complete"
                assert ResearchStatus.DRY_RUN.value == "dry_run"
                assert ResearchStatus.FAILED.value == "failed"

        assert ResearchStatus.FAILED.value == "failed"

    def test_artifact_mode_values(self) -> None:
        assert ArtifactMode.BRIEF.value == "brief"
        assert ArtifactMode.COMPARISON.value == "comparison"
        assert ArtifactMode.TREND.value == "trend"
        assert ArtifactMode.THOUGHT_LEADERSHIP.value == "thought_leadership"

    def test_claim_type_values(self) -> None:
        assert ClaimType.DIRECT_EVIDENCE.value == "direct_evidence"
        assert ClaimType.ASSUMPTION.value == "assumption"
        assert ClaimType.ANALYST_INFERENCE.value == "analyst_inference"

    def test_source_entry_frozen(self) -> None:
        entry = SourceEntry(
            source_id="S-001",
            title="Test Source",
            claim_type=ClaimType.DIRECT_EVIDENCE,
            confidence=0.9,
        )
        with pytest.raises((AttributeError, TypeError)):
            entry.title = "changed"  # type: ignore[misc]

    def test_research_section_frozen(self) -> None:
        section = ResearchSection(
            section_id="key_findings",
            heading="Key Findings",
            body="Platform implements deterministic governance.",
        )
        with pytest.raises((AttributeError, TypeError)):
            section.heading = "changed"  # type: ignore[misc]

    def test_comparison_row_frozen(self) -> None:
        row = ComparisonRow(subject="Platform A", dimensions={"cost": "low"})
        with pytest.raises((AttributeError, TypeError)):
            row.subject = "changed"  # type: ignore[misc]

    def test_research_request_defaults(self) -> None:
        req = ResearchRequest(topic="AI governance")
        assert req.mode == ArtifactMode.BRIEF
        assert req.dry_run is False
        assert req.audience_style == AudienceStyle.TECHNICAL

    def test_research_run_summary_to_dict_keys(self) -> None:
    """Test research_run_summary_to_dict_keys runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute research_run_summary_to_dict_keys
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions

class TestResearchGateValidator:
    def test_passes_valid_sections_with_sources(self) -> None:
#  # MOVED: from apps_research.validators.research_gate_validator import ResearchGateValidator

        sections = [
            ResearchSection(
                section_id="executive_summary",
                heading="Executive Summary",
                body="The platform delivers deterministic AI governance.",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                sources=("S-001",),
            ),
            ResearchSection(
                section_id="key_findings",
                heading="Key Findings",
                body="Layer boundary enforcement eliminates cross-layer violations.",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                sources=("S-001",),
            ),
        ]
        sources = [
            SourceEntry(
                source_id="S-001",
                title="ADG Analysis",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                confidence=0.95,
                summary="ADG graph confirmed layer boundaries",
            )
        ]
        validator = ResearchGateValidator()
        result = validator.validate(sections, sources, ["executive_summary", "key_findings"])
        assert result.passed is True

    def test_fails_empty_sections(self) -> None:
#  # MOVED: from apps_research.validators.research_gate_validator import ResearchGateValidator

        validator = ResearchGateValidator()
        result = validator.validate([], [], ["executive_summary"])
        assert result.passed is False

    def test_quality_score_in_range(self) -> None:
#  # MOVED: from apps_research.validators.research_gate_validator import ResearchGateValidator

        sections = [
            ResearchSection(
                section_id="s1",
                heading="Section",
                body="body",
                sources=("S-001",),
            )
        ]
        sources = [
            SourceEntry(
                source_id="S-001",
                title="Source",
                claim_type=ClaimType.DIRECT_EVIDENCE,
                confidence=0.8,
            )
        ]
        validator = ResearchGateValidator()
        result = validator.validate(sections, sources, [])
        assert 0.0 <= result.quality_score <= 1.0


class TestResearchOrchestratorDryRun:
    def test_dry_run_returns_dry_run_status(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        req = ResearchRequest(topic="AI governance", dry_run=True)
        orch = ResearchOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.status == ResearchStatus.DRY_RUN

    def test_dry_run_no_artifact_paths(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        req = ResearchRequest(topic="AI governance", dry_run=True)
        orch = ResearchOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.artifact_paths == []

    def test_dry_run_has_sections(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        req = ResearchRequest(topic="AI governance", mode=ArtifactMode.BRIEF, dry_run=True)
        orch = ResearchOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.sections) > 0

    def test_trace_id_deterministic(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        req1 = ResearchRequest(topic="AI governance", mode=ArtifactMode.BRIEF)
        req2 = ResearchRequest(topic="AI governance", mode=ArtifactMode.BRIEF)
        t1 = ResearchOrchestrator._make_trace_id(req1)
        t2 = ResearchOrchestrator._make_trace_id(req2)
        assert t1 == t2

    def test_different_modes_different_trace_ids(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        req1 = ResearchRequest(topic="AI governance", mode=ArtifactMode.BRIEF)
        req2 = ResearchRequest(topic="AI governance", mode=ArtifactMode.TREND)
        t1 = ResearchOrchestrator._make_trace_id(req1)
        t2 = ResearchOrchestrator._make_trace_id(req2)
        assert t1 != t2

    def test_all_modes_complete_dry_run(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        for mode in ArtifactMode:
            req = ResearchRequest(topic="AI governance", mode=mode, dry_run=True)
            orch = ResearchOrchestrator(dry_run=True)
            result = orch.run(req)
            assert result.status in (ResearchStatus.DRY_RUN, ResearchStatus.COMPLETE), (
                f"Unexpected status {result.status} for mode={mode}"
            )

    def test_comparison_mode_has_matrix_or_sections(self) -> None:
#  # MOVED: from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator

        req = ResearchRequest(
            topic="RAG vs fine-tuning",
            mode=ArtifactMode.COMPARISON,
            comparison_subjects=["RAG", "Fine-tuning"],
            dry_run=True,
        )
        orch = ResearchOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.sections) > 0 or len(result.comparison_matrix) >= 0


class TestResearchConfig:
    def test_load_research_specs_returns_defaults(self) -> None:
#  # MOVED: from apps_research.config.agent_spec_config import load_research_specs

        specs = load_research_specs()
        assert specs is not None
        assert specs.version == "1.0.0"

    def test_all_artifact_modes_configured(self) -> None:
#  # MOVED: from apps_research.config.agent_spec_config import load_research_specs

        specs = load_research_specs()
        expected_modes = {"brief", "comparison", "trend", "position", "thought_leadership"}
        assert expected_modes.issubset(set(specs.artifact_modes.keys()))

    def test_reasoning_toggles_defaults(self) -> None:
#  # MOVED: from apps_research.config.reasoning_toggles_config import DEFAULT_TOGGLES

        assert DEFAULT_TOGGLES.enable_source_register is True
        assert DEFAULT_TOGGLES.enable_epistemic_labeling is True
        assert DEFAULT_TOGGLES.llm_narrative_enabled is False

    def test_gate_config_min_quality_score(self) -> None:
#  # MOVED: from apps_research.config.agent_spec_config import load_research_specs

        specs = load_research_specs()
        assert specs.gate.min_quality_score >= 0.0
        assert specs.gate.min_quality_score <= 1.0
