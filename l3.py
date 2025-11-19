# FILE: l3.py
"""
Unified L3 Orchestration Layer (v10_9, Refactored) — PURE CONTROL FLOW

This module provides the orchestration logic for the v10_9 agentic
architecture. It enforces strict L3 responsibilities:

    • Phase machine (INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE/FAILED)
    • Graph-based orchestration (DAG) for a single L1 PlanObject
    • Domain execution via L2 route_executor(plan, state)
    • Safety evaluation via L5 SafetyEngine + PolicyEngine + ArbitrationEngine
    • Optional multi-agent QA council (COUNCIL_OF_QA)
    • Self-correction signal computation (META-only)
    • Emitting a final WorkflowState

Non-responsibilities (to preserve layer purity):

    • NO cognition (no planning; PlanObject is taken as input).
    • NO tool/LLM execution (delegated to L2 + providers/*).
    • NO state normalization/budgeting (delegated to L4.StateAdapter).
    • NO safety decisions (delegated to L5).
    • NO direct provider/SDK calls.

L3 depends only on:
    • models.PlanObject / WorkflowState / StatePatch / WorkflowPhase
    • l2.route_executor
    • l4.StateAdapter
    • l5.SafetyEngine, PolicyEngine, ArbitrationEngine
    • agents.COUNCIL_OF_QA, MultiAgentOrchestrator
    • self_correction (for advisory correction surfaces)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Optional, Set

from models import (
    WorkflowState,
    PlanObject,
    ExecutionResult,
    WorkflowPhase,
    StatePatch,
)
from runtime_utils import (
    ValidationError,
    ToolExecutionError,
    WorkflowTimeoutError,
    CostTracker,
    compute_optimization_hint,
    record_event,
)
from l2 import route_executor
from l4 import StateAdapter
from l5 import SafetyEngine, PolicyEngine, ArbitrationEngine
from agents import MultiAgentOrchestrator, COUNCIL_OF_QA
from self_correction import analyze_state_for_correction, to_patch_dict as sc_to_patch_dict


# ============================================================================
# 1. PHASE MACHINE
# ============================================================================

class PhaseMachine:
    """
    Manages allowed workflow phase transitions:

        INIT       → PLANNING
        PLANNING   → EXECUTING / FAILED
        EXECUTING  → REVIEWING / FAILED
        REVIEWING  → COMPLETE / PLANNING / FAILED
        COMPLETE   → (terminal)
        FAILED     → (terminal)

    This is a pure control-flow helper. It does not mutate state or
    perform any execution.
    """

    _ALLOWED: Dict[WorkflowPhase, List[WorkflowPhase]] = {
        WorkflowPhase.INIT: [WorkflowPhase.PLANNING, WorkflowPhase.FAILED],
        WorkflowPhase.PLANNING: [WorkflowPhase.EXECUTING, WorkflowPhase.FAILED],
        WorkflowPhase.EXECUTING: [WorkflowPhase.REVIEWING, WorkflowPhase.FAILED],
        WorkflowPhase.REVIEWING: [
            WorkflowPhase.COMPLETE,
            WorkflowPhase.PLANNING,
            WorkflowPhase.FAILED,
        ],
        WorkflowPhase.COMPLETE: [],
        WorkflowPhase.FAILED: [],
    }

    def __init__(self, initial: WorkflowPhase = WorkflowPhase.INIT) -> None:
        self.phase: WorkflowPhase = initial
        self.history: List[str] = [initial.value]

    def transition(self, target: WorkflowPhase) -> WorkflowPhase:
        """
        Move to the target phase if legal, otherwise raise ValidationError.
        """
        allowed = self._ALLOWED.get(self.phase, [])
        if target not in allowed:
            raise ValidationError(
                f"Illegal phase transition: {self.phase.value} → {target.value}"
            )
        self.phase = target
        self.history.append(target.value)
        return target

    def current(self) -> WorkflowPhase:
        return self.phase

    def current_value(self) -> str:
        return self.phase.value


# ============================================================================
# 2. DAG DEFINITIONS
# ============================================================================

@dataclass
class DAGNode:
    """
    Structural node definition for DAG orchestration.

    run(context) -> context is a deterministic transformation.
    condition(context) -> key is an optional condition used to choose
    conditional edges from this node.

    Fields:
        name:              node identifier (must be unique in DAG)
        run:               pure function from context→context
        condition:         optional function from context→str for
                           conditional routing
        conditional_edges: mapping: condition_key -> [target_node_names]
        retries:           number of retry attempts for run()
        fallback_edge:     optional node name to go to on failure (unused
                           in this reference implementation but present
                           for extensibility)
    """

    name: str
    run: Callable[[Dict[str, Any]], Dict[str, Any]]
    condition: Optional[Callable[[Dict[str, Any]], str]] = None
    conditional_edges: Dict[str, List[str]] = field(default_factory=dict)
    retries: int = 0
    fallback_edge: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValidationError("DAG nodes require a non-empty name.")


@dataclass
class DAG:
    """
    A directed acyclic graph of orchestration steps.

    nodes: mapping of node name -> DAGNode
    edges: default edges (fallback when conditional_edges not used)

    This structure is pure and contains no execution logic.
    """

    nodes: Dict[str, DAGNode]
    edges: Dict[str, List[str]]

    def validate(self) -> None:
        """
        Validate structural integrity (node keys, edge endpoints, etc.).
        """
        if not self.nodes:
            raise ValidationError("DAG must define at least one node.")

        # Names must match keys
        for node_name, node in self.nodes.items():
            if node_name != node.name:
                raise ValidationError(
                    f"Node key '{node_name}' does not match node name '{node.name}'."
                )

        # All edge endpoints must exist
        for source, targets in self.edges.items():
            if source not in self.nodes:
                raise ValidationError(f"Edge source '{source}' is not a defined node.")
            for target in targets:
                if target not in self.nodes:
                    raise ValidationError(
                        f"Edge target '{target}' from '{source}' is not a defined node."
                    )

        # Conditional edges also must be valid
        for node in self.nodes.values():
            for cond_targets in node.conditional_edges.values():
                for target in cond_targets:
                    if target not in self.nodes:
                        raise ValidationError(
                            f"Conditional edge target '{target}' from '{node.name}' "
                            "is not a defined node."
                        )

    def topological_order(self) -> List[str]:
        """
        Return a simple topological ordering of nodes based on edges.

        Used by higher layers (e.g., main_v10_9) when they want to run a
        statically-ordered DAG without invoking DAGExecutor.
        """
        # Kahn-like algorithm using only edges; we ignore conditional edges here.
        in_deg: Dict[str, int] = {name: 0 for name in self.nodes}
        for src, targets in self.edges.items():
            for tgt in targets:
                in_deg[tgt] = in_deg.get(tgt, 0) + 1

        ready = [name for name, deg in in_deg.items() if deg == 0]
        order: List[str] = []

        while ready:
            n = ready.pop(0)
            order.append(n)
            for tgt in self.edges.get(n, []):
                in_deg[tgt] -= 1
                if in_deg[tgt] == 0:
                    ready.append(tgt)

        # Fallback: if cycle, just return all node names as-is.
        if len(order) != len(self.nodes):
            return list(self.nodes.keys())
        return order


class DAGExecutor:
    """
    Deterministic executor for DAG nodes with simple retry logic.

    This engine:
        • Runs nodes when all their parents have completed.
        • For each node, executes it with optional retries.
        • Decides outgoing edges either via conditional_edges (if present
          and condition not None) or via default DAG edges.

    The context dict is the single mutable bag of data; nodes may
    mutate it by returning a new mapping. DAGExecutor itself does not
    know about PlanObjects, state adapters, or phases.
    """

    def run(self, dag: DAG, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        dag.validate()
        context: Dict[str, Any] = dict(initial_context)

        # Build parents map for gating node readiness
        parents: Dict[str, Set[str]] = {name: set() for name in dag.nodes}
        for src, targets in dag.edges.items():
            for tgt in targets:
                parents[tgt].add(src)
        for node in dag.nodes.values():
            for targets in node.conditional_edges.values():
                for tgt in targets:
                    parents[tgt].add(node.name)

        ready: List[str] = sorted(
            name for name, deps in parents.items() if not deps
        )
        executed: Set[str] = set()

        while ready:
            node_name = ready.pop(0)
            if node_name in executed:
                continue

            node = dag.nodes[node_name]
            context = self._execute_with_retries(node, context)
            outgoing = self._determine_edges(dag, node, context)
            executed.add(node_name)
            self._enqueue_targets(outgoing, dag, parents, executed, ready)

        return context

    def _execute_with_retries(self, node: DAGNode, context: Dict[str, Any]) -> Dict[str, Any]:
        attempts = node.retries + 1
        last_exc: Optional[Exception] = None

        for _ in range(attempts):
            try:
                new_context = node.run(dict(context))
                if not isinstance(new_context, dict):
                    raise ValidationError(
                        f"DAG node '{node.name}' did not return a context dict."
                    )
                return new_context
            except Exception as exc:
                last_exc = exc
        raise ToolExecutionError(f"Node '{node.name}' failed after {attempts} attempts: {last_exc}")

    def _determine_edges(self, dag: DAG, node: DAGNode, context: Dict[str, Any]) -> List[str]:
        if node.condition and node.conditional_edges:
            key = node.condition(context)
            return node.conditional_edges.get(key, dag.edges.get(node.name, []))
        return dag.edges.get(node.name, [])

    def _enqueue_targets(
        self,
        targets: List[str],
        dag: DAG,
        parents: Dict[str, Set[str]],
        executed: Set[str],
        ready: List[str],
    ) -> None:
        for tgt in targets:
            if tgt not in dag.nodes:
                raise ValidationError(f"Edge target '{tgt}' is not a defined node in the DAG.")
            if parents.get(tgt, set()).issubset(executed) and tgt not in ready:
                ready.append(tgt)
        ready.sort()


# ============================================================================
# 3. GLOBAL ORCHESTRATOR
# ============================================================================

@dataclass
class Orchestrator:
    """
    Central orchestrator for v10_9 agentic execution.

    Given:
        • a PlanObject from L1
        • an initial state dict (pre-L4)

    It will:
        1. Initialize L4.StateAdapter with the initial state.
        2. Use a PhaseMachine to move through:
            INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE / FAILED
        3. Build and run a DAG:
              plan_node → execute_node → safety_node
                         → qa_council_node? → finalize_node
        4. Call L2 route_executor to execute the plan.
        5. Call L5 SafetyEngine + PolicyEngine + ArbitrationEngine for safety.
        6. Optionally call MultiAgent QA council if mode == "qa".
        7. Compute self-correction signals (meta-only).
        8. Return a WorkflowState with final state and phase metadata.

    No tools/LLMs are called here, and no state mutation logic is
    embedded; all state updates are delegated to L4.StateAdapter.
    """

    state_adapter: StateAdapter = field(default_factory=StateAdapter)
    safety_engine: SafetyEngine = field(default_factory=SafetyEngine)
    policy_engine: PolicyEngine = field(default_factory=PolicyEngine)
    arbitration_engine: ArbitrationEngine = field(default_factory=ArbitrationEngine)

    def _apply_execution_to_state(self, mode: str, result: ExecutionResult[Any]) -> None:
        """
        Map an L2 ExecutionResult payload into L4 state via StatePatch.

        The shape is intentionally aligned with the simulation harness
        and downstream tooling (e.g., "draft_result", "qa_result").
        """
        payload = result.payload
        norm_mode = mode.lower()

        if hasattr(payload, "to_dict"):
            p = payload.to_dict()  # type: ignore[assignment]
        else:
            p = dict(payload)

        if norm_mode == "strategy":
            # store strategy result
            patch_value = {
                "branches": p.get("branches", []),
                "selected_strategy": p.get("selected_branch"),
                "decision": {
                    "aggregated_decision": p.get("aggregated_decision"),
                    "aggregated_confidence": p.get("aggregated_confidence"),
                    "aggregated_rationale": p.get("aggregated_rationale"),
                    "complexity": p.get("complexity"),
                },
            }
            self.state_adapter.apply_patch(StatePatch(key="strategy_result", value=patch_value))

        elif norm_mode == "rag":
            self.state_adapter.apply_patch(StatePatch(key="rag_result", value=p))

        elif norm_mode == "drafting":
            self.state_adapter.apply_patch(StatePatch(key="draft_result", value=p))

        elif norm_mode == "bullets":
            self.state_adapter.apply_patch(StatePatch(key="bullet_result", value=p))

        elif norm_mode == "qa":
            if "qa_report" in p:
                report_dict = p["qa_report"]
                patch_value = {"report": report_dict}
            else:
                patch_value = {"report": p}
            self.state_adapter.apply_patch(StatePatch(key="qa_result", value=patch_value))

        elif norm_mode == "safety":
            if "safety_report" in p:
                report_dict = p["safety_report"]
                patch_value = {
                    "report": report_dict,
                    "sanitized": p.get("sanitized_content", ""),
                }
            else:
                patch_value = {"report": p}
            self.state_adapter.apply_patch(StatePatch(key="safety_result", value=patch_value))

        elif norm_mode == "prompt_engineering":
            self.state_adapter.apply_patch(StatePatch(key="prompt_engineering_result", value=p))

        elif norm_mode == "hil":
            self.state_adapter.apply_patch(StatePatch(key="hil_result", value=p))

        elif norm_mode == "meta_learning":
            self.state_adapter.apply_patch(StatePatch(key="meta_learning_result", value=p))

        else:
            # Unknown modes are stored verbatim under "last_execution"
            self.state_adapter.apply_patch(
                StatePatch(key="last_execution", value={"mode": norm_mode, "payload": p})
            )

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def run(self, plan: PlanObject, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Execute full L3 orchestration for a single L1 PlanObject.

        This is a synchronous API; higher layers may wrap it with
        asyncio as needed. Internally, it uses asyncio.run to call
        async L2 route_executor when needed.

        All state mutations are performed via L4.StateAdapter; the
        returned WorkflowState contains the final state snapshot.
        """
        machine = PhaseMachine()
        cost_tracker = CostTracker()

        workflow_id = str(initial_state.get("workflow_id") or "workflow_v10_9")

        for key, value in (initial_state or {}).items():
            self.state_adapter.apply_patch(StatePatch(key=key, value=value))

        # Phase: INIT → PLANNING
        machine.transition(WorkflowPhase.PLANNING)
        mode = str(plan.get("mode", "")).lower()
        if not mode:
            raise ValidationError("PlanObject missing 'mode' field.")

        # Node: plan_node attaches plan + state
        def plan_node(context: Dict[str, Any]) -> Dict[str, Any]:
            context["plan"] = plan
            context["state"] = self.state_adapter.state
            context["workflow_phase"] = machine.current_value()
            context["workflow_id"] = workflow_id
            return context

        async def _execute_async(p: PlanObject, s: Dict[str, Any]) -> ExecutionResult[Any]:
            return await route_executor(p, s)

        def execute_node(context: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal cost_tracker
            cost_tracker.start_span("execution")
            current_state = self.state_adapter.state

            try:
                exec_result: ExecutionResult[Any] = asyncio.run(_execute_async(plan, current_state))
            except WorkflowTimeoutError as exc:
                raise ToolExecutionError(f"L2 execution timed out: {exc}") from exc

            cost_tracker.end_span("execution")

            context["execution_result"] = exec_result
            self._apply_execution_to_state(mode, exec_result)
            context["state"] = self.state_adapter.state

            machine.transition(WorkflowPhase.EXECUTING)
            context["workflow_phase"] = machine.current_value()
            return context

        def safety_node(context: Dict[str, Any]) -> Dict[str, Any]:
            state = context.get("state", self.state_adapter.state)
            safety_report = self.safety_engine.evaluate_content(state, plan)
            policy_decision = self.policy_engine.review(safety_report)
            arbitration_action = self.arbitration_engine.decide(policy_decision, safety_report)

            context["safety_report"] = safety_report
            context["policy_decision"] = policy_decision
            context["arbitration_action"] = arbitration_action

            self.state_adapter.apply_patch(
                StatePatch(key="safety_result", value={"report_l5": safety_report})
            )
            self.state_adapter.apply_patch(StatePatch(key="arbitration", value=arbitration_action))
            context["state"] = self.state_adapter.state

            machine.transition(WorkflowPhase.REVIEWING)
            context["workflow_phase"] = machine.current_value()
            return context

        def safety_condition(context: Dict[str, Any]) -> str:
            action = (context.get("arbitration_action") or {}).get("action", "proceed")
            if action == "halt":
                return "halt"
            return "proceed"

        def qa_council_node(context: Dict[str, Any]) -> Dict[str, Any]:
            if mode != "qa":
                return context
            state = context.get("state", self.state_adapter.state)
            ma_orch = MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=self.state_adapter)
            council_state = ma_orch.dispatch_for_qa(state, plan)
            for key, value in council_state.items():
                self.state_adapter.apply_patch(StatePatch(key=key, value=value))
            context["state"] = self.state_adapter.state
            return context

        def finalize_node(context: Dict[str, Any]) -> Dict[str, Any]:
            spans = cost_tracker.snapshot()
            optimization = compute_optimization_hint(spans.get("spans", []))

            telemetry_block = {
                "spans": spans.get("spans", []),
                "optimization": optimization,
            }
            self.state_adapter.apply_patch(StatePatch(key="telemetry", value=telemetry_block))

            sc_rec = analyze_state_for_correction(self.state_adapter.state)
            sc_patch = sc_to_patch_dict(sc_rec)
            self.state_adapter.apply_patch(StatePatch(key="self_correction", value=sc_patch["self_correction"]))

            context["state"] = self.state_adapter.state

            record_event(
                "orchestrator_cycle",
                {
                    "plan_mode": mode,
                    "workflow_id": workflow_id,
                    "spans": spans,
                    "optimization": optimization,
                    "self_correction": sc_patch["self_correction"],
                },
            )

            machine.transition(WorkflowPhase.COMPLETE)
            context["workflow_phase"] = machine.current_value()
            return context

        nodes: Dict[str, DAGNode] = {
            "plan_node": DAGNode(name="plan_node", run=plan_node),
            "execute_node": DAGNode(name="execute_node", run=execute_node),
            "safety_node": DAGNode(
                name="safety_node",
                run=safety_node,
                condition=safety_condition,
                conditional_edges={
                    "proceed": ["qa_council_node", "finalize_node"],
                    "halt": ["finalize_node"],
                },
            ),
            "qa_council_node": DAGNode(name="qa_council_node", run=qa_council_node),
            "finalize_node": DAGNode(name="finalize_node", run=finalize_node),
        }

        edges: Dict[str, List[str]] = {
            "plan_node": ["execute_node"],
            "execute_node": ["safety_node"],
            "safety_node": [],
            "qa_council_node": ["finalize_node"],
            "finalize_node": [],
        }

        dag = DAG(nodes=nodes, edges=edges)
        executor = DAGExecutor()

        initial_context = {
            "plan": plan,
            "state": self.state_adapter.state,
            "workflow_phase": machine.current_value(),
            "workflow_id": workflow_id,
        }

        try:
            final_context = executor.run(dag, initial_context)
        except ToolExecutionError:
            machine.transition(WorkflowPhase.FAILED)
            final_state = self.state_adapter.state
            phase_metadata = {"history": list(machine.history)}
            return WorkflowState(
                workflow_id=workflow_id,
                phase=machine.current_value(),
                nodes={},
                state=final_state,
                phase_metadata=phase_metadata,
            )

        final_state = self.state_adapter.state
        phase_metadata = {"history": list(machine.history)}

        return WorkflowState(
            workflow_id=workflow_id,
            phase=machine.current_value(),
            nodes={},
            state=final_state,
            phase_metadata=phase_metadata,
        )
