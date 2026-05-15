from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "headline"
CMD = [
    sys.executable,
    "-m",
    "apps_rg.runtime.dispatch.headline_dispatch",
    "--allow-non-allow-exit-zero",
]


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CMD + list(extra), cwd=REPO_ROOT, text=True, capture_output=True, timeout=180)


def mock_artifacts_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO_ROOT, LANE_KEY)
    if rd is not None:
        return rd
    legacy = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / LANE_KEY
    if (legacy / "l2_output.json").is_file():
        return legacy
    raise AssertionError(f"No mock artifacts for lane {LANE_KEY}; run headline_dispatch --provider mock first")


def load_json(name: str):
    return json.loads((mock_artifacts_dir() / name).read_text(encoding="utf-8"))


def test_mock_dispatch_executes():
    result = run_cmd("--provider", "mock", "--mock-judges")
    assert result.returncode == 0, result.stderr
    assert "HEADLINE_OUTPUT:" in result.stdout
    assert "WORD_COUNT:" in result.stdout


def test_mock_headline_format():
    run_cmd("--provider", "mock", "--mock-judges")
    l2 = load_json("l2_output.json")
    hl = l2["headline_line"].strip()
    assert hl.count("|") == 2
    assert "\n" not in hl


def test_x2_gate_count():
    run_cmd("--provider", "mock", "--mock-judges")
    x2 = load_json("x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 17
    assert x2["x2_failed"] == 0


def test_mock_word_count_range():
    run_cmd("--provider", "mock", "--mock-judges")
    l2 = load_json("l2_output.json")
    from apps_rg.runtime.validators.headline_x2 import headline_word_count

    wc = headline_word_count(l2["headline_line"])
    assert 8 <= wc <= 11


def test_mock_x3_review_plumbing():
    run_cmd("--provider", "mock", "--mock-judges")
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_l6_shadow_offline_only():
    run_cmd("--provider", "mock", "--mock-judges")
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["section_id"] == "headline"


def test_headline_overlay_files_exist():
    for rel in (
        "apps_rg/runtime/dispatch/headline_dispatch.py",
        "apps_rg/runtime/validators/headline_x2.py",
        "apps_rg/runtime/judges/headline_x1d.py",
        "apps_rg/runtime/exit/headline_x3.py",
        "apps_rg/runtime/shadow/headline_l6.py",
    ):
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    for rel in (
        "apps_rg/runtime/dispatch/headline_dispatch.py",
        "apps_rg/runtime/validators/headline_x2.py",
        "apps_rg/runtime/judges/headline_x1d.py",
        "apps_rg/runtime/exit/headline_x3.py",
        "apps_rg/runtime/shadow/headline_l6.py",
    ):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "agentic_core" not in text, rel
