from __future__ import annotations
from dataclasses import dataclass
"""
FileSystemAgent: Sovereign Non-Python File Naming Enforcer

[P5 CONSOLIDATION] 2025-12-31:
This agent is transitioning to READ-ONLY mode. File operations (moves, archives)
should be delegated to HealerAgent for centralized execution.

Current responsibilities (READ-ONLY):
- Scan for repeated suffixes (.archived.archived...)
- Detect generic/versioned names
- Identify low-signal files
- Report violations for HealerAgent to process

DEPRECATED operations (use HealerAgent instead):
- cleanup_violations() -> Use HealerAgent.heal_file_moves()
- run_with_cleanup() -> Use FilesystemAgent.run() + HealerAgent

For file operations, use:
    from agentic_core.L5_safety.gravity.StructuralHealerAgent import StructuralHealerAgent
    violations = FilesystemAgent(project_root).run()  # Detection only
    healer = StructuralHealerAgent(project_root)
    healer.heal_file_moves(violations)  # Execution

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

from agentic_core.L5_safety.validators.structure_blueprint import (
    FORBIDDEN_PATTERNS,
    HEALING_CONFIG,
    SOVEREIGN_EXCLUDED_FOLDERS,
    CANON_KEY_TO_FOLDER_MAP
)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError

Logger = logging.getLogger(__name__)


@dataclass
class FilesystemAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Autonomous agent for physical filesystem purity.
    Targets technical debt markers in non-Python files with auto-remediation.
    """
    def __init__(self, project_root: Path, dry_run: bool = False) -> None:
        """Initialize the instance."""
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
            Logger.info(f"[FileSystemAgent] Backup territory sealed at: {self.backup_dir}")
            Logger.info(f"[FileSystemAgent] Archives root initialized at: {self.archives_root}")

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

            # [BUG FIX 2025-12-31] Skip files that are already in archives directory
            # Prevents re-processing archived files
            if 'archives' in file_path.parts:
                continue

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
        AST-based categorization of non-Python files.
        Analyzes all .py files in directory:
        - Priority 1: Class/function names (strong signal)
        - Priority 2: Import paths
        - Priority 3: Keyword density (via NamingAgent)
        - Maps to CANON_KEY_TO_FOLDER_MAP paths
        - Fallback: archives/uncategorized/
        """
        dir_path = file_path.parent
        py_files = list(dir_path.glob("*.py"))

        if not py_files:
            uncat = self.archives_root / "uncategorized"
            uncat.mkdir(exist_ok=True)
            return uncat

        # Aggregate signals from all .py files in current territory
        all_classes = set()
        all_functions = set()
        all_imports = set()
        content_preview = ""

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                content_preview += content[:3000]  # Limit per file to avoid OOM
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        all_classes.add(node.name)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        all_functions.add(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            root = alias.name.split(".")[0]
                            all_imports.add(root)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        root = node.module.split(".")[0]
                        all_imports.add(root)
            except Exception:
                continue

        # PRIORITY 1: Strong class/function symbols
        strong_symbols = all_classes.union(all_functions)
        symbol_signals = {
            "orchestrator": "agentic_core/L3_orchestration",
            "engine": "agentic_core/L3_orchestration",
            "workflow": "agentic_core/L3_orchestration",
            "strategy": "agentic_core/L1_cognition",
            "reasoning": "agentic_core/L1_cognition",
            "memory": "agentic_core/L4_state",
            "state": "agentic_core/L4_state",
            "validator": "agentic_core/L5_safety",
            "guardrail": "agentic_core/L5_safety",
            "prompt": "agentic_core/prompt_governance",
            "template": "agentic_core/prompt_governance",
            "schema": "agentic_core/schemas",
        }

        for symbol in strong_symbols:
            lower_symbol = symbol.lower()
            for keyword, path in symbol_signals.items():
                if keyword in lower_symbol:
                    subpath = self.archives_root / path
                    subpath.mkdir(parents=True, exist_ok=True)
                    return subpath

        # PRIORITY 2: Import-based territory signals
        import_signals = {
            "L3_orchestration": "agentic_core/L3_orchestration",
            "L1_cognition": "agentic_core/L1_cognition",
            "L4_state": "agentic_core/L4_state",
            "L5_safety": "agentic_core/L5_safety",
            "prompt_governance": "agentic_core/prompt_governance",
            "schemas": "agentic_core/schemas",
        }

        for imp in all_imports:
            for key, path in import_signals.items():
                if key.lower() in imp.lower():
                    subpath = self.archives_root / path
                    subpath.mkdir(parents=True, exist_ok=True)
                    return subpath

        # PRIORITY 3: Keyword fallback using NamingAgent guidance
        if content_preview:
            try:
                from agentic_core.utils.naming.NamingAgent import NamingAgent
                naming = NamingAgent(self.project_root)
                guidance = naming.get_placement_guidance(content_preview)
                if "/" in guidance:
                    subpath = self.archives_root / guidance
                    subpath.mkdir(parents=True, exist_ok=True)
                    return subpath
            except Exception as e:
                Logger.debug(f"[FileSystemAgent] NamingAgent guidance failed: {e}")

        # FINAL FALLBACK: Uncategorized purge
        uncat = self.archives_root / "uncategorized"
        uncat.mkdir(exist_ok=True)
        return uncat

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
                Logger.warning(f"[FileSystemAgent] Healing budget exhausted ({self.max_cleanups} actions).")
                break

            action = {
                "type": "FILESYSTEM_PURGE",
                "file": str(file_path),
                "Violation": msg,
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
                    Logger.info(f"   [PURGED] {file_path.name} -> archives/{target_path.relative_to(self.archives_root)}")
                except Exception as e:
                    action["reason"] = f"Archival move error: {e}"

            actions.append(action)

        return actions

    def run_with_cleanup(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        [DEPRECATED - P5 CONSOLIDATION] Use run() + HealerAgent instead.
        
        Standard entry point for Orchestrator integration.
        Performs full scan followed by immediate autonomous healing.
        
        Prefer:
            violations = FilesystemAgent(project_root).run()
            healer = HealerAgent(project_root)
            healer.heal_file_moves(violations)
        """
        import warnings
        warnings.warn(
            "FilesystemAgent.run_with_cleanup() is deprecated. "
            "Use run() for detection, then HealerAgent for execution.",
            DeprecationWarning,
            stacklevel=2
        )
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

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Set[str] = None,
    ) -> Dict[str, int]:
        """
        Autonomous full-repository filesystem law healing.
        Canon Key 51 compliance - fully self-orchestrating.
        """
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        
        if agent_name in _call_path:
            print(f"  [!] HEALING CYCLE DETECTED: {agent_name}")
            return {"healed": 0, "errors": 0, "skipped": 0, "cycle_detected": True}
        
        if depth > max_depth:
            print(f"  [!] RECURSION DEPTH LIMIT ({depth}/{max_depth})")
            return {"healed": 0, "errors": 0, "skipped": 0, "depth_limited": True}
        
        _call_path.add(agent_name)
        
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            
            violations = self.run()
            print(f"[FILESYSTEM HEAL @ depth {depth}] Found {len(violations)} violations")
            
            counts = {"healed": 0, "errors": 0, "skipped": 0}
            
            for file_path, reason in violations:
                try:
                    cleanup_results = self.cleanup_violations([(file_path, reason)])
                    if cleanup_results and len(cleanup_results) > 0:
                        counts["healed"] += 1
                        print(f"  [+] HEALED: {file_path.name}")
                    else:
                        counts["skipped"] += 1
                except Exception as e:
                    counts["errors"] += 1
                    print(f"  [!] ERROR on {file_path.name}: {e}")
            
            print(f"\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin\n[FILESYSTEM HEAL SUMMARY] Healed: {counts['healed']} | Skipped: {counts['skipped']} | Errors: {counts['errors']}")
            return counts
        finally:
            _call_path.discard(agent_name)


# PascalCase is now the canonical name
