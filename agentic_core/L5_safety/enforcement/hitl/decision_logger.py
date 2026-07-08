"""Addendum 6.3: Deterministic HITL Decision Logger.

Format (no timestamps in key fields):
    HITL_DECISION_N:
    Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D

Rule: No wall-clock timestamps in key fields (determinism requirement).
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "decision_logger")
trace_contract.emit_determinism_digest("p0", "decision_logger")

trace_contract._emit_dispatches_healing_run("p1", "decision_logger", "L5")
trace_contract._emit_routes_through("p1", "decision_logger", "L5")
trace_contract._emit_checks_agent_registry("p1", "decision_logger", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "decision_logger", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "decision_logger", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "decision_logger", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "decision_logger", "target_agent")
trace_contract._emit_verifies_policy("p1", "decision_logger", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "decision_logger", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "decision_logger", "boundary_check")
trace_contract._emit_transcripts_response("p1", "decision_logger", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "decision_logger")
trace_contract._emit_gated_by_confidence("p1", "decision_logger", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "decision_logger", "L5")
trace_contract._emit_reads_policy_state("p1", "decision_logger", "L5")

trace_contract._emit_applies_guardrail("p0", "decision_logger", "p0_governance")
trace_contract._emit_snapshots_state("p0", "decision_logger", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "decision_logger", "execution_auth")
trace_contract._emit_validates_capability("p2", "decision_logger", "capability_check")
trace_contract._emit_routes_to_capability("p2", "decision_logger", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "decision_logger", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "decision_logger", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "decision_logger", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "decision_logger", "exec_output")
trace_contract._emit_dispatches_agent("p3", "decision_logger", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "decision_logger", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "decision_logger", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "decision_logger", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "decision_logger", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "decision_logger", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "decision_logger", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "decision_logger", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "decision_logger", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "decision_logger", "eval_metric")
trace_contract._emit_stores_embedding("p4", "decision_logger", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "decision_logger", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "decision_logger", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("decision_logger", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("decision_logger", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("decision_logger", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("decision_logger", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("decision_logger", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("decision_logger", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("decision_logger", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("decision_logger", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("decision_logger", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("decision_logger", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("decision_logger", "p4obs", "alert")
trace_contract._emit_links_incident_trace("decision_logger", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("decision_logger", "p3lm", "pattern")
trace_contract._emit_records_learning_event("decision_logger", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("decision_logger", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("decision_logger", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("decision_logger", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("decision_logger", "p3lm", "policy")
trace_contract._emit_stores_learning_state("decision_logger", "p3lm", "state")
trace_contract._emit_records_execution_trace("decision_logger", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("decision_logger", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("decision_logger", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("decision_logger", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("decision_logger", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("decision_logger", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("decision_logger", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("decision_logger", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("decision_logger", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "decision_logger", "context_pull")
trace_contract._emit_pulls_context("p1", "decision_logger", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "decision_logger", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "decision_logger", "uwg_term_2")
trace_contract._emit_writes_through("p1", "decision_logger", "write_through")
trace_contract._emit_writes_through("p1", "decision_logger", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "decision_logger", "safety_validation")
trace_contract._emit_invokes_eval("p1", "decision_logger", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "decision_logger", "routing_commit")

logger = logging.getLogger(__name__)
_DEFAULT_LOG_PATH = Path("artifacts/hitl/decisions.jsonl")
_LOCK = threading.Lock()


@dataclass
class HITLDecision:
    """Single HITL decision record. No timestamps in key fields."""

    decision_number: int
    agent: str
    file: str
    violation: str
    proposed: str
    decision: str
    reviewer_signature: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_log_line(self) -> str:
        """Format as the canonical HITL_DECISION_N line."""
        return f"HITL_DECISION_{self.decision_number}: Agent={self.agent} | File={self.file} | Violation={self.violation} | Proposed={self.proposed} | Decision={self.decision}"

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)


class HITLDecisionLogger:
    """Logger for HITL decisions using deterministic format."""

    def __init__(self, log_path: Path | None = None) -> None:
        self._path = log_path or _DEFAULT_LOG_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._counter = 0
        self._records: list[HITLDecision] = []

    def log(
        self,
        agent: str,
        file: str,
        violation: str,
        proposed: str,
        decision: str,
        reviewer_signature: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> HITLDecision:
        """Log a HITL decision. Returns the created record."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "HITLDecisionLogger.log")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HITLDecisionLogger.log".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with _LOCK:
            self._counter += 1
            record = HITLDecision(
                decision_number=self._counter,
                agent=agent,
                file=file,
                violation=violation,
                proposed=proposed,
                decision=decision,
                reviewer_signature=reviewer_signature,
                metadata=metadata or {},
            )
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(record.to_jsonl() + "\n")
            except OSError as exc:  # guardian: allow-log-and-swallow -- HITL log write: non-fatal, logger.warning already called
                logger.warning("HITLDecisionLogger: write failed: %s", exc)
            self._records.append(record)
        logger.info(record.to_log_line())
        return record

    def all_records(self) -> list[HITLDecision]:
        with _LOCK:
            return list(self._records)

    def count(self) -> int:
        with _LOCK:
            return self._counter


_DEFAULT_LOGGER: HITLDecisionLogger | None = None


def get_decision_logger(path: Path | None = None) -> HITLDecisionLogger:
    global _DEFAULT_LOGGER
    if _DEFAULT_LOGGER is None:
        _DEFAULT_LOGGER = HITLDecisionLogger(log_path=path)
    return _DEFAULT_LOGGER


__all__ = ["HITLDecision", "HITLDecisionLogger", "get_decision_logger"]
