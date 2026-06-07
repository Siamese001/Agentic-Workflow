"""INPUT_AUTHORITY block appended to compiled section prompts (apps_rg-only)."""
from __future__ import annotations

from typing import Any, Sequence

import json
from dataclasses import replace

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_ssot import format_product_shape_prompt_block


def format_input_authority_block(
    *,
    allowed_source_fact_ids: Sequence[str],
    skills_authority_metadata: dict[str, Any] | None = None,
    include_allowed_id_list: bool = True,
) -> str:
    meta = skills_authority_metadata if isinstance(skills_authority_metadata, dict) else {}
    from apps_rg.runtime.product_evidence_authority import (
        EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        validate_evidence_authority_block,
    )

    ea = meta.get("evidence_authority") if isinstance(meta.get("evidence_authority"), dict) else {}
    if not ea:
        raise ValueError(
            f"INPUT_AUTHORITY requires evidence_authority="
            f"{EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r} with graph_ref and ledger_ref"
        )
    validate_evidence_authority_block(ea)
    from apps_rg.runtime.section_spine_terminology import INPUT_AUTHORITY_GRAPH_SUBSTRATE_LINE

    substrate = INPUT_AUTHORITY_GRAPH_SUBSTRATE_LINE
    skills_meta = skills_authority_metadata or {}
    skills_lines: list[str] = []
    if skills_meta.get("augmented_skills_graph_present"):
        skills_lines.append(
            "- SKILLS/COMPETENCY AUTHORITY (AUGMENTED SKILLS GRAPH): "
            f"{skills_meta.get('graph_ref')} — sole authority for skills/competency inputs "
            f"(version {skills_meta.get('graph_version')})"
        )
    elif str(skills_meta.get("skills_source_authority_status") or "") == "BLOCKED":
        skills_lines.append(
            "- SKILLS/COMPETENCY AUTHORITY: BLOCKED — augmented skills graph unavailable; "
            "do not treat broad_skills_ledger or candidate_fact_ledger as skills SSOT"
        )
    if skills_meta.get("legacy_skills_ledger_ref"):
        skills_lines.append(
            "- LEGACY SKILLS LEDGER (deprecated_reference only): "
            f"{skills_meta.get('legacy_skills_ledger_ref')} — not skills authority"
        )
    lines = [
        "INPUT_AUTHORITY:",
        substrate,
        *skills_lines,
        "- JD/title/company/briefing: TARGETING_INPUT only (see I0 proof_law_v1)",
        "- source_fact_ids: ALLOWED_SOURCE_FACT_IDS in C0 only",
    ]
    if include_allowed_id_list:
        lines.extend(
            [
                "",
                "ALLOWED_SOURCE_FACT_IDS (JSON array):",
                json.dumps(list(allowed_source_fact_ids), ensure_ascii=False),
            ]
        )
    return "\n".join(lines)


def _append_block_to_last_message(compiled: SectionCompiledPrompt, block: str) -> SectionCompiledPrompt:
    art = compiled.artifact
    msgs = [dict(m) for m in art.messages]
    if msgs:
        last = msgs[-1]
        prev = str(last.get("content") or "").rstrip()
        last["content"] = f"{prev}\n\n{block}" if prev else block
        msgs[-1] = last
    new_art = replace(art, messages=msgs)
    return SectionCompiledPrompt(
        section_id=compiled.section_id,
        apps_rg_prompt_template_ref=compiled.apps_rg_prompt_template_ref,
        artifact=new_art,
    )


def augment_section_compiled_with_product_shape(compiled: SectionCompiledPrompt) -> SectionCompiledPrompt:
    """Append PRODUCT_SHAPE block for generated lanes (X2-aligned bounds)."""
    if compiled.section_id not in GENERATED_LANES:
        return compiled
    block = format_product_shape_prompt_block(compiled.section_id)
    return _append_block_to_last_message(compiled, block)


def format_graph_binding_materiality_prompt_block(summary: dict[str, Any]) -> str:
    payload = summary if isinstance(summary, dict) else {}
    return (
        "GRAPH_BINDING_MATERIALITY_SUMMARY:\n"
        f"{json.dumps(payload, ensure_ascii=False, sort_keys=True)}\n"
        "Use this only to prioritize and de-duplicate C0.3 graph-backed skills; "
        "do not treat JD or briefing text as claim proof."
    )


