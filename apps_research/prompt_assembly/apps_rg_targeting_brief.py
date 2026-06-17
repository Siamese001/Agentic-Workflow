"""Briefing packet prompt SSOT and builder for CompanyBriefEngine."""

from __future__ import annotations

import functools
import os
from pathlib import Path

from apps_research.prompt_assembly.consumer_briefs import (
    build_consumer_brief_prompt,
    consumer_brief_prompt_path,
    extract_jd_text,
    format_research_findings,
    load_consumer_brief_prompt_template,
)

_TEMPLATE_ID = "apps_rg_targeting_brief_synthesis_v1"

APPS_RG_TARGETING_BRIEF_PROMPT_PATH: Path = consumer_brief_prompt_path(_TEMPLATE_ID)


def apps_rg_targeting_brief_enabled(*, jd_context: dict | None = None) -> bool:
    """True when synthesis should emit apps_rg targeting markdown instead of JSON CompanyBrief."""
    env = os.environ.get("APPS_RESEARCH_APPS_RG_TARGETING_BRIEF", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    if isinstance(jd_context, dict):
        fmt = str(jd_context.get("output_format") or jd_context.get("synthesis_template") or "").strip()
        if fmt in (_TEMPLATE_ID, "apps_rg_targeting_brief", "apps_rg_targeting_brief_v1"):
            return True
    return False


@functools.lru_cache(maxsize=1)
def load_targeting_brief_prompt_template() -> str:
    """UTF-8 operator prompt with {{jd_text}}, {{research_notes}}, {{target_entity}} placeholders."""
    return load_consumer_brief_prompt_template(_TEMPLATE_ID)


def build_targeting_brief_prompt(
    *,
    jd_text: str,
    research_notes: str,
    target_entity: str,
    output_profile: str = "apps_rg",
) -> str:
    """Render the SSOT prompt with JD and grounded research notes."""
    template = load_targeting_brief_prompt_template()
    return (
        template.replace("{{jd_text}}", str(jd_text or "").strip() or "(no JD text provided)")
        .replace("{{research_notes}}", str(research_notes or "").strip() or "(no research notes)")
        .replace("{{target_entity}}", str(target_entity or "").strip() or "TBD")
        .replace("{{output_profile}}", str(output_profile or "apps_rg").strip() or "apps_rg")
    )


__all__ = [
    "APPS_RG_TARGETING_BRIEF_PROMPT_PATH",
    "apps_rg_targeting_brief_enabled",
    "build_targeting_brief_prompt",
    "extract_jd_text",
    "format_research_findings",
    "load_targeting_brief_prompt_template",
]
