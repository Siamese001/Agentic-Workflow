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
from apps_rg.runtime.sections.unify_bullets_graph_evidence import GRAPH_BULLET_EVIDENCE_PACK_MARKER


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

    pp_meta = runtime_payload.get("proof_pool_metadata") if isinstance(runtime_payload.get("proof_pool_metadata"), dict) else {}
    if not pp_meta.get("role_episode_bundle_consumption"):
        raise ValueError(
            "unify_bullets: proof_pool_metadata missing role_episode_bundle_consumption; graph packet is mandatory"
        )
    if not pp_meta.get("unify_role_episode_section_packet"):
        raise ValueError(
            "unify_bullets: proof_pool_metadata missing unify_role_episode_section_packet; graph packet is mandatory"
        )

    from apps_rg.runtime.sections.unify_role_episode_evidence import (
        format_unify_role_episode_evidence_pack,
    )

    return (
        f"{allowed_block}{_unify_id_hygiene_block()}\n\n"
        + format_unify_role_episode_evidence_pack(runtime_payload, section_id="unify_bullets")
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
        "LENGTH: bullet_text is ONE sentence of AT MOST 300 characters including spaces "
        "(hard cap — any bullet over 320 characters is rejected as a paragraph block; keep it tight). "
        "Organic generation: bullet_text must be newly written executive prose from bound_skills + "
        "proof_atoms only — do not reuse legacy base-resume bullet templates. "
        "Authenticity: material claims bind to allowed_source_fact_ids; use bound_skills allowed_phrases "
        "only when supported by linked ledger facts. "
        "claim_ledger: one row per bullet; claim_text non-empty after trim; source_fact_ids must match "
        "ALLOWED_SOURCE_FACT_IDS exactly (see C0 hygiene — bul_un_ify_* typos fail fact-scope).\n"
        "POOL: each Qwen path emits a full 6-bullet set with semantically distinct framing; "
        "Claude selector picks best variant per slot. "
        "Each slot must use the slot-specific metric_outcome_usage_contract from C0: select at least "
        "one approved metric_outcome_id from that role_episode_bundle, surface its metric/surface_tokens "
        "in bullet_text, set metric_raw to the selected metric_outcome_id(s), and record the same IDs in "
        "change_log.metric_outcome_ids[]. Numeric claims are allowed only when the selected metric_outcome_id "
        "explicitly supplies that number; otherwise use graph-native qualitative outcome surfaces.\n"
        "No first person; no em dash; no inline source tags; no narrative paragraph; max 4 consecutive JD words. "
        "Cite ONLY bul_unify_* source ids — never reference other employers' ids (bul_ibm_*, bul_insurtech_*, "
        "bul_ey_*) anywhere in the output (bullets, claim_ledger, selected_fact_plan, or change_log).\n\n"
        "# Targeting (U0 / JD block)\n"
        "Use JD_TEXT and BRIEFING to choose emphasis, ordering, and which bound_skills to foreground — "
        "not to invent employers, tools, platforms, or metrics. "
        "jd_alignment must include selected_jd_themes[], selected_briefing_themes[], targeting_rationale, "
        "targeting_only=true, jd_used_as_proof=false, briefing_used_as_proof=false.\n"
        "change_log: per bullet_id include role_episode_bundle_id, skill_ids_used[] or graph_skill_node_ids[], "
        "fact_ids_used[] or source_fact_ids[], and metric_outcome_ids[] (composition trace, not rewrite notes).\n"
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
            "Every bullet must carry one approved slot metric_outcome_id, visibly surface that outcome "
            "in bullet_text, and record it in change_log.metric_outcome_ids. "
            "Return one JSON object with bullets[6], complete claim_ledger, jd_alignment (themes + "
            "targeting_only flags), change_log with role_episode_bundle_id/skill_ids_used/"
            "fact_ids_used/metric_outcome_ids per slot, and self_check."
        ),
        r0_response_schema=BULLETS_R0,
        render_context={"section_id": "unify_bullets"},
    )
    compiled = compile_section_prompt(assembly, section_id="unify_bullets")
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_unify_bullets_prompt"]
