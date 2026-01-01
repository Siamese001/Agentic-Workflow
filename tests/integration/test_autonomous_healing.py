"""
Integration Tests for Phase 17: Autonomous L0 Self-Healing
Validates autonomous healing engine with transactional safety.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import Any
from agentic_core.L0_maintenance.P1_core.healing_engine import SovereignHealingEngine, run_autonomous_healing
from agentic_core.L0_maintenance.P1_core.transaction_manager import HealingTransaction
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_healing_engine:
    """Test suite for Sovereign Healing Engine."""

    @pytest.mark.asyncio
    async def test_healing_engine_initialization(self) -> Any:
        """Test healing engine initializes correctly."""
        engine: Any = SovereignHealingEngine()
        assert engine is not None
        assert engine.applied_fixes == 0
        assert hasattr(engine, 'transaction_manager')
        assert hasattr(engine, 'git_client')
        assert hasattr(engine, 'fs_client')

    @pytest.mark.asyncio
    async def test_healing_disabled_in_config(self) -> Any:
        """Test healing respects config disable flag."""
        original_value: Any = config.AUTONOMOUS_HEALING_ENABLED
        object.__setattr__(config, 'AUTONOMOUS_HEALING_ENABLED', False)
        try:
            engine: Any = SovereignHealingEngine()
            result: Any = await engine.execute_autonomous_cycle([{'file': 'test.py', 'type': 'IMPORT_BREACH'}])
            assert result['status'] == 'disabled'
            assert result['applied_fixes'] == 0
        finally:
            object.__setattr__(config, 'AUTONOMOUS_HEALING_ENABLED', original_value)

    @pytest.mark.asyncio
    async def test_healing_no_issues(self) -> Any:
        """Test healing handles no issues gracefully."""
        engine: Any = SovereignHealingEngine()
        result: Any = await engine.execute_autonomous_cycle([])
        assert result['status'] == 'clean'
        assert result['applied_fixes'] == 0
        assert 'No violations' in result['message']

    @pytest.mark.asyncio
    async def test_healing_respects_max_fixes(self) -> Any:
        """Test healing respects max fixes per cycle limit."""
        issues: Any = [{'file': f'test{i}.py', 'type': 'IMPORT_BREACH', 'message': 'HTTP Clients'} for i in range(30)]
        engine: Any = SovereignHealingEngine()
        assert len(issues[:config.HEALING_MAX_FIXES_PER_CYCLE]) <= config.HEALING_MAX_FIXES_PER_CYCLE

class test_healing_fix_generation:
    """Test healing fix generation logic."""

    @pytest.mark.asyncio
    async def test_fix_requests_import(self) -> Any:
        """Test healing fixes direct requests imports."""
        engine: Any = SovereignHealingEngine()
        content: Any = "import requests\nresponse = requests.get('url')"
        fixed: Any = await engine._generate_fix(content, 'IMPORT_BREACH', 'HTTP Clients')
        assert fixed is not None
        assert 'import requests' not in fixed or '# Sovereign healing' in fixed

    @pytest.mark.asyncio
    async def test_fix_redis_import(self) -> Any:
        """Test healing fixes direct Redis imports."""
        engine: Any = SovereignHealingEngine()
        content: Any = 'import redis\nclient = redis.Redis()'
        fixed: Any = await engine._generate_fix(content, 'IMPORT_BREACH', 'Redis')
        assert fixed is not None
        assert '# Sovereign healing' in fixed or 'get_redis_client' in fixed

    @pytest.mark.asyncio
    async def test_fix_pinecone_import(self) -> Any:
        """Test healing fixes direct Pinecone imports."""
        engine: Any = SovereignHealingEngine()
        content: Any = 'from pinecone import Pinecone\npc = Pinecone()'
        fixed: Any = await engine._generate_fix(content, 'IMPORT_BREACH', 'Vector SDKs')
        assert fixed is not None
        assert '# Sovereign healing' in fixed or 'get_pinecone_mcp_client' in fixed

    @pytest.mark.asyncio
    async def test_fix_legacy_path(self) -> Any:
        """Test healing fixes legacy path references."""
        engine: Any = SovereignHealingEngine()
        content: Any = 'from agentic_core.tools.guardian import check'
        fixed: Any = await engine._generate_fix(content, 'PATH_BREACH', "Legacy 'tools/' path")
        assert fixed is not None
        assert 'agentic_core/utils/' in fixed or 'agentic_core.utils.' in fixed

class test_healing_strategies:
    """Test healing strategies from healing_strategies.py."""

    @pytest.mark.asyncio
    async def test_direct_redis_strategy(self) -> Any:
        """Test DirectRedisHealing strategy."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import DirectRedisHealing
        strategy: Any = DirectRedisHealing()
        issues: Any = [{'file': 'test.py', 'description': 'import redis detected', 'message': 'Redis direct usage'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) > 0
        assert fixes[0]['action'] == 'replace_import'
        assert 'get_redis_client' in fixes[0]['new_usage']

    @pytest.mark.asyncio
    async def test_direct_llm_strategy(self) -> Any:
        """Test DirectLLMHealing strategy."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import DirectLLMHealing
        strategy: Any = DirectLLMHealing()
        issues: Any = [{'file': 'test.py', 'description': 'openai sdk detected', 'message': 'OpenAI direct usage'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) > 0
        assert fixes[0]['action'] == 'replace_llm_sdk'
        assert fixes[0]['sdk'] == 'OpenAI'

    @pytest.mark.asyncio
    async def test_filesystem_bypass_strategy(self) -> Any:
        """Test FilesystemBypassHealing strategy."""
        from agentic_core.L0_maintenance.P1_core.healing_strategies import FilesystemBypassHealing
        strategy: Any = FilesystemBypassHealing()
        issues: Any = [{'file': 'test.py', 'description': 'open( detected', 'message': 'Direct file I/O'}]
        fixes: Any = await strategy.diagnose(issues)
        assert len(fixes) > 0
        assert fixes[0]['action'] == 'replace_io'
        assert 'get_filesystem_client' in fixes[0]['new_client']

class test_transaction_manager:
    """Test transaction manager for rollback safety."""

    def test_transaction_initialization(self) -> Any:
        """Test transaction manager initializes correctly."""
        txn: Any = HealingTransaction()
        assert txn is not None
        assert txn.committed is False
        assert txn.rolled_back is False
        assert len(txn.backups) == 0

    def test_transaction_backup(self) -> Any:
        """Test transaction can backup files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('test content')
            temp_path: Any = Path(f.name)
        try:
            txn: Any = HealingTransaction()
            result: Any = txn.backup(temp_path)
            assert result is True
            assert len(txn.backups) == 1
            assert txn.backups[0][0] == temp_path
        finally:
            temp_path.unlink()
            if txn.backup_dir.exists():
                import shutil
                shutil.rmtree(txn.backup_dir)

    def test_transaction_rollback(self) -> Any:
        """Test transaction can rollback changes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('original content')
            temp_path: Any = Path(f.name)
        try:
            txn: Any = HealingTransaction()
            txn.backup(temp_path)
            temp_path.write_text('modified content')
            result: Any = txn.rollback()
            assert result is True
            assert temp_path.read_text() == 'original content'
            assert txn.rolled_back is True
        finally:
            temp_path.unlink()

    def test_transaction_commit(self) -> Any:
        """Test transaction can commit successfully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('test content')
            temp_path: Any = Path(f.name)
        try:
            txn: Any = HealingTransaction()
            txn.backup(temp_path)
            result: Any = txn.commit()
            assert result is True
            assert txn.committed is True
            assert not txn.backup_dir.exists()
        finally:
            temp_path.unlink()

    def test_transaction_context_manager(self) -> Any:
        """Test transaction works as context manager."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('test content')
            temp_path: Any = Path(f.name)
        try:
            with HealingTransaction() as txn:
                txn.backup(temp_path)
            assert txn.committed is True
        finally:
            temp_path.unlink()

class test_healing_integration:
    """Test healing integration with auditor."""

    @pytest.mark.asyncio
    async def test_run_autonomous_healing_function(self) -> Any:
        """Test standalone healing function."""
        issues: Any = []
        result: Any = await run_autonomous_healing(issues)
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'applied_fixes' in result

    @pytest.mark.asyncio
    async def test_healing_config_settings(self) -> Any:
        """Test healing respects all config settings."""
        assert hasattr(config, 'AUTONOMOUS_HEALING_ENABLED')
        assert hasattr(config, 'HEALING_AUTO_APPLY')
        assert hasattr(config, 'HEALING_AUTO_COMMIT')
        assert hasattr(config, 'HEALING_AUTO_PR')
        assert hasattr(config, 'HEALING_MAX_FIXES_PER_CYCLE')
        assert isinstance(config.AUTONOMOUS_HEALING_ENABLED, bool)
        assert isinstance(config.HEALING_MAX_FIXES_PER_CYCLE, int)
        assert config.HEALING_MAX_FIXES_PER_CYCLE > 0

class test_healing_mcp_integration:
    """Test healing uses MCP clients correctly."""

    @pytest.mark.asyncio
    async def test_healing_uses_filesystem_mcp(self) -> Any:
        """Test healing uses Filesystem MCP for file operations."""
        engine: Any = SovereignHealingEngine()
        assert engine.fs_client is not None
        assert hasattr(engine.fs_client, 'read_text')
        assert hasattr(engine.fs_client, 'write_text')

    @pytest.mark.asyncio
    async def test_healing_uses_gitkraken_mcp(self) -> Any:
        """Test healing uses GitKraken MCP for version control."""
        engine: Any = SovereignHealingEngine()
        assert engine.git_client is not None
        assert hasattr(engine.git_client, 'add_and_commit')
        assert hasattr(engine.git_client, 'create_pull_request')

def run_tests() -> None:
    """Run all autonomous healing tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
