"""Runtime Rails Contracts — L5 v4 Wave-B (G-03, G-05, G-15).

Implements three cross-cutting runtime rails that were placeholder fields
in earlier waves:

- **G-03 Risk-tier band selector**: given a `CapabilityTokenV4Artifact`
  (principal + permission_ladder + connector/tool context), compute the
  runtime risk_tier_band that the chokepoint uses to pick depth, HITL
  wiring, and logging verbosity. The band IS the token's declared band
  unless an escalation rule fires.
- **G-05 Handoff Validation (A2A)**: validates that an A2A handoff from
  agent X → agent Y respects (i) target's registry-declared scope
  ceiling, (ii) the principal's `delegation_depth` cap, (iii) cross-agent
  context-bleed rules derived from `scope_tag`.
- **G-15 Hard-Constraint Enforcement**: already enforced at
  `GuardrailOutcome` construction in Wave-A; this module adds a
  policy-side helper to tag policy rules with `hard_constraint=True`
  and validate a rules bundle at load time.

Additive: existing runtime lane keeps running; v4-aware call sites use
these helpers at the relevant chokepoints.

Reference:
  - docs/reference/00_L5_Policy_Plane/risk_tier_bands.md
  - docs/contracts/identity_propagation.md §3.3 (Handoff validation)
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md (G-15)
Parent plan: .windsurf/plans/l5-governance-best-practice-gap-4615ae.md
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


# --- G-03 Risk-tier band selector --------------------------------------


class RiskEscalationReason(str, Enum):
    """Why the runtime band was escalated above the token's declared band."""

    NONE = "none"
    EXTERNAL_RUNG = "external_rung"  # external-side-effect action
    MUTATE_ON_WRITE_SURFACE = "mutate_write"  # mutate + write surface intersect
    DELEGATION_DEPTH_AT_CAP = "depth_at_cap"  # depth equals cap (one more hop → fail)
    UNKNOWN_CONNECTOR = "unknown_connector"  # connector not in registry
    SHADOW_OPERATOR = "shadow_operator"  # invoking_user == unknown_local_operator


@dataclass(frozen=True)
class RiskTierDecision:
    """Immutable runtime risk-tier decision.

    Drives chokepoint depth, HITL wiring, and log verbosity. The decision
    is always `max(token_declared_band, escalated_band)` — runtime can
    escalate up but NEVER down.
    """

    token_band: RiskTierBand
    runtime_band: RiskTierBand
    escalation_reason: RiskEscalationReason
    requires_hitl: bool
    log_verbosity: int  # 0=minimal, 1=standard, 2=verbose, 3=forensic

    def __post_init__(self) -> None:
        order = {"LOW": 0, "MODERATE": 1, "HIGH": 2}
        if order[self.runtime_band] < order[self.token_band]:
            raise ValueError(
                "RiskTierDecision: runtime_band must be >= token_band. "
                "Escalation is monotonic; de-escalation is forbidden.",
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "escalation_reason": self.escalation_reason.value,
            "log_verbosity": self.log_verbosity,
            "requires_hitl": self.requires_hitl,
            "runtime_band": self.runtime_band,
            "token_band": self.token_band,
        }


_BAND_ORDER: dict[RiskTierBand, int] = {"LOW": 0, "MODERATE": 1, "HIGH": 2}
_BAND_FROM_ORDER: dict[int, RiskTierBand] = {0: "LOW", 1: "MODERATE", 2: "HIGH"}


def _escalate(a: RiskTierBand, b: RiskTierBand) -> RiskTierBand:
    return _BAND_FROM_ORDER[max(_BAND_ORDER[a], _BAND_ORDER[b])]


