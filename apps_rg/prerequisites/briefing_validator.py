"""apps_rg prerequisite gate — historical research briefing validator."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

__all__ = [
    "BriefingValidationResult",
    "BriefingCheck",
    "AppsResearchHandoffValidation",
    "HistoricalBriefingValidator",
    "find_apps_research_envelope_for_briefing",
    "validate_apps_research_handoff",
    "check_briefing_prerequisite",
]

_REQUIRES_RESEARCH_STATUSES = frozenset({
    "missing",
    "stale",
    "incomplete",
    "scope_mismatch",
})


class BriefingValidationResult(str, Enum):
    """Possible outcomes of briefing prerequisite validation."""

    VALID = "valid"
    MISSING = "missing"
    STALE = "stale"
    POLICY_MISMATCH = "policy_mismatch"
    BLUEPRINT_MISMATCH = "blueprint_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    INCOMPLETE = "incomplete"


@dataclass
class BriefingCheck:
    """Result of a briefing prerequisite check."""

    result: BriefingValidationResult
    briefing: Optional[dict[str, Any]]
    reason: str = ""
    freshness_hours: Optional[float] = None

    @property
    def is_valid(self) -> bool:
        return self.result == BriefingValidationResult.VALID

    @property
    def requires_apps_research(self) -> bool:
        return self.result.value in _REQUIRES_RESEARCH_STATUSES


@dataclass(frozen=True)
class AppsResearchHandoffValidation:
    """Validation result for an apps_research-produced apps_rg briefing."""

    observed: bool
    valid: bool
    reason: str
    envelope_path: str = ""
    envelope: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None

    def to_receipt(self) -> dict[str, Any]:
        if self.receipt is not None:
            return dict(self.receipt)
        return {
            "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v1",
            "observed": self.observed,
            "valid": self.valid,
            "reason": self.reason,
            "envelope_path": self.envelope_path,
        }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _read_text_ref(ref: str) -> tuple[str, str]:
    path = Path(str(ref or "").strip())
    if path.is_file():
        return path.read_text(encoding="utf-8").strip(), str(path.resolve())
    return str(ref or "").strip(), "inline:text"


def find_apps_research_envelope_for_briefing(brief_ref: str) -> Path | None:
    """Return a local apps_research handoff sidecar path when present."""
    ref = str(brief_ref or "").strip()
    if not ref or ref.startswith(("http://", "https://")):
        return None
    path = Path(ref)
    if not path.is_file():
        return None
    candidates = (
        path.parent / "apps_research_briefing_envelope.json",
        path.with_suffix(path.suffix + ".apps_research_envelope.json"),
        path.with_suffix(".envelope.json"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def validate_apps_research_handoff(
    *,
    brief_ref: str,
    jd_ref: str = "",
    now: datetime | None = None,
    require_observed: bool = False,
    require_x1_x3_authorization: bool = False,
) -> AppsResearchHandoffValidation:
    """Fail-closed validator for apps_research handoff envelopes.

    Absence of a sidecar is not a failure because ordinary user-authored
    ``--manual-brief`` files remain supported. Once an apps_research sidecar
    is present, it becomes authoritative for freshness, dry-run/stub status,
    handoff eligibility, and digest coherence.
    """
    envelope_path = find_apps_research_envelope_for_briefing(brief_ref)
    if envelope_path is None:
        valid = not require_observed
        return AppsResearchHandoffValidation(
            observed=False,
            valid=valid,
            reason=(
                "missing_apps_research_envelope"
                if require_observed
                else "no_apps_research_envelope_present"
            ),
        )

    failures: list[str] = []
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return AppsResearchHandoffValidation(
            observed=True,
            valid=False,
            reason=f"unreadable_envelope:{type(exc).__name__}",
            envelope_path=str(envelope_path),
        )
    if not isinstance(envelope, dict):
        envelope = {}
        failures.append("envelope_not_object")

    if envelope.get("schema_version") != "apps_research.apps_rg_briefing_envelope.v1":
        failures.append("unsupported_envelope_schema")
    if envelope.get("producer_app") != "apps_research":
        failures.append("producer_app_mismatch")
    if envelope.get("consumer_app") != "apps_rg":
        failures.append("consumer_app_mismatch")
    if bool(envelope.get("dry_run")):
        failures.append("dry_run_envelope")
    if bool(envelope.get("stub_detected")):
        failures.append("stub_detected")
    if bool(envelope.get("is_stale")):
        failures.append("stale_envelope")
    if not bool(envelope.get("handoff_eligible")):
        failures.append("handoff_not_eligible")

    generated_at = _parse_timestamp(envelope.get("generated_at_utc"))
    expires_at = _parse_timestamp(envelope.get("expires_at_utc"))
    observed_now = now or datetime.now(timezone.utc)
    if generated_at is None:
        failures.append("missing_generated_at_utc")
    if expires_at is None:
        failures.append("missing_expires_at_utc")
    elif observed_now > expires_at:
        failures.append("expired_envelope")

    try:
        brief_text, brief_source = _read_text_ref(brief_ref)
    except OSError as exc:
        brief_text, brief_source = "", str(brief_ref)
        failures.append(f"brief_unreadable:{type(exc).__name__}")
    brief_sha = _sha256_text(brief_text) if brief_text else ""
    expected_brief_sha = str(envelope.get("brief_sha256") or "").strip()
    if not expected_brief_sha:
        failures.append("missing_brief_sha256")
    elif brief_sha != expected_brief_sha:
        failures.append("brief_sha256_mismatch")

    jd_sha = ""
    if jd_ref:
        try:
            jd_text, _jd_source = _read_text_ref(jd_ref)
        except OSError as exc:
            jd_text = ""
            failures.append(f"jd_unreadable:{type(exc).__name__}")
        jd_sha = _sha256_text(jd_text) if jd_text else ""
        expected_jd_sha = str(envelope.get("jd_sha256") or "").strip()
        if not expected_jd_sha:
            failures.append("missing_jd_sha256")
        elif jd_sha != expected_jd_sha:
            failures.append("jd_sha256_mismatch")

    if not str(envelope.get("target_company") or "").strip():
        failures.append("missing_target_company")
    if not str(envelope.get("target_role") or "").strip():
        failures.append("missing_target_role")

    authorization = envelope.get("apps_research_x1_x3_authorization")
    if require_x1_x3_authorization:
        if not isinstance(authorization, dict):
            failures.append("missing_apps_research_x1_x3_authorization")
        else:
            if (
                authorization.get("schema_version")
                != "apps_research.apps_rg_handoff_x1_x3_authorization.v1"
            ):
                failures.append("unsupported_x1_x3_authorization_schema")
            if str(authorization.get("run_id") or "") != str(envelope.get("run_id") or ""):
                failures.append("x1_x3_run_id_mismatch")
            if str(authorization.get("brief_sha256") or "") != expected_brief_sha:
                failures.append("x1_x3_brief_sha256_mismatch")
            envelope_jd_sha = str(envelope.get("jd_sha256") or "").strip()
            if envelope_jd_sha and str(authorization.get("jd_sha256") or "") != envelope_jd_sha:
                failures.append("x1_x3_jd_sha256_mismatch")
            x1 = authorization.get("x1")
            x2 = authorization.get("x2")
            x3 = authorization.get("x3")
            if not isinstance(x1, dict) or x1.get("status") != "PASS":
                failures.append("x1_not_pass")
            if not isinstance(x2, dict) or x2.get("status") != "PASS":
                failures.append("x2_not_pass")
            if not isinstance(x3, dict) or x3.get("status") != "PASS":
                failures.append("x3_not_pass")
            else:
                disposition = str(x3.get("disposition") or "").strip()
                if disposition not in {"ALLOW", "X3_ALLOW", "X3D_ALLOW_FINISH"}:
                    failures.append("x3_disposition_not_allow")

    receipt = {
        "schema_version": "apps_rg.apps_research_handoff_validation_receipt.v1",
        "observed": True,
        "valid": not failures,
        "reason": "ok" if not failures else ";".join(failures),
        "envelope_path": str(envelope_path),
        "brief_ref": str(brief_ref),
        "brief_source": brief_source,
        "brief_sha256": brief_sha,
        "envelope_brief_sha256": expected_brief_sha,
        "jd_sha256": jd_sha,
        "envelope_jd_sha256": str(envelope.get("jd_sha256") or "").strip(),
        "require_observed": require_observed,
        "require_x1_x3_authorization": require_x1_x3_authorization,
        "x1_x3_authorization_observed": isinstance(authorization, dict),
        "checked_at_utc": observed_now.isoformat(),
    }
    return AppsResearchHandoffValidation(
        observed=True,
        valid=not failures,
        reason=str(receipt["reason"]),
        envelope_path=str(envelope_path),
        envelope=envelope,
        receipt=receipt,
    )


class HistoricalBriefingValidator:
    """Validates that a company research briefing meets prerequisite policy.

    Parameters
    ----------
    max_freshness_hours:
        Briefings older than this (in hours) are considered stale.
    required_sections:
        Section keys that must be present in a non-stale briefing.
    """

    DEFAULT_MAX_FRESHNESS_HOURS: float = 168.0  # 7 days
    DEFAULT_REQUIRED_SECTIONS: frozenset[str] = frozenset({
        "company_overview",
        "role_context",
    })

    def __init__(
        self,
        *,
        max_freshness_hours: float = DEFAULT_MAX_FRESHNESS_HOURS,
        required_sections: Optional[frozenset[str]] = None,
        policy_hash: str = "",
    ) -> None:
        self.max_freshness_hours = max_freshness_hours
        self.required_sections = required_sections or self.DEFAULT_REQUIRED_SECTIONS
        self.policy_hash = policy_hash

    def validate(
        self,
        briefing: Optional[dict[str, Any]],
        *,
        target_company: str = "",
        target_role: str = "",
    ) -> BriefingCheck:
        """Validate a briefing dict and return a BriefingCheck."""
        if briefing is None:
            return BriefingCheck(
                result=BriefingValidationResult.MISSING,
                briefing=None,
                reason="No briefing provided",
            )

        # Policy hash check
        if self.policy_hash:
            bp_hash = briefing.get("policy_hash", "")
            if bp_hash and bp_hash != self.policy_hash:
                return BriefingCheck(
                    result=BriefingValidationResult.POLICY_MISMATCH,
                    briefing=briefing,
                    reason=f"Policy hash mismatch: expected {self.policy_hash!r}, got {bp_hash!r}",
                )

        # Blueprint/company mismatch
        if target_company:
            brief_company = briefing.get("company", "") or briefing.get("target_company", "")
            if brief_company and brief_company.lower() != target_company.lower():
                return BriefingCheck(
                    result=BriefingValidationResult.BLUEPRINT_MISMATCH,
                    briefing=briefing,
                    reason=f"Briefing company {brief_company!r} != target {target_company!r}",
                )

        # Freshness check
        import datetime
        generated_at = briefing.get("generated_at") or briefing.get("created_at")
        freshness_hours: Optional[float] = None
        if generated_at:
            try:
                if isinstance(generated_at, str):
                    ts = datetime.datetime.fromisoformat(
                        generated_at.replace("Z", "+00:00")
                    )
                else:
                    ts = generated_at
                now = datetime.datetime.now(datetime.timezone.utc)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=datetime.timezone.utc)
                age_hours = (now - ts).total_seconds() / 3600
                freshness_hours = age_hours
                if age_hours > self.max_freshness_hours:
                    return BriefingCheck(
                        result=BriefingValidationResult.STALE,
                        briefing=briefing,
                        reason=f"Briefing is {age_hours:.1f}h old (limit: {self.max_freshness_hours}h)",
                        freshness_hours=age_hours,
                    )
            except Exception:
                pass

        # Required sections
        missing = self.required_sections - set(briefing.keys())
        if missing:
            return BriefingCheck(
                result=BriefingValidationResult.INCOMPLETE,
                briefing=briefing,
                reason=f"Missing required sections: {sorted(missing)}",
                freshness_hours=freshness_hours,
            )

        return BriefingCheck(
            result=BriefingValidationResult.VALID,
            briefing=briefing,
            reason="Briefing is valid",
            freshness_hours=freshness_hours,
        )


def check_briefing_prerequisite(
    briefing: Optional[dict[str, Any]],
    *,
    target_company: str = "",
    target_role: str = "",
    max_freshness_hours: float = HistoricalBriefingValidator.DEFAULT_MAX_FRESHNESS_HOURS,
) -> BriefingCheck:
    """Convenience wrapper — validates a briefing with default policy."""
    validator = HistoricalBriefingValidator(max_freshness_hours=max_freshness_hours)
    return validator.validate(
        briefing,
        target_company=target_company,
        target_role=target_role,
    )
