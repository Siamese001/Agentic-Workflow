"""
Integration Tests for MCP Manager Enhancements
Validates sovereign MCP connection management with async initialization and locking.
"""
import asyncio
import pytest
from agentic_core.L3_orchestration.workflow_engines.mcp_manager import MCPConnectionManager

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_mcp_connection_manager:
    """Test suite for enhanced MCP Connection Manager."""

    @pytest.mark.asyncio
    async def test_manager_initialization(self) -> Any:
        """Test MCP manager initializes correctly."""
        config: Any = {'roles': {}}
        manager: Any = MCPConnectionManager(config)
        assert manager is not None
        assert manager.config == config
        assert manager.connections == {}
        assert manager.initialized is False
        assert hasattr(manager, '_init_lock')

    @pytest.mark.asyncio
    async def test_async_initialization(self) -> Any:
        """Test async initialization with role configuration."""
        config: Any = {'roles': {'test_role': ['tool1', 'tool2', 'tool3']}}
        manager: Any = MCPConnectionManager(config)
        await manager.initialize()
        assert manager.initialized is True
        assert 'test_role' in manager.connections
        assert manager.connections['test_role']['status'] == 'connected'
        assert len(manager.connections['test_role']['tools']) == 3

    @pytest.mark.asyncio
    async def test_initialization_idempotency(self) -> Any:
        """Test initialization is idempotent (can be called multiple times)."""
        config: Any = {'roles': {'role1': ['tool1']}}
        manager: Any = MCPConnectionManager(config)
        await manager.initialize()
        await manager.initialize()
        await manager.initialize()
        assert manager.initialized is True
        assert len(manager.connections) == 1

    @pytest.mark.asyncio
    async def test_connect_triggers_initialization(self) -> Any:
        """Test connect method triggers initialization if not initialized."""
        config: Any = {'roles': {'role1': ['tool1']}}
        manager: Any = MCPConnectionManager(config)
        assert manager.initialized is False
        await manager.connect('role1')
        assert manager.initialized is True

    @pytest.mark.asyncio
    async def test_call_tool_triggers_initialization(self) -> Any:
        """Test call_tool triggers initialization if not initialized."""
        config: Any = {'roles': {'role1': ['tool1']}}
        manager: Any = MCPConnectionManager(config)
        assert manager.initialized is False
        result: Any = await manager.call_tool('test_tool', {'arg1': 'value1'})
        assert manager.initialized is True
        assert result['status'] == 'executed'
        assert result['tool'] == 'test_tool'

    @pytest.mark.asyncio
    async def test_call_tool_execution(self) -> Any:
        """Test tool call execution returns expected result."""
        config: Any = {'roles': {}}
        manager: Any = MCPConnectionManager(config)
        result: Any = await manager.call_tool('test_tool', {'arg1': 'value1', 'arg2': 'value2'})
        assert result['status'] == 'executed'
        assert result['tool'] == 'test_tool'
        assert result['args'] == {'arg1': 'value1', 'arg2': 'value2'}
        assert 'result' in result

    @pytest.mark.asyncio
    async def test_cleanup(self) -> Any:
        """Test cleanup clears connections and resets initialization."""
        config: Any = {'roles': {'role1': ['tool1']}}
        manager: Any = MCPConnectionManager(config)
        await manager.initialize()
        assert manager.initialized is True
        assert len(manager.connections) > 0
        await manager.cleanup()
        assert manager.initialized is False
        assert len(manager.connections) == 0

    @pytest.mark.asyncio
    async def test_multiple_roles_initialization(self) -> Any:
        """Test initialization with multiple roles."""
        config: Any = {'roles': {'role1': ['tool1', 'tool2'], 'role2': ['tool3', 'tool4', 'tool5'], 'role3': ['tool6']}}
        manager: Any = MCPConnectionManager(config)
        await manager.initialize()
        assert len(manager.connections) == 3
        assert all((role in manager.connections for role in ['role1', 'role2', 'role3']))
        assert len(manager.connections['role1']['tools']) == 2
        assert len(manager.connections['role2']['tools']) == 5
        assert len(manager.connections['role3']['tools']) == 1

    @pytest.mark.asyncio
    async def test_empty_roles_initialization(self) -> Any:
        """Test initialization with empty roles config."""
        config: Any = {'roles': {}}
        manager: Any = MCPConnectionManager(config)
        await manager.initialize()
        assert manager.initialized is True
        assert len(manager.connections) == 0

    @pytest.mark.asyncio
    async def test_concurrent_initialization(self) -> Any:
        """Test concurrent initialization calls are properly locked."""
        config: Any = {'roles': {'role1': ['tool1']}}
        manager: Any = MCPConnectionManager(config)
        results: Any = await asyncio.gather(manager.initialize(), manager.initialize(), manager.initialize())
        assert manager.initialized is True
        assert len(manager.connections) == 1

class test_mcp_manager_guardian_enforcement:
    """Test guardian enforcement for MCP manager imports."""

    def test_guardian_blocks_duplicate_imports(self) -> Any:
        """Test guardian blocks duplicate MCP manager imports."""
        from agentic_core.utils.guardian.sovereignty_auditor import BANNED_IMPORTS
from typing import Any
        mcp_patterns: Any = BANNED_IMPORTS.get('MCP Manager', [])
        assert len(mcp_patterns) > 0
        assert any(('L2_execution.*mcp_manager' in pattern for pattern in mcp_patterns))
        assert any(('P1_core.*mcp_manager' in pattern for pattern in mcp_patterns))
        assert any(('\\.mcp_manager' in pattern for pattern in mcp_patterns))

class test_mcp_manager_connection_lifecycle:
    """Test MCP manager connection lifecycle."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self) -> Any:
        """Test full connection lifecycle: init -> use -> cleanup."""
        config: Any = {'roles': {'role1': ['tool1']}}
        manager: Any = MCPConnectionManager(config)
        await manager.initialize()
        assert manager.initialized is True
        result: Any = await manager.call_tool('test_tool', {})
        assert result['status'] == 'executed'
        await manager.cleanup()
        assert manager.initialized is False
        await manager.initialize()
        assert manager.initialized is True

def run_tests() -> Any:
    """Run all MCP manager enhancement tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
