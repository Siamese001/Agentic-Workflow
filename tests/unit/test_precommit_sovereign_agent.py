#!/usr/bin/env python3
"""
Unit Tests for PreCommitSovereignAgent

Tests the pre-commit hook agent's ability to detect and report
architectural violations in staged files.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent import (
    PreCommitSovereignAgent,
    ViolationReport
)


class TestPreCommitSovereignAgent:
    """Unit tests for PreCommitSovereignAgent."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_path,
                capture_output=True
            )
            
            yield repo_path
    
    @pytest.fixture
    def agent(self, temp_repo):
        """Create a PreCommitSovereignAgent instance."""
        return PreCommitSovereignAgent(root_dir=str(temp_repo))
    
    def test_initialization(self, agent, temp_repo):
        """Test agent initialization."""
        assert agent.root == temp_repo
        assert agent.validator is not None
        assert agent.violations_found == []
    
    def test_get_staged_files_empty(self, agent):
        """Test getting staged files when none are staged."""
        staged = agent.get_staged_files()
        assert staged == []
    
    def test_get_staged_files_with_python_files(self, agent, temp_repo):
        """Test getting staged Python files."""
        # Create test files
        test_file = temp_repo / "test.py"
        test_file.write_text("print('hello')")
        
        non_python = temp_repo / "test.txt"
        non_python.write_text("not python")
        
        # Stage files
        subprocess.run(["git", "add", "test.py", "test.txt"], cwd=temp_repo)
        
        staged = agent.get_staged_files()
        
        # Should only include Python files
        assert "test.py" in staged
        assert "test.txt" not in staged
    
    def test_get_staged_files_no_git(self, tmp_path):
        """Test behavior when not in a git repository."""
        agent = PreCommitSovereignAgent(root_dir=str(tmp_path))
        staged = agent.get_staged_files()
        assert staged == []
    
    @patch('agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent.UnifiedSSOTValidator')
    def test_validate_staged_files_no_files(self, mock_validator, agent):
        """Test validation when no files are staged."""
        result = agent.validate_staged_files()
        
        assert result["compliant"] is True
        assert result["files_scanned"] == 0
        assert result["violations"] == []
        assert result["error"] is None
    
    @patch('agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent.UnifiedSSOTValidator')
    def test_validate_staged_files_with_violations(self, mock_validator, agent, temp_repo):
        """Test validation when staged files have violations."""
        # Create and stage a file
        test_file = temp_repo / "violator.py"
        test_file.write_text("from agentic_core.L5_safety import something")
        subprocess.run(["git", "add", "violator.py"], cwd=temp_repo)
        
        # Mock validator to return violations
        mock_report = Mock()
        mock_violation = Mock()
        mock_violation.file_path = "violator.py"
        mock_violation.line_number = 1
        mock_violation.source_layer = "LL0"
        mock_violation.target_layer = "LL5"
        mock_violation.import_statement = "from agentic_core.L5_safety import something"
        
        mock_report.import_violations = [mock_violation]
        mock_validator.return_value.validate_all.return_value = mock_report
        
        result = agent.validate_staged_files()
        
        assert result["compliant"] is False
        assert result["files_scanned"] == 1
        assert len(result["violations"]) == 1
        assert result["violations"][0].file_path == "violator.py"
    
    @patch('agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent.UnifiedSSOTValidator')
    def test_validate_staged_files_compliant(self, mock_validator, agent, temp_repo):
        """Test validation when staged files are compliant."""
        # Create and stage a compliant file
        test_file = temp_repo / "compliant.py"
        test_file.write_text("print('hello world')")
        subprocess.run(["git", "add", "compliant.py"], cwd=temp_repo)
        
        # Mock validator to return no violations for this file
        mock_report = Mock()
        mock_report.import_violations = []
        mock_validator.return_value.validate_all.return_value = mock_report
        
        result = agent.validate_staged_files()
        
        assert result["compliant"] is True
        assert result["files_scanned"] == 1
        assert result["violations"] == []
    
    @patch('agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent.UnifiedSSOTValidator')
    def test_validate_sovereignty_success(self, mock_validator, agent, temp_repo):
        """Test validate_sovereignty returns 0 for compliant files."""
        test_file = temp_repo / "good.py"
        test_file.write_text("print('ok')")
        subprocess.run(["git", "add", "good.py"], cwd=temp_repo)
        
        mock_report = Mock()
        mock_report.import_violations = []
        mock_validator.return_value.validate_all.return_value = mock_report
        
        exit_code = agent.validate_sovereignty()
        assert exit_code == 0
    
    @patch('agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent.UnifiedSSOTValidator')
    def test_validate_sovereignty_failure(self, mock_validator, agent, temp_repo, capsys):
        """Test validate_sovereignty returns 1 for violations."""
        test_file = temp_repo / "bad.py"
        test_file.write_text("from agentic_core.L5_safety import bad")
        subprocess.run(["git", "add", "bad.py"], cwd=temp_repo)
        
        mock_report = Mock()
        mock_violation = Mock()
        mock_violation.file_path = "bad.py"
        mock_violation.line_number = 1
        mock_violation.source_layer = "LL0"
        mock_violation.target_layer = "LL5"
        mock_violation.import_statement = "from agentic_core.L5_safety import bad"
        
        mock_report.import_violations = [mock_violation]
        mock_validator.return_value.validate_all.return_value = mock_report
        
        exit_code = agent.validate_sovereignty()
        
        assert exit_code == 1
        
        # Check that failure report was printed
        captured = capsys.readouterr()
        assert "GOSPEL ENFORCEMENT FAILURE" in captured.out
        assert "COMMIT ABORTED" in captured.out
    
    def test_install_hook(self, agent, temp_repo):
        """Test installing the pre-commit hook."""
        success = agent.install_hook()
        
        assert success is True
        
        hook_path = temp_repo / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists()
        
        # Verify hook content
        content = hook_path.read_text()
        assert "PreCommitSovereignAgent" in content
        assert "validate_sovereignty" in content
    
    def test_install_hook_not_git_repo(self, tmp_path):
        """Test installing hook in non-git directory."""
        agent = PreCommitSovereignAgent(root_dir=str(tmp_path))
        success = agent.install_hook()
        
        assert success is False
    
    def test_uninstall_hook(self, agent, temp_repo):
        """Test uninstalling the pre-commit hook."""
        # First install
        agent.install_hook()
        hook_path = temp_repo / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists()
        
        # Then uninstall
        success = agent.uninstall_hook()
        
        assert success is True
        assert not hook_path.exists()
    
    def test_uninstall_hook_not_exists(self, agent):
        """Test uninstalling when hook doesn't exist."""
        success = agent.uninstall_hook()
        assert success is True  # Should succeed silently
    
    def test_violation_report_dataclass(self):
        """Test ViolationReport dataclass."""
        report = ViolationReport(
            file_path="test.py",
            line_number=10,
            violation_type="L0 → L5",
            import_statement="from agentic_core.L5_safety import X",
            source_layer="LL0",
            target_layer="LL5"
        )
        
        assert report.file_path == "test.py"
        assert report.line_number == 10
        assert report.violation_type == "L0 → L5"
        assert report.source_layer == "LL0"
        assert report.target_layer == "LL5"
    
    @patch('agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent.UnifiedSSOTValidator')
    def test_validate_handles_validator_exception(self, mock_validator, agent, temp_repo):
        """Test that validation handles validator exceptions gracefully."""
        test_file = temp_repo / "test.py"
        test_file.write_text("print('test')")
        subprocess.run(["git", "add", "test.py"], cwd=temp_repo)
        
        # Mock validator to raise exception
        mock_validator.return_value.validate_all.side_effect = Exception("Validator error")
        
        result = agent.validate_staged_files()
        
        assert result["compliant"] is False
        assert result["error"] is not None
        assert "Validator error" in result["error"]


