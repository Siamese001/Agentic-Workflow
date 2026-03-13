"""
Unit tests for apps_rfp AI Proposal / RFP Generator pipeline.

Coverage:
- RfpAgentSpecs config: required sections, industry profiles
- ProposalAssemblyEngine: sections, roadmap, risks, assumptions
- ProposalGateValidator: missing sections, empty body, risk matrix
- RfpOrchestrator: dry_run, gate pass, artifact emission, run summary
- RfpRunSummary: to_dict() completeness
"""

from __future__ import annotations


class TestRfpAgentSpecs:
    def test_default_specs_load(self):
        import apps_rfp.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_rfp_specs()
        assert specs is not None
        assert len(specs.sections) >= 6

    def test_required_sections_present(self):
        import apps_rfp.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_rfp_specs()
        required_ids = {s.section_id for s in specs.sections if s.required}
        for must_have in ["executive_summary", "implementation_roadmap", "risk_and_governance", "value_case"]:
            assert must_have in required_ids

    def test_industry_profiles_non_empty(self):
        import apps_rfp.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_rfp_specs()
        assert len(specs.industries) >= 4
        assert "financial_services" in specs.industries

    def test_roadmap_has_governance_phase_requirement(self):
        import apps_rfp.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_rfp_specs()
        assert specs.roadmap.require_governance_phase is True


class TestProposalAssemblyEngine:
    def _make_request(self, industry="technology", problem="AI governance gap"):
        from apps_rfp.types.rfp_types import ArchitecturePosture, RfpRequest

        return RfpRequest(
            problem_statement=problem,
            industry=industry,
            architecture_posture=ArchitecturePosture.CLOUD_FIRST,
        )

    def test_all_required_sections_present(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine

        engine = ProposalAssemblyEngine()
        result = engine.execute(self._make_request())
        section_ids = {s.section_id for s in result.sections}
        for req_id in [
            "executive_summary",
            "current_state",
            "future_state",
            "implementation_roadmap",
            "risk_and_governance",
            "value_case",
        ]:
            assert req_id in section_ids, f"Missing required section: {req_id}"

    def test_roadmap_has_five_phases(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine

        engine = ProposalAssemblyEngine()
        result = engine.execute(self._make_request())
        assert len(result.roadmap) == 5

    def test_roadmap_has_govern_phase(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine

        engine = ProposalAssemblyEngine()
        result = engine.execute(self._make_request())
        phase_names = [p.name.lower() for p in result.roadmap]
        assert any("govern" in name for name in phase_names)

    def test_risk_matrix_non_empty(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine

        engine = ProposalAssemblyEngine()
        result = engine.execute(self._make_request())
        assert len(result.risks) >= 3

    def test_assumptions_labeled(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine

        engine = ProposalAssemblyEngine()
        result = engine.execute(self._make_request())
        assert len(result.assumptions) >= 3
        for asm in result.assumptions:
            assert asm.assumption_id.startswith("ASM-")

    def test_sections_non_empty_bodies(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine

        engine = ProposalAssemblyEngine()
        result = engine.execute(self._make_request())
        for section in result.sections:
            assert section.body.strip(), f"Section '{section.section_id}' has empty body"

    def test_timeline_assumption_added_when_provided(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine
        from apps_rfp.types.rfp_types import ArchitecturePosture, RfpRequest

        engine = ProposalAssemblyEngine()
        req = RfpRequest(
            problem_statement="Need AI platform",
            industry="healthcare",
            architecture_posture=ArchitecturePosture.SOVEREIGN,
            delivery_timeline_weeks=24,
        )
        result = engine.execute(req)
        asm_ids = [a.assumption_id for a in result.assumptions]
        assert "ASM-004" in asm_ids


class TestProposalGateValidator:
    def _make_sections(self):
        from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine
        from apps_rfp.types.rfp_types import ArchitecturePosture, RfpRequest

        engine = ProposalAssemblyEngine()
        req = RfpRequest(
            problem_statement="test",
            industry="technology",
            architecture_posture=ArchitecturePosture.CLOUD_FIRST,
        )
        return engine.execute(req)

    def test_valid_proposal_passes(self):
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        validator = ProposalGateValidator()
        assembly = self._make_sections()
        result = validator.validate(assembly.sections, assembly.roadmap, assembly.risks)
        assert result.passed

    def test_missing_section_blocks(self):
        from apps_rfp.types.rfp_types import ProposalSection
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        validator = ProposalGateValidator()
        incomplete_sections = [
            ProposalSection(section_id="executive_summary", heading="Exec", body="Summary text."),
        ]
        assembly = self._make_sections()
        result = validator.validate(incomplete_sections, assembly.roadmap, assembly.risks)
        assert not result.passed

    def test_empty_risks_blocks(self):
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        validator = ProposalGateValidator()
        assembly = self._make_sections()
        result = validator.validate(assembly.sections, assembly.roadmap, [])
        assert not result.passed

    def test_quality_score_high_for_valid(self):
        from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

        validator = ProposalGateValidator()
        assembly = self._make_sections()
        result = validator.validate(assembly.sections, assembly.roadmap, assembly.risks)
        assert result.quality_score >= 0.70


class TestRfpOrchestrator:
    def test_dry_run_no_artifacts(self):
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator
        from apps_rfp.types.rfp_types import ProposalStatus, RfpRequest

        orch = RfpOrchestrator(dry_run=True)
        req = RfpRequest(problem_statement="Test problem", industry="technology", dry_run=True)
        result = orch.run(req)
        assert result.status == ProposalStatus.DRY_RUN
        assert len(result.artifact_paths) == 0

    def test_result_has_sections(self):
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator
        from apps_rfp.types.rfp_types import RfpRequest

        orch = RfpOrchestrator(dry_run=True)
        req = RfpRequest(problem_statement="Test problem", dry_run=True)
        result = orch.run(req)
        assert len(result.sections) > 0

    def test_trace_id_propagated(self):
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator
        from apps_rfp.types.rfp_types import RfpRequest

        orch = RfpOrchestrator(dry_run=True)
        req = RfpRequest(problem_statement="Test", trace_id="rfp-trace-001", dry_run=True)
        result = orch.run(req)
        assert result.trace_id == "rfp-trace-001"

    def test_artifacts_written_in_non_dry_run(self, tmp_path):
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator
        from apps_rfp.types.rfp_types import ProposalStatus, RfpRequest

        orch = RfpOrchestrator(dry_run=False, output_dir=str(tmp_path))
        req = RfpRequest(problem_statement="Need AI governance platform", industry="technology")
        result = orch.run(req)
        if result.status == ProposalStatus.COMPLETE:
            assert len(result.artifact_paths) > 0


class TestRfpRunSummary:
    def test_to_dict_completeness(self):
        from apps_rfp.types.rfp_types import RfpRunSummary

        summary = RfpRunSummary(trace_id="rfp-001", status="complete", industry="technology")
        d = summary.to_dict()
        required_keys = [
            "trace_id",
            "app",
            "status",
            "industry",
            "sections_generated",
            "roadmap_phases",
            "risks_identified",
            "quality_score",
            "gate_violations",
            "artifacts",
            "provenance",
        ]
        for key in required_keys:
            assert key in d, f"Missing key: {key}"
