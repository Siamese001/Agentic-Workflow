"""Exit/X3C and evidence authority checks for R1B durable promotion."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from apps_rg.cache.r1b_constants import R1B_UWG_TARGET_SURFACE

X3C_COMMIT_AUTHORITY = "X3C"
X3_DISPOSITION_ARTIFACT = "x3_disposition.json"
REASON_X3C_REQUIRED = "x3_commit_authority_required"
REASON_X3_MISSING = "x3_disposition_missing"
REASON_X3_MALFORMED = "x3_disposition_malformed"
PLACEHOLDER_EVIDENCE = frozenset(
    {"", "unknown", "UNKNOWN", "MIGRATION_UNKNOWN", "l5_packet:missing"}
)


@dataclass(frozen=True)
class R1BCommitAuthorityDecision:
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
    return str(value or "").strip().upper()


def assess_r1b_commit_authority(
    *, x3_code: Any, disposition_ref: str = X3_DISPOSITION_ARTIFACT
) -> R1BCommitAuthorityDecision:
    normalized = normalize_x3_code(x3_code)
    if normalized == X3C_COMMIT_AUTHORITY:
        return R1BCommitAuthorityDecision(True, normalized, "", disposition_ref)
    return R1BCommitAuthorityDecision(
        False,
        normalized,
        REASON_X3_MISSING if not normalized else REASON_X3C_REQUIRED,
        disposition_ref,
    )


def assess_r1b_commit_authority_from_run_dir(
    run_dir: Path | str,
) -> R1BCommitAuthorityDecision:
    path = Path(run_dir) / X3_DISPOSITION_ARTIFACT
    if not path.is_file():
        return R1BCommitAuthorityDecision(False, "", REASON_X3_MISSING, str(path))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, TypeError):
        return R1BCommitAuthorityDecision(False, "", REASON_X3_MALFORMED, str(path))
    if not isinstance(payload, dict):
        return R1BCommitAuthorityDecision(False, "", REASON_X3_MALFORMED, str(path))
    return assess_r1b_commit_authority(
        x3_code=payload.get("x3_code") or payload.get("disposition"),
        disposition_ref=str(path),
    )


def _parse_l5_refs(values: Iterable[Any]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        text = str(value or "").strip()
        if "=" not in text:
            continue
        key, raw = text.split("=", 1)
        parsed[key.strip()] = raw.strip()
    return parsed


def compute_r1b_commit_request_signature(
    *,
    commit_request_id: str,
    staged_diff_hash: str,
    clearance_proof_id: str,
    l5_packet_digest: str = "",
    l5_verification_digest: str = "",
) -> str:
    from agentic_core.L4_state.contracts.digests import compute_deterministic_digest

    return compute_deterministic_digest(
        {
            "commit_request_id": str(commit_request_id),
            "staged_diff_hash": str(staged_diff_hash),
            "clearance_proof_id": str(clearance_proof_id),
            "l5_packet_digest": str(l5_packet_digest),
            "l5_verification_digest": str(l5_verification_digest),
        }
    )


def validate_r1b_commit_request_evidence(
    commit_request: Any,
    *,
    registry_digests: Iterable[Any] | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return strict R1B failures not covered by generic UWG shape checks."""

    failed: list[str] = []
    reasons: list[str] = []
    l5 = _parse_l5_refs(
        tuple(getattr(commit_request, "l5_certification_refs", ()) or ())
    )
    packet_digest = l5.get("packet_digest", "")
    verification_digest = l5.get("verification_digest", "")
    expected_signature = compute_r1b_commit_request_signature(
        commit_request_id=str(getattr(commit_request, "commit_request_id", "") or ""),
        staged_diff_hash=str(getattr(commit_request, "staged_diff_hash", "") or ""),
        clearance_proof_id=str(
            getattr(commit_request, "clearance_proof_id", "") or ""
        ),
        l5_packet_digest=packet_digest,
        l5_verification_digest=verification_digest,
    )
    supplied_signature = str(
        getattr(commit_request, "commit_request_signature", "")
        or getattr(commit_request, "signature", "")
        or ""
    ).strip()
    if supplied_signature != expected_signature:
        failed.append("r1b_commit_request_signature")
        reasons.append("commit_request_signature_invalid")

    capability_ref = str(
        getattr(commit_request, "capability_token_ref", "") or ""
    ).strip()
    expected_capability_ref = (
        f"capability:apps_rg:r1b:{str(getattr(commit_request, 'run_id', '') or '')}"
    )
    if (
        capability_ref in PLACEHOLDER_EVIDENCE
        or capability_ref != expected_capability_ref
    ):
        failed.append("r1b_capability_token_ref")
        reasons.append("missing_or_invalid_capability_token_ref")

    clearance_ref = str(
        getattr(commit_request, "cleared_exit_review_packet_ref", "") or ""
    ).strip()
    clearance_proof_id = str(
        getattr(commit_request, "clearance_proof_id", "") or ""
    ).strip()
    if not clearance_ref or clearance_ref != clearance_proof_id:
        failed.append("r1b_clearance_proof_binding")
        reasons.append("clearance_proof_binding_mismatch")

    normalized_registry = tuple(
        str(item or "").strip()
        for item in (
            tuple(registry_digests)
            if registry_digests is not None
            else tuple(getattr(commit_request, "registry_digest_set", ()) or ())
        )
    )
    if not normalized_registry or any(
        item in PLACEHOLDER_EVIDENCE for item in normalized_registry
    ):
        failed.append("r1b_registry_digest_set")
        reasons.append("missing_or_placeholder_registry_digest_set")
    elif len(set(normalized_registry)) != len(normalized_registry):
        failed.append("r1b_registry_digest_set")
        reasons.append("duplicate_registry_digest")
    else:
        expected_registry = {
            f"registry:policy:{str(getattr(commit_request, 'policy_hash', '') or '')}",
            f"registry:blueprint:{str(getattr(commit_request, 'blueprint_hash', '') or '')}",
        }
        if set(normalized_registry) != expected_registry:
            failed.append("r1b_registry_digest_set")
            reasons.append("registry_digest_binding_mismatch")

    affected_surfaces = tuple(
        str(item or "")
        for item in tuple(
            getattr(commit_request, "affected_state_surfaces", ()) or ()
        )
    )
    if affected_surfaces != (R1B_UWG_TARGET_SURFACE,):
        failed.append("r1b_target_surface_allowlist")
        reasons.append("target_surface_not_allowlisted")

    l5_ref = str(getattr(commit_request, "l5_certification_ref", "") or "").strip()
    runtime_binding_digest = l5.get("runtime_binding_digest", "")
    if l5_ref in PLACEHOLDER_EVIDENCE or l5_ref != f"l5_packet:{packet_digest}":
        failed.append("r1b_l5_certification_ref")
        reasons.append("l5_certification_ref_invalid")
    expected_verification_digest = ""
    if (
        packet_digest not in PLACEHOLDER_EVIDENCE
        and runtime_binding_digest not in PLACEHOLDER_EVIDENCE
        and l5_ref not in PLACEHOLDER_EVIDENCE
    ):
        from apps_rg.runtime.l5.packet_builder import (
            compute_l5_packet_verification_digest,
        )

        expected_verification_digest = compute_l5_packet_verification_digest(
            request_id=str(getattr(commit_request, "request_id", "") or ""),
            run_id=str(getattr(commit_request, "run_id", "") or ""),
            trace_id=str(getattr(commit_request, "trace_root", "") or ""),
            packet_ref=l5_ref,
            packet_digest=packet_digest,
            status=l5.get("status", ""),
            runtime_binding_digest_value=runtime_binding_digest,
        )
    if (
        l5.get("verified", "").lower() != "true"
        or l5.get("status") != "L5_CERTIFIED"
        or packet_digest in PLACEHOLDER_EVIDENCE
        or runtime_binding_digest in PLACEHOLDER_EVIDENCE
        or verification_digest in PLACEHOLDER_EVIDENCE
        or verification_digest != expected_verification_digest
    ):
        failed.append("r1b_l5_certification_evidence")
        reasons.append("l5_certification_evidence_not_verified")

    return tuple(dict.fromkeys(failed)), tuple(dict.fromkeys(reasons))


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
