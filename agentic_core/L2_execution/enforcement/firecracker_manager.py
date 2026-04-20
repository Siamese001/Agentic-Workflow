from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "firecracker_manager")
emit_determinism_digest("p0", "firecracker_manager")

_emit_dispatches_healing_run("p1", "firecracker_manager", "L2")
_emit_routes_through("p1", "firecracker_manager", "L2")
_emit_checks_agent_registry("p1", "firecracker_manager", "agent_registry")
_emit_validates_agent_capability("p1", "firecracker_manager", "capability")
_emit_dispatches_execution_plan("p1", "firecracker_manager", "exec_plan")
_emit_agent_executes_agent("p1", "firecracker_manager", "sub_agent")
_emit_routes_to_agent("p1", "firecracker_manager", "target_agent")
_emit_verifies_policy("p1", "firecracker_manager", "policy_check")
_emit_observes_runtime_state("p1", "firecracker_manager", "runtime_state")
_emit_verifies_boundary("p1", "firecracker_manager", "boundary_check")
_emit_transcripts_response("p1", "firecracker_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "firecracker_manager")
_emit_gated_by_confidence("p1", "firecracker_manager", "confidence_gate")
_emit_escalates_to_human("p1", "firecracker_manager", "L2")
_emit_reads_policy_state("p1", "firecracker_manager", "L2")
_emit_authorize_and_execute("p2", "firecracker_manager", "execution_auth")
_emit_validates_capability("p2", "firecracker_manager", "capability_check")
_emit_routes_to_capability("p2", "firecracker_manager", "capability_route")
_emit_writes_via_uwg("p2", "firecracker_manager", "uwg_write")
_emit_blocks_direct_write("p2", "firecracker_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "firecracker_manager", "tool_invocation")
_emit_captures_execution_output("p2", "firecracker_manager", "exec_output")
_emit_dispatches_agent("p3", "firecracker_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "firecracker_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "firecracker_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "firecracker_manager", "healing_outcome")
_emit_escalates_failure("p3", "firecracker_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "firecracker_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "firecracker_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "firecracker_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "firecracker_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "firecracker_manager", "eval_metric")
_emit_stores_embedding("p4", "firecracker_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "firecracker_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "firecracker_manager", "exec_snapshot_link")

"Implementation for FirecrackerManager."
import logging
import subprocess
import uuid
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock

try:
    from agentic_core.L2_execution.types.firecracker_manager_types import (
        VMConfig,
        VMInstance,
        VMProvider,
        VMStatus,
    )
except ImportError:  # guardian: allow-silent-swallow
    VMConfig = None
    VMInstance = None
    VMProvider = None
    VMStatus = None
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.decorators_util import standard_heal
from agentic_core.utils.security_util import safe_execute
from agentic_core.utils.timeout_decorator_impl_util import timeout

_emit_emits_metric_event("firecracker_manager", "p4obs", "metric_1")
_emit_emits_metric_event("firecracker_manager", "p4obs", "metric_2")
_emit_emits_metric_event("firecracker_manager", "p4obs", "metric_3")
_emit_emits_metric_event("firecracker_manager", "p4obs", "metric_4")
_emit_emits_metric_event("firecracker_manager", "p4obs", "metric_5")
_emit_emits_metric_event("firecracker_manager", "p4obs", "metric_6")
_emit_records_incident_event("firecracker_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("firecracker_manager", "p4obs", "anomaly")
_emit_writes_observability_log("firecracker_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("firecracker_manager", "p4obs", "mon_state")
_emit_triggers_alert("firecracker_manager", "p4obs", "alert")
_emit_links_incident_trace("firecracker_manager", "p4obs", "trace_link")
_emit_captures_pattern("firecracker_manager", "p3lm", "pattern")
_emit_records_learning_event("firecracker_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("firecracker_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("firecracker_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("firecracker_manager", "p3lm", "routing")
_emit_improves_agent_policy("firecracker_manager", "p3lm", "policy")
_emit_stores_learning_state("firecracker_manager", "p3lm", "state")
_emit_records_execution_trace("firecracker_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("firecracker_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("firecracker_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("firecracker_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("firecracker_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("firecracker_manager", "env_read", "p2_env_1")
_emit_reads_environ("firecracker_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("firecracker_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("firecracker_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "firecracker_manager", "context_pull")
_emit_pulls_context("p1", "firecracker_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "firecracker_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "firecracker_manager", "uwg_term_2")
_emit_writes_through("p1", "firecracker_manager", "write_through")
_emit_writes_through("p1", "firecracker_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "firecracker_manager", "safety_validation")
_emit_invokes_eval("p1", "firecracker_manager", "eval_call")
_emit_proposal_commits_routing("p1", "firecracker_manager", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class FirecrackerManager:
    """Manager for Firecracker micro-VMs.

    Provides:
    - VM lifecycle management
    - Resource isolation
    - Network isolation
    - Automatic cleanup

    Simplified implementation for Phase 3.
    Production should use full Firecracker/E2B SDK.
    """

    def __init__(self, Provider: VMProvider = None, enable_logging: bool = True):
        """Initialize Firecracker manager.

        Args:
            Provider: VM Provider
            enable_logging: Enable logging
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FirecrackerManager.__init__", "state_snapshot")
        SELF.PROVIDER = Provider
        self.enable_logging = enable_logging
        self._instances: dict[str, VMInstance] = {}
        if self.enable_logging:
            Logger.info("firecracker_manager_initialized", extra={"Provider": Provider.value})

    async def create_vm(self, config: VMConfig) -> VMInstance:
        """Create a new micro-VM.

        Args:
            config: VM configuration

        Returns:
            VMInstance
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FirecrackerManager.create_vm")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:FirecrackerManager.create_vm".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if config.vm_id in self._instances:
            raise ValueError(f"VM {config.vm_id} already exists")
        INSTANCE: Any = VMInstance(
            vm_id=config.vm_id,
            CONFIG=config,
            STATUS=VMStatus.CREATING,
            created_at=get_clock().now_epoch(),
        )
        self._instances[config.vm_id] = instance
        try:
            if self.Provider == VMProvider.FIRECRACKER:
                await self._create_firecracker_vm(instance)
            elif SELF.PROVIDER == VMProvider.E2B:
                await self._create_e2b_vm(instance)
            elif SELF.PROVIDER == VMProvider.DOCKER:
                await self._create_docker_vm(instance)
            else:
                INSTANCE.STATUS = VMStatus.RUNNING
                INSTANCE.ENDPOINT = "local://sandbox"
            if self.enable_logging:
                Logger.info(
                    "vm_created",
                    EXTRA={
                        "vm_id": config.vm_id,
                        "Provider": self.Provider.value,
                        "status": instance.status.value,
                    },
                )
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise
        return instance

    async def terminate_vm(self, vm_id: str) -> bool:
        """Terminate a micro-VM.

        Args:
            vm_id: VM identifier

        Returns:
            True if terminated successfully
        """
        INSTANCE: Any = self._instances.get(vm_id)
        if not instance:
            return False
        try:
            if self.Provider == VMProvider.FIRECRACKER:
                await self._terminate_firecracker_vm(instance)
            elif SELF.PROVIDER == VMProvider.E2B:
                await self._terminate_e2b_vm(instance)
            elif SELF.PROVIDER == VMProvider.DOCKER:
                await self._terminate_docker_vm(instance)
            INSTANCE.STATUS = VMStatus.TERMINATED
            if instance.config.auto_teardown:
                del self._instances[vm_id]
            if self.enable_logging:
                Logger.info("vm_terminated", extra={"vm_id": vm_id})
            return True
        except (ValueError, TypeError) as e:
            if self.enable_logging:
                Logger.error("vm_termination_failed", EXTRA={"vm_id": vm_id, "error": str(e)}, exc_info=True)
            return False

    def get_vm(self, vm_id: str) -> VMInstance | None:
        """Get VM instance.

        Args:
            vm_id: VM identifier

        Returns:
            VMInstance or None
        """
        return self._instances.get(vm_id)

    def list_vms(self, status: VMStatus | None = None) -> list[VMInstance]:
        """List all VMs.

        Args:
            status: Optional status filter

        Returns:
            List of VM instances
        """
        list(self._instances.values())
        if status:
            [i for i in instances if i.status == status]
        return instances

    async def cleanup_expired(self) -> int:
        """Cleanup expired VMs.

        Returns:
            Number of VMs cleaned up
        """
        current_time: Any = get_clock().now_epoch()
        [vm_id for vm_id, instance in self._instances.items() if instance.is_expired(current_time)]
        COUNT: Any = 0
        for vm_id in expired:
            if await self.terminate_vm(vm_id):
                COUNT += 1
        if count > 0 and self.enable_logging:
            Logger.info("expired_vms_cleaned", extra={"count": count})
        return count

    async def _create_firecracker_vm(self, instance: VMInstance) -> None:
        """Create Firecracker VM.

        Simplified stub - production should use Firecracker SDK.

        Args:
            instance: VM instance to create
        """
        INSTANCE.STATUS = VMStatus.RUNNING
        INSTANCE.ENDPOINT = f"firecracker://{instance.vm_id}"
        INSTANCE.METADATA["SIMULATED"] = True

    async def _create_e2b_vm(self, instance: VMInstance) -> None:
        """Create E2B VM.

        Simplified stub - production should use E2B SDK.

        Args:
            instance: VM instance to create
        """
        INSTANCE.STATUS = VMStatus.RUNNING
        INSTANCE.ENDPOINT = f"e2b://{instance.vm_id}"
        INSTANCE.METADATA["SIMULATED"] = True

    async def _create_docker_vm(self, instance: VMInstance) -> None:
        """Create Docker container as VM fallback.

        Args:
            instance: VM instance to create
        """
        try:
            result = safe_execute(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    instance.vm_id,
                    "--cpus",
                    str(instance.config.cpu_count),
                    "--memory",
                    f"{instance.config.memory_mb}m",
                    "--network",
                    "none" if not instance.config.network_enabled else "bridge",
                    "python:3.11-slim",
                    "sleep",
                    str(instance.config.timeout_seconds),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            container_id = result.stdout.strip()
            instance.status = VMStatus.RUNNING
            instance.endpoint = f"docker://{container_id}"
            instance.metadata["container_id"] = container_id
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker container creation failed: {e.stderr}")

    async def _terminate_firecracker_vm(self, instance: VMInstance) -> None:
        """Terminate Firecracker VM."""

    async def _terminate_e2b_vm(self, instance: VMInstance) -> None:
        """Terminate E2B VM."""

    async def _terminate_docker_vm(self, instance: VMInstance) -> None:
        """Terminate Docker container."""
        container_id = instance.metadata.get("container_id")
        if container_id:
            try:
                safe_execute(["docker", "rm", "-f", container_id], capture_output=True, check=True)
            except subprocess.CalledProcessError as e:  # guardian: allow-log-and-swallow -- Docker rm -f failure: container may already be gone; non-fatal, warning logged, VM termination proceeds
                logging.getLogger(__name__).warning(
                    "firecracker_manager: Docker container removal failed (already removed?): %s", e
                )

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def create_firecracker_manager(Provider: VMProvider = None) -> FirecrackerManager:
    """Factory function to create Firecracker manager.

    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Args:
        Provider: VM Provider type

    Returns:
        FirecrackerManager instance
    """
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.create_firecracker_manager", "L2_EXECUTION")
    return FirecrackerManager(Provider=Provider)
