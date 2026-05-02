"""UWG BlockedCommitReceipt — typed proof that UWG rejected a commit.

Emitted by ``DurableWriteGateway`` (or any UWG-stamped rejection path)
when a ``CommitRequest`` is denied. The receipt makes the rejection a
first-class artifact rather than a log line. It is the L4-side analog
of the bypass receipts at L3/C0/PA.

Failure modes captured:
    - WRONG_SOURCE          — CommitRequest source is not "Exit"
    - SCHEMA_INVALID        — request schema validation failed
    - POLICY_VIOLATION      — durable_write_consistency_gate denied
    - QUOTA_EXCEEDED        — per-write quota gate fired
    - REPLAY_DETECTED       — replay-key collision against ledger
    - CAPABILITY_INVALID    — capability token expired or unsigned
    - WRITE_CLASS_DENIED    — write_class not approved for this caller
    - CONFLICT              — optimistic concurrency conflict
    - INTERNAL_ERROR        — internal UWG fault (fail-closed)

The receipt does NOT imply the commit succeeded. A successful commit is
proven by an ``AtomicCommitReceipt`` (separate contract — outside this
pass).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION = "1.0"

ALLOWED_BLOCK_REASONS: frozenset[str] = frozenset({
    "WRONG_SOURCE",
    "SCHEMA_INVALID",
    "POLICY_VIOLATION",
    "QUOTA_EXCEEDED",
    "REPLAY_DETECTED",
    "CAPABILITY_INVALID",
    "WRITE_CLASS_DENIED",
    "CONFLICT",
    "INTERNAL_ERROR",
})

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "route_contract_id",
    "route_id",
    "commit_request_source",
    "commit_request_ref",
    "block_reason",
    "block_detail_codes",
    "no_durable_write_assertion",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class BlockedCommitReceipt:
    """Typed receipt proving UWG rejected a CommitRequest."""

    run_id: str
    request_id: str
    trace_root: str
    route_contract_id: str
    route_id: str
    commit_request_source: str
    block_reason: str
    block_detail_codes: tuple[str, ...] = ()
    commit_request_ref: str = ""
    state_diff_summary: Mapping[str, Any] = field(default_factory=dict)
    no_durable_write_assertion: bool = True
    schema_version: str = BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root", "route_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"BlockedCommitReceipt.{name} must be non-empty string; got {value!r}"
                )
        if self.block_reason not in ALLOWED_BLOCK_REASONS:
            raise ValueError(
                f"BlockedCommitReceipt.block_reason must be one of "
                f"{sorted(ALLOWED_BLOCK_REASONS)}; got {self.block_reason!r}"
            )
        if not isinstance(self.no_durable_write_assertion, bool):
            raise ValueError(
                "BlockedCommitReceipt.no_durable_write_assertion must be bool"
            )
        if self.no_durable_write_assertion is not True:
            raise ValueError(
                "BlockedCommitReceipt.no_durable_write_assertion must be True; "
                "by definition a blocked commit performed no durable write"
            )
        if self.schema_version != BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION:
            raise ValueError(
                f"BlockedCommitReceipt.schema_version must be "
                f"{BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION!r}; got {self.schema_version!r}"
            )
        if not isinstance(self.block_detail_codes, tuple):
            raise ValueError(
                "BlockedCommitReceipt.block_detail_codes must be a tuple of strings"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_contract_id": self.route_contract_id,
            "route_id": self.route_id,
            "commit_request_source": self.commit_request_source,
            "commit_request_ref": self.commit_request_ref,
            "block_reason": self.block_reason,
            "block_detail_codes": list(self.block_detail_codes),
            "state_diff_summary": dict(self.state_diff_summary),
            "no_durable_write_assertion": self.no_durable_write_assertion,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_blocked_commit_digest(payload: Mapping[str, Any]) -> str:
    stable: dict[str, Any] = {}
    for k in _DIGEST_STABLE_FIELDS:
        value = payload.get(k)
        if isinstance(value, (list, tuple)):
            stable[k] = list(value)
        else:
            stable[k] = value
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_blocked_commit_receipt(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    route_contract_id: str,
    route_id: str,
    commit_request_source: str,
    block_reason: str,
    block_detail_codes: tuple[str, ...] = (),
    commit_request_ref: str = "",
    state_diff_summary: Mapping[str, Any] | None = None,
) -> BlockedCommitReceipt:
    digest_input: dict[str, Any] = {
        "schema_version": BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_contract_id": route_contract_id,
        "route_id": route_id,
        "commit_request_source": commit_request_source,
        "commit_request_ref": commit_request_ref,
        "block_reason": block_reason,
        "block_detail_codes": list(block_detail_codes),
        "no_durable_write_assertion": True,
    }
    digest = compute_blocked_commit_digest(digest_input)
    return BlockedCommitReceipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=route_id,
        commit_request_source=commit_request_source,
        block_reason=block_reason,
        block_detail_codes=tuple(block_detail_codes),
        commit_request_ref=commit_request_ref,
        state_diff_summary=dict(state_diff_summary or {}),
        no_durable_write_assertion=True,
        deterministic_digest=digest,
    )


__all__ = [
    "ALLOWED_BLOCK_REASONS",
    "BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION",
    "BlockedCommitReceipt",
    "build_blocked_commit_receipt",
    "compute_blocked_commit_digest",
]
