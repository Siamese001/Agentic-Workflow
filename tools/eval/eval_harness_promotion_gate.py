"""Eval harness promotion evidence gate.

Promotion is blocked unless the harness evidence bundle contains current replay,
X2, X1D, L6 graduation, ADG transport, and baseline receipts. This gate is
intended for CI and for UWG promotion packet preflight references.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_EVIDENCE_KEYS: tuple[str, ...] = (
    "replay_receipt",
    "x2_micro_eval_receipt",
    "x1d_trust_receipt",
    "l6_graduation_receipt",
    "adg_transport_receipt",
)

TRIGGER_PATH_MARKERS: tuple[str, ...] = (
    "tools/eval/",
    "data/eval/",
    "apps_rg/runtime/validators/",
    "apps_rg/runtime/judges/",
    "apps_rg/runtime/shadow/",
    "apps_rg/runtime/spine/",
    "agentic_core/UWG/",
    "ops_scripts/ci/",
)


@dataclass(frozen=True, slots=True)
class EvidenceCheck:
    key: str
    path: str | None
    passed: bool
    reason_codes: list[str]


@dataclass(frozen=True, slots=True)
class PromotionGateDecision:
    passed: bool
    reason_codes: list[str]
    checks: list[EvidenceCheck]
    trigger_coverage: dict[str, bool]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return payload


def _manifest_path(manifest: dict[str, Any], key: str, root: Path) -> Path | None:
    evidence = manifest.get("evidence")
    if not isinstance(evidence, dict):
        return None
    value = evidence.get(key)
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _baseline_ok(payload: dict[str, Any]) -> bool:
    baseline = payload.get("baseline")
    if not isinstance(baseline, dict):
        return False
    return baseline.get("status") == "MATCH"


def _check_replay(payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if payload.get("schema_version") != "whole_spine_replay_receipt.v1":
        reasons.append("REPLAY_SCHEMA_INVALID")
    if payload.get("passed") is not True:
        reasons.append("REPLAY_NOT_PASSED")
    if not _baseline_ok(payload):
        reasons.append("REPLAY_BASELINE_NOT_MATCH")
    if not payload.get("runtime_receipt_sha256"):
        reasons.append("REPLAY_RUNTIME_RECEIPT_HASH_MISSING")
    return reasons


def _check_x2(payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if payload.get("passed") is not True:
        reasons.append("X2_MICRO_EVAL_NOT_PASSED")
    if payload.get("missing_required_families"):
        reasons.append("X2_REQUIRED_FAMILIES_MISSING")
    if int(payload.get("fixture_count") or 0) < 5:
        reasons.append("X2_FIXTURE_COUNT_TOO_LOW")
    return reasons


def _check_x1d(payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if payload.get("trusted") is not True:
        reasons.append("X1D_NOT_TRUSTED")
    if payload.get("canonical_metric") != "quadratic_weighted_kappa":
        reasons.append("X1D_CANONICAL_METRIC_INVALID")
    if not payload.get("calibration_snapshot_id"):
        reasons.append("X1D_CALIBRATION_SNAPSHOT_MISSING")
    if int(payload.get("calibrated_provider_count") or 0) < int(payload.get("required_provider_count") or 2):
        reasons.append("X1D_QUORUM_NOT_MET")
    return reasons


def _check_l6(payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if payload.get("graduated") is not True:
        reasons.append("L6_NOT_GRADUATED")
    if not payload.get("target_corpus_path"):
        reasons.append("L6_TARGET_CORPUS_PATH_MISSING")
    return reasons


def _check_adg(payload: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    status = str(payload.get("status") or payload.get("adg_health_status") or "").lower()
    if status != "ok":
        reasons.append("ADG_TRANSPORT_NOT_OK")
    if payload.get("transport_mode") == "DEGRADED_FALLBACK_SQLITE":
        reasons.append("ADG_DEGRADED_FALLBACK_NOT_PROMOTABLE")
    for field_name in ("pid", "snapshot_id", "sqlite_path"):
        if not payload.get(field_name):
            reasons.append(f"ADG_{field_name.upper()}_MISSING")
    if not payload.get("startup_nonce") and not (
        payload.get("direct_mcp_verified") is True
        and payload.get("runtime_info_available") is False
        and payload.get("runtime_info_unavailable_reason")
    ):
        reasons.append("ADG_STARTUP_NONCE_MISSING")
    if payload.get("redis_status") not in ("healthy", "ok", True):
        reasons.append("ADG_REDIS_NOT_HEALTHY")
    return reasons


CHECKERS = {
    "replay_receipt": _check_replay,
    "x2_micro_eval_receipt": _check_x2,
    "x1d_trust_receipt": _check_x1d,
    "l6_graduation_receipt": _check_l6,
    "adg_transport_receipt": _check_adg,
}


def _trigger_coverage(manifest: dict[str, Any]) -> dict[str, bool]:
    paths = [str(p).replace("\\", "/") for p in manifest.get("touched_paths") or []]
    return {marker: any(marker in path for path in paths) for marker in TRIGGER_PATH_MARKERS}


def evaluate_manifest(manifest_path: Path) -> PromotionGateDecision:
    manifest_path = manifest_path.resolve()
    root = manifest_path.parent
    manifest = _load_json(manifest_path)
    checks: list[EvidenceCheck] = []
    all_reasons: list[str] = []

    for key in REQUIRED_EVIDENCE_KEYS:
        path = _manifest_path(manifest, key, root)
        reasons: list[str] = []
        payload: dict[str, Any] = {}
        if path is None:
            reasons.append(f"{key.upper()}_PATH_MISSING")
        elif not path.is_file():
            reasons.append(f"{key.upper()}_FILE_MISSING")
        else:
            payload = _load_json(path)
            reasons.extend(CHECKERS[key](payload))
        if reasons:
            all_reasons.extend(reasons)
        checks.append(
            EvidenceCheck(
                key=key,
                path=str(path) if path else None,
                passed=not reasons,
                reason_codes=reasons,
            )
        )

    coverage = _trigger_coverage(manifest)
    if not any(coverage.values()):
        all_reasons.append("CI_TRIGGER_COVERAGE_EMPTY")

    return PromotionGateDecision(
        passed=not all_reasons,
        reason_codes=all_reasons,
        checks=checks,
        trigger_coverage=coverage,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        decision = evaluate_manifest(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[CONFIG_ERROR] {exc}", file=sys.stderr)
        return 2

    payload = asdict(decision)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
    return 0 if decision.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
