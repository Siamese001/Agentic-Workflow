"""W7: Unify/IBM lanes compile via section_prompt_adapter (mechanical migration proof)."""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from pathlib import Path

import pytest

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


def _minimal_proof_metadata() -> dict:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    return meta


def _product_lane_base() -> dict:
    return {
        "product_visible": False,
        "proof_pool_metadata": _minimal_proof_metadata(),
    }


def test_unify_narrative_compiled_shape():
    payload = {
        **_product_lane_base(),
        "run_id": "pa_un_narr",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "candidate_name": "",
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": _unify_facts()},
        "allowed_fact_ids": ["bul_unify_001"],
    }
    out = compile_unify_narrative_prompt(payload, "", run_id="pa_un_narr")
    _assert_compiled(out, "unify_narrative", "unify_position_narrative_v1.yaml")
    body = out.artifact.messages[0]["content"]
    assert "ALLOWED_SOURCE_FACT_IDS" in body
    assert "non-empty" in body.lower() and "claim_text" in body.lower()


def test_narrative_r0_claim_ledger_item_requires_claim_text_and_source_fact_ids():
    from apps_rg.runtime.dispatch.unify_ibm_pa_common import NARRATIVE_JD_ALIGNMENT_SCHEMA, NARRATIVE_R0

    schema = json.loads(NARRATIVE_R0)
    items = schema["properties"]["claim_ledger"]["items"]
    assert "claim_text" in items["required"]
    assert "source_fact_ids" in items["required"]
    assert items["properties"]["claim_text"]["minLength"] == 1
    assert items["properties"]["source_fact_ids"]["minItems"] == 1
    ja = schema["properties"]["jd_alignment"]
    assert ja == NARRATIVE_JD_ALIGNMENT_SCHEMA


def test_strategic_tailor_v1_yaml_resolvable():
    p = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "strategic_tailor_v1.yaml"
    assert p.is_file()


def test_unify_narrative_companion_fence_when_present():
    payload = {
        **_product_lane_base(),
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
        **_product_lane_base(),
        "run_id": "pa_ibm_narr",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "candidate_name": "",
        "ibm_header": _ibm_header(),
        "selected_fact_plan": {"facts": _ibm_facts()},
        "allowed_fact_ids": ["bul_ibm_001"],
    }
    out = compile_ibm_narrative_prompt(payload, "", run_id="pa_ibm_narr")
    _assert_compiled(out, "ibm_narrative", "ibm_position_narrative_v1.yaml")
    body = out.artifact.messages[0]["content"]
    assert "ALLOWED_SOURCE_FACT_IDS" in body
    assert "bul_ibm_001" in body
    assert "IBM NARRATIVE NORTH STAR" in body
    assert "JD and briefing are targeting context only" in body.lower() or "targeting context only" in body.lower()

    out_fence = compile_ibm_narrative_prompt(
        payload,
        "- bul_ibm_001: mock companion bullet KPIs live on bullet lines.",
        run_id="pa_ibm_fence",
    )
    body_f = out_fence.artifact.messages[0]["content"]
    assert "U_TIER_COMPANION_CONTEXT" in body_f
    assert "ACCEPTED_IBM_BULLETS" in body_f


@pytest.mark.contract_harness_live
def test_canonical_dispatch_routes_ibm_narrative_lane(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APPS_RG_C0_EVIDENCE_ROOM", "0")
    from apps_rg.runtime.orchestration.canonical_dispatch import run_canonical_apps_rg_from_cli_primitives

    art = REPO_ROOT / "artifacts" / "apps_rg" / "_pytest_ibm_narr_lane" / uuid.uuid4().hex[:12]
    art.mkdir(parents=True, exist_ok=True)
    try:
        result = run_canonical_apps_rg_from_cli_primitives(
            target_company="Synthetic Enterprise Corp.",
            target_role="SVP Engineering, Agentic AI Platforms",
            target_level="",
            jd="",
            job_description_ref="",
            job_description_text="",
            manual_brief="",
            resume_path="",
            source_resume_text="",
            generation_mode="strategic_tailor",
            artifact_dir=str(art),
            section="ibm_narrative",
            lane_provider="mock",
            lane_temperature=0.45,
            lane_x1d_judges="gemini_pro,openai_chatgpt,anthropic_claude",
            lane_mock_judges=False,
        )
        assert result.get("artifact_dir")
        ps = Path(str(result["artifact_dir"])) / "prompt_selection_trace.json"
        assert ps.is_file()
        trace = json.loads(ps.read_text(encoding="utf-8"))
        assert trace.get("runtime_path") == "apps_rg.runtime.sections.ibm_narrative_lane"
        cap = Path(str(result["artifact_dir"])) / "compiled_prompt_artifact.json"
        cap_doc = json.loads(cap.read_text(encoding="utf-8"))
        assert cap_doc.get("allowed_fact_ids")
        assert "ibm_position_narrative_v1.yaml" in cap_doc.get("apps_rg_prompt_template_ref", "")
    finally:
        shutil.rmtree(art, ignore_errors=True)


def test_unify_bullets_compiled_shape():
    payload = {
        **_product_lane_base(),
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
        **_product_lane_base(),
        "run_id": "pa_ibm_bul",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "ibm_header": _ibm_header(),
        "selected_fact_plan": {"facts": _ibm_facts()},
        "allowed_fact_ids": ["bul_ibm_001"],
    }
    out = compile_ibm_bullets_prompt(payload, run_id="pa_ibm_bul")
    _assert_compiled(out, "ibm_bullets", "ibm_bullet_tailor_v1.yaml")
    body = out.artifact.messages[0]["content"]
    assert "ALLOWED_SOURCE_FACT_IDS" in body
    assert "bul_ibm_001" in body
    assert "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1" in body
    assert "REWRITE_FROM_FACT_POOL_CONSTRAINED" in body
    assert "UNIFY_IBM_PROMPT_CORE_LAW_V3" in body
    assert "PRODUCT_SHAPE" in body


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
