"""Validate canonical apps_research Exit proof before apps_rg U0 accepts a brief."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class CanonicalAppsResearchExitValidation:
    observed: bool
    valid: bool
    reason: str
    envelope_path: str = ""
    exit_disposition_path: str = ""
    brief_sha256: str = ""
    jd_sha256: str = ""
    exit_disposition_receipt_digest: str = ""
    x3_code: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_rg.canonical_apps_research_exit_validation.v1",
            "observed": self.observed,
            "valid": self.valid,
            "reason": self.reason,
            "envelope_path": self.envelope_path,
            "exit_disposition_path": self.exit_disposition_path,
            "brief_sha256": self.brief_sha256,
            "jd_sha256": self.jd_sha256,
            "exit_disposition_receipt_digest": self.exit_disposition_receipt_digest,
            "x3_code": self.x3_code,
        }


def _read_text_ref(ref: str) -> tuple[str, Path | None]:
    raw = str(ref or "").strip()
    path = Path(raw)
    try:
        is_file = path.is_file()
    except OSError:
        is_file = False
    if is_file:
        return path.read_text(encoding="utf-8").strip(), path.resolve()
    return raw, None


def validate_canonical_apps_research_exit(
    *,
    brief_ref: str,
    jd_ref: str = "",
    require_observed: bool = True,
) -> CanonicalAppsResearchExitValidation:
    """Fail closed unless an adjacent committed v2 bundle proves exact Exit."""

    from apps_rg.prerequisites.briefing_validator import (
        find_apps_research_handoff_v2_for_briefing,
        find_legacy_apps_research_envelope_for_briefing,
        validate_apps_research_handoff,
    )

    handoff_v2 = find_apps_research_handoff_v2_for_briefing(brief_ref)
    if handoff_v2 is not None:
        validation = validate_apps_research_handoff(
            brief_ref=brief_ref,
            jd_ref=jd_ref,
            require_observed=True,
            require_x1_x3_authorization=True,
            require_canonical_exit=True,
        )
        receipt = dict(validation.receipt or {})
        identity = dict(receipt.get("identity") or {})
        exit_path = handoff_v2.parent / "exit_disposition_receipt.json"
        exit_digest = ""
        x3_code = ""
        if exit_path.is_file():
            try:
                persisted = json.loads(exit_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                persisted = {}
            exit_digest = str(persisted.get("deterministic_digest") or "")
            x3_code = str(persisted.get("x3_code") or "")
        return CanonicalAppsResearchExitValidation(
            observed=validation.observed,
            valid=validation.valid,
            reason=validation.reason,
            envelope_path=str(handoff_v2),
            exit_disposition_path=str(exit_path) if exit_path.is_file() else "",
            brief_sha256=str(identity.get("brief_sha256") or ""),
            jd_sha256=str(identity.get("jd_sha256") or ""),
            exit_disposition_receipt_digest=exit_digest,
            x3_code=x3_code,
        )

    try:
        brief_text, _brief_path = _read_text_ref(brief_ref)
    except OSError as exc:
        return CanonicalAppsResearchExitValidation(
            observed=False,
            valid=False,
            reason=f"brief_unreadable:{type(exc).__name__}",
        )
    brief_sha = _sha256_text(brief_text) if brief_text else ""
    legacy_path = find_legacy_apps_research_envelope_for_briefing(brief_ref)
    if legacy_path is not None:
        return CanonicalAppsResearchExitValidation(
            observed=True,
            valid=False,
            reason="legacy_only_handoff_rejected",
            envelope_path=str(legacy_path),
            brief_sha256=brief_sha,
        )
    return CanonicalAppsResearchExitValidation(
        observed=False,
        valid=not require_observed,
        reason=(
            "missing_apps_research_handoff_v2"
            if require_observed
            else "no_apps_research_handoff_present"
        ),
        brief_sha256=brief_sha,
    )


__all__ = [
    "CanonicalAppsResearchExitValidation",
    "validate_canonical_apps_research_exit",
]
