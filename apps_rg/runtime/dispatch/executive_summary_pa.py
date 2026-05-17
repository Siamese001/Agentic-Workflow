"""Executive summary: build PromptAssemblyInput from runtime payload + template YAML (W4).

Loads slot bodies from ``executive_summary.generate_scratch_v1.yaml`` and compiles via
``section_prompt_adapter``. C0 carries selected_fact_plan facts (proof). The
``c0_jd_requirements`` block carries JD_TEXT + BRIEFING + target framing for **targeting
only** (rank, order, vocabulary tilt among evidenced facts) - never as proof. Style should match the
canonical base résumé register (dense, concrete stack/governance nouns), without JD
keyword-stuffing.
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
            "claim_ledger": {
                "type": "array",
                "description": (
                    "Each row must include non-empty claim_text (material claim supported by source_fact_ids) and "
                    "source_fact_ids copied exactly from ALLOWED_SOURCE_FACT_IDS. Rows with only source_fact_ids fail "
                    "gate x2_claim_ledger_claim_text_non_empty. Malformed or orphan IDs fail X2 and block X3."
                ),
                "items": {
                    "type": "object",
                    "required": ["claim_text", "source_fact_ids"],
                    "properties": {
                        "claim_text": {
                            "type": "string",
                            "minLength": 1,
                            "description": (
                                "Non-empty material claim text supported by this row's source_fact_ids; must align with "
                                "resume_display_text. Whitespace-only is invalid."
                            ),
                        },
                        "claim": {
                            "type": "string",
                            "description": (
                                "Optional legacy alias for claim_text; normalize to claim_text. Do not use JD/title/"
                                "company/briefing as proof."
                            ),
                        },
                        "source_fact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Each string must exactly match one entry from ALLOWED_SOURCE_FACT_IDS. "
                                "Example: bul_unify_003 is valid when listed; bul_unify_ 003 is never valid."
                            ),
                        },
                    },
                },
            },
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


def _ordered_allowed_source_fact_ids(
    runtime_payload: dict[str, Any], facts: list[dict[str, Any]]
) -> list[str]:
    raw = runtime_payload.get("allowed_fact_ids")
    if isinstance(raw, list) and raw:
        return [str(x) for x in raw]
    out: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        fid = str(fact.get("fact_id") or "").strip()
        if fid and fid not in seen:
            seen.add(fid)
            out.append(fid)
    return out


def format_allowed_source_fact_ids_contract(allowed_ids: list[str]) -> str:
    """Pinned contract text: dynamic list + rules; spacing example matches orphan regressions."""
    lines = [
        "ALLOWED_SOURCE_FACT_IDS (authoritative list for every claim_ledger[].source_fact_ids entry):",
        "",
        "Rules:",
        "- Copy each ID character-for-character from the allowed lines below.",
        "- Do not invent, rewrite, normalize, split, merge, abbreviate, or approximate IDs.",
        "- Do not insert spaces or punctuation inside an ID (spacing drift fails coverage).",
        "- Every string in source_fact_ids MUST be exactly one of the allowed IDs below.",
        "- Tokens not in this list are orphan IDs: they fail deterministic gate x2_claim_ledger_orphan_zero and X3 stays BLOCK (not ALLOW).",
        "- Every claim_ledger row must include non-empty claim_text (material prose); rows with only source_fact_ids fail x2_claim_ledger_claim_text_non_empty.",
        "",
        "Spacing drift example (pattern only; your tokens are the allowed list):",
        '- INVALID: "bul_unify_ 003"  # space inside token',
        '- VALID when listed below: "bul_unify_003"  # exact copy from ALLOWED_SOURCE_FACT_IDS',
        "",
        "Allowed IDs:",
    ]
    for i in allowed_ids:
        lines.append(f"  - {i}")
    return "\n".join(lines)


def format_selected_facts_for_c0(facts: list[dict[str, Any]], allowed_source_fact_ids: list[str]) -> str:
    header = format_allowed_source_fact_ids_contract(allowed_source_fact_ids)
    lines: list[str] = []
    for fact in facts:
        fid = fact.get("fact_id", "")
        ct = str(fact.get("claim_text") or "").strip()
        extra = ""
        if fact.get("metric_raw"):
            extra = f" metric_raw={fact.get('metric_raw')!r}"
        lines.append(f"- {fid}: {ct}{extra}")
    body = "SELECTED_FACT_PLAN (proof-only; do not invent beyond these lines):\n" + "\n".join(lines)
    return f"{header}\n\n{body}"


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
        f"TARGET_TITLE (positioning only  -  NOT PROOF): {t_title}\n"
        f"TARGET_COMPANY (positioning only  -  NOT PROOF): {t_company}\n"
        f"JD_TEXT (targeting only  -  rank/order/frame facts; NOT PROOF): {jd}\n"
        f"BRIEFING (targeting only  -  rank/order/frame facts; NOT PROOF): {briefing}\n"
        "Use TARGET_TITLE and TARGET_COMPANY for positioning toward the reader. "
        "Use JD_TEXT and BRIEFING only to rank, order, and frame selected facts in resume_display_text: "
        "which themes lead, how vocabulary tilts toward the target, and what stays implicit. "
        "Never treat JD_TEXT, BRIEFING, titles, or company as proof of capability.\n"
        "Do not mirror JD phrasing, paste JD lists, or keyword-stuff. Paraphrase sparingly into the dense, "
        "concrete register of the canonical base résumé (stack and governance nouns from selected facts).\n"
        "Every substantive claim must trace to C0 selected facts; jd_alignment must state jd_used_as_proof=false."
    )

    allowed_ids = _ordered_allowed_source_fact_ids(runtime_payload, facts)
    if not allowed_ids:
        raise ValueError("allowed_fact_ids or non-empty fact_id on each selected fact is required for executive_summary PA")

    u0 = (
        f"Generate executive summary for target title: {t_title!r}. "
        f"Target company (positioning only, never as employer proof): {t_company!r}.\n"
        "Use ONLY facts listed in C0 candidate_facts (selected_fact_plan). "
        "Use JD_TEXT + BRIEFING in the jd_requirements block for targeting only: prioritization, ordering, "
        "and framing among those facts - never to add claims.\n"
        "Return RAW JSON only (object). First character {{, last character }}.\n"
        "Shape resume_display_text using **sentence role goals**, not word count or fixed sentence count: "
        "(1) executive identity and operating domain; "
        "(2) governed runtime, platform architecture, or autonomous systems capability; "
        "(3) platform lifecycle, operating model, engineering scale-out, or commercialization; "
        "(4) quantified business, reliability, capacity, margin, revenue, adoption, or deployment impact; "
        "(5) credential, actuarial, statistical, causal inference, or distributed systems depth only if directly supported. "
        "Combine roles when facts are thin; split when a sentence becomes comma-heavy; "
        "never one sentence per source fact; never pad a role or cut supported proof for length; "
        "prefer synthesized executive prose over bullet-by-bullet translation.\n"
        "Internally compare multiple supported narrative orderings before returning the final JSON. "
        "Do not output reasoning.\n"
        "resume_display_text must be clean prose: NO [source: ...], NO fact_id tokens, NO bracket citations. "
        "Bind every material claim in claim_ledger; each row MUST include non-empty claim_text (material prose for that "
        "claim) and source_fact_ids that are exact strings from ALLOWED_SOURCE_FACT_IDS in C0 "
        "(character-for-character; no interior spaces). Rows with only source_fact_ids fail x2_claim_ledger_claim_text_non_empty. "
        "Do not use JD, target title, target company, or BRIEFING to fabricate claim_text.\n"
        "Match canonical base-résumé style: third person, engineering executive density, preserve specific nouns "
        "from facts over generic dilution.\n"
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
            content=format_selected_facts_for_c0(facts, allowed_ids),
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
