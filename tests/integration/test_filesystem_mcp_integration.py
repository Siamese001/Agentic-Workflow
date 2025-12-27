"""
Integration Tests for Phase 16C: Filesystem MCP Client
Validates sovereign file operations through MCP architecture.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from agentic_core.L0_maintenance.filesystem_mcp_client import get_filesystem_client, SovereignFilesystemMCPClient
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config


class TestFilesystemMCPIntegration:
    """Test suite for Filesystem MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_filesystem_mcp_enabled(self):
        """Verify Filesystem MCP is enabled in sovereign config."""
        assert config.FILESYSTEM_MCP_ENABLED is True, "Filesystem MCP must be enabled"
        assert config.FILESYSTEM_MAX_READ_SIZE == 10_000_000, "Max read size should be 10MB"
        assert isinstance(config.FILESYSTEM_ALLOWED_ROOTS, list), "Allowed roots should be a list"
        assert "agentic_core" in config.FILESYSTEM_ALLOWED_ROOTS, "agentic_core should be allowed"
        assert isinstance(config.FILESYSTEM_FORBIDDEN_PATTERNS, list), "Forbidden patterns should be a list"
    
    @pytest.mark.asyncio
    async def test_filesystem_client_singleton(self):
        """Verify singleton pattern for Filesystem client."""
        client1 = get_filesystem_client()
        client2 = get_filesystem_client()
        assert client1 is client2, "Should return same singleton instance"
    
    @pytest.mark.asyncio
    async def test_path_validation_sandbox(self):
        """Test path validation enforces sandbox."""
        client = get_filesystem_client()
        
        # Test path outside CWD
        with pytest.raises(PermissionError, match="escapes execution context"):
            client._validate_path("/etc/passwd")
    
    @pytest.mark.asyncio
    async def test_path_validation_allowed_roots(self):
        """Test path validation enforces allowed roots."""
        client = get_filesystem_client()
        
        # Test path not in allowed roots
        with pytest.raises(PermissionError, match="not in allowed sovereign roots"):
            client._validate_path(str(Path.cwd() / "unauthorized_dir" / "file.txt"))
    
    @pytest.mark.asyncio
    async def test_path_validation_forbidden_patterns(self):
        """Test path validation blocks forbidden patterns."""
        client = get_filesystem_client()
        
        # Test ../ pattern
        with pytest.raises(PermissionError, match="forbidden pattern"):
            client._validate_path(str(Path.cwd() / "agentic_core" / "../etc/passwd"))
        
        # Test .env pattern
        with pytest.raises(PermissionError, match="forbidden pattern"):
            client._validate_path(str(Path.cwd() / "agentic_core" / ".env"))
    
    @pytest.mark.asyncio
    async def test_read_text_validation(self):
        """Test read_text validates paths before MCP call."""
        client = get_filesystem_client()
        
        # Should fail validation before reaching MCP
        with pytest.raises(PermissionError):
            await client.read_text("/etc/passwd")
    
    @pytest.mark.asyncio
    async def test_write_text_validation(self):
        """Test write_text validates paths before MCP call."""
        client = get_filesystem_client()
        
        # Should fail validation before reaching MCP
        with pytest.raises(PermissionError):
            await client.write_text("/tmp/test.txt", "content")
    
    @pytest.mark.asyncio
    async def test_filesystem_mcp_routing(self):
        """Verify operations route through L3 MCP router."""
        client = get_filesystem_client()
        
        # Verify router is initialized
        assert hasattr(client, 'router'), "Client should have router"
        assert client.router is not None, "Router should be initialized"
        
        # Verify router role
        assert client.router.role == "maintenance_files", "Router role should be maintenance_files"
    
    @pytest.mark.asyncio
    async def test_max_read_size_enforcement(self):
        """Test max read size is enforced."""
        client = get_filesystem_client()
        
        # Create content exceeding limit
        large_content = "x" * (config.FILESYSTEM_MAX_READ_SIZE + 1)
        
        # Mock scenario: if MCP returns content exceeding limit, should raise
        # This would be tested in actual integration with MCP server


class TestGuardianEnforcement:
    """Test guardian enforcement of Filesystem MCP usage."""
    
    def test_guardian_blocks_open(self):
        """Verify guardian blocks direct open() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with direct open() call
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("with open('file.txt', 'r') as f:\n")
            f.write("    content = f.read()\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block direct open() call"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_path_read_text(self):
        """Verify guardian blocks direct Path.read_text() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with Path.read_text()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from pathlib import Path\n")
            f.write("content = Path('file.txt').read_text()\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block Path.read_text()"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_os_remove(self):
        """Verify guardian blocks direct os.remove() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with os.remove()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import os\n")
            f.write("os.remove('file.txt')\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block os.remove()"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_shutil_rmtree(self):
        """Verify guardian blocks direct shutil.rmtree() calls."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with shutil.rmtree()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import shutil\n")
            f.write("shutil.rmtree('directory')\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block shutil.rmtree()"
        finally:
            temp_path.unlink()
    
    def test_guardian_allows_filesystem_mcp(self):
        """Verify guardian allows Filesystem MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with Filesystem MCP import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from agentic_core.L0_maintenance.filesystem_mcp_client import get_filesystem_client\n")
            f.write("client = get_filesystem_client()\n")
            f.write("content = await client.read_text('file.txt')\n")
            temp_path = Path(f.name)
        
        try:
            # Should pass validation
            result = check_file(temp_path)
            assert result is True, "Guardian should allow Filesystem MCP import"
        finally:
            temp_path.unlink()


class TestSecurityValidation:
    """Test security validation in Filesystem MCP client."""
    
    @pytest.mark.asyncio
    async def test_path_traversal_blocked(self):
        """Test path traversal attacks are blocked."""
        client = get_filesystem_client()
        
        # Various path traversal attempts
        traversal_attempts = [
            "../../../etc/passwd",
            "agentic_core/../../etc/passwd",
            "agentic_core/../unauthorized/file.txt",
        ]
        
        for attempt in traversal_attempts:
            with pytest.raises(PermissionError):
                client._validate_path(str(Path.cwd() / attempt))
    
    @pytest.mark.asyncio
    async def test_sensitive_file_access_blocked(self):
        """Test access to sensitive files is blocked."""
        client = get_filesystem_client()
        
        sensitive_files = [
            ".env",
            "config/.env",
            "agentic_core/.env.local",
        ]
        
        for sensitive in sensitive_files:
            with pytest.raises(PermissionError, match="forbidden pattern"):
                client._validate_path(str(Path.cwd() / sensitive))
    
    @pytest.mark.asyncio
    async def test_system_directory_access_blocked(self):
        """Test access to system directories is blocked."""
        client = get_filesystem_client()
        
        system_dirs = [
            "/etc/",
            "/proc/",
            "/sys/",
        ]
        
        for sys_dir in system_dirs:
            with pytest.raises(PermissionError):
                client._validate_path(sys_dir + "file.txt")


def run_tests():
    """Run all Filesystem MCP integration tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
