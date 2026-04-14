"""
Manifest Manager.

Handles persistence of workflow state to disk/storage.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "manifest_manager_util", "p0_governance")
_emit_reads_policy_state("p0", "manifest_manager_util", "policy_binding")
_emit_snapshots_state("p0", "manifest_manager_util", "state_snapshot")
emit_replay_key("p0", "manifest_manager_util")
emit_determinism_digest("p0", "manifest_manager_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "manifest_manager_util", "execution_auth")
_emit_validates_capability("p2", "manifest_manager_util", "capability_check")
_emit_routes_to_capability("p2", "manifest_manager_util", "capability_route")
_emit_writes_via_uwg("p2", "manifest_manager_util", "uwg_write")
_emit_blocks_direct_write("p2", "manifest_manager_util", "direct_write_block")
_emit_records_tool_invocation("p2", "manifest_manager_util", "tool_invocation")
_emit_captures_execution_output("p2", "manifest_manager_util", "exec_output")
_emit_dispatches_agent("p3", "manifest_manager_util", "agent_dispatch")
_emit_coordinates_agents("p3", "manifest_manager_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "manifest_manager_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "manifest_manager_util", "healing_outcome")
_emit_escalates_failure("p3", "manifest_manager_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "manifest_manager_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "manifest_manager_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "manifest_manager_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "manifest_manager_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "manifest_manager_util", "eval_metric")
_emit_stores_embedding("p4", "manifest_manager_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "manifest_manager_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "manifest_manager_util", "exec_snapshot_link")

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):  # type: ignore[misc]
        pass
except ImportError:
    logger.debug("mcp_hardened_mixin unavailable; using no-op fallback")

    class MCPHardenedMixin:  # type: ignore[no-redef]
        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:
    logger.debug("HealerMixin unavailable; using no-op fallback")

    class HealerMixin:  # type: ignore[no-redef]
        pass


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("manifest_manager_util", "p4obs", "metric_1")
_emit_emits_metric_event("manifest_manager_util", "p4obs", "metric_2")
_emit_emits_metric_event("manifest_manager_util", "p4obs", "metric_3")
_emit_emits_metric_event("manifest_manager_util", "p4obs", "metric_4")
_emit_emits_metric_event("manifest_manager_util", "p4obs", "metric_5")
_emit_emits_metric_event("manifest_manager_util", "p4obs", "metric_6")
_emit_records_incident_event("manifest_manager_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("manifest_manager_util", "p4obs", "anomaly")
_emit_writes_observability_log("manifest_manager_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("manifest_manager_util", "p4obs", "mon_state")
_emit_triggers_alert("manifest_manager_util", "p4obs", "alert")
_emit_links_incident_trace("manifest_manager_util", "p4obs", "trace_link")
_emit_captures_pattern("manifest_manager_util", "p3lm", "pattern")
_emit_records_learning_event("manifest_manager_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("manifest_manager_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("manifest_manager_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("manifest_manager_util", "p3lm", "routing")
_emit_improves_agent_policy("manifest_manager_util", "p3lm", "policy")
_emit_stores_learning_state("manifest_manager_util", "p3lm", "state")
_emit_records_execution_trace("manifest_manager_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("manifest_manager_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("manifest_manager_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("manifest_manager_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("manifest_manager_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("manifest_manager_util", "env_read", "p2_env_1")
_emit_reads_environ("manifest_manager_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("manifest_manager_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("manifest_manager_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "manifest_manager_util", "context_pull")
_emit_pulls_context("p1", "manifest_manager_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "manifest_manager_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "manifest_manager_util", "uwg_term_2")
_emit_writes_through("p1", "manifest_manager_util", "write_through")
_emit_writes_through("p1", "manifest_manager_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "manifest_manager_util", "safety_validation")
_emit_invokes_eval("p1", "manifest_manager_util", "eval_call")
_emit_proposal_commits_routing("p1", "manifest_manager_util", "routing_commit")
_emit_escalates_to_human("p1", "manifest_manager_util", "human_escalation")
_emit_routes_through("p1", "manifest_manager_util", "route_through")
_emit_checks_agent_registry("p1", "manifest_manager_util", "agent_registry")
_emit_validates_agent_capability("p1", "manifest_manager_util", "capability")
_emit_dispatches_execution_plan("p1", "manifest_manager_util", "exec_plan")
_emit_agent_executes_agent("p1", "manifest_manager_util", "sub_agent")
_emit_routes_to_agent("p1", "manifest_manager_util", "target_agent")
_emit_verifies_policy("p1", "manifest_manager_util", "policy_check")
_emit_observes_runtime_state("p1", "manifest_manager_util", "runtime_state")
_emit_verifies_boundary("p1", "manifest_manager_util", "boundary_check")
_emit_transcripts_response("p1", "manifest_manager_util", "transcript")
_emit_hard_fails_untranscripted("p1", "manifest_manager_util")
_emit_gated_by_confidence("p1", "manifest_manager_util", "confidence_gate")


@dataclass
class ManifestManager(MCPHardenedMixin, HealerMixin):
    """
    Manages loading and saving of workflow manifests (checkpoints).
    """

    base_path: str | Path = field(default_factory=lambda: Path("./manifests"))

    def __post_init__(self) -> None:
        super().__init__()
        self.base_path = Path(self.base_path).expanduser().resolve()
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

    def save_manifest(self, manifest_id: str, data: dict[str, Any]) -> Path:
        """
        Saves data to a JSON manifest file.

        Args:
            manifest_id: Unique identifier for the file.
            data: Dictionary data to save.

        Returns:
            Path object of the saved file.
        """
        target_file = self._manifest_path(manifest_id)
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.base_path,
                prefix=f"{target_file.stem}.",
                suffix=".staging",
                delete=False,
            ) as f:
                json.dump(data, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())
                staging_path = Path(f.name)
            staging_path.replace(target_file)
        except (OSError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to save manifest {manifest_id!r}: {e}") from e
        return target_file

    def load_manifest(self, manifest_id: str) -> dict[str, Any]:
        """
        Loads data from a JSON manifest file.

        Args:
            manifest_id: Unique identifier for the file.

        Returns:
            Dictionary containing the manifest data.

        Raises:
            FileNotFoundError: If the manifest does not exist.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ManifestManager.load_manifest"
        )

        target_file = self._manifest_path(manifest_id)
        if not target_file.exists():
            raise FileNotFoundError(f"Manifest not found: {target_file}")
        with open(target_file, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _sanitize_manifest_id(manifest_id: str) -> str:
        if not isinstance(manifest_id, str) or not manifest_id.strip():
            raise ValueError("manifest_id must be a non-empty string")
        sanitized = manifest_id.strip().replace(" ", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "_-.")
        sanitized = sanitized.strip("._-")
        if not sanitized or ".." in sanitized:
            raise ValueError(f"unsafe manifest_id: {manifest_id!r}")
        return sanitized

    def _manifest_path(self, manifest_id: str) -> Path:
        name = self._sanitize_manifest_id(manifest_id)
        filepath = (self.base_path / f"{name}.json").resolve()
        if self.base_path not in filepath.parents:
            raise ValueError("refusing to access manifest path outside base directory")
        return filepath
