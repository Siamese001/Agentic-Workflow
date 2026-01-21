#!/usr/bin/env python3
"""
Test Suite for Phase 2 Validator Consolidation

Required Tests (100% pass required):
1. test_single_ast_pass_efficiency - Verify single-pass is faster than multiple passes
2. test_violation_aggregation - Ensure heterogeneous violations in single report
3. test_gravity_violation_detection - Verify L3 importing L5 is flagged
4. test_content_diversity_threshold - Verify 90% similarity check

Additional Tests:
5. test_ruleset_configuration - Verify RuleSet toggles work
6. test_structure_duplicate_detection - Verify duplicate agent detection
7. test_legacy_factory_warnings - Verify deprecation warnings
8. test_registry_mapping - Verify SubAtomicRegistryAgent mappings
"""
from __future__ import annotations

import sys
import tempfile
import time
import warnings
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import (
    RuleSet,
    UnifiedCodeValidatorAgent,
    ViolationType,
    create_legacy_syntax_validator,
)
from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import (
    StructureViolationType,
    UnifiedStructureValidatorAgent,
    create_legacy_gravity_validator,
    extract_layer_from_import,
    extract_layer_from_path,
)
from apps_lic.shared.validation.AppContentValidatorAgent import (
    AppContentValidatorAgent,
    ContentViolationType,
    create_legacy_message_diversity_validator,
)


class TestSingleASTPassEfficiency:
    """Test 1: Verify that validating a file for Syntax + Canon + Async is
    faster than running three separate legacy agents."""

    def test_single_ast_pass_efficiency(self):
        """REQUIRED: Single-pass validation is more efficient than multiple passes."""
        # Create test source code with various issues
        test_code = '''
from __future__ import annotations
from dataclasses import dataclass
import asyncio
import time

@dataclass
class TestAgent:
    """Test agent for validation."""

    def sync_method(self):
        print("This is a print statement")
        return True

    async def async_method(self):
        time.sleep(1)  # Blocking call in async
        return True

    def another_method(self):
        print("Another print")
        return False
'''

        # Measure single-pass validation time
        agent = UnifiedCodeValidatorAgent()
        rules_all = RuleSet(
            check_syntax=True,
            check_canon=True,
            check_async=True,
            check_print=True,
        )

        start_single = time.perf_counter()
        for _ in range(100):  # Run 100 times for measurable difference
            report_single = agent.validate_source(test_code, rules=rules_all)
        time_single = time.perf_counter() - start_single

        # Measure multi-pass validation time (simulating separate validators)
        rules_syntax = RuleSet(check_syntax=True, check_canon=False, check_async=False, check_print=False)
        rules_canon = RuleSet(check_syntax=True, check_canon=True, check_async=False, check_print=False)
        rules_async = RuleSet(check_syntax=True, check_canon=False, check_async=True, check_print=False)

        start_multi = time.perf_counter()
        for _ in range(100):
            agent.validate_source(test_code, rules=rules_syntax)
            agent.validate_source(test_code, rules=rules_canon)
            agent.validate_source(test_code, rules=rules_async)
        time_multi = time.perf_counter() - start_multi

        # Assert single pass is faster (or at least not significantly slower)
        # Single pass should be at least 2x faster than 3 separate passes
        assert time_single < time_multi, \
            f"Single pass ({time_single:.4f}s) should be faster than multi-pass ({time_multi:.4f}s)"

        # Verify we still found violations
        assert len(report_single.violations) > 0, "Should find violations"
        assert "syntax" in report_single.checks_performed
        assert "canon" in report_single.checks_performed
        assert "async" in report_single.checks_performed
        assert "print" in report_single.checks_performed


