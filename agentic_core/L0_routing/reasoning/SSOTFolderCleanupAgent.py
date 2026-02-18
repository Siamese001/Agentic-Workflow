from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
[PHASE 24] SSOT Folder Cleanup Agent - Automated SSOT Compliance Enforcement.

Provides automated cleanup of non-SSOT-approved folders:
1. Identifies files in non-approved folders
2. Uses CognitiveDispositionAgent to determine target SSOT folder
3. Moves files via ArchivalGatekeeper (audited, safe)
4. Updates imports across the codebase
5. Deletes empty non-approved folders

This agent enforces the SSOT protocol by ensuring all files are in approved locations.

[SSOT] This is the canonical agent for SSOT folder cleanup operations.
"""


import ast
import logging
import os
import re
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write

Logger = logging.getLogger(__name__)


class SSOTFolderCleanupAgent(SovereignBaseAgent):
    """
    [PHASE 24] Automated SSOT Folder Cleanup Agent.

    Responsibilities:
    1. Scan for files in non-SSOT-approved folders
    2. Triage files using CognitiveDispositionAgent
    3. Move files to SSOT-approved locations via ArchivalGatekeeper
    4. Update all imports referencing moved files
    5. Delete empty non-approved folders

    Safety Features:
    - All moves go through ArchivalGatekeeper (audited)
    - Dry-run mode for preview
    - Import updates are AST-based (safe)
    - Empty folder deletion is recursive-safe
    """

    def __init__(
        self,
        project_root: Path | None = None,
        dry_run: bool = True,
    ):
        """
        Initialize the SSOT Folder Cleanup Agent.

        Args:
            project_root: Root of the project (auto-detected if None)
            dry_run: If True, only report actions without executing
        """
        self.project_root = project_root or self._detect_project_root()
        self.dry_run = dry_run

        # Lazy-loaded dependencies
        self._cognitive_agent = None
        self._archival_gatekeeper = None

        # Statistics
        self.stats = {
            "files_scanned": 0,
            "files_moved": 0,
            "files_archived": 0,
            "imports_updated": 0,
            "folders_deleted": 0,
            "errors": 0,
        }

        # Load SSOT configuration
        self._load_ssot_config()

    def _detect_project_root(self) -> Path:
        """Detect project root by looking for pyproject.toml or .git."""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                return parent
        return current

    def _load_ssot_config(self) -> None:
        """Load SSOT configuration from L0 config."""
        from agentic_core.L0_routing.config import (
            L4_APPROVED_FOLDERS,
            VARIABLE_DEPTH_SUBFOLDERS,
        )

        # Derive SOVEREIGN_REGISTRY and CORE_SUBFOLDER_MAP from L0 constants
        self.sovereign_registry = {
            "agentic_core": {"depth": 4},
            "apps_lic": {"depth": 3},
            "apps_rg": {"depth": 3},
        }
        self.core_subfolder_map = {
            "L0_routing": ["config", "reasoning", "scripts", "types", "utils", "enforcement"],
            "L1_cognition": ["P1_core", "reasoning", "types", "utils"],
            "L2_execution": ["P1_core", "enforcement", "reasoning", "types", "utils"],
            "L3_orchestration": ["P1_core", "engines", "reasoning", "types", "utils"],
            "L4_state": ["P1_core", "memory", "reasoning", "types", "utils"],
            "L5_safety": [
                "P1_core",
                "config",
                "core_kernel",
                "guardians",
                "reasoning",
                "types",
                "utils",
                "validators",
            ],
            "L6_observability": ["P1_core", "dashboards", "reasoning", "types", "utils"],
        }
        self.l4_approved_folders = L4_APPROVED_FOLDERS
        self.variable_depth_subfolders = VARIABLE_DEPTH_SUBFOLDERS

        # Build set of all approved paths
        self._build_approved_paths()

    def _build_approved_paths(self) -> None:
        """Build the complete set of SSOT-approved paths."""
        self.approved_paths = set()

        # Add sovereign registry roots
        for root in self.sovereign_registry.keys():
            self.approved_paths.add(root)

            # Add subfolders
            subfolders = self.sovereign_registry[root].get("subfolders", [])
            for subfolder in subfolders:
                self.approved_paths.add(f"{root}/{subfolder}")

        # Add core subfolder map paths
        for layer, subfolders in self.core_subfolder_map.items():
            for subfolder in subfolders:
                self.approved_paths.add(f"agentic_core/{layer}/{subfolder}")

        # Add L4 approved folders
        self.approved_paths.update(self.l4_approved_folders)

        # Add special folders
        self.approved_paths.add("archives")
        self.approved_paths.add("data")
        self.approved_paths.add("docs")
        self.approved_paths.add("reports")

    def _get_cognitive_agent(self):
        """Lazy-load CognitiveDispositionAgent."""
        if self._cognitive_agent is None:
            from agentic_core.L0_routing.seams.safety_reasoning_seam import (
                load_cognitive_disposition_agent,
            )

            CognitiveDispositionAgent = load_cognitive_disposition_agent()
            # guardian: allow-magic-config
            self._cognitive_agent = CognitiveDispositionAgent(
                project_root=self.project_root,
                confidence_threshold=0.75,  # Unified threshold > 0.75
            )
        return self._cognitive_agent

    def _get_archival_gatekeeper(self):
        """Lazy-load ArchivalGatekeeper."""
        if self._archival_gatekeeper is None:
            from agentic_core.L0_routing.seams.safety_enforcement_seam import (
                load_archival_gatekeeper,
            )

            ArchivalGatekeeper = load_archival_gatekeeper().ArchivalGatekeeper
            self._archival_gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)
        return self._archival_gatekeeper

    def is_path_ssot_approved(self, path: Path) -> bool:
        """
        Check if a path is in an SSOT-approved location.

        A path is approved if:
        1. It's directly in an approved subfolder (e.g., agentic_core/L5_safety/validators)
        2. It's a file directly in a layer folder (e.g., agentic_core/L5_safety/__init__.py)

        A path is NOT approved if:
        1. It's in a subfolder that's not in CORE_SUBFOLDER_MAP

        Args:
            path: Path to check (relative to project root)

        Returns:
            True if path is in an approved location
        """
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            return False

        parts = rel_path.parts

        if not parts:
            return False

        # For agentic_core, we need stricter checking
        if parts[0] == "agentic_core" and len(parts) >= 2:
            layer = parts[1]

            # Check if layer is valid
            valid_layers = self.sovereign_registry.get("agentic_core", {}).get("subfolders", [])
            if layer not in valid_layers:
                return False

            # If file is directly in layer folder (depth 2), it's approved
            # e.g., agentic_core/L5_safety/__init__.py
            if len(parts) == 3 and parts[2].endswith(".py"):
                return True

            # If there's a subfolder, check if it's in CORE_SUBFOLDER_MAP
            if len(parts) >= 3:
                subfolder = parts[2]
                approved_subfolders = self.core_subfolder_map.get(layer, [])

                if subfolder not in approved_subfolders:
                    return False

                return True

            return True

        # For other sovereign roots (tests, scripts, etc.)
        if parts[0] in self.sovereign_registry:
            return True

        # Check explicit approved paths
        for i in range(1, len(parts) + 1):
            check_path = "/".join(parts[:i])
            if check_path in self.approved_paths:
                return True

        return False

    def find_non_approved_files(self) -> list[Path]:
        """
        Find all Python files in non-SSOT-approved folders.

        Returns:
            List of file paths that need to be moved
        """
        non_approved_files = []

        # Scan agentic_core for non-approved files
        agentic_core = self.project_root / "agentic_core"
        if not agentic_core.exists():
            return non_approved_files

        for py_file in agentic_core.rglob("*.py"):
            self.stats["files_scanned"] += 1

            # Skip __pycache__ and hidden directories
            if "__pycache__" in str(py_file) or "/.git" in str(py_file):
                continue

            # Check if file is in approved location
            if not self.is_path_ssot_approved(py_file):
                non_approved_files.append(py_file)

        return non_approved_files

    def triage_file(self, file_path: Path) -> dict[str, Any]:
        """
        Determine where a file should go using FCA classification + CognitiveDispositionAgent.

        [DEDUP 2026-02-07] Uses FCA's classify_file() as primary routing source.
        Falls back to CognitiveDispositionAgent for files FCA can't classify confidently.

        Args:
            file_path: Path to the file to triage

        Returns:
            Dictionary with action, target_path, reason, confidence
        """
        # [DEDUP] Try FCA first for classification-based routing
        try:
            from agentic_core.L0_routing.seams.safety_reasoning_seam import (
                load_file_classification_agent,
            )

            FileClassificationAgent = load_file_classification_agent()
            fca = FileClassificationAgent(
                project_root=self.project_root,
                dry_run=True,
                validate_only=True,
            )
            file_type = fca.classify_file(file_path)
            correct_folder = fca._get_correct_folder_for_type(file_type)

            if correct_folder and file_type != "UTILITY":
                # Determine layer from current location
                try:
                    rel = file_path.relative_to(self.project_root / "agentic_core")
                    layer = rel.parts[0] if len(rel.parts) > 1 else "L5_safety"
                    target = f"agentic_core/{layer}/{correct_folder}"
                    return {
                        "action": "MOVE",
                        "target_path": target,
                        "reason": f"FCA classified as {file_type} -> {correct_folder}/",
                        "confidence": 0.85,
                    }
                except ValueError:
                    pass
        # guardian: allow-silent-swallow
        except Exception:
            pass

        # Fallback to CognitiveDispositionAgent
        cognitive = self._get_cognitive_agent()
        decision = cognitive.analyze_violation(file_path, "ORPHAN")

        return {
            "action": decision.action,
            "target_path": decision.target_path,
            "reason": decision.reason,
            "confidence": decision.confidence,
        }

    def move_file_to_ssot(
        self,
        source_path: Path,
        target_path: str,
    ) -> bool:
        """
        Move a file to its SSOT-approved location.

        Args:
            source_path: Current file path
            target_path: Target SSOT path (relative)

        Returns:
            True if move succeeded
        """
        if self.dry_run:
            Logger.info(f"[DRY RUN] Would move: {source_path} -> {target_path}")
            return True

        gatekeeper = self._get_archival_gatekeeper()

        # Ensure target directory exists
        full_target = self.project_root / target_path / source_path.name
        full_target.parent.mkdir(parents=True, exist_ok=True)

        # Move via gatekeeper (audited)
        success = gatekeeper.safe_move(source_path, full_target)

        if success:
            self.stats["files_moved"] += 1
            Logger.info(f"Moved: {source_path} -> {full_target}")
        else:
            self.stats["errors"] += 1
            Logger.error(f"Failed to move: {source_path}")

        return success

    def update_imports_for_moved_file(
        self,
        old_path: Path,
        new_path: Path,
    ) -> int:
        """
        Update all imports referencing a moved file.

        Args:
            old_path: Original file path
            new_path: New file path

        Returns:
            Number of files updated
        """
        # Convert paths to module names
        old_module = self._path_to_module(old_path)
        new_module = self._path_to_module(new_path)

        if not old_module or not new_module:
            return 0

        updated_count = 0

        # Scan all Python files for imports
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")

                # Check if file contains the old import
                if old_module not in content:
                    continue

                # Update imports
                new_content = self._update_imports_in_content(content, old_module, new_module)

                if new_content != content:
                    if self.dry_run:
                        Logger.info(f"[DRY RUN] Would update imports in: {py_file}")
                    else:
                        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
                        py_file.write_text(new_content, encoding="utf-8")
                        Logger.info(f"Updated imports in: {py_file}")

                    updated_count += 1
                    self.stats["imports_updated"] += 1

            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.warning(f"Failed to update imports in {py_file}: {e}")

        return updated_count

    def _path_to_module(self, path: Path) -> str | None:
        """Convert a file path to a Python module name."""
        try:
            rel_path = path.relative_to(self.project_root)
            # Remove .py extension and convert to module path
            module_parts = list(rel_path.parts)
            if module_parts[-1].endswith(".py"):
                module_parts[-1] = module_parts[-1][:-3]
            return ".".join(module_parts)
        except ValueError:
            return None

    def _update_imports_in_content(
        self,
        content: str,
        old_module: str,
        new_module: str,
    ) -> str:
        """
        Update import statements using AST-guided Regex.

        Uses AST to identify lines containing imports, then applies Regex
        ONLY to those lines to preserve formatting while ensuring safety.
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            Logger.warning("Syntax error in file, skipping import updates")
            return content

        # Identify lines that are definitely imports
        import_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                # Mark all lines covered by this node (including multi-line imports)
                for i in range(node.lineno, node.end_lineno + 1):
                    import_lines.add(i)

        lines = content.splitlines(keepends=True)
        new_lines = []

        # Regex patterns (compiled for performance)
        from_pattern = re.compile(rf"from\s+{re.escape(old_module)}(\.[^\s]+)?\s+import")
        import_pattern = re.compile(rf"import\s+{re.escape(old_module)}(\.[^\s]+)?")

        for i, line in enumerate(lines, 1):
            if i in import_lines:
                # Apply replacements ONLY on verified import lines
                # 1. Handle "from X import Y"
                line = from_pattern.sub(lambda m: f"from {new_module}{m.group(1) or ''} import", line)
                # 2. Handle "import X"
                # Ensure we don't match "import X" inside "from Z import X"
                # (which AST filtering helps with, but regex needs care)
                if not line.strip().startswith("from"):
                    line = import_pattern.sub(lambda m: f"import {new_module}{m.group(1) or ''}", line)
            new_lines.append(line)

        return "".join(new_lines)

    def delete_empty_folders(self, start_path: Path | None = None) -> int:
        """
        Delete empty non-SSOT-approved folders.

        Args:
            start_path: Starting path for deletion (default: agentic_core)

        Returns:
            Number of folders deleted
        """
        start_path = start_path or (self.project_root / "agentic_core")
        deleted_count = 0

        # Walk bottom-up to delete empty folders
        for dirpath, _dirnames, _filenames in os.walk(start_path, topdown=False):
            dir_path = Path(dirpath)

            # Skip approved folders
            if self.is_path_ssot_approved(dir_path):
                continue

            # Skip if not empty
            if any(dir_path.iterdir()):
                continue

            # Skip special folders
            if dir_path.name.startswith(".") or dir_path.name == "__pycache__":
                continue

            if self.dry_run:
                Logger.info(f"[DRY RUN] Would delete empty folder: {dir_path}")
            else:
                try:
                    dir_path.rmdir()
                    Logger.info(f"Deleted empty folder: {dir_path}")
                    deleted_count += 1
                    self.stats["folders_deleted"] += 1
                except OSError as e:
                    Logger.warning(f"Failed to delete folder {dir_path}: {e}")

        return deleted_count

    def cleanup_repository(self) -> dict[str, Any]:
        """
        Execute full SSOT folder cleanup.

        Returns:
            Summary of cleanup operations
        """
        Logger.info(f"Starting SSOT folder cleanup (dry_run={self.dry_run})")

        # Reset stats
        self.stats = {
            "files_scanned": 0,
            "files_moved": 0,
            "files_archived": 0,
            "imports_updated": 0,
            "folders_deleted": 0,
            "errors": 0,
        }

        # Step 1: Find non-approved files
        non_approved_files = self.find_non_approved_files()
        Logger.info(f"Found {len(non_approved_files)} files in non-approved locations")

        # Step 2: Triage and move each file
        move_plan = []
        for file_path in non_approved_files:
            triage = self.triage_file(file_path)

            if triage["action"] == "MOVE" and triage["target_path"]:
                move_plan.append(
                    {
                        "source": file_path,
                        "target": triage["target_path"],
                        "reason": triage["reason"],
                        "confidence": triage["confidence"],
                    },
                )
            elif triage["action"] == "ARCHIVE":
                move_plan.append(
                    {
                        "source": file_path,
                        "target": "archives/ssot_cleanup",
                        "reason": triage["reason"],
                        "confidence": triage["confidence"],
                        "archive": True,
                    },
                )
            else:
                Logger.info(f"Skipping {file_path}: {triage['action']} - {triage['reason']}")

        # Step 3: Execute moves
        for plan in move_plan:
            source = plan["source"]
            target = plan["target"]

            # Calculate new path
            new_path = self.project_root / target / source.name

            # Move file
            success = self.move_file_to_ssot(source, target)

            if success and not self.dry_run:
                # Update imports
                self.update_imports_for_moved_file(source, new_path)

                if plan.get("archive"):
                    self.stats["files_archived"] += 1

        # Step 4: Delete empty folders
        self.delete_empty_folders()

        # Build summary
        summary = {
            "dry_run": self.dry_run,
            "files_scanned": self.stats["files_scanned"],
            "non_approved_files": len(non_approved_files),
            "files_moved": self.stats["files_moved"],
            "files_archived": self.stats["files_archived"],
            "imports_updated": self.stats["imports_updated"],
            "folders_deleted": self.stats["folders_deleted"],
            "errors": self.stats["errors"],
            "move_plan": move_plan if self.dry_run else None,
        }

        Logger.info(f"SSOT cleanup complete: {summary}")
        return summary

    def preview_cleanup(self) -> dict[str, Any]:
        """
        Preview cleanup without making changes.

        Returns:
            Preview of what would be changed
        """
        original_dry_run = self.dry_run
        self.dry_run = True

        try:
            return self.cleanup_repository()
        finally:
            self.dry_run = original_dry_run

    def execute_cleanup(self) -> dict[str, Any]:
        """
        Execute cleanup with actual file changes.

        Returns:
            Summary of changes made
        """
        original_dry_run = self.dry_run
        self.dry_run = False

        try:
            return self.cleanup_repository()
        finally:
            self.dry_run = original_dry_run

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        self.dry_run = dry_run
        result = self.cleanup_repository()
        return {
            "violations_found": result.get("non_approved_files", 0),
            "violations_fixed": result.get("files_moved", 0),
            "errors": result.get("errors", 0),
            "skipped": 0,
        }

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal SSOT folder violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (orphan, misplaced)
                - path: Path to the violating file
                - target_path: Suggested target path

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        path = violation.get("path", "")
        target_path = violation.get("target_path", "")

        Logger.info(f"[SSOT_CLEANUP] Healing file location: {path}")

        if path and target_path:
            try:
                from pathlib import Path as PathLib

                source = PathLib(path)
                if source.exists():
                    success = self.move_file_to_ssot(source, target_path)
                    if success:
                        return {
                            "violations_fixed": 1,
                            "violations_found": 1,
                            "errors": 0,
                            "skipped": 0,
                        }
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"[SSOT_CLEANUP] Failed to heal: {e}")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
