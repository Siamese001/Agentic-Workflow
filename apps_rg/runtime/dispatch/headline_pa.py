"""Headline: PromptAssemblyInput from headline_tailor_v1.yaml + section_prompt_adapter (W6).

C0 carries canonical employment bullets, forbidden employer names, and selected_fact_plan stub.
JD/title/company/briefing are non-proof in ``c0_jd_requirements``. Companion lanes are U-tier only.
Compile failures propagate (no silent inline fallback).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (
            parent
            / "apps_rg"
            / "prompt_assembly"
            / "templates"
            / "headline_tailor_v1.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError("Cannot resolve repo root from headline_pa.py")


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "headline_tailor_v1.yaml"
)

_HEADLINE_OUTPUT_SCHEMA_JSON = json.dumps(
    {
        "type": "object",
        "required": [
            "headline_line",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "headline_line": {
                "type": "string",
                "description": "Single line X | Y | Z, 8-11 words, no metrics, no employer names",
            },
            "selected_fact_plan": {"type": "object"},
            "claim_ledger": {"type": "array"},
            "jd_alignment": {"type": "object"},
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
    },
    sort_keys=True,
)


def load_headline_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def build_headline_assembly_input(
    runtime_payload: dict[str, Any],
    fact_lines: str,
    forbidden_employer_lines: str,
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
) -> PromptAssemblyInput:
    slots = load_headline_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    stub = json.dumps(
        {
            "section_id": "headline",
            "selection_method": plan.get("selection_method") or "canonical_base_resume_employment_bullets",
            "required_fact_ids": plan.get("required_fact_ids") or [],
        },
        separators=(",", ":"),
        ensure_ascii=False,
    )

    t_title = str(runtime_payload.get("target_title") or "")
    t_company = str(runtime_payload.get("target_company") or "")
    jd = str(runtime_payload.get("jd_text") or "")
    briefing = str(runtime_payload.get("briefing") or "")

    c0_block = (
        "CANONICAL_EMPLOYMENT_BULLETS (proof only; do not paste verbatim into headline_line):\n"
        + fact_lines.strip()
        + "\n\nFORBIDDEN_EMPLOYER_NAMES (must not appear in headline_line):\n"
        + forbidden_employer_lines.strip()
        + "\n\nSELECTED_FACT_PLAN_STUB (output this shape only; do not paste facts[]):\n"
        + stub
    )

    jd_block = (
        f"TARGET_TITLE (NOT PROOF — framing only): {t_title}\n"
        f"TARGET_COMPANY (NOT PROOF): {t_company}\n"
        f"JD_TEXT (ranking/targeting only — NOT PROOF): {jd}\n"
        f"BRIEFING (NOT PROOF): {briefing}\n"
        "These lines may shape wording but cannot prove claims."
    )

    u0 = (
        "Produce exactly ONE resume headline per R0 schema.\n"
        "Return RAW JSON only: first character {, last character }. No markdown fences.\n"
        "headline_line MUST be exactly: SegmentOne | SegmentTwo | SegmentThree "
        "(single spaces around pipes), 8-11 words total, no metrics, no employer names, "
        "no inline source tags, no first person, no em dash.\n"
        "claim_ledger: bul_* source_fact_ids only from C0.\n"
        "jd_alignment must include jd_used_as_proof: false.\n"
    )

    return PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        s0_system_preamble=slots.get("S0", ""),
        d0_fences=slots.get("D0"),
        i0_instructions=slots.get("I0", ""),
        e0_examples=slots.get("E0"),
        y0_style_preferences=slots.get("Y0"),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content=c0_block,
            confidence=1.0,
            source_tag="candidate_facts",
        ),
        c0_jd_requirements=EvidenceSource(
            source_type="jd_requirements",
            content=jd_block,
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=u0,
        r0_response_schema=_HEADLINE_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "headline",
        },
    )


def compile_headline_prompt(
    runtime_payload: dict[str, Any],
    *,
    companion_context: str,
    fact_lines: str,
    forbidden_employer_lines: str,
    run_id: str,
) -> SectionCompiledPrompt:
    assembly = build_headline_assembly_input(
        runtime_payload,
        fact_lines,
        forbidden_employer_lines,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"headline:{run_id}",
    )
    tier = companion_context.strip() or None
    return compile_section_prompt(
        assembly,
        section_id="headline",
        companion_u_tier=tier,
    )


__all__ = [
    "build_headline_assembly_input",
    "compile_headline_prompt",
    "load_headline_template_slots",
]
