"""Capability Token V4 Types — L5 v4 Governance Plane (G-04 W1 P1.3).

Sibling of `capability_token_types.CapabilityTokenArtifact` (v3). Composes
the v3 artifact and adds the v4 fields mandated by ADR-049:

  - principal_chain        (SAIF Principle 3 — identity propagation)
  - risk_tier_band         (LOW | MODERATE | HIGH)
  - permission_ladder_entry (read | suggest | mutate | external)
  - ttl_seconds + single_use + expires_at_semantic_clock (capability TTL)
  - connector_allowlist    (MCP connector scoping)
  - tool_allowlist         (Tool registry scoping)
  - plan_digest            (transparency into the agent's declared plan)
  - standards_fingerprint  (NIST AI RMF / ISO 42001 / CoSAI alignment)
  - grant_mode             (one_time | permanent | sessioned)

**Why a sibling, not an extension**: v3 `CapabilityTokenArtifact` computes a
deterministic `trace_id = SHA-256(canonical payload)`. Mutating the payload
shape — even with Optional-None defaults — changes every historical
trace_id. The sibling pattern preserves v3 byte-identical and lets v4
callers opt in explicitly via `issue_capability_token_v4(...)`.

**Back-compat guarantee**: any code currently importing from
`capability_token_types` continues to work unchanged. No existing call site
is touched by this module's introduction.

Reference:
  - docs/reference/00_L5_Policy_Plane/capability_token.schema.md
  - docs/reference/00_L5_Policy_Plane/risk_tier_bands.md
  - docs/contracts/identity_propagation.md
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
ADR: ADR-049 §7 (§7.3 ratified: full principal_chain from day one)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal

from agentic_core.interfaces.principal_chain_types import (
    GrantMode,
    PermissionLadderRung,
    PrincipalChain,
    RiskTierBand,
)
from agentic_core.L0_routing.types.determinism_types import (  # guardian: allow-layer-violation -- mirror of v3 capability_token_types L2→L0 downward enforcement dependency; same contract, same exemption rationale
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityConstraints,
    CapabilityTokenArtifact,
    CapabilityTokenSubject,
    build_capability_token,
)

# Band-derived TTL caps (see risk_tier_bands.md §5)
_TTL_CAP_SECONDS: dict[RiskTierBand, int] = {
    "LOW": 3600,
    "MODERATE": 900,
    "HIGH": 300,
}

# Band delegation-depth caps (see risk_tier_bands.md §3)
_DELEGATION_DEPTH_CAP: dict[RiskTierBand, int] = {
    "LOW": 3,
    "MODERATE": 2,
    "HIGH": 1,
}


def _canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no extra whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _compute_v4_trace_id(payload: dict[str, Any]) -> str:
    """Deterministic v4 trace_id = SHA-256(canonical payload excluding trace_id)."""
    canonical = _canonical_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class StandardsFingerprint:
    """Compliance attestation fingerprint carried on every v4 token.

    Empty strings indicate a dimension is not asserted for this token.
    """

    nist_ai_rmf: str = ""
    iso_42001: str = ""
    cosai_baseline: str = ""
    sector_overlays: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # Enforce sorted sector overlays (deterministic serialization)
        if list(self.sector_overlays) != sorted(self.sector_overlays):
            object.__setattr__(
                self,
                "sector_overlays",
                tuple(sorted(self.sector_overlays)),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cosai_baseline": self.cosai_baseline,
            "iso_42001": self.iso_42001,
            "nist_ai_rmf": self.nist_ai_rmf,
            "sector_overlays": list(self.sector_overlays),
        }


@dataclass(frozen=True)
class CapabilityTokenV4Artifact:
    """§L5-v4 — Capability token with identity chain, risk band, and TTL.

    All fields are immutable. v4 trace_id is SEPARATE from the wrapped v3
    artifact's trace_id and does not affect v3 determinism. The v3
    artifact is carried verbatim as `v3_artifact` for downstream code that
    only knows v3.

    Verification contract (capability_token.schema.md §7) is enforced by
    L5 exit-control (W4), not here. This dataclass only enforces structural
    invariants at construction time.
    """

    artifact_type: Literal["CAPABILITY_TOKEN_V4"]
    semantic_clock: SemanticClockSnapshot
    v4_trace_id: str
    v3_artifact: CapabilityTokenArtifact

    # --- v4 additions -------------------------------------------------
    principal_chain: PrincipalChain
    risk_tier_band: RiskTierBand
    permission_ladder_entry: PermissionLadderRung
    ttl_seconds: int
    single_use: bool
    expires_at_semantic_clock: str
    connector_allowlist: tuple[str, ...]
    tool_allowlist: tuple[str, ...]
    plan_digest: str
    grant_mode: GrantMode
    standards_fingerprint: StandardsFingerprint

    # Policy-set pinning (same role as v3 policy_config_hash but explicit)
    policy_version: str = ""
    registry_digest: str = ""

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "CapabilityTokenV4Artifact")
        if self.artifact_type != "CAPABILITY_TOKEN_V4":
            raise ValueError(
                "CapabilityTokenV4Artifact: artifact_type must be "
                f"'CAPABILITY_TOKEN_V4', got '{self.artifact_type}'",
            )
        if not self.v4_trace_id:
            raise ValueError("CapabilityTokenV4Artifact: v4_trace_id required")
        if self.risk_tier_band not in ("LOW", "MODERATE", "HIGH"):
            raise ValueError(
                f"CapabilityTokenV4Artifact: risk_tier_band must be "
                f"LOW|MODERATE|HIGH, got '{self.risk_tier_band}'",
            )
        if self.permission_ladder_entry not in (
            "read",
            "suggest",
            "mutate",
            "external",
        ):
            raise ValueError(
                f"CapabilityTokenV4Artifact: permission_ladder_entry must be "
                f"read|suggest|mutate|external, got '{self.permission_ladder_entry}'",
            )
        if self.grant_mode not in ("one_time", "permanent", "sessioned"):
            raise ValueError(
                f"CapabilityTokenV4Artifact: grant_mode must be "
                f"one_time|permanent|sessioned, got '{self.grant_mode}'",
            )
        if self.ttl_seconds <= 0:
            raise ValueError(
                f"CapabilityTokenV4Artifact: ttl_seconds must be > 0, "
                f"got {self.ttl_seconds}",
            )

        # Band-derived TTL cap enforcement
        cap = _TTL_CAP_SECONDS[self.risk_tier_band]
        if self.ttl_seconds > cap:
            raise ValueError(
                f"CapabilityTokenV4Artifact: ttl_seconds {self.ttl_seconds} "
                f"exceeds {self.risk_tier_band} cap ({cap}s)",
            )

        # HIGH band requires single_use unless an explicit persistent grant
        if (
            self.risk_tier_band == "HIGH"
            and not self.single_use
            and self.grant_mode != "permanent"
        ):
            raise ValueError(
                "CapabilityTokenV4Artifact: HIGH band requires single_use=True "
                "unless grant_mode='permanent'",
            )

        # external rung requires single_use OR permanent grant
        if (
            self.permission_ladder_entry == "external"
            and not self.single_use
            and self.grant_mode != "permanent"
        ):
            raise ValueError(
                "CapabilityTokenV4Artifact: permission_ladder_entry='external' "
                "requires single_use=True unless grant_mode='permanent'",
            )

        # Delegation-depth cap enforcement
        depth_cap = _DELEGATION_DEPTH_CAP[self.risk_tier_band]
        if self.principal_chain.delegation_depth > depth_cap:
            raise ValueError(
                f"CapabilityTokenV4Artifact: delegation_depth "
                f"{self.principal_chain.delegation_depth} exceeds "
                f"{self.risk_tier_band} cap ({depth_cap})",
            )

        # Sorted invariants (deterministic serialization)
        if list(self.connector_allowlist) != sorted(self.connector_allowlist):
            object.__setattr__(
                self,
                "connector_allowlist",
                tuple(sorted(self.connector_allowlist)),
            )
        if list(self.tool_allowlist) != sorted(self.tool_allowlist):
            object.__setattr__(
                self,
                "tool_allowlist",
                tuple(sorted(self.tool_allowlist)),
            )

    def _payload_dict(self) -> dict[str, Any]:
        """Canonical payload for v4 serialization (includes v4_trace_id)."""
        return {
            "artifact_type": self.artifact_type,
            "connector_allowlist": list(self.connector_allowlist),
            "expires_at_semantic_clock": self.expires_at_semantic_clock,
            "grant_mode": self.grant_mode,
            "permission_ladder_entry": self.permission_ladder_entry,
            "plan_digest": self.plan_digest,
            "policy_version": self.policy_version,
            "principal_chain": self.principal_chain.to_dict(),
            "registry_digest": self.registry_digest,
            "risk_tier_band": self.risk_tier_band,
            "semantic_clock": self.semantic_clock.to_dict(),
            "single_use": self.single_use,
            "standards_fingerprint": self.standards_fingerprint.to_dict(),
            "tool_allowlist": list(self.tool_allowlist),
            "ttl_seconds": self.ttl_seconds,
            "v3_trace_id": self.v3_artifact.trace_id,
            "v4_trace_id": self.v4_trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON serialization of the v4 payload."""
        return _canonical_json(self._payload_dict())


