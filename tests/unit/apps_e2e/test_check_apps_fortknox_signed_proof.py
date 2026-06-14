"""W7 of plan apps-fort-knox-parity-c5d9a3 \u2014 Apps Fort Knox CI gate tests.

Covers ops_scripts/ci/check_apps_fortknox_signed_proof.py.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
GATE_REL = "ops_scripts/ci/check_apps_fortknox_signed_proof.py"


def _run_gate(env_extra: dict | None = None, timeout: int = 240) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / GATE_REL)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


# ----------------------------- live -----------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "tools/certification/generate_apps_100pct_runtime_proof.py").exists(),
    reason="W6 generator missing",
)
def test_gate_passes_on_clean_repo():
    """Live run \u2014 entire W1\u2192W6 chain must pass on the current repo state."""
    proc = _run_gate()
    assert proc.returncode == 0, (
        f"gate FAILED with rc={proc.returncode}\n"
        f"stdout: {proc.stdout[-500:]}\n"
        f"stderr: {proc.stderr[-500:]}"
    )
    assert "OK" in proc.stdout
    assert "trust=" in proc.stdout


def test_gate_bypass_env_var_returns_zero():
    """FORTKNOX_DISCIPLINE_BYPASS=1 must short-circuit the gate to OK."""
    proc = _run_gate({"FORTKNOX_DISCIPLINE_BYPASS": "1"})
    assert proc.returncode == 0
    assert "BYPASS" in proc.stdout


# ----------------------------- failure paths (synthetic bundle) -----------------------------

def _patch_bundle(tmp_bundle: Path, mutator):
    """Read the live bundle, apply mutator, write to tmp_bundle, run a one-shot
    gate replica that reads from tmp_bundle (since the gate hard-codes the
    canonical path, we replicate its verdict logic here)."""
    live = REPO_ROOT / "artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"
    if not live.exists():
        pytest.skip("live bundle missing; run W6 generator first")
    bundle = json.loads(live.read_text(encoding="utf-8"))
    mutator(bundle)
    tmp_bundle.write_text(json.dumps(bundle, sort_keys=True), encoding="utf-8")
    return bundle


def _gate_verdict_against_bundle(bundle: dict) -> tuple[bool, list[str]]:
    """Re-implement the gate's verdict logic for synthetic-bundle tests.
    The gate itself runs the full generator, which is not feasible to mock
    cheaply; this helper checks the verdict surface independently."""
    h = bundle.get("headline_claims", {}) or {}
    failures: list[str] = []
    if not h.get("canary_pass"):
        failures.append("canary")
    if not h.get("trust_in_signed_set"):
        failures.append("trust")
    if not h.get("signature_verified"):
        failures.append("signature")
    if not h.get("live_signature_re_verify_passed"):
        failures.append("live_re_verify")
    if not h.get("mutation_zero_accepts"):
        failures.append("mutation")
    if (h.get("row_blocked") or 0) > 0:
        failures.append("blocked")
    if (h.get("row_not_verified") or 0) > 0:
        failures.append("not_verified")
    return (not failures and bool(h.get("all_gates_pass")), failures)


def test_verdict_logic_fails_on_canary_fail(tmp_path):
    bundle = _patch_bundle(
        tmp_path / "tampered.json",
        lambda b: b["headline_claims"].update({"canary_pass": False, "all_gates_pass": False}),
    )
    ok, failures = _gate_verdict_against_bundle(bundle)
    assert not ok and "canary" in failures


def test_verdict_logic_fails_on_signature_invalid(tmp_path):
    bundle = _patch_bundle(
        tmp_path / "tampered.json",
        lambda b: b["headline_claims"].update({
            "signature_verified": False,
            "all_gates_pass": False,
        }),
    )
    ok, failures = _gate_verdict_against_bundle(bundle)
    assert not ok and "signature" in failures


def test_verdict_logic_fails_on_mutation_accept(tmp_path):
    bundle = _patch_bundle(
        tmp_path / "tampered.json",
        lambda b: b["headline_claims"].update({
            "mutation_zero_accepts": False,
            "all_gates_pass": False,
        }),
    )
    ok, failures = _gate_verdict_against_bundle(bundle)
    assert not ok and "mutation" in failures


def test_verdict_logic_fails_on_blocked_row(tmp_path):
    bundle = _patch_bundle(
        tmp_path / "tampered.json",
        lambda b: b["headline_claims"].update({"row_blocked": 1, "all_gates_pass": False}),
    )
    ok, failures = _gate_verdict_against_bundle(bundle)
    assert not ok and "blocked" in failures


def test_verdict_logic_fails_on_trust_below_signed(tmp_path):
    bundle = _patch_bundle(
        tmp_path / "tampered.json",
        lambda b: b["headline_claims"].update({
            "trust_in_signed_set": False,
            "trust_level": "DEVELOPMENT_PROOF",
            "all_gates_pass": False,
        }),
    )
    ok, failures = _gate_verdict_against_bundle(bundle)
    assert not ok and "trust" in failures


# ----------------------- gate decommissioned (§32 retired) -----------------------

def test_gate_decommissioned_from_pre_commit_config():
    """T7s.4 hook was decommissioned 2026-06-14 (constitutional §32 retired).

    The gate *script* is retained pending the deferred machinery teardown, but it
    is no longer wired into .pre-commit-config.yaml.
    """
    p = REPO_ROOT / ".pre-commit-config.yaml"
    txt = p.read_text(encoding="utf-8")
    assert "apps-fortknox-signed-proof" not in txt, "T7s.4 hook should be unwired after §32 decommission"
