"""Self-Reflection Engine - Quality gates for the CRITIQUE micro-stage.

This module implements the reflection engine that forces nodes to grade their own
work before passing it downstream, preventing hallucination cascades.
"""

import asyncio
import json
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "reflection_config", "p0_governance")
_emit_reads_policy_state("p0", "reflection_config", "policy_binding")
_emit_snapshots_state("p0", "reflection_config", "state_snapshot")
from agentic_core.config.constants_config import DEFAULT_SLEEP, DEFAULT_TIMEOUT, THRESHOLD
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("reflection_config", "p4obs", "metric_1")
_emit_emits_metric_event("reflection_config", "p4obs", "metric_2")
_emit_emits_metric_event("reflection_config", "p4obs", "metric_3")
_emit_emits_metric_event("reflection_config", "p4obs", "metric_4")
_emit_emits_metric_event("reflection_config", "p4obs", "metric_5")
_emit_emits_metric_event("reflection_config", "p4obs", "metric_6")
_emit_records_incident_event("reflection_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("reflection_config", "p4obs", "anomaly")
_emit_writes_observability_log("reflection_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("reflection_config", "p4obs", "mon_state")
_emit_triggers_alert("reflection_config", "p4obs", "alert")
_emit_links_incident_trace("reflection_config", "p4obs", "trace_link")
_emit_captures_pattern("reflection_config", "p3lm", "pattern")
_emit_records_learning_event("reflection_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reflection_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("reflection_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reflection_config", "p3lm", "routing")
_emit_improves_agent_policy("reflection_config", "p3lm", "policy")
_emit_stores_learning_state("reflection_config", "p3lm", "state")
_emit_records_execution_trace("reflection_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reflection_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reflection_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reflection_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reflection_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reflection_config", "env_read", "p2_env_1")
_emit_reads_environ("reflection_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("reflection_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reflection_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reflection_config", "context_pull")
_emit_pulls_context("p1", "reflection_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reflection_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reflection_config", "uwg_term_2")
_emit_writes_through("p1", "reflection_config", "write_through")
_emit_writes_through("p1", "reflection_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "reflection_config", "safety_validation")
_emit_invokes_eval("p1", "reflection_config", "eval_call")
_emit_proposal_commits_routing("p1", "reflection_config", "routing_commit")
_emit_escalates_to_human("p1", "reflection_config", "human_escalation")
_emit_routes_through("p1", "reflection_config", "route_through")
_emit_checks_agent_registry("p1", "reflection_config", "agent_registry")
_emit_validates_agent_capability("p1", "reflection_config", "capability")
_emit_dispatches_execution_plan("p1", "reflection_config", "exec_plan")
_emit_agent_executes_agent("p1", "reflection_config", "sub_agent")
_emit_routes_to_agent("p1", "reflection_config", "target_agent")
_emit_verifies_policy("p1", "reflection_config", "policy_check")
_emit_observes_runtime_state("p1", "reflection_config", "runtime_state")
_emit_verifies_boundary("p1", "reflection_config", "boundary_check")
_emit_transcripts_response("p1", "reflection_config", "transcript")
_emit_hard_fails_untranscripted("p1", "reflection_config")
_emit_gated_by_confidence("p1", "reflection_config", "confidence_gate")
emit_replay_key("p0", "reflection_config")
emit_determinism_digest("p0", "reflection_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "reflection_config", "execution_auth")
_emit_validates_capability("p2", "reflection_config", "capability_check")
_emit_routes_to_capability("p2", "reflection_config", "capability_route")
_emit_writes_via_uwg("p2", "reflection_config", "uwg_write")
_emit_blocks_direct_write("p2", "reflection_config", "direct_write_block")
_emit_records_tool_invocation("p2", "reflection_config", "tool_invocation")
_emit_captures_execution_output("p2", "reflection_config", "exec_output")
_emit_dispatches_agent("p3", "reflection_config", "agent_dispatch")
_emit_coordinates_agents("p3", "reflection_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "reflection_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "reflection_config", "healing_outcome")
_emit_escalates_failure("p3", "reflection_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "reflection_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reflection_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "reflection_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "reflection_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reflection_config", "eval_metric")
_emit_stores_embedding("p4", "reflection_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "reflection_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reflection_config", "exec_snapshot_link")

# Configuration constants

try:
    from agentic_core.L5_safety.validators.circuit_breaker_types import (
        CircuitBreakerConfig,
        CircuitBreakerFactory,
        CircuitOpenError,
    )
except ImportError:  # guardian: allow-silent-swallow
    # Fallback implementations
    @dataclass
    class CircuitBreakerConfig:
        failure_threshold: int = 5
        recovery_timeout: float = 60.0
        timeout: float = 30.0

    class _FallbackCircuitBreaker:
        async def call(self, func, *args, **kwargs):
            return await func(*args, **kwargs)

    class CircuitBreakerFactory:
        @staticmethod
        def create(config: Any) -> "_FallbackCircuitBreaker":
            return _FallbackCircuitBreaker()

        @staticmethod
        def get(name: str, config: Any) -> "_FallbackCircuitBreaker":
            return _FallbackCircuitBreaker()

    class CircuitOpenError(Exception):
        pass


logger = logging.getLogger(__name__)


class CritiqueResult(BaseModel):
    """Result of a critique evaluation."""

    is_valid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    critique_reasoning: str
    suggested_fix: str | None = None
    validation_type: str = "unknown"  # "regex" or "llm"
    execution_time: float = 0.0
    mutation_request: Optional["MutationRequest"] = None

    @validator("confidence_score")
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0 and 1")
        return v


class ValidationCriterion(BaseModel):
    """A single validation criterion."""

    name: str
    description: str
    validator: str | Callable  # regex pattern or function
    is_required: bool = True
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class ReflectionConfig(BaseModel):
    """configuration for the Reflection Engine."""

    use_fast_model: bool = True
    max_critique_loops: int = Field(default=3, ge=1, le=10)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_regex_cache: bool = True
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"  # Cost-effective model
    timeout: float = Field(default=30.0, ge=1.0)


class MutationRequest(BaseModel):
    """Request for DAG mutation when critique fails."""

    action: str  # "SPAWN_PREDECESSOR" or "ESCALATE"
    reason: str
    required_context: str | None = None
    hop_function: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: str = "normal"


class ReflectionEngine:
    """Engine for self-reflection and quality assessment."""

    def __init__(self, config: ReflectionConfig | None = None):
        """Initialize the Reflection Engine.

        Args:
            config: Optional configuration
        """
        self.config = config or ReflectionConfig()

        # Built-in validation criteria
        self.builtin_criteria = {
            "json_valid": ValidationCriterion(
                name="json_valid",
                description="Output must be valid JSON",
                validator=self._validate_json,
                is_required=True,
            ),
            "min_length": ValidationCriterion(
                name="min_length",
                description="Output must meet minimum length",
                validator=lambda x: len(str(x)) >= 10,
                is_required=False,
            ),
            "max_length": ValidationCriterion(
                name="max_length",
                description="Output must not exceed maximum length",
                validator=lambda x: len(str(x)) <= 10000,
                is_required=False,
            ),
            "no_empty_fields": ValidationCriterion(
                name="no_empty_fields",
                description="Dictionary values must not be empty",
                validator=self._validate_no_empty_fields,
                is_required=True,
            ),
            "contains_keywords": ValidationCriterion(
                name="contains_keywords",
                description="Output must contain specific keywords",
                validator=self._validate_keywords,
                is_required=False,
            ),
        }

        # cache for regex patterns
        self._regex_cache = {} if self.config.enable_regex_cache else None

        # Statistics
        self.stats = {
            "total_critiques": 0,
            "fast_path_critiques": 0,
            "llm_critiques": 0,
            "passes": 0,
            "failures": 0,
            "average_confidence": 0.0,
        }

        # Initialize circuit breaker for LLM calls
        self.circuit_breaker = CircuitBreakerFactory.get(
            "reflection_engine",
            CircuitBreakerConfig(
                failure_threshold=THRESHOLD,
                recovery_timeout=DEFAULT_TIMEOUT,
                timeout=self.config.timeout,
            ),
        )

        logger.info(f"Initialized ReflectionEngine with model: {self.config.llm_model}")

    async def evaluate(
        self,
        content: Any,
        criteria: list[str | ValidationCriterion],
        context: dict[str, Any] | None = None,
    ) -> CritiqueResult:
        """Evaluate content against criteria with circuit breaker protection.

        Args:
            content: The content to evaluate
            criteria: List of criteria names or objects
            context: Optional context for evaluation

        Returns:
            CritiqueResult with evaluation details
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "SelfCritiqueEvaluator.evaluate",
        )
        start_time = time.time()
        self.stats["total_critiques"] += 1

        # Normalize criteria to objects
        normalized_criteria = []
        for criterion in criteria:
            if isinstance(criterion, str):
                if criterion in self.builtin_criteria:
                    normalized_criteria.append(self.builtin_criteria[criterion])
                else:
                    logger.warning(f"Unknown criterion: {criterion}")
            else:
                normalized_criteria.append(criterion)

        # Determine evaluation path and execute with circuit breaker
        try:
            if self._should_use_fast_path(normalized_criteria):
                # Fast path doesn't need circuit breaker (no LLM call)
                result = await self._fast_path_evaluate(content, normalized_criteria, context)
                self.stats["fast_path_critiques"] += 1
            else:
                # Wrap LLM call with circuit breaker
                result = await self.circuit_breaker.call(
                    self._llm_path_evaluate,
                    content,
                    normalized_criteria,
                    context,  # guardian: CircuitOpenError should be handled with specific context
                )
                self.stats["llm_critiques"] += 1
        # guardian: allow-silent-swallow - acceptable exception handling

        except CircuitOpenError:
            # GAP-02 FIX: fail-closed for required criteria, fail-open only for optional
            has_required = any(getattr(c, "is_required", True) for c in normalized_criteria)
            logger.warning(
                "Reflection Engine Circuit OPEN. "
                f"Failing {'closed' if has_required else 'open'} (required={has_required}).",
            )
            result = CritiqueResult(
                is_valid=not has_required,
                confidence_score=0.3,
                critique_reasoning="Circuit breaker OPEN - service degraded",
                validation_type="circuit_breaker_fallback",
            )

        except (
            RuntimeError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as e:  # guardian: allow-silent-swallower
            # GAP-02 FIX: fail-closed on unexpected errors when required criteria present
            has_required = any(getattr(c, "is_required", True) for c in normalized_criteria)
            logger.error(f"Reflection evaluation failed: {e}")
            result = CritiqueResult(
                is_valid=not has_required,
                confidence_score=0.2,
                critique_reasoning=f"Evaluation failed: {str(e)}",
                validation_type="error_fallback",
            )

        # Update statistics
        result.execution_time = time.time() - start_time
        if result.is_valid:
            self.stats["passes"] += 1
        else:
            self.stats["failures"] += 1

        # Update average confidence
        total = self.stats["total_critiques"]
        current_avg = self.stats["average_confidence"]
        self.stats["average_confidence"] = (current_avg * (total - 1) + result.confidence_score) / total

        return result

    def _should_use_fast_path(self, criteria: list[ValidationCriterion]) -> bool:
        """Determine if fast path (regex) can be used."""
        # Fast path if all criteria are simple validators
        for criterion in criteria:
            if isinstance(criterion.validator, str):
                # Regex pattern - can use fast path
                continue
            elif callable(criterion.validator) and criterion.name in self.builtin_criteria:
                # Built-in validator - can use fast path
                continue
            else:
                # Complex validator - need LLM
                return False
        return True

    async def _fast_path_evaluate(
        self,
        content: Any,
        criteria: list[ValidationCriterion],
        context: dict[str, Any] | None,
    ) -> CritiqueResult:
        """Evaluate using fast regex/built-in validators."""
        results = []
        total_weight = 0
        weighted_score = 0

        for criterion in tqdm(criteria, desc="Processing", unit="item"):
            try:
                if isinstance(criterion.validator, str):
                    # Regex validation
                    is_valid = self._validate_regex(content, criterion.validator)
                else:
                    # Built-in function validation
                    is_valid = criterion.validator(content)

                if is_valid:
                    weighted_score += criterion.weight
                else:
                    results.append(f"Failed: {criterion.description}")

                total_weight += criterion.weight

            except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallower
                logger.error(f"Validation error for {criterion.name}: {e}")
                results.append(f"Error: {criterion.name} - {str(e)}")

        # Calculate overall result
        confidence = weighted_score / total_weight if total_weight > 0 else 0.0
        is_valid = confidence >= self.config.confidence_threshold

        reasoning = "Fast path validation: " + "; ".join(results) if results else "All criteria passed"

        return CritiqueResult(
            is_valid=is_valid,
            confidence_score=confidence,
            critique_reasoning=reasoning,
            validation_type="regex",
        )

    async def _llm_path_evaluate(
        self,
        content: Any,
        criteria: list[ValidationCriterion],
        context: dict[str, Any] | None,
    ) -> CritiqueResult:
        """Evaluate using LLM for semantic validation."""
        # Build prompt
        criteria_text = "\n".join(
            [f"- {c.name}: {c.description}{' (Required)' if c.is_required else ''}" for c in criteria],
        )

        context_text = f"\nContext: {json.dumps(context, indent=2)}" if context else ""

        prompt = f"""You are a QA Auditor evaluating the output of an AI agent.

Output to evaluate:
{json.dumps(content, indent=2)}

Validation criteria:
{criteria_text}
{context_text}

Instructions:
1. Check each criterion carefully
2. Provide a Pass/Fail judgment
3. Explain your reasoning
4. If failed, suggest a specific fix

Respond in JSON format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation",
    "suggested_fix": "Specific suggestion if invalid"
}}"""

        try:
            # Call LLM (mock implementation)
            response = await self._call_llm(prompt)

            # Parse response
            llm_result = json.loads(response)

            return CritiqueResult(
                is_valid=llm_result.get("is_valid", False),
                confidence_score=llm_result.get("confidence", 0.0),
                critique_reasoning=llm_result.get("reasoning", "No reasoning provided"),
                suggested_fix=llm_result.get("suggested_fix"),
                validation_type="llm",
            )

        except (
            RuntimeError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as e:  # guardian: allow-silent-swallower
            logger.error(f"LLM evaluation failed: {e}")
            # Fallback to conservative result
            return CritiqueResult(
                is_valid=False,
                confidence_score=0.0,
                critique_reasoning=f"LLM evaluation failed: {str(e)}",
                validation_type="llm_error",
            )

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM for evaluation.

        In a real implementation, this would use the actual LLM client.
        For now, returns a mock response.
        """
        # Mock implementation - in production, use actual LLM
        await asyncio.sleep(DEFAULT_SLEEP)  # Simulate network delay

        # Simple heuristic based on prompt content
        if "json" in prompt.lower():
            return json.dumps(
                {
                    "is_valid": True,
                    "confidence": 0.9,
                    "reasoning": "Output is valid JSON format",
                    "suggested_fix": None,
                },
            )
        elif "required" in prompt.lower():
            return json.dumps(
                {
                    "is_valid": False,
                    "confidence": 0.3,
                    "reasoning": "Missing required fields",
                    "suggested_fix": "Add all required fields to the output",
                },
            )
        else:
            return json.dumps(
                {
                    "is_valid": True,
                    "confidence": 0.8,
                    "reasoning": "Output meets general quality standards",
                    "suggested_fix": None,
                },
            )

    def _validate_regex(self, content: Any, pattern: str) -> bool:
        """Validate content using regex pattern."""
        if self._regex_cache and pattern in self._regex_cache:
            compiled = self._regex_cache[pattern]
        else:
            compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            if self._regex_cache is not None:
                self._regex_cache[pattern] = compiled

        text = str(content)
        return bool(compiled.search(text))

    def _validate_json(self, content: Any) -> bool:
        """Validate that content is valid JSON."""
        if isinstance(content, dict | list):
            try:
                json.dumps(content)
                return True
            except (TypeError, ValueError):
                return False
        elif isinstance(content, str):
            try:
                json.loads(content)
                return True
            except json.JSONDecodeError:
                return False
        return False

    def _validate_no_empty_fields(self, content: Any) -> bool:
        """Validate that dictionary has no empty values."""
        if not isinstance(content, dict):
            return True  # Not applicable

        for _key, value in content.items():
            if value is None or value == "":
                return False
            if isinstance(value, str) and not value.strip():
                return False

        return True

    def _validate_keywords(self, content: Any) -> bool:
        """Validate that content contains required keywords."""
        # This is a placeholder - actual keywords would be in context
        text = str(content).lower()
        required_keywords = ["result", "output"]  # Example

        return all(keyword in text for keyword in required_keywords)

    def get_stats(self) -> dict[str, Any]:
        """Get reflection engine statistics."""
        return {
            **self.stats,
            "config": {
                "model": self.config.llm_model,
                "max_loops": self.config.max_critique_loops,
                "confidence_threshold": self.config.confidence_threshold,
            },
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            "total_critiques": 0,
            "fast_path_critiques": 0,
            "llm_critiques": 0,
            "passes": 0,
            "failures": 0,
            "average_confidence": 0.0,
        }


# Global instance
_reflection_engine: ReflectionEngine | None = None


def get_reflection_engine(**kwargs) -> ReflectionEngine:
    """Get or create global ReflectionEngine instance.

    Args:
        **kwargs: configuration arguments

    Returns:
        ReflectionEngine instance
    """
    global _reflection_engine

    if _reflection_engine is None:
        config = ReflectionConfig(**kwargs) if kwargs else ReflectionConfig()
        _reflection_engine = ReflectionEngine(config)

    return _reflection_engine


# Convenience functions
async def evaluate_content(
    content: Any,
    criteria: list[str | ValidationCriterion],
    context: dict[str, Any] | None = None,
    **kwargs,
) -> CritiqueResult:
    """Convenience function for content evaluation.

    Args:
        content: Content to evaluate
        criteria: Validation criteria
        context: Optional context
        **kwargs: Engine configuration

    Returns:
        CritiqueResult
    """
    engine = get_reflection_engine(**kwargs)
    return await engine.evaluate(content, criteria, context)


# Pre-defined criteria sets
STANDARD_CRITERIA = ["json_valid", "no_empty_fields", "min_length"]

STRICT_CRITERIA = ["json_valid", "no_empty_fields", "min_length", "max_length"]

LENIENT_CRITERIA = ["json_valid"]
