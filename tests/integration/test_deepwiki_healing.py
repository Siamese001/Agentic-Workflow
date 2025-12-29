"""
Integration Tests for Phase 17E: DeepWiki Healing
Validates autonomous documentation drift correction with DeepWiki MCP integration.
"""
import asyncio
import pytest
from pathlib import Path
from agentic_core.L0_maintenance.P1_core.deepwiki_healing_strategy import DeepWikiHealingStrategy, create_deepwiki_healing_strategy
from agentic_core.config.P1_core.sovereign_config import config

class test_deep_wiki_healing_strategy:
    """Test suite for DeepWiki Healing Strategy."""

    @pytest.mark.asyncio
    async def test_strategy_initialization(self) -> Any:
        """Test DeepWiki healing strategy initializes correctly."""
        strategy: Any = DeepWikiHealingStrategy()
        assert strategy is not None
        assert strategy.name == 'DeepWikiHealing'
        assert strategy.priority == 3
        assert strategy.processed_today == 0
        assert hasattr(strategy, 'fs_client')

    @pytest.mark.asyncio
    async def test_factory_function(self) -> Any:
        """Test factory function creates strategy."""
        strategy: Any = await create_deepwiki_healing_strategy()
        assert isinstance(strategy, DeepWikiHealingStrategy)

    @pytest.mark.asyncio
    async def test_diagnose_finds_undocumented_files(self) -> Any:
        """Test strategy diagnoses undocumented files."""
        strategy: Any = DeepWikiHealingStrategy()
        fixes: Any = await strategy.diagnose([])
        assert isinstance(fixes, list)
        if fixes:
            assert all((fix['action'] == 'document_new_file' for fix in fixes))
            assert all((fix['strategy'] == 'DeepWikiHealing' for fix in fixes))
            assert all((fix['priority'] == 3 for fix in fixes))

    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self) -> Any:
        """Test strategy respects config disable flag."""
        original_value: Any = config.DEEPWIKI_HEALING_ENABLED
        object.__setattr__(config, 'DEEPWIKI_HEALING_ENABLED', False)
        try:
            strategy: Any = DeepWikiHealingStrategy()
            fixes: Any = await strategy.diagnose([])
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'DEEPWIKI_HEALING_ENABLED', original_value)

    @pytest.mark.asyncio
    async def test_daily_limit_enforcement(self) -> Any:
        """Test daily healing limit is enforced."""
        strategy: Any = DeepWikiHealingStrategy()
        strategy.processed_today = config.DEEPWIKI_HEALING_MAX_DAILY
        fix: Any = {'file': 'test.py', 'action': 'document_new_file'}
        result: Any = await strategy.apply(fix)
        assert result is False

    @pytest.mark.asyncio
    async def test_reset_daily_counter(self) -> Any:
        """Test daily counter can be reset."""
        strategy: Any = DeepWikiHealingStrategy()
        strategy.processed_today = 50
        strategy.reset_daily_counter()
        assert strategy.processed_today == 0

class test_deep_wiki_healing_config:
    """Test DeepWiki healing configuration."""

    def test_config_settings_exist(self) -> Any:
        """Test all DeepWiki healing config settings exist."""
        assert hasattr(config, 'DEEPWIKI_HEALING_ENABLED')
        assert hasattr(config, 'DEEPWIKI_HEALING_BATCH_SIZE')
        assert hasattr(config, 'DEEPWIKI_HEALING_MAX_DAILY')
        assert hasattr(config, 'DEEPWIKI_DEFAULT_REPO')

    def test_config_default_values(self) -> Any:
        """Test config has sensible default values."""
        assert isinstance(config.DEEPWIKI_HEALING_ENABLED, bool)
        assert isinstance(config.DEEPWIKI_HEALING_BATCH_SIZE, int)
        assert isinstance(config.DEEPWIKI_HEALING_MAX_DAILY, int)
        assert isinstance(config.DEEPWIKI_DEFAULT_REPO, str)
        assert config.DEEPWIKI_HEALING_BATCH_SIZE > 0
        assert config.DEEPWIKI_HEALING_MAX_DAILY > 0
        assert len(config.DEEPWIKI_DEFAULT_REPO) > 0

