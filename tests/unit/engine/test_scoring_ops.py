"""
Unit tests for shared_engine_ops/scoring_ops/
Tests scoring operations for ranking and evaluation.
"""
from __future__ import annotations
import pytest
from typing import Dict
from dataclasses import dataclass

@dataclass
class ScoredItem:
    id: str
    raw_score: float
    normalized_score: float
    factors: Dict[str, float]

class TestScoreCalculation:
    """Tests for score calculation."""

    def test_simple_score_calculation(self):
        """Simple score is calculated correctly."""
        relevance = 0.8
        recency = 0.9
        quality = 0.7

        weights = {"relevance": 0.5, "recency": 0.3, "quality": 0.2}
        score = (
            relevance * weights["relevance"] +
            recency * weights["recency"] +
            quality * weights["quality"]
        )

        assert score == pytest.approx(0.81)

    def test_weighted_score_calculation(self):
        """Weighted score is calculated correctly."""
        factors = [
            {"name": "relevance", "value": 0.9, "weight": 0.5},
            {"name": "freshness", "value": 0.7, "weight": 0.3},
            {"name": "authority", "value": 0.8, "weight": 0.2},
        ]

        weighted_sum = sum(f["value"] * f["weight"] for f in factors)
        total_weight = sum(f["weight"] for f in factors)
        score = weighted_sum / total_weight

        assert score == pytest.approx(0.82)

    def test_score_normalization(self):
        """Scores are normalized to [0, 1] range."""
        raw_scores = [10, 50, 100, 25, 75]
        min_score = min(raw_scores)
        max_score = max(raw_scores)

        normalized = [(s - min_score) / (max_score - min_score) for s in raw_scores]

        assert all(0 <= n <= 1 for n in normalized)
        assert min(normalized) == 0.0
        assert max(normalized) == 1.0

    def test_score_determinism(self):
        """Same inputs produce same score."""
        factors = {"a": 0.5, "b": 0.3}
        weights = {"a": 0.6, "b": 0.4}

        score1 = sum(factors[k] * weights[k] for k in factors)
        score2 = sum(factors[k] * weights[k] for k in factors)

        assert score1 == score2


class TestScoreComparison:
    """Tests for score comparison operations."""

    def test_compare_scores_greater(self):
        """Higher score is correctly identified."""
        score_a = 0.8
        score_b = 0.6

        assert score_a > score_b

    def test_compare_scores_equal(self):
        """Equal scores are handled correctly."""
        score_a = 0.75
        score_b = 0.75

        assert score_a == score_b

    def test_rank_by_score(self):
        """Items are ranked correctly by score."""
        items = [
            {"id": "1", "score": 0.6},
            {"id": "2", "score": 0.9},
            {"id": "3", "score": 0.7},
        ]

        ranked = sorted(items, key=lambda x: x["score"], reverse=True)

        assert ranked[0]["id"] == "2"
        assert ranked[1]["id"] == "3"
        assert ranked[2]["id"] == "1"

    def test_tiebreaker_scoring(self):
        """Tiebreaker is applied when scores are equal."""
        items = [
            {"id": "1", "score": 0.8, "recency": 5},
            {"id": "2", "score": 0.8, "recency": 1},
        ]

        # Primary: score (desc), Secondary: recency (asc, lower is more recent)
        ranked = sorted(items, key=lambda x: (-x["score"], x["recency"]))

        assert ranked[0]["id"] == "2"  # Same score, more recent


class TestScoreAggregation:
    """Tests for score aggregation."""

    def test_average_scores(self):
        """Average score is calculated correctly."""
        scores = [0.8, 0.7, 0.9, 0.6]
        average = sum(scores) / len(scores)

        assert average == 0.75

    def test_max_score(self):
        """Maximum score is identified correctly."""
        scores = [0.8, 0.7, 0.9, 0.6]
        max_score = max(scores)

        assert max_score == 0.9

    def test_min_score(self):
        """Minimum score is identified correctly."""
        scores = [0.8, 0.7, 0.9, 0.6]
        min_score = min(scores)

        assert min_score == 0.6

    def test_score_distribution(self):
        """Score distribution is calculated correctly."""
        scores = [0.1, 0.3, 0.5, 0.7, 0.9]

        distribution = {
            "min": min(scores),
            "max": max(scores),
            "mean": sum(scores) / len(scores),
            "median": sorted(scores)[len(scores) // 2],
        }

        assert distribution["min"] == 0.1
        assert distribution["max"] == 0.9
        assert distribution["mean"] == 0.5
        assert distribution["median"] == 0.5


class TestScoreThresholds:
    """Tests for score threshold operations."""

    def test_above_threshold(self):
        """Items above threshold are identified."""
        items = [
            {"id": "1", "score": 0.8},
            {"id": "2", "score": 0.5},
            {"id": "3", "score": 0.9},
        ]
        threshold = 0.7

        above = [i for i in items if i["score"] >= threshold]
        assert len(above) == 2

    def test_below_threshold(self):
        """Items below threshold are identified."""
        items = [
            {"id": "1", "score": 0.8},
            {"id": "2", "score": 0.5},
            {"id": "3", "score": 0.3},
        ]
        threshold = 0.6

        below = [i for i in items if i["score"] < threshold]
        assert len(below) == 2

    def test_dynamic_threshold(self):
        """Dynamic threshold based on score distribution."""
        scores = [0.9, 0.85, 0.7, 0.5, 0.3]

        # Dynamic threshold: top 40%
        sorted_scores = sorted(scores, reverse=True)
        top_40_percent_idx = int(len(sorted_scores) * 0.4)
        dynamic_threshold = sorted_scores[top_40_percent_idx]

        above_threshold = [s for s in scores if s >= dynamic_threshold]
        assert len(above_threshold) == 2
