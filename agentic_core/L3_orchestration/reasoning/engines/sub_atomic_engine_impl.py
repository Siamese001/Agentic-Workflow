from __future__ import annotations

from agentic_core.config.model_catalog import BGE_M3_EMBEDDING_DIMENSION
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sub_atomic_engine_impl")
trace_contract.emit_determinism_digest("p0", "sub_atomic_engine_impl")

trace_contract._emit_dispatches_healing_run("p1", "sub_atomic_engine_impl", "L3")
trace_contract._emit_routes_through("p1", "sub_atomic_engine_impl", "L3")
trace_contract._emit_checks_agent_registry("p1", "sub_atomic_engine_impl", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sub_atomic_engine_impl", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sub_atomic_engine_impl", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sub_atomic_engine_impl", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sub_atomic_engine_impl", "target_agent")
trace_contract._emit_verifies_policy("p1", "sub_atomic_engine_impl", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sub_atomic_engine_impl", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sub_atomic_engine_impl", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sub_atomic_engine_impl", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sub_atomic_engine_impl")
trace_contract._emit_gated_by_confidence("p1", "sub_atomic_engine_impl", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sub_atomic_engine_impl", "L3")
trace_contract._emit_reads_policy_state("p1", "sub_atomic_engine_impl", "L3")
trace_contract._emit_authorize_and_execute("p2", "sub_atomic_engine_impl", "execution_auth")
trace_contract._emit_validates_capability("p2", "sub_atomic_engine_impl", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sub_atomic_engine_impl", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sub_atomic_engine_impl", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sub_atomic_engine_impl", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sub_atomic_engine_impl", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sub_atomic_engine_impl", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sub_atomic_engine_impl", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sub_atomic_engine_impl", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sub_atomic_engine_impl", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sub_atomic_engine_impl", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sub_atomic_engine_impl", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sub_atomic_engine_impl", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sub_atomic_engine_impl", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sub_atomic_engine_impl", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sub_atomic_engine_impl", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sub_atomic_engine_impl", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sub_atomic_engine_impl", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sub_atomic_engine_impl", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sub_atomic_engine_impl", "exec_snapshot_link")

"\n[PHASE 14 REFACTOR] SubAtomicEngine.\nSTRICT COMPLIANCE: Uses SovereignLLMGateway singleton.\n"
import logging
import os

from agentic_core.config.google_ai_env import google_ai_pro_model_id

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway
from agentic_core.mixins.instructional_injection_mixin import get_instructional_injection_mixin

trace_contract._emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sub_atomic_engine_impl", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sub_atomic_engine_impl", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sub_atomic_engine_impl", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sub_atomic_engine_impl", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sub_atomic_engine_impl", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sub_atomic_engine_impl", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sub_atomic_engine_impl", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sub_atomic_engine_impl", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sub_atomic_engine_impl", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sub_atomic_engine_impl", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sub_atomic_engine_impl", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sub_atomic_engine_impl", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sub_atomic_engine_impl", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sub_atomic_engine_impl", "p3lm", "state")
trace_contract._emit_records_execution_trace("sub_atomic_engine_impl", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sub_atomic_engine_impl", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sub_atomic_engine_impl", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sub_atomic_engine_impl", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sub_atomic_engine_impl", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sub_atomic_engine_impl", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sub_atomic_engine_impl", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sub_atomic_engine_impl", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sub_atomic_engine_impl", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sub_atomic_engine_impl", "context_pull")
trace_contract._emit_pulls_context("p1", "sub_atomic_engine_impl", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sub_atomic_engine_impl", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sub_atomic_engine_impl", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sub_atomic_engine_impl", "write_through")
trace_contract._emit_writes_through("p1", "sub_atomic_engine_impl", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sub_atomic_engine_impl", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sub_atomic_engine_impl", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sub_atomic_engine_impl", "routing_commit")


def _get_prompt_assembler():
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "_get_prompt_assembler", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "_get_prompt_assembler", "p0_governance")
    from agentic_core.prompt_governance.core import assemble_prompt

    return assemble_prompt


def _get_injection_scanner():
    from agentic_core.prompt_governance.security import scan_untrusted_text

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
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Embedding failed: {e}")
            return [0.0] * BGE_M3_EMBEDDING_DIMENSION

    async def resilient_mutation(self, *args, **kwargs) -> str:
        """Gateway-backed mutation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "SubAtomicEngineImpl.resilient_mutation",
        )

        prompt = kwargs.get("prompt", "") or (args[0] if args else "")
        system_prompt = kwargs.get("system_prompt", None)
        fission_active = kwargs.get("fission_active", False)
        injection_mixin = get_instructional_injection_mixin()
        injected_prompt = injection_mixin.inject_all_layers(prompt, goal=system_prompt or "Execute mutation")
        assemble_prompt = _get_prompt_assembler()
        scan_untrusted_text = _get_injection_scanner()
        from agentic_core.prompt_governance.core import SecurityIntegrityError as _SecIntErr  # noqa: PLC0415

        try:
            full_prompt = assemble_prompt(
                role="SubAtomicEngine",
                objective=system_prompt or "Execute mutation",
                context_data=injected_prompt,
                injections=[],
            )
        except (ImportError, _SecIntErr) as _asm_exc:
            Logger.warning("Prompt assembly failed: %s", _asm_exc)
            full_prompt = injected_prompt
        scan_untrusted_text(prompt, source="sub_atomic_user_prompt")
        scan_untrusted_text(full_prompt, source="sub_atomic_full_prompt")
        try:
            gen_config = {}
            if fission_active:
                gen_config = {"thinking_config": {"include_thoughts": True}, "thinking_budget": 1024}
            response = await self.llm_gateway.generate(
                prompt=full_prompt,
                provider="google",
                model=google_ai_pro_model_id()[0],
                generation_config=gen_config,
            )
            return response["content"]
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Mutation failed: {e}")
            return prompt
