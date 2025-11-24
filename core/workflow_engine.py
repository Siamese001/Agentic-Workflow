"""Top-level agentic workflow engine wiring L3, L4, and L5.

This is a thin façade over the lower-level integration helpers in
`core.integration` and `core.workflow_context`. It intentionally
avoids pulling in L1/L2 concerns so that those layers can be
composed by callers as needed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

from l5.integration import SafetySystem

from .integration import WorkflowExecutionConfig, create_workflow_context, execute_workflow
from .models.dag_models import DAGResult


TState = TypeVar("TState")


@dataclass
class EngineConfig:
    """High-level configuration for the workflow engine."""

    max_retries: int = 3
    retry_delay: float = 0.5
    fail_fast: bool = True
    default_node_timeout: Optional[float] = 30.0


class AgenticWorkflowEngine:
    """Convenience wrapper for executing DAG-style workflows.

    Callers are expected to supply:
    - an initial L4-managed state object
    - a node-executor mapping
    - a dependency mapping
    - an optional L5 SafetySystem
    """

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        safety_system: Optional[SafetySystem] = None,
    ) -> None:
        self.config = config or EngineConfig()
        self.safety_system = safety_system

    async def run_dag(
        self,
        workflow_id: str,
        initial_state: TState,
        node_executors: Dict[str, Callable[..., Awaitable[Any]]],
        node_dependencies: Dict[str, List[str]],
        **metadata: Any,
    ) -> DAGResult:
        """Execute a DAG using the core L3–L4–L5 integration helpers."""

        wf_cfg = WorkflowExecutionConfig(
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            fail_fast=self.config.fail_fast,
            default_node_timeout=self.config.default_node_timeout,
        )

        return await execute_workflow(
            workflow_id=workflow_id,
            initial_state=initial_state,
            node_executors=node_executors,
            node_dependencies=node_dependencies,
            safety_system=self.safety_system,
            config=wf_cfg,
            **metadata,
        )
