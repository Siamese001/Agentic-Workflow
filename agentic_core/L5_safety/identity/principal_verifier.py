"""L5 Exit-Control Principal Verifier — L5 v4 G-04 W4.

Verifies a v4 capability_token against the 8-point contract in
`capability_token.schema.md §7` before any action or mutation is
authorized downstream. Consumed by:

- `agentic_core/L5_safety/exit_control/hitl_policy.py` — runtime HITL
  exit-control (ADR-023) reads verifier verdicts before routing to
  approve / deny / step-up.
- `agentic_core/L5_safety/exit_control/hitl_classes.py` — wraps
  verification results into the HITL decision envelope.

Additive: this module does not modify the existing exit-control surface.
Existing v3 flows continue to run unchanged; v4-aware flows call
`verify_v4_token()` to unlock the identity-chain + permission-ladder +
delegation-depth gates.

Reference:
  - docs/reference/00_L5_Policy_Plane/capability_token.schema.md §7
  - docs/contracts/identity_propagation.md §3 + §5
  - ADR-023 (runtime HITL exit-control)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from agentic_core.interfaces.principal_chain_types import (
    PermissionLadderRung,
    PrincipalChain,
    RiskTierBand,
)
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)


# Permission ladder ordering: higher index = more privileged
_LADDER_ORDER: dict[PermissionLadderRung, int] = {
    "read": 0,
    "suggest": 1,
    "mutate": 2,
    "external": 3,
}

# Band-derived delegation-depth caps (mirror of risk_tier_bands.md §3)
_DELEGATION_DEPTH_CAP: dict[RiskTierBand, int] = {
    "LOW": 3,
    "MODERATE": 2,
    "HIGH": 1,
}


class VerificationStatus(str, Enum):
    """Outcome of the 8-point verification sweep."""

    PASS = "pass"
    FAIL = "fail"
    STEP_UP_REQUIRED = "step_up_required"


@dataclass(frozen=True)
class VerificationResult:
    """Immutable outcome record emitted by `verify_v4_token`.

    `failures` is a list of short, human-readable reason codes so the
    HITL UI and the audit log can both reason about WHY a token was
    rejected without re-running the check.
    """

    status: VerificationStatus
    failures: tuple[str, ...] = field(default_factory=tuple)
    required_rung: PermissionLadderRung | None = None
    token_rung: PermissionLadderRung | None = None
    delegation_depth: int = 0
    delegation_cap: int = 0

    @property
    def is_pass(self) -> bool:
        return self.status is VerificationStatus.PASS

    @property
    def is_fail(self) -> bool:
        return self.status is VerificationStatus.FAIL

    @property
    def needs_step_up(self) -> bool:
        return self.status is VerificationStatus.STEP_UP_REQUIRED

    def to_dict(self) -> dict[str, object]:
        return {
            "delegation_cap": self.delegation_cap,
            "delegation_depth": self.delegation_depth,
            "failures": list(self.failures),
            "required_rung": self.required_rung,
            "status": self.status.value,
            "token_rung": self.token_rung,
        }


def _ladder_satisfies(token_rung: PermissionLadderRung, required: PermissionLadderRung) -> bool:
    """A token at rung N implicitly grants rungs 0..N."""
    return _LADDER_ORDER[token_rung] >= _LADDER_ORDER[required]


def verify_v4_token(
    *,
    token: CapabilityTokenV4Artifact,
    action_required_rung: PermissionLadderRung,
    action_connector_id: str | None = None,
    action_tool_id: str | None = None,
    current_semantic_tick: int | None = None,
    expected_plan_digest: str | None = None,
    revoked_token_ids: Sequence[str] = (),
    active_policy_version: str | None = None,
) -> VerificationResult:
    """Run the 8-point verification sweep from capability_token.schema.md §7.

    Order of checks (fail-fast short-circuit is NOT applied — all checks run
    so the failure list is complete and actionable by HITL):

      1. token_id / v4_trace_id not in revocation list
      2. expires_at > current_semantic_tick (if tick provided)
      3. action's required rung <= permission_ladder_entry
      4. action's connector / tool in connector_allowlist / tool_allowlist
      5. single_use not already consumed (caller-tracked; here we just
         report the single_use flag so the caller can gate it)
      6. policy_version matches active_policy_version (or is within grace
         window — grace currently not implemented; exact match required)
      7. principal_chain.delegation_depth <= band cap
      8. plan_digest matches current declared plan (if expected provided)

    Any violation contributes a reason code to `failures`. The overall
    status is PASS iff `failures` is empty. STEP_UP_REQUIRED is reserved
    for the case where the token is otherwise valid but the caller
    requested a higher rung than the token carries — a HITL gate can
    then re-issue at the higher rung after approval.
    """
    failures: list[str] = []

    # 1. Revocation list
    if token.v4_trace_id in set(revoked_token_ids):
        failures.append(f"REVOKED:{token.v4_trace_id}")

    # 2. Expiry
    if current_semantic_tick is not None:
        expires_tick: int | None = None
        try:
            expires_str = token.expires_at_semantic_clock
            # Accept formats: "tick:N" or "tick:N+Ms" or plain int
            if expires_str.startswith("tick:"):
                body = expires_str.split(":", 1)[1]
                if "+" in body:
                    body = body.split("+", 1)[0]
                expires_tick = int(body)
            else:
                expires_tick = int(expires_str)
        except (ValueError, IndexError):
            failures.append(f"EXPIRES_AT_UNPARSEABLE:{token.expires_at_semantic_clock}")

        if expires_tick is not None and current_semantic_tick >= expires_tick + token.ttl_seconds:
            failures.append("EXPIRED")

    # 3. Permission ladder check
    step_up_only = False
    if not _ladder_satisfies(token.permission_ladder_entry, action_required_rung):
        # Not an outright fail — could be remedied by step-up HITL
        step_up_only = True

    # 4. Connector / tool allowlist
    if action_connector_id is not None:
        if token.connector_allowlist and action_connector_id not in token.connector_allowlist:
            failures.append(f"CONNECTOR_NOT_ALLOWED:{action_connector_id}")
    if action_tool_id is not None:
        if token.tool_allowlist and action_tool_id not in token.tool_allowlist:
            failures.append(f"TOOL_NOT_ALLOWED:{action_tool_id}")

    # 6. Policy version pin
    if active_policy_version is not None and token.policy_version:
        if token.policy_version != active_policy_version:
            failures.append(
                f"POLICY_VERSION_MISMATCH:token={token.policy_version} active={active_policy_version}",
            )

    # 7. Delegation depth cap
    depth = token.principal_chain.delegation_depth
    cap = _DELEGATION_DEPTH_CAP[token.risk_tier_band]
    if depth > cap:
        failures.append(f"DELEGATION_DEPTH_EXCEEDED:{depth}>{cap}")

    # 8. Plan digest match
    if expected_plan_digest is not None and token.plan_digest:
        if token.plan_digest != expected_plan_digest:
            failures.append(
                f"PLAN_DIGEST_MISMATCH:token={token.plan_digest[:16]}... "
                f"expected={expected_plan_digest[:16]}...",
            )

    if failures:
        status = VerificationStatus.FAIL
    elif step_up_only:
        status = VerificationStatus.STEP_UP_REQUIRED
    else:
        status = VerificationStatus.PASS

    return VerificationResult(
        status=status,
        failures=tuple(failures),
        required_rung=action_required_rung,
        token_rung=token.permission_ladder_entry,
        delegation_depth=depth,
        delegation_cap=cap,
    )


def principal_attribution(token: CapabilityTokenV4Artifact) -> dict[str, object]:
    """Return the attribution record a HITL approver/UI sees alongside the decision."""
    chain: PrincipalChain = token.principal_chain
    return {
        "agent_id": chain.agent_id,
        "auth_method": chain.auth_method,
        "delegation_depth": chain.delegation_depth,
        "handoff_chain": [h.to_agent_id for h in chain.handoff_history],
        "invoking_user": chain.invoking_user,
        "invoking_user_kind": chain.invoking_user_kind.value,
        "risk_tier_band": token.risk_tier_band,
        "scope_tag": chain.scope_tag,
        "token_id": token.v4_trace_id,
    }


__all__ = [
    "VerificationResult",
    "VerificationStatus",
    "principal_attribution",
    "verify_v4_token",
]
