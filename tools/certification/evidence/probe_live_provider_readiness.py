"""RTC-REQ-056 consensus-jury readiness probe.

Reports presence/absence of API keys and resolved model IDs for the
three required jurors (Gemini / Claude / GPT). Never logs secret values.

This is a DIAGNOSTIC probe: it never writes a panel attestation and it
exits 0 regardless of which jurors are available. If any juror is
missing, downstream composer / verifier treat RTC-REQ-056 as
``INFRASTRUCTURE_GAP``.

Output: artifacts/certification/integrated_runtime/live_provider_readiness.json

Per operator directive 2026-05-01 13:39 UTC-04:00.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.consensus_juror_clients import (
    api_key_presence,
    resolve_model_id,
)
from tools.certification.safety.rtc_req_056_panel import (
    CERTIFICATION_SCOPE,
    CONTROL_SURFACE,
    PURPOSE,
    REQUIRED_JURORS,
    REQUIRED_JUROR_COUNT,
    RejectReason,
)

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
ARTIFACT_PATH = ARTIFACT_DIR / "live_provider_readiness.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_readiness_probe() -> dict[str, Any]:
    jurors: list[dict[str, Any]] = []
    missing: list[str] = []

    for j in REQUIRED_JURORS:
        key_present = api_key_presence(j)
        effective_model, reject_reason = resolve_model_id(j)
        entry: dict[str, Any] = {
            "juror_id": j.juror_id,
            "control_surface": CONTROL_SURFACE,
            "provider_family": j.provider_family,
            "provider": j.provider,
            "target_model_id": j.model_id,
            "resolved_model_id": effective_model,
            "env_key_primary": j.env_key,
            "env_key_aliases": list(j.env_key_aliases),
            "env_key_present": key_present,
            "model_override_env": j.model_env_override,
            "model_override_reject_reason": reject_reason,
            "available_for_certification": (
                key_present and reject_reason is None
            ),
        }
        jurors.append(entry)
        if not key_present:
            missing.append(
                f"{j.juror_id}: no key in {j.env_key} "
                f"or aliases {list(j.env_key_aliases)}"
            )
        if reject_reason is not None:
            missing.append(
                f"{j.juror_id}: {reject_reason} "
                f"(override env {j.model_env_override})"
            )

    all_required_available = all(
        e["available_for_certification"] for e in jurors
    )

    return {
        "schema_version": 3,
        "certification_scope": CERTIFICATION_SCOPE,
        "control_surface": CONTROL_SURFACE,
        "purpose": PURPOSE,
        "judge_mode": "consensus_jury",
        "required_juror_count": REQUIRED_JUROR_COUNT,
        "invoked_juror_count": len(jurors),
        "all_required_available": all_required_available,
        "jurors": jurors,
        "missing_requirements": missing,
        "rtc_req_056_status_hint": (
            "READY_FOR_CERTIFICATION"
            if all_required_available
            else RejectReason.INFRASTRUCTURE_GAP_MISSING_KEY
        ),
        "executed_at_utc": _utc_now_iso(),
    }


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    report = run_readiness_probe()
    ARTIFACT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"[readiness] scope={report['certification_scope']} "
        f"required={report['required_juror_count']} "
        f"all_available={report['all_required_available']}"
    )
    for j in report["jurors"]:
        status = "ok" if j["available_for_certification"] else "MISSING"
        print(
            f"[readiness]   {j['juror_id']} "
            f"key_present={j['env_key_present']} "
            f"resolved_model={j['resolved_model_id']} status={status}"
        )
    for m in report["missing_requirements"]:
        print(f"[readiness]   GAP: {m}")
    print(f"[readiness] artifact={ARTIFACT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
