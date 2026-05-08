"""PA.0 Boundary Check — confirms the component is doing assembly only.

W5 c0-policy-rectification-f7b2a9: C0 policy enforcement now uses frozen
RouteContract.c0_policy. L0 is the authority; PA must obey, not recompute.

Implements all seven boundary checks from the spec:

    CHECK 0.1: Has L1 produced a plan?
    CHECK 0.2: Has L0 produced a RouteContract?
    CHECK 0.3: Is this route terminal [RET]?
    CHECK 0.4: Is C0 evidence required per RouteContract.c0_policy?
            - If evidence_contract_required=True → require FinalEvidenceContract
            - If c0_mode is bypass → require C0BypassReceipt
            - Fail closed on missing contracts
    CHECK 0.5: Are durable writes requested?
    CHECK 0.6: Is HITL required before execution?
    CHECK 0.7: Are policy hashes consistent?

The function :func:`boundary_check` consumes lightweight protocol-shaped
inputs (so callers do not need to import L1/L0/C0 dataclasses) and returns a
deterministic :class:`BoundaryCheckResult`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class BoundaryStatus(str, Enum):
    """PA.0 disposition. Either we may proceed to PA.1 or we cannot."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"  # terminal route — PA is not needed at all


class BoundaryFailReason(str, Enum):
    """Canonical reason codes for PA.0 failures.

    Reason codes are stable strings used for telemetry and replay matching.
    """

    MISSING_PLAN_CONTRACT = "missing_plan_contract"
    MISSING_ROUTE_CONTRACT = "missing_route_contract"
    GROUNDING_REQUIRED_NO_EVIDENCE = "grounding_required_no_evidence"
    DURABLE_WRITE_NOT_PERMITTED = "durable_write_not_permitted"
    HITL_REQUIRED_BUT_EXECUTABLE_REQUESTED = "hitl_required_but_executable_requested"
    POLICY_HASH_MISMATCH = "policy_hash_mismatch"


@dataclass(frozen=True)
class BoundaryCheckResult:
    """Result of PA.0 boundary check.

    Attributes
    ----------
    status
        :class:`BoundaryStatus.PASS`  → proceed to PA.1.
        :class:`BoundaryStatus.SKIP`  → terminal [RET] route, skip PA entirely.
        :class:`BoundaryStatus.FAIL`  → block; consult ``fail_reason``.
    fail_reason
        Canonical reason code if status is FAIL. ``None`` otherwise.
    eligible_for_prompt_assembly
        Convenience boolean for callers. True iff status is PASS.
    notes
        Per-check notes for telemetry (one entry per check executed).
    """

    status: BoundaryStatus
    fail_reason: BoundaryFailReason | None = None
    eligible_for_prompt_assembly: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.status is BoundaryStatus.FAIL and self.fail_reason is None:
            raise ValueError("BoundaryCheckResult.FAIL requires a fail_reason")
        if self.status is BoundaryStatus.PASS and not self.eligible_for_prompt_assembly:
            object.__setattr__(self, "eligible_for_prompt_assembly", True)
        if self.status is not BoundaryStatus.PASS and self.eligible_for_prompt_assembly:
            object.__setattr__(self, "eligible_for_prompt_assembly", False)


def _is_present(value: Any) -> bool:
    """Truthy presence check that treats empty strings/dicts/tuples as absent."""
    if value is None:
        return False
    if isinstance(value, (str, bytes, list, tuple, dict, set)):
        return len(value) > 0
    return True


