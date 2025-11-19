# FILE: l3.py
"""
Unified L3 Orchestration Layer (v10_9) — ENTERPRISE REFACTOR

This file provides the complete orchestration logic for the v10_9
agentic architecture. It fully restores orchestration capabilities
(DAGs, multi-agent QA council, safety arbitration) while preserving
strict L1–L5 separation:

    • L1: planning only (PlanObject).
    • L2: execution only (ExecutionResult).
    • L3: control flow / orchestration only.
    • L4: state management only (StateAdapter).
    • L5: safety & policy only (SafetyEngine, PolicyEngine, ArbitrationEngine).

Responsibilities:
    • Phase machine (INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE/FAILED)
    • Graph-based orchestration (DAG) for a single L1 PlanObject
    • Domain execution via L2 route_executor(plan, state)
    • Safety evaluation via L5 SafetyEngine + PolicyEngine + ArbitrationEngine
    • Optional multi-agent QA council when plan.mode == "qa"
    • Emitting a final WorkflowState

Non-responsibilities:
    • NO cognition (L1).
    • NO tool/LLM execution (L2).
    • NO state normalization/budgeting (L4).
    • NO safety decisions (L5).
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


# =============================================================================
# 1. PHASE MACHINE
# =============================================================================


class PhaseMachine:
    """
    Manages allowed workflow phase transitions:

        INIT       → PLANNING
        PLANNING   → EXECUTING / FAILED
        EXECUTING  → REVIEWING / FAILED
        REVIEWING  → COMPLETE / PLANNING / FAILED
        COMPLETE   → (terminal)
        FAILED     → (terminal)
    """

    _ALLOWED = {
        WorkflowPhase.INIT.value: [WorkflowPhase.PLANNING.value, WorkflowPhase.FAILED.value],
        WorkflowPhase.PLANNING.value: [WorkflowPhase.EXECUTING.value, WorkflowPhase.FAILED.value],
        WorkflowPhase.EXECUTING.value: [WorkflowPhase.REVIEWING.value, WorkflowPhase.FAILED.value],
        WorkflowPhase.REVIEWING.value: [
            WorkflowPhase.COMPLETE.value,
            WorkflowPhase.PLANNING.value,
            WorkflowPhase.FAILED.value,
        ],
        WorkflowPhase.COMPLETE.value: [],
        WorkflowPhase.FAILED.value: [],
    }

    def __init__(self, initial: str = WorkflowPhase.INIT.value) -> None:
        self.phase: str = initial
        self.history: List[str] = [initial]

    def transition(self, target: str) -> str:
        target = target.lower()
        if target not in self._ALLOWED.get(self.phase, []):
            raise ValidationError(f"Illegal phase transition: {self.phase} → {target}")
        self.phase = target
        self.history.append(target)
        return target

    def current(self) -> str:
        return self.phase


# =============================================================================
# 2. DAG DEFINITIONS
# =============================================================================


@dataclass
class DAGNode:
    """
    Structural node definition for DAG orchestration.

    run(context) -> context is a deterministic transformation.
    condition(context) -> key is an optional condition used to choose
    conditional edges from this node.
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
    """

    nodes: Dict[str, DAGNode]
    edges: Dict[str, List[str]]

    def validate(self) -> None:
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
        Return a deterministic topological ordering of the DAG nodes.
        """
        self.validate()
        in_degree: Dict[str, int] = {name: 0 for name in self.nodes}
        for targets in self.edges.values():
            for target in targets:
                in_degree[target] += 1
        # Conditional edges are potential; they don't affect baseline in-degree here.

        ready = sorted([name for name, deg in in_degree.items() if deg == 0])
        order: List[str] = []

        adjacency = {src: list(dests) for src, dests in self.edges.items()}

        while ready:
            current = ready.pop(0)
            order.append(current)
            for neighbor in sorted(adjacency.get(current, [])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    ready.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValidationError("DAG contains cycles; topological sort failed.")
        return order


class DAGExecutor:
    """
    Deterministic executor for DAG nodes with simple retry logic.

    This engine:
        • Runs nodes in topological order.
        • For each node, executes it with optional retries.
        • Decides outgoing edges either via conditional_edges (if present
          and condition not None) or via default DAG edges.

    The context dict is the single mutable bag of data; nodes may
    mutate it by returning a new mapping.
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


# =============================================================================
# 3. GLOBAL ORCHESTRATOR
# =============================================================================


@dataclass
class Orchestrator:
    """
    Central orchestrator for v10_9 agentic execution.

    Given:
        • a PlanObject from L1
        • an initial state dict

    It will:
        1. Initialize L4.StateAdapter with the initial state.
        2. Use a PhaseMachine to move through:
            INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE / FAILED
        3. Build and run a DAG:
              plan_node → execute_node → safety_node → qa_council_node? → finalize_node
        4. Call L2 route_executor to execute the plan.
        5. Call L5 SafetyEngine + PolicyEngine + ArbitrationEngine for safety.
        6. Optionally call MultiAgent QA council if mode == "qa".
        7. Return a WorkflowState with final state and phase metadata.

    No tools/LLMs are called here, and no state mutation logic is embedded;
    all state updates are delegated to L4.StateAdapter.
    """

    state_adapter: StateAdapter = field(default_factory=StateAdapter)
    safety_engine: SafetyEngine = field(default_factory=SafetyEngine)
    policy_engine: PolicyEngine = field(default_factory=PolicyEngine)
    arbitration_engine: ArbitrationEngine = field(default_factory=ArbitrationEngine)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _apply_execution_to_state(self, mode: str, result: ExecutionResult[Any]) -> None:
        """
        Map an L2 ExecutionResult payload into L4 state via StatePatch.

        The shape is intentionally aligned with the simulation harness
        and downstream tooling (e.g., "draft_result", "qa_result").
        """
        payload = result.payload
        mode = mode.lower()

        if mode == "strategy":
            # Store selected strategy + decision metadata
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
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

        elif mode == "rag":
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="rag_result", value=p))

        elif mode == "drafting":
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="draft_result", value=p))

        elif mode == "bullets":
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="bullet_result", value=p))

        elif mode == "qa":
            # For QA, ensure "report" key exists
            if hasattr(payload, "qa_report"):
                report_dict = payload.qa_report.to_dict()  # type: ignore[attr-defined]
                patch_value = {"report": report_dict}
            else:
                patch_value = {"report": payload}
            self.state_adapter.apply_patch(StatePatch(key="qa_result", value=patch_value))

        elif mode == "safety":
            # For Safety, align with state["safety_result"]["report"]
            if hasattr(payload, "safety_report"):
                report_dict = payload.safety_report.to_dict()  # type: ignore[attr-defined]
                patch_value = {
                    "report": report_dict,
                    "sanitized": getattr(payload, "sanitized_content", ""),
                }
            else:
                patch_value = {"report": payload}
            self.state_adapter.apply_patch(StatePatch(key="safety_result", value=patch_value))

        elif mode == "prompt_engineering":
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="prompt_engineering_result", value=p))

        elif mode == "hil":
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="hil_result", value=p))

        elif mode == "meta_learning":
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="meta_learning_result", value=p))

        else:
            # Unknown modes are stored verbatim under "last_execution"
            p = payload.to_dict() if hasattr(payload, "to_dict") else dict(payload)
            self.state_adapter.apply_patch(StatePatch(key="last_execution", value={"mode": mode, "payload": p}))

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(self, plan: PlanObject, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Execute full L3 orchestration for a single L1 PlanObject.

        This is a synchronous API; higher layers (main/CLI) may wrap it
        with asyncio as needed.
        """
        # 1. Initialize phase machine and cost tracker
        machine = PhaseMachine()
        cost_tracker = CostTracker()

        # 2. Seed adapter with initial state via patches
        workflow_id = str(initial_state.get("workflow_id") or "workflow_v10_9")
        for key, value in (initial_state or {}).items():
            self.state_adapter.apply_patch(StatePatch(key=key, value=value))

        # 3. Phase: INIT → PLANNING
        machine.transition(WorkflowPhase.PLANNING.value)

        mode = str(plan.get("mode", "")).lower()
        if not mode:
            raise ValidationError("PlanObject missing 'mode' field.")

        # 4. Build DAG nodes
        def plan_node(context: Dict[str, Any]) -> Dict[str, Any]:
            # No planning here; plan already exists. We just attach it to context.
            context["plan"] = plan
            context["state"] = self.state_adapter.state
            context["workflow_phase"] = machine.current()
            return context

        async def _execute_async(p: PlanObject, s: Dict[str, Any]) -> ExecutionResult[Any]:
            return await route_executor(p, s)

        def execute_node(context: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal cost_tracker
            cost_tracker.start_span("execution")
            current_state = self.state_adapter.state

            # L2 execution
            exec_result: ExecutionResult[Any] = asyncio.run(_execute_async(plan, current_state))
            cost_tracker.end_span("execution")

            context["execution_result"] = exec_result
            # Patch state using L4 adapter, domain-specific keys
            self._apply_execution_to_state(mode, exec_result)
            context["state"] = self.state_adapter.state

            # Phase: PLANNING → EXECUTING
            machine.transition(WorkflowPhase.EXECUTING.value)
            context["workflow_phase"] = machine.current()
            return context

        def safety_node(context: Dict[str, Any]) -> Dict[str, Any]:
            """
            Run L5 safety evaluation based on current state and plan intent.
            Produces:
                context["safety_report"]
                context["policy_decision"]
                context["arbitration_action"]
            """
            state = context.get("state", self.state_adapter.state)
            # SafetyEngine consumes content; details are implemented in l5.py
            safety_report = self.safety_engine.evaluate_content(state, plan)
            policy_decision = self.policy_engine.review(safety_report)
            arbitration_action = self.arbitration_engine.decide(policy_decision, safety_report)

            context["safety_report"] = safety_report
            context["policy_decision"] = policy_decision
            context["arbitration_action"] = arbitration_action

            # Attach safety-related blocks into state via adapter, merging with
            # any executor-provided safety_result.
            self.state_adapter.apply_patch(StatePatch(key="safety_result", value={"report_l5": safety_report}))
            self.state_adapter.apply_patch(StatePatch(key="arbitration", value=arbitration_action))
            context["state"] = self.state_adapter.state

            # Phase: EXECUTING → REVIEWING
            machine.transition(WorkflowPhase.REVIEWING.value)
            context["workflow_phase"] = machine.current()
            return context

        def safety_condition(context: Dict[str, Any]) -> str:
            """
            Decide next edge key based on arbitration action:
                - "halt"    → stop further nodes
                - "proceed" → continue
            """
            action = (context.get("arbitration_action") or {}).get("action", "proceed")
            if action == "halt":
                return "halt"
            return "proceed"

        def qa_council_node(context: Dict[str, Any]) -> Dict[str, Any]:
            """
            If mode == "qa", run multi-agent QA council using COUNCIL_OF_QA.
            If not QA mode, this node is a no-op (still present in the DAG).
            """
            if mode != "qa":
                return context

            state = context.get("state", self.state_adapter.state)
            ma_orch = MultiAgentOrchestrator(graph=COUNCIL_OF_QA, state_adapter=self.state_adapter)
            council_state = ma_orch.dispatch_for_qa(state, plan)
            # The orchestrator returns a dict of fields; reconcile through L4
            for key, value in council_state.items():
                self.state_adapter.apply_patch(StatePatch(key=key, value=value))
            context["state"] = self.state_adapter.state
            return context

        def finalize_node(context: Dict[str, Any]) -> Dict[str, Any]:
            """
            Finalize context: attach telemetry, optimization hints, etc.
            """
            spans = cost_tracker.snapshot()
            optimization = compute_optimization_hint(spans.get("spans", []))

            # Attach telemetry into state
            telemetry_block = {
                "spans": spans.get("spans", []),
                "optimization": optimization,
            }
            self.state_adapter.apply_patch(StatePatch(key="telemetry", value=telemetry_block))
            context["state"] = self.state_adapter.state

            # Emit a global event
            record_event(
                "orchestrator_cycle",
                {
                    "plan_mode": mode,
                    "workflow_id": workflow_id,
                    "spans": spans,
                    "optimization": optimization,
                },
            )

            # Phase: REVIEWING → COMPLETE
            machine.transition(WorkflowPhase.COMPLETE.value)
            context["workflow_phase"] = machine.current()
            return context

        # Wrap node callables into DAGNodes
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

        # Default edges (when conditional edges don't override)
        edges: Dict[str, List[str]] = {
            "plan_node": ["execute_node"],
            "execute_node": ["safety_node"],
            "safety_node": [],        # actual edges decided by safety_condition
            "qa_council_node": ["finalize_node"],
            "finalize_node": [],
        }

        dag = DAG(nodes=nodes, edges=edges)
        executor = DAGExecutor()

        # Run DAG
        initial_context = {
            "plan": plan,
            "state": self.state_adapter.state,
            "workflow_phase": machine.current(),
        }

        try:
            final_context = executor.run(dag, initial_context)
        except ToolExecutionError as exc:
            # If orchestration fails at DAG level, mark workflow as FAILED.
            machine.transition(WorkflowPhase.FAILED.value)
            final_state = self.state_adapter.state
            phase_metadata = {"history": list(machine.history)}
            return WorkflowState(
                workflow_id=workflow_id,
                phase=machine.current(),
                nodes={},
                state=final_state,
                phase_metadata=phase_metadata,
            )

        final_state = self.state_adapter.state
        phase_metadata = {"history": list(machine.history)}

        return WorkflowState(
            workflow_id=workflow_id,
            phase=machine.current(),
            nodes={},
            state=final_state,
            phase_metadata=phase_metadata,
        )
