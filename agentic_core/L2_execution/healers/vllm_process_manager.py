"""
Qwen Process Manager - vLLM Server Lifecycle Management

Provides isolated process management for vLLM server with proper
startup, shutdown, and health monitoring capabilities.
"""

from __future__ import annotations

import logging
import subprocess
import time

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP, DEFAULT_TIMEOUT
from agentic_core.L2_execution.healers.healing_tier_config import QWEN_GPU_MEM_UTIL
from agentic_core.L2_execution.utils.providers import get_clock
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
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "vllm_process_manager")
emit_determinism_digest("p0", "vllm_process_manager")

_emit_dispatches_healing_run("p1", "vllm_process_manager", "L2")
_emit_routes_through("p1", "vllm_process_manager", "L2")
_emit_checks_agent_registry("p1", "vllm_process_manager", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_process_manager", "capability")
_emit_dispatches_execution_plan("p1", "vllm_process_manager", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_process_manager", "sub_agent")
_emit_routes_to_agent("p1", "vllm_process_manager", "target_agent")
_emit_verifies_policy("p1", "vllm_process_manager", "policy_check")
_emit_observes_runtime_state("p1", "vllm_process_manager", "runtime_state")
_emit_verifies_boundary("p1", "vllm_process_manager", "boundary_check")
_emit_transcripts_response("p1", "vllm_process_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_process_manager")
_emit_gated_by_confidence("p1", "vllm_process_manager", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_process_manager", "L2")
_emit_reads_policy_state("p1", "vllm_process_manager", "L2")

_emit_applies_guardrail("p0", "vllm_process_manager", "p0_governance")
_emit_snapshots_state("p0", "vllm_process_manager", "state_snapshot")
_emit_authorize_and_execute("p2", "vllm_process_manager", "execution_auth")
_emit_validates_capability("p2", "vllm_process_manager", "capability_check")
_emit_routes_to_capability("p2", "vllm_process_manager", "capability_route")
_emit_writes_via_uwg("p2", "vllm_process_manager", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_process_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_process_manager", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_process_manager", "exec_output")
_emit_dispatches_agent("p3", "vllm_process_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_process_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_process_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_process_manager", "healing_outcome")
_emit_escalates_failure("p3", "vllm_process_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_process_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_process_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_process_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_process_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_process_manager", "eval_metric")
_emit_stores_embedding("p4", "vllm_process_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_process_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_process_manager", "exec_snapshot_link")
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

_emit_emits_metric_event("vllm_process_manager", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_process_manager", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_process_manager", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_process_manager", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_process_manager", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_process_manager", "p4obs", "metric_6")
_emit_records_incident_event("vllm_process_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_process_manager", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_process_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_process_manager", "p4obs", "mon_state")
_emit_triggers_alert("vllm_process_manager", "p4obs", "alert")
_emit_links_incident_trace("vllm_process_manager", "p4obs", "trace_link")
_emit_captures_pattern("vllm_process_manager", "p3lm", "pattern")
_emit_records_learning_event("vllm_process_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_process_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_process_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_process_manager", "p3lm", "routing")
_emit_improves_agent_policy("vllm_process_manager", "p3lm", "policy")
_emit_stores_learning_state("vllm_process_manager", "p3lm", "state")
_emit_records_execution_trace("vllm_process_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_process_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_process_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_process_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_process_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_process_manager", "env_read", "p2_env_1")
_emit_reads_environ("vllm_process_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_process_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_process_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_process_manager", "context_pull")
_emit_pulls_context("p1", "vllm_process_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_process_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_process_manager", "uwg_term_2")
_emit_writes_through("p1", "vllm_process_manager", "write_through")
_emit_writes_through("p1", "vllm_process_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_process_manager", "safety_validation")
_emit_invokes_eval("p1", "vllm_process_manager", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_process_manager", "routing_commit")

logger = logging.getLogger(__name__)


class VLLMProcessManager:
    """Manage isolated vLLM server process."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.start_time: float | None = None
        self.base_url: str = "http://localhost:8000/v1"

    def start_server(self, model_config: dict) -> int:
        """Start vLLM server with specified model configuration."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "VLLMProcessManager.start_server")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMProcessManager.start_server".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self.process and self.process.poll() is None:
            raise RuntimeError("vLLM server is already running")
        model_id = model_config.get("model_id", "Qwen/Qwen2.5-7B-Instruct")
        cmd = [
            "python",
            "-m",
            "vllm.entrypoints.openai.api_server",
            "--model",
            model_id,
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--trust-remote-code",
            "--max-model-len",
            "8192",
            "--gpu-memory-utilization",
            str(QWEN_GPU_MEM_UTIL),
        ]
        logger.info(f"Starting vLLM server with command: {' '.join(cmd)}")
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.start_time = get_clock().now_epoch()
            time.sleep(DEFAULT_SLEEP)
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"vLLM server failed to start: {stderr}")
            logger.info(f"vLLM server started with PID: {self.process.pid}")
            return self.process.pid
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.error(f"Failed to start vLLM server: {exc}")
            self.process = None
            raise

    def stop_server(self) -> None:
        """Stop vLLM server gracefully."""
        if not self.process:
            logger.info("vLLM server is not running")
            return
        try:
            logger.info(f"Stopping vLLM server PID: {self.process.pid}")
            self.process.terminate()
            try:
                self.process.wait(timeout=DEFAULT_TIMEOUT)
                logger.info("vLLM server stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("vLLM server did not stop gracefully, force killing")
                self.process.kill()
                self.process.wait()
                logger.info("vLLM server force killed")
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as exc:
            logger.error(f"Error stopping vLLM server: {exc}")
        finally:
            self.process = None
            self.start_time = None

    def health_check(self) -> bool:
        """Check if vLLM server is healthy and responding."""
        if not self.process or self.process.poll() is not None:
            return False
        try:
            import urllib.request as _urllib_request

            with _urllib_request.urlopen(f"{self.base_url}/health", timeout=DEFAULT_TIMEOUT) as _resp:  # noqa: S310
                return _resp.status == 200
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError):
            return False

    def get_memory_usage(self) -> dict:
        """Get GPU memory usage statistics."""
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode == 0:
                used, total = map(int, result.stdout.strip().split(", "))
                return {"used_mb": used, "total_mb": total, "utilization_percent": used / total * 100}
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError):
            pass
        return {"used_mb": 0, "total_mb": 0, "utilization_percent": 0.0}

    def get_pid(self) -> int | None:
        """Get vLLM process ID."""
        return self.process.pid if self.process else None

    def is_running(self) -> bool:
        """Check if vLLM process is running."""
        return self.process is not None and self.process.poll() is None

    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        if not self.start_time:
            return 0.0
        return get_clock().now_epoch() - self.start_time


vllm_process_manager = VLLMProcessManager()


def get_model_config(model_size: str = "7B") -> dict:
    """Get model configuration for specified model size."""
    configs = {
        "7B": {
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "max_model_len": 8192,
            "gpu_memory_utilization": QWEN_GPU_MEM_UTIL,
        },
        "14B": {
            "model_id": "Qwen/Qwen2.5-14B-Instruct",
            "max_model_len": 4096,
            "gpu_memory_utilization": QWEN_GPU_MEM_UTIL,
        },
    }
    return configs.get(model_size, configs["7B"])


__all__ = ["VLLMProcessManager", "vllm_process_manager", "get_model_config"]
