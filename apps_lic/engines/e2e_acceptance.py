"""E2E acceptance modes for apps_lic LinkedIn outreach hardening.

This module is deliberately provider-free. It classifies already-produced E2E
rows so test reports can distinguish a policy-correct no-send block from a
failure to generate a sendable draft. It must never clear a message or weaken
X2/Exit gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from apps_lic.engines.recipient_classification import CLASS_UNKNOWN
from apps_lic.engines.validation_exit import (
    EXIT_CLEAR_DRAFT,
    GATE_RECIPIENT_CLASS,
    GATE_ROLE_OWNERSHIP_FIT,
)


ACCEPTANCE_MODE_STRICT_TARGET_FIT = "strict_target_fit"
ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE = "all_clear_eligible"
ACCEPTANCE_MODES = (
    ACCEPTANCE_MODE_STRICT_TARGET_FIT,
    ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
)

TARGET_ELIGIBLE = "ELIGIBLE"
TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE = "ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE"
TARGET_NOT_TARGETABLE = "NOT_TARGETABLE"
TARGET_C0_EVIDENCE_REQUIRED = "C0_EVIDENCE_REQUIRED"

ROW_ACCEPTED_CLEAR = "accepted_clear"
ROW_POLICY_CORRECT_BLOCK = "policy_correct_block"
ROW_ALL_CLEAR_REMEDIATION_REQUIRED = "all_clear_remediation_required"
ROW_EXCLUDED_FROM_ALL_CLEAR = "excluded_from_all_clear_eligible"
ROW_UNEXPECTED_GAP = "unexpected_gap"

NO_WEAKENING_REQUIRED_GATE_IDS = (
    GATE_RECIPIENT_CLASS,
    GATE_ROLE_OWNERSHIP_FIT,
)
NO_WEAKENING_INVARIANTS = (
    "recipient_class_present_and_derived_gate_must_remain_enabled",
    "role_ownership_fit_gate_must_remain_enabled",
    "sc_or_extra_judges_must_not_compensate_for_missing_c0_evidence",
    "x1d_must_not_override_c0_x2_no_send_or_exit",
)


@dataclass(frozen=True)
class E2EProfileAcceptance:
    profile_id: str
    disposition: str
    derived_class: str
    status: str
    reason: str
    failed_gates: tuple[str, ...]
    included_in_mode: bool = True

    @property
    def passed(self) -> bool:
        return self.status in {ROW_ACCEPTED_CLEAR, ROW_POLICY_CORRECT_BLOCK, ROW_EXCLUDED_FROM_ALL_CLEAR}

    def to_packet(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "disposition": self.disposition,
            "derived_class": self.derived_class,
            "status": self.status,
            "reason": self.reason,
            "failed_gates": list(self.failed_gates),
            "included_in_mode": self.included_in_mode,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class E2EAcceptanceReport:
    mode: str
    passed: bool
    profile_count: int
    included_profile_count: int
    clear_draft_count: int
    policy_correct_block_count: int
    excluded_profile_count: int
    remediation_required_count: int
    unexpected_gap_count: int
    no_weakening_violations: tuple[str, ...]
    rows: tuple[E2EProfileAcceptance, ...]
    notes: tuple[str, ...]

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.e2e_acceptance_report.v1",
            "mode": self.mode,
            "passed": self.passed,
            "profile_count": self.profile_count,
            "included_profile_count": self.included_profile_count,
            "clear_draft_count": self.clear_draft_count,
            "policy_correct_block_count": self.policy_correct_block_count,
            "excluded_profile_count": self.excluded_profile_count,
            "remediation_required_count": self.remediation_required_count,
            "unexpected_gap_count": self.unexpected_gap_count,
            "no_weakening_violations": list(self.no_weakening_violations),
            "rows": [row.to_packet() for row in self.rows],
            "notes": list(self.notes),
            "no_weakening_invariants": list(NO_WEAKENING_INVARIANTS),
        }


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_gate_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        if value.strip() in {"", "-"}:
            return ()
        return tuple(part.strip() for part in value.split(",") if part.strip())
    if isinstance(value, Iterable):
        return tuple(str(part).strip() for part in value if str(part).strip())
    return ()


def _as_bool(value: Any, *, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off"}
    return bool(value)


def _profile_id(row: Mapping[str, Any]) -> str:
    return _clean(row.get("id") or row.get("profile_id") or row.get("name"))


def _failed_gates(row: Mapping[str, Any]) -> tuple[str, ...]:
    return _as_gate_tuple(row.get("x2_failed_gates") or row.get("failed_gates"))


def _is_clear(row: Mapping[str, Any]) -> bool:
    return _clean(row.get("exit_disposition") or row.get("disposition")) == EXIT_CLEAR_DRAFT


def _derived_class(row: Mapping[str, Any]) -> str:
    return _clean(row.get("derived_class") or row.get("recipient_class") or CLASS_UNKNOWN)


def _has_policy_correct_blocker(row: Mapping[str, Any]) -> tuple[bool, str]:
    gates = set(_failed_gates(row))
    if GATE_ROLE_OWNERSHIP_FIT in gates:
        return True, "role_ownership_or_region_fit_block"
    if GATE_RECIPIENT_CLASS in gates:
        return True, "recipient_class_not_derived_block"
    if _derived_class(row) == CLASS_UNKNOWN:
        return True, "unknown_recipient_class_block"
    return False, "no_policy_correct_blocker"


def _no_weakening_violations(row: Mapping[str, Any]) -> tuple[str, ...]:
    violations: list[str] = []
    if not _is_clear(row):
        return ()

    profile_id = _profile_id(row)
    gates = set(_failed_gates(row))
    for gate_id in NO_WEAKENING_REQUIRED_GATE_IDS:
        if gate_id in gates:
            violations.append(f"{profile_id}:{gate_id}:clear_draft_despite_required_gate_failure")
    if _derived_class(row) == CLASS_UNKNOWN:
        violations.append(f"{profile_id}:UNKNOWN:clear_draft_despite_unknown_recipient_class")
    if _as_bool(row.get("sc_escalated_to_compensate_missing_evidence"), default=False):
        violations.append(f"{profile_id}:SC:sc_escalated_to_compensate_missing_c0_evidence")
    if _as_bool(row.get("x1d_overrode_x2_or_c0"), default=False):
        violations.append(f"{profile_id}:X1D:x1d_overrode_x2_or_c0")
    return tuple(violations)


def _strict_row_acceptance(row: Mapping[str, Any]) -> E2EProfileAcceptance:
    failed_gates = _failed_gates(row)
    if _is_clear(row):
        status = ROW_ACCEPTED_CLEAR
        reason = "strict_target_fit_clear_draft"
    else:
        correct_block, reason = _has_policy_correct_blocker(row)
        status = ROW_POLICY_CORRECT_BLOCK if correct_block else ROW_UNEXPECTED_GAP
    return E2EProfileAcceptance(
        profile_id=_profile_id(row),
        disposition=_clean(row.get("exit_disposition") or row.get("disposition")),
        derived_class=_derived_class(row),
        status=status,
        reason=reason,
        failed_gates=failed_gates,
    )


def _all_clear_row_acceptance(row: Mapping[str, Any]) -> E2EProfileAcceptance:
    failed_gates = _failed_gates(row)
    included = _as_bool(row.get("included_in_all_clear"), default=True)
    if not included:
        return E2EProfileAcceptance(
            profile_id=_profile_id(row),
            disposition=_clean(row.get("exit_disposition") or row.get("disposition")),
            derived_class=_derived_class(row),
            status=ROW_EXCLUDED_FROM_ALL_CLEAR,
            reason="profile_excluded_from_all_clear_eligible_matrix",
            failed_gates=failed_gates,
            included_in_mode=False,
        )
    if _is_clear(row):
        return E2EProfileAcceptance(
            profile_id=_profile_id(row),
            disposition=EXIT_CLEAR_DRAFT,
            derived_class=_derived_class(row),
            status=ROW_ACCEPTED_CLEAR,
            reason="all_clear_included_profile_clear_draft",
            failed_gates=failed_gates,
        )

    eligibility = _clean(row.get("target_eligibility"))
    alternate_mode = _clean(row.get("alternate_message_mode"))
    reason = "included_profile_did_not_clear_exit"
    if eligibility == TARGET_NOT_TARGETABLE:
        reason = "target_not_targetable_must_be_excluded_or_replaced"
    elif eligibility == TARGET_C0_EVIDENCE_REQUIRED:
        reason = "c0_evidence_required_before_all_clear"
    elif eligibility == TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE and alternate_mode:
        reason = "alternate_message_mode_declared_but_not_clear"

    return E2EProfileAcceptance(
        profile_id=_profile_id(row),
        disposition=_clean(row.get("exit_disposition") or row.get("disposition")),
        derived_class=_derived_class(row),
        status=ROW_ALL_CLEAR_REMEDIATION_REQUIRED,
        reason=reason,
        failed_gates=failed_gates,
    )


def evaluate_e2e_acceptance(
    rows: Iterable[Mapping[str, Any]],
    *,
    mode: str,
    expected_profile_count: int | None = None,
    expected_clear_draft_count: int | None = None,
    expected_policy_correct_block_count: int | None = None,
) -> E2EAcceptanceReport:
    """Evaluate E2E rows under an explicit apps_lic acceptance mode."""
    if mode not in ACCEPTANCE_MODES:
        raise ValueError(f"unknown apps_lic acceptance mode: {mode}")

    materialized_rows = tuple(rows)
    if mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT:
        accepted_rows = tuple(_strict_row_acceptance(row) for row in materialized_rows)
        notes = (
            "strict_target_fit accepts clear drafts plus policy-correct no-send blocks.",
            "Current AIG 30 baseline should remain 24 clear drafts and 6 correct blocks unless evidence changes.",
        )
    else:
        accepted_rows = tuple(_all_clear_row_acceptance(row) for row in materialized_rows)
        notes = (
            "all_clear_eligible requires every included profile to clear Exit.",
            "Non-targetable, stale, or weak-evidence profiles must be excluded, enriched, or rerouted with an explicit alternate message mode.",
        )

    no_weakening = tuple(
        violation
        for row in materialized_rows
        for violation in _no_weakening_violations(row)
    )
    clear_count = sum(1 for row in accepted_rows if row.status == ROW_ACCEPTED_CLEAR)
    block_count = sum(1 for row in accepted_rows if row.status == ROW_POLICY_CORRECT_BLOCK)
    excluded_count = sum(1 for row in accepted_rows if row.status == ROW_EXCLUDED_FROM_ALL_CLEAR)
    remediation_count = sum(1 for row in accepted_rows if row.status == ROW_ALL_CLEAR_REMEDIATION_REQUIRED)
    unexpected_count = sum(1 for row in accepted_rows if row.status == ROW_UNEXPECTED_GAP)
    included_count = sum(1 for row in accepted_rows if row.included_in_mode)

    count_mismatches: list[str] = []
    if expected_profile_count is not None and len(materialized_rows) != expected_profile_count:
        count_mismatches.append("profile_count_mismatch")
    if expected_clear_draft_count is not None and clear_count != expected_clear_draft_count:
        count_mismatches.append("clear_draft_count_mismatch")
    if expected_policy_correct_block_count is not None and block_count != expected_policy_correct_block_count:
        count_mismatches.append("policy_correct_block_count_mismatch")

    if mode == ACCEPTANCE_MODE_STRICT_TARGET_FIT:
        passed = (
            not no_weakening
            and not unexpected_count
            and not remediation_count
            and not count_mismatches
        )
    else:
        passed = (
            not no_weakening
            and included_count > 0
            and remediation_count == 0
            and unexpected_count == 0
            and clear_count == included_count
            and not count_mismatches
        )

    if count_mismatches:
        notes = (*notes, "count_mismatches:" + ",".join(count_mismatches))
    if no_weakening:
        notes = (*notes, "no_weakening_violation_detected")

    return E2EAcceptanceReport(
        mode=mode,
        passed=passed,
        profile_count=len(materialized_rows),
        included_profile_count=included_count,
        clear_draft_count=clear_count,
        policy_correct_block_count=block_count,
        excluded_profile_count=excluded_count,
        remediation_required_count=remediation_count,
        unexpected_gap_count=unexpected_count,
        no_weakening_violations=no_weakening,
        rows=accepted_rows,
        notes=notes,
    )


__all__ = [
    "ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE",
    "ACCEPTANCE_MODE_STRICT_TARGET_FIT",
    "ACCEPTANCE_MODES",
    "E2EAcceptanceReport",
    "E2EProfileAcceptance",
    "NO_WEAKENING_INVARIANTS",
    "NO_WEAKENING_REQUIRED_GATE_IDS",
    "ROW_ACCEPTED_CLEAR",
    "ROW_ALL_CLEAR_REMEDIATION_REQUIRED",
    "ROW_EXCLUDED_FROM_ALL_CLEAR",
    "ROW_POLICY_CORRECT_BLOCK",
    "ROW_UNEXPECTED_GAP",
    "TARGET_C0_EVIDENCE_REQUIRED",
    "TARGET_ELIGIBLE",
    "TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE",
    "TARGET_NOT_TARGETABLE",
    "evaluate_e2e_acceptance",
]
