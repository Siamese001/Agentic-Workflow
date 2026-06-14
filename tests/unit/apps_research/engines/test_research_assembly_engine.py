"""Wave 5 ADG testing-hotspots — apps_research.research_assembly_engine.

The engine's ``execute()`` pulls in a provenance ledger (lazy pydantic import)
and telemetry decorators, but the deterministic artifact-building surface is
pure: ``_build_source_register``, ``_build_sections`` (per ArtifactMode), and
``_build_comparison_matrix``. This module exercises that deterministic surface
plus the ``ResearchAssemblyResult`` dataclass defaults and module-level
comparison catalogs. Real ResearchRequest pydantic models are used as inputs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# The apps_research conftest inserts ``tests/`` onto sys.path, which would
# otherwise shadow the real top-level ``apps_research`` package with the
# ``tests/apps_research`` fixtures package. Front-load the repo root so the
# production package resolves first (house pattern from test_base_research_engine).
_REPO_ROOT = str(Path(__file__).resolve().parents[4])
if sys.path[0] != _REPO_ROOT:
    sys.path.insert(0, _REPO_ROOT)

from apps_research.engines.research_assembly_engine import (
    _AGENTIC_FRAMEWORKS,
    _COMPARISON_DIMENSIONS,
    ResearchAssemblyEngine,
    ResearchAssemblyResult,
)
from apps_research.types.research_types import ResearchRequest


@pytest.fixture
def engine() -> ResearchAssemblyEngine:
    return ResearchAssemblyEngine()


class TestModuleCatalogs:
    def test_comparison_dimensions(self):
        assert "architecture_model" in _COMPARISON_DIMENSIONS
        assert "open_source" in _COMPARISON_DIMENSIONS
        assert len(_COMPARISON_DIMENSIONS) == 6

    def test_framework_catalog_rows_have_all_dimensions(self):
        assert set(_AGENTIC_FRAMEWORKS) >= {"LangGraph", "AutoGen", "CrewAI"}
        for name, dims in _AGENTIC_FRAMEWORKS.items():
            assert set(dims) == set(_COMPARISON_DIMENSIONS), name


class TestResearchAssemblyResult:
    def test_defaults_are_empty(self):
        result = ResearchAssemblyResult()
        assert result.sections == []
        assert result.comparison_matrix == []
        assert result.source_register == []
        assert result.claim_provenance is None
        assert result.pa_slot_bindings is None

    def test_default_lists_are_independent(self):
        a = ResearchAssemblyResult()
        b = ResearchAssemblyResult()
        a.sections.append("x")  # type: ignore[arg-type]
        assert b.sections == []


class TestSourceRegister:
    def test_base_register_has_five_repo_sources(self, engine):
        req = ResearchRequest(topic="AI governance", mode="brief")
        sources = engine._build_source_register(req)
        assert len(sources) == 5
        assert sources[0].source_id == "SRC-001"
        # Confidence values are bounded.
        assert all(0.0 <= s.confidence <= 1.0 for s in sources)

    def test_comparison_subjects_append_extra_sources(self, engine):
        req = ResearchRequest(
            topic="x", mode="comparison", comparison_subjects=["LangGraph", "AutoGen"]
        )
        sources = engine._build_source_register(req)
        ids = [s.source_id for s in sources]
        assert "SRC-C01" in ids and "SRC-C02" in ids
        assert len(sources) == 7

    def test_claim_types_are_valid_literals(self, engine):
        req = ResearchRequest(topic="x", mode="brief")
        valid = {"direct_evidence", "interpretation", "analyst_inference", "assumption"}
        for s in engine._build_source_register(req):
            assert s.claim_type in valid


class TestBuildSections:
    @pytest.mark.parametrize(
        "mode,expected_first",
        [
            ("brief", "executive_summary"),
            ("comparison", "comparison_overview"),
            ("trend", "trend_overview"),
            ("position", "position_statement"),
            ("thought_leadership", "hook"),
        ],
    )
    def test_mode_produces_expected_opening_section(self, engine, mode, expected_first):
        req = ResearchRequest(topic="AI", mode=mode)
        sources = engine._build_source_register(req)
        sections = engine._build_sections(req, mode, sources)
        assert sections[0].section_id == expected_first
        assert len(sections) >= 3

    def test_unknown_mode_falls_back_to_brief(self, engine):
        req = ResearchRequest(topic="AI", mode="brief")
        sources = engine._build_source_register(req)
        sections = engine._build_sections(req, "totally_unknown_mode", sources)
        assert sections[0].section_id == "executive_summary"

    def test_sections_reference_source_ids(self, engine):
        req = ResearchRequest(topic="AI", mode="brief")
        sources = engine._build_source_register(req)
        sections = engine._build_sections(req, "brief", sources)
        # src_ids are the first four source ids (pydantic coerces to list).
        for section in sections:
            assert section.sources == ["SRC-001", "SRC-002", "SRC-003", "SRC-004"]

    def test_topic_embedded_in_body(self, engine):
        req = ResearchRequest(topic="Quantum Governance", mode="brief")
        sources = engine._build_source_register(req)
        sections = engine._build_sections(req, "brief", sources)
        assert any("Quantum Governance" in s.body for s in sections)


class TestComparisonMatrix:
    def test_default_subjects_from_catalog(self, engine):
        req = ResearchRequest(topic="x", mode="comparison")
        rows = engine._build_comparison_matrix(req)
        assert len(rows) == len(_AGENTIC_FRAMEWORKS)
        assert rows[0].subject in _AGENTIC_FRAMEWORKS

    def test_known_subject_uses_catalog_dimensions(self, engine):
        req = ResearchRequest(topic="x", mode="comparison", comparison_subjects=["LangGraph"])
        rows = engine._build_comparison_matrix(req)
        assert len(rows) == 1
        assert rows[0].dimensions == _AGENTIC_FRAMEWORKS["LangGraph"]

    def test_unknown_subject_gets_placeholder_dimensions(self, engine):
        req = ResearchRequest(
            topic="x", mode="comparison", comparison_subjects=["NovelFramework"]
        )
        rows = engine._build_comparison_matrix(req)
        assert rows[0].subject == "NovelFramework"
        assert set(rows[0].dimensions) == set(_COMPARISON_DIMENSIONS)
        assert all("Unknown" in v for v in rows[0].dimensions.values())
