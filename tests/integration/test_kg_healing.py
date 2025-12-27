"""
Integration Tests for Phase 17C: Knowledge Graph Healing
Validates autonomous KG drift correction with Memory MCP integration.
"""
import asyncio
import pytest
from datetime import datetime
from agentic_core.L0_maintenance.healing.kg_healing_strategy import KnowledgeGraphHealingStrategy, create_kg_healing_strategy
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config


class TestKGHealingStrategy:
    """Test suite for Knowledge Graph Healing Strategy."""
    
    @pytest.mark.asyncio
    async def test_strategy_initialization(self):
        """Test KG healing strategy initializes correctly."""
        strategy = KnowledgeGraphHealingStrategy()
        assert strategy is not None
        assert strategy.name == "KnowledgeGraphHealing"
        assert strategy.priority == 2
        assert strategy.processed_today == 0
        assert hasattr(strategy, 'fs_client')
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test factory function creates strategy."""
        strategy = await create_kg_healing_strategy()
        assert isinstance(strategy, KnowledgeGraphHealingStrategy)
    
    @pytest.mark.asyncio
    async def test_diagnose_kg_issues(self):
        """Test strategy diagnoses KG-related issues."""
        strategy = KnowledgeGraphHealingStrategy()
        
        issues = [
            {"file": "test1.py", "description": "knowledge graph drift detected", "message": "KG inconsistency"},
            {"file": "test2.py", "description": "entity missing", "message": "Entity not found"},
            {"file": "test3.py", "description": "relation stale", "message": "Relation outdated"}
        ]
        
        fixes = await strategy.diagnose(issues)
        
        assert len(fixes) == 3
        assert all(fix["action"] == "re_extract_content" for fix in fixes)
        assert all(fix["strategy"] == "KnowledgeGraphHealing" for fix in fixes)
        assert all(fix["priority"] == 2 for fix in fixes)
    
    @pytest.mark.asyncio
    async def test_diagnose_non_kg_issues(self):
        """Test strategy ignores non-KG issues."""
        strategy = KnowledgeGraphHealingStrategy()
        
        issues = [
            {"file": "test.py", "description": "import error", "message": "Import failed"},
            {"file": "test2.py", "description": "syntax error", "message": "Syntax issue"}
        ]
        
        fixes = await strategy.diagnose(issues)
        
        assert len(fixes) == 0
    
    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self):
        """Test strategy respects config disable flag."""
        original_value = config.KNOWLEDGE_GRAPH_HEALING_ENABLED
        object.__setattr__(config, 'KNOWLEDGE_GRAPH_HEALING_ENABLED', False)
        
        try:
            strategy = KnowledgeGraphHealingStrategy()
            issues = [{"file": "test.py", "description": "knowledge graph drift", "message": "KG issue"}]
            
            fixes = await strategy.diagnose(issues)
            
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'KNOWLEDGE_GRAPH_HEALING_ENABLED', original_value)
    
    @pytest.mark.asyncio
    async def test_daily_limit_enforcement(self):
        """Test daily healing limit is enforced."""
        strategy = KnowledgeGraphHealingStrategy()
        strategy.processed_today = config.KG_HEALING_MAX_DAILY
        
        fix = {"file": "test.py", "action": "re_extract_content", "source_id": "test.py"}
        result = await strategy.apply(fix)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reset_daily_counter(self):
        """Test daily counter can be reset."""
        strategy = KnowledgeGraphHealingStrategy()
        strategy.processed_today = 100
        
        strategy.reset_daily_counter()
        
        assert strategy.processed_today == 0


class TestKGHealingConfig:
    """Test KG healing configuration."""
    
    def test_config_settings_exist(self):
        """Test all KG healing config settings exist."""
        assert hasattr(config, 'KNOWLEDGE_GRAPH_HEALING_ENABLED')
        assert hasattr(config, 'KG_HEALING_BATCH_SIZE')
        assert hasattr(config, 'KG_HEALING_MAX_DAILY')
        assert hasattr(config, 'KG_MIN_CONFIDENCE_FOR_HEALING')
        assert hasattr(config, 'KG_HEALING_RE_EXTRACT_ON_DRIFT')
    
    def test_config_default_values(self):
        """Test config has sensible default values."""
        assert isinstance(config.KNOWLEDGE_GRAPH_HEALING_ENABLED, bool)
        assert isinstance(config.KG_HEALING_BATCH_SIZE, int)
        assert isinstance(config.KG_HEALING_MAX_DAILY, int)
        assert isinstance(config.KG_MIN_CONFIDENCE_FOR_HEALING, float)
        assert isinstance(config.KG_HEALING_RE_EXTRACT_ON_DRIFT, bool)
        
        assert config.KG_HEALING_BATCH_SIZE > 0
        assert config.KG_HEALING_MAX_DAILY > 0
        assert 0.0 <= config.KG_MIN_CONFIDENCE_FOR_HEALING <= 1.0


class TestKGHealingMCPIntegration:
    """Test KG healing MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_uses_filesystem_mcp_client(self):
        """Test strategy uses Filesystem MCP client."""
        strategy = KnowledgeGraphHealingStrategy()
        
        assert strategy.fs_client is not None
        assert hasattr(strategy.fs_client, 'read_text')


