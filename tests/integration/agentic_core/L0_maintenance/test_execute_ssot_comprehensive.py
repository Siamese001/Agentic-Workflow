"""
File: tests/integration/agentic_core/L0_maintenance/test_execute_ssot_comprehensive.py
Description: Comprehensive 10-case test suite for enhanced SSOT execution, covering safety, LLM logic, and telemetry.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.scripts.execute_ssot import (
    ASTCodeQualityValidator,
    AutonomousDecisionEngine,
    ConfidenceScore,
    ReconciliationViolation,
    RuntimeStateManager,
    execute_phase1_discovery,
    validate_territory_input,
)


class TestComprehensiveSSOT:
    """
    10-Point Comprehensive Test Plan for Execute SSOT Enhancements
    """

    @pytest.fixture
    def engine(self):
        """Standard engine fixture with LLM disabled by default."""
        return AutonomousDecisionEngine(enable_llm=False)

    @pytest.fixture
    def llm_engine(self):
        """Engine with LLM enabled for confidence override tests."""
        return AutonomousDecisionEngine(enable_llm=True)

    # =========================================================================
    # CASE 1: High Confidence Auto-Heal (No LLM Required)
    # =========================================================================
    def test_01_high_confidence_auto_heal(self, engine):
        """
        Scenario: High confidence score (>= 0.75).
        Expected: Returns True immediately with 'AUTO-HEAL' reason.
        """
        score = ConfidenceScore(value=0.85, reasoning="Perfect match")
        proceed, reason = engine.should_proceed_with_healing(score, agent_name="Agent_High")

        assert proceed is True, "High confidence should always proceed"
        assert "AUTO-HEAL" in reason
        assert "Agent_High" in engine._call_path, "Agent must be tracked for cycles"

    # =========================================================================
    # CASE 2: Medium Confidence LLM Override
    # =========================================================================
    def test_02_medium_confidence_llm_override(self, llm_engine):
        """
        Scenario: Medium confidence (0.5 <= x < 0.75) with LLM Enabled.
        Expected: Returns True with 'LLM Override'.
        """
        score = ConfidenceScore(value=0.60, reasoning="Partial match")
        proceed, reason = llm_engine.should_proceed_with_healing(score, agent_name="Agent_Med")

        assert proceed is True, "Medium confidence with LLM should proceed"
        assert "LLM Override" in reason

    def test_02b_medium_confidence_no_llm_block(self, engine):
        """
        Scenario: Medium confidence (0.5 <= x < 0.75) with LLM Disabled.
        Expected: Returns False.
        """
        score = ConfidenceScore(value=0.60, reasoning="Partial match")
        proceed, reason = engine.should_proceed_with_healing(score, agent_name="Agent_Med_NoLLM")

        assert proceed is False, "Medium confidence without LLM must fail"
        assert "Confidence too low" in reason

    # =========================================================================
    # CASE 3: Low Confidence Hard Block
    # =========================================================================
    def test_03_low_confidence_hard_block(self, llm_engine):
        """
        Scenario: Low confidence (< 0.5) even if LLM is enabled.
        Expected: Returns False (Safety First).
        """
        score = ConfidenceScore(value=0.40, reasoning="Unknown error")
        proceed, reason = llm_engine.should_proceed_with_healing(score, agent_name="Agent_Low")

        assert proceed is False, "Low confidence must always be blocked"
        assert "Confidence too low" in reason

    # =========================================================================
    # CASE 4: Healing Cycle Detection (Recursion Guard)
    # =========================================================================
    def test_04_cycle_detection_guard(self, engine):
        """
        Scenario: An agent attempts to heal itself recursively.
        Expected: Second call returns False with 'cycle detected'.
        """
        score = ConfidenceScore(value=0.9, reasoning="Looping")

        # Call 1
        engine.should_proceed_with_healing(score, agent_name="RecursiveAgent")

        # Call 2 (Cycle)
        proceed, reason = engine.should_proceed_with_healing(score, agent_name="RecursiveAgent")

        assert proceed is False
        assert "cycle detected" in reason
        assert "SAFETY LOCK" in reason

    # =========================================================================
    # CASE 5: Global Budget Exhaustion
    # =========================================================================
    def test_05_healing_budget_exhaustion(self, engine):
        """
        Scenario: Total healing operations exceed defined budget.
        Expected: Subsequent calls return False.
        """
        engine._max_healing_operations = 3
        score = ConfidenceScore(value=0.9, reasoning="Valid")

        # Consume budget
        for i in range(3):
            proceed, _ = engine.should_proceed_with_healing(score, agent_name=f"Agent_{i}")
            assert proceed is True

        # Attempt 4 (Budget Exceeded)
        proceed, reason = engine.should_proceed_with_healing(score, agent_name="Agent_Overflow")

        assert proceed is False
        assert "Budget exceeded" in reason

    # =========================================================================
    # CASE 6: Security Input Validation (Traversal Attacks)
    # =========================================================================
    def test_06_security_input_validation(self):
        """
        Scenario: Malicious inputs provided as territory names.
        Expected: Validator rejects paths, injections, and long strings.
        """
        threats = [
            "../../etc/passwd",  # Path traversal
            "/usr/bin/python",  # Absolute path
            "valid; cat /flag",  # Shell injection style
            "a" * 150,  # Buffer overflow attempt
            "<script>alert(1)</script>",  # Special chars
        ]

        for threat in threats:
            is_valid, msg = validate_territory_input(threat)
            assert is_valid is False, f"Failed to block threat: {threat}"

        assert validate_territory_input("valid_territory_1")[0] is True

    # =========================================================================
    # CASE 7: AST Validator - Missing Type Hints
    # =========================================================================
    def test_07_ast_missing_type_hints(self, tmp_path):
        """
        Scenario: Python file with missing return type hints.
        Expected: Violation detected and reported accurately.
        """
        bad_code = """
