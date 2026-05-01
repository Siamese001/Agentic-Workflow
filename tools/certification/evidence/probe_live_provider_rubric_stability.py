"""W2b Phase P2 — Rubric stability probe.

Invokes ``LLMJudgeVeto`` THREE times at temperature=0 against a canonical
safe-reuse query pair and records the verdicts. Used to validate that
the chosen live provider produces a stable SAFE verdict on a trivially
safe paraphrase pair before committing to an acceptance run.

Escalates `local_qwen` → `anthropic_haiku` on failure when both are
configured to be probed; exits 0 with a diagnostic report either way.
The composer/verifier treat FAIL as INFRASTRUCTURE_GAP.

Output: artifacts/certification/integrated_runtime/rubric_stability_report.json

Plan: .windsurf/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 2
"""

from __future__ import annotations

import hashlib
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

from tools.certification.safety.llm_judge_veto import LLMJudgeVeto  # noqa: E402
from tools.certification.safety.veto_protocol import VetoStatus  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
ARTIFACT_PATH = ARTIFACT_DIR / "rubric_stability_report.json"
READINESS_PATH = ARTIFACT_DIR / "live_provider_readiness.json"

NUM_RUNS = 3
CONFIDENCE_FLOOR = 0.75
STABILITY_TIMEOUT_MS = 10000
STORE_RAW = os.environ.get("W2B_STORE_RAW_PROVIDER_OUTPUT") == "1"

