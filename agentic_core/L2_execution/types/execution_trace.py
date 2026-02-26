"""ExecutionTrace — spec contract [4] REVISED.

Fields: trace_id, plan_hash, actor, target, diff, policy_hash,
        timestamp(frozen), prev_hash(chain), replay_key, transcript_hash.

replay_key = SHA256(trace_id + plan_hash + transcript_hash)  — deterministic, no time entropy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _compute_replay_key(trace_id: str, plan_hash: str, transcript_hash: str) -> str:
    raw = (trace_id + plan_hash + transcript_hash).encode("ascii", errors="replace")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ExecutionTrace:
    trace_id: str
    instruction_packet_id: str
    governed_payload_hash: str  # GovernedPayload.routing_hash
    sandbox_envelope_ids: tuple[str, ...]
    llm_response_hash: str
    validation_decision: str  # PASS | FAIL | ESCALATE
    timing_ms: int
    hash_chain_root: str  # HashChainAuditLog.seal() root
    policy_hash: str = ""  # L0 policy hash from InstructionPacket
    prev_hash: str = ""  # Content hash of previous trace (chain)
    transcript_hash: str = ""  # SHA256 of PTC ToolTranscript bytes
    agent_id: str = ""
    error: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    replay_key: str = field(init=False, default="")

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id required")
        if self.validation_decision not in ("PASS", "FAIL", "ESCALATE"):
            raise ValueError(
                f"validation_decision must be PASS|FAIL|ESCALATE, got {self.validation_decision!r}"
            )
        # Compute replay_key deterministically — no timestamp, no random
        rk = _compute_replay_key(self.trace_id, self.policy_hash, self.transcript_hash)
        object.__setattr__(self, "replay_key", rk)

    def canonical_bytes(self) -> bytes:
        obj = {
            "agent_id": self.agent_id,
            "governed_payload_hash": self.governed_payload_hash,
            "hash_chain_root": self.hash_chain_root,
            "instruction_packet_id": self.instruction_packet_id,
            "llm_response_hash": self.llm_response_hash,
            "policy_hash": self.policy_hash,
            "prev_hash": self.prev_hash,
            "replay_key": self.replay_key,
            "sandbox_envelope_ids": list(self.sandbox_envelope_ids),
            "timing_ms": self.timing_ms,
            "trace_id": self.trace_id,
            "transcript_hash": self.transcript_hash,
            "validation_decision": self.validation_decision,
        }
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class ExecutionTraceBuilder:
    """Mutable builder. Call seal() exactly once."""

    def __init__(self, trace_id: str, instruction_packet_id: str) -> None:
        self.trace_id = trace_id
        self.instruction_packet_id = instruction_packet_id
        self.governed_payload_hash = ""
        self.sandbox_envelope_ids: list[str] = []
        self.llm_response_hash = ""
        self.validation_decision = "PASS"
        self.timing_ms = 0
        self.hash_chain_root = ""
        self.policy_hash = ""
        self.prev_hash = ""
        self.transcript_hash = ""
        self.agent_id = ""
        self.error = ""
        self.extra: dict[str, Any] = {}

    def set_governed_payload(self, routing_hash: str) -> None:
        self.governed_payload_hash = routing_hash

    def add_sandbox_envelope(self, envelope_id: str) -> None:
        self.sandbox_envelope_ids.append(envelope_id)

    def set_llm_response(self, raw_text: str) -> None:
        self.llm_response_hash = hashlib.sha256(raw_text.encode("utf-8", errors="replace")).hexdigest()

    def set_transcript(self, transcript_bytes: bytes) -> None:
        """Set transcript_hash from raw PTC ToolTranscript bytes."""
        self.transcript_hash = hashlib.sha256(transcript_bytes).hexdigest()

    def set_policy_hash(self, policy_hash: str) -> None:
        self.policy_hash = policy_hash

    def set_prev_hash(self, prev_hash: str) -> None:
        self.prev_hash = prev_hash

    def set_validation_decision(self, decision: str) -> None:
        self.validation_decision = decision

    def set_hash_chain_root(self, root: str) -> None:
        self.hash_chain_root = root

    def set_timing(self, ms: int) -> None:
        self.timing_ms = ms

    def seal(self) -> ExecutionTrace:
        return ExecutionTrace(
            trace_id=self.trace_id,
            instruction_packet_id=self.instruction_packet_id,
            governed_payload_hash=self.governed_payload_hash,
            sandbox_envelope_ids=tuple(self.sandbox_envelope_ids),
            llm_response_hash=self.llm_response_hash,
            validation_decision=self.validation_decision,
            timing_ms=self.timing_ms,
            hash_chain_root=self.hash_chain_root,
            policy_hash=self.policy_hash,
            prev_hash=self.prev_hash,
            transcript_hash=self.transcript_hash,
            agent_id=self.agent_id,
            error=self.error,
            extra=self.extra,
        )
