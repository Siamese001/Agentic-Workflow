from __future__ import annotations

"""ArchitectureGovernorAgent - Universal Architecture Governance

Phase 1 Upgrade (2026-01-21): Activated from stub to functioning enforcer.
Phase 2 Upgrade (2026-01-21): Transition from Observer to Active Healer.
Phase 3 Upgrade (2026-01-21): Environmental Maintenance & Root-Level Lockdown.
Phase 4 Upgrade (2026-01-21): Deduplication & Logic Consolidation.
Phase 6 Upgrade (2026-01-21): Universal Logic Consolidation & Healing.
Phase 7 Upgrade (2026-01-21): Final Sovereign Lockdown & CI/CD Integration.
Phase 8 Upgrade (2026-01-28): Golden Baseline & Immutable Snapshotting.
Phase 9 Upgrade (2026-01-21): Golden Baseline Capture & SSOT Normalization.
Phase 10 Upgrade (2026-01-21): Sovereign Convergence & Categorical Drift Audits.

Responsibilities:
- Validate layer boundaries (L0-L6) across ALL sovereign territories
- Detect gravity violations (upward imports: L3 importing L5)
- Enforce naming conventions (*Agent.py suffix)
- Detect orphaned and duplicate agents
- Trigger cross-root deduplication audits
- Perform Categorical Drift Audits (Phase 10)
- Manage Immutable Project Baselines
- Execute Automated Sovereign Purges
- Enforce Universal Sovereignty via Phase 8 Golden Baseline with SHA-256 integrity
- Enforce Universal Sovereignty via CI/CD sync verification
- Support headless CI mode with auto_approve
- [Phase 2] Autonomous healing via GravityLeakRepairAgent orchestration
- [Phase 2] Naming convention auto-fix via ArchivalGatekeeper
- [Phase 3] Post-healing environmental cleanup
- [Phase 4] Cross-agent deduplication audit
- [Phase 6] Zero-loss collision resolution via ArchivalGatekeeper
- [Phase 7] Final CI-ready lockdown verification
- [Phase 8] SHA-256 snapshotting for immutable "Gold Master" state
- [Phase 8] Silent Drift detection (logic changes without naming violations)
- [Phase 8] Immutable audit logs for long-term sovereignty tracking
- [Phase 9] Golden Baseline capture for SSOT normalization
- [Phase 10] Sovereign Convergence terminal command

[SSOT] All territorial scope derived from SOVEREIGN_TERRITORIES in structure_blueprint.py
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.PascalSovereigntyAgent import (
    PascalSovereigntyAgent,
    get_python_files_fast,
)

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout

# [PHASE 24] Integrate L0 Maintenance Capability
from agentic_core.L5_safety.policy_engine.SSOTFolderCleanupAgent import SSOTFolderCleanupAgent
from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

Logger = logging.getLogger(__name__)

# Layer directories from SSOT
LAYER_DIRS: set[str] = set(SOVEREIGN_TERRITORIES.get("agentic_core", {}).get("subfolders", []))


@dataclass
class ArchitectureGovernorAgent(SovereignBaseAgent):
    """
    [L5 GOVERNOR] Universal Architecture Pattern Enforcement

    Phase 1 Upgrade: Activated from stub to functioning enforcer.
    Ensures code follows canonical architectural patterns and layer boundaries
    across ALL sovereign territories (not just agentic_core).

    Features:
    - Universal Scope: Scans all SOVEREIGN_TERRITORIES roots
    - Auto-Approve Mode: Headless CI operation without stdin prompts
    - Gravity Detection: L3 importing L5 = violation
    - Naming Enforcement: *Agent.py suffix validation
    """

    project_root: Path = field(default_factory=Path.cwd)
    healing_enabled: bool = True
    auto_approve: bool = False
    ci_mode: bool = False

    def __post_init__(self) -> None:
        """Initialize the ArchitectureGovernorAgent."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        self.violations: list[dict[str, Any]] = []
        self.stats = {
            "violations_found": 0,
            "violations_fixed": 0,
            "errors": 0,
            "drift_detected": 0,
        }
        self.name = self.__class__.__name__
        self.python_files: list[str] = []

        # Sovereign Data Locations for Phase 8
        self.baseline_dir = self.project_root / "agentic_core" / "config" / "baselines"
        self.audit_log_dir = self.project_root / "logs" / "sovereign_audit"

        self._structure_validator = None  # Lazy-loaded
        self._gravity_repair_agent = None  # Lazy-loaded
        self._archival_gatekeeper = None  # Lazy-loaded
        self._cognitive_agent = None  # Lazy-loaded (Phase 11)
        Logger.info(
            f"ArchitectureGovernorAgent initialized (auto_approve={self.auto_approve}, ci_mode={self.ci_mode})"
        )

    def _get_structure_validator(self):
        """Lazy-load StructuralValidatorAgent to avoid circular imports."""
        if self._structure_validator is None:
            from agentic_core.L5_safety.policy_engine.StructuralValidatorAgent import (
                StructuralValidatorAgent,
                StructureConfig,
            )

            config = StructureConfig(
                check_gravity=True,
                check_duplicates=True,
                check_orphans=True,
                check_registry=False,
                check_contracts=False,
                check_hierarchy=True,
                project_root=self.project_root,
            )
            self._structure_validator = StructuralValidatorAgent(config=config)
        return self._structure_validator

    def _get_gravity_repair_agent(self):
        """Lazy-load GravityLeakRepairAgent for orchestrated healing."""
        if self._gravity_repair_agent is None:
            from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import (
                GravityLeakRepairAgent,
            )

            self._gravity_repair_agent = GravityLeakRepairAgent(project_root=self.project_root)
        return self._gravity_repair_agent

    def _get_archival_gatekeeper(self):
        """Lazy-load ArchivalGatekeeper for safe file operations."""
        if self._archival_gatekeeper is None:
            from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

            self._archival_gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)
        return self._archival_gatekeeper

    def _get_cognitive_agent(self):
        """Lazy-load CognitiveDispositionAgent for AI-powered triage (Phase 11)."""
        if self._cognitive_agent is None:
            from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
                CognitiveDispositionAgent,
            )

            self._cognitive_agent = CognitiveDispositionAgent(
                project_root=self.project_root,
                confidence_threshold=0.75,  # Auto-execute at > 0.75 confidence (unified threshold)
            )
        return self._cognitive_agent

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for architecture violations.

        Args:
            violation: Violation dict with keys: type, file, message, severity, etc.

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

            # Dispatch to appropriate healing method
            if violation_type == "GRAVITY":
                result = self._heal_gravity_violation(violation, auto_approve=True)
                return {
                    "status": "success" if result else "failed",
                    "details": f"Gravity violation healing {'succeeded' if result else 'failed'}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Gravity healing failed"],
                }
            elif violation_type == "NAMING":
                result = self._heal_naming_violation(violation, auto_approve=True)
                return {
                    "status": "success" if result else "failed",
                    "details": f"Naming violation healing {'succeeded' if result else 'failed'}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Naming healing failed"],
                }
            elif violation_type == "DUPLICATE":
                result = self._resolve_collision(violation)
                return {
                    "status": "success" if result else "failed",
                    "details": f"Duplicate resolution {'succeeded' if result else 'failed'}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Duplicate resolution failed"],
                }
            elif violation_type == "ORPHAN":
                file_path_obj = Path(file_path)
                result = self._process_cognitive_disposition(file_path_obj, "ORPHAN")
                return {
                    "status": "success" if result else "failed",
                    "details": f"Orphan file processing {'succeeded' if result else 'failed'}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Orphan processing failed"],
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

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        auto_approve: bool | None = None,
        target_territory: str | None = None,  # [STRICT SCOPE] Target injection point
    ) -> dict[str, Any]:
        """
        Universal architecture governance with optional strict scope targeting.

        Phase 1 Upgrade: Now performs actual validation instead of returning stub.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking
            auto_approve: Override instance auto_approve setting
            target_territory: [STRICT SCOPE] If provided, restricts audit to specific territory

        Returns:
            Dictionary with canonical keys: violations_found, violations_fixed, status
        """
        # Call parent heal_repository with only supported args
        super().heal_repository()

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)

        # Resolve auto_approve
        effective_auto_approve = auto_approve if auto_approve is not None else self.auto_approve

        try:
            Logger.info(f"[{agent_name}] Starting Universal Architecture Governance...")

            violations_found = 0
            violations_fixed = 0
            roots_scanned = []
            all_violations = []

            # [STRICT SCOPE] Filter SOVEREIGN_TERRITORIES to prevent audit bleed
            from agentic_core.L5_safety.validators import (
                structure_blueprint as _structure_blueprint,
            )

            sovereign_territories = _structure_blueprint.SOVEREIGN_TERRITORIES

            if target_territory:
                if target_territory in sovereign_territories and target_territory != "agentic_core":
                    target_roots = [target_territory]
                else:
                    target_roots = ["agentic_core"]
                Logger.info(
                    f"[{agent_name}] TARGETED AUDIT: {target_territory} (Roots: {target_roots})"
                )
            else:
                target_roots = list(sovereign_territories.keys())

            for root_name in target_roots:
                root_path = self.project_root / root_name
                if not root_path.exists():
                    continue

                roots_scanned.append(root_name)
                Logger.info(f"  Scanning territory: {root_name}")

                # Use StructureValidatorAgent for detection
                validator = self._get_structure_validator()
                report = validator.validate_structure(root_path)

                for violation in report.violations:
                    # [REFINEMENT] Intelligent Noise Filtering
                    # Ignore Naming violations for Exception/Error classes often found in Agent files
                    if "must end with 'Agent'" in violation.message:
                        if "'Error'" in violation.message or "'Exception'" in violation.message:
                            continue
                        if "Error'" in violation.message or "Exception'" in violation.message:
                            continue

                    violations_found += 1

                    # [FIX] Robustly handle violation types (Enum vs String) to prevent crashes
                    v_type_raw = getattr(violation, "violation_type", "UNKNOWN")
                    if hasattr(v_type_raw, "name"):
                        v_type_name = v_type_raw.name
                    else:
                        v_type_name = str(v_type_raw)

                    violation_dict = {
                        "type": v_type_name,
                        "file": str(violation.file_path) if violation.file_path else None,
                        "message": violation.message,
                        "severity": getattr(violation, "severity", None),
                        "suggestion": getattr(violation, "suggestion", None),
                        "source_layer": getattr(violation, "source_layer", None),
                        "target_layer": getattr(violation, "target_layer", None),
                    }
                    all_violations.append(violation_dict)

                    # Phase 2: Active Healing
                    if execute and not dry_run and self.healing_enabled:
                        fixed = self._heal_violation(
                            violation_dict,
                            effective_auto_approve,
                        )
                        if fixed:
                            violations_fixed += 1
                    elif not dry_run:
                        Logger.warning(f"    [{v_type_name}] {violation.message}")

            # Store violations for inspection
            self.violations = all_violations

            # Summary
            if dry_run:
                Logger.info(
                    f"[DRY-RUN] Found {violations_found} violations across {len(roots_scanned)} territories"
                )
            else:
                Logger.info(f"Found {violations_found} violations, fixed {violations_fixed}")

            # Phase 9/10: Categorical Audit Reporting - Shield Alert
            if violations_found > 0 and not execute:
                Logger.warning(
                    f"[{agent_name}] SHIELD ALERT: {violations_found} violations blocking baseline purity."
                )

            # Phase 10: Convergence - Categorical Drift Analysis
            if violations_found > 0:
                self._log_categorical_drift(all_violations)

            # Phase 4/6: Logic Consolidation & Deduplication Audit with Resolution
            dedup_results = self._trigger_deduplication_audit(
                roots_scanned, execute=execute and not dry_run
            )

            # Phase 3: Post-Healing Environmental Maintenance
            if self.healing_enabled and execute and not dry_run and violations_fixed > 0:
                Logger.info("[Phase 3] Running post-healing cleanup...")
                for root_name in roots_scanned:
                    self._cleanup_empty_dirs(self.project_root / root_name)

            # [PHASE 24] Sub-routine: SSOT Folder Cleanup
            # Delegate physical reorganization to the specialized L5 agent
            ssot_moves = 0
            ssot_imports_updated = 0
            if not dry_run:
                try:
                    Logger.info(
                        f"[{agent_name}] Initiating SSOT Folder Cleanup (dry_run={dry_run})..."
                    )
                    janitor = SSOTFolderCleanupAgent(
                        project_root=self.project_root, dry_run=dry_run
                    )

                    # Execute cleanup (or preview)
                    cleanup_stats = janitor.cleanup_repository()

                    # Merge statistics
                    ssot_moves = cleanup_stats.get("files_moved", 0)
                    ssot_imports_updated = cleanup_stats.get("imports_updated", 0)
                    violations_fixed += ssot_moves

                    if cleanup_stats.get("errors", 0) > 0:
                        Logger.warning(
                            f"[{agent_name}] SSOT Cleanup reported errors: {cleanup_stats['errors']}"
                        )

                except Exception as e:
                    Logger.error(f"[{agent_name}] SSOT Cleanup Sub-routine failed: {e}")

            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "roots_scanned": roots_scanned,
                "status": "PASS" if violations_found == 0 else "FAIL",
                "deduplication_audit": dedup_results,
                "ssot_moves": ssot_moves,
                "ssot_imports_updated": ssot_imports_updated,
            }
        finally:
            _call_path.discard(agent_name)

    def run_ci_verification_sync(self) -> tuple[bool, dict[str, Any]]:
        """
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Returns (is_compliant, results_dict) for easy CI integration.
        No stdin prompts - fully headless operation.
        """
        Logger.info("Starting Architecture CI Verification (headless mode)...")

        results = self.heal_repository(
            dry_run=True,
            execute=False,
            auto_approve=True,
        )

        is_compliant = results.get("violations_found", 0) == 0

        if is_compliant:
            Logger.info("✅ Architecture Integrity Verified. No violations.")
        else:
            Logger.error(
                f"❌ Architecture violations detected: {results.get('violations_found', 0)}"
            )

        return is_compliant, results

    def run_audit(self, target_territories: list[str] | None = None) -> dict[str, Any]:
        """
        Executes a comprehensive structural and naming audit with Phase 8 Drift Detection.
        In CI mode, this returns a non-zero-weighted success status.

        Args:
            target_territories: [STRICT SCOPE] Optional list of specific paths/domains to audit.
        """
        Logger.info(
            f"🚀 Starting Sovereign Audit (CI_MODE: {self.ci_mode}, SCOPE: {target_territories or 'GLOBAL'})"
        )

        # [EFFICIENCY] Logic consolidated to scan all L5 Guardians in one pass
        structural_results = self._orchestrate_guardian_scan(target_territories)

        # [PHASE 8] Integrity Scan for Silent Drift
        # Only check drift if we are doing a global scan or if the drift checker supports partials
        # For now, we only run full drift check on global scans to prevent false positives on partials
        drift_violations = []
        if not target_territories:
            drift_violations = self._check_baseline_drift()

        # 3. Aggregation
        total_violations = structural_results.get("total_violations", 0) + len(drift_violations)

        self.stats.update(
            {
                "violations_found": total_violations,
                "drift_detected": len(drift_violations),
                "errors": structural_results.get("total_errors", 0),
            }
        )

        # [PHASE 8] Observability - Persist audit report
        self._persist_audit_report(structural_results, drift_violations)

        # [SIGNAL] Define failure threshold
        success = self.stats["violations_found"] == 0 and self.stats["errors"] == 0

        if self.ci_mode and not success:
            Logger.critical(
                f"🛑 CI FAILURE: {self.stats['violations_found']} violations (Drift: {len(drift_violations)})"
            )

        return {
            "success": success,
            "stats": self.stats,
            "violations": structural_results.get("violation_details", []),
            "drift_violations": drift_violations,
        }

    def _orchestrate_guardian_scan(
        self, target_territories: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Orchestrate scanning of all L5 Guardians in one pass.
        Internal method for run_audit to consolidate scanning logic.

        Now supports [STRICT SCOPE] targeting via target_territories.
        """
        total_violations = 0
        total_errors = 0
        violation_details = []
        roots_scanned = []

        try:
            # [STRICT SCOPE] Determine Audit Scope
            if target_territories:
                # Explicitly only scan the requested targets
                scan_targets = []
                for t in target_territories:
                    # Logic to resolve path (same as above, just ensuring it's robust)
                    p_core = self.project_root / "agentic_core" / t
                    p_root = self.project_root / t

                    if p_core.exists():
                        scan_targets.append(p_core)
                    elif p_root.exists():
                        scan_targets.append(p_root)
                    else:
                        Logger.warning(f"⚠️ Target territory not found: {t}")
            else:
                # GLOBAL SCOPE: Only runs if NO targets are provided
                scan_targets = [self.project_root / k for k in SOVEREIGN_TERRITORIES.keys()]

            for root_path in scan_targets:
                if not root_path.exists():
                    continue

                root_name = root_path.name
                roots_scanned.append(str(root_path.relative_to(self.project_root)))
                Logger.info(f"  Scanning territory: {roots_scanned[-1]}")

                # Use StructureValidatorAgent for detection
                validator = self._get_structure_validator()
                report = validator.validate_structure(root_path)

                # [UNIFIED AUDIT] Ingest Physical Hierarchy Violations
                try:
                    from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

                    hierarchy = HierarchyAgent(project_root=self.project_root)
                    # Scan specifically for files sitting in the root that shouldn't be there
                    h_report = hierarchy.scan_root_violations(target_territory=root_name)

                    for h_violation in h_report.get("violations", []):
                        total_violations += 1
                        violation_details.append(
                            {
                                "type": "STRUCTURE",
                                "file": h_violation.get("file"),
                                "message": "File sitting in territory root. Should be in SSOT subfolder.",
                                "severity": "ERROR",
                                "suggestion": "Relocate to approved subfolder (agents/, registry/, etc.)",
                            }
                        )
                except Exception as e:
                    Logger.warning(f"Hierarchy cross-check failed for {root_name}: {e}")

                for violation in report.violations:
                    # [REFINEMENT] Intelligent Noise Filtering
                    # Ignore Naming violations for Exception/Error classes often found in Agent files
                    if "must end with 'Agent'" in violation.message:
                        if "'Error'" in violation.message or "'Exception'" in violation.message:
                            continue
                        if "Error'" in violation.message or "Exception'" in violation.message:
                            continue

                    total_violations += 1

                    # [FIX] Robustly handle violation types (Enum vs String) to prevent crashes
                    v_type_raw = getattr(violation, "violation_type", "UNKNOWN")
                    if hasattr(v_type_raw, "name"):
                        v_type_name = v_type_raw.name
                    else:
                        v_type_name = str(v_type_raw)

                    violation_dict = {
                        "type": v_type_name,
                        "file": str(violation.file_path) if violation.file_path else None,
                        "message": violation.message,
                        "severity": getattr(violation, "severity", None),
                        "suggestion": getattr(violation, "suggestion", None),
                        "source_layer": getattr(violation, "source_layer", None),
                        "target_layer": getattr(violation, "target_layer", None),
                    }
                    violation_details.append(violation_dict)

        except Exception as e:
            Logger.error(f"Guardian scan failed: {e}")
            total_errors += 1

        return {
            "total_violations": total_violations,
            "total_errors": total_errors,
            "violation_details": violation_details,
            "roots_scanned": roots_scanned,
        }

    def validate_layer_boundaries(self, file_path: Path) -> tuple[bool, str]:
        """
        [PHASE 22] Validate that file respects layer boundaries (L0-L6) using Cognitive Triage.

        Integrates CognitiveDispositionAgent for intelligent violation analysis.
        Falls back to structural checks if cognitive triage is unavailable.

        Args:
            file_path: Path to file to validate

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts

            # Check agentic_core layer structure
            if len(parts) > 1 and parts[0] == "agentic_core":
                if len(parts) > 2 and parts[1] in LAYER_DIRS:
                    return (True, f"Valid layer structure: {parts[1]}")
                # Invalid layer - invoke Cognitive Triage
                return self._cognitive_triage_validation(file_path, "ORPHAN")

            # Check other sovereign territories
            if parts[0] in SOVEREIGN_TERRITORIES:
                return (True, f"Valid sovereign territory: {parts[0]}")

            # File outside sovereign territories - invoke Cognitive Triage
            return self._cognitive_triage_validation(file_path, "ORPHAN")

        except ValueError:
            return (False, "File outside project root")

    def _cognitive_triage_validation(
        self,
        file_path: Path,
        violation_type: str,
    ) -> tuple[bool, str]:
        """
        [PHASE 22] Invoke CognitiveDispositionAgent for intelligent violation analysis.

        Args:
            file_path: Path to the file with potential violation
            violation_type: Type of violation (ORPHAN, GRAVITY, etc.)

        Returns:
            Tuple of (is_valid, reason) with cognitive triage recommendation
        """
        try:
            cognitive = self._get_cognitive_agent()
            decision = cognitive.analyze_violation(file_path, violation_type)

            if decision.action == "IGNORE":
                return (True, f"False positive identified by Cognitive Triage: {decision.reason}")

            # Build detailed reason with recommendation
            reason = (
                f"Structural violation: {decision.reason}. Recommended Action: {decision.action}"
            )
            if decision.target_path:
                reason += f" to {decision.target_path}"
            reason += f" (confidence: {decision.confidence:.2f})"

            return (False, reason)

        except Exception as e:
            # Fallback to simple structural check if cognitive triage fails
            Logger.warning(f"Cognitive triage failed, using fallback: {e}")
            return (False, "File outside sovereign territories (cognitive triage unavailable)")

    def validate_architectural_patterns(self, file_path: Path) -> dict[str, Any]:
        """
        Validate architectural patterns in a file.

        Args:
            file_path: Path to file to validate

        Returns:
            Dictionary with validation results
        """
        is_valid, reason = self.validate_layer_boundaries(file_path)
        return {
            "file": str(file_path),
            "valid": is_valid,
            "reason": reason,
            "violations": self.violations,
        }

    def run_validation(self, files: list[Path]) -> dict[str, Any]:
        """
        Run architecture validation on multiple files.

        Args:
            files: List of file paths to validate

        Returns:
            Summary of validation results
        """
        results: Any = []
        total_violations: Any = 0
        for file_path in files:
            result: Any = self.validate_architectural_patterns(file_path)
            results.append(result)
            if not result["valid"]:
                total_violations += 1
        return {"total_files": len(files), "total_violations": total_violations, "results": results}

    # =========================================================================
    # PHASE 2: ACTIVE HEALING METHODS
    # =========================================================================

    def _heal_violation(
        self,
        violation: dict[str, Any],
        auto_approve: bool,
    ) -> bool:
        """
        Attempt to heal a single violation.

        Phase 2: Dispatches to appropriate healer based on violation type.

        Args:
            violation: Violation dict with type, file, message, etc.
            auto_approve: If True, skip interactive prompts

        Returns:
            True if violation was fixed, False otherwise
        """
        violation_type = violation.get("type", "")
        file_path = violation.get("file")

        if not file_path:
            Logger.warning(f"Cannot heal violation without file path: {violation}")
            return False

        file_path = Path(file_path)

        # Dispatch to appropriate healer
        if violation_type == "GRAVITY":
            result = self._heal_gravity_violation(violation, auto_approve)
            if not result:
                # Phase 11: Fallback to cognitive disposition if deterministic repair fails
                return self._process_cognitive_disposition(file_path, "GRAVITY_FAIL")
            return result
        elif violation_type == "NAMING":
            return self._heal_naming_violation(violation, auto_approve)
        elif violation_type == "DUPLICATE":
            # Phase 11: Use collision resolution instead of skipping
            return self._resolve_collision(violation)
        elif violation_type == "ORPHAN":
            # Phase 11: Intelligent Triage via CognitiveDispositionAgent
            return self._process_cognitive_disposition(file_path, "ORPHAN")
        else:
            Logger.debug(f"  [SKIP] No healer for violation type: {violation_type}")
            return False

    def _heal_gravity_violation(
        self,
        violation: dict[str, Any],
        auto_approve: bool,
    ) -> bool:
        """
        Heal a gravity violation by orchestrating GravityLeakRepairAgent.

        Phase 2: Governor acts as executive that decides WHEN to trigger repair.

        Args:
            violation: Gravity violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        """
        file_path = violation.get("file")
        source_layer = violation.get("source_layer")
        target_layer = violation.get("target_layer")

        if not file_path:
            return False

        Logger.info(f"  [GRAVITY] Attempting repair: {Path(file_path).name}")
        Logger.info(f"    Source layer: {source_layer} -> Target layer: {target_layer}")

        try:
            # Orchestrate GravityLeakRepairAgent
            repair_agent = self._get_gravity_repair_agent()

            # Analyze the specific violation
            fix = repair_agent.analyze_violation(
                file_path=Path(file_path),
                import_statement=violation.get("message", ""),
                file_layer=source_layer or "",
                import_layer=target_layer or "",
            )

            Logger.info(f"    Fix type: {fix.fix_type}")
            Logger.info(f"    Rationale: {fix.rationale}")

            # Apply fix if auto_approve or get approval
            if auto_approve:
                result = repair_agent.apply_fix(fix, dry_run=False)
                if result.get("status") == "fixed":
                    Logger.info(f"    ✅ Fixed via {fix.fix_type}")
                    return True
                else:
                    Logger.warning(f"    ⚠️ Fix not applied: {result.get('status')}")
                    return False
            else:
                # Log recommendation but don't apply without approval
                Logger.info(f"    [RECOMMENDATION] {fix.fix_type}: {fix.new_import}")
                return False

        except Exception as e:
            Logger.error(f"    ❌ Gravity repair failed: {e}")
            return False

    def _heal_naming_violation(
        self,
        violation: dict[str, Any],
        auto_approve: bool,
    ) -> bool:
        """
        Heal a naming convention violation via ArchivalGatekeeper safe rename.

        Phase 2: Fixes files missing *Agent.py suffix.

        Args:
            violation: Naming violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        """
        file_path = violation.get("file")
        if not file_path:
            return False

        file_path = Path(file_path)

        # Check if this is a missing Agent suffix violation
        if not file_path.name.endswith("Agent.py") and "Agent" in violation.get("message", ""):
            # Determine new name
            stem = file_path.stem
            if stem.endswith("Agent"):
                # Already has Agent suffix, just wrong extension?
                return False

            # Add Agent suffix
            new_name = f"{stem}Agent.py"
            new_path = file_path.parent / new_name

            Logger.info(f"  [NAMING] Attempting rename: {file_path.name} -> {new_name}")

            if new_path.exists():
                Logger.warning(f"    ⚠️ Target already exists: {new_path}")
                return False

            if auto_approve:
                try:
                    gatekeeper = self._get_archival_gatekeeper()
                    # Use batch mode for auto_approve
                    gatekeeper.set_require_approval(False)

                    result = gatekeeper.safe_move(
                        source=file_path,
                        destination=new_path,
                        requester_agent="ArchitectureGovernorAgent",
                        reason="Naming convention fix: add Agent suffix",
                    )

                    if result.success:
                        Logger.info(f"    ✅ Renamed to {new_name}")
                        return True
                    else:
                        Logger.warning(f"    ⚠️ Rename failed: {result.error}")
                        return False

                except Exception as e:
                    Logger.error(f"    ❌ Rename failed: {e}")
                    return False
            else:
                Logger.info(f"    [RECOMMENDATION] Rename to: {new_name}")
                return False

        return False

    # =========================================================================
    # PHASE 4/6: DEDUPLICATION & LOGIC CONSOLIDATION WITH HEALING
    # =========================================================================

    def _trigger_deduplication_audit(
        self, roots: list[str], execute: bool = False
    ) -> dict[str, Any]:
        """
        [PHASE 4/6] Identify and resolve redundant logic across roots.

        Scans all sovereign roots for duplicate agent definitions and
        redundant code patterns. When execute=True and auto_approve=True,
        resolves collisions via zero-loss merge using ArchivalGatekeeper.

        Args:
            roots: List of root names that were scanned
            execute: If True, attempt to resolve collisions

        Returns:
            Dictionary with audit results including collisions found/fixed
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] Triggering Deduplication Audit...")

        collisions: list[dict[str, Any]] = []

        # Use the structure validator to check for duplicates
        validator = self._get_structure_validator()

        for root_name in roots:
            root_path = self.project_root / root_name
            if not root_path.exists():
                continue

            # Check for duplicate agents in this root
            duplicates = validator.check_duplicates(root_path)
            for dup in duplicates:
                collisions.append(
                    {
                        "root": root_name,
                        "type": "DUPLICATE_AGENT",
                        "message": dup.message,
                        "file": str(dup.file_path) if dup.file_path else None,
                        "violation": dup,  # Keep original for resolution
                    }
                )

        # Phase 6: Collision Resolution
        collisions_fixed = 0
        if execute and self.auto_approve and self.healing_enabled and collisions:
            Logger.info(f"  [DEDUP] Attempting to resolve {len(collisions)} collisions...")
            for collision in collisions:
                violation = collision.get("violation")
                if violation:
                    fixed = self._resolve_collision(violation)
                    collisions_fixed += fixed

        if collisions:
            Logger.warning(
                f"  [DEDUP] Found {len(collisions)} potential collisions, fixed {collisions_fixed}"
            )
        else:
            Logger.info(f"  [DEDUP] No collisions found across {len(roots)} roots")

        return {
            "roots_audited": roots,
            "collisions_found": len(collisions),
            "collisions_fixed": collisions_fixed,
            "collisions": collisions[:10] if collisions else [],  # Limit to first 10
        }

    def _resolve_collision(self, violation: Any) -> int:
        """
        [PHASE 6] Zero-loss merge: Archives lower-priority duplicates.

        Priority order (highest to lowest):
        - agentic_core (0) - Master source
        - apps_shared (1) - Shared utilities
        - apps_rg (2) - Resume Generator app
        - apps_lic (3) - LinkedIn app
        - tests (4) - Test files
        - scripts (5) - Scripts

        Args:
            violation: StructureViolation with duplicate locations

        Returns:
            Number of files archived (0 if no action taken)
        """
        # Priority mapping for resolution
        priority = {
            "agentic_core": 0,
            "apps_shared": 1,
            "apps_rg": 2,
            "apps_lic": 3,
            "tests": 4,
            "scripts": 5,
        }

        # Extract paths from violation
        files = getattr(violation, "locations", [])
        if not files:
            # Try alternate attribute names
            files = getattr(violation, "file_paths", [])
        if not files:
            # Single file path
            single_path = getattr(violation, "file_path", None)
            if single_path:
                files = [single_path]

        if len(files) < 2:
            return 0

        # Convert to Path objects if needed
        files = [Path(f) if not isinstance(f, Path) else f for f in files]

        # Sort by priority (keep highest priority = lowest number)
        def get_priority(p: Path) -> int:
            try:
                rel_path = p.relative_to(self.project_root)
                root = rel_path.parts[0] if rel_path.parts else ""
                return priority.get(root, 99)
            except ValueError:
                return 99

        sorted_files = sorted(files, key=get_priority)

        master = sorted_files[0]
        to_archive = sorted_files[1:]

        archived_count = 0
        gatekeeper = self._get_archival_gatekeeper()

        for file_path in to_archive:
            try:
                result = gatekeeper.safe_move(
                    file_path,
                    destination_category="deduplication_cleanup",
                    reason=f"Duplicate of {master.name}",
                )
                if result.success:
                    Logger.info(f"  [DEDUP] Archived {file_path.name} in favor of {master.name}")
                    archived_count += 1
                else:
                    Logger.warning(f"  [DEDUP] Failed to archive {file_path.name}: {result.error}")
            except Exception as e:
                Logger.error(f"  [DEDUP] Error archiving {file_path.name}: {e}")

        return archived_count

    # =========================================================================
    # PHASE 3: ENVIRONMENTAL MAINTENANCE
    # =========================================================================

    def _cleanup_empty_dirs(self, path: Path) -> None:
        """
        Recursively remove empty directories after healing operations.

        Phase 3: Post-healing environmental maintenance to purge ghost directories
        left behind after renames or refactors.

        Args:
            path: Root path to start cleanup from
        """
        if not path.is_dir():
            return

        # Recurse into subdirectories first (depth-first)
        for child in list(path.iterdir()):
            if child.is_dir():
                self._cleanup_empty_dirs(child)

        # Check if directory is now empty (ignoring sentinels and hidden files)
        remaining = [
            p
            for p in path.iterdir()
            if p.name not in {"__pycache__", "__init__.py", ".gitkeep"}
            and not p.name.startswith(".")
        ]

        if not remaining:
            try:
                # Purge sentinels before removing directory
                for sentinel in [path / "__init__.py", path / ".gitkeep"]:
                    if sentinel.exists():
                        sentinel.unlink()

                # Remove __pycache__ if present
                pycache = path / "__pycache__"
                if pycache.exists():
                    import shutil

                    shutil.rmtree(pycache, ignore_errors=True)

                path.rmdir()
                try:
                    rel_path = path.relative_to(self.project_root)
                    Logger.info(f"  [CLEANUP] Removed empty directory: {rel_path}")
                except ValueError:
                    Logger.info(f"  [CLEANUP] Removed empty directory: {path}")
            except OSError:
                pass  # Directory not empty or permission denied

    # =========================================================================
    # PHASE 7: FINAL SOVEREIGN LOCKDOWN & CI/CD INTEGRATION
    # =========================================================================

    def finalize_sovereign_lockdown(self) -> tuple[bool, dict]:
        """
        [PHASE 7] Final CI-ready lockdown verification.

        Performs a non-blocking sync check to ensure the repository state
        perfectly matches the Sovereign SSOT. Designed for CI/CD pipelines
        and pre-commit hooks.

        Returns:
            Tuple of (is_pure: bool, results: dict)
            - is_pure: True if repository has 0 violations
            - results: Full heal_repository results for inspection

        Usage in CI:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            is_pure, results = agent.finalize_sovereign_lockdown()
            sys.exit(0 if is_pure else 1)
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] Initiating Final Sovereign Lockdown...")

        # Run dry-run audit to check current state
        results = self.heal_repository(
            dry_run=True,
            execute=False,
        )

        # Extract violations from normalized result
        raw_result = results.get("_raw_result", results)
        violations_found = raw_result.get("violations_found", 0)

        is_pure = violations_found == 0

        if is_pure:
            Logger.info(f"[{agent_name}] ✅ LOCKDOWN VERIFIED: Repository is sovereign-compliant")
        else:
            Logger.warning(
                f"[{agent_name}] ❌ LOCKDOWN FAILED: {violations_found} violations detected"
            )

        return is_pure, results

    # =========================================================================
    # PHASE 8: GOLDEN BASELINE & IMMUTABLE SNAPSHOTTING
    # =========================================================================

    def capture_golden_baseline(self) -> Path:
        """
        [PHASE 8] Generates a SHA-256 manifest of all files in sovereign territories.
        This represents the 'Gold Master' state of the repository.
        """
        Logger.info("📸 CAPTURING GOLDEN BASELINE...")

        # 1. Initialize Manifest
        manifest = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "audit_id": str(uuid.uuid4()),
            "files": {},
        }

        # 2. fast-scan the repository using the Phase 3 agent logic
        # We instantiate it temporarily just to use its optimized scanner
        PascalSovereigntyAgent(self.project_root)
        files = get_python_files_fast(self.project_root)

        # 3. Calculate Hashes
        for file_path in files:
            try:
                relative_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
                # Binary read ensures hash stability across OS line-ending differences
                file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                manifest["files"][relative_path] = file_hash
            except Exception as e:
                Logger.warning(f"Skipping file {file_path.name} in baseline: {e}")

        # 4. Atomic Write
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        baseline_path = self.baseline_dir / "golden_baseline.json"

        temp_path = baseline_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)
        temp_path.replace(baseline_path)

        Logger.info(f"✅ BASELINE CAPTURED: {len(manifest['files'])} files tracked.")
        return baseline_path

    def _check_baseline_drift(self) -> list[dict[str, Any]]:
        """[PHASE 8] Compares live files against the Golden Baseline."""
        baseline_path = self.baseline_dir / "golden_baseline.json"
        if not baseline_path.exists():
            Logger.warning("⚠️ No Golden Baseline found. Skipping integrity check.")
            return []

        violations = []
        try:
            with open(baseline_path) as f:
                baseline = json.load(f)

            # Check for Modified or Missing files
            for rel_path, expected_hash in baseline["files"].items():
                full_path = self.project_root / rel_path

                if not full_path.exists():
                    violations.append(
                        {"type": "MISSING_FILE", "path": rel_path, "severity": "CRITICAL"}
                    )
                    continue

                current_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
                if current_hash != expected_hash:
                    violations.append(
                        {
                            "type": "CONTENT_DRIFT",
                            "path": rel_path,
                            "expected": expected_hash,
                            "actual": current_hash,
                            "severity": "CRITICAL",
                        }
                    )

            # Check for Ghost Files (Files on disk but not in baseline)
            # (Optional: Can be expensive, omitted for speed in this iteration)

        except Exception as e:
            Logger.error(f"Drift check failed: {e}")

        return violations

    def _persist_audit_report(
        self, structural_results: dict[str, Any], drift_violations: list[dict[str, Any]]
    ) -> None:
        """[PHASE 8] Saves immutable audit record."""
        self.audit_log_dir.mkdir(parents=True, exist_ok=True)

        {
            "timestamp": datetime.utcnow().isoformat(),
            "audit_id": str(uuid.uuid4()),
            "structural_summary": structural_results,
            "drift_violations": drift_violations,
            "stats": self.stats,
        }

        # Audit logging removed - sovereign_audit files create unnecessary sprawl
        # Compliance reports are handled by execute_ssot.py in logs/compliance_reports/

    # =========================================================================
    # PHASE 9: GOLDEN BASELINE CAPTURE & SSOT NORMALIZATION
    # =========================================================================

    def capture_sovereign_baseline(self) -> dict[str, Any]:
        """
        [PHASE 9] Captures the post-purge state as the new SSOT baseline.

        This establishes the zero-violation benchmark for all future
        CI/CD enforcement gates. Should be called after a successful
        purge execution to lock in the clean state.

        Returns:
            Dictionary containing the baseline state with violation counts
            and root scan results.

        Usage:
            # After purge execution
            agent.heal_repository(execute=True, dry_run=False)

            # Capture the clean state as baseline
            baseline = agent.capture_sovereign_baseline()
            assert baseline.get("violations_found", 0) == 0
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] Capturing Golden Baseline...")

        # Run dry-run audit to capture current state
        baseline_state = self.heal_repository(dry_run=True)

        # Extract violations from normalized result
        raw_result = baseline_state.get("_raw_result", baseline_state)
        violations_found = raw_result.get("violations_found", 0)

        if violations_found > 0:
            Logger.warning(
                f"[{agent_name}] Baseline captured with {violations_found} unresolved violations."
            )
        else:
            Logger.info(f"[{agent_name}] ✅ Golden Baseline captured: 0 violations")

        return baseline_state

    # =========================================================================
    # PHASE 10: SOVEREIGN CONVERGENCE & CATEGORICAL DRIFT AUDITS
    # =========================================================================

    def _log_categorical_drift(self, violations: list[Any]) -> dict[str, int]:
        """
        [PHASE 10] Generates a diagnostic breakdown of architectural debt.

        Categorizes violations by type for targeted remediation.

        Args:
            violations: List of violation objects or dictionaries

        Returns:
            Dictionary with counts per violation category
        """
        agent_name = self.__class__.__name__

        report = {"GRAVITY": 0, "NAMING": 0, "ORPHAN": 0, "DUPLICATE": 0, "OTHER": 0}

        for v in violations:
            # Handle both dict and object violations
            if isinstance(v, dict):
                v_type = v.get("type", "OTHER")
            else:
                v_type = getattr(v, "violation_type", None)
                if v_type:
                    v_type = v_type.name if hasattr(v_type, "name") else str(v_type)
                else:
                    v_type = "OTHER"

            # Normalize type name
            v_type = str(v_type).upper()
            if v_type in report:
                report[v_type] += 1
            else:
                report["OTHER"] += 1

        Logger.warning(f"[{agent_name}] Drift Analysis: {report}")
        return report

    def execute_sovereign_convergence(self) -> dict[str, Any]:
        """
        [PHASE 10] Final convergence: Purge all drift and seal the baseline.

        This is the terminal command for the L5 safety transition.
        Executes a full purge followed by baseline lockdown verification.

        Returns:
            Dictionary containing:
            - purge_status: Results from heal_repository execution
            - lockdown_status: Tuple of (is_pure, results) from lockdown
            - final_purity: Boolean indicating if repository is clean

        Usage:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            result = agent.execute_sovereign_convergence()
            assert result["final_purity"] is True
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] INITIATING SOVEREIGN CONVERGENCE...")

        # Step 1: Full Purge - Execute healing with auto_approve
        purge_results = self.heal_repository(
            execute=True,
            dry_run=False,
        )

        # Step 2: Baseline Capture & Lockdown Verification
        lockdown_result = self.finalize_sovereign_lockdown()
        is_pure, lockdown_details = lockdown_result

        # Step 3: Report final status
        if is_pure:
            Logger.info(f"[{agent_name}] ✅ SOVEREIGN CONVERGENCE COMPLETE: Repository is pure.")
        else:
            raw_result = lockdown_details.get("_raw_result", lockdown_details)
            remaining = raw_result.get("violations_found", 0)
            Logger.warning(
                f"[{agent_name}] ⚠️ CONVERGENCE INCOMPLETE: {remaining} violations remain."
            )

        return {
            "purge_status": purge_results,
            "lockdown_status": lockdown_result,
            "final_purity": is_pure,
        }

    def execute_cognitive_purge(
        self,
        checkpoint_file: str = "cognitive_checkpoint.json",
        rate_limit_delay: float = 1.0,
    ) -> dict[str, Any]:
        """
        [PHASE 13] Execute AI-driven purge using Cognitive Batch Processor.

        Processes all violations through Gemini LLM with:
        - Rate limiting to respect API quotas
        - Progress checkpointing for resumable execution
        - Exponential backoff for API errors

        Args:
            checkpoint_file: Path to checkpoint file for progress tracking
            rate_limit_delay: Seconds to wait between API calls

        Returns:
            Dictionary with batch processing statistics
        """
        agent_name = self.__class__.__name__

        Logger.info(f"[{agent_name}] INITIATING COGNITIVE PURGE...")
        Logger.info("=" * 60)

        # Step 1: Gather all violations (dry run)
        Logger.info(f"[{agent_name}] Scanning for violations...")
        self.heal_repository(dry_run=True)

        # Extract violations from results
        violations = getattr(self, "violations", [])

        if not violations:
            Logger.info(f"[{agent_name}] No violations found. Repository is clean.")
            return {
                "violations_found": 0,
                "batch_stats": {"PROCESSED": 0, "SKIPPED": 0, "ERRORS": 0, "TOTAL": 0},
            }

        Logger.info(f"[{agent_name}] Found {len(violations)} violations to process")

        # Step 2: Initialize Batch Processor
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )

        cognitive = self._get_cognitive_agent()
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=checkpoint_file,
            rate_limit_delay=rate_limit_delay,
        )

        # Step 3: Process batch
        Logger.info(f"[{agent_name}] Starting batch processing...")
        batch_stats = processor.process_batch(violations)

        # Step 4: Get statistics
        results_stats = processor.get_statistics()

        Logger.info("=" * 60)
        Logger.info(f"[{agent_name}] COGNITIVE PURGE COMPLETE")
        Logger.info(f"[{agent_name}] Total Analyzed: {results_stats['total']}")
        Logger.info(f"[{agent_name}] Average Confidence: {results_stats['avg_confidence']:.2%}")
        Logger.info(f"[{agent_name}] Actions by Type:")
        for action, count in sorted(results_stats["by_action"].items()):
            Logger.info(f"    {action}: {count}")
        Logger.info("=" * 60)

        return {
            "violations_found": len(violations),
            "batch_stats": batch_stats,
            "results_stats": results_stats,
            "checkpoint_file": checkpoint_file,
        }

    # =========================================================================
    # PHASE 11: COGNITIVE DISPOSITION - AI-POWERED TRIAGE
    # =========================================================================

    def comprehensive_territory_audit(
        self,
        target_territories: list[str],
        check_layer_boundaries: bool = True,
        check_naming_conventions: bool = True,
    ) -> dict[str, Any]:
        """
        [HARDENED] Unified Compliance Audit.
        Aggregates output from Hierarchy, Location, and SystemArchitect agents into a single JSON manifest.
        """
        Logger.info(f"🎯 INITIATING UNIFIED AUDIT: {target_territories}")

        # 1. Base Naming/Drift Audit
        audit_results = self.run_audit(target_territories=target_territories)

        # Ensure violations list exists
        if "violations" not in audit_results:
            audit_results["violations"] = []

        # 2. Ingest Hierarchy (Physical Placement)
        try:
            from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

            hierarchy = HierarchyAgent(project_root=self.project_root)
            for territory in target_territories:
                h_report = hierarchy.scan_root_violations(target_territory=territory)
                for v in h_report.get("violations", []):
                    audit_results["violations"].append(
                        {
                            "type": "STRUCTURE",
                            "file": v.get("file"),
                            "message": "File sitting in territory root; must be in SSOT subfolder.",
                            "severity": "ERROR",
                        }
                    )
        except Exception as e:
            Logger.warning(f"Unified Audit: Hierarchy ingestion failed: {e}")

        # 3. Ingest System Architect (Circular Dependencies/Gravity)
        try:
            from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent

            architect = SystemArchitectAgent(project_root=self.project_root)
            for territory in target_territories:
                path = f"agentic_core/{territory}"
                arch_report = architect.validate_core_architecture(path)
                if not arch_report.get("imports_valid", True):
                    for circ in arch_report.get("circular_dependencies", []):
                        audit_results["violations"].append(
                            {
                                "type": "GRAVITY",
                                "file": territory,
                                "message": f"Circular dependency detected: {circ}",
                                "severity": "CRITICAL",
                            }
                        )
        except Exception as e:
            Logger.warning(f"Unified Audit: Architecture ingestion failed: {e}")

        # Update Total Stats
        audit_results["stats"]["violations_found"] = len(audit_results["violations"])
        audit_results["target_territories"] = target_territories

        return audit_results

    def generate_healing_plan(self, gov_report: dict[str, Any]) -> dict[str, Any]:
        """
        Generates a healing plan based on the governance report.
        Now recognizes STRUCTURE violations (Root Files) and GRAVITY violations.
        """
        Logger.info("🔧 Generating healing plan from governance report")

        # [INTEGRATION] Analyze violation types
        violations = gov_report.get("violations", [])
        has_naming = any(v.get("type") == "NAMING" for v in violations)
        has_structure = any(v.get("type") == "STRUCTURE" for v in violations)
        has_gravity = any(v.get("type") == "GRAVITY" for v in violations)

        plan = {
            "actions": [],
            "requires_healing": (len(violations) > 0),
            "violations_count": gov_report.get("stats", {}).get("violations_found", 0),
            "drift_count": gov_report.get("stats", {}).get("drift_detected", 0),
            "errors_count": gov_report.get("stats", {}).get("errors", 0),
            "target_territories": gov_report.get("target_territories", []),
            # Pass detailed breakdowns for the executor
            "naming_fixes": [v for v in violations if v.get("type") == "NAMING"],
            "structure_fixes": [v for v in violations if v.get("type") == "STRUCTURE"],
        }

        # Add specific healing actions
        if has_naming:
            plan["actions"].append("Rename Non-Compliant Agent Classes")
        if has_structure:
            plan["actions"].append("Relocate Root Files to SSOT Subfolders")
        if has_gravity:
            plan["actions"].append("Repair Circular Dependencies")

        if not plan["actions"]:
            plan["actions"].append("No healing required - system is compliant")

        Logger.info(f"Generated healing plan with {len(plan['actions'])} actions")
        return plan

        Logger.info(f"Generated healing plan with {len(plan['actions'])} actions")
        return plan

    def _process_cognitive_disposition(
        self,
        file_path: Path,
        violation_type: str,
    ) -> bool:
        """
        [PHASE 11] Delegates violation decision to CognitiveDispositionAgent.

        Uses AI-powered heuristics to determine the appropriate action for
        violations that cannot be resolved deterministically.

        Args:
            file_path: Path to the file with the violation
            violation_type: Type of violation (ORPHAN, GRAVITY_FAIL, etc.)

        Returns:
            True if the violation was resolved, False otherwise
        """
        cognitive = self._get_cognitive_agent()

        Logger.info(f"  [COGNITIVE] Analyzing: {file_path.name} ({violation_type})")

        try:
            decision = cognitive.analyze_violation(file_path, violation_type)

            Logger.info(f"    Decision: {decision.action} (confidence: {decision.confidence:.2f})")
            Logger.info(f"    Reason: {decision.reason}")

            # Execute based on decision action
            if decision.action == "MOVE" and decision.target_path:
                target = self.project_root / decision.target_path / file_path.name
                Logger.info(f"    [COGNITIVE] Moving {file_path.name} to {decision.target_path}")

                # Ensure target directory exists
                target.parent.mkdir(parents=True, exist_ok=True)

                # Use ArchivalGatekeeper for safe move
                gatekeeper = self._get_archival_gatekeeper()
                result = gatekeeper.safe_move(
                    file_path,
                    destination_category=decision.target_path,
                    reason=f"Cognitive disposition: {decision.reason}",
                )
                if hasattr(result, "success") and result.success:
                    Logger.info("    [OK] Moved successfully")
                    return True
                else:
                    Logger.warning("    [FAIL] Move failed")
                    return False

            elif decision.action == "ARCHIVE":
                archive_path = decision.target_path or "archives/cognitive_disposition"
                Logger.info(f"    [COGNITIVE] Archiving {file_path.name} to {archive_path}")

                gatekeeper = self._get_archival_gatekeeper()
                result = gatekeeper.safe_move(
                    file_path,
                    destination_category=archive_path,
                    reason=f"Cognitive archive: {decision.reason}",
                )
                if hasattr(result, "success") and result.success:
                    Logger.info("    [OK] Archived successfully")
                    return True
                else:
                    Logger.warning("    [FAIL] Archive failed")
                    return False

            elif decision.action == "IGNORE":
                Logger.info(f"    [COGNITIVE] Ignoring: {decision.reason}")
                return True  # Considered "resolved" by ignoring

            elif decision.action == "MANUAL_REVIEW":
                Logger.warning(f"    [COGNITIVE] Requires manual review: {decision.reason}")
                return False

            else:
                Logger.warning(f"    [COGNITIVE] Unknown action: {decision.action}")
                return False

        except Exception as e:
            Logger.error(f"    [COGNITIVE] Error processing disposition: {e}")
            return False

    def heal(self, violation: dict) -> dict:
        """Heal architecture violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming, gravity, orphan, duplicate)
                - path: Path to the violating file/directory
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        from agentic_core.base_agents.decorators import standard_heal

        @standard_heal
        def _heal_architecture_violation(self, violation: dict) -> dict:
            """Internal heal method with standard_heal decorator."""
            violation_type = violation.get("type", "unknown")
            path = violation.get("path", "")

            Logger.info(f"[ARCH_GOVERNOR] Healing {violation_type} violation at {path}")

            # Handle different violation types
            if violation_type == "naming":
                # Fix naming convention violations
                if not path.endswith("Agent.py") and path.endswith(".py"):
                    new_path = path.replace(".py", "Agent.py")
                    try:
                        Path(path).rename(new_path)
                        Logger.info(f"  Renamed {path} -> {new_path}")
                        return {
                            "violations_fixed": 1,
                            "violations_found": 1,
                            "errors": 0,
                            "skipped": 0,
                        }
                    except Exception as e:
                        Logger.error(f"  Failed to rename {path}: {e}")
                        return {
                            "violations_fixed": 0,
                            "violations_found": 1,
                            "errors": 1,
                            "skipped": 0,
                        }

            elif violation_type == "gravity":
                # Log gravity violations for manual review
                Logger.warning(f"  Gravity violation at {path} - requires manual review")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            elif violation_type == "orphan":
                # Archive orphaned files
                from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

                archivist = ArchivalGatekeeper(self.project_root)
                try:
                    archivist.archive_file(Path(path), reason="orphaned_agent")
                    Logger.info(f"  Archived orphaned file: {path}")
                    return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                except Exception as e:
                    Logger.error(f"  Failed to archive {path}: {e}")
                    return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

            elif violation_type == "duplicate":
                # Log duplicate agents for manual review
                Logger.warning(f"  Duplicate agent at {path} - requires manual review")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            else:
                Logger.warning(f"  Unknown violation type: {violation_type}")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        # Call the internal heal method
        return _heal_architecture_violation(self, violation)
