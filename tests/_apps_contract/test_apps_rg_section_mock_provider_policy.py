"""Contract tests: mock judges policy and offline Qwen stub on ``python -m apps_rg``."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
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
def test_mock_judges_cli_flag_rejected_on_product_entry(lane: str) -> None:
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
    assert r.returncode == 2, (r.stdout, r.stderr)
    err = (r.stderr or "").lower()
    assert "mock judges" in err or "mock-judges" in err
    assert "always live" in err or "production cli" in err


@pytest.mark.parametrize("lane", GENERATED_LANES)
def test_allow_non_allow_exit_zero_does_not_bypass_mock_judge_cli_block(lane: str) -> None:
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
    assert r.returncode == 2, (r.stdout, r.stderr)
    combined = ((r.stderr or "") + (r.stdout or "")).lower()
    assert "mock-judges" in combined


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
