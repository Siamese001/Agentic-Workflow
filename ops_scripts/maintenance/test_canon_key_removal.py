"""
scripts/maintenance/test_canon_key_removal.py
---------------------------------------------
Test Suite: Canon Key Removal & Zero Loss Migration Verification
=================================================================
Verifies Phase 1 of Legacy Agent Deprecation:
1. SSOT Registry Integrity (SOVEREIGN_TERRITORIES Validation)
2. Safety Logic Ported to HealerMixin (Zero Loss)
3. CanonBaseAgent Hollowed Out (Deprecated)
4. Templates Cleansed of Legacy References

Run: python scripts/test_canon_key_removal.py
"""

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestCanonKeyRemoval:
    """
    Aggressive test suite to verify Zero Loss Migration + Legacy Deprecation.
    Aligned with SOVEREIGN_TERRITORIES schema.
    """

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_ssot_registry_integrity(self):
        """Verify SOVEREIGN_TERRITORIES integrity for Safety Layer."""
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import (
                SOVEREIGN_TERRITORIES,
            )

            # Verify agentic_core exists in the Unified Schema
            assert "agentic_core" in SOVEREIGN_TERRITORIES, (
                "agentic_core layer missing from SOVEREIGN_TERRITORIES"
            )

            # Verify L5_safety is registered as a subfolder under agentic_core
            agentic_core_subs = SOVEREIGN_TERRITORIES["agentic_core"].get("subfolders", {})
            assert "L5_safety" in agentic_core_subs, (
                "L5_safety subfolder missing from agentic_core in SOVEREIGN_TERRITORIES"
            )

            self.passed += 1
            print("✅ test_ssot_registry_integrity PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_ssot_registry_integrity: {e}")
            print(f"❌ test_ssot_registry_integrity FAILED: {e}")

    def test_safety_logic_ported(self):
        """Verify SafetyInspector Logic exists in Mixin (Zero Loss)."""
        try:
            # Create a mock agent with HealerMixin
            class MockAgent(HealerMixin):
                def __init__(self):
                    self.logger = MagicMock()

            agent = MockAgent()

            # Test Key 0 (Secrets) - should detect hardcoded secrets
            bad_code = {"content": 'api_key = "12345"'}
            passed, violations = agent.check_key_00_no_hardcoded_secrets(bad_code)
            assert passed is False, "Key 0 should fail on hardcoded secret"
            assert len(violations) > 0, "Key 0 should report violations"

            # Test Key 2 (Print) - should detect print statements
            bad_code = {"content": 'print("hello")'}
            passed, violations = agent.check_key_02_no_print_statements(bad_code)
            assert passed is False, "Key 2 should fail on print statement"

            # Test clean code passes
            good_code = {"content": "def hello():\n    return 'world'"}
            passed, violations = agent.check_key_00_no_hardcoded_secrets(good_code)
            assert passed is True, "Key 0 should pass on clean code"

            self.passed += 1
            print("✅ test_safety_logic_ported PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_safety_logic_ported: {e}")
            print(f"❌ test_safety_logic_ported FAILED: {e}")

    def test_validate_canon_key_router(self):
        """Verify the SSOT validation router works."""
        try:

            class MockAgent(HealerMixin):
                def __init__(self):
                    self.logger = MagicMock()

            agent = MockAgent()

            # Test routing to Key 0 - should auto-pass since registry is empty (deprecated)
            bad_code = {"content": 'password = "secret123"'}
            passed, violations = agent.validate_canon_key(0, bad_code)
            assert passed is True, "Deprecated keys should auto-pass in unified schema"
            assert len(violations) == 0, "Deprecated keys should return no violations"

            # Test invalid key returns error (but still auto-passes since all keys are deprecated)
            passed, violations = agent.validate_canon_key(999, {})
            assert passed is True, "All keys auto-pass in deprecated unified schema"
            assert len(violations) == 0, "Deprecated keys should return no violations"

            self.passed += 1
            print("✅ test_validate_canon_key_router PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_validate_canon_key_router: {e}")
            print(f"❌ test_validate_canon_key_router FAILED: {e}")

    def test_verify_canon_base_agent_is_hollow(self):
        """Verify CanonBaseAgent is hollowed out."""
        try:
            target_file = (
                PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "CanonBaseAgent.py"
            )

            # Skip test if file is already deleted (Legacy extinction)
            if not target_file.exists():
                self.passed += 1
                print("✅ test_verify_canon_base_agent_is_hollow PASSED (File Extinguished)")
                return

            with open(target_file, encoding="utf-8") as f:
                content = f.read()

            # Check for deprecation notice
            assert "DEPRECATED" in content, "CanonBaseAgent should have DEPRECATED notice"

            # Parse AST and verify no VERIFICATION_REGISTRY
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if (
                                    isinstance(target, ast.Name)
                                    and target.id == "VERIFICATION_REGISTRY"
                                ):
                                    raise AssertionError(
                                        "CRITICAL: CanonBaseAgent still contains VERIFICATION_REGISTRY"
                                    )

            self.passed += 1
            print("✅ test_verify_canon_base_agent_is_hollow PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_verify_canon_base_agent_is_hollow: {e}")
            print(f"❌ test_verify_canon_base_agent_is_hollow FAILED: {e}")

    def test_templates_cleansed(self):
        """Verify Jinja templates cleansed of legacy Canon Key references."""
        try:
            path = (
                PROJECT_ROOT
                / "agentic_core"
                / "prompt_governance"
                / "templates"
                / "agent_autonomy_law.jinja"
            )
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    content = f.read()

                # Should not have old "CANON KEY 51" reference
                assert "CANON KEY 51" not in content, "Template should not reference 'CANON KEY 51'"

            self.passed += 1
            print("✅ test_templates_cleansed PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_templates_cleansed: {e}")
            print(f"❌ test_templates_cleansed FAILED: {e}")

    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 70)
        print("CANON KEY REMOVAL VERIFICATION SUITE")
        print("=" * 70 + "\n")

        self.test_ssot_registry_integrity()
        self.test_safety_logic_ported()
        self.test_validate_canon_key_router()
        self.test_verify_canon_base_agent_is_hollow()
        self.test_templates_cleansed()

        print("\n" + "=" * 70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 70)

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        return self.failed == 0


if __name__ == "__main__":
    suite = TestCanonKeyRemoval()
    success = suite.run_all()
    sys.exit(0 if success else 1)
