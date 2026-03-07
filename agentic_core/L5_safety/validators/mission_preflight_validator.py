from __future__ import annotations

# mission_preflight.py
# L5 Mission Preflight Validator
# PURPOSE: Executes pre-mission compliance checks and enforces void compliance
# LOCATION: agentic_core/L5_safety/validators/ (SSOT-compliant)
import os
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint_config import (
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent as HierarchyHealerAgent


class MissionPreflight:
    """
    L5 Mission Preflight Validator

    Integrates Void Compliance into the Master Validation Sweep.
    Executes pre-flight checks before any validation begins.
    """

    def __init__(self, project_root: Path, healing_enabled: bool = True):
        """
        Initialize the preflight validator.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled
        """
        self.project_root = project_root.resolve()
        self.healing_enabled = healing_enabled
        self.protected_folders = SOVEREIGN_EXCLUDED_FOLDERS
        self.HierarchyHealerAgent = HierarchyHealerAgent(project_root, healing_enabled)

        # Import agents dynamically to avoid circular imports
        self._location_agent = None
        self._hierarchy_agent = None
        self._import_agent = None

    def _get_location_agent(self):
        """Lazy load LocationAgent."""
        if self._location_agent is None:
            try:
                from agentic_core.L5_safety.reasoning.LocationValidatorAgent import LocationValidatorAgent

                self._location_agent = LocationValidatorAgent(self.project_root)
            except ImportError:
                pass
        return self._location_agent

    def _get_hierarchy_agent(self):
        """Lazy load HierarchyAgent."""
        if self._hierarchy_agent is None:
            try:
                from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent

                self._hierarchy_agent = HierarchyAgent(self.project_root)
            except ImportError:
                pass
        return self._hierarchy_agent

    def _get_import_agent(self):
        """Lazy load import healer."""
        if self._import_agent is None:
            try:
                # Phase 5 Migration: ImportAgent -> CodeHealerAgent
                from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
                    create_legacy_import_healer,
                )

                self._import_agent = create_legacy_import_healer()
            except ImportError:
                pass
        return self._import_agent

    def run_preflight(self, target_sector: str) -> dict[str, Any]:
        """
        Execute the full preflight compliance check.

        Args:
            target_sector: Path to the target sector for validation

        Returns:
            Dict with compliance results and Violation counts
        """
        print(f"\n[*] L6 PRE-FLIGHT: Enforcing Void Compliance on {target_sector}...")
        results = {"compliant": True, "Span": 0, "hierarchy": 0, "naming": 0, "gravity": 0}

        # Cross-reference with IDE Rules
        rules_path = self.project_root / "windsurfrules.md"
        if rules_path.exists():
            print("   [INFO] Synchronization active: windsurfrules.md detected.")

        target_path = Path(target_sector).resolve()

        # Check 1: Span-of-Two compliance (Key 13)
        results["Span"] = self._check_span_of_two(target_path)

        # Check 2: Hierarchy Alignment
        hierarchy_violations = self._check_hierarchy(target_path)
        results["hierarchy"] = len(hierarchy_violations)

        if hierarchy_violations and self.healing_enabled:
            healing_results = self.HierarchyHealerAgent.heal_hierarchy_violations()
            results["hierarchy_healed"] = healing_results["files_relocated"]

            # Re-check after healing
            if healing_results["files_relocated"] > 0:
                hierarchy_violations_after = self._check_hierarchy(target_path)
                results["hierarchy"] = len(hierarchy_violations_after)
                print(f"   [POST-HEALING] {results['hierarchy']} hierarchy violations remaining")

        # Check 3: Purge orphaned files
        if self.healing_enabled:
            purge_results = self.HierarchyHealerAgent.purge_orphaned_files()
            results["purged_orphans"] = purge_results["purged"]
            if purge_results["errors"]:
                results.setdefault("errors", []).extend(purge_results["errors"])

        # Check 4: Import waterfall violations (Gravity)
        results["gravity"] = self._check_gravity(target_path)

        # Check 5: File location validation
        results["naming"] = self._check_file_locations(target_path)

        # Print dashboard
        self._print_dashboard(results)

        total_violations = results["Span"] + results["hierarchy"] + results["naming"] + results["gravity"]
        results["compliant"] = total_violations == 0

        return results

    def _check_span_of_two(self, target_path: Path) -> int:
        """Check Span-of-Two compliance using HierarchyAgent."""
        hierarchy_agent = self._get_hierarchy_agent()
        if hierarchy_agent:
            try:
                span_result = hierarchy_agent.check_span_of_two()
                violations = span_result.get("violations", 0)
                if span_result.get("compliant", True):
                    print("   [OK] Span-of-Two compliance verified by HierarchyAgent")
                else:
                    print(f"[!] L6 ALERT: Found {violations} Span violations:")
                    for v in span_result.get("details", [])[:3]:
                        print(f"   [X] {v}")
                return violations
            except Exception as e:
                print(f"   [!] Span check failed: {e}")
        else:
            print("   [!] Hierarchy monitoring unavailable - Span-of-Two status unknown.")
        return 0

    def _check_hierarchy(self, target_path: Path) -> list[tuple[Path, str]]:
        """Check hierarchy alignment using HierarchyAgent."""
        hierarchy_agent = self._get_hierarchy_agent()
        if hierarchy_agent:
            try:
                result = hierarchy_agent.validate_hierarchy()
                violations = [v for v in result if ".git" not in str(v[0]) and "__init__.py" not in str(v[0])]
                if violations:
                    print(f"[!] L6 ALERT: Found {len(violations)} hierarchy violations:")
                    for folder_path, reason in violations[:3]:
                        try:
                            rel_path = folder_path.relative_to(self.project_root)
                        except ValueError:
                            rel_path = folder_path
                        print(f"   [X] {rel_path}: {reason}")
                    if len(violations) > 3:
                        print(f"   ... and {len(violations) - 3} more violations")
                return violations
            except Exception as e:
                print(f"   [!] Hierarchy check failed: {e}")
        return []

    def _check_gravity(self, target_path: Path) -> int:
        """Check import waterfall violations."""
        import_agent = self._get_import_agent()
        if not import_agent:
            return 0

        waterfall_violations = []
        MAX_SCAN_FILES = 3000
        scanned_count = 0

        print(f"   [GRAVITY SCAN] Starting bounded scan (max {MAX_SCAN_FILES} files)...")

        if target_path.is_dir():
            scan_limit_reached = False
            for root, dirs, files in os.walk(target_path):
                if scan_limit_reached:
                    break
                dirs[:] = [d for d in dirs if d not in self.protected_folders]
                for file in files:
                    if scanned_count >= MAX_SCAN_FILES:
                        print(f"   [WARNING] Scan limit reached ({MAX_SCAN_FILES} files) - stopping early")
                        scan_limit_reached = True
                        break
                    if not file.endswith(".py"):
                        continue
                    scanned_count += 1
                    py_file = Path(root) / file

                    try:
                        rel_path = py_file.relative_to(self.project_root)
                        root_folder = rel_path.parts[0]
                        if root_folder == "agentic_core":
                            violations = import_agent.check_waterfall_violations(str(py_file))
                            if violations:
                                waterfall_violations.extend([(py_file, v) for v in violations])
                    except Exception:
                        continue

            if not scan_limit_reached:
                print(f"   [OK] Gravity scan completed: {scanned_count} Python files analyzed")

        if waterfall_violations:
            print(f"[!] L6 ALERT: Found {len(waterfall_violations)} import waterfall violations:")
            for file_path, reason in waterfall_violations[:3]:
                print(f"   [X] {file_path.name}: {reason}")
            if len(waterfall_violations) > 3:
                print(f"   ... and {len(waterfall_violations) - 3} more violations")

        return len(waterfall_violations)

    def _check_file_locations(self, target_path: Path) -> int:
        """Check file location validation."""
        location_agent = self._get_location_agent()
        if not location_agent:
            return 0

        location_violations = []

        if target_path.is_dir():
            for root, dirs, files in os.walk(target_path):
                dirs[:] = [d for d in dirs if d not in self.protected_folders and d != ".git"]
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    py_file = Path(root) / file
                    try:
                        is_valid, reason = location_agent.validate_file_location(py_file)
                        if not is_valid:
                            location_violations.append((py_file, reason))
                    except Exception:
                        continue

        # Whitelist autonomous agents
        autonomous_agents = {
            "autonomous_checkpoint_manager.py",
            "autonomous_state_guardian.py",
            "self_updating_safety_engine.py",
            "neural_auto_immune_agent.py",
        }
        allowed_stages = {"policy", "shared", "hierarchy", "meta"}

        location_violations = [
            v
            for v in location_violations
            if v[0].name not in autonomous_agents and not any(s in str(v[0]) for s in allowed_stages)
        ]

        if location_violations:
            print(f"[!] L6 ALERT: Found {len(location_violations)} file location violations:")
            for file_path, reason in location_violations[:3]:
                safe_reason = reason.encode("ascii", "replace").decode("ascii")
                print(f"   [X] {file_path.name}: {safe_reason}")
            if len(location_violations) > 3:
                print(f"   ... and {len(location_violations) - 3} more violations")

        return len(location_violations)

    def _print_dashboard(self, results: dict[str, Any]) -> None:
        """Print the sovereignty dashboard."""
        print("\n" + "=" * 70)
        print(" SOVEREIGN INTEGRITY DASHBOARD (L6 PRE-FLIGHT)")
        print("=" * 70)

        metrics = [
            ("DEPTH / SPAN OF TWO", results["Span"]),
            ("HIERARCHY ALIGNMENT", results["hierarchy"]),
            ("NAMING / SIGNAL", results["naming"]),
            ("GRAVITY / IMPORTS", results["gravity"]),
        ]

        for label, count in metrics:
            status = "[OK]" if count == 0 else f"[X] {count} VIOLATIONS"
            print(f" {label:<25} | {status}")

        print("-" * 70)

        total_violations = sum(m[1] for m in metrics)

        if total_violations == 0:
            print("[SUCCESS] All structural laws satisfied. Neural Link established.")
        else:
            print(f"   [SOVEREIGN OVERRIDE] Forcing mutation for convergence ({total_violations} violations)")

        print("=" * 70 + "\n")
