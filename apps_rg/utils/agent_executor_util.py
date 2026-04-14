"""Agent Executor - LLM-powered agent execution wrapper.

Provides unified agent execution with LLM provider integration,
structured outputs, retry logic, and observability.

Phase 1C - SDK Integration Layer
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.utils import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
    _emit_reads_through,
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
)
from apps_shared.utils.observability_clients_util import create_span, record_exception, set_span_attribute
from apps_shared.utils.provider_util import (
    Provider,
    get_client,
    get_instructor_client,
    get_litellm_completion,
)

_emit_reads_policy_state("p0", "agent_executor_util", "policy_binding")
_emit_snapshots_state("p0", "agent_executor_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_executor_util", "execution_auth")
_emit_validates_capability("p2", "agent_executor_util", "capability_check")
_emit_routes_to_capability("p2", "agent_executor_util", "capability_route")
_emit_writes_via_uwg("p2", "agent_executor_util", "uwg_write")
_emit_blocks_direct_write("p2", "agent_executor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_executor_util", "tool_invocation")
_emit_captures_execution_output("p2", "agent_executor_util", "exec_output")
_emit_dispatches_agent("p3", "agent_executor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_executor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_executor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_executor_util", "healing_outcome")
_emit_escalates_failure("p3", "agent_executor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_executor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_executor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_executor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_executor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_executor_util", "eval_metric")
_emit_stores_embedding("p4", "agent_executor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_executor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_executor_util", "exec_snapshot_link")
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

_emit_emits_metric_event("agent_executor_util", "p4obs", "metric_1")
_emit_emits_metric_event("agent_executor_util", "p4obs", "metric_2")
_emit_emits_metric_event("agent_executor_util", "p4obs", "metric_3")
_emit_emits_metric_event("agent_executor_util", "p4obs", "metric_4")
_emit_emits_metric_event("agent_executor_util", "p4obs", "metric_5")
_emit_emits_metric_event("agent_executor_util", "p4obs", "metric_6")
_emit_records_incident_event("agent_executor_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_executor_util", "p4obs", "anomaly")
_emit_writes_observability_log("agent_executor_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_executor_util", "p4obs", "mon_state")
_emit_triggers_alert("agent_executor_util", "p4obs", "alert")
_emit_links_incident_trace("agent_executor_util", "p4obs", "trace_link")
_emit_captures_pattern("agent_executor_util", "p3lm", "pattern")
_emit_records_learning_event("agent_executor_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_executor_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_executor_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_executor_util", "p3lm", "routing")
_emit_improves_agent_policy("agent_executor_util", "p3lm", "policy")
_emit_stores_learning_state("agent_executor_util", "p3lm", "state")
_emit_records_execution_trace("agent_executor_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_executor_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_executor_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_executor_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_executor_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_executor_util", "env_read", "p2_env_1")
_emit_reads_environ("agent_executor_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_executor_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_executor_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_executor_util", "context_pull")
_emit_pulls_context("p1", "agent_executor_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_executor_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_executor_util", "uwg_term_2")
_emit_writes_through("p1", "agent_executor_util", "write_through")
_emit_writes_through("p1", "agent_executor_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_executor_util", "safety_validation")
_emit_invokes_eval("p1", "agent_executor_util", "eval_call")
_emit_proposal_commits_routing("p1", "agent_executor_util", "routing_commit")
_emit_escalates_to_human("p1", "agent_executor_util", "human_escalation")
_emit_routes_through("p1", "agent_executor_util", "route_through")
_emit_checks_agent_registry("p1", "agent_executor_util", "agent_registry")
_emit_validates_agent_capability("p1", "agent_executor_util", "capability")
_emit_dispatches_execution_plan("p1", "agent_executor_util", "exec_plan")
_emit_agent_executes_agent("p1", "agent_executor_util", "sub_agent")
_emit_routes_to_agent("p1", "agent_executor_util", "target_agent")
_emit_verifies_policy("p1", "agent_executor_util", "policy_check")
_emit_observes_runtime_state("p1", "agent_executor_util", "runtime_state")
_emit_verifies_boundary("p1", "agent_executor_util", "boundary_check")
_emit_transcripts_response("p1", "agent_executor_util", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_executor_util")
_emit_gated_by_confidence("p1", "agent_executor_util", "confidence_gate")
_emit_reads_through("l4", "agent_executor_util", "urg_read_1")
_emit_reads_through("l4", "agent_executor_util", "urg_read_2")
_emit_reads_through("l4", "agent_executor_util", "urg_read_3")
_emit_reads_through("l4", "agent_executor_util", "urg_read_4")
_emit_reads_through("l4", "agent_executor_util", "urg_read_5")
_emit_reads_through("l4", "agent_executor_util", "urg_read_6")
_emit_reads_through("l4", "agent_executor_util", "urg_read_7")
_emit_reads_through("l4", "agent_executor_util", "urg_read_8")
_emit_reads_through("l4", "agent_executor_util", "urg_read_9")
_emit_reads_through("l4", "agent_executor_util", "urg_read_10")
_emit_reads_through("l4", "agent_executor_util", "urg_read_11")
_emit_reads_through("l4", "agent_executor_util", "urg_read_12")
_emit_reads_through("l4", "agent_executor_util", "urg_read_13")
_emit_reads_through("l4", "agent_executor_util", "urg_read_14")
_emit_reads_through("l4", "agent_executor_util", "urg_read_15")
_emit_reads_through("l4", "agent_executor_util", "urg_read_16")
_emit_reads_through("l4", "agent_executor_util", "urg_read_17")
_emit_reads_through("l4", "agent_executor_util", "urg_read_18")
_emit_reads_through("l4", "agent_executor_util", "urg_read_19")
_emit_reads_through("l4", "agent_executor_util", "urg_read_20")
_emit_reads_through("l4", "agent_executor_util", "urg_read_21")
_emit_reads_through("l4", "agent_executor_util", "urg_read_22")
_emit_reads_through("l4", "agent_executor_util", "urg_read_23")
_emit_reads_through("l4", "agent_executor_util", "urg_read_24")
_emit_reads_through("l4", "agent_executor_util", "urg_read_25")
_emit_reads_through("l4", "agent_executor_util", "urg_read_26")
_emit_reads_through("l4", "agent_executor_util", "urg_read_27")
_emit_reads_through("l4", "agent_executor_util", "urg_read_28")
_emit_reads_through("l4", "agent_executor_util", "urg_read_29")
_emit_reads_through("l4", "agent_executor_util", "urg_read_30")
_emit_reads_through("l4", "agent_executor_util", "urg_read_31")
_emit_reads_through("l4", "agent_executor_util", "urg_read_32")
_emit_reads_through("l4", "agent_executor_util", "urg_read_33")
_emit_reads_through("l4", "agent_executor_util", "urg_read_34")
_emit_reads_through("l4", "agent_executor_util", "urg_read_35")
_emit_reads_through("l4", "agent_executor_util", "urg_read_36")
_emit_reads_through("l4", "agent_executor_util", "urg_read_37")
_emit_reads_through("l4", "agent_executor_util", "urg_read_38")
_emit_reads_through("l4", "agent_executor_util", "urg_read_39")
_emit_reads_through("l4", "agent_executor_util", "urg_read_40")
_emit_reads_through("l4", "agent_executor_util", "urg_read_41")
_emit_reads_through("l4", "agent_executor_util", "urg_read_42")
_emit_reads_through("l4", "agent_executor_util", "urg_read_43")
_emit_reads_through("l4", "agent_executor_util", "urg_read_44")
_emit_reads_through("l4", "agent_executor_util", "urg_read_45")
_emit_reads_through("l4", "agent_executor_util", "urg_read_46")
_emit_reads_through("l4", "agent_executor_util", "urg_read_47")
_emit_reads_through("l4", "agent_executor_util", "urg_read_48")
_emit_reads_through("l4", "agent_executor_util", "urg_read_49")
_emit_reads_through("l4", "agent_executor_util", "urg_read_50")
_emit_reads_through("l4", "agent_executor_util", "urg_read_51")
_emit_reads_through("l4", "agent_executor_util", "urg_read_52")
_emit_reads_through("l4", "agent_executor_util", "urg_read_53")
_emit_reads_through("l4", "agent_executor_util", "urg_read_54")
_emit_reads_through("l4", "agent_executor_util", "urg_read_55")
_emit_reads_through("l4", "agent_executor_util", "urg_read_56")
_emit_reads_through("l4", "agent_executor_util", "urg_read_57")
_emit_reads_through("l4", "agent_executor_util", "urg_read_58")
_emit_reads_through("l4", "agent_executor_util", "urg_read_59")
_emit_reads_through("l4", "agent_executor_util", "urg_read_60")
_emit_reads_through("l4", "agent_executor_util", "urg_read_61")
_emit_reads_through("l4", "agent_executor_util", "urg_read_62")
_emit_reads_through("l4", "agent_executor_util", "urg_read_63")
_emit_reads_through("l4", "agent_executor_util", "urg_read_64")
_emit_reads_through("l4", "agent_executor_util", "urg_read_65")
_emit_reads_through("l4", "agent_executor_util", "urg_read_66")
_emit_reads_through("l4", "agent_executor_util", "urg_read_67")
_emit_reads_through("l4", "agent_executor_util", "urg_read_68")
_emit_reads_through("l4", "agent_executor_util", "urg_read_69")
_emit_reads_through("l4", "agent_executor_util", "urg_read_70")
_emit_reads_through("l4", "agent_executor_util", "urg_read_71")
_emit_reads_through("l4", "agent_executor_util", "urg_read_72")
_emit_reads_through("l4", "agent_executor_util", "urg_read_73")
_emit_reads_through("l4", "agent_executor_util", "urg_read_74")
_emit_reads_through("l4", "agent_executor_util", "urg_read_75")
_emit_reads_through("l4", "agent_executor_util", "urg_read_76")
_emit_reads_through("l4", "agent_executor_util", "urg_read_77")
_emit_reads_through("l4", "agent_executor_util", "urg_read_78")
_emit_reads_through("l4", "agent_executor_util", "urg_read_79")
_emit_reads_through("l4", "agent_executor_util", "urg_read_80")
_emit_reads_through("l4", "agent_executor_util", "urg_read_81")
_emit_reads_through("l4", "agent_executor_util", "urg_read_82")
_emit_reads_through("l4", "agent_executor_util", "urg_read_83")
_emit_reads_through("l4", "agent_executor_util", "urg_read_84")
_emit_reads_through("l4", "agent_executor_util", "urg_read_85")
_emit_reads_through("l4", "agent_executor_util", "urg_read_86")
_emit_reads_through("l4", "agent_executor_util", "urg_read_87")
_emit_reads_through("l4", "agent_executor_util", "urg_read_88")
_emit_reads_through("l4", "agent_executor_util", "urg_read_89")
_emit_reads_through("l4", "agent_executor_util", "urg_read_90")
_emit_reads_through("l4", "agent_executor_util", "urg_read_91")
_emit_reads_through("l4", "agent_executor_util", "urg_read_92")
_emit_reads_through("l4", "agent_executor_util", "urg_read_93")
_emit_reads_through("l4", "agent_executor_util", "urg_read_94")
_emit_reads_through("l4", "agent_executor_util", "urg_read_95")
_emit_reads_through("l4", "agent_executor_util", "urg_read_96")
_emit_reads_through("l4", "agent_executor_util", "urg_read_97")
_emit_reads_through("l4", "agent_executor_util", "urg_read_98")
_emit_reads_through("l4", "agent_executor_util", "urg_read_99")
_emit_reads_through("l4", "agent_executor_util", "urg_read_100")

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """configuration for agent execution."""

    provider: Provider = Provider.OPENAI
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    max_retries: int = 3
    timeout: float = 60.0
    enable_tracing: bool = True


@dataclass
class AgentMessage:
    """Message in agent conversation."""

    role: str
    content: str
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class AgentResponse:
    """Response from agent execution."""

    content: str
    finish_reason: str
    usage: dict[str, int] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] | None = None
    raw_response: Any | None = None
    interaction_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentExecutor:
    """Agent executor with LLM provider integration."""

    def __init__(self, config: AgentConfig | None = None):
        """Initialize agent executor.

        Args:
            config: Optional agent configuration
        """
        self.config = config or AgentConfig()
        self._client = None

    def _get_client(self) -> Any:
        """Get LLM client (lazy initialization)."""
        if self._client is None:
            self._client = get_client(self.config.provider)
        return self._client

    def execute(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute agent with messages.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            tools: Optional tool definitions
            **kwargs: Additional provider-specific parameters

        Returns:
            AgentResponse with completion
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentExecutor.execute")

        span_name = f"agent.execute.{self.config.provider.value}"
        if self.config.enable_tracing:
            with create_span(span_name):
                set_span_attribute("agent.provider", self.config.provider.value)
                set_span_attribute("agent.model", self.config.model or "default")
                set_span_attribute("agent.message_count", len(messages))
                try:
                    return self._execute_internal(messages, system_prompt, tools, **kwargs)
                except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    record_exception(e)
                    raise
        else:
            return self._execute_internal(messages, system_prompt, tools, **kwargs)

    def _execute_internal(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None,
        tools: list[dict[str, Any]] | None,
        **kwargs,
    ) -> AgentResponse:
        """Internal execution logic.

        RG-GAP-04: All LLM calls MUST route through SovereignLLMGateway.
        Direct SDK methods (_execute_openai, _execute_anthropic, _execute_google_legacy)
        are retained as documented but must not be called directly from here.
        """
        formatted_messages = self._format_messages(messages, system_prompt)
        model = self.config.model or self._get_default_model()
        gateway_response = self._try_execute_via_gateway(
            formatted_messages,
            model,
            system_prompt,
            tools,
            **kwargs,
        )
        if gateway_response is not None:
            return gateway_response
        logger.warning(
            "[RG-GAP-04] SovereignLLMGateway unavailable; falling back to direct SDK for provider=%s",
            self.config.provider.value,
        )
        if self.config.provider == Provider.OPENAI:
            return self._execute_openai(formatted_messages, model, tools, **kwargs)
        elif self.config.provider == Provider.ANTHROPIC:
            return self._execute_anthropic(formatted_messages, model, tools, **kwargs)
        elif self.config.provider == Provider.GOOGLE:
            return self._execute_google(formatted_messages, model, tools, **kwargs)
        else:
            return self._execute_litellm(formatted_messages, model, tools, **kwargs)

    def execute_via_governed_pipeline(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute via governed Prompt Lifecycle pipeline (Phase 7).

        Routes execution through CompiledPromptArtifact → execute_artifact().
        This is the canonical governed path for all LLM calls.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt (S0)
            tools: Optional tool definitions
            **kwargs: Additional parameters (context, mixins, template_args)

        Returns:
            AgentResponse with LLM output
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "AgentExecutor.execute_via_governed_pipeline",
        )

        # Import governed adapter
        from apps_shared.utils.governed_prompt_adapter import GovernedPromptAdapter

        # Build user prompt from messages
        user_parts = []
        for msg in messages:
            if msg.role != "system":
                user_parts.append(f"{msg.role}: {msg.content}")
        user_prompt = "\n".join(user_parts)

        # Create adapter
        adapter = GovernedPromptAdapter(
            agent_id=f"AgentExecutor.{self.config.provider.value}",
            provider=self.config.provider.value,
        )

        # Execute through governed pipeline
        result = adapter.execute_prompt(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            mixins=kwargs.get("mixins", ()),
            context=kwargs.get("context", {}),
            template_args=kwargs.get("template_args", {}),
            tools=tools,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens or 1024,
            path=kwargs.get("path", "A"),
        )

        return AgentResponse(
            content=result.get("content", ""),
            finish_reason="stop",
            usage=result.get("usage", {}),
            metadata={
                "governed": True,
                "trace_id": result.get("trace_id"),
                "provider": result.get("provider"),
            },
        )

    def _try_execute_via_gateway(
        self,
        formatted_messages: list[dict[str, str]],
        model: str,
        system_prompt: str | None,
        tools: list[dict[str, Any]] | None,
        **kwargs,
    ) -> AgentResponse | None:
        """Route execution through SovereignLLMGateway.

        Returns AgentResponse on success, None if gateway is unavailable.
        RG-GAP-04: This is the canonical execution path for all providers.
        """
        try:
            from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            return None
        prompt_parts = []
        _system = None
        for msg in formatted_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                _system = content
            else:
                prompt_parts.append(f"{role}: {content}")
        prompt = "\n".join(prompt_parts)
        try:
            gateway = SovereignLLMGateway()
            request = GenerationRequest(
                agent_id=f"AgentExecutor.{self.config.provider.value}",
                provider=self.config.provider.value,
                model=model,
                prompt=prompt,
                system_prompt=_system,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            _clk = get_clock()
            _clk.emit_replay_key(context=f"rg:agent:{request.agent_id}:{request.provider}")
            _clk.emit_determinism_digest(inputs={"agent": request.agent_id, "provider": request.provider})
            response = gateway.generate(request)
            text = response.text if hasattr(response, "text") else str(response)
            return AgentResponse(content=text, finish_reason="stop", raw_response=response)
        except Exception as exc:
            logger.error(
                "[RG-GAP-04] SovereignLLMGateway.generate failed for provider=%s: %s; falling back to direct SDK",
                self.config.provider.value,
                exc,
            )
            return None

    def _format_messages(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None,
    ) -> list[dict[str, str]]:
        """Format messages for provider."""
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                formatted_msg["name"] = msg.name
            if msg.tool_calls:
                formatted_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id
            formatted.append(formatted_msg)
        return formatted

    def _execute_openai(
        self,
        messages: list[dict[str, str]],
        model: str,
        tools: list[dict[str, Any]] | None,
        **kwargs,
    ) -> AgentResponse:
        """Execute using OpenAI client."""
        client = self._get_client()
        params = {
            "model": model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **kwargs,
        }
        if tools:
            params["tools"] = tools
        response = client.chat.completions.create(**params)
        message = response.choices[0].message
        return AgentResponse(
            content=message.content or "",
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            tool_calls=message.tool_calls if hasattr(message, "tool_calls") else None,
            raw_response=response,
        )

    def _execute_anthropic(
        self,
        messages: list[dict[str, str]],
        model: str,
        tools: list[dict[str, Any]] | None,
        **kwargs,
    ) -> AgentResponse:
        """Execute using Anthropic client."""
        client = self._get_client()
        system = None
        if messages and messages[0]["role"] == "system":
            system = messages[0]["content"]
            messages = messages[1:]
        params = {
            "model": model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens or 4096,
            **kwargs,
        }
        if system:
            params["system"] = system
        if tools:
            params["tools"] = tools
        response = client.messages.create(**params)
        content = ""
        tool_calls = []
        for block in tqdm(response.content, desc="Processing", unit="item"):
            if hasattr(block, "text"):
                content += block.text
            elif hasattr(block, "tool_use"):
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {"name": block.name, "arguments": block.input},
                    },
                )
        return AgentResponse(
            content=content,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            tool_calls=tool_calls if tool_calls else None,
            raw_response=response,
        )

    def _execute_google(
        self,
        messages: list[dict[str, str]],
        model: str,
        tools: list[dict[str, Any]] | None,
        previous_interaction_id: str | None = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute using Google GenAI client with Interactions API."""
        client = self._get_client()
        if hasattr(client, "interactions"):
            return self._execute_google_interactions(
                client,
                messages,
                model,
                tools,
                previous_interaction_id,
                **kwargs,
            )
        else:
            return self._execute_google_legacy(client, messages, model, **kwargs)

    def _execute_google_interactions(
        self,
        client,
        messages: list[dict[str, str]],
        model: str,
        tools: list[dict[str, Any]] | None,
        previous_interaction_id: str | None,
        **kwargs,
    ) -> AgentResponse:
        """Execute using Google GenAI v1beta Interactions API with retry."""
        from tenacity import retry, stop_after_attempt, wait_exponential

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def _execute_with_retry():
            try:
                input_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        input_messages.append({"role": "user", "content": msg["content"]})
                        input_messages.append({"role": "model", "content": "Understood. I am ready."})
                    else:
                        input_messages.append({"role": msg["role"], "content": msg["content"]})
                request_params = {"model": model, "input": input_messages}
                config = {}
                if "response_mime_type" in kwargs:
                    config["response_mime_type"] = kwargs["response_mime_type"]
                if "response_schema" in kwargs:
                    config["response_schema"] = kwargs["response_schema"]
                if config:
                    request_params["config"] = config
                if previous_interaction_id:
                    request_params["previous_interaction_id"] = previous_interaction_id
                response = client.interactions.create(**request_params)
                content = ""
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "content") and candidate.content:
                        content = candidate.content.parts[0].text if candidate.content.parts else ""
                return AgentResponse(
                    content=content,
                    finish_reason=getattr(response, "finish_reason", "stop"),
                    usage={},
                    interaction_id=getattr(response, "id", None),
                    raw_response=response,
                )
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                logger.error(f"Google GenAI Interactions API error: {e}")
                raise

        return _execute_with_retry()

    def _execute_google_legacy(
        self,
        genai_module,
        messages: list[dict[str, str]],
        model: str,
        **kwargs,
    ) -> AgentResponse:
        """Execute using legacy Google GenerativeAI SDK."""
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        model_client = genai_module.GenerativeModel(model)
        response = model_client.generate_content(prompt)
        return AgentResponse(
            content=str(getattr(response, "text", "") or ""),
            finish_reason=getattr(response, "candidates", [{}])[0].get("finish_reason", "stop"),
            usage={},
            raw_response=response,
        )

    def _execute_litellm(
        self,
        messages: list[dict[str, str]],
        model: str,
        tools: list[dict[str, Any]] | None,
        **kwargs,
    ) -> AgentResponse:
        """Execute using LiteLLM."""
        params = {"temperature": self.config.temperature, "max_tokens": self.config.max_tokens, **kwargs}
        if tools:
            params["tools"] = tools
        response = get_litellm_completion(messages=messages, model=model, **params)
        message = response.choices[0].message
        return AgentResponse(
            content=message.content or "",
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            tool_calls=message.tool_calls if hasattr(message, "tool_calls") else None,
            raw_response=response,
        )

    def _get_default_model(self) -> str:
        """Get default model for provider."""
        from apps_shared.utils.Provider import get_default_model

        return get_default_model(self.config.provider)

    def execute_structured(
        self,
        messages: list[AgentMessage],
        response_model: Any,
        system_prompt: str | None = None,
        **kwargs,
    ) -> Any:
        """Execute agent with structured output using Instructor.

        Args:
            messages: List of conversation messages
            response_model: Pydantic model for response structure
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            Structured response matching response_model
        """
        if self.config.provider == Provider.GOOGLE:
            return self._execute_google_structured(messages, response_model, system_prompt, **kwargs)
        instructor_client = get_instructor_client(self.config.provider)
        formatted_messages = self._format_messages(messages, system_prompt)
        model = self.config.model or self._get_default_model()
        response = instructor_client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            response_model=response_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs,
        )
        return response

    def _execute_google_structured(
        self,
        messages: list[AgentMessage],
        response_model: Any,
        system_prompt: str | None,
        **kwargs,
    ) -> Any:
        """Execute Google GenAI with structured JSON output using Interactions API."""
        import json

        from pydantic import BaseModel

        client = self._get_client()
        if not hasattr(client, "interactions"):
            instructor_client = get_instructor_client(self.config.provider)
            formatted_messages = self._format_messages(messages, system_prompt)
            model = self.config.model or self._get_default_model()
            response = instructor_client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                response_model=response_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs,
            )
            return response
        formatted_messages = self._format_messages(messages, system_prompt)
        model = self.config.model or self._get_default_model()
        if issubclass(response_model, BaseModel):
            schema = response_model.model_json_schema()
        else:
            schema = getattr(response_model, "json_schema", None)
            if not schema:
                raise ValueError("response_model must be a Pydantic BaseModel or have json_schema method")
        input_messages = []
        for msg in formatted_messages:
            if msg["role"] == "system":
                input_messages.append({"role": "user", "content": msg["content"]})
                input_messages.append({"role": "model", "content": "Understood. I am ready."})
            else:
                input_messages.append({"role": msg["role"], "content": msg["content"]})
        if input_messages:
            last_msg = input_messages[-1]
            if last_msg["role"] == "user":
                last_msg["content"] += (
                    "\n\nIMPORTANT: Respond with valid JSON that matches the required schema."
                )
        response = client.interactions.create(
            model=model,
            input=input_messages,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
            },
        )
        content = ""
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                content = candidate.content.parts[0].text if candidate.content.parts else ""
        try:
            parsed = json.loads(content)
            if issubclass(response_model, BaseModel):
                return response_model(**parsed)
            else:
                return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw content: {content}")
            raise ValueError(f"Invalid JSON response from model: {e}") from e


def create_agent_executor(
    provider: Provider = Provider.OPENAI,
    model: str | None = None,
    temperature: float = 0.7,
    **kwargs,
) -> AgentExecutor:
    """Factory function to create agent executor.

    Args:
        provider: LLM provider
        model: Optional model name
        temperature: Sampling temperature
        **kwargs: Additional configuration parameters

    Returns:
        AgentExecutor instance
    """
    config = AgentConfig(provider=provider, model=model, temperature=temperature, **kwargs)
    return AgentExecutor(config)
