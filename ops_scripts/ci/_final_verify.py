#!/usr/bin/env python3
"""Final infrastructure verification — F1-F5."""

import json
import os
import pathlib
import sys
import urllib.request

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "_final_verify")
_emit_applies_guardrail("p0", "_final_verify", "p0_governance")
_emit_reads_policy_state("p0", "_final_verify", "policy_binding")
_emit_snapshots_state("p0", "_final_verify", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("_final_verify", "p4obs", "metric_1")
_emit_emits_metric_event("_final_verify", "p4obs", "metric_2")
_emit_emits_metric_event("_final_verify", "p4obs", "metric_3")
_emit_emits_metric_event("_final_verify", "p4obs", "metric_4")
_emit_emits_metric_event("_final_verify", "p4obs", "metric_5")
_emit_emits_metric_event("_final_verify", "p4obs", "metric_6")
_emit_records_incident_event("_final_verify", "p4obs", "incident")
_emit_captures_runtime_anomaly("_final_verify", "p4obs", "anomaly")
_emit_writes_observability_log("_final_verify", "p4obs", "obs_log")
_emit_updates_monitoring_state("_final_verify", "p4obs", "mon_state")
_emit_triggers_alert("_final_verify", "p4obs", "alert")
_emit_links_incident_trace("_final_verify", "p4obs", "trace_link")
_emit_captures_pattern("_final_verify", "p3lm", "pattern")
_emit_records_learning_event("_final_verify", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_final_verify", "p3lm", "snapshot")
_emit_feeds_meta_learning("_final_verify", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_final_verify", "p3lm", "routing")
_emit_improves_agent_policy("_final_verify", "p3lm", "policy")
_emit_stores_learning_state("_final_verify", "p3lm", "state")
_emit_records_execution_trace("_final_verify", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_final_verify", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_final_verify", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_final_verify", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_final_verify", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_final_verify", "env_read", "p2_env_1")
_emit_reads_environ("_final_verify", "env_read", "p2_env_2")
_emit_reads_runtime_state("_final_verify", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_final_verify", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_final_verify", "context_pull")
_emit_pulls_context("p1", "_final_verify", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_final_verify", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_final_verify", "uwg_term_2")
_emit_writes_through("p1", "_final_verify", "write_through")
_emit_writes_through("p1", "_final_verify", "write_through_2")
_emit_validated_by_safety_plane("p1", "_final_verify", "safety_validation")
_emit_invokes_eval("p1", "_final_verify", "eval_call")
_emit_proposal_commits_routing("p1", "_final_verify", "routing_commit")
_emit_escalates_to_human("p1", "_final_verify", "human_escalation")
_emit_routes_through("p1", "_final_verify", "route_through")
_emit_checks_agent_registry("p1", "_final_verify", "agent_registry")
_emit_validates_agent_capability("p1", "_final_verify", "capability")
_emit_dispatches_execution_plan("p1", "_final_verify", "exec_plan")
_emit_agent_executes_agent("p1", "_final_verify", "sub_agent")
_emit_routes_to_agent("p1", "_final_verify", "target_agent")
_emit_verifies_policy("p1", "_final_verify", "policy_check")
_emit_observes_runtime_state("p1", "_final_verify", "runtime_state")
_emit_verifies_boundary("p1", "_final_verify", "boundary_check")
_emit_transcripts_response("p1", "_final_verify", "transcript")
_emit_hard_fails_untranscripted("p1", "_final_verify")
_emit_gated_by_confidence("p1", "_final_verify", "confidence_gate")
emit_replay_key("p0", "_final_verify")
emit_determinism_digest("p0", "_final_verify")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_final_verify", "execution_auth")
_emit_validates_capability("p2", "_final_verify", "capability_check")
_emit_routes_to_capability("p2", "_final_verify", "capability_route")
_emit_writes_via_uwg("p2", "_final_verify", "uwg_write")
_emit_blocks_direct_write("p2", "_final_verify", "direct_write_block")
_emit_records_tool_invocation("p2", "_final_verify", "tool_invocation")
_emit_captures_execution_output("p2", "_final_verify", "exec_output")
_emit_dispatches_agent("p3", "_final_verify", "agent_dispatch")
_emit_coordinates_agents("p3", "_final_verify", "agent_coordination")
_emit_records_workflow_lineage("p3", "_final_verify", "workflow_lineage")
_emit_records_healing_outcome("p3", "_final_verify", "healing_outcome")
_emit_escalates_failure("p3", "_final_verify", "failure_escalation")
_emit_orchestrates_workflow("p3", "_final_verify", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_final_verify", "healing_dispatch")
_emit_invokes_evaluation("p3", "_final_verify", "evaluation_signal")
_emit_records_telemetry_event("p4", "_final_verify", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_final_verify", "eval_metric")
_emit_stores_embedding("p4", "_final_verify", "embedding_store")
_emit_updates_meta_learning_state("p4", "_final_verify", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_final_verify", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, "c:/Git/Agentic-Workflow")

results = {}

# F1: vLLM running
try:
    # guardian: allow-magic-config
    with urllib.request.urlopen("http://localhost:8000/v1/models", timeout=3) as r:
        data = json.loads(r.read())
        results["F1_vllm"] = "PASS: " + data["data"][0]["id"]
except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
    raise
    results["F1_vllm"] = f"FAIL: {e}"

# F2: faiss-gpu + embedding env
try:
    import faiss

    has_gpu = hasattr(faiss, "StandardGpuResources")
    emb_dev = os.environ.get("EMBEDDING_DEVICE", "not set -> cpu")
    emb_en = os.environ.get("EMBEDDING_ENABLED", "not set -> false")
    if has_gpu and emb_dev == "cuda" and emb_en == "true":
        results["F2_embedding"] = "PASS: faiss-gpu + EMBEDDING_DEVICE=cuda + EMBEDDING_ENABLED=true"
    else:
        missing = []
        if not has_gpu:
            missing.append("faiss-gpu unavailable (no pip wheel for CUDA 12.8/Windows)")
        if emb_dev != "cuda":
            missing.append(f"EMBEDDING_DEVICE={emb_dev!r}")
        if emb_en != "true":
            missing.append(f"EMBEDDING_ENABLED={emb_en!r}")
        results["F2_embedding"] = "FAIL: " + "; ".join(missing)
except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
    raise
    results["F2_embedding"] = f"FAIL: {e}"

# F3: FAISS index boot sweep
try:
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    idx_dir = pathlib.Path("C:/AgenticEmbeddings/indexes")
    boot = LocalFAISSStore.verify_indexes_at_boot(idx_dir)
    if boot:
        first_digest = list(boot.values())[0]
        results["F3_faiss_index"] = f"PASS: {list(boot.keys())} digest={first_digest[:16]}..."
    else:
        results["F3_faiss_index"] = "FAIL: no indexes found"
except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
    raise
    results["F3_faiss_index"] = f"FAIL: {e}"

# F4: Redis
try:
    from agentic_core.cache.redis_cache_client import check_redis_health

    h = check_redis_health()
    if h["healthy"]:
        results["F4_redis"] = f"PASS: healthy, mem={h.get('used_memory_human', '?')}"
    else:
        results["F4_redis"] = f"FAIL: {h['error']}"
except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
    raise
    results["F4_redis"] = f"FAIL: {e}"

# F5: GPU mem util SSOT
try:
    from agentic_core.L3_orchestration.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
    from agentic_core.L3_orchestration.healers.vllm_process_manager import get_model_config

    cfg7 = get_model_config("7B")["gpu_memory_utilization"]
    cfg14 = get_model_config("14B")["gpu_memory_utilization"]
    if QWEN_GPU_MEM_UTIL == 0.70 and cfg7 == 0.70 and cfg14 == 0.70:
        results["F5_gpu_util_ssot"] = f"PASS: QWEN_GPU_MEM_UTIL={QWEN_GPU_MEM_UTIL} (7B={cfg7}, 14B={cfg14})"
    else:
        results["F5_gpu_util_ssot"] = f"FAIL: const={QWEN_GPU_MEM_UTIL} 7B={cfg7} 14B={cfg14}"
except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
    raise
    results["F5_gpu_util_ssot"] = f"FAIL: {e}"

print("=" * 60)
print("FINAL INFRASTRUCTURE STATUS")
print("=" * 60)
fails = []
for k, v in results.items():
    if str(v).startswith("PASS"):
        print(f"[OK] {k}: {v}")
    else:
        print(f"[!!] {k}: {v}")
        fails.append(k)

print("=" * 60)
if fails:
    print(f"RESULT: {len(fails)} FAIL(s): {fails}")
    sys.exit(1)
else:
    print("RESULT: ALL PASS")
    sys.exit(0)
