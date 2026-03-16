"""ADG-driven tests for L2_execution/healers/qwen_gpu_validator.py — fan_in=1."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_qwen_gpu_validator_adg")
_emit_applies_guardrail("p0", "test_qwen_gpu_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_qwen_gpu_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_qwen_gpu_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_qwen_gpu_validator_adg")
emit_determinism_digest("p0", "test_qwen_gpu_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_qwen_gpu_validator_adg", "execution_auth")
_emit_validates_capability("p2", "test_qwen_gpu_validator_adg", "capability_check")
_emit_routes_to_capability("p2", "test_qwen_gpu_validator_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_qwen_gpu_validator_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_qwen_gpu_validator_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_qwen_gpu_validator_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_qwen_gpu_validator_adg", "exec_output")
_emit_dispatches_agent("p3", "test_qwen_gpu_validator_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_qwen_gpu_validator_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_qwen_gpu_validator_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_qwen_gpu_validator_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_qwen_gpu_validator_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_qwen_gpu_validator_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_qwen_gpu_validator_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_qwen_gpu_validator_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_qwen_gpu_validator_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_qwen_gpu_validator_adg", "eval_metric")
_emit_stores_embedding("p4", "test_qwen_gpu_validator_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_qwen_gpu_validator_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_qwen_gpu_validator_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.qwen_gpu_validator import (
    QwenGPUCapabilityError,
    get_cuda_version,
    get_gpu_memory_gb,
)


class TestQwenGPUCapabilityError:
    def test_creates(self):
        err = QwenGPUCapabilityError(
            requirement="24GB VRAM",
            current="8GB",
            model="Qwen-72B",
        )
        assert err.requirement == "24GB VRAM"
        assert err.current == "8GB"
        assert err.model == "Qwen-72B"

    def test_is_runtime_error(self):
        assert issubclass(QwenGPUCapabilityError, RuntimeError)

    def test_message_contains_model(self):
        err = QwenGPUCapabilityError("24GB", "8GB", "Qwen-72B")
        assert "Qwen-72B" in str(err)


class TestGetGpuMemoryGb:
    def test_returns_float(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            result = get_gpu_memory_gb()
            assert isinstance(result, float)

    def test_fallback_returns_zero(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = get_gpu_memory_gb()
            assert result == 0.0


class TestGetCudaVersion:
    def test_returns_string(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            result = get_cuda_version()
            assert isinstance(result, str)
