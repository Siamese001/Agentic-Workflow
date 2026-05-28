"""apps_rg targeting brief prompt SSOT and builder for CompanyBriefEngine."""

from __future__ import annotations

import functools
import json
import os
from pathlib import Path

_PROMPT_FILE = (
    Path(__file__).resolve().parents[1] / "config" / "prompts" / "apps_rg_targeting_brief_v1.md"
)
_TEMPLATE_ID = "apps_rg_targeting_brief_synthesis_v1"

APPS_RG_TARGETING_BRIEF_PROMPT_PATH: Path = _PROMPT_FILE


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
    return _PROMPT_FILE.read_text(encoding="utf-8")


def build_targeting_brief_prompt(
    *,
    jd_text: str,
    research_notes: str,
    target_entity: str,
) -> str:
    """Render the SSOT prompt with JD and grounded research notes."""
    template = load_targeting_brief_prompt_template()
    return (
        template.replace("{{jd_text}}", str(jd_text or "").strip() or "(no JD text provided)")
        .replace("{{research_notes}}", str(research_notes or "").strip() or "(no research notes)")
        .replace("{{target_entity}}", str(target_entity or "").strip() or "TBD")
    )


def format_research_findings(findings: dict[str, str], *, max_chars: int = 12000) -> str:
    """Flatten Tavily/C0 family blobs into a single research block for the prompt."""
    parts: list[str] = []
    for family, blob in findings.items():
        text = str(blob or "").strip()
        if not text:
            continue
        parts.append(f"### {family}\n{text[:2000]}")
    joined = "\n\n".join(parts)
    if len(joined) <= max_chars:
        return joined
    return joined[: max_chars - 3] + "..."


def extract_jd_text(
    *,
    jd_context: dict | None,
    jd_anchor: Path | None = None,
) -> str:
    """Resolve full JD body from jd_context or jd_anchor file."""
    if isinstance(jd_context, dict):
        for key in ("content", "jd_text", "body_text", "description", "job_description_text"):
            val = str(jd_context.get(key) or "").strip()
            if val:
                return val
        jd_ref = str(jd_context.get("jd_ref") or "").strip()
        if jd_ref:
            p = Path(jd_ref)
            if p.is_file():
                try:
                    return p.read_text(encoding="utf-8").strip()
                except OSError:
                    pass
    if jd_anchor and jd_anchor.is_file():
        try:
            raw = jd_anchor.read_text(encoding="utf-8").strip()
            if raw.lstrip().startswith("{"):
                data = json.loads(raw)
                if isinstance(data, dict):
                    return str(
                        data.get("description")
                        or data.get("body_text")
                        or data.get("content")
                        or raw
                    ).strip()
            return raw
        except (OSError, json.JSONDecodeError):
            return ""
    return ""


__all__ = [
    "APPS_RG_TARGETING_BRIEF_PROMPT_PATH",
    "apps_rg_targeting_brief_enabled",
    "build_targeting_brief_prompt",
    "extract_jd_text",
    "format_research_findings",
    "load_targeting_brief_prompt_template",
]
