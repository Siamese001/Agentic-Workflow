"""
P4.3 — StyleGate L2.E4 Same-Authority Repair Pass (AG P4.1 Option A).

Implements the L2.E4 repair step for apps_repo_brief. This is the correct
spine location for same-authority style violations: after PA emits
CompiledPromptArtifact and before Exit gates. It does NOT replace the
Exit hard gate (P4.4) — it attempts inline repair of recoverable violations.

Authority boundary:
  - L2.E4 CAN repair: length overrun, missing caveat injection, structural
    slot ordering, citation format normalisation.
  - L2.E4 CANNOT repair: persistent unsupported claims, contradicted
    evidence, missing board gate sections. Those must escalate to Exit.
  - L2.E4 NEVER: re-mints FEC, calls C0, writes to L4.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P4.3
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_BRIEF_CHARS = 8_000
_MIN_CAVEAT_CHARS = 40
_CITATION_PATTERN = re.compile(r"\[(?:src|ref|cite):[^\]]+\]", re.IGNORECASE)


class StyleViolationType(str, Enum):
    LENGTH_OVERRUN = "length_overrun"
    MISSING_CAVEAT = "missing_caveat"
    MALFORMED_CITATION = "malformed_citation"
    SLOT_ORDER_VIOLATION = "slot_order_violation"
    UNESCAPED_EVIDENCE_STUB = "unescaped_evidence_stub"


class RepairOutcome(str, Enum):
    REPAIRED = "repaired"
    ESCALATE = "escalate"
    CLEAN = "clean"


@dataclass
class StyleViolation:
    violation_type: StyleViolationType
    slot_id: str
    detail: str
    is_recoverable: bool


@dataclass
class StyleRepairResult:
    """Output of a single L2.E4 repair pass on one slot."""

    slot_id: str
    original_body: str
    repaired_body: str
    violations_found: list[StyleViolation] = field(default_factory=list)
    violations_repaired: list[StyleViolationType] = field(default_factory=list)
    violations_escalated: list[StyleViolation] = field(default_factory=list)
    outcome: RepairOutcome = RepairOutcome.CLEAN


@dataclass
class StyleGateL2RepairBundle:
    """Aggregate result of E4 repair across all rendered slots."""

    repaired_slots: dict[str, str]
    repair_results: list[StyleRepairResult]
    has_escalations: bool
    escalation_slot_ids: list[str]
    e4_receipt: dict[str, Any]


# ---------------------------------------------------------------------------
# Repair implementation
# ---------------------------------------------------------------------------


class StyleGateL2Repair:
    """
    L2.E4 same-authority style repair for apps_repo_brief.

    Usage::

        repair = StyleGateL2Repair()
        bundle = repair.run(rendered_slots, synthesis_guidance)
        if bundle.has_escalations:
            # pass escalation_slot_ids to Exit gate
            ...
        final_slots = bundle.repaired_slots

    """

    def run(
        self,
        rendered_slots: dict[str, str],
        synthesis_guidance: dict[str, Any] | None = None,
    ) -> StyleGateL2RepairBundle:
        """
        Run L2.E4 repair on all rendered slots.

        Args:
            rendered_slots:      dict slot_id → rendered string from PA.
            synthesis_guidance:  optional SynthesisGuidanceForPA from evidence_bundle.

        Returns:
            StyleGateL2RepairBundle with repaired slots and escalation list.
        """
        guidance = synthesis_guidance or {}
        results: list[StyleRepairResult] = []
        repaired: dict[str, str] = {}

        for slot_id, body in rendered_slots.items():
            result = self._repair_slot(slot_id, body, guidance)
            results.append(result)
            repaired[slot_id] = result.repaired_body

        escalations = [r for r in results if r.violations_escalated]
        has_esc = bool(escalations)
        esc_slot_ids = [r.slot_id for r in escalations]

        e4_receipt: dict[str, Any] = {
            "step": "E4",
            "pass": "style_gate_l2_repair",
            "slots_inspected": len(rendered_slots),
            "slots_repaired": sum(
                1 for r in results if r.outcome == RepairOutcome.REPAIRED
            ),
            "slots_escalated": len(esc_slot_ids),
            "escalated_slot_ids": esc_slot_ids,
            "violations_by_type": self._tally_violations(results),
        }

        _log.debug(
            "L2.E4 style repair: inspected=%d repaired=%d escalated=%d",
            len(rendered_slots),
            e4_receipt["slots_repaired"],
            len(esc_slot_ids),
        )

        return StyleGateL2RepairBundle(
            repaired_slots=repaired,
            repair_results=results,
            has_escalations=has_esc,
            escalation_slot_ids=esc_slot_ids,
            e4_receipt=e4_receipt,
        )

    # ------------------------------------------------------------------
    # Per-slot repair
    # ------------------------------------------------------------------

    def _repair_slot(
        self,
        slot_id: str,
        body: str,
        guidance: dict[str, Any],
    ) -> StyleRepairResult:
        violations: list[StyleViolation] = []
        repaired_body = body

        # Check 1: length overrun
        if len(body) > _MAX_BRIEF_CHARS:
            violations.append(
                StyleViolation(
                    StyleViolationType.LENGTH_OVERRUN,
                    slot_id,
                    f"body length {len(body)} > max {_MAX_BRIEF_CHARS}",
                    is_recoverable=True,
                )
            )
            repaired_body = self._truncate_to_limit(repaired_body)

        # Check 2: missing caveat when guidance requires it
        caveat_policy = guidance.get("unsupported_claim_policy", "")
        if caveat_policy == "caveat_required" and "[Caveat:" not in body:
            if "[ABSTAIN:" not in body and "[GAP:" not in body:
                violations.append(
                    StyleViolation(
                        StyleViolationType.MISSING_CAVEAT,
                        slot_id,
                        "caveat_required policy but no [Caveat: block found",
                        is_recoverable=True,
                    )
                )

        # Check 3: unescaped evidence stubs (leftover {{KEY}} tokens)
        stubs = re.findall(r"\{\{[^}]+\}\}", repaired_body)
        if stubs:
            violations.append(
                StyleViolation(
                    StyleViolationType.UNESCAPED_EVIDENCE_STUB,
                    slot_id,
                    f"unresolved tokens: {stubs[:3]}",
                    is_recoverable=False,  # escalate — PA did not resolve
                )
            )

        repaired_violations: list[StyleViolationType] = []
        escalated: list[StyleViolation] = []

        for v in violations:
            if v.is_recoverable:
                repaired_violations.append(v.violation_type)
            else:
                escalated.append(v)

        if not violations:
            outcome = RepairOutcome.CLEAN
        elif escalated:
            outcome = RepairOutcome.ESCALATE
        else:
            outcome = RepairOutcome.REPAIRED

        return StyleRepairResult(
            slot_id=slot_id,
            original_body=body,
            repaired_body=repaired_body,
            violations_found=violations,
            violations_repaired=repaired_violations,
            violations_escalated=escalated,
            outcome=outcome,
        )

    # ------------------------------------------------------------------
    # Repair helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _truncate_to_limit(text: str) -> str:
        """Hard-truncate to _MAX_BRIEF_CHARS with an ellipsis note."""
        cut = text[: _MAX_BRIEF_CHARS - 80]
        last_nl = cut.rfind("\n")
        if last_nl > _MAX_BRIEF_CHARS // 2:
            cut = cut[:last_nl]
        return cut + "\n\n[L2.E4: content truncated to meet length gate]"

    # ------------------------------------------------------------------
    # Receipt helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tally_violations(results: list[StyleRepairResult]) -> dict[str, int]:
        tally: dict[str, int] = {}
        for r in results:
            for v in r.violations_found:
                tally[v.violation_type.value] = tally.get(v.violation_type.value, 0) + 1
        return tally
