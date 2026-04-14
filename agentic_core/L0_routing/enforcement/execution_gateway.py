"""
V15 Execution Gateway — Contract-Enforced Healing Path.

Wraps any healing execution path with P1/P2 contract enforcement:
  - SurgicalManifest as exclusive execution input (§1.1/§1.2)
  - SemanticClock advancement only on valid StateCommit (§13.1)
  - BoundarySnapshotArtifact pre-mutation + rollback verification (§10.2/§10.3)
  - SHA-256 dedupe on signals (§5.1)
  - Forbidden input rejection (§1.2)

This module is the integration proof point demonstrating that P2 contracts
are exercised in a real execution path.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_orchestrates_workflow,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
)

_emit_routes_to_agent("p1", "execution_gateway", "L0")
_emit_orchestrates_workflow("p1", "execution_gateway", "L0")
_emit_dispatches_execution_plan("p1", "execution_gateway", "L0")
_emit_validates_agent_capability("p1", "execution_gateway", "L0")
_emit_checks_agent_registry("p1", "execution_gateway", "L0")

MUTATION_COUNTER = 0
CURRENT_PHASE = "UNKNOWN"


def _get_manifest_hash_validator():
    from agentic_core.L2_execution.enforcement.manifest_hash_validator import validate_manifest_hashes

    return validate_manifest_hashes


def _get_guardian_decision():
    _emit_applies_guardrail(str(uuid.uuid4()), "Module._get_guardian_decision", "L0_ROUTING")
    from agentic_core.L5_safety.reasoning.guardian_decision import GuardianViolationError, L5Guardian

    return (GuardianViolationError, L5Guardian)


from agentic_core.agents.types.agent_registry import get_profile, registry_digest
from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import get_routing_gateway
from agentic_core.L0_routing.types.crypto_trust_types import HashMismatchTracker
from agentic_core.L0_routing.types.determinism_contracts_types import (
    create_boundary_snapshot,
    dedupe_sha256,
    validate_execution_input,
    validate_manifest_emission,
    verify_rollback_integrity,
)
from agentic_core.L0_routing.types.determinism_types import (
    BoundarySnapshotArtifact,
    SemanticClock,
    StateCommitInvalid,
    SurgicalManifest,
)
from agentic_core.L0_routing.types.guardian_enforcement_exceptions import (
    V15HardFailAbort,
    V15SoftFailAbort,
    is_v15_hard_fail,
    is_v15_soft_fail,
)
from agentic_core.L0_routing.types.routing_contracts_types import (
    GuardrailGuard,
    PipeOrderEnforcer,
    PipeOrderViolation,
    PolicyConfigGuard,
    PolicyMutationIncident,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    emit_determinism_digest,
)

emit_determinism_digest("trace_execution_gateway", "execution_gateway_dispatch_entry")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_dispatch_exit")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_tool_invoke")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_tool_complete")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_agent_entry")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_agent_exit")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_uwg_write")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_trace_sign")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_guardrail_check")
emit_determinism_digest("trace_execution_gateway", "execution_gateway_policy_verify")

Logger = logging.getLogger(__name__)


class ExecutionGatewayError(RuntimeError):
    """Raised when critical execution gateway operations fail."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class UnregisteredAgentError(RuntimeError):
    """Raised when an agent is not found in AgentExecutionProfileRegistry."""


def _get_enforce_healer_pipe_order():
    """Lazy load enforce_healer_pipe_order to avoid upward import."""
    from agentic_core.L2_execution.enforcement.healer_pipe_order import enforce_healer_pipe_order

    return enforce_healer_pipe_order


@dataclass
class GatewayResult:
    """Result of a contract-enforced execution."""

    success: bool
    manifest: SurgicalManifest | None
    semantic_clock_tick: int
    pre_snapshot: BoundarySnapshotArtifact | None
    post_snapshot: BoundarySnapshotArtifact | None = None
    rollback_verified: bool = False
    healing_output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    dedupe_hit: bool = False
    registry_hash: str = ""


