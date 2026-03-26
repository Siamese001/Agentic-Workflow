"""
Tests for apps_exec — Executive Brief Generator.

All tests are deterministic: no LLM calls, no file I/O in non-dry-run paths.
"""

from __future__ import annotations

import pytest

#  # MOVED: from apps_exec.types.exec_types import (
    AudiencePersona,
    BriefSection,
    BriefStatus,
    BriefTone,
    ExecBriefRequest,
    ExecBriefResult,
    RunSummary,
)


class TestExecTypes:
    def test_audience_persona_values(self) -> None:
        from apps_exec.types.exec_types import (
        from apps_exec.validators.style_gate_validator import StyleGateValidator
        from apps_exec.validators.style_gate_validator import StyleGateValidator
        from apps_exec.validators.style_gate_validator import StyleGateValidator
        from apps_exec.validators.style_gate_validator import StyleGateValidator
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.config.agent_spec_config import load_exec_specs
        from apps_exec.config.reasoning_toggles_config import DEFAULT_TOGGLES
        from apps_exec.config.agent_spec_config import load_exec_specs
        from apps_exec.spine.exec_spine_adapter import ExecSpineAdapter
        assert AudiencePersona.RECRUITER.value == "recruiter"
        assert AudiencePersona.CTO.value == "cto"
        assert AudiencePersona.BOARD.value == "board"

    def test_brief_tone_values(self) -> None:
        assert BriefTone.BOARD_READY.value == "board-ready"
        assert BriefTone.CTO_READY.value == "cto-ready"

    def test_brief_status_enum_completeness(self) -> None:
        values = {s.value for s in BriefStatus}
        assert "complete" in values
        assert "dry_run" in values
        assert "failed" in values

    def test_brief_section_frozen(self) -> None:
        section = BriefSection(
            section_id="test",
            heading="Test",
            body="body",
            evidence_anchors=("anchor1",),
            why_this_matters="matters",
        )
        with pytest.raises((AttributeError, TypeError)):
            section.heading = "changed"  # type: ignore[misc]

    def test_exec_brief_request_defaults(self) -> None:
        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER)
        assert req.dry_run is False
        assert req.trace_id == ""
        assert req.tone == BriefTone.TECHNICAL

    def test_exec_brief_result_passed_gate(self) -> None:
        result = ExecBriefResult(
            trace_id="abc",
            audience="recruiter",
            tone="technical",
            status=BriefStatus.COMPLETE,
        )
        assert result.passed_gate is True

    def test_exec_brief_result_failed_gate(self) -> None:
        result = ExecBriefResult(
            trace_id="abc",
            audience="recruiter",
            tone="technical",
            status=BriefStatus.COMPLETE,
            gate_violations=["[STYLE_BUZZWORD_DENSITY:BLOCK] bad"],
        )
        assert result.passed_gate is False

    def test_run_summary_to_dict_keys(self) -> None:
    """Test run_summary_to_dict_keys runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute run_summary_to_dict_keys
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
            section_id="test",
            heading="Overview",
            body="The platform implements deterministic governance at the architecture layer.",
            evidence_anchors=("L0_routing",),
            why_this_matters="Shows governance maturity.",
        )
        validator = StyleGateValidator()
        result = validator.validate_sections([section])
        block_violations = [v for v in result.violations if v.severity == "BLOCK"]
        assert len(block_violations) == 0

    def test_blocks_unsupported_claim(self) -> None:
#  # MOVED: from apps_exec.validators.style_gate_validator import StyleGateValidator

        section = BriefSection(
            section_id="test",
            heading="Overview",
            body="This is guaranteed to always work with 100% accuracy.",
            evidence_anchors=("anchor",),
            why_this_matters="why",
        )
        validator = StyleGateValidator()
        result = validator.validate_sections([section])
        block_ids = [v.rule_id for v in result.violations if v.severity == "BLOCK"]
        assert "STYLE_UNSUPPORTED_CLAIM" in block_ids

    def test_warns_missing_evidence(self) -> None:
#  # MOVED: from apps_exec.validators.style_gate_validator import StyleGateValidator

        section = BriefSection(
            section_id="test",
            heading="Overview",
            body="Some body text.",
            evidence_anchors=(),
            why_this_matters="why",
        )
        validator = StyleGateValidator()
        result = validator.validate_sections([section])
        warn_ids = [v.rule_id for v in result.violations if v.severity == "WARN"]
        assert "STYLE_EVIDENCE_MISSING" in warn_ids

    def test_blocks_empty_body(self) -> None:
#  # MOVED: from apps_exec.validators.style_gate_validator import StyleGateValidator

        section = BriefSection(
            section_id="test",
            heading="Overview",
            body="",
            evidence_anchors=("anchor",),
            why_this_matters="why",
        )
        validator = StyleGateValidator()
        result = validator.validate_sections([section])
        block_ids = [v.rule_id for v in result.violations if v.severity == "BLOCK"]
        assert "STYLE_EMPTY_BODY" in block_ids

    def test_quality_score_range(self) -> None:
#  # MOVED: from apps_exec.validators.style_gate_validator import StyleGateValidator

        section = BriefSection(
            section_id="test",
            heading="Overview",
            body="The platform implements governance.",
            evidence_anchors=("anchor",),
            why_this_matters="why",
        )
        validator = StyleGateValidator()
        result = validator.validate_sections([section])
        assert 0.0 <= result.quality_score <= 1.0


class TestExecOrchestratorDryRun:
    def test_dry_run_returns_dry_run_status(self) -> None:
#  # MOVED: from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator

        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, dry_run=True)
        orch = ExecOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.status == BriefStatus.DRY_RUN

    def test_dry_run_no_artifact_paths(self) -> None:
#  # MOVED: from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator

        req = ExecBriefRequest(audience=AudiencePersona.CTO, dry_run=True)
        orch = ExecOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.artifact_paths == []

    def test_dry_run_has_sections(self) -> None:
#  # MOVED: from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator

        req = ExecBriefRequest(audience=AudiencePersona.BOARD, dry_run=True)
        orch = ExecOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.sections) > 0

    def test_dry_run_trace_id_deterministic(self) -> None:
    """Test dry_run_trace_id_deterministic runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute dry_run_trace_id_deterministic
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
            req = ExecBriefRequest(audience=persona, dry_run=True)
            orch = ExecOrchestrator(dry_run=True)
            result = orch.run(req)
            assert result.status in (BriefStatus.DRY_RUN, BriefStatus.COMPLETE), (
                f"Unexpected status {result.status} for persona {persona}"
            )