def issue_capability_token_v4(
    *,
    semantic_clock: SemanticClockSnapshot,
    principal_chain: PrincipalChain,
    risk_tier_band: RiskTierBand,
    permission_ladder_entry: PermissionLadderRung,
    subject_kind: str,
    subject_id: str,
    issued_by: str,
    permissions: list[str] | tuple[str, ...],
    allowed_paths: list[str] | tuple[str, ...],
    max_tool_calls: int,
    ttl_seconds: int,
    single_use: bool,
    expires_at_semantic_clock: str,
    connector_allowlist: list[str] | tuple[str, ...] = (),
    tool_allowlist: list[str] | tuple[str, ...] = (),
    plan_digest: str = "",
    grant_mode: GrantMode = "one_time",
    standards_fingerprint: StandardsFingerprint | None = None,
    policy_config_hash: str | None = None,
    policy_version: str = "",
    registry_digest: str = "",
) -> CapabilityTokenV4Artifact:
    """Mint a v4 capability token, wrapping a deterministic v3 artifact.

    The v3 artifact is built via the existing `build_capability_token`
    helper so its trace_id remains byte-identical to tokens that would
    have been issued by v3 callers for the same inputs. The v4 trace_id
    is computed over a canonical v4 payload that includes the v4 fields.
    """
    validate_semantic_clock(semantic_clock, "issue_capability_token_v4")

    if standards_fingerprint is None:
        standards_fingerprint = StandardsFingerprint()

    subject = CapabilityTokenSubject(kind=subject_kind, id=subject_id)
    constraints = CapabilityConstraints(
        allowed_paths=tuple(sorted(allowed_paths)),
        max_tool_calls=max_tool_calls,
    )

    v3_artifact = build_capability_token(
        semantic_clock=semantic_clock,
        subject=subject,
        issued_by=issued_by,
        permissions=tuple(sorted(permissions)),
        constraints=constraints,
        policy_config_hash=policy_config_hash,
    )

    sorted_connectors = tuple(sorted(connector_allowlist))
    sorted_tools = tuple(sorted(tool_allowlist))

    # Pre-compute v4 trace_id
    pre_payload = {
        "artifact_type": "CAPABILITY_TOKEN_V4",
        "connector_allowlist": list(sorted_connectors),
        "expires_at_semantic_clock": expires_at_semantic_clock,
        "grant_mode": grant_mode,
        "permission_ladder_entry": permission_ladder_entry,
        "plan_digest": plan_digest,
        "policy_version": policy_version,
        "principal_chain": principal_chain.to_dict(),
        "registry_digest": registry_digest,
        "risk_tier_band": risk_tier_band,
        "semantic_clock": semantic_clock.to_dict(),
        "single_use": single_use,
        "standards_fingerprint": standards_fingerprint.to_dict(),
        "tool_allowlist": list(sorted_tools),
        "ttl_seconds": ttl_seconds,
        "v3_trace_id": v3_artifact.trace_id,
    }
    v4_trace_id = _compute_v4_trace_id(pre_payload)

    return CapabilityTokenV4Artifact(
        artifact_type="CAPABILITY_TOKEN_V4",
        semantic_clock=semantic_clock,
        v4_trace_id=v4_trace_id,
        v3_artifact=v3_artifact,
        principal_chain=principal_chain,
        risk_tier_band=risk_tier_band,
        permission_ladder_entry=permission_ladder_entry,
        ttl_seconds=ttl_seconds,
        single_use=single_use,
        expires_at_semantic_clock=expires_at_semantic_clock,
        connector_allowlist=sorted_connectors,
        tool_allowlist=sorted_tools,
        plan_digest=plan_digest,
        grant_mode=grant_mode,
        standards_fingerprint=standards_fingerprint,
        policy_version=policy_version,
        registry_digest=registry_digest,
    )


__all__ = [
    "CapabilityTokenV4Artifact",
    "StandardsFingerprint",
    "issue_capability_token_v4",
]
