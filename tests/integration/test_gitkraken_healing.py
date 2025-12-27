"""
Integration Tests for Phase 17D: GitKraken Healing
Validates autonomous version control operations with GitKraken MCP integration.
"""
import asyncio
import pytest
from agentic_core.L0_maintenance.healing.gitkraken_healing_strategy import GitKrakenHealingStrategy, create_gitkraken_healing_strategy
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config


class TestGitKrakenHealingStrategy:
    """Test suite for GitKraken Healing Strategy."""
    
    @pytest.mark.asyncio
    async def test_strategy_initialization(self):
        """Test GitKraken healing strategy initializes correctly."""
        strategy = GitKrakenHealingStrategy()
        assert strategy is not None
        assert strategy.name == "GitKrakenHealing"
        assert strategy.priority == 1
        assert strategy.commits_today == 0
        assert hasattr(strategy, 'git_client')
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test factory function creates strategy."""
        strategy = await create_gitkraken_healing_strategy()
        assert isinstance(strategy, GitKrakenHealingStrategy)
    
    @pytest.mark.asyncio
    async def test_diagnose_groups_file_violations(self):
        """Test strategy groups violations by file."""
        strategy = GitKrakenHealingStrategy()
        
        issues = [
            {"file": "test1.py", "description": "violation 1", "reason": "Issue 1"},
            {"file": "test1.py", "description": "violation 2", "reason": "Issue 2"},
            {"file": "test2.py", "description": "violation 3", "reason": "Issue 3"}
        ]
        
        fixes = await strategy.diagnose(issues)
        
        assert len(fixes) == 2  # Two files
        assert all(fix["action"] == "git_healing_commit" for fix in fixes)
        assert all(fix["strategy"] == "GitKrakenHealing" for fix in fixes)
        assert all(fix["priority"] == 1 for fix in fixes)
    
    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self):
        """Test strategy respects config disable flag."""
        original_value = config.GITKRAKEN_HEALING_ENABLED
        object.__setattr__(config, 'GITKRAKEN_HEALING_ENABLED', False)
        
        try:
            strategy = GitKrakenHealingStrategy()
            issues = [{"file": "test.py", "description": "violation"}]
            
            fixes = await strategy.diagnose(issues)
            
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'GITKRAKEN_HEALING_ENABLED', original_value)
    
    @pytest.mark.asyncio
    async def test_reset_daily_counter(self):
        """Test daily counter can be reset."""
        strategy = GitKrakenHealingStrategy()
        strategy.commits_today = 50
        
        strategy.reset_daily_counter()
        
        assert strategy.commits_today == 0


class TestGitKrakenHealingConfig:
    """Test GitKraken healing configuration."""
    
    def test_config_settings_exist(self):
        """Test all GitKraken healing config settings exist."""
        assert hasattr(config, 'GITKRAKEN_HEALING_ENABLED')
        assert hasattr(config, 'GITKRAKEN_HEALING_AUTO_COMMIT')
        assert hasattr(config, 'GITKRAKEN_HEALING_AUTO_PR')
        assert hasattr(config, 'GITKRAKEN_HEALING_BRANCH')
        assert hasattr(config, 'GITKRAKEN_PR_TITLE_PREFIX')
        assert hasattr(config, 'GITKRAKEN_DEFAULT_REPO')
    
    def test_config_default_values(self):
        """Test config has sensible default values."""
        assert isinstance(config.GITKRAKEN_HEALING_ENABLED, bool)
        assert isinstance(config.GITKRAKEN_HEALING_AUTO_COMMIT, bool)
        assert isinstance(config.GITKRAKEN_HEALING_AUTO_PR, bool)
        assert isinstance(config.GITKRAKEN_HEALING_BRANCH, str)
        assert isinstance(config.GITKRAKEN_PR_TITLE_PREFIX, str)
        assert isinstance(config.GITKRAKEN_DEFAULT_REPO, str)
        
        assert len(config.GITKRAKEN_HEALING_BRANCH) > 0
        assert len(config.GITKRAKEN_PR_TITLE_PREFIX) > 0
        assert len(config.GITKRAKEN_DEFAULT_REPO) > 0


class TestGitKrakenHealingMCPIntegration:
    """Test GitKraken healing MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_uses_gitkraken_mcp_client(self):
        """Test strategy uses GitKraken MCP client."""
        strategy = GitKrakenHealingStrategy()
        
        assert strategy.git_client is not None
        assert hasattr(strategy.git_client, 'add')
        assert hasattr(strategy.git_client, 'commit')
        assert hasattr(strategy.git_client, 'create_pr')


