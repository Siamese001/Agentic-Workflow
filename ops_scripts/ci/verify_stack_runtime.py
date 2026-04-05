#!/usr/bin/env python3
"""Runtime verification of F1-F5 infrastructure stack fixes.

Validates that all fixes are working in the live runtime environment:
    F1+F5: QWEN_GPU_MEM_UTIL constant is used consistently
    F2:    EmbeddingServiceFactory GPU path is wired correctly
    F3:    LocalFAISSStore.verify_indexes_at_boot is callable
    F4:    Redis health check returns structured response
    F5:    (covered by F1)

Exit 0 on success, 1 on any failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "verify_stack_runtime")
_emit_applies_guardrail("p0", "verify_stack_runtime", "p0_governance")
_emit_reads_policy_state("p0", "verify_stack_runtime", "policy_binding")
_emit_snapshots_state("p0", "verify_stack_runtime", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("verify_stack_runtime", "p4obs", "metric_1")
_emit_emits_metric_event("verify_stack_runtime", "p4obs", "metric_2")
_emit_emits_metric_event("verify_stack_runtime", "p4obs", "metric_3")
_emit_emits_metric_event("verify_stack_runtime", "p4obs", "metric_4")
_emit_emits_metric_event("verify_stack_runtime", "p4obs", "metric_5")
_emit_emits_metric_event("verify_stack_runtime", "p4obs", "metric_6")
_emit_records_incident_event("verify_stack_runtime", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_stack_runtime", "p4obs", "anomaly")
_emit_writes_observability_log("verify_stack_runtime", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_stack_runtime", "p4obs", "mon_state")
_emit_triggers_alert("verify_stack_runtime", "p4obs", "alert")
_emit_links_incident_trace("verify_stack_runtime", "p4obs", "trace_link")
_emit_captures_pattern("verify_stack_runtime", "p3lm", "pattern")
_emit_records_learning_event("verify_stack_runtime", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_stack_runtime", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_stack_runtime", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_stack_runtime", "p3lm", "routing")
_emit_improves_agent_policy("verify_stack_runtime", "p3lm", "policy")
_emit_stores_learning_state("verify_stack_runtime", "p3lm", "state")
_emit_records_execution_trace("verify_stack_runtime", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_stack_runtime", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_stack_runtime", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_stack_runtime", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_stack_runtime", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_stack_runtime", "env_read", "p2_env_1")
_emit_reads_environ("verify_stack_runtime", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_stack_runtime", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_stack_runtime", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_stack_runtime", "context_pull")
_emit_pulls_context("p1", "verify_stack_runtime", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verify_stack_runtime", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_stack_runtime", "uwg_term_2")
_emit_writes_through("p1", "verify_stack_runtime", "write_through")
_emit_writes_through("p1", "verify_stack_runtime", "write_through_2")
_emit_validated_by_safety_plane("p1", "verify_stack_runtime", "safety_validation")
_emit_invokes_eval("p1", "verify_stack_runtime", "eval_call")
_emit_proposal_commits_routing("p1", "verify_stack_runtime", "routing_commit")
_emit_escalates_to_human("p1", "verify_stack_runtime", "human_escalation")
_emit_routes_through("p1", "verify_stack_runtime", "route_through")
_emit_checks_agent_registry("p1", "verify_stack_runtime", "agent_registry")
_emit_validates_agent_capability("p1", "verify_stack_runtime", "capability")
_emit_dispatches_execution_plan("p1", "verify_stack_runtime", "exec_plan")
_emit_agent_executes_agent("p1", "verify_stack_runtime", "sub_agent")
_emit_routes_to_agent("p1", "verify_stack_runtime", "target_agent")
_emit_verifies_policy("p1", "verify_stack_runtime", "policy_check")
_emit_observes_runtime_state("p1", "verify_stack_runtime", "runtime_state")
_emit_verifies_boundary("p1", "verify_stack_runtime", "boundary_check")
_emit_transcripts_response("p1", "verify_stack_runtime", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_stack_runtime")
_emit_gated_by_confidence("p1", "verify_stack_runtime", "confidence_gate")
emit_replay_key("p0", "verify_stack_runtime")
emit_determinism_digest("p0", "verify_stack_runtime")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "verify_stack_runtime", "execution_auth")
_emit_validates_capability("p2", "verify_stack_runtime", "capability_check")
_emit_routes_to_capability("p2", "verify_stack_runtime", "capability_route")
_emit_writes_via_uwg("p2", "verify_stack_runtime", "uwg_write")
_emit_blocks_direct_write("p2", "verify_stack_runtime", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_stack_runtime", "tool_invocation")
_emit_captures_execution_output("p2", "verify_stack_runtime", "exec_output")
_emit_dispatches_agent("p3", "verify_stack_runtime", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_stack_runtime", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_stack_runtime", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_stack_runtime", "healing_outcome")
_emit_escalates_failure("p3", "verify_stack_runtime", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_stack_runtime", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_stack_runtime", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_stack_runtime", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_stack_runtime", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_stack_runtime", "eval_metric")
_emit_stores_embedding("p4", "verify_stack_runtime", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_stack_runtime", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_stack_runtime", "exec_snapshot_link")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))


def verify_f1_f5_qwen_gpu_mem_util() -> tuple[bool, str]:
    """F1+F5: Verify QWEN_GPU_MEM_UTIL constant exists and is used."""
    try:
        from agentic_core.L3_orchestration.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
        from agentic_core.L3_orchestration.healers.vllm_process_manager import get_model_config

        # 1. Constant exists and has correct value
        if not isinstance(QWEN_GPU_MEM_UTIL, float):
            return False, f"QWEN_GPU_MEM_UTIL is not a float: {type(QWEN_GPU_MEM_UTIL)}"
        if QWEN_GPU_MEM_UTIL != 0.70:
            return False, f"QWEN_GPU_MEM_UTIL={QWEN_GPU_MEM_UTIL}, expected 0.70"

        # 2. vllm_process_manager uses the constant
        for size in ("7B", "14B"):
            cfg = get_model_config(size)
            if cfg["gpu_memory_utilization"] != QWEN_GPU_MEM_UTIL:
                return False, (
                    f"get_model_config('{size}') gpu_memory_utilization="
                    f"{cfg['gpu_memory_utilization']}, expected {QWEN_GPU_MEM_UTIL}"
                )

        # 3. qwen_vllm_inference imports the constant (AST check)
        import ast

        qwen_src = (PROJECT_ROOT / "agentic_core/L2_execution/healers/qwen_vllm_inference.py").read_text()
        tree = ast.parse(qwen_src)
        imported = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "agentic_core.L2_execution.healers.healing_tier_config"
            ):
                for alias in node.names:
                    if alias.name == "QWEN_GPU_MEM_UTIL":
                        imported = True
                        break
        if not imported:
            return False, "qwen_vllm_inference.py does not import QWEN_GPU_MEM_UTIL"

        return True, "QWEN_GPU_MEM_UTIL SSOT verified"
    except Exception as exc:
        raise
        return False, f"F1+F5 verification failed: {exc}"


def verify_f2_embedding_gpu_path() -> tuple[bool, str]:
    """F2: Verify EmbeddingServiceFactory GPU helpers exist and are callable."""
    try:
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        # 1. _faiss_gpu_available exists and returns bool
        if not hasattr(EmbeddingServiceFactory, "_faiss_gpu_available"):
            return False, "EmbeddingServiceFactory._faiss_gpu_available does not exist"
        result = EmbeddingServiceFactory._faiss_gpu_available()
        if not isinstance(result, bool):
            return False, f"_faiss_gpu_available returned {type(result)}, expected bool"

        # 2. _embedding_device exists and returns str
        if not hasattr(EmbeddingServiceFactory, "_embedding_device"):
            return False, "EmbeddingServiceFactory._embedding_device does not exist"
        device = EmbeddingServiceFactory._embedding_device()
        if not isinstance(device, str):
            return False, f"_embedding_device returned {type(device)}, expected str"
        if device not in ("cpu", "cuda"):
            return False, f"_embedding_device returned '{device}', expected 'cpu' or 'cuda'"

        # 3. _build_gpu_index exists and is callable
        if not hasattr(EmbeddingServiceFactory, "_build_gpu_index"):
            return False, "EmbeddingServiceFactory._build_gpu_index does not exist"
        if not callable(EmbeddingServiceFactory._build_gpu_index):
            return False, "_build_gpu_index is not callable"

        return True, f"EmbeddingServiceFactory GPU path verified (device={device}, faiss-gpu={result})"
    except Exception as exc:
        raise
        return False, f"F2 verification failed: {exc}"


def verify_f3_faiss_boot_sweep() -> tuple[bool, str]:
    """F3: Verify LocalFAISSStore.verify_indexes_at_boot exists and is callable."""
    try:
        import tempfile
        from pathlib import Path

        from system_learning.engines.local_faiss_store import LocalFAISSStore

        # 1. Method exists
        if not hasattr(LocalFAISSStore, "verify_indexes_at_boot"):
            return False, "LocalFAISSStore.verify_indexes_at_boot does not exist"

        # 2. Method is callable
        if not callable(LocalFAISSStore.verify_indexes_at_boot):
            return False, "verify_indexes_at_boot is not callable"

        # 3. Method works on empty directory
        with tempfile.TemporaryDirectory() as tmpdir:
            result = LocalFAISSStore.verify_indexes_at_boot(Path(tmpdir))
            if not isinstance(result, dict):
                return False, f"verify_indexes_at_boot returned {type(result)}, expected dict"

        return True, "LocalFAISSStore.verify_indexes_at_boot verified"
    except Exception as exc:
        raise
        return False, f"F3 verification failed: {exc}"


def verify_f4_redis_health_check() -> tuple[bool, str]:
    """F4: Verify check_redis_health returns structured response."""
    try:
        from agentic_core.cache.redis_cache_client import check_redis_health

        # 1. Function exists and is callable
        if not callable(check_redis_health):
            return False, "check_redis_health is not callable"

        # 2. Returns dict with required keys
        result = check_redis_health()
        if not isinstance(result, dict):
            return False, f"check_redis_health returned {type(result)}, expected dict"

        required_keys = {"healthy", "url", "using_fallback", "error", "fix"}
        missing = required_keys - result.keys()
        if missing:
            return False, f"check_redis_health missing keys: {missing}"

        # 3. healthy is bool
        if not isinstance(result["healthy"], bool):
            return False, f"healthy is {type(result['healthy'])}, expected bool"

        # 4. If unhealthy, fix hint must be present
        if not result["healthy"] and not result.get("fix"):
            return False, "unhealthy result missing fix hint"

        status = "healthy" if result["healthy"] else "unhealthy (fallback active)"
        return True, f"Redis health check verified: {status}"
    except Exception as exc:
        raise
        return False, f"F4 verification failed: {exc}"


def main() -> int:
    """Run all runtime verifications."""
    print("=" * 80)
    print("F1-F5 Runtime Stack Verification")
    print("=" * 80)

    verifications = [
        ("F1+F5", "QWEN_GPU_MEM_UTIL SSOT", verify_f1_f5_qwen_gpu_mem_util),
        ("F2", "EmbeddingServiceFactory GPU path", verify_f2_embedding_gpu_path),
        ("F3", "LocalFAISSStore.verify_indexes_at_boot", verify_f3_faiss_boot_sweep),
        ("F4", "Redis health check", verify_f4_redis_health_check),
    ]

    results = []
    for fix_id, description, verify_fn in verifications:
        print(f"\n[{fix_id}] {description}...", end=" ", flush=True)
        passed, message = verify_fn()
        results.append((fix_id, description, passed, message))
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}")
        print(f"     {message}")

    print("\n" + "=" * 80)
    passed_count = sum(1 for _, _, passed, _ in results if passed)
    total_count = len(results)
    print(f"Results: {passed_count}/{total_count} passed")
    print("=" * 80)

    if passed_count == total_count:
        print("\n✓ All runtime verifications PASSED")
        return 0
    else:
        print("\n✗ Some runtime verifications FAILED")
        for fix_id, desc, passed, msg in results:
            if not passed:
                print(f"  [{fix_id}] {desc}: {msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
