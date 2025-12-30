"""
FileSystemAgent: Sovereign Non-Python File Naming Enforcer

Enforces naming laws on all files (not just .py):
- No repeated suffixes (.archived.archived...)
- No generic/versioned names
- High-signal where applicable
- Move clutter to dedicated archives/ with AST-aware sub-paths
- Automatic cleanup (rename/archive) with guardrails

Integrates with HealerAgent safety system (backup, budget, dry-run) per Phase 10.

Placed in L5_safety/validators per SSOT extension:
  "Hard safety limits, mutation controls, deletion guards"

Depth: agentic_core/L5_safety/validators/filesystem_agent.py -> 4 parts -> compliant
"""
import re
import ast
import shutil
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Set
from datetime import datetime

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    FORBIDDEN_PATTERNS,
    HEALING_CONFIG,
    SOVEREIGN_EXCLUDED_FOLDERS,
    CANON_KEY_TO_FOLDER_MAP
)

logger = logging.getLogger(__name__)


class filesystem_agent:
    """
    Autonomous agent for physical filesystem purity.
    Targets technical debt markers in non-Python files with auto-remediation.
    """
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root.resolve()
        self.forbidden_patterns = FORBIDDEN_PATTERNS
        # REGEX: Catches repeated markers like .archived.archived or .old.old
        self.repeated_suffix = re.compile(r"\.(archived|backup|old|copy)+\.?\1", re.IGNORECASE)
        self.dry_run = dry_run

        # Healing configuration derived from Mission SSOT
        self.max_cleanups = HEALING_CONFIG.get("max_filesystem_cleanups_per_run", 50)
        self.backup_dir = self.project_root / ".sovereign_healing_backup" / "filesystem" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archives_root = self.project_root / "archives"
        self.cleanups_applied = 0

        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.archives_root.mkdir(exist_ok=True)
            logger.info(f"[FileSystemAgent] Backup territory sealed at: {self.backup_dir}")
            logger.info(f"[FileSystemAgent] Archives root initialized at: {self.archives_root}")

    def run(self) -> List[Tuple[Path, str]]:
        """
        Scan project root for naming violations in non-Python files.
        Excludes Python files (delegated to NamingAgent) and protected directories.
        """
        violations: List[Tuple[Path, str]] = []
        
        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Performance & Safety: Skip excluded territories and Python source
            if any(ex in file_path.parts for ex in SOVEREIGN_EXCLUDED_FOLDERS):
                continue
            if file_path.suffix == ".py":
                continue

            name = file_path.name

            # 1. Detection: Repeated Suffixes
            if self.repeated_suffix.search(name):
                violations.append((file_path, f"REPEATED technical suffix: {name}"))
                continue

            # 2. Detection: Forbidden Patterns (Generic/Versioned)
            for pattern in self.forbidden_patterns:
                if pattern.match(name):
                    violations.append((file_path, f"FORBIDDEN pattern: {name}"))
                    break

        return violations

    def _determine_archive_subpath(self, file_path: Path) -> Path:
        """
        Determine the closest matching sovereign territory sub-path in archives/
        by analyzing the AST of surrounding Python files.
        """
        dir_path = file_path.parent
        # Find nearby .py files to establish context
        py_files = list(dir_path.glob("*.py"))

        if not py_files:
            return self.archives_root / "uncategorized"

        # Analyze the primary script in the directory for context
        try:
            content = py_files[0].read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            imports: Set[str] = set()
            classes: Set[str] = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
                elif isinstance(node, ast.ClassDef):
                    classes.add(node.name)

            best_match = ""
            # Cross-reference symbols with the SSOT Folder Map
            for key_patterns in CANON_KEY_TO_FOLDER_MAP.values():
                for pattern in key_patterns:
                    if pattern == "*": continue
                    # Dot-notation match for imports (e.g., L1_cognition)
                    dot_pattern = pattern.replace("/", ".")
                    if any(imp.startswith(dot_pattern) for imp in imports) or \
                       any(cls.lower() in pattern.lower() for cls in classes):
                        best_match = pattern # Keyed to blueprint path

            if best_match:
                target_sub = self.archives_root / best_match
                target_sub.mkdir(parents=True, exist_ok=True)
                return target_sub

        except Exception as e:
            logger.debug(f"[FileSystemAgent] AST contextualization failed: {e}")

        # Explicit fallback to maintain structured purity
        return self.archives_root / "uncategorized"

    def _backup_file(self, file_path: Path) -> Path:
        """
        Create a physical safety copy before mutation.
        """
        if self.dry_run:
            return file_path
        rel = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def cleanup_violations(self, violations: List[Tuple[Path, str]]) -> List[Dict[str, Any]]:
        """
        Execute autonomous PURGE missions.
        - Relocates clutter directly to structured archives/
        - Strips technical suffixes (.archived, .old, .backup)
        - Uses AST context for sub-territory placement
        """
        actions = []

        for file_path, msg in violations:
            if self.cleanups_applied >= self.max_cleanups:
                logger.warning(f"[FileSystemAgent] Healing budget exhausted ({self.max_cleanups} actions).")
                break

            action = {
                "type": "FILESYSTEM_PURGE",
                "file": str(file_path),
                "violation": msg,
                "applied": False,
                "action_taken": "",
                "target": ""
            }

            # 1. Clean the filename (strip suffixes)
            name = file_path.name
            cleaned_name = name
            for marker in [".archived", ".backup", ".old", ".copy"]:
                while marker in cleaned_name.lower():
                    # Regex-free iterative stripping to handle multiple extensions
                    idx = cleaned_name.lower().find(marker)
                    cleaned_name = cleaned_name[:idx] + cleaned_name[idx+len(marker):]

            # 2. Determine Relocation Path
            archive_subpath = self._determine_archive_subpath(file_path)
            target_path = archive_subpath / cleaned_name

            if target_path.exists():
                action["reason"] = f"Aborted: Archive collision for {cleaned_name}"
            elif self.dry_run:
                action["applied"] = True
                action["action_taken"] = f"PURGE_PREVIEW: Would move to {target_path.relative_to(self.archives_root)}"
                action["target"] = str(target_path)
            else:
                try:
                    # Ensure subdirectory exists in archives/
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    self._backup_file(file_path)
                    
                    # Physical relocation
                    file_path.rename(target_path)
                    
                    action["applied"] = True
                    action["action_taken"] = f"PURGED: Relocated to archives/{target_path.relative_to(self.archives_root)}"
                    action["target"] = str(target_path)
                    self.cleanups_applied += 1
                    logger.info(f"   [PURGED] {file_path.name} -> archives/{target_path.relative_to(self.archives_root)}")
                except Exception as e:
                    action["reason"] = f"Archival move error: {e}"

            actions.append(action)

        return actions

    def run_with_cleanup(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Standard entry point for Orchestrator integration.
        Performs full scan followed by immediate autonomous healing.
        """
        original_dry_mode = self.dry_run
        self.dry_run = dry_run

        detected_violations = self.run()
        cleanup_results = self.cleanup_violations(detected_violations) if detected_violations else []

        self.dry_run = original_dry_mode # Restore state

        return {
            "violations_detected": len(detected_violations),
            "actions_applied": len(cleanup_results),
            "detailed_actions": cleanup_results,
            "backup_path": str(self.backup_dir) if not dry_run else "DRY-RUN_MODE"
        }


# Uppercase alias for backward compatibility
FileSystemAgent = filesystem_agent
