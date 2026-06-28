"""IBM bullets: PA compile via section_prompt_adapter.

W1 (Bullet Proof Bundle Redesign): IBM now uses ORGANIC_FROM_GRAPH_BUNDLE treatment.
C0 emits GRAPH_BULLET_EVIDENCE_PACK with bound_skills + proof_atoms (mechanism_vocab,
locked_metrics, domain). claim_text prose is never injected into C0.

W11-M4B SSOT: apps_rg.runtime.sections.ibm_bullets_pa."""

from __future__ import annotations

from typing import Any

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.prompt_assembly.e0_examples import resolve_e0_for_section
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import finalize_section_compiled_with_proof_pool
from apps_rg.runtime.dispatch.unify_ibm_pa_common import (
    BULLETS_R0,
    load_w7_shell_slot_bodies,
)
from apps_rg.runtime.sections.executive_summary_pa import format_jd_targeting_block
from apps_rg.runtime.sections.ibm_role_episode_evidence import (
    IBM_ROLE_EPISODE_EVIDENCE_MARKER,
    format_ibm_role_episode_evidence_pack,
)

GRAPH_BULLET_EVIDENCE_PACK_MARKER = IBM_ROLE_EPISODE_EVIDENCE_MARKER


def _legacy_i0(runtime_payload: dict[str, Any]) -> str:
    header = runtime_payload["ibm_header"]
    return (
        "<!-- UNIFY_IBM_PROMPT_CORE_LAW_V3 — section I0; X2 gate IDs in PRODUCT_SHAPE only -->\n\n"
        "# Role\n"
        f"Compose five IBM employment bullets for enterprise AI platform targets "
        f"from {GRAPH_BULLET_EVIDENCE_PACK_MARKER} (graph-bound skills + structured proof atoms). "
        "Proof and targeting: pa_proof_binding_v1 + pa_targeting_only_v1 (pa_core_law_v1.yaml). "
        "C0 bul_ibm_001..005 only; no Unify, InsurTech, EY, education, certification, or early-career facts. "
        "Base resume JSON is not in C0 — do not copy or paraphrase prior IBM bullet wording.\n\n"
        "# Output\n"
        "RAW JSON only ({ ... }); required keys: bullets, selected_fact_plan, claim_ledger, jd_alignment, "
        "gap_notes, change_log, self_check.\n\n"
        "# Read-only header\n"
        f"company={header['employer']}; title={header['title']}; location={header['location']}; "
        f"dates={header['start_date']} to {header['end_date']}. Never rewrite header fields.\n\n"
        "# Bullets\n"
        "Exactly 5 bullets; bullet_id bul_ibm_001..bul_ibm_005 (never B1/B2). "
        "Each bullet: bullet_id, bullet_text, has_metric, metric_raw, source_fact_ids. "
        "Organic generation: bullet_text must be newly written executive prose from bound_skills + "
        "proof_atoms only — do not reuse IBM base-resume bullet templates. "
        "Authenticity: material claims bind to allowed_source_fact_ids; use bound_skills allowed_phrases "
        "only when supported by linked ledger facts. "
        "claim_ledger: one row per bullet; claim_text non-empty after trim; source_fact_ids must match "
        "ALLOWED_SOURCE_FACT_IDS exactly.\n"
        "POOL: each PROVIDER_MODEL path emits a full 5-bullet set with semantically distinct framing; "
        "Claude selector picks best variant per bul_ibm_* slot. "
        "Metrics are expected when the graph supplies differentiated allowed_metric_outcome_ids; "
        "do not under-surface approved graph metrics. Metrics allowed only when bound to "
        "allowed_metric_outcome_ids from role episode bundles. Approved IBM metric examples include "
        "metric_ibm_20pct_joint_revenue_growth, metric_ibm_stress_test_cycle_weeks_to_hours, "
        "metric_ibm_budget_portfolio_bi_views, and metric_ibm_value_realization_account_reviews. "
        "Forbidden: unapproved held-value, overload, ARR, or generic cost-savings metrics.\n"
        "METRIC SURFACING (PROMOTABLE metrics only): when a bullet's selected_fact_plan fact has "
        "has_metric=true AND its metric binds a promotable metric_outcome_id, the bullet_text MUST "
        "literally include that metric token, inside the SAME single sentence (never append the metric "
        "as a second sentence). Do NOT write a qualitative bullet that drops its own approved metric. "
        "Example: a slot bound to metric_ibm_20pct_joint_revenue_growth must state '20%'; "
        "a slot bound to metric_ibm_stress_test_cycle_weeks_to_hours must state 'weeks to hours'. "
        "This rule NEVER applies to forbidden/HOLD figures: even if a fact carries one, "
        "write that bullet qualitatively with NO numeric figure. "
        "Mirror promotable metric_raw figures exactly; set has_metric=true and bind metric_outcome_ids.\n"
        "GATED-METRIC BAN: NEVER emit a metric whose outcome_id is only *_gated / unconfirmed. "
        "If a savings/efficiency figure is not bound to a confirmed promotable metric_outcome_id, "
        "write that bullet qualitatively with NO numeric figure.\n"
        "PER-SLOT COMPOSITION BINDING: each bul_ibm_NNN bullet_text MUST restate the core activity of "
        "ITS OWN graph_bundle_story from IBM_ROLE_EPISODE_EVIDENCE_PACK. NEVER borrow another "
        "slot's activity, technology, or metric; "
        "NEVER lift a metric from SKILL_PHRASE_CAPSULE guidance — capsule phrases are vocabulary, not claims. "
        "EXACTLY ONE sentence per bullet (one terminal period at the very end — never two sentences). "
        "Every bullet names at least one concrete mechanism, platform, or technology. "
        "No first person; no em dash; no inline source tags; no narrative paragraph; max 4 consecutive JD words. "
        "Cite ONLY bul_ibm_* ids — never reference any non-IBM id anywhere in the output (bullets, claim_ledger, "
        "selected_fact_plan, or change_log): not bul_unify_*, bul_insurtech_*, bul_ey_*, nor "
        "fact_engineering_platform_* (those are Unify facts).\n\n"
        "# Positioning\n"
        "IBM story (career-phase truth): cloud modernization, AWS/hyperscaler engineering, ML/analytics "
        "solutioning, AND pre-sales/GTM solution leadership — the IBM phase blends platform delivery with "
        "commercial engagement (technical pre-sales, client portfolio growth, alliance "
        "revenue). Write each bullet to ITS OWN slot fact's story: a GTM/pre-sales fact yields a "
        "commercial-engineering bullet (do NOT recast it as pure platform delivery); a platform fact yields "
        "a platform bullet. Regulatory lineage (Basel/CCAR) belongs to the EY phase — NOT the IBM story. "
        "NOT the Unify agentic-platform story either.\n"
        "Forbidden Unify/runtime vocab: agentic runtime, agentic AI, GraphRAG, multi-agent orchestration, "
        "judge mesh, governed spine, deterministic routing, sandboxed execution, replayable traces, "
        "governed AI runtime, prompt assembly, C0, L2, Exit, UWG.\n\n"
        "# Targeting (U0 / JD block)\n"
        "Use JD_TEXT and BRIEFING to choose emphasis, ordering, and which bound_skills to foreground — "
        "not to invent employers, tools, platforms, or metrics. "
        "jd_alignment must include selected_jd_themes[], selected_briefing_themes[], targeting_rationale, "
        "targeting_only=true, jd_used_as_proof=false, briefing_used_as_proof=false.\n"
        "change_log: per bullet_id include role_episode_bundle_id, graph_skill_node_ids[], "
        "fact_ids_used[], and metric_outcome_ids[] when has_metric=true.\n"
        "self_check: bullets_composed_from_role_episode_bundles=true, "
        "no_verbatim_base_resume_copy=true, no_archive_prose_copy=true."
    )


