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

from agentic_core.L0_maintenance.types.v15_p2_contracts import (
    RollbackHashMismatch,
    create_boundary_snapshot,
    dedupe_sha256,
    validate_execution_input,
    validate_manifest_emission,
    verify_rollback_integrity,
)
from agentic_core.L0_maintenance.types.v15_p2_types import (
    BoundarySnapshotArtifact,
    SemanticClock,
    StateCommitInvalid,
    SurgicalManifest,
)

Logger = logging.getLogger(__name__)


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
        # §1.1/§1.2 — Validate execution input
        manifest = validate_execution_input(execution_input)

        # §2.1 — Validate manifest emission integrity
        validate_manifest_emission(manifest)

        # §5.1 — Dedupe check
        signal_hash = dedupe_sha256(manifest.correlation_id + manifest.node_id)
        dedupe_hit = signal_hash in self._seen_signals
        self._seen_signals.add(signal_hash)

        # §10.2 — Capture pre-mutation boundary snapshot
        fs_hash, git_hash, mem_hash = state_hash_fn()
        self._clock.prepare_commit(manifest.target_layer)
        pre_snapshot = create_boundary_snapshot(
            trace_id=trace_id,
            filesystem_hash=fs_hash,
            git_state_hash=git_hash,
            agent_memory_hash=mem_hash,
            semantic_clock=self._clock,
        )

        # Execute the healing function
        commit_valid = False
        healing_output: dict[str, Any] = {}
        error: str | None = None
        try:
            healing_output = heal_fn(manifest)
            commit_valid = healing_output.get("errors", 0) == 0
        # guardian: allow-silent-swallow
        except Exception as exc:
            error = str(exc)
            commit_valid = False
            Logger.error(f"[V15-GW] Healing failed: {exc}")

        # §13.1/§13.1.1 — Advance semantic clock only on valid commit
        tick = self._clock.step_id
        if commit_valid:
            try:
                tick = self._clock.tick(manifest.target_layer, state_commit_valid=True)
            except StateCommitInvalid as sci:
                error = str(sci)
                commit_valid = False

        # §10.3 — Post-mutation snapshot + rollback verification
        post_snapshot: BoundarySnapshotArtifact | None = None
        rollback_verified = False

        if not commit_valid:
            # Rollback path: verify state matches pre-mutation snapshot
            try:
                current_fs, current_git, current_mem = state_hash_fn()
                verify_rollback_integrity(
                    pre_snapshot,
                    current_fs,
                    current_git,
                    current_mem,
                )
                rollback_verified = True
            except RollbackHashMismatch as rhm:
                Logger.error(f"[V15-GW] Rollback integrity FAILED: {rhm}")
                rollback_verified = False
                if error is None:
                    error = str(rhm)
        else:
            # Success path: capture post-mutation snapshot
            post_fs, post_git, post_mem = state_hash_fn()
            post_snapshot = create_boundary_snapshot(
                trace_id=trace_id,
                filesystem_hash=post_fs,
                git_state_hash=post_git,
                agent_memory_hash=post_mem,
                semantic_clock=self._clock,
            )

        return GatewayResult(
            success=commit_valid,
            manifest=manifest,
            semantic_clock_tick=tick,
            pre_snapshot=pre_snapshot,
            post_snapshot=post_snapshot,
            rollback_verified=rollback_verified,
            healing_output=healing_output,
            error=error,
            dedupe_hit=dedupe_hit,
        )


__all__ = [
    "GatewayResult",
    "V15ExecutionGateway",
]
