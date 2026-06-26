"""apps-test-model: APP CONTRACT.

W6: headline prompt is PA-compiled via section_prompt_adapter (+ optional U-tier companion).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.headline_pa import compile_headline_prompt

REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _minimal_proof_metadata() -> dict:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority
    from apps_rg.runtime.sections.headline_positioning_evidence import (
        attach_headline_positioning_bundles_to_proof_pool_metadata,
    )

    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
        "selected_graph_evidence_plan": {
            "section_id": "headline",
            "selected_headline_positioning_families": [
                "agentic_ai_platforms",
                "runtime_governance",
                "enterprise_ai_architecture",
            ],
            "selected_skill_ids": [],
        },
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    return attach_headline_positioning_bundles_to_proof_pool_metadata(meta, section_id="headline")


def _payload(*, run_id: str = "head_pa_test") -> dict:
    return {
        "run_id": run_id,
        "product_visible": False,
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI platform",
        "briefing": "regulated enterprise",
        "selected_fact_plan": {
            "section_id": "headline",
            "selection_method": "canonical_base_resume_employment_bullets",
            "required_fact_ids": ["bul_unify_001"],
            "facts": [],
        },
        "proof_pool_metadata": _minimal_proof_metadata(),
        "allowed_fact_ids": ["bul_unify_001"],
    }


def test_compile_headline_returns_adapter_shape():
    fact_lines = "- bul_unify_001: Example bullet with agentic platform delivery"
    out = compile_headline_prompt(
        _payload(),
        companion_context="",
        fact_lines=fact_lines,
        forbidden_employer_lines="- unify\n- ibm",
        run_id="t1",
    )
    assert isinstance(out, SectionCompiledPrompt)
    assert out.section_id == "headline"
    assert "headline_tailor_v1" in out.apps_rg_prompt_template_ref
    assert out.artifact.template_id == "strategic_tailor_v1"
    assert len(out.artifact.messages) == 1
    assert out.artifact.messages[0]["role"] == "system"


def test_companion_context_is_u_tier_not_in_candidate_facts_block():
    fact_lines = "- bul_x: claim"
    out = compile_headline_prompt(
        _payload(run_id="t2"),
        companion_context="### executive_summary\nSome exec text for tone only.",
        fact_lines=fact_lines,
        forbidden_employer_lines="- acme",
        run_id="t2",
    )
    content = out.artifact.messages[0]["content"]
    assert "U_TIER_COMPANION_CONTEXT" in content
    assert "Some exec text" in content
    assert "CANONICAL_EMPLOYMENT_BULLETS" in content or "bul_x" in content
    assert "companion_used_as_proof" in content


def test_dispatch_style_hash_stable():
    fact_lines = "- bul_1: a"
    out = compile_headline_prompt(
        _payload(run_id="t3"),
        companion_context="",
        fact_lines=fact_lines,
        forbidden_employer_lines="- x",
        run_id="t3",
    )
    msgs = out.artifact.messages
    compiled = json.dumps(msgs, ensure_ascii=False, separators=(",", ":"))
    assert len(_sha16(compiled)) == 16


def test_headline_template_yaml_has_slot_bodies():
    path = REPO_ROOT / "apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml"
    assert path.is_file()
    import yaml

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert raw.get("slot_bodies", {}).get("S0")
    txt = path.read_text(encoding="utf-8")
    assert "SVP Engineering | X | Y | Z" in txt or "SVP Engineering |" in txt
    assert raw.get("version") == "1.5"


def test_headline_prompt_registry_template_contract_versions_aligned():
    import yaml

    reg_path = REPO_ROOT / "apps_rg/prompt_assembly/prompt_registry.yaml"
    tpl_path = REPO_ROOT / "apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml"
    contract_path = REPO_ROOT / "apps_rg/prompt_assembly/section_prompt_contracts/headline.contract.yaml"
    reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    tpl = yaml.safe_load(tpl_path.read_text(encoding="utf-8"))
    contract_txt = contract_path.read_text(encoding="utf-8")
    v_reg = reg["templates"]["headline_tailor_v1"]["version"]
    v_tpl = tpl["version"]
    assert v_reg == v_tpl == "1.5"
    assert "v1.5" in contract_txt


def test_compiled_headline_production_prompt_markers():
    fact_lines = "- bul_unify_001: Example bullet with agentic platform delivery"
    out = compile_headline_prompt(
        _payload(),
        companion_context="",
        fact_lines=fact_lines,
        forbidden_employer_lines="- unify\n- ibm",
        run_id="t_prodshape",
    )
    content = out.artifact.messages[0]["content"]
    assert "SVP Engineering | X | Y | Z" in content
    low = content.lower()
    assert "north star" in low or "svp engineering | x | y | z" in low
    assert "jd_text" in low or "jd" in low
    assert "briefing" in low
    assert "fact ledger" in low or "canonical_employment_bullets" in low or "c0" in low
    assert "targeting" in low
    assert "fresh" in low or "newly composed" in low
    assert "not the default answer" in low or "identity reference" in low or "identity-reference" in low
    assert "headline display policy" in low
    assert "not raw vendor/tool architecture" in low
    assert "internal headline candidates" in low or "internal candidates" in low
    assert "pa_truth_oath_v1" in content or "pa_core_law" in content
    assert "PRODUCT_SHAPE" in content
    assert "forbidden: flat arrays of strings" in low or "flat arrays of strings" in low
    assert "claim_text" in content and "source_fact_ids" in content
    assert "pipe" in low and "word_count" in low
def test_headline_r0_embedded_schema_claim_ledger_requires_object_rows():
    import json as _json

    from apps_rg.runtime.sections.headline_pa import _HEADLINE_OUTPUT_SCHEMA_JSON

    schema = _json.loads(_HEADLINE_OUTPUT_SCHEMA_JSON)
    cl = schema["properties"]["claim_ledger"]
    assert cl["type"] == "array"
    assert cl["items"]["type"] == "object"
    assert set(cl["items"]["required"]) >= {"claim_text", "source_fact_ids"}


def test_compiled_headline_u0_forbids_flat_claim_ledger_and_shows_good_shape():
    fact_lines = "- bul_unify_001: Example bullet with agentic platform delivery"
    out = compile_headline_prompt(
        _payload(),
        companion_context="",
        fact_lines=fact_lines,
        forbidden_employer_lines="- unify\n- ibm",
        run_id="t_flatledger",
    )
    content = out.artifact.messages[0]["content"]
    assert "FORBIDDEN: flat arrays of strings" in content
    assert "claim_text" in content and "source_fact_ids" in content
    assert "bul_unify_001" in content and "bul_unify_005" in content
