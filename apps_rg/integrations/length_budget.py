"""Length budget extractor — derives per-bullet and per-section word budgets
from master_resume.json with a configurable tolerance (default ±15%).

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P3.1).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_TOLERANCE = 0.15


@dataclass(frozen=True)
class LengthBudget:
    label: str
    target_words: int
    min_words: int
    max_words: int
    target_sentences: Optional[int] = None

    def fits(self, text: str) -> bool:
        n = count_words(text)
        if not (self.min_words <= n <= self.max_words):
            return False
        if self.target_sentences is not None:
            sents = count_sentences(text)
            if sents not in (self.target_sentences, self.target_sentences - 1, self.target_sentences + 1):
                return False
        return True

    def diagnostic(self, text: str) -> Dict[str, Any]:
        return {
            "label": self.label,
            "n_words": count_words(text),
            "target": self.target_words,
            "min": self.min_words,
            "max": self.max_words,
            "fits": self.fits(text),
        }


def count_words(text: str) -> int:
    return len([w for w in (text or "").split() if w.strip()])


def count_sentences(text: str) -> int:
    if not text:
        return 0
    # Light heuristic — counts terminators.
    n = 0
    for ch in text:
        if ch in ".!?":
            n += 1
    return max(1, n) if text.strip() else 0


def budget_from_text(label: str, text: str, *, tolerance: float = DEFAULT_TOLERANCE) -> LengthBudget:
    target = count_words(text) or 1
    delta = max(1, int(round(target * tolerance)))
    return LengthBudget(
        label=label,
        target_words=target,
        min_words=max(1, target - delta),
        max_words=target + delta,
    )


def budget_for_section(
    label: str,
    *,
    target_words: int,
    target_sentences: Optional[int] = None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> LengthBudget:
    delta = max(1, int(round(target_words * tolerance)))
    return LengthBudget(
        label=label,
        target_words=target_words,
        min_words=max(1, target_words - delta),
        max_words=target_words + delta,
        target_sentences=target_sentences,
    )


def extract_master_resume_budgets(
    master_resume_path: Path | str,
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> Dict[str, LengthBudget]:
    """Build a budget map keyed by 'role_id::bullet_index'.

    Tolerant of multiple master_resume schema variants:
      - master_resume['roles'][i]['bullets'][j]['text']
      - master_resume['experience'][i]['bullet_pool'][j]['text']

    Unknown shapes degrade to empty dict; caller decides whether that is fatal.
    """
    path = Path(master_resume_path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    budgets: Dict[str, LengthBudget] = {}
    roles_block = data.get("roles") or data.get("experience") or []
    for role in roles_block:
        role_id = (
            role.get("role_id")
            or role.get("company")
            or role.get("title")
            or f"role_{len(budgets)}"
        )
        bullets = role.get("bullets") or role.get("bullet_pool") or []
        for idx, bullet in enumerate(bullets):
            text = _bullet_text(bullet)
            if not text:
                continue
            label = f"{role_id}::{idx}"
            budgets[label] = budget_from_text(label, text, tolerance=tolerance)
    return budgets


def _bullet_text(bullet: Any) -> str:
    if isinstance(bullet, str):
        return bullet
    if isinstance(bullet, dict):
        for key in ("text", "primary", "default", "content", "value"):
            v = bullet.get(key)
            if isinstance(v, str) and v.strip():
                return v
        # bullet_pool variant: pick first variant's text.
        variants = bullet.get("variants")
        if isinstance(variants, list) and variants:
            first = variants[0]
            if isinstance(first, dict):
                return str(first.get("text") or first.get("primary") or "")
            if isinstance(first, str):
                return first
    return ""


def best_fit(budgets: Iterable[LengthBudget], text: str) -> Optional[LengthBudget]:
    candidates = [b for b in budgets if b.fits(text)]
    if not candidates:
        return None
    return min(candidates, key=lambda b: abs(count_words(text) - b.target_words))


__all__ = [
    "DEFAULT_TOLERANCE",
    "LengthBudget",
    "best_fit",
    "budget_for_section",
    "budget_from_text",
    "count_sentences",
    "count_words",
    "extract_master_resume_budgets",
]
