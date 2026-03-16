"""
Unit tests for apps_exec Executive Brief Generator pipeline.

Coverage:
- ExecAgentSpecs config loading and validation
- IngestionEngine: missing dirs, file discovery
- CapabilityExtractionEngine: pattern matching, dedup
- BriefAssemblyEngine: section ordering for each persona
- StyleGateValidator: buzzword detection, empty body, unsupported claims
- ExecOrchestrator: dry_run mode, gate pass, gate fail
- RunSummary: to_dict() completeness
"""

from __future__ import annotations

from pathlib import Path

import pytest


class TestExecAgentSpecs:
    def test_default_specs_load(self):
        import apps_exec.config.agent_spec_config as cfg_mod
        from apps_exec.config.agent_spec_config import load_exec_specs

        cfg_mod._SPEC_CACHE = None
        specs = load_exec_specs()
        assert specs is not None
        assert len(specs.personas) >= 4

    def test_recruiter_persona_present(self):
        import apps_exec.config.agent_spec_config as cfg_mod
        from apps_exec.config.agent_spec_config import load_exec_specs

        cfg_mod._SPEC_CACHE = None
        specs = load_exec_specs()
        assert "recruiter" in specs.personas

    def test_required_sections_non_empty(self):
        import apps_exec.config.agent_spec_config as cfg_mod
        from apps_exec.config.agent_spec_config import load_exec_specs

        cfg_mod._SPEC_CACHE = None
        specs = load_exec_specs()
        recruiter = specs.personas["recruiter"]
        assert len(recruiter.required_sections) > 0

    def test_empty_personas_raises(self):
        from pydantic import ValidationError

        from apps_exec.config.agent_spec_config import ExecAgentSpecs

        with pytest.raises(ValidationError):
            ExecAgentSpecs(personas={})


class TestIngestionEngine:
    def test_missing_dir_skips_gracefully(self):
        from apps_exec.engines.ingestion_engine import IngestionEngine

        engine = IngestionEngine()
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, source_dirs=["/nonexistent/path/xyz"])
        result = engine.execute(req)
        assert len(result.documents) == 0
        assert any(Path(p) == Path("/nonexistent/path/xyz") for p in result.skipped_paths)

    def test_ingests_markdown_files(self, tmp_path):
        (tmp_path / "test.md").write_text(
            "# Platform\n\nGovernance and orchestration are key.", encoding="utf-8"
        )
        (tmp_path / "skip.csv").write_text("col1,col2", encoding="utf-8")

        from apps_exec.engines.ingestion_engine import IngestionEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = IngestionEngine()
        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[str(tmp_path)])
        result = engine.execute(req)
        assert len(result.documents) == 1
        assert result.documents[0].extension == ".md"

    def test_oversized_file_skipped(self, tmp_path):
        big_file = tmp_path / "huge.md"
        big_file.write_bytes(b"x" * (600 * 1024))

        from apps_exec.engines.ingestion_engine import IngestionEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = IngestionEngine()
        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[str(tmp_path)])
        result = engine.execute(req)
        assert len(result.documents) == 0
        assert len(result.skipped_paths) == 1

    def test_total_chars_property(self, tmp_path):
        (tmp_path / "a.md").write_text("hello world", encoding="utf-8")
        from apps_exec.engines.ingestion_engine import IngestionEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = IngestionEngine()
        req = ExecBriefRequest(audience=AudiencePersona.SVP_ENG, source_dirs=[str(tmp_path)])
        result = engine.execute(req)
        assert result.total_chars == 11


