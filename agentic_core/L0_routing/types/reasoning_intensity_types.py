"""
Reasoning Intensity Contracts — L0 Authority Surface.

Defines the sealed, versioned, cryptographically-bound contracts for
reasoning intensity governance. L0 computes and stamps these; L3 enforces;
apps_* consume read-only.

Design invariants:
  - All types are immutable (frozen dataclasses).
  - profile_hash = SHA256(deterministic_serialization(profile)).
  - Complexity scoring is a pure function of structural inputs only.
  - No C0 embedding outputs may appear as policy signals.
  - Tier mapping is discrete: LOW / MEDIUM / HIGH / CRITICAL.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import RouteDecisionArtifact

# =============================================================================
# Coarse-grained tier enumeration (discrete — no micro-adjustments)
# =============================================================================


class ReasoningTier(str, Enum):
    """Discrete reasoning intensity tiers. No fractional values allowed."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# Immutable per-stage token budget
# =============================================================================


@dataclass(frozen=True)
class StageTokenBudget:
    """Per-HOP-stage token budget constraint stamped by L0."""

    stage_id: int
    max_tokens: int

    def __post_init__(self) -> None:
        if self.stage_id < 1:
            raise ValueError(f"StageTokenBudget: stage_id must be >= 1, got {self.stage_id}")
        if self.max_tokens < 1:
            raise ValueError(f"StageTokenBudget: max_tokens must be >= 1, got {self.max_tokens}")


# =============================================================================
# Core profile — sealed by L0, consumed read-only by L3 and apps_*
# =============================================================================


@dataclass(frozen=True)
class ReasoningIntensityProfile:
    """Sealed reasoning intensity profile stamped by L0 ReasoningPolicyEngine.

    All fields are required. profile_hash is computed over the canonical
    serialization of all policy parameters and must be included in:
      - execution trace
      - replay key
      - L3 enforcement log

    L3 may only REDUCE (enforce ceilings). No upward mutation is permitted.
    """

    reasoning_profile_version: str
    reasoning_policy_hash: str
    tier: ReasoningTier
    max_branches: int
    max_depth: int
    enable_reflection: bool
    token_budget_per_stage: tuple[StageTokenBudget, ...]
    allowed_modes: tuple[str, ...]
    profile_hash: str

    def __post_init__(self) -> None:
        if not self.reasoning_profile_version:
            raise ValueError("ReasoningIntensityProfile: reasoning_profile_version must be non-empty")
        if not self.reasoning_policy_hash:
            raise ValueError("ReasoningIntensityProfile: reasoning_policy_hash must be non-empty")
        if self.max_branches < 1:
            raise ValueError(f"ReasoningIntensityProfile: max_branches must be >= 1, got {self.max_branches}")
        if self.max_depth < 1:
            raise ValueError(f"ReasoningIntensityProfile: max_depth must be >= 1, got {self.max_depth}")
        if not self.profile_hash:
            raise ValueError("ReasoningIntensityProfile: profile_hash must be non-empty")
        expected = _compute_profile_hash(
            version=self.reasoning_profile_version,
            policy_hash=self.reasoning_policy_hash,
            tier=self.tier.value,
            max_branches=self.max_branches,
            max_depth=self.max_depth,
            enable_reflection=self.enable_reflection,
            token_budget_per_stage=[
                {"stage_id": b.stage_id, "max_tokens": b.max_tokens} for b in self.token_budget_per_stage
            ],
            allowed_modes=sorted(self.allowed_modes),
        )
        if self.profile_hash != expected:
            raise ValueError(
                f"ReasoningIntensityProfile: profile_hash mismatch. "
                f"Expected {expected[:16]}..., got {self.profile_hash[:16]}..."
            )


# =============================================================================
# SignedExecutionEnvelope — first-class sealed contract
# =============================================================================


@dataclass(frozen=True)
class SignedExecutionEnvelope:
    """First-class sealed execution contract combining route decision and reasoning profile.

    L0 stamps this; L3 reads it; apps_* receive it as read-only constraints.
    The envelope_hash covers both route_decision and reasoning_profile to
    prevent partial substitution attacks.
    """

    route_decision: RouteDecisionArtifact
    reasoning_profile: ReasoningIntensityProfile
    enforcement_constraints: dict[str, Any]
    policy_hash: str
    envelope_hash: str

    def __post_init__(self) -> None:
        if not self.policy_hash:
            raise ValueError("SignedExecutionEnvelope: policy_hash must be non-empty")
        if not self.envelope_hash:
            raise ValueError("SignedExecutionEnvelope: envelope_hash must be non-empty")
        expected = _compute_envelope_hash(
            route_decision_trace_id=self.route_decision.trace_id,
            profile_hash=self.reasoning_profile.profile_hash,
            policy_hash=self.policy_hash,
        )
        if self.envelope_hash != expected:
            raise ValueError(
                f"SignedExecutionEnvelope: envelope_hash mismatch. "
                f"Expected {expected[:16]}..., got {self.envelope_hash[:16]}..."
            )


# =============================================================================
# ReasoningConstraintViolation — emitted by L3 on fail-closed enforcement
# =============================================================================


