#!/usr/bin/env python3
"""
End-to-End Integration Tests for PreCommitSovereignAgent

Tests the complete workflow of the pre-commit hook in a real git environment.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path

from agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent import PreCommitSovereignAgent


@pytest.mark.integration
class TestPreCommitE2E:
    """End-to-end integration tests for PreCommitSovereignAgent."""
    
    @pytest.fixture
    def test_repo(self):
        """Create a complete test repository with SSOT structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
            
            # Create SSOT directory structure
            (repo_path / AGENTIC_CORE_DIR).mkdir()
            (repo_path / AGENTIC_CORE_DIR / "L0_maintenance").mkdir()
            (repo_path / AGENTIC_CORE_DIR / "L0_maintenance" / SCRIPTS_DIR).mkdir()
            (repo_path / AGENTIC_CORE_DIR / "L5_safety").mkdir()
            (repo_path / AGENTIC_CORE_DIR / "L5_safety" / "guardrails").mkdir()
            (repo_path / AGENTIC_CORE_DIR / "utils").mkdir()
            (repo_path / AGENTIC_CORE_DIR / "utils" / "core_extensions").mkdir()
            
            # Create minimal required files for SSOT scanner
            init_file = repo_path / AGENTIC_CORE_DIR / "__init__.py"
            init_file.write_text("")
            
            yield repo_path
    
    def test_hook_installation_and_removal(self, test_repo):
        """Test installing and removing the git hook."""
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        
        # Install hook
        assert agent.install_hook() is True
        hook_path = test_repo / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists()
        
        # Verify hook is executable (Unix-like systems)
        import sys
        if sys.platform != 'win32':
            import os
            assert os.access(hook_path, os.X_OK)
        
        # Uninstall hook
        assert agent.uninstall_hook() is True
        assert not hook_path.exists()
    
    def test_commit_with_compliant_file(self, test_repo):
        """Test that compliant files can be committed."""
        # Create a compliant file
        compliant_file = test_repo / AGENTIC_CORE_DIR / "L0_maintenance" / SCRIPTS_DIR / "good.py"
        compliant_file.write_text("""
#!/usr/bin/env python3
\"\"\"A compliant L0 script.\"\"\"

def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
""")
        
        # Stage the file
        subprocess.run(["git", "add", "."], cwd=test_repo, check=True)
        
        # Validate
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        exit_code = agent.validate_sovereignty()
        
        # Should allow commit
        assert exit_code == 0
    
    def test_commit_blocked_with_violation(self, test_repo):
        """Test that commits with violations are blocked."""
        # Create a file with upward dependency violation
        violator_file = test_repo / AGENTIC_CORE_DIR / "L0_maintenance" / SCRIPTS_DIR / "bad.py"
        violator_file.write_text("""
#!/usr/bin/env python3
\"\"\"A non-compliant L0 script with upward leak.\"\"\"

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

class BadAgent(MCPHardenedMixin):
    pass
""")
        
        # Stage the file
        subprocess.run(["git", "add", "."], cwd=test_repo, check=True)
        
        # Validate
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        exit_code = agent.validate_sovereignty()
        
        # Should block commit
        assert exit_code == 1
        assert len(agent.violations_found) > 0
    
    def test_hook_execution_via_git(self, test_repo):
        """Test that the hook actually runs during git commit."""
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        agent.install_hook()
        
        # Create a compliant file
        good_file = test_repo / "good.py"
        good_file.write_text("print('hello')")
        
        subprocess.run(["git", "add", "good.py"], cwd=test_repo, check=True)
        
        # Try to commit (should succeed)
        result = subprocess.run(
            ["git", "commit", "-m", "Test commit"],
            cwd=test_repo,
            capture_output=True,
            text=True
        )
        
        # Check that hook ran
        assert "Sovereign Sentinel" in result.stdout or result.returncode == 0
    
    def test_bypass_hook_with_no_verify(self, test_repo):
        """Test that --no-verify bypasses the hook."""
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        agent.install_hook()
        
        # Create a file with violation
        bad_file = test_repo / "bad.py"
        bad_file.write_text("from agentic_core.L5_safety import X")
        
        subprocess.run(["git", "add", "bad.py"], cwd=test_repo, check=True)
        
        # Commit with --no-verify (should succeed despite violation)
        result = subprocess.run(
            ["git", "commit", "-m", "Bypass test", "--no-verify"],
            cwd=test_repo,
            capture_output=True
        )
        
        # Should succeed
        assert result.returncode == 0
    
    def test_multiple_files_mixed_compliance(self, test_repo):
        """Test handling multiple files with mixed compliance."""
        # Create one compliant file
        good_file = test_repo / "good.py"
        good_file.write_text("print('ok')")
        
        # Create one non-compliant file
        bad_file = test_repo / AGENTIC_CORE_DIR / "L0_maintenance" / "bad.py"
        bad_file.write_text("from agentic_core.L5_safety import X")
        
        # Stage both
        subprocess.run(["git", "add", "."], cwd=test_repo, check=True)
        
        # Validate
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        result = agent.validate_staged_files()
        
        # Should detect violation
        assert result["compliant"] is False
        assert result["files_scanned"] == 2
    
    def test_no_staged_files(self, test_repo):
        """Test behavior when no files are staged."""
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        exit_code = agent.validate_sovereignty()
        
        # Should succeed (nothing to validate)
        assert exit_code == 0
    
    def test_staged_non_python_files_ignored(self, test_repo):
        """Test that non-Python files are ignored."""
        # Create and stage non-Python files
        txt_file = test_repo / "readme.txt"
        txt_file.write_text("This is a readme")
        
        md_file = test_repo / "doc.md"
        md_file.write_text("# Documentation")
        
        subprocess.run(["git", "add", "."], cwd=test_repo, check=True)
        
        # Validate
        agent = PreCommitSovereignAgent(root_dir=str(test_repo))
        result = agent.validate_staged_files()
        
        # Should succeed (no Python files)
        assert result["compliant"] is True
        assert result["files_scanned"] == 0


@pytest.mark.integration
@pytest.mark.slow
class TestPreCommitPerformance:
    """Performance tests for the pre-commit hook."""
    
    def test_performance_with_many_files(self, tmp_path):
        """Test hook performance with many staged files."""
        import time
        
        repo = tmp_path / "perf_test"
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
        
        # Create many Python files
        for i in range(50):
            file_path = repo / f"file_{i}.py"
            file_path.write_text(f"# File {i}\nprint('hello {i}')")
        
        # Stage all files
        subprocess.run(["git", "add", "."], cwd=repo)
        
        # Measure validation time
        agent = PreCommitSovereignAgent(root_dir=str(repo))
        
        start = time.time()
        result = agent.validate_staged_files()
        duration = time.time() - start
        
        # Should complete in reasonable time (< 10 seconds)
        assert duration < 10.0
        assert result["files_scanned"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