class TestGitKrakenHealingStrategyRegistry:
    """Test GitKraken healing strategy is registered."""
    
    def test_strategy_in_registry(self):
        """Test GitKrakenHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        strategy_names = [s.name for s in HEALING_STRATEGIES]
        assert "GitKrakenHealing" in strategy_names
    
    def test_strategy_priority(self):
        """Test GitKrakenHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        gitkraken_strategy = next((s for s in HEALING_STRATEGIES if s.name == "GitKrakenHealing"), None)
        assert gitkraken_strategy is not None
        assert gitkraken_strategy.priority == 1


class TestGitKrakenHealingFileGrouping:
    """Test GitKraken healing file grouping logic."""
    
    @pytest.mark.asyncio
    async def test_groups_multiple_violations_per_file(self):
        """Test multiple violations for same file are grouped."""
        strategy = GitKrakenHealingStrategy()
        
        issues = [
            {"file": "test.py", "description": "violation 1", "reason": "Reason 1"},
            {"file": "test.py", "description": "violation 2", "reason": "Reason 2"},
            {"file": "test.py", "description": "violation 3", "reason": "Reason 3"}
        ]
        
        fixes = await strategy.diagnose(issues)
        
        assert len(fixes) == 1
        assert len(fixes[0]["details"]) == 3
        assert "3 violations" in fixes[0]["summary"]
    
    @pytest.mark.asyncio
    async def test_ignores_issues_without_file(self):
        """Test issues without file field are ignored."""
        strategy = GitKrakenHealingStrategy()
        
        issues = [
            {"description": "violation without file"},
            {"file": "test.py", "description": "violation with file"}
        ]
        
        fixes = await strategy.diagnose(issues)
        
        assert len(fixes) == 1
        assert fixes[0]["files"] == ["test.py"]


class TestGitKrakenHealingCommitGeneration:
    """Test GitKraken healing commit generation."""
    
    @pytest.mark.asyncio
    async def test_commit_summary_format(self):
        """Test commit summary has correct format."""
        strategy = GitKrakenHealingStrategy()
        
        issues = [
            {"file": "test.py", "description": "violation 1"},
            {"file": "test.py", "description": "violation 2"}
        ]
        
        fixes = await strategy.diagnose(issues)
        
        assert len(fixes) == 1
        assert "Sovereignty Fix:" in fixes[0]["summary"]
        assert "test.py" in fixes[0]["summary"]


class TestGitKrakenHealingPRGeneration:
    """Test GitKraken healing PR generation."""
    
    def test_pr_title_prefix_configured(self):
        """Test PR title prefix is configured."""
        assert config.GITKRAKEN_PR_TITLE_PREFIX is not None
        assert len(config.GITKRAKEN_PR_TITLE_PREFIX) > 0
        assert "[" in config.GITKRAKEN_PR_TITLE_PREFIX  # Should be like [SOVEREIGN HEALING]
    
    def test_pr_auto_creation_configurable(self):
        """Test PR auto-creation is configurable."""
        assert isinstance(config.GITKRAKEN_HEALING_AUTO_PR, bool)


class TestGitKrakenHealingGuardianIntegration:
    """Test GitKraken healing guardian integration."""
    
    def test_guardian_blocks_subprocess_git(self):
        """Test guardian blocks subprocess git calls."""
        from agentic_core.utils.guardian.sovereignty_auditor import BANNED_IMPORTS
        
        git_patterns = BANNED_IMPORTS.get("Git Operations", [])
        assert len(git_patterns) > 0
        
        # Should block subprocess.run with git
        assert any('subprocess' in pattern for pattern in git_patterns)
        
        # Should block os.system with git
        assert any('os.system' in pattern for pattern in git_patterns)
        
        # Should block GitPython
        assert any('import.*git' in pattern for pattern in git_patterns)


class TestGitKrakenHealingBranchConfiguration:
    """Test GitKraken healing branch configuration."""
    
    def test_healing_branch_configured(self):
        """Test healing branch is configured."""
        assert config.GITKRAKEN_HEALING_BRANCH is not None
        assert len(config.GITKRAKEN_HEALING_BRANCH) > 0
    
    def test_default_repo_configured(self):
        """Test default repository is configured."""
        assert config.GITKRAKEN_DEFAULT_REPO is not None
        assert len(config.GITKRAKEN_DEFAULT_REPO) > 0


def run_tests():
    """Run all GitKraken healing tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