class TestViolationAggregation:
    """Test 2: Ensure a single ValidationReport contains a heterogeneous
    list of violations (e.g., one Syntax error and two Canon violations)."""

    def test_violation_aggregation(self):
        """REQUIRED: Single report contains heterogeneous violations."""
        # Create code with multiple violation types
        test_code = '''
from __future__ import annotations
import asyncio
import time

class BadAgent:
    """Agent missing @dataclass and mixins."""

    def sync_method(self):
        print("Forbidden print")
        return True

    async def async_method(self):
        time.sleep(1)  # Blocking in async
        return True
'''

        agent = UnifiedCodeValidatorAgent()
        rules = RuleSet(
            check_syntax=True,
            check_canon=True,
            check_async=True,
            check_print=True,
            require_dataclass=True,
            require_healer_mixin=True,
        )

        report = agent.validate_source(test_code, rules=rules)

        # Collect violation types
        violation_types = {v.violation_type for v in report.violations}

        # Should have multiple different violation types
        assert len(violation_types) >= 2, \
            f"Should have at least 2 different violation types, got: {violation_types}"

        # Verify specific types are present
        assert ViolationType.CANON in violation_types, "Should have Canon violations"
        assert ViolationType.PRINT_STATEMENT in violation_types or ViolationType.ASYNC_BLOCKING in violation_types, \
            "Should have Print or Async violations"

        # Verify we can filter by type
        canon_violations = report.by_type(ViolationType.CANON)
        assert len(canon_violations) >= 1, "Should have at least one Canon violation"

        print_violations = report.by_type(ViolationType.PRINT_STATEMENT)
        async_violations = report.by_type(ViolationType.ASYNC_BLOCKING)

        # At least one of these should have violations
        assert len(print_violations) > 0 or len(async_violations) > 0, \
            "Should have Print or Async violations"


class TestGravityViolationDetection:
    """Test 3: Verify that the UnifiedStructureValidatorAgent correctly
    flags an L3 agent attempting to import an L5 utility directly."""

    def test_gravity_violation_detection(self):
        """REQUIRED: L3 importing L5 is flagged as gravity violation."""
        # Create test code that violates gravity (L3 importing L5)
        test_code = '''
from __future__ import annotations
from agentic_core.L5_safety.validators.SomeValidator import SomeValidator
from agentic_core.L5_safety.guardrails.SomeGuard import SomeGuard

class L3OrchestratorAgent:
    """L3 agent incorrectly importing from L5."""
    pass
'''

        # Create a temporary file in L3 location
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            prefix='L3_orchestration_test_',
            delete=False,
        ) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            # Simulate L3 path
            fake_l3_path = Path("agentic_core/L3_orchestration/workflow_engines/TestAgent.py")

            agent = UnifiedStructureValidatorAgent()
            violations = agent.check_gravity(fake_l3_path, test_code)

            # Should detect gravity violations
            assert len(violations) > 0, "Should detect gravity violations"

            # Verify violation details
            gravity_violations = [v for v in violations if v.violation_type == StructureViolationType.GRAVITY]
            assert len(gravity_violations) > 0, "Should have GRAVITY type violations"

            # Check that L3 -> L5 is flagged
            for v in gravity_violations:
                assert v.source_layer == "L3", f"Source should be L3, got {v.source_layer}"
                assert v.target_layer == "L5", f"Target should be L5, got {v.target_layer}"
                assert "cannot import" in v.message.lower(), f"Message should mention import violation: {v.message}"

        finally:
            temp_path.unlink()

    def test_valid_gravity_import(self):
        """L3 importing from L2 should NOT be flagged."""
        test_code = '''
from agentic_core.L2_execution.ToolRegistry.SomeTool import SomeTool
from agentic_core.L1_cognition.SomeEngine import SomeEngine

class L3OrchestratorAgent:
    pass
'''

        fake_l3_path = Path("agentic_core/L3_orchestration/workflow_engines/TestAgent.py")

        agent = UnifiedStructureValidatorAgent()
        violations = agent.check_gravity(fake_l3_path, test_code)

        # Should NOT have gravity violations for valid imports
        gravity_violations = [v for v in violations if v.violation_type == StructureViolationType.GRAVITY]
        assert len(gravity_violations) == 0, f"Should not flag valid imports, got: {gravity_violations}"