class TestExecConfig:
    def test_load_exec_specs_returns_defaults(self) -> None:
#  # MOVED: from apps_exec.config.agent_spec_config import load_exec_specs

        specs = load_exec_specs()
        assert specs is not None
        assert specs.version == "1.0.0"

    def test_reasoning_toggles_defaults(self) -> None:
#  # MOVED: from apps_exec.config.reasoning_toggles_config import DEFAULT_TOGGLES

        assert DEFAULT_TOGGLES.enable_capability_extraction is True
        assert DEFAULT_TOGGLES.enable_style_gate is True
        assert DEFAULT_TOGGLES.llm_narrative_enabled is False

    def test_exec_specs_personas_present(self) -> None:
#  # MOVED: from apps_exec.config.agent_spec_config import load_exec_specs

        specs = load_exec_specs()
        assert hasattr(specs, "personas")
        assert len(specs.personas) > 0


class TestExecSpineAdapter:
    def test_prefix_is_exec(self) -> None:
#  # MOVED: from apps_exec.spine.exec_spine_adapter import ExecSpineAdapter

        assert ExecSpineAdapter.__module__ == "apps_exec.spine.exec_spine_adapter"

    def test_adapter_has_execute_method(self) -> None:
    """Test adapter_has_execute_method runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute adapter_has_execute_method
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
