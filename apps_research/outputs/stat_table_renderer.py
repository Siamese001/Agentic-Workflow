"""Stat-table renderer (plan §P2.2).

Minimal Markdown table renderer for structured stats. Blend reference
shape uses three columns: metric | value | source. Column set is
configurable; the default matches the Blend reference PDF.
"""

from __future__ import annotations

from typing import Any

_DEFAULT_COLUMNS: tuple[str, ...] = ("metric", "value", "source")


def render(
    stats: list[dict[str, Any]] | None,
    columns: tuple[str, ...] = _DEFAULT_COLUMNS,
) -> str:
    """Render ``stats`` as a Markdown pipe-table with the given columns.

    Args:
        stats: list of dicts with keys matching ``columns``. Missing keys
            render as empty cells; extra keys are ignored.
        columns: column keys in output order. Defaults to
            ``("metric", "value", "source")``.

    Returns:
        Markdown table string ending with a newline. Empty/None input
        yields ``"_No structured stats available._\\n"``.
    """
    if not stats:
        return "_No structured stats available._\n"

    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join(["---"] * len(columns)) + "|"
    body_lines: list[str] = []
    for row in stats:
        if not isinstance(row, dict):
            continue
        cells = [str(row.get(col, "")) for col in columns]
        body_lines.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *body_lines]) + "\n"
