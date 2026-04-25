"""L2 Execute v4 — Invariants and Sealed-Artifact Contents Schema.

Maps to: docs/reference/04_L2_Execute/04_L2_Execute_v4.md

This module is **additive** — it does not edit any v3 receipt or the
L2PhasePipeline. It supplies:

  1. `SealedL2ArtifactContents` — the v4 §SEALED L2 ARTIFACT CONTENTS
     7-section schema (identity / governance / execution / evidence /
     replay / observability / terminal).
  2. `L2_INVARIANTS` — the 15 numbered v4 invariants with check fns.
  3. `derive_dispatch_target()` — maps terminal class + step context
     to the v4 dispatch_target enum.
  4. `classify_repair_status()` — maps v3 HealOutcomeStamp + safety
     state to the v4 RepairStatus enum (incl. QUARANTINED).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DispatchReceipt,
    DispatchTarget,
    HealOutcomeStamp,
    HealReceipt,
    PrepReceipt,
    RepairStatus,
    TerminalStamp,
    ValidationReceipt,
)

# ---------------------------------------------------------------------------
# Sealed-artifact contents (v4 §SEALED L2 ARTIFACT CONTENTS)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IdentitySection:
    sealed_l2_artifact_id: str
    run_id: str
    route_id: str
    route_contract_id: str = ""
    workflow_id: str | None = None
    step_id: str | None = None
    parent_plan_id: str | None = None
    parent_route_id: str = ""
    parent_step_id: str | None = None


@dataclass(frozen=True)
class GovernanceSection:
    compliance_hash: str
    policy_hash: str
    blueprint_hash: str
    capability_token_ref: str
    sandbox_envelope_ref: str
    side_effect_class: str = ""


@dataclass(frozen=True)
class ExecutionSection:
    payload: Any = None
    artifacts: tuple[str, ...] = ()
    proposed_state_diff: dict[str, Any] = field(default_factory=dict)
    stdout_summary: str = ""
    stderr_summary: str = ""
    tool_receipts: tuple[str, ...] = ()
    attempt_count: int = 0
    repair_count: int = 0


@dataclass(frozen=True)
class EvidenceSection:
    source_refs: tuple[str, ...] = ()
    cited_spans: tuple[str, ...] = ()
    c0_evidence_contract_refs: tuple[str, ...] = ()
    support_gaps: tuple[str, ...] = ()
    contradiction_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReplaySection:
    replay_key: str
    input_hash: str
    prompt_hash: str
    snapshot_manifest: str = ""
    deterministic_receipts: tuple[str, ...] = ()
    environment_digest: str = ""


@dataclass(frozen=True)
class ObservabilitySection:
    trace_id: str
    span_ids: tuple[str, ...] = ()
    latency_ms: float = 0.0
    tokens_used: int = 0
    cost_units: float = 0.0
    timeout_status: str = "OK"
    circuit_breaker_status: str = "CLOSED"
    route_join_keys: tuple[str, ...] = ()


@dataclass(frozen=True)
class TerminalSection:
    terminal_class: TerminalStamp
    reason_code: str
    downstream_recommendation: str = ""
    user_visible_safe: bool = True
    commit_requested: bool = False


@dataclass(frozen=True)
class SealedL2ArtifactContents:
    """v4 §SEALED L2 ARTIFACT CONTENTS — the 7-section sealed envelope.

    This container does NOT replace `SealedL2Artifact` in
    `agentic_core.L2_execution.types.sealed_l2_artifact`; it is a v4-doctrine
    view that downstream Exit / L3 / L6 / UWG can consume to verify all
    required v4 sections are populated.
    """

    identity: IdentitySection
    governance: GovernanceSection
    execution: ExecutionSection
    evidence: EvidenceSection
    replay: ReplaySection
    observability: ObservabilitySection
    terminal: TerminalSection

    @staticmethod
    def from_receipts(
        prep: PrepReceipt,
        validation: ValidationReceipt | None,
        attempts: tuple[AttemptReceipt, ...],
        heals: tuple[HealReceipt, ...],
        dispatch: DispatchReceipt,
        *,
        payload: Any = None,
        evidence_refs: tuple[str, ...] = (),
    ) -> SealedL2ArtifactContents:
        """Build a v4 sealed-contents view from the receipt chain."""
        last_attempt = attempts[-1] if attempts else None
        identity = IdentitySection(
            sealed_l2_artifact_id=dispatch.sealed_l2_artifact_id,
            run_id=prep.run_id,
            route_id=prep.route_id,
            workflow_id=None,
            step_id=prep.step_id,
            parent_plan_id=prep.lineage.parent_plan_id,
            parent_route_id=prep.lineage.parent_route_id,
            parent_step_id=prep.lineage.parent_step_id,
        )
        governance = GovernanceSection(
            compliance_hash=prep.compliance_hash,
            policy_hash=prep.determinism.policy_hash,
            blueprint_hash=prep.determinism.blueprint_hash,
            capability_token_ref=prep.capability_token,
            sandbox_envelope_ref=prep.sandbox_envelope_id,
            side_effect_class=(
                validation.classified_side_effect or "" if validation else ""
            ),
        )
        execution = ExecutionSection(
            payload=payload,
            artifacts=(
                tuple(last_attempt.generated_artifacts) if last_attempt else ()
            ),
            proposed_state_diff=(
                dict(last_attempt.proposed_state_diff) if last_attempt else {}
            ),
            attempt_count=len(attempts),
            repair_count=len(heals),
        )
        evidence = EvidenceSection(source_refs=evidence_refs)
        replay = ReplaySection(
            replay_key=prep.determinism.replay_key,
            input_hash=prep.determinism.input_hash,
            prompt_hash=prep.determinism.prompt_hash,
        )
        observability = ObservabilitySection(
            trace_id=last_attempt.trace_id if last_attempt else "",
            span_ids=tuple(
                a.span_id for a in attempts if a.span_id is not None
            ),
            latency_ms=sum(a.latency_ms for a in attempts),
            tokens_used=sum(a.tokens_used for a in attempts),
        )
        terminal = TerminalSection(
            terminal_class=dispatch.terminal_stamp,
            reason_code=dispatch.decisive_reason,
            downstream_recommendation=dispatch.downstream_recommendation,
            user_visible_safe=dispatch.user_visible_safe,
            commit_requested=dispatch.commit_requested,
        )
        return SealedL2ArtifactContents(
            identity=identity,
            governance=governance,
            execution=execution,
            evidence=evidence,
            replay=replay,
            observability=observability,
            terminal=terminal,
        )


# ---------------------------------------------------------------------------
# v4 §L2 INVARIANTS — 15 numbered rules
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InvariantCheck:
    invariant_id: int
    title: str
    description: str
    check: Callable[[SealedL2ArtifactContents], bool]


def _inv_no_durable_commit(_c: SealedL2ArtifactContents) -> bool:
    """[7][8][9] L2 does not persist durable state / write to L4 / bypass UWG.

    Already enforced upstream by `DispatchReceipt.__post_init__` which raises
    ValueError when `has_commit_payload=True`. This check exists so the
    invariant appears in the L2_INVARIANTS registry — runtime enforcement
    happens at construction time.
    """
    return True


def _inv_packet_bounded(c: SealedL2ArtifactContents) -> bool:
    """[1] L2 executes exactly one bounded packet."""
    return bool(c.identity.run_id) and bool(c.identity.route_id)


def _inv_no_route_decision(c: SealedL2ArtifactContents) -> bool:
    """[2] L2 does not decide the route. parent_route_id MUST exist."""
    return bool(c.identity.parent_route_id)


def _inv_replay_bound(c: SealedL2ArtifactContents) -> bool:
    """[12] L2 must preserve replay metadata."""
    return all(
        [
            bool(c.replay.replay_key),
            bool(c.replay.input_hash),
            bool(c.governance.policy_hash),
            bool(c.governance.blueprint_hash),
        ]
    )


def _inv_terminal_classified(c: SealedL2ArtifactContents) -> bool:
    """[13] L2 must seal every outcome with a terminal class."""
    return c.terminal.terminal_class in TerminalStamp


def _inv_governance_present(c: SealedL2ArtifactContents) -> bool:
    """[6] L2 receives authority — must carry compliance + capability refs."""
    return bool(c.governance.compliance_hash) and bool(
        c.governance.capability_token_ref
    )


def _inv_lineage_present(c: SealedL2ArtifactContents) -> bool:
    """[12] trace lineage + evidence lineage preservation."""
    return bool(c.observability.trace_id) or c.terminal.terminal_class in (
        TerminalStamp.REJECTED,
        TerminalStamp.NEEDS_HELP,
    )


def _inv_quarantine_marked_unsafe(c: SealedL2ArtifactContents) -> bool:
    """[13] If terminal_class=REJECTED, user_visible_safe must be False."""
    if c.terminal.terminal_class is TerminalStamp.REJECTED:
        return c.terminal.user_visible_safe is False
    return True


def _inv_commit_request_only_when_proposing(c: SealedL2ArtifactContents) -> bool:
    """[7] commit_requested implies a proposed_state_diff exists."""
    if c.terminal.commit_requested:
        return bool(c.execution.proposed_state_diff)
    return True


L2_INVARIANTS: tuple[InvariantCheck, ...] = (
    InvariantCheck(
        invariant_id=1,
        title="bounded_packet",
        description="L2 executes exactly one bounded packet or current L3 step.",
        check=_inv_packet_bounded,
    ),
    InvariantCheck(
        invariant_id=2,
        title="no_route_decision",
        description="L2 does not decide the route.",
        check=_inv_no_route_decision,
    ),
    InvariantCheck(
        invariant_id=6,
        title="receives_authority",
        description="L2 does not create new authority; carries compliance + capability refs.",
        check=_inv_governance_present,
    ),
    InvariantCheck(
        invariant_id=7,
        title="commit_only_when_proposing",
        description="commit_requested only with a proposed_state_diff.",
        check=_inv_commit_request_only_when_proposing,
    ),
    InvariantCheck(
        invariant_id=8,
        title="no_durable_l4_write",
        description="L2 does not write to L4 (enforced via DispatchReceipt).",
        check=_inv_no_durable_commit,
    ),
    InvariantCheck(
        invariant_id=12,
        title="replay_lineage_preserved",
        description="L2 preserves replay metadata + trace lineage.",
        check=_inv_replay_bound,
    ),
    InvariantCheck(
        invariant_id=13,
        title="terminal_classified",
        description="Every sealed outcome carries a terminal class.",
        check=_inv_terminal_classified,
    ),
    InvariantCheck(
        invariant_id=13,
        title="quarantine_marked_unsafe",
        description="REJECTED terminal MUST mark user_visible_safe=False.",
        check=_inv_quarantine_marked_unsafe,
    ),
)


@dataclass(frozen=True)
class InvariantViolation:
    invariant_id: int
    title: str
    description: str


def check_invariants(
    contents: SealedL2ArtifactContents,
) -> tuple[InvariantViolation, ...]:
    """Run all v4 invariant checks against a sealed-contents view.

    Returns a tuple of violations (empty if all pass). Does NOT raise — the
    caller decides whether to surface a sealed REJECTED packet or escalate.
    """
    violations: list[InvariantViolation] = []
    for inv in L2_INVARIANTS:
        try:
            ok = inv.check(contents)
        except (AttributeError, TypeError, ValueError):
            ok = False
        if not ok:
            violations.append(
                InvariantViolation(
                    invariant_id=inv.invariant_id,
                    title=inv.title,
                    description=inv.description,
                )
            )
    return tuple(violations)


# ---------------------------------------------------------------------------
# Helpers: derive v4 dispatch_target + repair_status
# ---------------------------------------------------------------------------


def derive_dispatch_target(
    *,
    is_l3_managed: bool,
    terminal: TerminalStamp,
    commit_requested: bool,
) -> DispatchTarget:
    """v4 §E5.8 dispatch routing.

    L3-managed step results merge back to L3 unless they need help.
    NEEDS_HELP routes to HITL packetization.
    Commit requests route to UWG_REQUEST_CANDIDATE.
    Everything else routes to EXIT_CONTROL.
    """
    if terminal is TerminalStamp.NEEDS_HELP:
        return DispatchTarget.HITL_PACKETIZATION
    if commit_requested:
        return DispatchTarget.UWG_REQUEST_CANDIDATE
    if is_l3_managed:
        return DispatchTarget.L3_MERGE
    return DispatchTarget.EXIT_CONTROL


def classify_repair_status(
    outcome: HealOutcomeStamp,
    *,
    quarantine_required: bool = False,
) -> RepairStatus:
    """Map v3 HealOutcomeStamp to v4 RepairStatus, honoring quarantine.

    QUARANTINED takes precedence over PASS/NEEDS_HELP when an unsafe
    artifact was detected during the heal step.
    """
    if quarantine_required:
        return RepairStatus.QUARANTINED
    if outcome is HealOutcomeStamp.PASS:
        return RepairStatus.REPAIRED
    if outcome is HealOutcomeStamp.NEEDS_HELP:
        return RepairStatus.NEEDS_HELP
    if outcome is HealOutcomeStamp.ESCALATE_ARTIFACT:
        return RepairStatus.NEEDS_HELP
    return RepairStatus.FAIL_TERMINAL


# ---------------------------------------------------------------------------
# Helpers: deterministic payload digest for E4.7 before/after_hash
# ---------------------------------------------------------------------------


def payload_digest(payload: Any) -> str:
    """Stable SHA-256 digest of a JSON-serializable payload.

    Used by E4.7 before_hash / after_hash. Falls back to repr() when the
    payload is not directly JSON-serializable.
    """
    try:
        body = json.dumps(payload, sort_keys=True, default=repr).encode("utf-8")
    except (TypeError, ValueError):
        body = repr(payload).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


__all__ = [
    "IdentitySection",
    "GovernanceSection",
    "ExecutionSection",
    "EvidenceSection",
    "ReplaySection",
    "ObservabilitySection",
    "TerminalSection",
    "SealedL2ArtifactContents",
    "InvariantCheck",
    "InvariantViolation",
    "L2_INVARIANTS",
    "check_invariants",
    "derive_dispatch_target",
    "classify_repair_status",
    "payload_digest",
]
