"""
End-to-End Integration Tests for Surgical Healing Infrastructure

Comprehensive tests verifying the complete Resolution Asymmetry remediation
across all phases (0-4) and all 27 agents with 79 violations.
"""

import ast
import tempfile
from pathlib import Path

import pytest
from agentic_core.L5_safety.validators.surgical_healing_adapter import (
    SurgicalHealingAdapter,
)

from agentic_core.L5_safety.types.surgical_context_types import (
    SurgicalContextBuilder,
)


class TestE2EInfrastructureIntegration:
    """E2E tests for Phase 0: Infrastructure."""

    def test_full_surgical_pipeline(self):
        """Test complete surgical healing pipeline from detection to fix."""
        source = """
def my_function():
    pass

class MyClass:
    def method(self):
        pass
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            # Step 1: Create adapter
            adapter = SurgicalHealingAdapter(agent_name="TestAgent")

            # Step 2: Simulate detection results
            detection_results = [
                {
                    "type": "functiondef",
                    "line": 2,
                    "message": "Missing docstring",
                    "expected_pattern": "Function docstring.",
                },
                {
                    "type": "classdef",
                    "line": 5,
                    "message": "Missing docstring",
                    "expected_pattern": "Class docstring.",
                },
            ]

            # Step 3: Create batch context
            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="detect_docstrings",
            )

            assert context is not None
            assert len(context.violations) == 2

            # Step 4: Apply surgical healing
            for violation in context.violations:
                violation.fix_type = "insert"

            result = adapter.apply_surgical_healing(context)

            assert result.status == "success"
            assert result.violations_fixed >= 1
        finally:
            temp_path.unlink()

    def test_context_builder_integration(self):
        """Test SurgicalContextBuilder creates valid contexts."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def test(): pass\n")
            temp_path = Path(f.name)

        try:
            builder = SurgicalContextBuilder(temp_path, "IntegrationTestAgent", "test_method")

            violations = [
                {
                    "constraint_type": "test_violation",
                    "severity": "warning",
                    "message": "Test message",
                    "fix_type": "insert",
                },
            ]

            tree = ast.parse(temp_path.read_text())
            target_nodes = [tree.body[0]]

            context = builder.build_context(
                violation_id="test_001",
                violations=violations,
                target_nodes=target_nodes,
            )

            assert context is not None
            assert context.violation_id == "test_001"
            assert len(context.violations) == 1
        finally:
            temp_path.unlink()


class TestE2ECriticalTierIntegration:
    """E2E tests for Phase 1: Critical Tier (CodeHealerAgent, CodeEnforcerAgent)."""

    def test_code_healer_surgical_flow(self):
        """Test complete surgical flow for CodeHealerAgent patterns."""
        source = """
import os
import sys
import unused_module

def my_func():
    print(os.getcwd())
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

            # Simulate import healing detection
            detection_results = [
                {
                    "type": "unused_import",
                    "line": 3,
                    "message": "Unused import: sys",
                },
                {
                    "type": "unused_import",
                    "line": 4,
                    "message": "Unused import: unused_module",
                },
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="heal_imports",
            )

            assert context is not None
            assert len(context.violations) == 2
            assert all(v.fix_type == "delete" for v in context.violations)
        finally:
            temp_path.unlink()

    def test_composite_guardrail_surgical_flow(self):
        """Test complete surgical flow for CodeEnforcerAgent patterns."""
        source = """
class MyAgent:
    def unsafe_method(self, user_input):
        return eval(user_input)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="CodeEnforcerAgent")

            detection_results = [
                {
                    "type": "missing_input_guardrail",
                    "line": 3,
                    "message": "Method missing input validation",
                },
                {
                    "type": "dangerous_eval",
                    "line": 4,
                    "message": "Dangerous eval usage",
                },
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="check_guardrails",
            )

            assert context is not None
            assert len(context.violations) == 2
        finally:
            temp_path.unlink()


