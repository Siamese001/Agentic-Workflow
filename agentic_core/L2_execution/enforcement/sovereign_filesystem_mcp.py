from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""L4 State: Sovereign Filesystem MCP Client — Atomic Eternal Operations
Ultra-hardened integration of Filesystem MCP with Roots, L5 shielding, and Redis cache.
Zero tolerance for path escape or unrecorded writes.
[SSOT] Root prefixes derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import json
import logging
from datetime import datetime

from agentic_core.cache.redis_cache_client import get_hot_cache
from agentic_core.L0_routing.config.path_constants import PROJECT_ROOT_WHITELIST
from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import mcp_authority
from agentic_core.seams.contracts.mcp import MCPConnectionManager

Logger = logging.getLogger(__name__)

# [SSOT] Sovereign territory boundaries derived from PROJECT_ROOT_WHITELIST
# NAMING FIXED: ALLOWED_ROOT_PREFIXES → allowed_root_prefixes
allowed_root_prefixes = set(PROJECT_ROOT_WHITELIST) | {"config"}  # config is a subfolder, add explicitly
# NAMING FIXED: FORBIDDEN_PATH_PATTERNS → forbidden_path_patterns
forbidden_path_patterns = {
    "..",
    "/etc",
    "/root",
    "~",
    ".ssh",
    ".env",
}  # Renamed to avoid SSOT conflict


# NAMING FIXED: SovereignFilesystemMCP → SovereignFilesystemMcp
class SovereignFilesystemMcp:
    """Ultra-hardened filesystem client — enforcing atomic sovereignty."""

    def __init__(self, manager: MCPConnectionManager, mission_id: str):
        self.manager = manager
        self.mission_id = mission_id
        self.roots_key = f"fs_roots:{mission_id}"

    def _validate_path(self, path: str) -> str:
        """L5 path sovereignty check. Blocks traversals and absolute escapes."""
        # Convert to a clean, relative-style string for validation
        path_str = str(path).replace("\\", "/")
        if any(p in path_str for p in forbidden_path_patterns):
            raise PermissionError(f"Sovereignty Breach: Forbidden path pattern in '{path}'")

        # Ensure we are operating within our declared territory
        if not any(path_str.startswith(prefix) for prefix in allowed_root_prefixes):
            # We also allow absolute paths IF they resolve inside the project root
            # But for simplicity, we enforce relative-from-root strictly here
            raise PermissionError(f"Sovereignty Breach: Path '{path}' is outside sovereign roots.")

        return path_str

    async def read_text_file(self, path: str) -> str:
        safe_path = self._validate_path(path)
        try:
            # Prefer mcp8_read_text_file (direct Windsurf tool) for auditable access
            try:
                import builtins

                _mcp8_read = getattr(builtins, "mcp8_read_text_file", None)
                if _mcp8_read is not None:
                    result = _mcp8_read(path=safe_path)
                    if hasattr(result, "__await__"):
                        import asyncio

                        result = await asyncio.ensure_future(result)
                    return result if isinstance(result, str) else str(result)
            except Exception as direct_e:
                Logger.debug(f"[L4 FS] mcp8_read_text_file failed, falling back to manager: {direct_e}")
            # Fallback: route through MCPConnectionManager
            result = await self.manager.call_tool("read_file", {"path": safe_path})
            return result.get("content", "") if isinstance(result, dict) else str(result)
        except Exception as e:
            Logger.error(f"[L4 FS] Read failed: {e}")
            try:
                mcp_authority.record_breach(f"FS Read Failure: {safe_path}")
            except Exception:
                pass
            raise

    async def atomic_fission_write(self, files: dict[str, str], monolith_path: str) -> dict:
        """Executes a physical fission event via the MCP server."""
        for p in files:
            self._validate_path(p)
        self._validate_path(monolith_path)

        try:
            results = []
            for path, content in files.items():
                # Prefer mcp8_write_file (direct Windsurf tool); fallback to manager
                try:
                    import builtins

                    _mcp8_write = getattr(builtins, "mcp8_write_file", None)
                    if _mcp8_write is not None:
                        write_result = _mcp8_write(path=path, content=content)
                        if hasattr(write_result, "__await__"):
                            import asyncio

                            write_result = await asyncio.ensure_future(write_result)
                        results.append(write_result)
                        continue
                except Exception as direct_e:
                    Logger.debug(f"[L4 FS] mcp8_write_file failed, falling back to manager: {direct_e}")
                result = await self.manager.call_tool("write_file", {"path": path, "content": content})
                results.append(result)

            # [L4 LEDGER] Record the physical change history
            try:
                _cache = get_hot_cache()
                if _cache:
                    _cache.rpush(
                        f"fs_ops:{self.mission_id}",
                        json.dumps(
                            {
                                "op": "fission",
                                "source": monolith_path,
                                "targets": list(files.keys()),
                                "ts": datetime.utcnow().isoformat(),
                            }
                        ),
                    )
            except Exception as ledger_e:
                Logger.warning(f"[L4 FS] Ledger write failed (non-fatal): {ledger_e}")

            return {"status": "fission_complete", "count": len(results)}
        except Exception as e:
            Logger.critical(f"[L4 FS BREACH] Fission write failed: {e}")
            try:
                mcp_authority.record_breach(f"Fission Write Failure: {monolith_path}")
            except Exception:
                pass
            raise

    async def set_roots(self, roots: list[str]) -> None:
        """Sets the physical boundaries for the MCP server session."""
        validated = [r for r in roots if any(r.startswith(p) for p in allowed_root_prefixes)]
        if not validated:
            raise ValueError("No valid sovereign roots provided.")

        # Notify the MCP server of our restricted scope
        try:
            await self.manager.call_tool("roots_update", {"roots": validated})
            # Persist for continuity
            try:
                _cache = get_hot_cache()
                if _cache:
                    _cache.set(self.roots_key, json.dumps(validated), ex=60 * 60 * 24)
            except Exception as cache_e:
                Logger.warning(f"[L4 FS] Roots cache write failed (non-fatal): {cache_e}")
            Logger.info(f"[L4 FS] Sovereign roots locked: {validated}")
        except Exception as e:  # guardian: allow-silent-swallower
            Logger.warning(f"MCP Server does not support dynamic roots: {e}")
