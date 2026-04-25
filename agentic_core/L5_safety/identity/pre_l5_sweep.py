"""Pre-L5 Unified Sweep Adapter — L5 v4 Wave-K wire-in.

Composes three previously-independent loaders/verifiers into a single
pre-runtime sweep that runtime_entry.py can invoke as one call:

- `registry_loader`   (Wave-I) — verify the v4 token's pinned registry_digest
                                  still matches the currently-active snapshot
- `data_authority_loader` (Wave-J) — verify no data-authority drift before
                                     any read/write sourced from RAG/KB/training
- `principal_verifier` (Wave W4) — the 8-point identity-chain verification

The sweep returns one immutable `PreL5SweepResult` capturing every signal.
`all_pass` lets runtime_entry short-circuit with a single bool; the
per-component fields let audit_binding record each failure reason
independently so forensic replay can attribute any denial precisely.

Adoption path:

    from agentic_core.L5_safety.identity.pre_l5_sweep import run_pre_l5_sweep

    result = run_pre_l5_sweep(
        token=v4_token,
        action_required_rung="mutate",
        action_connector_id="claude_mcp",
    )
    if not result.all_pass:
        # audit + refuse / step-up
        emit_audit(result.to_dict())
        return deny(result.combined_failures)

Design invariants:

- All three checks always run (no fail-fast); consumers need every reason
  code for complete audit records.
- The sweep NEVER raises on a verification failure — failures are surfaced
  in the result object. Only programming errors (wrong types) raise.
- Bound against process-local singletons from Wave-I and Wave-J so the
  digest-stability contract holds for the whole runtime entry call.

Reference:
  - registry_loader.py (Wave-I)
  - data_authority_loader.py (Wave-J)
  - principal_verifier.py (Wave W4)
  - runtime_entry.py (Wave G+H — next consumer)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
Ref: ADR-049, G-04 (identity propagation), G-13 (data authority)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from agentic_core.interfaces.principal_chain_types import PermissionLadderRung
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.data_authority_loader import (
    get_active_data_authority_resolution,
)
from agentic_core.L5_safety.identity.principal_verifier import (
    VerificationResult,
    VerificationStatus,
    verify_v4_token,
)
from agentic_core.L5_safety.identity.registries import verify_token_against_registry
from agentic_core.L5_safety.identity.registry_loader import (
    get_active_registry_snapshot,
)


@dataclass(frozen=True)
class PreL5SweepResult:
    """Immutable outcome of the unified pre-L5 sweep.

    `all_pass` = identity verification is PASS AND registry digest matches
    AND data-authority ledger reports no drift.

    `needs_step_up` short-circuits to the HITL step-up path even if identity
    alone is PASS (e.g. drift detected).
    """

    verification: VerificationResult
    registry_match: bool
    registry_reason: str
    data_authority_all_match: bool
    data_authority_drifts: tuple[str, ...] = field(default_factory=tuple)

    @property
    def all_pass(self) -> bool:
        return self.verification.is_pass and self.registry_match and self.data_authority_all_match

    @property
    def needs_step_up(self) -> bool:
        # Identity verifier explicitly flagged step-up OR any non-identity
        # gate failed (registry drift / data-authority drift) — both are
        # remediable by a policy-bump + re-issue rather than a hard deny.
        if self.verification.needs_step_up:
            return True
        if self.verification.is_pass and not (self.registry_match and self.data_authority_all_match):
            return True
        return False

    @property
    def combined_failures(self) -> tuple[str, ...]:
        """All reason codes across the three gates, in a stable order."""
        parts: list[str] = list(self.verification.failures)
        if not self.registry_match:
            parts.append(f"REGISTRY:{self.registry_reason}")
        for src in self.data_authority_drifts:
            parts.append(f"DATA_AUTHORITY_DRIFT:{src}")
        return tuple(parts)

    def to_dict(self) -> dict[str, object]:
        return {
            "all_pass": self.all_pass,
            "combined_failures": list(self.combined_failures),
            "data_authority_all_match": self.data_authority_all_match,
            "data_authority_drifts": list(self.data_authority_drifts),
            "needs_step_up": self.needs_step_up,
            "registry_match": self.registry_match,
            "registry_reason": self.registry_reason,
            "verification": self.verification.to_dict(),
        }


def run_pre_l5_sweep(
    *,
    token: CapabilityTokenV4Artifact,
    action_required_rung: PermissionLadderRung,
    action_connector_id: str | None = None,
    action_tool_id: str | None = None,
    current_semantic_tick: int | None = None,
    expected_plan_digest: str | None = None,
    revoked_token_ids: Sequence[str] = (),
    active_policy_version: str | None = None,
) -> PreL5SweepResult:
    """Compose identity + registry + data-authority checks into one sweep.

    All three gates always run. No fail-fast — complete reason codes are
    required for audit attribution.
    """
    # Gate 1: identity / 8-point verification
    verification = verify_v4_token(
        token=token,
        action_required_rung=action_required_rung,
        action_connector_id=action_connector_id,
        action_tool_id=action_tool_id,
        current_semantic_tick=current_semantic_tick,
        expected_plan_digest=expected_plan_digest,
        revoked_token_ids=revoked_token_ids,
        active_policy_version=active_policy_version,
    )

    # Gate 2: registry digest drift
    snapshot = get_active_registry_snapshot()
    registry_match, registry_reason = verify_token_against_registry(
        token_registry_digest=token.registry_digest,
        current_snapshot=snapshot,
    )

    # Gate 3: data-authority resolution (pinned digests match live content)
    resolution = get_active_data_authority_resolution()

    return PreL5SweepResult(
        verification=verification,
        registry_match=registry_match,
        registry_reason=registry_reason,
        data_authority_all_match=resolution.all_match,
        data_authority_drifts=resolution.drifts,
    )


__all__ = [
    "PreL5SweepResult",
    "VerificationStatus",
    "run_pre_l5_sweep",
]