# Canonical safe-reuse pair: trivially safe paraphrase. If the provider
# can't produce a stable SAFE here, it cannot be trusted for certification.
CANONICAL_PAIR = {
    "query": "What year did the Apollo 11 mission land humans on the Moon?",
    "cached_query": "In what year did Apollo 11 land astronauts on the lunar surface?",
    "cached_answer": (
        "Apollo 11 landed humans on the Moon on July 20, 1969. "
        "Neil Armstrong and Buzz Aldrin walked on the lunar surface."
    ),
    "context": {
        "policy_version": "w2b-canonical-v1",
        "tenant": "certification_fixture",
    },
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _readiness_chosen() -> str | None:
    """Read the chosen provider from the P1 readiness report, if present."""
    if not READINESS_PATH.exists():
        return None
    try:
        data = json.loads(READINESS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    chosen = data.get("chosen_provider")
    if isinstance(chosen, str) and chosen in {"local_qwen", "anthropic_haiku"}:
        return chosen
    return None


def _single_run(veto: LLMJudgeVeto, run_idx: int) -> dict[str, Any]:
    """Execute one LLMJudgeVeto.evaluate call on the canonical pair."""
    start = time.perf_counter()
    result = veto.evaluate(
        query=CANONICAL_PAIR["query"],
        cached_query=CANONICAL_PAIR["cached_query"],
        cached_answer=CANONICAL_PAIR["cached_answer"],
        context=CANONICAL_PAIR["context"],
    )
    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    # Surface raw response from metadata when the stage preserves it
    raw_resp = ""
    if result.metadata:
        raw_resp = str(result.metadata.get("raw", ""))

    verdict_name = (
        result.status.name if isinstance(result.status, VetoStatus) else str(result.status)
    )
    return {
        "run_index": run_idx,
        "verdict": verdict_name,
        "confidence": result.confidence,
        "latency_ms": latency_ms,
        "stage_name": result.stage_name,
        "rationale": result.rationale or "",
        "raw_response_sha256": _sha256_hex(raw_resp) if raw_resp else None,
        "raw_response": raw_resp if STORE_RAW else None,
        "error": result.error,
    }


def _evaluate_stability(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply the W2b § 2 PASS conditions to the 3 runs."""
    failures: list[str] = []

    verdicts = {r["verdict"] for r in runs}
    if verdicts != {"SAFE"}:
        failures.append(
            f"not all runs SAFE (got {sorted(verdicts)})"
        )

    confidences = [r["confidence"] for r in runs]
    if any(c < CONFIDENCE_FLOOR for c in confidences):
        failures.append(
            f"confidence below {CONFIDENCE_FLOOR} (got {confidences})"
        )

    latencies = [r["latency_ms"] for r in runs]
    if any(l > STABILITY_TIMEOUT_MS for l in latencies):
        failures.append(
            f"latency above {STABILITY_TIMEOUT_MS}ms (got {latencies})"
        )

    if any(r.get("error") for r in runs):
        failures.append(
            f"provider errors present: {[r.get('error') for r in runs]}"
        )

    # Response hash mode
    hashes = [r["raw_response_sha256"] for r in runs if r["raw_response_sha256"]]
    if hashes and len(set(hashes)) == 1:
        hash_mode = "exact"
    elif not failures:
        hash_mode = "paraphrase_tolerant"
    else:
        hash_mode = "unknown"

    return {
        "pass": not failures,
        "failure_reasons": failures,
        "response_hash_mode": hash_mode,
        "confidence_floor_required": CONFIDENCE_FLOOR,
        "timeout_ms_required": STABILITY_TIMEOUT_MS,
    }


def run_stability_probe(provider: str) -> dict[str, Any]:
    """Execute NUM_RUNS evaluates against the given provider."""
    veto = LLMJudgeVeto(provider=provider, temperature=0.0)
    available = veto.is_available()

    if not available:
        return {
            "schema_version": 1,
            "executed_at_utc": _utc_now_iso(),
            "provider": provider,
            "available": False,
            "runs": [],
            "stability": {
                "pass": False,
                "failure_reasons": [f"provider {provider} not available"],
                "response_hash_mode": "unknown",
                "confidence_floor_required": CONFIDENCE_FLOOR,
                "timeout_ms_required": STABILITY_TIMEOUT_MS,
            },
            "store_raw_provider_output": STORE_RAW,
            "canonical_pair_hash_sha256": _sha256_hex(
                json.dumps(CANONICAL_PAIR, sort_keys=True)
            ),
        }

    runs = [_single_run(veto, i + 1) for i in range(NUM_RUNS)]
    stability = _evaluate_stability(runs)
    return {
        "schema_version": 1,
        "executed_at_utc": _utc_now_iso(),
        "provider": provider,
        "available": True,
        "runs": runs,
        "stability": stability,
        "store_raw_provider_output": STORE_RAW,
        "canonical_pair_hash_sha256": _sha256_hex(
            json.dumps(CANONICAL_PAIR, sort_keys=True)
        ),
    }


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    # Provider resolution:
    #   1. explicit --provider X
    #   2. readiness report's chosen_provider
    #   3. local_qwen then anthropic_haiku
    argv_provider = None
    for i, a in enumerate(sys.argv[1:]):
        if a == "--provider" and i + 1 < len(sys.argv) - 1:
            argv_provider = sys.argv[i + 2]

    if argv_provider in {"local_qwen", "anthropic_haiku"}:
        providers_to_try = [argv_provider]
    else:
        chosen = _readiness_chosen()
        if chosen:
            providers_to_try = [chosen]
            # Keep the fallback path in reach if the chosen one fails stability
            if chosen == "local_qwen":
                providers_to_try.append("anthropic_haiku")
        else:
            providers_to_try = ["local_qwen", "anthropic_haiku"]

    report: dict[str, Any] | None = None
    attempted: list[str] = []
    for provider in providers_to_try:
        attempted.append(provider)
        candidate_report = run_stability_probe(provider)
        if candidate_report["stability"]["pass"]:
            report = candidate_report
            break
        # Keep last failing report but prefer a passing one
        if report is None:
            report = candidate_report

    assert report is not None
    report["attempted_providers"] = attempted

    ARTIFACT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    passed = report["stability"]["pass"]
    print(
        f"[w2b-stability] provider={report['provider']} "
        f"available={report['available']} pass={passed}"
    )
    if not passed:
        for reason in report["stability"]["failure_reasons"]:
            print(f"[w2b-stability]   fail_reason: {reason}")
    print(f"[w2b-stability] artifact={ARTIFACT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
