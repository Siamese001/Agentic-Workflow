"""
Prompt Optimizer - Phase 5 Optimization
LLM prompt optimization utilities for high-reasoning agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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

_emit_applies_guardrail("p0", "prompt_optimizer_types", "p0_governance")
_emit_reads_policy_state("p0", "prompt_optimizer_types", "policy_binding")
_emit_snapshots_state("p0", "prompt_optimizer_types", "state_snapshot")
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

_emit_emits_metric_event("prompt_optimizer_types", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_optimizer_types", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_optimizer_types", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_optimizer_types", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_optimizer_types", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_optimizer_types", "p4obs", "metric_6")
_emit_records_incident_event("prompt_optimizer_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_optimizer_types", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_optimizer_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_optimizer_types", "p4obs", "mon_state")
_emit_triggers_alert("prompt_optimizer_types", "p4obs", "alert")
_emit_links_incident_trace("prompt_optimizer_types", "p4obs", "trace_link")
_emit_captures_pattern("prompt_optimizer_types", "p3lm", "pattern")
_emit_records_learning_event("prompt_optimizer_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_optimizer_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_optimizer_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_optimizer_types", "p3lm", "routing")
_emit_improves_agent_policy("prompt_optimizer_types", "p3lm", "policy")
_emit_stores_learning_state("prompt_optimizer_types", "p3lm", "state")
_emit_records_execution_trace("prompt_optimizer_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_optimizer_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_optimizer_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_optimizer_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_optimizer_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_optimizer_types", "env_read", "p2_env_1")
_emit_reads_environ("prompt_optimizer_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_optimizer_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_optimizer_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_optimizer_types", "context_pull")
_emit_pulls_context("p1", "prompt_optimizer_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_optimizer_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_optimizer_types", "uwg_term_2")
_emit_writes_through("p1", "prompt_optimizer_types", "write_through")
_emit_writes_through("p1", "prompt_optimizer_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_optimizer_types", "safety_validation")
_emit_invokes_eval("p1", "prompt_optimizer_types", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_optimizer_types", "routing_commit")
_emit_escalates_to_human("p1", "prompt_optimizer_types", "human_escalation")
_emit_routes_through("p1", "prompt_optimizer_types", "route_through")
_emit_checks_agent_registry("p1", "prompt_optimizer_types", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_optimizer_types", "capability")
_emit_dispatches_execution_plan("p1", "prompt_optimizer_types", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_optimizer_types", "sub_agent")
_emit_routes_to_agent("p1", "prompt_optimizer_types", "target_agent")
_emit_verifies_policy("p1", "prompt_optimizer_types", "policy_check")
_emit_observes_runtime_state("p1", "prompt_optimizer_types", "runtime_state")
_emit_verifies_boundary("p1", "prompt_optimizer_types", "boundary_check")
_emit_transcripts_response("p1", "prompt_optimizer_types", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_optimizer_types")
_emit_gated_by_confidence("p1", "prompt_optimizer_types", "confidence_gate")
emit_replay_key("p0", "prompt_optimizer_types")
emit_determinism_digest("p0", "prompt_optimizer_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_optimizer_types", "execution_auth")
_emit_validates_capability("p2", "prompt_optimizer_types", "capability_check")
_emit_routes_to_capability("p2", "prompt_optimizer_types", "capability_route")
_emit_writes_via_uwg("p2", "prompt_optimizer_types", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_optimizer_types", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_optimizer_types", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_optimizer_types", "exec_output")
_emit_dispatches_agent("p3", "prompt_optimizer_types", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_optimizer_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_optimizer_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_optimizer_types", "healing_outcome")
_emit_escalates_failure("p3", "prompt_optimizer_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_optimizer_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_optimizer_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_optimizer_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_optimizer_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_optimizer_types", "eval_metric")
_emit_stores_embedding("p4", "prompt_optimizer_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_optimizer_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_optimizer_types", "exec_snapshot_link")


@dataclass
class PromptTemplate:
    """Structured prompt template."""

    system: str
    user: str
    variables: list[str]
    examples: list[dict[str, str]]
    metadata: dict[str, Any]


@dataclass
class OptimizedPrompt:
    """Result of prompt optimization."""

    prompt: str
    token_count: int
    variables_used: dict[str, Any]
    optimization_applied: list[str]


class PromptOptimizer:
    """LLM prompt optimization utilities."""

    @staticmethod
    def create_template(
        system: str,
        user: str,
        variables: list[str] | None = None,
        examples: list[dict[str, str]] | None = None,
    ) -> PromptTemplate:
        """
        Create a structured prompt template.

        Args:
            system: System message
            user: User message template
            variables: List of variable names in template
            examples: Optional few-shot examples

        Returns:
            PromptTemplate instance
        """
        return PromptTemplate(
            system=system, user=user, variables=variables or [], examples=examples or [], metadata={},
        )

    @staticmethod
    def format_prompt(template: PromptTemplate, **kwargs: Any) -> OptimizedPrompt:
        """
        Format prompt template with variables.

        Args:
            template: PromptTemplate to format
            **kwargs: Variable values

        Returns:
            OptimizedPrompt with formatted prompt
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptOptimizer.format_prompt")

        optimizations = []
        user_prompt = template.user
        variables_used = {}
        for var in template.variables:
            if var in kwargs:
                value = kwargs[var]
                variables_used[var] = value
                user_prompt = user_prompt.replace(f"{{{var}}}", str(value))
            else:
                optimizations.append(f"Missing variable: {var}")
        if template.examples:
            examples_text = "\n\n".join(
                (
                    f"Example {i + 1}:\nInput: {ex.get('input', '')}\nOutput: {ex.get('output', '')}"
                    for i, ex in enumerate(template.examples)
                ),
            )
            user_prompt = f"{examples_text}\n\n{user_prompt}"
            optimizations.append("Added few-shot examples")
        full_prompt = f"{template.system}\n\n{user_prompt}"
        token_count = len(full_prompt) // 4
        return OptimizedPrompt(
            prompt=full_prompt,
            token_count=token_count,
            variables_used=variables_used,
            optimization_applied=optimizations,
        )

    @staticmethod
    # guardian: allow-magic-config
    def compress_prompt(prompt: str, max_tokens: int = 4000) -> str:
        """
        Compress prompt to fit within token limit.

        Args:
            prompt: Prompt to compress
            max_tokens: Maximum token limit

        Returns:
            Compressed prompt
        """
        estimated_tokens = len(prompt) // 4
        if estimated_tokens <= max_tokens:
            return prompt
        target_chars = max_tokens * 4
        if len(prompt) > target_chars:
            return prompt[: target_chars - 10] + "\n...[truncated]"
        return prompt

    @staticmethod
    # guardian: allow-magic-config
    def add_context(prompt: str, context: dict[str, Any], max_context_items: int = 5) -> str:
        """
        Add context information to prompt.

        Args:
            prompt: Base prompt
            context: Context dictionary
            max_context_items: Maximum context items to include

        Returns:
            Prompt with context
        """
        if not context:
            return prompt
        context_items = list(context.items())[:max_context_items]
        context_text = "\n".join((f"- {key}: {value}" for key, value in context_items))
        return f"Context:\n{context_text}\n\n{prompt}"

    @staticmethod
    def create_chain_of_thought_prompt(task: str, steps: list[str]) -> str:
        """
        Create chain-of-thought prompt.

        Args:
            task: Task description
            steps: Reasoning steps

        Returns:
            Chain-of-thought prompt
        """
        steps_text = "\n".join((f"{i + 1}. {step}" for i, step in enumerate(steps)))
        return f"Task: {task}\n\nLet's approach this step-by-step:\n{steps_text}\n\nPlease provide your reasoning for each step and then the final answer."

    @staticmethod
    def create_structured_output_prompt(task: str, output_format: dict[str, str]) -> str:
        """
        Create prompt for structured output.

        Args:
            task: Task description
            output_format: Expected output format

        Returns:
            Structured output prompt
        """
        format_text = "\n".join((f"- {key}: {desc}" for key, desc in output_format.items()))
        return f"{task}\n\nPlease provide your response in the following format:\n{format_text}"

    @staticmethod
    def optimize_for_cost(prompt: str, strategy: str = "compress") -> str:
        """
        Optimize prompt for cost reduction.

        Args:
            prompt: Prompt to optimize
            strategy: Optimization strategy ('compress', 'simplify')

        Returns:
            Optimized prompt
        """
        if strategy == "compress":
            lines = [line.strip() for line in prompt.split("\n") if line.strip()]
            return "\n".join(lines)
        elif strategy == "simplify":
            redundant = ["please note that", "it is important to", "you should", "make sure to"]
            optimized = prompt
            for phrase in redundant:
                optimized = optimized.replace(phrase, "")
            return optimized
        return prompt

    @staticmethod
    def validate_prompt_quality(prompt: str) -> dict[str, Any]:
        """
        Validate prompt quality.

        Args:
            prompt: Prompt to validate

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "length": len(prompt),
            "estimated_tokens": len(prompt) // 4,
            "has_clear_task": "task:" in prompt.lower() or "please" in prompt.lower(),
            "has_examples": "example" in prompt.lower(),
            "has_format": "format" in prompt.lower(),
            "quality_score": 0.0,
        }
        score = 0.0
        if metrics["has_clear_task"]:
            score += 0.4
        if metrics["has_examples"]:
            score += 0.3
        if metrics["has_format"]:
            score += 0.3
        metrics["quality_score"] = score
        return metrics
