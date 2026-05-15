from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "unify_bullets"
CMD = [sys.executable, "-m", "apps_rg.runtime.dispatch.unify_bullets_dispatch", "--allow-non-allow-exit-zero"]


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CMD + list(extra), cwd=REPO_ROOT, text=True, capture_output=True, timeout=120)


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
    result = run_cmd("--provider", "mock", "--mock-judges")
    assert result.returncode == 0, result.stderr
    assert "UNIFY_BULLETS_OUTPUT:" in result.stdout
    assert "X3_DISPOSITION:" in result.stdout


def test_mock_outputs_six_bullets():
    run_cmd("--provider", "mock", "--mock-judges")
    l2 = load_json("l2_output.json")
    assert len(l2["bullets"]) == 6
    assert {b["bullet_id"] for b in l2["bullets"]} == {
        f"bul_unify_{i:03d}" for i in range(1, 7)
    }


def test_rewrite_distribution_default():
    run_cmd("--provider", "mock", "--mock-judges")
    dist = load_json("rewrite_distribution.json")
    assert dist["HEAVY"] == 2
    assert dist["MODERATE"] == 3
    assert dist["LIGHT_PROTECTED"] == 1
    assert dist["total"] == 6


def test_mocked_judges_review_only():
    run_cmd("--provider", "mock", "--mock-judges")
    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"
    assert x3["proceed_to_runtime"] is False


def test_x2_all_gates_pass_on_mock():
    run_cmd("--provider", "mock", "--mock-judges")
    x2 = load_json("x2_gate_outputs.json")
    assert x2["x2_failed"] == 0
    assert x2["total_x2_gates"] >= 20


def test_l6_shadow_offline_only():
    run_cmd("--provider", "mock", "--mock-judges")
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["promotion_allowed"] is False
    assert l6["human_label_required"] is True
    assert l6["runtime_approval_authority"] == "NONE"
    assert l6["learning_mutation_performed"] is False


def test_x3_soft_fail_anthropic_non_decisive():
    from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="bullets",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_unify_bullet_count_6", "pass": True}],
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
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"
    assert x3.soft_failed_judges == ["anthropic_claude"]


def test_x3_block_on_decisive_failure():
    from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="bullets",
        claim_ledger=[],
        x2_gates=[{"gate_id": "x2_unify_bullet_count_6", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": True,
            }
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
    )
    assert x3.x3_code == "X3_BLOCK"


def test_x2_rejects_wrong_bullet_count():
    from apps_rg.runtime.dispatch.unify_bullets_dispatch import build_mock_output, build_runtime_payload, build_selected_fact_plan, extract_unify_employment, load_base_resume
    from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    payload = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        unify_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP",
        target_company="Corp",
        jd_text="AI",
        briefing="gov",
    )
    parsed = build_mock_output(payload)
    parsed["bullets"] = parsed["bullets"][:5]
    gates = run_unify_bullets_x2_gates(
        bullets=parsed["bullets"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=allowed,
        jd_text="AI",
        runtime_generation_status="MOCKED",
    )
    gate_map = {g.gate_id: g.pass_ for g in gates}
    assert gate_map["x2_unify_bullet_count_6"] is False


def test_normalize_parsed_output_cycle_metric_qualifier_passes_x2_gate():
    """Gate requires exact substring 'six months to three weeks'; Qwen sometimes inserts 'just'."""
    from apps_rg.runtime.dispatch.unify_bullets_dispatch import normalize_parsed_output
    from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates

    from apps_rg.runtime.dispatch.unify_bullets_dispatch import (
        DEFAULT_INTENSITY_BY_BULLET,
        build_selected_fact_plan,
        extract_unify_employment,
        load_base_resume,
        build_runtime_payload,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    rp = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        unify_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP",
        target_company="Corp",
        jd_text="AI governance",
        briefing="regulated",
    )
    by_id = {f["fact_id"]: f for f in facts}
    parsed_in: dict[str, object] = {
        "bullets": [],
        "claim_ledger": [],
        "rewrite_distribution": {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6},
        "jd_alignment": {"targeting_only": True},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    bullets_in: list[dict[str, object]] = []
    for bid in (
        "bul_unify_001",
        "bul_unify_002",
        "bul_unify_003",
        "bul_unify_004",
        "bul_unify_005",
        "bul_unify_006",
    ):
        fact = by_id[bid]
        intensity = DEFAULT_INTENSITY_BY_BULLET[bid]
        text = str(fact["claim_text"])
        if bid == "bul_unify_004":
            text = (
                text.replace("six months to three weeks", "six months to just three weeks")
                if "six months to three weeks" in text.lower()
                else text + "; cycle from six months to just three weeks"
            )
        bullets_in.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
                "has_metric": fact.get("has_metric", False),
                "metric_raw": fact.get("metric_raw"),
                "source_fact_ids": [bid],
            }
        )

    parsed_in["bullets"] = bullets_in
    out = normalize_parsed_output(parsed_in, rp)
    assert out is not None
    b4 = next(b for b in out["bullets"] if b["bullet_id"] == "bul_unify_004")["bullet_text"]
    assert "six months to just three weeks" not in b4.lower()
    assert "six months to three weeks" in b4.lower()

    gates = [
        g.to_dict()
        for g in run_unify_bullets_x2_gates(
            bullets=out["bullets"],
            parsed_output=out,
            claim_ledger=out.get("claim_ledger") or [],
            allowed_fact_ids=allowed,
            jd_text="AI governance",
            runtime_generation_status="REAL_LLM",
            rewrite_distribution=out.get("rewrite_distribution"),
        )
    ]
    met = next(g for g in gates if g["gate_id"] == "x2_unify_metrics_preserved")
    assert met["pass"] is True


def test_unify_overlay_files_exist():
    overlay = [
        "apps_rg/runtime/dispatch/unify_bullets_dispatch.py",
        "apps_rg/runtime/validators/unify_bullets_x2.py",
        "apps_rg/runtime/judges/unify_bullets_x1d.py",
        "apps_rg/runtime/exit/unify_bullets_x3.py",
        "apps_rg/runtime/shadow/unify_bullets_l6.py",
    ]
    for rel in overlay:
        assert (REPO_ROOT / rel).exists()
