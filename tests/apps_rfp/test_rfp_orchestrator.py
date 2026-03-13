"""
Tests for apps_rfp — AI Proposal / RFP Generator.

All tests are deterministic: no LLM calls, no file I/O in non-dry-run paths.
"""

from __future__ import annotations

import pytest

from apps_rfp.types.rfp_types import (
    ArchitecturePosture,
    ProposalSection,
    ProposalStatus,
    RfpRequest,
    RfpRunSummary,
    RiskItem,
    RiskSeverity,
    RoadmapPhase,
)


class TestRfpTypes:
    def test_proposal_status_values(self) -> None:
        assert ProposalStatus.COMPLETE.value == "complete"
        assert ProposalStatus.DRY_RUN.value == "dry_run"
        assert ProposalStatus.FAILED.value == "failed"

    def test_architecture_posture_values(self) -> None:
        assert ArchitecturePosture.CLOUD_FIRST.value == "cloud-first"
        assert ArchitecturePosture.SOVEREIGN.value == "sovereign"

    def test_proposal_section_frozen(self) -> None:
        section = ProposalSection(
            section_id="test",
            heading="Test",
            body="body",
        )
        with pytest.raises((AttributeError, TypeError)):
            section.heading = "changed"  # type: ignore[misc]

    def test_roadmap_phase_frozen(self) -> None:
        phase = RoadmapPhase(
            phase_id="PHASE-01",
            name="Discovery",
            duration_weeks=4,
            objectives=("Baseline assessment",),
        )
        with pytest.raises((AttributeError, TypeError)):
            phase.name = "changed"  # type: ignore[misc]

    def test_risk_item_frozen(self) -> None:
        risk = RiskItem(
            risk_id="RISK-001",
            category="technical",
            description="desc",
            severity=RiskSeverity.HIGH,
            mitigation="mitigate",
        )
        with pytest.raises((AttributeError, TypeError)):
            risk.severity = RiskSeverity.LOW  # type: ignore[misc]

    def test_rfp_request_defaults(self) -> None:
        req = RfpRequest(problem_statement="we need AI")
        assert req.industry == "technology"
        assert req.dry_run is False
        assert req.architecture_posture == ArchitecturePosture.CLOUD_FIRST

    def test_rfp_run_summary_to_dict_keys(self) -> None:
        summary = RfpRunSummary(
            trace_id="abc",
            status="complete",
            industry="technology",
        )
        d = summary.to_dict()
        assert "trace_id" in d
        assert "app" in d
        assert d["app"] == "apps_rfp"
        assert "sections_generated" in d


class TestProposalGateValidator:
    def test_passes_valid_sections(self) -> None:
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        sections = [
            ProposalSection(
                section_id="executive_summary",
                heading="Executive Summary",
                body="The AI platform delivers governance and determinism.",
                is_deterministic=True,
                evidence=("L0_routing",),
            ),
            ProposalSection(
                section_id="current_state",
                heading="Current State",
                body="Existing workflows rely on manual review with no deterministic enforcement.",
                is_deterministic=True,
            ),
            ProposalSection(
                section_id="future_state",
                heading="Future State",
                body="Agentic AI platform with six-layer enforcement and policy hash validation.",
                is_deterministic=True,
            ),
            ProposalSection(
                section_id="implementation_roadmap",
                heading="Implementation Roadmap",
                body="Phased five-stage delivery starting with Discovery.",
                is_deterministic=True,
            ),
            ProposalSection(
                section_id="risk_and_governance",
                heading="Risk and Governance",
                body="Risk controls include static analysis and policy hash validation.",
                is_deterministic=True,
            ),
            ProposalSection(
                section_id="value_case",
                heading="Value Case",
                body="Value drivers include reduced manual review cycles.",
                is_deterministic=True,
                evidence=("capability_extraction",),
            ),
        ]
        roadmap = [
            RoadmapPhase(
                phase_id="PHASE-01",
                name="Discovery",
                duration_weeks=4,
                governance_milestone="baseline",
                measurement_milestone="kpi_captured",
            ),
            RoadmapPhase(
                phase_id="PHASE-02",
                name="Build and Integrate",
                duration_weeks=8,
                governance_milestone="layer_boundaries",
                measurement_milestone="test_coverage",
            ),
            RoadmapPhase(
                phase_id="PHASE-03",
                name="Governance and Hardening",
                duration_weeks=4,
                governance_milestone="policy_enforced",
                measurement_milestone="violations_zero",
            ),
        ]
        risks = [
            RiskItem(
                risk_id="RISK-001",
                category="technical",
                description="Data quality",
                severity=RiskSeverity.HIGH,
                mitigation="ingestion gates",
            )
        ]
        validator = ProposalGateValidator()
        result = validator.validate(sections, roadmap, risks)
        assert result.passed is True

    def test_fails_missing_required_section(self) -> None:
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        sections = [
            ProposalSection(
                section_id="executive_summary",
                heading="Executive Summary",
                body="Some text.",
            )
        ]
        validator = ProposalGateValidator()
        result = validator.validate(sections, [], [])
        assert result.passed is False

    def test_quality_score_in_range(self) -> None:
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        sections = [
            ProposalSection(
                section_id="executive_summary",
                heading="Executive Summary",
                body="body",
            )
        ]
        validator = ProposalGateValidator()
        result = validator.validate(sections, [], [])
        assert 0.0 <= result.quality_score <= 1.0


