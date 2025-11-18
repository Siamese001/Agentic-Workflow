# FILE: v10_9_clean/legacy_bridge_v10_7.py
"""
Legacy Bridge — v10_9 ↔ v10_7

This module provides a thin compatibility layer that lets the v10_9
workflow invoke the full v10_7 agentic LangGraph pipeline.

Usage:
    from legacy_bridge_v10_7 import run_10_7_workflow_sync

    result = run_10_7_workflow_sync(job_input_dict, master_resume_dict)
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, Optional

from core_v10_7 import (
    ConfigV10_7,
    MainGraphState,
    WorkflowContext,
    WorkflowError,
    create_workflow_context,
    get_checkpointer,
    cleanup_workflow_chroma_collection,
)
from agent_orchestration_v10_7 import get_graph_app, unwrap_node_result


def _build_initial_state(
    job_input: Dict[str, Any],
    master_resume: Dict[str, Any],
    workflow_id: str,
) -> Dict[str, Any]:
    """
    Build a v10_7 MainGraphState dict from job + resume payloads.

    Mirrors the initialization logic used in run_batch_v10_7/main_v10_7
    but without any CLI/file-system assumptions.
    """
    initial = MainGraphState()
    initial.resume.master_resume = master_resume

    initial.job.raw_jd = job_input.get("job_description", "")
    initial.job.company = job_input.get("company_name") or job_input.get("company", "")
    initial.job.job_title = job_input.get("job_title") or job_input.get("title", "")

    initial.metadata.workflow_id = workflow_id
    initial.metadata.complexity = "unknown"

    return initial.to_dict()


async def _run_10_7_workflow_async(
    job_input: Dict[str, Any],
    master_resume: Dict[str, Any],
    config_path: str = "master_config_v10_7.json",
    *,
    enable_hil: bool = True,
    enable_mcp: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Internal async runner that executes the full v10_7 LangGraph workflow
    and returns the final state dict.
    """
    if not isinstance(job_input, dict):
        raise WorkflowError("job_input must be a dict")
    if not isinstance(master_resume, dict):
        raise WorkflowError("master_resume must be a dict")

    # Load v10_7 config and composition root
    config = ConfigV10_7(config_path)
    context: WorkflowContext = create_workflow_context(config)

    workflow_id = str(job_input.get("workflow_id") or uuid.uuid4())
    context.workflow_id = workflow_id

    checkpointer = get_checkpointer(config)
    app = get_graph_app(
        checkpointer=checkpointer,
        workflow_context=context,
        enable_hil=enable_hil,
        enable_mcp=enable_mcp,
    )

    # Build initial state
    state_dict = _build_initial_state(job_input, master_resume, workflow_id)
    run_config = {"configurable": {"thread_id": workflow_id}}

    final_state_dict: Optional[Dict[str, Any]] = None

    async for step in app.astream(state_dict, run_config):
        # Each step is a {node_name: state} mapping; take the payload
        node_name = list(step.keys())[0]
        final_state_dict = step[node_name]

    if final_state_dict is None:
        raise WorkflowError("v10_7 workflow finished with no final state.")

    # Unwrap NodeResult → raw workflow state
    final_state_dict = unwrap_node_result(final_state_dict)

    # Validate round-trip through MainGraphState for consistency
    final_state = MainGraphState.from_dict(final_state_dict)
    out_state = final_state.to_dict()

    # Cleanup vector store for this workflow
    cleanup_workflow_chroma_collection(context)

    return {
        "workflow_id": workflow_id,
        "state": out_state,
        "cost_summary": context.cost_tracker.get_cost_summary(workflow_id),
    }


def run_10_7_workflow_sync(
    job_input: Dict[str, Any],
    master_resume: Dict[str, Any],
    config_path: str = "master_config_v10_7.json",
    *,
    enable_hil: bool = True,
    enable_mcp: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Synchronous wrapper around the full v10_7 workflow.

    Returns:
        {
            "workflow_id": str,
            "state": <final v10_7 MainGraphState as dict>,
            "cost_summary": <cost tracker summary dict>,
        }
    """
    return asyncio.run(
        _run_10_7_workflow_async(
            job_input=job_input,
            master_resume=master_resume,
            config_path=config_path,
            enable_hil=enable_hil,
            enable_mcp=enable_mcp,
        )
    )