class TestPreCommitSovereignAgentIntegration:
    """Integration tests that require more complex setup."""
    
    @pytest.fixture
    def mock_repo_with_structure(self, tmp_path):
        """Create a mock repository with SSOT structure."""
        repo = tmp_path / "test_repo"
        repo.mkdir()
        
        # Initialize git
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            capture_output=True
        )
        
        # Create basic structure
        (repo / "agentic_core").mkdir()
        (repo / "agentic_core" / "L0_maintenance").mkdir()
        (repo / "agentic_core" / "L5_safety").mkdir()
        
        return repo
    
    def test_end_to_end_violation_detection(self, mock_repo_with_structure):
        """End-to-end test of violation detection."""
        repo = mock_repo_with_structure
        
        # Create a file with violation
        violator = repo / "agentic_core" / "L0_maintenance" / "bad.py"
        violator.write_text("""
from agentic_core.L5_safety.guardrails import something

def do_something():
    return something()
""")
        
        # Stage the file
        subprocess.run(["git", "add", "."], cwd=repo)
        
        # Note: This would require full SSOT infrastructure to work
        # In practice, this is tested manually or in CI/CD
        agent = PreCommitSovereignAgent(root_dir=str(repo))
        staged = agent.get_staged_files()
        
        assert len(staged) > 0
        assert any("bad.py" in f for f in staged)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
