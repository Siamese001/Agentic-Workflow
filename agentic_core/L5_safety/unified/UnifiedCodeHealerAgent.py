#!/usr/bin/env python3
"""
UnifiedCodeHealerAgent - Code Healing & Repair

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
from __future__ import annotations

import ast
import logging
import re
import shutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

Logger = logging.getLogger(__name__)


from enum import Enum, auto


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
    """Configuration for code healing."""
    enable_canon: bool = True
    enable_import: bool = True
    enable_structural: bool = True
    dry_run: bool = True
    backup_before_heal: bool = True
    backup_dir: Optional[Path] = None


class UnifiedCodeHealerAgent:
    """
    Unified code healer for canon, imports, and structure.

    Consolidates:
    - CanonHealerAgent
    - ImportHealerAgent
    - StructuralHealerAgent

    Usage:
        healer = UnifiedCodeHealerAgent()

        # Heal imports in a file
        actions = healer.heal_imports(Path("my_agent.py"))

        # Heal all issues
        actions = healer.heal_all(Path("my_agent.py"))
    """

    # Standard library modules for import classification
    STDLIB_MODULES = {
        "os", "sys", "re", "json", "ast", "typing", "pathlib", "logging",
        "datetime", "collections", "functools", "itertools", "threading",
        "asyncio", "dataclasses", "enum", "abc", "contextlib", "copy",
        "hashlib", "secrets", "shutil", "tempfile", "unittest", "time",
    }

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[HealerConfig] = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.config = config or HealerConfig()
        self._lock = threading.RLock()
        self._actions: List[HealingAction] = []

        if self.config.backup_dir is None:
            self.config.backup_dir = self.project_root / "archives" / "healing_backups" / "code"

        Logger.info("UnifiedCodeHealerAgent initialized")

    def heal_all(self, file_path: Path) -> List[HealingAction]:
        """Run all enabled healing on a file."""
        actions = []

        if not file_path.exists():
            return actions

        if self.config.enable_import:
            actions.extend(self.heal_imports(file_path))

        if self.config.enable_canon:
            actions.extend(self.heal_canon(file_path))

        if self.config.enable_structural:
            actions.extend(self.heal_structural(file_path))

        return actions

    def heal_imports(self, file_path: Path) -> List[HealingAction]:
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
        imports: List[Tuple[ast.AST, str, int]] = []
        used_names: Set[str] = set()

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
        if not self.config.dry_run and unused_imports:
            self._backup_file(file_path)

            # Remove unused import lines
            new_lines = []
            unused_line_numbers = {lineno for _, lineno in unused_imports}

            for i, line in enumerate(lines, 1):
                if i not in unused_line_numbers:
                    new_lines.append(line)

            file_path.write_text("\n".join(new_lines), encoding="utf-8")

            for action in actions:
                action.applied = True

        self._actions.extend(actions)
        return actions

    def heal_canon(self, file_path: Path) -> List[HealingAction]:
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

            if not self.config.dry_run:
                new_lines.insert(0, "from __future__ import annotations")
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

                if not self.config.dry_run:
                    new_lines[i] = line.replace("except:", "except Exception:")
                    modified = True
                    action.applied = True

        if modified:
            self._backup_file(file_path)
            file_path.write_text("\n".join(new_lines), encoding="utf-8")

        self._actions.extend(actions)
        return actions

    def heal_structural(self, file_path: Path) -> List[HealingAction]:
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

                if not self.config.dry_run:
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
            self._backup_file(file_path)
            file_path.write_text("\n".join(new_lines), encoding="utf-8")

        self._actions.extend(actions)
        return actions

    def _backup_file(self, file_path: Path) -> Optional[Path]:
        """Create backup before healing."""
        if not self.config.backup_before_heal:
            return None

        backup_dir = self.config.backup_dir
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.name}.{timestamp}"

        shutil.copy2(file_path, backup_path)
        Logger.info(f"Backed up {file_path} to {backup_path}")

        return backup_path

    def get_actions(self) -> List[HealingAction]:
        """Get all recorded healing actions."""
        return self._actions.copy()


# Factory methods for backward compatibility
def create_legacy_canon_healer() -> UnifiedCodeHealerAgent:
    """Create healer for canon compliance only."""
    config = HealerConfig(
        enable_canon=True,
        enable_import=False,
        enable_structural=False,
    )
    return UnifiedCodeHealerAgent(config=config)


def create_legacy_import_healer() -> UnifiedCodeHealerAgent:
    """Create healer for imports only."""
    config = HealerConfig(
        enable_canon=False,
        enable_import=True,
        enable_structural=False,
    )
    return UnifiedCodeHealerAgent(config=config)
