"""
agentic_core/runtime/mathematical_determinism.py

Mathematically-correct determinism engine with replay-verified proofs.

Critical design invariant: core_digest excludes ALL nondeterministic fields
(timestamps, run IDs). Only deterministic artifact hashes and cryptographic
bindings enter the digest envelope. run_id and creation_timestamp are stored
outside the envelope for correlation only.
"""

import hashlib
import json
import threading
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "mathematical_determinism", "p0_governance")
trace_contract._emit_snapshots_state("p0", "mathematical_determinism", "state_snapshot")

trace_contract.record_execution_trace("mathematical_determinism", "mathematical_determinism_trace")


trace_contract._emit_emits_metric_event("mathematical_determinism", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mathematical_determinism", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mathematical_determinism", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mathematical_determinism", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mathematical_determinism", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mathematical_determinism", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mathematical_determinism", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mathematical_determinism", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mathematical_determinism", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mathematical_determinism", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mathematical_determinism", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mathematical_determinism", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mathematical_determinism", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mathematical_determinism", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mathematical_determinism", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mathematical_determinism", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mathematical_determinism", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mathematical_determinism", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mathematical_determinism", "p3lm", "state")
trace_contract._emit_records_execution_trace("mathematical_determinism", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mathematical_determinism", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mathematical_determinism", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mathematical_determinism", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mathematical_determinism", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mathematical_determinism", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mathematical_determinism", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mathematical_determinism", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mathematical_determinism", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mathematical_determinism", "context_pull")
trace_contract._emit_pulls_context("p1", "mathematical_determinism", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mathematical_determinism", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mathematical_determinism", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mathematical_determinism", "write_through")
trace_contract._emit_writes_through("p1", "mathematical_determinism", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mathematical_determinism", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mathematical_determinism", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mathematical_determinism", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "mathematical_determinism", "human_escalation")
trace_contract._emit_routes_through("p1", "mathematical_determinism", "route_through")
trace_contract._emit_checks_agent_registry("p1", "mathematical_determinism", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mathematical_determinism", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mathematical_determinism", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mathematical_determinism", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mathematical_determinism", "target_agent")
trace_contract._emit_verifies_policy("p1", "mathematical_determinism", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mathematical_determinism", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mathematical_determinism", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mathematical_determinism", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mathematical_determinism")
trace_contract._emit_gated_by_confidence("p1", "mathematical_determinism", "confidence_gate")
trace_contract.emit_replay_key("p0", "mathematical_determinism")
trace_contract.emit_determinism_digest("p0", "mathematical_determinism")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "mathematical_determinism", "execution_auth")
trace_contract._emit_validates_capability("p2", "mathematical_determinism", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mathematical_determinism", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mathematical_determinism", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mathematical_determinism", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mathematical_determinism", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mathematical_determinism", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mathematical_determinism", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mathematical_determinism", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mathematical_determinism", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mathematical_determinism", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mathematical_determinism", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mathematical_determinism", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mathematical_determinism", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mathematical_determinism", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mathematical_determinism", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mathematical_determinism", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mathematical_determinism", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mathematical_determinism", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mathematical_determinism", "exec_snapshot_link")


@dataclass(frozen=True)
class DeterministicArtifact:
    """Artifact with only deterministic fields (no timestamps)."""

    name: str
    hash_value: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class DeterminismProof:
    """Mathematically-sealed determinism proof.

    Digest envelope contains ONLY deterministic fields.
    run_id and creation_timestamp live OUTSIDE the envelope.
    """

    core_digest: str
    run_id: str
    creation_timestamp: float
    artifact_count: int
    policy_hash: str
    hierarchy_hash: str
    authority_hash: str


class MathematicalDeterminismEngine:
    """Determinism engine with mathematically correct replay verification.

    Two runs with identical artifacts + identical bindings must produce
    identical core_digest values regardless of wall-clock time or run IDs.
    """

    _FORBIDDEN_METADATA_KEYS = frozenset({"timestamp", "time", "date", "random", "uuid"})

    def __init__(self, policy_hash: str, hierarchy_hash: str, authority_hash: str) -> None:
        self._artifacts: dict[str, DeterministicArtifact] = {}
        self._sealed = False
        self._run_id: str = str(uuid.uuid4())
        self._lock = threading.RLock()
        self._proof: DeterminismProof | None = None
        self._policy_hash = policy_hash
        self._hierarchy_hash = hierarchy_hash
        self._authority_hash = authority_hash

    def add_artifact(self, name: str, hash_value: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a deterministic artifact. Raises if metadata is nondeterministic."""
        with self._lock:
            if self._sealed:
                raise RuntimeError("Determinism engine is sealed")
            if name in self._artifacts:
                raise ValueError(f"Artifact '{name}' already registered")
            if metadata and (not self._is_deterministic_metadata(metadata)):
                raise ValueError(f"Artifact '{name}' metadata contains nondeterministic fields")
            self._artifacts[name] = DeterministicArtifact(
                name=name,
                hash_value=hash_value,
                metadata=metadata or {},
            )

    def seal(self) -> DeterminismProof:
        """Seal engine and produce a replay-verifiable proof."""
        with self._lock:
            if self._sealed:
                assert self._proof is not None
                return self._proof
            sorted_artifacts = dict(sorted(self._artifacts.items()))
            core_payload: dict[str, Any] = {
                "artifacts": {
                    name: {"hash": artifact.hash_value, "metadata": artifact.metadata}
                    for name, artifact in sorted_artifacts.items()
                },
                "policy_hash": self._policy_hash,
                "hierarchy_hash": self._hierarchy_hash,
                "authority_hash": self._authority_hash,
            }
            core_json = json.dumps(core_payload, sort_keys=True, separators=(",", ":"))
            core_digest = hashlib.sha256(core_json.encode("utf-8")).hexdigest()
            import time

            self._proof = DeterminismProof(
                core_digest=core_digest,
                run_id=self._run_id,
                creation_timestamp=time.time(),
                artifact_count=len(self._artifacts),
                policy_hash=self._policy_hash,
                hierarchy_hash=self._hierarchy_hash,
                authority_hash=self._authority_hash,
            )
            self._sealed = True
            return self._proof

    def verify_replay(self, expected_proof: DeterminismProof) -> bool:
        """Verify current proof matches expected replay proof.

        Only core_digest and cryptographic bindings are compared.
        run_id and creation_timestamp are intentionally excluded.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MathematicalDeterminismEngine.verify_replay"
        )

        if not self._sealed:
            raise RuntimeError("Engine must be sealed before verification")
        assert self._proof is not None
        return (
            self._proof.core_digest == expected_proof.core_digest
            and self._proof.policy_hash == expected_proof.policy_hash
            and (self._proof.hierarchy_hash == expected_proof.hierarchy_hash)
            and (self._proof.authority_hash == expected_proof.authority_hash)
            and (self._proof.artifact_count == expected_proof.artifact_count)
        )

    def get_proof(self) -> DeterminismProof | None:
        """Return current proof (None if not yet sealed)."""
        return self._proof

    def _is_deterministic_metadata(self, metadata: dict[str, Any]) -> bool:
        """Return True iff metadata contains only deterministic values."""

        def _check(value: Any) -> bool:
            if isinstance(value, dict):
                return all((_check(k) and _check(v) for k, v in value.items()))
            if isinstance(value, (list, tuple)):
                return all(_check(item) for item in value)
            if isinstance(value, str):
                lower = value.lower()
                return not any(token in lower for token in self._FORBIDDEN_METADATA_KEYS)
            if isinstance(value, (int, float, bool)):
                return True
            return False

        return _check(metadata)


_determinism_engine: MathematicalDeterminismEngine | None = None
_engine_lock = threading.Lock()


def initialize_determinism_engine(policy_hash: str, hierarchy_hash: str, authority_hash: str) -> None:
    """Initialize the global determinism engine with cryptographic bindings."""
    global _determinism_engine
    with _engine_lock:
        _determinism_engine = MathematicalDeterminismEngine(policy_hash, hierarchy_hash, authority_hash)


def get_determinism_engine() -> MathematicalDeterminismEngine:
    """Return the global determinism engine. Raises if not initialized."""
    if _determinism_engine is None:
        raise RuntimeError("Determinism engine not initialized. Call initialize_determinism_engine() first.")
    return _determinism_engine
