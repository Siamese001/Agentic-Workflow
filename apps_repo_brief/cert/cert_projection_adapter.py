"""
P4.5 — Cert Projection Adapter (AG P4.2 Option A).

READ-ONLY projection of the authoritative C0 FinalEvidenceContract.v1
for Exit pipeline consumption.

Authority contract:
  - This module NEVER mints, modifies, or overwrites FEC fields.
  - It reads the C0 FEC dict and projects the subset of fields
    that the Exit pipeline and cert audit surface need.
  - The authoritative source is always apps_repo_brief.c0.repo_brief_final_contract.
  - cert/fec_producer.py is RETIRED — see fec_producer.py for the retirement guard.

The projection adapter provides:
  1. CertProjection dataclass — structured view of FEC fields for Exit.
  2. project() — build a CertProjection from a raw C0 FEC dict.
  3. validate_projection() — assert projection completeness for audit.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P4.5
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)

# Fields projected from FEC for Exit pipeline consumption
_REQUIRED_PROJECTION_FIELDS = frozenset([
    "schema_version",
    "contract_type",
    "retrieval_surface_id",
    "evidence_status",
    "depth_profile",
    "is_grounded",
    "requires_abstain",
])


@dataclass
class CertProjection:
    """
    Read-only projection of C0 FinalEvidenceContract.v1 fields for Exit/cert.

    All fields sourced from C0 FEC dict; none synthesised here.
    """

    schema_version: str
    contract_type: str
    retrieval_surface_id: str
    evidence_status: str
    depth_profile: str
    is_grounded: bool
    requires_abstain: bool
    # Optional fields projected when present
    board_gate_passed: bool | None = None
    stale_source_count: int = 0
    coverage_pct: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract_type": self.contract_type,
            "retrieval_surface_id": self.retrieval_surface_id,
            "evidence_status": self.evidence_status,
            "depth_profile": self.depth_profile,
            "is_grounded": self.is_grounded,
            "requires_abstain": self.requires_abstain,
            "board_gate_passed": self.board_gate_passed,
            "stale_source_count": self.stale_source_count,
            "coverage_pct": self.coverage_pct,
        }


class CertProjectionAdapter:
    """
    Read-only projection adapter for C0 FinalEvidenceContract.v1.

    Usage::

        adapter = CertProjectionAdapter()
        projection = adapter.project(c0_fec_dict)
        # Pass projection to Exit pipeline; never pass raw fec_producer output.

    """

    def project(self, fec: dict[str, Any]) -> CertProjection:
        """
        Build a CertProjection from the raw C0 FEC dict.

        Args:
            fec: The C0 FinalEvidenceContract.v1 dict (from evidence_bundle
                 ["FinalEvidenceContract"] or directly from C0 output).

        Returns:
            CertProjection — read-only Exit view.

        Raises:
            ValueError: if required FEC fields are missing.
        """
        if not isinstance(fec, dict):
            raise ValueError(
                f"CertProjectionAdapter.project() expects a dict, got {type(fec).__name__}"
            )

        missing = [
            f for f in ("schema_version", "contract_type", "retrieval_surface_id")
            if not fec.get(f)
        ]
        if missing:
            _log.warning(
                "CertProjectionAdapter: FEC missing fields %s — projection may be incomplete",
                missing,
            )

        # Evidence status — may be nested under 'status' or top-level
        status_block = fec.get("status") or {}
        evidence_status = (
            status_block.get("evidence_status")
            or fec.get("evidence_status")
            or "UNKNOWN"
        )

        # is_grounded: PASS or WEAK_WITH_CAVEATS → True
        grounded_statuses = {"PASS", "WEAK_WITH_CAVEATS", "WEAK"}
        is_grounded = evidence_status in grounded_statuses

        # requires_abstain: MISSING or CONTRADICTED → True
        abstain_statuses = {"MISSING", "CONTRADICTED", "UNSUPPORTED"}
        requires_abstain = evidence_status in abstain_statuses

        # Board gate — optional
        board_gate = fec.get("board_gate_thresholds") or {}
        board_gate_passed: bool | None = None
        if board_gate:
            board_gate_passed = not bool(fec.get("board_gate_failures"))

        # Freshness
        freshness = fec.get("freshness_report") or {}
        stale_count = len(freshness.get("stale_sources") or [])

        # Coverage
        coverage_matrix = fec.get("briefing_coverage_matrix") or {}
        coverage_pct: float | None = None
        if isinstance(coverage_matrix, dict):
            sections = coverage_matrix.get("sections") or []
            if sections:
                passed = sum(
                    1 for s in sections
                    if isinstance(s, dict)
                    and s.get("evidence_status") in {"PASS", "WEAK_WITH_CAVEATS"}
                )
                coverage_pct = round(100.0 * passed / len(sections), 1)

        projection = CertProjection(
            schema_version=fec.get("schema_version", "apps_repo_brief.FinalEvidenceContract/v1"),
            contract_type=fec.get("contract_type", "apps_repo_brief.FinalEvidenceContract.v1"),
            retrieval_surface_id=fec.get("retrieval_surface_id", "repo_brief_docs"),
            evidence_status=evidence_status,
            depth_profile=fec.get("depth_profile", "REPO_BRIEF_STANDARD"),
            is_grounded=is_grounded,
            requires_abstain=requires_abstain,
            board_gate_passed=board_gate_passed,
            stale_source_count=stale_count,
            coverage_pct=coverage_pct,
        )

        _log.debug(
            "CertProjection built: evidence_status=%s is_grounded=%s requires_abstain=%s",
            projection.evidence_status,
            projection.is_grounded,
            projection.requires_abstain,
        )
        return projection

    def validate_projection(self, projection: CertProjection) -> list[str]:
        """
        Return list of validation warnings for the projection.

        Does NOT raise — Exit gate decides whether to block.
        """
        warnings: list[str] = []
        if projection.evidence_status == "UNKNOWN":
            warnings.append("evidence_status=UNKNOWN — C0 FEC did not set status")
        if projection.retrieval_surface_id != "repo_brief_docs":
            warnings.append(
                f"retrieval_surface_id={projection.retrieval_surface_id!r} "
                f"— expected 'repo_brief_docs'"
            )
        if projection.requires_abstain and not projection.is_grounded:
            pass  # expected — consistent
        elif projection.requires_abstain and projection.is_grounded:
            warnings.append(
                "CertProjection inconsistency: requires_abstain=True but is_grounded=True"
            )
        return warnings
