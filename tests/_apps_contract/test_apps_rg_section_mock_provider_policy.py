"""Contract tests: mock judges policy and offline Qwen stub on ``python -m apps_rg``."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.section_proof.mock_runtime_proof_policy import MOCK_JUDGES_REJECT_EXIT_CODE
from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.runtime_proof_layout import resolve_run_dir_from_pointer

REPO_ROOT = Path(__file__).resolve().parents[2]

_BASE_ENV = {"APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO": "1"}


def _env(extra: dict[str, str] | None = None) -> dict[str, str]:
    import os

    out = {**os.environ, **_BASE_ENV}
    if extra:
        out.update(extra)
    return out


@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_invalid_provider_rejected(lane: str) -> None:
    """``--provider mock`` must fast-fail at CLI parse/resolve (no lane dispatch)."""
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            lane,
            "--provider",
            "mock",
            "--allow-non-allow-exit-zero",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        env=_env(),
    )
    assert r.returncode == 2, (r.stdout, r.stderr)
    err = (r.stderr or "").lower()
    assert "invalid" in err and "provider" in err
    assert "mock" in err


@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_mock_judges_rejected_without_test_hatch_before_run(lane: str) -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            lane,
            "--provider",
            "qwen_vllm",
            "--mock-judges",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        env=_env(),
    )
    assert r.returncode == MOCK_JUDGES_REJECT_EXIT_CODE
    err = (r.stderr or "").lower()
    assert "cannot produce runtime certification evidence" in err or "mock judges cannot certify" in err
    assert "mock judges" in err


@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_allow_non_allow_exit_zero_does_not_bypass_mock_judge_block(lane: str) -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            lane,
            "--provider",
            "qwen_vllm",
            "--mock-judges",
            "--allow-non-allow-exit-zero",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        env=_env(),
    )
    assert r.returncode == MOCK_JUDGES_REJECT_EXIT_CODE


@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_offline_qwen_stub_with_mock_judges_hatch_writes_real_bucket_manifest(lane: str) -> None:
    cmd = [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        lane,
        "--provider",
        "qwen_vllm",
        "--mock-judges",
        "--allow-test-mock-judges",
        "--allow-non-allow-exit-zero",
    ]
    r = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=300,
        env=_env({"APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1"}),
    )
    assert r.returncode == 0, r.stderr
    rd = resolve_run_dir_from_pointer(REPO_ROOT, lane, "real")
    assert rd is not None, f"expected real-bucket run dir for {lane}"
    manifest = rd / "run_manifest.json"
    assert manifest.is_file()
    mf = json.loads(manifest.read_text(encoding="utf-8"))
    assert mf.get("runtime_generation_status") == "REAL_LLM"
    assert mf.get("proof_eligible") is not True
    l2_path = rd / "l2_output.json"
    assert l2_path.is_file()
    l2 = json.loads(l2_path.read_text(encoding="utf-8"))
    assert l2.get("runtime_generation_status") == "REAL_LLM"
    assert l2.get("proof_eligible") is not True


def test_lane_dispatch_build_parser_default_provider_is_qwen_vllm() -> None:
    """Legacy dispatch argparse defaults use qwen_vllm (mock provider removed)."""
    import importlib

    from apps_rg.l2_recipe.modular_resume_generation import LANE_DISPATCH_MODULES

    for mod in LANE_DISPATCH_MODULES:
        m = importlib.import_module(mod)
        bp_factory = m.__dict__.get("build_parser")
        if bp_factory is None:
            continue
        bp = bp_factory()
        ns = bp.parse_args([])
        assert ns.provider == "qwen_vllm", mod
