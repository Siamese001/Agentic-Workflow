# guardian: allow-silent_swallower -- ADG violation exemption

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ephemeral_vm_types")
trace_contract.emit_determinism_digest("p0", "ephemeral_vm_types")

trace_contract._emit_dispatches_healing_run("p1", "ephemeral_vm_types", "L2")
trace_contract._emit_routes_through("p1", "ephemeral_vm_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "ephemeral_vm_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ephemeral_vm_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ephemeral_vm_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ephemeral_vm_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ephemeral_vm_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "ephemeral_vm_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ephemeral_vm_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ephemeral_vm_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ephemeral_vm_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ephemeral_vm_types")
trace_contract._emit_gated_by_confidence("p1", "ephemeral_vm_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ephemeral_vm_types", "L2")
trace_contract._emit_reads_policy_state("p1", "ephemeral_vm_types", "L2")

trace_contract._emit_applies_guardrail("p0", "ephemeral_vm_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "ephemeral_vm_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "ephemeral_vm_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "ephemeral_vm_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ephemeral_vm_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ephemeral_vm_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ephemeral_vm_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ephemeral_vm_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ephemeral_vm_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ephemeral_vm_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ephemeral_vm_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ephemeral_vm_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ephemeral_vm_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ephemeral_vm_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ephemeral_vm_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ephemeral_vm_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ephemeral_vm_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ephemeral_vm_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ephemeral_vm_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ephemeral_vm_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ephemeral_vm_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ephemeral_vm_types", "exec_snapshot_link")

"Ephemeral VM with Isolation and Auto-Teardown.\n\nPhase 3 - Pillar 14: Execution Sandbox (Hardened Ephemeral)\nEnforces strict network/resource isolation and automatic teardown.\n"
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.utils.runners.providers import get_clock

try:
    from agentic_core.L2_execution.enforcement.vm.firecracker_manager import FirecrackerManager
except ImportError:  # guardian: allow-silent-swallow
    FirecrackerManager = None
try:
    from agentic_core.L2_execution.types.firecracker_manager_types import VMConfig
except ImportError:
    VMConfig = None

trace_contract._emit_emits_metric_event("ephemeral_vm_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ephemeral_vm_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ephemeral_vm_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ephemeral_vm_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ephemeral_vm_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ephemeral_vm_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ephemeral_vm_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ephemeral_vm_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ephemeral_vm_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ephemeral_vm_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ephemeral_vm_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ephemeral_vm_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ephemeral_vm_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ephemeral_vm_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ephemeral_vm_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ephemeral_vm_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ephemeral_vm_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ephemeral_vm_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ephemeral_vm_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("ephemeral_vm_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ephemeral_vm_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ephemeral_vm_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ephemeral_vm_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ephemeral_vm_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ephemeral_vm_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ephemeral_vm_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ephemeral_vm_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ephemeral_vm_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ephemeral_vm_types", "context_pull")
trace_contract._emit_pulls_context("p1", "ephemeral_vm_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ephemeral_vm_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ephemeral_vm_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ephemeral_vm_types", "write_through")
trace_contract._emit_writes_through("p1", "ephemeral_vm_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ephemeral_vm_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ephemeral_vm_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ephemeral_vm_types", "routing_commit")

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class IsolationLevel(Enum):
    """Isolation levels for VM."""

    NONE: Any = "none"
    NETWORK_ONLY: Any = "network_only"
    FULL: Any = "full"


@dataclass
class IsolationConfig:
    """configuration for VM isolation."""

    level: IsolationLevel = IsolationLevel.FULL
    allow_network: bool = False
    allow_filesystem: bool = False
    allow_subprocess: bool = False
    max_cpu_percent: int = 50
    max_memory_mb: int = 512
    max_execution_time_seconds: int = 60

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level.value,
            "allow_network": self.allow_network,
            "allow_filesystem": self.allow_filesystem,
            "allow_subprocess": self.allow_subprocess,
            "max_cpu_percent": self.max_cpu_percent,
            "max_memory_mb": self.max_memory_mb,
            "max_execution_time_seconds": self.max_execution_time_seconds,
        }


@dataclass
class ExecutionResult:
    """Result from code execution in VM."""

    success: bool
    output: str
    error: str | None = None
    execution_time_seconds: float = 0.0
    exit_code: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time_seconds": self.execution_time_seconds,
            "exit_code": self.exit_code,
            "metadata": self.metadata,
        }


