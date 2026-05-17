"""Contract tests: mock provider is plumbing-only across all section dispatch CLIs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.l2_recipe.modular_resume_generation import LANE_DISPATCH_MODULES
from apps_rg.runtime.dispatch.mock_runtime_proof_policy import (
    MOCK_JUDGES_REJECT_EXIT_CODE,
    MOCK_PROVIDER_REJECT_EXIT_CODE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _lane_key_from_dispatch_module(mod: str) -> str:
    tail = mod.rsplit(".", 1)[-1]
    assert tail.endswith("_dispatch")
    return tail[: -len("_dispatch")]


@pytest.mark.parametrize("mod", LANE_DISPATCH_MODULES)
def test_mock_rejected_without_test_hatch_before_run(mod: str) -> None:
    r = subprocess.run(
        [sys.executable, "-m", mod, "--provider", "mock", "--allow-non-allow-exit-zero"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert r.returncode == MOCK_PROVIDER_REJECT_EXIT_CODE
    err = (r.stderr or "").lower()
    assert "cannot produce runtime proof" in err


@pytest.mark.parametrize("mod", LANE_DISPATCH_MODULES)
def test_allow_non_allow_exit_zero_does_not_bypass_mock_provider_block(mod: str) -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            mod,
            "--provider",
            "mock",
            "--mock-judges",
            "--allow-non-allow-exit-zero",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert r.returncode == MOCK_PROVIDER_REJECT_EXIT_CODE


@pytest.mark.parametrize("mod", LANE_DISPATCH_MODULES)
def test_mock_judges_rejected_without_test_hatch_before_run(mod: str) -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            mod,
            "--provider",
            "qwen_vllm",
            "--mock-judges",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert r.returncode == MOCK_JUDGES_REJECT_EXIT_CODE
    err = (r.stderr or "").lower()
    assert "cannot produce runtime proof" in err
    assert "mock judges" in err


@pytest.mark.parametrize("mod", LANE_DISPATCH_MODULES)
def test_allow_non_allow_exit_zero_does_not_bypass_mock_judge_block(mod: str) -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            mod,
            "--provider",
            "qwen_vllm",
            "--mock-judges",
            "--allow-non-allow-exit-zero",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert r.returncode == MOCK_JUDGES_REJECT_EXIT_CODE


@pytest.mark.parametrize("mod", LANE_DISPATCH_MODULES)
def test_mock_hatch_writes_proof_eligible_false_manifest(mod: str) -> None:
    lane = _lane_key_from_dispatch_module(mod)
    cmd = [
        sys.executable,
        "-m",
        mod,
        "--provider",
        "mock",
        "--allow-test-mock-provider",
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
    )
    assert r.returncode == 0, r.stderr
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO_ROOT, lane)
    assert rd is not None, f"expected mock run dir for {lane}"
    manifest = rd / "run_manifest.json"
    assert manifest.is_file()
    mf = json.loads(manifest.read_text(encoding="utf-8"))
    assert mf.get("runtime_generation_status") == "MOCKED"
    assert mf.get("proof_eligible") is False
    assert mf.get("proof_scope") == "plumbing_only"
    assert mf.get("test_only_mock_provider") is True
    assert mf.get("runtime_certification") is False
    assert mf.get("judge_proof_eligible") is False
    assert mf.get("x1d_runtime_status") == "MOCKED"
    assert mf.get("test_only_mock_judges") is True
    l2_path = rd / "l2_output.json"
    assert l2_path.is_file()
    l2 = json.loads(l2_path.read_text(encoding="utf-8"))
    assert l2.get("proof_eligible") is False
    assert l2.get("judge_proof_eligible") is False
    assert l2.get("x1d_runtime_status") == "MOCKED"


def test_lane_cli_default_provider_is_qwen_vllm() -> None:
    import importlib

    for mod in LANE_DISPATCH_MODULES:
        bp = importlib.import_module(mod).build_parser()
        ns = bp.parse_args([])
        assert ns.provider == "qwen_vllm", mod
