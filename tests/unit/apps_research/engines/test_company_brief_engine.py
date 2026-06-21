"""Wave 5 ADG testing-hotspots — apps_research.company_brief_engine.

CompanyBriefEngine.execute() drives SearXNG + an LLM synthesis cascade, but the
engine carries a substantial *pure* static/deterministic surface that needs no
provider: payload extraction, the env-flagged V2 toggle, prompt construction,
tolerant JSON parsing with fail-closed errors, the stub-disabled synthesis gate, JD
context normalization (incl. content hashing), and schema-shaped brief
assembly. This module covers that surface with real inputs. No mocks.
"""

from __future__ import annotations

import hashlib
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

from apps_research.engines.company_brief_engine import (
    CompanyBriefEngine,
    CompanyBriefUnavailableError,
    _v2_enabled,
)


@pytest.fixture
def engine() -> CompanyBriefEngine:
    return CompanyBriefEngine()


class TestFacetQueries:
    def test_facet_query_templates_present(self, engine):
        facets = [f for f, _ in engine._FACET_QUERIES]
        assert "overview" in facets
        assert "leadership" in facets
        assert "commercial_motion" in facets
        assert "partner_ecosystem" in facets
        assert "adoption_motion" in facets
        assert len(engine._FACET_QUERIES) == 10

    def test_templates_use_company_placeholder(self, engine):
        for _facet, template in engine._FACET_QUERIES:
            assert "{company}" in template


class TestV2Flag:
    def test_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("APPS_RESEARCH_RETRIEVAL_V2", raising=False)
        assert _v2_enabled() is False

    @pytest.mark.parametrize("val", ["1", "true", "yes", "on"])
    def test_truthy_values_enable(self, monkeypatch, val):
        monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", val)
        assert _v2_enabled() is True

    @pytest.mark.parametrize("val", ["0", "false", "no", ""])
    def test_falsey_values_disable(self, monkeypatch, val):
        monkeypatch.setenv("APPS_RESEARCH_RETRIEVAL_V2", val)
        assert _v2_enabled() is False


class TestExtract:
    def test_extract_from_dict(self, engine):
        assert engine._extract({"topic": "Acme"}, "topic") == "Acme"

    def test_extract_from_attr(self, engine):
        class Obj:
            topic = "Beta"

        assert engine._extract(Obj(), "topic") == "Beta"

    def test_extract_missing_returns_default(self, engine):
        assert engine._extract({}, "missing", default="fallback") == "fallback"

    def test_extract_non_dict_non_attr_returns_default(self, engine):
        assert engine._extract(42, "topic") is None


class TestBuildSynthesisPrompt:
    def test_includes_topic_and_facets(self, engine):
        prompt = engine._build_synthesis_prompt(
            topic="Acme Corp",
            findings={"overview": "founded 2010"},
            jd_facets=["python", "data"],
        )
        assert "Acme Corp" in prompt
        assert "python, data" in prompt
        assert "founded 2010" in prompt
        assert "strictly JSON" in prompt

    def test_empty_findings_marked(self, engine):
        prompt = engine._build_synthesis_prompt(
            topic="X", findings={"overview": ""}, jd_facets=[]
        )
        assert "(no research available)" in prompt
        assert "(none provided)" in prompt


class TestParseSynthesis:
    def test_extracts_embedded_json(self, engine):
        out = engine._parse_synthesis(
            'noise {"tagline": "hi", "core_offerings": ["x"]} trailing',
            topic="X",
            jd_facets=[],
        )
        assert out["tagline"] == "hi"

    def test_invalid_json_raises(self, engine):
        with pytest.raises(CompanyBriefUnavailableError, match="structured synthesis JSON parse failed"):
            engine._parse_synthesis("no json here", topic="Acme", jd_facets=["data"])

    def test_malformed_braces_raises(self, engine):
        with pytest.raises(CompanyBriefUnavailableError, match="structured synthesis JSON parse failed"):
            engine._parse_synthesis("{not valid json", topic="Acme", jd_facets=[])


class TestStubSynthesis:
    def test_stub_synthesis_disabled(self, engine):
        with pytest.raises(CompanyBriefUnavailableError, match="stub synthesis disabled"):
            engine._stub_synthesis(topic="Acme", jd_facets=[])


