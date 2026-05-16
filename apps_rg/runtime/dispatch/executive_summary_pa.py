"""Executive summary: build PromptAssemblyInput from runtime payload + template YAML (W4).

Loads slot bodies from ``executive_summary.generate_scratch_v1.yaml`` and compiles via
``section_prompt_adapter``. C0 carries **only** selected_fact_plan facts and JD/briefing
as non-proof context — no full-resume dump.
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
            / "executive_summary.generate_scratch_v1.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError(
        "Cannot resolve repo root from executive_summary_pa.py (template yaml not found in parents)"
    )


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "executive_summary.generate_scratch_v1.yaml"
)

_EXEC_SUMMARY_OUTPUT_SCHEMA_JSON = json.dumps(
    {
        "type": "object",
        "required": [
            "resume_display_text",
            "selected_fact_plan",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "resume_display_text": {
                "type": "string",
                "description": "Third-person executive summary only; no inline citations or fact IDs",
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


def load_executive_summary_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def format_selected_facts_for_c0(facts: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for fact in facts:
        fid = fact.get("fact_id", "")
        ct = str(fact.get("claim_text") or "").strip()
        extra = ""
        if fact.get("metric_raw"):
            extra = f" metric_raw={fact.get('metric_raw')!r}"
        lines.append(f"- {fid}: {ct}{extra}")
    return "SELECTED_FACT_PLAN (proof-only; do not invent beyond these lines):\n" + "\n".join(lines)


def build_executive_summary_assembly_input(
    runtime_payload: dict[str, Any],
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
) -> PromptAssemblyInput:
    slots = load_executive_summary_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    if not facts:
        raise ValueError("selected_fact_plan.facts is required for executive_summary PA input")

    t_title = str(runtime_payload.get("target_title") or "")
    t_company = str(runtime_payload.get("target_company") or "")
    jd = str(runtime_payload.get("jd_text") or "")
    briefing = str(runtime_payload.get("briefing") or "")

    jd_block = (
        f"TARGET_ROLE_CONTEXT (NOT PROOF): {jd}\n"
        f"BRIEFING (NOT PROOF): {briefing}\n"
        "These lines are targeting context only. Do not treat them as candidate experience."
    )

    u0 = (
        f"Generate executive summary for target title: {t_title!r}. "
        f"Target company (positioning only, never as employer): {t_company!r}.\n"
        "Use ONLY facts listed in C0 candidate_facts (selected_fact_plan). "
        "Return RAW JSON only (object). First character {{, last character }}.\n"
        "Default: exactly TWO synthesized sentences in resume_display_text (commercial arc, then governance/delivery).\n"
        "resume_display_text must be clean prose: NO [source: ...], NO fact_id tokens, NO bracket citations. "
        "Bind every material claim in claim_ledger with source_fact_ids from the selected facts only.\n"
        "jd_alignment must state jd_used_as_proof=false."
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
            content=format_selected_facts_for_c0(facts),
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
        r0_response_schema=_EXEC_SUMMARY_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "executive_summary",
        },
    )


def compile_executive_summary_prompt(runtime_payload: dict[str, Any], *, run_id: str) -> SectionCompiledPrompt:
    assembly = build_executive_summary_assembly_input(
        runtime_payload,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"exec_summary:{run_id}",
    )
    return compile_section_prompt(assembly, section_id="executive_summary")


__all__ = [
    "build_executive_summary_assembly_input",
    "compile_executive_summary_prompt",
    "load_executive_summary_template_slots",
]
