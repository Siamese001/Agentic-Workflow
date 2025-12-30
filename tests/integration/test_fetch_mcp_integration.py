"""
Integration Tests for Phase 16G: Fetch MCP Client
Validates sovereign content ingestion through MCP architecture.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from agentic_core.L2_execution.tool_registry.fetch_mcp_client import SovereignFetchMCPClient, get_fetch_client
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_fetch_mcp_integration:
    """Test suite for Fetch MCP client integration."""

    @pytest.mark.asyncio
    async def test_fetch_mcp_enabled(self) -> Any:
        """Verify Fetch MCP is enabled in sovereign config."""
        assert config.FETCH_MCP_ENABLED is True, 'Fetch MCP must be enabled'
        assert config.FETCH_MAX_CONTENT_LENGTH > 0, 'Max content length should be set'
        assert config.FETCH_TIMEOUT_SECONDS > 0, 'Timeout should be set'

    @pytest.mark.asyncio
    async def test_fetch_client_singleton(self) -> Any:
        """Verify singleton pattern for Fetch client."""
        client1: Any = get_fetch_client()
        client2: Any = get_fetch_client()
        assert client1 is client2, 'Should return same singleton instance'

    @pytest.mark.asyncio
    async def test_fetch_mcp_routing(self) -> Any:
        """Verify operations route through L3 MCP router."""
        client: Any = get_fetch_client()
        assert hasattr(client, 'router'), 'Client should have router'
        assert client.router is not None, 'Router should be initialized'
        assert client.router.role == 'content_ingestion', 'Router role should be content_ingestion'

    @pytest.mark.asyncio
    async def test_fetch_client_methods_available(self) -> Any:
        """Test all required MCP methods are available."""
        client: Any = get_fetch_client()
        required_methods: Any = ['get_clean_content', 'fetch_raw_html', 'fetch_youtube_transcript', 'fetch_multiple_urls', 'health_check']
        for method in required_methods:
            assert hasattr(client, method), f'Client should have {method} method'
            assert callable(getattr(client, method)), f'{method} should be callable'

class test_guardian_enforcement:
    """Test guardian enforcement of Fetch MCP usage."""

    def test_guardian_blocks_requests_import(self) -> Any:
        """Verify guardian blocks direct requests imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import requests\n')
            f.write("response = requests.get('https://example.com')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block requests import'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_httpx_import(self) -> Any:
        """Verify guardian blocks direct httpx imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import httpx\n')
            f.write('async with httpx.AsyncClient() as client:\n')
            f.write("    response = await client.get('https://example.com')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block httpx import'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_urllib_import(self) -> Any:
        """Verify guardian blocks direct urllib imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import urllib\n')
            f.write('from urllib.request import urlopen\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block urllib import'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_requests_get(self) -> Any:
        """Verify guardian blocks direct requests.get() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import requests\n')
            f.write("response = requests.get('https://api.example.com/data')\n")
            f.write('data = response.json()\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block requests.get()'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_httpx_async_client(self) -> Any:
        """Verify guardian blocks direct httpx.AsyncClient() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import httpx\n')
            f.write('client = httpx.AsyncClient()\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block httpx.AsyncClient()'
        finally:
            temp_path.unlink()

    def test_guardian_allows_fetch_mcp(self) -> Any:
        """Verify guardian allows Fetch MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from agentic_core.L2_execution.tool_registry.fetch_mcp_client import get_fetch_client\n')
            f.write('client = get_fetch_client()\n')
            f.write("content = await client.get_clean_content('https://example.com')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is True, 'Guardian should allow Fetch MCP import'
        finally:
            temp_path.unlink()

class test_l2_execution_integration:
    """Test L2 Execution integration with Fetch MCP."""

    @pytest.mark.asyncio
    async def test_fetch_client_initialization(self) -> Any:
        """Test client initializes correctly."""
        client: Any = get_fetch_client()
        assert client is not None, 'Client should initialize'
        assert hasattr(client, 'router'), 'Client should have router'

    @pytest.mark.asyncio
    async def test_clean_content_method_signature(self) -> Any:
        """Test get_clean_content method has correct signature."""
        client: Any = get_fetch_client()
        import inspect
        assert inspect.iscoroutinefunction(client.get_clean_content), 'get_clean_content should be async'

    @pytest.mark.asyncio
    async def test_raw_html_method_signature(self) -> Any:
        """Test fetch_raw_html method has correct signature."""
        client: Any = get_fetch_client()
        import inspect
        assert inspect.iscoroutinefunction(client.fetch_raw_html), 'fetch_raw_html should be async'

    @pytest.mark.asyncio
    async def test_youtube_transcript_method_signature(self) -> Any:
        """Test fetch_youtube_transcript method has correct signature."""
        client: Any = get_fetch_client()
        import inspect
        assert inspect.iscoroutinefunction(client.fetch_youtube_transcript), 'fetch_youtube_transcript should be async'

class test_content_ingestion:
    """Test content ingestion features."""

    @pytest.mark.asyncio
    async def test_markdown_conversion_enabled(self) -> Any:
        """Test Markdown conversion is enabled by default."""
        assert config.FETCH_EXTRACT_MARKDOWN is True, 'Markdown extraction should be enabled'

    @pytest.mark.asyncio
    async def test_max_content_length_configured(self) -> Any:
        """Test max content length is properly configured."""
        assert config.FETCH_MAX_CONTENT_LENGTH > 0, 'Max content length should be positive'
        assert config.FETCH_MAX_CONTENT_LENGTH <= 10000000, 'Max content length should be reasonable'

    @pytest.mark.asyncio
    async def test_timeout_configured(self) -> Any:
        """Test timeout is properly configured."""
        assert config.FETCH_TIMEOUT_SECONDS > 0, 'Timeout should be positive'
        assert config.FETCH_TIMEOUT_SECONDS <= 120, 'Timeout should be reasonable'

class test_sovereignty_protection:
    """Test sovereignty protection for content ingestion."""

    @pytest.mark.asyncio
    async def test_l3_routing_enforced(self) -> Any:
        """Test all fetch operations route through L3."""
        client: Any = get_fetch_client()
        assert hasattr(client, 'router'), 'Client must have L3 router'
        assert client.router.role == 'content_ingestion', 'Router must have content_ingestion role'

    @pytest.mark.asyncio
    async def test_mcp_tools_used(self) -> Any:
        """Test correct MCP tools are used."""
        client: Any = get_fetch_client()

def run_tests() -> Any:
    """Run all Fetch MCP integration tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
