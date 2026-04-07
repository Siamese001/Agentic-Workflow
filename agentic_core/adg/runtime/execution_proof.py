"""Execution Proof — runtime proof recording, replay keys, and trace comparison.

Provides deterministic execution proof infrastructure for ADG runtime:
- ExecutionTrace: captures a single execution's proof chain
- ReplayKey: deterministic replay identifier
- ExecutionProofRecorder: records and manages execution proofs
- ProofComparison / ProofComparisonOutcome: compares two proof chains
- ExecutionProofReport: summary report of proof verification
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "execution_proof")
_emit_applies_guardrail("p0", "execution_proof", "p0_governance")
_emit_reads_policy_state("p0", "execution_proof", "policy_binding")
_emit_snapshots_state("p0", "execution_proof", "state_snapshot")
emit_replay_key("p0", "execution_proof")
emit_determinism_digest("p0", "execution_proof")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class ProofComparisonOutcome(Enum):
    """Result of comparing two execution proofs."""

    MATCH = "match"
    MISMATCH = "mismatch"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class ReplayKey:
    """Deterministic replay identifier for an execution trace."""

    key_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    trace_id: str = ""
    run_id: str = ""
    input_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def create(cls, trace_id: str, run_id: str, input_data: str = "") -> ReplayKey:
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()[:16] if input_data else ""
        return cls(trace_id=trace_id, run_id=run_id, input_hash=input_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "input_hash": self.input_hash,
            "timestamp": self.timestamp,
        }


@dataclass
class ExecutionTrace:
    """Captures a single execution's proof chain."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    run_id: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    replay_key: ReplayKey | None = None
    proof_hash: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    status: str = "pending"

    def record_step(self, step_name: str, step_data: Any = None) -> None:
        self.steps.append({
            "step_name": step_name,
            "step_data": step_data,
            "timestamp": time.time(),
        })

    def finalize(self) -> str:
        self.end_time = time.time()
        self.status = "complete"
        content = str([(s["step_name"], s.get("step_data")) for s in self.steps])
        self.proof_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        return self.proof_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "steps": self.steps,
            "replay_key": self.replay_key.to_dict() if self.replay_key else None,
            "proof_hash": self.proof_hash,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
        }


@dataclass
class ProofComparison:
    """Compares two execution proof chains."""

    trace_a: ExecutionTrace
    trace_b: ExecutionTrace
    outcome: ProofComparisonOutcome = ProofComparisonOutcome.INCONCLUSIVE
    details: str = ""

    def compare(self) -> ProofComparisonOutcome:
        if not self.trace_a.proof_hash or not self.trace_b.proof_hash:
            self.outcome = ProofComparisonOutcome.INCONCLUSIVE
            self.details = "One or both traces not finalized"
        elif self.trace_a.proof_hash == self.trace_b.proof_hash:
            self.outcome = ProofComparisonOutcome.MATCH
            self.details = "Proof hashes match"
        else:
            matching_steps = sum(
                1
                for a, b in zip(self.trace_a.steps, self.trace_b.steps)
                if a["step_name"] == b["step_name"]
            )
            total_steps = max(len(self.trace_a.steps), len(self.trace_b.steps))
            if total_steps > 0 and matching_steps / total_steps > 0.5:
                self.outcome = ProofComparisonOutcome.PARTIAL
                self.details = f"{matching_steps}/{total_steps} steps match"
            else:
                self.outcome = ProofComparisonOutcome.MISMATCH
                self.details = "Proof hashes differ significantly"
        return self.outcome


@dataclass
class ExecutionProofReport:
    """Summary report of proof verification."""

    total_traces: int = 0
    verified_count: int = 0
    mismatch_count: int = 0
    comparisons: list[ProofComparison] = field(default_factory=list)
    summary: str = ""

    def add_comparison(self, comparison: ProofComparison) -> None:
        self.comparisons.append(comparison)
        self.total_traces = len(self.comparisons)
        if comparison.outcome == ProofComparisonOutcome.MATCH:
            self.verified_count += 1
        elif comparison.outcome == ProofComparisonOutcome.MISMATCH:
            self.mismatch_count += 1

    def generate_summary(self) -> str:
        self.summary = (
            f"Proof Report: {self.total_traces} comparisons, "
            f"{self.verified_count} verified, {self.mismatch_count} mismatches"
        )
        return self.summary


class ExecutionProofRecorder:
    """Records and manages execution proofs."""

    def __init__(self) -> None:
        self._traces: dict[str, ExecutionTrace] = {}
        self._reports: list[ExecutionProofReport] = []

    def start_trace(self, run_id: str = "", input_data: str = "") -> ExecutionTrace:
        trace = ExecutionTrace(run_id=run_id)
        trace.replay_key = ReplayKey.create(
            trace_id=trace.trace_id, run_id=run_id, input_data=input_data,
        )
        self._traces[trace.trace_id] = trace
        return trace

    def finalize_trace(self, trace_id: str) -> str:
        trace = self._traces.get(trace_id)
        if trace is None:
            raise KeyError(f"Trace {trace_id} not found")
        return trace.finalize()

    def compare_traces(self, trace_id_a: str, trace_id_b: str) -> ProofComparison:
        trace_a = self._traces.get(trace_id_a)
        trace_b = self._traces.get(trace_id_b)
        if trace_a is None or trace_b is None:
            raise KeyError("One or both traces not found")
        comparison = ProofComparison(trace_a=trace_a, trace_b=trace_b)
        comparison.compare()
        return comparison

    def get_trace(self, trace_id: str) -> ExecutionTrace | None:
        return self._traces.get(trace_id)

    def get_all_traces(self) -> list[ExecutionTrace]:
        return list(self._traces.values())


__all__ = [
    "ExecutionProofRecorder",
    "ExecutionProofReport",
    "ExecutionTrace",
    "ProofComparison",
    "ProofComparisonOutcome",
    "ReplayKey",
]
