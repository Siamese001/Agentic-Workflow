"""Tests for apps_eval engine components."""

import pytest

from apps_eval.engines.evaluation_retrieval_engine import (
    EvaluationRetrievalEngine,
)
from apps_eval.engines.scorecard_engine import (
    ScorecardEngine,
)


class TestEvaluationRetrievalEngine:
    """Test EvaluationRetrievalEngine."""

    def test_engine_import(self):
        """Test that EvaluationRetrievalEngine can be imported."""
        assert EvaluationRetrievalEngine is not None

    def test_engine_class_exists(self):
        """Test that EvaluationRetrievalEngine class exists."""
        assert callable(EvaluationRetrievalEngine)


class TestScorecardEngine:
    """Test ScorecardEngine."""

    def test_engine_import(self):
        """Test that ScorecardEngine can be imported."""
        assert ScorecardEngine is not None

    def test_engine_class_exists(self):
        """Test that ScorecardEngine class exists."""
        assert callable(ScorecardEngine)
