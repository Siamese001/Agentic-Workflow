"""
Test Suite: Phase 1.5 Cognitive Logic Migration Verification
================================================================
Verifies that cognitive logic (Keys 17, 19) has been properly migrated
from BudgetAgent to HealerMixin and BudgetAgent now delegates to SSOT.

Run: python scripts/test_phase1_5_cognitive_migration.py
"""

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase1_5_CognitiveMigration:
    """
    Enforces SSOT compliance for Cognitive/Budget logic migration.
    """

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_budget_agent_inherits_mixin(self):
        """BudgetAgent must inherit HealerMixin to access registry."""
        try:
            from agentic_core.L1_cognition.thought_engine.BudgetAgent import BudgetAgent
            from agentic_core.base_agents.healer_mixin import HealerMixin

            assert issubclass(BudgetAgent, HealerMixin), "BudgetAgent must inherit HealerMixin"

            self.passed += 1
            print("✅ test_budget_agent_inherits_mixin PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_budget_agent_inherits_mixin: {e}")
            print(f"❌ test_budget_agent_inherits_mixin FAILED: {e}")

    def test_logic_moved_to_mixin(self):
        """Logic must exist in Mixin, NOT locally in BudgetAgent."""
        try:
            from agentic_core.L1_cognition.thought_engine.BudgetAgent import BudgetAgent
            from agentic_core.base_agents.healer_mixin import HealerMixin

            # Check Mixin has the logic
            assert hasattr(HealerMixin, "check_key_17_no_large_functions"), (
                "HealerMixin missing check_key_17_no_large_functions"
            )
            assert hasattr(HealerMixin, "check_key_19_no_complex_functions"), (
                "HealerMixin missing check_key_19_no_complex_functions"
            )

            # Check BudgetAgent does NOT override (no local definitions)
            assert "check_key_17_no_large_functions" not in BudgetAgent.__dict__, (
                "BudgetAgent should not define check_key_17_no_large_functions locally"
            )
            assert "check_key_19_no_complex_functions" not in BudgetAgent.__dict__, (
                "BudgetAgent should not define check_key_19_no_complex_functions locally"
            )

            # Check BudgetAgent doesn't have helper methods either
            assert "_parse_file_safe" not in BudgetAgent.__dict__, (
                "BudgetAgent should not have _parse_file_safe"
            )
            assert "_calculate_complexity" not in BudgetAgent.__dict__, (
                "BudgetAgent should not have _calculate_complexity"
            )

            self.passed += 1
            print("✅ test_logic_moved_to_mixin PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_logic_moved_to_mixin: {e}")
            print(f"❌ test_logic_moved_to_mixin FAILED: {e}")

    def test_budget_delegates_to_registry(self):
        """BudgetAgent.execute() must call SSOT router."""
        try:
            from agentic_core.L1_cognition.thought_engine.BudgetAgent import BudgetAgent

            # Create mock context with python_files
            mock_ctx = MagicMock()
            mock_ctx.python_files = ["test_file.py"]

            with patch(
                "agentic_core.base_agents.healer_mixin.HealerMixin.validate_canon_key"
            ) as mock_validate:
                mock_validate.return_value = (True, [])

                agent = BudgetAgent(context=mock_ctx)
                agent.execute()

                # Verify calls to Key 17 and 19
                called_keys = [args[0] for args, _ in mock_validate.call_args_list]
                assert 17 in called_keys, "BudgetAgent should call validate_canon_key(17)"
                assert 19 in called_keys, "BudgetAgent should call validate_canon_key(19)"
                assert len(called_keys) == 2, f"Expected 2 calls, got {len(called_keys)}"

            self.passed += 1
            print("✅ test_budget_delegates_to_registry PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_budget_delegates_to_registry: {e}")
            print(f"❌ test_budget_delegates_to_registry FAILED: {e}")

    def test_mixin_logic_functionality(self):
        """Verify the migrated logic in HealerMixin actually works."""
        try:
            from agentic_core.base_agents.healer_mixin import HealerMixin

            # Create a mock agent with HealerMixin
            class MockAgent(HealerMixin):
                def __init__(self):
                    self.logger = MagicMock()

            agent = MockAgent()

            # Test Key 17 (Large Functions)
            large_function_code = '''def large_function():
    """A very large function."""
    x = 1
    x = 2
    x = 3
    x = 4
    x = 5
    x = 6
    x = 7
    x = 8
    x = 9
    x = 10
    x = 11
    x = 12
    x = 13
    x = 14
    x = 15
    x = 16
    x = 17
    x = 18
    x = 19
    x = 20
    x = 21
    x = 22
    x = 23
    x = 24
    x = 25
    x = 26
    x = 27
    x = 28
    x = 29
    x = 30
    x = 31
    x = 32
    x = 33
    x = 34
    x = 35
    x = 36
    x = 37
    x = 38
    x = 39
    x = 40
    x = 41
    x = 42
    x = 43
    x = 44
    x = 45
    x = 46
    x = 47
    x = 48
    x = 49
    x = 50
    x = 51
    x = 52
    x = 53
    x = 54
    x = 55
    return x
'''

            # Create temporary file for testing
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(large_function_code)
                temp_file = f.name

            try:
                # Test with low limit to trigger violation
                os.environ["MAX_FUNCTION_LINES"] = "30"
                ctx = {"python_files": [temp_file]}
                passed, violations = agent.check_key_17_no_large_functions(ctx)
                assert passed is False, "Key 17 should detect large function"
                assert len(violations) > 0, "Key 17 should report violations"
                assert "too large" in violations[0], (
                    "Violation message should mention function size"
                )
            finally:
                os.unlink(temp_file)
                if "MAX_FUNCTION_LINES" in os.environ:
                    del os.environ["MAX_FUNCTION_LINES"]

            # Test Key 19 (Complex Functions)
            complex_function_code = """def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                if x > 1000:
                    if x > 10000:
                        return x * 2
                    else:
                        return x * 3
                else:
                    return x * 4
            else:
                return x * 5
        else:
            return x * 6
    else:
        return x * 7
"""

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(complex_function_code)
                temp_file = f.name

            try:
                # Test with low complexity limit
                os.environ["MAX_CYCLOMATIC_COMPLEXITY"] = "5"
                ctx = {"python_files": [temp_file]}
                passed, violations = agent.check_key_19_no_complex_functions(ctx)
                assert passed is False, "Key 19 should detect complex function"
                assert len(violations) > 0, "Key 19 should report violations"
                assert "too complex" in violations[0], "Violation message should mention complexity"
            finally:
                os.unlink(temp_file)
                if "MAX_CYCLOMATIC_COMPLEXITY" in os.environ:
                    del os.environ["MAX_CYCLOMATIC_COMPLEXITY"]

            self.passed += 1
            print("✅ test_mixin_logic_functionality PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_mixin_logic_functionality: {e}")
            print(f"❌ test_mixin_logic_functionality FAILED: {e}")

    def test_budget_agent_cleaned_up(self):
        """Verify BudgetAgent no longer has AST-related imports."""
        try:
            # Read the BudgetAgent file
            budget_file = (
                PROJECT_ROOT / "agentic_core" / "L1_cognition" / "thought_engine" / "BudgetAgent.py"
            )
            with open(budget_file, encoding="utf-8") as f:
                content = f.read()

            # Should not import ast or os anymore
            assert "import ast" not in content, "BudgetAgent should not import ast"
            assert "import os" not in content, "BudgetAgent should not import os"

            # Parse AST and verify no AST-related methods
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Should not have AST parsing functions
                    assert node.name not in [
                        "_parse_file_safe",
                        "_get_function_line_count",
                        "_calculate_complexity",
                    ], f"BudgetAgent should not have {node.name}"

            self.passed += 1
            print("✅ test_budget_agent_cleaned_up PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_budget_agent_cleaned_up: {e}")
            print(f"❌ test_budget_agent_cleaned_up FAILED: {e}")

    def test_registry_still_intact(self):
        """Ensure Phase 1 registry is still intact after Phase 1.5."""
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import (
                CANON_VALIDATION_REGISTRY,
            )

            # Keys 17 and 19 should still point to correct methods
            assert 17 in CANON_VALIDATION_REGISTRY, "Key 17 missing from registry"
            assert CANON_VALIDATION_REGISTRY[17]["method"] == "check_key_17_no_large_functions", (
                "Key 17 method mismatch"
            )

            assert 19 in CANON_VALIDATION_REGISTRY, "Key 19 missing from registry"
            assert CANON_VALIDATION_REGISTRY[19]["method"] == "check_key_19_no_complex_functions", (
                "Key 19 method mismatch"
            )

            self.passed += 1
            print("✅ test_registry_still_intact PASSED")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"test_registry_still_intact: {e}")
            print(f"❌ test_registry_still_intact FAILED: {e}")

    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 70)
        print("PHASE 1.5 COGNITIVE MIGRATION VERIFICATION SUITE")
        print("=" * 70 + "\n")

        self.test_budget_agent_inherits_mixin()
        self.test_logic_moved_to_mixin()
        self.test_budget_delegates_to_registry()
        self.test_mixin_logic_functionality()
        self.test_budget_agent_cleaned_up()
        self.test_registry_still_intact()

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
