"""W9 — apps_rg whole-run R1B preflight contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w9_fixtures"
CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"


@pytest.fixture(scope="module", autouse=True)
def _ensure_w9_fixtures() -> None:
    if not (FIXTURES / "accepted_r1b_hit.json").is_file():
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "apps_rg" / "emit_r1b_w9_fixtures.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


def test_cache_profile_whole_run_preflight() -> None:
    data = yaml.safe_load(CACHE_PROFILE.read_text(encoding="utf-8"))
    wr = data.get("whole_run_cache_preflight") or {}
    assert wr.get("enabled") is True
    assert wr.get("r1b_lookup_grain") == "ROLE_TARGET_RUN"
    assert wr.get("section_level_loose_reuse") is False
    assert wr.get("c0_collection_excluded") == "fact_vectors"
    order = wr.get("route_order") or []
    assert order[0] == "R1A_EXACT_CACHE"
    assert order[1] == "R1B_SEMANTIC_ROLE_TARGET_RUN"


def test_w9_fixtures_present() -> None:
    for name in (
        "accepted_r1b_hit",
        "semantic_miss_fallthrough",
        "inadmissible_profile_mismatch",
        "fallthrough_to_generation",
        "child_chunks_inspected_not_independently_retrieved",
        "r1b_vs_c0_separation",
    ):
        assert (FIXTURES / f"{name}.json").is_file(), name


def test_accepted_hit_fixture() -> None:
    payload = json.loads((FIXTURES / "accepted_r1b_hit.json").read_text(encoding="utf-8"))
    assert payload["r1b_hit"] is True
    assert payload["lookup_anchor"] == "HistoricalIntentRecord.request_intent_vector"
    assert payload["terminal_packet"]["no_l2_execution_assertion"] is True
    assert payload["c0_fact_vectors_consulted"] is False


def test_miss_and_inadmissible_no_hit() -> None:
    miss = json.loads((FIXTURES / "semantic_miss_fallthrough.json").read_text(encoding="utf-8"))
    assert miss["r1b_hit"] is False
    assert miss["generation_required"] is True
    bad = json.loads((FIXTURES / "inadmissible_profile_mismatch.json").read_text(encoding="utf-8"))
    assert bad["r1b_hit"] is False


def test_child_chunk_inspection_fixture() -> None:
    payload = json.loads(
        (FIXTURES / "child_chunks_inspected_not_independently_retrieved.json").read_text(encoding="utf-8")
    )
    assert payload["independent_chunk_lookup_performed"] is False
    assert all(not c["used_as_lookup_key"] for c in payload["chunks_inspected"])


def test_c0_separation_fixture() -> None:
    payload = json.loads((FIXTURES / "r1b_vs_c0_separation.json").read_text(encoding="utf-8"))
    assert payload["c0_fact_vectors_consulted"] is False
    assert payload["not_c0_fact_vectors"] is True
