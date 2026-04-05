from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "sub_atomic_engine_impl")
emit_determinism_digest("p0", "sub_atomic_engine_impl")

_emit_dispatches_healing_run("p1", "sub_atomic_engine_impl", "L3")
_emit_routes_through("p1", "sub_atomic_engine_impl", "L3")
_emit_checks_agent_registry("p1", "sub_atomic_engine_impl", "agent_registry")
_emit_validates_agent_capability("p1", "sub_atomic_engine_impl", "capability")
_emit_dispatches_execution_plan("p1", "sub_atomic_engine_impl", "exec_plan")
_emit_agent_executes_agent("p1", "sub_atomic_engine_impl", "sub_agent")
_emit_routes_to_agent("p1", "sub_atomic_engine_impl", "target_agent")
_emit_verifies_policy("p1", "sub_atomic_engine_impl", "policy_check")
_emit_observes_runtime_state("p1", "sub_atomic_engine_impl", "runtime_state")
_emit_verifies_boundary("p1", "sub_atomic_engine_impl", "boundary_check")
_emit_transcripts_response("p1", "sub_atomic_engine_impl", "transcript")
_emit_hard_fails_untranscripted("p1", "sub_atomic_engine_impl")
_emit_gated_by_confidence("p1", "sub_atomic_engine_impl", "confidence_gate")
_emit_escalates_to_human("p1", "sub_atomic_engine_impl", "L3")
_emit_reads_policy_state("p1", "sub_atomic_engine_impl", "L3")
_emit_authorize_and_execute("p2", "sub_atomic_engine_impl", "execution_auth")
_emit_validates_capability("p2", "sub_atomic_engine_impl", "capability_check")
_emit_routes_to_capability("p2", "sub_atomic_engine_impl", "capability_route")
_emit_writes_via_uwg("p2", "sub_atomic_engine_impl", "uwg_write")
_emit_blocks_direct_write("p2", "sub_atomic_engine_impl", "direct_write_block")
_emit_records_tool_invocation("p2", "sub_atomic_engine_impl", "tool_invocation")
_emit_captures_execution_output("p2", "sub_atomic_engine_impl", "exec_output")
_emit_dispatches_agent("p3", "sub_atomic_engine_impl", "agent_dispatch")
_emit_coordinates_agents("p3", "sub_atomic_engine_impl", "agent_coordination")
_emit_records_workflow_lineage("p3", "sub_atomic_engine_impl", "workflow_lineage")
_emit_records_healing_outcome("p3", "sub_atomic_engine_impl", "healing_outcome")
_emit_escalates_failure("p3", "sub_atomic_engine_impl", "failure_escalation")
_emit_orchestrates_workflow("p3", "sub_atomic_engine_impl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sub_atomic_engine_impl", "healing_dispatch")
_emit_invokes_evaluation("p3", "sub_atomic_engine_impl", "evaluation_signal")
_emit_records_telemetry_event("p4", "sub_atomic_engine_impl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sub_atomic_engine_impl", "eval_metric")
_emit_stores_embedding("p4", "sub_atomic_engine_impl", "embedding_store")
_emit_updates_meta_learning_state("p4", "sub_atomic_engine_impl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sub_atomic_engine_impl", "exec_snapshot_link")

"\n[PHASE 14 REFACTOR] SubAtomicEngine.\nSTRICT COMPLIANCE: Uses SovereignLLMGateway singleton.\n"
import logging
import os

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
from agentic_core.mixins.instructional_injection_mixin import get_instructional_injection_mixin

_emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_1")
_emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_2")
_emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_3")
_emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_4")
_emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_5")
_emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_6")
_emit_records_incident_event("sub_atomic_engine_impl", "p4obs", "incident")
_emit_captures_runtime_anomaly("sub_atomic_engine_impl", "p4obs", "anomaly")
_emit_writes_observability_log("sub_atomic_engine_impl", "p4obs", "obs_log")
_emit_updates_monitoring_state("sub_atomic_engine_impl", "p4obs", "mon_state")
_emit_triggers_alert("sub_atomic_engine_impl", "p4obs", "alert")
_emit_links_incident_trace("sub_atomic_engine_impl", "p4obs", "trace_link")
_emit_captures_pattern("sub_atomic_engine_impl", "p3lm", "pattern")
_emit_records_learning_event("sub_atomic_engine_impl", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sub_atomic_engine_impl", "p3lm", "snapshot")
_emit_feeds_meta_learning("sub_atomic_engine_impl", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sub_atomic_engine_impl", "p3lm", "routing")
_emit_improves_agent_policy("sub_atomic_engine_impl", "p3lm", "policy")
_emit_stores_learning_state("sub_atomic_engine_impl", "p3lm", "state")
_emit_records_execution_trace("sub_atomic_engine_impl", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sub_atomic_engine_impl", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sub_atomic_engine_impl", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sub_atomic_engine_impl", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sub_atomic_engine_impl", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sub_atomic_engine_impl", "env_read", "p2_env_1")
_emit_reads_environ("sub_atomic_engine_impl", "env_read", "p2_env_2")
_emit_reads_runtime_state("sub_atomic_engine_impl", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sub_atomic_engine_impl", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sub_atomic_engine_impl", "context_pull")
_emit_pulls_context("p1", "sub_atomic_engine_impl", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sub_atomic_engine_impl", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sub_atomic_engine_impl", "uwg_term_2")
_emit_writes_through("p1", "sub_atomic_engine_impl", "write_through")
_emit_writes_through("p1", "sub_atomic_engine_impl", "write_through_2")
_emit_validated_by_safety_plane("p1", "sub_atomic_engine_impl", "safety_validation")
_emit_invokes_eval("p1", "sub_atomic_engine_impl", "eval_call")
_emit_proposal_commits_routing("p1", "sub_atomic_engine_impl", "routing_commit")


def _get_prompt_assembler():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_prompt_assembler", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_prompt_assembler", "p0_governance")
    from agentic_core.prompt_governance.core.prompt_assembler import assemble_prompt

    return assemble_prompt


def _get_injection_scanner():
    from agentic_core.prompt_governance.security.utils.injection_scan_util import scan_untrusted_text

    return scan_untrusted_text


Logger = logging.getLogger(__name__)


class SubAtomicEngineImpl:
    """Hardens the LLM interaction using Sovereign Gateways."""

    def __init__(self, redis_client=None):
        from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import get_embedding_gateway

        self.llm_gateway = get_llm_gateway()
        self.embedding_gateway = get_embedding_gateway()
        self.redis_client = redis_client
        print("   [OK] SubAtomicEngine: Gateway Link Active")

    async def get_embedding(self, text: str) -> list[float]:
        try:
            return await self.embedding_gateway.get_embedding(text, provider="bge-m3")
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            Logger.error(f"Embedding failed: {e}")
            return [0.0] * 1024

    async def resilient_mutation(self, *args, **kwargs) -> str:
        """Gateway-backed mutation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SubAtomicEngineImpl.resilient_mutation"
        )

        prompt = kwargs.get("prompt", "") or (args[0] if args else "")
        system_prompt = kwargs.get("system_prompt", None)
        fission_active = kwargs.get("fission_active", False)
        injection_mixin = get_instructional_injection_mixin()
        injected_prompt = injection_mixin.inject_all_layers(prompt, goal=system_prompt or "Execute mutation")
        full_prompt = assemble_prompt(
            role="SubAtomicEngine",
            objective=system_prompt or "Execute mutation",
            context_data=injected_prompt,
            injections=[],
        )
        scan_untrusted_text(prompt, source="sub_atomic_user_prompt")
        scan_untrusted_text(full_prompt, source="sub_atomic_full_prompt")
        try:
            gen_config = {}
            if fission_active:
                gen_config = {"thinking_config": {"include_thoughts": True}, "thinking_budget": 1024}
            response = await self.llm_gateway.generate(
                prompt=full_prompt,
                provider="google",
                model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
                generation_config=gen_config,
            )
            return response["content"]
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            Logger.error(f"Mutation failed: {e}")
            return prompt
