# FILE: main_v10_9.py
"""
Main Orchestration Entrypoint — v10_9 Agentic Workflow

This file implements the top-level workflow runner for the enterprise
agentic architecture using strict OpenAI-style layering:

    • L1  = Cognition / Planning
    • L2  = Execution / Tool Use
    • L3  = Orchestration / DAG Control Flow
    • L4  = State Adapter / Memory / Patches
    • L5  = Safety / Policy / Arbitration
    • META = Prompting / Routing / Telemetry / Simulation

This module is the ONLY place where all layers come together in a stable,
typed, deterministic pipeline. It never:

    • Does cognition (L1)
    • Does execution (L2)
    • Mutates raw state directly (L4-only)
    • Makes safety decisions (L5-only)
    • Builds prompts (META only)
    • Performs model calls (routing/providers only)

It ONLY:

    • Initializes the system components
    • Defines the orchestration DAG template
    • Executes the DAG using L3.DAGExecutor
    • Applies patches via L4.StateAdapter
    • Passes safety decisions through L5
    • Emits structured WorkflowState output
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

# Layer imports
from models import (
    PlanObject,
    WorkflowState,
    StatePatch,
    WorkflowPhase,
    ArbitrationDecision,
)
from l1 import route_plan
from l2 import route_executor
from l3 import DAG, DAGNode, DAGExecutor
from l4 import StateAdapter
from l5 import SafetyEngine, PolicyEngine, ArbitrationEngine
from observability import TELEMETRY, summarize_run
from runtime_utils import CostTracker, record_event


# ============================================================================
# ORCHESTRATION HELPERS
# ============================================================================

def _get_content_for_safety(state: Dict[str, Any]) -> str:
    """
    Extract the deterministic content candidate for L5 Safety evaluation.
    Priority:
        1. state["draft_result"]["draft"]
        2. last user message
        3. state["summary"]
    """
    draft = state.get("draft_result") or {}
    draft_list = draft.get("draft") or []
    if isinstance(draft_list, list) and draft_list:
        return "\n".join(str(x) for x in draft_list)

    msgs = state.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, dict) and m.get("role") == "user":
            return str(m.get("content", "")) or ""

    return str(state.get("summary", "")) or ""


# ============================================================================
# STEP RUNNERS: These wrap L1/L2/L5 calls cleanly for DAG nodes
# ============================================================================

async def _run_l1_planning(context: Dict[str, Any]) -> Dict[str, Any]:
    state = context["state"]
    plan: PlanObject = route_plan(state)
    return {
        **context,
        "plan": plan,
        "phase": WorkflowPhase.PLANNING.value,
    }


async def _run_l2_execution(context: Dict[str, Any]) -> Dict[str, Any]:
    plan: PlanObject = context.get("plan")
    state = context["state"]

    result = await route_executor(plan, state)

    return {
        **context,
        "execution_result": result,
        "phase": WorkflowPhase.EXECUTING.value,
    }


async def _run_l4_patch(context: Dict[str, Any]) -> Dict[str, Any]:
    adapter: StateAdapter = context["state_adapter"]
    result = context["execution_result"]
    payload = result.payload

    # Patch the state under the correct domain key
    key = f"{result.model}_result"
    new_state = adapter.apply_patch(StatePatch(key=key, value=payload.to_dict() if hasattr(payload, "to_dict") else payload))

    return {
        **context,
        "state": new_state,
        "phase": WorkflowPhase.REVIEWING.value,
    }


async def _run_l5_safety(context: Dict[str, Any]) -> Dict[str, Any]:
    state = context["state"]
    plan = context["plan"]

    engine = context["safety_engine"]
    policy_engine = context["policy_engine"]
    arbiter = context["arbiter"]

    content = _get_content_for_safety(state)
    safety_report = engine.validate(content, audience=str(plan.get("audience", "general")))
    policy = policy_engine.review(safety_report)
    decision = arbiter.decide(policy, safety_report)

    return {
        **context,
        "safety_report": safety_report,
        "policy_decision": policy,
        "arbitration": decision,
    }


async def _run_phase_complete(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **context,
        "phase": WorkflowPhase.COMPLETE.value,
    }


# ============================================================================
# DAG TEMPLATE — The canonical v10_9 orchestrator graph
# ============================================================================

def _build_dag() -> DAG:
    return DAG(
        nodes={
            "plan": DAGNode(
                name="plan",
                run=_run_l1_planning,
            ),
            "execute": DAGNode(
                name="execute",
                run=_run_l2_execution,
            ),
            "patch": DAGNode(
                name="patch",
                run=_run_l4_patch,
            ),
            "safety": DAGNode(
                name="safety",
                run=_run_l5_safety,
            ),
            "complete": DAGNode(
                name="complete",
                run=_run_phase_complete,
            ),
        },
        edges={
            "plan": ["execute"],
            "execute": ["patch"],
            "patch": ["safety"],
            "safety": ["complete"],
            "complete": [],
        },
    )


# ============================================================================
# MAIN WORKFLOW RUNNER
# ============================================================================

async def run_workflow_v10_9(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Primary runtime workflow entrypoint for v10_9.

    Inputs:
        initial_state — raw dict-like state before L4 adaptation
        compat_mode   — optional compatibility flag
        debug_mode    — attaches extra metadata for observability
        stream_callback — optional streaming hook

    Returns:
        {
            "workflow_id": str,
            "phase": str,
            "state": dict,
            "phase_metadata": dict,
            "run_summary": dict,
        }
    """

    # Initialize L4
    adapter = StateAdapter(initial_state)
    state = adapter.state

    # Add workflow_id if missing
    if "workflow_id" not in state:
        import uuid
        state["workflow_id"] = f"wf_{uuid.uuid4().hex}"

    wf_id = state["workflow_id"]

    # Safety engines
    safety_engine = SafetyEngine()
    policy_engine = PolicyEngine()
    arbiter = ArbitrationEngine()

    # Initialize DAG
    dag = _build_dag()
    executor = DAGExecutor()

    # Create orchestration context
    context: Dict[str, Any] = {
        "state": state,
        "state_adapter": adapter,
        "safety_engine": safety_engine,
        "policy_engine": policy_engine,
        "arbiter": arbiter,
        "phase": WorkflowPhase.INIT.value,
    }

    cost_tracker = CostTracker()
    phase_history: List[str] = []

    # Run DAG
    current_context = context
    for node_name in dag.topological_order():
        cost_tracker.start_span(node_name)
        current_context = await dag.nodes[node_name].run(current_context)
        cost_tracker.end_span(node_name)

        phase = current_context.get("phase", "")
        if phase:
            phase_history.append(phase)

        # Stream callback (if provided)
        if stream_callback:
            await stream_callback({"node": node_name, "context": current_context})

        # Arbitration may halt the DAG
        arb = current_context.get("arbitration", {})
        if isinstance(arb, dict) and arb.get("action") == "halt":
            break

    # Build WorkflowState
    workflow_state = WorkflowState(
        workflow_id=wf_id,
        phase=current_context.get("phase", WorkflowPhase.COMPLETE.value),
        nodes={},
        state=current_context.get("state", {}),
        phase_metadata={"history": phase_history},
    )

    # Observability summary
    run_summary = summarize_run(
        workflow_id=wf_id,
        state=workflow_state.state,
        phase_history=phase_history,
        cost_tracker=cost_tracker,
    )

    return {
        "workflow_id": workflow_state.workflow_id,
        "phase": workflow_state.phase,
        "state": workflow_state.state,
        "phase_metadata": workflow_state.phase_metadata,
        "run_summary": run_summary,
    }


# ============================================================================
# SYNC WRAPPER
# ============================================================================

def run_workflow_v10_9_sync(initial_state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    return asyncio.run(run_workflow_v10_9(initial_state, **kwargs))
