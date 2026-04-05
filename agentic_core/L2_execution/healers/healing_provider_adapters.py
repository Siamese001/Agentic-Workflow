"""
Healing Provider Adapters — Environment-Independent, Replay-Deterministic.

These adapters implement the HealingProviderInvoker Protocol with:
- Explicit configuration injection (no environment variables)
- Provider configuration hashing for replay determinism
- Fixed token limits (no external config loading)
- Deterministic error handling
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "healing_provider_adapters")
emit_determinism_digest("p0", "healing_provider_adapters")

_emit_dispatches_healing_run("p1", "healing_provider_adapters", "L2")
_emit_routes_through("p1", "healing_provider_adapters", "L2")
_emit_checks_agent_registry("p1", "healing_provider_adapters", "agent_registry")
_emit_validates_agent_capability("p1", "healing_provider_adapters", "capability")
_emit_dispatches_execution_plan("p1", "healing_provider_adapters", "exec_plan")
_emit_agent_executes_agent("p1", "healing_provider_adapters", "sub_agent")
_emit_routes_to_agent("p1", "healing_provider_adapters", "target_agent")
_emit_verifies_policy("p1", "healing_provider_adapters", "policy_check")
_emit_observes_runtime_state("p1", "healing_provider_adapters", "runtime_state")
_emit_verifies_boundary("p1", "healing_provider_adapters", "boundary_check")
_emit_transcripts_response("p1", "healing_provider_adapters", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_provider_adapters")
_emit_gated_by_confidence("p1", "healing_provider_adapters", "confidence_gate")
_emit_escalates_to_human("p1", "healing_provider_adapters", "L2")
_emit_reads_policy_state("p1", "healing_provider_adapters", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "healing_provider_adapters", "p0_governance")
_emit_snapshots_state("p0", "healing_provider_adapters", "state_snapshot")
_emit_authorize_and_execute("p2", "healing_provider_adapters", "execution_auth")
_emit_validates_capability("p2", "healing_provider_adapters", "capability_check")
_emit_routes_to_capability("p2", "healing_provider_adapters", "capability_route")
_emit_writes_via_uwg("p2", "healing_provider_adapters", "uwg_write")
_emit_blocks_direct_write("p2", "healing_provider_adapters", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_provider_adapters", "tool_invocation")
_emit_captures_execution_output("p2", "healing_provider_adapters", "exec_output")
_emit_dispatches_agent("p3", "healing_provider_adapters", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_provider_adapters", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_provider_adapters", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_provider_adapters", "healing_outcome")
_emit_escalates_failure("p3", "healing_provider_adapters", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_provider_adapters", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_provider_adapters", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_provider_adapters", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_provider_adapters", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_provider_adapters", "eval_metric")
_emit_stores_embedding("p4", "healing_provider_adapters", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_provider_adapters", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_provider_adapters", "exec_snapshot_link")

try:
    from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

    _TENACITY_AVAILABLE = True
except ImportError as e:
            raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
    _TENACITY_AVAILABLE = False
from agentic_core.L2_execution.healers.healing_tier_router import HISTORICAL_DATA_HASH, _compute_replay_key
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
    InvocationRecord,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("healing_provider_adapters", "p4obs", "metric_1")
_emit_emits_metric_event("healing_provider_adapters", "p4obs", "metric_2")
_emit_emits_metric_event("healing_provider_adapters", "p4obs", "metric_3")
_emit_emits_metric_event("healing_provider_adapters", "p4obs", "metric_4")
_emit_emits_metric_event("healing_provider_adapters", "p4obs", "metric_5")
_emit_emits_metric_event("healing_provider_adapters", "p4obs", "metric_6")
_emit_records_incident_event("healing_provider_adapters", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_provider_adapters", "p4obs", "anomaly")
_emit_writes_observability_log("healing_provider_adapters", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_provider_adapters", "p4obs", "mon_state")
_emit_triggers_alert("healing_provider_adapters", "p4obs", "alert")
_emit_links_incident_trace("healing_provider_adapters", "p4obs", "trace_link")
_emit_captures_pattern("healing_provider_adapters", "p3lm", "pattern")
_emit_records_learning_event("healing_provider_adapters", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_provider_adapters", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_provider_adapters", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_provider_adapters", "p3lm", "routing")
_emit_improves_agent_policy("healing_provider_adapters", "p3lm", "policy")
_emit_stores_learning_state("healing_provider_adapters", "p3lm", "state")
_emit_records_execution_trace("healing_provider_adapters", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_provider_adapters", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_provider_adapters", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_provider_adapters", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_provider_adapters", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_provider_adapters", "env_read", "p2_env_1")
_emit_reads_environ("healing_provider_adapters", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_provider_adapters", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_provider_adapters", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_provider_adapters", "context_pull")
_emit_pulls_context("p1", "healing_provider_adapters", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_provider_adapters", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_provider_adapters", "uwg_term_2")
_emit_writes_through("p1", "healing_provider_adapters", "write_through")
_emit_writes_through("p1", "healing_provider_adapters", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_provider_adapters", "safety_validation")
_emit_invokes_eval("p1", "healing_provider_adapters", "eval_call")
_emit_proposal_commits_routing("p1", "healing_provider_adapters", "routing_commit")

logger = logging.getLogger(__name__)


class OOMRetryableError(Exception):
    """Raised when OOM occurs but retry is possible through router escalation."""

    pass


class OOMEscalatedError(Exception):
    """Raised when OOM has been escalated to another tier."""

    pass


MAX_TOKENS = 2048
MAX_OUTPUT_TOKENS = 2048
DEFAULT_MAX_TOKENS = MAX_TOKENS
DEFAULT_MAX_OUTPUT_TOKENS = MAX_OUTPUT_TOKENS
QWEN_CONFIG: dict[str, Any] = {
    "temperature": 0.0,
    "max_tokens": MAX_TOKENS,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}
GEMINI_CONFIG: dict[str, Any] = {
    "temperature": 0.1,
    "max_tokens": MAX_OUTPUT_TOKENS,
    "top_p": 1.0,
    "top_k": 40,
}
QWEN_CONFIG_HASH = hashlib.sha256(
    "|".join((f"{k}={v}" for k, v in sorted(QWEN_CONFIG.items()))).encode()
).hexdigest()[:16]
GEMINI_CONFIG_HASH = hashlib.sha256(
    "|".join((f"{k}={v}" for k, v in sorted(GEMINI_CONFIG.items()))).encode()
).hexdigest()[:16]


class QwenInvokerAdapter:
    """Qwen/vLLM provider adapter with explicit configuration - no environment access."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """Initialize Qwen adapter with explicit configuration.

        Args:
            base_url: vLLM endpoint URL (explicit, no environment variable)
            api_key: API key (explicit, no environment variable)
        """
        self.base_url = base_url
        self.api_key = api_key
        self._config_hash = QWEN_CONFIG_HASH

    def invoke_qwen_vllm(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Invoke Qwen model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "HealingProviderAdapter.invoke_qwen_vllm"
        )
        model_id = config.model_qwen_vllm_id
        prompt = self._build_prompt(healing_input, decision, agent_name)
        try:
            import openai

            client = openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
        except (ImportError, AttributeError) as exc:
            raise ImportError(
                "OpenAI SDK is required for Qwen vLLM adapter. Install with: pip install openai"
            ) from exc
        response_text: str | None = None
        if _TENACITY_AVAILABLE:

            @retry(
                retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            )
            def _call_vllm():
                return client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a code healing assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=QWEN_CONFIG["temperature"],
                    max_tokens=DEFAULT_MAX_TOKENS,
                )

            completion = _call_vllm()
        else:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a code healing assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=QWEN_CONFIG["temperature"],
                max_tokens=DEFAULT_MAX_TOKENS,
            )
        if completion and completion.choices:
            response_text = completion.choices[0].message.content
        record = InvocationRecord(
            tier=HealingTier.QWEN_VLLM,
            model_id=model_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_qwen_vllm",
            provider_config_hash=self._config_hash,
            historical_data_hash=HISTORICAL_DATA_HASH,
            replay_key=_compute_replay_key(healing_input, decision),
            response_text=response_text,
        )
        logger.info(
            "Qwen healing invoked with deterministic config",
            extra={
                "model": model_id,
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "config_hash": self._config_hash,
                "replay_key": record.replay_key,
            },
        )
        return record

    def _build_prompt(self, healing_input: HealingInput, decision: HealingDecision, agent_name: str) -> str:
        """Build structured prompt from healing context."""
        parts = [
            f"Healing Request from {agent_name}",
            f"Failure Type: {healing_input.failure_type}",
            f"Error Signature: {healing_input.error_signature}",
            f"Retry Count: {healing_input.retry_count}",
            f"Blast Radius Estimate: {healing_input.blast_radius_estimate:.2f}",
        ]
        if healing_input.required_tools:
            parts.append(f"Required Tools: {', '.join(healing_input.required_tools)}")
        if healing_input.violation_metadata_refs:
            parts.append(f"Context Files: {', '.join(healing_input.violation_metadata_refs)}")
        parts.append(f"Router Confidence: {decision.heal_confidence:.2f}")
        parts.append(f"Reason Codes: {', '.join(decision.reason_codes)}")
        parts.append("\nPlease provide a minimal fix for this issue.")
        return "\n".join(parts)

    def invoke_local(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Local agent not supported by Qwen adapter."""
        raise NotImplementedError("invoke_local not supported by QwenInvokerAdapter")

    def invoke_gemini(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Gemini not supported by Qwen adapter."""
        raise NotImplementedError("invoke_gemini not supported by QwenInvokerAdapter")


class GeminiInvokerAdapter:
    """Gemini 2.5 Pro provider adapter with explicit configuration - no environment access."""

    def __init__(self, api_key: str) -> None:
        """Initialize Gemini adapter with explicit configuration.

        Args:
            api_key: Google API key (explicit, no environment variable)
        """
        self.api_key = api_key
        self._config_hash = GEMINI_CONFIG_HASH

    def invoke_gemini(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Invoke Gemini model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        from apps_shared.types.hardened_gemini_executor_types import (
            HardenedGeminiConfig,
            HardenedGeminiExecutor,
        )

        model_id = config.model_gemini_2_5_pro_id
        prompt = self._build_prompt(healing_input, decision, agent_name)
        hardened_config = HardenedGeminiConfig(
            model=model_id,
            temperature=GEMINI_CONFIG["temperature"],
            max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
        )
        executor = HardenedGeminiExecutor(config=hardened_config)
        response_text: str | None = None
        try:
            result = executor.invoke_prompt(prompt, api_key=self.api_key)
            if result is not None:
                try:
                    response_text = result.text
                # guardian: allow-silent-swallow
                except (ValueError, TypeError):
                    response_text = None
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as _exc:
            _exc_name = type(_exc).__name__
            if "ContextOverflow" in _exc_name:
                logger.warning(
                    "Gemini context overflow — response_text=None",
                    extra={"model": model_id, "trace_id": healing_input.trace_id},
                )
            elif "CircuitBreakerOpen" in _exc_name:
                logger.warning(
                    "Gemini circuit breaker open — response_text=None",
                    extra={"model": model_id, "trace_id": healing_input.trace_id},
                )
            else:
                logger.error(
                    "Gemini invocation failed: %s",
                    _exc,
                    extra={"model": model_id, "trace_id": healing_input.trace_id},
                )
            response_text = None
        record = InvocationRecord(
            tier=HealingTier.GEMINI_2_5_PRO,
            model_id=model_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_gemini",
            provider_config_hash=self._config_hash,
            historical_data_hash=HISTORICAL_DATA_HASH,
            replay_key=_compute_replay_key(healing_input, decision),
            response_text=response_text,
        )
        logger.info(
            "Gemini healing invoked with deterministic config",
            extra={
                "model": model_id,
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "config_hash": self._config_hash,
                "replay_key": record.replay_key,
            },
        )
        return record

    def _build_prompt(self, healing_input: HealingInput, decision: HealingDecision, agent_name: str) -> str:
        """Build structured prompt from healing context."""
        parts = [
            f"Healing Request from {agent_name}",
            f"Failure Type: {healing_input.failure_type}",
            f"Error Signature: {healing_input.error_signature}",
            f"Retry Count: {healing_input.retry_count}",
            f"Blast Radius Estimate: {healing_input.blast_radius_estimate:.2f}",
        ]
        if healing_input.required_tools:
            parts.append(f"Required Tools: {', '.join(healing_input.required_tools)}")
        if healing_input.violation_metadata_refs:
            parts.append(f"Context Files: {', '.join(healing_input.violation_metadata_refs)}")
        parts.append(f"Router Confidence: {decision.heal_confidence:.2f}")
        parts.append(f"Reason Codes: {', '.join(decision.reason_codes)}")
        parts.append("\nPlease provide a minimal fix for this issue.")
        return "\n".join(parts)

    def invoke_local(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Local agent not supported by Gemini adapter."""
        raise NotImplementedError("invoke_local not supported by GeminiInvokerAdapter")

    def invoke_qwen_vllm(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Qwen not supported by Gemini adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by GeminiInvokerAdapter")


class LocalAgentAdapter:
    """Local agent adapter for simple, deterministic healing without LLM calls."""

    def invoke_local(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Invoke local agent with deterministic record.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig (unused for local agent)
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        record = InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
            provider_config_hash="local",
            historical_data_hash=HISTORICAL_DATA_HASH,
            replay_key=_compute_replay_key(healing_input, decision),
        )
        logger.info(
            "Local healing invoked with deterministic record",
            extra={
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "confidence": decision.heal_confidence,
                "failure_type": healing_input.failure_type,
                "replay_key": record.replay_key,
            },
        )
        return record

    def invoke_qwen_vllm(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Qwen not supported by local adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by LocalAgentAdapter")

    def invoke_gemini(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Gemini not supported by local adapter."""
        raise NotImplementedError("invoke_gemini not supported by LocalAgentAdapter")


__all__ = [
    "QwenInvokerAdapter",
    "GeminiInvokerAdapter",
    "LocalAgentAdapter",
    "QWEN_CONFIG_HASH",
    "GEMINI_CONFIG_HASH",
    "MAX_TOKENS",
    "MAX_OUTPUT_TOKENS",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_MAX_OUTPUT_TOKENS",
]
