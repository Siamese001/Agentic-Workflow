"""Live CLI runs: verify section_input_usage_ledger dual-source receipts for all sections."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT,
    artifact_dir_from_stdout,
    contract_artifact_dir,
    qwen_live_available,
    run_lane_cli,
)

pytestmark = pytest.mark.skipif(
    not qwen_live_available(),
    reason="section CLI receipt tests require live qwen_vllm",
)

SECTION_IDS = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)


def _section_kwargs(section_id: str) -> dict[str, str]:
    if section_id != "executive_summary":
        return {}
    return {
        "target_company": "CI-Probe-Co",
        "target_role": "Software Engineer",
        "jd": str(REPO_ROOT / "tests" / "_fixtures" / "ci-probe-jd.txt"),
        "manual_brief": str(REPO_ROOT / "apps_rg" / "config" / "default_targeting_briefing.txt"),
    }


def _assert_usage_ledger_dual_source(doc: dict) -> None:
    assert doc.get("skills_authority_source_type") == "augmented_skills_graph"
    assert doc.get("skills_authority_status") == "PASS"
    claim_type = doc.get("claim_evidence_source_type")
    assert claim_type in ("candidate_fact_ledger", "selected_role_fact_set", "base_resume_fallback")
    ia = doc.get("input_authority") or {}
    assert ia.get("augmented_skills_graph") == "SKILLS_COMPETENCY_AUTHORITY"
    assert doc.get("legacy_broad_skills_ledger_skills_authority") is not True
    riu = doc.get("required_input_usage") or {}
    assert "augmented_skills_graph" in riu
    assert riu["augmented_skills_graph"]["authority"] == "SKILLS_COMPETENCY_AUTHORITY"
    if claim_type == "candidate_fact_ledger":
        assert ia.get("broad_skills_ledger") == "CLAIM_EVIDENCE_ONLY_DEPRECATED_SKILLS_LABEL"


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_live_cli_refreshes_dual_source_usage_ledger(section_id: str) -> None:
    art = contract_artifact_dir(section_id)
    rel = art.relative_to(REPO_ROOT).as_posix()
    r = run_lane_cli(section_id, artifact_dir=rel, timeout_s=600, **_section_kwargs(section_id))
    assert r.returncode == 0, f"{section_id} stderr={r.stderr!r} stdout={r.stdout!r}"
    rd = artifact_dir_from_stdout(r)
    led_path = rd / "section_input_usage_ledger.json"
    assert led_path.is_file(), led_path
    doc = json.loads(led_path.read_text(encoding="utf-8"))
    _assert_usage_ledger_dual_source(doc)
    x2_path = rd / "x2_source_fact_pool_receipt.json"
    if x2_path.is_file():
        x2 = json.loads(x2_path.read_text(encoding="utf-8"))
        assert x2.get("skills_authority_source_type") in (None, "augmented_skills_graph")
        if x2.get("skills_authority_status"):
            assert x2.get("skills_authority_status") == "PASS"
            assert x2.get("skills_authority_x2_boundary") == "PASS"
