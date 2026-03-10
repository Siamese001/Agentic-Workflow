"""
Test nested LCD prevention policy.

Validates:
- Leaf domains cannot sprout LCD subtrees
- Only L0-L6 layer roots may have LCD subfolders
- validate_no_nested_lcd() correctly detects violations
"""

import pytest

from agentic_core.L5_safety.config.structure_blueprint import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    LEAF_DOMAINS_NO_LCD,
    validate_no_nested_lcd,
)
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR


class TestLeafDomainsNoLCD:
    """Tests for LEAF_DOMAINS_NO_LCD constant."""

    def test_leaf_domains_contains_expected(self):
        """LEAF_DOMAINS_NO_LCD contains known leaf domains."""
        expected = {
            "prompt_governance",
            "knowledge",
            "mixins",
            "runtime",
            "interfaces",
            "base_agents",
            "config",
        }
        assert expected.issubset(LEAF_DOMAINS_NO_LCD)

    def test_leaf_domains_is_frozenset(self):
        """LEAF_DOMAINS_NO_LCD must be immutable."""
        assert isinstance(LEAF_DOMAINS_NO_LCD, frozenset)


class TestValidateNoNestedLCD:
    """Tests for validate_no_nested_lcd() function."""

    @pytest.mark.parametrize(
        "leaf_domain,lcd_subfolder",
        [
            ("prompt_governance", "reasoning"),
            ("prompt_governance", "enforcement"),
            ("prompt_governance", "utils"),
            ("knowledge", "types"),
            ("runtime", "validators"),
            ("base_agents", "config"),
        ],
    )
    def test_nested_lcd_under_leaf_domain_flagged(self, leaf_domain: str, lcd_subfolder: str):
        """LCD subfolders under leaf domains must be flagged as violations."""
        path_parts = [AGENTIC_CORE_DIR, leaf_domain, lcd_subfolder]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None, f"Expected violation for {leaf_domain}/{lcd_subfolder}"
        assert result["domain"] == leaf_domain
        assert result["illegal_subfolder"] == lcd_subfolder

    @pytest.mark.parametrize(
        "layer,lcd_subfolder",
        [
            ("L0_routing", "reasoning"),
            ("L1_cognition", "enforcement"),
            ("L2_execution", "types"),
            ("L3_orchestration", "config"),
            ("L4_state", "validators"),
            ("L5_safety", "utils"),
            ("L6_observability", "reasoning"),
        ],
    )
    def test_lcd_under_layer_root_allowed(self, layer: str, lcd_subfolder: str):
        """LCD subfolders under layer roots are allowed."""
        path_parts = [AGENTIC_CORE_DIR, layer, lcd_subfolder]
        result = validate_no_nested_lcd(path_parts)
        assert result is None, f"Unexpected violation for {layer}/{lcd_subfolder}"

    def test_deeply_nested_lcd_allowed_under_layer(self):
        """LCD subfolders nested under layer scripts are allowed."""
        # L0_routing/scripts/prompt_governance is OK because L0 is a layer root
        path_parts = [AGENTIC_CORE_DIR, "L0_routing", "scripts", "prompt_governance"]
        result = validate_no_nested_lcd(path_parts)
        # This should be allowed because L0_routing is a layer root ancestor
        assert result is None

    def test_non_lcd_subfolder_under_leaf_allowed(self):
        """Non-LCD subfolders under leaf domains are allowed."""
        # prompt_governance/templates is not an LCD subfolder
        path_parts = [AGENTIC_CORE_DIR, "prompt_governance", "templates"]
        result = validate_no_nested_lcd(path_parts)
        assert result is None

    def test_empty_path_parts(self):
        """Empty path parts should not cause errors."""
        result = validate_no_nested_lcd([])
        assert result is None

    def test_single_element_path(self):
        """Single element path should not cause errors."""
        result = validate_no_nested_lcd([AGENTIC_CORE_DIR])
        assert result is None


class TestNestedLCDViolationMessage:
    """Tests for violation message content."""

    def test_violation_message_contains_domain(self):
        """Violation message should mention the offending domain."""
        path_parts = [AGENTIC_CORE_DIR, "prompt_governance", "reasoning"]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None
        assert "prompt_governance" in result["message"]

    def test_violation_message_contains_subfolder(self):
        """Violation message should mention the illegal subfolder."""
        path_parts = [AGENTIC_CORE_DIR, "knowledge", "enforcement"]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None
        assert "enforcement" in result["message"]

    def test_violation_message_mentions_layer_roots(self):
        """Violation message should mention that only layer roots may have LCD."""
        path_parts = [AGENTIC_CORE_DIR, "runtime", "validators"]
        result = validate_no_nested_lcd(path_parts)
        assert result is not None
        assert "L0" in result["message"] or "layer roots" in result["message"].lower()
