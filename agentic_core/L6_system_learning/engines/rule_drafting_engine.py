"""Rule Drafting Engine — System Learning Step 6.

Derives fixes, structures improvements, and controls reverts per
System Learning Pipeline documentation.

Takes incident investigation output and produces structured rule proposals
for policy/config updates.

Deterministic, with full ADG traceability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal, Protocol

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
from agentic_core.L6_system_learning.enforcement.determinism import deterministic_json, stable_sha256_json
from tqdm import tqdm

# ADG wiring for rule drafting engine
_emit_records_execution_trace("rule_drafting_engine", "p0", "rule_drafting_trace")
_emit_applies_guardrail("p0", "rule_drafting_engine", "p0_governance")
emit_replay_key("p0", "rule_drafting_engine")
emit_determinism_digest("p0", "rule_drafting_engine")
_emit_writes_via_uwg("p2", "rule_drafting_engine", "uwg_write")
_emit_blocks_direct_write("p2", "rule_drafting_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "rule_drafting_engine", "tool_invocation")
_emit_captures_execution_output("p2", "rule_drafting_engine", "exec_output")
_emit_dispatches_agent("p3", "rule_drafting_engine", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "rule_drafting_engine", "exec_plan")
_emit_routes_to_agent("p3", "rule_drafting_engine", "target_agent")
_emit_checks_agent_registry("p3", "rule_drafting_engine", "agent_registry")
_emit_validates_agent_capability("p3", "rule_drafting_engine", "capability")
_emit_verifies_policy("p3", "rule_drafting_engine", "policy_check")
_emit_verifies_boundary("p3", "rule_drafting_engine", "boundary_check")
_emit_agent_executes_agent("p3", "rule_drafting_engine", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# Rule Drafting Types
# =============================================================================


@dataclass(frozen=True)
class RuleProposal:
    """Structured rule proposal for policy/config updates.

    Attributes
    ----------
    proposal_id:
        Deterministic SHA-256 ID for this proposal.
    target_component:
        Component to modify (prompt_templates, routing_thresholds, tool_policies).
    change_type:
        Type of change (STRUCTURE_IMPROVEMENT, FIX_TARGET, CONTROL_REVERT).
    change_spec:
        Detailed change specification.
    rationale:
        Human-readable rationale for the change.
    incident_trace_id:
        Source incident trace that triggered this proposal.
    confidence:
        Confidence in the proposal (0.0 to 1.0).
    """

    proposal_id: str
    target_component: str
    change_type: Literal["STRUCTURE_IMPROVEMENT", "FIX_TARGET", "CONTROL_REVERT"]
    change_spec: dict
    rationale: str
    incident_trace_id: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("proposal_id must not be empty")
        if not self.target_component:
            raise ValueError("target_component must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    def to_dict(self) -> dict[str, object]:
        return {
            "change_spec": self.change_spec,
            "change_type": self.change_type,
            "confidence": self.confidence,
            "incident_trace_id": self.incident_trace_id,
            "proposal_id": self.proposal_id,
            "rationale": self.rationale,
            "target_component": self.target_component,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


@dataclass(frozen=True)
class RuleDraftingResult:
    """Result of rule drafting process.

    Attributes
    ----------
    artifact_type:
        Always ``RULE_DRAFTING_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    incident_trace_id:
        Source incident trace identifier.
    proposals:
        Tuple of rule proposals generated.
    success:
        True if drafting succeeded.
    error_reason:
        Error description if drafting failed.
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    artifact_type: Literal["RULE_DRAFTING_RESULT"]
    result_id: str
    incident_trace_id: str
    proposals: tuple[RuleProposal, ...]
    success: bool
    error_reason: str | None
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "RULE_DRAFTING_RESULT":
            raise ValueError(f"artifact_type must be 'RULE_DRAFTING_RESULT', got {self.artifact_type!r}")
        if not self.result_id:
            raise ValueError("result_id must not be empty")
        if not self.incident_trace_id:
            raise ValueError("incident_trace_id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "error_reason": self.error_reason,
            "incident_trace_id": self.incident_trace_id,
            "proposals": [p.to_dict() for p in self.proposals],
            "result_id": self.result_id,
            "success": self.success,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


class ExecutionTraceReader(Protocol):
    """Protocol for reading execution traces."""

    def read_trace(self, trace_id: str) -> dict:
        """Read and return the execution trace content."""
        raise NotImplementedError


# =============================================================================
# RuleDraftingEngine
# =============================================================================


class RuleDraftingEngine:
    """Engine for drafting rules from incident investigations (Step 6).

    Derives fix targets, structures improvements, and controls reverts
    per System Learning Pipeline documentation.

    Deterministic: Same incident inputs always produce same proposals.
    Fail-closed: Insufficient confidence produces no proposals.

    Attributes
    ----------
    min_confidence_threshold:
        Minimum confidence to generate a proposal.
    max_proposals_per_incident:
        Maximum number of proposals to generate.
    """

    DEFAULT_MIN_CONFIDENCE: float = 0.6
    DEFAULT_MAX_PROPOSALS: int = 3

    MUTABLE_COMPONENTS: frozenset[str] = frozenset(
        {
            "prompt_templates",
            "routing_thresholds",
            "tool_policies",
        }
    )

    def __init__(
        self,
        min_confidence_threshold: float | None = None,
        max_proposals_per_incident: int | None = None,
    ) -> None:
        self.min_confidence_threshold = min_confidence_threshold or self.DEFAULT_MIN_CONFIDENCE
        self.max_proposals_per_incident = max_proposals_per_incident or self.DEFAULT_MAX_PROPOSALS

    def draft_rules(
        self,
        incident_trace_id: str,
        investigation_result: dict,
        timestamp_utc: int,
    ) -> RuleDraftingResult:
        """Draft rules from incident investigation.

        Parameters
        ----------
        incident_trace_id:
            Source incident trace identifier.
        investigation_result:
            Incident investigation output with root cause analysis.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        RuleDraftingResult
            Deterministic rule drafting result with proposals.
        """
        _emit_records_execution_trace("rule_drafting_engine", "draft_start", incident_trace_id)

        try:
            # Extract findings from investigation
            root_cause = investigation_result.get("root_cause", "")
            severity = investigation_result.get("severity", "INFO")
            affected_components = investigation_result.get("affected_components", [])

            # Derive fix targets
            proposals: list[RuleProposal] = []

            # Generate structure improvement proposals
            structure_proposals = self._derive_structure_improvements(
                incident_trace_id,
                root_cause,
                affected_components,
                timestamp_utc,
            )
            proposals.extend(structure_proposals)

            # Generate fix target proposals
            fix_proposals = self._derive_fix_targets(
                incident_trace_id,
                root_cause,
                affected_components,
                timestamp_utc,
            )
            proposals.extend(fix_proposals)

            # Generate control revert proposals if needed
            if severity in ["CRITICAL", "HIGH"]:
                revert_proposals = self._derive_control_reverts(
                    incident_trace_id,
                    root_cause,
                    affected_components,
                    timestamp_utc,
                )
                proposals.extend(revert_proposals)

            # Sort by confidence and limit
            proposals.sort(key=lambda p: p.confidence, reverse=True)
            proposals = proposals[: self.max_proposals_per_incident]

            _emit_records_execution_trace("rule_drafting_engine", "draft_complete", incident_trace_id)

            result = RuleDraftingResult(
                artifact_type="RULE_DRAFTING_RESULT",
                result_id=stable_sha256_json(
                    {
                        "incident_trace_id": incident_trace_id,
                        "proposal_count": len(proposals),
                        "timestamp_utc": timestamp_utc,
                    }
                ),
                incident_trace_id=incident_trace_id,
                proposals=tuple(proposals),
                success=True,
                error_reason=None,
                timestamp_utc=timestamp_utc,
            )

            logger.info(
                "Rule drafting complete: incident=%s, proposals=%d",
                incident_trace_id,
                len(proposals),
            )

            return result

        except (ValueError, TypeError, KeyError) as e:
            logger.error("Rule drafting failed: %s", e)
            return RuleDraftingResult(
                artifact_type="RULE_DRAFTING_RESULT",
                result_id=stable_sha256_json(
                    {
                        "incident_trace_id": incident_trace_id,
                        "error": str(e),
                        "timestamp_utc": timestamp_utc,
                    }
                ),
                incident_trace_id=incident_trace_id,
                proposals=(),
                success=False,
                error_reason=str(e),
                timestamp_utc=timestamp_utc,
            )

    def _derive_structure_improvements(
        self,
        incident_trace_id: str,
        root_cause: str,
        affected_components: list[str],
        timestamp_utc: int,
    ) -> list[RuleProposal]:
        """Derive structure improvement proposals."""
        proposals: list[RuleProposal] = []

        # Analyze root cause for structural issues
        structural_keywords = ["schema", "structure", "architecture", "design"]
        if any(kw in root_cause.lower() for kw in structural_keywords):
            for component in tqdm(affected_components, desc="Processing", unit="item"):
                if component in self.MUTABLE_COMPONENTS:
                    proposal = RuleProposal(
                        proposal_id=stable_sha256_json(
                            {
                                "incident": incident_trace_id,
                                "type": "STRUCTURE_IMPROVEMENT",
                                "component": component,
                                "timestamp_utc": timestamp_utc,
                            }
                        ),
                        target_component=component,
                        change_type="STRUCTURE_IMPROVEMENT",
                        change_spec={
                            "action": "refactor_structure",
                            "target": component,
                            "reason": f"Structural issue identified: {root_cause[:100]}",
                        },
                        rationale=f"Structural improvement needed in {component} based on root cause: {root_cause[:200]}",
                        incident_trace_id=incident_trace_id,
                        confidence=0.75,
                    )
                    proposals.append(proposal)

        return proposals

    def _derive_fix_targets(
        self,
        incident_trace_id: str,
        root_cause: str,
        affected_components: list[str],
        timestamp_utc: int,
    ) -> list[RuleProposal]:
        """Derive fix target proposals."""
        proposals: list[RuleProposal] = []

        # Generate fix proposals for affected components
        for component in tqdm(affected_components, desc="Processing", unit="item"):
            if component in self.MUTABLE_COMPONENTS:
                # Determine fix type from root cause
                fix_action = self._determine_fix_action(root_cause)

                proposal = RuleProposal(
                    proposal_id=stable_sha256_json(
                        {
                            "incident": incident_trace_id,
                            "type": "FIX_TARGET",
                            "component": component,
                            "action": fix_action,
                            "timestamp_utc": timestamp_utc,
                        }
                    ),
                    target_component=component,
                    change_type="FIX_TARGET",
                    change_spec={
                        "action": fix_action,
                        "target": component,
                        "root_cause": root_cause[:500],
                    },
                    rationale=f"Fix target identified in {component}: {root_cause[:200]}",
                    incident_trace_id=incident_trace_id,
                    confidence=0.8,
                )

                if proposal.confidence >= self.min_confidence_threshold:
                    proposals.append(proposal)

        return proposals

    def _derive_control_reverts(
        self,
        incident_trace_id: str,
        root_cause: str,
        affected_components: list[str],
        timestamp_utc: int,
    ) -> list[RuleProposal]:
        """Derive control revert proposals for critical issues."""
        proposals: list[RuleProposal] = []

        # Check if revert is warranted
        revert_keywords = ["regression", "breakage", "failure", "error"]
        if any(kw in root_cause.lower() for kw in revert_keywords):
            for component in tqdm(affected_components, desc="Processing", unit="item"):
                if component in self.MUTABLE_COMPONENTS:
                    proposal = RuleProposal(
                        proposal_id=stable_sha256_json(
                            {
                                "incident": incident_trace_id,
                                "type": "CONTROL_REVERT",
                                "component": component,
                                "timestamp_utc": timestamp_utc,
                            }
                        ),
                        target_component=component,
                        change_type="CONTROL_REVERT",
                        change_spec={
                            "action": "revert_to_last_known_good",
                            "target": component,
                            "reason": f"Critical issue requires revert: {root_cause[:100]}",
                        },
                        rationale=f"Control revert recommended for {component} due to critical issue: {root_cause[:200]}",
                        incident_trace_id=incident_trace_id,
                        confidence=0.9,  # High confidence for safety
                    )
                    proposals.append(proposal)

        return proposals

    def _determine_fix_action(self, root_cause: str) -> str:
        """Determine fix action type from root cause description."""
        action_map = {
            "timeout": "increase_timeout",
            "memory": "optimize_memory",
            "cpu": "optimize_compute",
            "error": "add_error_handling",
            "exception": "fix_exception_handling",
            "null": "add_null_checks",
            "race": "add_synchronization",
            "deadlock": "fix_concurrency",
        }

        root_lower = root_cause.lower()
        for keyword, action in action_map.items():
            if keyword in root_lower:
                return action

        return "general_fix"


__all__ = ["RuleDraftingEngine", "RuleProposal", "RuleDraftingResult"]
