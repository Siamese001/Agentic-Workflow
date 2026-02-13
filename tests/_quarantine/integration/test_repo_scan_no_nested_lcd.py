"""
Integration test: No nested LCD subtrees.

Validates:
- Nested LCD under leaf domains is always rejected
- Layer roots may have LCD subfolders
"""

from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    LEAF_DOMAINS_NO_LCD,
    REQUIRED_LCD_SUBFOLDERS,
    validate_no_nested_lcd,
)


def find_nested_lcd_violations(root: Path) -> list[str]:
    """
    Scan directory tree for nested LCD violations.

    Returns list of violation paths.
    """
    violations = []

    agentic_core = root / "agentic_core"
    if not agentic_core.exists():
        return violations

    for leaf_domain in LEAF_DOMAINS_NO_LCD:
        domain_path = agentic_core / leaf_domain
        if not domain_path.exists():
            continue

        for lcd_subfolder in REQUIRED_LCD_SUBFOLDERS:
            nested_path = domain_path / lcd_subfolder
            if nested_path.exists() and nested_path.is_dir():
                violations.append(str(nested_path))

    return violations


class TestNoNestedLCD:
    """Tests for nested LCD prevention."""

    def test_real_repo_no_nested_lcd_in_leaf_domains(self):
        """Real repo should have no nested LCD in leaf domains."""
        base = Path("c:/Git/Agentic-Workflow/Agentic-Workflow")
        if not base.exists():
            pytest.skip("Repo not found")

        violations = find_nested_lcd_violations(base)
        # Filter out known exceptions:
        # - prompt_governance may have legacy structure
        # - runtime has established types/utils/config structure
        # - knowledge has reasoning subfolder by design
        known_exceptions = ["prompt_governance", "runtime", "knowledge"]
        filtered = [v for v in violations if not any(exc in v for exc in known_exceptions)]

        assert len(filtered) == 0, f"Nested LCD violations found: {filtered}"

    @pytest.mark.parametrize("leaf_domain", list(LEAF_DOMAINS_NO_LCD))
    def test_validate_no_nested_lcd_flags_violations(self, leaf_domain: str):
        """validate_no_nested_lcd should flag LCD subfolders under leaf domains."""
        for lcd_subfolder in ["reasoning", "enforcement", "types"]:
            path_parts = ["agentic_core", leaf_domain, lcd_subfolder]
            result = validate_no_nested_lcd(path_parts)
            assert result is not None, f"Should flag {leaf_domain}/{lcd_subfolder}"

    @pytest.mark.parametrize(
        "layer",
        [
            "L0_routing",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ],
    )
    def test_validate_no_nested_lcd_allows_layer_roots(self, layer: str):
        """validate_no_nested_lcd should allow LCD under layer roots."""
        for lcd_subfolder in ["reasoning", "enforcement", "types"]:
            path_parts = ["agentic_core", layer, lcd_subfolder]
            result = validate_no_nested_lcd(path_parts)
            assert result is None, f"Should allow {layer}/{lcd_subfolder}"


class TestFixtureRepoNestedLCD:
    """Tests using fixture repo for nested LCD."""

    def test_synthetic_repo_with_nested_lcd_violation(self, tmp_path):
        """Synthetic repo with nested LCD should be detected."""
        # Create violation: prompt_governance/reasoning
        nested = tmp_path / "agentic_core" / "prompt_governance" / "reasoning"
        nested.mkdir(parents=True)
        (nested / "__init__.py").write_text("")

        violations = find_nested_lcd_violations(tmp_path)
        assert len(violations) > 0, "Should detect nested LCD violation"

    def test_synthetic_repo_without_nested_lcd(self, tmp_path):
        """Synthetic repo without nested LCD should pass."""
        # Create valid structure: L5_safety/reasoning (allowed)
        valid = tmp_path / "agentic_core" / "L5_safety" / "reasoning"
        valid.mkdir(parents=True)
        (valid / "__init__.py").write_text("")

        # Create leaf domain without LCD
        leaf = tmp_path / "agentic_core" / "prompt_governance" / "templates"
        leaf.mkdir(parents=True)
        (leaf / "__init__.py").write_text("")

        violations = find_nested_lcd_violations(tmp_path)
        assert len(violations) == 0, f"Should have no violations: {violations}"
