"""
Integration Tests for Phase 17: Autonomous L0 Self-Healing
Validates autonomous healing engine with transactional safety.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from agentic_core.L0_maintenance.P1_core.healing_engine import SovereignHealingEngine, run_autonomous_healing
from agentic_core.L0_maintenance.P1_core.transaction_manager import HealingTransaction
from agentic_core.config.P1_core.sovereign_config import config


class TestHealingEngine:
    """Test suite for Sovereign Healing Engine."""
    
    @pytest.mark.asyncio
    async def test_healing_engine_initialization(self):
        """Test healing engine initializes correctly."""
        engine = SovereignHealingEngine()
        assert engine is not None
        assert engine.applied_fixes == 0
        assert hasattr(engine, 'transaction_manager')
        assert hasattr(engine, 'git_client')
        assert hasattr(engine, 'fs_client')
    
    @pytest.mark.asyncio
    async def test_healing_disabled_in_config(self):
        """Test healing respects config disable flag."""
        # Temporarily disable healing
        original_value = config.AUTONOMOUS_HEALING_ENABLED
        object.__setattr__(config, 'AUTONOMOUS_HEALING_ENABLED', False)
        
        try:
            engine = SovereignHealingEngine()
            result = await engine.execute_autonomous_cycle([{"file": "test.py", "type": "IMPORT_BREACH"}])
            
            assert result["status"] == "disabled"
            assert result["applied_fixes"] == 0
        finally:
            object.__setattr__(config, 'AUTONOMOUS_HEALING_ENABLED', original_value)
    
    @pytest.mark.asyncio
    async def test_healing_no_issues(self):
        """Test healing handles no issues gracefully."""
        engine = SovereignHealingEngine()
        result = await engine.execute_autonomous_cycle([])
        
        assert result["status"] == "clean"
        assert result["applied_fixes"] == 0
        assert "No violations" in result["message"]
    
    @pytest.mark.asyncio
    async def test_healing_respects_max_fixes(self):
        """Test healing respects max fixes per cycle limit."""
        # Create more issues than the limit
        issues = [
            {"file": f"test{i}.py", "type": "IMPORT_BREACH", "message": "HTTP Clients"}
            for i in range(30)
        ]
        
        engine = SovereignHealingEngine()
        # Should only process up to HEALING_MAX_FIXES_PER_CYCLE
        assert len(issues[:config.HEALING_MAX_FIXES_PER_CYCLE]) <= config.HEALING_MAX_FIXES_PER_CYCLE


class TestHealingFixGeneration:
    """Test healing fix generation logic."""
    
    @pytest.mark.asyncio
    async def test_fix_requests_import(self):
        """Test healing fixes direct requests imports."""
        engine = SovereignHealingEngine()
        
        content = "import requests\nresponse = requests.get('url')"
        fixed = await engine._generate_fix(content, "IMPORT_BREACH", "HTTP Clients")
        
        assert fixed is not None
        assert "import requests" not in fixed or "# Sovereign healing" in fixed
    
    @pytest.mark.asyncio
    async def test_fix_redis_import(self):
        """Test healing fixes direct Redis imports."""
        engine = SovereignHealingEngine()
        
        content = "import redis\nclient = redis.Redis()"
        fixed = await engine._generate_fix(content, "IMPORT_BREACH", "Redis")
        
        assert fixed is not None
        assert "# Sovereign healing" in fixed or "get_redis_client" in fixed
    
    @pytest.mark.asyncio
    async def test_fix_pinecone_import(self):
        """Test healing fixes direct Pinecone imports."""
        engine = SovereignHealingEngine()
        
        content = "from pinecone import Pinecone\npc = Pinecone()"
        fixed = await engine._generate_fix(content, "IMPORT_BREACH", "Vector SDKs")
        
        assert fixed is not None
        assert "# Sovereign healing" in fixed or "get_pinecone_mcp_client" in fixed
    
    @pytest.mark.asyncio
    async def test_fix_legacy_path(self):
        """Test healing fixes legacy path references."""
        engine = SovereignHealingEngine()
        
        content = "from agentic_core.tools.guardian import check"
        fixed = await engine._generate_fix(content, "PATH_BREACH", "Legacy 'tools/' path")
        
        assert fixed is not None
        assert "agentic_core/utils/" in fixed or "agentic_core.utils." in fixed


class TestHealingStrategies:
    """Test healing strategies from healing_strategies.py."""
    
    @pytest.mark.asyncio
    async def test_direct_redis_strategy(self):
        """Test DirectRedisHealing strategy."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import DirectRedisHealing
        
        strategy = DirectRedisHealing()
        issues = [
            {"file": "test.py", "description": "import redis detected", "message": "Redis direct usage"}
        ]
        
        fixes = await strategy.diagnose(issues)
        assert len(fixes) > 0
        assert fixes[0]["action"] == "replace_import"
        assert "get_redis_client" in fixes[0]["new_usage"]
    
    @pytest.mark.asyncio
    async def test_direct_llm_strategy(self):
        """Test DirectLLMHealing strategy."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import DirectLLMHealing
        
        strategy = DirectLLMHealing()
        issues = [
            {"file": "test.py", "description": "openai sdk detected", "message": "OpenAI direct usage"}
        ]
        
        fixes = await strategy.diagnose(issues)
        assert len(fixes) > 0
        assert fixes[0]["action"] == "replace_llm_sdk"
        assert fixes[0]["sdk"] == "OpenAI"
    
    @pytest.mark.asyncio
    async def test_filesystem_bypass_strategy(self):
        """Test FilesystemBypassHealing strategy."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import FilesystemBypassHealing
        
        strategy = FilesystemBypassHealing()
        issues = [
            {"file": "test.py", "description": "open( detected", "message": "Direct file I/O"}
        ]
        
        fixes = await strategy.diagnose(issues)
        assert len(fixes) > 0
        assert fixes[0]["action"] == "replace_io"
        assert "get_filesystem_client" in fixes[0]["new_client"]


