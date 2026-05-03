"""Corporate-history timeline renderer (plan §P4.2).

Renders a chronologically-sorted Markdown timeline from a list of events
with ``{year, event, source_url}`` shape.
"""

from __future__ import annotations

from typing import Any


def _event_sort_key(event: dict[str, Any]) -> tuple[int, str]:
    year_raw = event.get("year", 0)
    try:
        year = int(year_raw)
    except (TypeError, ValueError):
        year = 0
    return (year, str(event.get("event", "")))


def render(events: list[dict[str, Any]] | None, company: str = "") -> str:
    """Render ``events`` as a Markdown timeline sorted ascending by year.

    Args:
        events: list of event dicts each with ``year`` (int),
            ``event`` (str), and ``source_url`` (str).
        company: optional company name for the H1 title.

    Returns:
        Markdown string. Empty/None events list yields a placeholder.
    """
    title = f"# {company} — Corporate History" if company else "# Corporate History"
    lines = [title, ""]
    if not events:
        lines.append("_No historical events recorded._")
        lines.append("")
        return "\n".join(lines)

    sorted_events = sorted(events, key=_event_sort_key)
    for ev in sorted_events:
        year = ev.get("year", "?")
        text = ev.get("event", "")
        url = ev.get("source_url", "")
        line = f"- **{year}**: {text}"
        if url:
            line += f" ([source]({url}))"
        lines.append(line)
    lines.append("")
    return "\n".join(lines)
