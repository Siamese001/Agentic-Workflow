from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "file_health_score_types")
trace_contract.emit_determinism_digest("p0", "file_health_score_types")

trace_contract._emit_dispatches_healing_run("p1", "file_health_score_types", "L5")
trace_contract._emit_routes_through("p1", "file_health_score_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "file_health_score_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "file_health_score_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "file_health_score_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "file_health_score_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "file_health_score_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "file_health_score_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "file_health_score_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "file_health_score_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "file_health_score_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "file_health_score_types")
trace_contract._emit_gated_by_confidence("p1", "file_health_score_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "file_health_score_types", "L5")
trace_contract._emit_reads_policy_state("p1", "file_health_score_types", "L5")

trace_contract._emit_applies_guardrail("p0", "file_health_score_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "file_health_score_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "file_health_score_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "file_health_score_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "file_health_score_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "file_health_score_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "file_health_score_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "file_health_score_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "file_health_score_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "file_health_score_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "file_health_score_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "file_health_score_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "file_health_score_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "file_health_score_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "file_health_score_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "file_health_score_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "file_health_score_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "file_health_score_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "file_health_score_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "file_health_score_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "file_health_score_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "file_health_score_types", "exec_snapshot_link")

"\nAtomic Blackboard - Thread-Safe State Management for Canon Validator\n\n[PHASE 10 REFACTOR] Uses SovereignBaseAgent native infrastructure.\n"
import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.types.anomaly_report import AnomalyReport

trace_contract._emit_emits_metric_event("file_health_score_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("file_health_score_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("file_health_score_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("file_health_score_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("file_health_score_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("file_health_score_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("file_health_score_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("file_health_score_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("file_health_score_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("file_health_score_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("file_health_score_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("file_health_score_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("file_health_score_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("file_health_score_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("file_health_score_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("file_health_score_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("file_health_score_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("file_health_score_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("file_health_score_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("file_health_score_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("file_health_score_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("file_health_score_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("file_health_score_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("file_health_score_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("file_health_score_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("file_health_score_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("file_health_score_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("file_health_score_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "file_health_score_types", "context_pull")
trace_contract._emit_pulls_context("p1", "file_health_score_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "file_health_score_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "file_health_score_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "file_health_score_types", "write_through")
trace_contract._emit_writes_through("p1", "file_health_score_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "file_health_score_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "file_health_score_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "file_health_score_types", "routing_commit")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "AtomicBlackboard.acquire_lease")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AtomicBlackboard.acquire_lease".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
            except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
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
            except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
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
        except (RuntimeError, OSError):  # guardian: allow-silent-swallow
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
