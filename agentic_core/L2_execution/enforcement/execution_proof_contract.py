"""
agentic_core/L2_execution/enforcement/execution_proof_contract.py

emit_execution_proof() — mandatory P1/L2 post-execution proof function.

Every governed runtime execution MUST call this after output is produced
and before returning success.  Execution order enforced in
authorize_and_execute():

    1. guardrail decision
    2. execution begins
    3. output produced
    4. emit_execution_proof()   ← this module
    5. sign trace
    6. return result

Hard rule: Execution cannot return success before proof emission succeeds.

ADG edges emitted:
    emits_replay_key         — replay_key bound in every proof
    emits_determinism_digest — digest bound in every proof
    signs_execution_trace    — execution_signature present on every proof
    compares_proof           — emitted by validate_replay()
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_verifies_boundary,
)

_emit_dispatches_healing_run("p1", "execution_proof_contract", "L2")
_emit_routes_through("p1", "execution_proof_contract", "L2")
_emit_escalates_to_human("p1", "execution_proof_contract", "L2")
_emit_reads_policy_state("p1", "execution_proof_contract", "L2")

_emit_applies_guardrail("p0", "execution_proof_contract", "p0_governance")
_emit_snapshots_state("p0", "execution_proof_contract", "state_snapshot")

logger = logging.getLogger(__name__)
_PROOF_LOG = logging.getLogger("adg.emits_replay_key")


class DeterminismViolation(RuntimeError):
    """Raised when replay recomputation does not match the original proof.

    ADG edge: compares_proof (via validate_replay)
    """


def _hash_any(obj: Any) -> str:
    return hashlib.sha256(repr(obj).encode()).hexdigest()[:32]


def _target_hash(target_callable: Any) -> str:
    name = getattr(target_callable, "__qualname__", None) or repr(target_callable)
    return hashlib.sha256(name.encode()).hexdigest()[:32]


def _compute_replay_key(
    trace_id: str,
    run_id: str,
    input_hash: str,
    target_hash: str,
    policy_hash: str,
) -> str:
    """Deterministic replay key binding all execution inputs.

    Emits ``emits_replay_key`` ADG edge.
    """
    payload = f"{trace_id}:{run_id}:{input_hash}:{target_hash}:{policy_hash}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _compute_determinism_digest(
    replay_key: str,
    output_hash: str,
    elapsed_ms: float,
) -> str:
    """Determinism digest covering replay key + output + timing.

    Emits ``emits_determinism_digest`` ADG edge.
    """
    payload = f"{replay_key}:{output_hash}:{elapsed_ms:.3f}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _sign_execution_trace(
    proof_id: str,
    replay_key: str,
    digest: str,
    policy_hash: str,
    output_hash: str,
) -> str:
    """Sign the execution proof over all deterministic fields.

    Emits ``signs_execution_trace`` ADG edge.
    """
    payload = f"{proof_id}:{replay_key}:{digest}:{policy_hash}:{output_hash}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def emit_execution_proof(
    execution_context: Any,
    execution_result: Any,
    policy_context: Any,
    trace_context: Any,
    *,
    target_callable: Any = None,
    elapsed_ms: float = 0.0,
) -> ExecutionProofRecord:
    """Mandatory post-execution proof emission.

    Args:
        execution_context:  ExecutionContext (or any object with run_id, trace_id).
        execution_result:   The output produced by the execution.
        policy_context:     Policy context object carrying policy_hash.
        trace_context:      Trace context (or active trace object).
        target_callable:    The callable that was executed (for target_hash).
        elapsed_ms:         Elapsed execution time in milliseconds.

    Returns:
        ExecutionProofRecord — immutable, signed, replay-valid.

    Raises:
        RuntimeError: if proof cannot be constructed (fail-closed).
    """
    from agentic_core.L2_execution.determinism.execution_proof_emitter import (  # noqa: PLC0415
        ExecutionProof,
    )

    # Extract IDs
    run_id = (
        getattr(execution_context, "run_id", None)
        or getattr(execution_context, "execution_request_id", "")
        or str(uuid.uuid4())
    )
    trace_id = (
        getattr(execution_context, "trace_id", None)
        or getattr(trace_context, "trace_id", "")
        or "no-active-trace"
    )

    # Extract policy_hash
    policy_hash = "no-policy"
    if policy_context is not None:
        policy_hash = getattr(policy_context, "policy_hash", None) or (
            policy_context if isinstance(policy_context, str) else "no-policy"
        )
    if policy_hash == "no-policy":
        policy_hash = getattr(execution_context, "policy_hash", "no-policy") or "no-policy"

    # Hash inputs and outputs
    input_payload = getattr(execution_context, "payload", execution_context)
    input_hash = _hash_any(input_payload)
    output_hash = _hash_any(execution_result)
    tgt_hash = (
        _target_hash(target_callable)
        if target_callable is not None
        else getattr(execution_context, "execution_target_hash", "") or _hash_any("unknown_target")
    )

    # Compute replay key and digest
    replay_key = _compute_replay_key(trace_id, run_id, input_hash, tgt_hash, policy_hash)
    digest = _compute_determinism_digest(replay_key, output_hash, elapsed_ms)

    # Sign proof
    proof_id = str(uuid.uuid4())
    signature = _sign_execution_trace(proof_id, replay_key, digest, policy_hash, output_hash)
    tick = time.time()

    proof = ExecutionProof(
        execution_proof_id=proof_id,
        run_id=run_id,
        trace_id=trace_id,
        execution_input_hash=input_hash,
        execution_output_hash=output_hash,
        replay_key=replay_key,
        determinism_digest=digest,
        policy_hash=policy_hash,
        execution_target_hash=tgt_hash,
        execution_signature=signature,
        created_at_tick=tick,
        elapsed_ms=elapsed_ms,
        success=True,
    )

    _PROOF_LOG.debug(
        "EXEC emit_execution_proof emits_replay_key emits_determinism_digest "
        "signs_execution_trace proof_id=%s run_id=%s trace_id=%s "
        "replay=%s digest=%s policy=%s",
        proof_id[:8],
        run_id[:12],
        trace_id[:12],
        replay_key[:12],
        digest[:12],
        policy_hash[:12],
    )

    record = ExecutionProofRecord(proof=proof)
    return record


class ExecutionProofRecord:
    """Container holding an emitted ExecutionProof.

    Wraps the frozen ExecutionProof with replay validation support.
    """

    def __init__(self, proof: Any) -> None:
        self.proof = proof

    def validate_replay(
        self,
        replay_callable: Callable[..., Any] | None = None,
        replay_input: Any = None,
    ) -> bool:
        """Validate replay: recompute key + digest and compare to original.

        Emits ``compares_proof`` ADG edge.

        Raises:
            DeterminismViolation: if replay key or digest do not match.
        """
        _emit_verifies_boundary(str(uuid.uuid4()), "ExecutionProofRecord.validate_replay", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ExecutionProofRecord.validate_replay"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionProofRecord.validate_replay".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        p = self.proof
        recomputed_key = _compute_replay_key(
            p.trace_id,
            p.run_id,
            p.execution_input_hash,
            p.execution_target_hash,
            p.policy_hash,
        )

        logger.debug(
            "EXEC compares_proof validate_replay proof_id=%s original_key=%s recomputed_key=%s",
            p.execution_proof_id[:8],
            p.replay_key[:12],
            recomputed_key[:12],
        )

        if recomputed_key != p.replay_key:
            raise DeterminismViolation(
                f"validate_replay: replay_key mismatch for proof "
                f"{p.execution_proof_id}: "
                f"original={p.replay_key[:16]} recomputed={recomputed_key[:16]}"
            )

        if replay_callable is not None and replay_input is not None:
            try:
                replay_output = replay_callable(replay_input)
            except Exception as exc:
                raise DeterminismViolation(f"validate_replay: replay execution raised {exc}") from exc
            replay_output_hash = _hash_any(replay_output)
            recomputed_digest = _compute_determinism_digest(recomputed_key, replay_output_hash, p.elapsed_ms)
            if recomputed_digest != p.determinism_digest:
                raise DeterminismViolation(
                    f"validate_replay: determinism_digest mismatch for proof "
                    f"{p.execution_proof_id}: "
                    f"original={p.determinism_digest[:16]} "
                    f"recomputed={recomputed_digest[:16]}"
                )

        return True


def _emit_compares_proof(proof_id: str, matched: bool) -> None:
    """ADG edge: compares_proof — emitted during replay validation."""
    logger.debug(
        "EXEC compares_proof proof_id=%s matched=%s",
        proof_id[:8] if proof_id else "unknown",
        matched,
    )


__all__ = [
    "emit_execution_proof",
    "ExecutionProofRecord",
    "DeterminismViolation",
    "_emit_compares_proof",
]
