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

# [SSOT IMPORT] Master Constitution is the absolute source of truth
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
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

# [MISSION AUDIT] Standardized logging for L4 Ledger consumption
logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)


class HierarchyAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Unified Hierarchy Management Agent
    
    Combines capabilities from HierarchyEnforcerAgent and HierarchyHealerAgent:
    
    1. Structure Creation:
       - Creates missing L2 (Layer) and L3 (Sub-territory) directories per SSOT Maps.
       
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
        # [SSOT] 'archives' is a protected folder in SOVEREIGN_EXCLUDED_FOLDERS
        self.archive_root = project_root / "archives" / "hierarchy_violations"
        
        if healing_enabled:
            self.archive_root.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # STRUCTURE CREATION
    # ========================================================================
    
    def create_missing_structure(self) -> Dict[str, Any]:
        """
        Create missing L2 (Layer) and L3 (Sub-territory) directories.
        
        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.
        
        Hierarchy: Project Root (L0) → agentic_core (L1) → Layer Folders (L2, e.g., L1_cognition) 
                   → Sub-territories (L3, e.g., thought_engine)
        
        Returns:
            Dict with counts of created directories and violations found
        """
        results = {"created": [], "errors": [], "violations_found": 0}
        
        Logger.info("HierarchyAgent: Enforcing L3 sub-territory subatomic structure per SSOT...")
        
        # agentic_core is L1; subfolders are L2 layers (L1_cognition, etc.)
        approved_layers_l2 = SOVEREIGN_REGISTRY.get("agentic_core", {}).get("subfolders", [])
        
        for layer_l2_name in approved_layers_l2:
            layer_l2_path = self.project_root / "agentic_core" / layer_l2_name
            if not layer_l2_path.exists():
                results["violations_found"] += 1
                Logger.warning(f"   [!] MISSING L2 LAYER: agentic_core/{layer_l2_name}")
                if self.healing_enabled:
                    self._create_dir_with_init(layer_l2_path, results, f"agentic_core/{layer_l2_name}")
                continue
            
            # L3 Sub-territories (thought_engine, guardrails, etc.)
            expected_territories_l3 = set(CORE_SUBFOLDER_MAP.get(layer_l2_name, []))
            if not expected_territories_l3:
                continue
            
            actual_l3 = {p.name for p in layer_l2_path.iterdir() if p.is_dir() and not p.name.startswith(".")}
            missing_l3 = expected_territories_l3 - actual_l3
            
            for territory_l3_name in missing_l3:
                results["violations_found"] += 1
                l3_path = layer_l2_path / territory_l3_name
                Logger.warning(f"   [!] MISSING L3 TERRITORY: agentic_core/{layer_l2_name}/{territory_l3_name}")
                if self.healing_enabled:
                    self._create_dir_with_init(l3_path, results, f"agentic_core/{layer_l2_name}/{territory_l3_name}")
        
        if results["violations_found"] > 0:
            Logger.info(f"HierarchyAgent: [STRUCTURE] Found {results['violations_found']} missing directories")
            if self.healing_enabled and results["created"]:
                Logger.info(f"HierarchyAgent: [STRUCTURE] Created {len(results['created'])} directories")
        
        return results

    def _create_dir_with_init(self, path: Path, results: Dict, rel_label: str) -> None:
        """Helper to create directory and touch __init__.py sentinel."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            (path / "__init__.py").touch()
            results["created"].append(rel_label)
            Logger.info(f"   [✓] CREATED: {rel_label}/")
        except Exception as e:
            Logger.error(f"   [!] FAILED: {rel_label}: {e}")
            results["errors"].append(f"Failed to create {rel_label}: {e}")

    # ========================================================================
    # FILE RELOCATION (from HierarchyHealerAgent)
    # ========================================================================
    
    def relocate_misplaced_files(self) -> Dict[str, Any]:
        """
        Relocate files from non-approved L1/L2 folders to approved locations.
        
        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.
        
        Returns:
            Dict with counts of relocated files, removed folders, and violations found
        """
        results = {"files_relocated": 0, "folders_removed": 0, "violations_found": 0, "errors": []}
        
        Logger.info("HierarchyAgent: Auditing misplaced files across sovereign layers...")
        
        # Approved L2 Layers (e.g., L5_safety)
        approved_layers_l2 = set(SOVEREIGN_REGISTRY.get("agentic_core", {}).get("subfolders", []))
        
        agentic_core_path = self.project_root / "agentic_core"
        if not agentic_core_path.exists():
            return results
        
        # Phase 1: Find all non-approved Layer (L2) folders
        actual_layers_l2 = {
            p.name for p in agentic_core_path.iterdir() 
            if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
        }
        non_approved_l2 = actual_layers_l2 - approved_layers_l2
        
        for bad_layer_l2 in non_approved_l2:
            bad_path = agentic_core_path / bad_layer_l2
            
            # Detection-First: Count all violations
            for py_file in bad_path.rglob("*.py"):
                if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                    continue
                results["violations_found"] += 1
                Logger.warning(f"   [!] MISPLACED FILE: {py_file.name} in illegal layer '{bad_layer_l2}'")
                
                if self.healing_enabled:
                    try:
                        target_layer_l2 = get_best_target_l1(bad_layer_l2, approved_layers_l2)
                        target_path = agentic_core_path / target_layer_l2
                        target_territory_l3 = get_best_target_l2(target_layer_l2, py_file.name)
                        final_target = target_path / target_territory_l3
                        final_target.mkdir(parents=True, exist_ok=True)
                        
                        dest = final_target / py_file.name
                        if not dest.exists():
                            shutil.move(str(py_file), str(dest))
                            Logger.info(f"      [✓] RELOCATED: {py_file.name} -> {target_layer_l2}/{target_territory_l3}/")
                            results["files_relocated"] += 1
                        else:
                            Logger.info(f"      [!] SKIP (exists): {py_file.name}")
                    except Exception as e:
                        results["errors"].append(f"{py_file.name}: {e}")
            
            # Try to remove empty folder tree (only if healing)
            if self.healing_enabled:
                try:
                    self._remove_empty_dirs(bad_path)
                    if not bad_path.exists():
                        Logger.info(f"      [✓] REMOVED empty folder: {bad_layer_l2}")
                        results["folders_removed"] += 1
                except Exception as e:
                    results["errors"].append(f"Remove {bad_layer_l2}: {e}")
        
        # Phase 2: Check L3 sub-territories within approved L2 Layers
        for layer_l2_name in approved_layers_l2:
            layer_l2_path = agentic_core_path / layer_l2_name
            if not layer_l2_path.exists():
                continue
            
            approved_territories_l3 = set(CORE_SUBFOLDER_MAP.get(layer_l2_name, []))
            if not approved_territories_l3:
                continue
            
            actual_territories_l3 = {
                p.name for p in layer_l2_path.iterdir() 
                if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
            }
            non_approved_l3 = actual_territories_l3 - approved_territories_l3
            
            for bad_territory_l3 in non_approved_l3:
                bad_path = layer_l2_path / bad_territory_l3
                
                # Detection-First: Count all violations
                for py_file in bad_path.rglob("*.py"):
                    if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                        continue
                    results["violations_found"] += 1
                    Logger.warning(f"   [!] MISPLACED FILE: {py_file.name} in illegal territory '{layer_l2_name}/{bad_territory_l3}'")
                    
                    if self.healing_enabled:
                        try:
                            target_territory_l3 = get_best_target_l2(layer_l2_name, bad_territory_l3)
                            target_path = layer_l2_path / target_territory_l3
                            target_path.mkdir(parents=True, exist_ok=True)
                            
                            dest = target_path / py_file.name
                            if not dest.exists():
                                shutil.move(str(py_file), str(dest))
                                Logger.info(f"      [✓] RELOCATED: {py_file.name} -> {layer_l2_name}/{target_territory_l3}/")
                                results["files_relocated"] += 1
                            else:
                                Logger.info(f"      [!] SKIP (exists): {py_file.name}")
                        except Exception as e:
                            results["errors"].append(f"{py_file.name}: {e}")
                
                # Try to remove empty folder tree (only if healing)
                if self.healing_enabled:
                    try:
                        self._remove_empty_dirs(bad_path)
                        if not bad_path.exists():
                            Logger.info(f"      [✓] REMOVED empty folder: {layer_l2_name}/{bad_territory_l3}")
                            results["folders_removed"] += 1
                    except Exception as e:
                        results["errors"].append(f"Remove {layer_l2_name}/{bad_territory_l3}: {e}")
        
        if results["violations_found"] > 0:
            Logger.info(f"HierarchyAgent: [RELOCATION] Found {results['violations_found']} misplaced files")
            if self.healing_enabled:
                Logger.info(f"HierarchyAgent: [RELOCATION] {results['files_relocated']} files relocated, {results['folders_removed']} folders removed")
        
        return results

    # ========================================================================
    # DEPTH ENFORCEMENT (from HierarchyEnforcerAgent)
    # ========================================================================
    
    def enforce_depth_rules(self) -> Dict[str, Any]:
        """
        Enforce depth rules and archive violations.
        
        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.
        
        Returns:
            Dict with counts of archived files by category and violations found
        """
        results = {
            "apps_archived": 0,
            "tests_archived": 0,
            "universal_archived": 0,
            "violations_found": 0,
            "errors": []
        }
        
        Logger.info("HierarchyAgent: Performing Depth-Precision audit (agentic_core=3, apps=2, tests=2)...")
        
        # Enforce apps_* depth
        apps_count = self._enforce_apps_depth()
        results["violations_found"] += apps_count
        if self.healing_enabled:
            results["apps_archived"] = apps_count
        
        # Enforce tests depth
        tests_count = self._enforce_tests_depth()
        results["violations_found"] += tests_count
        if self.healing_enabled:
            results["tests_archived"] = tests_count
        
        # Enforce universal depth (non-Python files)
        universal_count = self._enforce_universal_depth()
        results["violations_found"] += universal_count
        if self.healing_enabled:
            results["universal_archived"] = universal_count
        
        if results["violations_found"] > 0:
            Logger.info(f"HierarchyAgent: [DEPTH] Found {results['violations_found']} depth violations")
            if self.healing_enabled:
                total_archived = results["apps_archived"] + results["tests_archived"] + results["universal_archived"]
                Logger.info(f"HierarchyAgent: [DEPTH] Archived {total_archived} files (apps: {results['apps_archived']}, tests: {results['tests_archived']}, universal: {results['universal_archived']})")
        
        return results
    
    def _enforce_apps_depth(self) -> int:
        """Enforce apps_* depth rule (depth 2). Detection-First."""
        apps_exact_depth = SOVEREIGN_REGISTRY.get("apps_rg", {}).get("depth", 2)
        archived = 0
        violations = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            rel = file_path.relative_to(self.project_root)
            if not rel.parts[0].startswith("apps_"):
                continue
            
            depth = len(rel.parts)
            if depth != apps_exact_depth:
                violations += 1
                Logger.warning(f"   [!] DEPTH DRIFT: {rel} is depth {depth}, expected {apps_exact_depth}")
                
                if self.healing_enabled:
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
        
        return violations if not self.healing_enabled else archived
    
    def _enforce_tests_depth(self) -> int:
        """Enforce tests depth rule (depth 2). Detection-First."""
        tests_exact_depth = SOVEREIGN_REGISTRY.get("tests", {}).get("depth", 2)
        archived = 0
        violations = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_dir() or any(part.startswith(".") for part in file_path.parts):
                continue
            
            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] != "tests":
                continue
            
            depth = len(rel.parts)
            if depth != tests_exact_depth:
                violations += 1
                Logger.warning(f"   [!] DEPTH DRIFT: {rel} is depth {depth}, expected {tests_exact_depth}")
                
                if self.healing_enabled:
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
        
        return violations if not self.healing_enabled else archived
    
    def _enforce_universal_depth(self) -> int:
        """Enforce universal depth for non-Python files in agentic_core (depth 3). Detection-First."""
        agentic_core_exact_depth = SOVEREIGN_REGISTRY.get("agentic_core", {}).get("depth", 3)
        archived = 0
        violations = 0
        
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
                    violations += 1
                    Logger.warning(f"   [!] DEPTH DRIFT: {rel} is depth {depth}, expected {agentic_core_exact_depth}")
                    
                    if self.healing_enabled:
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
        
        return violations if not self.healing_enabled else archived

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
        
        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.
        
        Returns:
            Dict with purge count, violations found, and errors
        """
        import os
        
        purged_count = 0
        violations_found = 0
        errors = []
        
        # [SSOT] Dynamically pull roots from registry
        allowed_roots = set(SOVEREIGN_REGISTRY.keys())
        
        Logger.info("HierarchyAgent: Scanning for orphaned files outside sovereign territory...")
        
        orphaned_files = []
        # [SCALABILITY] Increased budget for mature repositories
        MAX_PURGE_SCAN = 5000
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
                    violations_found += 1
                    Logger.warning(f"      [⚠]  ORPHANED IN {parts[0].upper()}: {rel_path}")
                elif len(parts) == 1:
                    violations_found += 1
                    Logger.warning(f"      [⚠]  ORPHANED ROOT FILE: {file_path.name}")
                else:
                    continue
                
                if self.healing_enabled:
                    # Ensure purge artifacts are ignored
                    self._update_gitignore_for_purge()
                    
                    backup_path = file_path.with_name(file_path.name + ".archived")
                    if not backup_path.exists():
                        file_path.rename(backup_path)
                        Logger.info(f"      [✓] ARCHIVED & PURGED: {file_path.name}")
                    else:
                        file_path.unlink()
                        Logger.info(f"      [✓] PURGED (backup exists): {file_path.name}")
                    purged_count += 1
            except Exception as e:
                errors.append(f"Failed to purge {file_path}: {e}")
        
        if violations_found > 0:
            Logger.info(f"HierarchyAgent: [PURGE] Found {violations_found} orphaned files")
            if self.healing_enabled and purged_count > 0:
                Logger.info(f"HierarchyAgent: [PURGE] {purged_count} orphaned files archived/purged")
        
        return {"purged": purged_count, "violations_found": violations_found, "errors": errors}
    
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
        total_violations = (
            results["structure"].get("violations_found", 0) +
            results["relocation"].get("violations_found", 0) +
            results["depth"].get("violations_found", 0) +
            results["purge"].get("violations_found", 0)
        )
        
        results["summary"] = {
            "violations_found": total_violations,
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
        print(f"Total violations found: {results['summary']['violations_found']}")
        if self.healing_enabled:
            print(f"Directories created: {results['summary']['directories_created']}")
            print(f"Files relocated: {results['summary']['files_relocated']}")
            print(f"Folders removed: {results['summary']['folders_removed']}")
            print(f"Depth violations archived: {results['summary']['depth_violations_archived']}")
            print(f"Orphans purged: {results['summary']['orphans_purged']}")
            print(f"\nTotal actions taken: {results['summary']['total_actions']}")
        else:
            print(f"[DRY-RUN] No changes were made - run with healing_enabled=True to fix violations")
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
