"""
Integration Tests for Phase 17D: GitKraken Healing
Validates autonomous version control operations with GitKraken MCP integration.
"""
import asyncio
import pytest
from agentic_core.L0_maintenance.P1_core.gitkraken_healing_strategy import GitKrakenHealingStrategy, create_gitkraken_healing_strategy
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_git_kraken_healing_strategy:
    """Test suite for GitKraken Healing Strategy."""

    @pytest.mark.asyncio
    async def test_strategy_initialization(self) -> Any:
        """Test GitKraken healing strategy initializes correctly."""
        strategy: Any = GitKrakenHealingStrategy()
        assert strategy is not None
        assert strategy.name == 'GitKrakenHealing'
        assert strategy.priority == 1
        assert strategy.commits_today == 0
        assert hasattr(strategy, 'git_client')

    @pytest.mark.asyncio
    async def test_factory_function(self) -> Any:
        """Test factory function creates strategy."""
        strategy: Any = await create_gitkraken_healing_strategy()
        assert isinstance(strategy, GitKrakenHealingStrategy)

    @pytest.mark.asyncio
    async def test_diagnose_groups_file_violations(self) -> Any:
        """Test strategy groups violations by file."""
        strategy: Any = GitKrakenHealingStrategy()
        issues: Any = [{'file': 'test1.py', 'description': 'violation 1', 'reason': 'Issue 1'}, {'file': 'test1.py', 'description': 'violation 2', 'reason': 'Issue 2'}, {'file': 'test2.py', 'description': 'violation 3', 'reason': 'Issue 3'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) == 2
        assert all((fix['action'] == 'git_healing_commit' for fix in fixes))
        assert all((fix['strategy'] == 'GitKrakenHealing' for fix in fixes))
        assert all((fix['priority'] == 1 for fix in fixes))

    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self) -> Any:
        """Test strategy respects config disable flag."""
        original_value: Any = config.GITKRAKEN_HEALING_ENABLED
        object.__setattr__(config, 'GITKRAKEN_HEALING_ENABLED', False)
        try:
            strategy: Any = GitKrakenHealingStrategy()
            issues: Any = [{'file': 'test.py', 'description': 'violation'}]
            fixes: Any = await strategy.diagnose(issues)
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'GITKRAKEN_HEALING_ENABLED', original_value)

    @pytest.mark.asyncio
    async def test_reset_daily_counter(self) -> Any:
        """Test daily counter can be reset."""
        strategy: Any = GitKrakenHealingStrategy()
        strategy.commits_today = 50
        strategy.reset_daily_counter()
        assert strategy.commits_today == 0

class test_git_kraken_healing_config:
    """Test GitKraken healing configuration."""

    def test_config_settings_exist(self) -> Any:
        """Test all GitKraken healing config settings exist."""
        assert hasattr(config, 'GITKRAKEN_HEALING_ENABLED')
        assert hasattr(config, 'GITKRAKEN_HEALING_AUTO_COMMIT')
        assert hasattr(config, 'GITKRAKEN_HEALING_AUTO_PR')
        assert hasattr(config, 'GITKRAKEN_HEALING_BRANCH')
        assert hasattr(config, 'GITKRAKEN_PR_TITLE_PREFIX')
        assert hasattr(config, 'GITKRAKEN_DEFAULT_REPO')

    def test_config_default_values(self) -> Any:
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

class test_git_kraken_healing_mcp_integration:
    """Test GitKraken healing MCP client integration."""

    @pytest.mark.asyncio
    async def test_uses_gitkraken_mcp_client(self) -> Any:
        """Test strategy uses GitKraken MCP client."""
        strategy: Any = GitKrakenHealingStrategy()
        assert strategy.git_client is not None
        assert hasattr(strategy.git_client, 'add')
        assert hasattr(strategy.git_client, 'commit')
        assert hasattr(strategy.git_client, 'create_pr')

