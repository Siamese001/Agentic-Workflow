"""
Integration Tests for MCP Manager Enhancements
Validates sovereign MCP connection management with async initialization and locking.
"""
import asyncio
import pytest
from agentic_core.L3_orchestration.workflow_engines.mcp_manager import MCPConnectionManager


class TestMCPConnectionManager:
    """Test suite for enhanced MCP Connection Manager."""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test MCP manager initializes correctly."""
        config = {"roles": {}}
        manager = MCPConnectionManager(config)
        
        assert manager is not None
        assert manager.config == config
        assert manager.connections == {}
        assert manager.initialized is False
        assert hasattr(manager, '_init_lock')
    
    @pytest.mark.asyncio
    async def test_async_initialization(self):
        """Test async initialization with role configuration."""
        config = {
            "roles": {
                "test_role": ["tool1", "tool2", "tool3"]
            }
        }
        manager = MCPConnectionManager(config)
        
        await manager.initialize()
        
        assert manager.initialized is True
        assert "test_role" in manager.connections
        assert manager.connections["test_role"]["status"] == "connected"
        assert len(manager.connections["test_role"]["tools"]) == 3
    
    @pytest.mark.asyncio
    async def test_initialization_idempotency(self):
        """Test initialization is idempotent (can be called multiple times)."""
        config = {"roles": {"role1": ["tool1"]}}
        manager = MCPConnectionManager(config)
        
        # Initialize multiple times
        await manager.initialize()
        await manager.initialize()
        await manager.initialize()
        
        # Should still be initialized only once
        assert manager.initialized is True
        assert len(manager.connections) == 1
    
    @pytest.mark.asyncio
    async def test_connect_triggers_initialization(self):
        """Test connect method triggers initialization if not initialized."""
        config = {"roles": {"role1": ["tool1"]}}
        manager = MCPConnectionManager(config)
        
        assert manager.initialized is False
        
        await manager.connect("role1")
        
        assert manager.initialized is True
    
    @pytest.mark.asyncio
    async def test_call_tool_triggers_initialization(self):
        """Test call_tool triggers initialization if not initialized."""
        config = {"roles": {"role1": ["tool1"]}}
        manager = MCPConnectionManager(config)
        
        assert manager.initialized is False
        
        result = await manager.call_tool("test_tool", {"arg1": "value1"})
        
        assert manager.initialized is True
        assert result["status"] == "executed"
        assert result["tool"] == "test_tool"
    
    @pytest.mark.asyncio
    async def test_call_tool_execution(self):
        """Test tool call execution returns expected result."""
        config = {"roles": {}}
        manager = MCPConnectionManager(config)
        
        result = await manager.call_tool("test_tool", {"arg1": "value1", "arg2": "value2"})
        
        assert result["status"] == "executed"
        assert result["tool"] == "test_tool"
        assert result["args"] == {"arg1": "value1", "arg2": "value2"}
        assert "result" in result
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test cleanup clears connections and resets initialization."""
        config = {"roles": {"role1": ["tool1"]}}
        manager = MCPConnectionManager(config)
        
        await manager.initialize()
        assert manager.initialized is True
        assert len(manager.connections) > 0
        
        await manager.cleanup()
        
        assert manager.initialized is False
        assert len(manager.connections) == 0
    
    @pytest.mark.asyncio
    async def test_multiple_roles_initialization(self):
        """Test initialization with multiple roles."""
        config = {
            "roles": {
                "role1": ["tool1", "tool2"],
                "role2": ["tool3", "tool4", "tool5"],
                "role3": ["tool6"]
            }
        }
        manager = MCPConnectionManager(config)
        
        await manager.initialize()
        
        assert len(manager.connections) == 3
        assert all(role in manager.connections for role in ["role1", "role2", "role3"])
        assert len(manager.connections["role1"]["tools"]) == 2
        assert len(manager.connections["role2"]["tools"]) == 5
        assert len(manager.connections["role3"]["tools"]) == 1
    
    @pytest.mark.asyncio
    async def test_empty_roles_initialization(self):
        """Test initialization with empty roles config."""
        config = {"roles": {}}
        manager = MCPConnectionManager(config)
        
        await manager.initialize()
        
        assert manager.initialized is True
        assert len(manager.connections) == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_initialization(self):
        """Test concurrent initialization calls are properly locked."""
        config = {"roles": {"role1": ["tool1"]}}
        manager = MCPConnectionManager(config)
        
        # Attempt concurrent initialization
        results = await asyncio.gather(
            manager.initialize(),
            manager.initialize(),
            manager.initialize()
        )
        
        # Should still be initialized only once
        assert manager.initialized is True
        assert len(manager.connections) == 1


class TestMCPManagerGuardianEnforcement:
    """Test guardian enforcement for MCP manager imports."""
    
    def test_guardian_blocks_duplicate_imports(self):
        """Test guardian blocks duplicate MCP manager imports."""
        from agentic_core.utils.guardian.sovereignty_auditor import BANNED_IMPORTS
        
        mcp_patterns = BANNED_IMPORTS.get("MCP Manager", [])
        assert len(mcp_patterns) > 0
        
        # Should block L2_execution imports
        assert any('L2_execution.*mcp_manager' in pattern for pattern in mcp_patterns)
        
        # Should block P1_core imports
        assert any('P1_core.*mcp_manager' in pattern for pattern in mcp_patterns)
        
        # Should block relative imports
        assert any(r'\.mcp_manager' in pattern for pattern in mcp_patterns)


class TestMCPManagerConnectionLifecycle:
    """Test MCP manager connection lifecycle."""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test full connection lifecycle: init -> use -> cleanup."""
        config = {"roles": {"role1": ["tool1"]}}
        manager = MCPConnectionManager(config)
        
        # Initialize
        await manager.initialize()
        assert manager.initialized is True
        
        # Use
        result = await manager.call_tool("test_tool", {})
        assert result["status"] == "executed"
        
        # Cleanup
        await manager.cleanup()
        assert manager.initialized is False
        
        # Can reinitialize after cleanup
        await manager.initialize()
        assert manager.initialized is True


def run_tests():
    """Run all MCP manager enhancement tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
