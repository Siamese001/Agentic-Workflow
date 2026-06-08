"""W7 blocked artifact UX for apps_lic.

This module turns blocked Exit rows into action-oriented artifacts while keeping
blocked draft text out of product-facing reports by default.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


EXIT_CLEAR_DRAFT = "clear_draft"

DO_NOT_SEND_WATERMARK = "DO_NOT_SEND"

PRIMARY_RECIPIENT_CLASS_NOT_DERIVED = "recipient_class_not_derived"
PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH = "role_ownership_region_mismatch"
PRIMARY_MESSAGE_REQUIREMENTS_NOT_PASSED = "message_requirements_not_passed"
PRIMARY_SENDER_PROOF_NOT_READY = "sender_proof_graph_not_ready"
PRIMARY_UNSUPPORTED_CLAIM = "unsupported_claim"
PRIMARY_SCHEMA_NOT_READY = "schema_not_ready"
PRIMARY_BLOCKED_BY_EXIT = "blocked_by_exit"

GATE_RECIPIENT_CLASS = "recipient_class_present_and_derived_gate"
GATE_ROLE_OWNERSHIP_FIT = "role_ownership_fit_gate"
GATE_UNSUPPORTED_CLAIM = "unsupported_claim_gate"
GATE_SCHEMA = "schema_gate"


@dataclass(frozen=True)
class BlockedProfileUX:
    primary_blocker: str
    user_action_required: str
    safe_alternative: str
    diagnostics: Mapping[str, Any]
    product_draft_exposed: bool
    blocked_draft_ref: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.blocked_profile_ux.v1",
            "primary_blocker": self.primary_blocker,
            "user_action_required": self.user_action_required,
            "safe_alternative": self.safe_alternative,
            "diagnostics": dict(self.diagnostics),
            "product_draft_exposed": self.product_draft_exposed,
            "blocked_draft_ref": self.blocked_draft_ref,
        }


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _as_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (_clean(value),) if _clean(value) else ()
    if isinstance(value, Iterable):
        return tuple(_clean(item) for item in value if _clean(item))
    return ()


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _all_blocking_signals(row: Mapping[str, Any]) -> tuple[str, ...]:
    signals: list[str] = []
    signals.extend(_as_tuple(row.get("request_blocking_reasons")))
    signals.extend(_as_tuple(row.get("x2_failed_gates")))
    signals.extend(_as_tuple(row.get("message_missing_fields")))
    signals.extend(_as_tuple(row.get("class_reason_codes")))
    if _clean(row.get("class_status")):
        signals.append(_clean(row.get("class_status")))
    return tuple(dict.fromkeys(signals))


def _primary_blocker(row: Mapping[str, Any]) -> str:
    signals = set(_all_blocking_signals(row))
    derived_class = _clean(row.get("derived_class"))
    class_status = _clean(row.get("class_status"))
    if (
        derived_class == "UNKNOWN"
        or GATE_RECIPIENT_CLASS in signals
        or PRIMARY_RECIPIENT_CLASS_NOT_DERIVED in signals
        or "RECIPIENT_CLASS_NOT_DERIVED" in signals
        or class_status == "RECIPIENT_CLASS_LOW_CONFIDENCE"
    ):
        return PRIMARY_RECIPIENT_CLASS_NOT_DERIVED
    if GATE_ROLE_OWNERSHIP_FIT in signals:
        return PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH
    if PRIMARY_MESSAGE_REQUIREMENTS_NOT_PASSED in signals:
        return PRIMARY_MESSAGE_REQUIREMENTS_NOT_PASSED
    if PRIMARY_SENDER_PROOF_NOT_READY in signals:
        return PRIMARY_SENDER_PROOF_NOT_READY
    if GATE_UNSUPPORTED_CLAIM in signals:
        return PRIMARY_UNSUPPORTED_CLAIM
    if GATE_SCHEMA in signals:
        return PRIMARY_SCHEMA_NOT_READY
    return PRIMARY_BLOCKED_BY_EXIT


_ACTION_AND_ALTERNATIVE: dict[str, tuple[str, str]] = {
    PRIMARY_RECIPIENT_CLASS_NOT_DERIVED: (
        "Provide or ingest stronger public profile evidence that shows the contact's role ownership before generating a draft.",
        "Do not send a draft. Use C0 enrichment or choose a contact with clear recruiter, TA, hiring-owner, or executive signals.",
    ),
    PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH: (
        "Use a contact who owns the target requisition/region, or supply evidence that this contact owns the specific AIG JD.",
        "Do not send the role-specific draft. Use a non-JD networking note only after explicit alternate-scope approval.",
    ),
    PRIMARY_MESSAGE_REQUIREMENTS_NOT_PASSED: (
        "Supply the missing mission-critical inputs for this message type before drafting.",
        "Keep the profile blocked until required inputs are present.",
    ),
    PRIMARY_SENDER_PROOF_NOT_READY: (
        "Refresh C0.3 sender-proof selection so every sender claim is approved and scoped.",
        "Use a lower-claim note only if policy explicitly permits it.",
    ),
    PRIMARY_UNSUPPORTED_CLAIM: (
        "Remove or re-ground unsupported claims against the C0.3 proof packet.",
        "Generate a low-claim draft only after unsupported claims are removed.",
    ),
    PRIMARY_SCHEMA_NOT_READY: (
        "Repair upstream request/candidate schema readiness before exposing any draft.",
        "Keep the profile blocked; do not copy any generated text.",
    ),
    PRIMARY_BLOCKED_BY_EXIT: (
        "Review the diagnostics and fix the first upstream blocker before drafting.",
        "No safe send action is available until Exit clears the profile.",
    ),
}


def derive_blocked_profile_ux(row: Mapping[str, Any]) -> BlockedProfileUX:
    """Return action-oriented blocked UX for one blocked profile row."""
    primary = _primary_blocker(row)
    action, alternative = _ACTION_AND_ALTERNATIVE[primary]
    all_signals = _all_blocking_signals(row)
    collapsed = tuple(signal for signal in all_signals if signal != primary)
    draft_text = _clean(row.get("draft_text"))
    diagnostics = {
        "collapsed_downstream_failures": list(collapsed),
        "request_blocking_reasons": list(_as_tuple(row.get("request_blocking_reasons"))),
        "x2_failed_gates": list(_as_tuple(row.get("x2_failed_gates"))),
        "message_missing_fields": list(_as_tuple(row.get("message_missing_fields"))),
        "class_status": _clean(row.get("class_status")),
        "class_reason_codes": list(_as_tuple(row.get("class_reason_codes"))),
        "draft_present_in_internal_appendix": bool(draft_text),
    }
    return BlockedProfileUX(
        primary_blocker=primary,
        user_action_required=action,
        safe_alternative=alternative,
        diagnostics=diagnostics,
        product_draft_exposed=False,
        blocked_draft_ref=_digest(draft_text) if draft_text else "",
    )


def apply_blocked_artifact_ux(rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Enrich blocked rows with W7 user-facing root cause fields."""
    enriched: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        if _clean(next_row.get("exit_disposition")) != EXIT_CLEAR_DRAFT:
            ux = derive_blocked_profile_ux(next_row)
            packet = ux.to_packet()
            next_row["blocked_artifact_ux"] = packet
            next_row["primary_blocker"] = ux.primary_blocker
            next_row["user_action_required"] = ux.user_action_required
            next_row["safe_alternative"] = ux.safe_alternative
            next_row["diagnostics"] = dict(ux.diagnostics)
            next_row["product_draft_exposed"] = False
            next_row["blocked_draft_ref"] = ux.blocked_draft_ref
        enriched.append(next_row)
    return tuple(enriched)


