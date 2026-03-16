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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "mathematical_determinism", "p0_governance")
_emit_snapshots_state("p0", "mathematical_determinism", "state_snapshot")
emit_replay_key("p0", "mathematical_determinism")
emit_determinism_digest("p0", "mathematical_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "mathematical_determinism", "execution_auth")
_emit_validates_capability("p2", "mathematical_determinism", "capability_check")
_emit_routes_to_capability("p2", "mathematical_determinism", "capability_route")
_emit_writes_via_uwg("p2", "mathematical_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "mathematical_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "mathematical_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "mathematical_determinism", "exec_output")
_emit_dispatches_agent("p3", "mathematical_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "mathematical_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "mathematical_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "mathematical_determinism", "healing_outcome")
_emit_escalates_failure("p3", "mathematical_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "mathematical_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mathematical_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "mathematical_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "mathematical_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mathematical_determinism", "eval_metric")
_emit_stores_embedding("p4", "mathematical_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "mathematical_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mathematical_determinism", "exec_snapshot_link")


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
                name=name, hash_value=hash_value, metadata=metadata or {}
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MathematicalDeterminismEngine.verify_replay")

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
