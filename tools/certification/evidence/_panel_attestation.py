"""Schema-v2 panel attestation writer for RTC-REQ-056.

Emits ``live_provider_attestation.json`` into the canonical panel
subdirectory:

    artifacts/certification/integrated_runtime/consensus_jury/
        live_provider_attestation.json

This attestation is the ONLY artifact that can certify RTC-REQ-056
at ACCEPTED. The legacy single-provider attestation (schema v1) at
the parent integrated_runtime/ directory is diagnostic-only and
cannot certify.

Per operator directive 2026-05-01 13:39 UTC-04:00.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.certification.safety.consensus_veto import JurorVerdict
from tools.certification.safety.rtc_req_056_panel import (
    ATTESTATION_SCHEMA_VERSION,
    CERTIFICATION_SCOPE,
    CONSENSUS_JURY_ARTIFACT_SUBDIR,
    CONTROL_SURFACE,
    JUDGE_MODE,
    PANEL_ATTESTATION_FILENAME,
    PURPOSE,
    QUORUM_RULE,
    REJECTED_PROVIDERS_FOR_CERT,
    REQUIRED_JURORS,
    REQUIRED_JUROR_COUNT,
    JurorSpec,
    is_registered_model,
)

__all__ = [
    "ATTESTATION_KIND",
    "build_panel_attestation",
    "panel_attestation_path",
    "write_panel_attestation",
]

ATTESTATION_KIND = "rtc_req_056_consensus_jury_panel"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, FileNotFoundError):
        return None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def panel_attestation_path(repo_root: Path) -> Path:
    return (
        Path(repo_root)
        / "artifacts"
        / "certification"
        / "integrated_runtime"
        / CONSENSUS_JURY_ARTIFACT_SUBDIR
        / PANEL_ATTESTATION_FILENAME
    )


def _find_registry_spec(family: str, provider: str) -> JurorSpec | None:
    """Return the registry JurorSpec matching (family, provider), or None."""
    for j in REQUIRED_JURORS:
        if (
            j.provider_family.lower() == (family or "").lower()
            and j.provider.lower() == (provider or "").lower()
        ):
            return j
    return None


def _classify_provider_match(
    observed: JurorVerdict, target: JurorSpec | None
) -> str:
    if target is None:
        return "FAIL"
    if (
        observed.family.lower() == target.provider_family.lower()
        and observed.family.lower() not in [
            p.lower() for p in REJECTED_PROVIDERS_FOR_CERT
        ]
    ):
        return "PASS"
    return "FAIL"


def _classify_model_match(
    observed: JurorVerdict, target: JurorSpec | None
) -> str:
    if target is None:
        return "FAIL"
    if observed.model_id == target.model_id or (
        observed.model_id in target.model_aliases
    ):
        return "PASS"
    return "FAIL"


def _parse_status(v: JurorVerdict) -> str:
    if v.verdict == "ERROR":
        # rationale encodes the specific reason code at prefix
        if "PARSE_FAIL" in v.rationale:
            return "PARSE_FAIL"
        if "TIMEOUT" in v.rationale:
            return "TIMEOUT"
        if "UNREGISTERED" in v.rationale or "MISSING_KEY" in v.rationale:
            return "INFRASTRUCTURE"
        return "ERROR"
    if v.verdict in ("SAFE", "UNSAFE_DIFFERENT_INTENT", "UNSAFE_POLICY_DRIFT"):
        return "OK"
    if v.verdict == "UNCERTAIN":
        return "UNKNOWN"
    return "UNKNOWN"


def _juror_entry(v: JurorVerdict) -> dict[str, Any]:
    """Build one per-juror attestation record."""
    target = _find_registry_spec(v.family, _provider_from_family(v.family))
    provider = _provider_from_family(v.family)

    target_family = target.provider_family if target else None
    target_provider = target.provider if target else None
    target_model = target.model_id if target else None

    provider_match = _classify_provider_match(v, target)
    model_match = _classify_model_match(v, target)
    parse_status = _parse_status(v)

    # Per-juror failure counters (used by verifier hard gates)
    timeout_count = 1 if parse_status == "TIMEOUT" else 0
    error_count = 1 if v.verdict == "ERROR" and parse_status not in (
        "TIMEOUT", "PARSE_FAIL"
    ) else 0
    parse_fail_count = 1 if parse_status == "PARSE_FAIL" else 0
    unknown_count = 1 if v.verdict == "UNCERTAIN" else 0
    unsafe_count = 1 if v.verdict in (
        "UNSAFE_DIFFERENT_INTENT", "UNSAFE_POLICY_DRIFT"
    ) else 0

    # Approved-provider flag: registered AND not in rejected list
    approved = (
        target is not None
        and provider_match == "PASS"
        and model_match == "PASS"
        and v.family.lower() not in REJECTED_PROVIDERS_FOR_CERT
    )

    return {
        "juror_id": v.juror_id,
        # Schema v3: per-juror control_surface stamp — belt-and-suspenders
        # against mixed-surface documents. Required by RTC-REQ-056 gate.
        "control_surface": CONTROL_SURFACE,
        "provider_family": v.family,
        "provider": provider,
        "model_id": v.model_id,
        "target_provider_family": target_family,
        "target_provider": target_provider,
        "target_model_id": target_model,
        "provider_match_status": provider_match,
        "model_match_status": model_match,
        "approved_provider": approved,
        "verdict": v.verdict,
        "confidence": v.confidence,
        "latency_ms": v.latency_ms,
        "response_hash_sha256": v.raw_response_sha256,
        "parse_status": parse_status,
        "timeout_count": timeout_count,
        "error_count": error_count,
        "unknown_count": unknown_count,
        "unsafe_count": unsafe_count,
        "parse_fail_count": parse_fail_count,
        "mock_safe_used": v.family.lower() in ("mock", "mock_safe"),
        "deterministic_proof_stage_used": v.family.lower() in (
            "deterministic", "deterministic_proof_stage"
        ),
        "raw_output_retention_mode": "hash_only",
    }


def _provider_from_family(family: str) -> str:
    """Map provider_family -> provider short-name via registry lookup."""
    for j in REQUIRED_JURORS:
        if j.provider_family.lower() == (family or "").lower():
            return j.provider
    return family


def _panel_response_hash(jurors: list[JurorVerdict]) -> str:
    """Stable hash across the juror panel (sorted by juror_id)."""
    acc = sorted(
        (j.juror_id, j.verdict, j.raw_response_sha256) for j in jurors
    )
    return _sha256_text(json.dumps(acc, sort_keys=True))


# ---------------------------------------------------------------------------
# Panel attestation builder
# ---------------------------------------------------------------------------


def build_panel_attestation(
    *,
    jurors: list[JurorVerdict],
    final_consensus_verdict: str,
    final_safe_reuse_allow: bool,
    final_x3_disposition: str,
    rubric_path: Path,
    request_text: str,
    cache_candidate_text: str,
    invocation_count: int | None = None,
) -> dict[str, Any]:
    """Construct a schema-v2 panel attestation payload.

    Args:
        jurors: Per-juror verdicts produced by ConsensusVeto.
        final_consensus_verdict: The aggregated verdict string ("SAFE" or
            one of the blocking labels).
        final_safe_reuse_allow: True iff the panel allowed reuse.
        final_x3_disposition: The X3 disposition label (e.g. "X3D" for
            approved allow, or a fail-closed label).
        rubric_path: Path to the judge rubric used for this run.
        request_text: The incoming query text (hashed, not stored raw).
        cache_candidate_text: The cached query text (hashed, not stored).
        invocation_count: Optional override for invoked_juror_count
            (defaults to len(jurors)).
    """
    juror_records = [_juror_entry(v) for v in jurors]

    # Panel-level match statuses: PASS iff every juror matched
    provider_panel_match = (
        "PASS"
        if all(r["provider_match_status"] == "PASS" for r in juror_records)
        and len(juror_records) == REQUIRED_JUROR_COUNT
        else "FAIL"
    )
    model_panel_match = (
        "PASS"
        if all(r["model_match_status"] == "PASS" for r in juror_records)
        and len(juror_records) == REQUIRED_JUROR_COUNT
        else "FAIL"
    )

    mock_safe_used_any = any(r["mock_safe_used"] for r in juror_records)
    deterministic_used_any = any(
        r["deterministic_proof_stage_used"] for r in juror_records
    )

    payload = {
        "attestation_schema_version": ATTESTATION_SCHEMA_VERSION,
        "attestation_kind": ATTESTATION_KIND,
        "certification_scope": CERTIFICATION_SCOPE,
        # Schema v3: top-level control_surface + purpose. Required by
        # RTC-REQ-056 gate. Healing documents carry
        # control_surface="healing" and will be rejected.
        "control_surface": CONTROL_SURFACE,
        "purpose": PURPOSE,
        "judge_mode": JUDGE_MODE,
        "quorum_rule": QUORUM_RULE,
        "required_juror_count": REQUIRED_JUROR_COUNT,
        "invoked_juror_count": (
            invocation_count if invocation_count is not None else len(jurors)
        ),
        "final_consensus_verdict": final_consensus_verdict,
        "final_safe_reuse_allow": final_safe_reuse_allow,
        "final_x3_disposition": final_x3_disposition,
        "rubric_hash_sha256": _sha256_file(rubric_path) or "",
        "request_hash_sha256": _sha256_text(request_text),
        "cache_candidate_hash_sha256": _sha256_text(cache_candidate_text),
        "panel_response_hash_sha256": _panel_response_hash(jurors),
        "provider_panel_match_status": provider_panel_match,
        "model_panel_match_status": model_panel_match,
        "mock_safe_used_any": mock_safe_used_any,
        "deterministic_proof_stage_used_any": deterministic_used_any,
        "created_at_utc": _utc_now_iso(),
        "jurors": juror_records,
        "env_probe": {
            # Boolean presence only. Never log secret values.
            "GEMINI_API_KEY_present": bool(os.environ.get("GEMINI_API_KEY")),
            "GOOGLE_API_KEY_present": bool(os.environ.get("GOOGLE_API_KEY")),
            "ANTHROPIC_API_KEY_present": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "OPENAI_API_KEY_present": bool(os.environ.get("OPENAI_API_KEY")),
        },
    }

    # Self-hash (excluding the hash field itself, to make the file
    # auditable against its own declared artifact_hash after write).
    payload["artifact_hash"] = _sha256_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )
    return payload


def write_panel_attestation(
    target_dir: Path, payload: dict[str, Any]
) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / PANEL_ATTESTATION_FILENAME
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
