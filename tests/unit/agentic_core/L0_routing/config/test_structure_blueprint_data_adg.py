"""ADG-driven tests for L0_routing/config/structure_blueprint_data.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.config.structure_blueprint_data import (
    FOLDER_PURITY_RULES,
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
    SCRIPTS_FORBIDDEN_PATTERNS,
)


class TestScriptsForbiddenPatterns:
    def test_is_sequence(self):
        assert hasattr(SCRIPTS_FORBIDDEN_PATTERNS, "__len__")

    def test_contains_patterns(self):
        assert len(SCRIPTS_FORBIDDEN_PATTERNS) >= 1


class TestAllowlists:
    def test_l5_subprocess_allowlist_is_sequence(self):
        assert hasattr(L5_SUBPROCESS_ALLOWLIST, "__len__")

    def test_l5_contains_safe_subprocess(self):
        assert any("safe_subprocess" in p for p in L5_SUBPROCESS_ALLOWLIST)

    def test_l6_hybrid_allowlist_is_sequence(self):
        assert hasattr(L6_HYBRID_ALLOWLIST, "__len__")


class TestFolderPurityRules:
    def test_is_mapping(self):
        assert hasattr(FOLDER_PURITY_RULES, "__getitem__")

    def test_reasoning_key_present(self):
        assert "reasoning" in FOLDER_PURITY_RULES