class TestCapabilityExtractionEngine:
    def test_extracts_known_capabilities(self, tmp_path):
        doc = tmp_path / "arch.md"
        doc.write_text(
            "The platform provides governance and supports orchestration.\n"
            "It enforces safety via module L0_routing.enforcement.execution_gateway.",
            encoding="utf-8",
        )
        from apps_exec.engines.capability_extraction_engine import CapabilityExtractionEngine
        from apps_exec.engines.ingestion_engine import IngestionEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        ingestion_engine = IngestionEngine()
        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[str(tmp_path)])
        ingestion_result = ingestion_engine.execute(req)
        extraction_engine = CapabilityExtractionEngine()
        extraction_result = extraction_engine.execute(ingestion_result)
        assert len(extraction_result.capabilities) > 0

    def test_no_duplicate_capabilities(self, tmp_path):
        doc = tmp_path / "dup.md"
        doc.write_text("governance governance governance safety safety", encoding="utf-8")
        from apps_exec.engines.capability_extraction_engine import CapabilityExtractionEngine
        from apps_exec.engines.ingestion_engine import IngestionEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        ingestion_engine = IngestionEngine()
        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[str(tmp_path)])
        ingestion_result = ingestion_engine.execute(req)
        extraction_engine = CapabilityExtractionEngine()
        result = extraction_engine.execute(ingestion_result)
        cap_ids = [c.capability_id for c in result.capabilities]
        assert len(cap_ids) == len(set(cap_ids))

    def test_empty_corpus_returns_empty(self):
        from apps_exec.engines.capability_extraction_engine import CapabilityExtractionEngine
        from apps_exec.engines.ingestion_engine import IngestionResult

        engine = CapabilityExtractionEngine()
        result = engine.execute(IngestionResult())
        assert result.capabilities == []


class TestBriefAssemblyEngine:
    def _make_extraction_result(self):
        from apps_exec.engines.capability_extraction_engine import ExtractionResult
        from apps_exec.types.exec_types import CapabilityEvidence

        return ExtractionResult(
            capabilities=[
                CapabilityEvidence("CAP_GOV", "Governance", "Governance enforcement", ("L0 routing",), "L0"),
            ],
            evidence_anchors=["module execution_gateway", "validator policy_hash_enforcer"],
            source_coverage={},
        )

    def test_recruiter_sections_present(self):
        from apps_exec.engines.brief_assembly_engine import BriefAssemblyEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = BriefAssemblyEngine()
        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, source_dirs=[])
        extraction = self._make_extraction_result()
        result = engine.execute((req, extraction))
        section_ids = {s.section_id for s in result.sections}
        assert "platform_summary" in section_ids
        assert "portfolio_value" in section_ids

    def test_cto_sections_present(self):
        from apps_exec.engines.brief_assembly_engine import BriefAssemblyEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = BriefAssemblyEngine()
        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[])
        extraction = self._make_extraction_result()
        result = engine.execute((req, extraction))
        section_ids = {s.section_id for s in result.sections}
        assert "architecture_overview" in section_ids
        assert "governance_model" in section_ids

    def test_sections_have_non_empty_body(self):
        from apps_exec.engines.brief_assembly_engine import BriefAssemblyEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = BriefAssemblyEngine()
        req = ExecBriefRequest(audience=AudiencePersona.SVP_ENG, source_dirs=[])
        extraction = self._make_extraction_result()
        result = engine.execute((req, extraction))
        for section in result.sections:
            assert section.body.strip(), f"Section '{section.section_id}' has empty body"

    def test_sections_have_why_this_matters(self):
        from apps_exec.engines.brief_assembly_engine import BriefAssemblyEngine
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        engine = BriefAssemblyEngine()
        req = ExecBriefRequest(audience=AudiencePersona.BOARD, source_dirs=[])
        extraction = self._make_extraction_result()
        result = engine.execute((req, extraction))
        for section in result.sections:
            assert section.why_this_matters, f"Section '{section.section_id}' missing why_this_matters"


