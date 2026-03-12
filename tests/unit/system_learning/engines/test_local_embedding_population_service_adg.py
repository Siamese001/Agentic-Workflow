"""ADG-driven tests for system_learning/engines/local_embedding_population_service.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from system_learning.engines.local_embedding_population_service import (
    extract_embedding_text,
    normalize_l2,
)


class TestExtractEmbeddingText:
    def test_extracts_text_field(self):
        record = {"text": "hello world", "other": 123}
        assert extract_embedding_text(record) == "hello world"

    def test_missing_text_raises(self):
        with pytest.raises(ValueError, match="missing required 'text'"):
            extract_embedding_text({"key": "value"})

    def test_non_string_text_raises(self):
        with pytest.raises(ValueError, match="must be string"):
            extract_embedding_text({"text": 42})


class TestNormalizeL2:
    def test_unit_vector_unchanged(self):
        v = [1.0, 0.0, 0.0]
        result = normalize_l2(v)
        assert abs(result[0] - 1.0) < 1e-6

    def test_returns_unit_norm(self):
        import math
        v = [3.0, 4.0]
        result = normalize_l2(v)
        norm = math.sqrt(sum(x ** 2 for x in result))
        assert abs(norm - 1.0) < 1e-6

    def test_returns_list(self):
        result = normalize_l2([1.0, 2.0, 3.0])
        assert isinstance(result, list)
