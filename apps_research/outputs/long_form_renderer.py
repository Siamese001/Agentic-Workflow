"""Long-form render mode (plan §P4.1).

Produces a Markdown document with ≥5 H2 sections and ≥10 URL citations,
targeting 2000–3000 rendered tokens. Input is a CompanyBrief-shaped
dict; output is pure Markdown string.
"""

from __future__ import annotations

from typing import Any

_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Executive Summary", "summary"),
    ("Strategic Priorities", "strategic_priorities"),
    ("Customer Profile", "customer_profile"),
    ("Capabilities", "capabilities"),
    ("Market Position", "market_position"),
    ("Leadership", "leadership"),
    ("Risks & Constraints", "risks"),
)


def _as_list(val: Any) -> list[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def _render_section(title: str, items: list[Any]) -> str:
    lines = [f"## {title}", ""]
    if not items:
        lines.append("_No content recorded for this section._")
    else:
        for item in items:
            if isinstance(item, dict):
                text = item.get("text") or item.get("value") or str(item)
            else:
                text = str(item)
            lines.append(f"- {text}")
    lines.append("")
    return "\n".join(lines)


def render(brief: Any) -> str:
    """Render ``brief`` as a long-form Markdown document.

    Args:
        brief: CompanyBrief pydantic model or equivalent dict.

    Returns:
        Markdown string with H1 title, ≥5 H2 sections, and a Sources
        footer section listing all URLs from ``source_register``.
    """
    if hasattr(brief, "model_dump"):
        data = brief.model_dump()
    elif isinstance(brief, dict):
        data = brief
    else:
        data = {}

    company = data.get("company") or data.get("topic") or "Unknown Company"
    out: list[str] = [f"# {company} — Long-form Research Brief", ""]

    for title, key in _SECTIONS:
        out.append(_render_section(title, _as_list(data.get(key))))

    from apps_research.outputs.source_register_renderer import render as render_sources

    out.append(render_sources(brief))
    return "\n".join(out)
