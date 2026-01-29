"""
Test Suite for execute_ssot.py Enhancement Validation

This module provides comprehensive tests to validate the proposed enhancements
identified in EXECUTE_SSOT_ENHANCEMENT_REPORT.md.

Run with:
    pytest tests/unit/agentic_core/L0_maintenance/test_execute_ssot_enhancements.py -v
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the classes we need to test
from agentic_core.L0_maintenance.scripts.execute_ssot import (
    AutonomousDecisionEngine,
    ConfidenceScore,
    ASTCodeQualityValidator,
    validate_territory_input,
    ReconciliationViolation
)


class TestSafetyMechanisms:
    """CRITICAL: Test safety guards for cycles and resource exhaustion."""

    def test_cycle_detection_hard_stop(self):
        """
        Verify that recursive healing calls are blocked immediately.
        Requirement: Must return False and specific error message.
        """
        # Use the enhanced version with cycle detection
        from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine as EnhancedEngine
        
        engine = EnhancedEngine(enable_llm=False)
        
        # 1. First call - OK
        proceed, _ = engine.should_proceed_with_healing(
            ConfidenceScore(1.0, "Perfect"), agent_name="Agent_A"
        )
        assert proceed is True, "First call should pass"
        
        # 2. Recursive call (Same Agent) - BLOCK
        proceed, msg = engine.should_proceed_with_healing(
            ConfidenceScore(1.0, "Perfect"), agent_name="Agent_A"
        )
        assert proceed is False, "Recursive call must be blocked"
        assert "cycle detected" in msg.lower(), "Error message must indicate cycle"

    def test_healing_budget_exhaustion(self):
        """
        Verify global healing budget prevents runaway processes.
        Requirement: Stop after N operations.
        """
        from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine as EnhancedEngine
        
        engine = EnhancedEngine(enable_llm=False)
        engine._max_healing_operations = 2
        
        # Consume budget
        engine.should_proceed_with_healing(ConfidenceScore(1.0, ""), agent_name="Agent_1")
        engine.should_proceed_with_healing(ConfidenceScore(1.0, ""), agent_name="Agent_2")
        
        # Exceed budget
        proceed, msg = engine.should_proceed_with_healing(
            ConfidenceScore(1.0, ""), agent_name="Agent_3"
        )
        assert proceed is False
        assert "budget exceeded" in msg.lower()

    def test_territory_validation_security_fuzzing(self):
        """
        Fuzz territory input to ensure security against injection/traversal.
        """
        from agentic_core.L0_maintenance.scripts.execute_ssot import validate_territory_input
        
        inputs = [
            ("valid_territory", True),
            ("../etc/passwd", False),   # Traversal
            ("/root/hack", False),      # Absolute path
            ("valid; rm -rf /", False), # Shell injection attempt
            ("a" * 101, False),         # Buffer overflow attempt
            ("valid_123", True)
        ]
        
        for inp, expected in inputs:
            valid, msg = validate_territory_input(inp)
            assert valid == expected, f"Failed security check for: {inp}"


class TestASTValidator:
    """Verify code quality analysis and memory safety."""

    def test_detect_missing_types(self, tmp_path):
        """Ensure missing type hints are caught."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import ASTCodeQualityValidator
        
        f = tmp_path / "dirty.py"
        f.write_text("def bad_func(x): return x")
        
        validator = ASTCodeQualityValidator(tmp_path)
        res = validator.check_file_quality(f)
        
        assert res['violations_count'] == 1
        assert res['violations'][0]['type'] == 'MISSING_TYPE_HINT'

    def test_memory_safety_guard(self, tmp_path):
        """
        Verify that massive files are rejected to prevent OOM.
        Requirement: Must return error, not crash.
        """
        from agentic_core.L0_maintenance.scripts.execute_ssot import ASTCodeQualityValidator
        
        f = tmp_path / "massive.py"
        # Create dummy large file (1.1MB)
        f.write_text("x = 1\n" * 200_000)
        
        validator = ASTCodeQualityValidator(tmp_path)
        # Verify write size
        assert os.path.getsize(f) > 1_000_000
        
        res = validator.check_file_quality(f)
        assert "error" in res
        assert "too large" in res['error'], "Must reject large files"


