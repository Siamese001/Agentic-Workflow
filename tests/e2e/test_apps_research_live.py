"""apps_research DOSSIER-depth live E2E test — P3.2.

Plan: apps-research-spine-deferred-followup-9c3e1a W3.

Requirements
------------
- ``SEARXNG_BASE_URL`` must be set in the environment.
- Test is skipped automatically when the base URL is absent; CI can mark
  this file as ``--ignore`` on offline builds.

SLO baseline targets (per ``apps_research/SLO.md`` DOSSIER extension):

  - ``total_final_sources >= 25``
  - ``total_citation_anchors >= 45``
  - gate verdict in {PASS, WEAK_WITH_CAVEATS}  (not FAIL)
  - full run completes within 300s (p99 ceiling for DOSSIER)

These are TARGETS — the first live run establishes the concrete baseline.
Results are emitted to ``artifacts/slo/apps_research_dossier_<run_id>.json``
for the W4.3 measurement rollup.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path

import pytest

_SEARXNG_BASE_URL = os.environ.get("SEARXNG_BASE_URL", "").strip()

pytestmark = pytest.mark.skipif(
    not _SEARXNG_BASE_URL,
    reason="SEARXNG_BASE_URL not set — live DOSSIER test skipped",
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SLO_TARGET_SOURCES = 25
_SLO_TARGET_ANCHORS = 45
_SLO_TTL_SECONDS = 300


def _emit_slo_artifact(run_id: str, result: dict) -> None:
    """Persist SLO measurement to artifacts/slo/ for W4.3 rollup."""
    slo_dir = _REPO_ROOT / "artifacts" / "slo"
    slo_dir.mkdir(parents=True, exist_ok=True)
    path = slo_dir / f"apps_research_dossier_{run_id}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


class TestAppsResearchDossierLive:
    """Live integration tests for DOSSIER-depth retrieval via real SearXNG.

    All tests in this class are automatically skipped when ``SEARXNG_BASE_URL``
    is not set — this keeps CI green on offline builds.

    The fixture ``dossier_result`` runs the engine once and caches the output
    so all assertions share a single SearXNG-backed run.
    """

    @pytest.fixture(scope="class")
    def dossier_result(self) -> dict:
        """Execute CompanyBriefEngine at DOSSIER depth and return brief + timing."""
        from apps_research.engines.company_brief_engine import CompanyBriefEngine

        engine = CompanyBriefEngine()
        run_id = str(uuid.uuid4())[:8]
        start = time.monotonic()
        brief = engine.execute({
            "topic": "OpenAI",
            "depth": "COMPANY_BRIEF_DOSSIER",
        })
        elapsed = time.monotonic() - start

        result = {
            "run_id": run_id,
            "elapsed_seconds": round(elapsed, 2),
            "depth_profile": brief.get("_depth_profile"),
            "gate_verdict": brief.get("_gate_verdict"),
            "total_final_sources": (
                brief.get("_c0_bundle", {})
                .get("source_portfolio_summary", {})
                .get("total_final_sources", 0)
            ),
            "total_citation_anchors": (
                brief.get("_c0_bundle", {})
                .get("source_portfolio_summary", {})
                .get("total_citation_anchors", 0)
            ),
            "slo_targets": {
                "min_sources": _SLO_TARGET_SOURCES,
                "min_anchors": _SLO_TARGET_ANCHORS,
                "max_seconds": _SLO_TTL_SECONDS,
            },
        }
        _emit_slo_artifact(run_id, result)
        return {"brief": brief, "timing": result}

    def test_dossier_live_completes_within_slo_ttl(self, dossier_result):
        """Full DOSSIER run must complete within 300s (p99 ceiling)."""
        elapsed = dossier_result["timing"]["elapsed_seconds"]
        assert elapsed <= _SLO_TTL_SECONDS, (
            f"DOSSIER run exceeded SLO ceiling: {elapsed:.1f}s > {_SLO_TTL_SECONDS}s"
        )

    def test_dossier_live_depth_profile_set(self, dossier_result):
        """Brief must carry _depth_profile == 'COMPANY_BRIEF_DOSSIER'."""
        assert dossier_result["brief"].get("_depth_profile") == "COMPANY_BRIEF_DOSSIER"

    def test_dossier_live_gate_verdict_not_fail(self, dossier_result):
        """Gate verdict must not be FAIL with real SearXNG sources."""
        verdict = dossier_result["brief"].get("_gate_verdict")
        assert verdict in ("PASS", "WEAK_WITH_CAVEATS"), (
            f"DOSSIER live gate verdict was FAIL — check SearXNG connectivity: {verdict}"
        )

    def test_dossier_live_total_final_sources_meets_slo(self, dossier_result):
        """total_final_sources must be >= 25 (DOSSIER SLO target)."""
        sources = dossier_result["timing"]["total_final_sources"]
        assert sources >= _SLO_TARGET_SOURCES, (
            f"DOSSIER live sources {sources} < SLO target {_SLO_TARGET_SOURCES}"
        )

    def test_dossier_live_citation_anchors_meet_slo(self, dossier_result):
        """total_citation_anchors must be >= 45 (DOSSIER SLO target)."""
        anchors = dossier_result["timing"]["total_citation_anchors"]
        assert anchors >= _SLO_TARGET_ANCHORS, (
            f"DOSSIER live anchors {anchors} < SLO target {_SLO_TARGET_ANCHORS}"
        )

    def test_dossier_live_c0_bundle_present(self, dossier_result):
        """Brief must have a non-empty _c0_bundle."""
        c0 = dossier_result["brief"].get("_c0_bundle")
        assert isinstance(c0, dict) and c0, "_c0_bundle missing or empty in live run"

    def test_dossier_live_slo_artifact_emitted(self, dossier_result):
        """SLO artifact must have been written to artifacts/slo/."""
        run_id = dossier_result["timing"]["run_id"]
        artifact_path = _REPO_ROOT / "artifacts" / "slo" / f"apps_research_dossier_{run_id}.json"
        assert artifact_path.exists(), f"SLO artifact not found: {artifact_path}"
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert data["depth_profile"] == "COMPANY_BRIEF_DOSSIER"
