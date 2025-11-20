# FILE: 10_10/l3.py
"""
Unified L3 Orchestration Layer (v10_10)
=======================================

Responsibilities:
    • Execute the workflow DAG in the correct order.
    • Coordinate L2 (execution/cognition) without doing execution itself.
    • Integrate self-correction (retry logic) based on CorrectionSignals.
    • Gate outputs via L5 safety.
    • Produce a deterministic StatePatch via L4 (no mutation here).
    • Emit spans + events for Observability (Pillar 10).

Non-Responsibilities:
    • No LLM calls (L2 only).
    • No planning (L1 only).
    • No state mutation (L4 only).
    • No safety policy decisions (L5 only).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from models import WorkflowPlanBundle, L2ResultBundle, ExecutionContext
from l2 import execute_workflow_plans
from self_correction import evaluate_all_surfaces, aggregate_correction_signals, CorrectionSignal
from l4 import apply_state_patch
from l5 import safety_gate
from observability import start_span, end_span, record_event, record_exception


# ============================================================================
# DAG Definition (Declarative)
# ============================================================================

# NOTE:
# In 10_10 the DAG is ALWAYS:
#   Strategy → RAG → Drafting → QA → Safety
#
# L3 orchestrates this with retries if correction surfaces fire.
#
DAG_NODES = ["strategy", "rag", "drafting", "qa", "safety"]


@dataclass
class DAGResult:
    """
    A typed bundle returned by L3 after DAG execution.
    """
    l2_results: L2ResultBundle
    corrections: List[CorrectionSignal]
    corrected: bool
    safety_passed: bool
    final_state_patch: Dict[str, Any]


# ============================================================================
# L3 Orchestration Entrypoint
# ============================================================================

def run_dag(
    ctx: ExecutionContext,
    plans: WorkflowPlanBundle,
    max_retries: int = 2,
) -> DAGResult:
    """
    L3 DAG Execution Loop (Deterministic)

    Workflow:
        For up to max_retries:
            1. Execute L2 (strategy → rag → drafting → qa → safety)
            2. Evaluate correction surfaces
            3. If severe issues → retry
            4. Else break loop

        After loop:
            5. Run L5 safety gate
            6. Build final state patch via L4
            7. Return DAGResult

    Notes:
        • No LLM calls here.
        • No tool calls here.
        • No state mutation here.
    """

    span = start_span("l3.run_dag", ctx=ctx.span_context())

    retries = 0
    corrected = False
    last_l2: Optional[L2ResultBundle] = None
    last_corrections: List[CorrectionSignal] = []

    try:
        while True:
            record_event("l3.dag_iteration", {"retries": retries})

            # --------------------------------------------------------------
            # 1. Execute full L2 pipeline
            # --------------------------------------------------------------
            last_l2 = execute_workflow_plans(plans, ctx)

            # --------------------------------------------------------------
            # 2. Evaluate Correction Surfaces
            # --------------------------------------------------------------
            corrections = evaluate_all_surfaces(
                strategy=last_l2.strategy,
                rag=last_l2.rag,
                drafting=last_l2.drafting,
                qa=last_l2.qa,
                safety=last_l2.safety,
            )
            last_corrections = corrections

            signal = aggregate_correction_signals(corrections)

            # --------------------------------------------------------------
            # 3. Break / Retry Logic
            # --------------------------------------------------------------
            if signal is None or signal.severity == 0:
                record_event("l3.no_correction_needed", {})
                break  # done

            corrected = True

            record_event(
                "l3.correction_triggered",
                {
                    "severity": signal.severity,
                    "reason": signal.reason,
                    "recommended": signal.recommended_action,
                },
            )

            retries += 1
            if retries > max_retries:
                record_event("l3.max_retries_exceeded", {"max_retries": max_retries})
                break

            # otherwise → loop again with same plans & ctx

        # --------------------------------------------------------------
        # 4. Apply L5 Safety Gate
        # --------------------------------------------------------------
        safety_passed = safety_gate(last_l2.safety)

        # --------------------------------------------------------------
        # 5. Generate L4 State Patch
        # --------------------------------------------------------------
        final_state_patch = apply_state_patch(
            l2_results=last_l2,
            corrections=last_corrections,
            ctx=ctx,
            safety_passed=safety_passed,
        )

        return DAGResult(
            l2_results=last_l2,
            corrections=last_corrections,
            corrected=corrected,
            safety_passed=safety_passed,
            final_state_patch=final_state_patch,
        )

    except Exception as exc:
        record_exception("l3.dag_failure", exc)
        raise
    finally:
        end_span(span)
