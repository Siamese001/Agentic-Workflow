"""Unify narrative: PA compile via section_prompt_adapter (W7 mechanical).

Legacy prompt semantics preserved: I0 matches prior inline system; C0 carries CANONICAL UNIFY FACTS;
jd_requirements carries targeting only; accepted companion bullets are required U-tier read-only sequencing context for production.
Compile failures propagate (no inline fallback).

W11-M4B SSOT: apps_rg.runtime.sections.unify_narrative_pa."""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.prompt_assembly.e0_examples import resolve_e0_for_section
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool
from apps_rg.runtime.sections.executive_summary_pa import format_selected_facts_for_c0
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    NARRATIVE_R0,
    jd_non_proof_block,
    load_w7_shell_slot_bodies,
)


def _canonical_unify_facts_c0(runtime_payload: dict[str, Any]) -> str:
    facts = list((runtime_payload.get("selected_fact_plan") or {}).get("facts") or [])
    raw_allowed = runtime_payload.get("allowed_fact_ids")
    if isinstance(raw_allowed, list) and raw_allowed:
        allowed_ids = [str(x) for x in raw_allowed]
    else:
        allowed_ids = [str(f.get("fact_id") or "") for f in facts if f.get("fact_id")]
    return format_selected_facts_for_c0(facts, allowed_ids)


def _legacy_i0(runtime_payload: dict[str, Any]) -> str:
    header = runtime_payload["unify_header"]
    dep_status = str(runtime_payload.get("companion_unify_bullets_status") or "UNKNOWN")
    dep_reason = str(runtime_payload.get("companion_unify_bullets_reason") or "")
    return (
        "<!-- UNIFY_IBM_PROMPT_CORE_LAW_V3 — section I0; X2 gate IDs in PRODUCT_SHAPE only -->\n\n"
        "# Role\n"
        "Write exactly ONE Unify Consulting role capstone sentence above six finalized bullets — strategic mandate, "
        "not bullet recap. pa_proof_binding_v1 + pa_targeting_only_v1 (pa_core_law_v1.yaml).\n\n"
        "# North star (paraphrase; stay inside C0 unify_narrative_base_* and bul_unify_*)\n"
        "Platform roadmap, core systems architecture, commercialization of supported AI platform/Solution Accelerator, "
        "bespoke delivery → reusable IP or scalable platform services in enterprise contexts.\n\n"
        "# Output\n"
        "RAW JSON; keys: narrative_sentence, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, change_log, self_check.\n"
        "claim_ledger: non-empty claim_text and source_fact_ids from ALLOWED_SOURCE_FACT_IDS only.\n"
        "jd_alignment: selected_jd_themes, selected_briefing_themes (non-empty when briefing present), targeting_rationale, "
        "jd_used_as_proof:false, briefing_used_as_proof:false, companion_context_used_as_proof:false.\n\n"
        f"# Dependency\n"
        f"companion_unify_bullets_status={dep_status}; reason={dep_reason}. "
        "If not ACCEPTED_FINALIZED, record gap in gap_notes/self_check — do not fabricate production narrative.\n\n"
        f"# Header\n"
        f"employer={header['employer']}; title={header['title']}; location={header['location']}; "
        f"dates={header['start_date']} to {header['end_date']}. Unify Consulting once; never candidate name.\n"
        "No IBM, InsurTech, EY, education, certification, early-career facts.\n\n"
        "# Shape\n"
        "One sentence; 34–48 words preferred; max 58 words / 360 chars; no bullets; third person; no em dash; no inline tags.\n"
        "Companion bullets: anti-repetition only, not proof. Default zero metrics; at most one cluster if C0-supported and non-redundant.\n"
        "Forbidden labels: Enterprise Agentic AI Platform Architecture; Dependency Graph Accelerator; Governed Runtime Reliability; "
        "Production Adoption; Distributed Ecosystem Engineering; Platform Commercialization and Engineering Leadership.\n"
        "Do not open with At Unify Consulting, the / At Unify, the; no mechanism comma-stacks (routing, GraphRAG, gating, traces).\n"
        "FORBIDDEN MECHANICAL OPENERS — narrative MUST NOT begin with any of (case-insensitive): "
        "led, successfully, also, built, delivered, designed, implemented, architected. "
        "Use substantive openers instead: Owned, Drove, Scaled, Championed, Productized, Operationalized, Established, "
        "Anchored, Stewarded, Originated; or noun-phrase openers like \"Platform roadmap and commercialization of ...\".\n"
        "STRICT METRIC POLICY — DEFAULT zero metrics in the narrative; bullets carry the metrics. "
        "NEVER repeat $22M, 20%, six-months-to-three-weeks, 8-to-28 (or any bullet-side number) — those are bullet content, not capstone content.\n\n"
        "# Examples (patterns only)\n"
        "Good: Owned the platform roadmap and commercialization of a production-grade agentic AI platform at Unify Consulting, "
        "converting bespoke delivery into reusable platform services for regulated financial-services adoption.\n"
        "Good alt: Drove the strategic mandate to industrialize a governed agentic AI platform at Unify Consulting, "
        "establishing reusable IP and scalable platform services for regulated financial-services adoption.\n"
        "Bad (mechanical opener): \"Led platform roadmap and commercialization ...\" — fails the forbidden-opener gate.\n"
        "Bad (metric recap): \"... reducing cycle times from six months to three weeks while generating $22M ...\" — "
        "fails metric-cap and bullet-overlap gates.\n"
        "Bad: JD-as-proof; bullet-label paste."
    )


def _u0(companion_nonempty: bool, dependency_status: str) -> str:
    closing = (
        "Write one narrative_sentence only: north-star role capstone for Unify Consulting (roadmap + architecture + "
        "commercialization + reusable IP + enterprise deployment), third person, one period, "
        "preferred 34–48 words, hard max 58 words and 360 characters, no while also stack."
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
        e0_examples=resolve_e0_for_section("unify_narrative", slots.get("E0")),
        y0_style_preferences=slots["Y0"],
        i0_instructions=_legacy_i0(runtime_payload),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content=_canonical_unify_facts_c0(runtime_payload),
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
    compiled = compile_section_prompt(assembly, section_id="unify_narrative", companion_u_tier=tier)
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_unify_narrative_prompt"]
