"""Pairwise bullet duplicate detector (embedding-free cosine heuristic)."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _cosine_similarity(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0
    common = left.keys() & right.keys()
    dot = sum(left[w] * right[w] for w in common)
    n1 = math.sqrt(sum(v * v for v in left.values()))
    n2 = math.sqrt(sum(v * v for v in right.values()))
    if n1 <= 0.0 or n2 <= 0.0:
        return 0.0
    return dot / (n1 * n2)


class DuplicateDetector:
    """Structural duplicate finder for bullets + cross-section summaries."""

    def __init__(self, default_threshold: float = 0.9) -> None:
        self.default_threshold = default_threshold

    @staticmethod
    def _bullet_text(record: dict[str, Any]) -> str:
        return str(record.get("bullet_text") or "").strip()

    def find_duplicates(
        self, bullets: list[dict[str, Any]], threshold: float | None = None
    ) -> list[tuple[int, int, float]]:
        thr = self.default_threshold if threshold is None else threshold
        out: list[tuple[int, int, float]] = []
        reps: list[Counter[str]] = []
        for rec in bullets:
            reps.append(Counter(_tokens(self._bullet_text(rec))))
        n = len(reps)
        for i in range(n):
            for j in range(i + 1, n):
                sim = _cosine_similarity(reps[i], reps[j])
                if sim >= thr:
                    out.append((i, j, sim))
        return out

    def compute_similarity_matrix(
        self, sections: dict[str, list[Any]] | None
    ) -> dict[str, Any]:
        if not sections:
            return {
                "pairwise_checks": [],
                "total_comparisons": 0,
                "duplicates_found": [],
                "max_similarity": 0.0,
                "sections_analyzed": [],
            }

        section_names = list(sections.keys())
        pairwise_checks: list[dict[str, Any]] = []
        duplicates_found: list[dict[str, Any]] = []
        max_similarity = 0.0
        bullets_meta: list[tuple[str, int, Counter[str]]] = []

        # Flatten bullets with (section_name, bullet_index_within_flat, vocab)
        for sec in section_names:
            raw_items = sections.get(sec, []) or []
            for idx, raw in enumerate(raw_items):
                if raw is None:
                    continue
                if isinstance(raw, str):
                    text = raw.strip()
                else:
                    text = ""
                if not text:
                    continue
                c = Counter(_tokens(text))
                if not sum(c.values()):
                    continue
                bullets_meta.append((sec, idx, c))

        for i in range(len(bullets_meta)):
            for j in range(i + 1, len(bullets_meta)):
                si, _, ci = bullets_meta[i]
                sj, _, cj = bullets_meta[j]
                sim = _cosine_similarity(ci, cj)
                max_similarity = max(max_similarity, sim)
                cross_section = si != sj
                pairwise_checks.append(
                    {"i": i, "j": j, "similarity": sim, "cross_section": cross_section}
                )
                if sim >= self.default_threshold:
                    duplicates_found.append(
                        {"i": i, "j": j, "similarity": sim, "cross_section": cross_section}
                    )

        return {
            "pairwise_checks": pairwise_checks,
            "total_comparisons": len(pairwise_checks),
            "duplicates_found": duplicates_found,
            "max_similarity": float(max_similarity),
            "sections_analyzed": section_names,
        }
