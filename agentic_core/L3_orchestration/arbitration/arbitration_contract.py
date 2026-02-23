"""
Multi-Agent Arbitration Contract

Defines immutable data structures for multi-agent arbitration system.
Provides deterministic JSON serialization for advisor proposals and decisions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AdvisorProposal:
    """Immutable proposal from an advisor agent."""

    advisor_id: str
    decision: str
    confidence: int  # 0-100
    rationale: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate proposal constraints."""
        if not self.advisor_id:
            raise ValueError("advisor_id cannot be empty")
        if not self.decision:
            raise ValueError("decision cannot be empty")
        if not (0 <= self.confidence <= 100):
            raise ValueError("confidence must be between 0 and 100")
        if any(not r for r in self.rationale):
            raise ValueError("rationale items cannot be empty")
        if any(not r for r in self.risks):
            raise ValueError("risk items cannot be empty")
        if any(not a for a in self.artifacts):
            raise ValueError("artifact items cannot be empty")


@dataclass(frozen=True)
class ArbitrationInput:
    """Immutable input for arbitration process."""

    task_id: str
    task_kind: str
    proposals: list[AdvisorProposal] = field(default_factory=list)

    def __post_init__(self):
        """Validate input constraints."""
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.task_kind:
            raise ValueError("task_kind cannot be empty")
        # Check for duplicate advisor IDs
        advisor_ids = [p.advisor_id for p in self.proposals]
        if len(advisor_ids) != len(set(advisor_ids)):
            raise ValueError("duplicate advisor IDs not allowed")


@dataclass(frozen=True)
class ArbitrationDecision:
    """Immutable final arbitration decision."""

    selected_advisor_id: str
    selected_decision: str
    score_breakdown: dict[str, int] = field(default_factory=dict)
    merged_rationale: list[str] = field(default_factory=list)
    merged_risks: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate decision constraints."""
        if not self.selected_advisor_id:
            raise ValueError("selected_advisor_id cannot be empty")
        if not self.selected_decision:
            raise ValueError("selected_decision cannot be empty")


# =============================================================================
# Deterministic Serialization Helpers
# =============================================================================


def proposal_to_json(proposal: AdvisorProposal) -> str:
    """Serialize AdvisorProposal to deterministic JSON."""
    data = {
        "advisor_id": proposal.advisor_id,
        "decision": proposal.decision,
        "confidence": proposal.confidence,
        "rationale": sorted(proposal.rationale),  # Stable ordering
        "risks": sorted(proposal.risks),  # Stable ordering
        "artifacts": sorted(proposal.artifacts),  # Stable ordering
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def proposal_from_json(json_str: str) -> AdvisorProposal:
    """Deserialize JSON string to AdvisorProposal."""
    data = json.loads(json_str)
    return AdvisorProposal(
        advisor_id=data["advisor_id"],
        decision=data["decision"],
        confidence=data["confidence"],
        rationale=data["rationale"],
        risks=data["risks"],
        artifacts=data["artifacts"],
    )


def arbitration_input_to_json(input_data: ArbitrationInput) -> str:
    """Serialize ArbitrationInput to deterministic JSON."""
    data = {
        "task_id": input_data.task_id,
        "task_kind": input_data.task_kind,
        "proposals": [proposal_to_json(p) for p in input_data.proposals],
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def arbitration_input_from_json(json_str: str) -> ArbitrationInput:
    """Deserialize JSON string to ArbitrationInput."""
    data = json.loads(json_str)
    proposals = [proposal_from_json(p_json) for p_json in data["proposals"]]
    return ArbitrationInput(
        task_id=data["task_id"],
        task_kind=data["task_kind"],
        proposals=proposals,
    )


def decision_to_json(decision: ArbitrationDecision) -> str:
    """Serialize ArbitrationDecision to deterministic JSON."""
    data = {
        "selected_advisor_id": decision.selected_advisor_id,
        "selected_decision": decision.selected_decision,
        "score_breakdown": decision.score_breakdown,
        "merged_rationale": sorted(decision.merged_rationale),  # Stable ordering
        "merged_risks": sorted(decision.merged_risks),  # Stable ordering
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def decision_from_json(json_str: str) -> ArbitrationDecision:
    """Deserialize JSON string to ArbitrationDecision."""
    data = json.loads(json_str)
    return ArbitrationDecision(
        selected_advisor_id=data["selected_advisor_id"],
        selected_decision=data["selected_decision"],
        score_breakdown=data["score_breakdown"],
        merged_rationale=data["merged_rationale"],
        merged_risks=data["merged_risks"],
    )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "AdvisorProposal",
    "ArbitrationInput",
    "ArbitrationDecision",
    "proposal_to_json",
    "proposal_from_json",
    "arbitration_input_to_json",
    "arbitration_input_from_json",
    "decision_to_json",
    "decision_from_json",
]
