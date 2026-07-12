"""Exit/X3C authority checks for R1B durable cache promotion.

R1B may be reusable after an Exit finish decision, but durable cache mutation is
separate authority.  Only an explicit X3C disposition authorizes creation of a
CommitRequest for UWG.  X3_ALLOW/X3D/EXIT_OK remain finish outcomes and cannot
be interpreted as durable-write clearance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

X3C_COMMIT_AUTHORITY = "X3C"
X3_DISPOSITION_ARTIFACT = "x3_disposition.json"
REASON_X3C_REQUIRED = "x3_commit_authority_required"
REASON_X3_MISSING = "x3_disposition_missing"
REASON_X3_MALFORMED = "x3_disposition_malformed"
PLACEHOLDER_EVIDENCE: frozenset[str] = frozenset(
    {"", "unknown", "UNKNOWN", "MIGRATION_UNKNOWN"}
)


@dataclass(frozen=True)
class R1BCommitAuthorityDecision:
    """Fail-closed decision for the Exit-to-UWG R1B write boundary."""

    authorized: bool
    x3_code: str
    reason_code: str
    disposition_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorized": self.authorized,
            "x3_code": self.x3_code,
            "reason_code": self.reason_code,
            "disposition_ref": self.disposition_ref,
            "required_x3_code": X3C_COMMIT_AUTHORITY,
        }


def normalize_x3_code(value: Any) -> str:
    """Normalize an Exit disposition token without inventing aliases."""

    return str(value or "").strip().upper()


def assess_r1b_commit_authority(
    *,
    x3_code: Any,
    disposition_ref: str = X3_DISPOSITION_ARTIFACT,
) -> R1BCommitAuthorityDecision:
    """Authorize durable R1B promotion only for the literal X3C outcome."""

    normalized = normalize_x3_code(x3_code)
    if normalized == X3C_COMMIT_AUTHORITY:
        return R1BCommitAuthorityDecision(
            authorized=True,
            x3_code=normalized,
            reason_code="",
            disposition_ref=disposition_ref,
        )
    return R1BCommitAuthorityDecision(
        authorized=False,
        x3_code=normalized,
        reason_code=REASON_X3_MISSING if not normalized else REASON_X3C_REQUIRED,
        disposition_ref=disposition_ref,
    )


def assess_r1b_commit_authority_from_run_dir(run_dir: Path | str) -> R1BCommitAuthorityDecision:
    """Load ``x3_disposition.json`` and return an X3C-only authority decision."""

    root = Path(run_dir)
    path = root / X3_DISPOSITION_ARTIFACT
    if not path.is_file():
        return R1BCommitAuthorityDecision(
            authorized=False,
            x3_code="",
            reason_code=REASON_X3_MISSING,
            disposition_ref=str(path),
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, TypeError):
        return R1BCommitAuthorityDecision(
            authorized=False,
            x3_code="",
            reason_code=REASON_X3_MALFORMED,
            disposition_ref=str(path),
        )
    if not isinstance(payload, dict):
        return R1BCommitAuthorityDecision(
            authorized=False,
            x3_code="",
            reason_code=REASON_X3_MALFORMED,
            disposition_ref=str(path),
        )
    return assess_r1b_commit_authority(
        x3_code=payload.get("x3_code") or payload.get("disposition"),
        disposition_ref=str(path),
    )


def compute_r1b_commit_request_signature(
    *,
    commit_request_id: str,
    staged_diff_hash: str,
    clearance_proof_id: str,
) -> str:
    """Compute the deterministic R1B CommitRequest evidence signature."""

    from agentic_core.L4_state.contracts.digests import compute_deterministic_digest

    return compute_deterministic_digest(
        {
            "commit_request_id": str(commit_request_id),
            "staged_diff_hash": str(staged_diff_hash),
            "clearance_proof_id": str(clearance_proof_id),
        }
    )


def validate_r1b_commit_request_evidence(
    commit_request: Any,
    *,
    registry_digests: Iterable[Any] | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return additional strict rule failures and reason codes for R1B UWG admission."""

    failed: list[str] = []
    reasons: list[str] = []

    expected_signature = compute_r1b_commit_request_signature(
        commit_request_id=str(getattr(commit_request, "commit_request_id", "") or ""),
        staged_diff_hash=str(getattr(commit_request, "staged_diff_hash", "") or ""),
        clearance_proof_id=str(getattr(commit_request, "clearance_proof_id", "") or ""),
    )
    supplied_signature = str(
        getattr(commit_request, "commit_request_signature", "")
        or getattr(commit_request, "signature", "")
        or ""
    ).strip()
    if supplied_signature != expected_signature:
        failed.append("r1b_commit_request_signature")
        reasons.append("commit_request_signature_invalid")

    capability_ref = str(getattr(commit_request, "capability_token_ref", "") or "").strip()
    if capability_ref in PLACEHOLDER_EVIDENCE:
        failed.append("r1b_capability_token_ref")
        reasons.append("missing_or_placeholder_capability_token_ref")

    clearance_ref = str(
        getattr(commit_request, "cleared_exit_review_packet_ref", "") or ""
    ).strip()
    clearance_proof_id = str(getattr(commit_request, "clearance_proof_id", "") or "").strip()
    if not clearance_ref or clearance_ref != clearance_proof_id:
        failed.append("r1b_clearance_proof_binding")
        reasons.append("clearance_proof_binding_mismatch")

    raw_registry = (
        tuple(registry_digests)
        if registry_digests is not None
        else tuple(getattr(commit_request, "registry_digest_set", ()) or ())
    )
    normalized_registry = tuple(str(item or "").strip() for item in raw_registry)
    if not normalized_registry or any(item in PLACEHOLDER_EVIDENCE for item in normalized_registry):
        failed.append("r1b_registry_digest_set")
        reasons.append("missing_or_placeholder_registry_digest_set")
    elif len(set(normalized_registry)) != len(normalized_registry):
        failed.append("r1b_registry_digest_set")
        reasons.append("duplicate_registry_digest")

    return tuple(failed), tuple(reasons)


__all__ = [
    "PLACEHOLDER_EVIDENCE",
    "REASON_X3C_REQUIRED",
    "REASON_X3_MALFORMED",
    "REASON_X3_MISSING",
    "R1BCommitAuthorityDecision",
    "X3C_COMMIT_AUTHORITY",
    "X3_DISPOSITION_ARTIFACT",
    "assess_r1b_commit_authority",
    "assess_r1b_commit_authority_from_run_dir",
    "compute_r1b_commit_request_signature",
    "normalize_x3_code",
    "validate_r1b_commit_request_evidence",
]
