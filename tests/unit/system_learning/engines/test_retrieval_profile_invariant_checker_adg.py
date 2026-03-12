"""ADG-driven tests for system_learning/engines/retrieval_profile_invariant_checker.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from system_learning.engines.retrieval_profile_invariant_checker import (
    InvariantViolation,
    RetrievalProfileInvariantChecker,
)


class TestInvariantViolation:
    def test_creates(self):
        v = InvariantViolation(
            field="top_k",
            expected="in [1, 200]",
            actual="300",
            message="top_k out of bounds",
        )
        assert v.field == "top_k"
        assert v.message == "top_k out of bounds"

    def test_is_frozen(self):
        v = InvariantViolation(field="f", expected="e", actual="a", message="m")
        with pytest.raises(Exception):
            v.field = "modified"


class TestRetrievalProfileInvariantChecker:
    def test_creates_with_defaults(self):
        checker = RetrievalProfileInvariantChecker()
        assert checker.min_top_k == 1
        assert checker.max_top_k == 200

    def test_creates_with_custom_bounds(self):
        checker = RetrievalProfileInvariantChecker(min_top_k=5, max_top_k=50)
        assert checker.min_top_k == 5
        assert checker.max_top_k == 50

    def test_has_validate(self):
        assert hasattr(RetrievalProfileInvariantChecker, "validate")
