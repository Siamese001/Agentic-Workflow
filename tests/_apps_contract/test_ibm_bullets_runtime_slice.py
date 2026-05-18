from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_CMD = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "ibm_bullets",
    "--target-company",
    "Synthetic Enterprise Corp.",
    "--target-role",
    "SVP Engineering, Agentic AI Platforms",
    "--provider",
    "mock",
    "--mock-judges",
    "--allow-test-mock-judges",
    "--allow-non-allow-exit-zero",
]


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CANONICAL_CMD + list(extra), cwd=REPO_ROOT, text=True, capture_output=True, timeout=180)


def _artifact_dir_from_stdout(proc: subprocess.CompletedProcess[str]) -> Path:
    """Prefer stdout ``artifact_dir=`` over ``latest_mock_run`` pointers (xdist-safe)."""
    for line in (proc.stdout or "").splitlines():
        if line.startswith("artifact_dir="):
            return Path(line.split("=", 1)[1].strip())
    raise AssertionError(f"artifact_dir missing in stdout: {proc.stdout!r} stderr={proc.stderr!r}")


def load_json_at(rd: Path, name: str):
    return json.loads((rd / name).read_text(encoding="utf-8"))


def test_deprecated_dispatch_module_exits_2():
    """``python -m apps_rg.runtime.dispatch.ibm_bullets_dispatch`` exits fail-closed; use ``--section ibm_bullets``."""
    r = subprocess.run(
        [sys.executable, "-m", "apps_rg.runtime.dispatch.ibm_bullets_dispatch"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 2, r.stderr
    blob = (r.stderr + r.stdout).lower()
    assert "deprecated" in blob or "ibm_bullets" in blob


def test_mock_dispatch_executes():
    result = run_cmd()
    assert result.returncode == 0, result.stderr
    assert "IBM_BULLETS_OUTPUT:" in result.stdout


def test_mock_outputs_five_bullets():
    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc)
    l2 = load_json_at(rd, "l2_output.json")
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
    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc)
    dist = load_json_at(rd, "rewrite_distribution.json")
    assert dist["HEAVY"] == 0
    assert dist["MODERATE"] == 3
    assert dist["LIGHT_PROTECTED"] == 2
    assert dist["total"] == 5


def test_mocked_judges_review_only():
    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc)
    x3 = load_json_at(rd, "x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_x2_all_gates_pass_on_mock():
    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc)
    x2 = load_json_at(rd, "x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 31
    assert x2["x2_failed"] == 0


def test_l6_shadow_offline_only():
    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc)
    l6 = load_json_at(rd, "l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["human_label_required"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"
    assert l6.get("observer_law_assertion")
    assert l6.get("future_run_only_assertion") is True
    assert l6.get("current_run_mutation_assertion") is False
    assert l6.get("durable_write_assertion") is False
    assert l6.get("proof_eligible") is False
    assert l6.get("proof_scope") == "plumbing_only"
    assert l6.get("authorization_scope") == "PLUMBING_ONLY"
    assert isinstance(l6.get("mocked_judges"), list)
    assert l6.get("no_runtime_approval_authority_assertion") is True
    assert l6.get("no_current_run_mutation_assertion") is True
    cal = l6.get("foundation_proof_calibration") or {}
    assert cal.get("foundation_proof_model_id") == "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1"
    assert cal.get("treatment_profile") == "REWRITE_FROM_FACT_POOL_CONSTRAINED"
    assert cal.get("taxonomy_label_prefix_gate_pass") is True
    assert cal.get("unify_bullet_overlap_risk_level") == "none"
    assert cal.get("x2_gate_summary", {}).get("x2_no_taxonomy_label_prefix_in_display_text") is True
    summ = l6.get("allowed_fact_ids_summary") or {}
    assert summ.get("allowed_fact_ids_sorted")
    assert l6.get("claim_ledger_summary", {}).get("row_count", 0) >= 5


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
    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc)
    l2 = load_json_at(rd, "l2_output.json")
    joined = " ".join(b["bullet_text"] for b in l2["bullets"])
    assert "$15M" in joined or "$15m" in joined.lower()
    assert "99.9%" in joined
    assert "30%" in joined
    assert "25%" in joined
    assert "50%" in joined


def test_canonicalize_bul_ibm_double_underscore_source_fact_id():
    from apps_rg.runtime.sections.ibm_bullets_lane import _canonicalize_bul_ibm_source_fact_id

    assert _canonicalize_bul_ibm_source_fact_id("bul_ibm__002") == "bul_ibm_002"
    assert _canonicalize_bul_ibm_source_fact_id("bul_ibm____003") == "bul_ibm_003"


