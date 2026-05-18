"""Contract tests: shared proof-pool resolver across all seven canonical section lanes."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_BASE_RESUME_FALLBACK,
    PROOF_SOURCE_BROAD_SKILLS_LEDGER,
    PROOF_SOURCE_SRFS,
    resolve_section_proof_pool,
)

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = default_ledger_path(REPO)
SECTION_IDS = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)


def _high_row(candidate_fact_id: str, *, claim_text: str = "Fixture claim.") -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": claim_text,
        "metric_values": [],
        "capability_tags": ["leadership", "platform"],
    }


def _srfs_doc(sections: dict[str, list[dict]]) -> dict:
    from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS

    out = {
        "selection_id": "proof_pool_contract",
        "selected_facts_by_section": {k: [] for k in SECTION_KEYS},
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
    }
    for k, rows in sections.items():
        out["selected_facts_by_section"][k] = rows
    return out


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_default_resolves_broad_skills_ledger_when_srfs_absent(section_id: str) -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(
        section=section_id,
        selected_role_fact_set_path=None,
        repo_root=REPO,
        target_company="Acme",
        target_title="VP Engineering",
        jd_text="Lead platform engineering.",
        briefing_text="Emphasize scale and delivery.",
    )
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    assert pool.broad_skills_ledger_present is True
    assert pool.srfs_present is False
    assert pool.base_resume_fallback_used is False
    assert pool.proof_pool_digest
    assert pool.targeting_inputs_used.get("jd_title_company") is True
    assert pool.targeting_inputs_used.get("briefing") is True


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_srfs_wins_over_broad_skills_ledger(section_id: str, tmp_path: Path) -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    srfs_path = tmp_path / "srfs.json"
    srfs_path.write_text(
        json.dumps(
            _srfs_doc({section_id: [_high_row(f"bul_{section_id}_srfs_001")]}),
            indent=2,
        ),
        encoding="utf-8",
    )
    pool = resolve_section_proof_pool(
        section=section_id,
        selected_role_fact_set_path=str(srfs_path),
        repo_root=REPO,
        target_company="Acme",
        target_title="VP Engineering",
        jd_text="JD targeting only.",
        briefing_text="Briefing context only.",
    )
    assert pool.proof_source == PROOF_SOURCE_SRFS
    assert pool.srfs_present is True
    assert pool.base_resume_fallback_used is False


def test_base_resume_fallback_explicit_when_ledger_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_BROAD_SKILLS_LEDGER_PATH", str(tmp_path / "missing_ledger.json"))
    pool = resolve_section_proof_pool(
        section="headline",
        selected_role_fact_set_path=None,
        repo_root=REPO,
    )
    assert pool.proof_source == PROOF_SOURCE_BASE_RESUME_FALLBACK
    assert pool.base_resume_fallback_used is True
    assert pool.fallback_used is True
    assert pool.proof_pool_metadata.get("proof_pool_type") == "base_resume_fallback"


def test_non_proof_inputs_recorded_in_usage_extension() -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    from apps_rg.runtime.proof_pool_resolver import proof_pool_usage_ledger_extension

    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO,
        jd_text="Role needs cloud leadership.",
        briefing_text="Position for enterprise SaaS.",
        target_company="TargetCo",
        target_title="CTO",
    )
    ext = proof_pool_usage_ledger_extension(pool)
    assert ext["non_proof_inputs"] == ["jd_title_company", "briefing"]
    assert "jd_title_company" not in ext["claim_support_inputs"]
    assert "briefing" not in ext["claim_support_inputs"]
    assert ext["claim_support_inputs"] == ["broad_skills_ledger"]


def test_competencies_ledger_slice_not_employment_bullets_only() -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(section="competencies", repo_root=REPO)
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    assert pool.selected_fact_plan.get("selection_method", "").startswith("broad_skills")
    assert pool.selected_fact_plan.get("facts")


def test_resume_override_recorded(tmp_path: Path) -> None:
    base = {
        "facts": {
            "employment": [
                {
                    "employer": "Fixture Co",
                    "bullets": [
                        {
                            "bullet_id": "bul_fixture_001",
                            "claim_text": "Led delivery.",
                        }
                    ],
                }
            ]
        }
    }
    resume_path = tmp_path / "override_resume.json"
    resume_path.write_text(json.dumps(base), encoding="utf-8")
    pool = resolve_section_proof_pool(
        section="headline",
        base_resume_ref=str(resume_path),
        repo_root=REPO,
        broad_skills_ledger_path=str(tmp_path / "no_ledger.json"),
    )
    assert pool.base_resume_override_used is True
    assert "override_resume.json" in pool.base_resume_json_ref or pool.base_resume_json_ref.endswith("override_resume.json")


def test_load_section_proof_for_lane_forwards_args_base_resume_ref(tmp_path: Path) -> None:
    from apps_rg.runtime.proof_pool_lane_integration import load_section_proof_for_lane

    base = {
        "facts": {
            "employment": [
                {
                    "employer": "Fixture Co",
                    "bullets": [{"bullet_id": "bul_fixture_002", "claim_text": "Shipped platform."}],
                }
            ]
        }
    }
    resume_path = tmp_path / "lane_resume.json"
    resume_path.write_text(json.dumps(base), encoding="utf-8")
    args = SimpleNamespace(
        selected_role_fact_set="",
        base_resume_ref=str(resume_path),
        broad_skills_ledger_path=str(tmp_path / "missing.json"),
        target_company="",
        target_title="",
        target_role=None,
        jd_text="",
        briefing="",
    )
    pool, _base, _path, _hash = load_section_proof_for_lane(
        section_id="headline",
        args=args,
        repo_root=REPO,
    )
    assert pool.base_resume_override_used is True
