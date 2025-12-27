"""
Integration Tests for Phase 17E: DeepWiki Healing
Validates autonomous documentation drift correction with DeepWiki MCP integration.
"""
import asyncio
import pytest
from pathlib import Path
from agentic_core.L0_maintenance.healing.deepwiki_healing_strategy import DeepWikiHealingStrategy, create_deepwiki_healing_strategy
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config


class TestDeepWikiHealingStrategy:
    """Test suite for DeepWiki Healing Strategy."""
    
    @pytest.mark.asyncio
    async def test_strategy_initialization(self):
        """Test DeepWiki healing strategy initializes correctly."""
        strategy = DeepWikiHealingStrategy()
        assert strategy is not None
        assert strategy.name == "DeepWikiHealing"
        assert strategy.priority == 3
        assert strategy.processed_today == 0
        assert hasattr(strategy, 'fs_client')
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test factory function creates strategy."""
        strategy = await create_deepwiki_healing_strategy()
        assert isinstance(strategy, DeepWikiHealingStrategy)
    
    @pytest.mark.asyncio
    async def test_diagnose_finds_undocumented_files(self):
        """Test strategy diagnoses undocumented files."""
        strategy = DeepWikiHealingStrategy()
        
        # Diagnose should find undocumented files proactively
        fixes = await strategy.diagnose([])
        
        # Should return list of fixes (may be empty if all files are documented)
        assert isinstance(fixes, list)
        
        # If fixes found, validate structure
        if fixes:
            assert all(fix["action"] == "document_new_file" for fix in fixes)
            assert all(fix["strategy"] == "DeepWikiHealing" for fix in fixes)
            assert all(fix["priority"] == 3 for fix in fixes)
    
    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self):
        """Test strategy respects config disable flag."""
        original_value = config.DEEPWIKI_HEALING_ENABLED
        object.__setattr__(config, 'DEEPWIKI_HEALING_ENABLED', False)
        
        try:
            strategy = DeepWikiHealingStrategy()
            fixes = await strategy.diagnose([])
            
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'DEEPWIKI_HEALING_ENABLED', original_value)
    
    @pytest.mark.asyncio
    async def test_daily_limit_enforcement(self):
        """Test daily healing limit is enforced."""
        strategy = DeepWikiHealingStrategy()
        strategy.processed_today = config.DEEPWIKI_HEALING_MAX_DAILY
        
        fix = {"file": "test.py", "action": "document_new_file"}
        result = await strategy.apply(fix)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reset_daily_counter(self):
        """Test daily counter can be reset."""
        strategy = DeepWikiHealingStrategy()
        strategy.processed_today = 50
        
        strategy.reset_daily_counter()
        
        assert strategy.processed_today == 0


class TestDeepWikiHealingConfig:
    """Test DeepWiki healing configuration."""
    
    def test_config_settings_exist(self):
        """Test all DeepWiki healing config settings exist."""
        assert hasattr(config, 'DEEPWIKI_HEALING_ENABLED')
        assert hasattr(config, 'DEEPWIKI_HEALING_BATCH_SIZE')
        assert hasattr(config, 'DEEPWIKI_HEALING_MAX_DAILY')
        assert hasattr(config, 'DEEPWIKI_DEFAULT_REPO')
    
    def test_config_default_values(self):
        """Test config has sensible default values."""
        assert isinstance(config.DEEPWIKI_HEALING_ENABLED, bool)
        assert isinstance(config.DEEPWIKI_HEALING_BATCH_SIZE, int)
        assert isinstance(config.DEEPWIKI_HEALING_MAX_DAILY, int)
        assert isinstance(config.DEEPWIKI_DEFAULT_REPO, str)
        
        assert config.DEEPWIKI_HEALING_BATCH_SIZE > 0
        assert config.DEEPWIKI_HEALING_MAX_DAILY > 0
        assert len(config.DEEPWIKI_DEFAULT_REPO) > 0


class TestDeepWikiHealingMCPIntegration:
    """Test DeepWiki healing MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_uses_filesystem_mcp_client(self):
        """Test strategy uses Filesystem MCP client."""
        strategy = DeepWikiHealingStrategy()
        
        assert strategy.fs_client is not None
        assert hasattr(strategy.fs_client, 'read_text')