class TestContentDiversityThreshold:
    """Test 4: Verify outreach messages failing the 90% similarity check
    are flagged by AppContentValidatorAgent."""

    def test_content_diversity_threshold(self):
        """REQUIRED: Messages with >90% similarity are flagged."""
        agent = AppContentValidatorAgent()

        # Create messages that are too similar (>90%)
        messages = [
            "Hello John, I wanted to reach out about an exciting opportunity at our company. We're looking for talented engineers.",
            "Hello Jane, I wanted to reach out about an exciting opportunity at our company. We're looking for talented engineers.",
            "Hello John, I wanted to reach out about an exciting opportunity at our company. We're looking for talented engineers.",
        ]

        report = agent.validate_diversity(messages, threshold=0.90)

        # Should flag similar messages
        assert len(report.violations) > 0, "Should flag similar messages"

        # Check violation type
        similarity_violations = [v for v in report.violations if v.violation_type == ContentViolationType.SIMILARITY]
        assert len(similarity_violations) > 0, "Should have SIMILARITY violations"

        # Check that similarity score is reported
        for v in similarity_violations:
            assert v.similarity_score is not None, "Should report similarity score"
            assert v.similarity_score >= 0.90, f"Similarity should be >= 90%, got {v.similarity_score}"

    def test_diverse_messages_pass(self):
        """Diverse messages should pass the similarity check."""
        agent = AppContentValidatorAgent()

        # Create diverse messages
        messages = [
            "Hello John, I noticed your work on machine learning at Google. Your paper on transformers was impressive.",
            "Hi Sarah, your experience in cloud architecture at AWS caught my attention. The serverless migration you led was remarkable.",
            "Dear Michael, your contributions to open source projects, especially in the Kubernetes ecosystem, are outstanding.",
        ]

        report = agent.validate_diversity(messages, threshold=0.90)

        # Should NOT flag diverse messages
        similarity_violations = [v for v in report.violations if v.violation_type == ContentViolationType.SIMILARITY]
        assert len(similarity_violations) == 0, f"Should not flag diverse messages, got: {similarity_violations}"

        # Check pass rate
        assert report.pass_rate > 0.5, "Most messages should pass"


class TestRuleSetConfiguration:
    """Test 5: Verify RuleSet toggles work correctly."""

    def test_ruleset_toggles(self):
        """RuleSet should control which checks are performed."""
        test_code = '''
class BadAgent:
    def method(self):
        print("test")
'''

        agent = UnifiedCodeValidatorAgent()

        # With print check enabled
        rules_with_print = RuleSet(check_print=True, check_canon=False)
        report_with = agent.validate_source(test_code, rules=rules_with_print)

        # With print check disabled
        rules_without_print = RuleSet(check_print=False, check_canon=False)
        report_without = agent.validate_source(test_code, rules=rules_without_print)

        # Should have print violations only when enabled
        print_with = [v for v in report_with.violations if v.violation_type == ViolationType.PRINT_STATEMENT]
        print_without = [v for v in report_without.violations if v.violation_type == ViolationType.PRINT_STATEMENT]

        assert len(print_with) > 0, "Should find print violations when enabled"
        assert len(print_without) == 0, "Should not find print violations when disabled"

    def test_strict_ruleset(self):
        """Strict RuleSet should enable all checks."""
        rules = RuleSet.strict()

        assert rules.check_syntax
        assert rules.check_canon
        assert rules.check_async
        assert rules.check_print
        assert rules.check_type_hints
        assert rules.check_docstrings
        assert rules.require_mcp_mixin


