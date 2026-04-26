"""L3 Orchestration Doctrine — formal contract types per docs/reference/03_L0_Routing/03.6-03.8.

This sub-package realizes 03.6/03.7/03.8 contracts as additive types alongside
existing L3 implementations.

- ``contracts_l3_6`` — 03.6 Workflow Eligibility + DAG (L3WorkflowInput, ExecutionShapeClassification, ManagedWorkflowBlueprint, WorkflowNode, WorkflowEdge)
- ``eligibility``     — 03.6 ``build_l3_workflow()``
- ``contracts_l3_7`` — 03.7 State Ledger + Step Contract (L3StateLedger, NodeReadinessDecision, L3ContextBus, L3StepContract, StepResultIngest)
- ``state``           — 03.7 ``select_next_ready_node``, ``emit_step_contract``, ``ingest_step_result``
- ``contracts_l3_8`` — 03.8 Concurrency / Quality / Fallback / Completion (ConcurrencyPlan, QualityLoopPlan, FallbackCascadeState, WorkflowCompletionTest, SealedWorkflowPackage)
- ``governance``      — 03.8 governors

Constitutional compliance: frozen dataclasses, specific exceptions, closed-vocabulary
enums, no I/O, no PowerShell, no ``except Exception``.

Entry law (03.6 §ENTRY LAW):

L3 doctrine modules MUST refuse to operate when the upstream RouteContract's
``selected_route_id != R3R4_MANAGED_WORKFLOW`` or ``execution_form != MANAGED_WORKFLOW``.
"""

from __future__ import annotations


class L3DoctrineContractError(ValueError):
    """Raised when an L3 doctrine contract violates an invariant.

    Specific subclass of ``ValueError``. Per constitutional §15, callers must
    NOT catch bare ``Exception``.
    """


__all__ = ["L3DoctrineContractError"]
