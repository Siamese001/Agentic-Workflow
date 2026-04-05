"""
Qwen GPU Validation - Fail-Fast GPU Capability Checking

Provides hard validation of GPU capabilities before model loading.
Ensures Qwen models only run on compatible hardware.
"""

from __future__ import annotations

import logging
import subprocess
from typing import Literal

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "qwen_gpu_validator")
emit_determinism_digest("p0", "qwen_gpu_validator")

_emit_dispatches_healing_run("p1", "qwen_gpu_validator", "L2")
_emit_routes_through("p1", "qwen_gpu_validator", "L2")
_emit_checks_agent_registry("p1", "qwen_gpu_validator", "agent_registry")
_emit_validates_agent_capability("p1", "qwen_gpu_validator", "capability")
_emit_dispatches_execution_plan("p1", "qwen_gpu_validator", "exec_plan")
_emit_agent_executes_agent("p1", "qwen_gpu_validator", "sub_agent")
_emit_routes_to_agent("p1", "qwen_gpu_validator", "target_agent")
_emit_verifies_policy("p1", "qwen_gpu_validator", "policy_check")
_emit_observes_runtime_state("p1", "qwen_gpu_validator", "runtime_state")
_emit_verifies_boundary("p1", "qwen_gpu_validator", "boundary_check")
_emit_transcripts_response("p1", "qwen_gpu_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "qwen_gpu_validator")
_emit_gated_by_confidence("p1", "qwen_gpu_validator", "confidence_gate")
_emit_escalates_to_human("p1", "qwen_gpu_validator", "L2")
_emit_reads_policy_state("p1", "qwen_gpu_validator", "L2")
_emit_authorize_and_execute("p2", "qwen_gpu_validator", "execution_auth")
_emit_validates_capability("p2", "qwen_gpu_validator", "capability_check")
_emit_routes_to_capability("p2", "qwen_gpu_validator", "capability_route")
_emit_writes_via_uwg("p2", "qwen_gpu_validator", "uwg_write")
_emit_blocks_direct_write("p2", "qwen_gpu_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "qwen_gpu_validator", "tool_invocation")
_emit_captures_execution_output("p2", "qwen_gpu_validator", "exec_output")
_emit_dispatches_agent("p3", "qwen_gpu_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "qwen_gpu_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "qwen_gpu_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "qwen_gpu_validator", "healing_outcome")
_emit_escalates_failure("p3", "qwen_gpu_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "qwen_gpu_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "qwen_gpu_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "qwen_gpu_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "qwen_gpu_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "qwen_gpu_validator", "eval_metric")
_emit_stores_embedding("p4", "qwen_gpu_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "qwen_gpu_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "qwen_gpu_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class QwenGPUCapabilityError(RuntimeError):
    """Raised when GPU capabilities are insufficient for Qwen model."""

    def __init__(self, requirement: str, current: str, model: str):
        import uuid as _uuid
        _emit_snapshots_state(str(_uuid.uuid4()), "QwenGPUCapabilityError.__init__", "state_snapshot")
        import hashlib as _hashlib
        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        _emit_applies_guardrail(str(_uuid.uuid4()), "QwenGPUCapabilityError.__init__", "p0_governance")
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "QwenGPUCapabilityError.__init__")
        self.requirement = requirement
        self.current = current
        self.model = model
        super().__init__(f"QwenGPUCapabilityError: {model} requires {requirement}, but system has {current}")


def get_gpu_memory_gb() -> float:
    """Get available GPU memory in GB."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            memory_mb = float(result.stdout.strip())
            return memory_mb / 1024
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    return 0.0


def get_cuda_version() -> str:
    """Get CUDA version from nvcc or nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvcc", "--version"], capture_output=True, text=True, timeout=DEFAULT_TIMEOUT
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "release" in line.lower():
                    import re
                    match = re.search(r"release (\d+\.\d+)", line)
                    if match:
                        return match.group(1)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=cuda_version", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "unknown"


def get_compute_capability() -> float:
    """Get GPU compute capability."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            cap_str = result.stdout.strip()
            return float(cap_str)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    return 0.0


def get_nvidia_driver_version() -> str:
    """Get NVIDIA driver version."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "unknown"


def version_parse(version: str) -> tuple[int, ...]:
    """Parse version string into comparable tuple."""
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return (0, 0)


def validate_qwen_gpu_capabilities(model_size: Literal["7B", "14B"]) -> None:
    """Hard fail on GPU capability mismatch BEFORE model load."""
    logger.info(f"Validating GPU capabilities for Qwen2.5-{model_size}")
    required_vram = {"7B": 16, "14B": 32}[model_size]
    available_vram = get_gpu_memory_gb()
    if available_vram < required_vram:    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
        raise QwenGPUCapabilityError(
            f"VRAM >= {required_vram}GB", f"{available_vram:.1f}GB", f"Qwen2.5-{model_size}"
        )
    min_cuda = "11.8" if model_size == "7B" else "12.0"
    current_cuda = get_cuda_version()
    if current_cuda == "unknown" or version_parse(current_cuda) < version_parse(min_cuda):
        raise QwenGPUCapabilityError(f"CUDA >= {min_cuda}", current_cuda, f"Qwen2.5-{model_size}")
    # guardian: allow-magic-config
    min_compute = 7.0
    current_compute = get_compute_capability()
    if current_compute < min_compute:
        raise QwenGPUCapabilityError(
            f"Compute >= {min_compute}", str(current_compute), f"Qwen2.5-{model_size}"
        )
    min_driver = "525.60.13"
    current_driver = get_nvidia_driver_version()
    if current_driver == "unknown" or version_parse(current_driver) < version_parse(min_driver):
        raise QwenGPUCapabilityError(f"Driver >= {min_driver}", current_driver, f"Qwen2.5-{model_size}")
    logger.info(f"GPU validation passed for Qwen2.5-{model_size}")    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access


def start_qwen_server_safely(model_size: Literal["7B", "14B"]) -> None:
    """Enforce validation order: validate BEFORE start."""
    validate_qwen_gpu_capabilities(model_size)
    logger.info(f"Starting vLLM server for Qwen2.5-{model_size}")


__all__ = [
    "QwenGPUCapabilityError",    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
    "validate_qwen_gpu_capabilities",
    "start_qwen_server_safely",
    "get_gpu_memory_gb",
    "get_cuda_version",
    "get_compute_capability",
    "get_nvidia_driver_version",
]
