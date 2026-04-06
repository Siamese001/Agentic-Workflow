"""
Multi-Agent Arbitration Contract

Defines immutable data structures for multi-agent arbitration system.
Provides deterministic JSON serialization for advisor proposals and decisions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

@dataclass(frozen=True)
class AdvisorProposal:
    """Immutable proposal from an advisor agent."""

    advisor_id: str
    decision: str
    confidence: int
    rationale: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate proposal constraints and normalize list ordering."""
        if not self.advisor_id:
            raise ValueError("advisor_id cannot be empty")
        if not self.decision:
            raise ValueError("decision cannot be empty")
        if not 0 <= self.confidence <= 100:
            raise ValueError("confidence must be between 0 and 100")
        if any(not r for r in self.rationale):
            raise ValueError("rationale items cannot be empty")
        if any(not r for r in self.risks):
            raise ValueError("risk items cannot be empty")
        if any(not a for a in self.artifacts):
            raise ValueError("artifact items cannot be empty")
        object.__setattr__(self, "rationale", sorted(self.rationale))
        object.__setattr__(self, "risks", sorted(self.risks))
        object.__setattr__(self, "artifacts", sorted(self.artifacts))


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
        """Validate decision constraints and normalize list ordering."""
        if not self.selected_advisor_id:
            raise ValueError("selected_advisor_id cannot be empty")
        if not self.selected_decision:
            raise ValueError("selected_decision cannot be empty")
        object.__setattr__(self, "merged_rationale", sorted(self.merged_rationale))
        object.__setattr__(self, "merged_risks", sorted(self.merged_risks))


def proposal_to_json(proposal: AdvisorProposal) -> str:
    """Serialize AdvisorProposal to deterministic JSON."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "proposal_to_json", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "proposal_to_json", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "proposal_to_json")
    data = {
        "advisor_id": proposal.advisor_id,
        "decision": proposal.decision,
        "confidence": proposal.confidence,
        "rationale": sorted(proposal.rationale),
        "risks": sorted(proposal.risks),
        "artifacts": sorted(proposal.artifacts),
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
    return ArbitrationInput(task_id=data["task_id"], task_kind=data["task_kind"], proposals=proposals)


def decision_to_json(decision: ArbitrationDecision) -> str:
    """Serialize ArbitrationDecision to deterministic JSON."""
    data = {
        "selected_advisor_id": decision.selected_advisor_id,
        "selected_decision": decision.selected_decision,
        "score_breakdown": decision.score_breakdown,
        "merged_rationale": sorted(decision.merged_rationale),
        "merged_risks": sorted(decision.merged_risks),
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
