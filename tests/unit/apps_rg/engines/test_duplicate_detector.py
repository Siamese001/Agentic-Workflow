"""Tests for apps_rg.engines.duplicate_detector.DuplicateDetector.

Verifies the restored capability that closes the broken DataEnricher import
documented in plan apps-rg-prior-art-gap-closure-3e3d5b.
"""

from __future__ import annotations

import pytest

try:
    from apps_rg.engines.duplicate_detector import DuplicateDetector
except ModuleNotFoundError:
    pytest.skip(
        "apps-rg-unit-pytest-remediation-f7e2a9 W1: apps_rg.engines.duplicate_detector "
        "not on disk (engines tree removed/migrated).",
        allow_module_level=True,
    )


class TestDuplicateDetectorFindDuplicates:
    """find_duplicates() — pairwise duplicate detection."""

    def test_no_duplicates_in_distinct_bullets(self) -> None:
        d = DuplicateDetector()
        bullets = [
            {"bullet_text": "Led data engineering team of 5 across cloud platforms"},
            {"bullet_text": "Authored compliance policy for healthcare ingestion pipeline"},
            {"bullet_text": "Reduced query latency 40% via index restructuring"},
        ]
        assert d.find_duplicates(bullets) == []

    def test_identical_bullets_flagged(self) -> None:
        d = DuplicateDetector()
        bullets = [
            {"bullet_text": "Led data engineering team of 5 across cloud platforms"},
            {"bullet_text": "Led data engineering team of 5 across cloud platforms"},
        ]
        result = d.find_duplicates(bullets)
        assert len(result) == 1
        i, j, sim = result[0]
        assert (i, j) == (0, 1)
        assert sim == pytest.approx(1.0, abs=1e-6)

    def test_threshold_parameter_overrides_default(self) -> None:
        """A high (1.01) threshold should suppress even identical-bullet matches."""
        d = DuplicateDetector()
        bullets = [
            {"bullet_text": "Led team of 5 engineers"},
            {"bullet_text": "Led team of 5 engineers"},
        ]
        # default 0.9 → match
        assert len(d.find_duplicates(bullets)) == 1
        # >1.0 threshold → no match (cosine cannot exceed 1.0)
        assert d.find_duplicates(bullets, threshold=1.01) == []

    def test_missing_bullet_text_treated_as_empty(self) -> None:
        d = DuplicateDetector()
        bullets = [
            {"bullet_text": "Real bullet content here"},
            {},  # no bullet_text key
        ]
        # An empty string vs real text should not be flagged as a duplicate.
        assert d.find_duplicates(bullets) == []

    def test_pair_indices_are_ordered_i_lt_j(self) -> None:
        """Restored contract: only (i, j) with i < j returned."""
        d = DuplicateDetector()
        bullets = [
            {"bullet_text": "Same exact text alpha beta gamma delta"},
            {"bullet_text": "Same exact text alpha beta gamma delta"},
            {"bullet_text": "Same exact text alpha beta gamma delta"},
        ]
        pairs = [(i, j) for i, j, _ in d.find_duplicates(bullets)]
        # 3 bullets → 3 unique unordered pairs: (0,1), (0,2), (1,2)
        assert pairs == [(0, 1), (0, 2), (1, 2)]


class TestDuplicateDetectorSimilarityMatrix:
    """compute_similarity_matrix() — cross-section pairwise matrix."""

    def test_empty_sections_yield_empty_matrix(self) -> None:
        d = DuplicateDetector()
        matrix = d.compute_similarity_matrix({})
        assert matrix["pairwise_checks"] == []
        assert matrix["total_comparisons"] == 0
        assert matrix["duplicates_found"] == []
        assert matrix["max_similarity"] == 0.0
        assert matrix["sections_analyzed"] == []

    def test_cross_section_flag_distinguishes_section_origin(self) -> None:
        d = DuplicateDetector()
        sections = {
            "experience": ["Led data engineering team of 5"],
            "summary": ["Led data engineering team of 5"],  # same text, diff section
        }
        matrix = d.compute_similarity_matrix(sections)
        assert matrix["total_comparisons"] == 1
        assert matrix["pairwise_checks"][0]["cross_section"] is True
        assert len(matrix["duplicates_found"]) == 1

    def test_non_string_or_empty_bullets_filtered(self) -> None:
        d = DuplicateDetector()
        sections: dict = {
            "experience": ["Real bullet here", "", None, 42, "   "],
        }
        matrix = d.compute_similarity_matrix(sections)
        # Only one valid bullet → no pairwise comparison possible.
        assert matrix["total_comparisons"] == 0