class TestRfpOrchestratorDryRun:
    def test_dry_run_returns_dry_run_status(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req = RfpRequest(problem_statement="need AI platform", dry_run=True)
        orch = RfpOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.status == ProposalStatus.DRY_RUN

    def test_dry_run_no_artifact_paths(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req = RfpRequest(problem_statement="need AI platform", dry_run=True)
        orch = RfpOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.artifact_paths == []

    def test_dry_run_has_sections(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req = RfpRequest(problem_statement="need AI platform", dry_run=True)
        orch = RfpOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.sections) > 0

    def test_dry_run_has_roadmap(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req = RfpRequest(problem_statement="need AI platform", dry_run=True)
        orch = RfpOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.roadmap) > 0

    def test_dry_run_has_risks(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req = RfpRequest(problem_statement="need AI platform", dry_run=True)
        orch = RfpOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.risks) > 0

    def test_trace_id_deterministic(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req1 = RfpRequest(problem_statement="need AI platform", industry="technology")
        req2 = RfpRequest(problem_statement="need AI platform", industry="technology")
        t1 = RfpOrchestrator._make_trace_id(req1)
        t2 = RfpOrchestrator._make_trace_id(req2)
        assert t1 == t2

    def test_different_inputs_different_trace_ids(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        req1 = RfpRequest(problem_statement="need AI platform", industry="technology")
        req2 = RfpRequest(problem_statement="need AI platform", industry="healthcare")
        t1 = RfpOrchestrator._make_trace_id(req1)
        t2 = RfpOrchestrator._make_trace_id(req2)
        assert t1 != t2

    def test_all_industries_complete_dry_run(self) -> None:
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator

        for industry in ["financial_services", "healthcare", "technology", "government"]:
            req = RfpRequest(problem_statement="need AI", industry=industry, dry_run=True)
            orch = RfpOrchestrator(dry_run=True)
            result = orch.run(req)
            assert result.status in (ProposalStatus.DRY_RUN, ProposalStatus.COMPLETE), (
                f"Unexpected status {result.status} for industry={industry}"
            )


class TestRfpConfig:
    def test_load_rfp_specs_returns_defaults(self) -> None:
        from apps_rfp.config.agent_spec_config import load_rfp_specs

        specs = load_rfp_specs()
        assert specs is not None
        assert specs.version == "1.0.0"

    def test_required_sections_present(self) -> None:
        from apps_rfp.config.agent_spec_config import load_rfp_specs

        specs = load_rfp_specs()
        section_ids = {s.section_id for s in specs.sections}
        must_have = {"executive_summary", "implementation_roadmap", "risk_and_governance", "value_case"}
        assert must_have.issubset(section_ids)

    def test_reasoning_toggles_defaults(self) -> None:
        from apps_rfp.config.reasoning_toggles_config import DEFAULT_TOGGLES

        assert DEFAULT_TOGGLES.enable_roadmap_generation is True
        assert DEFAULT_TOGGLES.enable_risk_matrix is True
        assert DEFAULT_TOGGLES.llm_narrative_enabled is False

    def test_industry_profiles_configured(self) -> None:
        from apps_rfp.config.agent_spec_config import load_rfp_specs

        specs = load_rfp_specs()
        assert "technology" in specs.industries
        assert "healthcare" in specs.industries
        assert "financial_services" in specs.industries
