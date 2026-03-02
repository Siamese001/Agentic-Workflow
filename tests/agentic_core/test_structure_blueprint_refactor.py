"""
Regression Tests for Structure Blueprint Refactor

Tests behavioral equivalence between the new modular package and the
original monolithic module. Verifies:
1. All public exports are available
2. Derived registries match expected structure
3. Lazy loading works correctly
4. Import-time performance is improved
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class TestExportEquivalence:
    """Verify all public exports are available from the new package."""

    def test_layer_roots_available(self):
        """LAYER_ROOTS should be a frozenset with 7 layers."""
        from agentic_core.L5_safety.config.structure_blueprint import LAYER_ROOTS

        assert isinstance(LAYER_ROOTS, frozenset)
        assert len(LAYER_ROOTS) == 7
        assert "L0_routing" in LAYER_ROOTS
        assert "L5_safety" in LAYER_ROOTS

    def test_required_lcd_subfolders_available(self):
        """REQUIRED_LCD_SUBFOLDERS should have 6 canonical folders."""
        from agentic_core.L5_safety.config.structure_blueprint import REQUIRED_LCD_SUBFOLDERS

        assert isinstance(REQUIRED_LCD_SUBFOLDERS, frozenset)
        assert len(REQUIRED_LCD_SUBFOLDERS) == 6
        assert "reasoning" in REQUIRED_LCD_SUBFOLDERS
        assert "enforcement" in REQUIRED_LCD_SUBFOLDERS
        assert "config" in REQUIRED_LCD_SUBFOLDERS

    def test_sovereign_territories_available(self):
        """SOVEREIGN_TERRITORIES should be a dict with expected keys."""
        from agentic_core.L5_safety.config.structure_blueprint import SOVEREIGN_TERRITORIES

        assert isinstance(SOVEREIGN_TERRITORIES, dict)
        assert "agentic_core" in SOVEREIGN_TERRITORIES
        assert "apps_rg" in SOVEREIGN_TERRITORIES
        assert "apps_lic" in SOVEREIGN_TERRITORIES
        assert "tests" in SOVEREIGN_TERRITORIES

    def test_core_subfolder_map_derived(self):
        """CORE_SUBFOLDER_MAP should be derived from SOVEREIGN_TERRITORIES."""
        from agentic_core.L5_safety.config.structure_blueprint import CORE_SUBFOLDER_MAP

        assert isinstance(CORE_SUBFOLDER_MAP, dict)
        assert "L0_routing" in CORE_SUBFOLDER_MAP
        assert "L5_safety" in CORE_SUBFOLDER_MAP

    def test_validation_functions_available(self):
        """Validation functions should be importable and callable."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            is_allowed_subfolder,
            is_layer_root,
            validate_no_nested_lcd,
        )

        assert callable(is_layer_root)
        assert callable(is_allowed_subfolder)
        assert callable(validate_no_nested_lcd)

        assert is_layer_root("L5_safety") is True
        assert is_layer_root("not_a_layer") is False
        assert is_allowed_subfolder("L5_safety", "reasoning") is True

    def test_path_constants_available(self):
        """Path constants should be available."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            AGENTIC_CORE_DIR,
            APPS_RG_DIR,
            L5_SAFETY_DIR,
        )

        assert AGENTIC_CORE_DIR == "agentic_core"
        assert APPS_RG_DIR == "apps_rg"
        assert L5_SAFETY_DIR == "agentic_core/L5_safety"

    def test_allowlists_path_based(self):
        """Allowlists should use repo-relative paths."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            L5_SUBPROCESS_ALLOWLIST,
            L6_HYBRID_ALLOWLIST,
        )

        assert isinstance(L5_SUBPROCESS_ALLOWLIST, frozenset)
        assert isinstance(L6_HYBRID_ALLOWLIST, frozenset)

        for path in L5_SUBPROCESS_ALLOWLIST:
            assert "/" in path, f"Path should be repo-relative: {path}"
            assert path.startswith("agentic_core/"), f"L5 path should start with agentic_core/: {path}"


