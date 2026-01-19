"""Dependency Pruning Agent - Detects and removes unused Python dependencies.

This module provides a batch agent that detects and removes unused Python
dependencies from requirements.txt using 'deptry' for accurate AST-based
unused detection.

Typical usage:
    agent = DependencyPruningAgent(project_root=Path("/path/to/project"), ctx=context)
    result = await agent.execute()
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.decorators import standard_heal


@dataclass
class DependencyPruningAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """L5 Safety agent that detects and removes unused Python dependencies.
    
    This batch agent uses 'deptry' for accurate AST-based detection of unused
    dependencies and can remove them from requirements.txt.
    
    Attributes:
        project_root: Root directory of the project.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be removed (default: True).
        requirements_path: Path to requirements.txt file.
        
    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, project_root: Path, ctx: Any) -> None:
        """Initialize the dependency pruning agent.
        
        Args:
            project_root: Root directory of the project.
            ctx: Execution context with optional report() method.
        """
        self.project_root: Path = Path(project_root)
        self.ctx: Any = ctx
        self.dry_run: bool = True  # Safety: Default to non-destructive
        self.requirements_path: Path = self.project_root / "requirements.txt"

    def _find_unused_deptry(self) -> List[str]:
        """Use deptry to find unused dependencies via AST analysis.
        
        Returns:
            List of unused package names, empty if deptry fails or not installed.
        """
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                ["deptry", ".", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                data: Dict[str, Any] = json.loads(result.stdout)
                return data.get("unused", [])
        except FileNotFoundError:
            pass  # deptry not installed
        except (json.JSONDecodeError, Exception):
            pass  # JSON parsing or other error
        return []

    def _remove_from_requirements_txt(self, unused: List[str]) -> Dict[str, Any]:
        """Remove unused packages from requirements.txt.
        
        Args:
            unused: List of package names to remove.
            
        Returns:
            Dictionary with removal results:
                - removed: Count of packages removed
                - file: Name of the modified file
        """
        if not self.requirements_path.exists():
            return {"removed": 0}

        content: str = self.requirements_path.read_text(encoding="utf-8")
        lines: List[str] = content.splitlines()
        new_lines: List[str] = []
        removed: int = 0

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#"):
                new_lines.append(line)
                continue

            match = re.match(r"^([a-zA-Z0-9_-]+)", line_stripped)
            if match and match.group(1).lower() in [u.lower() for u in unused]:
                removed += 1
                if self.dry_run:
                    new_lines.append(f"# [PRUNED UNUSED] {line}")
                else:
                    continue  # Skip writing this line
            else:
                new_lines.append(line)

        if removed > 0 and not self.dry_run:
            self.requirements_path.write_text(
                "\n".join(new_lines) + "\n", encoding="utf-8"
            )

        return {"removed": removed, "file": "requirements.txt"}

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """Execute L5 safety healing operations.
        
        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.
        
        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.
            
        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
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

    async def execute(self) -> Dict[str, Any]:
        """Scan for and optionally remove unused dependencies.
        
        Returns:
            Dictionary with scan results:
                - unused_found: Count of unused dependencies found
                - removed: Count of dependencies removed
                - dry_run: Whether this was a dry run
        """
        print("   [PRUNE] Scanning for unused dependencies...")
        unused: List[str] = self._find_unused_deptry()

        if not unused:
            print("   [✓] No unused dependencies detected")
            return {"unused_found": 0, "removed": 0}

        print(
            f"   [!] Found {len(unused)} potentially unused packages: {', '.join(unused[:5])}"
        )
        if len(unused) > 5:
            print(f"       ... and {len(unused) - 5} more")

        result: Dict[str, Any] = self._remove_from_requirements_txt(unused)

        return {
            "unused_found": len(unused),
            "removed": result["removed"],
            "dry_run": self.dry_run,
        }
