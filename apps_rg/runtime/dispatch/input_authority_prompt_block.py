"""INPUT_AUTHORITY block appended to compiled section prompts (apps_rg-only)."""
from __future__ import annotations

from typing import Sequence

import json
from dataclasses import replace

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt


def format_input_authority_block(
    *,
    allowed_source_fact_ids: Sequence[str],
    selected_role_fact_set_mode: bool = False,
) -> str:
    substrate = (
        "- SELECTED_ROLE_FACT_SET_EXECUTIVE_SLICE (from artifact): CLAIM_EVIDENCE - sole proof substrate for SelectedRoleFactSet mode executive_summary adaptive claims."
        if selected_role_fact_set_mode
        else (
            "- BASE_RESUME_SELECTED_FACTS: CLAIM_EVIDENCE after selection (only substrate for factual resume claims)"
        )
    )
    lines = [
        "INPUT_AUTHORITY:",
        substrate,
        "- JD_TEXT: TARGETING_INPUT (mandatory; guides prioritization and wording; not claim evidence)",
        "- TARGET_TITLE: POSITIONING_INPUT (mandatory; not claim evidence)",
        "- TARGET_COMPANY: POSITIONING_INPUT (mandatory; not claim evidence)",
        "- BRIEFING_RESEARCH: CONTEXT_INPUT (mandatory; positioning and themes; not claim evidence)",
        "",
        "Rules:",
        "- source_fact_ids must come only from ALLOWED_SOURCE_FACT_IDS",
        "- JD, target title, target company, and briefing/research must never appear in source_fact_ids",
        "- If a claim cannot be supported by selected base-resume facts, omit it",
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
) -> SectionCompiledPrompt:
    """Return a copy of ``compiled`` with INPUT_AUTHORITY appended to the last message."""
    block = format_input_authority_block(
        allowed_source_fact_ids=allowed_source_fact_ids,
        selected_role_fact_set_mode=selected_role_fact_set_mode,
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


__all__ = ["augment_section_compiled_with_input_authority", "format_input_authority_block"]