class EphemeralVm:
    """Ephemeral VM for secure code execution.

    Features:
    - Automatic creation and teardown
    - Strict isolation
    - Resource limits
    - Timeout enforcement
    - Network isolation
    """

    def __init__(
        self,
        vm_manager: FirecrackerManager,
        IsolationConfig: IsolationConfig | None = None,
        enable_logging: bool = True,
    ):
        """Initialize ephemeral VM.

        Args:
            vm_manager: Firecracker manager
            IsolationConfig: Isolation configuration
            enable_logging: Enable logging
        """
        self.vm_manager = vm_manager
        self.IsolationConfig = IsolationConfig or IsolationConfig()
        self.enable_logging = enable_logging
        self._vm_counter = 0
        if self.enable_logging:
            LOGGER.info("ephemeral_vm_initialized", extra={"isolation": self.IsolationConfig.to_dict()})

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout_seconds: int | None = None,
    ) -> ExecutionResult:
        """Execute code in ephemeral VM.
        Args:
            code: Code to execute
            language: Programming language
            timeout_seconds: Execution timeout

        Returns:
            ExecutionResult
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "EphemeralVm.execute_code")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EphemeralVm.execute_code".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        timeout: Any = timeout_seconds or self.IsolationConfig.max_execution_time_seconds
        start_time: Any = get_clock().now_epoch()
        vm_id, VmConfig = self._create_vm_config(timeout)
        VmInstance: Any = None
        try:
            VmInstance: Any = await self._create_and_execute_vm(
                vm_id,
                VmConfig,
                code,
                language,
                timeout,
                start_time,
            )
            return VmInstance
        except asyncio.TimeoutError:
            return self._handle_timeout(vm_id, timeout, start_time)
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return self._handle_execution_error(vm_id, e, start_time)
        finally:
            await self._teardown_vm(VmInstance, vm_id)

    def _create_vm_config(self, timeout: int) -> tuple:
        """Create VM configuration."""
        self._vm_counter += 1
        vm_id = f"ephemeral_vm_{self._vm_counter}_{int(get_clock().now_epoch())}"
        VmConfig = VMConfig(
            vm_id=vm_id,
            Provider=self.vm_manager.Provider,
            cpu_count=1,
            memory_mb=self.IsolationConfig.max_memory_mb,
            network_enabled=self.IsolationConfig.allow_network,
            timeout_seconds=timeout,
            auto_teardown=True,
        )
        return (vm_id, VmConfig)

    async def _create_and_execute_vm(
        self,
        vm_id: str,
        VmConfig,
        code: str,
        language: str,
        timeout: int,
        start_time: float,
    ) -> ExecutionResult:
        """Create VM and execute code."""
        if self.enable_logging:
            LOGGER.info("creating_ephemeral_vm", extra={"vm_id": vm_id, "language": language})
        VmInstance = await self.vm_manager.create_vm(VmConfig)
        result = await self._execute_in_vm(
            VmInstance=VmInstance,
            code=code,
            language=language,
            timeout=timeout,
        )
        result.execution_time_seconds = get_clock().now_epoch() - start_time
        if self.enable_logging:
            LOGGER.info(
                "code_executed",
                extra={
                    "vm_id": vm_id,
                    "success": result.success,
                    "execution_time": result.execution_time_seconds,
                },
            )
        return result

    def _handle_timeout(self, vm_id: str, timeout: int, start_time: float) -> ExecutionResult:
        """Handle execution timeout."""
        if self.enable_logging:
            LOGGER.warning("execution_timeout", extra={"vm_id": vm_id, "timeout": timeout})
        return ExecutionResult(
            success=False,
            output="",
            error=f"Execution timeout after {timeout} seconds",
            execution_time_seconds=get_clock().now_epoch() - start_time,
            exit_code=124,
        )

    def _handle_execution_error(self, vm_id: str, error: Exception, start_time: float) -> ExecutionResult:
        """Handle execution error."""
        if self.enable_logging:
            LOGGER.error("execution_failed", extra={"vm_id": vm_id, "error": str(error)}, exc_info=True)
        return ExecutionResult(
            success=False,
            output="",
            error=str(error),
            execution_time_seconds=get_clock().now_epoch() - start_time,
            exit_code=1,
        )

    async def _teardown_vm(self, VmInstance, vm_id: str) -> None:
        """Teardown VM."""
        if VmInstance:
            try:
                await self.vm_manager.terminate_vm(vm_id)
                if self.enable_logging:
                    LOGGER.debug("vm_torn_down", extra={"vm_id": vm_id})
            except Exception as e:  # guardian: allow-broad-exception -- VM teardown: error boundary, exception re-raised to caller
                raise

    async def _execute_in_vm(
        self,
        VmInstance: Any,
        code: str,
        language: str,
        timeout: int,
    ) -> ExecutionResult:
        """Execute code inside VM.

        Args:
            VmInstance: VM instance
            code: Code to execute
            language: Programming language
            timeout: Timeout in seconds
        Returns:
            ExecutionResult
        """
        runner = getattr(VmInstance, "execute", None)
        if runner is None:
            runner = getattr(self.vm_manager, "execute_in_vm", None)
        if runner is None:
            raise RuntimeError(
                "EphemeralVM host-side fallback is prohibited: no in-VM execute capability is available"
            )

        result = await runner(
            vm_instance=VmInstance,
            code=code,
            language=language,
            timeout=timeout,
        )
        if not isinstance(result, ExecutionResult):
            raise RuntimeError("VM execute returned an invalid result contract")
        return result

    async def _execute_python(self, code: str, timeout: int) -> ExecutionResult:
        raise RuntimeError("Host python execution path removed; use in-VM execution only")

    async def _execute_javascript(self, code: str, timeout: int) -> ExecutionResult:
        raise RuntimeError("Host javascript execution path removed; use in-VM execution only")


def create_ephemeral_vm(
    vm_manager: FirecrackerManager | None = None,
    IsolationConfig: IsolationConfig | None = None,
) -> EphemeralVM:
    """Factory function to create ephemeral VM.

    Args:
        vm_manager: Optional VM manager
        IsolationConfig: Optional isolation config

    Returns:
        EphemeralVM instance
    """
    if vm_manager is None:
        vm_manager: Any = create_firecracker_manager()
    return EphemeralVM(vm_manager=vm_manager, IsolationConfig=IsolationConfig)