def augment_section_compiled_with_graph_binding_materiality(
    compiled: SectionCompiledPrompt,
    *,
    runtime_payload: dict[str, Any],
) -> SectionCompiledPrompt:
    from apps_rg.runtime.c0.c03_graph_ref_policy import extract_c03_bindings_from_runtime_payload
    from apps_rg.runtime.graph_skills_utilization_scorer import (
        build_graph_binding_materiality_summary,
    )

    summary = build_graph_binding_materiality_summary(
        section_id=compiled.section_id,
        runtime_payload=runtime_payload,
        graph_bindings=extract_c03_bindings_from_runtime_payload(runtime_payload),
    )
    return _append_block_to_last_message(
        compiled,
        format_graph_binding_materiality_prompt_block(summary),
    )


def augment_section_compiled_with_input_authority(
    compiled: SectionCompiledPrompt,
    *,
    allowed_source_fact_ids: Sequence[str],
    skills_authority_metadata: dict[str, Any] | None = None,
    include_allowed_id_list: bool = True,
    runtime_payload: dict[str, Any] | None = None,
) -> SectionCompiledPrompt:
    """Return a copy of ``compiled`` with INPUT_AUTHORITY + PRODUCT_SHAPE on the last message."""
    block = format_input_authority_block(
        allowed_source_fact_ids=allowed_source_fact_ids,
        skills_authority_metadata=skills_authority_metadata,
        include_allowed_id_list=include_allowed_id_list,
    )
    out = _append_block_to_last_message(compiled, block)
    out = augment_section_compiled_with_product_shape(out)
    if runtime_payload is not None:
        from apps_rg.runtime.graph_skill_phrase_capsule import augment_section_compiled_with_skill_phrase_capsule

        out = augment_section_compiled_with_skill_phrase_capsule(out, runtime_payload=runtime_payload)
        out = augment_section_compiled_with_graph_binding_materiality(
            out,
            runtime_payload=runtime_payload,
        )
    return out


def finalize_section_compiled_with_proof_pool(
    compiled: SectionCompiledPrompt,
    *,
    runtime_payload: dict[str, Any],
) -> SectionCompiledPrompt:
    """Append INPUT_AUTHORITY using FEC bridge PA authority (not raw proof_pool_metadata)."""
    from apps_rg.runtime.product_evidence_authority import validate_compiled_prompt_story_authority
    from apps_rg.runtime.spine.c0_fec_compose import resolve_pa_proof_authority_for_compile

    ids = sorted(str(x) for x in (runtime_payload.get("allowed_fact_ids") or []))
    pp_meta, _fec = resolve_pa_proof_authority_for_compile(runtime_payload)
    proof_pool_mode_from_metadata(pp_meta if isinstance(pp_meta, dict) else None)
    skills_meta = pp_meta if isinstance(pp_meta, dict) else None
    out = augment_section_compiled_with_input_authority(
        compiled,
        allowed_source_fact_ids=ids,
        skills_authority_metadata=skills_meta,
    )
    from apps_rg.runtime.graph_skill_phrase_capsule import augment_section_compiled_with_skill_phrase_capsule

    out = augment_section_compiled_with_skill_phrase_capsule(out, runtime_payload=runtime_payload)
    out = augment_section_compiled_with_graph_binding_materiality(
        out,
        runtime_payload=runtime_payload,
    )
    last_content = ""
    if out.artifact.messages:
        last_content = str(out.artifact.messages[-1].get("content") or "")
    validate_compiled_prompt_story_authority(last_content, section_id=compiled.section_id)
    return out


def proof_pool_mode_from_metadata(metadata: dict[str, Any] | None) -> str:
    """Validate metadata; product lanes use evidence_authority (not proof_pool_type switch)."""
    from apps_rg.runtime.product_evidence_authority import (
        EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        validate_evidence_authority_block,
    )

    meta = metadata if isinstance(metadata, dict) else {}
    ea = meta.get("evidence_authority") if isinstance(meta.get("evidence_authority"), dict) else {}
    if not ea:
        raise ValueError(
            f"product lanes require evidence_authority={EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}; "
            "proof_pool_type is not an authority switch"
        )
    validate_evidence_authority_block(ea)
    return EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH


__all__ = [
    "augment_section_compiled_with_graph_binding_materiality",
    "augment_section_compiled_with_input_authority",
    "augment_section_compiled_with_product_shape",
    "finalize_section_compiled_with_proof_pool",
    "format_graph_binding_materiality_prompt_block",
    "format_input_authority_block",
    "proof_pool_mode_from_metadata",
]
