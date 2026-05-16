"""W7: Unify/IBM lanes compile via section_prompt_adapter (mechanical migration proof)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.ibm_bullets_pa import compile_ibm_bullets_prompt
from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt
from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.dispatch.unify_narrative_pa import compile_unify_narrative_prompt

REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _unify_header() -> dict:
    return {
        "employer": "Unify Consulting",
        "title": "SVP Engineering, Agentic AI Platforms",
        "location": "Boca Raton, FL",
        "start_date": "2023-02",
        "end_date": "present",
    }


def _ibm_header() -> dict:
    return {
        "employer": "IBM",
        "title": "Lead Client Partner",
        "location": "Edgewater, NJ",
        "start_date": "2017-04",
        "end_date": "2022-10",
    }


def _unify_facts() -> list[dict]:
    return [
        {"fact_id": "bul_unify_001", "claim_text": "Architected governed agentic platform execution.", "metric_raw": ""},
    ]


def _ibm_facts() -> list[dict]:
    return [
        {"fact_id": "bul_ibm_001", "claim_text": "Delivered enterprise cloud programs.", "metric_raw": ""},
    ]


def test_unify_narrative_compiled_shape():
    payload = {
        "run_id": "pa_un_narr",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "candidate_name": "",
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": _unify_facts()},
    }
    out = compile_unify_narrative_prompt(payload, "", run_id="pa_un_narr")
    _assert_compiled(out, "unify_narrative", "unify_position_narrative_v1.yaml")


def test_unify_narrative_companion_fence_when_present():
    payload = {
        "run_id": "pa_un_narr2",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "candidate_name": "",
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": _unify_facts()},
    }
    out = compile_unify_narrative_prompt(
        payload,
        "- bul_unify_001: mock bullet text",
        run_id="pa_un_narr2",
    )
    assert "U_TIER_COMPANION_CONTEXT" in out.artifact.messages[0]["content"]


def test_ibm_narrative_compiled_shape():
    payload = {
        "run_id": "pa_ibm_narr",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "candidate_name": "",
        "ibm_header": _ibm_header(),
        "selected_fact_plan": {"facts": _ibm_facts()},
    }
    out = compile_ibm_narrative_prompt(payload, "", run_id="pa_ibm_narr")
    _assert_compiled(out, "ibm_narrative", "ibm_position_narrative_v1.yaml")


def test_unify_bullets_compiled_shape():
    payload = {
        "run_id": "pa_un_bul",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": _unify_facts()},
    }
    out = compile_unify_bullets_prompt(payload, run_id="pa_un_bul")
    _assert_compiled(out, "unify_bullets", "unify_bullet_tailor_v1.yaml")


def test_ibm_bullets_compiled_shape():
    payload = {
        "run_id": "pa_ibm_bul",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "ibm_header": _ibm_header(),
        "selected_fact_plan": {"facts": _ibm_facts()},
    }
    out = compile_ibm_bullets_prompt(payload, run_id="pa_ibm_bul")
    _assert_compiled(out, "ibm_bullets", "ibm_bullet_tailor_v1.yaml")


def test_w7_shell_slots_file_exists():
    path = REPO_ROOT / "apps_rg/prompt_assembly/templates/w7_strategic_tailor_shell_slots.yaml"
    assert path.is_file()


def _assert_compiled(out: SectionCompiledPrompt, section_id: str, template_substr: str) -> None:
    assert isinstance(out, SectionCompiledPrompt)
    assert out.section_id == section_id
    assert template_substr in out.apps_rg_prompt_template_ref
    assert out.artifact.template_id == "strategic_tailor_v1"
    assert len(out.artifact.messages) == 1
    assert out.artifact.messages[0]["role"] == "system"
    assert out.artifact.prompt_hash
    compact = json.dumps(out.artifact.messages, ensure_ascii=False, separators=(",", ":"))
    assert len(_sha16(compact)) == 16
    body = out.artifact.messages[0]["content"]
    assert "<candidate_facts" in body
    assert "<jd_requirements" in body
