"""IBM bullets: PA compile via section_prompt_adapter (W7 mechanical).

W11-M4B SSOT: apps_rg.runtime.sections.ibm_bullets_pa."""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool
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


def _allowed_source_fact_ids_block(runtime_payload: dict[str, Any]) -> str:
    raw = runtime_payload.get("allowed_fact_ids") or []
    if not raw:
        return ""
    ordered = sorted(str(x) for x in raw)
    return (
        "ALLOWED_SOURCE_FACT_IDS (authoritative list — claim_ledger.source_fact_ids must cite only these IDs):\n"
        + "\n".join(f"- {fid}" for fid in ordered)
    )


def _legacy_i0(runtime_payload: dict[str, Any]) -> str:
    header = runtime_payload["ibm_header"]
    return (
        "<!-- UNIFY_IBM_PROMPT_CORE_LAW_V3 — section I0; X2 gate IDs in PRODUCT_SHAPE only -->\n\n"
        "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1 — REWRITE_FROM_FACT_POOL_CONSTRAINED.\n"
        "Proof and targeting: pa_proof_binding_v1 + pa_targeting_only_v1 (pa_core_law_v1.yaml).\n"
        "RAW JSON only ({ ... }); keys: bullets, selected_fact_plan, claim_ledger, jd_alignment, "
        "gap_notes, change_log, rewrite_distribution, self_check.\n\n"
        f"Read-only header: company={header['employer']}; title={header['title']}; "
        f"location={header['location']}; dates={header['start_date']} to {header['end_date']}.\n\n"
        "Positioning: enterprise AI/data platform, cloud modernization, reusable platform patterns, "
        "lineage/observability/regulatory response, hyperscaler leverage — NOT Unify agentic-platform story.\n\n"
        "Scope: bul_ibm_001..005 only; no Unify, InsurTech, EY, education, certification, early-career.\n"
        "Exactly 5 bullets (bul_ibm_001..005); optional bullet_theme only (never prefix bullet_text with taxonomy labels).\n"
        "claim_ledger row per bullet; non-empty claim_text; include bul_ibm_*_metric_* when metrics cited.\n"
        "DISTRIBUTION: HEAVY=0, MODERATE=3, LIGHT_PROTECTED=2. Preserve metrics as tokens: $15M, 99.9%, 30%, 25%, 50%.\n"
        "Forbidden Unify/runtime vocab: agentic runtime, agentic AI, GraphRAG, multi-agent orchestration, "
        "judge mesh, governed spine, deterministic routing, sandboxed execution, replayable traces, "
        "governed AI runtime, prompt assembly, C0, L2, Exit, UWG.\n"
        "No first person; no em dash; no inline source tags."
    )


def compile_ibm_bullets_prompt(
    runtime_payload: dict[str, Any],
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    fact_lines = _fact_lines(runtime_payload)
    allowed_block = _allowed_source_fact_ids_block(runtime_payload)
    c0_parts = ["CANONICAL IBM FACTS:\n" + fact_lines]
    if allowed_block:
        c0_parts.append(allowed_block)
    c0_body = "\n\n".join(c0_parts)
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
            content=c0_body,
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
            "Return one JSON object for IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1: "
            "rewrite_distribution HEAVY=0, MODERATE=3, LIGHT_PROTECTED=2, total=5; "
            "no taxonomy label prefixes on bullet_text; themes only in bullet_theme/metadata."
        ),
        r0_response_schema=BULLETS_R0,
        render_context={"section_id": "ibm_bullets"},
    )
    compiled = compile_section_prompt(assembly, section_id="ibm_bullets")
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_ibm_bullets_prompt"]
