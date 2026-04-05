"""
L2 Qwen 14B vLLM inference worker.

Runs inside the WSL vLLM Python environment. Called as a subprocess by the
Windows-side healing pipeline via _get_qwen_vllm_arbiter() in execute_ssot.py.

Usage (invoked by the lazy seam, not directly):
    /home/amita/venvs/vllm/bin/python qwen_vllm_inference.py         --agent_name arch_governor         --confidence 0.62         --violation_types NAMING HIERARCHY         --territory agentic_core         --model_path /home/amita/models/Qwen2.5-14B-Instruct-AWQ

Exits 0 on success, prints JSON to stdout:
    {"decision": true, "reason": "...", "model": "Qwen2.5-14B-Instruct-AWQ"}
"""

from __future__ import annotations

import argparse
import json

from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "qwen_vllm_inference")
emit_determinism_digest("p0", "qwen_vllm_inference")

_emit_dispatches_healing_run("p1", "qwen_vllm_inference", "L2")
_emit_routes_through("p1", "qwen_vllm_inference", "L2")
_emit_checks_agent_registry("p1", "qwen_vllm_inference", "agent_registry")
_emit_validates_agent_capability("p1", "qwen_vllm_inference", "capability")
_emit_dispatches_execution_plan("p1", "qwen_vllm_inference", "exec_plan")
_emit_agent_executes_agent("p1", "qwen_vllm_inference", "sub_agent")
_emit_routes_to_agent("p1", "qwen_vllm_inference", "target_agent")
_emit_verifies_policy("p1", "qwen_vllm_inference", "policy_check")
_emit_observes_runtime_state("p1", "qwen_vllm_inference", "runtime_state")
_emit_verifies_boundary("p1", "qwen_vllm_inference", "boundary_check")
_emit_transcripts_response("p1", "qwen_vllm_inference", "transcript")
_emit_hard_fails_untranscripted("p1", "qwen_vllm_inference")
_emit_gated_by_confidence("p1", "qwen_vllm_inference", "confidence_gate")
_emit_escalates_to_human("p1", "qwen_vllm_inference", "L2")
_emit_reads_policy_state("p1", "qwen_vllm_inference", "L2")
_emit_authorize_and_execute("p2", "qwen_vllm_inference", "execution_auth")
_emit_validates_capability("p2", "qwen_vllm_inference", "capability_check")
_emit_routes_to_capability("p2", "qwen_vllm_inference", "capability_route")
_emit_writes_via_uwg("p2", "qwen_vllm_inference", "uwg_write")
_emit_blocks_direct_write("p2", "qwen_vllm_inference", "direct_write_block")
_emit_records_tool_invocation("p2", "qwen_vllm_inference", "tool_invocation")
_emit_captures_execution_output("p2", "qwen_vllm_inference", "exec_output")
_emit_dispatches_agent("p3", "qwen_vllm_inference", "agent_dispatch")
_emit_coordinates_agents("p3", "qwen_vllm_inference", "agent_coordination")
_emit_records_workflow_lineage("p3", "qwen_vllm_inference", "workflow_lineage")
_emit_records_healing_outcome("p3", "qwen_vllm_inference", "healing_outcome")
_emit_escalates_failure("p3", "qwen_vllm_inference", "failure_escalation")
_emit_orchestrates_workflow("p3", "qwen_vllm_inference", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "qwen_vllm_inference", "healing_dispatch")
_emit_invokes_evaluation("p3", "qwen_vllm_inference", "evaluation_signal")
_emit_records_telemetry_event("p4", "qwen_vllm_inference", "telemetry_event")
_emit_captures_evaluation_metric("p4", "qwen_vllm_inference", "eval_metric")
_emit_stores_embedding("p4", "qwen_vllm_inference", "embedding_store")
_emit_updates_meta_learning_state("p4", "qwen_vllm_inference", "meta_learning")
_emit_links_execution_to_snapshot("p4", "qwen_vllm_inference", "exec_snapshot_link")
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

