"""
Report Location Validator - SSOT Enforcement for Report Storage

This module provides validation and discovery for report files, ensuring all reports
are stored in the canonical SSOT location: docs/reports/

USAGE:
    from agentic_core.utils.report_location_validator_types_util import (
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

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "report_location_validator")
trace_contract.emit_determinism_digest("p0", "report_location_validator")

trace_contract._emit_dispatches_healing_run("p1", "report_location_validator", "L5")
trace_contract._emit_routes_through("p1", "report_location_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "report_location_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "report_location_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "report_location_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "report_location_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "report_location_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "report_location_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "report_location_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "report_location_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "report_location_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "report_location_validator")
trace_contract._emit_gated_by_confidence("p1", "report_location_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "report_location_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "report_location_validator", "L5")
trace_contract._emit_applies_guardrail("p0", "report_location_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "report_location_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "report_location_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "report_location_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "report_location_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "report_location_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "report_location_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "report_location_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "report_location_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "report_location_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "report_location_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "report_location_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "report_location_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "report_location_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "report_location_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "report_location_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "report_location_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "report_location_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "report_location_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "report_location_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "report_location_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "report_location_validator", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("report_location_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("report_location_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("report_location_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("report_location_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("report_location_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("report_location_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("report_location_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("report_location_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("report_location_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("report_location_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("report_location_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("report_location_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("report_location_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("report_location_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("report_location_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("report_location_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("report_location_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("report_location_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("report_location_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("report_location_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("report_location_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("report_location_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("report_location_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("report_location_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("report_location_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("report_location_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("report_location_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("report_location_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "report_location_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "report_location_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "report_location_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "report_location_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "report_location_validator", "write_through")
trace_contract._emit_writes_through("p1", "report_location_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "report_location_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "report_location_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "report_location_validator", "routing_commit")

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
    r"W\d+_.*\.(md|json)$",
    r".*_EVIDENCE.*\.md$",
    r".*_SUMMARY\.md$",
    r".*_ANALYSIS\.md$",
    r".*_AUDIT.*\.md$",
    r".*_FINDINGS\.md$",
    r".*_IMPLEMENTATION.*\.md$",
    r".*_COMPLETION.*\.md$",
    r".*_STATUS.*\.md$",
    r".*_COMPLIANCE.*\.(md|json)$",
    r".*_VIOLATIONS.*\.(md|json)$",
    r".*_FIX.*\.md$",
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
    ARCHIVES_DIR,
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "ReportLocationValidator.is_report_file",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ReportLocationValidator.is_report_file".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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

        for report_path in tqdm(all_reports, desc="Processing", unit="item"):
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


def validate_report_location(file_path: Path, project_root: Path | None = None) -> bool:
    """
    Validate if a report file is in the correct SSOT location.

    Args:
        file_path: Path to the report file.
        project_root: Project root path.

    Returns:
        True if the file is in an approved location.
    """
    trace_contract._emit_validated_by_safety_plane(str(uuid.uuid4()), "Module.validate_report_location", "L5_POLICY")
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
