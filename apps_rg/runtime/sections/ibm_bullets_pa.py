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
from apps_rg.runtime.sections.ibm_bullets_graph_evidence import (
    GRAPH_BULLET_EVIDENCE_PACK_MARKER,
    format_ibm_graph_bullet_evidence_pack,
)


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
        "POOL: each Qwen path emits a full 5-bullet set with semantically distinct framing; "
        "Claude selector picks best variant per bul_ibm_* slot. "
        "Preserve locked_metrics from proof_atoms per slot "
        "(bul_ibm_001: 99.9% uptime; bul_ibm_002: 30% overhead; bul_ibm_003: 25% renewal; "
        "bul_ibm_004: 50% latency; bul_ibm_005: $15M).\n"
        "No first person; no em dash; no inline source tags; no narrative paragraph; max 4 consecutive JD words.\n\n"
        "# Positioning\n"
        "IBM story: enterprise AI/data platform, cloud modernization, reusable platform patterns, "
        "lineage/observability/regulatory response, hyperscaler leverage — NOT Unify agentic-platform story.\n"
        "Forbidden Unify/runtime vocab: agentic runtime, agentic AI, GraphRAG, multi-agent orchestration, "
        "judge mesh, governed spine, deterministic routing, sandboxed execution, replayable traces, "
        "governed AI runtime, prompt assembly, C0, L2, Exit, UWG.\n\n"
        "# Targeting (U0 / JD block)\n"
        "Use JD_TEXT and BRIEFING to choose emphasis, ordering, and which bound_skills to foreground — "
        "not to invent employers, tools, platforms, or metrics. "
        "jd_alignment must include selected_jd_themes[], selected_briefing_themes[], targeting_rationale, "
        "targeting_only=true, jd_used_as_proof=false, briefing_used_as_proof=false.\n"
        "change_log: per bullet_id include graph_skill_node_ids[] and fact_ids_used[] "
        "(composition trace — which proof bundle skills and atoms were drawn upon).\n"
        "self_check: bullets_composed_from_graph_evidence=true, no_verbatim_base_resume_copy=true."
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
    c0_body = format_ibm_graph_bullet_evidence_pack(runtime_payload)
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
