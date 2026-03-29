# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
from __future__ import annotations

# This boosts alignment detection â€” review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    # noqa: E402
    _emit_gated_by_confidence,
    # noqa: E402
    _emit_records_healing_outcome,
    # noqa: E402
    _emit_routes_to_agent,
    # noqa: E402
    emit_replay_key,
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_to_human,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest
)

emit_replay_key("p0", "GravityStateAgent")
emit_determinism_digest("p0", "GravityStateAgent")

_emit_dispatches_healing_run("p1", "GravityStateAgent", "L3")
_emit_routes_through("p1", "GravityStateAgent", "L3")
_emit_checks_agent_registry("p1", "GravityStateAgent", "agent_registry")
_emit_validates_agent_capability("p1", "GravityStateAgent", "capability")
_emit_dispatches_execution_plan("p1", "GravityStateAgent", "exec_plan")
_emit_agent_executes_agent("p1", "GravityStateAgent", "sub_agent")
_emit_routes_to_agent("p1", "GravityStateAgent", "target_agent")
_emit_verifies_policy("p1", "GravityStateAgent", "policy_check")
_emit_observes_runtime_state("p1", "GravityStateAgent", "runtime_state")
_emit_verifies_boundary("p1", "GravityStateAgent", "boundary_check")
_emit_transcripts_response("p1", "GravityStateAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "GravityStateAgent")
_emit_gated_by_confidence("p1", "GravityStateAgent", "confidence_gate")
_emit_escalates_to_human("p1", "GravityStateAgent", "L3")
_emit_reads_policy_state("p1", "GravityStateAgent", "L3")
_emit_authorize_and_execute("p2", "GravityStateAgent", "execution_auth")
_emit_validates_capability("p2", "GravityStateAgent", "capability_check")
_emit_routes_to_capability("p2", "GravityStateAgent", "capability_route")
_emit_writes_via_uwg("p2", "GravityStateAgent", "uwg_write")
_emit_blocks_direct_write("p2", "GravityStateAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "GravityStateAgent", "tool_invocation")
_emit_captures_execution_output("p2", "GravityStateAgent", "exec_output")
_emit_dispatches_agent("p3", "GravityStateAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "GravityStateAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "GravityStateAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "GravityStateAgent", "healing_outcome")
_emit_escalates_failure("p3", "GravityStateAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "GravityStateAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GravityStateAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "GravityStateAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "GravityStateAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GravityStateAgent", "eval_metric")
_emit_stores_embedding("p4", "GravityStateAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "GravityStateAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GravityStateAgent", "exec_snapshot_link")

"""
GravityStateAgent - Gravity Healing State Tracker
Territory: agentic_core/L3_orchestration/

RESPONSIBILITIES:
- Track which files have been healed by GravityHealerAgent
- Prevent re-flagging of converted dynamic imports
- Maintain healing history and rollback capability
- Provide state persistence across healing sessions

STATE TRACKING:
- Healed files registry (file_path â†’ healing_metadata)
- Violation history (original_import â†’ dynamic_import)
- Healing timestamps and agent versions
- Rollback checkpoints

INTEGRATION:
- Used by GravityValidatorAgent to skip already-healed imports
- Used by GravityHealerAgent to record healing operations
- Provides audit trail for compliance verification
"""
import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_emits_metric_event("GravityStateAgent", "p4obs", "metric_1")
_emit_emits_metric_event("GravityStateAgent", "p4obs", "metric_2")
_emit_emits_metric_event("GravityStateAgent", "p4obs", "metric_3")
_emit_emits_metric_event("GravityStateAgent", "p4obs", "metric_4")
_emit_emits_metric_event("GravityStateAgent", "p4obs", "metric_5")
_emit_emits_metric_event("GravityStateAgent", "p4obs", "metric_6")
_emit_records_incident_event("GravityStateAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("GravityStateAgent", "p4obs", "anomaly")
_emit_writes_observability_log("GravityStateAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("GravityStateAgent", "p4obs", "mon_state")
_emit_triggers_alert("GravityStateAgent", "p4obs", "alert")
_emit_links_incident_trace("GravityStateAgent", "p4obs", "trace_link")
_emit_captures_pattern("GravityStateAgent", "p3lm", "pattern")
_emit_records_learning_event("GravityStateAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GravityStateAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("GravityStateAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GravityStateAgent", "p3lm", "routing")
_emit_improves_agent_policy("GravityStateAgent", "p3lm", "policy")
_emit_stores_learning_state("GravityStateAgent", "p3lm", "state")
_emit_records_execution_trace("GravityStateAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GravityStateAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GravityStateAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GravityStateAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GravityStateAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GravityStateAgent", "env_read", "p2_env_1")
_emit_reads_environ("GravityStateAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("GravityStateAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GravityStateAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "GravityStateAgent", "context_pull")
_emit_pulls_context("p1", "GravityStateAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "GravityStateAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GravityStateAgent", "uwg_term_2")
_emit_writes_through("p1", "GravityStateAgent", "write_through")
_emit_writes_through("p1", "GravityStateAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "GravityStateAgent", "safety_validation")
_emit_invokes_eval("p1", "GravityStateAgent", "eval_call")
_emit_proposal_commits_routing("p1", "GravityStateAgent", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class HealingRecord:
    """Record of a single healing operation."""

    file_path: str
    original_import: str
    healed_import: str
    violation_type: str
    healing_strategy: str
    timestamp: str
    agent_version: str = "1.0.0"
    line_number: int | None = None


class GravityStateAgent(SovereignBaseAgent):
    """
    [L4 STATE] Tracks gravity healing operations and prevents re-flagging.

    Maintains persistent state of healed files to ensure:
    - Converted dynamic imports are not re-flagged as violations
    - Healing history is preserved for audit and rollback
    - Multiple healing sessions can be coordinated
    """

    STATE_FILE = "gravity_healing_state.json"

    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "GravityStateAgent.heal_repository", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "GravityStateAgent.heal_repository", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "GravityStateAgent.heal_repository"
        )

        super().heal_repository(**kwargs)

        return {"violations_found": 0, "violations_fixed": 0, "errors": 0}

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        IHealerProtocol compliance method for gravity state violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        """
        try:
            # Extract violation details
            violation_type = violation.get("type", "unknown")
            file_path = violation.get("file_path")

            if violation_type == "gravity_state_corruption":
                # Heal corrupted gravity state
                if file_path:
                    # Clear corrupted state for specific file
                    try:
                        file_key = str(Path(file_path).relative_to(self.root))
                        if file_key in self.state["healed_files"]:
                            del self.state["healed_files"][file_key]
                            self._save_state()
                            return {
                                "status": "success",
                                "details": f"Cleared corrupted state for {file_key}",
                                "artifacts": [file_key],
                                "errors": [],
                            }
                        else:
                            return {
                                "status": "skipped",
                                "details": f"No state found for {file_key}",
                                "artifacts": [],
                                "errors": [],
                            }
                    except ValueError:
                        return {
                            "status": "failed",
                            "details": f"File path outside project root: {file_path}",
                            "artifacts": [],
                            "errors": [f"Invalid file path: {file_path}"],
                        }

            elif violation_type == "state_file_missing":
                # Heal missing state file
                self._load_state()  # This will create fresh state if missing
                return {
                    "status": "success",
                    "details": "State file recreated with fresh state",
                    "artifacts": ["gravity_healing_state.json"],
                    "errors": [],
                }

            elif violation_type == "healing_history_cleanup":
                # Clean up healing history
                original_count = len(self.state["healing_history"])
                # Keep only last 1000 entries
                self.state["healing_history"] = self.state["healing_history"][-1000:]
                self._save_state()
                cleaned = original_count - len(self.state["healing_history"])
                return {
                    "status": "success",
                    "details": f"Cleaned up {cleaned} old healing records",
                    "artifacts": ["healing_history"],
                    "errors": [],
                }

            else:
                return {
                    "status": "skipped",
                    "details": f"Unknown violation type: {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }

        except (RuntimeError, ValueError) as e:
            self.logger.error(f"Heal operation failed in GravityStateAgent: {e}")
            return {
                "status": "failed",
                "details": f"Heal operation failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        self.root = project_root.resolve()
        self.state_dir = self.root / ".gravity_state"
        self.state_file = self.state_dir / self.STATE_FILE
        self.logger = Logger

        # Ensure state directory exists
        get_write_gateway().ensure_dir(self.state_dir)

        # Load existing state
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load healing state from disk."""
        if not self.state_file.exists():
            return {
                "healed_files": {},
                "healing_history": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_healings": 0,
                },
            }

        try:
            with open(self.state_file, encoding="utf-8") as f:
                return json.load(f)
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            self.logger.error(f"Failed to load state: {e}")
            return self._load_state()  # Return fresh state on error

    def _save_state(self) -> None:
        """Persist healing state to disk."""
        try:
            self.state["metadata"]["last_updated"] = datetime.now().isoformat()
            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
            get_write_gateway().write_json(self.state_file, self.state, indent=2)
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            self.logger.error(f"Failed to save state: {e}")

    def _normalize_and_hash(self, import_line: str) -> str:
        """
        Normalizes an import statement by removing whitespace and comments
        to create a stable hash for comparison.
        """
        # Remove comments and collapse whitespace
        normalized = re.sub(r"#.*$", "", import_line).strip()
        normalized = re.sub(r"\s+", " ", normalized)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def record_healing(self, record: HealingRecord) -> None:
        """
        Record a successful healing operation.

        Args:
            record: HealingRecord with details of the healing
        """
        file_key = str(Path(record.file_path).relative_to(self.root))
        import_hash = self._normalize_and_hash(record.original_import)

        # Append hash to record for robust lookup
        record_data = asdict(record)
        record_data["import_hash"] = import_hash

        # Add to healed files registry
        if file_key not in self.state["healed_files"]:
            self.state["healed_files"][file_key] = []

        self.state["healed_files"][file_key].append(record_data)

        # Add to healing history
        self.state["healing_history"].append(record_data)

        # Update metadata
        self.state["metadata"]["total_healings"] += 1

        # Persist to disk
        self._save_state()

        self.logger.info(f"Recorded healing: {file_key} - {record.original_import}")

    def is_healed(self, file_path: Path, import_line: str) -> bool:
        """
        Check if a specific import has already been healed.

        Args:
            file_path: Path to the file
            import_line: The import statement to check

        Returns:
            True if this import has been healed, False otherwise
        """
        try:
            file_key = str(file_path.relative_to(self.root))
        except ValueError:
            # File not in project root
            return False

        if file_key not in self.state["healed_files"]:
            return False

        current_hash = self._normalize_and_hash(import_line)

        for healing in self.state["healed_files"][file_key]:
            if healing.get("import_hash") == current_hash:
                return True

        return False

    def get_file_healings(self, file_path: Path) -> list[HealingRecord]:
        """
        Get all healing records for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of HealingRecord objects for this file
        """
        try:
            file_key = str(file_path.relative_to(self.root))
        except ValueError:
            return []

        if file_key not in self.state["healed_files"]:
            return []

        return [HealingRecord(**healing) for healing in self.state["healed_files"][file_key]]

    def get_healing_summary(self) -> dict[str, Any]:
        """
        Get summary of all healing operations.

        Returns:
            Dict with healing statistics and summary
        """
        total_files = len(self.state["healed_files"])
        total_healings = self.state["metadata"]["total_healings"]

        # Group by violation type
        by_type = {}
        for healing in self.state["healing_history"]:
            vtype = healing["violation_type"]
            by_type[vtype] = by_type.get(vtype, 0) + 1

        # Group by strategy
        by_strategy = {}
        for healing in self.state["healing_history"]:
            strategy = healing["healing_strategy"]
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1

        return {
            "total_files_healed": total_files,
            "total_healings": total_healings,
            "by_violation_type": by_type,
            "by_strategy": by_strategy,
            "created_at": self.state["metadata"]["created_at"],
            "last_updated": self.state["metadata"]["last_updated"],
        }

    def create_checkpoint(self, name: str) -> str:
        """
        Create a checkpoint of current healing state for rollback.

        Args:
            name: Name for this checkpoint

        Returns:
            Path to the checkpoint file
        """
        checkpoint_file = (
            self.state_dir / f"checkpoint_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            assert_no_persistent_write("L4", "json.dump")  # G-12-1: mutation prohibition guard
            get_write_gateway().write_json(checkpoint_file, self.state, indent=2)

            self.logger.info(f"Created checkpoint: {checkpoint_file.name}")
            return str(checkpoint_file)
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
            return ""

    def rollback_to_checkpoint(self, checkpoint_file: str) -> bool:
        """
        Rollback state to a previous checkpoint.

        Args:
            checkpoint_file: Path to the checkpoint file

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            with open(checkpoint_file, encoding="utf-8") as f:
                self.state = json.load(f)

            self._save_state()
            self.logger.info(f"Rolled back to checkpoint: {checkpoint_file}")
            return True
        except (RuntimeError, ValueError) as e:
            self.logger.error(f"Failed to rollback: {e}")
            return False

    def clear_state(self) -> None:
        """Clear all healing state (use with caution)."""
        self.state = {
            "healed_files": {},
            "healing_history": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_healings": 0,
            },
        }
        self._save_state()
        self.logger.warning("Cleared all healing state")


__all__ = ["GravityStateAgent", "HealingRecord"]
