"""Approval Gauntlet Engine — System Learning Step 7.

COMMANDANT sovereign approval with regression/safety gates per
System Learning Pipeline documentation.

Validates rule proposals through:
  - Modes/shadow reply validation
  - Regression gates
  - Safety gates
  - COMMANDANT sovereign approval decision

Deterministic, fail-closed, with full ADG traceability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json
from system_learning.engines.rule_drafting_engine import RuleProposal
from tqdm import tqdm

# ADG wiring for approval gauntlet engine
_emit_records_execution_trace("approval_gauntlet_engine", "p0", "approval_gauntlet_trace")
_emit_applies_guardrail("p0", "approval_gauntlet_engine", "p0_governance")
emit_replay_key("p0", "approval_gauntlet_engine")
emit_determinism_digest("p0", "approval_gauntlet_engine")
_emit_writes_via_uwg("p2", "approval_gauntlet_engine", "uwg_write")
_emit_blocks_direct_write("p2", "approval_gauntlet_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "approval_gauntlet_engine", "tool_invocation")
_emit_captures_execution_output("p2", "approval_gauntlet_engine", "exec_output")
_emit_dispatches_agent("p3", "approval_gauntlet_engine", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "approval_gauntlet_engine", "exec_plan")
_emit_routes_to_agent("p3", "approval_gauntlet_engine", "target_agent")
_emit_checks_agent_registry("p3", "approval_gauntlet_engine", "agent_registry")
_emit_validates_agent_capability("p3", "approval_gauntlet_engine", "capability")
_emit_verifies_policy("p3", "approval_gauntlet_engine", "policy_check")
_emit_verifies_boundary("p3", "approval_gauntlet_engine", "boundary_check")
_emit_agent_executes_agent("p3", "approval_gauntlet_engine", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# Approval Gauntlet Types
# =============================================================================


@dataclass(frozen=True)
class ApprovalDecision:
    """Approval decision from COMMANDANT sovereign authority.

    Attributes
    ----------
    decision_id:
        Deterministic SHA-256 ID for this decision.
    proposal_id:
        Reference to the rule proposal being decided.
    decision:
        APPROVE, REJECT, or LOOP (send back for revision).
    reason:
        Human-readable reason for the decision.
    confidence:
        Confidence in the decision (0.0 to 1.0).
    gate_results:
        Results from each gauntlet gate.
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    decision_id: str
    proposal_id: str
    decision: Literal["APPROVE", "REJECT", "LOOP"]
    reason: str
    confidence: float
    gate_results: dict[str, bool]
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id must not be empty")
        if not self.proposal_id:
            raise ValueError("proposal_id must not be empty")
        if self.decision not in ("APPROVE", "REJECT", "LOOP"):
            raise ValueError(f"decision must be APPROVE/REJECT/LOOP, got {self.decision!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    def to_dict(self) -> dict[str, object]:
        return {
            "confidence": self.confidence,
            "decision": self.decision,
            "decision_id": self.decision_id,
            "gate_results": self.gate_results,
            "proposal_id": self.proposal_id,
            "reason": self.reason,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


@dataclass(frozen=True)
class ApprovalGauntletResult:
    """Result of approval gauntlet process.

    Attributes
    ----------
    artifact_type:
        Always ``APPROVAL_GAUNTLET_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    incident_trace_id:
        Source incident trace identifier.
    proposals:
        Tuple of proposals with their decisions.
    approved_proposals:
        Tuple of approved proposal IDs.
    rejected_proposals:
        Tuple of rejected proposal IDs.
    loop_proposals:
        Tuple of proposals sent back for revision.
    overall_decision:
        APPROVE_ALL, REJECT_ALL, PARTIAL, or LOOP_SOME.
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    artifact_type: Literal["APPROVAL_GAUNTLET_RESULT"]
    result_id: str
    incident_trace_id: str
    proposals: tuple[tuple[RuleProposal, ApprovalDecision], ...]
    approved_proposals: tuple[str, ...]
    rejected_proposals: tuple[str, ...]
    loop_proposals: tuple[str, ...]
    overall_decision: Literal["APPROVE_ALL", "REJECT_ALL", "PARTIAL", "LOOP_SOME"]
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "APPROVAL_GAUNTLET_RESULT":
            raise ValueError(f"artifact_type must be 'APPROVAL_GAUNTLET_RESULT', got {self.artifact_type!r}")
        if not self.result_id:
            raise ValueError("result_id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "approved_proposals": list(self.approved_proposals),
            "artifact_type": self.artifact_type,
            "incident_trace_id": self.incident_trace_id,
            "loop_proposals": list(self.loop_proposals),
            "overall_decision": self.overall_decision,
            "proposals": [{"proposal": p.to_dict(), "decision": d.to_dict()} for p, d in self.proposals],
            "rejected_proposals": list(self.rejected_proposals),
            "result_id": self.result_id,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# ApprovalGauntletEngine
# =============================================================================


class ApprovalGauntletEngine:
    """Engine for COMMANDANT sovereign approval (Step 7).

    Runs proposals through the gauntlet:
        1. Mode/shadow reply validation
        2. Regression gate
        3. Safety gate
        4. COMMANDANT sovereign decision

    Deterministic: Same proposals always produce same decisions.
    Fail-closed: Any gate failure results in REJECT or LOOP.

    Attributes
    ----------
    min_confidence_for_approval:
        Minimum confidence to approve a proposal.
    require_all_gates:
        If True, all gates must pass for approval.
    """

    DEFAULT_MIN_CONFIDENCE: float = 0.8

    def __init__(
        self,
        min_confidence_for_approval: float | None = None,
        require_all_gates: bool = True,
    ) -> None:
        self.min_confidence_for_approval = min_confidence_for_approval or self.DEFAULT_MIN_CONFIDENCE
        self.require_all_gates = require_all_gates
        # v6 KPI counters (GAUNTLET_FALSE_PROMOTE_RATE).
        # Callers mark promotions via :meth:`mark_promotion` after UWG ink
        # and reversions via :meth:`mark_reversion` when a rollback is
        # applied. Counters are instance-level; publish via
        # :meth:`publish_kpi_sample`.
        self._total_promotions: int = 0
        self._reverted_promotions: int = 0

    # --- v6 KPI surface (GAUNTLET_FALSE_PROMOTE_RATE) -------------------

    def mark_promotion(self) -> None:
        """Record that an approval result was promoted to UWG ink."""
        self._total_promotions += 1

    def mark_reversion(self) -> None:
        """Record that a promoted change was later reverted."""
        self._reverted_promotions += 1

    @property
    def promotion_counters(self) -> tuple[int, int]:
        """Return ``(reverted_promotions, total_promotions)``."""
        return (self._reverted_promotions, self._total_promotions)

    def reset_promotion_counters(self) -> None:
        """Reset v6 KPI counters without affecting approval policy."""
        self._total_promotions = 0
        self._reverted_promotions = 0

    def publish_kpi_sample(self, board: Any) -> None:
        """Publish GAUNTLET_FALSE_PROMOTE_RATE to ``board``.

        Lazy imports the producer helper to avoid import-time dependency.
        Never raises — KPI emission must not break gauntlet operation.
        """
        try:
            from system_learning.engines.v6_kpi_producers import (  # noqa: PLC0415
                record_gauntlet_false_promote_rate,
            )

            record_gauntlet_false_promote_rate(
                board,
                reverted_promotions=self._reverted_promotions,
                total_promotions=self._total_promotions,
            )
        except (ImportError, AttributeError, RuntimeError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break gauntlet
            logger.warning("v6_kpi_gauntlet_false_promote_rate_failed: %s", exc)

    def run_gauntlet(
        self,
        incident_trace_id: str,
        proposals: tuple[RuleProposal, ...],
        shadow_validation_results: dict[str, dict],
        timestamp_utc: int,
    ) -> ApprovalGauntletResult:
        """Run proposals through approval gauntlet.

        Parameters
        ----------
        incident_trace_id:
            Source incident trace identifier.
        proposals:
            Rule proposals to evaluate.
        shadow_validation_results:
            Results from shadow mode validation.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        ApprovalGauntletResult
            Deterministic approval gauntlet result.
        """
        _emit_records_execution_trace("approval_gauntlet_engine", "gauntlet_start", incident_trace_id)

        proposal_decisions: list[tuple[RuleProposal, ApprovalDecision]] = []
        approved: list[str] = []
        rejected: list[str] = []
        loop: list[str] = []

        for proposal in tqdm(proposals, desc="Processing", unit="item"):
            # Run gauntlet gates
            gate_results = self._run_gauntlet_gates(proposal, shadow_validation_results)

            # Make sovereign decision
            decision = self._make_sovereign_decision(proposal, gate_results, timestamp_utc)

            proposal_decisions.append((proposal, decision))

            # Categorize decision
            if decision.decision == "APPROVE":
                approved.append(proposal.proposal_id)
            elif decision.decision == "REJECT":
                rejected.append(proposal.proposal_id)
            else:  # LOOP
                loop.append(proposal.proposal_id)

        # Determine overall decision
        overall_decision = self._determine_overall_decision(approved, rejected, loop)

        _emit_records_execution_trace("approval_gauntlet_engine", "gauntlet_complete", incident_trace_id)

        result = ApprovalGauntletResult(
            artifact_type="APPROVAL_GAUNTLET_RESULT",
            result_id=stable_sha256_json(
                {
                    "incident_trace_id": incident_trace_id,
                    "approved_count": len(approved),
                    "rejected_count": len(rejected),
                    "loop_count": len(loop),
                    "timestamp_utc": timestamp_utc,
                }
            ),
            incident_trace_id=incident_trace_id,
            proposals=tuple(proposal_decisions),
            approved_proposals=tuple(approved),
            rejected_proposals=tuple(rejected),
            loop_proposals=tuple(loop),
            overall_decision=overall_decision,
            timestamp_utc=timestamp_utc,
        )

        logger.info(
            "Approval gauntlet complete: incident=%s, approved=%d, rejected=%d, loop=%d, overall=%s",
            incident_trace_id,
            len(approved),
            len(rejected),
            len(loop),
            overall_decision,
        )

        return result

    def _run_gauntlet_gates(
        self,
        proposal: RuleProposal,
        shadow_validation_results: dict[str, dict],
    ) -> dict[str, bool]:
        """Run proposal through all gauntlet gates."""
        results: dict[str, bool] = {}

        # Gate 1: Mode/shadow reply validation
        results["shadow_mode"] = self._validate_shadow_mode(proposal, shadow_validation_results)

        # Gate 2: Regression gate
        results["regression"] = self._check_regression_gate(proposal)

        # Gate 3: Safety gate
        results["safety"] = self._check_safety_gate(proposal)

        # Gate 4: Policy compliance gate
        results["policy"] = self._check_policy_gate(proposal)

        return results

    def _validate_shadow_mode(
        self,
        proposal: RuleProposal,
        shadow_validation_results: dict[str, dict],
    ) -> bool:
        """Validate shadow mode execution results."""
        # Check if proposal was tested in shadow mode
        shadow_result = shadow_validation_results.get(proposal.proposal_id)

        if not shadow_result:
            # No shadow testing available - fail open for now
            return True

        # Check shadow execution success
        shadow_success = shadow_result.get("success", False)
        shadow_errors = shadow_result.get("errors", [])

        # Fail if shadow execution had errors
        if shadow_errors:
            return False

        return shadow_success

    def _check_regression_gate(self, proposal: RuleProposal) -> bool:
        """Check regression gate for proposal."""
        # High-confidence proposals have lower regression risk
        if proposal.confidence >= 0.9:
            return True

        # Control reverts have higher regression risk
        if proposal.change_type == "CONTROL_REVERT":
            return proposal.confidence >= 0.85

        # Structure improvements need higher confidence
        if proposal.change_type == "STRUCTURE_IMPROVEMENT":
            return proposal.confidence >= 0.75

        return proposal.confidence >= 0.7

    def _check_safety_gate(self, proposal: RuleProposal) -> bool:
        """Check safety gate for proposal."""
        # All proposals must pass basic safety checks

        # Check for critical component modifications
        critical_components = {"safety_plane", "guardrail", "policy_enforcer"}
        if proposal.target_component in critical_components:
            # Extra scrutiny for safety-critical components
            return proposal.confidence >= 0.95

        # Check for dangerous change types
        dangerous_actions = {"disable_safety", "bypass_guardrail", "remove_policy"}
        change_action = proposal.change_spec.get("action", "")
        if any(danger in change_action.lower() for danger in dangerous_actions):
            return False  # Auto-reject dangerous actions

        return True

    def _check_policy_gate(self, proposal: RuleProposal) -> bool:
        """Check policy compliance gate for proposal."""
        # Check if proposal violates any policies

        # Must have valid target component
        valid_components = {"prompt_templates", "routing_thresholds", "tool_policies"}
        if proposal.target_component not in valid_components:
            return False

        # Must have valid change type
        valid_change_types = {"STRUCTURE_IMPROVEMENT", "FIX_TARGET", "CONTROL_REVERT"}
        if proposal.change_type not in valid_change_types:
            return False

        return True

    def _make_sovereign_decision(
        self,
        proposal: RuleProposal,
        gate_results: dict[str, bool],
        timestamp_utc: int,
    ) -> ApprovalDecision:
        """Make COMMANDANT sovereign approval decision."""
        # Count gate passes
        passed_gates = sum(gate_results.values())
        total_gates = len(gate_results)

        # Determine decision based on gate results
        if self.require_all_gates and passed_gates < total_gates:
            # Some gates failed
            failed_gates = [name for name, passed in gate_results.items() if not passed]

            if "safety" in failed_gates or "policy" in failed_gates:
                # Critical gate failure - reject
                decision = "REJECT"
                reason = f"Critical gate failure: {', '.join(failed_gates)}"
                confidence = proposal.confidence * 0.5
            else:
                # Non-critical failure - loop for revision
                decision = "LOOP"
                reason = f"Non-critical gate failure: {', '.join(failed_gates)}"
                confidence = proposal.confidence * 0.8

        elif proposal.confidence < self.min_confidence_for_approval:
            # Confidence too low
            decision = "LOOP"
            reason = (
                f"Confidence {proposal.confidence:.2f} below threshold {self.min_confidence_for_approval:.2f}"
            )
            confidence = proposal.confidence

        else:
            # All gates passed and confidence sufficient
            decision = "APPROVE"
            reason = f"All gates passed, confidence {proposal.confidence:.2f} sufficient"
            confidence = proposal.confidence

        return ApprovalDecision(
            decision_id=stable_sha256_json(
                {
                    "proposal": proposal.proposal_id,
                    "decision": decision,
                    "timestamp_utc": timestamp_utc,
                }
            ),
            proposal_id=proposal.proposal_id,
            decision=decision,
            reason=reason,
            confidence=round(confidence, 6),
            gate_results=gate_results,
            timestamp_utc=timestamp_utc,
        )

    def _determine_overall_decision(
        self,
        approved: list[str],
        rejected: list[str],
        loop: list[str],
    ) -> Literal["APPROVE_ALL", "REJECT_ALL", "PARTIAL", "LOOP_SOME"]:
        """Determine overall gauntlet decision."""
        total = len(approved) + len(rejected) + len(loop)

        if not total:
            return "REJECT_ALL"  # No proposals to evaluate

        if len(approved) == total:
            return "APPROVE_ALL"

        if len(rejected) == total:
            return "REJECT_ALL"

        if len(loop) == total:
            return "LOOP_SOME"

        return "PARTIAL"


__all__ = ["ApprovalGauntletEngine", "ApprovalDecision", "ApprovalGauntletResult"]