class test_git_kraken_healing_strategy_registry:
    """Test GitKraken healing strategy is registered."""

    def test_strategy_in_registry(self) -> Any:
        """Test GitKrakenHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
        strategy_names: Any = [s.name for s in HEALING_STRATEGIES]
        assert 'GitKrakenHealing' in strategy_names

    def test_strategy_priority(self) -> Any:
        """Test GitKrakenHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
        gitkraken_strategy: Any = next((s for s in HEALING_STRATEGIES if s.name == 'GitKrakenHealing'), None)
        assert gitkraken_strategy is not None
        assert gitkraken_strategy.priority == 1

class test_git_kraken_healing_file_grouping:
    """Test GitKraken healing file grouping logic."""

    @pytest.mark.asyncio
    async def test_groups_multiple_violations_per_file(self) -> Any:
        """Test multiple violations for same file are grouped."""
        strategy: Any = GitKrakenHealingStrategy()
        issues: Any = [{'file': 'test.py', 'description': 'violation 1', 'reason': 'Reason 1'}, {'file': 'test.py', 'description': 'violation 2', 'reason': 'Reason 2'}, {'file': 'test.py', 'description': 'violation 3', 'reason': 'Reason 3'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) == 1
        assert len(fixes[0]['details']) == 3
        assert '3 violations' in fixes[0]['summary']

    @pytest.mark.asyncio
    async def test_ignores_issues_without_file(self) -> Any:
        """Test issues without file field are ignored."""
        strategy: Any = GitKrakenHealingStrategy()
        issues: Any = [{'description': 'violation without file'}, {'file': 'test.py', 'description': 'violation with file'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) == 1
        assert fixes[0]['files'] == ['test.py']

class test_git_kraken_healing_commit_generation:
    """Test GitKraken healing commit generation."""

    @pytest.mark.asyncio
    async def test_commit_summary_format(self) -> Any:
        """Test commit summary has correct format."""
        strategy: Any = GitKrakenHealingStrategy()
        issues: Any = [{'file': 'test.py', 'description': 'violation 1'}, {'file': 'test.py', 'description': 'violation 2'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) == 1
        assert 'Sovereignty Fix:' in fixes[0]['summary']
        assert 'test.py' in fixes[0]['summary']

class test_git_kraken_healing_pr_generation:
    """Test GitKraken healing PR generation."""

    def test_pr_title_prefix_configured(self) -> Any:
        """Test PR title prefix is configured."""
        assert config.GITKRAKEN_PR_TITLE_PREFIX is not None
        assert len(config.GITKRAKEN_PR_TITLE_PREFIX) > 0
        assert '[' in config.GITKRAKEN_PR_TITLE_PREFIX

    def test_pr_auto_creation_configurable(self) -> Any:
        """Test PR auto-creation is configurable."""
        assert isinstance(config.GITKRAKEN_HEALING_AUTO_PR, bool)

class test_git_kraken_healing_guardian_integration:
    """Test GitKraken healing guardian integration."""

    def test_guardian_blocks_subprocess_git(self) -> Any:
        """Test guardian blocks subprocess git calls."""
        from agentic_core.utils.guardian.sovereignty_auditor import BANNED_IMPORTS
        git_patterns: Any = BANNED_IMPORTS.get('Git Operations', [])
        assert len(git_patterns) > 0
        assert any(('subprocess' in pattern for pattern in git_patterns))
        assert any(('os.system' in pattern for pattern in git_patterns))
        assert any(('import.*git' in pattern for pattern in git_patterns))

class test_git_kraken_healing_branch_configuration:
    """Test GitKraken healing branch configuration."""

    def test_healing_branch_configured(self) -> Any:
        """Test healing branch is configured."""
        assert config.GITKRAKEN_HEALING_BRANCH is not None
        assert len(config.GITKRAKEN_HEALING_BRANCH) > 0

    def test_default_repo_configured(self) -> Any:
        """Test default repository is configured."""
        assert config.GITKRAKEN_DEFAULT_REPO is not None
        assert len(config.GITKRAKEN_DEFAULT_REPO) > 0

def run_tests() -> Any:
    """Run all GitKraken healing tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
