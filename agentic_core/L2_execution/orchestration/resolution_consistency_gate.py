"""Resolution Consistency Gate — E2 ↔ E4 validator/heal digest equality.

Maps to: docs/reference/04_L2_Execute/04.5a_L2_Resolution_Context_Invariant.md

This module is the single chokepoint enforcing INV-RC-1..INV-RC-8 from 04.5a.
It is pure: no I/O, no logging side effects beyond the explicit OTEL emission
(which goes through `l2_resolution_spans.emit_compare_span`), no HITL,
no durable write.

Public surface:
  - `ResolutionMismatchError` — raised on any mismatch
  - `assert_validator_heal_resolution_match` — the gate function
  - `MISMATCH_DECISIVE_RULE_ID` — the constant `VALIDATOR_AGENT_RESOLUTION_MISMATCH`

Behavior:
  1. Reject if either context has `is_default_agent_fallback()` true (INV-RC-8).
  2. Reject if either digest is empty / not a 64-char hex string.
  3. Reject if validator_digest != heal_digest (bit-for-bit, no substring).
  4. On reject, raise `ResolutionMismatchError` carrying:
     - decisive_rule_id = "VALIDATOR_AGENT_RESOLUTION_MISMATCH"
     - validator_resolution_digest, heal_resolution_digest
     - first_mismatched_field (computed from contexts)
     - trace_id, request_id, run_id, route_id, step_id, agent_id, validator_id
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from agentic_core.L2_execution.types.l2_resolution_context import (
    L2ResolutionContext,
    is_default_agent_fallback,
)

MISMATCH_DECISIVE_RULE_ID: str = "VALIDATOR_AGENT_RESOLUTION_MISMATCH"

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ResolutionMismatchEvidence:
    """Structured evidence carried by `ResolutionMismatchError`.

    Every field is what 04.5a Phase 5 requires the sealed REJECTED dispatch
    to include.
    """

    decisive_rule_id: str
    validator_resolution_digest: str
    heal_resolution_digest: str
    first_mismatched_field: str
    trace_id: str
    request_id: str
    run_id: str
    route_id: str
    step_id: str | None
    agent_id_validator: str
    agent_id_heal: str
    validator_id_validator: str
    validator_id_heal: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "decisive_rule_id": self.decisive_rule_id,
            "validator_resolution_digest": self.validator_resolution_digest,
            "heal_resolution_digest": self.heal_resolution_digest,
            "first_mismatched_field": self.first_mismatched_field,
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "route_id": self.route_id,
            "step_id": self.step_id,
            "agent_id_validator": self.agent_id_validator,
            "agent_id_heal": self.agent_id_heal,
            "validator_id_validator": self.validator_id_validator,
            "validator_id_heal": self.validator_id_heal,
            "reason": self.reason,
        }


class ResolutionMismatchError(Exception):
    """Raised by the consistency gate on any RC-* invariant violation.

    The exception is the failure carrier; upstream pipelines catch it and
    seal a REJECTED dispatch with terminal_class =
    `TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH`.
    """

    def __init__(self, evidence: ResolutionMismatchEvidence) -> None:
        super().__init__(
            f"{evidence.decisive_rule_id}: {evidence.reason} "
            f"first_mismatched_field={evidence.first_mismatched_field!r} "
            f"trace_id={evidence.trace_id!r}"
        )
        self.evidence = evidence


def _looks_like_digest(value: str) -> bool:
    return isinstance(value, str) and bool(_HEX64_RE.match(value))


def assert_validator_heal_resolution_match(
    *,
    validator_context: L2ResolutionContext,
    heal_context: L2ResolutionContext,
    validator_digest: str,
    heal_digest: str,
) -> None:
    """Raise `ResolutionMismatchError` unless every RC-* invariant holds.

    All four arguments are required and keyword-only so callers cannot
    accidentally swap validator and heal sides.

    Steps (in order — first failing step wins):
      1. INV-RC-8: neither side may be a default-agent fallback.
      2. Digest format: both digests must be 64-char lowercase hex.
      3. Digest equality (INV-RC-1): bit-for-bit.
      4. Field-level cross-check: even if digests happen to match by
         coincidence, the contexts themselves must agree
         (defense-in-depth against a buggy `compute_resolution_digest`).
    """
    # 1. Default-agent fallback (INV-RC-8)
    if is_default_agent_fallback(validator_context):
        raise ResolutionMismatchError(
            _build_evidence(
                validator_context,
                heal_context,
                validator_digest,
                heal_digest,
                first_mismatched_field="agent_id",
                reason="validator-side agent_id is a default/fallback sentinel",
            )
        )
    if is_default_agent_fallback(heal_context):
        raise ResolutionMismatchError(
            _build_evidence(
                validator_context,
                heal_context,
                validator_digest,
                heal_digest,
                first_mismatched_field="agent_id",
                reason="heal-side agent_id is a default/fallback sentinel",
            )
        )

    # 2. Digest format
    if not _looks_like_digest(validator_digest):
        raise ResolutionMismatchError(
            _build_evidence(
                validator_context,
                heal_context,
                validator_digest,
                heal_digest,
                first_mismatched_field="validator_resolution_digest",
                reason="validator_resolution_digest is not a 64-char hex SHA-256",
            )
        )
    if not _looks_like_digest(heal_digest):
        raise ResolutionMismatchError(
            _build_evidence(
                validator_context,
                heal_context,
                validator_digest,
                heal_digest,
                first_mismatched_field="heal_resolution_digest",
                reason="heal_resolution_digest is not a 64-char hex SHA-256",
            )
        )

    # 3. Digest equality (INV-RC-1, bit-for-bit)
    if validator_digest != heal_digest:
        # Identify first mismatched field for the sealed evidence.
        first = validator_context.first_mismatched_field(heal_context)
        if first == "":
            # Digests differ but contexts agree byte-for-byte ⇒ caller
            # passed inconsistent (digest, context) pair. Surface that.
            first = "<digest_context_inconsistency>"
        raise ResolutionMismatchError(
            _build_evidence(
                validator_context,
                heal_context,
                validator_digest,
                heal_digest,
                first_mismatched_field=first,
                reason="validator_resolution_digest != heal_resolution_digest",
            )
        )

    # 4. Defense-in-depth: contexts must also agree field-wise.
    first = validator_context.first_mismatched_field(heal_context)
    if first != "":
        raise ResolutionMismatchError(
            _build_evidence(
                validator_context,
                heal_context,
                validator_digest,
                heal_digest,
                first_mismatched_field=first,
                reason=(
                    "digests matched but contexts diverge field-wise — "
                    "indicates compute_resolution_digest collision or caller bug"
                ),
            )
        )

    # All checks passed. No return value — absence of exception is success.


def _build_evidence(
    validator_context: L2ResolutionContext,
    heal_context: L2ResolutionContext,
    validator_digest: str,
    heal_digest: str,
    *,
    first_mismatched_field: str,
    reason: str,
) -> ResolutionMismatchEvidence:
    return ResolutionMismatchEvidence(
        decisive_rule_id=MISMATCH_DECISIVE_RULE_ID,
        validator_resolution_digest=validator_digest,
        heal_resolution_digest=heal_digest,
        first_mismatched_field=first_mismatched_field,
        trace_id=validator_context.trace_id,
        request_id=validator_context.request_id,
        run_id=validator_context.run_id,
        route_id=validator_context.route_id,
        step_id=validator_context.step_id,
        agent_id_validator=validator_context.agent_id,
        agent_id_heal=heal_context.agent_id,
        validator_id_validator=validator_context.validator_id,
        validator_id_heal=heal_context.validator_id,
        reason=reason,
    )


__all__ = [
    "MISMATCH_DECISIVE_RULE_ID",
    "ResolutionMismatchEvidence",
    "ResolutionMismatchError",
    "assert_validator_heal_resolution_match",
]
