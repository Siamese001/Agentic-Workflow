"""G1 (gap): Runtime Behavior Plane — runtime event graph infrastructure.

This module provides the data structures and collectors for the RUNTIME side of
the ADG mental model (nodes 7-11 in the six-plane architecture). It captures
events that cannot be known statically — agent observe/reason/act/evaluate/learn
cycles, healer/validator loop executions, meta-learning feedback, and HITL decisions.

Architecture:
  Static ADG (this package's core)  → code catalog: modules, imports, edges
  Runtime Graph (this module)        → execution trace: events, outcomes, decisions

  The RuntimeGraph is complementary to the ScanResult — it captures WHAT HAPPENED
  at execution time, while ScanResult captures WHAT IS DECLARED in the code.

Data model:
  RuntimeEvent    — a single atomic runtime observation (agent started, healer ran, etc.)
  RuntimeEdge     — a directed edge between two runtime entities
  RuntimeGraph    — collection of RuntimeEdges + RuntimeEvents
  RuntimeGraphCollector — interface for agent code to emit events
  AgentLoopRecorder     — records the 5-phase agent loop (observe→reason→act→evaluate→learn)
  HealerLoopRecorder    — records healer→validator→learning events

Usage::

    from agentic_core.adg.runtime.event_graph import AgentLoopRecorder, RuntimeGraph

    graph = RuntimeGraph()
    recorder = AgentLoopRecorder(graph, agent_id="CampaignPlannerAgent", run_id="run-001")
    recorder.observe(input_hash="abc123")
    recorder.reason(strategy="archetype_routing")
    recorder.act(tool="SovereignLLMGateway", output_hash="def456")
    recorder.evaluate(outcome="SUCCESS", confidence=0.92)
    recorder.learn(delta_applied=True, strategy_weight_delta=0.05)
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuntimePhase(str, Enum):
    """The five phases of an agent execution loop."""

    OBSERVE = "observe"
    REASON = "reason"
    ACT = "act"
    EVALUATE = "evaluate"
    LEARN = "learn"


class HealerPhase(str, Enum):
    """The phases of a healer/validator loop."""

    DETECT = "detect"
    PLAN = "plan"
    HEAL = "heal"
    VALIDATE = "validate"
    COMMIT = "commit"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class RuntimeEvent:
    """A single atomic observation from a running agent or orchestrator.

    Attributes:
        event_type:  Phase or action name (e.g. ``observe``, ``heal``, ``escalate``).
        agent_id:    Canonical agent class name that emitted this event.
        run_id:      Execution run identifier (UUID or deterministic hash).
        timestamp:   Unix epoch seconds at emission time.
        payload:     Arbitrary structured payload (kept shallow for serialization).
        phase:       Optional phase enum if this is part of a structured loop.
    """

    event_type: str
    agent_id: str
    run_id: str
    timestamp: float
    payload: dict[str, Any] = field(default_factory=dict)
    phase: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "phase": self.phase,
            "payload": self.payload,
        }


@dataclass(frozen=True)
class RuntimeEdge:
    """A directed edge in the runtime graph.

    Attributes:
        from_entity:   Source entity (e.g. agent class name).
        relation_type: Relation type (matches ADG schema RelationType).
        to_entity:     Target entity.
        run_id:        Execution run that produced this edge.
        timestamp:     When the edge was produced.
        metadata:      Additional structured metadata.
    """

    from_entity: str
    relation_type: str
    to_entity: str
    run_id: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_entity": self.from_entity,
            "relation_type": self.relation_type,
            "to_entity": self.to_entity,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class RuntimeGraph:
    """Collection of runtime edges and events produced during execution.

    This is the runtime counterpart to ScanResult. While ScanResult is
    built statically from AST analysis, RuntimeGraph is populated by
    agent execution via RuntimeGraphCollector subclasses.

    Attributes:
        run_id:  Unique identifier for this execution session.
        edges:   All directed runtime edges observed.
        events:  All atomic runtime events recorded.
    """

    run_id: str = field(default_factory=lambda: _make_run_id())
    edges: list[RuntimeEdge] = field(default_factory=list)
    events: list[RuntimeEvent] = field(default_factory=list)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def event_count(self) -> int:
        return len(self.events)

    def edges_by_relation(self) -> dict[str, list[RuntimeEdge]]:
        """Group edges by relation_type."""
        groups: dict[str, list[RuntimeEdge]] = {}
        for edge in self.edges:
            groups.setdefault(edge.relation_type, []).append(edge)
        return groups

    def events_by_phase(self) -> dict[str, list[RuntimeEvent]]:
        """Group events by phase."""
        groups: dict[str, list[RuntimeEvent]] = {}
        for event in self.events:
            key = event.phase or event.event_type
            groups.setdefault(key, []).append(event)
        return groups

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "edge_count": self.edge_count,
            "event_count": self.event_count,
            "edges": [e.to_dict() for e in self.edges],
            "events": [e.to_dict() for e in self.events],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class RuntimeGraphCollector:
    """Base interface for emitting runtime edges and events into a RuntimeGraph.

    Subclass this and pass the shared RuntimeGraph to coordinate across
    multiple agents in the same execution session.
    """

    def __init__(self, graph: RuntimeGraph, agent_id: str, run_id: str | None = None) -> None:
        self._graph = graph
        self._agent_id = agent_id
        self._run_id = run_id or graph.run_id

    def _emit_event(
        self,
        event_type: str,
        phase: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self._graph.events.append(
            RuntimeEvent(
                event_type=event_type,
                agent_id=self._agent_id,
                run_id=self._run_id,
                timestamp=time.time(),
                payload=payload or {},
                phase=phase,
            )
        )

    def _emit_edge(
        self,
        relation_type: str,
        to_entity: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._graph.edges.append(
            RuntimeEdge(
                from_entity=self._agent_id,
                relation_type=relation_type,
                to_entity=to_entity,
                run_id=self._run_id,
                timestamp=time.time(),
                metadata=metadata or {},
            )
        )


class AgentLoopRecorder(RuntimeGraphCollector):
    """Records the 5-phase agent execution loop: observe→reason→act→evaluate→learn.

    Each phase call emits a RuntimeEvent and, where applicable, a RuntimeEdge
    to the entity being interacted with (tool invoked, decision made, etc.).

    Example::

        graph = RuntimeGraph()
        rec = AgentLoopRecorder(graph, agent_id="CampaignPlannerAgent", run_id="r1")
        rec.observe(input_hash="sha256:abc")
        rec.reason(strategy="archetype_routing")
        rec.act(tool="SovereignLLMGateway", output_hash="sha256:def")
        rec.evaluate(outcome="SUCCESS", confidence=0.92)
        rec.learn(delta_applied=True, strategy_weight_delta=0.05)
    """

    def observe(self, input_hash: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "observe",
            phase=RuntimePhase.OBSERVE,
            payload={"input_hash": input_hash, **kwargs},
        )

    def reason(self, strategy: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "reason",
            phase=RuntimePhase.REASON,
            payload={"strategy": strategy, **kwargs},
        )

    def act(self, tool: str = "", output_hash: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "act",
            phase=RuntimePhase.ACT,
            payload={"tool": tool, "output_hash": output_hash, **kwargs},
        )
        if tool:
            self._emit_edge("invokes_tool", tool, metadata={"output_hash": output_hash})

    def evaluate(self, outcome: str = "", confidence: float = 0.0, **kwargs: Any) -> None:
        self._emit_event(
            "evaluate",
            phase=RuntimePhase.EVALUATE,
            payload={"outcome": outcome, "confidence": confidence, **kwargs},
        )

    def learn(self, delta_applied: bool = False, strategy_weight_delta: float = 0.0, **kwargs: Any) -> None:
        self._emit_event(
            "learn",
            phase=RuntimePhase.LEARN,
            payload={
                "delta_applied": delta_applied,
                "strategy_weight_delta": strategy_weight_delta,
                **kwargs,
            },
        )
        if delta_applied:
            self._emit_edge(
                "learns_from_decision",
                f"{self._agent_id}.meta_learning",
                metadata={"strategy_weight_delta": strategy_weight_delta},
            )


class HealerLoopRecorder(RuntimeGraphCollector):
    """Records the healer/validator loop: detect→plan→heal→validate→commit|escalate.

    Each phase call emits RuntimeEvents and RuntimeEdges into the shared graph,
    building the runtime healer/validator relationship graph described in Gap 1.

    Example::

        graph = RuntimeGraph()
        rec = HealerLoopRecorder(graph, agent_id="LicHealingOrchestrator", run_id="r1")
        rec.detect(violation_type="UWG_BYPASS", violation_id="v001")
        rec.plan(strategy="rewrite_to_uwg")
        rec.heal(target_module="apps_lic/reasoning/TargetAgent.py")
        rec.validate(validator="ResolutionValidator", passed=True)
        rec.commit(mutation_hash="sha256:abc")
    """

    def detect(self, violation_type: str = "", violation_id: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "detect",
            phase=HealerPhase.DETECT,
            payload={"violation_type": violation_type, "violation_id": violation_id, **kwargs},
        )
        if violation_type:
            self._emit_edge("heals", f"violation:{violation_type}", metadata={"violation_id": violation_id})

    def plan(self, strategy: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "plan",
            phase=HealerPhase.PLAN,
            payload={"strategy": strategy, **kwargs},
        )

    def heal(self, target_module: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "heal",
            phase=HealerPhase.HEAL,
            payload={"target_module": target_module, **kwargs},
        )
        if target_module:
            self._emit_edge("orchestrates_healing", target_module)

    def validate(self, validator: str = "", passed: bool = False, **kwargs: Any) -> None:
        self._emit_event(
            "validate",
            phase=HealerPhase.VALIDATE,
            payload={"validator": validator, "passed": passed, **kwargs},
        )
        if validator:
            self._emit_edge("dispatches_to", validator, metadata={"passed": passed})

    def commit(self, mutation_hash: str = "", **kwargs: Any) -> None:
        self._emit_event(
            "commit",
            phase=HealerPhase.COMMIT,
            payload={"mutation_hash": mutation_hash, **kwargs},
        )

    def escalate(self, reason: str = "", confidence: float = 0.0, **kwargs: Any) -> None:
        self._emit_event(
            "escalate",
            phase=HealerPhase.ESCALATE,
            payload={"reason": reason, "confidence": confidence, **kwargs},
        )
        self._emit_edge(
            "escalates_to_human",
            "HITL::checkpoint",
            metadata={"reason": reason, "confidence": confidence},
        )


def _make_run_id() -> str:
    """Generate a deterministic-ish run ID from current time."""
    raw = str(time.time()).encode()
    return "run-" + hashlib.sha256(raw).hexdigest()[:12]


__all__ = [
    "RuntimePhase",
    "HealerPhase",
    "RuntimeEvent",
    "RuntimeEdge",
    "RuntimeGraph",
    "RuntimeGraphCollector",
    "AgentLoopRecorder",
    "HealerLoopRecorder",
]