@dataclass(frozen=True)
class ReasoningConstraintViolation:
    """Emitted by L3 ReasoningIntensityEnforcer on policy ceiling breach.

    This is a deterministic failure artifact — not a soft warning.
    The violating stage MUST be halted immediately.
    """

    trace_id: str
    profile_hash: str
    stage_id: int
    violation_kind: str
    limit_value: int | float
    observed_value: int | float

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("ReasoningConstraintViolation: trace_id must be non-empty")
        if not self.profile_hash:
            raise ValueError("ReasoningConstraintViolation: profile_hash must be non-empty")
        if not self.violation_kind:
            raise ValueError("ReasoningConstraintViolation: violation_kind must be non-empty")


# =============================================================================
# L3 enforcement telemetry (non-authoritative — future calibration only)
# =============================================================================


@dataclass(frozen=True)
class ReasoningEnforcementTelemetry:
    """Non-authoritative telemetry emitted by L3 after stage execution.

    CRITICAL: This data MUST NOT influence the current run.
    It may only be used by L0 for FUTURE calibration, and only after
    windowed aggregation and versioning (no direct feedback loops).
    """

    trace_id: str
    profile_hash: str
    stage_id: int
    branches_used: int
    depth_reached: int
    tokens_used: int
    reflection_triggered: bool
    early_stop_triggered: bool
    compliant: bool


# =============================================================================
# Pure-function hash helpers (deterministic, no side effects)
# =============================================================================


def _compute_profile_hash(
    version: str,
    policy_hash: str,
    tier: str,
    max_branches: int,
    max_depth: int,
    enable_reflection: bool,
    token_budget_per_stage: list[dict[str, int]],
    allowed_modes: list[str],
) -> str:
    """Compute SHA256 over deterministic canonical serialization of profile parameters."""
    canonical = json.dumps(
        {
            "version": version,
            "policy_hash": policy_hash,
            "tier": tier,
            "max_branches": max_branches,
            "max_depth": max_depth,
            "enable_reflection": enable_reflection,
            "token_budget_per_stage": sorted(token_budget_per_stage, key=lambda x: x["stage_id"]),
            "allowed_modes": sorted(allowed_modes),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _compute_envelope_hash(
    route_decision_trace_id: str,
    profile_hash: str,
    policy_hash: str,
) -> str:
    """Compute SHA256 over envelope binding fields."""
    canonical = json.dumps(
        {
            "route_decision_trace_id": route_decision_trace_id,
            "profile_hash": profile_hash,
            "policy_hash": policy_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# =============================================================================
# Public builder helpers
# =============================================================================


def build_profile_hash(
    version: str,
    policy_hash: str,
    tier: ReasoningTier,
    max_branches: int,
    max_depth: int,
    enable_reflection: bool,
    token_budget_per_stage: list[StageTokenBudget],
    allowed_modes: list[str],
) -> str:
    """Compute the profile_hash for use before constructing ReasoningIntensityProfile."""
    return _compute_profile_hash(
        version=version,
        policy_hash=policy_hash,
        tier=tier.value,
        max_branches=max_branches,
        max_depth=max_depth,
        enable_reflection=enable_reflection,
        token_budget_per_stage=[
            {"stage_id": b.stage_id, "max_tokens": b.max_tokens} for b in token_budget_per_stage
        ],
        allowed_modes=sorted(allowed_modes),
    )


def build_envelope_hash(
    route_decision_trace_id: str,
    profile_hash: str,
    policy_hash: str,
) -> str:
    """Compute the envelope_hash for use before constructing SignedExecutionEnvelope."""
    return _compute_envelope_hash(
        route_decision_trace_id=route_decision_trace_id,
        profile_hash=profile_hash,
        policy_hash=policy_hash,
    )


# =============================================================================
# Tier → profile parameter table (discrete, no heuristics)
# =============================================================================

TIER_PARAMETER_TABLE: dict[ReasoningTier, dict[str, Any]] = {
    ReasoningTier.LOW: {
        "max_branches": 1,
        "max_depth": 1,
        "enable_reflection": False,
        "allowed_modes": ["cot"],
        "token_budget_multiplier": 0.5,
    },
    ReasoningTier.MEDIUM: {
        "max_branches": 2,
        "max_depth": 2,
        "enable_reflection": False,
        "allowed_modes": ["cot", "hybrid_cot_tot"],
        "token_budget_multiplier": 1.0,
    },
    ReasoningTier.HIGH: {
        "max_branches": 3,
        "max_depth": 3,
        "enable_reflection": True,
        "allowed_modes": ["cot", "hybrid_cot_tot", "tot"],
        "token_budget_multiplier": 1.5,
    },
    ReasoningTier.CRITICAL: {
        "max_branches": 5,
        "max_depth": 5,
        "enable_reflection": True,
        "allowed_modes": ["cot", "hybrid_cot_tot", "tot", "reflexion"],
        "token_budget_multiplier": 2.0,
    },
}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TIER_PARAMETER_TABLE",
    "ReasoningConstraintViolation",
    "ReasoningEnforcementTelemetry",
    "ReasoningIntensityProfile",
    "ReasoningTier",
    "SignedExecutionEnvelope",
    "StageTokenBudget",
    "build_envelope_hash",
    "build_profile_hash",
]
