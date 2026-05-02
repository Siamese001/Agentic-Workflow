"""HOP-4.7-MARQUEE — Pull top 3-4 quantified bullets across all roles
into a callout above Professional Experience.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P6.2).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

SECTION_ID = "hop_4_7_marquee"

_METRIC_RE = re.compile(r"(?:\$\d|\d+\s*%|\d+x|\b\d{2,}\b)")


@dataclass(frozen=True)
class MarqueeOutcome:
    role_id: str
    bullet_index: int
    text: str
    metric_count: int


def select_marquee(
    *,
    bullets_by_role: Sequence[dict],
    n: int = 4,
    min_metric_count: int = 1,
    exclude_texts: Optional[Iterable[str]] = None,
) -> List[MarqueeOutcome]:
    """Score every bullet by metric density, return top n unique.

    Args:
        bullets_by_role: list of {"role_id": ..., "bullets": [{"text": ...}, ...]}
        n: max marquee outcomes to return (3-4 per spec).
        min_metric_count: minimum metric matches a bullet must have.
        exclude_texts: bullets already used elsewhere in the resume to dedup.
    """
    exclude_norm = {(t or "").strip().lower() for t in (exclude_texts or [])}
    candidates: List[MarqueeOutcome] = []
    for role in bullets_by_role:
        role_id = str(role.get("role_id") or role.get("company") or "?")
        for idx, bullet in enumerate(role.get("bullets") or []):
            text = str(bullet.get("text") if isinstance(bullet, dict) else bullet or "").strip()
            if not text or text.lower() in exclude_norm:
                continue
            metric_count = len(_METRIC_RE.findall(text))
            if metric_count < min_metric_count:
                continue
            candidates.append(
                MarqueeOutcome(
                    role_id=role_id,
                    bullet_index=idx,
                    text=text,
                    metric_count=metric_count,
                )
            )

    # Sort by metric count desc, then bullet length asc to favor crisp lines.
    candidates.sort(key=lambda m: (-m.metric_count, len(m.text)))
    out: List[MarqueeOutcome] = []
    seen: set[str] = set()
    for c in candidates:
        norm = c.text.lower()
        if norm in seen:
            continue
        seen.add(norm)
        out.append(c)
        if len(out) >= n:
            break
    return out


__all__ = ["MarqueeOutcome", "SECTION_ID", "select_marquee"]