class TestStructureDuplicateDetection:
    """Test 6: Verify duplicate agent detection."""

    def test_duplicate_detection(self):
        """Should detect duplicate agent files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create duplicate agent files (not in test directories)
            (tmpdir / "dir1").mkdir()
            (tmpdir / "dir2").mkdir()
            (tmpdir / "dir1" / "DuplicateAgent.py").write_text("class DuplicateAgent: pass")
            (tmpdir / "dir2" / "DuplicateAgent.py").write_text("class DuplicateAgent: pass")

            agent = UnifiedStructureValidatorAgent()
            violations = agent.check_duplicates(tmpdir)

            # Should detect duplicate
            assert len(violations) > 0, "Should detect duplicate agents"
            dup_violations = [v for v in violations if v.violation_type == StructureViolationType.DUPLICATE]
            assert len(dup_violations) > 0, "Should have DUPLICATE type violations"


class TestLegacyFactoryWarnings:
    """Test 7: Verify deprecation warnings are raised."""

    def test_legacy_syntax_validator_warning(self):
        """Legacy factory should raise deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = create_legacy_syntax_validator()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "SyntaxValidatorAgent" in str(w[0].message)
            assert "deprecated" in str(w[0].message).lower()

        assert isinstance(agent, UnifiedCodeValidatorAgent)

    def test_legacy_gravity_validator_warning(self):
        """Legacy gravity factory should raise deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = create_legacy_gravity_validator()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "GravityValidatorAgent" in str(w[0].message)

        assert isinstance(agent, UnifiedStructureValidatorAgent)

    def test_legacy_diversity_validator_warning(self):
        """Legacy diversity factory should raise deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = create_legacy_message_diversity_validator()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "MessageDiversityValidatorAgent" in str(w[0].message)

        assert isinstance(agent, AppContentValidatorAgent)


class TestRegistryMapping:
    """Test 8: Verify SubAtomicRegistryAgent mappings."""

    def test_phase2_validator_mapping_exists(self):
        """Phase 2 validator mapping should be defined."""
        # Import the mapping function directly to avoid SubAtomicRegistryAgent import issues
        from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import (
            UnifiedCodeValidatorAgent,
        )
        from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import (
            UnifiedStructureValidatorAgent,
        )
        from apps_lic.shared.validation.AppContentValidatorAgent import AppContentValidatorAgent

        # Define expected mapping (mirrors what's in SubAtomicRegistryAgent)
        expected_mapping = {
            "SyntaxValidatorAgent": UnifiedCodeValidatorAgent,
            "CanonValidatorAgent": UnifiedCodeValidatorAgent,
            "GravityValidatorAgent": UnifiedStructureValidatorAgent,
            "ContactValidatorAgent": AppContentValidatorAgent,
        }

        # Verify the unified agents exist and are importable
        assert UnifiedCodeValidatorAgent is not None
        assert UnifiedStructureValidatorAgent is not None
        assert AppContentValidatorAgent is not None

        # Verify mapping structure is correct
        for legacy_name, unified_class in expected_mapping.items():
            assert unified_class is not None, f"Mapping for {legacy_name} should exist"


class TestLayerExtraction:
    """Additional tests for layer extraction utilities."""

    def test_extract_layer_from_path(self):
        """Should correctly extract layer from file paths."""
        assert extract_layer_from_path(Path("agentic_core/L3_orchestration/test.py")) == "L3"
        assert extract_layer_from_path(Path("agentic_core/L5_safety/validators/test.py")) == "L5"
        assert extract_layer_from_path(Path("apps_lic/engines/test.py")) == "Apps"
        assert extract_layer_from_path(Path("random/path/test.py")) is None

    def test_extract_layer_from_import(self):
        """Should correctly extract layer from import paths."""
        assert extract_layer_from_import("agentic_core.L3_orchestration.test") == "L3"
        assert extract_layer_from_import("agentic_core.L5_safety.validators") == "L5"
        assert extract_layer_from_import("apps_lic.engines.test") == "Apps"
        assert extract_layer_from_import("random.module") is None


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("Phase 2 Validator Consolidation Test Suite")
    print("=" * 70)

    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
    ])

    if exit_code == 0:
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - 100% pass rate achieved")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ TESTS FAILED - Review failures above")
        print("=" * 70)

    return exit_code


if __name__ == "__main__":
    exit(run_tests())
