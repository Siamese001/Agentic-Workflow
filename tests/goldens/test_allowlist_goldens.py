"""
Test allowlist goldens match actual allowlists.

These tests ensure allowlist changes are intentional and reviewed.
If a test fails, update the golden in allowlist_goldens.py.
"""

from agentic_core.L5_safety.config.structure_blueprint_config import (
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
    LAYER_ROOTS,
    LEAF_DOMAINS_NO_LCD,
    REQUIRED_LCD_SUBFOLDERS,
    SCRIPTS_FORBIDDEN_PATTERNS,
)
from tests.goldens.allowlist_goldens import (
    L5_SUBPROCESS_ALLOWLIST_GOLDEN,
    L6_HYBRID_ALLOWLIST_GOLDEN,
    LAYER_ROOTS_GOLDEN,
    LEAF_DOMAINS_NO_LCD_GOLDEN,
    REQUIRED_LCD_SUBFOLDERS_GOLDEN,
    SCRIPTS_FORBIDDEN_PATTERNS_GOLDEN,
)


class TestL5SubprocessAllowlistGolden:
    """Tests for L5 subprocess allowlist golden."""

    def test_allowlist_matches_golden(self):
        """L5_SUBPROCESS_ALLOWLIST must match golden."""
        assert L5_SUBPROCESS_ALLOWLIST == L5_SUBPROCESS_ALLOWLIST_GOLDEN, (
            f"L5_SUBPROCESS_ALLOWLIST changed!\n"
            f"Actual: {L5_SUBPROCESS_ALLOWLIST}\n"
            f"Golden: {L5_SUBPROCESS_ALLOWLIST_GOLDEN}\n"
            f"Added: {L5_SUBPROCESS_ALLOWLIST - L5_SUBPROCESS_ALLOWLIST_GOLDEN}\n"
            f"Removed: {L5_SUBPROCESS_ALLOWLIST_GOLDEN - L5_SUBPROCESS_ALLOWLIST}"
        )

    def test_no_unexpected_additions(self):
        """No unexpected additions to L5 allowlist."""
        added = L5_SUBPROCESS_ALLOWLIST - L5_SUBPROCESS_ALLOWLIST_GOLDEN
        assert len(added) == 0, f"Unexpected additions to L5 allowlist: {added}"

    def test_no_unexpected_removals(self):
        """No unexpected removals from L5 allowlist."""
        removed = L5_SUBPROCESS_ALLOWLIST_GOLDEN - L5_SUBPROCESS_ALLOWLIST
        assert len(removed) == 0, f"Unexpected removals from L5 allowlist: {removed}"


class TestL6HybridAllowlistGolden:
    """Tests for L6 hybrid allowlist golden."""

    def test_allowlist_matches_golden(self):
        """L6_HYBRID_ALLOWLIST must match golden."""
        assert L6_HYBRID_ALLOWLIST == L6_HYBRID_ALLOWLIST_GOLDEN, (
            f"L6_HYBRID_ALLOWLIST changed!\n"
            f"Actual: {L6_HYBRID_ALLOWLIST}\n"
            f"Golden: {L6_HYBRID_ALLOWLIST_GOLDEN}"
        )


class TestScriptsForbiddenPatternsGolden:
    """Tests for scripts forbidden patterns golden."""

    def test_patterns_match_golden(self):
        """SCRIPTS_FORBIDDEN_PATTERNS must match golden."""
        assert list(SCRIPTS_FORBIDDEN_PATTERNS) == SCRIPTS_FORBIDDEN_PATTERNS_GOLDEN, (
            f"SCRIPTS_FORBIDDEN_PATTERNS changed!\n"
            f"Actual: {SCRIPTS_FORBIDDEN_PATTERNS}\n"
            f"Golden: {SCRIPTS_FORBIDDEN_PATTERNS_GOLDEN}"
        )


class TestLayerRootsGolden:
    """Tests for layer roots golden."""

    def test_layer_roots_match_golden(self):
        """LAYER_ROOTS must match golden."""
        assert LAYER_ROOTS == LAYER_ROOTS_GOLDEN, (
            f"LAYER_ROOTS changed!\nActual: {LAYER_ROOTS}\nGolden: {LAYER_ROOTS_GOLDEN}"
        )


class TestRequiredLCDSubfoldersGolden:
    """Tests for required LCD subfolders golden."""

    def test_lcd_subfolders_match_golden(self):
        """REQUIRED_LCD_SUBFOLDERS must match golden."""
        assert REQUIRED_LCD_SUBFOLDERS == REQUIRED_LCD_SUBFOLDERS_GOLDEN, (
            f"REQUIRED_LCD_SUBFOLDERS changed!\n"
            f"Actual: {REQUIRED_LCD_SUBFOLDERS}\n"
            f"Golden: {REQUIRED_LCD_SUBFOLDERS_GOLDEN}"
        )


class TestLeafDomainsGolden:
    """Tests for leaf domains golden."""

    def test_leaf_domains_match_golden(self):
        """LEAF_DOMAINS_NO_LCD must match golden."""
        assert LEAF_DOMAINS_NO_LCD == LEAF_DOMAINS_NO_LCD_GOLDEN, (
            f"LEAF_DOMAINS_NO_LCD changed!\n"
            f"Actual: {LEAF_DOMAINS_NO_LCD}\n"
            f"Golden: {LEAF_DOMAINS_NO_LCD_GOLDEN}"
        )
