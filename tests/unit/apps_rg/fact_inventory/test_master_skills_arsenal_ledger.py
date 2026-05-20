"""Arsenal ledger load, validation, and executive_summary projection (no live generation)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.executive_summary_arsenal_projection import (
    project_executive_summary_arsenal,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    REQUIRED_SKILL_ROW_FIELDS,
    REQUIRED_TOP_LEVEL,
    arsenal_skill_ids,
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
    validate_skill_row_for_external_output,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"


@pytest.fixture
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=LEDGER_PATH)


def test_arsenal_ledger_loads_and_top_level_keys(ledger: dict) -> None:
    validate_arsenal_ledger_shape(ledger)
    for key in REQUIRED_TOP_LEVEL:
        assert key in ledger
    assert ledger["metadata"]["schema_version"] == "master_skills_arsenal_graph_v1"
    assert ledger["metadata"].get("w4a_hardened") is True
    assert len(ledger["pillars"]) == 29
    assert len(ledger["skill_rows"]) >= 162
    assert len(ledger["actuarial_career_matrix"]) == 22
    assert len(ledger["partner_gtm_matrix"]) == 16
    assert len(ledger["role_family_projection_profiles"]) == 9
    assert len(ledger["agentic_runtime_matrix"]) >= 65
    assert len(arsenal_skill_ids(ledger)) == len(ledger["skill_rows"])


def test_skill_row_required_fields_present(ledger: dict) -> None:
    for row in ledger["skill_rows"]:
        for field in REQUIRED_SKILL_ROW_FIELDS:
            assert field in row, f"{row.get('skill_id')} missing {field}"


def test_pending_source_blocked_from_external_claim(ledger: dict) -> None:
    pending = [
        r
        for r in ledger["skill_rows"]
        if r["support_level"] == "USER_CONFIRMED_PENDING_SOURCE"
    ]
    assert pending, "fixture must include pending-source rows"
    for row in pending:
        assert not skill_row_eligible_for_external_claim(row)
        violations = validate_skill_row_for_external_output(row)
        assert violations


def test_direct_archive_skill_can_be_external_eligible(ledger: dict) -> None:
    direct = [
        r
        for r in ledger["skill_rows"]
        if r["support_level"] == "DIRECT_FROM_RESUME_ARCHIVE" and r.get("source_snippets")
    ]
    assert direct
    eligible = [r for r in direct if skill_row_eligible_for_external_claim(r)]
    assert eligible, "at least one archive-supported row should be externally eligible"


def test_targeting_only_and_style_only_not_proof() -> None:
    targeting = {
        "skill_id": "skill_test_targeting",
        "fact_id_links": [],
        "pillar": "pillar_agentic_ai_platforms",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["jd emphasis only"],
        "user_confirmed": False,
        "support_level": "TARGETING_ONLY",
        "role_family_weights": {},
        "allowed_phrases": ["emphasis"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "never_external",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(targeting)
    style = {**targeting, "skill_id": "skill_test_style", "support_level": "STYLE_ONLY"}
    assert not skill_row_eligible_for_external_claim(style)


def test_blocked_not_selectable() -> None:
    blocked = {
        "skill_id": "skill_test_blocked",
        "fact_id_links": ["fact_engineering_platform_001"],
        "pillar": "pillar_agentic_ai_platforms",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["x"],
        "user_confirmed": False,
        "support_level": "BLOCKED",
        "role_family_weights": {},
        "allowed_phrases": [],
        "forbidden_phrases": [],
        "allowed_sections": [],
        "visibility_rule": "never_external",
        "evidence_risk": "high",
        "activation_status": "RETIRED",
        "human_confirmation_required": True,
    }
    assert not skill_row_eligible_for_external_claim(blocked)


def test_no_fact_links_internal_only_for_external_claim() -> None:
    row = {
        "skill_id": "skill_test_no_facts",
        "fact_id_links": [],
        "pillar": "pillar_actuarial_foundation",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": [],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {"ENGINEERING_PLATFORM": 1.0},
        "allowed_phrases": ["x"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(row)


def test_derived_requires_fact_links() -> None:
    row = {
        "skill_id": "skill_test_derived",
        "fact_id_links": [],
        "pillar": "pillar_actuarial_foundation",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["Derived phrase supported by quant_hpc fact anchor in ledger."],
        "user_confirmed": False,
        "support_level": "DERIVED_SUPPORTED",
        "role_family_weights": {},
        "allowed_phrases": ["derived"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(row)
    row["fact_id_links"] = ["fact_quant_hpc_003"]
    assert skill_row_eligible_for_external_claim(row)


def test_jd_briefing_not_in_fact_id_links() -> None:
    row = {
        "skill_id": "skill_test_jd",
        "fact_id_links": ["jd_targeting_snippet"],
        "pillar": "pillar_agentic_ai_platforms",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["ok"],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {},
        "allowed_phrases": ["ok"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(row)


def test_svp_projection_actuarial_differentiator(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("SVP_ENGINEERING_AI_PLATFORM", ledger=ledger)
    assert "pillar_actuarial_foundation" in proj.selected_pillar_ids
    assert "pillar_agentic_ai_platforms" in proj.selected_pillar_ids
    assert proj.actuarial_differentiator_included
    assert proj.internal_ranked_skill_ids


def test_anthropic_partnerships_projection_partner_gtm(ledger: dict) -> None:
    proj = project_executive_summary_arsenal(
        "ANTHROPIC_PARTNERSHIPS_APPLIED_AI", ledger=ledger
    )
    assert "pillar_partner_gtm_alliances" in proj.selected_pillar_ids
    assert "pillar_cosell_partner_engineering" in proj.selected_pillar_ids
    assert "pillar_presales_solutioning" in proj.selected_pillar_ids
    assert "pillar_cloud_data_aws" in proj.selected_pillar_ids
    assert proj.partner_gtm_included


def test_ai_financial_services_governance_actuarial_derivatives(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("AI_FINANCIAL_SERVICES", ledger=ledger)
    assert proj.governance_risk_included
    pillars = set(proj.selected_pillar_ids)
    assert "pillar_regulatory_governance" in pillars
    assert "pillar_actuarial_foundation" in pillars
    greek_or_deriv = pillars & {
        "pillar_greeks_hedging",
        "pillar_derivatives_structured",
    }
    assert greek_or_deriv or any(
        sid.startswith("skill_greeks_") or sid.startswith("skill_derivatives_")
        for sid in proj.internal_ranked_skill_ids
    )


def test_pending_source_not_in_svp_external_eligible(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("SVP_ENGINEERING_AI_PLATFORM", ledger=ledger)
    pending_ids = {
        r["skill_id"]
        for r in ledger["skill_rows"]
        if r["support_level"] == "USER_CONFIRMED_PENDING_SOURCE"
    }
    assert not pending_ids & set(proj.external_eligible_skill_ids)


def test_agentic_core_diff_empty() -> None:
    import subprocess

    result = subprocess.run(
        ["git", "diff", "HEAD", "--", "agentic_core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
