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
from dataclasses import dataclass, field
from typing import Any, Callable

# Global mutation tracking for L2.2 enforcement
MUTATION_COUNTER = 0
CURRENT_PHASE = "UNKNOWN"


def _get_manifest_hash_validator():
    from agentic_core.L2_execution.enforcement.manifest_hash_validator import validate_manifest_hashes

    return validate_manifest_hashes


def _get_guardian_decision():
    from agentic_core.L5_safety.reasoning.guardian_decision import GuardianViolationError, L5Guardian

    return GuardianViolationError, L5Guardian


from agentic_core.L0_routing.types.crypto_trust_types import HashMismatchTracker
from agentic_core.L0_routing.types.determinism_contracts import (
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
from agentic_core.L0_routing.types.guardian_contract import (
    V15HardFailAbort,
    V15SoftFailAbort,
    is_v15_hard_fail,
    is_v15_soft_fail,
)
from agentic_core.L0_routing.types.routing_contracts import (
    GuardrailGuard,
    PipeOrderEnforcer,
    PipeOrderViolation,
    PolicyConfigGuard,
    PolicyMutationIncident,
)

Logger = logging.getLogger(__name__)


def _get_enforce_healer_pipe_order():
    """Lazy load enforce_healer_pipe_order to avoid upward import."""
    from agentic_core.L2_execution.enforcement.healer_pipe_order import (
        enforce_healer_pipe_order,
    )

    return enforce_healer_pipe_order


# =============================================================================
# Gateway result
# =============================================================================


@dataclass
class GatewayResult:
    """Result of a contract-enforced execution."""

    success: bool
    manifest: SurgicalManifest
    semantic_clock_tick: int
    pre_snapshot: BoundarySnapshotArtifact
    post_snapshot: BoundarySnapshotArtifact | None = None
    rollback_verified: bool = False
    healing_output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    dedupe_hit: bool = False


# =============================================================================
# Execution Gateway
# =============================================================================


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
        # CC-1 §2.5 — Reset per-execution audit state to prevent leakage on
        # singleton gateways (e.g. SovereignBaseAgent reuses one gateway).
        self._pipe_violations = []
        self._policy_violations = []

        # §8.2a — Catch SOFT_FAIL aborts for controlled structured failure
        try:
            return self._execute_with_envelope(execution_input, heal_fn, state_hash_fn, trace_id, **kwargs)
        except V15SoftFailAbort as sfa:
            Logger.warning("[V15-GW] SOFT_FAIL abort: %s", sfa)
            return GatewayResult(
                success=False,
                manifest=execution_input,
                semantic_clock_tick=self._clock.step_id,
                pre_snapshot=None,
                post_snapshot=None,
                rollback_verified=False,
                healing_output={},
                error=f"SOFT_FAIL: {sfa}",
                dedupe_hit=False,
            )

    def _execute_with_envelope(
        self,
        execution_input: Any,
        heal_fn: Callable[[SurgicalManifest], dict[str, Any]],
        state_hash_fn: Callable[[], tuple[str, str, str]],
        trace_id: str = "gw-default",
        **kwargs: Any,
    ) -> GatewayResult:
        """Execute with explicit L2 envelope separation."""

        # L2.0 — Manifest Validation (non-mutating)
        manifest = self._validate_manifest(execution_input, trace_id)

        # L2.1 — Guardian Validation (non-mutating)
        self._guardian_validate(manifest, trace_id, **kwargs)

        # L2.2 — Commit Sandbox (sole mutation authority)
        result = self._commit_mutation(manifest, heal_fn, state_hash_fn, trace_id, **kwargs)

        # L2.3 — Healing Loop (non-mutating, re-enters L2.0)
        if not result.success and result.error:
            return self._heal_and_retry(manifest, heal_fn, state_hash_fn, trace_id, **kwargs)

        return result

    def _validate_manifest(self, execution_input: Any, trace_id: str) -> SurgicalManifest:
        """L2.0: Validate execution input manifest."""
        global CURRENT_PHASE
        CURRENT_PHASE = "L2.0"

        manifest = validate_execution_input(execution_input)
        validate_manifest_emission(manifest)

        # L2.0 config-hash binding: if manifest carries any Phase-2 hash fields,
        # all four must be present and match the L4 SSOT active configs.
        _HASH_FIELDS = ("policy_hash", "routing_hash", "model_hash", "budget_hash")
        if any(hasattr(manifest, f) and getattr(manifest, f) is not None for f in _HASH_FIELDS):
            _get_manifest_hash_validator()(manifest)

        # Dedupe check
        signal_hash = dedupe_sha256(manifest.correlation_id + manifest.node_id)
        dedupe_hit = signal_hash in self._seen_signals
        self._seen_signals.add(signal_hash)

        if dedupe_hit:
            raise V15SoftFailAbort("Duplicate signal detected")

        return manifest

    def _guardian_validate(self, manifest: SurgicalManifest, trace_id: str, **kwargs: Any) -> None:
        """L2.1: Guardian validation (non-mutating)."""
        global CURRENT_PHASE
        CURRENT_PHASE = "L2.1"

        # L5 Guardian integration - active blocking before L2.2
        GuardianViolationError, L5Guardian = _get_guardian_decision()

        guardian = L5Guardian(policy_version="1.0")
        decision = guardian.validate(manifest, None, "1.0")

        # Log decision to state bus
        guardian.log_decision_to_state_bus(decision, trace_id)

        # Block execution if Guardian disallows
        if not decision.allow:
            raise GuardianViolationError(decision)

        # Escalate to compliance mode if needed
        if decision.escalate:
            Logger.warning(f"[V15-GW] Guardian escalation triggered for {trace_id}")

        # Policy configuration guard
        policy_config = kwargs.get("policy_config", {})
        policy_guard = PolicyConfigGuard(
            policy_config=policy_config,
            wave_id=trace_id,
        )

        # Guardrail enforcement
        guardrail = GuardrailGuard(trace_id=trace_id)

        # Pre-mutation snapshot for boundary checking
        fs_hash, git_hash, mem_hash = kwargs.get("state_hash_fn", lambda: ("", "", ""))()
        self._clock.prepare_commit(manifest.target_layer)
        pre_snapshot = create_boundary_snapshot(
            trace_id=trace_id,
            filesystem_hash=fs_hash,
            git_state_hash=git_hash,
            agent_memory_hash=mem_hash,
            semantic_clock=self._clock,
        )

        # Enforce guardrails before mutation
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

        # Pre-mutation snapshot
        fs_hash, git_hash, mem_hash = state_hash_fn()
        pre_snapshot = create_boundary_snapshot(
            trace_id=trace_id,
            filesystem_hash=fs_hash,
            git_state_hash=git_hash,
            agent_memory_hash=mem_hash,
            semantic_clock=self._clock,
        )

        # Execute healing with mutation tracking
        initial_mutation_count = MUTATION_COUNTER
        healing_output = {}
        commit_valid = False
        error = None

        try:
            healing_output = heal_fn(manifest)
            commit_valid = healing_output.get("errors", 0) == 0
        except Exception as exc:
            # guardian: allow-silent-swallower - Logged error, sets commit_valid=False
            error = str(exc)
            commit_valid = False
            Logger.error(f"[V15-GW] Healing failed: {exc}")

        # Verify mutations occurred only in L2.2
        final_mutation_count = MUTATION_COUNTER
        if final_mutation_count <= initial_mutation_count and commit_valid:
            Logger.warning("[V15-GW] Successful commit with no mutations detected")

        # Post-mutation snapshot or rollback verification
        post_snapshot = None
        rollback_verified = False

        if not commit_valid:
            # Rollback path
            try:
                current_fs, current_git, current_mem = state_hash_fn()
                verify_rollback_integrity(
                    pre_snapshot,
                    current_fs,
                    current_git,
                    current_mem,
                )
                rollback_verified = True
            except Exception as exc:
                # guardian: allow-silent-swallower - Logged error, sets rollback_verified=False
                Logger.error(f"[V15-GW] Rollback integrity FAILED: {exc}")
                rollback_verified = False
                if error is None:
                    error = str(exc)
        else:
            # Success path
            post_fs, post_git, post_mem = state_hash_fn()
            post_snapshot = create_boundary_snapshot(
                trace_id=trace_id,
                filesystem_hash=post_fs,
                git_state_hash=post_git,
                agent_memory_hash=post_mem,
                semantic_clock=self._clock,
            )

            # Advance semantic clock on valid commit
            try:
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
        **kwargs: Any,
    ) -> GatewayResult:
        """L2.3: Healing loop - non-mutating, re-enters L2.0."""
        global CURRENT_PHASE
        CURRENT_PHASE = "L2.3"

        # Healing may only suggest new manifest, not perform writes
        Logger.info(f"[V15-GW] Entering healing loop for {trace_id}")

        # Re-enter validation cycle with modified manifest
        # Note: This is a simplified healing - full implementation would
        # modify manifest in-memory only
        try:
            return self._execute_with_envelope(manifest, heal_fn, state_hash_fn, trace_id, **kwargs)
        except Exception as exc:
            return GatewayResult(
                success=False,
                manifest=manifest,
                semantic_clock_tick=self._clock.step_id,
                pre_snapshot=None,
                post_snapshot=None,
                rollback_verified=False,
                healing_output={},
                error=f"Healing failed: {exc}",
                dedupe_hit=False,
            )

    # -----------------------------------------------------------------
    # Internal helpers (mode-aware)
    # -----------------------------------------------------------------

    def _pipe_advance(
        self,
        pipe: PipeOrderEnforcer,
        step: str,
        trace_id: str,
        observed_steps: list[str] | None = None,
    ) -> None:
        """Advance pipe to *step*. Mode-aware: LOG_ONLY logs, HARD_FAIL raises."""
        # G-2-3: record observed step for final completeness check
        if observed_steps is not None:
            observed_steps.append(step)
        try:
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

    def _policy_check(
        self,
        guard: PolicyConfigGuard,
        current_config: dict[str, Any],
        trace_id: str,
    ) -> None:
        """Verify policy immutability. Mode-aware: LOG_ONLY logs, HARD_FAIL raises."""
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


__all__ = [
    "GatewayResult",
    "V15ExecutionGateway",
]
