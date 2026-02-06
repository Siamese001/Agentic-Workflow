# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: memory, orchestrator, prompt, state, workflow
from __future__ import annotations

# ruff: noqa: E501, E402, F811
from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

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

import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any

from agentic_core.base_agents.timeout_decorator import timeout
from agentic_core.L5_safety.core.archival_gatekeeper_config import ArchivalGatekeeper
from agentic_core.L5_safety.gravity.mission_utils import (
    get_best_target_l1,
    get_best_target_l2,
)
from agentic_core.L5_safety.validators.core.decorators import standard_heal

# [SSOT IMPORT] Master Constitution is the absolute source of truth
from agentic_core.L5_safety.validators.structure_blueprint_config import (
    ALLOWED_DUPLICATE_FILENAMES,
    CORE_SUBFOLDER_MAP,
    ROOT_PROTECTED_FILES,
    SOVEREIGN_EXCLUDED_FOLDERS,
    SOVEREIGN_TERRITORIES,
    VARIABLE_DEPTH_SUBFOLDERS,
)

# [MISSION AUDIT] Standardized logging for L4 Ledger consumption
logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)


@dataclass
class HierarchyAgent(AtomicExecutionMixin, SovereignBaseAgent):
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

    def __init__(
        self,
        project_root: Path,
        healing_enabled: bool = True,
        ctx: Any = None,
        auto_approve: bool = False,
    ) -> None:
        """
        Initialize the unified hierarchy agent.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled (dry-run if False)
            ctx: Optional context for reporting
            auto_approve: If True, bypasses interactive user confirmation for moves
        """
        self.project_root = project_root.resolve()
        self.healing_enabled = healing_enabled
        self.ctx = ctx
        self.protected_folders = SOVEREIGN_EXCLUDED_FOLDERS
        # [REFACTOR 2026-02-05] Changed from archives/ to .healing_backups/ (gitignored, not indexed)
        self.archive_root = project_root / ".healing_backups" / "hierarchy_violations"

        # Initialize ArchivalGatekeeper for safe file operations
        # [PHASE 33j] Gatekeeper is the SINGLE POINT OF APPROVAL
        # It checks SOVEREIGN_AUTO_APPROVE and ARCHIVE_BATCH_ACCEPT env vars
        self.gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)
        self.agent_name = "HierarchyAgent"

        # Configure gatekeeper based on auto_approve setting
        if auto_approve:
            self.gatekeeper.set_require_approval(False)

        if healing_enabled:
            self.archive_root.mkdir(parents=True, exist_ok=True)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for hierarchy violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        try:
            violation_type = violation.get("type", "")
            file_path = violation.get("file")

            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }

            Path(file_path)

            # Dispatch based on violation type
            if violation_type == "STRUCTURE" or "MISSING" in violation_type:
                # Structure violations - create missing directories
                if self.healing_enabled:
                    results = self.create_missing_structure()
                    return {
                        "status": "success" if results["violations_found"] == 0 else "partial_success",
                        "details": f"Created {len(results['created'])} directories",
                        "artifacts": results["created"],
                        "errors": results["errors"],
                    }
                else:
                    return {
                        "status": "skipped",
                        "details": "Healing disabled - dry run mode",
                        "artifacts": [],
                        "errors": [],
                    }
            elif violation_type == "MISPLACED" or violation_type == "ORPHAN":
                # [CONSOLIDATED] File relocation delegated to LocationHealerAgent
                # LocationHealerAgent is the SSOT for all file mutation operations
                if self.healing_enabled:
                    try:
                        from agentic_core.L5_safety.validators.LocationHealerAgent import (
                            LocationHealerAgent,
                        )

                        healer = LocationHealerAgent(project_root=self.project_root)
                        return healer.heal(violation)
                    except ImportError:
                        # Fallback to local implementation if LocationHealerAgent unavailable
                        results = self.relocate_misplaced_files()
                        return {
                            "status": "success" if results["violations_found"] == 0 else "partial_success",
                            "details": f"Relocated {results['files_relocated']} files",
                            "artifacts": [file_path],
                            "errors": results["errors"],
                        }
                else:
                    return {
                        "status": "skipped",
                        "details": "Healing disabled - dry run mode",
                        "artifacts": [],
                        "errors": [],
                    }
            elif "DEPTH" in violation_type:
                # Depth violations
                if self.healing_enabled:
                    results = self.enforce_depth_rules()
                    total_archived = (
                        results["apps_archived"] + results["tests_archived"] + results["universal_archived"]
                    )
                    return {
                        "status": "success" if results["violations_found"] == 0 else "partial_success",
                        "details": f"Archived {total_archived} depth violations",
                        "artifacts": [file_path],
                        "errors": results["errors"],
                    }
                else:
                    return {
                        "status": "skipped",
                        "details": "Healing disabled - dry run mode",
                        "artifacts": [],
                        "errors": [],
                    }
            else:
                return {
                    "status": "skipped",
                    "details": f"No healer available for violation type: {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }

        except Exception as e:
            Logger.error(f"Heal operation failed: {e}")
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    # ========================================================================
    # STRUCTURE CREATION
    # ========================================================================

    def create_missing_structure(self, target_territory: str | None = None) -> dict[str, Any]:
        """
        Create missing L2 (Layer) and L3 (Sub-territory) directories.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        [HARDENED] Accepts target_territory to optimize scoped creation.

        Hierarchy: Project Root (L0) → agentic_core (L1) → Layer Folders (L2, e.g., L1_cognition)
                   → Sub-territories (L3, e.g., thought_engine)

        Returns:
            Dict with counts of created directories and violations found
        """
        results = {"created": [], "errors": [], "violations_found": 0}

        Logger.info("HierarchyAgent: Enforcing L3 sub-territory subatomic structure per SSOT...")

        # agentic_core is L1; subfolders are L2 layers (L1_cognition, etc.)
        approved_layers_l2 = SOVEREIGN_TERRITORIES.get("agentic_core", {}).get("subfolders", [])

        for layer_l2_name in approved_layers_l2:
            # [SCOPED] Skip unrelated layers
            if target_territory and target_territory != layer_l2_name:
                # Check if target is L3 nested in this L2
                expected_l3 = set(CORE_SUBFOLDER_MAP.get(layer_l2_name, []))
                if target_territory not in expected_l3:
                    continue

            layer_l2_path = self.project_root / "agentic_core" / layer_l2_name
            if not layer_l2_path.exists():
                # Only create L2 if it matches target or we are in global mode
                if not target_territory or target_territory == layer_l2_name:
                    results["violations_found"] += 1
                    Logger.warning(f"   [!] MISSING L2 LAYER: agentic_core/{layer_l2_name}")
                    if self.healing_enabled:
                        self._create_dir_with_init(layer_l2_path, results, f"agentic_core/{layer_l2_name}")
                # If parent L2 doesn't exist and we are scoped to something else, we might skip
                if not layer_l2_path.exists():
                    continue

            # L3 Sub-territories (thought_engine, guardrails, etc.)
            expected_territories_l3 = set(CORE_SUBFOLDER_MAP.get(layer_l2_name, []))
            if not expected_territories_l3:
                continue

            # [SCOPED] Filter L3 targets
            if target_territory and target_territory in expected_territories_l3:
                expected_territories_l3 = {target_territory}

            actual_l3 = {p.name for p in layer_l2_path.iterdir() if p.is_dir() and not p.name.startswith(".")}
            missing_l3 = expected_territories_l3 - actual_l3

            for territory_l3_name in missing_l3:
                results["violations_found"] += 1
                l3_path = layer_l2_path / territory_l3_name
                Logger.warning(
                    f"   [!] MISSING L3 TERRITORY: agentic_core/{layer_l2_name}/{territory_l3_name}",
                )
                if self.healing_enabled:
                    self._create_dir_with_init(
                        l3_path,
                        results,
                        f"agentic_core/{layer_l2_name}/{territory_l3_name}",
                    )

        if results["violations_found"] > 0:
            Logger.info(
                f"HierarchyAgent: [STRUCTURE] Found {results['violations_found']} missing directories",
            )
            if self.healing_enabled and results["created"]:
                Logger.info(f"HierarchyAgent: [STRUCTURE] Created {len(results['created'])} directories")

        return results

    def _create_dir_with_init(self, path: Path, results: dict, rel_label: str) -> None:
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

    def relocate_misplaced_files(self, target_territory: str | None = None) -> dict[str, Any]:
        """
        Relocate files from Sovereign Roots with optional territory filtering.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        Args:
            target_territory: If specified, restricts auditing to the relevant root (Strict Targeting).

        Returns:
            Dict with counts of relocated files, removed folders, violations found, and roots processed
        """
        results = {
            "files_relocated": 0,
            "folders_removed": 0,
            "violations_found": 0,
            "errors": [],
            "roots_processed": [],
        }

        # [STRICT SCOPE] Scope Targeting Logic
        if target_territory:
            # If territory is a known root, target only that. Otherwise, target agentic_core.
            if target_territory in SOVEREIGN_TERRITORIES:
                target_roots = [target_territory]
            else:
                target_roots = ["agentic_core"]
            Logger.info(f"HierarchyAgent: 🎯 TARGETED SCAN: {target_territory} -> Roots: {target_roots}")
        else:
            # Universal Scope: Iterate through all roots defined in SOVEREIGN_TERRITORIES
            target_roots = [r for r in SOVEREIGN_TERRITORIES.keys() if (self.project_root / r).exists()]
            Logger.info(f"HierarchyAgent: 🌍 Universal Scope active: {len(target_roots)} roots")

        Logger.info(f"HierarchyAgent: Auditing {len(target_roots)} sovereign territories: {target_roots}")

        for root_name in target_roots:
            root_path = self.project_root / root_name
            results["roots_processed"].append(root_name)

            # Dispatch based on root type
            if root_name == "agentic_core":
                self._enforce_agentic_core_structure(root_path, results)
            elif root_name.startswith("apps_"):
                self._enforce_apps_structure(root_path, results)
            elif root_name == "tests":
                self._enforce_tests_structure(root_path, results)

        if results["violations_found"] > 0:
            Logger.info(f"HierarchyAgent: [RELOCATION] Found {results['violations_found']} misplaced files")
            if self.healing_enabled:
                Logger.info(
                    f"HierarchyAgent: [RELOCATION] {results['files_relocated']} files relocated, {results['folders_removed']} folders removed",
                )
                # Universal Cleanup: Trigger recursive empty dir removal for all processed roots
                for root_name in results.get("roots_processed", []):
                    root_path = self.project_root / root_name
                    self._remove_empty_dirs(root_path)

        return results

    def _enforce_agentic_core_structure(self, agentic_core_path: Path, results: dict[str, Any]) -> None:
        """Enforce strictly defined L2 structure for agentic_core."""
        approved_layers_l2 = set(SOVEREIGN_TERRITORIES.get("agentic_core", {}).get("subfolders", []))

        # Phase 1: Find all non-approved Layer (L2) folders
        actual_layers_l2 = {
            p.name
            for p in agentic_core_path.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
        }
        non_approved_l2 = actual_layers_l2 - approved_layers_l2

        for bad_layer_l2 in non_approved_l2:
            self._relocate_l2_layer_files(agentic_core_path, bad_layer_l2, approved_layers_l2, results)

        # Phase 2: Check L3 sub-territories within approved L2 Layers
        for layer_l2_name in approved_layers_l2:
            self._relocate_l3_territory_files(agentic_core_path, layer_l2_name, results)

    def _enforce_apps_structure(self, root_path: Path, results: dict[str, Any]) -> None:
        """Flatten files in apps_*/subfolder/subsubfolder/ to match target depth."""
        root_key = root_path.name
        target_depth = SOVEREIGN_TERRITORIES.get(root_key, {}).get("depth", 2)

        # Use existing depth enforcement logic but specifically for apps scope
        # This will trigger _heal_depth_violation which handles flattening
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(root_path):
            rel = py_file.relative_to(self.project_root)
            current_depth = len(rel.parts) - 1

            if current_depth > target_depth:
                results["violations_found"] += 1
                Logger.warning(f"   [!] DEPTH DRIFT: {rel} is depth {current_depth}, expected {target_depth}")
                if self.healing_enabled:
                    archived = self._heal_depth_violation(py_file, rel, current_depth, target_depth)
                    if archived:
                        results["files_relocated"] += 1

    def _enforce_tests_structure(self, root_path: Path, results: dict[str, Any]) -> None:
        """Categorize test files into unit, integration, e2e, functional, or fixtures."""
        # Use rglob directly since we specifically want test files
        approved_subfolders = {"unit", "integration", "e2e", "functional", "fixtures"}

        # Get all .py files in tests directory
        py_files = list(root_path.rglob("*.py"))

        for py_file in py_files:
            rel = py_file.relative_to(root_path)

            # Skip files already in approved subfolders
            if len(rel.parts) > 1 and rel.parts[0] in approved_subfolders:
                continue

            # Skip whitelisted root files (conftest.py, pytest.ini)
            if len(rel.parts) == 1:
                from agentic_core.L5_safety.validators.structure_blueprint_config import (
                    TESTS_ROOT_FILE_WHITELIST,
                )

                if py_file.name in TESTS_ROOT_FILE_WHITELIST:
                    continue

            # Determine target category
            name = py_file.name.lower()
            if "fixture" in name or "conftest" in name:
                category = "fixtures"
            elif "_e2e" in name or "e2e" in name:
                category = "e2e"
            elif "_integration" in name or "integration" in name:
                category = "integration"
            elif "_functional" in name or "functional" in name:
                category = "functional"
            else:
                category = "unit"  # Default

            target_dir = root_path / category
            target_dir.mkdir(parents=True, exist_ok=True)
            dest = target_dir / py_file.name

            if not dest.exists():
                results["violations_found"] += 1
                Logger.warning(f"   [!] UNCATEGORIZED TEST: {rel} -> {category}/")
                if self.healing_enabled:
                    # [PHASE 33j] Gatekeeper is Single Point of Approval
                    gk_result = self.gatekeeper.safe_move(
                        py_file,
                        dest,
                        self.agent_name,
                        f"Test categorization: {category}",
                    )
                    if gk_result.success:
                        results["files_relocated"] += 1
                        Logger.info(f"      [✓] CATEGORIZED: {py_file.name} -> {category}/")
            else:
                Logger.warning(f"      [!] SKIP (exists): {py_file.name} in {category}/")

    def _relocate_l2_layer_files(
        self,
        agentic_core_path: Path,
        bad_layer_l2: str,
        approved_layers_l2: set,
        results: dict[str, Any],
    ) -> None:
        """Relocate files from non-approved L2 layer."""
        bad_path = agentic_core_path / bad_layer_l2

        # Phase 4.1: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(bad_path):
            if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                continue
            results["violations_found"] += 1
            Logger.warning(f"   [!] MISPLACED FILE: {py_file.name} in illegal layer '{bad_layer_l2}'")

            if self.healing_enabled:
                self._relocate_file_to_l2(
                    py_file,
                    bad_layer_l2,
                    agentic_core_path,
                    approved_layers_l2,
                    results,
                )

        if self.healing_enabled:
            self._cleanup_empty_folder(bad_path, bad_layer_l2, results)

    def _relocate_file_to_l2(
        self,
        py_file: Path,
        bad_layer_l2: str,
        agentic_core_path: Path,
        approved_layers_l2: set,
        results: dict[str, Any],
    ) -> None:
        """Relocate a single file to approved L2 layer."""
        from agentic_core.L5_safety.validators.structure_blueprint_config import (
            check_forbidden_signals,
        )

        try:
            # ARTIFACT ROUTING NEGATIVE LOGIC CHECK
            # Prevent files with forbidden extensions/keywords from being relocated
            try:
                content = None
                if py_file.exists() and py_file.stat().st_size < 1_000_000:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")

                rejection_reason = check_forbidden_signals(py_file.name, content)
                if rejection_reason:
                    Logger.warning(f"      [!] SKIP (forbidden): {py_file.name} - {rejection_reason}")
                    results["errors"].append(f"{py_file.name}: {rejection_reason}")
                    return
            except Exception:
                pass  # Non-blocking

            target_layer_l2 = get_best_target_l1(bad_layer_l2, approved_layers_l2)
            target_path = agentic_core_path / target_layer_l2
            target_territory_l3 = get_best_target_l2(target_layer_l2, py_file.name)
            final_target = target_path / target_territory_l3
            final_target.mkdir(parents=True, exist_ok=True)

            dest = final_target / py_file.name
            if not dest.exists():
                # [PHASE 33j] Gatekeeper is Single Point of Approval
                gk_result = self.gatekeeper.safe_move(
                    py_file,
                    dest,
                    self.agent_name,
                    f"Relocate from illegal layer '{bad_layer_l2}'",
                )
                if gk_result.success:
                    Logger.info(
                        f"      [✓] RELOCATED: {py_file.name} -> {target_layer_l2}/{target_territory_l3}/",
                    )
                    results["files_relocated"] += 1
                elif gk_result.approval_status == "DENIED":
                    Logger.info(f"      [SKIPPED] User declined: {py_file.name}")
            else:
                Logger.info(f"      [!] SKIP (exists): {py_file.name}")
        except Exception as e:
            results["errors"].append(f"{py_file.name}: {e}")

    def _relocate_l3_territory_files(
        self,
        agentic_core_path: Path,
        layer_l2_name: str,
        results: dict[str, Any],
    ) -> None:
        """Relocate files from non-approved L3 territories."""
        layer_l2_path = agentic_core_path / layer_l2_name
        if not layer_l2_path.exists():
            return

        approved_territories_l3 = set(CORE_SUBFOLDER_MAP.get(layer_l2_name, []))
        if not approved_territories_l3:
            return

        actual_territories_l3 = {
            p.name
            for p in layer_l2_path.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.name not in self.protected_folders
        }
        non_approved_l3 = actual_territories_l3 - approved_territories_l3

        for bad_territory_l3 in non_approved_l3:
            bad_path = layer_l2_path / bad_territory_l3

            # Phase 4.1: Use ssot_discovery instead of rglob
            from agentic_core.utils.ssot_discovery_validator import get_python_files

            for py_file in get_python_files(bad_path):
                if py_file.name in ALLOWED_DUPLICATE_FILENAMES:
                    continue
                results["violations_found"] += 1
                Logger.warning(
                    f"   [!] MISPLACED FILE: {py_file.name} in illegal territory '{layer_l2_name}/{bad_territory_l3}'",
                )

                if self.healing_enabled:
                    self._relocate_file_to_l3(
                        py_file,
                        layer_l2_name,
                        layer_l2_path,
                        bad_territory_l3,
                        results,
                    )

            if self.healing_enabled:
                self._cleanup_empty_folder(bad_path, f"{layer_l2_name}/{bad_territory_l3}", results)

    def _relocate_file_to_l3(
        self,
        py_file: Path,
        layer_l2_name: str,
        layer_l2_path: Path,
        bad_territory_l3: str,
        results: dict[str, Any],
    ) -> None:
        """Relocate a single file to approved L3 territory."""
        from agentic_core.L5_safety.validators.structure_blueprint_config import (
            check_forbidden_signals,
        )

        try:
            # ARTIFACT ROUTING NEGATIVE LOGIC CHECK
            # Prevent files with forbidden extensions/keywords from being relocated
            try:
                content = None
                if py_file.exists() and py_file.stat().st_size < 1_000_000:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")

                rejection_reason = check_forbidden_signals(py_file.name, content)
                if rejection_reason:
                    Logger.warning(f"      [!] SKIP (forbidden): {py_file.name} - {rejection_reason}")
                    results["errors"].append(f"{py_file.name}: {rejection_reason}")
                    return
            except Exception:
                pass  # Non-blocking

            target_territory_l3 = get_best_target_l2(layer_l2_name, bad_territory_l3)
            target_path = layer_l2_path / target_territory_l3
            target_path.mkdir(parents=True, exist_ok=True)

            dest = target_path / py_file.name
            if not dest.exists():
                # [PHASE 33j] Gatekeeper is Single Point of Approval
                gk_result = self.gatekeeper.safe_move(
                    py_file,
                    dest,
                    self.agent_name,
                    f"Relocate from illegal territory '{bad_territory_l3}'",
                )
                if gk_result.success:
                    Logger.info(
                        f"      [✓] RELOCATED: {py_file.name} -> {layer_l2_name}/{target_territory_l3}/",
                    )
                    results["files_relocated"] += 1
                elif gk_result.approval_status == "DENIED":
                    Logger.info(f"      [SKIPPED] User declined: {py_file.name}")
            else:
                Logger.info(f"      [!] SKIP (exists): {py_file.name}")
        except Exception as e:
            results["errors"].append(f"{py_file.name}: {e}")

    def _cleanup_empty_folder(self, folder_path: Path, folder_label: str, results: dict[str, Any]) -> None:
        """Remove empty folder tree after relocation."""
        try:
            self._remove_empty_dirs(folder_path)
            if not folder_path.exists():
                Logger.info(f"      [✓] REMOVED empty folder: {folder_label}")
                results["folders_removed"] += 1
        except Exception as e:
            results["errors"].append(f"Remove {folder_label}: {e}")

    # ========================================================================
    # DEPTH ENFORCEMENT (from HierarchyEnforcerAgent)
    # ========================================================================

    def enforce_depth_rules(self, target_territory: str | None = None) -> dict[str, Any]:
        """
        Enforce depth rules and archive violations.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        [HARDENED] Accepts target_territory to skip unrelated roots.

        Returns:
            Dict with counts of archived files by category and violations found
        """
        results = {
            "apps_archived": 0,
            "tests_archived": 0,
            "universal_archived": 0,
            "violations_found": 0,
            "errors": [],
        }

        Logger.info("HierarchyAgent: Performing Depth-Precision audit (agentic_core=3, apps=2, tests=2)...")

        # If target_territory is specified (e.g., prompt_governance), depth rules for apps/tests are irrelevant
        # Only enforce universal depth if inside agentic_core
        # Depth enforcement is usually global hygiene. We will skip apps/tests if targeting a core module.

        # [SCOPED] Skip apps depth if targeting core
        if not target_territory or target_territory.startswith("apps_"):
            apps_count = self._enforce_apps_depth()
            results["violations_found"] += apps_count
            if self.healing_enabled:
                results["apps_archived"] = apps_count

        # [SCOPED] Skip tests depth if targeting core/apps
        if not target_territory or target_territory == "tests":
            tests_count = self._enforce_tests_depth()
            results["violations_found"] += tests_count
            if self.healing_enabled:
                results["tests_archived"] = tests_count

        # Universal depth (agentic_core)
        if not target_territory or not (target_territory.startswith("apps_") or target_territory == "tests"):
            universal_count = self._enforce_universal_depth()
            results["violations_found"] += universal_count
            if self.healing_enabled:
                results["universal_archived"] = universal_count

        if results["violations_found"] > 0:
            Logger.info(f"HierarchyAgent: [DEPTH] Found {results['violations_found']} depth violations")
            if self.healing_enabled:
                total_archived = (
                    results["apps_archived"] + results["tests_archived"] + results["universal_archived"]
                )
                Logger.info(
                    f"HierarchyAgent: [DEPTH] Archived {total_archived} files (apps: {results['apps_archived']}, tests: {results['tests_archived']}, universal: {results['universal_archived']})",
                )

        return results

    def _enforce_depth_for_root(
        self,
        root_key: str,
        root_check: callable,
        archive_subdir: str,
        label: str,
    ) -> int:
        """Generic depth enforcement using dispatch pattern."""
        expected_depth = SOVEREIGN_TERRITORIES.get(root_key, {}).get("depth", 2)
        archived, violations = 0, 0
        # Phase 6.5: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

        all_files = list(get_python_files(self.project_root)) + list(
            get_data_files(self.project_root, extensions=[".json", ".md", ".yaml", ".yml"]),
        )
        for file_path in all_files:
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(self.project_root)
            if not root_check(rel.parts[0]):
                continue
            # [FIX] Depth = folder level where file resides, not path length
            # agentic_core/L0_maintenance/scripts/file.md → depth 3 (scripts is level 3)
            depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level

            # [SSOT FIX] Check if this is a variable-depth subfolder (exempt from strict depth check)
            if len(rel.parts) > 1:
                subfolder = rel.parts[1]
                if subfolder in VARIABLE_DEPTH_SUBFOLDERS:
                    # Allow any depth >= 2 for variable-depth subfolders
                    if depth >= 2:
                        continue  # Skip this file - it's in a variable-depth subfolder

            if depth != expected_depth:
                violations += 1
                Logger.warning(f"   [!] DEPTH DRIFT: {rel} is depth {depth}, expected {expected_depth}")
                if self.healing_enabled:
                    archived += self._heal_depth_violation(file_path, rel, depth, expected_depth)
        return violations if not self.healing_enabled else archived

    def _heal_depth_violation(self, file_path: Path, rel: Path, depth: int, expected: int) -> int:
        """
        Smart depth re-alignment instead of archiving.

        Strategy:
        - DEEP Violation (> expected): Flatten by moving up.
        - SHALLOW Violation (< expected): Nest by adding 'depth_aligned' spacers.
        """
        try:
            if depth > expected:
                # DEEP: Flatten (move up) - Keep the filename, remove intermediate folders
                # Logic: Take first 'expected' parts + filename
                new_parts = rel.parts[:expected] + (rel.parts[-1],)
                target_path = self.project_root.joinpath(*new_parts)
                action = "FLATTENED"
            else:
                # SHALLOW: Nest (add depth_aligned spacers)
                deficit = expected - depth
                spacers = tuple(["depth_aligned"] * deficit)
                # Logic: Insert spacers before the filename
                new_parts = rel.parts[:-1] + spacers + (rel.parts[-1],)
                target_path = self.project_root.joinpath(*new_parts)
                action = "NESTED"

            # Safety Check: Don't overwrite existing files without verification
            if target_path.exists():
                # Fallback to legacy archive if target exists to prevent data loss
                return self._legacy_archive_depth_violation(
                    file_path,
                    rel,
                    depth,
                    expected,
                    "collision",
                    "COLLISION",
                )

            # Execute Move using ArchivalGatekeeper
            target_path.parent.mkdir(parents=True, exist_ok=True)
            gk_result = self.gatekeeper.safe_move(
                file_path,
                target_path,
                self.agent_name,
                f"Depth healing: {action}",
            )

            if not gk_result.success:
                Logger.error(f"  [ERROR] Gatekeeper move failed: {gk_result.error}")
                return 0

            # Log the healing action
            Logger.info(f"  [HEALED] {action}: {rel} -> {target_path.relative_to(self.project_root)}")
            return 1

        except Exception as e:
            # Failsafe: If healing fails, log error
            Logger.error(f"  [ERROR] Healing failed for {rel}: {e}")
            return 0

    def _legacy_archive_depth_violation(
        self,
        file_path: Path,
        rel: Path,
        depth: int,
        expected: int,
        subdir: str,
        label: str,
    ) -> int:
        """Legacy archive method - only used as fallback when smart healing has collision.

        [PHASE 33j] Gatekeeper is Single Point of Approval - handles user prompts.
        """
        try:
            # [PHASE 33j] Use Gatekeeper's safe_archive which handles approval
            reason = f"{label} DEPTH VIOLATION: depth {depth}, expected {expected}"
            gk_result = self.gatekeeper.safe_archive(file_path, self.agent_name, reason)

            if gk_result.success:
                Logger.info(f"  [ARCHIVED] {rel} -> {gk_result.destination_path}")
                return 1
            elif gk_result.approval_status == "DENIED":
                Logger.info(f"  [SKIPPED] User declined archive: {rel}")
                return 0
            else:
                Logger.error(f"  [ERROR] Archive failed: {gk_result.error}")
                return 0
        except Exception:
            return 0

    def _enforce_apps_depth(self) -> int:
        """Enforce apps_* depth rule using generic handler for each apps folder."""
        total_violations = 0
        # Check each apps_* folder with its own depth requirement
        for apps_key in ["apps_rg", "apps_lic", "apps_shared"]:
            if apps_key in SOVEREIGN_TERRITORIES:
                violations = self._enforce_depth_for_root(
                    apps_key,
                    lambda r, key=apps_key: r == key,
                    "apps_depth",
                    f"APPS_{apps_key.upper()}",
                )
                total_violations += violations
        return total_violations

    def _enforce_tests_depth(self) -> int:
        """Enforce tests depth rule using generic handler."""
        return self._enforce_depth_for_root("tests", lambda r: r == "tests", "tests_depth", "TESTS")

    def _enforce_universal_depth(self) -> int:
        """Enforce universal depth for non-Python files in agentic_core (depth 3). Detection-First."""
        agentic_core_exact_depth = SOVEREIGN_TERRITORIES.get("agentic_core", {}).get("depth", 3)
        archived = 0
        violations = 0

        # Phase 6.5: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_data_files

        target_exts = [".json", ".md", ".yaml", ".yml", ".toml", ".txt"]
        for file_path in get_data_files(self.project_root, extensions=target_exts):
            if file_path.is_dir():
                continue

            if file_path.suffix.lower() not in target_exts:
                continue

            rel = file_path.relative_to(self.project_root)
            if rel.parts[0] == "agentic_core":
                # [FIX] Depth = folder level where file resides, not path length
                # agentic_core/L0_maintenance/scripts/file.md → depth 3 (scripts is level 3)
                depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level

                # [SSOT FIX] Check if this is a variable-depth subfolder (exempt from strict depth check)
                if len(rel.parts) > 1:
                    subfolder = rel.parts[1]
                    if subfolder in VARIABLE_DEPTH_SUBFOLDERS:
                        # Allow any depth >= 2 for variable-depth subfolders
                        if depth >= 2:
                            continue  # Skip this file - it's in a variable-depth subfolder

                if depth != agentic_core_exact_depth:
                    violations += 1
                    Logger.warning(
                        f"   [!] DEPTH DRIFT: {rel} is depth {depth}, expected {agentic_core_exact_depth}",
                    )

                    if self.healing_enabled:
                        # Use smart depth re-alignment instead of archiving
                        archived += self._heal_depth_violation(
                            file_path,
                            rel,
                            depth,
                            agentic_core_exact_depth,
                        )

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
            p
            for p in path.iterdir()
            if p.name not in {"__pycache__", "__init__.py", ".gitkeep"} and not p.name.startswith(".")
        ]

        if not remaining:
            # Aggressively purge empty shell using ArchivalGatekeeper
            init_file = path / "__init__.py"
            if init_file.exists():
                self.gatekeeper.safe_delete(init_file, self.agent_name, "Empty folder cleanup - __init__.py")

            pycache = path / "__pycache__"
            if pycache.exists():
                shutil.rmtree(pycache, ignore_errors=True)  # Keep shutil for __pycache__ (not tracked)

            gitkeep = path / ".gitkeep"
            if gitkeep.exists():
                self.gatekeeper.safe_delete(gitkeep, self.agent_name, "Empty folder cleanup - .gitkeep")

            try:
                path.rmdir()
            except OSError:
                pass

    # ========================================================================
    # ORPHAN PURGING (from HierarchyHealerAgent)
    # ========================================================================

    def purge_orphaned_files(self) -> dict[str, Any]:
        """
        Purge code and assets in forbidden or root-level locations.

        Detection-First: Always scans and counts violations, only heals if healing_enabled=True.

        Returns:
            Dict with purge count, violations found, and errors
        """

        purged_count = 0
        violations_found = 0
        errors = []

        # [SSOT] Dynamically pull roots from registry
        allowed_roots = set(SOVEREIGN_TERRITORIES.keys())

        Logger.info("HierarchyAgent: Scanning for orphaned files outside sovereign territory...")

        orphaned_files = []
        # [SCALABILITY] Increased budget for mature repositories
        MAX_PURGE_SCAN = 5000
        scan_count = 0

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.protected_folders and not d.startswith(".")]
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

                archive_markers = (".archived", ".backup", ".old", ".copy")
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
                elif parts and parts[0] not in allowed_roots:
                    # File is in a non-SSOT root folder (e.g., rogue_folder/)
                    violations_found += 1
                    Logger.warning(f"      [⚠]  ORPHANED IN NON-SSOT ROOT '{parts[0]}': {rel_path}")
                else:
                    continue

                if self.healing_enabled:
                    # Ensure purge artifacts are ignored
                    self._update_gitignore_for_purge()

                    # Use ArchivalGatekeeper for safe archival
                    gk_result = self.gatekeeper.safe_archive(
                        file_path,
                        self.agent_name,
                        "Orphaned file purge",
                    )
                    if gk_result.success:
                        Logger.info(
                            f"      [✓] ARCHIVED & PURGED: {file_path.name} -> {gk_result.destination_path}",
                        )
                        purged_count += 1
                    else:
                        Logger.error(f"      [!] ARCHIVE FAILED: {file_path.name} - {gk_result.error}")
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

            new_lines = (
                lines[:insert_idx]
                + ["", marker_comment, dated_comment, purge_pattern, ""]
                + lines[insert_idx:]
            )
            new_content = "\n".join(new_lines).rstrip() + "\n"

            gitignore_path.write_text(new_content, encoding="utf-8")
        except Exception:
            pass

    # ========================================================================
    # UNIFIED INTERFACE
    # ========================================================================

    def heal_hierarchy(
        self,
        create_structure: bool = True,
        relocate_files: bool = True,
        enforce_depth: bool = True,
        purge_orphans: bool = True,
        execute: bool = False,
        dry_run: bool = True,
        auto_approve: bool = False,
        target_territory: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Unified hierarchy healing with granular control.

        Args:
            create_structure: Create missing L2/L3 directories
            relocate_files: Relocate files from non-approved folders
            enforce_depth: Enforce depth rules and archive violations
            purge_orphans: Purge orphaned files
            auto_approve: If True, bypasses interactive user confirmation for moves.
                          USE WITH CAUTION - intended for CI/automated enforcement.
            target_territory: If specified, scope healing to this territory only
                              (e.g., "prompt_governance" -> agentic_core/prompt_governance)

        Returns:
            Comprehensive results dictionary
        """
        # Set auto-approve mode if requested and not in dry-run
        if auto_approve and not dry_run:
            Logger.warning("[HierarchyAgent] SOVEREIGN MODE ACTIVE: Auto-approving all structural changes.")
            self._auto_approve = True
        else:
            self._auto_approve = False

        # Store target_territory for scoped operations
        self._target_territory = target_territory
        if target_territory:
            Logger.info(f"[HierarchyAgent] Scoped to territory: {target_territory}")

        print("=" * 80)
        print(f"HIERARCHY AGENT - {'DRY RUN' if not self.healing_enabled else 'ACTIVE'}")
        if target_territory:
            print(f"SCOPED TO: {target_territory}")
        print("=" * 80)

        results = {"structure": {}, "relocation": {}, "depth": {}, "purge": {}, "summary": {}}

        if create_structure:
            # [FIX] Pass target_territory
            results["structure"] = self.create_missing_structure(target_territory)

        if relocate_files:
            # [FIX] Pass target_territory
            results["relocation"] = self.relocate_misplaced_files(target_territory)

        if enforce_depth:
            # [FIX] Pass target_territory
            results["depth"] = self.enforce_depth_rules(target_territory)

        if purge_orphans:
            # [FIX] Skip global orphan purge if scoped, or implement scoped purge
            if target_territory:
                Logger.info(
                    "[HierarchyAgent] Skipping global orphan purge in scoped mode to protect out-of-scope assets.",
                )
                results["purge"] = {"purged": 0, "violations_found": 0}
            else:
                results["purge"] = self.purge_orphaned_files()

        # Summary
        total_violations = (
            results["structure"].get("violations_found", 0)
            + results["relocation"].get("violations_found", 0)
            + results["depth"].get("violations_found", 0)
            + results["purge"].get("violations_found", 0)
        )

        results["summary"] = {
            "violations_found": total_violations,
            "directories_created": len(results["structure"].get("created", [])),
            "files_relocated": results["relocation"].get("files_relocated", 0),
            "folders_removed": results["relocation"].get("folders_removed", 0),
            "depth_violations_archived": (
                results["depth"].get("apps_archived", 0)
                + results["depth"].get("tests_archived", 0)
                + results["depth"].get("universal_archived", 0)
            ),
            "orphans_purged": results["purge"].get("purged", 0),
            "total_actions": 0,
        }

        results["summary"]["total_actions"] = (
            results["summary"]["directories_created"]
            + results["summary"]["files_relocated"]
            + results["summary"]["folders_removed"]
            + results["summary"]["depth_violations_archived"]
            + results["summary"]["orphans_purged"]
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
            print("[DRY-RUN] No changes were made - run with healing_enabled=True to fix violations")
        print("=" * 80)

        return results

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Unified Hierarchy Healing - Enforces structure, relocation, and depth rules.

        WIRED CAPABILITIES:
        - heal_hierarchy(): Standard L2/L3 structure and file relocation.
        - heal_root_violations(): Root-level hygiene (scripts/, logs/, .archived).
        """
        # CRITICAL: Chain up to HealerMixin
        parent_result = super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
            **kwargs,
        )

        # Cycle detection is handled by @standard_heal / super(), but we add safe state management
        original_healing = self.healing_enabled
        # Enable healing if execute=True and dry_run=False
        should_heal = execute and not dry_run
        self.healing_enabled = should_heal

        try:
            # 1. Standard Hierarchy Healing
            result = self.heal_hierarchy(
                create_structure=True,
                relocate_files=True,
                enforce_depth=True,
                purge_orphans=True,
                execute=execute,
                dry_run=dry_run,
            )

            # 2. Root Directory Healing
            root_result = self.heal_root_violations(dry_run=dry_run)
            result["root_healing"] = root_result

            # Merge metrics
            metrics = {
                "violations": result.get("summary", {}).get("violations_found", 0)
                + root_result.get("violations_found", 0),
                "fixed": result.get("summary", {}).get("total_actions", 0)
                + len(root_result.get("actions", [])),
                "errors": len(result.get("structure", {}).get("errors", []))
                + len(root_result.get("errors", [])),
                "hierarchy_details": result,
            }

            return {**parent_result, **metrics}

        except Exception as e:
            Logger.error(f"Hierarchy healing failed: {e}")
            return {**parent_result, "errors": parent_result.get("errors", 0) + 1}
        finally:
            self.healing_enabled = original_healing

    def heal(self, violation: dict) -> dict:
        """
        [SOVEREIGN CONTRACT] Standardized healing interface for Hierarchy violations.
        """
        try:
            target = violation.get("file")
            violation.get("type", "")

            if not target:
                return {"status": "skipped", "reason": "No target specified"}

            # For hierarchy violations, delegate to existing heal_hierarchy logic
            # Since heal_hierarchy expects different params, return manual_required
            return {
                "status": "manual_required",
                "reason": "Hierarchy restructuring requires careful execution",
                "suggested_action": f"Run heal_repository() for {target}",
                "confidence": 0.8,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ========================================================================
    # ROOT DIRECTORY SCANNING (Gap Fix - 2026-01-18)
    # ========================================================================

    # Forbidden folders at root (they have SSOT locations elsewhere)
    # [SSOT UPDATE] scripts/ and logs/ are now VALID project roots per PROJECT_ROOT_METADATA
    FORBIDDEN_ROOT_FOLDERS = {
        "coverage_html",  # SSOT: reports/coverage_html/ or gitignored
        "observability",  # SSOT: agentic_core/L6_observability/
        "legacy_code",
        "legacy_engines",
    }

    def scan_root_violations(self, target_territory: str | None = None) -> dict[str, Any]:
        """
        [ULTRA-HARDENED] Universal Root Purge.
        Flags EVERY file in the territory root. Nothing is allowed to sit at L3 root.

        Detects:
        1. Forbidden folders at project root (scripts/, logs/, coverage_html/)
        2. .archived files at project root (should be in .healing_backups/)
        3. Files sitting in territory root instead of SSOT subfolders

        Args:
            target_territory: If specified, scans territory root for structural violations

        Returns:
            Dict with violations found and details
        """
        results = {
            "violations_found": 0,
            "forbidden_folders": [],
            "archived_files_at_root": [],
            "territory_root_files": [],
            "duplicate_folders": [],
            "errors": [],
        }

        # Phase 1: Traditional project root scanning
        if not target_territory:
            Logger.info("HierarchyAgent: Scanning project root directory for SSOT violations...")

            # 1. Check for forbidden folders at root
            for item in self.project_root.iterdir():
                if item.is_dir() and item.name in self.FORBIDDEN_ROOT_FOLDERS:
                    results["violations_found"] += 1
                    results["forbidden_folders"].append(item.name)
                    Logger.warning(f"   [!] FORBIDDEN ROOT FOLDER: {item.name}/")

            # 2. Check for .archived files at root
            archive_patterns = (".archived", ".backup", ".old")
            for item in self.project_root.iterdir():
                if item.is_file():
                    for pattern in archive_patterns:
                        if pattern in item.name:
                            results["violations_found"] += 1
                            results["archived_files_at_root"].append(item.name)
                            break

            if results["archived_files_at_root"]:
                Logger.warning(
                    f"   [!] {len(results['archived_files_at_root'])} archived files at root (should be in .healing_backups/)",
                )

        # Phase 2: Territory root violation scanning (Ultra-hardened)
        if target_territory:
            search_path = self.project_root / "agentic_core" / target_territory
            Logger.info(f"HierarchyAgent: 🎯 ULTRA SCAN: Territory root violations in {target_territory}")

            if not search_path.exists():
                results["errors"].append(f"Territory path not found: {search_path}")
                return results

            # Approved subfolders for prompt_governance per Blueprint
            # meta_prompts, templates, scripts, version_registry, agents, registry

            for item in search_path.iterdir():
                # Flag any file sitting at the root level of the territory
                if item.is_file() and item.name not in {".gitkeep", "__init__.py"}:
                    violation = {
                        "file": str(item.name),
                        "path": str(item.relative_to(self.project_root)),
                        "type": "STRUCTURE",
                        "message": f"File '{item.name}' sitting in {target_territory} root. Must be in SSOT subfolder.",
                        "severity": "ERROR",
                        "territory": target_territory,
                    }
                    results["territory_root_files"].append(violation)
                    results["violations_found"] += 1
                    Logger.warning(f"   [!] TERRITORY ROOT FILE: {item.name} in {target_territory}/")

        # Phase 3: Check for duplicate folders (original logic preserved)
        # [SSOT UPDATE] scripts/ and logs/ allowed at root. Only flag if they contain conflicting content?
        # For now, we disable the duplicate check for these valid roots to prevent false positives.
        pass

        if results["violations_found"] > 0:
            Logger.info(f"HierarchyAgent: [ROOT SCAN] Found {results['violations_found']} root violations")
        else:
            Logger.info("HierarchyAgent: [ROOT SCAN] No root violations found")

        return results

    # SSOT target locations for forbidden root folders
    ROOT_FOLDER_SSOT_TARGETS = {
        "coverage_html": "reports/coverage_html",  # Or add to .gitignore
        "observability": "agentic_core/L6_observability",
    }

    def heal_root_violations(self, dry_run: bool = True) -> dict[str, Any]:
        """
        Heal root directory SSOT violations.

        Actions:
        1. Move .archived files to .healing_backups/root_archived/
        2. [DEPRECATED] scripts/ and logs/ are now valid roots (no merge)
        3. Add coverage_html/ to .gitignore or move to reports/

        Args:
            dry_run: If True, only preview actions

        Returns:
            Dict with healing results
        """
        results = {
            "archived_files_moved": 0,
            "scripts_files_moved": 0,
            "logs_files_moved": 0,
            "coverage_handled": False,
            "folders_removed": 0,
            "errors": [],
            "actions": [],
        }

        scan_results = self.scan_root_violations()

        if scan_results["violations_found"] == 0:
            results["message"] = "No root violations to heal"
            return results

        # 1. Move .archived files to .healing_backups/root_archived/
        archives_dir = self.project_root / ".healing_backups" / "root_archived"
        if not dry_run:
            archives_dir.mkdir(parents=True, exist_ok=True)

        for filename in scan_results["archived_files_at_root"]:
            src = self.project_root / filename
            dst = archives_dir / filename

            action = {
                "type": "MOVE_ARCHIVED_FILE",
                "source": str(src),
                "destination": str(dst),
                "applied": False,
            }

            if not dry_run and src.exists():
                # [PHASE 33j] Gatekeeper is Single Point of Approval
                try:
                    gk_result = self.gatekeeper.safe_move(
                        src,
                        dst,
                        self.agent_name,
                        "Move archived file from root",
                    )
                    if gk_result.success:
                        action["applied"] = True
                        results["archived_files_moved"] += 1
                        Logger.info(f"   [✓] MOVED: {filename} -> .healing_backups/root_archived/")
                    elif gk_result.approval_status == "DENIED":
                        Logger.info(f"   [SKIPPED] User declined: {filename}")
                    else:
                        action["error"] = gk_result.error
                        results["errors"].append(f"Failed to move {filename}: {gk_result.error}")
                except Exception as e:
                    action["error"] = str(e)
                    results["errors"].append(f"Failed to move {filename}: {e}")

            results["actions"].append(action)

        # 2. [UPDATED] scripts/ and logs/ are valid - no action taken unless explicitly forbidden
        pass

        # 4. Handle coverage_html/ - add to .gitignore
        if "coverage_html" in scan_results["forbidden_folders"]:
            coverage_result = self._handle_coverage_html(dry_run)
            results["coverage_handled"] = coverage_result.get("handled", False)
            results["actions"].extend(coverage_result.get("actions", []))

        results["message"] = (
            f"Moved {results['archived_files_moved']} archived files, "
            f"{results['scripts_files_moved']} scripts, "
            f"{results['logs_files_moved']} logs. "
            f"Coverage: {'handled' if results['coverage_handled'] else 'pending'}. "
            f"Folders removed: {results['folders_removed']}"
        )
        return results

    def _merge_root_folder_to_ssot(self, folder_name: str, dry_run: bool) -> dict[str, Any]:
        """
        Merge a root folder's contents into its SSOT location.

        Args:
            folder_name: Name of folder at root (e.g., 'scripts', 'logs')
            dry_run: If True, only preview actions

        Returns:
            Dict with merge results
        """
        result = {
            "files_moved": 0,
            "files_skipped": 0,
            "folder_removed": False,
            "actions": [],
            "errors": [],
        }

        root_folder = self.project_root / folder_name
        ssot_target = self.ROOT_FOLDER_SSOT_TARGETS.get(folder_name)

        if not ssot_target or not root_folder.exists():
            return result

        ssot_folder = self.project_root / ssot_target

        if not dry_run:
            ssot_folder.mkdir(parents=True, exist_ok=True)

        Logger.info(f"HierarchyAgent: Merging {folder_name}/ -> {ssot_target}/")

        # Phase 6.5: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

        # Iterate through all files in root folder
        all_files = list(get_python_files(root_folder)) + list(
            get_data_files(root_folder, extensions=[".json", ".md", ".yaml", ".yml", ".txt", ".log"]),
        )
        for src_file in all_files:
            if src_file.is_dir():
                continue

            # Calculate relative path within the folder
            rel_path = src_file.relative_to(root_folder)
            dst_file = ssot_folder / rel_path

            action = {
                "type": f"MERGE_{folder_name.upper()}_FILE",
                "source": str(src_file),
                "destination": str(dst_file),
                "applied": False,
            }

            # Skip if destination already exists
            if dst_file.exists():
                action["skipped"] = True
                action["reason"] = "Destination exists"
                result["files_skipped"] += 1
                result["actions"].append(action)
                continue

            if not dry_run:
                # [PHASE 33j] Gatekeeper is Single Point of Approval
                try:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    gk_result = self.gatekeeper.safe_move(
                        src_file,
                        dst_file,
                        self.agent_name,
                        f"Merge {folder_name} file to SSOT location",
                    )
                    if gk_result.success:
                        action["applied"] = True
                        result["files_moved"] += 1
                        Logger.info(f"   [✓] MERGED: {rel_path} -> {ssot_target}/")
                    elif gk_result.approval_status == "DENIED":
                        Logger.info(f"   [SKIPPED] User declined: {rel_path}")
                    else:
                        action["error"] = gk_result.error
                        result["errors"].append(f"Failed to move {src_file}: {gk_result.error}")
                except Exception as e:
                    action["error"] = str(e)
                    result["errors"].append(f"Failed to move {src_file}: {e}")

            result["actions"].append(action)

        # Try to remove the now-empty root folder
        if not dry_run and root_folder.exists():
            try:
                self._remove_empty_dirs(root_folder)
                if not root_folder.exists():
                    result["folder_removed"] = True
                    Logger.info(f"   [✓] REMOVED empty folder: {folder_name}/")
            except Exception as e:
                result["errors"].append(f"Failed to remove {folder_name}/: {e}")

        return result

    def _handle_coverage_html(self, dry_run: bool) -> dict[str, Any]:
        """
        Handle coverage_html/ folder by adding to .gitignore.

        Args:
            dry_run: If True, only preview actions

        Returns:
            Dict with handling results
        """
        result = {
            "handled": False,
            "actions": [],
        }

        gitignore_path = self.project_root / ".gitignore"
        coverage_entry = "coverage_html/"

        action = {
            "type": "ADD_TO_GITIGNORE",
            "entry": coverage_entry,
            "applied": False,
        }

        # Check if already in .gitignore
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
            if coverage_entry in content or "coverage_html" in content:
                action["skipped"] = True
                action["reason"] = "Already in .gitignore"
                result["handled"] = True
                result["actions"].append(action)
                return result

        if not dry_run:
            try:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write(f"\n# Test coverage output\n{coverage_entry}\n")
                action["applied"] = True
                result["handled"] = True
                Logger.info(f"   [✓] ADDED to .gitignore: {coverage_entry}")
            except Exception as e:
                action["error"] = str(e)

        result["actions"].append(action)
        return result


# Singleton getter for canon_validator compatibility
_hierarchy_agent_instance = None


def get_hierarchy_agent(project_root):
    """Get or create HierarchyAgent singleton."""
    global _hierarchy_agent_instance
    if _hierarchy_agent_instance is None:
        _hierarchy_agent_instance = HierarchyAgent(project_root)
    return _hierarchy_agent_instance
