from __future__ import annotations
from typing import Dict, Any, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeouts
#!/usr/bin/env python3
"""
Unused Cleanup Agent
Atomic agent: Removes unused imports and variables using autoflake.
"""
import subprocess
from pathlib import Path
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin


class UnusedCleanupAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Atomic agent: Removes unused imports and variables using autoflake.
    """

    def __init__(self, project_root, ctx) -> None:
        self.project_root = Path(project_root)
        self.ctx = ctx

    async def execute(self, file_path: str):
        """Remove unused imports and variables from a single file."""
        file = Path(file_path)
        if not file.exists():
            return {"healed": False}

        try:
            # Autoflake removes unused imports/variables in place
            result = subprocess.run(
                [
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(file),
                ],
                capture_output=True,
                text=True,
            )

            # Check if file changed (autoflake returns 0 on success)
            if result.returncode == 0:
                # Assume success if return code is 0
                # To confirm 'healed', we rely on git diff or hash check in main loop
                return {"healed": True, "action": "unused_removed"}

        except FileNotFoundError:
            return {"healed": False, "error": "autoflake not installed"}

        return {"healed": False}

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()
        
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
