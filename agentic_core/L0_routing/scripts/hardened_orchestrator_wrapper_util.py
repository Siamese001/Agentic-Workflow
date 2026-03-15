from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_routes_through("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_escalates_to_human("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_reads_policy_state("p1", "hardened_orchestrator_wrapper_util", "L0")

"\nHardened Orchestrator - Thin Wrapper\nDelegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py\n\nThis is a stub-and-proxy pattern implementation that eliminates race conditions\nby routing all orchestration through the consolidated AtomicBlackboard-integrated core.\n"
import asyncio
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


def _get_ValidationContext():
    """Lazy load ValidationContext to avoid upward import."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_ValidationContext", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_ValidationContext", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_ValidationContext")
    from agentic_core.L1_cognition.P2_domain.context import ValidationContext

    return ValidationContext


async def run_hardened_orchestrator(
    workflow_id: str,
    WorkflowType: str = "resume_generation",
    storage_path: str | None = None,
    run_base_dir: str = "./pipeline_runs",
) -> Any:
    """
    Run hardened workflow orchestrator with atomic state management.

    This is a thin wrapper that delegates to the consolidated orchestrator.

    Args:
        workflow_id: Workflow identifier
        WorkflowType: Type of workflow
        storage_path: Path for atomic state storage
        run_base_dir: Base directory for run outputs

    Returns:
        Workflow execution results
    """
    from agentic_core.L3_orchestration.config.orchestrator_config import (
        OrchestratorConfig,
        create_orchestrator,
    )

    Logger.info("🚀 Hardened Orchestrator (Wrapper)")
    Logger.info(f"   Workflow: {workflow_id}")
    Logger.info(f"   Type: {WorkflowType}")
    # guardian: allow-magic-config
    config: Any = OrchestratorConfig(
        max_cycles=5, enable_checkpointing=True, checkpoint_dir=storage_path or "./checkpoints"
    )
    context: Any = _get_ValidationContext()()
    orchestrator: Any = create_orchestrator(config=config, context=context)
    resume_agent: Any = create_resume_agent(
        context=context,
        workflow_id=workflow_id,
        WorkflowType=WorkflowType,
        enable_titanium_rag=True,
        enable_state_persistence=True,
        storage_path=storage_path,
        run_base_dir=run_base_dir,
    )
    results: Any = await orchestrator.execute_workflow(workflow_id=workflow_id, agents=[resume_agent])
    return results


if __name__ == "__main__":
    import argparse

    parser: Any = argparse.ArgumentParser(description="Hardened Orchestrator")
    parser.add_argument("--workflow-id", required=True, help="Workflow ID")
    parser.add_argument("--workflow-type", default="resume_generation", help="Workflow type")
    parser.add_argument("--storage-path", help="Storage path for state")
    args: Any = parser.parse_args()
    asyncio.run(
        run_hardened_orchestrator(
            workflow_id=args.workflow_id, WorkflowType=args.WorkflowType, storage_path=args.storage_path
        )
    )
