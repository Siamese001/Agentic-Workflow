"""Unify bullets: PA compile via section_prompt_adapter (W7 mechanical)."""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import augment_section_compiled_with_input_authority
from apps_rg.runtime.dispatch.executive_summary_pa import (
    _ordered_allowed_source_fact_ids,
    format_allowed_source_fact_ids_contract,
)
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    BULLETS_R0,
    jd_non_proof_block,
    load_w7_shell_slot_bodies,
)
from apps_rg.runtime.validators.unify_bullets_x2 import PROTECTED_BULLET_DEFAULT


def _candidate_facts_block(runtime_payload: dict[str, Any]) -> str:
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    allowed_ids_list = _ordered_allowed_source_fact_ids(runtime_payload, facts)
    allowed_block = format_allowed_source_fact_ids_contract(allowed_ids_list)
    fact_lines = "\n".join(
        f"- {fact['fact_id']}: {fact['claim_text']}"
        + (f" | metric: {fact['metric_raw']}" if fact.get("metric_raw") else "")
        for fact in facts
    )
    unify_id_hygiene = (
        "\nUNIFY FACT-ID HYGIENE (gate x2_unify_only_fact_scope checks every bullets[].source_fact_ids "
        "and claim_ledger[].source_fact_ids token):\n"
        '- Prefix must be exactly bul_unify_ with no extra underscores inside that prefix '
        '(letters u-n-i-f-y must be contiguous).\n'
        '- INVALID typo observed on real runs: bul_un_ify_NNN_metric_* '
        "(underscore between 'un' and 'ify') — fails fact-scope gate.\n"
        '- VALID metric satellites match allowed lines exactly, e.g. bul_unify_006_metric_<hash>.\n'
        "- bullets[].source_fact_ids must mirror claim_ledger[].source_fact_ids for the same bullet "
        "(same strings; no stray typo in bullets while ledger is correct).\n"
    )
    return (
        f"{allowed_block}{unify_id_hygiene}\n"
        "CANONICAL UNIFY FACTS (canonical starting bullets / fact pool — rewrite from these):\n"
        f"{fact_lines}"
    )


def _legacy_i0(runtime_payload: dict[str, Any]) -> str:
    header = runtime_payload["unify_header"]
    return (
        "# Role and Objective\n"
        "You are a senior executive resume editor for SVP Engineering and Agentic AI platform roles. "
        "Rewrite ONLY the Unify Consulting employment bullets so they are credible, specific, and targeted to the JD, "
        "target company, target title, and briefing without inventing facts.\n\n"
        "# Output Contract\n"
        "Return RAW JSON ONLY: response must begin with { and end with }. No markdown fences. No prose outside JSON.\n"
        "Top-level keys required: bullets, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, "
        "change_log, rewrite_distribution, self_check.\n\n"
        "# Read-Only Role Header\n"
        f"company={header['employer']}; title={header['title']}; "
        f"location={header['location']}; dates={header['start_date']} to {header['end_date']}.\n"
        "Never rewrite company, title, location, or dates.\n\n"
        "# Source Authority Hierarchy\n"
        "1. Candidate proof source: ONLY bul_unify_001..006 facts from the canonical base resume.\n"
        "2. Targeting context: target_title, target_company, JD, and briefing may influence emphasis and vocabulary only.\n"
        "3. JD and briefing are NOT proof of candidate experience and must not create new claims.\n"
        "4. No IBM, InsurTech, EY, education, certification, or early-career facts.\n\n"
        "# Private Drafting Process\n"
        "Think privately before writing JSON. Do not expose reasoning.\n"
        "Step 1: Identify the highest-value SVP Engineering themes in the JD/company/briefing.\n"
        "Step 2: Map each theme to supported Unify facts before wording any bullet.\n"
        "Step 3: Preserve base-resume information density and concrete mechanism nouns.\n"
        "Step 4: Draft bullets with one action/outcome spine each, then self-repair for proof, specificity, ATS fit, "
        "natural executive voice, and no JD mirroring.\n\n"
        "# Bullet Requirements\n"
        "OUTPUT: exactly 6 bullets. bullet_id MUST be bul_unify_001 through bul_unify_006, never B1/B2 aliases.\n"
        "Each bullet object: bullet_id, bullet_text, rewrite_intensity, has_metric, metric_raw, source_fact_ids.\n"
        "claim_ledger MUST list every bullet as its own ledger row.\n"
        "Each claim_ledger row MUST include claim_text as a non-null, non-empty string after trim (material prose).\n"
        "Whitespace-only claim_text is invalid.\n"
        "Every row is checked by deterministic gate x2_claim_ledger_claim_text_non_empty before X3 aggregation.\n"
        "Every source_fact_ids entry must match ALLOWED_SOURCE_FACT_IDS pinned in C0 candidate_facts exactly "
        "(character-for-character; typos such as bul_un_ify_* instead of bul_unify_* fail X2).\n"
        "DISTRIBUTION: 2 HEAVY, 3 MODERATE, 1 LIGHT_PROTECTED, max HEAVY=3, min LIGHT_PROTECTED=1.\n"
        f"Protected bullet {PROTECTED_BULLET_DEFAULT} must be LIGHT_PROTECTED and preserve $22M, 20%, 8 to 28 metrics.\n"
        "Preserve cycle-time metric in bul_unify_004: six months to three weeks.\n"
        "No first person. No em dash. No inline source tags. No generic filler. No narrative paragraph.\n"
        "No more than 4 consecutive words copied from the JD.\n\n"
        "# SVP Engineering Attention Bar\n"
        "Prefer supported language that shows platform architecture, governed runtime reliability, agentic orchestration, "
        "retrieval/evaluation discipline, enterprise delivery, commercialization, and engineering scale. "
        "Avoid vague claims like strategic leadership, innovative AI, stakeholder alignment, or business impact unless tied "
        "to specific Unify mechanisms and metrics.\n\n"
        "# Sequencing\n"
        "This bullets lane is the upstream source for unify_position_narrative_v1. Generate bullets only; do not write narrative text."
    )


def compile_unify_bullets_prompt(
    runtime_payload: dict[str, Any],
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    candidate_body = _candidate_facts_block(runtime_payload)
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=run_id,
        run_id=run_id,
        trace_root=f"unify_bullets:{run_id}",
        s0_system_preamble=slots["S0"],
        d0_fences=slots["D0"],
        e0_examples=slots["E0"],
        y0_style_preferences=slots["Y0"],
        i0_instructions=_legacy_i0(runtime_payload),
        c0_candidate_facts=EvidenceSource(
            source_type="candidate_facts",
            content=candidate_body,
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
            "Return one JSON object with rewrite_distribution HEAVY=2, MODERATE=3, LIGHT_PROTECTED=1, total=6."
        ),
        r0_response_schema=BULLETS_R0,
        render_context={"section_id": "unify_bullets"},
    )
    compiled = compile_section_prompt(assembly, section_id="unify_bullets")
    ids = list(runtime_payload.get("allowed_fact_ids") or [])
    return augment_section_compiled_with_input_authority(compiled, allowed_source_fact_ids=ids)


__all__ = ["compile_unify_bullets_prompt"]
