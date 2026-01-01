"""
Integration Tests for Phase 16C: Filesystem MCP Client
Validates sovereign file operations through MCP architecture.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client import get_filesystem_client, SovereignFilesystemMCPClient
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_filesystem_mcp_integration:
    """Test suite for Filesystem MCP client integration."""

    @pytest.mark.asyncio
    async def test_filesystem_mcp_enabled(self) -> Any:
        """Verify Filesystem MCP is enabled in sovereign config."""
        assert config.FILESYSTEM_MCP_ENABLED is True, 'Filesystem MCP must be enabled'
        assert config.FILESYSTEM_MAX_READ_SIZE == 10000000, 'Max read size should be 10MB'
        assert isinstance(config.FILESYSTEM_ALLOWED_ROOTS, list), 'Allowed roots should be a list'
        assert 'agentic_core' in config.FILESYSTEM_ALLOWED_ROOTS, 'agentic_core should be allowed'
        assert isinstance(config.FILESYSTEM_FORBIDDEN_PATTERNS, list), 'Forbidden patterns should be a list'

    @pytest.mark.asyncio
    async def test_filesystem_client_singleton(self) -> Any:
        """Verify singleton pattern for Filesystem client."""
        client1: Any = get_filesystem_client()
        client2: Any = get_filesystem_client()
        assert client1 is client2, 'Should return same singleton instance'

    @pytest.mark.asyncio
    async def test_path_validation_sandbox(self) -> Any:
        """Test path validation enforces sandbox."""
        client: Any = get_filesystem_client()
        with pytest.raises(PermissionError, match='escapes execution context'):
            client._validate_path('/etc/passwd')

    @pytest.mark.asyncio
    async def test_path_validation_allowed_roots(self) -> Any:
        """Test path validation enforces allowed roots."""
        client: Any = get_filesystem_client()
        with pytest.raises(PermissionError, match='not in allowed sovereign roots'):
            client._validate_path(str(Path.cwd() / 'unauthorized_dir' / 'file.txt'))

    @pytest.mark.asyncio
    async def test_path_validation_forbidden_patterns(self) -> Any:
        """Test path validation blocks forbidden patterns."""
        client: Any = get_filesystem_client()
        with pytest.raises(PermissionError, match='forbidden pattern'):
            client._validate_path(str(Path.cwd() / 'agentic_core' / '../etc/passwd'))
        with pytest.raises(PermissionError, match='forbidden pattern'):
            client._validate_path(str(Path.cwd() / 'agentic_core' / '.env'))

    @pytest.mark.asyncio
    async def test_read_text_validation(self) -> Any:
        """Test read_text validates paths before MCP call."""
        client: Any = get_filesystem_client()
        with pytest.raises(PermissionError):
            await client.read_text('/etc/passwd')

    @pytest.mark.asyncio
    async def test_write_text_validation(self) -> Any:
        """Test write_text validates paths before MCP call."""
        client: Any = get_filesystem_client()
        with pytest.raises(PermissionError):
            await client.write_text('/tmp/test.txt', 'content')

    @pytest.mark.asyncio
    async def test_filesystem_mcp_routing(self) -> Any:
        """Verify operations route through L3 MCP router."""
        client: Any = get_filesystem_client()
        assert hasattr(client, 'router'), 'Client should have router'
        assert client.router is not None, 'Router should be initialized'
        assert client.router.role == 'maintenance_files', 'Router role should be maintenance_files'

    @pytest.mark.asyncio
    async def test_max_read_size_enforcement(self) -> Any:
        """Test max read size is enforced."""
        client: Any = get_filesystem_client()
        large_content: Any = 'x' * (config.FILESYSTEM_MAX_READ_SIZE + 1)

class test_guardian_enforcement:
    """Test guardian enforcement of Filesystem MCP usage."""

    def test_guardian_blocks_open(self) -> Any:
        """Verify guardian blocks direct open() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("with open('file.txt', 'r') as f:\n")
            f.write('    content = f.read()\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block direct open() call'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_path_read_text(self) -> Any:
        """Verify guardian blocks direct Path.read_text() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from pathlib import Path\n')
            f.write("content = Path('file.txt').read_text()\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block Path.read_text()'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_os_remove(self) -> Any:
        """Verify guardian blocks direct os.remove() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import os\n')
            f.write("os.remove('file.txt')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block os.remove()'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_shutil_rmtree(self) -> Any:
        """Verify guardian blocks direct shutil.rmtree() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import shutil\n')
            f.write("shutil.rmtree('directory')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block shutil.rmtree()'
        finally:
            temp_path.unlink()

    def test_guardian_allows_filesystem_mcp(self) -> Any:
        """Verify guardian allows Filesystem MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client import get_filesystem_client\n')
            f.write('client = get_filesystem_client()\n')
            f.write("content = await client.read_text('file.txt')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is True, 'Guardian should allow Filesystem MCP import'
        finally:
            temp_path.unlink()

class test_security_validation:
    """Test security validation in Filesystem MCP client."""

    @pytest.mark.asyncio
    async def test_path_traversal_blocked(self) -> Any:
        """Test path traversal attacks are blocked."""
        client: Any = get_filesystem_client()
        traversal_attempts: Any = ['../../../etc/passwd', 'agentic_core/../../etc/passwd', 'agentic_core/../unauthorized/file.txt']
        for attempt in traversal_attempts:
            with pytest.raises(PermissionError):
                client._validate_path(str(Path.cwd() / attempt))

    @pytest.mark.asyncio
    async def test_sensitive_file_access_blocked(self) -> Any:
        """Test access to sensitive files is blocked."""
        client: Any = get_filesystem_client()
        sensitive_files: Any = ['.env', 'config/.env', 'agentic_core/.env.local']
        for sensitive in sensitive_files:
            with pytest.raises(PermissionError, match='forbidden pattern'):
                client._validate_path(str(Path.cwd() / sensitive))

    @pytest.mark.asyncio
    async def test_system_directory_access_blocked(self) -> Any:
        """Test access to system directories is blocked."""
from typing import Any
        client: Any = get_filesystem_client()
        system_dirs: Any = ['/etc/', '/proc/', '/sys/']
        for sys_dir in system_dirs:
            with pytest.raises(PermissionError):
                client._validate_path(sys_dir + 'file.txt')

def run_tests() -> Any:
    """Run all Filesystem MCP integration tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