class TestSemanticIntelligence:
    """Verify decision engine scoring logic."""

    def test_confidence_calculation_bounds(self):
        """
        Verify confidence score never exceeds 1.0 or drops below 0.0.
        Requirement: Mathematical correctness.
        """
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Max inputs
        conf = engine.calculate_healing_confidence(
            violations_count=0,
            violation_types=["NAMING_ERROR"], 
            territory="prompt_governance",    
            historical_success_rate=1.0
        )
        assert 0.0 <= conf.value <= 1.0, f"Score out of bounds: {conf.value}"

    def test_semantic_jaccard_scoring(self):
        """Verify Jaccard similarity logic."""
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Partial match
        score = engine._calculate_semantic_similarity(
            "user_auth_controller", 
            ["user_controller", "auth_service"]
        )
        assert score > 0.0, "Should detect similarity"
        
        # No match
        score = engine._calculate_semantic_similarity(
            "banana_bread",
            ["rocket_science"]
        )
        assert score == 0.0


class TestReconciliationViolation:
    """Verify structured violation data model."""

    def test_violation_serialization(self):
        """Test violation to_dict conversion."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import ReconciliationViolation
        
        violation = ReconciliationViolation(
            is_valid=False,
            message="Test violation",
            drift_type="NAMING",
            file_path=Path("/test/file.py"),
            severity=7
        )
        
        data = violation.to_dict()
        assert data["is_valid"] is False
        assert data["message"] == "Test violation"
        assert data["drift_type"] == "NAMING"
        assert data["file_path"] == "/test/file.py"
        assert data["severity"] == 7

    def test_violation_optional_fields(self):
        """Test violation with minimal required fields."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import ReconciliationViolation
        
        violation = ReconciliationViolation(
            is_valid=True,
            message="OK"
        )
        
        data = violation.to_dict()
        assert data["is_valid"] is True
        assert data["message"] == "OK"
        assert data["drift_type"] is None
        assert data["file_path"] is None
        assert data["severity"] == 5  # Default value


class TestConfidenceScoring:
    """Test confidence scoring enhancements from LocationHealerAgent patterns."""

    def test_calculate_healing_confidence_zero_violations(self):
        """Zero violations should return perfect confidence."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine
        
        engine = AutonomousDecisionEngine(enable_llm=False)
        confidence = engine.calculate_healing_confidence(
            violations_count=0,
            violation_types=[],
            territory="prompt_governance"
        )
        
        assert confidence.value == 1.0, "Zero violations should have perfect confidence"
        assert confidence.is_high_confidence is True

    def test_calculate_healing_confidence_trusted_territory(self):
        """Trusted territories should have higher confidence for same violation count."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine
        
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Trusted territory
        trusted_conf = engine.calculate_healing_confidence(
            violations_count=10,
            violation_types=["NAMING"],
            territory="prompt_governance"
        )
        
        # Critical territory
        critical_conf = engine.calculate_healing_confidence(
            violations_count=10,
            violation_types=["NAMING"],
            territory="L5_safety"
        )
        
        assert trusted_conf.value > critical_conf.value, \
            "Trusted territories should have higher confidence than critical ones"

    def test_calculate_healing_confidence_known_types(self):
        """Known violation types should increase confidence."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import AutonomousDecisionEngine
        
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        # Known types
        known_conf = engine.calculate_healing_confidence(
            violations_count=5,
            violation_types=["NAMING", "HIERARCHY", "IMPORT"],
            territory="scripts"
        )
        
        # Unknown types
        unknown_conf = engine.calculate_healing_confidence(
            violations_count=5,
            violation_types=["UNKNOWN_XYZ", "MYSTERY_ABC"],
            territory="scripts"
        )
        
        assert known_conf.value > unknown_conf.value, \
            "Known violation types should have higher confidence"

    def test_should_proceed_with_healing_high_confidence(self):
        """High confidence (>0.75) should proceed with healing."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            AutonomousDecisionEngine,
            ConfidenceScore
        )
        
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        high_conf = ConfidenceScore(value=0.85, reasoning="Test high confidence")
        proceed, reason = engine.should_proceed_with_healing(high_conf)
        
        assert proceed is True, "High confidence should proceed"
        assert "AUTO-HEAL" in reason

    def test_should_proceed_with_healing_low_confidence_no_llm(self):
        """Low confidence without LLM should not proceed."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            AutonomousDecisionEngine,
            ConfidenceScore
        )
        
        engine = AutonomousDecisionEngine(enable_llm=False)
        
        low_conf = ConfidenceScore(value=0.5, reasoning="Test low confidence")
        proceed, reason = engine.should_proceed_with_healing(low_conf)
        
        assert proceed is False, "Low confidence without LLM should not proceed"
        assert "LLM Disabled" in reason

    def test_should_proceed_with_healing_low_confidence_with_llm(self):
        """Low confidence with LLM enabled should proceed with override."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            AutonomousDecisionEngine,
            ConfidenceScore
        )
        
        engine = AutonomousDecisionEngine(enable_llm=True)
        
        low_conf = ConfidenceScore(value=0.5, reasoning="Test low confidence")
        proceed, reason = engine.should_proceed_with_healing(low_conf)
        
        assert proceed is True, "Low confidence with LLM should proceed"
        assert "LLM Override" in reason


