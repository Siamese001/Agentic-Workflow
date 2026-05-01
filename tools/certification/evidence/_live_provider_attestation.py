"""W2b Phase P4 — Live-provider attestation writer.

Emits ``live_provider_attestation.json`` into the canonical
``c_primary_allow/`` directory when, and only when, a live approved
SAFE-producing provider completed the integrated-runtime run with
verdict=SAFE / x3=X3D / allow=True.

The schema matches plan § 3. Composer + verifier consume this file.

Placement: next to the manifest emitted by the integrated-runtime
entrypoint for the canonical acceptance run.

Plan: .windsurf/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 3, § 4
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

__all__ = [
    "APPROVED_PROVIDERS",
    "ATTESTATION_SCHEMA_VERSION",
    "build_attestation_payload",
    "write_attestation",
]

ATTESTATION_SCHEMA_VERSION = 1
ATTESTATION_KIND = "live_provider_allow_path"
ATTESTATION_FILENAME = "live_provider_attestation.json"

# Authoritative set of providers acceptable for W2b certification.
APPROVED_PROVIDERS = frozenset({"local_qwen", "anthropic_haiku"})


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, FileNotFoundError):
        return None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_attestation_payload(
    *,
    provider: str,
    model_id: str,
    model_version: str | None,
    rubric_path: Path,
    raw_response: str,
    response_hash_mode: str,
    verdict: str,
    confidence: float,
    latency_ms: float,
    llm_judge_invocation_count: int,
    veto_stage_class: str,
    deterministic_proof_stage_used: bool,
    x3_disposition: str,
    safe_reuse_allow: bool,
) -> dict[str, Any]:
    """Construct a schema-v1 attestation payload.

    No raw secrets are included. Only:
      - boolean presence of ``ANTHROPIC_API_KEY``
      - the local_qwen endpoint URL (public local address)
      - boolean state of ``LLMJUDGEVETO_APPROVED_MOCK_SAFE``
    """
    rubric_hash = _sha256_file(rubric_path)

    # response_hash_mode controls what the canonical hash represents.
    # In paraphrase_tolerant mode we hash the parsed-verdict object so
    # stochastic LLM wording does not invalidate the attestation.
    if response_hash_mode == "exact":
        response_hash_input = raw_response
    else:
        # paraphrase_tolerant / unknown — hash the parsed verdict view
        response_hash_input = json.dumps(
            {"verdict": verdict, "confidence_bucket": round(confidence, 2)},
            sort_keys=True,
        )
    response_hash = _sha256_text(response_hash_input)

    approved = provider in APPROVED_PROVIDERS
    mock_safe_used = provider == "mock_safe"

    payload = {
        "schema_version": ATTESTATION_SCHEMA_VERSION,
        "attestation_kind": ATTESTATION_KIND,
        "provider": provider,
        "model_id": model_id,
        "model_version": model_version or model_id,
        "rubric_path": str(
            rubric_path.relative_to(rubric_path.parents[len(rubric_path.parents) - 1])
        ) if rubric_path.is_absolute() else str(rubric_path),
        "rubric_hash_sha256": rubric_hash,
        "response_hash_sha256": response_hash,
        "response_hash_mode": response_hash_mode,
        "verdict": verdict,
        "confidence": confidence,
        "latency_ms": latency_ms,
        "wall_clock_utc": _utc_now_iso(),
        "llm_judge_invocation_count": llm_judge_invocation_count,
        "veto_stage_class": veto_stage_class,
        "deterministic_proof_stage_used": deterministic_proof_stage_used,
        "x3_disposition": x3_disposition,
        "safe_reuse_allow": safe_reuse_allow,
        "mock_safe_used": mock_safe_used,
        "approved_provider": approved and not mock_safe_used,
        "env_probe": {
            "LLMJUDGEVETO_APPROVED_MOCK_SAFE": (
                "set" if os.environ.get("LLMJUDGEVETO_APPROVED_MOCK_SAFE") else "unset"
            ),
            "LOCAL_QWEN_ENDPOINT": os.environ.get(
                "LOCAL_QWEN_ENDPOINT", "http://localhost:8000/v1"
            ),
            "ANTHROPIC_API_KEY_present": bool(os.environ.get("ANTHROPIC_API_KEY")),
        },
    }
    return payload


def write_attestation(target_dir: Path, payload: dict[str, Any]) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / ATTESTATION_FILENAME
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
