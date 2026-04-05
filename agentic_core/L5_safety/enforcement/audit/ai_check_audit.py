"""GAP-C / Phase 9: AI-Checking-AI Unified Audit Trail.

Thread-safe JSONL emitter. Schema:
  {timestamp_utc, component, model_id, input_hash, verdict, confidence,
   human_enqueued, trace_id}

CI invariant: zero entries with confidence < 0.5 AND human_enqueued == false.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

from agentic_core.runtime.lifecycle_trace_contract import (
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

logger = logging.getLogger(__name__)
_DEFAULT_AUDIT_PATH = Path("artifacts/audit/ai_check_audit.jsonl")
_LOCK = threading.Lock()
_HUMAN_ENQUEUE_THRESHOLD = 0.7


@dataclass
class AICheckAuditRecord:
    """Single AI-checking-AI audit record."""

    timestamp_utc: str
    component: str
    model_id: str
    input_hash: str
    verdict: str
    confidence: float
    human_enqueued: bool
    trace_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)


class AICheckAuditEmitter:
    """Thread-safe JSONL audit emitter for AI-check decisions.

    Usage:
        emitter = AICheckAuditEmitter()
        emitter.emit(
            component="JudgeEvaluator",
            model_id="gemini-2.5-pro",
            input_data="some input string",
            verdict="PASS",
            confidence=0.92,
            trace_id="abc123",
        )
    """

    def __init__(self, audit_path: Path | None = None) -> None:
        self._path = audit_path or _DEFAULT_AUDIT_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash_input(input_data: Any) -> str:
        """Deterministic SHA256 of the input."""
        raw = json.dumps(input_data, sort_keys=True, ensure_ascii=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def emit(
        self,
        component: str,
        model_id: str,
        input_data: Any,
        verdict: str,
        confidence: float,
        trace_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> AICheckAuditRecord:
        """Emit a single audit record.

        Automatically sets human_enqueued=True when confidence < 0.7 (C5 rule).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AICheckAuditEmitter.emit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AICheckAuditEmitter.emit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        human_enqueued = confidence < _HUMAN_ENQUEUE_THRESHOLD
        record = AICheckAuditRecord(
            timestamp_utc=datetime.now(tz=timezone.utc).isoformat(),
            component=component,
            model_id=model_id,
            input_hash=self._hash_input(input_data),
            verdict=verdict,
            confidence=confidence,
            human_enqueued=human_enqueued,
            trace_id=trace_id,
            metadata=metadata or {},
        )
        with _LOCK:
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(record.to_jsonl() + "\n")
            except OSError as exc:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                logger.warning("AICheckAuditEmitter: write failed: %s", exc)
        if human_enqueued:
            logger.warning(
                "AI-check confidence %.2f < %.2f — human_enqueued=True [%s component=%s]",
                confidence,
                _HUMAN_ENQUEUE_THRESHOLD,
                trace_id,
                component,
            )
        return record

    def read_all(self) -> list[AICheckAuditRecord]:
        """Read all audit records from the JSONL file."""
        records: list[AICheckAuditRecord] = []
        if not self._path.exists():
            return records
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    records.append(AICheckAuditRecord(**d))
                except (json.JSONDecodeError, TypeError):
                    continue
        return records

    def check_ci_invariant(self) -> list[str]:
        """CI: Return violations where confidence < 0.5 AND human_enqueued == False."""
        violations: list[str] = []
        for rec in self.read_all():
            if rec.confidence < 0.5 and (not rec.human_enqueued):
                violations.append(
                    f"[{rec.trace_id}] {rec.component}: confidence={rec.confidence:.2f} but human_enqueued=False — policy violation"
                )
        return violations


_DEFAULT_EMITTER: AICheckAuditEmitter | None = None


def get_audit_emitter(path: Path | None = None) -> AICheckAuditEmitter:
    """Return the module-level default emitter (singleton pattern)."""
    global _DEFAULT_EMITTER
    if _DEFAULT_EMITTER is None:
        _DEFAULT_EMITTER = AICheckAuditEmitter(audit_path=path)
    return _DEFAULT_EMITTER


__all__ = ["AICheckAuditEmitter", "AICheckAuditRecord", "get_audit_emitter"]