class TestRuntimeStateManager:
    """Test RuntimeStateManager functionality."""

    def test_state_initialization(self, tmp_path):
        """Test that state is properly initialized."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
        
        state_mgr = RuntimeStateManager(tmp_path)
        
        assert state_mgr.state["status"] == "idle"
        assert state_mgr.state["start_time"] is None
        assert state_mgr.state["agents_order"] == []
        assert state_mgr.state["completed_agents"] == []

    def test_start_mission(self, tmp_path):
        """Test mission start updates state correctly."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
        
        state_mgr = RuntimeStateManager(tmp_path)
        state_mgr.start_mission("Test Mission", ["Agent1", "Agent2"])
        
        assert state_mgr.state["status"] == "running"
        assert state_mgr.state["start_time"] is not None
        assert state_mgr.state["agents_order"] == ["Agent1", "Agent2"]

    def test_update_agent(self, tmp_path):
        """Test agent update tracking."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
        
        state_mgr = RuntimeStateManager(tmp_path)
        state_mgr.update_agent("TestAgent", "L5 - Safety")
        
        assert state_mgr.state["current_agent"] == "TestAgent"
        assert state_mgr.state["current_layer"] == "L5 - Safety"

    def test_complete_agent(self, tmp_path):
        """Test agent completion tracking."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
        
        state_mgr = RuntimeStateManager(tmp_path)
        state_mgr.complete_agent("TestAgent", True, "Completed successfully")
        
        assert len(state_mgr.state["completed_agents"]) == 1
        assert state_mgr.state["completed_agents"][0]["agent"] == "TestAgent"
        assert state_mgr.state["completed_agents"][0]["success"] is True

    def test_finish_mission(self, tmp_path):
        """Test mission finish updates state correctly."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
        
        state_mgr = RuntimeStateManager(tmp_path)
        state_mgr.start_mission("Test", [])
        state_mgr.finish_mission("completed")
        
        assert state_mgr.state["status"] == "completed"
        assert state_mgr.state["end_time"] is not None
        assert state_mgr.state["current_agent"] is None

    def test_atomic_save(self, tmp_path):
        """Test that state is saved atomically."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import RuntimeStateManager
        import json
        
        state_mgr = RuntimeStateManager(tmp_path)
        state_mgr.state["test_key"] = "test_value"
        state_mgr.save()
        
        state_file = tmp_path / "runtime_state.json"
        assert state_file.exists(), "State file should be created"
        
        with open(state_file) as f:
            saved_state = json.load(f)
        
        assert saved_state["test_key"] == "test_value"


