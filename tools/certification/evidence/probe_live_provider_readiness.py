"""W2b Phase P1 — Live-provider readiness probe.

Diagnostic probe that inspects the environment for approved SAFE-producing
LLM providers in the order mandated by W2b:

    1. ``local_qwen`` (vLLM OpenAI-compatible endpoint at localhost:8000/v1)
    2. ``anthropic_haiku`` (requires ANTHROPIC_API_KEY)

The ``mock_safe`` provider is NEVER reported as a certification candidate here.
It remains available for unit tests only, gated on LLMJUDGEVETO_APPROVED_MOCK_SAFE.

This probe is diagnostic, not a gate: it exits 0 regardless of whether any
provider is available. Downstream composer / verifier interpret absence as
INFRASTRUCTURE_GAP per plan rtc-w2b-live-provider-allow-proof-b24f8e § 1.

No secret values are logged or persisted — only booleans and public endpoint URLs.

Output: artifacts/certification/integrated_runtime/live_provider_readiness.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
ARTIFACT_PATH = ARTIFACT_DIR / "live_provider_readiness.json"

LOCAL_QWEN_ENDPOINT = os.environ.get(
    "LOCAL_QWEN_ENDPOINT", "http://localhost:8000/v1"
)
LOCAL_QWEN_MODEL = os.environ.get(
    "LOCAL_QWEN_MODEL", "Qwen/Qwen2.5-7B-Instruct"
)
ANTHROPIC_MODEL = os.environ.get(
    "ANTHROPIC_MODEL", "claude-haiku-4-5"
)
PROBE_TIMEOUT_S = 5.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _probe_local_qwen() -> dict[str, Any]:
    """Probe the local vLLM OpenAI-compatible endpoint.

    Uses a GET /v1/models with a 5s timeout. Records latency and the
    first reported model id when available. Never raises.
    """
    import urllib.error
    import urllib.request

    url = f"{LOCAL_QWEN_ENDPOINT.rstrip('/')}/models"
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT_S) as resp:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            body = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
            reported_model = None
            if isinstance(parsed, dict):
                data = parsed.get("data") or []
                if isinstance(data, list) and data:
                    entry = data[0]
                    if isinstance(entry, dict):
                        reported_model = entry.get("id")
        return {
            "provider": "local_qwen",
            "order": 1,
            "available": True,
            "endpoint": LOCAL_QWEN_ENDPOINT,
            "model_id": reported_model or LOCAL_QWEN_MODEL,
            "model_version": reported_model or LOCAL_QWEN_MODEL,
            "probe_latency_ms": latency_ms,
            "probe_method": "GET /v1/models",
            "failure_reason": None,
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "provider": "local_qwen",
            "order": 1,
            "available": False,
            "endpoint": LOCAL_QWEN_ENDPOINT,
            "model_id": LOCAL_QWEN_MODEL,
            "model_version": None,
            "probe_latency_ms": None,
            "probe_method": "GET /v1/models",
            "failure_reason": f"{type(exc).__name__}: {exc}",
        }


def _probe_anthropic_haiku() -> dict[str, Any]:
    """Check for ANTHROPIC_API_KEY presence. Does NOT call the API.

    Recording only a boolean keeps secrets out of artifacts per W2b § 4.
    """
    key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return {
        "provider": "anthropic_haiku",
        "order": 2,
        "available": key_present,
        "endpoint": "https://api.anthropic.com",
        "model_id": ANTHROPIC_MODEL,
        "model_version": ANTHROPIC_MODEL,
        "probe_latency_ms": None,
        "probe_method": "env[ANTHROPIC_API_KEY] presence",
        "failure_reason": (
            None if key_present else "ANTHROPIC_API_KEY not set in CERT env"
        ),
    }


def _choose_provider(candidates: list[dict[str, Any]]) -> tuple[str | None, str]:
    """Pick the first available candidate by declared order.

    Returns ``(chosen_provider_or_None, human_reason)``. Never returns
    ``mock_safe`` — W2b § 1 forbids it from the certification path.
    """
    for cand in sorted(candidates, key=lambda c: c["order"]):
        if cand["available"]:
            return cand["provider"], (
                f"{cand['provider']} available and ordered {cand['order']}"
            )
    return None, "No approved provider available; INFRASTRUCTURE_GAP will be raised downstream"


def _unavailable_reasons(candidates: list[dict[str, Any]]) -> list[str]:
    return [
        f"{c['provider']}: {c['failure_reason']}"
        for c in candidates
        if not c["available"] and c["failure_reason"]
    ]


def run_readiness_probe() -> dict[str, Any]:
    candidates = [_probe_local_qwen(), _probe_anthropic_haiku()]
    chosen, reason = _choose_provider(candidates)
    return {
        "schema_version": 1,
        "executed_at_utc": _utc_now_iso(),
        "candidates": candidates,
        "chosen_provider": chosen,
        "chosen_reason": reason,
        "unavailable_reasons": _unavailable_reasons(candidates),
    }


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    report = run_readiness_probe()
    ARTIFACT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    chosen = report["chosen_provider"] or "<none>"
    print(f"[w2b-readiness] chosen_provider={chosen}")
    for cand in report["candidates"]:
        status = "ok" if cand["available"] else "unavailable"
        reason = cand["failure_reason"] or "-"
        print(
            f"[w2b-readiness]   order={cand['order']} "
            f"provider={cand['provider']} status={status} reason={reason}"
        )
    print(f"[w2b-readiness] artifact={ARTIFACT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
