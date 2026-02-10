#!/usr/bin/env python3
from __future__ import annotations

"""
GravityLeakDetector: Cross-boundary dependency detection agent

Responsibility: Detect and mark gravity leaks (core → apps dependencies)
- AST-based dependency extraction
- Downstream root detection
- TODO marker insertion for manual review
- Deep import validation

Migrated from LocationAgent.py during Phase 4 of the fission process.
"""


import ast
import logging
import re
import shutil
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)
# Gravity-specific constants - define locally if not in location_constants
CORE_TERRITORY_KEYWORDS = {"core", "sovereign", "canon", "base", "mixin", "agent"}
APP_RG_AST_TERMS = {"rg", "regulatory", "compliance"}
APP_LIC_AST_TERMS = {"lic", "linkedin", "canonical"}
APP_RG_VARIABLE_TERMS = {"rg_", "regulatory_"}
APP_LIC_VARIABLE_TERMS = {"lic_", "linkedin_"}
APP_RG_STRING_TERMS = {"RG", "Regulatory"}
APP_LIC_STRING_TERMS = {"LIC", "LinkedIn Canonical"}
VARIABLE_HIT_WEIGHT = 1.0
STRING_HIT_WEIGHT = 0.5


class GravityLeakDetector:
    """
    Cross-boundary dependency detection agent.

    Detects:
    - Gravity leaks (agentic_core importing from apps_*)
    - Downstream dependency chains
    - Semantic alignment violations
    - AST-based semantic scoring

    Performs:
    - TODO marker insertion for manual review
    - Gravity violation healing (import removal)
    - Deep import validation

    Does NOT perform:
    - Validation (use LocationValidatorAgent)
    - File operations (delegates to LocationHealerAgent)

    Gravity leaks require manual review and architectural decisions.
    """

    def __init__(self, project_root: Path):
        """Initialize gravity detector."""
        self.project_root = Path(project_root).resolve()

    # ========================================================================
    # AST SCORE COMPUTATION (Phase 4)
    # ========================================================================

    def _recompute_ast_scores(self, tree: ast.AST) -> tuple[float, float, dict[str, float]]:
        """AST score recomputation orchestrator — linear walk + aggregation."""
        initial_scores = {
            "app_rg": 0.0,
            "app_lic": 0.0,
            "territories": dict.fromkeys(CORE_TERRITORY_KEYWORDS, 0.0),
        }

        # Phase 1: Walk and collect raw increments
        raw_increments = self._collect_ast_increments(tree)

        # Phase 2: Aggregate and apply
        final_scores = self._aggregate_ast_increments(initial_scores, raw_increments)

        return final_scores["app_rg"], final_scores["app_lic"], final_scores["territories"]

    def _collect_ast_increments(self, tree: ast.AST) -> dict:
        """Phase 1: Pure AST walk — collect raw risk increments."""
        increments = {
            "app_rg": 0.0,
            "app_lic": 0.0,
            "territories": dict.fromkeys(CORE_TERRITORY_KEYWORDS, 0.0),
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                self._score_identifier(node.name.lower(), 1.0, increments)
            elif isinstance(node, ast.arguments):
                self._score_arguments(node, increments)
            elif isinstance(node, ast.Assign):
                self._score_assignments(node, increments)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 8:
                self._score_string(node.value.lower(), increments)
        return increments

    def _score_identifier(self, name: str, weight: float, increments: dict) -> None:
        """Score an identifier against app/territory terms."""
        if any(t in name for t in APP_RG_AST_TERMS):
            increments["app_rg"] += weight
        if any(t in name for t in APP_LIC_AST_TERMS):
            increments["app_lic"] += weight
        for terr, cats in CORE_TERRITORY_KEYWORDS.items():
            if any(t in name for terms in cats.values() for t in terms):
                increments["territories"][terr] += weight

    def _score_arguments(self, node: ast.arguments, increments: dict) -> None:
        """Score function arguments."""
        all_args = node.args + getattr(node, "kwonlyargs", []) + getattr(node, "posonlyargs", [])
        for arg in all_args:
            if arg.arg and arg.arg not in {"self", "cls"}:
                self._score_variable(arg.arg.lower(), increments)

    def _score_assignments(self, node: ast.Assign, increments: dict) -> None:
        """Score assignment targets."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._score_variable(target.id.lower(), increments)

    def _score_variable(self, name: str, increments: dict) -> None:
        """Score a variable name."""
        if any(t in name for t in APP_RG_VARIABLE_TERMS):
            increments["app_rg"] += VARIABLE_HIT_WEIGHT
        if any(t in name for t in APP_LIC_VARIABLE_TERMS):
            increments["app_lic"] += VARIABLE_HIT_WEIGHT
        for terr, cats in CORE_TERRITORY_KEYWORDS.items():
            if any(t in name for terms in cats.values() for t in terms):
                increments["territories"][terr] += VARIABLE_HIT_WEIGHT

    def _score_string(self, text: str, increments: dict) -> None:
        """Score a string literal."""
        increments["app_rg"] += sum(1 for t in APP_RG_STRING_TERMS if t in text) * STRING_HIT_WEIGHT
        increments["app_lic"] += sum(1 for t in APP_LIC_STRING_TERMS if t in text) * STRING_HIT_WEIGHT
        for terr, cats in CORE_TERRITORY_KEYWORDS.items():
            increments["territories"][terr] += (
                sum(1 for terms in cats.values() for t in terms if t in text) * STRING_HIT_WEIGHT
            )

    def _aggregate_ast_increments(self, initial_scores: dict, increments: dict) -> dict:
        """Phase 2: Simple aggregation."""
        final_scores = initial_scores.copy()
        final_scores["app_rg"] += increments["app_rg"]
        final_scores["app_lic"] += increments["app_lic"]
        for terr in final_scores["territories"]:
            final_scores["territories"][terr] += increments["territories"].get(terr, 0.0)
        return final_scores

    # ========================================================================
    # GRAVITY VIOLATION HEALING (Phase 4)
    # ========================================================================

    def _heal_gravity_violations(self, gravity_issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Helper method to heal gravity violations by removing offending imports."""
        gravity_heal_actions = []
        for grav in gravity_issues:
            path = Path(grav["path"]) if isinstance(grav["path"], str) else grav["path"]
            msg = grav["issue"]

            try:
                downstream_roots = self._extract_downstream_roots(msg)
                if not downstream_roots:
                    continue

                content = path.read_text(encoding="utf-8")
                lines = content.splitlines()

                # Import from LocationHealerAgent
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
                    LocationHealerAgent,
                )

                healer = LocationHealerAgent(project_root=self.project_root)
                new_lines, removed_modules = healer._remove_offending_imports(lines, downstream_roots)

                if removed_modules:
                    new_content = self._insert_gravity_heal_todo(new_lines, msg, removed_modules)
                    self._backup_and_write_file(path, new_content)

                    gravity_heal_actions.append(
                        {
                            "type": "GRAVITY_AUTO_HEAL",
                            "file": grav["file"],
                            "removed_imports": removed_modules,
                        },
                    )

            # guardian: allow-silent-swallow
            except Exception as e:
                gravity_heal_actions.append(
                    {
                        "type": "GRAVITY_HEAL_ERROR",
                        "file": grav["file"],
                        "error": str(e),
                    },
                )

        return gravity_heal_actions

    def _extract_downstream_roots(self, msg: str) -> list[str]:
        """Extract downstream roots from gravity violation message."""
        downstream_match = re.search(r"downstream roots: \[(.*?)\]", msg)
        if downstream_match:
            return [r.strip().strip("'\"") for r in downstream_match.group(1).split(",")]

        downstream_match = re.search(r"apps_[a-z_]+", msg)
        if downstream_match:
            return [downstream_match.group(0)]

        return []

    def _insert_gravity_heal_todo(self, lines: list[str], msg: str, removed_modules: list[str]) -> str:
        """Insert TODO block after shebang/docstring."""
        todo_block = [
            "",
            "# TODO: GRAVITY VIOLATION AUTO-HEALED",
            "# Downstream imports removed — move shared logic to apps_shared or sovereign utils",
            "# Original violation: " + msg[:200],
            "# Removed: " + ", ".join(removed_modules),
            "",
        ]

        insert_idx = self._find_todo_insert_position(lines)
        new_lines = lines[:insert_idx] + todo_block + lines[insert_idx:]
        return "\n".join(new_lines)

    def _find_todo_insert_position(self, lines: list[str]) -> int:
        """Find position to insert TODO block after shebang/docstring."""
        insert_idx = 0

        if lines and lines[0].startswith("#!"):
            insert_idx = 1

        if len(lines) > insert_idx and lines[insert_idx].strip().startswith('"""'):
            for i, l in enumerate(lines[insert_idx:], insert_idx):
                if i > insert_idx and '"""' in l:
                    insert_idx = i + 1
                    break

        return insert_idx

    def _backup_and_write_file(self, path: Path, content: str) -> None:
        """Backup file and write new content."""
        # Import from LocationHealerAgent for backup directory initialization
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        healer = LocationHealerAgent(project_root=self.project_root)
        backup_dir = healer._init_backup_dir() / "gravity_auto_heal"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / path.relative_to(self.project_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        path.write_text(content, encoding="utf-8")
