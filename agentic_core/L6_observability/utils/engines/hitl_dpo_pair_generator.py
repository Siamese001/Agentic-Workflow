"""DPO Pair Generator - deterministic human-in-the-loop feedback processing.

Converts APPROVE/REJECT decisions into DPO pairs with stable hashing.
"""

from __future__ import annotations

import hashlib
from typing import Protocol

from agentic_core.L6_observability.types.dpo_types import DPOExampleId, DPOPair
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    record_execution_trace,
)

record_execution_trace("hitl_dpo_pair_generator", "hitl_dpo_pair_generator_trace")


class DPOPairGenerator(Protocol):
    """Protocol for generating DPO pairs from human feedback."""

    def generate(
        self,
        *,
        control_output_bytes: bytes,
        candidate_output_bytes: bytes,
        human_decision: str,
        reason_codes: tuple[str, ...],
    ) -> DPOPair:
        """Generate a DPO pair from human feedback.

        Parameters:
            control_output_bytes: Raw bytes of control output.
            candidate_output_bytes: Raw bytes of candidate output.
            human_decision: Human decision ("APPROVE" or "REJECT").
            reason_codes: Tuple of short deterministic reason codes.

        Returns:
            DPOPair with deterministic hashing.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DPOPairGenerator.generate", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DPOPairGenerator.generate", "p0_governance")
        ...


class DefaultDeterministicDPOPairGenerator:
    """Default deterministic DPO pair generator.

    Generates stable DPO pairs with SHA-256 hashing and no side effects.
    """

    def generate(
        self,
        *,
        control_output_bytes: bytes,
        candidate_output_bytes: bytes,
        human_decision: str,
        reason_codes: tuple[str, ...],
    ) -> DPOPair:
        """Generate a DPO pair with deterministic behavior.

        Args:
            control_output_bytes: Raw bytes of control output.
            candidate_output_bytes: Raw bytes of candidate output.
            human_decision: Human decision ("APPROVE" or "REJECT").
            reason_codes: Tuple of short deterministic reason codes.

        Returns:
            DPOPair with stable example_id and content_hash.

        Raises:
            ValueError: If human_decision is not "APPROVE" or "REJECT".
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "DefaultDeterministicDPOPairGenerator.generate",
        )

        if human_decision not in {"APPROVE", "REJECT"}:
            raise ValueError(f"human_decision must be 'APPROVE' or 'REJECT', got: {human_decision}")
        control_hash = hashlib.sha256(control_output_bytes).hexdigest()
        candidate_hash = hashlib.sha256(candidate_output_bytes).hexdigest()
        example_id = DPOExampleId(control_hash=control_hash, candidate_hash=candidate_hash)
        pair = DPOPair(
            example_id=example_id,
            control_output_hash=control_hash,
            candidate_output_hash=candidate_hash,
            human_decision=human_decision,
            reasons=reason_codes,
        )
        return pair
