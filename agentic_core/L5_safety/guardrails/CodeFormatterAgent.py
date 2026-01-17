from __future__ import annotations
from typing import Dict, Any, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from dataclasses import dataclass
#!/usr/bin/env python3
"""
Code Formatter Agent
Atomic agent: Enforces consistent formatting using Black + Ruff auto-fix.
"""
import subprocess
from pathlib import Path
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin


@dataclass
class CodeFormatterAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Atomic agent: Enforces consistent formatting using Black + Ruff auto-fix.
    """

    def __init__(self, project_root: str, ctx: Any) -> None:
        """
        Initialize the code formatter agent.
        
        Args:
            project_root: Root directory of the project
            ctx: Execution context
        """
        self.project_root: Path = Path(project_root)
        self.ctx = ctx

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """
        Format a single file using Black and Ruff.
        
        Args:
            file_path: Path to file to format
        
        Returns:
            Dict with healed status and action taken
        """
        file: Path = Path(file_path)
        if not file.exists():
            return {"healed": False}

        changed: bool = False
        try:
            # Black formatting
            black_result = subprocess.run(
                ["black", "--quiet", str(file)], capture_output=True, text=True
            )
            if black_result.returncode == 0 and "reformatted" in black_result.stderr:
                changed = True

            # Ruff lint auto-fix
            ruff_result = subprocess.run(
                ["ruff", "check", "--fix", "--quiet", str(file)], capture_output=True
            )
            if ruff_result.returncode == 0:
                # Ruff ran successfully, assume it enforced standards
                pass

            if changed:
                print(f"   [OK] Formatted: {file_path}")
                return {"healed": True, "action": "formatted"}

        except FileNotFoundError as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "CodeFormatterAgent", 0, False, f"Tool Missing: {e.filename}"
                )
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("CodeFormatterAgent", 0, False, f"Format error: {e}")

        return {"healed": changed}

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
