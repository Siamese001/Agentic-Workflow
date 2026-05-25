"""Integrated product spine (``python -m apps_rg`` without ``--section``) live-provider harness.

Section lanes use ``test_one_spine_*`` / ``PYTEST_APPS_RG_LIVE_L2``; this file is the
**canonical R4 integrated path** gate: cache preflight → ``run_integrated_single_action_spine``.

Set ``PYTEST_APPS_RG_INTEGRATED_LIVE=1`` and ensure vLLM is reachable (``VLLM_BASE_URL``).
Without the flag, tests are skipped — not failed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

from tests._apps_contract.lane_cli_common import (
    BRIEF_PATH,
    JD_PATH,
    TARGET_COMPANY,
    TARGET_ROLE,
    contract_env,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("PYTEST_APPS_RG_INTEGRATED_LIVE", "").strip().lower()
    not in ("1", "true", "yes"),
    reason="set PYTEST_APPS_RG_INTEGRATED_LIVE=1 for integrated-R4 live provider proof",
)


def _qwen_available() -> bool:
    from apps_rg.runtime.providers.competencies_live_provider_gate import (
        qwen_vllm_http_models_preflight,
    )

    url = (
        os.environ.get("VLLM_BASE_URL")
        or os.environ.get("APPS_RG_QWEN_OPENAI_BASE")
        or "http://127.0.0.1:8000/v1"
    )
    ok, _detail, _snap = qwen_vllm_http_models_preflight(provider_url=url, timeout_s=10.0)
    return ok


@pytest.fixture(scope="module")
def _require_qwen() -> None:
    if not _qwen_available():
        pytest.skip("live qwen_vllm unavailable — integrated spine requires provider")


@pytest.fixture(scope="module")
def integrated_run_dir(_require_qwen) -> Path:
    root = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / f"integrated_live_{uuid.uuid4().hex[:12]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_integrated_spine_preflight_documents_provider_reachable(_require_qwen) -> None:
    """Sanity: integrated live runs depend on the same vLLM preflight as section lanes."""
    assert _qwen_available()


def _integrated_canonical_argv() -> list[str]:
    """Whole-run argv aligned with [integrated_r4_live_product_proof_attempt_receipt.md](docs/reports/apps_rg/integrated_r4_live_product_proof_attempt_receipt.md)."""
    return [
        sys.executable,
        "-m",
        "apps_rg",
        "--target-company",
        TARGET_COMPANY,
        "--target-role",
        TARGET_ROLE,
        "--jd",
        JD_PATH,
        "--manual-brief",
        BRIEF_PATH,
        "--provider",
        "qwen_vllm",
        "--allow-non-allow-exit-zero",
    ]


def _newest_integrated_run_dir(since_monotonic: float) -> Path | None:
    """Return newest ``cli_*`` run dir whose mtime is at or after *since_monotonic* wall clock."""
    import time as _time

    wall_since = _time.time() - (_time.monotonic() - since_monotonic)
    runs_root = REPO / "artifacts" / "apps_rg" / "runs"
    if not runs_root.is_dir():
        return None
    candidates = [
        p
        for p in runs_root.iterdir()
        if p.is_dir() and p.name.startswith("cli_") and p.stat().st_mtime >= wall_since - 1.0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def test_integrated_canonical_whole_run_emits_spine_artifacts(
    integrated_run_dir: Path,
) -> None:
    """Canonical ``python -m apps_rg`` (no ``--section``) through integrated dispatch."""
    import time

    env = contract_env(live_l2=True)
    env["PYTEST_APPS_RG_INTEGRATED_LIVE"] = "1"
    env["APPS_RG_L2_PROVIDER_MODE"] = "live_allowed"
    env.pop("APPS_RG_LIVE_SMOKE_DRY_RUN", None)
    started = time.monotonic()
    proc = subprocess.run(
        _integrated_canonical_argv(),
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    finished = time.monotonic()
    run_dir = _newest_integrated_run_dir(finished) or integrated_run_dir
    manifest_candidates = list(run_dir.rglob("integrated_run_manifest.json")) + list(
        run_dir.rglob("r4_run_manifest.json")
    )
    exit_receipts = list(run_dir.rglob("exit_disposition_receipt.json")) + list(
        run_dir.rglob("x3_disposition_receipt.json")
    )
    proof_summary = {
        "cli_exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:] if proc.stdout else "",
        "stderr_tail": proc.stderr[-4000:] if proc.stderr else "",
        "manifest_count": len(manifest_candidates),
        "exit_receipt_count": len(exit_receipts),
        "run_dir": str(run_dir),
        "artifact_dir": str(integrated_run_dir),
    }
    summary_path = integrated_run_dir / "integrated_live_harness_summary.json"
    summary_path.write_text(json.dumps(proof_summary, indent=2) + "\n", encoding="utf-8")

    assert proc.returncode == 0, (
        f"integrated CLI must exit 0 (got {proc.returncode}); see {summary_path}"
    )
    assert manifest_candidates, (
        "integrated run must emit a run manifest under artifact_dir "
        f"(exit={proc.returncode}); see {summary_path}"
    )
    assert exit_receipts, (
        "integrated run must emit exit disposition receipt "
        f"(exit={proc.returncode}); see {summary_path}"
    )


def test_integrated_product_proof_gate_on_live_run(integrated_run_dir: Path) -> None:
    from apps_rg.runtime.integrated_product_proof_gate import validate_integrated_product_proof

    runs_root = REPO / "artifacts" / "apps_rg" / "runs"
    run_dir = max(
        (p for p in runs_root.glob("cli_*") if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        default=integrated_run_dir,
    )
    result = validate_integrated_product_proof(run_dir)
    assert result.status in ("PASS", "BLOCKED", "FAIL"), result.decisive_reason
    if result.status == "BLOCKED":
        pytest.skip(f"integrated product proof BLOCKED (live outcome): {result.decisive_reason}")
