"""X1D calibration trust contract.

Offline eval may only trust X1D scores when they are tied to a fresh calibration
snapshot, a single canonical metric, provider-mode parity, and quorum.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CANONICAL_CALIBRATION_METRIC = "quadratic_weighted_kappa"


@dataclass(frozen=True, slots=True)
class X1DTrustDecision:
    trusted: bool
    reason_codes: list[str]
    canonical_metric: str
    calibration_snapshot_id: str | None
    calibrated_provider_count: int
    required_provider_count: int


def _text(value: Any) -> str:
    return str(value or "").strip()


def _calibration(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("calibration")
    if not isinstance(value, dict):
        return {}
    return value


def _judge_scores(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("judge_scores")
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def evaluate_trust(payload: dict[str, Any]) -> X1DTrustDecision:
    calibration = _calibration(payload)
    scores = _judge_scores(payload)
    required_provider_count = int(payload.get("required_provider_count") or 2)
    expected_provider_mode = _text(payload.get("provider_mode") or "live")
    metric = _text(calibration.get("metric"))
    snapshot_id = _text(calibration.get("snapshot_id")) or None
    reasons: list[str] = []

    if metric != CANONICAL_CALIBRATION_METRIC:
        reasons.append("CALIBRATION_METRIC_MISMATCH")
        if metric in {"raw_agreement", "agreement"}:
            reasons.append("RAW_AGREEMENT_NOT_ACCEPTED")

    threshold = float(calibration.get("threshold") or 0.0)
    value = calibration.get("value")
    if not isinstance(value, (int, float)) or float(value) < threshold:
        reasons.append("CALIBRATION_BELOW_THRESHOLD")

    if not snapshot_id:
        reasons.append("CALIBRATION_SNAPSHOT_MISSING")

    status = _text(calibration.get("status")).upper()
    if status != "FRESH":
        reasons.append("CALIBRATION_STALE")

    calibrated_providers: set[str] = set()
    for index, row in enumerate(scores):
        provider = _text(row.get("provider") or row.get("provider_key") or row.get("judge_id"))
        score_snapshot = _text(row.get("calibration_snapshot_id") or row.get("snapshot_id"))
        provider_mode = _text(row.get("provider_mode") or expected_provider_mode)
        prefix = f"JUDGE_SCORE_{index}"
        if not score_snapshot:
            reasons.append(prefix + "_SNAPSHOT_MISSING")
            continue
        if snapshot_id and score_snapshot != snapshot_id:
            reasons.append(prefix + "_SNAPSHOT_MISMATCH")
            continue
        if provider_mode != expected_provider_mode:
            reasons.append(prefix + "_PROVIDER_MODE_MISMATCH")
            continue
        if provider:
            calibrated_providers.add(provider)

    if len(calibrated_providers) < required_provider_count:
        reasons.append("QUORUM_NOT_MET")

    return X1DTrustDecision(
        trusted=not reasons,
        reason_codes=reasons,
        canonical_metric=CANONICAL_CALIBRATION_METRIC,
        calibration_snapshot_id=snapshot_id,
        calibrated_provider_count=len(calibrated_providers),
        required_provider_count=required_provider_count,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        payload = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("receipt must be a JSON object")
        decision = evaluate_trust(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[CONFIG_ERROR] {exc}", file=sys.stderr)
        return 2

    out = asdict(decision)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        json.dump(out, sys.stdout, indent=2, sort_keys=True)
        print()
    return 0 if decision.trusted else 1


if __name__ == "__main__":
    raise SystemExit(main())