class TestDerivedRegistries:
    """Verify derived registries are computed correctly."""

    def test_core_subfolder_map_has_lcd_folders(self):
        """Each layer in CORE_SUBFOLDER_MAP should have LCD subfolders."""
        from agentic_core.L5_safety.config.structure_blueprint import CORE_SUBFOLDER_MAP

        lcd_folders = {"config", "types", "reasoning", "enforcement", "validators", "utils"}

        for layer in [
            "L0_routing",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ]:
            if layer in CORE_SUBFOLDER_MAP:
                layer_folders = set(CORE_SUBFOLDER_MAP[layer])
                assert lcd_folders.issubset(layer_folders), (
                    f"{layer} missing LCD folders: {lcd_folders - layer_folders}"
                )

    def test_verify_derived_registries_passes(self):
        """verify_derived_registries should return no discrepancies."""
        from agentic_core.L5_safety.config.structure_blueprint import verify_derived_registries

        discrepancies = verify_derived_registries()
        assert discrepancies == [], f"Derived registry discrepancies: {discrepancies}"


class TestLazyLoading:
    """Verify lazy loading works correctly."""

    def test_lazy_loaders_return_same_instance(self):
        """Lazy loaders should return cached instances."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_core_subfolder_map,
            get_sovereign_territories,
        )

        territories1 = get_sovereign_territories()
        territories2 = get_sovereign_territories()
        assert territories1 is territories2

        map1 = get_core_subfolder_map()
        map2 = get_core_subfolder_map()
        assert map1 is map2

    def test_classification_patterns_lazy_compiled(self):
        """Classification patterns should compile lazily."""
        from agentic_core.L5_safety.config.structure_blueprint.classification import (
            CLASSIFICATION_SUFFIX_PATTERNS,
            get_classification_suffix_patterns_compiled,
        )

        assert isinstance(CLASSIFICATION_SUFFIX_PATTERNS, dict)
        for key in CLASSIFICATION_SUFFIX_PATTERNS:
            assert isinstance(key, str), "Patterns should be strings before compilation"

        compiled = get_classification_suffix_patterns_compiled()
        for pattern in compiled:
            assert hasattr(pattern, "match"), "Compiled patterns should have match method"


class TestValidateNoNestedLcd:
    """Test the validate_no_nested_lcd function."""

    def test_valid_path_returns_none(self):
        """Valid paths should return None."""
        from agentic_core.L5_safety.config.structure_blueprint import validate_no_nested_lcd

        result = validate_no_nested_lcd(["agentic_core", "L5_safety", "reasoning", "SomeAgent.py"])
        assert result is None

    def test_leaf_domain_with_lcd_returns_violation(self):
        """Leaf domain with LCD subfolder should return violation."""
        from agentic_core.L5_safety.config.structure_blueprint import validate_no_nested_lcd

        result = validate_no_nested_lcd(["agentic_core", "mixins", "reasoning", "SomeMixin.py"])
        assert result is not None
        assert result["domain"] == "mixins"
        assert result["illegal_subfolder"] == "reasoning"


class TestImportPerformance:
    """Test import-time performance improvements."""

    def test_ssot_module_imports_fast(self):
        """SSOT module should import in under 100ms."""
        import importlib
        import sys

        module_name = "agentic_core.L5_safety.config.structure_blueprint.ssot"
        if module_name in sys.modules:
            del sys.modules[module_name]

        start = time.perf_counter()
        importlib.import_module(module_name)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.1, f"SSOT import took {elapsed:.3f}s, expected < 0.1s"

    def test_package_init_imports_fast(self):
        """Package __init__ should import in under 200ms."""
        import importlib
        import sys

        module_name = "agentic_core.L5_safety.config.structure_blueprint"
        if module_name in sys.modules:
            del sys.modules[module_name]

        start = time.perf_counter()
        importlib.import_module(module_name)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.2, f"Package import took {elapsed:.3f}s, expected < 0.2s"


class TestTypeDefinitions:
    """Test TypedDict definitions are available."""

    def test_subfolder_definition_available(self):
        """SubfolderDefinition TypedDict should be importable."""
        from agentic_core.L5_safety.config.structure_blueprint import SubfolderDefinition

        assert SubfolderDefinition is not None

    def test_territory_definition_available(self):
        """TerritoryDefinition TypedDict should be importable."""
        from agentic_core.L5_safety.config.structure_blueprint import TerritoryDefinition

        assert TerritoryDefinition is not None
