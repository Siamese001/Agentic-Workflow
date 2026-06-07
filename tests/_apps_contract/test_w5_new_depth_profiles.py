"""Contract tests for DS-5 W5: new depth profiles beyond DOSSIER.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-research-deferred-scope-b7e3d2.md W5 (DS-5).

Acceptance criteria:
- COMPANY_BRIEF_COMPETITIVE_SCAN profile exists with documented thresholds.
- COMPANY_BRIEF_FORENSIC profile exists with documented thresholds.
- Forensic covers all catalog families (including DS-5 additions).
- Aliases ('forensic', 'competitive_scan', etc.) resolve correctly.
- decompose_coverage_families works for both new profiles.
- New families (competitive_intel, regulatory_and_legal) are in catalog.
- SLO.md contains new profile rows.
- Mocked engine integration: FORENSIC profile gate not FAIL with 35 stub sources.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine():
    from apps_research.engines.company_brief_engine import CompanyBriefEngine
    return CompanyBriefEngine()


def _stub_findings(n: int) -> dict:
    """Return findings as {family: url_blob} — the shape _build_c0_bundle expects."""
    from apps_research.engines.query_decomposer import _COVERAGE_FAMILY_CATALOG
    families = list(_COVERAGE_FAMILY_CATALOG.keys())
    urls = [f"https://src{i}.example.com/doc" for i in range(n)]
    per_family = max(1, n // len(families))
    findings: dict = {}
    for idx, fam in enumerate(families):
        start = idx * per_family
        end = start + per_family if idx < len(families) - 1 else n
        findings[fam] = "\n".join(urls[start:end])
    return findings


_SYNTHESIS = {
    "tagline": "Corp",
    "strategic_priorities": ["Growth"],
    "verticals": ["enterprise"],
    "buyer_titles": ["CTO"],
    "tech_stack_signals": ["k8s"],
    "cultural_cues": ["open source"],
    "leadership": [{"name": "Jane CEO"}],
    "competitive_set": ["Rival"],
    "pain_points_inferred": ["scale"],
    "recent_moves": ["Partnership"],
}


def _run_profile_engine(profile: str, n_sources: int) -> dict:
    engine = _make_engine()
    findings = _stub_findings(n_sources)
    with (
        patch.object(engine, "_run_research_adaptive", return_value=findings),
        patch.object(engine, "_run_research_v2", return_value=findings),
        patch.object(engine, "_synthesize", return_value=_SYNTHESIS),
    ):
        return engine.execute({"topic": "ForensicCorp", "depth": profile})


# ---------------------------------------------------------------------------
# 5.1 New catalog families
# ---------------------------------------------------------------------------

class TestNewCoverageFamilies:
    def test_competitive_intel_in_catalog(self):
        from apps_research.engines.query_decomposer import _COVERAGE_FAMILY_CATALOG
        assert "competitive_intel" in _COVERAGE_FAMILY_CATALOG

    def test_regulatory_and_legal_in_catalog(self):
        from apps_research.engines.query_decomposer import _COVERAGE_FAMILY_CATALOG
        assert "regulatory_and_legal" in _COVERAGE_FAMILY_CATALOG

    def test_catalog_now_has_ten_families(self):
        from apps_research.engines.query_decomposer import _COVERAGE_FAMILY_CATALOG
        assert len(_COVERAGE_FAMILY_CATALOG) == 10

    def test_competitive_intel_query_template_present(self):
        from apps_research.engines.query_decomposer import _COVERAGE_FAMILY_CATALOG
        tmpl = _COVERAGE_FAMILY_CATALOG["competitive_intel"].get("query_template", "")
        assert "{topic}" in tmpl

    def test_regulatory_and_legal_query_template_present(self):
        from apps_research.engines.query_decomposer import _COVERAGE_FAMILY_CATALOG
        tmpl = _COVERAGE_FAMILY_CATALOG["regulatory_and_legal"].get("query_template", "")
        assert "{topic}" in tmpl


# ---------------------------------------------------------------------------
# 5.2 COMPETITIVE_SCAN profile thresholds
# ---------------------------------------------------------------------------

class TestCompetitiveScanProfile:
    def test_competitive_scan_profile_exists(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert "COMPANY_BRIEF_COMPETITIVE_SCAN" in _DEPTH_PROFILES

    def test_competitive_scan_min_sources(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_COMPETITIVE_SCAN"]["min_sources"] == 20

    def test_competitive_scan_min_citation_anchors(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_COMPETITIVE_SCAN"]["min_citation_anchors"] == 35

    def test_competitive_scan_max_queries(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_COMPETITIVE_SCAN"]["max_queries"] == 12

    def test_competitive_scan_gate_weak_floor(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_COMPETITIVE_SCAN"]["gate_weak_floor"] == 0.65

    def test_competitive_scan_alias_resolves(self):
        from apps_research.engines.query_decomposer import _resolve_depth_profile
        assert _resolve_depth_profile("competitive_scan") == "COMPANY_BRIEF_COMPETITIVE_SCAN"
        assert _resolve_depth_profile("competitive") == "COMPANY_BRIEF_COMPETITIVE_SCAN"
        assert _resolve_depth_profile("COMPANY_BRIEF_COMPETITIVE_SCAN") == "COMPANY_BRIEF_COMPETITIVE_SCAN"

    def test_competitive_scan_required_families(self):
        from apps_research.engines.query_decomposer import _PROFILE_REQUIRED_FAMILIES
        families = set(_PROFILE_REQUIRED_FAMILIES["COMPANY_BRIEF_COMPETITIVE_SCAN"])
        assert "competitive_intel" in families
        assert "competitive_landscape" in families

    def test_competitive_scan_decompose_returns_plans(self):
        from apps_research.engines.query_decomposer import decompose_coverage_families, _PROFILE_REQUIRED_FAMILIES
        plans = decompose_coverage_families("CompetitiveCorp", "COMPANY_BRIEF_COMPETITIVE_SCAN")
        required = _PROFILE_REQUIRED_FAMILIES["COMPANY_BRIEF_COMPETITIVE_SCAN"]
        assert len(plans) == len(required)
        assert {p.family for p in plans} == set(required)


# ---------------------------------------------------------------------------
# 5.3 FORENSIC profile thresholds
# ---------------------------------------------------------------------------

class TestForensicProfile:
    def test_forensic_profile_exists(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert "COMPANY_BRIEF_FORENSIC" in _DEPTH_PROFILES

    def test_forensic_min_sources(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_FORENSIC"]["min_sources"] == 35

    def test_forensic_min_citation_anchors(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_FORENSIC"]["min_citation_anchors"] == 60

    def test_forensic_max_queries(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_FORENSIC"]["max_queries"] == 20

    def test_forensic_gate_weak_floor(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        assert _DEPTH_PROFILES["COMPANY_BRIEF_FORENSIC"]["gate_weak_floor"] == 0.80

    def test_forensic_alias_resolves(self):
        from apps_research.engines.query_decomposer import _resolve_depth_profile
        assert _resolve_depth_profile("forensic") == "COMPANY_BRIEF_FORENSIC"
        assert _resolve_depth_profile("due_diligence") == "COMPANY_BRIEF_FORENSIC"
        assert _resolve_depth_profile("COMPANY_BRIEF_FORENSIC") == "COMPANY_BRIEF_FORENSIC"

    def test_forensic_covers_all_catalog_families(self):
        from apps_research.engines.query_decomposer import (
            _COVERAGE_FAMILY_CATALOG,
            _PROFILE_REQUIRED_FAMILIES,
        )
        forensic = set(_PROFILE_REQUIRED_FAMILIES["COMPANY_BRIEF_FORENSIC"])
        assert forensic == set(_COVERAGE_FAMILY_CATALOG.keys())

    def test_forensic_includes_ds5_families(self):
        from apps_research.engines.query_decomposer import _PROFILE_REQUIRED_FAMILIES
        forensic = set(_PROFILE_REQUIRED_FAMILIES["COMPANY_BRIEF_FORENSIC"])
        assert "competitive_intel" in forensic
        assert "regulatory_and_legal" in forensic

    def test_forensic_decompose_returns_all_families(self):
        from apps_research.engines.query_decomposer import (
            decompose_coverage_families,
            _COVERAGE_FAMILY_CATALOG,
        )
        plans = decompose_coverage_families("ForensicCorp", "COMPANY_BRIEF_FORENSIC")
        assert len(plans) == len(_COVERAGE_FAMILY_CATALOG)
        assert {p.family for p in plans} == set(_COVERAGE_FAMILY_CATALOG.keys())

    def test_forensic_deeper_than_dossier(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        dossier = _DEPTH_PROFILES["COMPANY_BRIEF_DOSSIER"]
        forensic = _DEPTH_PROFILES["COMPANY_BRIEF_FORENSIC"]
        assert forensic["min_sources"] > dossier["min_sources"]
        assert forensic["min_citation_anchors"] > dossier["min_citation_anchors"]
        assert forensic["max_queries"] > dossier["max_queries"]


# ---------------------------------------------------------------------------
# 5.4 DOSSIER backward-compat (still 8 families post-DS-5)
# ---------------------------------------------------------------------------

class TestDossierBackwardCompat:
    def test_dossier_thresholds_unchanged(self):
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES
        d = _DEPTH_PROFILES["COMPANY_BRIEF_DOSSIER"]
        assert d["min_sources"] == 25
        assert d["min_citation_anchors"] == 45
        assert d["max_queries"] == 15

    def test_dossier_still_has_eight_families(self):
        from apps_research.engines.query_decomposer import _PROFILE_REQUIRED_FAMILIES
        assert len(_PROFILE_REQUIRED_FAMILIES["COMPANY_BRIEF_DOSSIER"]) == 8


# ---------------------------------------------------------------------------
# 5.5 SLO.md updated
# ---------------------------------------------------------------------------

class TestSLOMdUpdated:
    def _read_slo(self) -> str:
        return (REPO_ROOT / "apps_research" / "SLO.md").read_text(encoding="utf-8")

    def test_slo_contains_competitive_scan_row(self):
        assert "COMPANY_BRIEF_COMPETITIVE_SCAN" in self._read_slo()

    def test_slo_contains_forensic_row(self):
        assert "COMPANY_BRIEF_FORENSIC" in self._read_slo()

    def test_slo_competitive_scan_min_sources(self):
        assert "20" in self._read_slo()

    def test_slo_forensic_min_sources(self):
        assert "35" in self._read_slo()


# ---------------------------------------------------------------------------
# 5.6 Mocked engine integration
# ---------------------------------------------------------------------------

class TestForensicEngineIntegration:
    def test_forensic_35_sources_gate_not_fail(self):
        """With 35 stub sources, FORENSIC gate must not be FAIL."""
        brief = _run_profile_engine("COMPANY_BRIEF_FORENSIC", n_sources=35)
        verdict = brief.get("_gate_verdict")
        assert verdict in ("PASS", "WEAK_WITH_CAVEATS", None), (
            f"Unexpected gate verdict: {verdict}"
        )

    def test_forensic_depth_profile_attached(self):
        """Brief must carry _depth_profile == 'COMPANY_BRIEF_FORENSIC'."""
        brief = _run_profile_engine("COMPANY_BRIEF_FORENSIC", n_sources=35)
        assert brief.get("_depth_profile") == "COMPANY_BRIEF_FORENSIC"

    def test_competitive_scan_20_sources_gate_not_fail(self):
        """With 20 stub sources, COMPETITIVE_SCAN gate must not be FAIL."""
        brief = _run_profile_engine("COMPANY_BRIEF_COMPETITIVE_SCAN", n_sources=20)
        verdict = brief.get("_gate_verdict")
        assert verdict in ("PASS", "WEAK_WITH_CAVEATS", None), (
            f"Unexpected gate verdict: {verdict}"
        )

    def test_competitive_scan_depth_profile_attached(self):
        """Brief must carry _depth_profile == 'COMPANY_BRIEF_COMPETITIVE_SCAN'."""
        brief = _run_profile_engine("COMPANY_BRIEF_COMPETITIVE_SCAN", n_sources=20)
        assert brief.get("_depth_profile") == "COMPANY_BRIEF_COMPETITIVE_SCAN"
