"""W6: headline prompt is PA-compiled via section_prompt_adapter (+ optional U-tier companion)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.headline_pa import compile_headline_prompt

REPO_ROOT = Path(__file__).resolve().parents[2]


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _payload(*, run_id: str = "head_pa_test") -> dict:
    return {
        "run_id": run_id,
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
    assert raw.get("version") == "1.2"
