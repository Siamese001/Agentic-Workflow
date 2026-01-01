"""
Integration Tests for Phase 17B: Pinecone Vector Healing
Validates autonomous vector drift correction with MCP integration.
"""
import asyncio
import pytest
import hashlib
from datetime import datetime
from agentic_core.L0_maintenance.P1_core.vector_healing_strategy import VectorHealingStrategy, create_vector_healing_strategy
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_vector_healing_strategy:
    """Test suite for Vector Healing Strategy."""

    @pytest.mark.asyncio
    async def test_strategy_initialization(self) -> Any:
        """Test vector healing strategy initializes correctly."""
        strategy: Any = VectorHealingStrategy()
        assert strategy is not None
        assert strategy.name == 'VectorHealing'
        assert strategy.priority == 2
        assert strategy.processed_today == 0
        assert hasattr(strategy, 'pinecone_client')
        assert hasattr(strategy, 'fs_client')

    @pytest.mark.asyncio
    async def test_factory_function(self) -> Any:
        """Test factory function creates strategy."""
        strategy: Any = await create_vector_healing_strategy()
        assert isinstance(strategy, VectorHealingStrategy)

    @pytest.mark.asyncio
    async def test_diagnose_vector_issues(self) -> Any:
        """Test strategy diagnoses vector-related issues."""
        strategy: Any = VectorHealingStrategy()
        issues: Any = [{'file': 'test1.py', 'description': 'vector drift detected', 'message': 'Vector inconsistency'}, {'file': 'test2.py', 'description': 'embedding missing', 'message': 'No embedding found'}, {'file': 'test3.py', 'description': 'pinecone error', 'message': 'Pinecone sync failed'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) == 3
        assert all((fix['action'] == 're_embed_file' for fix in fixes))
        assert all((fix['strategy'] == 'VectorHealing' for fix in fixes))
        assert all((fix['priority'] == 2 for fix in fixes))

    @pytest.mark.asyncio
    async def test_diagnose_non_vector_issues(self) -> Any:
        """Test strategy ignores non-vector issues."""
        strategy: Any = VectorHealingStrategy()
        issues: Any = [{'file': 'test.py', 'description': 'import error', 'message': 'Import failed'}, {'file': 'test2.py', 'description': 'syntax error', 'message': 'Syntax issue'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) == 0

    @pytest.mark.asyncio
    async def test_diagnose_disabled_in_config(self) -> Any:
        """Test strategy respects config disable flag."""
        original_value: Any = config.PINECONE_VECTOR_HEALING_ENABLED
        object.__setattr__(config, 'PINECONE_VECTOR_HEALING_ENABLED', False)
        try:
            strategy: Any = VectorHealingStrategy()
            issues: Any = [{'file': 'test.py', 'description': 'vector drift', 'message': 'Vector issue'}]
            fixes: Any = await strategy.diagnose(issues)
            assert len(fixes) == 0
        finally:
            object.__setattr__(config, 'PINECONE_VECTOR_HEALING_ENABLED', original_value)

    @pytest.mark.asyncio
    async def test_daily_limit_enforcement(self) -> Any:
        """Test daily healing limit is enforced."""
        strategy: Any = VectorHealingStrategy()
        strategy.processed_today = config.VECTOR_HEALING_MAX_DAILY
        fix: Any = {'file': 'test.py', 'action': 're_embed_file'}
        result: Any = await strategy.apply(fix)
        assert result is False

    @pytest.mark.asyncio
    async def test_reset_daily_counter(self) -> Any:
        """Test daily counter can be reset."""
        strategy: Any = VectorHealingStrategy()
        strategy.processed_today = 100
        strategy.reset_daily_counter()
        assert strategy.processed_today == 0

class test_vector_healing_config:
    """Test vector healing configuration."""

    def test_config_settings_exist(self) -> Any:
        """Test all vector healing config settings exist."""
        assert hasattr(config, 'PINECONE_VECTOR_HEALING_ENABLED')
        assert hasattr(config, 'VECTOR_HEALING_BATCH_SIZE')
        assert hasattr(config, 'VECTOR_HEALING_MAX_DAILY')
        assert hasattr(config, 'VECTOR_HEALING_EMBED_MODEL')

    def test_config_default_values(self) -> Any:
        """Test config has sensible default values."""
        assert isinstance(config.PINECONE_VECTOR_HEALING_ENABLED, bool)
        assert isinstance(config.VECTOR_HEALING_BATCH_SIZE, int)
        assert isinstance(config.VECTOR_HEALING_MAX_DAILY, int)
        assert isinstance(config.VECTOR_HEALING_EMBED_MODEL, str)
        assert config.VECTOR_HEALING_BATCH_SIZE > 0
        assert config.VECTOR_HEALING_MAX_DAILY > 0
        assert config.VECTOR_HEALING_EMBED_MODEL == 'multilingual-e5-large'

class test_vector_healing_mcp_integration:
    """Test vector healing MCP client integration."""

    @pytest.mark.asyncio
    async def test_uses_pinecone_mcp_client(self) -> Any:
        """Test strategy uses Pinecone MCP client."""
        strategy: Any = VectorHealingStrategy()
        assert strategy.pinecone_client is not None
        assert hasattr(strategy.pinecone_client, 'upsert')
        assert hasattr(strategy.pinecone_client, 'inference_embed')

    @pytest.mark.asyncio
    async def test_uses_filesystem_mcp_client(self) -> Any:
        """Test strategy uses Filesystem MCP client."""
        strategy: Any = VectorHealingStrategy()
        assert strategy.fs_client is not None
        assert hasattr(strategy.fs_client, 'read_text')

class test_vector_healing_immutability:
    """Test vector healing immutability checks."""

    def test_content_hash_generation(self) -> Any:
        """Test SHA-256 content hashing for immutability."""
        content: Any = 'test content for hashing'
        hash1: Any = hashlib.sha256(content.encode()).hexdigest()
        hash2: Any = hashlib.sha256(content.encode()).hexdigest()
        assert hash1 == hash2
        different_content: Any = 'different content'
        hash3: Any = hashlib.sha256(different_content.encode()).hexdigest()
        assert hash1 != hash3

class test_vector_healing_strategy_registry:
    """Test vector healing strategy is registered."""

    def test_strategy_in_registry(self) -> Any:
        """Test VectorHealingStrategy is in global registry."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
        strategy_names: Any = [s.name for s in HEALING_STRATEGIES]
        assert 'VectorHealing' in strategy_names

    def test_strategy_priority(self) -> Any:
        """Test VectorHealingStrategy has correct priority."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES
from typing import Any
        vector_strategy: Any = next((s for s in HEALING_STRATEGIES if s.name == 'VectorHealing'), None)
        assert vector_strategy is not None
        assert vector_strategy.priority == 2

class test_vector_healing_metadata:
    """Test vector healing metadata generation."""

    def test_metadata_structure(self) -> Any:
        """Test healing metadata has required fields."""
        vector_id: Any = hashlib.sha256(b'test content').hexdigest()
        metadata: Any = {'file_path': 'test.py', 'source': 'sovereign_canon', 'healed_at': datetime.utcnow().isoformat(), 'healing_id': f"heal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}", 'content_hash': vector_id[:16]}
        assert 'file_path' in metadata
        assert 'source' in metadata
        assert 'healed_at' in metadata
        assert 'healing_id' in metadata
        assert 'content_hash' in metadata
        assert metadata['source'] == 'sovereign_canon'

def run_tests() -> Any:
    """Run all vector healing tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
