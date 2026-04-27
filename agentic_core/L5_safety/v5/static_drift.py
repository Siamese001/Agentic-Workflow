"""L5 Static Governance & Structure Drift (00A.7) — G7 closure.

Surfaces CI-baseline-detected drift as L5-plane discrete dataclasses so
``GovernanceResult.governance_reports["static_report"]`` carries typed,
deterministic shape rather than free-form CI output.

Doctrine: ``docs/reference/00A_L5_Governance_Safety/00A.7_L5_Static_Governance_and_Structure_Drift.md``
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.L5_safety.v5.types import StaticDriftKind


def _sorted_strings(values: tuple[str, ...]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class StaticGovernanceReviewPacket:
    """Top-level packet enumerating changed files + scan refs + waiver/ADR status."""

    review_id: str
    changed_files: tuple[str, ...]
    changed_authority_surfaces: tuple[str, ...]
    policy_hash_before: str
    policy_hash_after: str
    blueprint_hash_before: str
    blueprint_hash_after: str
    registry_digest_before: tuple[str, ...]
    registry_digest_after: tuple[str, ...]
    scan_refs: tuple[str, ...]
    waiver_refs: tuple[str, ...]
    adr_refs: tuple[str, ...]
    audit_replay_refs: tuple[str, ...]

    @property
    def governance_changed(self) -> bool:
        return (
            self.policy_hash_before != self.policy_hash_after
            or self.blueprint_hash_before != self.blueprint_hash_after
            or set(self.registry_digest_before) != set(self.registry_digest_after)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "adr_refs": _sorted_strings(self.adr_refs),
            "audit_replay_refs": _sorted_strings(self.audit_replay_refs),
            "blueprint_hash_after": self.blueprint_hash_after,
            "blueprint_hash_before": self.blueprint_hash_before,
            "changed_authority_surfaces": _sorted_strings(self.changed_authority_surfaces),
            "changed_files": _sorted_strings(self.changed_files),
            "governance_changed": self.governance_changed,
            "policy_hash_after": self.policy_hash_after,
            "policy_hash_before": self.policy_hash_before,
            "registry_digest_after": _sorted_strings(self.registry_digest_after),
            "registry_digest_before": _sorted_strings(self.registry_digest_before),
            "review_id": self.review_id,
            "scan_refs": _sorted_strings(self.scan_refs),
            "waiver_refs": _sorted_strings(self.waiver_refs),
        }


@dataclass(frozen=True)
class StaticDriftEvidencePacket:
    """Per-drift-kind evidence packet aggregating findings."""

    evidence_id: str
    drift_kind: StaticDriftKind
    findings: tuple[str, ...]
    severity: str  # info | warn | critical
    waiver_required: bool
    adr_required: bool

    def __post_init__(self) -> None:
        if self.severity not in {"info", "warn", "critical"}:
            raise ValueError(
                f"StaticDriftEvidencePacket: severity must be info|warn|critical, "
                f"got {self.severity!r}",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "adr_required": self.adr_required,
            "drift_kind": self.drift_kind.value,
            "evidence_id": self.evidence_id,
            "findings": _sorted_strings(self.findings),
            "severity": self.severity,
            "waiver_required": self.waiver_required,
        }


@dataclass(frozen=True)
class ArchitectureDriftReport:
    """Layer boundary / dependency / route topology drift."""

    report_id: str
    layer_boundary_violations: tuple[str, ...]
    dependency_inversions: tuple[str, ...]
    route_topology_changes: tuple[str, ...]
    write_path_changes: tuple[str, ...]
    retrieval_boundary_changes: tuple[str, ...]
    prompt_assembly_boundary_changes: tuple[str, ...]
    learning_boundary_changes: tuple[str, ...]
    uwg_boundary_changes: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not (
            self.layer_boundary_violations
            or self.dependency_inversions
            or self.write_path_changes
            or self.retrieval_boundary_changes
            or self.prompt_assembly_boundary_changes
            or self.learning_boundary_changes
            or self.uwg_boundary_changes
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependency_inversions": _sorted_strings(self.dependency_inversions),
            "layer_boundary_violations": _sorted_strings(self.layer_boundary_violations),
            "learning_boundary_changes": _sorted_strings(self.learning_boundary_changes),
            "passed": self.passed,
            "prompt_assembly_boundary_changes": _sorted_strings(
                self.prompt_assembly_boundary_changes,
            ),
            "report_id": self.report_id,
            "retrieval_boundary_changes": _sorted_strings(self.retrieval_boundary_changes),
            "route_topology_changes": _sorted_strings(self.route_topology_changes),
            "uwg_boundary_changes": _sorted_strings(self.uwg_boundary_changes),
            "write_path_changes": _sorted_strings(self.write_path_changes),
        }


@dataclass(frozen=True)
class PolicyWeakeningReport:
    """Hard-constraint / risk-tier / HITL threshold / standards weakening."""

    report_id: str
    hard_constraint_weakening: tuple[str, ...]
    risk_tier_weakening: tuple[str, ...]
    hitl_threshold_weakening: tuple[str, ...]
    sector_overlay_weakening: tuple[str, ...]
    standards_fingerprint_weakening: tuple[str, ...]
    replay_audit_weakening: tuple[str, ...]
    egress_weakening: tuple[str, ...]
    sandbox_weakening: tuple[str, ...]
    credential_weakening: tuple[str, ...]
    data_sensitivity_weakening: tuple[str, ...]

    @property
    def weakened(self) -> bool:
        return any(
            (
                self.hard_constraint_weakening,
                self.risk_tier_weakening,
                self.hitl_threshold_weakening,
                self.sector_overlay_weakening,
                self.standards_fingerprint_weakening,
                self.replay_audit_weakening,
                self.egress_weakening,
                self.sandbox_weakening,
                self.credential_weakening,
                self.data_sensitivity_weakening,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "credential_weakening": _sorted_strings(self.credential_weakening),
            "data_sensitivity_weakening": _sorted_strings(self.data_sensitivity_weakening),
            "egress_weakening": _sorted_strings(self.egress_weakening),
            "hard_constraint_weakening": _sorted_strings(self.hard_constraint_weakening),
            "hitl_threshold_weakening": _sorted_strings(self.hitl_threshold_weakening),
            "replay_audit_weakening": _sorted_strings(self.replay_audit_weakening),
            "report_id": self.report_id,
            "risk_tier_weakening": _sorted_strings(self.risk_tier_weakening),
            "sandbox_weakening": _sorted_strings(self.sandbox_weakening),
            "sector_overlay_weakening": _sorted_strings(self.sector_overlay_weakening),
            "standards_fingerprint_weakening": _sorted_strings(
                self.standards_fingerprint_weakening,
            ),
            "weakened": self.weakened,
        }


@dataclass(frozen=True)
class GoldenSnapshotComparisonReport:
    """Compares current state against golden snapshot for new bypasses / deletions / weakening."""

    report_id: str
    new_bypasses: tuple[str, ...]
    deleted_gates: tuple[str, ...]
    weakened_defaults: tuple[str, ...]
    relaxed_scopes: tuple[str, ...]
    missing_replay_metadata: tuple[str, ...]
    missing_audit_metadata: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not any(
            (
                self.new_bypasses,
                self.deleted_gates,
                self.weakened_defaults,
                self.relaxed_scopes,
                self.missing_replay_metadata,
                self.missing_audit_metadata,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "deleted_gates": _sorted_strings(self.deleted_gates),
            "missing_audit_metadata": _sorted_strings(self.missing_audit_metadata),
            "missing_replay_metadata": _sorted_strings(self.missing_replay_metadata),
            "new_bypasses": _sorted_strings(self.new_bypasses),
            "passed": self.passed,
            "relaxed_scopes": _sorted_strings(self.relaxed_scopes),
            "report_id": self.report_id,
            "weakened_defaults": _sorted_strings(self.weakened_defaults),
        }


__all__ = [
    "ArchitectureDriftReport",
    "GoldenSnapshotComparisonReport",
    "PolicyWeakeningReport",
    "StaticDriftEvidencePacket",
    "StaticGovernanceReviewPacket",
]
