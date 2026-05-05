"""
P4.7 — Exit v6 X3 Checks: Board-Readiness + Citation Integrity.

Two X3 gate checks consumed by the apps_repo_brief Exit v6 pipeline:

1. BoardReadinessCheck — for BOARD_DOSSIER depth profile only.
   Verifies the L2 receipt bundle confirms all board gate thresholds
   were met (from P3.12 c0_board_gates.yaml). BLOCK if any board gate
   failed or was not checked.

2. CitationIntegrityCheck — all depth profiles.
   Verifies that citation anchors in the rendered brief meet the
   minimum count for the active depth profile. BLOCK if count < threshold.

Authority:
  - Both checks are READ-ONLY over L2ReceiptBundle and rendered slots.
  - Neither check re-mints FEC or writes state.
  - BLOCK emits X3; PASS is silent.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P4.7
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)

_CITATION_ANCHOR_RE = re.compile(r"\[(?:src|ref|cite):[^\]]{1,80}\]", re.IGNORECASE)

_PROFILE_MIN_CITATIONS: dict[str, int] = {
    "REPO_BRIEF_LIGHT": 3,
    "REPO_BRIEF_STANDARD": 8,
    "REPO_BRIEF_DEEP": 15,
    "REPO_BRIEF_BOARD_DOSSIER": 25,
}

_BOARD_PROFILE = "REPO_BRIEF_BOARD_DOSSIER"


class ExitCheckVerdict(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    SKIP = "SKIP"


@dataclass
class ExitV6CheckResult:
    check_name: str
    verdict: ExitCheckVerdict
    detail: str = ""
    metrics: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.metrics is None:
            self.metrics = {}

    @property
    def x3_triggered(self) -> bool:
        return self.verdict == ExitCheckVerdict.BLOCK

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_name": self.check_name,
            "verdict": self.verdict.value,
            "detail": self.detail,
            "metrics": self.metrics,
            "x3_triggered": self.x3_triggered,
        }


class ExitV6Checker:
    """
    Runs both Exit v6 X3 checks for apps_repo_brief.

    Usage::

        checker = ExitV6Checker()
        results = checker.run_all(receipt_bundle_dict, rendered_slots, depth_profile)
        for r in results:
            if r.x3_triggered:
                # BLOCK_COMMIT
                ...

    """

    def run_all(
        self,
        receipt_bundle: dict[str, Any],
        rendered_slots: dict[str, str],
        depth_profile: str,
    ) -> list[ExitV6CheckResult]:
        """Run all Exit v6 checks and return results."""
        results = [
            self.check_board_readiness(receipt_bundle, depth_profile),
            self.check_citation_integrity(rendered_slots, depth_profile),
        ]
        return results

    # ------------------------------------------------------------------
    # Check 1: Board readiness
    # ------------------------------------------------------------------

    def check_board_readiness(
        self,
        receipt_bundle: dict[str, Any],
        depth_profile: str,
    ) -> ExitV6CheckResult:
        """
        Board-readiness X3 gate (BOARD_DOSSIER only).

        Verifies:
          - E5 receipt coverage_pct >= 95.0
          - E4 has no escalated slots
          - E1 evidence_status is PASS or WEAK_WITH_CAVEATS (not MISSING/CONTRADICTED)
        """
        if depth_profile != _BOARD_PROFILE:
            return ExitV6CheckResult(
                check_name="board_readiness",
                verdict=ExitCheckVerdict.SKIP,
                detail=f"profile={depth_profile} — board gate not required",
            )

        e5 = receipt_bundle.get("e5", {})
        e4 = receipt_bundle.get("e4", {})
        e1 = receipt_bundle.get("e1", {})

        blocking_reasons: list[str] = []

        coverage_pct = float(e5.get("coverage_pct", 0.0))
        if coverage_pct < 95.0:
            blocking_reasons.append(
                f"E5 section coverage {coverage_pct:.1f}% < 95.0% required for BOARD_DOSSIER"
            )

        escalated = e4.get("escalated_slot_ids", [])
        if escalated:
            blocking_reasons.append(
                f"E4 has {len(escalated)} unresolved style escalation(s): {escalated}"
            )

        evidence_status = e1.get("evidence_status", "UNKNOWN")
        _disqualifying = {"MISSING", "CONTRADICTED", "UNSUPPORTED", "UNKNOWN"}
        if evidence_status in _disqualifying:
            blocking_reasons.append(
                f"E1 evidence_status={evidence_status!r} is disqualifying for board brief"
            )

        if blocking_reasons:
            _log.warning(
                "ExitV6 board_readiness BLOCK: %d reason(s)", len(blocking_reasons)
            )
            return ExitV6CheckResult(
                check_name="board_readiness",
                verdict=ExitCheckVerdict.BLOCK,
                detail="; ".join(blocking_reasons),
                metrics={
                    "coverage_pct": coverage_pct,
                    "evidence_status": evidence_status,
                    "escalated_slot_count": len(escalated),
                },
            )

        return ExitV6CheckResult(
            check_name="board_readiness",
            verdict=ExitCheckVerdict.PASS,
            metrics={
                "coverage_pct": coverage_pct,
                "evidence_status": evidence_status,
            },
        )

    # ------------------------------------------------------------------
    # Check 2: Citation integrity
    # ------------------------------------------------------------------

    def check_citation_integrity(
        self,
        rendered_slots: dict[str, str],
        depth_profile: str,
    ) -> ExitV6CheckResult:
        """
        Citation integrity X3 gate (all profiles).

        Counts [src:...], [ref:...], [cite:...] anchors across all
        rendered slots and compares against the profile minimum.
        """
        min_required = _PROFILE_MIN_CITATIONS.get(depth_profile, 3)
        full_text = "\n".join(rendered_slots.values())
        anchors = _CITATION_ANCHOR_RE.findall(full_text)
        count = len(anchors)

        if count < min_required:
            _log.warning(
                "ExitV6 citation_integrity BLOCK: found=%d required=%d profile=%s",
                count,
                min_required,
                depth_profile,
            )
            return ExitV6CheckResult(
                check_name="citation_integrity",
                verdict=ExitCheckVerdict.BLOCK,
                detail=(
                    f"citation count {count} < {min_required} required "
                    f"for profile {depth_profile}"
                ),
                metrics={
                    "citation_count": count,
                    "min_required": min_required,
                    "depth_profile": depth_profile,
                },
            )

        return ExitV6CheckResult(
            check_name="citation_integrity",
            verdict=ExitCheckVerdict.PASS,
            metrics={
                "citation_count": count,
                "min_required": min_required,
                "depth_profile": depth_profile,
            },
        )
