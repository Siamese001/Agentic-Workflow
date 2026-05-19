"""INPUT_AUTHORITY block appended to compiled section prompts (apps_rg-only)."""
from __future__ import annotations

from typing import Any, Sequence

import json
from dataclasses import replace

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt


def format_input_authority_block(
    *,
    allowed_source_fact_ids: Sequence[str],
    selected_role_fact_set_mode: bool = False,
    proof_pool_mode: str = "base_resume_fallback",
    skills_authority_metadata: dict[str, Any] | None = None,
) -> str:
    if selected_role_fact_set_mode or proof_pool_mode == "srfs":
        substrate = (
            "- CLAIM SUPPORT POOL (SRFS): SelectedRoleFactSet section slice — sole substrate for factual claims"
        )
    elif proof_pool_mode == "broad_skills_ledger":
        substrate = (
            "- CLAIM SUPPORT POOL (CANDIDATE FACT LEDGER): governed candidate_fact_id rows — "
            "sole substrate for factual claims (not skills/competency authority; see augmented skills graph)"
        )
    else:
        substrate = (
            "- CLAIM SUPPORT POOL (BASE RESUME FALLBACK): canonical employment bullets — explicit fallback; "
            "not ledger/SRFS primary"
        )
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
        "- JD_TEXT: TARGETING_INPUT (mandatory; guides prioritization and wording; not claim evidence)",
        "- TARGET_TITLE: POSITIONING_INPUT (mandatory; not claim evidence)",
        "- TARGET_COMPANY: POSITIONING_INPUT (mandatory; not claim evidence)",
        "- BRIEFING_RESEARCH: CONTEXT_INPUT (mandatory; positioning and themes; not claim evidence)",
        "",
        "Rules:",
        "- TARGETING INPUTS (NON-PROOF): JD/title/company and briefing — prioritize relevance only",
        "- source_fact_ids must come only from ALLOWED_SOURCE_FACT_IDS in the CLAIM SUPPORT POOL",
        "- JD, target title, target company, and briefing/research must never appear in source_fact_ids",
        "- If a claim cannot be supported by the CLAIM SUPPORT POOL, omit it or write conservatively",
        "- Do not invent facts to satisfy the JD",
        "- Do not turn briefing/research into resume experience",
        "",
        "ALLOWED_SOURCE_FACT_IDS (JSON array):",
        json.dumps(list(allowed_source_fact_ids), ensure_ascii=False),
    ]
    return "\n".join(lines)


def augment_section_compiled_with_input_authority(
    compiled: SectionCompiledPrompt,
    *,
    allowed_source_fact_ids: Sequence[str],
    selected_role_fact_set_mode: bool = False,
    proof_pool_mode: str = "base_resume_fallback",
    skills_authority_metadata: dict[str, Any] | None = None,
) -> SectionCompiledPrompt:
    """Return a copy of ``compiled`` with INPUT_AUTHORITY appended to the last message."""
    block = format_input_authority_block(
        allowed_source_fact_ids=allowed_source_fact_ids,
        selected_role_fact_set_mode=selected_role_fact_set_mode,
        proof_pool_mode=proof_pool_mode,
        skills_authority_metadata=skills_authority_metadata,
    )
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


def finalize_section_compiled_with_proof_pool(
    compiled: SectionCompiledPrompt,
    *,
    runtime_payload: dict[str, Any],
) -> SectionCompiledPrompt:
    """Append INPUT_AUTHORITY using runtime proof_pool_metadata when present."""
    ids = sorted(str(x) for x in (runtime_payload.get("allowed_fact_ids") or []))
    pp_meta = runtime_payload.get("proof_pool_metadata") or {}
    mode = proof_pool_mode_from_metadata(pp_meta if isinstance(pp_meta, dict) else None)
    skills_meta = pp_meta if isinstance(pp_meta, dict) else None
    return augment_section_compiled_with_input_authority(
        compiled,
        allowed_source_fact_ids=ids,
        selected_role_fact_set_mode=(mode == "srfs"),
        proof_pool_mode=mode,
        skills_authority_metadata=skills_meta,
    )


def proof_pool_mode_from_metadata(metadata: dict[str, Any] | None) -> str:
    pt = str((metadata or {}).get("proof_pool_type") or "")
    if pt == "selected_role_fact_set":
        return "srfs"
    if pt == "broad_skills_ledger":
        return "broad_skills_ledger"
    return "base_resume_fallback"


__all__ = [
    "augment_section_compiled_with_input_authority",
    "finalize_section_compiled_with_proof_pool",
    "format_input_authority_block",
    "proof_pool_mode_from_metadata",
]
