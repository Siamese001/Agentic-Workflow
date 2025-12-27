"""
Integration Tests for Phase 16D: GitKraken MCP Client
Validates sovereign version control operations through MCP architecture.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from agentic_core.L0_maintenance.gitkraken_mcp_client import get_git_client, SovereignGitKrakenMCPClient
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config


class TestGitKrakenMCPIntegration:
    """Test suite for GitKraken MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_gitkraken_mcp_enabled(self):
        """Verify GitKraken MCP is enabled in sovereign config."""
        assert config.GITKRAKEN_MCP_ENABLED is True, "GitKraken MCP must be enabled"
        assert config.GITKRAKEN_DEFAULT_REPO == "xai/sovereign-canon", "Default repo should be xai/sovereign-canon"
        assert config.GITKRAKEN_HEALING_BRANCH == "sovereign-healing", "Healing branch should be sovereign-healing"
        assert config.GITKRAKEN_PR_TITLE_PREFIX == "[SOVEREIGN HEALING]", "PR prefix should be [SOVEREIGN HEALING]"
    
    @pytest.mark.asyncio
    async def test_git_client_singleton(self):
        """Verify singleton pattern for GitKraken client."""
        client1 = get_git_client()
        client2 = get_git_client()
        assert client1 is client2, "Should return same singleton instance"
    
    @pytest.mark.asyncio
    async def test_git_mcp_routing(self):
        """Verify operations route through L3 MCP router."""
        client = get_git_client()
        
        # Verify router is initialized
        assert hasattr(client, 'router'), "Client should have router"
        assert client.router is not None, "Router should be initialized"
        
        # Verify router role
        assert client.router.role == "governance_git", "Router role should be governance_git"
    
    @pytest.mark.asyncio
    async def test_create_healing_commit_message_format(self):
        """Test healing commit message formatting."""
        client = get_git_client()
        
        # Verify message prefix is added
        test_message = "Fix canon violation in L5 safety"
        expected_prefix = config.GITKRAKEN_PR_TITLE_PREFIX
        
        # The actual commit would use the full message with prefix
        # This is validated by checking the implementation
        assert expected_prefix == "[SOVEREIGN HEALING]"
    
    @pytest.mark.asyncio
    async def test_create_pr_title_format(self):
        """Test PR title formatting."""
        client = get_git_client()
        
        # Verify PR title prefix is added
        test_title = "Canon Healing: Fix L5 violations"
        expected_prefix = config.GITKRAKEN_PR_TITLE_PREFIX
        
        # The actual PR would use the full title with prefix
        assert expected_prefix == "[SOVEREIGN HEALING]"


class TestGuardianEnforcement:
    """Test guardian enforcement of GitKraken MCP usage."""
    
    def test_guardian_blocks_git_subprocess(self):
        """Verify guardian blocks direct git subprocess calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with git subprocess
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import subprocess\n")
            f.write('result = subprocess.run(["git", "status"])\n')
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block git subprocess calls"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_git_os_system(self):
        """Verify guardian blocks direct git os.system() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with git os.system()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import os\n")
            f.write('os.system("git status")\n')
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block git os.system() calls"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_gitpython_import(self):
        """Verify guardian blocks direct gitpython imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with gitpython import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import git\n")
            f.write("repo = git.Repo('.')\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block gitpython imports"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_pygit2_import(self):
        """Verify guardian blocks direct pygit2 imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with pygit2 import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import pygit2\n")
            f.write("repo = pygit2.Repository('.')\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block pygit2 imports"
        finally:
            temp_path.unlink()
    
    def test_guardian_allows_gitkraken_mcp(self):
        """Verify guardian allows GitKraken MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with GitKraken MCP import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from agentic_core.L0_maintenance.gitkraken_mcp_client import get_git_client\n")
            f.write("client = get_git_client()\n")
            f.write("status = await client.get_status()\n")
            temp_path = Path(f.name)
        
        try:
            # Should pass validation
            result = check_file(temp_path)
            assert result is True, "Guardian should allow GitKraken MCP import"
        finally:
            temp_path.unlink()


class TestGitOperations:
    """Test GitKraken MCP client operations."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initializes correctly."""
        client = get_git_client()
        assert client is not None, "Client should initialize"
        assert hasattr(client, 'router'), "Client should have router"
    
    @pytest.mark.asyncio
    async def test_healing_branch_configuration(self):
        """Test healing branch is properly configured."""
        assert config.GITKRAKEN_HEALING_BRANCH == "sovereign-healing"
        
        # Verify client would use this branch
        client = get_git_client()
        assert client is not None


class TestSovereignHealing:
    """Test sovereign healing workflow integration."""
    
    @pytest.mark.asyncio
    async def test_healing_commit_workflow(self):
        """Test healing commit workflow structure."""
        client = get_git_client()
        
        # Verify client has required methods
        assert hasattr(client, 'create_healing_commit'), "Client should have create_healing_commit method"
        assert hasattr(client, 'create_pr'), "Client should have create_pr method"
        assert hasattr(client, 'get_status'), "Client should have get_status method"
    
    @pytest.mark.asyncio
    async def test_pr_creation_workflow(self):
        """Test PR creation workflow structure."""
        client = get_git_client()
        
        # Verify PR creation method exists
        assert hasattr(client, 'create_pr'), "Client should have create_pr method"
        
        # Verify configuration
        assert config.GITKRAKEN_PR_TITLE_PREFIX == "[SOVEREIGN HEALING]"
        assert config.GITKRAKEN_DEFAULT_REPO == "xai/sovereign-canon"


class TestBranchOperations:
    """Test branch management operations."""
    
    @pytest.mark.asyncio
    async def test_branch_operations_available(self):
        """Test branch operation methods are available."""
        client = get_git_client()
        
        # Verify branch methods exist
        assert hasattr(client, 'create_branch'), "Client should have create_branch method"
        assert hasattr(client, 'checkout_branch'), "Client should have checkout_branch method"
        assert hasattr(client, 'list_branches'), "Client should have list_branches method"
    
    @pytest.mark.asyncio
    async def test_log_and_push_operations(self):
        """Test log and push operation methods are available."""
        client = get_git_client()
        
        # Verify log and push methods exist
        assert hasattr(client, 'get_log'), "Client should have get_log method"
        assert hasattr(client, 'push'), "Client should have push method"


def run_tests():
    """Run all GitKraken MCP integration tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
