from __future__ import annotations
"""
HierarchyAgent - Unified Hierarchy Management
Consolidates HierarchyEnforcerAgent and HierarchyHealerAgent into a single agent.

PURPOSE: Complete hierarchy management including:
- L2/L3 structure creation (from Enforcer)
- File relocation to approved folders (from Healer)
- Depth enforcement and archiving (from Enforcer)
- Empty folder cleanup (from Healer)
- Orphaned file purging (from Healer)

LOCATION: agentic_core/L5_safety/guardrails/ (SSOT-compliant)
"""

import shutil
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


class HierarchyAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Unified Hierarchy Management Agent
    
    Combines capabilities from HierarchyEnforcerAgent and HierarchyHealerAgent:
    
    1. Structure Creation:
       - Creates missing L2 (Layer) and L3 (Sub-territory) directories per 
         CORE_SUBFOLDER_MAP to maintain Depth-3 compliance.
       
    2. File Relocation (from Healer):
       - Moves files from non-approved folders to approved locations
       
    3. Depth Enforcement (from Enforcer):
       - Archives files violating depth rules (apps_*, tests, agentic_core)
       
    4. Folder Cleanup (from Healer):
       - Removes empty non-approved directories
       
    5. Orphan Purging (from Healer):
       - Archives orphaned files from forbidden locations
    """
    
    def __init__(self, project_root: Path, healing_enabled: bool = True, ctx: Any = None) -> None:
        """
        Initialize the unified hierarchy agent.
        
        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled (dry-run if False)
            ctx: Optional context for reporting
        """
        self.project_root = project_root.resolve()
        self.healing_enabled = healing_enabled
        self.ctx = ctx
        self.protected_folders = SOVEREIGN_EXCLUDED_FOLDERS
        # Fallback to hardcoded 'archives' per SOVEREIGN_EXCLUDED_FOLDERS
        self.archive_root = project_root / "archives" / "hierarchy_violations"
        
        if healing_enabled:
            self.archive_root.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # STRUCTURE CREATION
    # ========================================================================
    
    def create_missing_structure(self) -> Dict[str, Any]:
        """
        Create missing L2 (Layer) and L3 (Sub-territory) directories.
        
        Hierarchy: Project Root (L0) → agentic_core (L1) → Layer Folders (L2, e.g., L1_cognition) 
                   → Sub-territories (L3, e.g., thought_engine)
        
        Returns:
            Dict with counts of created directories
        """
        results = {"created": [], "errors": []}
        
        if not self.healing_enabled:
            print("   [DRY-RUN] Structure creation disabled")
            return results
        
        print("\n[*] HIERARCHY: Enforcing L3 sub-territory subatomic structure...")
        
        l2_layers = SOVEREIGN_REGISTRY["agentic_core"]["subfolders"]
        
        for l2_name in l2_layers:
            l2_path = self.project_root / "agentic_core" / l2_name
            if not l2_path.exists():
                continue
            
            # Drill down to L3 sub-territories
            expected_l3 = set(CORE_SUBFOLDER_MAP.get(l2_name, []))
            if not expected_l3:
                continue
            
            actual_l3 = {p.name for p in l2_path.iterdir() if p.is_dir() and not p.name.startswith(".")}
            missing_l3 = expected_l3 - actual_l3
            
            for l3_name in missing_l3:
                l3_path = l2_path / l3_name
                self._create_dir_with_init(l3_path, results, f"agentic_core/{l2_name}/{l3_name}")
        
        if results["created"]:
            print(f"   [STRUCTURE] Created {len(results['created'])} missing directories")
        
        return results

    def _create_dir_with_init(self, path: Path, results: Dict, rel_label: str) -> None:
        """Helper to create directory and touch __init__.py sentinel."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            (path / "__init__.py").touch()
            results["created"].append(rel_label)
            print(f"      [✓] CREATED: {rel_label}/")
        except Exception as e:
            results["errors"].append(f"Failed to create {rel_label}: {e}")

    # ========================================================================
    # FILE RELOCATION (from HierarchyHealerAgent)
    # ========================================================================
    
    def relocate_misplaced_files(self) -> Dict[str, Any]:
        """
        Relocate files from non-approved L1/L2 folders to approved locations.
        
        Returns:
            Dict with counts of relocated files and removed folders
        """
        results = {"files_relocated": 0, "folders_removed": 0, "errors": []}
        
        if not self.healing_enabled:
            print("   [DRY-RUN] File relocation disabled")
            return results
        
        print("\n[*] HIERARCHY: Relocating files from non-approved folders...")
        
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
            bad_path = agentic_core_path / bad_l1
            print(f"   [!] Non-approved L1 folder: {bad_l1}")
            
            # Find best target based on folder name heuristics
            target_l1 = get_best_target_l1(bad_l1, approved_l1)
            target_path = agentic_core_path / target_l1
            
            # Relocate all files from non-approved folder
            for py_file in bad_path.rglob("*.py"):
                if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                    continue
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
            
            # Try to remove empty folder tree
            try:
                self._remove_empty_dirs(bad_path)
                if not bad_path.exists():
                    print(f"      [✓] REMOVED empty folder: {bad_l1}")
                    results["folders_removed"] += 1
            except Exception as e:
                results["errors"].append(f"Remove {bad_l1}: {e}")
        
        # Phase 2: Check L2 subfolders within approved L1 folders
        for l1_name in approved_l1:
            l1_path = agentic_core_path / l1_name
            if not l1_path.exists():
                continue
            
            approved_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
            if not approved_l2:
                continue
            
            actual_l2 = {
                p.name for p in l1_path.iterdir() 
                if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
            }
            non_approved_l2 = actual_l2 - approved_l2
            
            for bad_l2 in non_approved_l2:
                bad_path = l1_path / bad_l2
                print(f"   [!] Non-approved L2 folder: {l1_name}/{bad_l2}")
                
                target_l2 = get_best_target_l2(l1_name, bad_l2)
                target_path = l1_path / target_l2
                target_path.mkdir(parents=True, exist_ok=True)
                
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
                
                try:
                    self._remove_empty_dirs(bad_path)
                    if not bad_path.exists():
                        print(f"      [✓] REMOVED empty folder: {l1_name}/{bad_l2}")
                        results["folders_removed"] += 1
                except Exception as e:
                    results["errors"].append(f"Remove {l1_name}/{bad_l2}: {e}")
        
        if results["files_relocated"] or results["folders_removed"]:
            print(f"   [RELOCATION] {results['files_relocated']} files relocated, {results['folders_removed']} folders removed")
        
        return results

    # ========================================================================
    # DEPTH ENFORCEMENT (from HierarchyEnforcerAgent)
    # ========================================================================
    
    def enforce_depth_rules(self) -> Dict[str, Any]:
        """
        Enforce depth rules and archive violations.
        
        Returns:
            Dict with counts of archived files by category
        """
        results = {
            "apps_archived": 0,
            "tests_archived": 0,
            "universal_archived": 0,
            "errors": []
        }
        
        if not self.healing_enabled:
            print("   [DRY-RUN] Depth enforcement disabled")
            return results
        
        print("\n[*] HIERARCHY: Enforcing depth rules...")
        
        # Enforce apps_* depth
        apps_count = self._enforce_apps_depth()
        results["apps_archived"] = apps_count
        
        # Enforce tests depth
        tests_count = self._enforce_tests_depth()
        results["tests_archived"] = tests_count
        
        # Enforce universal depth (non-Python files)
        universal_count = self._enforce_universal_depth()
        results["universal_archived"] = universal_count
        
        total = apps_count + tests_count + universal_count
        if total > 0:
            print(f"   [DEPTH] Archived {total} files (apps: {apps_count}, tests: {tests_count}, universal: {universal_count})")
        
        return results
    
    def _enforce_apps_depth(self) -> int:
        """Enforce apps_* depth rule (depth 2)."""
        apps_exact_depth = SOVEREIGN_REGISTRY["apps_rg"]["depth"]
        archived = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            rel = file_path.relative_to(self.project_root)
            if not rel.parts[0].startswith("apps_"):
                continue
            
            depth = len(rel.parts)
            if depth != apps_exact_depth:
                try:
                    archive_path = self.archive_root / "apps_depth" / rel
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    header = f"# APPS DEPTH VIOLATION — {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    header += f"# {rel} was depth {depth}, but apps_* MUST be exactly {apps_exact_depth}.\n\n"
                    
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    archive_path.write_text(header + content, encoding="utf-8")
                    file_path.unlink()
                    archived += 1
                except Exception:
                    pass
        
        return archived
    
    def _enforce_tests_depth(self) -> int:
        """Enforce tests depth rule (depth 2)."""
        tests_exact_depth = SOVEREIGN_REGISTRY["tests"]["depth"]
        archived = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] != "tests":
                continue
            
            depth = len(rel.parts)
            if depth != tests_exact_depth:
                try:
                    archive_path = self.archive_root / "tests_depth" / rel
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    header = f"# TESTS DEPTH VIOLATION — {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    header += f"# {rel} was depth {depth}, but tests MUST be exactly {tests_exact_depth}.\n\n"
                    
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    archive_path.write_text(header + content, encoding="utf-8")
                    file_path.unlink()
                    archived += 1
                except Exception:
                    pass
        
        return archived
    
    def _enforce_universal_depth(self) -> int:
        """Enforce universal depth for non-Python files in agentic_core (depth 3)."""
        agentic_core_exact_depth = SOVEREIGN_REGISTRY["agentic_core"]["depth"]
        archived = 0
        
        target_exts = {".json", ".md", ".yaml", ".yml", ".toml", ".txt"}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            if file_path.suffix.lower() not in target_exts:
                continue
            
            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] == "agentic_core":
                depth = len(rel.parts)
                if depth != agentic_core_exact_depth:
                    try:
                        archive_path = self.archive_root / "universal_depth" / rel
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        header = f"# UNIVERSAL DEPTH VIOLATION — {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        header += f"# {rel} was depth {depth}, but MUST be {agentic_core_exact_depth}.\n\n"
                        
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        archive_path.write_text(header + content, encoding="utf-8")
                        file_path.unlink()
                        archived += 1
                    except Exception:
                        pass
        
        return archived

    # ========================================================================
    # FOLDER CLEANUP (from HierarchyHealerAgent)
    # ========================================================================
    
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
            
            try:
                path.rmdir()
            except OSError:
                pass

    # ========================================================================
    # ORPHAN PURGING (from HierarchyHealerAgent)
    # ========================================================================
    
    def purge_orphaned_files(self) -> Dict[str, Any]:
        """
        Purge code and assets in forbidden or root-level locations.
        
        Returns:
            Dict with purge count and errors
        """
        import os
        
        if not self.healing_enabled:
            print("   [DRY-RUN] Orphan purging disabled")
            return {"purged": 0, "errors": []}
        
        # Ensure purge artifacts are ignored
        self._update_gitignore_for_purge()
        
        purged_count = 0
        errors = []
        
        allowed_roots = {"agentic_core", "apps_shared", "apps_rg", "apps_lic", "tests"}
        
        print("\n[*] HIERARCHY: Scanning for orphaned files...")
        
        orphaned_files = []
        MAX_PURGE_SCAN = 500
        scan_count = 0
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.protected_folders and not d.startswith('.')]
            for file in files:
                if scan_count >= MAX_PURGE_SCAN:
                    break
                orphaned_files.append(Path(root) / file)
                scan_count += 1
            if scan_count >= MAX_PURGE_SCAN:
                break
        
        seen = set()
        for file_path in orphaned_files:
            if file_path in seen or not file_path.is_file():
                continue
            seen.add(file_path)
            
            try:
                rel_path = file_path.relative_to(self.project_root)
                parts = rel_path.parts
                
                if parts and parts[0] in allowed_roots:
                    continue
                
                if len(parts) == 1 and file_path.name in ROOT_PROTECTED_FILES:
                    continue
                
                archive_markers = ('.archived', '.backup', '.old', '.copy')
                if any(file_path.name.lower().endswith(marker) for marker in archive_markers):
                    continue
                if any(marker in file_path.name.lower() for marker in archive_markers):
                    continue
                
                if parts and parts[0] in self.protected_folders:
                    if parts[0] in {"data", "archives"}:
                        continue
                    print(f"      [⚠]  ORPHANED IN {parts[0].upper()}: {rel_path}")
                elif len(parts) == 1:
                    print(f"      [⚠]  ORPHANED ROOT FILE: {file_path.name}")
                else:
                    continue
                
                backup_path = file_path.with_name(file_path.name + ".archived")
                if not backup_path.exists():
                    file_path.rename(backup_path)
                    print(f"      [✓] ARCHIVED & PURGED: {file_path.name}")
                else:
                    file_path.unlink()
                    print(f"      [✓] PURGED (backup exists): {file_path.name}")
                purged_count += 1
            except Exception as e:
                errors.append(f"Failed to purge {file_path}: {e}")
        
        if purged_count > 0:
            print(f"   [PURGE] {purged_count} orphaned files archived/purged")
        
        return {"purged": purged_count, "errors": errors}
    
    def _update_gitignore_for_purge(self) -> None:
        """Ensure purge artifacts (*.archived) are permanently ignored by git."""
        if not self.healing_enabled:
            return
        
        gitignore_path = self.project_root / ".gitignore"
        purge_pattern = "*.archived"
        marker_comment = "# [HIERARCHY AGENT] Purge artifacts — do not remove"
        dated_comment = f"# Auto-generated on {time.strftime('%Y-%m-%d')} by HierarchyAgent"
        
        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                lines = content.splitlines()
            else:
                lines = []
            
            pattern_exists = any(purge_pattern in line for line in lines)
            marker_exists = any(marker_comment in line for line in lines)
            
            if pattern_exists or marker_exists:
                return
            
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
        except Exception:
            pass

    # ========================================================================
    # UNIFIED INTERFACE
    # ========================================================================
    
    def heal_hierarchy(self, 
                      create_structure: bool = True,
                      relocate_files: bool = True,
                      enforce_depth: bool = True,
                      purge_orphans: bool = True) -> Dict[str, Any]:
        """
        Unified hierarchy healing with granular control.
        
        Args:
            create_structure: Create missing L2/L3 directories
            relocate_files: Relocate files from non-approved folders
            enforce_depth: Enforce depth rules and archive violations
            purge_orphans: Purge orphaned files
            
        Returns:
            Comprehensive results dictionary
        """
        print("=" * 80)
        print(f"HIERARCHY AGENT - {'DRY RUN' if not self.healing_enabled else 'ACTIVE'}")
        print("=" * 80)
        
        results = {
            "structure": {},
            "relocation": {},
            "depth": {},
            "purge": {},
            "summary": {}
        }
        
        if create_structure:
            results["structure"] = self.create_missing_structure()
        
        if relocate_files:
            results["relocation"] = self.relocate_misplaced_files()
        
        if enforce_depth:
            results["depth"] = self.enforce_depth_rules()
        
        if purge_orphans:
            results["purge"] = self.purge_orphaned_files()
        
        # Summary
        results["summary"] = {
            "directories_created": len(results["structure"].get("created", [])),
            "files_relocated": results["relocation"].get("files_relocated", 0),
            "folders_removed": results["relocation"].get("folders_removed", 0),
            "depth_violations_archived": (
                results["depth"].get("apps_archived", 0) +
                results["depth"].get("tests_archived", 0) +
                results["depth"].get("universal_archived", 0)
            ),
            "orphans_purged": results["purge"].get("purged", 0),
            "total_actions": 0
        }
        
        results["summary"]["total_actions"] = (
            results["summary"]["directories_created"] +
            results["summary"]["files_relocated"] +
            results["summary"]["folders_removed"] +
            results["summary"]["depth_violations_archived"] +
            results["summary"]["orphans_purged"]
        )
        
        print("\n" + "=" * 80)
        print("HIERARCHY HEALING SUMMARY")
        print("=" * 80)
        print(f"Directories created: {results['summary']['directories_created']}")
        print(f"Files relocated: {results['summary']['files_relocated']}")
        print(f"Folders removed: {results['summary']['folders_removed']}")
        print(f"Depth violations archived: {results['summary']['depth_violations_archived']}")
        print(f"Orphans purged: {results['summary']['orphans_purged']}")
        print(f"\nTotal actions: {results['summary']['total_actions']}")
        print("=" * 80)
        
        return results
    
    @timeout(300)
    def heal_repository(self, dry_run: bool = True, **kwargs) -> Dict[str, Any]:
        """Repository healing with parent chain invocation."""
        # Set healing_enabled based on dry_run
        original_healing = self.healing_enabled
        self.healing_enabled = not dry_run
        
        try:
            result = self.heal_hierarchy(**kwargs)
            parent_result = super().heal_repository(dry_run=dry_run, **kwargs)
            return {"hierarchy": result, "parent": parent_result}
        finally:
            self.healing_enabled = original_healing
