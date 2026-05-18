from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "headline"
_BASE_CMD = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "headline",
    "--provider",
    "mock",
    "--target-company",
    "Synthetic Enterprise Corp.",
    "--target-role",
    "SVP Engineering, Agentic AI Platforms",
    "--mock-judges",
    "--allow-test-mock-judges",
    "--allow-non-allow-exit-zero",
]


def _slice_subprocess_env() -> dict[str, str]:
    """Deterministic headline slice: offline Qwen contract stub (canonical ``build_mock_output`` JSON).

    Without this, a reachable local vLLM returns variable headlines (word count / self_check drift)
    and these contract tests become order- and environment-sensitive.
    """
    env = {**os.environ}
    env["APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"] = "1"
    return env


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _BASE_CMD + list(extra),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        env=_slice_subprocess_env(),
    )


def proof_run_dir_fallback() -> Path:
    """Resolve the latest headline proof run without subprocess stdout (last resort)."""
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir, resolve_run_dir_from_pointer

    rd = resolve_latest_mock_run_dir(REPO_ROOT, LANE_KEY)
    if rd is not None:
        return rd
    rd = resolve_run_dir_from_pointer(REPO_ROOT, LANE_KEY, "real")
    if rd is not None:
        return rd
    legacy = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / LANE_KEY
    if (legacy / "l2_output.json").is_file():
        return legacy
    raise AssertionError(
        f"No headline runtime proof artifacts for lane {LANE_KEY}; run "
        "`python -m apps_rg --section headline --provider mock` with stub env first."
    )


def proof_run_dir_from_result(result: subprocess.CompletedProcess[str]) -> Path:
    """Bind assertions to the proof directory for this CLI invocation (not `latest_mock_run`)."""
    last: Path | None = None
    for line in result.stdout.splitlines():
        if line.startswith("artifact_dir="):
            raw = line.split("=", 1)[1].strip()
            cand = Path(raw)
            cand = cand.resolve() if cand.is_absolute() else (REPO_ROOT / cand).resolve()
            last = cand
    if last is not None and (last / "l2_output.json").is_file():
        return last
    if last is not None:
        raise AssertionError(
            f"artifact_dir={last} missing l2_output.json; tail stdout={result.stdout[-1500:]!r}"
        )
    return proof_run_dir_fallback()


def load_json_from(run_dir: Path, name: str) -> object:
    return json.loads((run_dir / name).read_text(encoding="utf-8"))


def test_canonical_cli_executes_headline_lane():
    result = run_cmd()
    assert result.returncode == 0, (result.stderr, result.stdout)
    assert "HEADLINE_OUTPUT:" in result.stdout
    assert "WORD_COUNT:" in result.stdout


def test_stub_headline_format():
    result = run_cmd()
    assert result.returncode == 0, (result.stderr, result.stdout)
    rd = proof_run_dir_from_result(result)
    l2 = load_json_from(rd, "l2_output.json")
    hl = l2["headline_line"].strip()
    assert hl.count("|") == 3
    assert "\n" not in hl


def test_x2_gate_count():
    result = run_cmd()
    assert result.returncode == 0, (result.stderr, result.stdout)
    rd = proof_run_dir_from_result(result)
    x2 = load_json_from(rd, "x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 42
    assert x2["x2_failed"] == 0


def test_stub_word_count_range():
    result = run_cmd()
    assert result.returncode == 0, (result.stderr, result.stdout)
    rd = proof_run_dir_from_result(result)
    l2 = load_json_from(rd, "l2_output.json")
    from apps_rg.runtime.validators.headline_x2 import headline_word_count

    wc = headline_word_count(l2["headline_line"])
    assert 10 <= wc <= 13


def test_stub_x3_review_plumbing_with_mock_judges():
    result = run_cmd()
    assert result.returncode == 0, (result.stderr, result.stdout)
    rd = proof_run_dir_from_result(result)
    x3 = load_json_from(rd, "x3_disposition.json")
    assert x3["x3_code"] in ("X3_REVIEW_MOCKED_PLUMBING_ONLY", "X3_ALLOW")


def test_l6_shadow_offline_only():
    result = run_cmd()
    assert result.returncode == 0, (result.stderr, result.stdout)
    rd = proof_run_dir_from_result(result)
    l6 = load_json_from(rd, "l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["section_id"] == "headline"


def test_headline_overlay_files_exist():
    for rel in (
        "apps_rg/runtime/sections/headline_lane.py",
        "apps_rg/runtime/validators/headline_x2.py",
        "apps_rg/runtime/judges/headline_x1d.py",
        "apps_rg/runtime/exit/headline_x3.py",
        "apps_rg/runtime/shadow/headline_l6.py",
    ):
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    for rel in (
        "apps_rg/runtime/sections/headline_lane.py",
        "apps_rg/runtime/validators/headline_x2.py",
        "apps_rg/runtime/judges/headline_x1d.py",
        "apps_rg/runtime/exit/headline_x3.py",
        "apps_rg/runtime/shadow/headline_l6.py",
    ):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "agentic_core" not in text, rel
