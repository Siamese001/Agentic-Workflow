"""Competencies: build PromptAssemblyInput from runtime payload + competency_selector_v2.pa_slots (W5).

Loads slot bodies from ``competency_selector_v2.pa_slots.yaml`` (PA-only extract) and compiles via
``section_prompt_adapter``. Narrative SSOT remains ``competency_selector_v2.yaml`` on disk for humans/registry;

**Proof facts** live in **C0 only** (single canonical employment block). JD/title/company/briefing are
non-proof in ``c0_jd_requirements``. Companion lanes are **U-tier only** via ``companion_u_tier``.

Runtime compile failures propagate (no silent inline fallback).
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
            / "competency_selector_v2.pa_slots.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError(
        "Cannot resolve repo root from competencies_pa.py (competency_selector_v2.pa_slots.yaml not found)"
    )


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "competency_selector_v2.pa_slots.yaml"
)

_COMPETENCIES_OUTPUT_SCHEMA_JSON = json.dumps(
    {
        "type": "object",
        "required": [
            "competencies",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "excluded_jd_skills",
            "removed_or_rewritten_terms",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "competencies": {
                "type": "array",
                "minItems": 8,
                "maxItems": 8,
                "description": "Each category: category_label, terms (string or object), source_fact_ids",
            },
            "selected_fact_plan": {"type": "object"},
            "claim_ledger": {"type": "array"},
            "jd_alignment": {"type": "object"},
            "excluded_jd_skills": {"type": "array"},
            "removed_or_rewritten_terms": {"type": "array"},
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
        "definitions": {
            "competency_term": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "required": ["text", "source_fact_id"],
                        "properties": {
                            "text": {"type": "string"},
                            "source_fact_id": {"type": "string"},
                            "jd_signal_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional JD phrases used only for ranking; not proof",
                            },
                        },
                    },
                ]
            }
        },
    },
    sort_keys=True,
)


def load_competencies_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def build_competencies_assembly_input(
    runtime_payload: dict[str, Any],
    fact_lines: str,
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
) -> PromptAssemblyInput:
    slots = load_competencies_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    stub = json.dumps(
        {
            "section_id": plan.get("section_id") or "competencies",
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

    c0_facts = (
        "CANONICAL_EMPLOYMENT_BULLETS (proof source only — use ONLY fact ids from this list):\n"
        + fact_lines.strip()
        + "\n\nSELECTED_FACT_PLAN_STUB (echo this shape in output only; do not paste facts[] array):\n"
        + stub
    )

    jd_block = (
        f"TARGET_TITLE (NOT PROOF): {t_title}\n"
        f"TARGET_COMPANY (NOT PROOF): {t_company}\n"
        f"JD_TEXT (ranking/targeting only — NOT PROOF): {jd}\n"
        f"BRIEFING (NOT PROOF): {briefing}\n"
        "JD may rank or select terms but must NOT be treated as candidate experience."
    )

    u0 = (
        "Generate exactly EIGHT resume competency categories for ATS alignment.\n"
        "Return RAW JSON only: first character {, last character }. No ``` fences.\n\n"
        "OUTPUT CONTRACT (top-level object):\n"
        "- competencies: array of exactly 8 objects, each with:\n"
        "  - category_label: short title (no colon, no newlines, not a sentence)\n"
        "  - terms: array of 2 to 6 entries; each entry is EITHER a short noun phrase string OR an object "
        'with keys "text", "source_fact_id" (single bul_*), and optional "jd_signal_ids": [strings]; '
        "if any term in a category uses the object form, every term in that category MUST use it.\n"
        "  - source_fact_ids: non-empty array of bul_* ids backing the category\n"
        "- selected_fact_plan: stub only {section_id, selection_method, required_fact_ids}\n"
        "- claim_ledger: one row per term with claim_text and source_fact_ids ([single bul_*] for structured terms)\n"
        '- jd_alignment: {targeting_only: true, jd_used_as_proof: false}\n'
        "- excluded_jd_skills, removed_or_rewritten_terms, gap_notes, change_log, self_check\n\n"
        "RULES:\n"
        "- Terms augment resume evidence; do not paste long bullet fragments.\n"
        "- C0 candidate_facts are the only proof block; U-tier companion is context only.\n"
        "- No inline [source:] tags in display strings.\n"
        "- Third person / capability voice only.\n"
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
            content=c0_facts,
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
        r0_response_schema=_COMPETENCIES_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "competencies",
        },
    )


def compile_competencies_prompt(
    runtime_payload: dict[str, Any],
    *,
    companion_context: str,
    fact_lines: str,
    run_id: str,
) -> SectionCompiledPrompt:
    assembly = build_competencies_assembly_input(
        runtime_payload,
        fact_lines,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"competencies:{run_id}",
    )
    tier = companion_context.strip() or None
    return compile_section_prompt(
        assembly,
        section_id="competencies",
        companion_u_tier=tier,
    )


__all__ = [
    "build_competencies_assembly_input",
    "compile_competencies_prompt",
    "load_competencies_template_slots",
]
