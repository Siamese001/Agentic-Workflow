#!/usr/bin/env python3
from __future__ import annotations

"""
CodeHealerAgent - Code Healing & Repair

Phase 4 Hard Migration: Consolidates:
- CanonHealerAgent (canon compliance healing)
- ImportHealerAgent (import fixing)
- StructuralHealerAgent (structural repair)

Features:
- Canon compliance auto-healing
- Broken import detection and fixing
- Unused import removal
- Structural code repair
- Safe file mutation with backup
"""


import ast
import logging
import os
import re
import shutil
import tempfile
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


from enum import Enum


class HealingType(Enum):
    """Types of code healing."""

    CANON = "CANON"
    IMPORT = "IMPORT"
    STRUCTURAL = "STRUCTURAL"


@dataclass
class HealingAction:
    """Represents a healing action taken."""

    healing_type: str
    file_path: Path
    line_number: int
    description: str
    old_code: str
    new_code: str
    applied: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HealerConfig:
    """configuration for code healing."""

    enable_canon: bool = True
    enable_import: bool = True
    enable_structural: bool = True
    dry_run: bool = True
    backup_before_heal: bool = True
    backup_dir: Path | None = None


class CodeHealerAgent(SovereignBaseAgent):
    """
    Unified code healer for canon, imports, and structure.

    Consolidates:
    - CanonHealerAgent
    - ImportHealerAgent
    - StructuralHealerAgent

    Usage:
        healer = CodeHealerAgent()

        # Heal imports in a file
        actions = healer.heal_imports(Path("my_agent.py"))

        # Heal all issues
        actions = healer.heal_all(Path("my_agent.py"))
    """

    # Standard library modules for import classification
    STDLIB_MODULES = {
        "os",
        "sys",
        "re",
        "json",
        "ast",
        "typing",
        "pathlib",
        "logging",
        "datetime",
        "collections",
        "functools",
        "itertools",
        "threading",
        "asyncio",
        "dataclasses",
        "enum",
        "abc",
        "contextlib",
        "copy",
        "hashlib",
        "secrets",
        "shutil",
        "tempfile",
        "unittest",
        "time",
    }

    def __init__(
        self,
        project_root: Path | None = None,
        agent_config: HealerConfig | None = None,
    ):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self._agent_config = agent_config or HealerConfig()
        self._lock = threading.RLock()
        self._actions: list[HealingAction] = []

        if self._agent_config.backup_dir is None:
            self._agent_config.backup_dir = (
                self.project_root / "archives" / "healing_backups" / "code"
            )

        Logger.info("CodeHealerAgent initialized")

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Wraps heal_all to provide the standard Sovereign interface.
        """
        # Update config based on args
        self._agent_config.dry_run = dry_run

        actions = []
        violations_found = 0
        violations_fixed = 0
        errors = 0

        # In a real repository context, we would iterate over all relevant files.
        # For the agent interface, we assume the caller might pass a specific file
        # or we scan the project root.
        target_file = kwargs.get("file_path")
        if target_file:
            actions = self.heal_all(Path(target_file))
            violations_found = len(actions)
            violations_fixed = len([a for a in actions if a.applied])

        return {
            "violations_found": violations_found,
            "violations_fixed": violations_fixed,
            "errors": errors,
            "skipped": violations_found - violations_fixed - errors,
        }

    def atomic_write(self, file_path: Path, new_content: str) -> bool:
        """
        [ATOMIC SAFETY] Writes file safely using temp-swap pattern.
        """
        try:
            # 1. Create Temp File
            temp_fd, temp_path = tempfile.mkstemp(dir=file_path.parent, text=True)
            with os.fdopen(temp_fd, "w", encoding="utf-8") as tf:
                tf.write(new_content)

            # 2. Create Backup
            self._backup_file(file_path)

            # 3. Atomic Swap
            os.replace(temp_path, file_path)
            return True
        except Exception as e:
            Logger.critical(f"Atomic write failed for {file_path}: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return False

    def heal_all(self, file_path: Path) -> list[HealingAction]:
        """Run all enabled healing on a file."""
        actions = []

        if not file_path.exists():
            return actions

        if self._agent_config.enable_import:
            actions.extend(self.heal_imports(file_path))

        if self._agent_config.enable_canon:
            actions.extend(self.heal_canon(file_path))

        if self._agent_config.enable_structural:
            actions.extend(self.heal_structural(file_path))

        return actions

    def heal_imports(self, file_path: Path) -> list[HealingAction]:
        """Fix broken and unused imports."""
        actions = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return actions

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            Logger.error(f"Syntax error in {file_path}: {e}")
            return actions

        # Collect imports and their usage
        imports: list[tuple[ast.AST, str, int]] = []
        used_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imports.append((node, name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports.append((node, name, node.lineno))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        # Find unused imports
        lines = content.split("\n")
        unused_imports = []

        for node, name, lineno in imports:
            if name not in used_names and name not in ("*", "__future__"):
                unused_imports.append((name, lineno))

                action = HealingAction(
                    healing_type="IMPORT",
                    file_path=file_path,
                    line_number=lineno,
                    description=f"Remove unused import: {name}",
                    old_code=lines[lineno - 1] if lineno <= len(lines) else "",
                    new_code="# REMOVED: " + (lines[lineno - 1] if lineno <= len(lines) else ""),
                )
                actions.append(action)

        # Apply fixes if not dry run
        if not self._agent_config.dry_run and unused_imports:
            # Remove unused import lines
            new_lines = []
            unused_line_numbers = {lineno for _, lineno in unused_imports}

            for i, line in enumerate(lines, 1):
                if i not in unused_line_numbers:
                    new_lines.append(line)

            # Use atomic write instead of direct write
            new_content = "\n".join(new_lines)
            if self.atomic_write(file_path, new_content):
                for action in actions:
                    action.applied = True
            else:
                Logger.error(f"Failed to apply atomic write to {file_path}")

        self._actions.extend(actions)
        return actions

    def heal_canon(self, file_path: Path) -> list[HealingAction]:
        """Fix canon compliance issues."""
        actions = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return actions

        lines = content.split("\n")
        new_lines = lines.copy()
        modified = False

        # Check for missing __future__ import
        has_future = any("from __future__" in line for line in lines[:10])
        if not has_future and file_path.suffix == ".py":
            action = HealingAction(
                healing_type="CANON",
                file_path=file_path,
                line_number=1,
                description="Add __future__ annotations import",
                old_code="",
                new_code="from __future__ import annotations",
            )
            actions.append(action)

            if not self._agent_config.dry_run:
                modified = True
                action.applied = True

        # Check for bare except clauses
        for i, line in enumerate(lines):
            if re.match(r"^\s*except\s*:\s*$", line):
                action = HealingAction(
                    healing_type="CANON",
                    file_path=file_path,
                    line_number=i + 1,
                    description="Replace bare except with except Exception",
                    old_code=line,
                    new_code=line.replace("except:", "except Exception:"),
                )
                actions.append(action)

                if not self._agent_config.dry_run:
                    new_lines[i] = line.replace("except:", "except Exception:")
                    modified = True
                    action.applied = True

        if modified:
            new_content = "\n".join(new_lines)
            if self.atomic_write(file_path, new_content):
                for action in actions:
                    if not action.applied:
                        action.applied = True
            else:
                Logger.error(f"Failed to apply atomic write to {file_path}")

        self._actions.extend(actions)
        return actions

    def heal_structural(self, file_path: Path) -> list[HealingAction]:
        """Fix structural issues."""
        actions = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return actions

        lines = content.split("\n")
        new_lines = lines.copy()
        modified = False

        # Check for trailing whitespace
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                action = HealingAction(
                    healing_type="STRUCTURAL",
                    file_path=file_path,
                    line_number=i + 1,
                    description="Remove trailing whitespace",
                    old_code=repr(line),
                    new_code=repr(line.rstrip()),
                )
                actions.append(action)

                if not self._agent_config.dry_run:
                    new_lines[i] = line.rstrip()
                    modified = True
                    action.applied = True

        # Check for multiple blank lines
        blank_count = 0
        for i, line in enumerate(lines):
            if line.strip() == "":
                blank_count += 1
                if blank_count > 2:
                    action = HealingAction(
                        healing_type="STRUCTURAL",
                        file_path=file_path,
                        line_number=i + 1,
                        description="Remove excessive blank lines",
                        old_code="(blank line)",
                        new_code="(removed)",
                    )
                    actions.append(action)
            else:
                blank_count = 0

        if modified:
            new_content = "\n".join(new_lines)
            if self.atomic_write(file_path, new_content):
                for action in actions:
                    if not action.applied:
                        action.applied = True
            else:
                Logger.error(f"Failed to apply atomic write to {file_path}")

        self._actions.extend(actions)
        return actions

    def _backup_file(self, file_path: Path) -> Path | None:
        """Create backup before healing."""
        if not self._agent_config.backup_before_heal:
            return None

        backup_dir = self._agent_config.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.name}.{timestamp}"

        shutil.copy2(file_path, backup_path)
        Logger.info(f"Backed up {file_path} to {backup_path}")

        return backup_path

    def get_actions(self) -> list[HealingAction]:
        """Get all recorded healing actions."""
        return self._actions.copy()

    def heal(self, violation: dict) -> dict:
        """Heal code violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (canon, import, structural, syntax)
                - path: Path to the violating file
                - severity: Severity level of the violation
                - line_number: Line number of the violation (if applicable)

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        from agentic_core.base_agents.decorators import standard_heal

        @standard_heal
        def _heal_code_violation(self, violation: dict) -> dict:
            """Internal heal method with standard_heal decorator."""
            violation_type = violation.get("type", "syntax")
            path = violation.get("path", "")
            line_number = violation.get("line_number", 0)

            Logger.info(f"[CODE_HEALER] Healing {violation_type} violation at {path}:{line_number}")

            if violation_type == "canon":
                # Heal canon compliance violations
                return self._heal_canon_violation(violation)
            elif violation_type == "import":
                # Heal import violations
                return self._heal_import_violation(violation)
            elif violation_type == "structural":
                # Heal structural violations
                return self._heal_structural_violation(violation)
            elif violation_type == "syntax":
                # Heal syntax violations
                return self._heal_syntax_violation(violation)
            else:
                Logger.warning(f"[CODE_HEALER] Unknown violation type: {violation_type}")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        return _heal_code_violation(self, violation)

    def _heal_canon_violation(self, violation: dict) -> dict:
        """Heal canon compliance violations."""
        try:
            path = Path(violation.get("path", ""))
            if not path.exists():
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

            # Apply canon healing
            actions = self.heal_canon(path)
            fixed_count = sum(1 for action in actions if action.applied)
            
            Logger.info(f"[CODE_HEALER] Fixed {fixed_count} canon violations in {path}")
            return {"violations_fixed": fixed_count, "violations_found": len(actions), "errors": 0, "skipped": 0}
        except Exception as e:
            Logger.error(f"[CODE_HEALER] Failed to heal canon violation: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

    def _heal_import_violation(self, violation: dict) -> dict:
        """Heal import violations."""
        try:
            path = Path(violation.get("path", ""))
            if not path.exists():
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

            # Apply import healing
            actions = self.heal_imports(path)
            fixed_count = sum(1 for action in actions if action.applied)
            
            Logger.info(f"[CODE_HEALER] Fixed {fixed_count} import violations in {path}")
            return {"violations_fixed": fixed_count, "violations_found": len(actions), "errors": 0, "skipped": 0}
        except Exception as e:
            Logger.error(f"[CODE_HEALER] Failed to heal import violation: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

    def _heal_structural_violation(self, violation: dict) -> dict:
        """Heal structural violations."""
        try:
            path = Path(violation.get("path", ""))
            if not path.exists():
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

            # Apply structural healing
            actions = self.heal_structural(path)
            fixed_count = sum(1 for action in actions if action.applied)
            
            Logger.info(f"[CODE_HEALER] Fixed {fixed_count} structural violations in {path}")
            return {"violations_fixed": fixed_count, "violations_found": len(actions), "errors": 0, "skipped": 0}
        except Exception as e:
            Logger.error(f"[CODE_HEALER] Failed to heal structural violation: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

    def _heal_syntax_violation(self, violation: dict) -> dict:
        """Heal syntax violations."""
        try:
            path = Path(violation.get("path", ""))
            if not path.exists():
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

            # For syntax violations, we typically can't auto-heal
            # Log the issue and mark as skipped
            Logger.warning(f"[CODE_HEALER] Syntax violations require manual intervention: {path}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        except Exception as e:
            Logger.error(f"[CODE_HEALER] Failed to heal syntax violation: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}


# Factory methods for backward compatibility
def create_legacy_canon_healer() -> CodeHealerAgent:
    """Create healer for canon compliance only."""
    config = HealerConfig(
        enable_canon=True,
        enable_import=False,
        enable_structural=False,
    )
    return CodeHealerAgent(config=config)


def create_legacy_import_healer() -> CodeHealerAgent:
    """Create healer for imports only."""
    config = HealerConfig(
        enable_canon=False,
        enable_import=True,
        enable_structural=False,
    )
    return CodeHealerAgent(config=config)