def select_runtime_band(
    *,
    token: CapabilityTokenV4Artifact,
    action_required_rung: PermissionLadderRung,
    action_connector_id: str | None = None,
    connector_is_registered: bool = True,
    touches_write_surface: bool = False,
) -> RiskTierDecision:
    """Select the runtime band, accounting for escalation triggers.

    Deterministic. Never calls into I/O. Call this once at the runtime-lane
    entry (chokepoint) to pick the depth of subsequent checks.
    """
    runtime = token.risk_tier_band
    reason = RiskEscalationReason.NONE

    # Rule 1: external rung always HIGH
    if action_required_rung == "external":
        runtime = _escalate(runtime, "HIGH")
        reason = RiskEscalationReason.EXTERNAL_RUNG

    # Rule 2: mutate + write surface intersect → at least MODERATE
    if action_required_rung == "mutate" and touches_write_surface:
        runtime = _escalate(runtime, "MODERATE")
        if reason == RiskEscalationReason.NONE:
            reason = RiskEscalationReason.MUTATE_ON_WRITE_SURFACE

    # Rule 3: delegation depth at cap → escalate one band
    cap = {"LOW": 3, "MODERATE": 2, "HIGH": 1}[token.risk_tier_band]
    if token.principal_chain.delegation_depth >= cap:
        runtime = _escalate(runtime, "HIGH")
        if reason == RiskEscalationReason.NONE:
            reason = RiskEscalationReason.DELEGATION_DEPTH_AT_CAP

    # Rule 4: unknown connector → MODERATE minimum
    if action_connector_id is not None and not connector_is_registered:
        runtime = _escalate(runtime, "MODERATE")
        if reason == RiskEscalationReason.NONE:
            reason = RiskEscalationReason.UNKNOWN_CONNECTOR

    # Rule 5: shadow operator (front-door sentinel) → MODERATE minimum
    if token.principal_chain.invoking_user == "unknown_local_operator":
        runtime = _escalate(runtime, "MODERATE")
        if reason == RiskEscalationReason.NONE:
            reason = RiskEscalationReason.SHADOW_OPERATOR

    # HITL wiring + log verbosity per band
    requires_hitl = runtime == "HIGH"
    log_verbosity = {"LOW": 1, "MODERATE": 2, "HIGH": 3}[runtime]

    return RiskTierDecision(
        token_band=token.risk_tier_band,
        runtime_band=runtime,
        escalation_reason=reason,
        requires_hitl=requires_hitl,
        log_verbosity=log_verbosity,
    )


# --- G-05 Handoff Validation (A2A) ------------------------------------


@dataclass(frozen=True)
class AgentRegistryRecord:
    """Minimum-viable registry record for handoff validation.

    Full Agent Registry lives in `agentic_core/L5_safety/config/` and has
    richer fields; this record carries only what handoff validation needs.
    """

    agent_id: str
    allowed_scope_ceiling: tuple[str, ...]
    # Scopes this agent may receive from any upstream handoff
    allowed_inbound_handoff_scopes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.agent_id:
            raise ValueError("AgentRegistryRecord: agent_id required")


@dataclass(frozen=True)
class HandoffValidationResult:
    """Outcome of a G-05 A2A handoff validation."""

    allow: bool
    failures: tuple[str, ...]
    target_agent_id: str
    effective_scopes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "allow": self.allow,
            "effective_scopes": list(self.effective_scopes),
            "failures": list(self.failures),
            "target_agent_id": self.target_agent_id,
        }


