"""RTC-REQ-056 consensus-jury rubric stability probe.

Runs each required juror against the canonical SAFE stability pair and
requires a structured SAFE verdict from each. If any juror is
non-SAFE, unavailable, timeout, error, or parse-fail, the probe
reports fail-closed and emits NO panel attestation.

Output:
  artifacts/certification/integrated_runtime/live_provider_rubric_stability.json

This probe is the gate between "keys present" (readiness) and
"integrated runtime run" (safe-reuse). It verifies that each juror
actually produces a well-formed SAFE verdict under the canonical
equivalence pair before the real certification run is attempted.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.consensus_juror_clients import (
    DEFAULT_RUBRIC_PATH,
    make_real_juror_call_impl,
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
ARTIFACT_PATH = ARTIFACT_DIR / "live_provider_rubric_stability.json"

# Canonical SAFE stability pair (paraphrase with same intent)
STABILITY_QUERY = "What is the weather in Paris today?"
STABILITY_CACHED_QUERY = "Tell me the current weather in Paris."
STABILITY_CACHED_ANSWER = (
    "Partly cloudy with 18C and light winds from the west."
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_rubric_stability_probe() -> dict[str, Any]:
    # Build the real juror call impl (lazy SDK imports; missing SDK ->
    # per-juror ERROR verdict, no exception leaks out)
    impl = make_real_juror_call_impl(rubric_path=DEFAULT_RUBRIC_PATH)

    juror_results: list[dict[str, Any]] = []
    all_safe = True
    failure_reasons: list[str] = []

    for j in REQUIRED_JURORS:
        verdict = impl(
            j.provider_family,
            j.model_id,
            STABILITY_QUERY,
            STABILITY_CACHED_QUERY,
            STABILITY_CACHED_ANSWER,
            {"stability_probe": True},
        )
        juror_dict = verdict.to_dict()
        # Schema v3: stamp control_surface on every juror record
        juror_dict["control_surface"] = CONTROL_SURFACE
        juror_results.append(juror_dict)
        if verdict.verdict != "SAFE":
            all_safe = False
            failure_reasons.append(
                f"{verdict.juror_id}: verdict={verdict.verdict} "
                f"rationale={verdict.rationale[:140]}"
            )

    return {
        "schema_version": 3,
        "certification_scope": CERTIFICATION_SCOPE,
        "control_surface": CONTROL_SURFACE,
        "purpose": PURPOSE,
        "judge_mode": "consensus_jury",
        "required_juror_count": REQUIRED_JUROR_COUNT,
        "invoked_juror_count": len(juror_results),
        "all_required_safe": all_safe,
        "jurors": juror_results,
        "failure_reasons": failure_reasons,
        "rtc_req_056_status_hint": (
            "RUBRIC_STABILITY_PASS"
            if all_safe
            else "RUBRIC_STABILITY_FAIL"
        ),
        "stability_pair": {
            "query": STABILITY_QUERY,
            "cached_query": STABILITY_CACHED_QUERY,
            # No raw cached_answer — hash-only would be more secure, but
            # the stability pair is canonical and non-sensitive.
            "cached_answer": STABILITY_CACHED_ANSWER,
        },
        "executed_at_utc": _utc_now_iso(),
    }


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    report = run_rubric_stability_probe()
    ARTIFACT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"[stability] scope={report['certification_scope']} "
        f"all_safe={report['all_required_safe']}"
    )
    for j in report["jurors"]:
        print(
            f"[stability]   {j['juror_id']} "
            f"verdict={j['verdict']} "
            f"latency={j['latency_ms']:.0f}ms"
        )
    for r in report["failure_reasons"]:
        print(f"[stability]   FAIL: {r}")
    print(f"[stability] artifact={ARTIFACT_PATH}")
    # Exit 0 always — this is diagnostic. Downstream gates decide.
    return 0


if __name__ == "__main__":
    sys.exit(main())