class TestTransactionManager:
    """Test transaction manager for rollback safety."""
    
    def test_transaction_initialization(self):
        """Test transaction manager initializes correctly."""
        txn = HealingTransaction()
        assert txn is not None
        assert txn.committed is False
        assert txn.rolled_back is False
        assert len(txn.backups) == 0
    
    def test_transaction_backup(self):
        """Test transaction can backup files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            txn = HealingTransaction()
            result = txn.backup(temp_path)
            
            assert result is True
            assert len(txn.backups) == 1
            assert txn.backups[0][0] == temp_path
        finally:
            temp_path.unlink()
            if txn.backup_dir.exists():
                import shutil
                shutil.rmtree(txn.backup_dir)
    
    def test_transaction_rollback(self):
        """Test transaction can rollback changes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("original content")
            temp_path = Path(f.name)
        
        try:
            txn = HealingTransaction()
            txn.backup(temp_path)
            
            # Modify file
            temp_path.write_text("modified content")
            
            # Rollback
            result = txn.rollback()
            
            assert result is True
            assert temp_path.read_text() == "original content"
            assert txn.rolled_back is True
        finally:
            temp_path.unlink()
    
    def test_transaction_commit(self):
        """Test transaction can commit successfully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            txn = HealingTransaction()
            txn.backup(temp_path)
            
            result = txn.commit()
            
            assert result is True
            assert txn.committed is True
            assert not txn.backup_dir.exists()
        finally:
            temp_path.unlink()
    
    def test_transaction_context_manager(self):
        """Test transaction works as context manager."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            with HealingTransaction() as txn:
                txn.backup(temp_path)
            
            # Should auto-commit on successful exit
            assert txn.committed is True
        finally:
            temp_path.unlink()


class TestHealingIntegration:
    """Test healing integration with auditor."""
    
    @pytest.mark.asyncio
    async def test_run_autonomous_healing_function(self):
        """Test standalone healing function."""
        issues = []
        result = await run_autonomous_healing(issues)
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "applied_fixes" in result
    
    @pytest.mark.asyncio
    async def test_healing_config_settings(self):
        """Test healing respects all config settings."""
        assert hasattr(config, 'AUTONOMOUS_HEALING_ENABLED')
        assert hasattr(config, 'HEALING_AUTO_APPLY')
        assert hasattr(config, 'HEALING_AUTO_COMMIT')
        assert hasattr(config, 'HEALING_AUTO_PR')
        assert hasattr(config, 'HEALING_MAX_FIXES_PER_CYCLE')
        
        assert isinstance(config.AUTONOMOUS_HEALING_ENABLED, bool)
        assert isinstance(config.HEALING_MAX_FIXES_PER_CYCLE, int)
        assert config.HEALING_MAX_FIXES_PER_CYCLE > 0


class TestHealingMCPIntegration:
    """Test healing uses MCP clients correctly."""
    
    @pytest.mark.asyncio
    async def test_healing_uses_filesystem_mcp(self):
        """Test healing uses Filesystem MCP for file operations."""
        engine = SovereignHealingEngine()
        
        # Verify fs_client is initialized
        assert engine.fs_client is not None
        assert hasattr(engine.fs_client, 'read_text')
        assert hasattr(engine.fs_client, 'write_text')
    
    @pytest.mark.asyncio
    async def test_healing_uses_gitkraken_mcp(self):
        """Test healing uses GitKraken MCP for version control."""
        engine = SovereignHealingEngine()
        
        # Verify git_client is initialized
        assert engine.git_client is not None
        assert hasattr(engine.git_client, 'add_and_commit')
        assert hasattr(engine.git_client, 'create_pull_request')


def run_tests():
    """Run all autonomous healing tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