def boundary_check(
    *,
    plan_contract: Mapping[str, Any] | None,
    route_contract: Mapping[str, Any] | None,
    evidence_contract: Mapping[str, Any] | None,
    governance: Mapping[str, Any] | None = None,
    execution_metadata: Mapping[str, Any] | None = None,
) -> BoundaryCheckResult:
    """Run PA.0 boundary checks.

    Parameters
    ----------
    plan_contract
        L1 plan contract dict-like. Must include ``plan_id`` to be considered
        present. ``None``/empty → CHECK 0.1 fails.
    route_contract
        L0 route contract dict-like. Must include ``route_id``. ``None``/empty
        → CHECK 0.2 fails. ``execution_form`` of ``"TERMINAL_SHORTCIRCUIT"``
        triggers SKIP (CHECK 0.3).
    evidence_contract
        C0 evidence contract dict-like (FinalEvidenceContract) OR C0BypassReceipt
        dict-like. CHECK 0.4 inspects RouteContract.c0_policy to determine
        which is required:
        - If ``c0_policy.evidence_contract_required=True``: must be present
          and valid (not BYPASS status)
        - If ``c0_policy.c0_mode`` is a bypass mode: must have
          ``c0_bypass_reason`` field
        A missing contract when required is a FAIL.
    governance
        Optional governance artifact dict. Inspected for
        ``hitl_required`` / ``allowed_tool_posture`` / ``durable_write_allowed``.
    execution_metadata
        Optional execution-meta dict carrying ``policy_hash``. CHECK 0.7
        compares this against route/plan/evidence policy hashes.

    Returns
    -------
    BoundaryCheckResult
    """
    notes: list[str] = []

    # CHECK 0.1 — plan present?
    if not _is_present(plan_contract) or not plan_contract.get("plan_id"):  # type: ignore[union-attr]
        return BoundaryCheckResult(
            status=BoundaryStatus.FAIL,
            fail_reason=BoundaryFailReason.MISSING_PLAN_CONTRACT,
            notes=tuple(notes + ["check_0_1_failed: no L1 plan_id"]),
        )
    notes.append("check_0_1_pass")

    # CHECK 0.2 — route present?
    if not _is_present(route_contract) or not route_contract.get("route_id"):  # type: ignore[union-attr]
        return BoundaryCheckResult(
            status=BoundaryStatus.FAIL,
            fail_reason=BoundaryFailReason.MISSING_ROUTE_CONTRACT,
            notes=tuple(notes + ["check_0_2_failed: no L0 route_id"]),
        )
    notes.append("check_0_2_pass")

    # CHECK 0.3 — terminal route? PA is not needed.
    execution_form = (route_contract or {}).get("execution_form", "")
    if execution_form == "TERMINAL_SHORTCIRCUIT":
        notes.append("check_0_3_skip: terminal [RET] route")
        return BoundaryCheckResult(
            status=BoundaryStatus.SKIP,
            fail_reason=None,
            notes=tuple(notes),
        )
    notes.append("check_0_3_pass")

    # W5 c0-policy-rectification-f7b2a9: CHECK 0.4 uses frozen RouteContract.c0_policy
    # L0 is the authority; PA must obey the frozen policy, not recompute from L1.
    c0_policy = (route_contract or {}).get("c0_policy")
    if c0_policy is not None:
        evidence_contract_required = bool(c0_policy.get("evidence_contract_required", False))
        c0_mode = str(c0_policy.get("c0_mode", "NOT_REQUIRED"))
    else:
        # Fallback: derive from legacy grounding_required (backward compatibility)
        evidence_contract_required = bool((plan_contract or {}).get("grounding_required", False))
        c0_mode = "RETRIEVE_REQUIRED" if evidence_contract_required else "NOT_REQUIRED"

    if evidence_contract_required:
        # W5: Must have FinalEvidenceContract (not bypass receipt)
        if not _is_present(evidence_contract):
            return BoundaryCheckResult(
                status=BoundaryStatus.FAIL,
                fail_reason=BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE,
                notes=tuple(notes + ["check_0_4_failed: c0_policy.evidence_contract_required=True, no evidence"]),
            )
        evidence_status = str((evidence_contract or {}).get("status", "")).upper()
        if evidence_status == "BLOCKED":
            return BoundaryCheckResult(
                status=BoundaryStatus.FAIL,
                fail_reason=BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE,
                notes=tuple(notes + ["check_0_4_failed: evidence status=BLOCKED"]),
            )
        # W5: Validate evidence came from C0, not a bypass receipt
        c0_status = str((evidence_contract or {}).get("c0_status", "")).upper()
        if c0_status == "BYPASS":
            return BoundaryCheckResult(
                status=BoundaryStatus.FAIL,
                fail_reason=BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE,
                notes=tuple(notes + ["check_0_4_failed: evidence required but got bypass receipt"]),
            )
    else:
        # W5: Bypass mode must have explicit C0BypassReceipt
        bypass_modes = ("BYPASS_PRELOADED_CONTEXT", "BYPASS_CACHE_RETURN", "BYPASS_FALLBACK", "NOT_REQUIRED")
        if c0_mode in bypass_modes:
            # Check if bypass receipt is present
            bypass_receipt = (evidence_contract or {}).get("c0_bypass_reason", "")
            if not bypass_receipt:
                # W5: Allow missing bypass receipt for NOT_REQUIRED with advisory only
                if c0_mode != "NOT_REQUIRED":
                    return BoundaryCheckResult(
                        status=BoundaryStatus.FAIL,
                        fail_reason=BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE,
                        notes=tuple(notes + [f"check_0_4_failed: c0_mode={c0_mode} but no bypass receipt"]),
                    )
    notes.append(f"check_0_4_pass: c0_mode={c0_mode}, evidence_required={evidence_contract_required}")

    # CHECK 0.5 — durable writes requested?
    write_requested = bool((plan_contract or {}).get("write_requested", False))
    if write_requested:
        gov = governance or {}
        durable_write_allowed = bool(gov.get("durable_write_allowed", False))
        # PA itself can never write; we may only PACKAGE proposed mutations
        # if route + governance permit. If not permitted → FAIL.
        if not durable_write_allowed:
            return BoundaryCheckResult(
                status=BoundaryStatus.FAIL,
                fail_reason=BoundaryFailReason.DURABLE_WRITE_NOT_PERMITTED,
                notes=tuple(notes + ["check_0_5_failed: write requested but not permitted"]),
            )
    notes.append("check_0_5_pass")

    # CHECK 0.6 — HITL required?
    gov = governance or {}
    hitl_required = bool(gov.get("hitl_required", False))
    if hitl_required:
        # PA must not produce an executable packet that bypasses HITL.
        # Caller must request escalation_packet=True so PA produces a
        # review-only artifact. If the caller asked for an executable packet
        # while HITL is required, FAIL.
        executable_requested = bool((execution_metadata or {}).get("executable_requested", True))
        if executable_requested:
            return BoundaryCheckResult(
                status=BoundaryStatus.FAIL,
                fail_reason=BoundaryFailReason.HITL_REQUIRED_BUT_EXECUTABLE_REQUESTED,
                notes=tuple(notes + ["check_0_6_failed: HITL required, executable packet requested"]),
            )
    notes.append("check_0_6_pass")

    # CHECK 0.7 — policy hashes consistent across L1/L0/C0/PA/L2.
    declared_hashes = {
        "plan": (plan_contract or {}).get("policy_hash"),
        "route": (route_contract or {}).get("policy_hash"),
        "evidence": (evidence_contract or {}).get("policy_hash") if evidence_contract else None,
        "execution": (execution_metadata or {}).get("policy_hash"),
    }
    seen: set[str] = {h for h in declared_hashes.values() if isinstance(h, str) and h}
    if len(seen) > 1:
        return BoundaryCheckResult(
            status=BoundaryStatus.FAIL,
            fail_reason=BoundaryFailReason.POLICY_HASH_MISMATCH,
            notes=tuple(notes + [f"check_0_7_failed: policy_hash mismatch across {sorted(seen)}"]),
        )
    notes.append("check_0_7_pass")

    return BoundaryCheckResult(
        status=BoundaryStatus.PASS,
        fail_reason=None,
        eligible_for_prompt_assembly=True,
        notes=tuple(notes),
    )


__all__ = [
    "BoundaryCheckResult",
    "BoundaryFailReason",
    "BoundaryStatus",
    "boundary_check",
]