def test_mock_provider_runtime_proof_surfaces_single_run():
    """Single subprocess: bucket path, manifest, RUN_BUNDLE_INDEX, CLI summary lines."""
    from apps_rg.runtime.cli_section_execution_report import parse_cli_execution_summary_block

    proc = run_cmd()
    assert proc.returncode == 0, proc.stderr
    rd = _artifact_dir_from_stdout(proc).resolve()
    rel = rd.relative_to(REPO_ROOT).as_posix()
    assert "/runtime_proofs/ibm_bullets/mock/" in rel

    mf = load_json_at(rd, "run_manifest.json")
    assert mf.get("proof_eligible") is False
    assert mf.get("proof_scope") == "plumbing_only"
    assert mf.get("artifact_namespace_class") == "NON_PROOF_PLUMBING"
    assert mf.get("test_only_mock_judges") is True

    idx = load_json_at(rd, "RUN_BUNDLE_INDEX.json")
    assert idx.get("proof_eligible") is False
    assert idx.get("proof_scope") == "plumbing_only"

    parsed = parse_cli_execution_summary_block(proc.stdout)
    assert parsed.get("STATUS") == "PASS_NONCERTIFYING_RUNTIME_PROOF"
    assert parsed.get("PROOF_STATUS") == "NOT_PROOF_ELIGIBLE"
    assert parsed.get("PRODUCT_STATUS", "").startswith("X3_")
    assert parsed.get("COMMAND_STATUS") == "PASS"


def test_mock_provider_stores_under_mock_bucket():
    test_mock_provider_runtime_proof_surfaces_single_run()


def test_runtime_manifest_proof_accounting_non_proof():
    test_mock_provider_runtime_proof_surfaces_single_run()


def test_run_bundle_index_merges_proof_accounting():
    test_mock_provider_runtime_proof_surfaces_single_run()


def test_cli_execution_summary_explicit_non_proof_labels():
    test_mock_provider_runtime_proof_surfaces_single_run()


def test_lane_proof_bundle_mock_judge_hatch_and_offline_stub():
    from types import SimpleNamespace

    from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
    from apps_rg.runtime.section_proof.mock_runtime_proof_policy import compute_lane_proof_bundle

    class X3Allow:
        x3_code = "X3_ALLOW"
        pass_ = True
        authorization_scope = "PRODUCT_QUALITY"

    judge = {
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "normalized_score": 0.9,
        "normalized_threshold": 0.5,
        "provider_key": "openai_chatgpt",
    }
    x2 = [{"gate_id": "g1", "pass": True}]
    args = SimpleNamespace(
        mock_judges=False,
        allow_test_mock_judges=True,
        allow_non_allow_exit_zero=False,
        provider="qwen_vllm",
        allow_test_mock_provider=False,
    )
    hatch_bundle = compute_lane_proof_bundle(
        args,
        runtime_generation_status="REAL_LLM",
        x1d_judges=[judge],
        x2_gates=x2,
        x3=X3Allow(),
        offline_contract_stub_used=False,
    )
    assert hatch_bundle["proof_eligible"] is False
    assert hatch_bundle["proof_scope"] == "plumbing_only"

    stub_bundle = compute_lane_proof_bundle(
        args,
        runtime_generation_status=OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
        x1d_judges=[judge],
        x2_gates=x2,
        x3=X3Allow(),
        offline_contract_stub_used=True,
    )
    assert stub_bundle["provider_proof_eligible"] is False
    assert stub_bundle["runtime_generation_status_class"] == "OFFLINE_CONTRACT_STUB"


def test_ibm_bullet_taxonomy_prefix_detector():
    from apps_rg.runtime.validators.ibm_bullets_x2 import ibm_bullet_text_has_taxonomy_label_prefix

    assert ibm_bullet_text_has_taxonomy_label_prefix(
        "AI and Data Platform Architecture: Architected cloud-native AI."
    )
    assert ibm_bullet_text_has_taxonomy_label_prefix("Cloud Modernization: Led migration from legacy.")
    assert not ibm_bullet_text_has_taxonomy_label_prefix(
        "Architected cloud-native AI and analytics platforms supporting regulated enterprise decision systems."
    )


def test_provider_request_dict_redacts_bearer_substrings():
    import json

    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderRequest

    req = ProviderRequest(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_url="http://127.0.0.1:8000/v1/chat?api_key=supersecret",
        model="m",
        temperature=0.4,
        max_tokens=10,
        timeout_seconds=30,
        prompt_hash="p",
        input_payload_hash="i",
        mock_fallback_allowed=False,
    )
    dumped = json.dumps(req.to_dict())
    assert "supersecret" not in dumped
    assert "?" not in dumped  # query stripped from artifact URL
