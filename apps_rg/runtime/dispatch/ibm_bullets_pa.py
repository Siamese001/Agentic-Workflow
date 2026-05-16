"""IBM bullets: PA compile via section_prompt_adapter (W7 mechanical)."""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    BULLETS_R0,
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
        "You are an IBM employment bullet tailor. "
        "Return RAW JSON ONLY: response must begin with { and end with }. "
        "No markdown fences. No prose outside JSON.\n\n"
        "READ-ONLY HEADER (never rewrite): "
        f"company={header['employer']}; title={header['title']}; "
        f"location={header['location']}; dates={header['start_date']} to {header['end_date']}.\n\n"
        "SCOPE: Use ONLY bul_ibm_001..005 facts. No Unify, InsurTech, EY, education, certification, or early-career facts.\n"
        "IBM bullets must read as supporting enterprise/platform proof, not current agentic runtime ownership.\n"
        "OUTPUT: exactly 5 bullets. bullet_id MUST be bul_ibm_001 through bul_ibm_005.\n"
        "Each bullet object: bullet_id, bullet_text, rewrite_intensity, has_metric, metric_raw, source_fact_ids.\n"
        "claim_ledger MUST list every bullet with claim_text and source_fact_ids (include granular bul_ibm_*_metric_* IDs when metrics are cited).\n"
        "DISTRIBUTION: 0 HEAVY, 3 MODERATE, 2 LIGHT_PROTECTED (total=5). No HEAVY rewrites.\n"
        "Preserve core IBM metrics in bullet_text exactly as tokens: $15M, 99.9%, 30%, 25%, 50%.\n"
        "Never import Unify runtime vocabulary: agentic AI, GraphRAG, multi-agent orchestration, deterministic routing, "
        "sandboxed execution, replayable traces, governed AI runtime, prompt assembly, C0, L2, Exit, UWG.\n"
        "JD and briefing are targeting context only, never proof.\n"
        "No first person. No em dash. No inline source tags. No generic filler.\n"
        "Include top-level: bullets, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, "
        "change_log, rewrite_distribution, self_check."
    )


def compile_ibm_bullets_prompt(
    runtime_payload: dict[str, Any],
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    fact_lines = _fact_lines(runtime_payload)
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=run_id,
        run_id=run_id,
        trace_root=f"ibm_bullets:{run_id}",
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
        u0_user_task=(
            "Return one JSON object with rewrite_distribution HEAVY=0, MODERATE=3, LIGHT_PROTECTED=2, total=5."
        ),
        r0_response_schema=BULLETS_R0,
        render_context={"section_id": "ibm_bullets"},
    )
    return compile_section_prompt(assembly, section_id="ibm_bullets")


__all__ = ["compile_ibm_bullets_prompt"]
