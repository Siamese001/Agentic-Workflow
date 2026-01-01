"""
Integration Tests for Phase 16F: Sovereignty Verification
Validates that L1 Agent Logic uses L4 MCP Client instead of direct SDK.
"""
import pytest
import tempfile
from pathlib import Path
from agentic_core.L4_state.semantic_memory.pinecone_mcp_client import SovereignPineconeMCPClient, get_pinecone_mcp_client

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_pinecone_sovereignty:
    """Test suite for Pinecone sovereignty verification."""

    @pytest.mark.asyncio
    async def test_pinecone_mcp_client_exists(self) -> Any:
        """Verify Pinecone MCP client is available."""
        client: Any = get_pinecone_mcp_client()
        assert client is not None, 'Pinecone MCP client should be available'
        assert isinstance(client, SovereignPineconeMCPClient), 'Should be SovereignPineconeMCPClient instance'

    @pytest.mark.asyncio
    async def test_pinecone_mcp_client_singleton(self) -> Any:
        """Verify singleton pattern for Pinecone MCP client."""
        client1: Any = get_pinecone_mcp_client()
        client2: Any = get_pinecone_mcp_client()
        assert client1 is client2, 'Should return same singleton instance'

    @pytest.mark.asyncio
    async def test_pinecone_mcp_has_search_method(self) -> Any:
        """Verify Pinecone MCP client has search method."""
        client: Any = get_pinecone_mcp_client()
        assert hasattr(client, 'search'), 'Client should have search method'
        assert callable(client.search), 'search should be callable'

    @pytest.mark.asyncio
    async def test_pinecone_mcp_has_upsert_method(self) -> Any:
        """Verify Pinecone MCP client has upsert method."""
        client: Any = get_pinecone_mcp_client()
        assert hasattr(client, 'upsert'), 'Client should have upsert method'
        assert callable(client.upsert), 'upsert should be callable'

    @pytest.mark.asyncio
    async def test_pinecone_mcp_has_router(self) -> Any:
        """Verify Pinecone MCP client has L3 router."""
        client: Any = get_pinecone_mcp_client()
        assert hasattr(client, 'router'), 'Client should have router'
        assert client.router is not None, 'Router should be initialized'

class test_guardian_enforcement:
    """Test guardian enforcement of Pinecone MCP usage."""

    def test_guardian_blocks_pinecone_import(self) -> Any:
        """Verify guardian blocks direct pinecone imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from pinecone import Pinecone\n')
            f.write("pc = Pinecone(api_key='test')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block direct pinecone import'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_pinecone_instantiation(self) -> Any:
        """Verify guardian blocks direct Pinecone() instantiation."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import os\n')
            f.write('from pinecone import Pinecone\n')
            f.write("pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block Pinecone() instantiation'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_index_access(self) -> Any:
        """Verify guardian blocks direct pc.Index() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('pc = get_pinecone_client()\n')
            f.write("index = pc.Index('my-index')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block pc.Index() calls'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_hardcoded_index_name(self) -> Any:
        """Verify guardian blocks hardcoded index names."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("index_name = 'sovereign-territory-index'\n")
            f.write('results = search_index(index_name)\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block hardcoded index names'
        finally:
            temp_path.unlink()

    def test_guardian_allows_pinecone_mcp(self) -> Any:
        """Verify guardian allows Pinecone MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from agentic_core.L4_state.semantic_memory.pinecone_mcp_client import get_pinecone_mcp_client\n')
            f.write('client = get_pinecone_mcp_client()\n')
            f.write("results = await client.search('query text')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is True, 'Guardian should allow Pinecone MCP import'
        finally:
            temp_path.unlink()

class test_l4_state_integration:
    """Test L4 State integration with Pinecone MCP."""

    @pytest.mark.asyncio
    async def test_pinecone_mcp_routing(self) -> Any:
        """Verify operations route through L3 MCP router."""
        client: Any = get_pinecone_mcp_client()
        assert hasattr(client, 'router'), 'Client should have router'
        assert client.router is not None, 'Router should be initialized'
        assert client.router.role == 'semantic_memory', 'Router role should be semantic_memory'

    @pytest.mark.asyncio
    async def test_pinecone_mcp_methods_available(self) -> Any:
        """Test all required MCP methods are available."""
        client: Any = get_pinecone_mcp_client()
        required_methods: Any = ['search', 'upsert', 'inference_embed', 'describe_index_stats', 'health_check']
        for method in required_methods:
            assert hasattr(client, method), f'Client should have {method} method'
            assert callable(getattr(client, method)), f'{method} should be callable'

class test_agent_logic_sovereignty:
    """Test Agent Logic sovereignty - ensuring no direct SDK usage."""

    def test_no_direct_pinecone_in_agent_logic(self) -> Any:
        """Verify agent_logic.py doesn't use direct Pinecone SDK."""
        from pathlib import Path
        agent_logic_path: Any = Path('c:/Git/Agentic-Workflow/agentic_core/L1_cognition/thought_engine/agent_logic.py')
        if agent_logic_path.exists():
            content: Any = agent_logic_path.read_text()
            assert 'from pinecone import' not in content, 'Should not import from pinecone directly'
            assert 'Pinecone(' not in content, 'Should not instantiate Pinecone directly'
            assert 'sovereign-territory-index' not in content, 'Should not hardcode index names'

    def test_agent_logic_uses_mcp_pattern(self) -> Any:
        """Verify agent_logic.py follows MCP pattern if it uses Pinecone."""
        from pathlib import Path
        agent_logic_path: Any = Path('c:/Git/Agentic-Workflow/agentic_core/L1_cognition/thought_engine/agent_logic.py')
        if agent_logic_path.exists():
            content: Any = agent_logic_path.read_text()
            if 'pinecone' in content.lower():
                assert 'pinecone_mcp_client' in content or 'SovereignPineconeMCPClient' in content or 'get_pinecone_mcp_client' in content, 'Should use Pinecone MCP client if using Pinecone'

class test_mcp_client_features:
    """Test Pinecone MCP client features."""

    @pytest.mark.asyncio
    async def test_search_method_signature(self) -> Any:
        """Test search method has correct signature."""
        client: Any = get_pinecone_mcp_client()
        import inspect
        assert inspect.iscoroutinefunction(client.search), 'search should be async'

    @pytest.mark.asyncio
    async def test_upsert_method_signature(self) -> Any:
        """Test upsert method has correct signature."""
        client: Any = get_pinecone_mcp_client()
        import inspect
        assert inspect.iscoroutinefunction(client.upsert), 'upsert should be async'

    @pytest.mark.asyncio
    async def test_inference_embed_method_signature(self) -> Any:
        """Test inference_embed method has correct signature."""
        client: Any = get_pinecone_mcp_client()
        import inspect
from typing import Any
        assert inspect.iscoroutinefunction(client.inference_embed), 'inference_embed should be async'

def run_tests() -> Any:
    """Run all sovereignty verification tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
