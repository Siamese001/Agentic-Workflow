"""ADG-driven tests for knowledge/static_index/action_verbs_types.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.knowledge.static_index.action_verbs_types import ACTION_VERBS


class TestActionVerbs:
    def test_is_dict(self):
        assert isinstance(ACTION_VERBS, dict)

    def test_has_engineering_category(self):
        assert "Engineering" in ACTION_VERBS

    def test_has_leadership_category(self):
        assert "Leadership" in ACTION_VERBS

    def test_has_analysis_category(self):
        assert "Analysis" in ACTION_VERBS

    def test_engineering_is_list(self):
        assert isinstance(ACTION_VERBS["Engineering"], list)

    def test_engineering_nonempty(self):
        assert len(ACTION_VERBS["Engineering"]) > 0

    def test_all_values_are_lists_of_strings(self):
        for category, verbs in ACTION_VERBS.items():
            assert isinstance(verbs, list), f"{category} should be a list"
            for v in verbs:
                assert isinstance(v, str), f"{v} in {category} should be str"
