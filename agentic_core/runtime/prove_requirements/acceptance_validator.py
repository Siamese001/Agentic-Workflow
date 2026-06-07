"""Acceptance Validator — pure-function legality engine for hardened matrix.

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``

Implements RTC-REQ-004, 005, 111, 127:
  - ACCEPTED iff ``actual_proof_depth >= required_proof_depth`` (rule §1)
  - ``E5_COMPOSITION_PROOF`` cannot satisfy E6/E7/E8/E9 (rule §2 / RTC-REQ-127)
  - DOC_REFERENCE_ONLY rows can NEVER claim runtime (RTC-REQ-005)
  - ``runtime_claim_allowed`` must be honored (RTC-REQ-005)
  - PARTIAL/BLOCKED status MUST carry a non-empty ``acceptance_caveat``
    or ``blocking_gap`` respectively (RTC-REQ-002 schema rule)

Anti-cheat
----------

This module produces a verdict; it does not write artifacts and it does not
read evidence on its own. Verifier scripts call ``validate_acceptance(row)``
with the ``actual_proof_depth`` they observed elsewhere; the validator
applies the legality rules and returns ``AcceptanceVerdict``. This separation
is what makes "ACCEPTED row with weaker proof than required" detectable
across the whole CSV in a single pass.

Public API
----------

- ``AcceptanceVerdict`` — dataclass returned for every row
- ``ALLOWED_FINAL_STATUSES`` — frozenset of valid final_acceptance_status
- ``validate_acceptance(...)`` — pure function, no I/O
- ``apply_to_matrix(...)`` — vectorised over loaded rows, returns
  list of verdicts ready to feed into reports
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, Iterable

from .proof_depth_ladder import (
    COMPOSITION_NON_PROMOTABLE_TARGETS,
    can_satisfy,
    is_valid_depth,
)
from .matrix_loader import (
    ALLOWED_CLAIM_TYPES,
    RUNTIME_CLAIM_TYPES,
    RUNTIME_FORBIDDEN_CLAIM_TYPES,
)

ALLOWED_FINAL_STATUSES: Final[frozenset[str]] = frozenset({
    "ACCEPTED",
    "ACCEPTED_WITH_CAVEAT",
    "PARTIAL",
    "BLOCKED",
    "PENDING",
})


@dataclass(frozen=True)
class AcceptanceVerdict:
    """Outcome of running ``validate_acceptance`` on one row."""

    req_id: str
    claim_type: str
    required_proof_depth: str
    actual_proof_depth: str
    proof_depth_status: str
    final_acceptance_status: str
    runtime_claim_allowed: bool
    acceptance_caveat: str
    blocking_gap: str
    legal: bool
    expected_fail_reason: str
    actual_fail_reason: str
    rule_violations: tuple[str, ...] = field(default_factory=tuple)

    def to_row(self) -> dict[str, Any]:
        return {
            "req_id": self.req_id,
            "claim_type": self.claim_type,
            "required_proof_depth": self.required_proof_depth,
            "actual_proof_depth": self.actual_proof_depth,
            "proof_depth_status": self.proof_depth_status,
            "final_acceptance_status": self.final_acceptance_status,
            "runtime_claim_allowed": self.runtime_claim_allowed,
            "acceptance_caveat": self.acceptance_caveat,
            "blocking_gap": self.blocking_gap,
            "legal": self.legal,
            "expected_fail_reason": self.expected_fail_reason,
            "actual_fail_reason": self.actual_fail_reason,
            "rule_violations": list(self.rule_violations),
        }


def _is_truthy(s: str | None) -> bool:
    if s is None:
        return False
    return str(s).strip().lower() == "true"


def validate_acceptance(
    row: dict[str, Any],
    *,
    actual_proof_depth: str | None = None,
    proof_depth_status: str | None = None,
    final_acceptance_status: str | None = None,
    runtime_claim_allowed: bool | None = None,
    acceptance_caveat: str | None = None,
    blocking_gap: str | None = None,
) -> AcceptanceVerdict:
    """Apply legality rules to one row.

    Inputs default to the row's own metadata-encoded values when caller
    omits them. This lets the validator be driven both by metadata-only
    schema checks (W0) and by evidence-driven verifiers (W1+) that supply
    a freshly observed ``actual_proof_depth``.
    """
    rid = (row.get("req_id") or "").strip()
    claim_type = (row.get("claim_type") or "").strip()
    required = (row.get("required_proof_depth") or "").strip()

    # Defaulting: when the caller doesn't supply an actual depth, treat the
    # row as proven-at-required-tier IF the row carries no explicit status
    # contradicting that. For W0, where no evidence exists yet, the default
    # is E0_REQUIREMENT_TEXT — fail-closed.
    actual = (actual_proof_depth or "E0_REQUIREMENT_TEXT").strip()
    final_status = (final_acceptance_status or "PENDING").strip()
    if runtime_claim_allowed is None:
        # Resolve from the row's runtime_claim_allowed_rule when it's
        # boolean-shaped, else default conservatively to False.
        rule_text = (row.get("runtime_claim_allowed_rule") or "").strip().lower()
        runtime_claim_allowed = rule_text in ("true", "yes")
    caveat = (acceptance_caveat or "").strip()
    gap = (blocking_gap or "").strip()

    violations: list[str] = []
    expected_fail = ""
    actual_fail = ""

    # ── Rule §1 / RTC-REQ-004: actual >= required AND composition non-promotion
    if not is_valid_depth(required):
        violations.append("INVALID_REQUIRED_PROOF_DEPTH")
        expected_fail = "REQUIRED_PROOF_DEPTH_INVALID"
        actual_fail = f"required_proof_depth='{required}' is not in canonical ladder"
    if not is_valid_depth(actual):
        violations.append("INVALID_ACTUAL_PROOF_DEPTH")
        if not expected_fail:
            expected_fail = "ACTUAL_PROOF_DEPTH_INVALID"
            actual_fail = f"actual_proof_depth='{actual}' is not in canonical ladder"

    actual_satisfies_required = can_satisfy(actual, required)

    # ── RTC-REQ-127: composition proof cannot promote final acceptance
    if (
        actual == "E5_COMPOSITION_PROOF"
        and required in COMPOSITION_NON_PROMOTABLE_TARGETS
    ):
        violations.append("COMPOSITION_PROOF_CANNOT_PROMOTE")
        if not expected_fail:
            expected_fail = "COMPOSITION_PROOF_CANNOT_PROMOTE_TO_RUNTIME_TIER"
            actual_fail = (
                f"req_id={rid} required={required} but actual=E5_COMPOSITION_PROOF "
                "(rule §2 forbids this promotion regardless of metadata)"
            )

    # ── RTC-REQ-003: claim_type must be in enum
    if claim_type and claim_type not in ALLOWED_CLAIM_TYPES:
        violations.append("INVALID_CLAIM_TYPE")
        if not expected_fail:
            expected_fail = "CLAIM_TYPE_OUT_OF_ENUM"
            actual_fail = f"req_id={rid} claim_type='{claim_type}' not in allowed enum"

    # ── RTC-REQ-005: DOC_REFERENCE_ONLY cannot carry runtime tiers nor
    #    runtime_claim_allowed=true.
    if claim_type in RUNTIME_FORBIDDEN_CLAIM_TYPES:
        if runtime_claim_allowed:
            violations.append("DOC_REFERENCE_ONLY_CANNOT_CLAIM_RUNTIME")
            if not expected_fail:
                expected_fail = "DOC_REFERENCE_ONLY_RUNTIME_FORBIDDEN"
                actual_fail = f"req_id={rid} claim_type=DOC_REFERENCE_ONLY but runtime_claim_allowed=True"

    # ── RTC-REQ-002: PARTIAL and BLOCKED MUST carry caveat / gap text
    if final_status == "PARTIAL" and not caveat:
        violations.append("PARTIAL_WITHOUT_CAVEAT")
        if not expected_fail:
            expected_fail = "PARTIAL_REQUIRES_ACCEPTANCE_CAVEAT"
            actual_fail = f"req_id={rid} final_status=PARTIAL but acceptance_caveat is empty"
    if final_status == "BLOCKED" and not gap:
        violations.append("BLOCKED_WITHOUT_BLOCKING_GAP")
        if not expected_fail:
            expected_fail = "BLOCKED_REQUIRES_BLOCKING_GAP"
            actual_fail = f"req_id={rid} final_status=BLOCKED but blocking_gap is empty"

    # ── Rule §1 / RTC-REQ-004 main check: ACCEPTED requires actual >= required
    if final_status == "ACCEPTED" and not actual_satisfies_required:
        violations.append("ACCEPTED_WITH_WEAK_PROOF")
        if not expected_fail:
            expected_fail = "ACCEPTED_REQUIRES_ACTUAL_GE_REQUIRED"
            actual_fail = (
                f"req_id={rid} final_status=ACCEPTED but actual={actual} does not "
                f"satisfy required={required}"
            )
    if final_status == "ACCEPTED_WITH_CAVEAT" and not caveat:
        violations.append("ACCEPTED_WITH_CAVEAT_MISSING_CAVEAT_TEXT")
        if not expected_fail:
            expected_fail = "ACCEPTED_WITH_CAVEAT_REQUIRES_CAVEAT_TEXT"
            actual_fail = f"req_id={rid} final_status=ACCEPTED_WITH_CAVEAT but acceptance_caveat empty"

    if final_status not in ALLOWED_FINAL_STATUSES:
        violations.append("INVALID_FINAL_ACCEPTANCE_STATUS")
        if not expected_fail:
            expected_fail = "FINAL_ACCEPTANCE_STATUS_OUT_OF_ENUM"
            actual_fail = f"req_id={rid} final_status='{final_status}' not in allowed enum"

    # Compute proof_depth_status if not supplied
    pd_status = (proof_depth_status or "").strip()
    if not pd_status:
        if not is_valid_depth(actual) or not is_valid_depth(required):
            pd_status = "INVALID"
        elif actual_satisfies_required:
            pd_status = "PASS"
        elif actual == "E5_COMPOSITION_PROOF" and required in COMPOSITION_NON_PROMOTABLE_TARGETS:
            pd_status = "BLOCKED_BY_COMPOSITION_NON_PROMOTION"
        else:
            pd_status = "WEAKER_THAN_REQUIRED"

    legal = len(violations) == 0

    return AcceptanceVerdict(
        req_id=rid,
        claim_type=claim_type,
        required_proof_depth=required,
        actual_proof_depth=actual,
        proof_depth_status=pd_status,
        final_acceptance_status=final_status,
        runtime_claim_allowed=bool(runtime_claim_allowed),
        acceptance_caveat=caveat,
        blocking_gap=gap,
        legal=legal,
        expected_fail_reason=expected_fail,
        actual_fail_reason=actual_fail,
        rule_violations=tuple(violations),
    )


def apply_to_matrix(
    rows: Iterable[dict[str, Any]],
    *,
    actual_proof_depth_overrides: dict[str, str] | None = None,
    final_acceptance_status_overrides: dict[str, str] | None = None,
    acceptance_caveat_overrides: dict[str, str] | None = None,
    blocking_gap_overrides: dict[str, str] | None = None,
) -> list[AcceptanceVerdict]:
    """Run ``validate_acceptance`` over every row, with optional per-req overrides.

    W0 baseline: no overrides supplied. Every row defaults to
    ``actual=E0_REQUIREMENT_TEXT`` and ``final_status=PENDING``, which is
    legal (PENDING never triggers acceptance violations). Future waves
    populate overrides from real evidence.
    """
    overrides_actual = actual_proof_depth_overrides or {}
    overrides_final = final_acceptance_status_overrides or {}
    overrides_caveat = acceptance_caveat_overrides or {}
    overrides_gap = blocking_gap_overrides or {}

    out: list[AcceptanceVerdict] = []
    for row in rows:
        rid = (row.get("req_id") or "").strip()
        out.append(validate_acceptance(
            row,
            actual_proof_depth=overrides_actual.get(rid),
            final_acceptance_status=overrides_final.get(rid),
            acceptance_caveat=overrides_caveat.get(rid),
            blocking_gap=overrides_gap.get(rid),
        ))
    return out


__all__ = [
    "AcceptanceVerdict",
    "ALLOWED_FINAL_STATUSES",
    "validate_acceptance",
    "apply_to_matrix",
]