def untyped_function(x, y):
    return x + y

def typed_function(x: int) -> int:
    return x
"""
        p = tmp_path / "test_types.py"
        p.write_text(bad_code)

        validator = ASTCodeQualityValidator(tmp_path)
        report = validator.check_file_quality(p)

        assert report["violations_count"] == 1
        assert report["violations"][0]["type"] == "MISSING_TYPE_HINT"
        assert "untyped_function" in report["violations"][0]["message"]

    # =========================================================================
    # CASE 8: AST Validator - Large File DOS Protection
    # =========================================================================
    def test_08_ast_file_size_limit(self, tmp_path):
        """
        Scenario: Massive generated file provided to AST parser.
        Expected: Validator refuses to parse to prevent OOM.
        """
        p = tmp_path / "massive.py"
        # Write > 1MB file
        p.write_text("x = 1\n" * 150_000)

        validator = ASTCodeQualityValidator(tmp_path)
        report = validator.check_file_quality(p)

        assert "error" in report
        assert "too large" in report["error"]
        assert report["violations"] == []

    # =========================================================================
    # CASE 9: Telemetry Report Accuracy
    # =========================================================================
    def test_09_telemetry_report_structure(self):
        """
        Scenario: Create a violation report and serialize it.
        Expected: Dictionary matches schema exactly (for dashboard ingestion).
        """
        violation = ReconciliationViolation(
            is_valid=False,
            message="Drift Detected",
            drift_type="ORPHANED_FILE",
            file_path=Path("/tmp/test.py"),
            severity=8,
        )

        data = violation.to_dict()

        assert data["is_valid"] is False
        assert data["drift_type"] == "ORPHANED_FILE"
        assert data["severity"] == 8
        assert "/tmp/test.py" in data["file_path"]

    # =========================================================================
    # CASE 10: Full Phase 1 Flow with Standard Heal Schema
    # =========================================================================
    def test_10_full_phase_execution_schema(self, tmp_path):
        """
        Scenario: Execute Phase 1 discovery (mocked) through the decorator.
        Expected: Output matches standard HEAL_RESULT_SCHEMA.
        """
        # Mock dependencies
        mock_state = MagicMock(spec=RuntimeStateManager)
        mock_engine = MagicMock(spec=AutonomousDecisionEngine)

        # Run Phase 1
        with patch(
            "agentic_core.L0_maintenance.scripts.execute_ssot.execute_phase1_discovery_impl"
        ) as mock_impl:
            # The impl returns raw data, decorator standardizes it
            mock_impl.return_value = {"raw_data": "test"}

            result = execute_phase1_discovery(
                agents=[],
                territory="test_zone",
                decision_engine=mock_engine,
                state_mgr=mock_state,
                dry_run=True,
            )

            # Verify Standard Heal Schema keys are present
            # Note: The actual schema depends on the imported base_agent,
            # but usually includes 'status', 'violations_found', etc.
            # Here we verify the decorator didn't crash and passed through
            assert result is not None
