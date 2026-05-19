"""IBM narrative metric budget trimming (companion full-metric-bundle mode)."""

from __future__ import annotations

import re

from apps_rg.runtime.validators.ibm_narrative_x2 import (
    companion_ibm_bullets_have_full_metric_bundle,
    count_ibm_narrative_metric_hits,
)


def truncate_narrative_after_first_metric_hit(narrative: str) -> str:
    """When multiple tracked IBM metrics remain in one clause, drop text from the second metric onward."""
    s = narrative.strip()
    patterns = (
        re.compile(r"\$15\s*m", re.I),
        re.compile(r"99\.9%"),
        re.compile(r"\b30\s*%"),
        re.compile(r"\b25\s*%"),
        re.compile(r"\b50\s*%"),
    )
    spans: list[tuple[int, int]] = []
    for rx in patterns:
        for m in rx.finditer(s):
            spans.append((m.start(), m.end()))
    spans.sort(key=lambda x: x[0])
    if len(spans) < 2:
        return s
    cut = spans[1][0]
    clipped = s[:cut].rstrip()
    clipped = re.sub(r"\s*[,;:]\s*$", "", clipped)
    clipped = re.sub(r"\s+and\s*$", "", clipped, flags=re.I)
    clipped = clipped.rstrip(" ,")
    return clipped if clipped else s


def _remove_earliest_metric_span(narrative: str) -> str:
    """Drop the earliest tracked IBM metric substring (best-effort for companion full-metric-bundle mode)."""
    s = narrative.strip()
    if not s:
        return s
    patterns = (
        re.compile(r"\$15\s*m", re.I),
        re.compile(r"99\.9%"),
        re.compile(r"\b30\s*%"),
        re.compile(r"\b25\s*%"),
        re.compile(r"\b50\s*%"),
    )
    earliest: tuple[int, int] | None = None
    for rx in patterns:
        m = rx.search(s)
        if m and (earliest is None or m.start() < earliest[0]):
            earliest = (m.start(), m.end())

    dollar_plain = re.search(r"\$15\b", s)
    if dollar_plain:
        cand = (dollar_plain.start(), dollar_plain.end())
        if earliest is None or cand[0] < earliest[0]:
            earliest = cand

    if earliest is None:
        return s
    left = s[: earliest[0]].rstrip()
    right = s[earliest[1] :].lstrip()
    out = left
    if right:
        out = (left + " " + right).strip() if left else right
    out = re.sub(r"\s*[,;:]\s*$", "", out)
    out = re.sub(r"^\s*[,;:]\s*", "", out)
    out = re.sub(r"\s+and\s+$", "", out, flags=re.I)
    return out.strip()


def collapse_narrative_sentence_for_companion_metric_budget(
    narrative: str, companion_text: str, max_rounds: int = 48
) -> str:
    """When companion bullets expose the KPI bundle, strip tracked bullet metrics until none remain."""
    s = narrative.strip()
    if not companion_text.strip() or not companion_ibm_bullets_have_full_metric_bundle(companion_text):
        return s
    for _ in range(max_rounds):
        hits = count_ibm_narrative_metric_hits(s)
        if hits == 0:
            break
        before = s
        s = _remove_earliest_metric_span(s)
        if count_ibm_narrative_metric_hits(s) == hits:
            alt = truncate_narrative_after_first_metric_hit(before)
            if alt != before:
                s = alt
        if count_ibm_narrative_metric_hits(s) == hits and s == before:
            break
    return s
