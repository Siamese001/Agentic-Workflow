from __future__ import annotations
# HierarchyHealerAgent.py
# L5 Hierarchy Healing Agent
# PURPOSE: Heals hierarchy violations by relocating files and removing empty folders
# LOCATION: agentic_core/L5_safety/guardrails/ (SSOT-compliant)

import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Set

from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    SOVEREIGN_EXCLUDED_FOLDERS,
    ROOT_PROTECTED_FILES,
    ALLOWED_DUPLICATE_FILENAMES,
)
from agentic_core.utils.general_helpers.mission_utils import (
    get_best_target_l1,
    get_best_target_l2,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HierarchyHealerAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    L5 Hierarchy Healer Agent
    
    Heals hierarchy violations by:
    1. Relocating files from non-approved subfolders to the nearest approved subfolder
    2. Removing empty non-approved subfolders after relocation
    3. Purging orphaned files from forbidden or root-level locations
    """
    
    def __init__(self, project_root: Path, healing_enabled: bool = True) -> None:
        """
        Initialize the hierarchy healer.
        
        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled
        """
        self.project_root = project_root.resolve()
        self.healing_enabled = healing_enabled
        self.protected_folders = SOVEREIGN_EXCLUDED_FOLDERS

    def heal_hierarchy_violations(self) -> Dict[str, Any]:
        """
        Heal hierarchy violations by relocating files and removing empty folders.
        
        Returns:
            Dict with counts of relocated files and removed folders
        """
        results = {"files_relocated": 0, "folders_removed": 0, "errors": []}
        
        if not self.healing_enabled:
            print("   [INFO] Hierarchy healing disabled (healing_enabled=False)")
            return results
        
        print("\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[*] L6 HIERARCHY ENFORCEMENT: Healing non-approved subfolders...")
        
        # Get approved L1 folders for agentic_core from SSOT
        approved_l1 = set(SOVEREIGN_REGISTRY["agentic_core"]["subfolders"])
        
        agentic_core_path = self.project_root / "agentic_core"
        if not agentic_core_path.exists():
            return results
        
        # Phase 1: Find all non-approved L1 folders
        actual_l1 = {
            p.name for p in agentic_core_path.iterdir() 
            if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
        }
        non_approved_l1 = actual_l1 - approved_l1
        
        for bad_l1 in non_approved_l1:
            self._heal_l1_folder(bad_l1, agentic_core_path, approved_l1, results)
        
        # Phase 2: Check L2 subfolders within approved L1 folders
        for l1_name in approved_l1:
            self._heal_l2_folders(l1_name, agentic_core_path, results)
        
        print(f"   [HIERARCHY HEALING COMPLETE] {results['files_relocated']} files relocated, {results['folders_removed']} folders removed")
        if results["errors"]:
            print(f"   [!] {len(results['errors'])} errors occurred during healing")
        
        return results

    def _heal_l1_folder(self, bad_l1: str, agentic_core_path: Path, approved_l1: set, results: Dict[str, Any]) -> None:
        """Heal non-approved L1 folder by relocating files and removing empty folder."""
        bad_path = agentic_core_path / bad_l1
        print(f"   [!] Non-approved L1 folder: {bad_l1}")
        
        # Find best target based on folder name heuristics
        target_l1 = get_best_target_l1(bad_l1, approved_l1)
        target_path = agentic_core_path / target_l1
        
        # Relocate all files from non-approved folder
        for py_file in bad_path.rglob("*.py"):
            if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                continue
            self._relocate_file_to_l1(py_file, target_l1, target_path, results)
        
        # Try to remove empty folder tree
        self._cleanup_empty_folder(bad_path, bad_l1, results)
    
    def _relocate_file_to_l1(self, py_file: Path, target_l1: str, target_path: Path, results: Dict[str, Any]) -> None:
        """Relocate a single file to approved L1 folder."""
        try:
            target_l2 = get_best_target_l2(target_l1, py_file.name)
            final_target = target_path / target_l2
            final_target.mkdir(parents=True, exist_ok=True)
            
            dest = final_target / py_file.name
            if not dest.exists():
                shutil.move(str(py_file), str(dest))
                print(f"      [✓] RELOCATED: {py_file.name} -> {target_l1}/{target_l2}/")
                results["files_relocated"] += 1
            else:
                print(f"      [!] SKIP (exists): {py_file.name}")
        except Exception as e:
            results["errors"].append(f"{py_file.name}: {e}")
    
    def _heal_l2_folders(self, l1_name: str, agentic_core_path: Path, results: Dict[str, Any]) -> None:
        """Heal non-approved L2 folders within an approved L1 folder."""
        l1_path = agentic_core_path / l1_name
        if not l1_path.exists():
            return
        
        approved_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
        if not approved_l2:
            return  # No L2 enforcement for this L1
        
        actual_l2 = {
            p.name for p in l1_path.iterdir() 
            if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
        }
        non_approved_l2 = actual_l2 - approved_l2
        
        for bad_l2 in non_approved_l2:
            self._heal_single_l2_folder(l1_name, l1_path, bad_l2, results)
    
    def _heal_single_l2_folder(self, l1_name: str, l1_path: Path, bad_l2: str, results: Dict[str, Any]) -> None:
        """Heal a single non-approved L2 folder."""
        bad_path = l1_path / bad_l2
        print(f"   [!] Non-approved L2 folder: {l1_name}/{bad_l2}")
        
        # Find best target L2 folder
        target_l2 = get_best_target_l2(l1_name, bad_l2)
        target_path = l1_path / target_l2
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Relocate all files
        for py_file in bad_path.rglob("*.py"):
            if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                continue
            try:
                dest = target_path / py_file.name
                if not dest.exists():
                    shutil.move(str(py_file), str(dest))
                    print(f"      [✓] RELOCATED: {py_file.name} -> {l1_name}/{target_l2}/")
                    results["files_relocated"] += 1
                else:
                    print(f"      [!] SKIP (exists): {py_file.name}")
            except Exception as e:
                results["errors"].append(f"{py_file.name}: {e}")
        
        # Try to remove empty folder
        self._cleanup_empty_folder(bad_path, f"{l1_name}/{bad_l2}", results)
    
    def _cleanup_empty_folder(self, folder_path: Path, folder_label: str, results: Dict[str, Any]) -> None:
        """Remove empty folder tree after relocation."""
        try:
            self._remove_empty_dirs(folder_path)
            if not folder_path.exists():
                print(f"      [✓] REMOVED empty folder: {folder_label}")
                results["folders_removed"] += 1
        except Exception as e:
            results["errors"].append(f"Remove {folder_label}: {e}")

    def _remove_empty_dirs(self, path: Path) -> None:
        """
        Recursively remove empty directories.
        
        Args:
            path: Directory path to check and potentially remove
        """
        if not path.is_dir():
            return
        
        # First, recurse into subdirectories
        for child in path.iterdir():
            if child.is_dir():
                self._remove_empty_dirs(child)
        
        # Then check if this directory is now empty
        remaining = [
            p for p in path.iterdir() 
            if p.name not in {"__pycache__", "__init__.py", ".gitkeep"}
            and not p.name.startswith(".")
        ]
        
        if not remaining:
            # Aggressively purge empty shell
            init_file = path / "__init__.py"
            if init_file.exists():
                init_file.unlink(missing_ok=True)
            
            pycache = path / "__pycache__"
            if pycache.exists():
                shutil.rmtree(pycache, ignore_errors=True)
            
            gitkeep = path / ".gitkeep"
            if gitkeep.exists():
                gitkeep.unlink()
                print(f"      [✓] Removed .gitkeep sentinel: {gitkeep}")
            
            try:
                path.rmdir()
                print(f"      [✓] PURGED ghost folder: {path}")
            except OSError:
                if list(path.iterdir()):
                    print(f"   [!] Failed to remove {path} - still contains files after purge")
                else:
                    print(f"   [!] rmdir failed on empty {path} - Permission/filesystem issue")

    def update_gitignore_for_purge(self) -> None:
        """
        Ensure purge artifacts (*.archived) are permanently ignored by git.
        Idempotently inserts a clear, dated, commented entry in .gitignore.
        """
        if not self.healing_enabled:
            return

        gitignore_path = self.project_root / ".gitignore"
        purge_pattern = "*.archived"
        marker_comment = "# [CANON VALIDATOR] Sovereign purge artifacts — do not remove"
        dated_comment = f"# Auto-generated on {time.strftime('%Y-%m-%d')} by canon validator"

        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                lines = content.splitlines()
            else:
                lines = []
                print(f"   [INFO] Creating new .gitignore at {gitignore_path}")

            # Check if pattern or marker already exists
            pattern_exists = any(purge_pattern in line for line in lines)
            marker_exists = any(marker_comment in line for line in lines)

            if pattern_exists or marker_exists:
                print(f"   [OK] .gitignore already configured for purge artifacts")
                return

            # Find first non-comment line for strategic insertion
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    insert_idx = i
                    break
                if i > 50:
                    break

            new_lines = lines[:insert_idx] + ["", marker_comment, dated_comment, purge_pattern, ""] + lines[insert_idx:]
            new_content = "\n".join(new_lines).rstrip() + "\n"

            gitignore_path.write_text(new_content, encoding="utf-8")
            print(f"   [✓] .gitignore hardened: added {purge_pattern} with sovereign marker")
        except Exception as e:
            print(f"   [!] Failed to update .gitignore: {e}")

    def purge_orphaned_files(self) -> Dict[str, Any]:
        """
        Purge code and assets in forbidden or root-level locations.
        Only files with no legal home are archived.
        
        Returns:
            Dict with purge count and errors
        """
        import os
        
        if not self.healing_enabled:
            return {"purged": 0, "errors": []}

        # Ensure purge artifacts are ignored
        self.update_gitignore_for_purge()

        purged_count = 0
        errors = []

        # Define allowed sovereign roots from SSOT
        allowed_roots = {"agentic_core", "apps_shared", "apps_rg", "apps_lic", "tests"}

        print("   [L6 PURGE] Scanning for orphaned assets outside sovereign territory...")

        orphaned_files = []
        MAX_PURGE_SCAN = 500
        scan_count = 0
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip protected folders entirely
            dirs[:] = [d for d in dirs if d not in self.protected_folders and not d.startswith('.')]
            for file in files:
                if scan_count >= MAX_PURGE_SCAN:
                    break
                orphaned_files.append(Path(root) / file)
                scan_count += 1
            if scan_count >= MAX_PURGE_SCAN:
                print(f"   [INFO] Purge scan limit reached ({MAX_PURGE_SCAN} files)")
                break

        seen = set()
        for file_path in orphaned_files:
            if file_path in seen or not file_path.is_file():
                continue
            seen.add(file_path)

            try:
                rel_path = file_path.relative_to(self.project_root)
                parts = rel_path.parts

                # Skip if in allowed sovereign root
                if parts and parts[0] in allowed_roots:
                    continue

                # Skip explicitly protected root files
                if len(parts) == 1 and file_path.name in ROOT_PROTECTED_FILES:
                    continue

                # [BUG FIX 2025-12-31] Skip files that are already archived
                # Prevents infinite loop: file.json → file.json.archived → file.json.archived.archived...
                archive_markers = ('.archived', '.backup', '.old', '.copy')
                if any(file_path.name.lower().endswith(marker) for marker in archive_markers):
                    continue
                if any(marker in file_path.name.lower() for marker in archive_markers):
                    # Also catch files with markers in the middle (e.g., file.archived.json)
                    continue

                # Skip if in protected_folders
                if parts and parts[0] in self.protected_folders:
                    if parts[0] in {"data", "archives"}:
                        continue
                    print(f"      [⚠]  ORPHANED IN {parts[0].upper()}: {rel_path}")
                elif len(parts) == 1:
                    print(f"      [⚠]  ORPHANED ROOT FILE: {file_path.name}")
                else:
                    continue

                # Archive the file
                backup_path = file_path.with_name(file_path.name + ".archived")
                if not backup_path.exists():
                    file_path.rename(backup_path)
                    print(f"      [✓] ARCHIVED & PURGED: {file_path.name} → {backup_path.name}")
                else:
                    file_path.unlink()
                    print(f"      [✓] PURGED (backup exists): {file_path.name}")
                purged_count += 1
            except Exception as e:
                errors.append(f"Failed to purge {file_path}: {e}")

        print(f"   [L6 PURGE] Complete: {purged_count} orphaned files archived/purged")
        return {"purged": purged_count, "errors": errors}

    def heal_repository(self, dry_run: bool = True, **kwargs) -> Dict[str, Any]:
        """Repository healing with parent chain invocation."""
        result = super().heal_repository(dry_run=dry_run, **kwargs)
        return {"healed": 0, "skipped": 0, "parent": result}
