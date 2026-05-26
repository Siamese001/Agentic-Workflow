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
    format_jd_targeting_block,
)
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    BULLETS_R0,
    load_w7_shell_slot_bodies,
)
from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
    GRAPH_BULLET_EVIDENCE_PACK_MARKER,
    format_unify_graph_bullet_evidence_pack,
)
from apps_rg.runtime.validators.unify_bullets_x2 import PROTECTED_BULLET_DEFAULT


def _unify_id_hygiene_block() -> str:
    return (
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


def _candidate_facts_block(runtime_payload: dict[str, Any]) -> str:
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    allowed_ids_list = _ordered_allowed_source_fact_ids(runtime_payload, facts)
    allowed_block = format_allowed_source_fact_ids_contract(allowed_ids_list)
    return format_unify_graph_bullet_evidence_pack(
        runtime_payload,
        allowed_block=allowed_block,
        unify_id_hygiene=_unify_id_hygiene_block(),
    )


def _jd_targeting_block(runtime_payload: dict[str, Any]) -> str:
    return format_jd_targeting_block(
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        jd_text=str(runtime_payload.get("jd_text") or ""),
        briefing=str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or ""),
        graph_proof_pool_mode=True,
    )


def _legacy_i0(runtime_payload: dict[str, Any]) -> str:
    header = runtime_payload["unify_header"]
    return (
        "<!-- UNIFY_IBM_PROMPT_CORE_LAW_V3 — section I0; X2 gate IDs in PRODUCT_SHAPE only -->\n\n"
        "# Role\n"
        "Compose six Unify Consulting employment bullets for SVP Engineering / Agentic AI platform targets "
        f"from {GRAPH_BULLET_EVIDENCE_PACK_MARKER} (graph-bound skills + fact atoms). "
        "Proof and targeting: pa_proof_binding_v1 + pa_targeting_only_v1 (pa_core_law_v1.yaml). "
        "C0 bul_unify_001..006 only; no IBM, InsurTech, EY, education, certification, or early-career facts. "
        "Base resume JSON is not in C0 — do not seek parity with prior bullet wording.\n\n"
        "# Output\n"
        "RAW JSON only ({ ... }); required keys: bullets, selected_fact_plan, claim_ledger, jd_alignment, "
        "gap_notes, change_log, self_check.\n\n"
        f"# Read-only header\n"
        f"company={header['employer']}; title={header['title']}; location={header['location']}; "
        f"dates={header['start_date']} to {header['end_date']}. Never rewrite header fields.\n\n"
        "# Bullets\n"
        "Exactly 6 bullets; bullet_id bul_unify_001..bul_unify_006 (never B1/B2). "
        "Each bullet: bullet_id, bullet_text, has_metric, metric_raw, source_fact_ids. "
        "Organic generation: bullet_text must be newly written executive prose — no sentence with "
        "≥8 consecutive words from C0 archive_reference_only lines. "
        "Authenticity: material claims bind to allowed_source_fact_ids; use bound_skills allowed_phrases "
        "only when supported by linked ledger facts. "
        "claim_ledger: one row per bullet; claim_text non-empty after trim; source_fact_ids must match "
        "ALLOWED_SOURCE_FACT_IDS exactly (see C0 hygiene — bul_un_ify_* typos fail fact-scope).\n"
        "POOL: each Qwen path emits a full 6-bullet set with semantically distinct framing; "
        "Claude selector picks best variant per slot "
        f"(protected {PROTECTED_BULLET_DEFAULT}: preserve $22M, 20%, 8 to 28). "
        "Preserve bul_unify_004 cycle-time: six months to three weeks.\n"
        "No first person; no em dash; no inline source tags; no narrative paragraph; max 4 consecutive JD words.\n\n"
        "# Targeting (U0 / JD block)\n"
        "Use JD_TEXT and BRIEFING to choose emphasis, ordering, and which bound_skills to foreground — "
        "not to invent employers, tools, platforms, or metrics. "
        "jd_alignment must include selected_jd_themes[], selected_briefing_themes[], targeting_rationale, "
        "targeting_only=true, jd_used_as_proof=false, briefing_used_as_proof=false.\n"
        "change_log: per bullet_id include skill_ids_used[] and fact_ids_used[] (composition trace, not rewrite notes).\n"
        "self_check: bullets_composed_from_graph_evidence=true, no_verbatim_archive_copy=true.\n\n"
        "# Quality\n"
        "Distinct executive outcomes per bullet; dense mechanism inventory in at most one bullet "
        "(no comma-stack of routing/orchestration/GraphRAG/gating/traces across bullets). "
        "SKILL_PHRASE_CAPSULE is lexical guidance only — supplements bound_skills, not proof. "
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
            content=_jd_targeting_block(runtime_payload),
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=(
            "Synthesize exactly six Unify bullets (bul_unify_001..006) by composing proof from "
            f"{GRAPH_BULLET_EVIDENCE_PACK_MARKER} and bound_skills. "
            "Use TARGET_TITLE, JD_TEXT, and BRIEFING only for emphasis and ordering — not as proof. "
            "Return one JSON object with bullets[6], complete claim_ledger, jd_alignment (themes + "
            "targeting_only flags), change_log with skill_ids_used/fact_ids_used per slot, and self_check."
        ),
        r0_response_schema=BULLETS_R0,
        render_context={"section_id": "unify_bullets"},
    )
    compiled = compile_section_prompt(assembly, section_id="unify_bullets")
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_unify_bullets_prompt"]
