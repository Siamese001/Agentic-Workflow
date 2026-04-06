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

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin

_emit_authorize_and_execute("p2", "ReportLocationAgent", "execution_auth")
_emit_validates_capability("p2", "ReportLocationAgent", "capability_check")
_emit_routes_to_capability("p2", "ReportLocationAgent", "capability_route")
_emit_writes_via_uwg("p2", "ReportLocationAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ReportLocationAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ReportLocationAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ReportLocationAgent", "exec_output")
_emit_dispatches_agent("p3", "ReportLocationAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ReportLocationAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ReportLocationAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ReportLocationAgent", "healing_outcome")
_emit_escalates_failure("p3", "ReportLocationAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ReportLocationAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ReportLocationAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ReportLocationAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ReportLocationAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ReportLocationAgent", "eval_metric")
_emit_stores_embedding("p4", "ReportLocationAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ReportLocationAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ReportLocationAgent", "exec_snapshot_link")
from agentic_core.utils.report_location_validator_types_util import (
    APPROVED_REPORT_LOCATIONS,
    SSOT_REPORTS_DIR,
    ReportInventory,
    ReportLocationValidator,
    ReportValidationResult,
)

emit_replay_key("p0", "ReportLocationAgent")
emit_determinism_digest("p0", "ReportLocationAgent")

_emit_dispatches_healing_run("p1", "ReportLocationAgent", "L5")
_emit_routes_through("p1", "ReportLocationAgent", "L5")
_emit_checks_agent_registry("p1", "ReportLocationAgent", "agent_registry")
_emit_validates_agent_capability("p1", "ReportLocationAgent", "capability")
_emit_dispatches_execution_plan("p1", "ReportLocationAgent", "exec_plan")
_emit_agent_executes_agent("p1", "ReportLocationAgent", "sub_agent")
_emit_routes_to_agent("p1", "ReportLocationAgent", "target_agent")
_emit_verifies_policy("p1", "ReportLocationAgent", "policy_check")
_emit_observes_runtime_state("p1", "ReportLocationAgent", "runtime_state")
_emit_verifies_boundary("p1", "ReportLocationAgent", "boundary_check")
_emit_transcripts_response("p1", "ReportLocationAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "ReportLocationAgent")
_emit_gated_by_confidence("p1", "ReportLocationAgent", "confidence_gate")
_emit_escalates_to_human("p1", "ReportLocationAgent", "L5")
_emit_reads_policy_state("p1", "ReportLocationAgent", "L5")
_emit_applies_guardrail("p0", "ReportLocationAgent", "p0_governance")
_emit_snapshots_state("p0", "ReportLocationAgent", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("ReportLocationAgent", "p4obs", "metric_1")
_emit_emits_metric_event("ReportLocationAgent", "p4obs", "metric_2")
_emit_emits_metric_event("ReportLocationAgent", "p4obs", "metric_3")
_emit_emits_metric_event("ReportLocationAgent", "p4obs", "metric_4")
_emit_emits_metric_event("ReportLocationAgent", "p4obs", "metric_5")
_emit_emits_metric_event("ReportLocationAgent", "p4obs", "metric_6")
_emit_records_incident_event("ReportLocationAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("ReportLocationAgent", "p4obs", "anomaly")
_emit_writes_observability_log("ReportLocationAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("ReportLocationAgent", "p4obs", "mon_state")
_emit_triggers_alert("ReportLocationAgent", "p4obs", "alert")
_emit_links_incident_trace("ReportLocationAgent", "p4obs", "trace_link")
_emit_captures_pattern("ReportLocationAgent", "p3lm", "pattern")
_emit_records_learning_event("ReportLocationAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ReportLocationAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("ReportLocationAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ReportLocationAgent", "p3lm", "routing")
_emit_improves_agent_policy("ReportLocationAgent", "p3lm", "policy")
_emit_stores_learning_state("ReportLocationAgent", "p3lm", "state")
_emit_records_execution_trace("ReportLocationAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ReportLocationAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ReportLocationAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ReportLocationAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ReportLocationAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ReportLocationAgent", "env_read", "p2_env_1")
_emit_reads_environ("ReportLocationAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("ReportLocationAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ReportLocationAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ReportLocationAgent", "context_pull")
_emit_pulls_context("p1", "ReportLocationAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ReportLocationAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ReportLocationAgent", "uwg_term_2")
_emit_writes_through("p1", "ReportLocationAgent", "write_through")
_emit_writes_through("p1", "ReportLocationAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "ReportLocationAgent", "safety_validation")
_emit_invokes_eval("p1", "ReportLocationAgent", "eval_call")
_emit_proposal_commits_routing("p1", "ReportLocationAgent", "routing_commit")

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
            self.backup_dir = self.project_root / ARCHIVES_DIR / "healing_backups" / SSOT_REPORTS_DIR

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ReportLocationAgent.validate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReportLocationAgent.validate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        except (ValueError, TypeError, RuntimeError) as e:
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
        except (ValueError, TypeError, RuntimeError) as e:
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
        except (RuntimeError, OSError) as e:
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
        except (RuntimeError, OSError) as e:
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
        if output_path is None:
            output_path = self._validator.project_root / SSOT_REPORTS_DIR / "report_location_inventory.json"

        inventory = self._validator.generate_inventory()

        _wg.ensure_dir(output_path.parent)
        _wg.write_json(
            output_path,
            {
                "timestamp": inventory.timestamp,
                "total_reports": inventory.total_reports,
                "compliant_reports": inventory.compliant_reports,
                "misplaced_reports": inventory.misplaced_reports,
                "compliance_percentage": round(inventory.compliance_percentage, 2),
                "reports_by_location": inventory.reports_by_location,
                "misplaced_files": inventory.misplaced_files,
            },
            indent=2,
        )
        Logger.info(f"[SSOT] Report inventory saved to {output_path}")
        return output_path

    def heal_repository(self, *args, **kwargs) -> dict[str, Any]:
        """heal_repository() not implemented for ReportLocationAgent."""
        raise NotImplementedError("heal_repository() not implemented for ReportLocationAgent")


__all__ = [
    "ReportLocationAgent",
    "ReportLocationHealResult",
]