def _jd_targeting_block(runtime_payload: dict[str, Any]) -> str:
    return format_jd_targeting_block(
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        jd_text=str(runtime_payload.get("jd_text") or ""),
        briefing=str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or ""),
        graph_proof_pool_mode=True,
    )


def compile_ibm_bullets_prompt(
    runtime_payload: dict[str, Any],
    *,
    run_id: str,
) -> SectionCompiledPrompt:
    slots = load_w7_shell_slot_bodies()
    c0_body = format_ibm_role_episode_evidence_pack(runtime_payload, section_id="ibm_bullets")
    assembly = PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=run_id,
        run_id=run_id,
        trace_root=f"ibm_bullets:{run_id}",
        s0_system_preamble=slots["S0"],
        d0_fences=slots["D0"],
        e0_examples=resolve_e0_for_section("ibm_bullets", slots.get("E0")),
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
            content=_jd_targeting_block(runtime_payload),
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=(
            f"Synthesize exactly five IBM bullets (bul_ibm_001..005) by composing proof from "
            f"{GRAPH_BULLET_EVIDENCE_PACK_MARKER} and bound_skills. "
            "Use TARGET_TITLE, JD_TEXT, and BRIEFING only for emphasis and ordering — not as proof. "
            "Return one JSON object with bullets[5], complete claim_ledger, jd_alignment (themes + "
            "targeting_only flags), change_log with graph_skill_node_ids/fact_ids_used per slot, and self_check."
        ),
        r0_response_schema=BULLETS_R0,
        render_context={"section_id": "ibm_bullets"},
    )
    compiled = compile_section_prompt(assembly, section_id="ibm_bullets")
    return finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)


__all__ = ["compile_ibm_bullets_prompt"]
