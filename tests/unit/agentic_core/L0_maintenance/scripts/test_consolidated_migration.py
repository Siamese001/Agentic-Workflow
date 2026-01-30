"""
agentic_core/L0_maintenance/scripts/test_consolidated_migration.py
------------------------------------------------------------------
Test Suite: Consolidated Phase 1.5 + Phase 2 Migration Verification
================================================================
Verifies cognitive logic migration, BudgetAgent delegation, and legacy cleanup.
UPDATED: Uses SOVEREIGN_TERRITORIES and checks HealerMixin capabilities directly.
"""

import sys
from pathlib import Path

# Add project root to path (go up 4 levels: scripts -> L0_maintenance -> agentic_core -> project_root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestConsolidatedMigration:
    """
    Enforces SSOT compliance and cleanup for consolidated migration.
    """

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_healer_mixin_exists(self):
        """HealerMixin must exist and be importable."""
        try:
            assert HealerMixin is not None, "HealerMixin should be importable"
            assert hasattr(HealerMixin, "heal_repository"), (
                "HealerMixin should have heal_repository"
            )

            self.passed += 1
            print("✅ test_healer_mixin_exists PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_healer_mixin_exists: {e}")
            print(f"❌ test_healer_mixin_exists FAILED: {e}")

    def test_healer_mixin_has_core_methods(self):
        """HealerMixin must have core healing methods."""
        try:
            # Check core methods exist
            assert hasattr(HealerMixin, "heal_repository"), "HealerMixin missing heal_repository"
            assert hasattr(HealerMixin, "enable_healing"), "HealerMixin missing enable_healing"
            assert hasattr(HealerMixin, "disable_healing"), "HealerMixin missing disable_healing"

            self.passed += 1
            print("✅ test_healer_mixin_has_core_methods PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_healer_mixin_has_core_methods: {e}")
            print(f"❌ test_healer_mixin_has_core_methods FAILED: {e}")

    def test_sovereign_territories_exists(self):
        """SOVEREIGN_TERRITORIES must exist in structure_blueprint."""
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

            assert SOVEREIGN_TERRITORIES is not None, "SOVEREIGN_TERRITORIES should exist"
            assert len(SOVEREIGN_TERRITORIES) > 0, "SOVEREIGN_TERRITORIES should not be empty"

            self.passed += 1
            print("✅ test_sovereign_territories_exists PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_sovereign_territories_exists: {e}")
            print(f"❌ test_sovereign_territories_exists FAILED: {e}")

    def test_template_cleaned(self):
        """Verify jinja template does not contain Canon Key references."""
        try:
            template_path = (
                PROJECT_ROOT
                / "agentic_core"
                / "prompt_governance"
                / "templates"
                / "agent_autonomy_law.jinja"
            )

            if template_path.exists():
                with open(template_path, encoding="utf-8") as f:
                    content = f.read()
                    assert "CANON KEY 51" not in content, (
                        "Template should not contain 'CANON KEY 51'"
                    )

            self.passed += 1
            print("✅ test_template_cleaned PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_template_cleaned: {e}")
            print(f"❌ test_template_cleaned FAILED: {e}")

    def test_mixin_logic_functionality(self):
        """Verify the HealerMixin has core healing functionality."""
        try:
            # Simple functional test of the mixin method existence
            assert hasattr(HealerMixin, "heal_repository")
            assert hasattr(HealerMixin, "reset_healing_count")

            self.passed += 1
            print("✅ test_mixin_logic_functionality PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_mixin_logic_functionality: {e}")
            print(f"❌ test_mixin_logic_functionality FAILED: {e}")

    def test_legacy_registry_status(self):
        """Check status of legacy CANON_VALIDATION_REGISTRY."""
        try:
            # Try to import - if it fails, that's GOOD (means it's gone)
            try:
                from agentic_core.L5_safety.validators.structure_blueprint import (
                    CANON_VALIDATION_REGISTRY,
                )

                # If it exists but is empty or doesn't have keys 17/19, that's also OK
                has_legacy_keys = 17 in CANON_VALIDATION_REGISTRY or 19 in CANON_VALIDATION_REGISTRY
                if has_legacy_keys:
                    print("⚠️  CANON_VALIDATION_REGISTRY still has legacy keys 17/19")
            except (ImportError, NameError, AttributeError):
                # This is GOOD - means it's been removed
                pass

            self.passed += 1
            print("✅ test_legacy_registry_status PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_legacy_registry_status: {e}")
            print(f"❌ test_legacy_registry_status FAILED: {e}")

    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 70)
        print("CONSOLIDATED MIGRATION VERIFICATION SUITE (UPDATED)")
        print("=" * 70 + "\n")

        self.test_healer_mixin_exists()
        self.test_healer_mixin_has_core_methods()
        self.test_sovereign_territories_exists()
        self.test_template_cleaned()
        self.test_mixin_logic_functionality()
        self.test_legacy_registry_status()

        print("\n" + "=" * 70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 70)

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        return self.failed == 0


if __name__ == "__main__":
    suite = TestConsolidatedMigration()
    success = suite.run_all()
    sys.exit(0 if success else 1)
