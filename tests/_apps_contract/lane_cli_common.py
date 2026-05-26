"""Shared ``python -m apps_rg`` argv/env for generated-lane contract and live-proof tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGET_COMPANY = "Brown & Brown"
TARGET_ROLE = "SVP IT Strategy & Innovation"
JD_PATH = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF_PATH = "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"


def contract_env(*, live_l2: bool = False) -> dict[str, str]:
    """Live ``qwen_vllm`` contract runs — no mock provider, no offline Qwen stub."""
    env = {**os.environ, "APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO": "1"}
    for key in (
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "APPS_RG_TEST_HARNESS",
        "APPS_RG_MOCK_JUDGES",
        "APPS_RG_SKIP_QWEN_VLLM_HEALTH",
        "APPS_RG_L2_FORCE_STUB",
    ):
        env.pop(key, None)
    env["APPS_RG_ALLOW_STALE_TARGETING_SSOT"] = "1"
    env.setdefault("APPS_RG_ALLOW_DEFAULT_TARGETING_PATHS", "1")
    env["APPS_RG_L2_PROVIDER_MODE"] = "live_allowed"
    env["PYTEST_APPS_RG_LIVE_L2"] = "1" if live_l2 else env.get("PYTEST_APPS_RG_LIVE_L2", "1")
    chroma = REPO_ROOT / "data" / "cache" / "chromadb"
    if chroma.is_dir():
        env.setdefault("CHROMA_PERSIST_DIR", str(chroma.resolve()))
    return env


def base_canonical_argv(
    section: str,
    *,
    artifact_dir: str | None = None,
    target_company: str | None = None,
    target_role: str | None = None,
    jd: str | None = None,
    manual_brief: str | None = None,
) -> list[str]:
    argv = [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        section,
        "--target-company",
        target_company or TARGET_COMPANY,
        "--target-role",
        target_role or TARGET_ROLE,
        "--jd",
        jd or JD_PATH,
        "--manual-brief",
        manual_brief or BRIEF_PATH,
        "--provider",
        "qwen_vllm",
        "--allow-non-allow-exit-zero",
    ]
    if artifact_dir:
        argv.extend(["--artifact-dir", artifact_dir])
    return argv


def contract_harness_fast() -> bool:
    """When true, skip live ``python -m apps_rg`` subprocess contract lanes (dev/CI fast path)."""
    return os.environ.get("APPS_RG_CONTRACT_HARNESS_FAST", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def qwen_live_available() -> bool:
    from apps_rg.runtime.providers.competencies_live_provider_gate import qwen_vllm_http_models_preflight

    url = os.environ.get("VLLM_BASE_URL") or os.environ.get("APPS_RG_QWEN_OPENAI_BASE") or "http://127.0.0.1:8000/v1"
    ok, _detail, _snap = qwen_vllm_http_models_preflight(provider_url=url, timeout_s=10.0)
    return ok


def should_skip_contract_live_lane() -> bool:
    return contract_harness_fast() or not qwen_live_available()


def live_lane_skip_reason(section: str = "") -> str:
    if contract_harness_fast():
        return (
            f"APPS_RG_CONTRACT_HARNESS_FAST=1 — skipping live CLI lane{f' ({section})' if section else ''}; "
            "unset for nightly live proof"
        )
    return (
        f"{section or 'lane'} CLI contract tests require live qwen_vllm (mock provider removed)"
    )


def contract_live_pytestmark(section: str = ""):
    """Module-level mark: skip entire file when fast mode or vLLM unreachable."""
    import pytest

    return pytest.mark.skipif(should_skip_contract_live_lane(), reason=live_lane_skip_reason(section))


def run_lane_cli_once(
    section: str,
    *,
    run_key: str | None = None,
    timeout_s: int = 600,
    live_l2: bool = False,
    target_company: str | None = None,
    target_role: str | None = None,
    jd: str | None = None,
    manual_brief: str | None = None,
) -> Path:
    """Single subprocess lane run; reuse via module-scoped pytest fixture in pipeline modules."""
    art = contract_artifact_dir(section, run_key=run_key or f"pipeline_{section}")
    rel = art.relative_to(REPO_ROOT).as_posix()
    proc = run_lane_cli(
        section,
        artifact_dir=rel,
        timeout_s=timeout_s,
        live_l2=live_l2,
        target_company=target_company,
        target_role=target_role,
        jd=jd,
        manual_brief=manual_brief,
    )
    assert proc.returncode == 0, proc.stderr
    return artifact_dir_from_stdout(proc) if (proc.stdout or "").find("artifact_dir=") >= 0 else art


def contract_artifact_dir(section: str, *, run_key: str | None = None) -> Path:
    key = run_key or f"contract_{section}_{uuid.uuid4().hex[:10]}"
    art = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "contract_harness" / key
    art.mkdir(parents=True, exist_ok=True)
    return art


def run_lane_cli(
    section: str,
    *,
    artifact_dir: str | None = None,
    target_company: str | None = None,
    target_role: str | None = None,
    jd: str | None = None,
    manual_brief: str | None = None,
    timeout_s: int = 600,
    live_l2: bool = False,
) -> subprocess.CompletedProcess[str]:
    argv = base_canonical_argv(
        section,
        artifact_dir=artifact_dir,
        target_company=target_company,
        target_role=target_role,
        jd=jd,
        manual_brief=manual_brief,
    )
    return subprocess.run(
        argv,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        env=contract_env(live_l2=live_l2),
    )


def artifact_dir_from_stdout(proc: subprocess.CompletedProcess[str]) -> Path:
    for line in (proc.stdout or "").splitlines():
        if line.startswith("artifact_dir="):
            raw = line.split("=", 1)[1].strip()
            p = Path(raw)
            return p if p.is_absolute() else (REPO_ROOT / p).resolve()
    raise AssertionError(f"artifact_dir missing in stdout: {proc.stdout!r} stderr={proc.stderr!r}")


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
    "artifact_dir_from_stdout",
    "assert_critical_x2_passes",
    "assert_live_lane_product_proof",
    "base_canonical_argv",
    "contract_artifact_dir",
    "contract_env",
    "contract_harness_fast",
    "contract_live_pytestmark",
    "critical_gate_ids",
    "live_lane_skip_reason",
    "qwen_live_available",
    "resolve_latest_real_run_dir",
    "run_lane_cli",
    "run_lane_cli_once",
    "should_skip_contract_live_lane",
]
