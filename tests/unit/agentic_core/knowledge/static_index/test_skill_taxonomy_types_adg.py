"""ADG-driven tests for knowledge/static_index/skill_taxonomy_types.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.knowledge.static_index.skill_taxonomy_types import SKILL_TAXONOMY


class TestSkillTaxonomy:
    def test_is_dict(self):
        assert isinstance(SKILL_TAXONOMY, dict)

    def test_has_ai_ml_category(self):
        assert "AI/ML" in SKILL_TAXONOMY

    def test_has_backend_category(self):
        assert "Backend" in SKILL_TAXONOMY

    def test_ai_ml_is_list(self):
        assert isinstance(SKILL_TAXONOMY["AI/ML"], list)

    def test_ai_ml_nonempty(self):
        assert len(SKILL_TAXONOMY["AI/ML"]) > 0

    def test_all_values_are_lists_of_strings(self):
        for category, skills in SKILL_TAXONOMY.items():
            assert isinstance(skills, list), f"{category} should be a list"
            for s in skills:
                assert isinstance(s, str), f"{s} in {category} should be str"
