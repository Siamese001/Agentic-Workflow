"""
P4.6 — L2 E1-E5 Receipt Definitions for apps_repo_brief (AG P4.1 Option A).

L2 bounded synthesis emits one receipt per execution step (E1-E5).
Exit consumes the receipt bundle for X3 gate decisions.

Receipt authority:
  - E1: evidence ingestion from C0 FEC.v1 (read-only, no re-mint)
  - E2: slot body assembly from CompiledPromptArtifact (read rendered_slots)
  - E3: caveat and confidence annotation pass
  - E4: style repair (StyleGateL2Repair — same-authority violations only)
  - E5: section gap reconciliation (verify required sections covered)

None of E1-E5 may:
  - Write to L4
  - Call external providers
  - Re-mint authoritative FEC
  - Modify CompiledPromptArtifact (read-only input)

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P4.6
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReceiptStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class L2Receipt:
    """Base receipt emitted by every L2 step."""

    step: str = ""
    status: ReceiptStatus = ReceiptStatus.PASS
    detail: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "status": self.status.value,
            "detail": self.detail,
            "metrics": self.metrics,
        }


@dataclass
class E1Receipt(L2Receipt):
    """
    E1 — Evidence ingestion receipt.

    Confirms that the C0 FinalEvidenceContract.v1 was read and
    all required sections were present for the active depth profile.
    """

    step: str = field(default="E1")
    sections_required: int = 0
    sections_present: int = 0
    evidence_status: str = ""
    depth_profile: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "sections_required": self.sections_required,
            "sections_present": self.sections_present,
            "evidence_status": self.evidence_status,
            "depth_profile": self.depth_profile,
        })
        return d


@dataclass
class E2Receipt(L2Receipt):
    """
    E2 — Slot assembly receipt.

    Confirms that all required slots from the CompiledPromptArtifact
    were assembled into the L2 working document.
    """

    step: str = field(default="E2")
    slots_required: int = 0
    slots_assembled: int = 0
    missing_slots: list[str] = field(default_factory=list)
    template_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "slots_required": self.slots_required,
            "slots_assembled": self.slots_assembled,
            "missing_slots": self.missing_slots,
            "template_id": self.template_id,
        })
        return d


@dataclass
class E3Receipt(L2Receipt):
    """
    E3 — Caveat and confidence annotation receipt.

    Confirms that weak-evidence slots received caveat injection
    and that confidence annotations are consistent with C0 FEC.
    """

    step: str = field(default="E3")
    slots_annotated: int = 0
    caveats_injected: int = 0
    caveat_policy: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "slots_annotated": self.slots_annotated,
            "caveats_injected": self.caveats_injected,
            "caveat_policy": self.caveat_policy,
        })
        return d


@dataclass
class E4Receipt(L2Receipt):
    """
    E4 — StyleGate L2 repair receipt.

    Records the outcome of the same-authority style repair pass.
    Escalations are forwarded to Exit gate (P4.4).
    """

    step: str = field(default="E4")
    slots_inspected: int = 0
    slots_repaired: int = 0
    slots_escalated: int = 0
    escalated_slot_ids: list[str] = field(default_factory=list)
    violations_by_type: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "slots_inspected": self.slots_inspected,
            "slots_repaired": self.slots_repaired,
            "slots_escalated": self.slots_escalated,
            "escalated_slot_ids": self.escalated_slot_ids,
            "violations_by_type": self.violations_by_type,
        })
        return d


@dataclass
class E5Receipt(L2Receipt):
    """
    E5 — Section gap reconciliation receipt.

    Verifies that all required brief sections are covered after E1-E4.
    Emits a final coverage summary for Exit to consume.
    """

    step: str = field(default="E5")
    sections_covered: int = 0
    sections_total: int = 0
    coverage_pct: float = 0.0
    gap_section_ids: list[str] = field(default_factory=list)
    board_gate_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "sections_covered": self.sections_covered,
            "sections_total": self.sections_total,
            "coverage_pct": self.coverage_pct,
            "gap_section_ids": self.gap_section_ids,
            "board_gate_required": self.board_gate_required,
        })
        return d


@dataclass
class L2ReceiptBundle:
    """
    Aggregate of all E1-E5 receipts emitted by L2.

    Exit gate consumes this bundle for X3 decisions.
    The bundle is read-only after construction — L2 is the sole emitter.
    """

    e1: E1Receipt
    e2: E2Receipt
    e3: E3Receipt
    e4: E4Receipt
    e5: E5Receipt

    def overall_status(self) -> ReceiptStatus:
        """Aggregate status: FAIL if any step fails, WARN if any warns, SKIP if all skip, else PASS."""
        statuses = [self.e1.status, self.e2.status, self.e3.status, self.e4.status, self.e5.status]
        if ReceiptStatus.FAIL in statuses:
            return ReceiptStatus.FAIL
        if ReceiptStatus.WARN in statuses:
            return ReceiptStatus.WARN
        if all(s == ReceiptStatus.SKIP for s in statuses):
            return ReceiptStatus.SKIP
        return ReceiptStatus.PASS

    def has_exit_escalations(self) -> bool:
        """True when E4 has style violations that L2 could not repair."""
        return bool(self.e4.escalated_slot_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_status": self.overall_status().value,
            "e1": self.e1.to_dict(),
            "e2": self.e2.to_dict(),
            "e3": self.e3.to_dict(),
            "e4": self.e4.to_dict(),
            "e5": self.e5.to_dict(),
        }

    @classmethod
    def make_skip_bundle(cls) -> "L2ReceiptBundle":
        """Return a SKIP bundle for paths that bypass L2 (e.g. cache terminal return)."""
        return cls(
            e1=E1Receipt(status=ReceiptStatus.SKIP, detail="cache_terminal_return"),
            e2=E2Receipt(status=ReceiptStatus.SKIP),
            e3=E3Receipt(status=ReceiptStatus.SKIP),
            e4=E4Receipt(status=ReceiptStatus.SKIP),
            e5=E5Receipt(status=ReceiptStatus.SKIP),
        )
