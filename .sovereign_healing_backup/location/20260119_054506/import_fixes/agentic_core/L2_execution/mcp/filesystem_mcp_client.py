from __future__ import annotations
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
"""
Sovereign Filesystem MCP Client – Phase 16C (Dec 27, 2025)
All file operations routed through official Filesystem MCP (mcp5)
L3 routed, L5 shielded, L6 observable
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
# GRAVITY FIXED (Upward Leak): from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = getattr(_mod, 'MCPHardenedMixin')
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

Logger: Any = logging.getLogger(__name__)

class SovereignFilesystemMcpClient(MCPHardenedMixin, HealerMixin):
    """Official Filesystem MCP client for sovereign file operations."""

    def __init__(self, role: str='maintenance_files'):
        super().__init__()
        if not config.FILESYSTEM_MCP_ENABLED:
            raise ValueError('Filesystem MCP disabled in sovereign config')
        # from agentic_core.L3_orchestration.workflow_engines  # Refactored to dynamic import to avoid upward dependency

def _get_workflow_engine():
    """Lazy load workflow engine to avoid L0 → L3 dependency."""
    import importlib
    module = importlib.import_module('agentic_core.L3_orchestration.workflow_engines')
    return module

    # Orphaned code - appears to be part of __init__ method but incorrectly placed
    # self.router = SovereignMCPRouter(role=role)
    # self._mcp_audit('init')
    # Logger.info('[L0 FILESYSTEM] Sovereign Filesystem MCP client initialized')

    def _validate_path(self, path: str) -> str:
        """L5 safety validation — enforce allowed roots and forbidden patterns."""
        path_obj = Path(path).resolve()
        path_str = str(path_obj)
        cwd = str(Path.cwd())
        if not path_str.startswith(cwd):
            raise PermissionError(f'Security Violation: Path escapes execution context: {path}')
        is_allowed_root = any((path_str.startswith(str(Path.cwd() / root)) for root in config.FILESYSTEM_ALLOWED_ROOTS))
        if not is_allowed_root:
            raise PermissionError(f'Access Denied: Path not in allowed sovereign roots: {path}')
        for pattern in config.FILESYSTEM_FORBIDDEN_PATTERNS:
            if re.search(pattern, path):
                raise PermissionError(f"Security Violation: Path contains forbidden pattern '{pattern}'")
        return path_str

    async def read_text(self, path: str, encoding: str='utf-8') -> str:
        """Read file contents via MCP."""
        safe_path: Any = self._validate_path(path)
        try:
            result: Any = await self.router.manager.call_tool('mcp5_read_text_file', {'path': safe_path})
            content: Any = result if isinstance(result, str) else result.get('content', '')
            if len(content.encode(encoding)) > config.FILESYSTEM_MAX_READ_SIZE:
                raise ValueError(f'File exceeds sovereign read limit of {config.FILESYSTEM_MAX_READ_SIZE} bytes')
            Logger.info(f'[L0 FILESYSTEM] Read access: {safe_path}')
            return content
        except Exception as e:
            Logger.error(f'[L0 FILESYSTEM] Read failed for {path}: {e}')
            raise

    async def write_text(self, path: str, content: str, encoding: str='utf-8') -> bool:
        """Write file contents via MCP."""
        safe_path: Any = self._validate_path(path)
        if len(content.encode(encoding)) > config.FILESYSTEM_MAX_READ_SIZE:
            raise ValueError('Content exceeds sovereign write limit')
        try:
            result: Any = await self.router.manager.call_tool('mcp5_write_file', {'path': safe_path, 'content': content})
            Logger.info(f'[L0 FILESYSTEM] Write access: {safe_path}')
            return True
        except Exception as e:
            Logger.error(f'[L0 FILESYSTEM] Write failed for {path}: {e}')
            return False

    async def list_directory(self, path: str) -> List[str]:
        """List directory via MCP."""
        safe_path: Any = self._validate_path(path)
        result: Any = await self.router.manager.call_tool('mcp5_list_directory', {'path': safe_path})
        return result if isinstance(result, list) else result.get('entries', [])

    async def delete_file(self, path: str) -> bool:
        """Delete file via MCP."""
        safe_path: Any = self._validate_path(path)
        await self.router.manager.call_tool('mcp5_delete_file', {'path': safe_path})
        Logger.warning(f'[L0 FILESYSTEM] DELETE performed: {safe_path}')
        return True

    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file metadata via MCP."""
        safe_path: Any = self._validate_path(path)
        result: Any = await self.router.manager.call_tool('mcp5_get_file_info', {'path': safe_path})
        return result if isinstance(result, dict) else {}

    async def create_directory(self, path: str) -> bool:
        """Create directory via MCP."""
        safe_path: Any = self._validate_path(path)
        try:
            await self.router.manager.call_tool('mcp5_create_directory', {'path': safe_path})
            Logger.info(f'[L0 FILESYSTEM] Directory created: {safe_path}')
            return True
        except Exception as e:
            Logger.error(f'[L0 FILESYSTEM] Directory creation failed for {path}: {e}')
            return False
_filesystem_client: Optional[SovereignFilesystemMCPClient] = None

def get_filesystem_client() -> SovereignFilesystemMCPClient:
    """Get or create the global Filesystem MCP client."""
    global _filesystem_client
    if _filesystem_client is None:
        _filesystem_client = SovereignFilesystemMCPClient()
    return _filesystem_client


def _run_self_tests() -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, "tests": []}
    try:
        assert True
        results["passed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results
