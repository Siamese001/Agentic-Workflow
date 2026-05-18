from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "unify_narrative"
CMD = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "unify_narrative",
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


def test_mock_dispatch_runs():
    result = run_cmd()
    assert result.returncode == 0, result.stderr
    assert "L2_UNIFY_NARRATIVE_OUTPUT:" in result.stdout


def test_mock_one_sentence():
    run_cmd()
    l2 = load_json("l2_output.json")
    assert l2["narrative_sentence"].count(".") >= 1
    text = l2["narrative_sentence"].strip()
    assert "\n" not in text or len(text.split(".")) <= 2


def test_x2_gate_count():
    run_cmd()
    x2 = load_json("x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 35
    assert x2["x2_failed"] == 0


def test_mock_x3_review_plumbing():
    run_cmd()
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_l6_flags():
    run_cmd()
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["human_label_required"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"


def _minimal_section_input_usage_ledger() -> dict[str, Any]:
    return {
        "schema": "section_input_usage_ledger_v1",
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": False,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {
            "claims_with_targeting_input_in_source_fact_ids": 0,
            "claims_with_context_input_in_source_fact_ids": 0,
        },
    }


def test_x3_soft_fail_unit():
    from apps_rg.runtime.exit.unify_narrative_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="One sentence.",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_json_parse_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 1.0,
                "normalized_threshold": 0.8,
            },
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 0.92,
                "normalized_threshold": 0.8,
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": False,
                "normalized_score": 0.72,
                "normalized_threshold": 0.8,
            },
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=_minimal_section_input_usage_ledger(),
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"


def test_unify_overlay_files_exist():
    for rel in (
        "apps_rg/runtime/dispatch/unify_narrative_dispatch.py",
        "apps_rg/runtime/validators/unify_narrative_x2.py",
        "apps_rg/runtime/judges/unify_narrative_x1d.py",
        "apps_rg/runtime/exit/unify_narrative_x3.py",
        "apps_rg/runtime/shadow/unify_narrative_l6.py",
    ):
        assert (REPO_ROOT / rel).exists()
