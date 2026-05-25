"""W2: SKILL_PHRASE_CAPSULE_NOT_EVIDENCE in all seven lane compiles."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.dispatch.headline_pa import compile_headline_prompt
from apps_rg.runtime.dispatch.ibm_bullets_pa import compile_ibm_bullets_prompt
from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt
from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.dispatch.unify_narrative_pa import compile_unify_narrative_prompt
from apps_rg.runtime.graph_skill_phrase_capsule import SKILL_PHRASE_CAPSULE_MARKER
from apps_rg.runtime.sections.competencies_pa import compile_competencies_prompt
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.validators.graph_skills_proof_common import (
    assert_capsule_phrases_not_proof_authority,
)

REPO = Path(__file__).resolve().parents[3]
CAPSULE_RE = re.compile(re.escape(SKILL_PHRASE_CAPSULE_MARKER))


@pytest.fixture(autouse=True)
def _fixture_bypass():
    os.environ.setdefault("PYTEST_CURRENT_TEST", "test_graph_skills_skill_capsule_w2")
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _minimal_proof_metadata(*, skill_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    meta: dict[str, Any] = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
        "augmented_skills_graph_present": True,
        "graph_version": "test",
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    if skill_rows is not None:
        meta["selected_skill_rows"] = skill_rows
    return meta


def _skill_row(skill_id: str, phrase: str) -> dict[str, Any]:
    return {
        "skill_id": skill_id,
        "allowed_phrases": [phrase],
        "fact_id_links": ["fact_engineering_platform_001"],
        "graph_hop_path": ["TRACK_GENAI_AGENTIC", "skill", skill_id, "fact_engineering_platform_001"],
    }


def _prompt_text(compiled: Any) -> str:
    return str(compiled.artifact.messages[-1]["content"])


@pytest.mark.parametrize("section_id", [
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
])
def test_compiled_prompt_contains_skill_phrase_capsule_marker(section_id: str) -> None:
    meta = _minimal_proof_metadata(skill_rows=[_skill_row("skill_agentic_platform_productization", "agentic platform orchestration")])
    base: dict[str, Any] = {
        "product_visible": True,
        "run_id": f"w2_{section_id}",
        "target_title": "SVP IT Strategy & Innovation",
        "target_company": "Brown & Brown",
        "jd_text": (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(encoding="utf-8"),
        "briefing": "Enterprise IT strategy targeting.",
        "proof_pool_metadata": meta,
        "allowed_fact_ids": ["bul_unify_001"],
    }
    if section_id == "headline":
        base["selected_fact_plan"] = {"section_id": "headline", "facts": [], "required_fact_ids": ["bul_unify_001"]}
        out = compile_headline_prompt(
            base,
            companion_context="",
            fact_lines="- bul_unify_001: Platform delivery for regulated enterprise.",
            forbidden_employer_lines="- ibm",
            run_id=base["run_id"],
        )
    elif section_id == "executive_summary":
        base["selected_fact_plan"] = {
            "facts": [{"fact_id": "bul_unify_001", "claim_text": "Platform.", "metric_raw": ""}],
        }
        out = compile_executive_summary_prompt(base, run_id=base["run_id"])
    elif section_id == "competencies":
        base["selected_fact_plan"] = {
            "section_id": "competencies",
            "facts": [{"fact_id": "bul_unify_001", "claim_text": "Platform.", "metric_raw": ""}],
        }
        out = compile_competencies_prompt(
            base,
            companion_context="",
            fact_lines="- bul_unify_001: Platform.",
            run_id=base["run_id"],
        )
    elif section_id == "unify_bullets":
        base["unify_header"] = {"employer": "Unify Consulting", "title": "SVP", "location": "FL", "start_date": "2023", "end_date": "present"}
        base["selected_fact_plan"] = {"facts": [{"fact_id": "bul_unify_001", "claim_text": "Platform.", "metric_raw": ""}]}
        out = compile_unify_bullets_prompt(base, run_id=base["run_id"])
    elif section_id == "unify_narrative":
        base["unify_header"] = base.get("unify_header") or {"employer": "Unify Consulting", "title": "SVP", "location": "FL", "start_date": "2023", "end_date": "present"}
        base["companion_unify_bullets_status"] = "ACCEPTED_FINALIZED"
        base["selected_fact_plan"] = {"facts": [{"fact_id": "bul_unify_001", "claim_text": "Platform.", "metric_raw": ""}]}
        out = compile_unify_narrative_prompt(base, "", run_id=base["run_id"])
    elif section_id == "ibm_bullets":
        base["allowed_fact_ids"] = ["bul_ibm_001"]
        base["ibm_header"] = {"employer": "IBM", "title": "Lead", "location": "NJ", "start_date": "2017", "end_date": "2022"}
        base["selected_fact_plan"] = {"facts": [{"fact_id": "bul_ibm_001", "claim_text": "Cloud.", "metric_raw": ""}]}
        out = compile_ibm_bullets_prompt(base, run_id=base["run_id"])
    else:
        base["ibm_header"] = {"employer": "IBM", "title": "Lead", "location": "NJ", "start_date": "2017", "end_date": "2022"}
        base["companion_ibm_bullets_status"] = "ACCEPTED_FINALIZED"
        base["selected_fact_plan"] = {"facts": [{"fact_id": "bul_ibm_001", "claim_text": "Cloud.", "metric_raw": ""}]}
        out = compile_ibm_narrative_prompt(base, "", run_id=base["run_id"])

    content = _prompt_text(out)
    assert CAPSULE_RE.search(content), f"{section_id}: missing {SKILL_PHRASE_CAPSULE_MARKER}"
    assert "agentic platform orchestration" in content
    assert_capsule_phrases_not_proof_authority(
        section_id=section_id,
        proof_pool_metadata=meta,
        allowed_fact_ids=base["allowed_fact_ids"],
        selected_fact_plan=base.get("selected_fact_plan"),
    )