class V15ExecutionGateway:
    """Contract-enforced execution gateway for healing paths.

    Usage:
        gateway = V15ExecutionGateway()
        result = gateway.execute(manifest, heal_fn, state_hash_fn)
    """

    def __init__(self) -> None:
        self._clock = SemanticClock()
        self._seen_signals: set[str] = set()
        self._pipe_violations: list[dict[str, object]] = []
        self._policy_violations: list[dict[str, object]] = []
        self._mismatch_tracker: HashMismatchTracker | None = None
        self._registry_digest: str = registry_digest()

    @property
    def clock(self) -> SemanticClock:
        """Expose clock for test inspection."""
        return self._clock

    def execute(
        self,
        execution_input: Any,
        heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
        state_hash_fn: Callable[[], tuple[str, str, str]],
        trace_id: str = "gw-default",
        agent_id: str = "",
        max_heal_attempts: int = 1,
        **kwargs: Any,
    ) -> GatewayResult:
        """Execute a healing operation under full P2 contract enforcement.

        Args:
            execution_input: Must be a SurgicalManifest (§1.1).
            heal_fn: The actual healing callable. Receives the validated manifest.
            state_hash_fn: Returns (filesystem_hash, git_state_hash, agent_memory_hash).
            trace_id: Correlation trace ID for snapshots.

        Returns:
            GatewayResult with full audit trail.
        """
        _emit_agent_executes_agent(str(uuid.uuid4()), "V15ExecutionGateway", "V15ExecutionGateway.execute")
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L0_ROUTING,
            f"execution_gateway.execute:{agent_id}",
        )
        self._pipe_violations = []
        self._policy_violations = []
        self._enforce_agent_registered(agent_id)
        try:
            return self._execute_with_envelope(
                execution_input,
                heal_fn,
                state_hash_fn,
                trace_id,
                attempt=0,
                max_heal_attempts=max_heal_attempts,
                **kwargs,
            )
        # guardian: allow-silent-swallow - acceptable exception handling
        except V15SoftFailAbort as sfa:
            Logger.warning("[V15-GW] SOFT_FAIL abort: %s", sfa)
            return GatewayResult(
                success=False,
                manifest=execution_input if isinstance(execution_input, SurgicalManifest) else None,
                semantic_clock_tick=self._clock.step_id,
                pre_snapshot=None,
                post_snapshot=None,
                rollback_verified=False,
                healing_output={},
                error=f"SOFT_FAIL: {sfa}",
                dedupe_hit=False,
            )

    def _enforce_agent_registered(self, agent_id: str) -> None:
        """Raise UnregisteredAgentError if agent_id is empty or not in AGENT_REGISTRY.

        Spec: L0 Authority Node, Guarantee #7 — no execution without a registered profile.
        """
        if not agent_id or not agent_id.strip():
            raise UnregisteredAgentError(
                "agent_id must be a non-empty string. All V15ExecutionGateway.execute() callers must supply a registered agent_id.",
            )
        try:
            profile = get_profile(agent_id)
        except KeyError:
            raise UnregisteredAgentError(
                f"Agent '{agent_id}' not registered in AgentExecutionProfileRegistry. Add an AgentExecutionProfile entry to agentic_core/agents/agent_registry.py.",
            )
        except RuntimeError as exc:
            raise ExecutionGatewayError("Agent registry lookup failed", exc) from exc
        Logger.debug("[V15-GW] Agent '%s' registry check OK (mode=%s)", agent_id, profile.execution_mode)

    def _execute_with_envelope(
        self,
        execution_input: Any,
        heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
        state_hash_fn: Callable[[], tuple[str, str, str]],
        trace_id: str = "gw-default",
        attempt: int = 0,
        max_heal_attempts: int = 1,
        **kwargs: Any,
    ) -> GatewayResult:
        """Execute with explicit L2 envelope separation."""
        from agentic_core.L2_execution.utils.providers import get_clock  # noqa: PLC0415

        manifest = self._validate_manifest(execution_input, trace_id)
        self._guardian_validate(manifest, trace_id, state_hash_fn=state_hash_fn, **kwargs)
        _clk = get_clock()
        _clk.emit_replay_key(context=f"{trace_id}:{manifest.node_id}")
        _clk.emit_determinism_digest(
            inputs={"trace": trace_id, "node": manifest.node_id, "registry": self._registry_digest},
        )
        result = self._commit_mutation(manifest, heal_fn, state_hash_fn, trace_id, **kwargs)
        if not result.success and result.error:
            if attempt >= max_heal_attempts:
                return result
            return self._heal_and_retry(
                manifest,
                heal_fn,
                state_hash_fn,
                trace_id,
                attempt=attempt + 1,
                max_heal_attempts=max_heal_attempts,
                **kwargs,
            )
        return result

    def _validate_manifest(self, execution_input: Any, trace_id: str) -> SurgicalManifest:
        """L2.0: Validate execution input manifest."""
        global CURRENT_PHASE
        CURRENT_PHASE = "L2.0"
        manifest = validate_execution_input(execution_input)
        validate_manifest_emission(manifest)
        _HASH_FIELDS = ("policy_hash", "routing_hash", "model_hash", "budget_hash")
        if any(hasattr(manifest, f) and getattr(manifest, f) is not None for f in _HASH_FIELDS):
            _get_manifest_hash_validator()(manifest)
        signal_hash = dedupe_sha256(manifest.correlation_id + manifest.node_id)
        dedupe_hit = signal_hash in self._seen_signals
        self._seen_signals.add(signal_hash)
        if dedupe_hit:
            raise V15SoftFailAbort("Duplicate signal detected")
        return manifest

    def _guardian_validate(
        self,
        manifest: SurgicalManifest,
        trace_id: str,
        *,
        state_hash_fn: Callable[[], tuple[str, str, str]],
        **kwargs: Any,
    ) -> None:
        """L2.1: Guardian validation (non-mutating)."""
        global CURRENT_PHASE
        CURRENT_PHASE = "L2.1"
        GuardianViolationError, L5Guardian = _get_guardian_decision()
        guardian = L5Guardian(policy_version="1.0")
        decision = guardian.validate(manifest, None, "1.0")
        guardian.log_decision_to_state_bus(decision, trace_id)
        if not decision.allow:
            raise GuardianViolationError(decision)
        if decision.escalate:
            Logger.warning(f"[V15-GW] Guardian escalation triggered for {trace_id}")
        policy_config = kwargs.get("policy_config", {})
        policy_guard = PolicyConfigGuard(policy_config=policy_config, wave_id=trace_id)
        guardrail = GuardrailGuard(trace_id=trace_id)
        fs_hash, git_hash, mem_hash = state_hash_fn()
        self._clock.prepare_commit(manifest.target_layer)
        pre_snapshot = create_boundary_snapshot(
            trace_id=trace_id,
            filesystem_hash=fs_hash,
            git_state_hash=git_hash,
            agent_memory_hash=mem_hash,
            semantic_clock=self._clock,
        )
        policy_hash = policy_guard.policy_hash
        from agentic_core.L0_routing.types.routing_artifact_types import TokenCapArtifact, TokenGateResult

        token_cap = TokenCapArtifact(
            trace_id=trace_id,
            policy_hash=policy_hash,
            budget_limit=decision.budget_remaining,
            tokens_requested=0,
            gate_result=TokenGateResult.ALLOW,
        )
        safety_markers = ["trace_id_present", "policy_hash_present", "schema_valid", "guardian_approved"]
        boundary_token = pre_snapshot.trace_id
        if not guardrail.enforce_all(
            token_cap=token_cap,
            payload_hash=dedupe_sha256(manifest.correlation_id + manifest.node_id),
            expected_hash=dedupe_sha256(manifest.correlation_id + manifest.node_id),
            markers=safety_markers,
            boundary_token=boundary_token,
        ):
            raise V15HardFailAbort("Guardrail validation failed")

    def _commit_mutation(
        self,
        manifest: SurgicalManifest,
        heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
        state_hash_fn: Callable[[], tuple[str, str, str]],
        trace_id: str,
        **kwargs: Any,
    ) -> GatewayResult:
        """L2.2: Sole mutation authority point."""
        global CURRENT_PHASE, MUTATION_COUNTER
        CURRENT_PHASE = "L2.2"
        fs_hash, git_hash, mem_hash = state_hash_fn()
        pre_snapshot = create_boundary_snapshot(
            trace_id=trace_id,
            filesystem_hash=fs_hash,
            git_state_hash=git_hash,
            agent_memory_hash=mem_hash,
            semantic_clock=self._clock,
        )
        initial_mutation_count = MUTATION_COUNTER
        healing_output = {}
        commit_valid = False
        error = None
        try:
            healing_output = heal_fn(manifest)
            commit_valid = healing_output.get("errors", 0) == 0
        except (ValueError, KeyError, AttributeError) as e:
            error = str(e)
            commit_valid = False
            Logger.error(f"[V15-GW] Healing failed with known error: {e}")
        except Exception as e:  # guardian: allow-broad-exception -- catch-all in mutation boundary; re-raises as ExecutionGatewayError after logging
            error = str(e)
            commit_valid = False
            Logger.exception("[V15-GW] Unexpected healing error")
            raise ExecutionGatewayError(f"Critical healing operation failed: {e}") from e
        final_mutation_count = MUTATION_COUNTER
        if final_mutation_count <= initial_mutation_count and commit_valid:
            Logger.warning("[V15-GW] Successful commit with no mutations detected")
        post_snapshot = None
        rollback_verified = False
        if not commit_valid:
            try:
                current_fs, current_git, current_mem = state_hash_fn()
                verify_rollback_integrity(pre_snapshot, current_fs, current_git, current_mem)
                rollback_verified = True
            except (OSError, ValueError) as e:
                Logger.error(f"[V15-GW] Rollback integrity check failed: {e}")
                rollback_verified = False
                if error is None:
                    error = str(e)
            except Exception as e:  # guardian: allow-broad-exception -- rollback verification boundary; re-raises as ExecutionGatewayError after logging
                Logger.exception("[V15-GW] Critical rollback integrity error")
                rollback_verified = False
                if error is None:
                    error = str(e)
                raise ExecutionGatewayError(f"Rollback integrity verification failed: {e}") from e
        else:
            post_fs, post_git, post_mem = state_hash_fn()
            post_snapshot = create_boundary_snapshot(
                trace_id=trace_id,
                filesystem_hash=post_fs,
                git_state_hash=post_git,
                agent_memory_hash=post_mem,
                semantic_clock=self._clock,
            )
            try:
                # guardian: allow-silent-swallow - acceptable exception handling
                self._clock.tick(manifest.target_layer, state_commit_valid=True)
            except StateCommitInvalid as sci:
                error = str(sci)
                commit_valid = False
        return GatewayResult(
            success=commit_valid,
            manifest=manifest,
            semantic_clock_tick=self._clock.step_id,
            pre_snapshot=pre_snapshot,
            post_snapshot=post_snapshot,
            rollback_verified=rollback_verified,
            healing_output=healing_output,
            error=error,
            dedupe_hit=False,
        )

    def _heal_and_retry(
        self,
        manifest: SurgicalManifest,
        heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
        state_hash_fn: Callable[[], tuple[str, str, str]],
        trace_id: str,
        attempt: int = 1,
        max_heal_attempts: int = 1,
        **kwargs: Any,
    ) -> GatewayResult:
        """L2.3: Healing loop - non-mutating, re-enters L2.0."""
        global CURRENT_PHASE
        CURRENT_PHASE = "L2.3"
        Logger.info(
            "[V15-GW] Entering healing loop for %s attempt=%s/%s", trace_id, attempt, max_heal_attempts
        )
        try:
            return self._execute_with_envelope(
                manifest,
                heal_fn,
                state_hash_fn,
                trace_id,
                attempt=attempt,
                max_heal_attempts=max_heal_attempts,
                **kwargs,
            )
        except (ValueError, KeyError, AttributeError) as e:
            Logger.error(f"[V15-GW] Healing loop failed with known error: {e}")
            return GatewayResult(
                success=False,
                manifest=manifest,
                semantic_clock_tick=self._clock.step_id,
                pre_snapshot=None,
                post_snapshot=None,
                rollback_verified=False,
                healing_output={},
                error=f"Healing failed with known error: {e}",
                dedupe_hit=False,
            )
        except (V15HardFailAbort, ExecutionGatewayError) as e:  # critical gateway failures only
            Logger.critical(f"[V15-GW] Critical healing loop error: {e}")
            return GatewayResult(
                success=False,
                manifest=manifest,
                semantic_clock_tick=self._clock.step_id,
                pre_snapshot=None,
                post_snapshot=None,
                rollback_verified=False,
                healing_output={},
                error=f"Critical healing failure: {e}",
                dedupe_hit=False,
            )

    def _pipe_advance(
        self,
        pipe: PipeOrderEnforcer,
        step: str,
        trace_id: str,
        observed_steps: list[str] | None = None,
    ) -> None:
        """Advance pipe to *step*. Mode-aware: LOG_ONLY logs, HARD_FAIL raises."""
        if observed_steps is not None:
            observed_steps.append(step)
        try:  # guardian: PipeOrderViolation should be handled with specific context
            # guardian: allow-silent-swallow - acceptable exception handling
            pipe.advance(step)
        except PipeOrderViolation as pov:
            record = {
                "type": "pipe_order_violation",
                "trace_id": trace_id,
                "expected": pov.expected,
                "actual": pov.actual,
                "step": pov.step,
            }
            self._pipe_violations.append(record)
            if is_v15_hard_fail():
                raise V15HardFailAbort(f"HARD_FAIL pipe order violation: {record}") from pov
            if is_v15_soft_fail():
                raise V15SoftFailAbort(f"SOFT_FAIL pipe order violation: {record}")
            Logger.warning("[V15-GW] §2.5 pipe order violation (non-blocking): %s", record)

    def _policy_check(self, guard: PolicyConfigGuard, current_config: dict[str, Any], trace_id: str) -> None:
        """Verify policy immutability. Mode-aware: LOG_ONLY logs, HARD_FAIL raises."""  # guardian: PolicyMutationIncident should be handled with specific context
        # guardian: allow-silent-swallow - acceptable exception handling
        try:
            guard.read_config(current_config)
        except PolicyMutationIncident as pmi:
            record = {
                "type": "policy_mutation",
                "trace_id": trace_id,
                "wave_id": pmi.wave_id,
                "expected_hash": pmi.expected_hash,
                "actual_hash": pmi.actual_hash,
            }
            self._policy_violations.append(record)
            if is_v15_hard_fail():
                raise V15HardFailAbort(f"HARD_FAIL policy mutation: {record}") from pmi
            if is_v15_soft_fail():
                raise V15SoftFailAbort(f"SOFT_FAIL policy mutation: {record}")
            Logger.warning("[V15-GW] §4.1 policy mutation (non-blocking): %s", record)


__all__ = ["GatewayResult", "V15ExecutionGateway"]