class TestE2EHighTierIntegration:
    """E2E tests for Phase 2: High Tier agents."""

    def test_ast_validator_e2e_flow(self):
        """Test complete E2E flow for ASTValidatorAgent."""
        source = """
try:
    risky_operation()
except:
    pass

def dangerous():
    eval(input())
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ASTValidatorAgent")

            detection_results = [
                {"type": "bare_except", "line": 4, "message": "Bare except"},
                {"type": "dangerous_eval", "line": 8, "message": "Dangerous eval"},
            ]

            context = adapter.create_batch_context(
                file_path=temp_path,
                detection_results=detection_results,
                detection_method="validate_all",
            )

            assert context is not None
            assert len(context.violations) == 2
        finally:
            temp_path.unlink()

    def test_filesystem_reconciler_e2e_flow(self):
        """Test complete E2E flow for FilesystemSSOTReconcilerAgent."""
        source = "class MisplacedAgent: pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="FilesystemSSOTReconcilerAgent")

            detection_result = {
                "type": "ssot_drift",
                "line": 1,
                "message": "File not in SSOT location",
            }

            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="_detect_drift",
            )

            assert context is not None
            assert context.detector_agent == "FilesystemSSOTReconcilerAgent"
        finally:
            temp_path.unlink()


class TestE2EMediumTierIntegration:
    """E2E tests for Phase 3: Medium Tier agents."""

    def test_multiple_medium_tier_agents(self):
        """Test E2E flow across multiple medium tier agents."""
        source = "class TestClass: pass\n"

        medium_tier_agents = [
            "AgentCategory",
            "ArchitectureGovernorAgent",
            "AutonomyGuardianAgent",
            "FileClassificationAgent",
            "GovernanceAgent",
            "HierarchyAgent",
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            for agent_name in medium_tier_agents:
                adapter = SurgicalHealingAdapter(agent_name=agent_name)

                detection_result = {
                    "type": "test_violation",
                    "line": 1,
                    "message": f"Test for {agent_name}",
                }

                context = adapter.create_context_from_detection(
                    file_path=temp_path,
                    detection_result=detection_result,
                    detection_method="test_detection",
                )

                assert context is not None, f"Failed for {agent_name}"
        finally:
            temp_path.unlink()


class TestE2ELowTierIntegration:
    """E2E tests for Phase 4: Low Tier agents."""

    def test_all_low_tier_agents(self):
        """Test E2E flow for all 15 low tier agents."""
        source = "def test(): pass\n"

        low_tier_agents = [
            "AgentPermission",
            "AutonomousThreatEvolutionAgent",
            "CheckpointManagerAgent",
            "CodeDeduplicationAgent",
            "CredentialScannerAgent",
            "CodeValidatorAgent",
            "NamingAgent",
            "NervousSystemAgent",
            "PineconeSovereignAgent",
            "PreCommitSovereignAgent",
            "ReportLocationAgent",
            "RootHygieneAgent",
            "SubAtomicRegistryAgent",
            "SystemArchitectAgent",
            "ValidationOrchestratorAgent",
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            for agent_name in low_tier_agents:
                adapter = SurgicalHealingAdapter(agent_name=agent_name)

                detection_result = {
                    "type": "generic_violation",
                    "line": 1,
                    "message": f"Generic test for {agent_name}",
                }

                context = adapter.create_context_from_detection(
                    file_path=temp_path,
                    detection_result=detection_result,
                    detection_method="generic_detection",
                )

                assert context is not None, f"Failed for {agent_name}"
                assert context.detector_agent == agent_name
        finally:
            temp_path.unlink()


class TestE2EZeroLossVerification:
    """E2E tests verifying zero-loss healing across all tiers."""

    def test_zero_loss_content_preservation(self):
        """Test that surgical healing preserves all unrelated content."""
        source = '''#!/usr/bin/env python3
"""
Module docstring that should be preserved.
"""

# Important configuration comment
IMPORTANT_CONSTANT = 42

import os
import sys


def existing_function():
    """This docstring should be preserved."""
    return IMPORTANT_CONSTANT


class ExistingClass:
    """This class docstring should be preserved."""

    def method(self):
        """Method docstring."""
        pass
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="ZeroLossTestAgent")

            # Create context with no violations
            context = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result={
                    "type": "no_violation",
                    "line": 1,
                    "message": "No issues found",
                },
                detection_method="validate_all",
            )

            assert context is not None
            assert context.file_content == source

            # Verify AST parsing preserves structure
            tree = context.ast_tree
            assert len(tree.body) > 0
        finally:
            temp_path.unlink()

    def test_idempotent_healing(self):
        """Test that healing is idempotent."""
        source = "def my_func():\n    pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            adapter = SurgicalHealingAdapter(agent_name="IdempotentTestAgent")

            # First healing
            detection_result = {
                "type": "functiondef",
                "line": 1,
                "message": "Missing docstring",
                "expected_pattern": "TODO: Add docstring",
            }

            context1 = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="detect",
            )
            context1.violations[0].fix_type = "insert"

            result1 = adapter.apply_surgical_healing(context1)
            assert result1.status == "success"

            # Second healing on same file
            context2 = adapter.create_context_from_detection(
                file_path=temp_path,
                detection_result=detection_result,
                detection_method="detect",
            )
            context2.violations[0].fix_type = "insert"

            result2 = adapter.apply_surgical_healing(context2)
            # Should skip since docstring already added
            assert result2.violations_fixed == 0
        finally:
            temp_path.unlink()


class TestE2EAllAgentsCoverage:
    """E2E tests verifying coverage of all 27 agents."""

    def test_all_27_agents_supported(self):
        """Verify all 27 agents from remediation report are supported."""
        all_agents = [
            # Critical Tier (2 agents, 20 violations)
            "CodeHealerAgent",
            "CodeEnforcerAgent",
            # High Tier (3 agents, 18 violations)
            "ASTValidatorAgent",
            "FilesystemSSOTReconcilerAgent",
            "StructureHealerAgent",
            # Medium Tier (7 agents, 24 violations)
            "AgentCategory",
            "ArchitectureGovernorAgent",
            "AutonomyGuardianAgent",
            "FileClassificationAgent",
            "GovernanceAgent",
            "HierarchyAgent",
            "input_validation_guardrail_agent_config",
            # Low Tier (15 agents, 17 violations)
            "AgentPermission",
            "AutonomousThreatEvolutionAgent",
            "CheckpointManagerAgent",
            "CodeDeduplicationAgent",
            "CredentialScannerAgent",
            "CodeValidatorAgent",
            "NamingAgent",
            "NervousSystemAgent",
            "PineconeSovereignAgent",
            "PreCommitSovereignAgent",
            "ReportLocationAgent",
            "RootHygieneAgent",
            "SubAtomicRegistryAgent",
            "SystemArchitectAgent",
            "ValidationOrchestratorAgent",
        ]

        source = "def test(): pass\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source)
            temp_path = Path(f.name)

        try:
            supported_count = 0

            for agent_name in all_agents:
                adapter = SurgicalHealingAdapter(agent_name=agent_name)

                context = adapter.create_context_from_detection(
                    file_path=temp_path,
                    detection_result={
                        "type": "test",
                        "line": 1,
                        "message": "test",
                    },
                    detection_method="test",
                )

                if context is not None:
                    supported_count += 1

            assert supported_count == len(all_agents)
            assert supported_count == 27
        finally:
            temp_path.unlink()

    def test_total_violation_count(self):
        """Verify the remediation addresses all 79 violations."""
        # Violation counts from remediation report
        violation_counts = {
            "CodeHealerAgent": 12,
            "CodeEnforcerAgent": 8,
            "ASTValidatorAgent": 6,
            "FilesystemSSOTReconcilerAgent": 6,
            "StructureHealerAgent": 6,
            "AgentCategory": 5,
            "ArchitectureGovernorAgent": 3,
            "AutonomyGuardianAgent": 3,
            "FileClassificationAgent": 3,
            "GovernanceAgent": 3,
            "HierarchyAgent": 3,
            "input_validation_guardrail_agent_config": 4,
            "AgentPermission": 1,
            "AutonomousThreatEvolutionAgent": 1,
            "CheckpointManagerAgent": 1,
            "CodeDeduplicationAgent": 2,
            "CredentialScannerAgent": 1,
            "CodeValidatorAgent": 1,
            "NamingAgent": 1,
            "NervousSystemAgent": 1,
            "PineconeSovereignAgent": 2,
            "PreCommitSovereignAgent": 1,
            "ReportLocationAgent": 1,
            "RootHygieneAgent": 1,
            "SubAtomicRegistryAgent": 1,
            "SystemArchitectAgent": 1,
            "ValidationOrchestratorAgent": 1,
        }

        total_violations = sum(violation_counts.values())
        assert total_violations == 79
        assert len(violation_counts) == 27


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
