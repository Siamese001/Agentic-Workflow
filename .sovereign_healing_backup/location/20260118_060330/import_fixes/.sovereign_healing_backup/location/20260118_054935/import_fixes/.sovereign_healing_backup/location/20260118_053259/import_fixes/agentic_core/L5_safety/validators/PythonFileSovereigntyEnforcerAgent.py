# File: agentic_core/L5_safety/validators/PythonFileSovereigntyEnforcerAgent.py
# CANONICAL: True - Enforces dedicated ClassNameAgent.py file naming (2026-01-06)

from __future__ import annotations
from dataclasses import dataclass

import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Set

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


@dataclass
class PythonFileSovereigntyEnforcerAgent(SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """
    L5 Safety agent - enforces dedicated ClassNameAgent.py file naming standard.
    
    Technical rationale:
    - Uses AST to reliably extract primary agent class (first ClassDef ending in "Agent")
    - git mv preserves history and updates imports automatically in most cases
    - Dry-run mode for safe preview
    - Healer chain + timeout compatible
    """

    def __init__(self, project_root: Path, dry_run: bool = True) -> None:
        """Initialize the instance."""
        self.project_root = project_root.resolve()
        self.dry_run = dry_run
        self.target_prefixes = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
        self.renames_applied = 0

    def run(self) -> List[Dict[str, str]]:
        """Scan and perform/return proposed file renames."""
        actions: List[Dict[str, str]] = []

        for py_file in self.project_root.rglob("*.py"):
            rel_path = py_file.relative_to(self.project_root)
            if not any(rel_path.parts[0].startswith(prefix) for prefix in self.target_prefixes):
                continue

            primary_agent = self._extract_primary_agent_class(py_file)
            if not primary_agent:
                continue

            expected_name = f"{primary_agent}.py"
            if py_file.name != expected_name:
                old_path = str(py_file)
                new_path = str(py_file.parent / expected_name)
                action = {
                    "current_path": old_path,
                    "expected_path": new_path,
                    "class_name": primary_agent,
                    "status": "PROPOSED"
                }

                if not self.dry_run:
                    success = self._safe_git_mv(py_file, py_file.parent / expected_name)
                    action["status"] = "APPLIED" if success else "FAILED"
                    if success:
                        self.renames_applied += 1

                actions.append(action)
                print(f"[{'DRY-RUN' if self.dry_run else 'APPLIED'}] {py_file.name} → {expected_name}")

        return actions

    def _extract_primary_agent_class(self, file_path: Path) -> Optional[str]:
        """Extract first class name ending in 'Agent' (heuristic: first match)."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    return node.name
        except Exception as e:
            print(f"[ERROR] AST parse failed for {file_path}: {e}")
        return None

    def _safe_git_mv(self, old_path: Path, new_path: Path) -> bool:
        """Execute git mv with error handling."""
        try:
            subprocess.run(["git", "mv", str(old_path), str(new_path)], check=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] git mv failed {old_path} → {new_path}: {e}")
            return False

    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[Set[str]] = None) -> Dict[str, int]:
        """Healer chain entrypoint."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            super().heal_repository(dry_run=dry_run, execute=execute)
            self.dry_run = not execute
            results = self.run()
            return {
                "renames_proposed": len(results),
                "renames_applied": self.renames_applied,
                "errors": len(results) - self.renames_applied
            }
        finally:
            _call_path.discard(agent_name)
