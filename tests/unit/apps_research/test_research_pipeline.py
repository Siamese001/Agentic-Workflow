"""
Unit tests for apps_research Autonomous Research Engine pipeline.

Coverage:
- ResearchAgentSpecs: artifact modes, source register config
- ResearchAssemblyEngine: sections per mode, comparison matrix, source register
- ResearchGateValidator: missing sections, empty source register
- ResearchOrchestrator: dry_run, mode routing, source register emission
- ResearchRunSummary: to_dict() completeness
"""

from __future__ import annotations

from pathlib import Path


class TestResearchAgentSpecs:
    def test_default_specs_load(self):
        import apps_research.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_research_specs()
        assert specs is not None
        assert len(specs.artifact_modes) >= 5

    def test_all_modes_present(self):
        import apps_research.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_research_specs()
        for mode in ["brief", "comparison", "trend", "position", "thought_leadership"]:
            assert mode in specs.artifact_modes, f"Missing mode: {mode}"

    def test_comparison_mode_requires_comparison_table(self):
        import apps_research.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_research_specs()
        assert specs.artifact_modes["comparison"].requires_comparison_table is True

    def test_source_register_required_fields(self):
        import apps_research.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_research_specs()
        required = specs.source_register.required_fields
        assert "source_id" in required
        assert "claim_type" in required
        assert "confidence" in required


class TestResearchAssemblyEngine:
    def test_brief_mode_required_sections(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, AudienceStyle, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(
            topic="agentic AI governance",
            mode=ArtifactMode.BRIEF,
            audience_style=AudienceStyle.TECHNICAL,
        )
        result = engine.execute(req)
        section_ids = {s.section_id for s in result.sections}
        assert "executive_summary" in section_ids
        assert "key_findings" in section_ids
        assert "strategic_implications" in section_ids

    def test_comparison_mode_builds_matrix(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(
            topic="agentic frameworks",
            mode=ArtifactMode.COMPARISON,
            comparison_subjects=["LangGraph", "AutoGen"],
        )
        result = engine.execute(req)
        assert len(result.comparison_matrix) >= 2
        subjects = [row.subject for row in result.comparison_matrix]
        assert "LangGraph" in subjects
        assert "AutoGen" in subjects

    def test_source_register_non_empty(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="governance patterns", mode=ArtifactMode.BRIEF)
        result = engine.execute(req)
        assert len(result.source_register) > 0

    def test_source_register_has_required_fields(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="governance", mode=ArtifactMode.BRIEF)
        result = engine.execute(req)
        for src in result.source_register:
            assert src.source_id
            assert src.title
            assert src.confidence >= 0.0

    def test_claim_types_labeled_in_sections(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="determinism contracts", mode=ArtifactMode.BRIEF)
        result = engine.execute(req)
        for section in result.sections:
            assert section.claim_type is not None

    def test_thought_leadership_mode(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="constitutional governance", mode=ArtifactMode.THOUGHT_LEADERSHIP)
        result = engine.execute(req)
        section_ids = {s.section_id for s in result.sections}
        assert "hook" in section_ids
        assert "insight" in section_ids
        assert "evidence" in section_ids
        assert "call_to_action" in section_ids

    def test_trend_mode_sections(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="agentic AI trend", mode=ArtifactMode.TREND, time_horizon="12 months")
        result = engine.execute(req)
        section_ids = {s.section_id for s in result.sections}
        assert "trend_overview" in section_ids
        assert "horizon_implications" in section_ids


class TestResearchGateValidator:
    def test_valid_artifact_passes(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest
        from apps_research.validators.research_gate_validator import ResearchGateValidator

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="governance", mode=ArtifactMode.BRIEF)
        assembly = engine.execute(req)
        validator = ResearchGateValidator()
        result = validator.validate(
            assembly.sections,
            assembly.source_register,
            ["executive_summary", "key_findings", "strategic_implications"],
        )
        assert result.passed

    def test_empty_source_register_blocks(self):
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest
        from apps_research.validators.research_gate_validator import ResearchGateValidator

        engine = ResearchAssemblyEngine()
        req = ResearchRequest(topic="test", mode=ArtifactMode.BRIEF)
        assembly = engine.execute(req)
        validator = ResearchGateValidator()
        result = validator.validate(assembly.sections, [], [])
        assert not result.passed

    def test_missing_required_section_blocks(self):
        from apps_research.types.research_types import ClaimType, ResearchSection
        from apps_research.validators.research_gate_validator import ResearchGateValidator

        validator = ResearchGateValidator()
        sections = [
            ResearchSection(
                section_id="executive_summary",
                heading="Summary",
                body="Content here.",
                claim_type=ClaimType.DIRECT_EVIDENCE,
            )
        ]
        from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        engine = ResearchAssemblyEngine()
        assembly = engine.execute(ResearchRequest(topic="t", mode=ArtifactMode.BRIEF))
        result = validator.validate(sections, assembly.source_register, ["executive_summary", "key_findings"])
        assert not result.passed


class TestResearchOrchestrator:
    def test_dry_run_no_artifacts(self):
        from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
        from apps_research.types.research_types import ArtifactMode, ResearchRequest, ResearchStatus

        orch = ResearchOrchestrator(dry_run=True)
        req = ResearchRequest(topic="governance", mode=ArtifactMode.BRIEF, dry_run=True)
        result = orch.run(req)
        assert result.status == ResearchStatus.DRY_RUN
        assert len(result.artifact_paths) == 0

    def test_result_has_sections(self):
        from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        orch = ResearchOrchestrator(dry_run=True)
        req = ResearchRequest(topic="platform strategy", mode=ArtifactMode.BRIEF, dry_run=True)
        result = orch.run(req)
        assert len(result.sections) >= 3

    def test_comparison_mode_has_matrix(self):
        from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        orch = ResearchOrchestrator(dry_run=True)
        req = ResearchRequest(
            topic="framework comparison",
            mode=ArtifactMode.COMPARISON,
            comparison_subjects=["LangGraph", "CrewAI"],
            dry_run=True,
        )
        result = orch.run(req)
        assert len(result.comparison_matrix) >= 2

    def test_artifacts_written_in_non_dry_run(self, tmp_path):
        from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
        from apps_research.types.research_types import ArtifactMode, ResearchRequest, ResearchStatus

        orch = ResearchOrchestrator(dry_run=False, output_dir=str(tmp_path))
        req = ResearchRequest(topic="governance patterns", mode=ArtifactMode.BRIEF)
        result = orch.run(req)
        if result.status == ResearchStatus.COMPLETE:
            assert len(result.artifact_paths) > 0
            for path in result.artifact_paths:
                assert Path(path).exists()

    def test_source_register_in_result(self):
        from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
        from apps_research.types.research_types import ArtifactMode, ResearchRequest

        orch = ResearchOrchestrator(dry_run=True)
        req = ResearchRequest(topic="determinism", mode=ArtifactMode.BRIEF, dry_run=True)
        result = orch.run(req)
        assert len(result.source_register) > 0


class TestResearchRunSummary:
    def test_to_dict_completeness(self):
        from apps_research.types.research_types import ResearchRunSummary

        summary = ResearchRunSummary(
            trace_id="res-001",
            status="complete",
            topic="governance",
            mode="brief",
        )
        d = summary.to_dict()
        for key in [
            "trace_id",
            "app",
            "status",
            "topic",
            "mode",
            "sections_generated",
            "sources_registered",
            "quality_score",
            "gate_violations",
            "artifacts",
            "provenance",
        ]:
            assert key in d, f"Missing key: {key}"
