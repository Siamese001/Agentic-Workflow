"""
Report Location Validator - SSOT Enforcement for Report Storage

This module provides validation and discovery for report files, ensuring all reports
are stored in the canonical SSOT location: docs/reports/

USAGE:
    from agentic_core.utils.report_location_validator_types import (
        ReportLocationValidator,
        validate_report_location,
        get_misplaced_reports,
        generate_report_inventory,
    )

SSOT PRINCIPLE:
    All reports must reside in docs/reports/ or approved subdirectories.
    This module enforces that principle through validation and discovery.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    get_validated_project_root,
)

Logger = logging.getLogger(__name__)

# ============================================================================
# SSOT REPORT LOCATION CONSTANTS
# ============================================================================

SSOT_REPORTS_DIR: Final[str] = "docs/reports"

REPORT_FILE_PATTERNS: Final[tuple[str, ...]] = (
    r".*[Rr]eport.*\.md$",
    r".*[Rr]eport.*\.json$",
    r".*[Rr]eport.*\.txt$",
    r"RCA.*\.md$",
    r"PHASE\d+.*\.(md|json)$",
    r".*_SUMMARY\.md$",
    r".*_ANALYSIS\.md$",
    r".*_AUDIT.*\.md$",
    r".*_FINDINGS\.md$",
    r".*_IMPLEMENTATION.*\.md$",
    r".*_COMPLETION.*\.md$",
    r".*_STATUS.*\.md$",
)

EXCLUDED_DIRECTORIES: Final[tuple[str, ...]] = (
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".sovereign_healing_backup",
    "archives",
)

APPROVED_REPORT_LOCATIONS: Final[tuple[str, ...]] = (
    "docs/reports",
    "docs/reports/MCP",
    "logs/compliance_reports",
    "data/freeze_reports",
)


@dataclass
class ReportValidationResult:
    """Result of a report location validation."""

    file_path: Path
    is_compliant: bool
    current_location: str
    expected_location: str
    violation_type: str | None = None
    suggested_action: str | None = None


@dataclass
class ReportInventory:
    """Comprehensive inventory of all reports in the repository."""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_reports: int = 0
    compliant_reports: int = 0
    misplaced_reports: int = 0
    reports_by_location: dict[str, list[str]] = field(default_factory=dict)
    misplaced_files: list[dict[str, Any]] = field(default_factory=list)
    compliance_percentage: float = 0.0


class ReportLocationValidator:
    """
    Validates report file locations against SSOT requirements.

    Ensures all reports are stored in docs/reports/ or approved subdirectories.
    """

    def __init__(self, project_root: Path | None = None, dry_run: bool = True):
        """
        Initialize the validator.

        Args:
            project_root: Project root path. If None, uses get_validated_project_root().
            dry_run: If True, only report violations without taking action.
        """
        self.project_root = project_root or get_validated_project_root()
        self.dry_run = dry_run
        self._compiled_patterns: list[re.Pattern] = [re.compile(pattern) for pattern in REPORT_FILE_PATTERNS]

    def is_report_file(self, file_path: Path) -> bool:
        """
        Check if a file matches report file patterns.

        Args:
            file_path: Path to check.

        Returns:
            True if the file matches a report pattern.
        """
        filename = file_path.name
        return any(pattern.match(filename) for pattern in self._compiled_patterns)

    def is_excluded_directory(self, file_path: Path) -> bool:
        """
        Check if a file is in an excluded directory.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is in an excluded directory.
        """
        path_str = str(file_path)
        return any(excluded in path_str for excluded in EXCLUDED_DIRECTORIES)

    def is_approved_location(self, file_path: Path) -> bool:
        """
        Check if a file is in an approved report location.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is in an approved location.
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
            rel_path_str = str(rel_path).replace("\\", "/")

            for approved in APPROVED_REPORT_LOCATIONS:
                if rel_path_str.startswith(approved):
                    return True
            return False
        except ValueError:
            return False

    def validate_file(self, file_path: Path) -> ReportValidationResult:
        """
        Validate a single file's location.

        Args:
            file_path: Path to validate.

        Returns:
            ReportValidationResult with validation details.
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
            rel_path_str = str(rel_path).replace("\\", "/")
        except ValueError:
            rel_path_str = str(file_path)

        is_compliant = self.is_approved_location(file_path)

        if is_compliant:
            return ReportValidationResult(
                file_path=file_path,
                is_compliant=True,
                current_location=rel_path_str,
                expected_location=rel_path_str,
            )

        # Determine suggested location
        filename = file_path.name
        suggested_location = f"{SSOT_REPORTS_DIR}/{filename}"

        return ReportValidationResult(
            file_path=file_path,
            is_compliant=False,
            current_location=rel_path_str,
            expected_location=suggested_location,
            violation_type="misplaced_report",
            suggested_action=f"Move to {suggested_location}",
        )

    def find_all_reports(self) -> list[Path]:
        """
        Find all report files in the repository.

        Returns:
            List of paths to report files.
        """
        reports = []

        for file_path in self.project_root.rglob("*"):
            if not file_path.is_file():
                continue

            if self.is_excluded_directory(file_path):
                continue

            if self.is_report_file(file_path):
                reports.append(file_path)

        return reports

    def get_misplaced_reports(self) -> list[ReportValidationResult]:
        """
        Get all misplaced report files.

        Returns:
            List of validation results for misplaced reports.
        """
        misplaced = []

        for report_path in self.find_all_reports():
            result = self.validate_file(report_path)
            if not result.is_compliant:
                misplaced.append(result)

        return misplaced

    def get_compliant_reports(self) -> list[ReportValidationResult]:
        """
        Get all compliant report files.

        Returns:
            List of validation results for compliant reports.
        """
        compliant = []

        for report_path in self.find_all_reports():
            result = self.validate_file(report_path)
            if result.is_compliant:
                compliant.append(result)

        return compliant

    def generate_inventory(self) -> ReportInventory:
        """
        Generate a comprehensive inventory of all reports.

        Returns:
            ReportInventory with categorized report information.
        """
        inventory = ReportInventory()
        reports_by_location: dict[str, list[str]] = {}

        all_reports = self.find_all_reports()
        inventory.total_reports = len(all_reports)

        for report_path in all_reports:
            result = self.validate_file(report_path)

            # Categorize by parent directory
            try:
                rel_path = report_path.relative_to(self.project_root)
                parent = str(rel_path.parent).replace("\\", "/")
            except ValueError:
                parent = "unknown"

            if parent not in reports_by_location:
                reports_by_location[parent] = []
            reports_by_location[parent].append(report_path.name)

            if result.is_compliant:
                inventory.compliant_reports += 1
            else:
                inventory.misplaced_reports += 1
                inventory.misplaced_files.append(
                    {
                        "file": result.current_location,
                        "suggested_location": result.expected_location,
                        "violation_type": result.violation_type,
                    },
                )

        inventory.reports_by_location = reports_by_location

        if inventory.total_reports > 0:
            inventory.compliance_percentage = (inventory.compliant_reports / inventory.total_reports) * 100

        return inventory

    def save_inventory(self, output_path: Path | None = None) -> Path:
        """
        Save the report inventory to a JSON file.

        Args:
            output_path: Path to save the inventory.
                Defaults to docs/reports/report_location_inventory.json.

        Returns:
            Path to the saved inventory file.
        """
        if output_path is None:
            output_path = self.project_root / SSOT_REPORTS_DIR / "report_location_inventory.json"

        inventory = self.generate_inventory()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": inventory.timestamp,
                    "total_reports": inventory.total_reports,
                    "compliant_reports": inventory.compliant_reports,
                    "misplaced_reports": inventory.misplaced_reports,
                    "compliance_percentage": round(inventory.compliance_percentage, 2),
                    "reports_by_location": inventory.reports_by_location,
                    "misplaced_files": inventory.misplaced_files,
                },
                f,
                indent=2,
            )

        Logger.info(f"[SSOT] Report inventory saved to {output_path}")
        return output_path


def validate_report_location(file_path: Path, project_root: Path | None = None) -> bool:
    """
    Validate if a report file is in the correct SSOT location.

    Args:
        file_path: Path to the report file.
        project_root: Project root path.

    Returns:
        True if the file is in an approved location.
    """
    validator = ReportLocationValidator(project_root)
    result = validator.validate_file(file_path)
    return result.is_compliant


def get_misplaced_reports(project_root: Path | None = None) -> list[ReportValidationResult]:
    """
    Get all misplaced report files in the repository.

    Args:
        project_root: Project root path.

    Returns:
        List of validation results for misplaced reports.
    """
    validator = ReportLocationValidator(project_root)
    return validator.get_misplaced_reports()


def generate_report_inventory(project_root: Path | None = None) -> ReportInventory:
    """
    Generate a comprehensive inventory of all reports.

    Args:
        project_root: Project root path.

    Returns:
        ReportInventory with categorized report information.
    """
    validator = ReportLocationValidator(project_root)
    return validator.generate_inventory()


__all__ = [
    "ReportLocationValidator",
    "ReportValidationResult",
    "ReportInventory",
    "validate_report_location",
    "get_misplaced_reports",
    "generate_report_inventory",
    "SSOT_REPORTS_DIR",
    "REPORT_FILE_PATTERNS",
    "APPROVED_REPORT_LOCATIONS",
]
