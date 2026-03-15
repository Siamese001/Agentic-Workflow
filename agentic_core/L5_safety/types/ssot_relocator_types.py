from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

"\nSSOT Relocator - Automated Violation Remediation\n\nReplaces 4 manual relocation scripts with a single, reusable library:\n- phase2_gravity_relocation.py\n- phase4_final_gravity_relocation.py\n- phase4_final_observability_relocation.py\n- phase4_perfection_absolute.py\n\nProvides automated remediation for:\n1. Drift violations (orphaned folders → archives)\n2. Hierarchy violations (excessive depth → flattening)\n3. Gravity violations (wrong layer → correct layer)\n"
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR, ARCHIVES_DIR
from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RelocationResult:
    """Result of a single relocation operation."""

    source: str
    target: str
    success: bool
    action: str
    error: str | None = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class EnforcementReport:
    """Summary of enforcement operations."""

    total_operations: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[RelocationResult] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_operations == 0:
            return 100.0
        return self.successful / self.total_operations * 100


class SSOTRelocator:
    """
    Automated SSOT violation remediation.

    Provides reusable methods for fixing violations detected by UnifiedSSOTValidator:
    - relocate_orphans(): Move drift violations to archives
    - enforce_hierarchy(): Flatten folders exceeding depth limits
    - relocate_agents(): Move agents to correct layers
    """

    def __init__(self, project_root: Path, dry_run: bool = True, log_file: Path | None = None):
        """
        Initialize SSOT relocator.

        Args:
            project_root: Root directory of the project
            dry_run: If True, preview operations without executing
            log_file: Path to enforcement history log
        """
        self.project_root = project_root.resolve()
        self.dry_run = dry_run
        if log_file is None:
            log_dir = project_root / AGENTIC_CORE_DIR / "L0_routing" / "logs"
            _wg.ensure_dir(log_dir)
            log_file = log_dir / "enforcement_history.log"
        self.log_file = log_file
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
        self.archive_root = project_root / ARCHIVES_DIR / "unmapped_drift"
        if not dry_run:
            _wg.ensure_dir(self.archive_root)
        self.gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)

    def relocate_orphans(self, drift_violations: list[Any]) -> EnforcementReport:
        """
        Move orphaned folders (drift violations) to archives.

        Args:
            drift_violations: List of DriftViolation objects from validator

        Returns:
            EnforcementReport with operation results
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, f"OrphanRelocator.relocate_orphans:{len(drift_violations)}")
        report = EnforcementReport()
        logger.info(f"{('[DRY-RUN] ' if self.dry_run else '')}Starting orphan relocation")
        logger.info(f"Target violations: {len(drift_violations)}")
        for violation in drift_violations:
            source = self.project_root / violation.folder_path
            timestamp = datetime.now().strftime("%Y%m%d")
            archive_path = self.archive_root / timestamp / violation.folder_path
            result = self._relocate_folder(source=source, target=archive_path, action="ARCHIVED")
            report.results.append(result)
            report.total_operations += 1
            if result.success:
                report.successful += 1
            elif result.action == "SKIPPED":
                report.skipped += 1
            else:
                report.failed += 1
        logger.info(f"Orphan relocation complete: {report.successful}/{report.total_operations} successful")
        return report

    def enforce_hierarchy(self, hierarchy_violations: list[Any]) -> EnforcementReport:
        """
        Flatten folders exceeding depth limits.

        Moves files from deep folders to parent folders within depth limits.

        Args:
            hierarchy_violations: List of HierarchyViolation objects from validator

        Returns:
            EnforcementReport with operation results
        """
        report = EnforcementReport()
        logger.info(f"{('[DRY-RUN] ' if self.dry_run else '')}Starting hierarchy enforcement")
        logger.info(f"Target violations: {len(hierarchy_violations)}")
        for violation in hierarchy_violations:
            source = self.project_root / violation.folder_path
            if not source.exists():
                result = RelocationResult(
                    source=str(source),
                    target="N/A",
                    success=False,
                    action="SKIPPED",
                    error="Source does not exist",
                )
                report.results.append(result)
                report.total_operations += 1
                report.skipped += 1
                continue
            parts = Path(violation.folder_path).parts
            target_parts = parts[: violation.max_depth + 1]
            target = self.project_root / Path(*target_parts)
            result = self._flatten_folder(source=source, target=target, max_depth=violation.max_depth)
            report.results.append(result)
            report.total_operations += 1
            if result.success:
                report.successful += 1
            elif result.action == "SKIPPED":
                report.skipped += 1
            else:
                report.failed += 1
        logger.info(
            f"Hierarchy enforcement complete: {report.successful}/{report.total_operations} successful"
        )
        return report

    def relocate_agents(self, gravity_violations: list[Any]) -> EnforcementReport:
        """
        Move agents to their correct layers (gravity violation remediation).

        Args:
            gravity_violations: List of GravityViolation objects from validator

        Returns:
            EnforcementReport with operation results
        """
        report = EnforcementReport()
        logger.info(f"{('[DRY-RUN] ' if self.dry_run else '')}Starting agent relocation")
        logger.info(f"Target violations: {len(gravity_violations)}")
        for violation in gravity_violations:
            source = self.project_root / violation.file_path
            target_path = violation.file_path.replace(
                f"/{violation.actual_layer}/", f"/{violation.assigned_layer}/"
            )
            target = self.project_root / target_path
            result = self._relocate_file(source=source, target=target, action="MOVED")
            report.results.append(result)
            report.total_operations += 1
            if result.success:
                report.successful += 1
            elif result.action == "SKIPPED":
                report.skipped += 1
            else:
                report.failed += 1
        logger.info(f"Agent relocation complete: {report.successful}/{report.total_operations} successful")
        return report

    def _relocate_file(self, source: Path, target: Path, action: str = "MOVED") -> RelocationResult:
        """
        Relocate a single file with safety checks.

        Args:
            source: Source file path
            target: Target file path
            action: Action description

        Returns:
            RelocationResult with operation details
        """
        result = RelocationResult(
            source=str(source.relative_to(self.project_root)),
            target=str(target.relative_to(self.project_root)),
            success=False,
            action=action,
        )
        if not source.exists():
            result.error = "Source file does not exist"
            result.action = "SKIPPED"
            return result
        if target.exists():
            result.error = "Target file already exists"
            result.action = "SKIPPED"
            return result
        if self.dry_run:
            result.success = True
            result.action = f"{action} (DRY-RUN)"
            logger.info(f"[DRY-RUN] Would {action.lower()}: {result.source} → {result.target}")
        else:
            try:
                gk_result = self.gatekeeper.safe_move(
                    source, target, "SSOTRelocator", f"SSOT Reconciliation: {action}"
                )
                if gk_result.success:
                    result.success = True
                    logger.info(f"{action}: {result.source} → {result.target}")
                    self._cleanup_empty_dirs(source.parent)
                elif gk_result.approval_status == "DENIED":
                    result.action = "SKIPPED"
                    result.error = "User declined move"
                    logger.info(f"Skipped {action.lower()} of {result.source} - user declined")
                else:
                    result.error = gk_result.error
                    logger.error(f"Failed to {action.lower()} {result.source}: {gk_result.error}")
            # guardian: allow-silent-swallow
            except Exception as e:
                result.error = str(e)
                logger.error(f"Failed to {action.lower()} {result.source}: {e}")
        return result

    def _relocate_folder(self, source: Path, target: Path, action: str = "MOVED") -> RelocationResult:
        """
        Relocate an entire folder with safety checks.

        Args:
            source: Source folder path
            target: Target folder path
            action: Action description

        Returns:
            RelocationResult with operation details
        """
        result = RelocationResult(
            source=str(source.relative_to(self.project_root)),
            target=str(target.relative_to(self.project_root)),
            success=False,
            action=action,
        )
        if not source.exists():
            result.error = "Source folder does not exist"
            result.action = "SKIPPED"
            return result
        if target.exists():
            result.error = "Target folder already exists"
            result.action = "SKIPPED"
            return result
        if self.dry_run:
            result.success = True
            result.action = f"{action} (DRY-RUN)"
            logger.info(f"[DRY-RUN] Would {action.lower()}: {result.source} → {result.target}")
        else:
            try:
                gk_result = self.gatekeeper.safe_move(
                    source, target, "SSOTRelocator", f"SSOT Reconciliation: {action} folder"
                )
                if gk_result.success:
                    result.success = True
                    logger.info(f"{action}: {result.source} → {result.target}")
                elif gk_result.approval_status == "DENIED":
                    result.action = "SKIPPED"
                    result.error = "User declined move"
                    logger.info(f"Skipped {action.lower()} of {result.source} - user declined")
                else:
                    result.error = gk_result.error
                    logger.error(f"Failed to {action.lower()} {result.source}: {gk_result.error}")
            # guardian: allow-silent-swallow
            except Exception as e:
                result.error = str(e)
                logger.error(f"Failed to {action.lower()} {result.source}: {e}")
        return result

    def _flatten_folder(self, source: Path, target: Path, max_depth: int) -> RelocationResult:
        """
        Flatten a folder by moving its contents to a shallower location.

        Args:
            source: Source folder path (too deep)
            target: Target folder path (within depth limit)
            max_depth: Maximum allowed depth

        Returns:
            RelocationResult with operation details
        """
        result = RelocationResult(
            source=str(source.relative_to(self.project_root)),
            target=str(target.relative_to(self.project_root)),
            success=False,
            action="FLATTENED",
        )
        if not source.exists():
            result.error = "Source folder does not exist"
            result.action = "SKIPPED"
            return result
        if self.dry_run:
            result.success = True
            result.action = "FLATTENED (DRY-RUN)"
            logger.info(f"[DRY-RUN] Would flatten: {result.source} -> {result.target}")
        else:
            try:
                _wg.ensure_dir(target)
                from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

                all_items = list(get_python_files(source)) + list(get_data_files(source))
                for item in all_items:
                    if item.is_file():
                        rel_path = item.relative_to(source)
                        target_file = target / rel_path.name
                        if not target_file.exists():
                            _wg.ensure_dir(target_file.parent)
                            gk_result = self.gatekeeper.safe_move(
                                item, target_file, "SSOTRelocator", "SSOT Reconciliation: Flatten folder"
                            )
                            if not gk_result.success and gk_result.approval_status == "DENIED":
                                result.action = "SKIPPED"
                                result.error = "User declined move"
                                logger.info(f"Skipped flatten of {result.source} - user declined")
                                return result
                if source.exists() and (not any(source.iterdir())):
                    _wg.remove_dir(source)
                result.success = True
                logger.info(f"FLATTENED: {result.source} -> {result.target}")
            # guardian: allow-silent-swallow
            except Exception as e:
                result.error = str(e)
                logger.error(f"Failed to flatten {result.source}: {e}")
        return result

    def _cleanup_empty_dirs(self, directory: Path) -> None:
        """
        Recursively remove empty parent directories.

        Args:
            directory: Directory to check and clean up
        """
        if not directory.exists() or not directory.is_dir():
            return
        try:
            if not any(directory.iterdir()):
                _wg.remove_dir(directory)
                logger.info(f"Cleaned up empty directory: {directory}")
                self._cleanup_empty_dirs(directory.parent)
        except (OSError, PermissionError):
            pass
