"""
Coordinates résumé analysis workflow execution with safety and retry mechanisms.

Improves résumé processing reliability by managing complex multi-agent analysis workflows with error handling.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

from l5 import SafetySystem

from .integration import WorkflowExecutionConfig, execute_workflow
from .models.dag_models import DAGResult


TState = TypeVar("TState")


@dataclass
class OrchestratorConfig:
    """
    Configures résumé analysis workflow execution settings for reliability and performance optimization.

    Improves résumé processing by defining retry policies, timeouts, and failure handling for multi-agent workflows.
    """

    max_retries: int = 3
    retry_delay: float = 0.5
    fail_fast: bool = True
    default_node_timeout: Optional[float] = 30.0


class WorkflowOrchestrator:
    """
    Manages complex résumé analysis workflows with multiple agents and safety validation.

    Improves résumé processing by coordinating strategy, drafting, QA, and safety agents for comprehensive job matching analysis.
    """
    """High-level orchestrator for DAG-style workflows.

    This remains L3-only: no direct state mutation, no safety logic.
    It simply wires node executors into the shared integration layer.
    """

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        safety_system: Optional[SafetySystem] = None,
    ) -> None:
        """
        Sets up résumé workflow coordination system with retry policies and safety validation.

        Improves résumé processing reliability by configuring error handling and safety checks for multi-agent analysis.
        """
        self.config = config or OrchestratorConfig()
        self.safety_system = safety_system

    async def run(
        self,
        workflow_id: str,
        initial_state: TState,
        node_executors: Dict[str, Callable[..., Awaitable[Any]]],
        node_dependencies: Dict[str, List[str]],
        **metadata: Any,
    ) -> DAGResult:
        """
        Executes résumé analysis workflow with coordinated multi-agent processing and safety validation.

        Improves résumé processing by managing complex analysis workflows with proper error handling and retry logic.
        """
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



