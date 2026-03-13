"""
Domain Planner Adapter - V10 Legacy Bridge for DomainPlannerAgent.

Per Phase 1 Audit Report, DomainPlannerAgent was identified as requiring
V10 compliance wrapping. This adapter provides:
1. Circuit breaker integration for failure isolation
2. Input validation for external_touch requirements
3. Audit trail for observability
4. Non-blocking execution timeout protection

References:
- Adapters Usage.png: Bridge Pattern for orphan agents
- V10 Diagram: Legacy Bridge integration layer
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker

logger = logging.getLogger(__name__)


@dataclass
class AdapterContext:
    """Context passed through adapter chain."""

    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    risk_level: str = "medium"
    bypass_validation: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Standardized result from adapter operations."""

    success: bool
    data: Any = None
    error: str | None = None
    skipped: bool = False
    skip_reason: str | None = None
    audit_trail: dict[str, Any] = field(default_factory=dict)


class DomainPlannerAdapter:
    """
    V10-Compliant wrapper for DomainPlannerAgent.

    V15 P0.2: Refactored to eliminate AdapterBase/HealingAdapter dependency.
    Circuit breaker and validation logic inlined.
    """

    def __init__(self, legacy_agent: Any, project_root: Path | None = None):
        self._legacy_agent = legacy_agent
        self._service_name = "domain_planner"
        self._project_root = project_root or Path.cwd()
        self._circuit_breaker = get_breaker(f"adapter_{self._service_name}")
        self._required_job_context_keys = {"job_title", "company"}
        self._required_plan_attributes = {"focus_areas", "key_achievements_to_highlight"}

    def _validate_input(self, context: AdapterContext, *args, **kwargs) -> bool:
        """
        V10 Input validation for DomainPlannerAgent.

        Validates:
        1. Required job_context keys exist
        2. Plan object has required attributes
        3. External touch requirements (API keys if needed)

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            True if input is valid, False to reject
        """
        plan = kwargs.get("plan") or (args[0] if len(args) > 0 else None)
        job_context = kwargs.get("job_context") or (args[1] if len(args) > 1 else None)
        workflow_id = kwargs.get("workflow_id") or (args[2] if len(args) > 2 else None)
        if job_context is None:
            logger.warning("DomainPlannerAdapter: job_context is required")
            return False
        if not isinstance(job_context, dict):
            logger.warning("DomainPlannerAdapter: job_context must be a dictionary")
            return False
        if not any(key in job_context for key in self._required_job_context_keys):
            logger.warning(
                f"DomainPlannerAdapter: job_context must contain at least one of {self._required_job_context_keys}"
            )
            return False
        if plan is None:
            logger.warning("DomainPlannerAdapter: plan is required")
            return False
        for attr in self._required_plan_attributes:
            if not hasattr(plan, attr):
                logger.warning(f"DomainPlannerAdapter: plan missing required attribute '{attr}'")
                return False
        if not workflow_id:
            logger.warning("DomainPlannerAdapter: workflow_id is required")
            return False
        if context.metadata.get("requires_external_api"):
            api_key = context.metadata.get("api_key")
            if not api_key:
                logger.warning("DomainPlannerAdapter: external API required but no api_key provided")
                return False
        logger.debug("DomainPlannerAdapter: input validation passed")
        return True

    def _validate_output(self, result: Any, context: AdapterContext) -> bool:
        """
        V10 Output validation for DomainPlannerAgent results.

        Validates:
        1. Result is a PlannerAssessment-like object
        2. Required fields are present (vote, confidence, rationale)

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        """
        if result is None:
            logger.warning("DomainPlannerAdapter: result is None")
            return False
        required_attrs = {"vote", "confidence", "rationale"}
        for attr in required_attrs:
            if not hasattr(result, attr):
                logger.warning(f"DomainPlannerAdapter: result missing '{attr}' attribute")
                return False
        vote = getattr(result, "vote", None)
        if vote not in {"approve", "revise"}:
            logger.warning(f"DomainPlannerAdapter: invalid vote value '{vote}'")
            return False
        confidence = getattr(result, "confidence", None)
        if not isinstance(confidence, int | float) or not 0.0 <= confidence <= 1.0:
            logger.warning(f"DomainPlannerAdapter: confidence must be 0.0-1.0, got {confidence}")
            return False
        logger.debug("DomainPlannerAdapter: output validation passed")
        return True

    def _execute_legacy(self, context: AdapterContext, *args, **kwargs) -> Any:
        """
        Execute the DomainPlannerAgent's run_async method.

        The legacy agent uses async, so we run it in an event loop.

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            PlannerAssessment from the legacy agent
        """
        plan = kwargs.get("plan") or (args[0] if len(args) > 0 else None)
        job_context = kwargs.get("job_context") or (args[1] if len(args) > 1 else None)
        workflow_id = kwargs.get("workflow_id") or (args[2] if len(args) > 2 else None)
        logger.info(f"DomainPlannerAdapter: executing legacy agent for workflow {workflow_id}")
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self._legacy_agent.run_async(plan, job_context, workflow_id)
                )
                return future.result()
        else:
            return loop.run_until_complete(self._legacy_agent.run_async(plan, job_context, workflow_id))

    def plan(
        self, plan: Any, job_context: dict[str, Any], workflow_id: str, context: AdapterContext | None = None
    ) -> AdapterResult:
        """
        Convenience method matching the expected domain planner interface.

        Args:
            plan: StrategyPlan object
            job_context: Job context dictionary
            workflow_id: Workflow identifier
            context: Optional adapter context

        Returns:
            AdapterResult with PlannerAssessment data
        """
        return self.execute(context=context, plan=plan, job_context=job_context, workflow_id=workflow_id)

    def execute(self, context: AdapterContext | None = None, *args: Any, **kwargs: Any) -> AdapterResult:
        """Execute with circuit breaker + input/output validation."""
        if context is None:
            context = AdapterContext(request_id=str(uuid.uuid4()))
        if not self._circuit_breaker.allow_request():
            return AdapterResult(
                success=False,
                skipped=True,
                skip_reason="circuit_breaker_open",
                error="Circuit breaker is OPEN",
            )
        if not self._validate_input(context, *args, **kwargs):
            return AdapterResult(
                success=False,
                skipped=True,
                skip_reason="input_validation_failed",
                error="Input validation failed",
            )
        try:
            raw_result = self._execute_legacy(context, *args, **kwargs)
            self._circuit_breaker.record_success()
        except Exception as e:
            self._circuit_breaker.record_failure(e)
            return AdapterResult(success=False, error=str(e))
        if not self._validate_output(raw_result, context):
            return AdapterResult(success=False, data=raw_result, error="Output validation failed")
        return AdapterResult(success=True, data=raw_result)

    def heal(self, violation: dict[str, Any], context: AdapterContext | None = None) -> AdapterResult:
        """Execute healing with V10 compliance."""
        if context is None:
            context = AdapterContext(request_id=str(uuid.uuid4()))
        try:
            if not self._circuit_breaker.allow_request():
                return AdapterResult(
                    success=False,
                    skipped=True,
                    skip_reason="circuit_breaker_open",
                    error="Circuit breaker is OPEN",
                )
            result = self._legacy_agent.heal(violation)
            self._circuit_breaker.record_success()
            return AdapterResult(
                success=result.get("status") == "success",
                data=result,
                error=result.get("errors", [None])[0] if result.get("errors") else None,
            )
        except Exception as e:
            self._circuit_breaker.record_failure(e)
            return AdapterResult(success=False, error=str(e))


__all__ = ["DomainPlannerAdapter"]
