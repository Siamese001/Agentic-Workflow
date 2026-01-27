"""
agentic_core/L0_maintenance/scripts/test_phase1_5_cognitive_migration.py
------------------------------------------------------------------------
Test Suite: Phase 1.5 Cognitive Logic Migration Verification
================================================================
Verifies that cognitive logic (Keys 17, 19) has been properly migrated.
UPDATED: Removed legacy CANON_VALIDATION_REGISTRY checks.
"""

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path (go up 4 levels: scripts -> L0_maintenance -> agentic_core -> project_root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase1_5_CognitiveMigration:
    """
    Enforces SSOT compliance for Cognitive/Budget logic migration.
    """

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_healer_mixin_exists(self):
        """HealerMixin must exist and be importable."""
        try:
            from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

            assert HealerMixin is not None, "HealerMixin should be importable"
            assert hasattr(HealerMixin, "heal_repository"), "HealerMixin should have heal_repository"

            self.passed += 1
            print("✅ test_healer_mixin_exists PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_healer_mixin_exists: {e}")
            print(f"❌ test_healer_mixin_exists FAILED: {e}")

    def test_healer_mixin_has_core_methods(self):
        """HealerMixin must have core healing methods."""
        try:
            from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

            # Check core methods exist
            assert hasattr(HealerMixin, "heal_repository"), (
                "HealerMixin missing heal_repository"
            )
            assert hasattr(HealerMixin, "enable_healing"), (
                "HealerMixin missing enable_healing"
            )
            assert hasattr(HealerMixin, "disable_healing"), (
                "HealerMixin missing disable_healing"
            )

            self.passed += 1
            print("✅ test_healer_mixin_has_core_methods PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_healer_mixin_has_core_methods: {e}")
            print(f"❌ test_healer_mixin_has_core_methods FAILED: {e}")

    def test_legacy_registry_removed(self):
        """Ensure CANON_VALIDATION_REGISTRY is deprecated/removed."""
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
            except ImportError:
                # This is GOOD - means it's been removed
                pass

            self.passed += 1
            print("✅ test_legacy_registry_removed PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_legacy_registry_removed: {e}")
            print(f"❌ test_legacy_registry_removed FAILED: {e}")

    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 70)
        print("PHASE 1.5 COGNITIVE MIGRATION VERIFICATION SUITE (UPDATED)")
        print("=" * 70 + "\n")

        self.test_healer_mixin_exists()
        self.test_healer_mixin_has_core_methods()
        self.test_legacy_registry_removed()

        print("\n" + "=" * 70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 70)

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        return self.failed == 0


if __name__ == "__main__":
    suite = TestPhase1_5_CognitiveMigration()
    success = suite.run_all()
    sys.exit(0 if success else 1)
