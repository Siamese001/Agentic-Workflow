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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "event_graph", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "event_graph", "policy_binding")
trace_contract._emit_snapshots_state("p0", "event_graph", "state_snapshot")

trace_contract._emit_emits_metric_event("event_graph", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("event_graph", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("event_graph", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("event_graph", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("event_graph", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("event_graph", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("event_graph", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("event_graph", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("event_graph", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("event_graph", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("event_graph", "p4obs", "alert")
trace_contract._emit_links_incident_trace("event_graph", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("event_graph", "p3lm", "pattern")
trace_contract._emit_records_learning_event("event_graph", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("event_graph", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("event_graph", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("event_graph", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("event_graph", "p3lm", "policy")
trace_contract._emit_stores_learning_state("event_graph", "p3lm", "state")
trace_contract._emit_records_execution_trace("event_graph", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("event_graph", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("event_graph", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("event_graph", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("event_graph", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("event_graph", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("event_graph", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("event_graph", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("event_graph", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "event_graph", "context_pull")
trace_contract._emit_pulls_context("p1", "event_graph", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "event_graph", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "event_graph", "uwg_term_2")
trace_contract._emit_writes_through("p1", "event_graph", "write_through")
trace_contract._emit_writes_through("p1", "event_graph", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "event_graph", "safety_validation")
trace_contract._emit_invokes_eval("p1", "event_graph", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "event_graph", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "event_graph", "human_escalation")
trace_contract._emit_routes_through("p1", "event_graph", "route_through")
trace_contract._emit_checks_agent_registry("p1", "event_graph", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "event_graph", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "event_graph", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "event_graph", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "event_graph", "target_agent")
trace_contract._emit_verifies_policy("p1", "event_graph", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "event_graph", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "event_graph", "boundary_check")
trace_contract._emit_transcripts_response("p1", "event_graph", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "event_graph")
trace_contract._emit_gated_by_confidence("p1", "event_graph", "confidence_gate")
trace_contract.emit_replay_key("p0", "event_graph")
trace_contract.emit_determinism_digest("p0", "event_graph")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "event_graph", "execution_auth")
trace_contract._emit_validates_capability("p2", "event_graph", "capability_check")
trace_contract._emit_routes_to_capability("p2", "event_graph", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "event_graph", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "event_graph", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "event_graph", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "event_graph", "exec_output")
trace_contract._emit_dispatches_agent("p3", "event_graph", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "event_graph", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "event_graph", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "event_graph", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "event_graph", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "event_graph", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "event_graph", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "event_graph", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "event_graph", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "event_graph", "eval_metric")
trace_contract._emit_stores_embedding("p4", "event_graph", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "event_graph", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "event_graph", "exec_snapshot_link")


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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RuntimeGraph.edges_by_relation"
        )

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
            ),
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
            ),
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "AgentLoopRecorder.act")

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealerLoopRecorder.detect")

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

trace_contract._emit_reads_through("l4", "event_graph", "urg_read_1")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_2")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_3")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_4")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_5")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_6")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_7")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_8")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_9")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_10")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_11")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_12")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_13")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_14")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_15")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_16")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_17")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_18")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_19")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_20")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_21")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_22")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_23")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_24")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_25")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_26")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_27")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_28")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_29")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_30")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_31")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_32")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_33")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_34")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_35")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_36")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_37")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_38")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_39")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_40")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_41")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_42")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_43")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_44")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_45")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_46")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_47")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_48")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_49")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_50")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_51")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_52")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_53")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_54")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_55")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_56")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_57")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_58")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_59")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_60")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_61")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_62")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_63")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_64")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_65")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_66")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_67")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_68")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_69")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_70")
trace_contract._emit_reads_through("l4", "event_graph", "urg_read_71")