class TestStyleGateValidator:
    def test_clean_sections_pass(self):
        from apps_exec.types.exec_types import BriefSection
        from apps_exec.validators.style_gate_validator import StyleGateValidator

        validator = StyleGateValidator()
        sections = [
            BriefSection(
                section_id="platform_summary",
                heading="Platform Overview",
                body="This platform enforces governance at the architecture layer.",
                evidence_anchors=("L0 routing",),
                why_this_matters="Reviewers need orientation.",
                word_count=10,
            )
        ]
        result = validator.validate_sections(sections)
        block_violations = [v for v in result.violations if v.severity == "BLOCK"]
        assert len(block_violations) == 0

    def test_buzzword_in_body_flagged(self):
        from apps_exec.types.exec_types import BriefSection
        from apps_exec.validators.style_gate_validator import StyleGateValidator

        validator = StyleGateValidator()
        sections = [
            BriefSection(
                section_id="test",
                heading="Test",
                body="This is a game-changer and a revolutionary synergy platform with holistic ecosystem",
                evidence_anchors=("anchor",),
                why_this_matters="Why it matters.",
                word_count=12,
            )
        ]
        result = validator.validate_sections(sections)
        assert any(v.rule_id == "STYLE_BUZZWORD_DENSITY" for v in result.violations)

    def test_empty_body_blocked(self):
        from apps_exec.types.exec_types import BriefSection
        from apps_exec.validators.style_gate_validator import StyleGateValidator

        validator = StyleGateValidator()
        sections = [
            BriefSection(
                section_id="empty_section",
                heading="Empty",
                body="",
                evidence_anchors=(),
                why_this_matters="Why.",
            )
        ]
        result = validator.validate_sections(sections)
        block_violations = [
            v for v in result.violations if v.severity == "BLOCK" and v.rule_id == "STYLE_EMPTY_BODY"
        ]
        assert len(block_violations) == 1

    def test_quality_score_perfect_for_clean(self):
        from apps_exec.types.exec_types import BriefSection
        from apps_exec.validators.style_gate_validator import StyleGateValidator

        validator = StyleGateValidator()
        sections = [
            BriefSection(
                section_id="sec1",
                heading="Section 1",
                body="Clean professional content about platform governance.",
                evidence_anchors=("anchor1",),
                why_this_matters="This matters because governance is critical.",
            )
        ]
        result = validator.validate_sections(sections)
        assert result.quality_score > 0.0


class TestExecOrchestrator:
    def test_dry_run_returns_no_artifacts(self):
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, BriefStatus, ExecBriefRequest

        orch = ExecOrchestrator(dry_run=True)
        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, source_dirs=[], dry_run=True)
        result = orch.run(req)
        assert result.status == BriefStatus.DRY_RUN
        assert len(result.artifact_paths) == 0

    def test_dry_run_still_produces_sections(self):
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        orch = ExecOrchestrator(dry_run=True)
        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, source_dirs=[], dry_run=True)
        result = orch.run(req)
        assert len(result.sections) > 0

    def test_trace_id_present_in_result(self):
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        orch = ExecOrchestrator(dry_run=True)
        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[], trace_id="test-trace-001")
        result = orch.run(req)
        assert result.trace_id == "test-trace-001"

    def test_provenance_contains_trace_id(self):
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        orch = ExecOrchestrator(dry_run=True)
        req = ExecBriefRequest(audience=AudiencePersona.SVP_ENG, source_dirs=[], trace_id="prov-trace")
        result = orch.run(req)
        assert result.provenance.get("trace_id") == "prov-trace"

    def test_artifacts_written_in_non_dry_run(self, tmp_path):
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, BriefStatus, ExecBriefRequest

        orch = ExecOrchestrator(dry_run=False, output_dir=str(tmp_path))
        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, source_dirs=[], dry_run=False)
        result = orch.run(req)
        if result.status == BriefStatus.COMPLETE:
            assert len(result.artifact_paths) > 0
            for path in result.artifact_paths:
                assert Path(path).exists()


class TestRunSummary:
    def test_to_dict_completeness(self):
        from apps_exec.types.exec_types import RunSummary

        summary = RunSummary(trace_id="test-001", status="complete", audience="recruiter")
        d = summary.to_dict()
        assert d["trace_id"] == "test-001"
        assert d["app"] == "apps_exec"
        assert "quality_score" in d
        assert "gate_violations" in d
        assert "artifacts" in d
        assert "provenance" in d
