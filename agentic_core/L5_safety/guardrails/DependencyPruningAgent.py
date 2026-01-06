from __future__ import annotations
#!/usr/bin/env python3
"""
Dependency Pruning Agent
Batch agent: Detects and removes unused Python dependencies from requirements.txt.
Uses 'deptry' for accurate unused detection via AST analysis.
"""
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class DependencyPruningAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Batch agent: Detects and removes unused Python dependencies from requirements.txt.
    Uses 'deptry' for accurate unused detection.
    """

    def __init__(self, project_root: Path, ctx) -> None:
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.dry_run = True  # Safety: Default to non-destructive
        self.requirements_path = self.project_root / "requirements.txt"

    def _find_unused_deptry(self) -> List[str]:
        """Use deptry to find unused dependencies via AST analysis."""
        try:
            # Run deptry in JSON mode for reliable parsing
            result = subprocess.run(
                ["deptry", ".", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("unused", [])
        except FileNotFoundError:
            # deptry not installed
            pass
        except Exception:
            # JSON parsing or other error
            pass
        return []

    def _remove_from_requirements_txt(self, unused: List[str]) -> Dict:
        """Remove unused packages from requirements.txt."""
        if not self.requirements_path.exists():
            return {"removed": 0}

        content = self.requirements_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        new_lines = []
        removed = 0

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#"):
                new_lines.append(line)
                continue

            # Regex to capture package name before any version specifiers
            match = re.match(r"^([a-zA-Z0-9_-]+)", line_stripped)
            if match and match.group(1).lower() in [u.lower() for u in unused]:
                removed += 1
                if self.dry_run:
                    # Comment out instead of removing (dry run)
                    new_lines.append(f"# [PRUNED UNUSED] {line}")
                else:
                    # Skip writing this line (actually remove)
                    continue
            else:
                new_lines.append(line)

        if removed > 0 and not self.dry_run:
            self.requirements_path.write_text(
                "\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n".join(new_lines) + "\n", encoding="utf-8"
            )

        return {"removed": removed, "file": "requirements.txt"}

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
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

    async def execute(self) -> Dict:
        """Scan for and optionally remove unused dependencies."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        print("   [PRUNE] Scanning for unused dependencies...")
        unused = self._find_unused_deptry()

        if not unused:
            print("   [✓] No unused dependencies detected")
            return {"unused_found": 0, "removed": 0}

        print(
            f"   [!] Found {len(unused)} potentially unused packages: {', '.join(unused[:5])}"
        )
        if len(unused) > 5:
            print(f"       ... and {len(unused) - 5} more")

        result = self._remove_from_requirements_txt(unused)

        return {
            "unused_found": len(unused),
            "removed": result["removed"],
            "dry_run": self.dry_run,
        }
