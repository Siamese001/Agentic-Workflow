"""
File: tests/integration/agentic_core/L0_maintenance/test_ssot_phases_v2.py
Description: Updated aggressive integration testing for Phase 2 (Write) and Phase 3 (Validation) logic.
Updated to work with @standard_heal decorator schema.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import datetime

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from agentic_core.L0_maintenance.scripts.execute_ssot import (
    execute_phase2_reconciliation,
    execute_phase3_final_validation,
    AutonomousDecisionEngine,
    RuntimeStateManager,
    ConfidenceScore,
    ReconciliationManifest,
    ASTCodeQualityValidator
)


class TestPhaseExecutionSafety:
    """
    Verifies that Phase 2 respects decision gates and Phase 3 accurately reports drift.
    """

    @pytest.fixture
    def mock_components(self, tmp_path):
        """Setup mock components for testing."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        state = RuntimeStateManager(tmp_path)
        agents = {"FixerAgent": MagicMock()}
        return engine, state, agents

    @pytest.fixture
    def sample_violations(self):
        """Create sample violations for testing."""
        return [
            {
                "file": "broken.py",
                "type": "NAMING",
                "suggested_agent": "FixerAgent",
                "severity": "medium"
            },
            {
                "file": "another_file.py", 
                "type": "HIERARCHY",
                "suggested_agent": "FixerAgent",
                "severity": "high"
            }
        ]

    def test_phase2_hard_gate_budget_exhausted(self, mock_components, sample_violations):
        """
        Critical: Phase 2 must ABORT fix if budget is exhausted, ignoring Phase 1 plan.
        """
        engine, state, agents = mock_components
        
        # Setup: Exhaust budget immediately
        engine._max_healing_operations = 0
        
        plan = {
            "violations_found": sample_violations
        }
        
        result = execute_phase2_reconciliation(
            agents, "test_zone", engine, state, plan, dry_run=False
        )
        
        # Verify HEAL_RESULT_SCHEMA compliance
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "status" in result
        assert "errors" in result
        assert "skipped" in result
        
        # Verify NO modifications occurred due to budget exhaustion
        assert result['violations_found'] == 2
        assert result['violations_fixed'] == 0
        assert result['status'] in ["ERROR", "FAIL"]
        assert result['errors'] >= 0
        
        # Verify custom fields are preserved in _raw_result
        assert '_raw_result' in result
        raw = result['_raw_result']
        assert 'modifications' in raw
        assert 'failures' in raw
        assert 'manifest' in raw
        assert len(raw['modifications']) == 0
        assert len(raw['failures']) == 2  # Both violations should fail
        
        # Verify budget exhaustion reason in failures
        for failure in raw['failures']:
            assert "Budget exceeded" in failure['reason']
        
        # Verify manifest tracking
        manifest = raw['manifest']
        assert manifest['violations']['found'] == 2
        assert manifest['violations']['attempted'] == 0
        assert manifest['violations']['failed'] == 2
        assert manifest['budget']['consumed'] == 0

    def test_phase2_hard_gate_cycle_detection(self, mock_components, sample_violations):
        """
        Critical: Phase 2 must prevent the same agent from running twice on same path if cycle detected.
        """
        engine, state, agents = mock_components
        
        plan = {
            "violations_found": [
                {"file": "A.py", "type": "R1", "suggested_agent": "FixerAgent"},
                {"file": "A.py", "type": "R2", "suggested_agent": "FixerAgent"}  # Same agent, same file
            ]
        }
        
        # Pre-fill call path to simulate cycle
        engine._call_path.add("FixerAgent")
        
        result = execute_phase2_reconciliation(
            agents, "test_zone", engine, state, plan, dry_run=False
        )
        
        # Should reject both as FixerAgent is already in call_path
        assert result['violations_found'] == 2
        assert result['violations_fixed'] == 0
        assert len(result['failures']) == 2
        for failure in result['failures']:
            assert "cycle detected" in failure['reason']

    def test_phase2_dry_run_safety(self, mock_components, sample_violations):
        """
        Critical: Dry Run must NEVER call agent.heal().
        """
        engine, state, agents = mock_components
        agent_mock = agents["FixerAgent"]
        
        plan = {
            "violations_found": sample_violations
        }
        
        # Ensure high confidence so it *would* run if not for dry_run
        with patch.object(engine, 'calculate_healing_confidence', return_value=ConfidenceScore(0.9, "OK")):
            result = execute_phase2_reconciliation(
                agents, "test_zone", engine, state, plan, dry_run=True
            )
        
        # Verify HEAL_RESULT_SCHEMA compliance
        assert result['violations_found'] == 2
        assert result['violations_fixed'] == 0  # Dry run doesn't fix
        assert result['status'] == "SKIPPED"
        assert result['skipped'] == 2
        
        # Verify dry run behavior
        assert len(result['modifications']) == 2
        for mod in result['modifications']:
            assert mod['action'] == "would_fix"
            assert mod['success'] is True
        
        # The agent.heal() method must NOT have been called
        agent_mock.heal.assert_not_called()
        
        # Verify manifest tracks dry run correctly
        manifest = result['manifest']
        assert manifest['violations']['attempted'] == 2
        assert manifest['violations']['fixed'] == 2  # Dry run counts as "successful"

    def test_phase2_confidence_threshold_blocking(self, mock_components):
        """
        Critical: Phase 2 must block low confidence fixes even if Phase 1 recommended them.
        """
        engine, state, agents = mock_components
        
        plan = {
            "violations_found": [
                {"file": "risky.py", "type": "UNKNOWN", "suggested_agent": "FixerAgent"}
            ]
        }
        
        # Mock low confidence calculation
        with patch.object(engine, 'calculate_healing_confidence', return_value=ConfidenceScore(0.3, "Too risky")):
            result = execute_phase2_reconciliation(
                agents, "test_zone", engine, state, plan, dry_run=False
            )
        
        # Should block due to low confidence
        assert result['violations_found'] == 1
        assert result['violations_fixed'] == 0
        assert result['status'] in ["ERROR", "FAIL"]
        assert len(result['modifications']) == 0
        assert len(result['failures']) == 1
        assert "Confidence too low" in result['failures'][0]['reason']
        assert result['failures'][0]['confidence'] == 0.3

    def test_phase2_agent_not_found_handling(self, mock_components):
        """
        Critical: Phase 2 must handle missing agents gracefully.
        """
        engine, state, agents = mock_components
        
        plan = {
            "violations_found": [
                {"file": "test.py", "type": "NAMING", "suggested_agent": "NonExistentAgent"}
            ]
        }
        
        result = execute_phase2_reconciliation(
            agents, "test_zone", engine, state, plan, dry_run=False
        )
        
        # Should fail gracefully with agent not found error
        assert result['violations_found'] == 1
        assert result['violations_fixed'] == 0
        assert result['status'] in ["ERROR", "FAIL"]
        assert result['errors'] >= 1
        assert len(result['failures']) == 1
        assert "Agent NonExistentAgent not found" in result['failures'][0]['error']

    def test_phase2_successful_execution_with_telemetry(self, mock_components):
        """
        Critical: Phase 2 must track successful executions with complete telemetry.
        """
        engine, state, agents = mock_components
        agent_mock = agents["FixerAgent"]
        
        # Mock successful heal response
        agent_mock.heal.return_value = {"status": "success", "changes": 3}
        
        plan = {
            "violations_found": [
                {"file": "fixable.py", "type": "NAMING", "suggested_agent": "FixerAgent"}
            ]
        }
        
        result = execute_phase2_reconciliation(
            agents, "test_zone", engine, state, plan, dry_run=False
        )
        
        # Verify HEAL_RESULT_SCHEMA compliance
        assert result['violations_found'] == 1
        assert result['violations_fixed'] == 1
        assert result['status'] == "PASS"
        assert result['errors'] == 0
        assert result['skipped'] == 0
        
        # Verify successful execution
        assert len(result['modifications']) == 1
        assert len(result['failures']) == 0
        
        mod = result['modifications'][0]
        assert mod['action'] == "fix_applied"
        assert mod['target'] == "fixable.py"
        assert mod['agent'] == "FixerAgent"
        assert mod['success'] is True
        assert 'result' in mod
        
        # Verify manifest telemetry
        manifest = result['manifest']
        assert manifest['violations']['found'] == 1
        assert manifest['violations']['attempted'] == 1
        assert manifest['violations']['fixed'] == 1
        assert manifest['budget']['consumed'] == 1
        assert len(manifest['confidence']['scores']) == 1

    def test_phase3_ast_validation_catch_syntax_error(self, mock_components, tmp_path):
        """
        Critical: Phase 3 must detect if a 'fix' resulted in broken syntax.
        """
        engine, state, agents = mock_components
        
        # Create a "fixed" file that is actually broken
        broken_file = tmp_path / "fixed_but_broken.py"
        broken_file.write_text("def syntax_error_here(")
        
        # Simulate Phase 1 having reported this file
        original_violations = [{"file": str(broken_file)}]
        
        # Patch os.getcwd to return tmp_path
        with patch('os.getcwd', return_value=str(tmp_path)):
            result = execute_phase3_final_validation(
                agents, "test_zone", original_violations, engine, state, dry_run=False
            )
        
        # Verify HEAL_RESULT_SCHEMA compliance
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "status" in result
        assert "errors" in result
        assert "skipped" in result
        
        assert result['status'] == "FAIL"
        assert result['violations_found'] > 0
        assert result['violations_fixed'] == 0  # Validation doesn't fix
        assert result['errors'] > 0  # Syntax errors count as errors
        
        # Check custom fields
        assert len(result['remaining_violations']) > 0
        
        violation = result['remaining_violations'][0]
        assert violation['type'] == "SYNTAX_ERROR"
        assert violation['severity'] == "critical"
        assert "Error parsing" in violation['message']
        
        # Verify telemetry
        telemetry = result['telemetry']
        assert telemetry['files_checked'] == 1
        assert telemetry['files_failed'] == 1
        assert telemetry['syntax_errors'] == 1
        assert telemetry['status'] == "drift_detected"

    def test_phase3_ast_validation_missing_type_hints(self, mock_components, tmp_path):
        """
        Critical: Phase 3 must detect missing type hints in 'fixed' files.
        """
        engine, state, agents = mock_components
        
        # Create a file without type hints
        no_hints_file = tmp_path / "no_hints.py"
        no_hints_file.write_text("""
def function_without_return_type():
    return "hello"

def another_function(param):
    return param + 1
""")
        
        original_violations = [{"file": str(no_hints_file)}]
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            result = execute_phase3_final_validation(
                agents, "test_zone", original_violations, engine, state, dry_run=False
            )
        
        assert result['status'] == "FAIL"
        assert result['violations_found'] == 2  # Two functions missing hints
        assert result['violations_fixed'] == 0
        assert result['errors'] == 0  # Type hints are not syntax errors
        
        # Check specific violations
        violations = result['remaining_violations']
        for v in violations:
            assert v['type'] == "MISSING_TYPE_HINT"
            assert v['file'] == str(no_hints_file)
        
        # Verify telemetry
        telemetry = result['telemetry']
        assert telemetry['files_checked'] == 1
        assert telemetry['files_failed'] == 1
        assert telemetry['ast_violations'] == 2

    def test_phase3_validation_clean_file(self, mock_components, tmp_path):
        """
        Critical: Phase 3 must pass clean files without issues.
        """
        engine, state, agents = mock_components
        
        # Create a properly typed file
        clean_file = tmp_path / "clean_file.py"
        clean_file.write_text("""
def properly_typed_function(param: int) -> str:
    return str(param)

def __init_helper__():
    pass  # Dunder methods should be ignored
""")
        
        original_violations = [{"file": str(clean_file)}]
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            result = execute_phase3_final_validation(
                agents, "test_zone", original_violations, engine, state, dry_run=False
            )
        
        assert result['status'] == "PASS"
        assert result['violations_found'] == 0
        assert result['violations_fixed'] == 0
        assert result['errors'] == 0
        assert result['skipped'] == 0
        assert len(result['remaining_violations']) == 0
        
        # Verify telemetry
        telemetry = result['telemetry']
        assert telemetry['files_checked'] == 1
        assert telemetry['files_passed'] == 1
        assert telemetry['files_failed'] == 0
        assert telemetry['status'] == "clean"

    def test_phase3_dry_run_skip(self, mock_components):
        """
        Critical: Phase 3 must skip validation in dry run mode.
        """
        engine, state, agents = mock_components
        
        original_violations = [{"file": "any_file.py"}]
        
        result = execute_phase3_final_validation(
            agents, "test_zone", original_violations, engine, state, dry_run=True
        )
        
        assert result['status'] == "SKIPPED"
        assert result['violations_found'] == 0
        assert result['violations_fixed'] == 0
        assert result['errors'] == 0
        assert result['skipped'] == 1
        assert result['message'] == "Dry run - validation skipped"

    def test_phase3_nonexistent_file_handling(self, mock_components):
        """
        Critical: Phase 3 must handle nonexistent files gracefully.
        """
        engine, state, agents = mock_components
        
        original_violations = [
            {"file": "nonexistent.py"},
            {"file": ""},  # Empty file path
            {"file": None}  # None file path
        ]
        
        result = execute_phase3_final_validation(
            agents, "test_zone", original_violations, engine, state, dry_run=False
        )
        
        # Should complete without crashing, no files to check
        assert result['status'] == "PASS"
        assert result['violations_found'] == 0
        assert len(result['remaining_violations']) == 0
        
        # Verify telemetry shows no files checked
        telemetry = result['telemetry']
        assert telemetry['files_checked'] == 0

    def test_phase3_large_file_protection(self, mock_components, tmp_path):
        """
        Critical: Phase 3 must skip files that are too large to prevent OOM.
        """
        engine, state, agents = mock_components
        
        # Create a large file (simulate > 1MB)
        large_file = tmp_path / "large_file.py"
        large_content = "x" * 1_500_000  # 1.5MB
        large_file.write_text(large_content)
        
        original_violations = [{"file": str(large_file)}]
        
        with patch('os.getcwd', return_value=str(tmp_path)):
            result = execute_phase3_final_validation(
                agents, "test_zone", original_violations, engine, state, dry_run=False
            )
        
        # Should skip large file and remain clean
        assert result['status'] == "PASS"
        assert result['violations_found'] == 0
        assert len(result['remaining_violations']) == 0

    def test_reconciliation_manifest_telemetry(self, mock_components):
        """
        Critical: ReconciliationManifest must track all telemetry accurately.
        """
        engine, state, agents = mock_components
        
        # Test manifest creation and finalization
        manifest = ReconciliationManifest(
            mission_id="TEST_MISSION",
            territory="test_territory",
            start_time=datetime.now().isoformat(),
            violations_found=5
        )
        
        # Add some modifications
        manifest.add_modification({
            "action": "fix_applied",
            "target": "file1.py",
            "success": True
        })
        
        manifest.add_modification({
            "action": "fix_failed", 
            "target": "file2.py",
            "success": False
        })
        
        # Add a failure
        manifest.add_failure({
            "violation": {"file": "file3.py"},
            "reason": "Budget exceeded"
        })
        
        # Add confidence scores
        manifest.confidence_scores = [0.8, 0.6, 0.9]
        manifest.budget_consumed = 2
        
        # Finalize and verify structure
        final = manifest.finalize()
        
        assert final['mission_id'] == "TEST_MISSION"
        assert final['territory'] == "test_territory"
        assert final['violations']['found'] == 5
        assert final['violations']['attempted'] == 2
        assert final['violations']['fixed'] == 1
        assert final['violations']['failed'] == 2  # 1 failed mod + 1 direct failure
        assert final['budget']['consumed'] == 2
        assert final['budget']['remaining'] == 98
        assert abs(final['confidence']['average'] - 0.7666666666666667) < 1e-10  # (0.8+0.6+0.9)/3
        assert len(final['modifications']) == 2
        assert len(final['failures']) == 1

    def test_phase2_mixed_success_failure_scenario(self, mock_components):
        """
        Critical: Phase 2 must handle mixed success/failure scenarios correctly.
        """
        engine, state, agents = mock_components
        agent_mock = agents["FixerAgent"]
        
        # Mock agent to succeed on first call, fail on second
        agent_mock.heal.side_effect = [
            {"status": "success", "changes": 2},
            Exception("Agent failure")
        ]
        
        plan = {
            "violations_found": [
                {"file": "success.py", "type": "NAMING", "suggested_agent": "FixerAgent"},
                {"file": "fail.py", "type": "HIERARCHY", "suggested_agent": "FixerAgent"}
            ]
        }
        
        result = execute_phase2_reconciliation(
            agents, "test_zone", engine, state, plan, dry_run=False
        )
        
        # Verify HEAL_RESULT_SCHEMA compliance
        assert result['violations_found'] == 2
        assert result['violations_fixed'] == 1  # Only one succeeded
        assert result['status'] == "PARTIAL"  # Mixed success
        assert result['errors'] == 1  # One failure
        assert result['skipped'] == 0
        
        # Verify mixed result
        assert len(result['modifications']) == 1
        assert len(result['failures']) == 1
        
        # Check successful modification
        success_mod = result['modifications'][0]
        assert success_mod['success'] is True
        assert success_mod['target'] == "success.py"
        
        # Check failure
        failure = result['failures'][0]
        assert "Agent failure" in failure['error']
        assert failure['violation']['file'] == "fail.py"
        
        # Verify manifest tracks mixed results
        manifest = result['manifest']
        assert manifest['violations']['attempted'] == 1  # Only successful attempts count
        assert manifest['violations']['fixed'] == 1
        assert manifest['violations']['failed'] == 2  # 1 execution failure + 1 tracked failure
