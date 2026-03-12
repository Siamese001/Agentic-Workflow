"""G4 (gap): HITL Graph — Human-in-the-Loop escalation and decision graph.

Models the confidence-threshold gating path that routes low-confidence agent
decisions to a human reviewer, then feeds the human decision back into the
meta-learning system.

Architecture node flow (Gap 4):
  Agent outcome
    → HealingConfidenceScorer (confidence gate)
    → [if confidence < threshold] → HITLCheckpoint (human review queue)
    → HumanDecision (approve / reject / override)
    → MetaLearning feedback edge (learns_from_decision)

Static detection:
  The `_HITLVisitor` in static_scanner.py detects statically-declared
  `gated_by_confidence` and `escalates_to_human` edges from code.

Runtime tracking:
  HITLRuntimeRecorder emits RuntimeEdges into a shared RuntimeGraph for
  each checkpoint, human decision, and learning feedback event.

Data model:
  HITLCheckpoint     — a queued item awaiting human review
  HumanDecision      — the outcome of a human review (approve/reject/override)
  HITLGraph          — collection of checkpoints and decisions

Usage::

    from agentic_core.adg.runtime.hitl_graph import HITLGraph, HITLRuntimeRecorder
    from agentic_core.adg.runtime.event_graph import RuntimeGraph

    rt_graph = RuntimeGraph()
    hitl = HITLGraph()
    recorder = HITLRuntimeRecorder(rt_graph, hitl, agent_id="LicHealingOrchestrator")
    recorder.checkpoint(violation_id="v001", confidence=0.28, context={"strategy": "rewrite"})
    # ... human reviews ...
    recorder.decide(checkpoint_id="cp-001", decision="approve", reviewer="human:alice")
    recorder.learn(checkpoint_id="cp-001", weight_delta=0.1)
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.adg.runtime.event_graph import RuntimeGraph, RuntimeGraphCollector


class HITLDecisionType(str, Enum):
    """Possible human review decisions."""

    APPROVE = "approve"
    REJECT = "reject"
    OVERRIDE = "override"
    DEFER = "defer"


@dataclass
class HITLCheckpoint:
    """A single item queued for human review.

    Attributes:
        checkpoint_id:  Unique identifier for this checkpoint.
        agent_id:       Agent class that generated the checkpoint.
        run_id:         Execution run that produced this item.
        violation_id:   Violation or decision being reviewed.
        confidence:     Agent's confidence score that triggered escalation.
        context:        Arbitrary structured context for the reviewer.
        created_at:     Unix epoch timestamp when queued.
        resolved:       Whether a human decision has been recorded.
    """

    checkpoint_id: str
    agent_id: str
    run_id: str
    violation_id: str
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    resolved: bool = False


@dataclass(frozen=True)
class HumanDecision:
    """The outcome of a human reviewer acting on a HITLCheckpoint.

    Attributes:
        checkpoint_id:  ID of the checkpoint being resolved.
        decision:       Human's decision (approve/reject/override/defer).
        reviewer:       Identifier of the human reviewer.
        rationale:      Optional free-text rationale.
        decided_at:     Unix epoch timestamp of the decision.
        override_value: If decision == override, the corrected value.
    """

    checkpoint_id: str
    decision: HITLDecisionType
    reviewer: str
    rationale: str = ""
    decided_at: float = field(default_factory=time.time)
    override_value: Any = None


@dataclass
class HITLGraph:
    """Collection of HITL checkpoints and human decisions.

    This is the runtime-populated HITL subgraph. It is complementary to the
    static `gated_by_confidence` and `escalates_to_human` edges produced by
    `_HITLVisitor` in static_scanner.py.

    Attributes:
        checkpoints: All checkpoints queued for human review.
        decisions:   All human decisions recorded.
    """

    checkpoints: list[HITLCheckpoint] = field(default_factory=list)
    decisions: list[HumanDecision] = field(default_factory=list)

    @property
    def pending_count(self) -> int:
        return sum(1 for cp in self.checkpoints if not cp.resolved)

    @property
    def resolved_count(self) -> int:
        return sum(1 for cp in self.checkpoints if cp.resolved)

    def checkpoint_by_id(self, checkpoint_id: str) -> HITLCheckpoint | None:
        for cp in self.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                return cp
        return None

    def decisions_for(self, checkpoint_id: str) -> list[HumanDecision]:
        return [d for d in self.decisions if d.checkpoint_id == checkpoint_id]

    def decision_distribution(self) -> dict[str, int]:
        """Count decisions by type."""
        dist: dict[str, int] = {}
        for d in self.decisions:
            dist[d.decision] = dist.get(d.decision, 0) + 1
        return dist


class HITLRuntimeRecorder(RuntimeGraphCollector):
    """Records HITL escalations, human decisions, and learning feedback.

    Emits both into a shared RuntimeGraph (as RuntimeEdges/Events) and
    into a HITLGraph (as typed domain objects for downstream analysis).

    Args:
        rt_graph:  Shared RuntimeGraph for this execution session.
        hitl_graph: HITLGraph to record typed checkpoints/decisions into.
        agent_id:  Agent class name emitting HITL events.
        run_id:    Execution run identifier.
    """

    def __init__(
        self,
        rt_graph: RuntimeGraph,
        hitl_graph: HITLGraph,
        agent_id: str,
        run_id: str | None = None,
    ) -> None:
        super().__init__(rt_graph, agent_id, run_id)
        self._hitl = hitl_graph

    def checkpoint(
        self,
        violation_id: str,
        confidence: float,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Queue a new HITL checkpoint for human review.

        Returns the generated checkpoint_id.
        """
        cp_id = _make_checkpoint_id(self._agent_id, violation_id)
        cp = HITLCheckpoint(
            checkpoint_id=cp_id,
            agent_id=self._agent_id,
            run_id=self._run_id,
            violation_id=violation_id,
            confidence=confidence,
            context=context or {},
        )
        self._hitl.checkpoints.append(cp)
        self._emit_event(
            "hitl_checkpoint",
            phase="escalate",
            payload={
                "checkpoint_id": cp_id,
                "violation_id": violation_id,
                "confidence": confidence,
            },
        )
        self._emit_edge(
            "escalates_to_human",
            f"HITL::Checkpoint::{cp_id}",
            metadata={"confidence": confidence, "violation_id": violation_id},
        )
        return cp_id

    def decide(
        self,
        checkpoint_id: str,
        decision: str,
        reviewer: str,
        rationale: str = "",
        override_value: Any = None,
    ) -> None:
        """Record a human decision on a queued checkpoint."""
        decision_type = HITLDecisionType(decision)
        d = HumanDecision(
            checkpoint_id=checkpoint_id,
            decision=decision_type,
            reviewer=reviewer,
            rationale=rationale,
            override_value=override_value,
        )
        self._hitl.decisions.append(d)
        cp = self._hitl.checkpoint_by_id(checkpoint_id)
        if cp is not None:
            cp.resolved = True
        self._emit_event(
            "human_decision",
            phase="decide",
            payload={
                "checkpoint_id": checkpoint_id,
                "decision": decision,
                "reviewer": reviewer,
            },
        )
        self._emit_edge(
            "awaits_approval",
            reviewer,
            metadata={"checkpoint_id": checkpoint_id, "decision": decision},
        )

    def learn(self, checkpoint_id: str, weight_delta: float = 0.0) -> None:
        """Feed human decision back into meta-learning system."""
        self._emit_event(
            "hitl_learning",
            phase="learn",
            payload={"checkpoint_id": checkpoint_id, "weight_delta": weight_delta},
        )
        self._emit_edge(
            "learns_from_decision",
            f"HITL::Decision::{checkpoint_id}",
            metadata={"weight_delta": weight_delta},
        )


def _make_checkpoint_id(agent_id: str, violation_id: str) -> str:
    """Generate a deterministic checkpoint ID."""
    raw = f"{agent_id}:{violation_id}:{time.time()}".encode()
    return "cp-" + hashlib.sha256(raw).hexdigest()[:12]


__all__ = [
    "HITLDecisionType",
    "HITLCheckpoint",
    "HumanDecision",
    "HITLGraph",
    "HITLRuntimeRecorder",
]
