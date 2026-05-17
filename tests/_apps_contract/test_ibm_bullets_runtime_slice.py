from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "ibm_bullets"
CMD = [sys.executable, "-m", "apps_rg.runtime.dispatch.ibm_bullets_dispatch", "--allow-non-allow-exit-zero"]


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
    raise AssertionError(f"No mock artifacts for lane {LANE_KEY}; run mock dispatch first")


def load_json(name: str):
    return json.loads((mock_artifacts_dir() / name).read_text(encoding="utf-8"))


def test_mock_dispatch_executes():
    result = run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    assert result.returncode == 0, result.stderr
    assert "IBM_BULLETS_OUTPUT:" in result.stdout


def test_mock_outputs_five_bullets():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    l2 = load_json("l2_output.json")
    assert len(l2["bullets"]) == 5
    ids = [b["bullet_id"] for b in l2["bullets"]]
    assert ids == [
        "bul_ibm_001",
        "bul_ibm_002",
        "bul_ibm_003",
        "bul_ibm_004",
        "bul_ibm_005",
    ]


def test_rewrite_distribution_default():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    dist = load_json("rewrite_distribution.json")
    assert dist["HEAVY"] == 0
    assert dist["MODERATE"] == 3
    assert dist["LIGHT_PROTECTED"] == 2
    assert dist["total"] == 5


def test_mocked_judges_review_only():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_x2_all_gates_pass_on_mock():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    x2 = load_json("x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 20
    assert x2["x2_failed"] == 0


def test_l6_shadow_offline_only():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["human_label_required"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"


def test_ibm_overlay_files_exist():
    expected = [
        "apps_rg/runtime/dispatch/ibm_bullets_dispatch.py",
        "apps_rg/runtime/validators/ibm_bullets_x2.py",
        "apps_rg/runtime/judges/ibm_bullets_x1d.py",
        "apps_rg/runtime/exit/ibm_bullets_x3.py",
        "apps_rg/runtime/shadow/ibm_bullets_l6.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    overlay = [
        REPO_ROOT / "apps_rg/runtime/dispatch/ibm_bullets_dispatch.py",
        REPO_ROOT / "apps_rg/runtime/validators/ibm_bullets_x2.py",
        REPO_ROOT / "apps_rg/runtime/judges/ibm_bullets_x1d.py",
        REPO_ROOT / "apps_rg/runtime/exit/ibm_bullets_x3.py",
        REPO_ROOT / "apps_rg/runtime/shadow/ibm_bullets_l6.py",
    ]
    for path in overlay:
        text = path.read_text(encoding="utf-8")
        assert "agentic_core" not in text, path


def test_core_metrics_in_mock_output():
    run_cmd("--provider", "mock", "--allow-test-mock-provider", "--mock-judges")
    l2 = load_json("l2_output.json")
    joined = " ".join(b["bullet_text"] for b in l2["bullets"])
    assert "$15M" in joined or "$15m" in joined.lower()
    assert "99.9%" in joined
    assert "30%" in joined
    assert "25%" in joined
    assert "50%" in joined


def test_canonicalize_bul_ibm_double_underscore_source_fact_id():
    from apps_rg.runtime.dispatch.ibm_bullets_dispatch import _canonicalize_bul_ibm_source_fact_id

    assert _canonicalize_bul_ibm_source_fact_id("bul_ibm__002") == "bul_ibm_002"
    assert _canonicalize_bul_ibm_source_fact_id("bul_ibm____003") == "bul_ibm_003"