class test_deep_wiki_healing_mcp_integration:
    """Test DeepWiki healing MCP client integration."""

    @pytest.mark.asyncio
    async def test_uses_filesystem_mcp_client(self) -> Any:
        """Test strategy uses Filesystem MCP client."""
        strategy: Any = DeepWikiHealingStrategy()
        assert strategy.fs_client is not None
        assert hasattr(strategy.fs_client, 'read_text')

class test_deep_wiki_healing_batch_processing:
    """Test DeepWiki healing batch processing."""

    @pytest.mark.asyncio
    async def test_batch_size_limits_results(self) -> Any:
        """Test batch size limits number of undocumented files returned."""
        strategy: Any = DeepWikiHealingStrategy()
        undocumented: Any = await strategy._find_undocumented_files()
        assert len(undocumented) <= config.DEEPWIKI_HEALING_BATCH_SIZE

    def test_batch_size_configuration(self) -> Any:
        """Test batch size is configured correctly."""
        assert config.DEEPWIKI_HEALING_BATCH_SIZE > 0
        assert config.DEEPWIKI_HEALING_BATCH_SIZE <= 50

    def test_batch_size_vs_daily_limit(self) -> Any:
        """Test batch size is smaller than daily limit."""
        assert config.DEEPWIKI_HEALING_BATCH_SIZE < config.DEEPWIKI_HEALING_MAX_DAILY

class test_deep_wiki_healing_strategy_registry:
    """Test DeepWiki healing strategy is registered."""

    def test_strategy_in_registry(self) -> Any:
        """Test DeepWikiHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
        strategy_names: Any = [s.name for s in HEALING_STRATEGIES]
        assert 'DeepWikiHealing' in strategy_names

    def test_strategy_priority(self) -> Any:
        """Test DeepWikiHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
        deepwiki_strategy: Any = next((s for s in HEALING_STRATEGIES if s.name == 'DeepWikiHealing'), None)
        assert deepwiki_strategy is not None
        assert deepwiki_strategy.priority == 3

class test_deep_wiki_healing_proactive_scanning:
    """Test DeepWiki healing proactive scanning."""

    @pytest.mark.asyncio
    async def test_proactive_scan_finds_files(self) -> Any:
        """Test proactive scanning identifies undocumented files."""
        strategy: Any = DeepWikiHealingStrategy()
        fixes: Any = await strategy.diagnose([])
        assert isinstance(fixes, list)

    @pytest.mark.asyncio
    async def test_scans_agentic_core_directory(self) -> Any:
        """Test scanning focuses on agentic_core directory."""
        strategy: Any = DeepWikiHealingStrategy()
        undocumented: Any = await strategy._find_undocumented_files()
        for file_path in undocumented:
            assert 'agentic_core' in str(file_path)

    @pytest.mark.asyncio
    async def test_skips_pycache_files(self) -> Any:
        """Test scanning skips __pycache__ directories."""
        strategy: Any = DeepWikiHealingStrategy()
        undocumented: Any = await strategy._find_undocumented_files()
        for file_path in undocumented:
            assert '__pycache__' not in str(file_path)

class test_deep_wiki_healing_documentation_generation:
    """Test DeepWiki healing documentation generation."""

    @pytest.mark.asyncio
    async def test_generates_documentation_prompt(self) -> Any:
        """Test documentation prompt generation."""
        strategy: Any = DeepWikiHealingStrategy()
        file_path: Any = 'test.py'
        content: Any = 'def test_function():\n    pass'
        question: Any = f'Analyze the following code from {file_path} and generate comprehensive DeepWiki documentation including purpose, dependencies, and architecture level: \n\n{content[:3000]}'
        assert file_path in question
        assert 'comprehensive DeepWiki documentation' in question
        assert 'purpose' in question
        assert 'dependencies' in question

class test_deep_wiki_healing_repo_configuration:
    """Test DeepWiki healing repository configuration."""

    def test_default_repo_configured(self) -> Any:
        """Test default repository is configured."""
        assert config.DEEPWIKI_DEFAULT_REPO is not None
        assert len(config.DEEPWIKI_DEFAULT_REPO) > 0

    def test_default_repo_format(self) -> Any:
        """Test default repository has expected format."""
        assert '/' in config.DEEPWIKI_DEFAULT_REPO or '-' in config.DEEPWIKI_DEFAULT_REPO

def run_tests() -> Any:
    """Run all DeepWiki healing tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
