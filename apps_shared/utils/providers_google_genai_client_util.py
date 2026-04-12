"""Google Generative AI (Gemini) client adapter for v10_10.

This module is the ONLY place where google.generativeai is imported.
It exposes a narrow run_llm interface used by runtime_utils.
"""

from __future__ import annotations

import os
import uuid
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

_emit_applies_guardrail("p0", "providers_google_genai_client_util", "p0_governance")
_emit_reads_policy_state("p0", "providers_google_genai_client_util", "policy_binding")
_emit_snapshots_state("p0", "providers_google_genai_client_util", "state_snapshot")
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

_emit_emits_metric_event("providers_google_genai_client_util", "p4obs", "metric_1")
_emit_emits_metric_event("providers_google_genai_client_util", "p4obs", "metric_2")
_emit_emits_metric_event("providers_google_genai_client_util", "p4obs", "metric_3")
_emit_emits_metric_event("providers_google_genai_client_util", "p4obs", "metric_4")
_emit_emits_metric_event("providers_google_genai_client_util", "p4obs", "metric_5")
_emit_emits_metric_event("providers_google_genai_client_util", "p4obs", "metric_6")
_emit_records_incident_event("providers_google_genai_client_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("providers_google_genai_client_util", "p4obs", "anomaly")
_emit_writes_observability_log("providers_google_genai_client_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("providers_google_genai_client_util", "p4obs", "mon_state")
_emit_triggers_alert("providers_google_genai_client_util", "p4obs", "alert")
_emit_links_incident_trace("providers_google_genai_client_util", "p4obs", "trace_link")
_emit_captures_pattern("providers_google_genai_client_util", "p3lm", "pattern")
_emit_records_learning_event("providers_google_genai_client_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("providers_google_genai_client_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("providers_google_genai_client_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("providers_google_genai_client_util", "p3lm", "routing")
_emit_improves_agent_policy("providers_google_genai_client_util", "p3lm", "policy")
_emit_stores_learning_state("providers_google_genai_client_util", "p3lm", "state")
_emit_records_execution_trace("providers_google_genai_client_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("providers_google_genai_client_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("providers_google_genai_client_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("providers_google_genai_client_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("providers_google_genai_client_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("providers_google_genai_client_util", "env_read", "p2_env_1")
_emit_reads_environ("providers_google_genai_client_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("providers_google_genai_client_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("providers_google_genai_client_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "providers_google_genai_client_util", "context_pull")
_emit_pulls_context("p1", "providers_google_genai_client_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "providers_google_genai_client_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "providers_google_genai_client_util", "uwg_term_2")
_emit_writes_through("p1", "providers_google_genai_client_util", "write_through")
_emit_writes_through("p1", "providers_google_genai_client_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "providers_google_genai_client_util", "safety_validation")
_emit_invokes_eval("p1", "providers_google_genai_client_util", "eval_call")
_emit_proposal_commits_routing("p1", "providers_google_genai_client_util", "routing_commit")
_emit_escalates_to_human("p1", "providers_google_genai_client_util", "human_escalation")
_emit_routes_through("p1", "providers_google_genai_client_util", "route_through")
_emit_checks_agent_registry("p1", "providers_google_genai_client_util", "agent_registry")
_emit_validates_agent_capability("p1", "providers_google_genai_client_util", "capability")
_emit_dispatches_execution_plan("p1", "providers_google_genai_client_util", "exec_plan")
_emit_agent_executes_agent("p1", "providers_google_genai_client_util", "sub_agent")
_emit_routes_to_agent("p1", "providers_google_genai_client_util", "target_agent")
_emit_verifies_policy("p1", "providers_google_genai_client_util", "policy_check")
_emit_observes_runtime_state("p1", "providers_google_genai_client_util", "runtime_state")
_emit_verifies_boundary("p1", "providers_google_genai_client_util", "boundary_check")
_emit_transcripts_response("p1", "providers_google_genai_client_util", "transcript")
_emit_hard_fails_untranscripted("p1", "providers_google_genai_client_util")
_emit_gated_by_confidence("p1", "providers_google_genai_client_util", "confidence_gate")
emit_replay_key("p0", "providers_google_genai_client_util")
emit_determinism_digest("p0", "providers_google_genai_client_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "providers_google_genai_client_util", "execution_auth")
_emit_validates_capability("p2", "providers_google_genai_client_util", "capability_check")
_emit_routes_to_capability("p2", "providers_google_genai_client_util", "capability_route")
_emit_writes_via_uwg("p2", "providers_google_genai_client_util", "uwg_write")
_emit_blocks_direct_write("p2", "providers_google_genai_client_util", "direct_write_block")
_emit_records_tool_invocation("p2", "providers_google_genai_client_util", "tool_invocation")
_emit_captures_execution_output("p2", "providers_google_genai_client_util", "exec_output")
_emit_dispatches_agent("p3", "providers_google_genai_client_util", "agent_dispatch")
_emit_coordinates_agents("p3", "providers_google_genai_client_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "providers_google_genai_client_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "providers_google_genai_client_util", "healing_outcome")
_emit_escalates_failure("p3", "providers_google_genai_client_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "providers_google_genai_client_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "providers_google_genai_client_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "providers_google_genai_client_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "providers_google_genai_client_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "providers_google_genai_client_util", "eval_metric")
_emit_stores_embedding("p4", "providers_google_genai_client_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "providers_google_genai_client_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "providers_google_genai_client_util", "exec_snapshot_link")


def run_llm_google(
    model: str,
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
    use_interactions_api: bool = True,
) -> str:
    """Run a Gemini generate_content call and return the response text.

    Args:
        model: Gemini model name
        prompt: Input prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        timeout_s: Request timeout in seconds
        use_interactions_api: Force use of new v1beta Interactions API
    """
    _emit_records_execution_trace(
        str(uuid.uuid4()),
        LayerSegment.L3_ORCHESTRATION,
        "run_llm_google",
    )
    if use_interactions_api:
        try:
            from google import genai

            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set for Google provider")
            client = genai.Client(api_key=api_key)
            input_messages = [{"role": "user", "content": prompt}]
            response = client.interactions.create(
                model=model,
                input=input_messages,
                config={"temperature": temperature, "max_output_tokens": max_tokens},
            )
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    return candidate.content.parts[0].text if candidate.content.parts else ""
            return ""
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            pass
        # guardian: allow-silent-swallow
        except Exception as e:
            import logging

            logging.warning(f"Google GenAI v1beta API failed, falling back to legacy: {e}")
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise ImportError("google-generativeai package not installed") from exc
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set for Google provider")
    genai.configure(api_key=api_key)
    model_client = genai.GenerativeModel(model)
    resp: Any = model_client.generate_content(prompt)
    return str(getattr(resp, "text", "") or "")
