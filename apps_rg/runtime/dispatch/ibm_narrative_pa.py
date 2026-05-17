"""IBM narrative: PA compile via section_prompt_adapter (W7 mechanical).

Preserves prior inline system/user semantics via I0 + C0 + jd_requirements + U0; companion IBM bullets U-tier when present.
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
    header = runtime_payload["ibm_header"]
    return (
        "You write exactly ONE polished IBM employment narrative sentence. "
        "Return RAW JSON only: first character {, last character }. No markdown fences.\n\n"
        f"READ-ONLY CONTEXT (not copy-paste openers): employer={header['employer']}, title={header['title']}, "
        f"location={header['location']}, dates={header['start_date']} to {header['end_date']}.\n"
        "IDENTITY (mandatory):\n"
        "- Do not include the candidate's given name, surname, initials, or full name — the résumé header already identifies them.\n"
        "- Use implied subject or role-first framing (e.g. \"At IBM, architected …\" / \"While at IBM, …\") without naming the person.\n\n"
        "VOICE (mandatory):\n"
        "- Include the exact text \"IBM\" once as the employer anchor (company name).\n"
        "- Third person or implied subject only. No first person. No em dash. No inline source tags.\n"
        "- IBM should read as supporting enterprise and platform credibility, not current agentic runtime ownership.\n\n"
        "LANE ORDER (mandatory when U-tier companion bullets exist):\n"
        "- Those ACCEPTED_IBM_BULLETS are the finalized JD-tailored bullet set from the prior lane.\n"
        "- Write narrative_sentence as the capstone after that tailoring: match their strategic emphasis and vocabulary, "
        "do not contradict them, and do not paste their sentences.\n\n"
        "SCOPE: Use ONLY bul_ibm_001..005 facts for proof. No Unify, InsurTech, EY, education, certification, or early-career facts.\n"
        "Never use Unify-era runtime vocabulary (agentic AI, GraphRAG, multi-agent orchestration, deterministic routing, "
        "sandboxed execution, replayable traces, governed AI runtime, prompt assembly, C0, L2, Exit, UWG).\n"
        "JD and briefing are targeting context only, never proof.\n\n"
        "METRICS: When companion IBM bullets already enumerate $15M, 99.9%, 30%, 25%, and 50%, narrative_sentence MUST contain "
        "at most ONE numeric token from that IBM proof set—or zero numbers. Prefer qualitative enterprise cloud and reliability "
        "framing instead of stacking metrics (never pair two percentages such as 99.9% and 30%; never cite $15M and a percentage in "
        "the same sentence).\n\n"
        "SYNTHESIS: Complement the five bullets with connective framing; do not summarize each bullet or copy a five-word opening from them.\n\n"
        "Required JSON keys: narrative_sentence, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, change_log, self_check.\n"
        "claim_ledger: array of {claim_text, source_fact_ids} with bul_ibm_001 through bul_ibm_005 only (single underscores; no typos).\n"
        "Every substantive clause in narrative_sentence must appear as claim_text in claim_ledger with matching bul_ibm_* IDs."
    )


def _u0(companion_nonempty: bool) -> str:
    closing = (
        "Write one narrative_sentence only: enterprise platform credibility at IBM, third person, "
        "one period at the end, under 52 words."
    )
    if companion_nonempty:
        return closing
    return "(No companion ibm_bullets artifact; still avoid repeating every metric in one list.)\n\n" + closing


def compile_ibm_narrative_prompt(
    runtime_payload: dict[str, Any],
    companion_text: str,
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    fact_lines = _fact_lines(runtime_payload)
    companion_nonempty = bool(companion_text.strip())
    tier = (
        f"ACCEPTED_IBM_BULLETS (read-only; do not recap each line):\n{companion_text.strip()}"
        if companion_nonempty
        else None
    )
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=run_id,
        run_id=run_id,
        trace_root=f"ibm_narrative:{run_id}",
        s0_system_preamble=slots["S0"],
        d0_fences=slots["D0"],
        e0_examples=slots["E0"],
        y0_style_preferences=slots["Y0"],
        i0_instructions=_legacy_i0(runtime_payload),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content="CANONICAL IBM FACTS:\n" + fact_lines,
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
            "section_id": "ibm_narrative",
            "target_title": str(runtime_payload.get("target_title") or ""),
            "target_company": str(runtime_payload.get("target_company") or ""),
        },
    )
    return compile_section_prompt(assembly, section_id="ibm_narrative", companion_u_tier=tier)


__all__ = ["compile_ibm_narrative_prompt"]