def validate_handoff(
    *,
    source_chain: PrincipalChain,
    target_agent: AgentRegistryRecord,
    requested_scope_added: Sequence[str] = (),
    requested_scope_removed: Sequence[str] = (),
    risk_tier_band: RiskTierBand = "LOW",
) -> HandoffValidationResult:
    """Validate an A2A handoff BEFORE building the new PrincipalChain.

    Checks (order preserves failure-list legibility):

      1. Delegation-depth cap for the current band (LOW=3, MODERATE=2, HIGH=1).
      2. Requested scope_added is a subset of the target's
         `allowed_inbound_handoff_scopes` (if that allowlist is non-empty)
         AND within the target's `allowed_scope_ceiling`.
      3. Effective scopes after add/remove MUST be within the target's ceiling.
      4. scope_tag bleed: the effective scopes MUST NOT widen the privacy
         compartment (G-09) — that is, no scope may contain "*" unless the
         source already had it.

    Returns a HandoffValidationResult. The caller (runtime lane) uses the
    result to either call `source_chain.with_handoff(...)` or short-circuit
    with a REJECT.
    """
    failures: list[str] = []

    # 1. Depth cap
    cap = {"LOW": 3, "MODERATE": 2, "HIGH": 1}[risk_tier_band]
    if source_chain.delegation_depth + 1 > cap:
        failures.append(
            f"DEPTH_CAP_EXCEEDED:{source_chain.delegation_depth + 1}>{cap}(band={risk_tier_band})",
        )

    # 2. Inbound scope whitelist + 3. ceiling
    ceiling = set(target_agent.allowed_scope_ceiling)
    inbound_whitelist = set(target_agent.allowed_inbound_handoff_scopes)

    for scope in requested_scope_added:
        if inbound_whitelist and scope not in inbound_whitelist:
            failures.append(f"SCOPE_NOT_IN_INBOUND_WHITELIST:{scope}")
        if ceiling and scope not in ceiling:
            failures.append(f"SCOPE_ABOVE_CEILING:{scope}")

    # Compute effective scopes
    effective = (set(source_chain.scopes) | set(requested_scope_added)) - set(requested_scope_removed)

    for scope in effective:
        if ceiling and scope not in ceiling:
            failures.append(f"EFFECTIVE_SCOPE_ABOVE_CEILING:{scope}")

    # 4. Wildcard bleed check
    if "*" in effective and "*" not in set(source_chain.scopes):
        failures.append("WILDCARD_SCOPE_BLEED_FORBIDDEN")

    return HandoffValidationResult(
        allow=not failures,
        failures=tuple(failures),
        target_agent_id=target_agent.agent_id,
        effective_scopes=tuple(sorted(effective)),
    )


# --- G-15 Hard-Constraint policy-rule validation ----------------------


@dataclass(frozen=True)
class PolicyRule:
    """Minimum-viable policy-rule shape with hard_constraint tag.

    Full policy-set schema lives elsewhere; this shape carries the fields
    Wave-A / Wave-B need. A `hard_constraint=True` rule MUST never be
    remediate-able — the bank enforces this at outcome construction.
    """

    rule_id: str
    family: str  # matches GuardrailFamily.value
    policy_version: str
    hard_constraint: bool
    description: str = ""

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("PolicyRule: rule_id required")
        if not self.policy_version:
            raise ValueError("PolicyRule: policy_version required")


def validate_policy_bundle(rules: Sequence[PolicyRule]) -> tuple[str, ...]:
    """Return a tuple of validation failures for a policy bundle.

    Empty tuple ⇒ bundle is internally consistent.

    Currently enforces:
      - Unique rule_id within a bundle
      - Every rule has a non-empty policy_version
      - Same-family rules share the same policy_version (cross-rule consistency)
    """
    failures: list[str] = []

    # Unique rule_id
    ids: dict[str, int] = {}
    for r in rules:
        ids[r.rule_id] = ids.get(r.rule_id, 0) + 1
    for rule_id, count in ids.items():
        if count > 1:
            failures.append(f"DUPLICATE_RULE_ID:{rule_id}(x{count})")

    # Cross-rule policy_version consistency by family
    family_versions: dict[str, set[str]] = {}
    for r in rules:
        family_versions.setdefault(r.family, set()).add(r.policy_version)
    for family, versions in family_versions.items():
        if len(versions) > 1:
            failures.append(
                f"INCONSISTENT_FAMILY_VERSION:{family}:{sorted(versions)}",
            )

    return tuple(failures)


__all__ = [
    "AgentRegistryRecord",
    "HandoffValidationResult",
    "PolicyRule",
    "RiskEscalationReason",
    "RiskTierDecision",
    "select_runtime_band",
    "validate_handoff",
    "validate_policy_bundle",
]
