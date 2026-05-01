"""
Duplicate Detector Engine - Resume bullet deduplication via TF-IDF cosine similarity.

Restored from git 3a60f9f001:apps_rg/L5_safety/check_duplicate_content.py (2025-12-08
atomization snapshot). The original module was deleted in commit db0ee78b1c
(2025-12-23) along with the L5_safety/ tree but the call site in
apps_rg/tools/DataEnricher.py was never updated, leaving DataEnricher with a
broken NameError at runtime.

This is a passive utility (synchronous, no async execute()) so it does not
inherit BaseRGEngine — that contract is for runtime-dispatched engines with
lifecycle traces. DuplicateDetector is invoked directly by DataEnricher.

Used by:
  - apps_rg/tools/DataEnricher.py (HOP-2 bullet deduplication)
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.utils.text_similarity_util import (
    TextSimilarityCalculator,
)


class DuplicateDetector:
    """Detect duplicate or near-duplicate bullets using TF-IDF cosine similarity.

    Threshold defaults to 0.9 — bullets with cosine similarity at or above this
    value are flagged as duplicates. The threshold is exposed as a parameter
    on find_duplicates() to allow caller-side tuning without rebuilding state.
    """

    DEFAULT_THRESHOLD: float = 0.9

    def __init__(self) -> None:
        """Initialize the duplicate detector with a fresh similarity calculator."""
        self.similarity_calc = TextSimilarityCalculator()

    def find_duplicates(
        self, bullets: list[dict[str, Any]], threshold: float | None = None
    ) -> list[tuple[int, int, float]]:
        """Find bullets with cosine similarity >= threshold.

        Args:
            bullets: List of bullet dicts. Each dict must have a "bullet_text" key.
                     Bullets without "bullet_text" are treated as empty strings.
            threshold: Cosine similarity threshold (default DEFAULT_THRESHOLD = 0.9).

        Returns:
            List of (i, j, similarity) tuples for each duplicate pair, where i < j.
        """
        thr = self.DEFAULT_THRESHOLD if threshold is None else threshold
        duplicates: list[tuple[int, int, float]] = []
        for i in range(len(bullets)):
            for j in range(i + 1, len(bullets)):
                similarity = self.similarity_calc.calculate(
                    bullets[i].get("bullet_text", ""),
                    bullets[j].get("bullet_text", ""),
                )
                if similarity >= thr:
                    duplicates.append((i, j, similarity))
        return duplicates

    def compute_similarity_matrix(
        self, sections: dict[str, list[str]]
    ) -> dict[str, Any]:
        """Compute pairwise similarity matrix across all section bullets.

        Args:
            sections: Mapping of section_id -> list of bullet text strings.
                      Non-string or empty bullets are filtered out.

        Returns:
            Dict with keys: pairwise_checks, total_comparisons, duplicates_found,
            max_similarity, sections_analyzed. Cross-section duplicates are flagged
            via the cross_section field on each comparison.
        """
        matrix_data: dict[str, Any] = {
            "pairwise_checks": [],
            "total_comparisons": 0,
            "duplicates_found": [],
            "max_similarity": 0.0,
            "sections_analyzed": list(sections.keys()),
        }

        all_bullets: list[dict[str, Any]] = []
        for section_id, bullets in sections.items():
            if isinstance(bullets, list):
                for idx, bullet in enumerate(bullets):
                    if isinstance(bullet, str) and bullet.strip():
                        all_bullets.append(
                            {
                                "section": section_id,
                                "index": idx,
                                "text": bullet.strip(),
                            }
                        )

        for i in range(len(all_bullets)):
            for j in range(i + 1, len(all_bullets)):
                b1, b2 = all_bullets[i], all_bullets[j]
                similarity = self.similarity_calc.calculate(b1["text"], b2["text"])

                comparison = {
                    "bullet_1": f"{b1['section']}[{b1['index']}]",
                    "bullet_2": f"{b2['section']}[{b2['index']}]",
                    "similarity": round(similarity, 4),
                    "cross_section": b1["section"] != b2["section"],
                }

                matrix_data["pairwise_checks"].append(comparison)
                matrix_data["total_comparisons"] += 1
                matrix_data["max_similarity"] = max(
                    matrix_data["max_similarity"], similarity
                )

                if similarity >= self.DEFAULT_THRESHOLD:
                    matrix_data["duplicates_found"].append(comparison)

        return matrix_data
