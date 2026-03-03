#!/usr/bin/env python3
"""
ReportLocationAgent - SSOT Report Storage Enforcement Agent.

Validates and heals report file locations to ensure all reports
are stored in the canonical SSOT location: docs/reports/

USAGE:
    from agentic_core.L5_safety.validators.ReportLocationAgent import (
        ReportLocationAgent,
    )

    agent = ReportLocationAgent(project_root=Path("."))
    result = agent.validate()
    heal_result = agent.heal()

SSOT PRINCIPLE:
    All reports must reside in docs/reports/ or approved subdirectories.
    This agent enforces that principle through validation and healing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin
from agentic_core.utils.report_location_validator_types_util import (
    APPROVED_REPORT_LOCATIONS,
    SSOT_REPORTS_DIR,
    ReportInventory,
    ReportLocationValidator,
    ReportValidationResult,
)

Logger = logging.getLogger(__name__)


@dataclass
class ReportLocationHealResult:
    """Result of a report location healing operation."""

    total_violations: int = 0
    healed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    healed_files: list[dict[str, str]] = field(default_factory=list)
    failed_files: list[dict[str, str]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ReportLocationAgent(AtomicExecutionMixin):
    """
    SSOT Report Storage Enforcement Agent.

    Validates and heals report file locations to ensure compliance
    with the SSOT principle: all reports in docs/reports/.

    Capabilities:
    - Validate report locations across the repository
    - Generate compliance inventory
    - Heal violations by moving files to SSOT location
    - Git-aware moves to preserve history
    - Backup before healing operations

    Integration:
    - Works with pre-commit hooks for enforcement
    - Integrates with Guardian tests for validation
    - Supports dry-run mode for safe testing
    """

    project_root: Path = field(default=None)
    dry_run: bool = True
    backup_dir: Path = field(default=None)

    def __post_init__(self):
        """Initialize the agent."""
        if self.project_root is None:
            self.project_root = Path.cwd()
        self.project_root = self.project_root.resolve()

        if self.backup_dir is None:
            self.backup_dir = self.project_root / ".sovereign_healing_backup" / "reports"

        self.agent_name = "ReportLocationAgent"
        self._validator = ReportLocationValidator(self.project_root, self.dry_run)

    def validate(self) -> dict[str, Any]:
        """
        Validate all report locations in the repository.

        Returns:
            Dictionary with validation results including:
            - total_reports: Total number of report files found
            - compliant_reports: Number of reports in approved locations
            - misplaced_reports: Number of reports in wrong locations
            - compliance_percentage: Percentage of compliant reports
            - violations: List of violation details
        """
        inventory = self._validator.generate_inventory()

        return {
            "total_reports": inventory.total_reports,
            "compliant_reports": inventory.compliant_reports,
            "misplaced_reports": inventory.misplaced_reports,
            "compliance_percentage": round(inventory.compliance_percentage, 2),
            "violations": inventory.misplaced_files,
            "reports_by_location": inventory.reports_by_location,
            "timestamp": inventory.timestamp,
            "ssot_location": SSOT_REPORTS_DIR,
            "approved_locations": list(APPROVED_REPORT_LOCATIONS),
        }

    def get_violations(self) -> list[ReportValidationResult]:
        """
        Get all report location violations.

        Returns:
            List of ReportValidationResult for misplaced reports.
        """
        return self._validator.get_misplaced_reports()

    def get_inventory(self) -> ReportInventory:
        """
        Generate a comprehensive report inventory.

        Returns:
            ReportInventory with categorized report information.
        """
        return self._validator.generate_inventory()

    def is_git_tracked(self, file_path: Path) -> bool:
        """Check if a file is tracked by git via L5-safe subprocess delegation."""
        try:
            from agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer import (
                safe_subprocess_run,
            )

            result = safe_subprocess_run(
                ["git", "ls-files", "--error-unmatch", str(file_path)],
                cwd=str(self.project_root),
            )
            return result.returncode == 0
        except Exception:
            return False

    def git_move(self, source: Path, destination: Path) -> bool:
        """Move a file using git mv to preserve history (L5-safe delegation)."""
        try:
            _wg.ensure_dir(destination.parent)
            from agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer import (
                safe_subprocess_run,
            )

            result = safe_subprocess_run(
                ["git", "mv", str(source), str(destination)],
                cwd=str(self.project_root),
            )
            return result.returncode == 0
        except Exception:
            return False

    def backup_file(self, file_path: Path) -> Path | None:
        """Create a backup of a file before healing."""
        try:
            _wg.ensure_dir(self.backup_dir)
            rel_path = file_path.relative_to(self.project_root)
            backup_path = self.backup_dir / rel_path
            _wg.ensure_dir(backup_path.parent)
            _wg.copy_file(file_path, backup_path)
            return backup_path
        except Exception as e:
            Logger.warning(f"[ReportLocationAgent] Backup failed for {file_path}: {e}")
            return None

    def heal_file(self, violation: ReportValidationResult) -> dict[str, Any]:
        """
        Heal a single report location violation.

        Args:
            violation: The violation to heal.

        Returns:
            Dictionary with heal result for this file.
        """
        source = self.project_root / violation.current_location
        destination = self.project_root / violation.expected_location

        result = {
            "source": violation.current_location,
            "destination": violation.expected_location,
            "status": "pending",
            "error": None,
        }

        if self.dry_run:
            result["status"] = "dry_run"
            return result

        # Check if destination already exists
        if destination.exists():
            result["status"] = "skipped"
            result["error"] = "Destination file already exists"
            return result

        # Create backup
        backup = self.backup_file(source)
        if not backup:
            result["status"] = "failed"
            result["error"] = "Failed to create backup"
            return result

        # Perform the move
        try:
            _wg.ensure_dir(destination.parent)

            if self.is_git_tracked(source):
                success = self.git_move(source, destination)
            else:
                _wg.move_path(str(source), str(destination))
                success = True

            if success:
                result["status"] = "healed"
                Logger.info(
                    f"[ReportLocationAgent] Healed: {violation.current_location} "
                    f"-> {violation.expected_location}",
                )
            else:
                result["status"] = "failed"
                result["error"] = "Move operation failed"
        # guardian: allow-silent-swallow
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def heal(self, limit: int | None = None) -> ReportLocationHealResult:
        """
        Heal all report location violations.

        Args:
            limit: Optional limit on number of files to heal (for pilot runs).

        Returns:
            ReportLocationHealResult with healing statistics.
        """
        violations = self.get_violations()

        if limit:
            violations = violations[:limit]

        heal_result = ReportLocationHealResult(total_violations=len(violations))

        for violation in violations:
            file_result = self.heal_file(violation)

            if file_result["status"] == "healed":
                heal_result.healed_count += 1
                heal_result.healed_files.append(file_result)
            elif file_result["status"] == "failed":
                heal_result.failed_count += 1
                heal_result.failed_files.append(file_result)
            elif file_result["status"] in ("skipped", "dry_run"):
                heal_result.skipped_count += 1

        return heal_result

    def standard_heal(self) -> dict[str, Any]:
        """
        Standard heal interface for integration with healing framework.

        Returns:
            Dictionary with standard heal result keys:
            - violations_found: Number of violations detected
            - violations_fixed: Number of violations healed
            - errors: List of error messages
            - skipped: Number of skipped files
        """
        heal_result = self.heal()

        return {
            "violations_found": heal_result.total_violations,
            "violations_fixed": heal_result.healed_count,
            "errors": [f["error"] for f in heal_result.failed_files if f.get("error")],
            "skipped": heal_result.skipped_count,
        }

    def save_inventory(self, output_path: Path | None = None) -> Path:
        """
        Save the report inventory to a JSON file.

        Args:
            output_path: Path to save the inventory.

        Returns:
            Path to the saved inventory file.
        """
        return self._validator.save_inventory(output_path)

    def heal_repository(self, *args, **kwargs) -> dict[str, Any]:
        """heal_repository() not implemented for ReportLocationAgent."""
        raise NotImplementedError("heal_repository() not implemented for ReportLocationAgent")


__all__ = [
    "ReportLocationAgent",
    "ReportLocationHealResult",
]
