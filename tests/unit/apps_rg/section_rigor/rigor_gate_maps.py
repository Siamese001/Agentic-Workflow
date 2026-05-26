"""Rigor/runtime X2 gate classification maps for complexity radar (W1.0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from apps_rg.runtime.rigor.lane_registry import C0_CRITICAL_GATES
from apps_rg.runtime.sections.section_product_shape_ssot import (
    RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
    RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS,
    RETIRED_UNIFY_BULLETS_X2_GATE_IDS,
)

GateAccounting = Literal["C0_SIDECAR", "RETIRED", "REQUIRES_RUNTIME_X2", "UNCLASSIFIED"]

# Explicit markers for red-path tests only (not in C0/RETIRED maps).
UNCLASSIFIED_GATE_MARKERS: frozenset[str] = frozenset(
    {
        "x2___synthetic_unregistered_gate___",
        "x2___ghost_not_in_maps___",
    }
)

C0_SIDECAR_GATE_IDS: frozenset[str] = frozenset(C0_CRITICAL_GATES)

_PLAN_ID = "apps-rg-complexity-test-radar-605dcc"
_OWNER = "apps_rg_section_rigor"


@dataclass(frozen=True)
class RetiredGateRef:
    gate_id: str
    retired_reason: str
    replacement_gate_id: str | None
    NOT_REPLACED_WITH_REASON: str | None
    test_ref: str
    owner: str

    def validate(self) -> None:
        if not self.gate_id:
            raise ValueError("gate_id required")
        if not self.retired_reason.strip():
            raise ValueError(f"{self.gate_id}: retired_reason required")
        if not self.test_ref.strip():
            raise ValueError(f"{self.gate_id}: test_ref required")
        if not self.owner.strip():
            raise ValueError(f"{self.gate_id}: owner required")
        if self.replacement_gate_id and self.NOT_REPLACED_WITH_REASON:
            raise ValueError(f"{self.gate_id}: replacement_gate_id and NOT_REPLACED_WITH_REASON are mutually exclusive")
        if not self.replacement_gate_id and not (self.NOT_REPLACED_WITH_REASON or "").strip():
            raise ValueError(f"{self.gate_id}: replacement_gate_id or NOT_REPLACED_WITH_REASON required")


def _retired(
    gate_id: str,
    *,
    retired_reason: str,
    replacement_gate_id: str | None = None,
    not_replaced_reason: str | None = None,
    test_ref: str = "tests/unit/apps_rg/section_rigor/test_rigor_runtime_x2_emission_parity.py",
) -> RetiredGateRef:
    return RetiredGateRef(
        gate_id=gate_id,
        retired_reason=retired_reason,
        replacement_gate_id=replacement_gate_id,
        NOT_REPLACED_WITH_REASON=not_replaced_reason,
        test_ref=test_ref,
        owner=_OWNER,
    )


def _build_retired_gate_refs() -> dict[str, RetiredGateRef]:
    out: dict[str, RetiredGateRef] = {}
    for gid in RETIRED_EXEC_SUMMARY_X2_GATE_IDS:
        out[gid] = _retired(
            gid,
            retired_reason="Legacy exec summary shape bands superseded by x2_exec_summary_sentence_count_6",
            replacement_gate_id="x2_exec_summary_sentence_count_6",
        )
    from apps_rg.runtime.sections.section_product_shape_ssot import (
        RETIRED_IBM_BULLETS_X2_GATE_IDS,
        RETIRED_UNIFY_BULLETS_X2_GATE_IDS,
    )

    for gid in RETIRED_UNIFY_BULLETS_X2_GATE_IDS:
        out[gid] = _retired(
            gid,
            retired_reason="Rewrite intensity model retired; pool selection + score floor governs bullets",
            replacement_gate_id="x2_unify_bullet_count_6",
        )
    for gid in RETIRED_IBM_BULLETS_X2_GATE_IDS:
        out[gid] = _retired(
            gid,
            retired_reason="Rewrite intensity model retired; pool selection + score floor governs bullets",
            replacement_gate_id="x2_ibm_bullet_count_5",
        )
    for gid in RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS:
        out[gid] = _retired(
            gid,
            retired_reason="SRFS slice membership gate retired; active pool source facts gate replaces",
            replacement_gate_id=gid.replace("_source_fact_ids_within_srfs_slice", "_active_proof_pool_source_fact_ids"),
        )
    # Rigor-registry gates not emitted in stale proof bundles — documented retirement / sidecar alignment
    rigor_only: tuple[tuple[str, str, str | None], ...] = (
        (
            "x2_headline_claim_ledger_no_silent_row_drop",
            "Rigor-only ledger integrity; covered by dedicated headline claim ledger tests",
            "x2_headline_claim_ledger_rows_present",
        ),
        (
            "x2_headline_source_fact_ids_within_srfs_slice",
            "Superseded by graph active proof pool gate family",
            None,
        ),
    )
    for gid, reason, repl in rigor_only:
        if gid not in out:
            out[gid] = _retired(
                gid,
                retired_reason=reason,
                replacement_gate_id=repl,
                not_replaced_reason=None if repl else reason,
            )
    return out


RETIRED_GATE_REFS: dict[str, RetiredGateRef] = _build_retired_gate_refs()


def validate_retired_gate_ref(ref: RetiredGateRef) -> None:
    ref.validate()


def gate_accounting_status(gate_id: str) -> GateAccounting:
    gid = str(gate_id or "").strip()
    if not gid or gid in UNCLASSIFIED_GATE_MARKERS:
        return "UNCLASSIFIED"
    if gid in C0_SIDECAR_GATE_IDS:
        return "C0_SIDECAR"
    if gid in RETIRED_GATE_REFS:
        validate_retired_gate_ref(RETIRED_GATE_REFS[gid])
        return "RETIRED"
    return "REQUIRES_RUNTIME_X2"


def is_gate_verdict_known(gate_row: dict | None) -> bool:
    if not isinstance(gate_row, dict):
        return False
    if "pass" not in gate_row and "pass_" not in gate_row:
        return False
    return True


__all__ = [
    "C0_SIDECAR_GATE_IDS",
    "RETIRED_GATE_REFS",
    "RetiredGateRef",
    "GateAccounting",
    "gate_accounting_status",
    "is_gate_verdict_known",
    "validate_retired_gate_ref",
]
