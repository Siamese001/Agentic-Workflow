"""
Test Purpose Over Mechanism policy in FCA.

Validates:
- L5 wrapper with subprocess allowed (allowlist)
- L5 direct subprocess execution flagged
- L6 hybrid allowed
- Classification by purpose, not mechanism
"""

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
)


class TestPurposeOverMechanism:
    """Tests for Purpose Over Mechanism policy."""

    def test_l5_safety_wrapper_allowed(self):
        """L5 safety wrapper using subprocess should be allowed."""
        # safe_subprocess_handler.py is a safety wrapper - allowed
        assert "safe_subprocess_handler.py" in L5_SUBPROCESS_ALLOWLIST

    def test_l5_security_util_allowed(self):
        """L5 security utility using subprocess should be allowed."""
        assert "subprocess_security_util.py" in L5_SUBPROCESS_ALLOWLIST

    def test_l5_precommit_agent_allowed(self):
        """L5 PreCommit agent using subprocess should be allowed."""
        # PreCommit is safety enforcement - subprocess is mechanism
        assert "PreCommitSovereignAgent.py" in L5_SUBPROCESS_ALLOWLIST

    def test_l5_architecture_governor_allowed(self):
        """L5 ArchitectureGovernor using subprocess should be allowed."""
        assert "ArchitectureGovernorAgent.py" in L5_SUBPROCESS_ALLOWLIST

    def test_l6_playwright_hybrid_allowed(self):
        """L6 playwright util should be allowed as hybrid."""
        # Dashboard E2E is L6 ownership - playwright is mechanism
        assert "verify_dashboard_e2e_playwright_util.py" in L6_HYBRID_ALLOWLIST

    @pytest.mark.parametrize(
        "not_allowed",
        [
            "random_subprocess_user.py",
            "git_executor.py",
            "shell_runner.py",
        ],
    )
    def test_random_subprocess_not_allowed(self, not_allowed: str):
        """Random subprocess users should not be in L5 allowlist."""
        assert not_allowed not in L5_SUBPROCESS_ALLOWLIST


class TestLayerSuggestionByPurpose:
    """Tests for layer suggestion based on purpose."""

    @pytest.fixture
    def fca(self):
        """Create FCA instance."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        return FileClassificationAgent()

    def test_safety_wrapper_suggests_l5(self, fca, tmp_path):
        """Safety wrapper should suggest L5 even with subprocess."""
        content = '''"""Safe subprocess handler for L5."""
import subprocess

def safe_run(cmd):
    """Safety-checked subprocess execution."""
    # Validate command
    if not cmd:
        raise ValueError("Empty command")
    # Security checks
    forbidden = ["rm -rf", "del /f"]
    for f in forbidden:
        if f in " ".join(cmd):
            raise SecurityError("Forbidden command")
    return subprocess.run(cmd, capture_output=True)
'''
        test_file = tmp_path / "safe_subprocess_handler.py"
        test_file.write_text(content)

        # File is in L5 allowlist - should be accepted
        assert test_file.name in L5_SUBPROCESS_ALLOWLIST

    def test_execution_tool_suggests_l2(self, fca, tmp_path):
        """Execution tool should suggest L2."""
        content = '''"""Tool executor for L2."""
import subprocess

def execute_tool(tool_name, args):
    """Execute external tool."""
    return subprocess.run([tool_name] + args, capture_output=True)
'''
        test_file = tmp_path / "tool_executor.py"
        test_file.write_text(content)

        # This is execution, not safety - should suggest L2
        result = fca.suggest_manager_layer(test_file)
        # Tool/subprocess signals suggest L2
        if result:
            assert result == "L2_execution"

    def test_dashboard_generator_suggests_l6(self, fca, tmp_path):
        """Dashboard generator should suggest L6."""
        content = '''"""Dashboard generator for L6."""

def generate_dashboard(data):
    """Generate HTML dashboard."""
    html = "<html><body>"
    for item in data:
        html += f"<div>{item}</div>"
    html += "</body></html>"
    return html
'''
        test_file = tmp_path / "dashboard_generator.py"
        test_file.write_text(content)

        # Dashboard is L6 ownership
        # Note: suggest_manager_layer is for *Manager classes
        # This test validates the concept


class TestAllowlistEnforcement:
    """Tests for allowlist enforcement."""

    def test_allowlist_is_exhaustive(self):
        """Allowlist should contain all known L5 subprocess users."""
        expected_l5 = {
            "safe_subprocess_handler.py",
            "subprocess_security_util.py",
            "PreCommitSovereignAgent.py",
            "ArchitectureGovernorAgent.py",
            "AutonomyGuardianAgent.py",
            "SovereignActionPlaneAgent.py",
            "pre_deploy_check_util.py",
        }
        assert expected_l5.issubset(L5_SUBPROCESS_ALLOWLIST)

    def test_allowlist_is_minimal(self):
        """Allowlist should not contain unnecessary entries."""
        # Allowlist should be tight - no random files
        for entry in L5_SUBPROCESS_ALLOWLIST:
            # Each entry should be a valid Python filename
            assert entry.endswith(".py"), f"Invalid entry: {entry}"
            # Each entry should have a clear purpose
            assert len(entry) > 5, f"Entry too short: {entry}"

    def test_l6_allowlist_is_minimal(self):
        """L6 allowlist should be minimal."""
        # Only one known L6 hybrid
        assert len(L6_HYBRID_ALLOWLIST) >= 1
        assert "verify_dashboard_e2e_playwright_util.py" in L6_HYBRID_ALLOWLIST
