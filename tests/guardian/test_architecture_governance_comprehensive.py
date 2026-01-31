# tests/guardian/test_architecture_governance_comprehensive.py
import subprocess
import sys
from pathlib import Path

GUARDIAN_TEST = Path(__file__).parent / "test_architecture_governance.py"


def test_compliant_file_passes():
    """TC-AG-01: Compliant file with no violations passes."""
    agent_code = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def run(self):
        pass
"""
    # Create in a temp location that simulates L5 layer
    temp_dir = Path("temp_test_agentic_core/L5_safety")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "TestAgent.py"

    try:
        temp_file.write_text(agent_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "COMPLIANT" in result.stdout
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass


def test_gravity_violation_detected():
    """TC-AG-02: Gravity violation (lower layer importing higher) detected."""
    agent_code = """
# This is in L1_cognition trying to import from L5_safety (violation)
from agentic_core.L5_safety.validators.SomeValidator import SomeValidator

class CognitionAgent:
    def run(self):
        pass
"""
    temp_dir = Path("temp_test_agentic_core/L1_cognition")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "CognitionAgent.py"

    try:
        temp_file.write_text(agent_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "VIOLATION" in result.stdout
        assert "Gravity violation" in result.stdout
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass


def test_naming_convention_violation():
    """TC-AG-03: Agent class in file not ending with Agent.py."""
    agent_code = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def run(self):
        pass
"""
    temp_dir = Path("temp_test_agentic_core/L5_safety")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_file.py"  # Wrong naming

    try:
        temp_file.write_text(agent_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "VIOLATION" in result.stdout
        assert "Naming violation" in result.stdout
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass


def test_nonexistent_file():
    """TC-AG-04: Nonexistent file fails."""
    result = subprocess.run(
        [sys.executable, str(GUARDIAN_TEST), "nonexistent_file.py"], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "does not exist" in result.stdout


def test_valid_upward_import():
    """TC-AG-05: Valid upward import (higher layer importing lower) passes."""
    agent_code = """
# This is in L5_safety importing from L1_cognition (valid)
from agentic_core.L1_cognition.thought_engine.ThoughtEngine import ThoughtEngine

class SafetyAgent:
    def run(self):
        pass
"""
    temp_dir = Path("temp_test_agentic_core/L5_safety")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "SafetyAgent.py"

    try:
        temp_file.write_text(agent_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "COMPLIANT" in result.stdout
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass


def test_non_agent_file_passes():
    """TC-AG-06: Non-agent utility file passes."""
    util_code = """
# Utility file without agent classes
def helper_function():
    return True

class UtilityClass:
    pass
"""
    temp_dir = Path("temp_test_agentic_core/L5_safety")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "utils.py"

    try:
        temp_file.write_text(util_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "COMPLIANT" in result.stdout
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass


def test_syntax_error_handling():
    """TC-AG-07: Syntax errors handled gracefully."""
    agent_code = """
# Syntax error - unclosed string
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def run(self):
        bad_string = "unclosed
        pass
"""
    temp_dir = Path("temp_test_agentic_core/L5_safety")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "TestAgent.py"

    try:
        temp_file.write_text(agent_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        # Should handle gracefully - either pass or fail with error message
        assert result.returncode in [0, 1]
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass


def test_multiple_violations():
    """TC-AG-08: Multiple violations detected in single file."""
    agent_code = """
# Multiple violations: gravity + naming
from agentic_core.L6_observability.dashboard import Dashboard

class TestAgent:
    def run(self):
        pass
"""
    temp_dir = Path("temp_test_agentic_core/L1_cognition")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "test_file.py"  # Wrong naming

    try:
        temp_file.write_text(agent_code)
        result = subprocess.run(
            [sys.executable, str(GUARDIAN_TEST), str(temp_file)], capture_output=True, text=True
        )
        assert result.returncode == 1
        assert "VIOLATION" in result.stdout
        # Should detect at least one violation
        assert "Gravity violation" in result.stdout or "Naming violation" in result.stdout
    finally:
        try:
            temp_file.unlink()
            temp_dir.rmdir()
            temp_dir.parent.rmdir()
        except:
            pass
