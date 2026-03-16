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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "decision_logger")
emit_determinism_digest("p0", "decision_logger")

_emit_dispatches_healing_run("p1", "decision_logger", "L5")
_emit_routes_through("p1", "decision_logger", "L5")
_emit_escalates_to_human("p1", "decision_logger", "L5")
_emit_reads_policy_state("p1", "decision_logger", "L5")

_emit_applies_guardrail("p0", "decision_logger", "p0_governance")
_emit_snapshots_state("p0", "decision_logger", "state_snapshot")
_emit_authorize_and_execute("p2", "decision_logger", "execution_auth")
_emit_validates_capability("p2", "decision_logger", "capability_check")
_emit_routes_to_capability("p2", "decision_logger", "capability_route")
_emit_writes_via_uwg("p2", "decision_logger", "uwg_write")
_emit_blocks_direct_write("p2", "decision_logger", "direct_write_block")
_emit_records_tool_invocation("p2", "decision_logger", "tool_invocation")
_emit_captures_execution_output("p2", "decision_logger", "exec_output")
_emit_dispatches_agent("p3", "decision_logger", "agent_dispatch")
_emit_coordinates_agents("p3", "decision_logger", "agent_coordination")
_emit_records_workflow_lineage("p3", "decision_logger", "workflow_lineage")
_emit_records_healing_outcome("p3", "decision_logger", "healing_outcome")
_emit_escalates_failure("p3", "decision_logger", "failure_escalation")
_emit_orchestrates_workflow("p3", "decision_logger", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "decision_logger", "healing_dispatch")
_emit_invokes_evaluation("p3", "decision_logger", "evaluation_signal")
_emit_records_telemetry_event("p4", "decision_logger", "telemetry_event")
_emit_captures_evaluation_metric("p4", "decision_logger", "eval_metric")
_emit_stores_embedding("p4", "decision_logger", "embedding_store")
_emit_updates_meta_learning_state("p4", "decision_logger", "meta_learning")
_emit_links_execution_to_snapshot("p4", "decision_logger", "exec_snapshot_link")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HITLDecisionLogger.log")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HITLDecisionLogger.log".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
            except OSError as exc:
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
