"""Executive summary: build PromptAssemblyInput from runtime payload + template YAML (W4).

Loads slot bodies from ``executive_summary.generate_scratch_v1.yaml`` and compiles via
``section_prompt_adapter``. C0 carries selected_fact_plan facts (proof). The
``c0_jd_requirements`` block carries JD_TEXT + BRIEFING + target framing for **targeting
only** (rank, order, vocabulary tilt among evidenced facts) - never as proof. Style should match the
canonical base résumé register (dense, concrete stack/governance nouns), without JD
keyword-stuffing.

W11-M4B SSOT: apps_rg.runtime.sections.executive_summary_pa."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.prompt_assembly.e0_examples import example_after_text, resolve_e0_for_section
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import augment_section_compiled_with_input_authority


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (
            parent
            / "apps_rg"
            / "prompt_assembly"
            / "templates"
            / "executive_summary.generate_scratch_v1.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError(
        "Cannot resolve repo root from executive_summary_pa.py (template yaml not found in parents)"
    )


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "executive_summary.generate_scratch_v1.yaml"
)

_EXEC_SUMMARY_OUTPUT_SCHEMA_JSON = json.dumps(
    {
        "type": "object",
        "required": [
            "executive_strategy_thesis",
            "resume_display_text",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "executive_strategy_thesis": {"type": "string", "minLength": 1},
            "resume_display_text": {"type": "string"},
            "claim_ledger": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["claim_text", "source_fact_ids"],
                    "properties": {
                        "claim_text": {"type": "string", "minLength": 1},
                        "claim": {"type": "string"},
                        "source_fact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "jd_alignment": {"type": "object"},
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
    },
    sort_keys=True,
)


def load_executive_summary_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def _ordered_allowed_source_fact_ids(
    runtime_payload: dict[str, Any], facts: list[dict[str, Any]]
) -> list[str]:
    raw = runtime_payload.get("allowed_fact_ids")
    if isinstance(raw, list) and raw:
        return [str(x) for x in raw]
    out: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        fid = str(fact.get("fact_id") or "").strip()
        if fid and fid not in seen:
            seen.add(fid)
            out.append(fid)
    return out


def format_allowed_source_fact_ids_contract(allowed_ids: list[str]) -> str:
    """Dynamic allowlist + minimal copy rules (full law in I0 proof_law_v1)."""
    lines = [
        "ALLOWED_SOURCE_FACT_IDS (authoritative list; copy verbatim into every claim_ledger.source_fact_ids):",
        *[f"  - {i}" for i in allowed_ids],
        "Copy each ID character-for-character; no interior spaces in tokens.",
        "Spacing drift fails X2 (e.g. bul_unify_ 003 invalid; bul_unify_003 valid when listed).",
    ]
    return "\n".join(lines)


def is_strategy_executive_target_title(target_title: str) -> bool:
    """True when TARGET_TITLE signals IT strategy / innovation SVP-style positioning."""
    blob = str(target_title or "").strip().lower()
    if not blob:
        return False
    markers = (
        "it strategy",
        "strategy & innovation",
        "strategy and innovation",
        "technology strategy",
        "chief information",
        "cio",
        "cito",
        "enterprise architecture",
        "digital innovation",
    )
    return any(m in blob for m in markers) or (
        "svp" in blob and ("strategy" in blob or "innovation" in blob)
    )


def format_strategy_executive_targeting_appendix(target_title: str) -> str:
    """Extra U0/JD framing for SVP IT strategy lanes (targeting only — never proof)."""
    if not is_strategy_executive_target_title(target_title):
        return ""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        format_strategy_executive_u0_block,
    )

    return format_strategy_executive_u0_block(target_title=target_title)


def format_jd_targeting_block(
    *,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    srfs_mode: bool = False,
    graph_proof_pool_mode: bool | None = None,
) -> str:
    """Targeting payload only; non-proof rules live in I0 proof_law_v1."""
    graph_mode = graph_proof_pool_mode if graph_proof_pool_mode is not None else srfs_mode
    block = (
        f"TARGET_TITLE (positioning only - NOT PROOF): {target_title}\n"
        f"TARGET_COMPANY (targeting only - NOT PROOF): {target_company}\n"
        f"JD_TEXT (targeting only - NOT PROOF): {jd_text}\n"
        f"BRIEFING (targeting only - NOT PROOF): {briefing}\n"
        "Use JD_TEXT and BRIEFING to rank and frame evidenced themes only - never as proof. "
        "jd_alignment: targeting_only=true; jd_used_as_proof=false; briefing_used_as_proof=false."
    )
    if graph_mode:
        block += (
            " augmented_skills_graph proof pool filters ALLOWED_SOURCE_FACT_IDS; "
            "cite only listed IDs in claim_ledger."
        )
    return block


def _proof_pool_counts_from_payload(runtime_payload: dict[str, Any]) -> dict[str, int]:
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        pp = {}
    return {
        "blocked_facts_count": int(pp.get("blocked_facts_count") or 0),
        "facts_requiring_human_confirmation_count": int(
            pp.get("facts_requiring_human_confirmation_count") or 0
        ),
        "unsupported_jd_needs_count": int(pp.get("unsupported_jd_needs_count") or 0),
    }


def _selection_id_from_payload(runtime_payload: dict[str, Any]) -> str:
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        pp = {}
    ss = pp.get("selection_scope")
    if isinstance(ss, dict):
        sid = str(ss.get("selection_id") or "").strip()
        if sid:
            return sid
    return str(pp.get("selection_id") or "").strip()


def format_graph_proof_pool_appendix(runtime_payload: dict[str, Any]) -> str:
    """Prompt-only rules when in-memory graph projection supplies the exec proof pool."""
    ids = list(runtime_payload.get("allowed_fact_ids") or [])
    if not ids:
        plan = runtime_payload.get("selected_fact_plan") or {}
        for fact in plan.get("facts") or []:
            if isinstance(fact, dict):
                fid = str(fact.get("fact_id") or "").strip()
                if fid:
                    ids.append(fid)
    counts = _proof_pool_counts_from_payload(runtime_payload)
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        pp = {}
    sid = _selection_id_from_payload(runtime_payload)
    pool_type = str(pp.get("proof_pool_type") or "augmented_skills_graph")
    id_tail = ", ".join(str(x) for x in ids[:12])
    if len(ids) > 12:
        id_tail += ", …"
    return (
        "GRAPH_PROOF_POOL_APPENDIX:\n"
        f"- proof_pool_type: {pool_type}\n"
        "- evidence_authority: in-memory augmented_skills_graph projection (no JSON file authority)\n"
        f"- selection_id: {sid or '(in-memory)'}\n"
        f"- HIGH proof pool source_fact_ids (executive_summary slice only): [{id_tail}]\n"
        f"- Counts - blocked_facts: {counts['blocked_facts_count']}; "
        f"facts_requiring_human_confirmation: {counts['facts_requiring_human_confirmation_count']}; "
        f"unsupported_jd_needs: {counts['unsupported_jd_needs_count']}\n"
        "- These source_fact_ids are the ONLY allowable proof identifiers for substantive executive_summary claims; "
        "each claim_ledger row must cite concrete values from ALLOWED_SOURCE_FACT_IDS (verbatim).\n"
        "- JD_TEXT and BRIEFING remain targeting/context inputs only - never citations, never proof substrates; "
        "jd_alignment jd_used_as_proof must remain false.\n"
        "- Unsupported JD themes in selection metadata MUST be omitted from resume_display_text; "
        "do not fabricate JD-only needs.\n"
        "- MEDIUM, LOW, and NEEDS_VERIFICATION rows excluded from ALLOWED_SOURCE_FACT_IDS MUST NOT appear in "
        "source_fact_ids unless explicitly promoted after human confirmation.\n"
        "- Numeric evidence must still map to ledger metric-hash IDs when ALLOWED_SOURCE_FACT_IDS includes *_metric_* lines.\n"
        "- **Credential facts (e.g. fact_certs_001) are optional supporting context, not mandatory paragraph filler** "
        "(waived from utilization). Prefer platform, governance, lifecycle, and commercial facts when the "
        "six-sentence / 140-word budget is tight. "
        "Cite **every non-credential** allowed fact_id across the claim_ledger / resume_display_text -- "
        "enforced by x2_exec_summary_allowed_fact_utilization (a ledger row may carry multiple source_fact_ids).\n"
        "- **Section ownership:** named certifications (AWS, Databricks, FSA, Basel, CCAR labels, "
        "Certified …, Lakehouse …) belong primarily in **Certifications/Credentials** and **Competencies** sections. "
        "Executive summary may imply quantitative or regulated depth without enumerating credential labels.\n"
    )


def format_srfs_role_adaptive_appendix(srfs_integration: dict[str, Any]) -> str:
    """Deprecated alias: legacy SRFS dicts are ignored; callers should use format_graph_proof_pool_appendix."""
    _ = srfs_integration
    return format_graph_proof_pool_appendix({})


SRFS_STYLE_ONESHOT_MARKER = "SRFS_BASE_RESUME_STYLE_ONESHOT_V1"
SRFS_COMPOSITION_ONESHOT_MARKER = "SRFS_COMPOSITION_ONESHOT_V1"
# Legacy markers retained for grep/tooling continuity only (not emitted in SRFS appendix).
SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER = "SRFS_THREE_SENTENCE_EXEC_ARCH_V1"
SRFS_FIVE_PART_EXEC_ARCH_MARKER = "SRFS_FIVE_PART_EXEC_ARCH_V1"
SRFS_SENTENCE_RESP_SEP_MARKER = "SRFS_SENTENCE_RESP_SEP_V1"
SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER = "SRFS_FORBIDDEN_PHRASE_CONTRACT_V1"

# W4C: global resume_display_text bans (prompt contract; judge_safe may also strip at repair).
SRFS_FORBIDDEN_PHRASES_ALWAYS: tuple[str, ...] = (
    "applied depth",
    "documented credential training",
    "quantitative methods training",
    "distributed systems training",
    "fully autonomous production agents",
    "self-learning runtime",
    "autonomous AGI without oversight",
    "unsupervised production agents",
    "commercialization",
    "bespoke delivery",
    "reusable platform services adopted across enterprise programs",
    "engineering scale-out",
    "converting bespoke delivery",
)


def format_srfs_forbidden_phrase_guardrails_block() -> str:
    """SRFS-only: explicit banned phrases + fact-supported exceptions for GraphRAG/partner engineering."""
    always = ", ".join(SRFS_FORBIDDEN_PHRASES_ALWAYS)
    return (
        f'<srfs_forbidden_phrase_contract marker="{SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER}">\n'
        "**Global forbidden phrases (never emit in resume_display_text):**\n"
        f"- {always}.\n"
        "- **Unsupported GraphRAG claims:** Do not introduce GraphRAG, graph-aware retrieval, or Graph-RAG "
        "vocabulary unless **verbatim** in a selected fact claim_text for an ALLOWED_SOURCE_FACT_ID. When the "
        "allowed claim_text includes GraphRAG or graph-aware retrieval, use **only** that fact-supported wording; "
        "do not extrapolate beyond the proved claim line.\n"
        "- **Unsupported partner engineering claims:** Do not introduce partner engineering, co-sell, ISV alliance, "
        "or partner GTM vocabulary unless a selected ALLOWED_SOURCE_FACT_ID claim_text **explicitly** supports "
        "partner / alliance / GTM substance. Do not infer partner engineering from JD_TEXT or BRIEFING alone.\n"
        "- **JD/briefing non-proof:** JD_TEXT and BRIEFING are targeting-only; they **cannot** authorize GraphRAG, "
        "partner engineering, autonomous runtime, or credential-training claims without matching proof IDs.\n"
        "- **Preserve allowed fact text:** When claim_text for an ALLOWED_SOURCE_FACT_ID includes GraphRAG or partner "
        "terms, you may reuse that exact vocabulary in prose tied to that fact_id; ban **unsupported extrapolation**, "
        "not verbatim allowed-fact wording.\n"
        "</srfs_forbidden_phrase_contract>\n\n"
    )


# SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR removed 2026-05-27 — was never injected into any
# prompt path (format_srfs_style_only_quality_oneshot_block does not reference it).
# It also diverged from the YAML example (different S5 wording) creating a maintenance hazard.
# Style exemplar is now exclusively in executive_summary_examples.yaml (E0 SSOT).

def load_executive_summary_example_after(example_id: str) -> str:
    """Return the ``after`` prose for a multishot example id (style-only; not proof)."""
    return example_after_text("executive_summary", example_id)


def format_srfs_style_only_quality_oneshot_block() -> str:
    """SRFS-only compact reinforcement; style from E0 slot. X2 gates: appended PRODUCT_SHAPE only."""
    return (
        f'<srfs_style_only_oneshot marker="{SRFS_STYLE_ONESHOT_MARKER}">\n'
        f'<srfs_composition_oneshot marker="{SRFS_COMPOSITION_ONESHOT_MARKER}">\n'
        "STYLE_ONLY_NOT_PROOF - SelectedRoleFactSet reinforcement (compact).\n"
        "- Proof: C0 HIGH facts + ALLOWED_SOURCE_FACT_IDS only (pa_proof_binding_v1).\n"
        "- JD_TEXT/BRIEFING: targeting-only (pa_targeting_only_v1).\n"
        "- Product shape and X2 gate IDs: see appended PRODUCT_SHAPE (do not restate here).\n"
        "- Voice/density: use E0 many_shot_examples (judge-aligned SVP positives / negatives); do not copy exemplar metrics.\n"
        "- Arc, voice, and credential rules: I0 judge_alignment_contract (not restated here).\n"
        "- Cite every non-credential allowed fact_id (credential/cert facts are waived); document any credential omissions in gap_notes/self_check.\n"
        + format_srfs_forbidden_phrase_guardrails_block()
        + (
            "<srfs_governance_required_or_explain>\n"
            "When governance facts are in the allowlist and JD emphasizes governance: cite in claim_ledger or explain "
            "omission via self_check.srfs_governance_omission_explained=true.\n"
            "</srfs_governance_required_or_explain>\n"
            f"</srfs_composition_oneshot>\n"
            f"<!-- Retired markers (grep only): {SRFS_FIVE_PART_EXEC_ARCH_MARKER}, "
            f"{SRFS_SENTENCE_RESP_SEP_MARKER}, {SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER} -->\n"
            "</srfs_style_only_oneshot>\n"
        )
    )


def format_selected_facts_for_c0(facts: list[dict[str, Any]], allowed_source_fact_ids: list[str]) -> str:
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        FACT_C0_DISPLAY_OVERRIDES,
    )

    header = format_allowed_source_fact_ids_contract(allowed_source_fact_ids)
    prohibition_lines: list[str] = []
    fact_lines: list[str] = []
    for fact in facts:
        fid = fact.get("fact_id", "")
        # Prefer graph-node framing, then contract override, then raw claim_text.
        display_override = (
            str(fact.get("preferred_c0_display_text") or "").strip()
            or str(FACT_C0_DISPLAY_OVERRIDES.get(str(fid), "")).strip()
        )
        ct = display_override or str(fact.get("claim_text") or "").strip()
        extra = ""
        if fact.get("metric_raw"):
            extra = f" metric_raw={fact.get('metric_raw')!r}"
        if display_override:
            prohibition_lines.append(
                f"- {fid}: MUST NOT write 'derivatives pricing' or 'multi-Greek' in resume_display_text — "
                f"use the DISPLAY_OVERRIDE text below verbatim."
            )
            fact_lines.append(f"- {fid}: [DISPLAY_OVERRIDE: use exactly this text] {ct}{extra}")
        else:
            fact_lines.append(f"- {fid}: {ct}{extra}")
    parts = [header]
    if prohibition_lines:
        parts.append(
            "DISPLAY_OVERRIDE_PROHIBITIONS (ABSOLUTE — violation fails X2 gate):\n"
            + "\n".join(prohibition_lines)
        )
    parts.append("SELECTED_FACT_PLAN (proof-only; do not invent beyond these lines):\n" + "\n".join(fact_lines))
    return "\n\n".join(parts)


def build_executive_summary_assembly_input(
    runtime_payload: dict[str, Any],
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
) -> PromptAssemblyInput:
    slots = load_executive_summary_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    if not facts:
        raise ValueError("selected_fact_plan.facts is required for executive_summary PA input")

    t_title = str(runtime_payload.get("target_title") or "")
    t_company = str(runtime_payload.get("target_company") or "")
    jd = str(runtime_payload.get("jd_text") or "")
    briefing = str(runtime_payload.get("briefing") or "")

    pp_meta = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp_meta, dict):
        pp_meta = {}
    from apps_rg.runtime.product_evidence_authority import is_product_evidence_authority_active

    graph_product = is_product_evidence_authority_active(pp_meta) or bool(
        pp_meta.get("graph_skills_proof_pool")
    )
    jd_block = format_jd_targeting_block(
        target_title=t_title,
        target_company=t_company,
        jd_text=jd,
        briefing=briefing,
        graph_proof_pool_mode=True,
    )
    strategy_appendix = format_strategy_executive_targeting_appendix(t_title)
    if strategy_appendix:
        jd_block = jd_block + "\n\n" + strategy_appendix

    allowed_ids = _ordered_allowed_source_fact_ids(runtime_payload, facts)
    if not allowed_ids:
        raise ValueError("allowed_fact_ids or non-empty fact_id on each selected fact is required for executive_summary PA")
    if strategy_appendix:
        from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
            format_strategy_targeting_gap_note,
        )

        gap_note = format_strategy_targeting_gap_note(allowed_fact_ids=set(allowed_ids))
        if gap_note:
            jd_block = jd_block + "\n\n" + gap_note

    use_capsule = bool(runtime_payload.get("evidence_capsule_active"))
    cap = runtime_payload.get("evidence_capsule") if use_capsule else None
    if use_capsule and isinstance(cap, dict) and cap.get("c0_block"):
        c0_content = str(cap["c0_block"])
    else:
        c0_content = format_selected_facts_for_c0(facts, allowed_ids)

    strategy_voice = ""
    if is_strategy_executive_target_title(t_title):
        strategy_voice = " SVP lane: follow I0 judge_alignment_contract (thesis-first, six-sentence arc)."
    composition_block = ""
    _pp_for_plan = runtime_payload.get("proof_pool_metadata")
    if not isinstance(_pp_for_plan, dict):
        _pp_for_plan = {}
    from apps_rg.runtime.sections.executive_summary_composition import (
        build_executive_summary_composition_plan,
        format_composition_plan_for_pa,
    )

    _composition_plan = runtime_payload.get("executive_summary_composition_plan")
    if not isinstance(_composition_plan, dict):
        _composition_plan = build_executive_summary_composition_plan(
            selected_facts=facts,
            allowed_fact_ids=set(allowed_ids),
            target_role=t_title,
            target_company=t_company,
            proof_pool_metadata=_pp_for_plan,
            briefing_text=str(runtime_payload.get("briefing") or ""),
            jd_text=str(runtime_payload.get("jd_text") or ""),
        )
        runtime_payload["executive_summary_composition_plan"] = _composition_plan
    composition_block = format_composition_plan_for_pa(_composition_plan)
    u0 = (
        f"Task: executive summary for {t_title!r} at {t_company!r} (targeting context only).\n"
        "Proof: C0 + ALLOWED_SOURCE_FACT_IDS only. Generation law: I0 + R0; voice: E0 examples.\n"
        f"{strategy_voice}"
        "Return bare JSON per R0 (executive_strategy_thesis, resume_display_text, claim_ledger, jd_alignment, "
        "gap_notes, change_log, self_check). Do not emit selected_fact_plan."
    )
    product_patch = (
        "\nGRAPH PRODUCT HARD RULES: JD_TEXT/BRIEFING are targeting-only framing; NEVER list them "
        "(or surrogate targeting tokens such as standalone JD_/BRIEFING_ placeholders) "
        "inside claim_ledger source_fact_ids. Every ID must exactly match ALLOWED_SOURCE_FACT_IDS "
        "from the in-memory graph proof pool.\n"
    )
    if not use_capsule:
        if graph_product or facts:
            product_patch += "\n\n" + format_graph_proof_pool_appendix(runtime_payload)
        capsule = pp_meta.get("graph_targeting_capsule")
        if isinstance(capsule, dict):
            from apps_rg.runtime.c0.exec_summary_graph_targeting_capsule import (
                format_graph_targeting_capsule_for_pa,
            )

            product_patch += "\n\n" + format_graph_targeting_capsule_for_pa(capsule)
        product_patch += "\n\n" + format_srfs_style_only_quality_oneshot_block()
    if composition_block:
        product_patch += "\n\n" + composition_block
    return PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        s0_system_preamble=slots.get("S0", ""),
        d0_fences=slots.get("D0"),
        i0_instructions=slots.get("I0", "").rstrip() + "\n",
        e0_examples=resolve_e0_for_section(
            "executive_summary",
            slots.get("E0"),
            allow_template_fallback=False,
            strategy_executive=is_strategy_executive_target_title(t_title),
        ),
        y0_style_preferences=slots.get("Y0"),
        c0_candidate_facts=EvidenceSource(
            source_type="selected_facts",
            content=c0_content,
            confidence=1.0,
            source_tag="selected_facts",
        ),
        c0_jd_requirements=EvidenceSource(
            source_type="jd_requirements",
            content=jd_block,
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=u0 + product_patch,
        r0_response_schema=_EXEC_SUMMARY_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "executive_summary",
        },
    )


def format_graph_only_quality_guardrails_block() -> str:
    """Graph-substrate synthesis guards (metrics/causality); shape law remains in I0."""
    return (
        "<graph_only_generation_quality>\n"
        "Graph path: metrics only from fact lines; no invented revenue/margin/%. "
        "No cross-fact causality unless one fact states it; graph edges are not proof. "
        "Claim ledger: emit exactly one row per displayed sentence (one-to-one; 6 rows for the S1-S6 summary), "
        "each tracing to an allowed fact -- enforced by x2_claim_ledger_row_count_matches_sentence_count; "
        "credentials woven or omitted (see I0 credential_policy_v1).\n"
        "</graph_only_generation_quality>"
    )


def _proof_pool_metadata_for_compile(runtime_payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    from apps_rg.runtime.c0.product_runtime_guards import product_fec_bridge_mandatory
    from apps_rg.runtime.spine.c0_fec_compose import (
        assert_section_pa_fec_preconditions,
        resolve_pa_proof_authority_for_compile,
    )

    if not product_fec_bridge_mandatory():
        return dict(runtime_payload.get("proof_pool_metadata") or {}), False
    if runtime_payload.get("section_fec_bridge") or runtime_payload.get("canonical_final_evidence_contract"):
        return resolve_pa_proof_authority_for_compile(runtime_payload)
    if not bool(runtime_payload.get("product_visible", True)):
        return dict(runtime_payload.get("proof_pool_metadata") or {}), False
    assert_section_pa_fec_preconditions(runtime_payload)
    return resolve_pa_proof_authority_for_compile(runtime_payload)


def compile_executive_summary_prompt(runtime_payload: dict[str, Any], *, run_id: str) -> SectionCompiledPrompt:
    assembly = build_executive_summary_assembly_input(
        runtime_payload,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"exec_summary:{run_id}",
    )
    compiled = compile_section_prompt(assembly, section_id="executive_summary")
    from apps_rg.runtime.spine.governed_pa_compose import stamp_section_governed_pa_receipt

    stamp_section_governed_pa_receipt(runtime_payload, compiled)
    ids = list(runtime_payload.get("allowed_fact_ids") or [])
    pp, _fec_consumed = _proof_pool_metadata_for_compile(runtime_payload)
    from apps_rg.runtime.dispatch.input_authority_prompt_block import proof_pool_mode_from_metadata

    product_visible = bool(runtime_payload.get("product_visible"))
    if product_visible:
        proof_pool_mode_from_metadata(pp if isinstance(pp, dict) else None)
    ea = pp.get("evidence_authority") if isinstance(pp.get("evidence_authority"), dict) else {}
    use_product_input_authority = product_visible and bool(str(ea.get("authority") or "").strip())
    from apps_rg.runtime.dispatch.input_authority_prompt_block import (
        augment_section_compiled_with_input_authority,
        augment_section_compiled_with_product_shape,
    )

    if use_product_input_authority:
        compiled = augment_section_compiled_with_input_authority(
            compiled,
            allowed_source_fact_ids=ids,
            skills_authority_metadata=pp if isinstance(pp, dict) else None,
            include_allowed_id_list=False,
            runtime_payload=runtime_payload,
        )
    else:
        compiled = augment_section_compiled_with_product_shape(compiled)
    graph_guard = format_graph_only_quality_guardrails_block()
    forbidden_guard = format_srfs_forbidden_phrase_guardrails_block()
    art = compiled.artifact
    msgs = [dict(m) for m in art.messages]
    if msgs:
        last = msgs[-1]
        content = str(last.get("content") or "").rstrip()
        if SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER not in content:
            content = f"{content}\n\n{forbidden_guard}".rstrip()
        last["content"] = f"{content}\n\n{graph_guard}".rstrip() + "\n"
        msgs[-1] = last
    compiled = SectionCompiledPrompt(
        section_id=compiled.section_id,
        apps_rg_prompt_template_ref=compiled.apps_rg_prompt_template_ref,
        artifact=replace(art, messages=msgs),
    )
    return compiled


__all__ = [
    "SRFS_COMPOSITION_ONESHOT_MARKER",
    "SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER",
    "SRFS_FORBIDDEN_PHRASES_ALWAYS",
    "SRFS_STYLE_ONESHOT_MARKER",
    "SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER",
    "SRFS_FIVE_PART_EXEC_ARCH_MARKER",
    "SRFS_SENTENCE_RESP_SEP_MARKER",
    "load_executive_summary_example_after",
    "build_executive_summary_assembly_input",
    "compile_executive_summary_prompt",
    "format_srfs_forbidden_phrase_guardrails_block",
    "format_graph_proof_pool_appendix",
    "format_srfs_role_adaptive_appendix",
    "format_srfs_style_only_quality_oneshot_block",
    "format_graph_only_quality_guardrails_block",
    "format_jd_targeting_block",
    "load_executive_summary_template_slots",
]
