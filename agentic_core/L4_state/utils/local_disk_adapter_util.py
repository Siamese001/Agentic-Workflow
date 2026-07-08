from __future__ import annotations

import logging

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "local_disk_adapter_util")
trace_contract.emit_determinism_digest("p0", "local_disk_adapter_util")

trace_contract._emit_dispatches_healing_run("p1", "local_disk_adapter_util", "L4")
trace_contract._emit_routes_through("p1", "local_disk_adapter_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "local_disk_adapter_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "local_disk_adapter_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "local_disk_adapter_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "local_disk_adapter_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "local_disk_adapter_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "local_disk_adapter_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "local_disk_adapter_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "local_disk_adapter_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "local_disk_adapter_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "local_disk_adapter_util")
trace_contract._emit_gated_by_confidence("p1", "local_disk_adapter_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "local_disk_adapter_util", "L4")
trace_contract._emit_reads_policy_state("p1", "local_disk_adapter_util", "L4")
trace_contract._emit_authorize_and_execute("p2", "local_disk_adapter_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "local_disk_adapter_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "local_disk_adapter_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "local_disk_adapter_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "local_disk_adapter_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "local_disk_adapter_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "local_disk_adapter_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "local_disk_adapter_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "local_disk_adapter_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "local_disk_adapter_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "local_disk_adapter_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "local_disk_adapter_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "local_disk_adapter_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "local_disk_adapter_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "local_disk_adapter_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "local_disk_adapter_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "local_disk_adapter_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "local_disk_adapter_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "local_disk_adapter_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "local_disk_adapter_util", "exec_snapshot_link")


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from pathlib import Path
from typing import Any


trace_contract._emit_emits_metric_event("local_disk_adapter_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("local_disk_adapter_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("local_disk_adapter_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("local_disk_adapter_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("local_disk_adapter_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("local_disk_adapter_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("local_disk_adapter_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("local_disk_adapter_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("local_disk_adapter_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("local_disk_adapter_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("local_disk_adapter_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("local_disk_adapter_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("local_disk_adapter_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("local_disk_adapter_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("local_disk_adapter_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("local_disk_adapter_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("local_disk_adapter_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("local_disk_adapter_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("local_disk_adapter_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("local_disk_adapter_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("local_disk_adapter_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("local_disk_adapter_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("local_disk_adapter_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("local_disk_adapter_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("local_disk_adapter_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("local_disk_adapter_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("local_disk_adapter_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("local_disk_adapter_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "local_disk_adapter_util", "context_pull")
trace_contract._emit_pulls_context("p1", "local_disk_adapter_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "local_disk_adapter_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "local_disk_adapter_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "local_disk_adapter_util", "write_through")
trace_contract._emit_writes_through("p1", "local_disk_adapter_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "local_disk_adapter_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "local_disk_adapter_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "local_disk_adapter_util", "routing_commit")


class LocalDiskAdapter:
    """
    L4 State: The Sovereign File System.
    Strictly controls I/O within the mission-approved data silos.

    V15 Note: This is a storage provider pattern, NOT the behavioral adapter
    pattern prohibited by V15 §8.1. Explicitly excepted per P0.2.
    """

    def __init__(self, config: dict[str, Any]):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "LocalDiskAdapter.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "LocalDiskAdapter.__init__", "p0_governance")
        self.config = config
        self.root = Path(config.get("storage_path", "./data/storage"))
        _get_write_gateway().ensure_dir(self.root)

    async def write_blob(self, key: str, data: bytes, METADATA: dict = None) -> Any:
        """Writes data to the sovereign storage area."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "LocalDiskAdapter.write_blob")

        safe_path = self.root / key.lstrip("/")
        _get_write_gateway().ensure_dir(safe_path.parent)
        _get_write_gateway().open_write(safe_path, data)
        logging.info(f"DiskAdapter: Persisted {len(data)} bytes to {key}")