class TestNonInteractiveGuard:
    """Test NonInteractiveGuard for CI/CD safety."""

    def test_guard_blocks_input(self):
        """Test that guard blocks input() calls."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import NonInteractiveGuard
        import builtins
        
        original_input = builtins.input
        
        with NonInteractiveGuard(active=True):
            with pytest.raises(RuntimeError) as exc_info:
                input("This should be blocked")
            
            assert "Interactive prompt blocked" in str(exc_info.value)
        
        # Verify input is restored
        assert builtins.input == original_input

    def test_guard_inactive_allows_input(self):
        """Test that inactive guard allows input() calls."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import NonInteractiveGuard
        import builtins
        
        original_input = builtins.input
        
        # Mock input to avoid actual stdin read
        with patch.object(builtins, 'input', return_value="test"):
            with NonInteractiveGuard(active=False):
                result = input("This should work")
                assert result == "test"

    def test_guard_exhaustion_protection(self):
        """Test that guard prevents infinite prompt loops."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import NonInteractiveGuard
        
        with NonInteractiveGuard(active=True, max_blocked_prompts=3):
            # First 3 should raise RuntimeError
            for i in range(3):
                with pytest.raises(RuntimeError):
                    input(f"Prompt {i}")
            
            # 4th should raise RecursionError (exhaustion protection)
            with pytest.raises(RecursionError) as exc_info:
                input("Exhaustion trigger")
            
            assert "Infinite Loop Protection" in str(exc_info.value)


class TestWithRetryDecorator:
    """Test the with_retry decorator for transient failure resilience."""

    def test_retry_succeeds_on_first_attempt(self):
        """Test that successful first attempt returns immediately."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import with_retry
        
        call_count = 0
        
        @with_retry(max_retries=3, delay=0.01)
        def always_succeeds():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = always_succeeds()
        
        assert result == "success"
        assert call_count == 1

    def test_retry_succeeds_after_failures(self):
        """Test that retry succeeds after transient failures."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import with_retry
        
        call_count = 0
        
        @with_retry(max_retries=3, delay=0.01)
        def fails_twice_then_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient failure")
            return "success"
        
        result = fails_twice_then_succeeds()
        
        assert result == "success"
        assert call_count == 3

    def test_retry_exhausted_raises(self):
        """Test that exhausted retries raise the last exception."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import with_retry
        
        @with_retry(max_retries=2, delay=0.01)
        def always_fails():
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError) as exc_info:
            always_fails()
        
        assert "Persistent failure" in str(exc_info.value)

    def test_retry_does_not_retry_prompt_errors(self):
        """Test that prompt-related errors are not retried."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import with_retry
        
        call_count = 0
        
        @with_retry(max_retries=3, delay=0.01)
        def raises_prompt_error():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Interactive prompt blocked")
        
        with pytest.raises(RuntimeError):
            raises_prompt_error()
        
        assert call_count == 1, "Prompt errors should not be retried"


class TestEnhancedAutonomousDecisionEngine:
    """Test EnhancedAutonomousDecisionEngine with CDA integration."""

    def test_enhanced_engine_initialization(self, tmp_path):
        """Test enhanced engine initializes correctly."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            EnhancedAutonomousDecisionEngine,
            RuntimeStateManager
        )
        
        state_mgr = RuntimeStateManager(tmp_path)
        engine = EnhancedAutonomousDecisionEngine(
            enable_llm=False,
            state_mgr=state_mgr,
            enable_cda=False
        )
        
        assert engine.enable_llm is False
        assert engine.enable_cda is False
        assert engine.state_mgr is state_mgr

    def test_classify_violation_type(self, tmp_path):
        """Test violation type classification."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            EnhancedAutonomousDecisionEngine,
            RuntimeStateManager
        )
        
        state_mgr = RuntimeStateManager(tmp_path)
        engine = EnhancedAutonomousDecisionEngine(
            enable_llm=False,
            state_mgr=state_mgr,
            enable_cda=False
        )
        
        # Test various violation message patterns
        assert engine._classify_violation_type("Missing sovereign root: xyz") == "MISSING_DIRECTORY"
        assert engine._classify_violation_type("Forbidden keyword 'def test_'") == "FORBIDDEN_CONTENT"
        assert engine._classify_violation_type("Forbidden extension .py") == "EXTENSION_MISMATCH"
        assert engine._classify_violation_type("test_ file found") == "TEST_FILE_MISPLACED"
        assert engine._classify_violation_type("sovereign violation") == "SOVEREIGN_VIOLATION"
        assert engine._classify_violation_type("random issue") == "STRUCTURAL_VIOLATION"


class TestAgentDiscovery:
    """Test agent discovery functionality."""

    def test_list_available_agents_from_cache(self, tmp_path):
        """Test agent discovery from cached JSON."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import list_available_agents
        import json
        
        # Create mock discovery cache
        cache_data = [
            {"class_name": "TestAgent1", "path": "agentic_core/test/TestAgent1.py"},
            {"class_name": "TestAgent2", "path": "agentic_core/test/TestAgent2.py"},
        ]
        
        cache_file = tmp_path / "agent_discovery_full.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        agents = list_available_agents(tmp_path)
        
        assert len(agents) == 2
        assert ("TestAgent1", "agentic_core.test.TestAgent1") in agents
        assert ("TestAgent2", "agentic_core.test.TestAgent2") in agents

    def test_list_available_agents_deduplication(self, tmp_path):
        """Test that duplicate agents are removed."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import list_available_agents
        import json
        
        # Create mock discovery cache with duplicates
        cache_data = [
            {"class_name": "TestAgent", "path": "agentic_core/test/TestAgent.py"},
            {"class_name": "TestAgent", "path": "agentic_core/test/TestAgent.py"},
        ]
        
        cache_file = tmp_path / "agent_discovery_full.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        agents = list_available_agents(tmp_path, dedupe=True)
        
        assert len(agents) == 1

    def test_list_available_agents_rejects_invalid_modules(self, tmp_path):
        """Test that invalid module paths are rejected."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import list_available_agents
        import json
        
        # Create mock discovery cache with invalid paths
        cache_data = [
            {"class_name": "ValidAgent", "path": "agentic_core/test/ValidAgent.py"},
            {"class_name": "InvalidAgent", "path": "malicious_package/InvalidAgent.py"},
        ]
        
        cache_file = tmp_path / "agent_discovery_full.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        agents = list_available_agents(tmp_path)
        
        # Only valid agent should be included
        assert len(agents) == 1
        assert agents[0][0] == "ValidAgent"


