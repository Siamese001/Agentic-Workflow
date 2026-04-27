"""L5 Risk-Tier Control Matrix (`risk_tier_bands.md` §3) — G10 closure.

Encodes the 11 control parameters × 3 bands matrix as a deterministic SSOT.
Callers ``apply_band_controls(band)`` to derive band-specific defaults.

Doctrine: ``docs/reference/00A_L5_Governance_Safety/risk_tier_bands.md``
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L5_safety.v5.types import (
    AuditDetailLevel,
    CalibrationCadence,
    ConnectorAllowlistWidth,
    RetentionBand,
    RiskTierBandV5,
    SandboxIsolationTier,
)


@dataclass(frozen=True)
class BandControls:
    """All band-derived controls for a single risk-tier band."""

    band: RiskTierBandV5
    audit_detail_level: AuditDetailLevel
    replay_retention: RetentionBand
    sandbox_isolation_tier: SandboxIsolationTier
    capability_token_ttl_max_seconds: int
    capability_token_single_use_default: bool
    connector_allowlist_width: ConnectorAllowlistWidth
    delegation_depth_max: int
    calibration_cadence: CalibrationCadence
    red_team_gate: str
    hitl_required: bool
    guard_model_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_detail_level": self.audit_detail_level.value,
            "band": self.band.value,
            "calibration_cadence": self.calibration_cadence.value,
            "capability_token_single_use_default": self.capability_token_single_use_default,
            "capability_token_ttl_max_seconds": self.capability_token_ttl_max_seconds,
            "connector_allowlist_width": self.connector_allowlist_width.value,
            "delegation_depth_max": self.delegation_depth_max,
            "guard_model_review_required": self.guard_model_review_required,
            "hitl_required": self.hitl_required,
            "red_team_gate": self.red_team_gate,
            "replay_retention": self.replay_retention.value,
            "sandbox_isolation_tier": self.sandbox_isolation_tier.value,
        }


# `risk_tier_bands.md` §3 — control matrix SSOT
_BAND_CONTROL_MATRIX: dict[RiskTierBandV5, BandControls] = {
    RiskTierBandV5.LOW: BandControls(
        band=RiskTierBandV5.LOW,
        audit_detail_level=AuditDetailLevel.SUMMARY,
        replay_retention=RetentionBand.SHORT,
        sandbox_isolation_tier=SandboxIsolationTier.PROCESS,
        capability_token_ttl_max_seconds=3600,
        capability_token_single_use_default=False,
        connector_allowlist_width=ConnectorAllowlistWidth.DEFAULT,
        delegation_depth_max=3,
        calibration_cadence=CalibrationCadence.WEEKLY,
        red_team_gate="quarterly",
        hitl_required=False,
        guard_model_review_required=False,
    ),
    RiskTierBandV5.MODERATE: BandControls(
        band=RiskTierBandV5.MODERATE,
        audit_detail_level=AuditDetailLevel.FULL,
        replay_retention=RetentionBand.STANDARD,
        sandbox_isolation_tier=SandboxIsolationTier.PROCESS_FS,
        capability_token_ttl_max_seconds=900,
        capability_token_single_use_default=False,  # configurable per spec
        connector_allowlist_width=ConnectorAllowlistWidth.NARROWED,
        delegation_depth_max=2,
        calibration_cadence=CalibrationCadence.DAILY,
        red_team_gate="monthly",
        hitl_required=False,
        guard_model_review_required=False,
    ),
    RiskTierBandV5.HIGH: BandControls(
        band=RiskTierBandV5.HIGH,
        audit_detail_level=AuditDetailLevel.FULL_STRUCTURED,
        replay_retention=RetentionBand.EXTENDED_FORENSIC,
        sandbox_isolation_tier=SandboxIsolationTier.PROCESS_FS_NET,
        capability_token_ttl_max_seconds=300,
        capability_token_single_use_default=True,
        connector_allowlist_width=ConnectorAllowlistWidth.STRICT,
        delegation_depth_max=1,
        calibration_cadence=CalibrationCadence.CONTINUOUS,
        red_team_gate="pre-deploy+weekly",
        hitl_required=True,
        guard_model_review_required=True,
    ),
    # CRITICAL collapses to HIGH per `bridges.py::map_v5_band_to_v4`; spec doesn't
    # define a separate matrix for it. We mirror HIGH but escalate where natural.
    RiskTierBandV5.CRITICAL: BandControls(
        band=RiskTierBandV5.CRITICAL,
        audit_detail_level=AuditDetailLevel.FULL_STRUCTURED,
        replay_retention=RetentionBand.EXTENDED_FORENSIC,
        sandbox_isolation_tier=SandboxIsolationTier.PROCESS_FS_NET,
        capability_token_ttl_max_seconds=300,
        capability_token_single_use_default=True,
        connector_allowlist_width=ConnectorAllowlistWidth.STRICT,
        delegation_depth_max=1,
        calibration_cadence=CalibrationCadence.CONTINUOUS,
        red_team_gate="pre-deploy+weekly+incident",
        hitl_required=True,
        guard_model_review_required=True,
    ),
}


def apply_band_controls(band: RiskTierBandV5) -> BandControls:
    """Return the deterministic band-controls record for a risk-tier band."""
    if band not in _BAND_CONTROL_MATRIX:
        raise ValueError(f"apply_band_controls: unknown band {band!r}")
    return _BAND_CONTROL_MATRIX[band]


def assert_band_monotonicity() -> None:
    """Confirm restrictiveness ordering LOW > MODERATE > HIGH (delegation/TTL).

    Raises ``AssertionError`` on violation. Test harness uses this to prevent
    accidental band relaxation during refactors.
    """
    low = _BAND_CONTROL_MATRIX[RiskTierBandV5.LOW]
    mod = _BAND_CONTROL_MATRIX[RiskTierBandV5.MODERATE]
    high = _BAND_CONTROL_MATRIX[RiskTierBandV5.HIGH]
    assert low.delegation_depth_max >= mod.delegation_depth_max >= high.delegation_depth_max
    assert (
        low.capability_token_ttl_max_seconds
        >= mod.capability_token_ttl_max_seconds
        >= high.capability_token_ttl_max_seconds
    )


__all__ = [
    "BandControls",
    "apply_band_controls",
    "assert_band_monotonicity",
]