class TestResolveJdContext:
    def test_no_jd_returns_empty(self, engine):
        assert engine._resolve_jd_context({"topic": "X"}) == {}

    def test_empty_jd_dict_returns_empty(self, engine):
        assert engine._resolve_jd_context({"jd_context": {}}) == {}

    def test_content_hash_computed_when_absent(self, engine):
        out = engine._resolve_jd_context({"jd_context": {"content": "JD body text"}})
        expected = "sha256-" + hashlib.sha256(b"JD body text").hexdigest()[:16]
        assert out["jd_content_hash"] == expected

    def test_existing_hash_preserved(self, engine):
        out = engine._resolve_jd_context(
            {"jd_context": {"content": "x", "jd_content_hash": "preset"}}
        )
        assert out["jd_content_hash"] == "preset"

    def test_reads_attribute_form(self, engine):
        class Obj:
            jd_context = {"jd_ref": "ref-1"}

        out = engine._resolve_jd_context(Obj())
        assert out["jd_content_hash"].startswith("sha256-")


class TestCuratedTargetingFallback:
    def test_adaptive_research_blocks_when_search_is_empty_instead_of_curated_pack(
        self, monkeypatch, engine
    ):
        def _boom(*_args, **_kwargs):
            raise RuntimeError("usage limit")

        monkeypatch.setattr(
            "apps_research.integrations.search_retrieval.retrieve",
            _boom,
        )

        with pytest.raises(
            CompanyBriefUnavailableError,
            match="adaptive research returned no grounded findings",
        ):
            engine._run_research_adaptive(
                topic="Anthropic",
                depth_profile="COMPANY_BRIEF_STANDARD",
                jd_context={
                    "company_name": "Anthropic",
                    "job_title": "Manager of Applied AI Architecture, Partnerships",
                },
            )

    def test_active_company_brief_retrieval_path_does_not_import_tavily(self):
        import inspect

        source = inspect.getsource(CompanyBriefEngine)
        assert "apps_research.integrations.tavily_retrieval" not in source


class TestAssembleBrief:
    def test_schema_shape(self, engine):
        synthesis = {
            "company_archetype": "scale-up enterprise vendor",
            "company_dna": {
                "archetype": "scale-up enterprise vendor",
                "commercial_motion": "partner-led growth",
                "partner_ecosystem": "GSI + ISV",
                "adoption_motion": "technical close and enablement",
                "operating_tension": "speed versus governance",
                "distinguishing_traits": ["co-sell discipline", "ecosystem revenue"],
            },
            "tagline": "Acme modernizes enterprise workflows through partner-led platform adoption.",
            "core_offerings": ["platform", "services"],
            "strategic_priorities": ["partner scale", "AI adoption"],
            "verticals": ["insurance"],
            "buyer_titles": ["SVP"],
            "tech_stack_signals": ["AWS"],
            "commercial_motion": ["co-sell"],
            "partner_ecosystem": ["GSI", "ISV"],
            "adoption_motion": ["pilot to production"],
            "leadership": [{"name": "A", "title": "CEO", "background": "exec"}],
            "competitive_set": ["Competitor"],
            "recent_moves": [{"date": "2026-01-01", "event": "launch", "signal": "partner"}],
            "language_to_mirror": ["partner-led"],
            "language_to_avoid": ["generic"],
        }
        brief = engine._assemble_brief(topic="Acme", synthesis=synthesis)
        assert brief["company"] == "Acme"
        assert brief["source"] == "apps_research"
        assert brief["freshness_ttl_days"] == 30
        assert "overview" in brief
        assert "core_offerings" in brief["overview"]
        assert "company_dna" in brief
        assert "commercial_motion" in brief
        assert "partner_ecosystem" in brief
        assert "customer_profile" in brief

    def test_missing_synthesis_keys_default_to_empty(self, engine):
        brief = engine._assemble_brief(topic="Acme", synthesis={})
        assert brief["overview"]["tagline"] == "Acme"  # falls back to topic
        assert brief["strategic_priorities"] == []
        assert brief["language_to_mirror"] == []

    def test_fetched_at_is_iso_timestamp(self, engine):
        brief = engine._assemble_brief(topic="Acme", synthesis={})
        # ISO 8601 with timezone — contains a 'T' separator.
        assert "T" in brief["fetched_at"]