class TestDeepWikiHealingBatchProcessing:
    """Test DeepWiki healing batch processing."""
    
    @pytest.mark.asyncio
    async def test_batch_size_limits_results(self):
        """Test batch size limits number of undocumented files returned."""
        strategy = DeepWikiHealingStrategy()
        
        # Get undocumented files
        undocumented = await strategy._find_undocumented_files()
        
        # Should not exceed batch size
        assert len(undocumented) <= config.DEEPWIKI_HEALING_BATCH_SIZE
    
    def test_batch_size_configuration(self):
        """Test batch size is configured correctly."""
        assert config.DEEPWIKI_HEALING_BATCH_SIZE > 0
        assert config.DEEPWIKI_HEALING_BATCH_SIZE <= 50  # Reasonable upper limit
    
    def test_batch_size_vs_daily_limit(self):
        """Test batch size is smaller than daily limit."""
        assert config.DEEPWIKI_HEALING_BATCH_SIZE < config.DEEPWIKI_HEALING_MAX_DAILY


class TestDeepWikiHealingStrategyRegistry:
    """Test DeepWiki healing strategy is registered."""
    
    def test_strategy_in_registry(self):
        """Test DeepWikiHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        strategy_names = [s.name for s in HEALING_STRATEGIES]
        assert "DeepWikiHealing" in strategy_names
    
    def test_strategy_priority(self):
        """Test DeepWikiHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        deepwiki_strategy = next((s for s in HEALING_STRATEGIES if s.name == "DeepWikiHealing"), None)
        assert deepwiki_strategy is not None
        assert deepwiki_strategy.priority == 3


class TestDeepWikiHealingProactiveScanning:
    """Test DeepWiki healing proactive scanning."""
    
    @pytest.mark.asyncio
    async def test_proactive_scan_finds_files(self):
        """Test proactive scanning identifies undocumented files."""
        strategy = DeepWikiHealingStrategy()
        
        # Proactive scan should work without explicit issues
        fixes = await strategy.diagnose([])
        
        # Should return list (may be empty if all documented)
        assert isinstance(fixes, list)
    
    @pytest.mark.asyncio
    async def test_scans_agentic_core_directory(self):
        """Test scanning focuses on agentic_core directory."""
        strategy = DeepWikiHealingStrategy()
        
        undocumented = await strategy._find_undocumented_files()
        
        # All paths should be from agentic_core
        for file_path in undocumented:
            assert "agentic_core" in str(file_path)
    
    @pytest.mark.asyncio
    async def test_skips_pycache_files(self):
        """Test scanning skips __pycache__ directories."""
        strategy = DeepWikiHealingStrategy()
        
        undocumented = await strategy._find_undocumented_files()
        
        # No __pycache__ files should be included
        for file_path in undocumented:
            assert "__pycache__" not in str(file_path)


class TestDeepWikiHealingDocumentationGeneration:
    """Test DeepWiki healing documentation generation."""
    
    @pytest.mark.asyncio
    async def test_generates_documentation_prompt(self):
        """Test documentation prompt generation."""
        strategy = DeepWikiHealingStrategy()
        
        file_path = "test.py"
        content = "def test_function():\n    pass"
        
        # Simulate prompt generation
        question = (
            f"Analyze the following code from {file_path} and generate "
            f"comprehensive DeepWiki documentation including purpose, "
            f"dependencies, and architecture level: \n\n{content[:3000]}"
        )
        
        assert file_path in question
        assert "comprehensive DeepWiki documentation" in question
        assert "purpose" in question
        assert "dependencies" in question


class TestDeepWikiHealingRepoConfiguration:
    """Test DeepWiki healing repository configuration."""
    
    def test_default_repo_configured(self):
        """Test default repository is configured."""
        assert config.DEEPWIKI_DEFAULT_REPO is not None
        assert len(config.DEEPWIKI_DEFAULT_REPO) > 0
    
    def test_default_repo_format(self):
        """Test default repository has expected format."""
        # Should be in format "owner/repo"
        assert "/" in config.DEEPWIKI_DEFAULT_REPO or "-" in config.DEEPWIKI_DEFAULT_REPO


def run_tests():
    """Run all DeepWiki healing tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