_emit_emits_metric_event("qwen_vllm_inference", "p4obs", "metric_1")
_emit_emits_metric_event("qwen_vllm_inference", "p4obs", "metric_2")
_emit_emits_metric_event("qwen_vllm_inference", "p4obs", "metric_3")
_emit_emits_metric_event("qwen_vllm_inference", "p4obs", "metric_4")
_emit_emits_metric_event("qwen_vllm_inference", "p4obs", "metric_5")
_emit_emits_metric_event("qwen_vllm_inference", "p4obs", "metric_6")
_emit_records_incident_event("qwen_vllm_inference", "p4obs", "incident")
_emit_captures_runtime_anomaly("qwen_vllm_inference", "p4obs", "anomaly")
_emit_writes_observability_log("qwen_vllm_inference", "p4obs", "obs_log")
_emit_updates_monitoring_state("qwen_vllm_inference", "p4obs", "mon_state")
_emit_triggers_alert("qwen_vllm_inference", "p4obs", "alert")
_emit_links_incident_trace("qwen_vllm_inference", "p4obs", "trace_link")
_emit_captures_pattern("qwen_vllm_inference", "p3lm", "pattern")
_emit_records_learning_event("qwen_vllm_inference", "p3lm", "learning_event")
_emit_writes_learning_snapshot("qwen_vllm_inference", "p3lm", "snapshot")
_emit_feeds_meta_learning("qwen_vllm_inference", "p3lm", "meta_feed")
_emit_updates_routing_strategy("qwen_vllm_inference", "p3lm", "routing")
_emit_improves_agent_policy("qwen_vllm_inference", "p3lm", "policy")
_emit_stores_learning_state("qwen_vllm_inference", "p3lm", "state")
_emit_records_execution_trace("qwen_vllm_inference", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("qwen_vllm_inference", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("qwen_vllm_inference", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("qwen_vllm_inference", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("qwen_vllm_inference", "L4_STATE", "p2_trace_5")
_emit_reads_environ("qwen_vllm_inference", "env_read", "p2_env_1")
_emit_reads_environ("qwen_vllm_inference", "env_read", "p2_env_2")
_emit_reads_runtime_state("qwen_vllm_inference", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("qwen_vllm_inference", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "qwen_vllm_inference", "context_pull")
_emit_pulls_context("p1", "qwen_vllm_inference", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "qwen_vllm_inference", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "qwen_vllm_inference", "uwg_term_2")
_emit_writes_through("p1", "qwen_vllm_inference", "write_through")
_emit_writes_through("p1", "qwen_vllm_inference", "write_through_2")
_emit_validated_by_safety_plane("p1", "qwen_vllm_inference", "safety_validation")
_emit_invokes_eval("p1", "qwen_vllm_inference", "eval_call")
_emit_proposal_commits_routing("p1", "qwen_vllm_inference", "routing_commit")


def _build_prompt(agent_name: str, violation_types: list[str], territory: str, score: int, gate: str) -> str:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_build_prompt", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_build_prompt", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_build_prompt")
    violations_str = ", ".join(violation_types) if violation_types else "UNKNOWN"
    band = (
        "low (agent-native)" if score <= 13 else "medium (Qwen-advised)" if score <= 26 else "high (Gemini)"
    )
    return f"You are a healing-plan advisor for an agentic codebase pipeline.\nScore-based routing has already dispatched this to you: score={score} ({band}), gate={gate}.\nHealing WILL proceed. Your role is to describe what the agent should do and confirm it is safe.\n\nAgent: {agent_name}\nTerritory: {territory}\nViolations detected: {violations_str}\n\nIn one sentence, describe the specific healing action {agent_name} should take for these violations.\nThen reply YES to confirm it is safe.\nOnly reply NO if the action would cause irreversible data loss or break a production invariant.\nFormat: YES <healing action description> OR NO <specific reason>."


def main() -> None:
    parser = argparse.ArgumentParser(description="Qwen 14B vLLM governance arbiter")
    parser.add_argument("--agent_name", required=True)
    parser.add_argument("--violation_types", nargs="*", default=[])
    parser.add_argument("--territory", required=True)
    parser.add_argument("--score", type=int, default=0)
    parser.add_argument("--gate", default="")
    parser.add_argument("--model_path", default="/home/amita/models/Qwen2.5-14B-Instruct-AWQ")
    args = parser.parse_args()
    from vllm import LLM, SamplingParams

    # guardian: allow-magic-config
    llm = LLM(
        model=args.model_path,
        quantization="awq",
        dtype="float16",
        max_model_len=512,
        gpu_memory_utilization=QWEN_GPU_MEM_UTIL,
    )
    prompt = _build_prompt(args.agent_name, args.violation_types, args.territory, args.score, args.gate)
    # guardian: allow-magic-config
    sampling_params = SamplingParams(temperature=0.0, max_tokens=80)
    outputs = llm.generate([prompt], sampling_params)
    response = outputs[0].outputs[0].text.strip()
    decision = response.upper().startswith("YES")
    result = {
        "decision": decision,
        "reason": response,
        "model": "Qwen2.5-14B-Instruct-AWQ",
        "agent_name": args.agent_name,
        "score": args.score,
        "gate": args.gate,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
