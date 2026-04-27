"""L5 Egress Receipt Family (00A.5) — G5 closure.

Surfaces the v4 egress lane evidence as L5-plane discrete dataclasses so
``GovernanceResult.governance_reports["egress_report"]`` carries typed,
deterministic shape rather than free-form bridge output.

Doctrine: ``docs/reference/00A_L5_Governance_Safety/00A.5_L5_Egress_and_Provider_Governance.md``
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.L5_safety.v5.types import EgressKind


def _sorted_strings(values: tuple[str, ...]) -> list[str]:
    return sorted(values)


# =============================================================================
# 00A.5 §7.1 contract 1 — EgressCertificationRequest
# =============================================================================


@dataclass(frozen=True)
class EgressCertificationRequest:
    """Egress certification request: declared lane + scope + credentials."""

    request_id: str
    egress_kind: EgressKind
    target_id: str  # provider name | tool id | connector id | network destination
    requested_scope: tuple[str, ...]
    declared_payload_hash: str
    declared_credential_scope: tuple[str, ...]
    side_effect_class: str  # NONE | READ | MODEL_CALL | ...
    region: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "declared_credential_scope": _sorted_strings(self.declared_credential_scope),
            "declared_payload_hash": self.declared_payload_hash,
            "egress_kind": self.egress_kind.value,
            "region": self.region,
            "request_id": self.request_id,
            "requested_scope": _sorted_strings(self.requested_scope),
            "side_effect_class": self.side_effect_class,
            "target_id": self.target_id,
        }


# =============================================================================
# 00A.5 §7.1 contract 2 — EgressCertificationReceipt
# =============================================================================


@dataclass(frozen=True)
class EgressCertificationReceipt:
    """L5 certification status for an egress lane."""

    receipt_id: str
    request_id: str
    egress_kind: EgressKind
    certification_status: str  # CERTIFIED | NOT_CERTIFIED | REQUIRES_RE_REVIEW
    granted_scope: tuple[str, ...]
    denied_scope: tuple[str, ...]
    audit_ref: str
    replay_ref: str

    def __post_init__(self) -> None:
        if self.certification_status not in {"CERTIFIED", "NOT_CERTIFIED", "REQUIRES_RE_REVIEW"}:
            raise ValueError(
                f"EgressCertificationReceipt: certification_status must be "
                f"CERTIFIED|NOT_CERTIFIED|REQUIRES_RE_REVIEW, got "
                f"{self.certification_status!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_ref": self.audit_ref,
            "certification_status": self.certification_status,
            "denied_scope": _sorted_strings(self.denied_scope),
            "egress_kind": self.egress_kind.value,
            "granted_scope": _sorted_strings(self.granted_scope),
            "receipt_id": self.receipt_id,
            "replay_ref": self.replay_ref,
            "request_id": self.request_id,
        }


# =============================================================================
# 00A.5 §7.1 contracts 3–6 — Substitution reports (Provider/Model/Tool/Connector)
# =============================================================================


@dataclass(frozen=True)
class SubstitutionReport:
    """Generic substitution detection. Specialized by `kind` discriminator."""

    report_id: str
    kind: str  # provider | model | tool | connector
    declared_target: str
    actual_target: str
    substituted: bool
    silent_fallback: bool
    re_certification_required: bool

    def __post_init__(self) -> None:
        if self.kind not in {"provider", "model", "tool", "connector"}:
            raise ValueError(
                f"SubstitutionReport: kind must be provider|model|tool|connector, "
                f"got {self.kind!r}",
            )
        # Substitution always requires re-certification per spec invariant 11
        if self.substituted and not self.re_certification_required:
            raise ValueError(
                "SubstitutionReport: substituted=True requires "
                "re_certification_required=True (spec lines 7+11 — no silent "
                "fallback; provider/model/tool/connector change re-certifies)",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "actual_target": self.actual_target,
            "declared_target": self.declared_target,
            "kind": self.kind,
            "re_certification_required": self.re_certification_required,
            "report_id": self.report_id,
            "silent_fallback": self.silent_fallback,
            "substituted": self.substituted,
        }


def provider_substitution_report(**kw: Any) -> SubstitutionReport:
    return SubstitutionReport(kind="provider", **kw)


def model_substitution_report(**kw: Any) -> SubstitutionReport:
    return SubstitutionReport(kind="model", **kw)


def tool_substitution_report(**kw: Any) -> SubstitutionReport:
    return SubstitutionReport(kind="tool", **kw)


def connector_substitution_report(**kw: Any) -> SubstitutionReport:
    return SubstitutionReport(kind="connector", **kw)


# =============================================================================
# 00A.5 §7.1 — HiddenEgressPathReport / DirectSDKBypassReport / NoSilentFallbackReceipt
# =============================================================================


@dataclass(frozen=True)
class HiddenEgressPathReport:
    """Detected unauthorized egress path (direct SDK / hardcoded URL / wrapper bypass)."""

    report_id: str
    detected_paths: tuple[str, ...]
    bypass_kind: tuple[str, ...]  # subset of: direct_sdk_import|hardcoded_url|wrapper_bypass|...
    severity: str  # info | warn | critical

    def __post_init__(self) -> None:
        if self.severity not in {"info", "warn", "critical"}:
            raise ValueError(
                f"HiddenEgressPathReport: severity must be info|warn|critical, "
                f"got {self.severity!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "bypass_kind": _sorted_strings(self.bypass_kind),
            "detected_paths": _sorted_strings(self.detected_paths),
            "report_id": self.report_id,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class NoSilentFallbackReceipt:
    """Affirmative receipt that no silent fallback occurred during egress."""

    receipt_id: str
    egress_kind: EgressKind
    declared_target: str
    actual_target: str
    silent_fallback_detected: bool = False

    def __post_init__(self) -> None:
        if self.silent_fallback_detected and self.declared_target == self.actual_target:
            raise ValueError(
                "NoSilentFallbackReceipt: silent_fallback_detected=True but "
                "declared_target==actual_target (inconsistent state)",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "actual_target": self.actual_target,
            "declared_target": self.declared_target,
            "egress_kind": self.egress_kind.value,
            "receipt_id": self.receipt_id,
            "silent_fallback_detected": self.silent_fallback_detected,
        }


__all__ = [
    "EgressCertificationReceipt",
    "EgressCertificationRequest",
    "HiddenEgressPathReport",
    "NoSilentFallbackReceipt",
    "SubstitutionReport",
    "connector_substitution_report",
    "model_substitution_report",
    "provider_substitution_report",
    "tool_substitution_report",
]
