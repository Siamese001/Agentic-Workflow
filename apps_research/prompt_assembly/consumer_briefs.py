"""Shared consumer brief prompt helpers for apps_research.

This module centralizes the compact downstream brief prompts used by apps_rg
and apps_lic so each consumer can request a tighter signal-shaped artifact
instead of the full company brief.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

_PROMPT_DIR = Path(__file__).resolve().parents[1] / "config" / "prompts"

_TEMPLATE_PROMPT_FILES: dict[str, Path] = {
    "apps_rg_targeting_brief_synthesis_v1": _PROMPT_DIR / "apps_rg_targeting_brief_v1.md",
    "downstream_research_substrate_v1": _PROMPT_DIR / "downstream_research_substrate_v1.md",
    "apps_lic_research_substrate_v1": _PROMPT_DIR / "apps_lic_research_substrate_v1.md",
    "apps_exec_executive_brief_v1": _PROMPT_DIR / "apps_exec_executive_brief_v1.md",
}

_TEMPLATE_ALIASES: dict[str, str] = {
    "apps_rg_targeting_brief": "apps_rg_targeting_brief_synthesis_v1",
    "apps_rg_targeting_brief_v1": "apps_rg_targeting_brief_synthesis_v1",
    "apps_rg_targeting_brief_synthesis_v1": "apps_rg_targeting_brief_synthesis_v1",
    "downstream_research_substrate": "downstream_research_substrate_v1",
    "downstream_research_substrate_v1": "downstream_research_substrate_v1",
    "apps_lic_research_substrate": "apps_lic_research_substrate_v1",
    "apps_lic_research_substrate_v1": "apps_lic_research_substrate_v1",
    "apps_exec_executive_brief": "apps_exec_executive_brief_v1",
    "apps_exec_executive_brief_v1": "apps_exec_executive_brief_v1",
}


def normalize_consumer_template_id(template_id: str | None) -> str | None:
    raw = str(template_id or "").strip()
    if not raw:
        return None
    return _TEMPLATE_ALIASES.get(raw, raw if raw in _TEMPLATE_PROMPT_FILES else None)


def consumer_brief_template_id(*, jd_context: dict | None = None) -> str | None:
    """Resolve an explicit consumer brief template from JD context metadata."""
    if not isinstance(jd_context, dict):
        return None
    for key in ("output_format", "synthesis_template"):
        resolved = normalize_consumer_template_id(jd_context.get(key))
        if resolved:
            return resolved
    return None


@functools.lru_cache(maxsize=None)
def load_consumer_brief_prompt_template(template_id: str) -> str:
    """Load the SSOT prompt text for a downstream consumer brief template."""
    normalized = normalize_consumer_template_id(template_id)
    if not normalized:
        raise KeyError(f"Unknown consumer brief template_id: {template_id!r}")
    prompt_path = _TEMPLATE_PROMPT_FILES[normalized]
    return prompt_path.read_text(encoding="utf-8")


def consumer_brief_prompt_path(template_id: str) -> Path:
    """Return the prompt file path for a downstream consumer brief template."""
    normalized = normalize_consumer_template_id(template_id)
    if not normalized:
        raise KeyError(f"Unknown consumer brief template_id: {template_id!r}")
    return _TEMPLATE_PROMPT_FILES[normalized]


def build_consumer_brief_prompt(
    *,
    template_id: str,
    jd_text: str,
    research_notes: str,
    target_entity: str,
) -> str:
    """Render a compact downstream consumer prompt with shared placeholders."""
    template = load_consumer_brief_prompt_template(template_id)
    return (
        template.replace("{{jd_text}}", str(jd_text or "").strip() or "(no JD text provided)")
        .replace("{{research_notes}}", str(research_notes or "").strip() or "(no research notes)")
        .replace("{{target_entity}}", str(target_entity or "").strip() or "TBD")
    )


def extract_jd_text(
    *,
    jd_context: dict | None,
    jd_anchor: Path | None = None,
) -> str:
    """Resolve a full JD body from jd_context or a JD anchor file."""
    if isinstance(jd_context, dict):
        for key in ("content", "jd_text", "body_text", "description", "job_description_text"):
            value = str(jd_context.get(key) or "").strip()
            if value:
                return value
        jd_ref = str(jd_context.get("jd_ref") or "").strip()
        if jd_ref:
            p = Path(jd_ref)
            if p.is_file():
                try:
                    return p.read_text(encoding="utf-8", errors="replace").strip()
                except FileNotFoundError:
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


def format_research_findings(findings: dict[str, str], *, max_chars: int = 12000) -> str:
    """Flatten family-level research blobs into a bounded prompt block."""
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
