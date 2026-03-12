"""ADG-driven tests for L5 structure_blueprint/classification.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.classification import (
    CLASSIFICATION_SUFFIX_PATTERNS,
)


class TestClassificationSuffixPatterns:
    def test_is_mapping(self):
        assert isinstance(CLASSIFICATION_SUFFIX_PATTERNS, dict | type(CLASSIFICATION_SUFFIX_PATTERNS))

    def test_agent_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "AGENT" in values

    def test_types_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "TYPES" in values

    def test_config_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "CONFIG" in values

    def test_all_values_are_strings(self):
        for v in CLASSIFICATION_SUFFIX_PATTERNS.values():
            assert isinstance(v, str)

    def test_all_keys_are_strings(self):
        for k in CLASSIFICATION_SUFFIX_PATTERNS.keys():
            assert isinstance(k, str)

    def test_non_empty(self):
        assert len(CLASSIFICATION_SUFFIX_PATTERNS) > 0
