# Ownership: apps_rg / L5_safety
# Layer: L5_safety
# Agent: apps_rg
# -*- coding: utf-8 -*-
"""
Duplicate content detection for resume sections.

Detects duplicate or near-duplicate bullets across sections.
"""

from __future__ import annotations

from typing import Dict, List

from apps_rg.L2_execution.compute_text_similarity import TextSimilarityCalculator


class DuplicateDetector:
    """Detect duplicate or near-duplicate bullets using TF-IDF cosine similarity."""

    def __init__(self) -> None:
        """Initialize the duplicate detector."""
        self.similarity_calc = TextSimilarityCalculator()

    def find_duplicates(
        self, bullets: List[Dict], threshold: float = 0.9
    ) -> List[tuple]:
        """Find bullets with cosine similarity >= threshold."""
        duplicates = []
        for i in range(len(bullets)):
            for j in range(i + 1, len(bullets)):
                similarity = self.similarity_calc.calculate(
                    bullets[i].get("bullet_text", ""),
                    bullets[j].get("bullet_text", ""),
                )
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        return duplicates

    def compute_similarity_matrix(self, sections: Dict[str, List[str]]) -> Dict:
        """Compute pairwise similarity matrix across all sections."""
        matrix_data = {
            "pairwise_checks": [],
            "total_comparisons": 0,
            "duplicates_found": [],
            "max_similarity": 0.0,
            "sections_analyzed": list(sections.keys()),
        }

        all_bullets = []
        for section_id, bullets in sections.items():
            if isinstance(bullets, list):
                for idx, bullet in enumerate(bullets):
                    if isinstance(bullet, str) and bullet.strip():
                        all_bullets.append(
                            {"section": section_id, "index": idx, "text": bullet.strip()}
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

                if similarity >= 0.9:
                    matrix_data["duplicates_found"].append(comparison)

        return matrix_data