def build_blocked_ux_summary(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    blocked_rows = [
        row for row in rows if _clean(row.get("exit_disposition")) != EXIT_CLEAR_DRAFT
    ]
    counts: dict[str, int] = {}
    blocked_with_internal_draft = 0
    product_exposed = 0
    for row in blocked_rows:
        primary = _clean(row.get("primary_blocker")) or PRIMARY_BLOCKED_BY_EXIT
        counts[primary] = counts.get(primary, 0) + 1
        if _clean(row.get("draft_text")):
            blocked_with_internal_draft += 1
        if bool(row.get("product_draft_exposed")):
            product_exposed += 1
    return {
        "schema_version": "apps_lic.blocked_ux_summary.v1",
        "blocked_profile_count": len(blocked_rows),
        "primary_blocker_counts": counts,
        "blocked_profiles_with_internal_draft_count": blocked_with_internal_draft,
        "product_facing_blocked_draft_exposure_count": product_exposed,
        "product_facing_blocked_drafts_suppressed": product_exposed == 0,
        "internal_appendix_watermark": DO_NOT_SEND_WATERMARK,
    }


def blocked_profile_report_lines(row: Mapping[str, Any]) -> tuple[str, ...]:
    diagnostics = dict(row.get("diagnostics") or {})
    collapsed = ", ".join(diagnostics.get("collapsed_downstream_failures") or ()) or "none"
    return (
        f"Primary blocker: `{_clean(row.get('primary_blocker'))}`",
        f"User action required: {_clean(row.get('user_action_required'))}",
        f"Safe alternative: {_clean(row.get('safe_alternative'))}",
        f"Diagnostics collapsed: `{collapsed}`",
        "No draft shown: blocked draft text is suppressed in product-facing artifacts.",
    )


def internal_blocked_draft_appendix(rows: Iterable[Mapping[str, Any]], *, mode: str, x1d_mode: str) -> str:
    """Render the internal blocked draft appendix with explicit watermarking."""
    lines = [
        f"# Internal Blocked Draft Appendix - {mode} - {x1d_mode}",
        "",
        f"{DO_NOT_SEND_WATERMARK}: Internal diagnostic artifact only. Blocked draft text below must not be sent or copied into outreach.",
        "",
    ]
    index = 1
    for row in rows:
        if _clean(row.get("exit_disposition")) == EXIT_CLEAR_DRAFT:
            continue
        draft = _clean(row.get("draft_text"))
        if not draft:
            continue
        lines.extend(
            [
                f"## {index}. {row.get('name')} - {row.get('derived_class')}",
                "",
                f"{DO_NOT_SEND_WATERMARK}: This blocked draft failed `{_clean(row.get('primary_blocker'))}` and is shown only for internal diagnosis.",
                "",
                f"Profile ID: `{row.get('id')}`",
                f"Blocked draft ref: `{row.get('blocked_draft_ref')}`",
                "",
                draft,
                "",
            ]
        )
        index += 1
    if index == 1:
        lines.append("No blocked draft text was present in this run.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "DO_NOT_SEND_WATERMARK",
    "PRIMARY_BLOCKED_BY_EXIT",
    "PRIMARY_MESSAGE_REQUIREMENTS_NOT_PASSED",
    "PRIMARY_RECIPIENT_CLASS_NOT_DERIVED",
    "PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH",
    "PRIMARY_SCHEMA_NOT_READY",
    "PRIMARY_SENDER_PROOF_NOT_READY",
    "PRIMARY_UNSUPPORTED_CLAIM",
    "BlockedProfileUX",
    "apply_blocked_artifact_ux",
    "blocked_profile_report_lines",
    "build_blocked_ux_summary",
    "derive_blocked_profile_ux",
    "internal_blocked_draft_appendix",
]
