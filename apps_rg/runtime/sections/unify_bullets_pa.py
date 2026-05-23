"""Unify bullets: PA compile via section_prompt_adapter (W7 mechanical).

W11-M4B SSOT: apps_rg.runtime.sections.unify_bullets_pa."""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.prompt_assembly.e0_examples import resolve_e0_for_section
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool
from apps_rg.runtime.sections.executive_summary_pa import (
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
        "\nUNIFY FACT-ID HYGIENE (fact-scope checks every bullets[].source_fact_ids "
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
        "<!-- UNIFY_IBM_PROMPT_CORE_LAW_V3 — section I0; X2 gate IDs in PRODUCT_SHAPE only -->\n\n"
        "# Role\n"
        "Rewrite ONLY Unify Consulting employment bullets for SVP Engineering / Agentic AI platform targets. "
        "Proof and targeting: pa_proof_binding_v1 + pa_targeting_only_v1 (pa_core_law_v1.yaml). "
        "C0 bul_unify_001..006 only; no IBM, InsurTech, EY, education, certification, or early-career facts.\n\n"
        "# Output\n"
        "RAW JSON only ({ ... }); required keys: bullets, selected_fact_plan, claim_ledger, jd_alignment, "
        "gap_notes, change_log, rewrite_distribution, self_check.\n\n"
        f"# Read-only header\n"
        f"company={header['employer']}; title={header['title']}; location={header['location']}; "
        f"dates={header['start_date']} to {header['end_date']}. Never rewrite header fields.\n\n"
        "# Bullets\n"
        "Exactly 6 bullets; bullet_id bul_unify_001..bul_unify_006 (never B1/B2). "
        "Each bullet: bullet_id, bullet_text, rewrite_intensity, has_metric, metric_raw, source_fact_ids. "
        "claim_ledger: one row per bullet; claim_text non-empty after trim; source_fact_ids must match "
        "ALLOWED_SOURCE_FACT_IDS exactly (see C0 hygiene — bul_un_ify_* typos fail fact-scope).\n"
        "DISTRIBUTION: HEAVY=2, MODERATE=3, LIGHT_PROTECTED=1 — "
        "001 MODERATE; 002 MODERATE; 003 HEAVY; 004 MODERATE (metric-anchored, not HEAVY); 005 HEAVY; "
        f"006 LIGHT_PROTECTED (protected {PROTECTED_BULLET_DEFAULT}: preserve $22M, 20%, 8 to 28). "
        "Preserve bul_unify_004 cycle-time: six months to three weeks.\n"
        "No first person; no em dash; no inline source tags; no narrative paragraph; max 4 consecutive JD words.\n\n"
        "# Quality\n"
        "Distinct executive outcomes per bullet; dense mechanism inventory in at most one HEAVY bullet "
        "(no comma-stack of routing/orchestration/GraphRAG/gating/traces across bullets). "
        "Upstream for unify_position_narrative — bullets only."
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
        e0_examples=resolve_e0_for_section("unify_bullets", slots.get("E0")),
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
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_unify_bullets_prompt"]