class TestConfidenceScoreDataclass:
    """Test ConfidenceScore dataclass properties."""

    def test_is_high_confidence(self):
        """Test high confidence threshold."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import ConfidenceScore
        
        high = ConfidenceScore(value=0.80, reasoning="High")
        medium = ConfidenceScore(value=0.75, reasoning="Medium")
        low = ConfidenceScore(value=0.50, reasoning="Low")
        
        assert high.is_high_confidence is True
        assert medium.is_high_confidence is False
        assert low.is_high_confidence is False

    def test_is_medium_confidence(self):
        """Test medium confidence threshold."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import ConfidenceScore
        
        high = ConfidenceScore(value=0.80, reasoning="High")
        medium = ConfidenceScore(value=0.60, reasoning="Medium")
        low = ConfidenceScore(value=0.40, reasoning="Low")
        
        assert high.is_medium_confidence is False
        assert medium.is_medium_confidence is True
        assert low.is_medium_confidence is False

    def test_is_low_confidence(self):
        """Test low confidence threshold."""
        from agentic_core.L0_maintenance.scripts.execute_ssot import ConfidenceScore
        
        high = ConfidenceScore(value=0.80, reasoning="High")
        medium = ConfidenceScore(value=0.60, reasoning="Medium")
        low = ConfidenceScore(value=0.40, reasoning="Low")
        
        assert high.is_low_confidence is False
        assert medium.is_low_confidence is False
        assert low.is_low_confidence is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
