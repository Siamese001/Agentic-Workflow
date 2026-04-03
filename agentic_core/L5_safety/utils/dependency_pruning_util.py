"""Dependency Pruning Utility - Deterministic unused dependency detection.

This module provides deterministic dependency pruning functionality previously
implemented in DependencyPruningAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 9).

Usage:
    from agentic_core.L5_safety.utils.dependency_pruning_util import (
        DependencyPruner, find_unused_deptry, remove_from_requirements_txt
    )
    
    # Find unused dependencies
    unused = find_unused_deptry(Path("."))
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT

Logger = logging.getLogger(__name__)


@dataclass
class PruningResult:
    """Result of dependency pruning."""
    
    unused_found: int
    removed: int
    dry_run: bool
    packages: list[str]
    adg_dead_import_signals: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "unused_found": self.unused_found,
            "removed": self.removed,
            "dry_run": self.dry_run,
            "packages": self.packages,
            "adg_dead_import_signals": self.adg_dead_import_signals,
        }


def safe_execute(
    command: list[str],
    cwd: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> subprocess.CompletedProcess | None:
    """Safely execute a subprocess command.
    
    Args:
        command: Command and arguments to execute
        cwd: Working directory for execution
        timeout: Timeout in seconds
        
    Returns:
        CompletedProcess result or None if failed
    """
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        Logger.debug(f"Command execution failed: {e}")
        return None


def find_unused_deptry(project_root: Path) -> list[str]:
    """Use deptry to find unused dependencies via AST analysis.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        List of unused package names, empty if deptry fails or not installed
    """
    result = safe_execute(["deptry", ".", "--json"], cwd=project_root)
    
    if result is None or result.returncode != 0:
        return []
    
    try:
        data: dict[str, Any] = json.loads(result.stdout)
        return data.get("unused", [])
    except (json.JSONDecodeError, Exception):
        return []


def remove_from_requirements_txt(
    unused: list[str],
    requirements_path: Path,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Remove unused packages from requirements.txt.
    
    Args:
        unused: List of package names to remove
        requirements_path: Path to requirements.txt
        dry_run: If True, only comment out instead of removing
        
    Returns:
        Dictionary with removal results
    """
    if not requirements_path.exists():
        return {"removed": 0}
    
    content: str = requirements_path.read_text(encoding="utf-8")
    lines: list[str] = content.splitlines()
    new_lines: list[str] = []
    removed: int = 0
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            new_lines.append(line)
            continue
        
        match = re.match("^([a-zA-Z0-9_-]+)", line_stripped)
        if match and match.group(1).lower() in [u.lower() for u in unused]:
            removed += 1
            if dry_run:
                new_lines.append(f"# [PRUNED UNUSED] {line}")
            else:
                continue
        else:
            new_lines.append(line)
    
    if removed > 0 and not dry_run:
        requirements_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    
    return {"removed": removed, "file": "requirements.txt"}


class DependencyPruner:
    """Deterministic dependency pruner."""
    
    def __init__(
        self,
        project_root: Path,
        dry_run: bool = True,
    ) -> None:
        """Initialize dependency pruner.
        
        Args:
            project_root: Root directory of the project
            dry_run: If True, only report what would be removed
        """
        self.project_root: Path = Path(project_root)
        self.dry_run: bool = dry_run
        self.requirements_path: Path = self.project_root / "requirements.txt"
    
    def scan(self) -> PruningResult:
        """Scan for unused dependencies.
        
        Returns:
            PruningResult with scan results
        """
        Logger.info("[PRUNE] Scanning for unused dependencies...")
        
        # Get ADG dead import signals if available
        adg_dead_imports: int = 0
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp
            _src = Path(__file__).resolve()
            _bp = _gbp(_src, self.project_root)
            adg_dead_imports = len(_bp.antipattern_signals)
        except (RuntimeError, OSError, ImportError):
            pass
        
        # Find unused dependencies
        unused: list[str] = find_unused_deptry(self.project_root)
        
        if not unused:
            Logger.info("[✓] No unused dependencies detected")
            return PruningResult(
                unused_found=0,
                removed=0,
                dry_run=self.dry_run,
                packages=[],
                adg_dead_import_signals=adg_dead_imports,
            )
        
        Logger.info(f"[!] Found {len(unused)} potentially unused packages: {', '.join(unused[:5])}")
        if len(unused) > 5:
            Logger.info(f"       ... and {len(unused) - 5} more")
        
        return PruningResult(
            unused_found=len(unused),
            removed=0,  # Not removed yet, just scanned
            dry_run=self.dry_run,
            packages=unused,
            adg_dead_import_signals=adg_dead_imports,
        )
    
    def prune(self) -> PruningResult:
        """Scan and optionally remove unused dependencies.
        
        Returns:
            PruningResult with pruning results
        """
        scan_result = self.scan()
        
        if scan_result.unused_found == 0:
            return scan_result
        
        # Remove from requirements.txt
        removal_result = remove_from_requirements_txt(
            scan_result.packages,
            self.requirements_path,
            self.dry_run,
        )
        
        return PruningResult(
            unused_found=scan_result.unused_found,
            removed=removal_result["removed"],
            dry_run=self.dry_run,
            packages=scan_result.packages,
            adg_dead_import_signals=scan_result.adg_dead_import_signals,
        )
    
    def heal_repository(self, dry_run: bool = True) -> dict[str, Any]:
        """Heal repository by pruning unused dependencies.
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Healing result dictionary
        """
        self.dry_run = dry_run
        result = self.prune()
        
        return {
            "violations_found": result.unused_found,
            "violations_fixed": result.removed if not dry_run else 0,
            "errors": 0,
            "skipped": result.unused_found - result.removed,
            "packages": result.packages,
        }
    
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal a single dependency violation.
        
        Args:
            violation: Dictionary with violation details
            
        Returns:
            Healing result dictionary
        """
        package = violation.get("package", "")
        if package:
            try:
                self.dry_run = False
                result = remove_from_requirements_txt([package], self.requirements_path, False)
                return {
                    "violations_fixed": result.get("removed", 0),
                    "violations_found": 1,
                    "errors": 0,
                    "skipped": 0,
                }
            except (RuntimeError, OSError):
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}
        
        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}


def prune_dependencies(
    project_root: str | Path,
    dry_run: bool = True,
) -> PruningResult:
    """Convenience function to prune dependencies.
    
    Args:
        project_root: Project root directory
        dry_run: If True, only report what would be removed
        
    Returns:
        PruningResult with pruning results
    """
    pruner = DependencyPruner(Path(project_root), dry_run)
    return pruner.prune()
