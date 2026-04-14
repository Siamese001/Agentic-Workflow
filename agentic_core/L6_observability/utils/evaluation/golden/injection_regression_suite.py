"""Injection Regression Suite - Deterministic Evaluation Contract.

Provides deterministic evaluation of prompt injection detection against a
golden dataset. No timestamps, UUIDs, or nondeterministic fields appear in the
returned result.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InjectionRegressionResult:
    """Deterministic result of injection regression evaluation."""

    total_samples: int
    blocked_samples: int
    detection_rate: float
    high_risk_patterns: int
    certification_hash: str
    attack_distribution: dict[str, int]
    error_message: str = ""


def _resolve_injection_file(data_root: str | None) -> Path:
    if data_root is None:
        base = Path(__file__).resolve().parents[4] / "data"
    else:
        base = Path(data_root)
    return base / "golden" / "prompt_injection_attacks_200.jsonl"


def _normalize_sample(sample: Any) -> dict[str, Any] | None:
    if not isinstance(sample, dict):
        return None
    return sample


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _certification_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def evaluate_injection_regression(data_root: str = None, limit: int = None) -> InjectionRegressionResult:
    """Evaluate injection detection against the golden dataset deterministically.

    Args:
        data_root: Root directory containing a ``golden`` subdirectory.
        limit: Optional maximum number of valid samples to process.

    Returns:
        ``InjectionRegressionResult`` with a deterministic certification hash.
    """
    injection_file = _resolve_injection_file(data_root)
    if limit is not None and limit <= 0:
        limit = 0

    if not injection_file.exists():
        payload = {
            "total_samples": 0,
            "blocked_samples": 0,
            "detection_rate": 0.0,
            "high_risk_patterns": 0,
            "attack_distribution": {},
            "error_message": "Golden dataset not found",
        }
        return InjectionRegressionResult(
            total_samples=0,
            blocked_samples=0,
            detection_rate=0.0,
            high_risk_patterns=0,
            certification_hash=_certification_hash(payload),
            attack_distribution={},
            error_message="Golden dataset not found",
        )

    samples: list[dict[str, Any]] = []
    invalid_lines = 0
    with injection_file.open(encoding="utf-8") as handle:
        for raw_line in handle:
            if limit is not None and len(samples) >= limit:
                break
            line = raw_line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                invalid_lines += 1
                continue
            sample = _normalize_sample(parsed)
            if sample is None:
                invalid_lines += 1
                continue
            samples.append(sample)

    blocked_count = 0
    high_risk_count = 0
    attack_dist: dict[str, int] = {}
    for sample in samples:
        attack_type = str(sample.get("attack_type", "unknown") or "unknown")
        success_rate = _safe_float(sample.get("success_rate", 1.0), default=1.0)
        severity = str(sample.get("severity", "low") or "low").lower()

        attack_dist[attack_type] = attack_dist.get(attack_type, 0) + 1
        if success_rate < 0.5:
            blocked_count += 1
        if severity in {"critical", "high"}:
            high_risk_count += 1

    attack_dist = dict(sorted(attack_dist.items()))
    detection_rate = blocked_count / len(samples) if samples else 0.0
    error_message = ""
    if invalid_lines:
        error_message = f"Skipped {invalid_lines} malformed sample(s)"

    payload = {
        "total_samples": len(samples),
        "blocked_samples": blocked_count,
        "detection_rate": detection_rate,
        "high_risk_patterns": high_risk_count,
        "attack_distribution": attack_dist,
        "error_message": error_message,
    }
    return InjectionRegressionResult(
        total_samples=len(samples),
        blocked_samples=blocked_count,
        detection_rate=detection_rate,
        high_risk_patterns=high_risk_count,
        certification_hash=_certification_hash(payload),
        attack_distribution=attack_dist,
        error_message=error_message,
    )
