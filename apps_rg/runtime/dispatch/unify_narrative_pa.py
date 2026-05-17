"""Unify narrative: PA compile via section_prompt_adapter (W7 mechanical).

Legacy prompt semantics preserved: I0 matches prior inline system; C0 carries CANONICAL UNIFY FACTS;
jd_requirements carries targeting only; accepted companion bullets are required U-tier read-only sequencing context for production.
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
    dep_status = str(runtime_payload.get("companion_unify_bullets_status") or "UNKNOWN")
    dep_reason = str(runtime_payload.get("companion_unify_bullets_reason") or "")
    return (
        "# Role and Objective\n"
        "You are a senior executive resume editor writing exactly ONE Unify Consulting role narrative sentence. "
        "This sentence must sit above finalized Unify bullets and position the current role as the candidate's strongest "
        "SVP Engineering proof point.\n\n"
        "# Output Contract\n"
        "Return RAW JSON only: first character {, last character }. No markdown fences.\n"
        "Required JSON keys: narrative_sentence, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, change_log, self_check.\n\n"
        "# Required Upstream Dependency\n"
        f"companion_unify_bullets_status={dep_status}; reason={dep_reason}.\n"
        "Production narrative requires accepted finalized Unify bullets from the prior lane. If status is not ACCEPTED_FINALIZED, "
        "produce a safe JSON object that records the dependency gap in gap_notes and self_check; do not pretend the bullets are finalized.\n\n"
        "# Read-Only Role Header\n"
        f"employer={header['employer']}; title={header['title']}; location={header['location']}; "
        f"dates={header['start_date']} to {header['end_date']}.\n"
        "Include the exact text Unify Consulting once as the employer anchor. Never name the candidate.\n\n"
        "# Source Authority Hierarchy\n"
        "1. Proof sources: canonical bul_unify_* facts and accepted Unify bullets only.\n"
        "2. Targeting context: target title, target company, JD, and briefing influence angle and vocabulary only.\n"
        "3. JD, company brief, and target company are never proof of candidate experience.\n"
        "4. No IBM, InsurTech, EY, education, certification, or early-career facts.\n\n"
        "# Private Drafting Process\n"
        "Think privately before writing JSON. Do not expose reasoning.\n"
        "Step 1: Read accepted bullets and identify what they already prove.\n"
        "Step 2: Choose one complementary angle: platform mandate, governed operating model, commercialization, delivery cadence, or engineering scale.\n"
        "Step 3: Use JD/company/briefing only to pick emphasis, not proof.\n"
        "Step 4: Draft one sentence and self-repair for repetition, unsupported claims, JD mirroring, and executive readability.\n\n"
        "# Voice and Openers\n"
        "Do NOT begin with At Unify Consulting, the or At Unify, the.\n"
        "Do NOT write the SVP Engineering, the Senior Vice President, or any the <job title> stack before a verb.\n"
        "Prefer a subject-first or implied-subject executive arc.\n"
        "Frame Unify as current agentic AI platform leadership proof, not a generic job summary.\n\n"
        "# Narrative Shape\n"
        "One flowing sentence, roughly 32 to 44 words and under 52 words.\n"
        "One strategic through-line plus one supported proof cue if needed.\n"
        "Complement the six bullets; do not recap each bullet.\n"
        "Do not paste contiguous phrases from CANONICAL UNIFY FACTS or accepted bullets.\n"
        "No first person. No candidate name. No em dash. No inline source tags. No generic filler.\n\n"
        "# Metric Repetition\n"
        "If accepted bullets already carry $22M, 20%, 8-to-28 headcount, and six-months-to-three-weeks, "
        "the narrative may mention at most one metric cluster. Prefer conceptual language such as commercialization, "
        "platform economics, organization scaling, or deployment acceleration.\n"
        "When citing cycle-time improvement, use the supported literal: reducing lab-to-production cycle time from six months to three weeks.\n\n"
        "# Forbidden Checklist Sentence\n"
        "Do not string these as a list: deterministic routing, multi-agent orchestration, GraphRAG, sandboxed execution, policy gating, replayable traces."
    )


def _u0(companion_nonempty: bool, dependency_status: str) -> str:
    closing = (
        "Write one narrative_sentence only: strong platform-leadership arc for Unify Consulting, third person, "
        "one period at the end, under 52 words, no while also stack."
    )
    if dependency_status != "ACCEPTED_FINALIZED":
        return (
            "Finalized Unify bullets are not accepted yet. Return JSON that marks dependency_not_finalized in "
            "gap_notes and self_check. Do not fabricate a production-ready narrative.\n\n"
            + closing
        )
    if companion_nonempty:
        return closing
    return (
        "Accepted dependency metadata exists but no companion bullet text was supplied; mark this as a dependency gap.\n\n"
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
        u0_user_task=_u0(companion_nonempty, str(runtime_payload.get("companion_unify_bullets_status") or "UNKNOWN")),
        r0_response_schema=NARRATIVE_R0,
        render_context={
            "section_id": "unify_narrative",
            "target_title": str(runtime_payload.get("target_title") or ""),
            "target_company": str(runtime_payload.get("target_company") or ""),
        },
    )
    return compile_section_prompt(assembly, section_id="unify_narrative", companion_u_tier=tier)


__all__ = ["compile_unify_narrative_prompt"]