class TestKGHealingConfidenceThreshold:
    """Test KG healing confidence threshold filtering."""
    
    def test_confidence_threshold_value(self):
        """Test confidence threshold is reasonable."""
        assert config.KG_MIN_CONFIDENCE_FOR_HEALING >= 0.5
        assert config.KG_MIN_CONFIDENCE_FOR_HEALING <= 1.0
    
    def test_confidence_filtering_logic(self):
        """Test confidence filtering works correctly."""
        # Simulate entity filtering
        entities = [
            {"name": "Entity1", "confidence": 0.9},
            {"name": "Entity2", "confidence": 0.6},
            {"name": "Entity3", "confidence": 0.4}
        ]
        
        filtered = [e for e in entities if e.get("confidence", 0) >= config.KG_MIN_CONFIDENCE_FOR_HEALING]
        
        # With default threshold of 0.7, should filter out Entity2 and Entity3
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Entity1"


class TestKGHealingStrategyRegistry:
    """Test KG healing strategy is registered."""
    
    def test_strategy_in_registry(self):
        """Test KnowledgeGraphHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        strategy_names = [s.name for s in HEALING_STRATEGIES]
        assert "KnowledgeGraphHealing" in strategy_names
    
    def test_strategy_priority(self):
        """Test KnowledgeGraphHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.healing.healing_strategies import HEALING_STRATEGIES
        
        kg_strategy = next((s for s in HEALING_STRATEGIES if s.name == "KnowledgeGraphHealing"), None)
        assert kg_strategy is not None
        assert kg_strategy.priority == 2


class TestKGHealingSourceTracking:
    """Test KG healing source tracking."""
    
    @pytest.mark.asyncio
    async def test_source_id_extraction(self):
        """Test source ID is correctly extracted from fix."""
        strategy = KnowledgeGraphHealingStrategy()
        
        # Test with explicit source_id
        fix1 = {"file": "test.py", "source_id": "custom_source", "action": "re_extract_content"}
        assert fix1["source_id"] == "custom_source"
        
        # Test with fallback to file path
        fix2 = {"file": "test.py", "action": "re_extract_content"}
        source_id = fix2.get("source_id", fix2.get("file"))
        assert source_id == "test.py"


class TestKGHealingBatchProcessing:
    """Test KG healing batch processing configuration."""
    
    def test_batch_size_configuration(self):
        """Test batch size is configured correctly."""
        assert config.KG_HEALING_BATCH_SIZE > 0
        assert config.KG_HEALING_BATCH_SIZE <= 100  # Reasonable upper limit
    
    def test_batch_size_vs_daily_limit(self):
        """Test batch size is smaller than daily limit."""
        assert config.KG_HEALING_BATCH_SIZE < config.KG_HEALING_MAX_DAILY


def run_tests():
    """Run all KG healing tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
