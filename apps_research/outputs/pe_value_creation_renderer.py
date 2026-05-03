"""Private-equity value-creation renderer (plan §P4.3).

Renders a structured PE bundle: thesis paragraph, levers list, risks
list, and source register. Acceptance requires 1 thesis, ≥3 levers, ≥3
risks, each lever/risk with ≥1 ``source_url``.
"""

from __future__ import annotations

from typing import Any


def _render_claim_block(label: str, items: list[dict[str, Any]]) -> str:
    lines = [f"## {label}", ""]
    if not items:
        lines.append(f"_No {label.lower()} recorded._")
        lines.append("")
        return "\n".join(lines)
    for idx, item in enumerate(items, start=1):
        text = item.get("text") or item.get("description") or ""
        url = item.get("source_url", "")
        if url:
            lines.append(f"{idx}. {text} ([source]({url}))")
        else:
            lines.append(f"{idx}. {text}")
    lines.append("")
    return "\n".join(lines)


def render(bundle: dict[str, Any], company: str = "") -> str:
    """Render a PE value-creation bundle as Markdown.

    Args:
        bundle: dict with keys ``thesis`` (str), ``levers`` (list[dict]),
            ``risks`` (list[dict]), ``source_register`` (list[dict]).
        company: optional company name for the H1 title.

    Returns:
        Markdown string.
    """
    title = (
        f"# {company} — PE Value-Creation Brief" if company else "# PE Value-Creation Brief"
    )
    lines = [title, ""]

    thesis = str(bundle.get("thesis") or "").strip()
    lines.append("## Thesis")
    lines.append("")
    lines.append(thesis or "_No thesis recorded._")
    lines.append("")

    levers = bundle.get("levers") or []
    risks = bundle.get("risks") or []
    lines.append(_render_claim_block("Levers", levers))
    lines.append(_render_claim_block("Risks", risks))

    # Sources footer (reuse canonical renderer).
    from apps_research.outputs.source_register_renderer import render as render_sources

    lines.append(render_sources(bundle))
    return "\n".join(lines)
