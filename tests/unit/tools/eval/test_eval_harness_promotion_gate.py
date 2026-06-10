from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.eval.eval_harness_promotion_gate import evaluate_manifest


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _bundle(tmp_path: Path, *, adg_ok: bool = True) -> Path:
    _write_json(
        tmp_path / "replay.json",
        {
            "schema_version": "whole_spine_replay_receipt.v1",
            "passed": True,
            "runtime_receipt_sha256": "abc",
            "baseline": {"status": "MATCH"},
        },
    )
    _write_json(
        tmp_path / "x2.json",
        {"passed": True, "fixture_count": 5, "missing_required_families": []},
    )
    _write_json(
        tmp_path / "x1d.json",
        {
            "trusted": True,
            "canonical_metric": "quadratic_weighted_kappa",
            "calibration_snapshot_id": "calib",
            "calibrated_provider_count": 2,
            "required_provider_count": 2,
        },
    )
    _write_json(
        tmp_path / "l6.json",
        {"graduated": True, "target_corpus_path": "data/eval/golden/l6/case.json"},
    )
    _write_json(
        tmp_path / "adg.json",
        {
            "status": "ok" if adg_ok else "transport_closed",
            "pid": 123,
            "startup_nonce": "nonce",
            "snapshot_id": "06082026_1212",
            "sqlite_path": "artifacts/adg/adg.sqlite",
            "redis_status": "healthy",
            **({"transport_mode": "DEGRADED_FALLBACK_SQLITE"} if not adg_ok else {}),
        },
    )
    manifest = {
        "evidence": {
            "replay_receipt": "replay.json",
            "x2_micro_eval_receipt": "x2.json",
            "x1d_trust_receipt": "x1d.json",
            "l6_graduation_receipt": "l6.json",
            "adg_transport_receipt": "adg.json",
        },
        "touched_paths": ["tools/eval/whole_spine_replay.py", "agentic_core/UWG/package_driven_write_admission.py"],
    }
    path = tmp_path / "manifest.json"
    _write_json(path, manifest)
    return path


def _adg_receipt_path(manifest: Path) -> Path:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    return manifest.parent / payload["evidence"]["adg_transport_receipt"]


def test_complete_evidence_bundle_passes(tmp_path: Path) -> None:
    decision = evaluate_manifest(_bundle(tmp_path))

    assert decision.passed is True
    assert decision.reason_codes == []
    assert all(check.passed for check in decision.checks)


def test_closed_adg_transport_blocks_promotion(tmp_path: Path) -> None:
    decision = evaluate_manifest(_bundle(tmp_path, adg_ok=False))

    assert decision.passed is False
    assert "ADG_TRANSPORT_NOT_OK" in decision.reason_codes
    assert "ADG_DEGRADED_FALLBACK_NOT_PROMOTABLE" in decision.reason_codes


def test_direct_mcp_health_allows_missing_runtime_nonce_when_unavailable(tmp_path: Path) -> None:
    manifest = _bundle(tmp_path)
    adg_path = _adg_receipt_path(manifest)
    adg = json.loads(adg_path.read_text(encoding="utf-8"))
    adg.pop("startup_nonce")
    adg.update(
        {
            "direct_mcp_verified": True,
            "runtime_info_available": False,
            "runtime_info_unavailable_reason": "Codex exposed ADG tool list omits adg_runtime_info.",
        }
    )
    _write_json(adg_path, adg)

    decision = evaluate_manifest(manifest)

    assert decision.passed is True
    assert "ADG_STARTUP_NONCE_MISSING" not in decision.reason_codes


def test_missing_runtime_nonce_without_direct_mcp_proof_blocks_promotion(tmp_path: Path) -> None:
    manifest = _bundle(tmp_path)
    adg_path = _adg_receipt_path(manifest)
    adg = json.loads(adg_path.read_text(encoding="utf-8"))
    adg.pop("startup_nonce")
    _write_json(adg_path, adg)

    decision = evaluate_manifest(manifest)

    assert decision.passed is False
    assert "ADG_STARTUP_NONCE_MISSING" in decision.reason_codes


def test_replay_baseline_regression_blocks_promotion(tmp_path: Path) -> None:
    manifest = _bundle(tmp_path)
    replay = json.loads((tmp_path / "replay.json").read_text())
    replay["baseline"] = {"status": "REGRESSION"}
    _write_json(tmp_path / "replay.json", replay)

    decision = evaluate_manifest(manifest)

    assert decision.passed is False
    assert "REPLAY_BASELINE_NOT_MATCH" in decision.reason_codes


def test_ci_wrapper_returns_nonzero_for_blocked_bundle(tmp_path: Path) -> None:
    manifest = _bundle(tmp_path, adg_ok=False)
    result = subprocess.run(
        [
            sys.executable,
            "ops_scripts/ci/check_eval_harness_promotion_evidence.py",
            "--manifest",
            str(manifest),
        ],
        cwd=Path(__file__).resolve().parents[4],
        text=True,
        capture_output=True,
        timeout=30,
        shell=False,
    )

    assert result.returncode == 1
    assert "ADG_TRANSPORT_NOT_OK" in result.stdout
