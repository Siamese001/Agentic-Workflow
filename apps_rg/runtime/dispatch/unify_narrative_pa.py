"""Unify narrative: PA compile via section_prompt_adapter (W7 mechanical).

Legacy prompt semantics preserved: I0 matches prior inline system; C0 carries CANONICAL UNIFY FACTS;
jd_requirements carries targeting only; companion bullets are U-tier only when present.
Compile failures propagate (no inline fallback).
"""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    NARRATIVE_R0,
    jd_non_proof_block,
    load_w7_shell_slot_bodies,
)


def _fact_lines(runtime_payload: dict[str, Any]) -> str:
    facts = runtime_payload["selected_fact_plan"]["facts"]
    return "\n".join(
        f"- {fact['fact_id']}: {fact['claim_text']}"
        + (f" | metric: {fact['metric_raw']}" if fact.get("metric_raw") else "")
        for fact in facts
    )


def _legacy_i0(runtime_payload: dict[str, Any]) -> str:
    header = runtime_payload["unify_header"]
    cand = str(runtime_payload.get("candidate_name") or "").strip()
    cand_line = f"Executive name from resume (optional, at most once, natural third person): {cand}.\n" if cand else ""
    return (
        "You write exactly ONE polished Unify Consulting role narrative sentence. "
        "Return RAW JSON only: first character {, last character }. No markdown fences.\n\n"
        f"READ-ONLY CONTEXT (not copy-paste openers): employer={header['employer']}, title={header['title']}, "
        f"location={header['location']}, dates={header['start_date']} to {header['end_date']}.\n"
        f"{cand_line}"
        "VOICE AND OPENERS (mandatory):\n"
        "- Do NOT begin with \"At Unify Consulting, the\" or \"At Unify, the\".\n"
        "- Do NOT write \"the SVP Engineering\", \"the Senior Vice President\", or any \"the <job title>\" stack before a verb.\n"
        "- Prefer subject-first or implied-subject executive arc: who shaped what outcome at Unify Consulting.\n"
        "- Include the exact text \"Unify Consulting\" once as the employer anchor (never omit the company name).\n"
        "- Frame Unify as the current agentic AI platform leadership proof point, not a generic job summary.\n\n"
        "ARC (one flowing sentence):\n"
        "- Weave governed agentic platform execution, reusable AI primitives, retrieval and lifecycle operating discipline, "
        "and enterprise delivery momentum without sounding like a task list.\n"
        "- Paraphrase each idea; do NOT paste contiguous phrases from CANONICAL UNIFY FACTS claim_text (especially avoid "
        "copying the opening clause of bul_unify_001 verbatim).\n"
        "- Banned substrings (case-insensitive rewrite required if any appear): "
        "\"designed and operationalized\", \"governed agentic ai platform for regulated enterprise workflows\", "
        "\"architected a governed\".\n"
        "- Optionally nod once to dependency intelligence (002) and retrieval quality (003) with short fresh wording, "
        "without a technical inventory.\n"
        "- When citing cycle-time improvement, use the supported literal: "
        "\"reducing lab-to-production cycle time from six months to three weeks\" (bul_unify_004). "
        "Do NOT use vague phrases like \"reduce cycle times significantly\" or \"faster time to market\" as substitutes.\n"
        "- If companion bullets already carry $22M, 20%, 8-to-28 headcount, and six-months-to-three-weeks, "
        "the narrative_sentence must mention AT MOST ONE of those metric clusters, and it should be "
        "\"reducing lab-to-production cycle time from six months to three weeks\" (no $22M, no 20%, no 8-to-28 in that sentence).\n"
        "- You may still reference bul_unify_006 themes qualitatively (productized primitives, IP-led revenue momentum, "
        "margin discipline, specialist bench scaling) without dollar signs, percent figures, or numeric headcount.\n"
        "- Add SVP-level operating signal: enterprise scale, delivery cadence, operating discipline, or cross-team "
        "engineering momentum, synthesized across facts rather than chaining two claim_text fragments.\n"
        "FORBIDDEN LISTS (do not string these as a comma checklist in the sentence):\n"
        "deterministic routing, multi-agent orchestration, GraphRAG, sandboxed execution, policy gating, replayable traces.\n"
        "You may refer to the governed platform at a high level without enumerating that full stack.\n\n"
        "LENGTH AND SHAPE (mandatory):\n"
        "- Aim for roughly 32 to 44 words; stay under 52 words so the line reads as one executive clause, not a bullet rollup.\n"
        "- At most one comma spine before the cycle clause; avoid \"while also\", \"along with\", or three-part conjunction stacks.\n"
        "- One strategic through-line (why the platform operating model mattered) plus the exact cycle clause; "
        "do not mirror four bullet domains in one sentence.\n\n"
        "SCOPE: Use ONLY bul_unify_* facts for proof. No IBM, InsurTech, EY, education, or early-career facts.\n"
        "JD and briefing are targeting context only, never proof.\n"
        "Third person or implied subject only. No first person. No em dash. No inline source tags. No generic filler.\n"
        "Complement the six bullets with connective synthesis; do not summarize each bullet.\n\n"
        "Required JSON keys: narrative_sentence, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, change_log, self_check.\n"
        "claim_ledger: array of {claim_text, source_fact_ids}. Each ID must be EXACTLY one of "
        "bul_unify_001, bul_unify_002, bul_unify_003, bul_unify_004, bul_unify_005, bul_unify_006 "
        "(single underscore only; never bul_unify__006 or other typos).\n"
        "Every substantive clause in narrative_sentence must appear as claim_text in claim_ledger with matching bul_unify_* IDs."
    )


def _u0(companion_nonempty: bool) -> str:
    closing = (
        "Write one narrative_sentence only: strong platform-leadership arc for Unify Consulting, third person, "
        "one period at the end, under 52 words, no \"while also\" stack."
    )
    if companion_nonempty:
        return closing
    return (
        "(No companion unify_bullets artifact; still avoid repeating every metric in one list.)\n\n"
        + closing
    )


def compile_unify_narrative_prompt(
    runtime_payload: dict[str, Any],
    companion_text: str,
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    fact_lines = _fact_lines(runtime_payload)
    companion_nonempty = bool(companion_text.strip())
    tier = (
        f"ACCEPTED_UNIFY_BULLETS (read-only; do not recap each line):\n{companion_text.strip()}"
        if companion_nonempty
        else None
    )
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=run_id,
        run_id=run_id,
        trace_root=f"unify_narrative:{run_id}",
        s0_system_preamble=slots["S0"],
        d0_fences=slots["D0"],
        e0_examples=slots["E0"],
        y0_style_preferences=slots["Y0"],
        i0_instructions=_legacy_i0(runtime_payload),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content="CANONICAL UNIFY FACTS:\n" + fact_lines,
            confidence=1.0,
            source_tag="candidate_facts",
        ),
        c0_jd_requirements=EvidenceSource(
            source_type="jd_requirements",
            content=jd_non_proof_block(runtime_payload),
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=_u0(companion_nonempty),
        r0_response_schema=NARRATIVE_R0,
        render_context={
            "section_id": "unify_narrative",
            "target_title": str(runtime_payload.get("target_title") or ""),
            "target_company": str(runtime_payload.get("target_company") or ""),
        },
    )
    return compile_section_prompt(assembly, section_id="unify_narrative", companion_u_tier=tier)


__all__ = ["compile_unify_narrative_prompt"]
