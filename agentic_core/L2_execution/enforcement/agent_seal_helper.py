"""agent_seal_helper — build SealedL2Artifact from agent output + HealResult.

Plan: `docs/archive/windsurf/legacy-tree/plans/l2-execute-v2-agent-conformance-c8e4f1.md` §W5.
Closes G-V7 from plan §5.

Helper primitives:

* :func:`build_seal_from_heal`: constructs a :class:`SealedL2Artifact` from a
  :class:`HealResult` (from W2), mapping the E4 outcome onto the E5 terminal
  classification.
* :func:`build_seal_from_validator`: constructs a sealed artifact from an
  E2 validation verdict dict (from ``evaluate_work_order`` / ``e2_agent_gate``).
* :func:`requires_sealed_return`: opt-in class decorator that marks an agent
  as MUST-seal. The CI gate in ``ops_scripts/ci/check_agent_sealed_return.py``
  only inspects classes carrying this marker — legacy agents without the
  marker are NOT retroactively failed.

All helpers are ADDITIVE. No existing agent is required to migrate in this
plan; W6 demonstrates the pattern on two exemplar agents.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, TypeVar

from agentic_core.L2_execution.types.sealed_l2_artifact import (
    ReplayMetadata,
    SealedL2Artifact,
    TerminalClassification,
    ValidationCounters,
)
from agentic_core.L5_safety.types.heal_request_types import HealOutcome, HealResult

__all__ = [
    "REQUIRES_SEALED_RETURN_ATTR",
    "build_seal_from_heal",
    "build_seal_from_validator",
    "heal_outcome_to_terminal",
    "requires_sealed_return",
    "sealed_exempt",
]


REQUIRES_SEALED_RETURN_ATTR = "__l2v2_requires_sealed_return__"


def heal_outcome_to_terminal(outcome: HealOutcome) -> TerminalClassification:
    """Map W2 HealOutcome to E5 TerminalClassification.

    Mapping rules:
      * SUCCESS            -> SUCCESS
      * SOFT_REPAIRABLE    -> SUCCESS (repair succeeded on retry)
      * FAIL_TERMINAL      -> FAILURE
      * NEEDS_HELP         -> NEEDS_HELP
    """
    if outcome is HealOutcome.SUCCESS:
        return TerminalClassification.SUCCESS
    if outcome is HealOutcome.SOFT_REPAIRABLE:
        return TerminalClassification.SUCCESS
    if outcome is HealOutcome.FAIL_TERMINAL:
        return TerminalClassification.FAILURE
    if outcome is HealOutcome.NEEDS_HELP:
        return TerminalClassification.NEEDS_HELP
    # Defensive: should be unreachable because HealOutcome is exhaustive.
    raise ValueError(f"Unhandled HealOutcome {outcome!r}")


def build_seal_from_heal(
    heal_result: HealResult,
    *,
    trace_id: str,
    evidence_bundle: dict[str, Any] | None = None,
) -> SealedL2Artifact:
    """Build a SealedL2Artifact from a HealResult.

    The seal's ``exec_trace`` embeds the HealResult's snapshot-binding fields
    so downstream [5] Exit Control can verify the repair stayed on the
    originating policy/blueprint snapshot (L2 Execute v2 §E4 invariant).

    ``state_diff`` stays empty because L2 does not commit state — the seal
    is read-only handoff, per the L2 "no durable commit" invariant.

    ``has_commit_payload`` is always False for heal-originated seals;
    downstream [5] owns any commit authority.
    """
    outcome = heal_result.outcome
    escalation = heal_result.message or None if outcome is HealOutcome.NEEDS_HELP else None
    return SealedL2Artifact(
        artifact_id=str(uuid.uuid4()),
        trace_id=trace_id,
        exec_trace={
            "trace_id": trace_id,
            "policy_hash": heal_result.policy_hash,
            "blueprint_hash": heal_result.blueprint_hash,
            "parent_packet_id": heal_result.parent_packet_id,
            "reason_code": heal_result.reason_code,
            "repair_count": heal_result.repair_count,
        },
        state_diff={},
        evidence_bundle=dict(evidence_bundle or heal_result.evidence or {}),
        validation_counters=ValidationCounters(),
        terminal_classification=heal_outcome_to_terminal(outcome),
        replay_metadata=ReplayMetadata(
            replay_key=trace_id,
            determinism_digest="",
            replay_completeness=0.0,
            seed_captured=False,
            isolation_verified=False,
        ),
        has_commit_payload=False,
        escalation_reason=escalation,
        sealed_at=time.monotonic(),
    )


def build_seal_from_validator(
    verdict: dict[str, Any],
    *,
    trace_id: str,
    evidence_bundle: dict[str, Any] | None = None,
) -> SealedL2Artifact:
    """Build a SealedL2Artifact from an E2 validation verdict dict.

    Input is the dict produced by ``E2Verdict.to_dict()`` (from
    ``e2_validate_before_execute``) or any shape with ``decision`` in
    ``{"approved", "confirm_required", "rejected"}``.

    Mapping:
      * decision="approved"         -> SUCCESS
      * decision="confirm_required" -> NEEDS_HELP (escalate to [5])
      * decision="rejected"         -> REJECTED

    Validator seals carry ``validation_counters`` populated by the caller;
    the helper defaults to 1 policy-check-passed on approved, 1 failed
    otherwise.
    """
    decision = str(verdict.get("decision", "rejected")).lower()
    if decision == "approved":
        tc = TerminalClassification.SUCCESS
        counters = ValidationCounters(policy_checks_passed=1)
        escalation = None
    elif decision == "confirm_required":
        tc = TerminalClassification.NEEDS_HELP
        counters = ValidationCounters(policy_checks_passed=0, policy_checks_failed=0)
        escalation = verdict.get("reason", "confirm required")
    else:
        tc = TerminalClassification.REJECTED
        counters = ValidationCounters(policy_checks_failed=1)
        escalation = verdict.get("reason", "rejected by E2 gate")
    return SealedL2Artifact(
        artifact_id=str(uuid.uuid4()),
        trace_id=trace_id,
        exec_trace={
            "trace_id": trace_id,
            "e2_decision": decision,
            "tool_name": verdict.get("tool_name", ""),
            "reason": verdict.get("reason", ""),
        },
        state_diff={},
        evidence_bundle=dict(evidence_bundle or {}),
        validation_counters=counters,
        terminal_classification=tc,
        replay_metadata=ReplayMetadata(
            replay_key=trace_id,
            determinism_digest="",
            replay_completeness=0.0,
            seed_captured=False,
            isolation_verified=False,
        ),
        has_commit_payload=False,
        escalation_reason=escalation,
        sealed_at=time.monotonic(),
    )


_T = TypeVar("_T", bound=type)


def sealed_exempt(method: Any) -> Any:
    """Method decorator exempting a method from the sealed-return CI gate.

    Use on inherited contract methods (``validate()``, ``heal()``) whose
    return type is fixed by the base class (ValidationVerdict dict or
    HealResult) and is NOT expected to be a SealedL2Artifact. The public
    sealer method on the class (e.g. ``evaluate()``, ``repair()``) is
    the one that returns SealedL2Artifact and IS inspected.

    The decorator is a no-op at runtime; it only marks the method for the
    AST-based gate in ``ops_scripts/ci/check_agent_sealed_return.py``.
    """
    return method


def requires_sealed_return(cls: _T) -> _T:
    """Class decorator: mark an agent class as MUST-seal-its-return.

    The marker is an attribute (``__l2v2_requires_sealed_return__ = True``)
    inspected by :mod:`ops_scripts.ci.check_agent_sealed_return`. The CI
    gate walks marked classes and asserts every public method has a return
    annotation that is or contains :class:`SealedL2Artifact`.

    Legacy agents that don't carry this marker are NOT retroactively
    failed. New agents (and migrated exemplars in W6) SHOULD opt in.
    """
    setattr(cls, REQUIRES_SEALED_RETURN_ATTR, True)
    return cls
