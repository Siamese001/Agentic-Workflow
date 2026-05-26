from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT,
    artifact_dir_from_stdout,
    assert_live_lane_product_proof,
    contract_artifact_dir,
    qwen_live_available,
    run_lane_cli,
)

pytestmark = pytest.mark.skipif(
    not qwen_live_available(),
    reason="unify_narrative runtime slice tests require live qwen_vllm",
)

LANE_KEY = "unify_narrative"
_SYNTHETIC_COMPANY = "Synthetic Enterprise Corp."
_SYNTHETIC_ROLE = "SVP Engineering, Agentic AI Platforms"
_CACHED_RD: Path | None = None


def _run_contract() -> Path:
    global _CACHED_RD
    if _CACHED_RD is not None:
        return _CACHED_RD
    art = contract_artifact_dir(LANE_KEY)
    rel = art.relative_to(REPO_ROOT).as_posix()
    proc = run_lane_cli(
        LANE_KEY,
        artifact_dir=rel,
        target_company=_SYNTHETIC_COMPANY,
        target_role=_SYNTHETIC_ROLE,
        timeout_s=600,
    )
    assert proc.returncode == 0, proc.stderr
    _CACHED_RD = artifact_dir_from_stdout(proc)
    return _CACHED_RD


def artifacts_dir() -> Path:
    return _run_contract()


def load_json(name: str):
    return json.loads((artifacts_dir() / name).read_text(encoding="utf-8"))


def test_live_cli_dispatch_runs():
    proc = run_lane_cli(
        LANE_KEY,
        artifact_dir=contract_artifact_dir(LANE_KEY).relative_to(REPO_ROOT).as_posix(),
        target_company=_SYNTHETIC_COMPANY,
        target_role=_SYNTHETIC_ROLE,
        timeout_s=600,
    )
    assert proc.returncode == 0, proc.stderr
    assert "L2_UNIFY_NARRATIVE_OUTPUT:" in proc.stdout


def test_live_one_sentence():
    _run_contract()
    l2 = load_json("l2_output.json")
    assert l2["narrative_sentence"].count(".") >= 1
    text = l2["narrative_sentence"].strip()
    assert "\n" not in text or len(text.split(".")) <= 2


def test_x2_gate_count():
    _run_contract()
    x2 = load_json("x2_gate_outputs.json")
    assert x2["total_x2_gates"] == 36
    assert x2["x2_failed"] == 0


def test_live_x3_allow_or_review_family():
    rd = _run_contract()
    assert_live_lane_product_proof(rd, LANE_KEY)


def test_l6_shadow_package_present():
    _run_contract()
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6.get("section_id") == LANE_KEY
    assert l6.get("human_label_required") is True
    assert l6.get("learning_mutation_performed") is False


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
        "apps_rg/runtime/sections/unify_narrative_lane.py",
        "apps_rg/runtime/validators/unify_narrative_x2.py",
        "apps_rg/runtime/judges/unify_narrative_x1d.py",
        "apps_rg/runtime/exit/unify_narrative_x3.py",
        "apps_rg/runtime/shadow/unify_narrative_l6.py",
    ):
        assert (REPO_ROOT / rel).exists()
