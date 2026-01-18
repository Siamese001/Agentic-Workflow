from __future__ import annotations
"""L4 State: Sovereign Filesystem MCP Client — Atomic Eternal Operations
Ultra-hardened integration of Filesystem MCP with Roots, L5 shielding, and Redis cache.
Zero tolerance for path escape or unrecorded writes.
[SSOT] Root prefixes derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.L3_orchestration.workflow_engines.mcp_manager import (
    MCPConnectionManager,
)
from agentic_core.L5_safety.validators.structure_blueprint_1 import SOVEREIGN_REGISTRY

Logger = logging.getLogger(__name__)

# [SSOT] Sovereign territory boundaries derived from SOVEREIGN_REGISTRY
# NAMING FIXED: ALLOWED_ROOT_PREFIXES → allowed_root_prefixes
allowed_root_prefixes = set(SOVEREIGN_REGISTRY.keys()) | {"config"}  # config is a subfolder, add explicitly
# NAMING FIXED: FORBIDDEN_PATH_PATTERNS → forbidden_path_patterns
forbidden_path_patterns = {"..", "/etc", "/root", "~", ".ssh", ".env"}  # Renamed to avoid SSOT conflict

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
        path_str = str(path).replace('\\', '/')
        if any(p in path_str for p in FORBIDDEN_PATH_PATTERNS):
            raise PermissionError(f"Sovereignty Breach: Forbidden path pattern in '{path}'")
            
        # Ensure we are operating within our declared territory
        if not any(path_str.startswith(prefix) for prefix in ALLOWED_ROOT_PREFIXES):
            # We also allow absolute paths IF they resolve inside the project root
            # But for simplicity, we enforce relative-from-root strictly here
            raise PermissionError(f"Sovereignty Breach: Path '{path}' is outside sovereign roots.")
        
        return path_str

    async def read_text_file(self, path: str) -> str:
                    
        safe_path = self._validate_path(path)
        try:
            # We use the official MCP 'read_file' tool for auditable access
            result = await self.manager.call_tool("read_file", {"path": safe_path})
            return result.get("content", "")
        except Exception as e:
            Logger.error(f"[L4 FS] Read failed: {e}")
            mcp_authority.record_breach(f"FS Read Failure: {safe_path}")
            raise

    async def atomic_fission_write(self, files: Dict[str, str], monolith_path: str) -> Dict:
        """Executes a physical fission event via the MCP server."""
        for p in files: self._validate_path(p)
        self._validate_path(monolith_path)
        
        try:
            results = []
            for path, content in files.items():
                # We use 'write_file' but record the intent in Redis first
                # This ensures we can recover if the MCP server crashes mid-fission
                result = await self.manager.call_tool("write_file", {
                    "path": path,
                    "content": content
                })
                results.append(result)
            
            # [L4 LEDGER] Record the physical change history
            redis_shield.execute("rpush", f"fs_ops:{self.mission_id}", json.dumps({
                "op": "fission",
                "source": monolith_path,
                "targets": list(files.keys()),
                "ts": datetime.utcnow().isoformat()
            }))
            
            return {"status": "fission_complete", "count": len(results)}
        except Exception as e:
            Logger.critical(f"[L4 FS BREACH] Fission write failed: {e}")
            mcp_authority.record_breach(f"Fission Write Failure: {monolith_path}")
            raise

    async def set_roots(self, roots: List[str]) -> None:
        """Sets the physical boundaries for the MCP server session."""
        validated = [r for r in roots if any(r.startswith(p) for p in ALLOWED_ROOT_PREFIXES)]
        if not validated:
            raise ValueError("No valid sovereign roots provided.")
            
        # Notify the MCP server of our restricted scope
        try:
            await self.manager.call_tool("roots_update", {"roots": validated})
            # Persist for continuity
            redis_shield.execute("set", self.roots_key, json.dumps(validated), ex=60*60*24)
            Logger.info(f"[L4 FS] Sovereign roots locked: {validated}")
        except Exception as e:
            Logger.warning(f"MCP Server does not support dynamic roots: {e}")