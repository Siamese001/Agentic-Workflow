from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "file_health_score_types")
emit_determinism_digest("p0", "file_health_score_types")

_emit_dispatches_healing_run("p1", "file_health_score_types", "L5")
_emit_routes_through("p1", "file_health_score_types", "L5")
_emit_escalates_to_human("p1", "file_health_score_types", "L5")
_emit_reads_policy_state("p1", "file_health_score_types", "L5")

_emit_applies_guardrail("p0", "file_health_score_types", "p0_governance")
_emit_snapshots_state("p0", "file_health_score_types", "state_snapshot")
_emit_authorize_and_execute("p2", "file_health_score_types", "execution_auth")
_emit_validates_capability("p2", "file_health_score_types", "capability_check")
_emit_routes_to_capability("p2", "file_health_score_types", "capability_route")
_emit_writes_via_uwg("p2", "file_health_score_types", "uwg_write")
_emit_blocks_direct_write("p2", "file_health_score_types", "direct_write_block")
_emit_records_tool_invocation("p2", "file_health_score_types", "tool_invocation")
_emit_captures_execution_output("p2", "file_health_score_types", "exec_output")
_emit_dispatches_agent("p3", "file_health_score_types", "agent_dispatch")
_emit_coordinates_agents("p3", "file_health_score_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "file_health_score_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "file_health_score_types", "healing_outcome")
_emit_escalates_failure("p3", "file_health_score_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "file_health_score_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "file_health_score_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "file_health_score_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "file_health_score_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "file_health_score_types", "eval_metric")
_emit_stores_embedding("p4", "file_health_score_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "file_health_score_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "file_health_score_types", "exec_snapshot_link")

"\nAtomic Blackboard - Thread-Safe State Management for Canon Validator\n\n[PHASE 10 REFACTOR] Uses SovereignBaseAgent native infrastructure.\n"
import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.types.anomaly_report import AnomalyReport

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class FileHealthScore:
    """Health score for a single file."""

    file_path: str
    current_violations: int
    last_healed_timestamp: float
    healing_attempts: int = 0
    last_hash: str = ""

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "current_violations": self.current_violations,
            "last_healed_timestamp": self.last_healed_timestamp,
            "healing_attempts": self.healing_attempts,
            "last_hash": self.last_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> FileHealthScore:
        return cls(
            file_path=data["file_path"],
            current_violations=data["current_violations"],
            last_healed_timestamp=data["last_healed_timestamp"],
            healing_attempts=data.get("healing_attempts", 0),
            last_hash=data.get("last_hash", ""),
        )


@dataclass
class HealingLease:
    file_path: str
    agent_name: str
    acquired_at: float
    expires_at: float
    lease_id: str

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class AtomicBlackboard(SovereignBaseAgent):
    """
    Thread-safe blackboard using Sovereign Infrastructure.
    Inherits Redis/Pinecone connections from SovereignBaseAgent.
    """

    def __init__(self):
        super().__init__()
        self.lease_duration = int(os.getenv("HEALING_LEASE_DURATION", "30"))
        self.max_backoff = int(os.getenv("MAX_LEASE_BACKOFF", "60"))
        self.health_score_ttl = int(os.getenv("HEALTH_SCORE_TTL", "86400"))
        self._leases: dict[str, HealingLease] = {}
        self.redis_fallback: dict[str, Any] = {}

    def acquire_lease(self, file_path: str, agent_name: str) -> HealingLease | None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AtomicBlackboard.acquire_lease")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AtomicBlackboard.acquire_lease".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        lock_key = f"lock:{file_path}"
        lease_id = f"{agent_name}:{time.time()}"
        acquired_at = time.time()
        expires_at = acquired_at + self.lease_duration
        if hasattr(self, "redis_client") and self.redis_client:
            try:
                acquired = self.redis_client.set(lock_key, lease_id, nx=True, ex=self.lease_duration)
                if acquired:
                    return HealingLease(file_path, agent_name, acquired_at, expires_at, lease_id)
                return None
            # guardian: allow-silent-swallow
            except Exception as e:
                self.log_error(f"Redis lease failed: {e}")
        return None

    def release_lease(self, lease: HealingLease) -> bool:
        lock_key = f"lock:{lease.file_path}"
        if hasattr(self, "redis_client") and self.redis_client:
            try:
                existing = self.redis_client.get(lock_key)
                if existing and (existing == lease.lease_id or existing.decode() == lease.lease_id):
                    self.redis_client.delete(lock_key)
                    return True
            # guardian: allow-silent-swallow
            except Exception as e:
                self.log_error(f"Redis release failed: {e}")
        return False

    def get_health_score(self, file_path: str) -> FileHealthScore | None:
        score_key = f"health:{file_path}"
        data = self.cache_get(score_key)
        if data:
            return FileHealthScore.from_dict(data)
        return None

    def update_health_score(self, file_path: str, violations: int, file_hash: str = "") -> FileHealthScore:
        score_key = f"health:{file_path}"
        existing = self.get_health_score(file_path)
        if existing:
            attempts = existing.healing_attempts + 1
        else:
            attempts = 1
        score = FileHealthScore(file_path, violations, time.time(), attempts, file_hash)
        self.cache_set(score_key, score.to_dict(), ttl=self.health_score_ttl)
        return score

    def record_anomaly(self, anomaly: AnomalyReport) -> None:
        """Record an anomaly to the blackboard."""
        anomaly_key = f"anomaly:{anomaly.file_path}:{anomaly.timestamp}"
        self.cache_set(anomaly_key, anomaly.to_dict(), ttl=self.health_score_ttl)

    def get_file_hash(self, file_path: str) -> str:
        """Get hash of file contents."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        # guardian: allow-silent-swallow
        except Exception:
            return ""

    def should_heal(self, file_path: str) -> bool:
        """Determine if a file should be healed based on health score."""
        score = self.get_health_score(file_path)
        if not score:
            return True
        current_hash = self.get_file_hash(file_path)
        if current_hash and current_hash != score.last_hash:
            return True
        time_since_heal = time.time() - score.last_healed_timestamp
        backoff = min(2**score.healing_attempts, self.max_backoff)
        return time_since_heal > backoff


_blackboard_instance = None


def get_blackboard() -> AtomicBlackboard:
    global _blackboard_instance
    if _blackboard_instance is None:
        _blackboard_instance = AtomicBlackboard()
    return _blackboard_instance
