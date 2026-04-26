"""L4UWGProofPacket — acceptance proof bundle (00.8 §L4UWGProofPacket).

Per ``docs/reference/00_L4_State_and_UWG/00.8_*``, the proof packet is the
durable artifact a release submits to assert that the L4/UWG pack is
operational. It must be backed by ACTUAL test output, ACTUAL spans, and
ACTUAL receipts — never asserted dry.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Tuple

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest


def _empty_tuple() -> Tuple[Any, ...]:
    return ()


@dataclass(frozen=True)
class L4UWGProofPacket:
    """Acceptance proof packet for the L4/UWG pack (00.8 §PHASE 4)."""

    proof_packet_id: str
    trace_root: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    acceptance_summary: str
    schema_version: str = "L4-UWG-1.0.0"
    deterministic_digest: str = ""
    run_id: str = ""
    test_run_id: str = ""
    test_command_results: Tuple[str, ...] = field(default_factory=_empty_tuple)
    otel_trace_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    direct_write_block_receipts: Tuple[str, ...] = field(default_factory=_empty_tuple)
    commit_request_examples: Tuple[str, ...] = field(default_factory=_empty_tuple)
    uwg_commit_receipts: Tuple[str, ...] = field(default_factory=_empty_tuple)
    blocked_commit_receipts: Tuple[str, ...] = field(default_factory=_empty_tuple)
    rollback_receipts: Tuple[str, ...] = field(default_factory=_empty_tuple)
    replay_reconstruction_receipts: Tuple[str, ...] = field(default_factory=_empty_tuple)
    audit_ledger_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    read_scope_test_refs: Tuple[str, ...] = field(default_factory=_empty_tuple)
    known_gaps: Tuple[str, ...] = field(default_factory=_empty_tuple)


def stamp_proof_digest(packet: L4UWGProofPacket) -> L4UWGProofPacket:
    """Return ``packet`` with ``deterministic_digest`` filled in."""
    if packet.deterministic_digest:
        return packet
    payload = {
        "proof_packet_id": packet.proof_packet_id,
        "trace_root": packet.trace_root,
        "policy_hash": packet.policy_hash,
        "blueprint_hash": packet.blueprint_hash,
        "replay_key": packet.replay_key,
        "acceptance_summary": packet.acceptance_summary,
        "test_command_results": list(packet.test_command_results),
        "otel_trace_refs": list(packet.otel_trace_refs),
        "direct_write_block_receipts": list(packet.direct_write_block_receipts),
        "commit_request_examples": list(packet.commit_request_examples),
        "uwg_commit_receipts": list(packet.uwg_commit_receipts),
        "blocked_commit_receipts": list(packet.blocked_commit_receipts),
        "rollback_receipts": list(packet.rollback_receipts),
        "replay_reconstruction_receipts": list(packet.replay_reconstruction_receipts),
        "audit_ledger_refs": list(packet.audit_ledger_refs),
        "read_scope_test_refs": list(packet.read_scope_test_refs),
        "known_gaps": list(packet.known_gaps),
        "schema_version": packet.schema_version,
    }
    digest = compute_deterministic_digest(payload)
    return replace(packet, deterministic_digest=digest)


__all__ = ["L4UWGProofPacket", "stamp_proof_digest"]
