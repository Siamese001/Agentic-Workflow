"""HOP-4H-EARLY-CAREER — Deterministic 1-line compression.

Per locked decision (user 2026-05-01 §"ignore early career"): collapse to a
single deterministic line ≤25 words. No LLM call. Pure template fill from
chronology metadata.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P6.1).
"""

from __future__ import annotations

from typing import Iterable, Sequence

SECTION_ID = "hop_4h_early_career"
TIER = "skip"

MAX_WORDS = 25


def compress_early_career(
    *,
    roles: Sequence[dict],
    label: str = "Earlier Career",
) -> str:
    """Produce a single line summarizing pre-2010 roles.

    Args:
        roles: list of dicts with at least one of {start_year, end_year, title, company}.
        label: prefix label.
    """
    if not roles:
        return f"{label}: 2002-2009 — Quantitative & Analytical roles."

    years = sorted(
        (
            int(r.get("start_year") or 0)
            for r in roles
            if r.get("start_year")
        )
    )
    end_years = sorted(
        (
            int(r.get("end_year") or 0)
            for r in roles
            if r.get("end_year")
        )
    )
    start = years[0] if years else 2002
    end = end_years[-1] if end_years else 2009

    titles_seen: list[str] = []
    for r in roles:
        title = (r.get("title") or "").strip()
        if title and title not in titles_seen:
            titles_seen.append(title)
        if len(titles_seen) >= 3:
            break

    title_phrase = (
        ", ".join(titles_seen) if titles_seen else "Quantitative & Analytical roles"
    )
    line = f"{label}: {start}-{end} — {title_phrase}."

    # Enforce MAX_WORDS by truncation if necessary.
    words = line.split()
    if len(words) > MAX_WORDS:
        line = " ".join(words[: MAX_WORDS - 1]) + " …"
    return line


__all__ = ["MAX_WORDS", "SECTION_ID", "TIER", "compress_early_career"]
