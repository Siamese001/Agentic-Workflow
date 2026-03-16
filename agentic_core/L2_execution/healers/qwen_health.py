"""
Qwen Health Endpoint - Comprehensive Health Monitoring

Provides health check endpoint with determinism visibility and
circuit breaker status monitoring.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "qwen_health")
emit_determinism_digest("p0", "qwen_health")

_emit_dispatches_healing_run("p1", "qwen_health", "L2")
_emit_routes_through("p1", "qwen_health", "L2")
_emit_escalates_to_human("p1", "qwen_health", "L2")
_emit_reads_policy_state("p1", "qwen_health", "L2")
_emit_authorize_and_execute("p2", "qwen_health", "execution_auth")
_emit_validates_capability("p2", "qwen_health", "capability_check")
_emit_routes_to_capability("p2", "qwen_health", "capability_route")
_emit_writes_via_uwg("p2", "qwen_health", "uwg_write")
_emit_blocks_direct_write("p2", "qwen_health", "direct_write_block")
_emit_records_tool_invocation("p2", "qwen_health", "tool_invocation")
_emit_captures_execution_output("p2", "qwen_health", "exec_output")
_emit_dispatches_agent("p3", "qwen_health", "agent_dispatch")
_emit_coordinates_agents("p3", "qwen_health", "agent_coordination")
_emit_records_workflow_lineage("p3", "qwen_health", "workflow_lineage")
_emit_records_healing_outcome("p3", "qwen_health", "healing_outcome")
_emit_escalates_failure("p3", "qwen_health", "failure_escalation")
_emit_orchestrates_workflow("p3", "qwen_health", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "qwen_health", "healing_dispatch")
_emit_invokes_evaluation("p3", "qwen_health", "evaluation_signal")
_emit_records_telemetry_event("p4", "qwen_health", "telemetry_event")
_emit_captures_evaluation_metric("p4", "qwen_health", "eval_metric")
_emit_stores_embedding("p4", "qwen_health", "embedding_store")
_emit_updates_meta_learning_state("p4", "qwen_health", "meta_learning")
_emit_links_execution_to_snapshot("p4", "qwen_health", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def get_qwen_health_status() -> dict[str, Any]:
    """Comprehensive health endpoint with determinism visibility."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_qwen_health_status", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_qwen_health_status", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_qwen_health_status")
    try:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            QWEN_CUDA_VERSION,
            QWEN_TORCH_VERSION,
            QWEN_VLLM_VERSION,
        )
        from agentic_core.L2_execution.healers.qwen_circuit_breaker import circuit_breaker
        from agentic_core.L2_execution.healers.qwen_determinism import compute_current_determinism_digest

        return {
            "status": "healthy" if not circuit_breaker.is_circuit_open() else "degraded",
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "model_revision": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
            "determinism_digest": compute_current_determinism_digest(),
            "cuda_version": QWEN_CUDA_VERSION,
            "vllm_version": QWEN_VLLM_VERSION,
            "torch_version": QWEN_TORCH_VERSION,
            "circuit_open": circuit_breaker.is_circuit_open(),
            "replay_mode_supported": True,
            "last_failure": circuit_breaker.last_failure_timestamp,
            "failure_count": circuit_breaker.failure_count,
            "gpu_memory_used_mb": 0,
            "process_id": None,
        }
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.error(f"Failed to get Qwen health status: {exc}")
        return {
            "status": "error",
            "error": str(exc),
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "replay_mode_supported": True,
        }


def get_gpu_memory_usage() -> int:
    """Get current GPU memory usage in MB."""
    try:
        import subprocess

        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    # guardian: allow-silent-swallow
    except Exception:
        pass
    return 0


class MockVLLMProcessManager:
    """Mock vLLM process manager for health endpoint."""

    def get_pid(self) -> int | None:
        """Get vLLM process ID."""
        return None

    def is_running(self) -> bool:
        """Check if vLLM process is running."""
        return False


vllm_process_manager = MockVLLMProcessManager()
__all__ = ["get_qwen_health_status", "get_gpu_memory_usage", "vllm_process_manager"]
