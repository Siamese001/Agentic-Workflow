"""Shared ``python -m apps_rg`` argv/env for generated-lane contract and live-proof tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGET_COMPANY = "Brown & Brown"
TARGET_ROLE = "SVP IT Strategy & Innovation"
JD_PATH = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF_PATH = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"


def contract_env(*, live_l2: bool = False) -> dict[str, str]:
    """Environment for subprocess contract runs (no mock provider; stub disabled in product)."""
    env = {**os.environ, "APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO": "1"}
    env.pop("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", None)
    if live_l2:
        env["PYTEST_APPS_RG_LIVE_L2"] = "1"
    return env


def base_canonical_argv(section: str, *, artifact_dir: str | None = None) -> list[str]:
    argv = [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        section,
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
    if artifact_dir:
        argv.extend(["--artifact-dir", artifact_dir])
    return argv


def qwen_live_available() -> bool:
    from apps_rg.runtime.providers.competencies_live_provider_gate import qwen_vllm_http_models_preflight

    url = os.environ.get("VLLM_BASE_URL") or os.environ.get("APPS_RG_QWEN_OPENAI_BASE") or "http://127.0.0.1:8000/v1"
    ok, _detail, _snap = qwen_vllm_http_models_preflight(provider_url=url, timeout_s=10.0)
    return ok


def run_lane_cli(
    section: str,
    *,
    artifact_dir: str | None = None,
    timeout_s: int = 600,
    live_l2: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        base_canonical_argv(section, artifact_dir=artifact_dir),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        env=contract_env(live_l2=live_l2),
    )


def resolve_latest_real_run_dir(section: str) -> Path | None:
    from apps_rg.runtime.runtime_proof_layout import resolve_accepted_real_rollup_run_dir

    rd, _tag = resolve_accepted_real_rollup_run_dir(REPO_ROOT, section)
    return rd


def critical_gate_ids(section: str) -> frozenset[str]:
    from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane

    return spec_for_lane(section).critical_gates


def assert_critical_x2_passes(run_dir: Path, section: str) -> None:
    x2_path = run_dir / "x2_gate_outputs.json"
    assert x2_path.is_file(), f"missing x2_gate_outputs.json under {run_dir}"
    x2 = json.loads(x2_path.read_text(encoding="utf-8"))
    gates = {g["gate_id"]: g for g in x2.get("gates") or []}
    required = critical_gate_ids(section)
    missing = sorted(required - set(gates))
    assert not missing, f"missing critical gates: {missing}"
    failed = [gid for gid in required if not gates[gid].get("pass")]
    assert not failed, f"critical X2 failures: {[(g, gates[g].get('failure_reason')) for g in failed]}"


def assert_live_lane_product_proof(run_dir: Path, section: str) -> None:
    """REAL_LLM + product PASS + critical X2; X3 ALLOW or judge-blocked REVIEW only."""
    assert_critical_x2_passes(run_dir, section)
    l2 = json.loads((run_dir / "l2_output.json").read_text(encoding="utf-8"))
    assert l2.get("runtime_generation_status") == "REAL_LLM", l2
    assert l2.get("product_quality_status") == "PASS", l2
    x3 = json.loads((run_dir / "x3_disposition.json").read_text(encoding="utf-8"))
    code = str(x3.get("x3_code") or x3.get("x3_disposition") or "")
    assert code in ("X3_ALLOW", "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"), x3
    if code != "X3_ALLOW":
        assert not x3.get("x2_failed_gates"), x3


__all__ = [
    "BRIEF_PATH",
    "JD_PATH",
    "REPO_ROOT",
    "TARGET_COMPANY",
    "TARGET_ROLE",
    "assert_critical_x2_passes",
    "base_canonical_argv",
    "contract_env",
    "critical_gate_ids",
    "resolve_latest_real_run_dir",
    "assert_live_lane_product_proof",
    "qwen_live_available",
    "run_lane_cli",
]
