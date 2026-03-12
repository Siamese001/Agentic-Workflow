"""G14 (gap): Execution trace / proof runtime.

Models the proof artifact layer on top of execution:
  ExecutionTrace → replay_key → determinism digests
  → singleton digest emission → proof comparison across runs.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProofComparisonOutcome(str, Enum):
    MATCH = "match"
    DIGEST_MISMATCH = "digest_mismatch"
    EVENT_COUNT_MISMATCH = "event_count_mismatch"
    REPLAY_KEY_MISMATCH = "replay_key_mismatch"


@dataclass
class ExecutionTrace:
    """Signed runtime trace of one agent execution slot."""

    trace_id: str = field(default_factory=lambda: f"tr-{uuid.uuid4().hex[:12]}")
    run_id: str = ""
    agent_id: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    ended_at: float = 0.0
    event_count: int = 0
    trace_hash: str = ""
    signature: str = ""
    sealed: bool = False

    def record_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self.events.append(
            {
                "seq": len(self.events),
                "event_type": event_type,
                "ts": time.time(),
                "payload": payload or {},
            }
        )
        self.event_count = len(self.events)

    def seal(self) -> str:
        """Finalize and hash the trace; returns the trace_hash."""
        self.ended_at = time.time()
        payload = f"{self.run_id}:{self.agent_id}:{self.event_count}:{self.started_at}"
        for ev in self.events:
            payload += f":{ev['event_type']}"
        self.trace_hash = hashlib.sha256(payload.encode()).hexdigest()
        self.sealed = True
        return self.trace_hash

    def sign(self, signing_key: str = "") -> str:
        if not self.sealed:
            self.seal()
        raw = f"{self.trace_hash}:{signing_key}"
        self.signature = hashlib.sha256(raw.encode()).hexdigest()
        return self.signature

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "event_count": self.event_count,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "trace_hash": self.trace_hash,
            "signature": self.signature,
            "sealed": self.sealed,
        }


@dataclass
class ReplayKey:
    """Opaque key that allows exact replay of an execution slot."""

    key_id: str = field(default_factory=lambda: f"rk-{uuid.uuid4().hex[:12]}")
    run_id: str = ""
    agent_id: str = ""
    trace_id: str = ""
    rng_seed: int = 0
    clock_start_ns: int = 0
    determinism_digest_hash: str = ""
    emitted_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "trace_id": self.trace_id,
            "rng_seed": self.rng_seed,
            "clock_start_ns": self.clock_start_ns,
            "determinism_digest_hash": self.determinism_digest_hash,
            "emitted_at": self.emitted_at,
        }


@dataclass
class ProofComparison:
    """Result of comparing two ExecutionTrace proofs."""

    comparison_id: str = field(default_factory=lambda: f"cmp-{uuid.uuid4().hex[:8]}")
    trace_a_id: str = ""
    trace_b_id: str = ""
    outcome: ProofComparisonOutcome = ProofComparisonOutcome.MATCH
    mismatched_fields: list[str] = field(default_factory=list)
    compared_at: float = field(default_factory=time.time)

    @property
    def matches(self) -> bool:
        return self.outcome == ProofComparisonOutcome.MATCH

    def to_dict(self) -> dict[str, Any]:
        return {
            "comparison_id": self.comparison_id,
            "trace_a_id": self.trace_a_id,
            "trace_b_id": self.trace_b_id,
            "outcome": self.outcome.value,
            "matches": self.matches,
            "mismatched_fields": self.mismatched_fields,
            "compared_at": self.compared_at,
        }


@dataclass
class ExecutionProofReport:
    """Aggregated proof artifacts for one session."""

    agent_id: str = ""
    run_id: str = ""
    traces: list[ExecutionTrace] = field(default_factory=list)
    replay_keys: list[ReplayKey] = field(default_factory=list)
    comparisons: list[ProofComparison] = field(default_factory=list)

    @property
    def sealed_trace_count(self) -> int:
        return sum(1 for t in self.traces if t.sealed)

    @property
    def match_count(self) -> int:
        return sum(1 for c in self.comparisons if c.matches)

    @property
    def mismatch_count(self) -> int:
        return sum(1 for c in self.comparisons if not c.matches)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "trace_count": len(self.traces),
            "sealed_trace_count": self.sealed_trace_count,
            "replay_key_count": len(self.replay_keys),
            "comparison_count": len(self.comparisons),
            "match_count": self.match_count,
            "mismatch_count": self.mismatch_count,
        }

    @property
    def summary(self) -> str:
        return (
            f"ExecutionProof [{self.agent_id}] — "
            f"{self.sealed_trace_count} sealed traces, "
            f"{len(self.replay_keys)} replay keys, "
            f"{self.match_count}/{len(self.comparisons)} comparisons matched"
        )


class ExecutionProofRecorder:
    """Runtime recorder for execution traces, replay keys, and proof comparisons."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = ExecutionProofReport(agent_id=agent_id, run_id=run_id)
        self._active_trace: ExecutionTrace | None = None

    def start_trace(self) -> ExecutionTrace:
        trace = ExecutionTrace(run_id=self.report.run_id, agent_id=self.report.agent_id)
        self.report.traces.append(trace)
        self._active_trace = trace
        return trace

    def record_execution_trace(
        self, event_type: str, payload: dict[str, Any] | None = None
    ) -> ExecutionTrace:
        if self._active_trace is None:
            self.start_trace()
        assert self._active_trace is not None
        self._active_trace.record_event(event_type, payload)
        return self._active_trace

    def sign_execution_trace(self, signing_key: str = "") -> str:
        if self._active_trace is None:
            raise RuntimeError("No active trace to sign")
        return self._active_trace.sign(signing_key)

    def emit_replay_key(
        self,
        rng_seed: int = 0,
        clock_start_ns: int = 0,
        determinism_digest_hash: str = "",
    ) -> ReplayKey:
        trace_id = self._active_trace.trace_id if self._active_trace else ""
        key = ReplayKey(
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
            trace_id=trace_id,
            rng_seed=rng_seed,
            clock_start_ns=clock_start_ns,
            determinism_digest_hash=determinism_digest_hash,
        )
        self.report.replay_keys.append(key)
        return key

    def compare_proof(self, trace_a: ExecutionTrace, trace_b: ExecutionTrace) -> ProofComparison:
        cmp = ProofComparison(trace_a_id=trace_a.trace_id, trace_b_id=trace_b.trace_id)
        mismatches: list[str] = []
        if trace_a.trace_hash != trace_b.trace_hash:
            mismatches.append("trace_hash")
        if trace_a.event_count != trace_b.event_count:
            mismatches.append("event_count")
        if trace_a.signature != trace_b.signature:
            mismatches.append("signature")
        if mismatches:
            cmp.mismatched_fields = mismatches
            cmp.outcome = (
                ProofComparisonOutcome.DIGEST_MISMATCH
                if "trace_hash" in mismatches
                else ProofComparisonOutcome.EVENT_COUNT_MISMATCH
            )
        self.report.comparisons.append(cmp)
        return cmp

    def emit_singleton_digest(self) -> str:
        """Emit a singleton digest covering all sealed traces."""
        hashes = [t.trace_hash for t in self.report.traces if t.sealed]
        combined = ":".join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()
