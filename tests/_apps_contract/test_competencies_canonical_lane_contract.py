"""Competencies canonical lane contract — ``apps_rg.runtime.sections.competencies_lane`` only.

Uses offline Qwen contract stub (no live provider). Not a smoke bundle gate.

Depends on ``tests/_apps_contract/conftest.py`` autouse fixtures:
``APPS_RG_QWEN_OFFLINE_CONTRACT_STUB`` (via ``competencies_offline_env``) and
non-product ``fixture_dev_bypass`` for proof-pool preconditions when one-spine
kill switch is on. Lane execution supplies ``SectionFrontSpineBridge`` via
``load_section_proof_for_lane`` when product-visible.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.shadow.competencies_l6 import OBSERVER_LAW_TEXT

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def competencies_offline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")


@pytest.fixture
def competencies_lane_args(competencies_offline_env: None):
    from apps_rg.runtime.sections import competencies_lane as lane

    return lane.build_competencies_lane_args(
        provider="qwen_vllm",
        temperature=lane.COMPETENCIES_TEMP_DEFAULT,
        x1d_judges="gemini_pro,openai_chatgpt,anthropic_claude",
        mock_judges=True,
        allow_test_mock_judges=True,
        target_title="SVP Engineering",
        target_company="Synthetic Enterprise Corp.",
        jd_text="",
        briefing="",
    )


def test_canonical_lane_records_trace_runtime_path(competencies_lane_args) -> None:
    from apps_rg.runtime.sections import competencies_lane as lane

    ctx = lane.run_competencies_lane_execution(competencies_lane_args)
    art = Path(ctx["artifact_dir"])
    trace = json.loads((art / "prompt_selection_trace.json").read_text(encoding="utf-8"))
    assert trace.get("runtime_path") == "apps_rg.runtime.sections.competencies_lane"


def test_canonical_lane_writes_l6_shadow_learning_payload(competencies_lane_args) -> None:
    from apps_rg.runtime.sections import competencies_lane as lane

    ctx = lane.run_competencies_lane_execution(competencies_lane_args)
    art = Path(ctx["artifact_dir"])
    l6_pkg = json.loads((art / "l6_shadow_eval_package.json").read_text(encoding="utf-8"))
    learn = l6_pkg.get("l6_shadow_learning")
    assert isinstance(learn, dict)
    assert learn.get("enabled") is True
    assert learn.get("section_id") == "competencies"
    assert learn.get("runtime_exhaust_ref")
    assert learn.get("observer_law_receipt", {}).get("observer_law") == OBSERVER_LAW_TEXT
    assert learn.get("current_run_mutation_assertion") is False
    assert learn.get("current_run_rescue_assertion") is False
    assert learn.get("runtime_allow_contribution") is False
    assert learn.get("uwg_promotion_request_ref") is None

    sidecar = art / "l6_shadow_learning.json"
    assert sidecar.is_file()
    raw_side = json.loads(sidecar.read_text(encoding="utf-8"))
    assert raw_side.get("section_id") == "competencies"

    proposals = art / "l6_future_run_proposals.json"
    assert proposals.is_file()
    prop_body = json.loads(proposals.read_text(encoding="utf-8"))
    assert prop_body.get("inert_until_uwg") is True
    assert isinstance(prop_body.get("future_run_recommendations"), list)

    assert learn.get("mock_fixture_marker_summary", {}).get("classification") in {
        "clean",
        "proof_quality_defect",
        "n/a_not_real_llm",
    }
    ras = learn.get("repair_action_summary") or {}
    assert "anomaly_operation_counts" in ras
    assert "operation_counts" in ras


def test_canonical_lane_writes_competencies_section_aggregation_artifact(competencies_lane_args) -> None:
    from apps_rg.runtime.sections import competencies_lane as lane

    ctx = lane.run_competencies_lane_execution(competencies_lane_args)
    art = Path(ctx["artifact_dir"])
    path = art / "competencies_section_output.json"
    assert path.is_file()
    agg = json.loads(path.read_text(encoding="utf-8"))
    assert agg.get("section_id") == "competencies"
    assert isinstance(agg.get("display_lines"), list)
    assert isinstance(agg.get("competencies"), list)
    assert isinstance(agg.get("claim_ledger"), list)
    assert isinstance(agg.get("selected_fact_ids"), list)
    assert agg.get("jd_used_as_proof") is False
    assert agg.get("briefing_used_as_proof") is False
    assert agg.get("companion_context_used_as_proof") is False
    assert agg.get("runtime_generation_status")
    assert agg.get("x2_gate_outputs_ref", "").endswith("x2_gate_outputs.json")
    assert agg.get("x3_disposition_ref", "").endswith("x3_disposition.json")
    assert str(agg.get("section_input_usage_ledger_ref") or "").endswith("section_input_usage_ledger.json")
    assert agg.get("proof_eligible") is False
    assert agg.get("product_quality_status")
    assert agg.get("x3_code")
    assert agg.get("artifact_role_bundle", {}).get("competencies_section_output.json")
    assert str(agg.get("l6_shadow_eval_package_ref") or "").endswith("l6_shadow_eval_package.json")
    assert str(agg.get("l6_shadow_learning_ref") or "").endswith("l6_shadow_learning.json")
    assert agg.get("targeting_only") is True
    cmd_out = (art / "command_output.txt").read_text(encoding="utf-8")
    assert "CANONICAL_AGGREGATION_INPUT: competencies_section_output.json" in cmd_out
    assert "STATUS PASS alone never implies" in cmd_out

    l2 = json.loads((art / "l2_output.json").read_text(encoding="utf-8"))
    ref = str(l2.get("competencies_section_output_ref") or "")
    assert ref.endswith("competencies_section_output.json")
    assert str(l2.get("l6_shadow_eval_package_ref") or "").endswith("l6_shadow_eval_package.json")


def test_l6_shadow_learning_second_pass_does_not_rewrite_x3(competencies_lane_args) -> None:
    from apps_rg.runtime.shadow.competencies_l6 import build_competencies_shadow_learning

    from apps_rg.runtime.sections import competencies_lane as lane

    ctx = lane.run_competencies_lane_execution(competencies_lane_args)
    art = Path(ctx["artifact_dir"])
    x3_path = art / "x3_disposition.json"
    before = x3_path.read_bytes()
    pkt = json.loads((art / "l6_shadow_eval_package.json").read_text(encoding="utf-8"))
    base_packet = {k: v for k, v in pkt.items() if k != "l6_shadow_learning"}
    build_competencies_shadow_learning(artifact_dir=art, repo_root=REPO_ROOT, base_packet=base_packet)
    assert x3_path.read_bytes() == before


def test_canonical_lane_x2_gate_cardinality(competencies_lane_args) -> None:
    from apps_rg.runtime.sections import competencies_lane as lane

    ctx = lane.run_competencies_lane_execution(competencies_lane_args)
    art = Path(ctx["artifact_dir"])
    x2 = json.loads((art / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    # 41 core competencies gates + section_input_usage_x2 bundle (append_section_input_usage_x2_gates).
    assert x2.get("total_x2_gates") == 42
    assert "x2_no_keyword_stuffing" not in (x2.get("failed_gates") or [])


def test_canonical_lane_mock_judge_x3_review_code(competencies_lane_args) -> None:
    from apps_rg.runtime.sections import competencies_lane as lane

    ctx = lane.run_competencies_lane_execution(competencies_lane_args)
    art = Path(ctx["artifact_dir"])
    x3 = json.loads((art / "x3_disposition.json").read_text(encoding="utf-8"))
    assert x3.get("x3_code") == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_duplicate_variants_collapsed_regression_fixture():
    """Historical REAL_LLM run duplicated 'high availability' across categories."""
    from apps_rg.runtime.sections.competencies_lane_runtime import (
        JD_TEXT_DEFAULT,
        build_resume_support_blob,
        collect_employment_bullets,
        collapse_duplicate_competency_terms,
        load_base_resume,
        load_companion_context,
        rebuild_claim_ledger_from_competencies,
    )
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    from apps_rg.runtime.competencies_proof_boundary import merge_jd_alignment

    fixture = (
        REPO_ROOT
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "competencies"
        / "real"
        / "competencies_20260515_190942"
        / "l2_output.json"
    )
    if not fixture.is_file():
        pytest.skip(f"Missing competencies regression fixture under {fixture.parent}")
    p = json.loads(fixture.read_text(encoding="utf-8"))
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, load_companion_context())
    parsed = {
        "competencies": json.loads(json.dumps(p["competencies"])),
        "selected_fact_plan": p["selected_fact_plan"],
        "jd_alignment": merge_jd_alignment(p.get("jd_alignment", {})),
        "excluded_jd_skills": list(p.get("excluded_jd_skills") or []),
        "removed_or_rewritten_terms": list(p.get("removed_or_rewritten_terms") or []),
        "gap_notes": list(p.get("gap_notes") or []),
        "change_log": list(p.get("change_log") or []),
        "self_check": p.get("self_check", {}) or {},
        "claim_ledger": list(p.get("claim_ledger") or []),
    }
    flat_before = []
    for c in parsed["competencies"]:
        flat_before.extend(str(t).lower() for t in (c.get("terms") or []) if str(t).strip())
    assert flat_before.count("high availability") >= 2

    collapse_duplicate_competency_terms(parsed, rows, blob)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    flat_after = []
    for c in parsed["competencies"]:
        flat_after.extend(str(t).lower() for t in (c.get("terms") or []) if str(t).strip())
    assert flat_after.count("high availability") <= 1

    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text=JD_TEXT_DEFAULT,
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        model_name="regression",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=[],
    )
    dup = next(g for g in gates if g.gate_id == "x2_duplicate_variants_collapsed")
    assert dup.pass_ is True, dup.observed_value


def test_x3_soft_fail_unit():
    from apps_rg.runtime.exit.competencies_x3 import aggregate_x3

    usage = {
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

    x3 = aggregate_x3(
        resume_display_text="Label: one, two, three",
        claim_ledger=[{"claim_text": "one", "source_fact_ids": ["bul_unify_001"]}],
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
        section_input_usage_ledger=usage,
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"


def test_competencies_overlay_files_exist():
    expected = [
        "apps_rg/runtime/sections/competencies_lane_runtime.py",
        "apps_rg/runtime/validators/competencies_x2.py",
        "apps_rg/runtime/judges/competencies_x1d.py",
        "apps_rg/runtime/exit/competencies_x3.py",
        "apps_rg/runtime/shadow/competencies_l6.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel


def test_no_agentic_core_in_overlay_files():
    overlay = [
        REPO_ROOT / "apps_rg/runtime/sections/competencies_lane_runtime.py",
        REPO_ROOT / "apps_rg/runtime/validators/competencies_x2.py",
        REPO_ROOT / "apps_rg/runtime/judges/competencies_x1d.py",
        REPO_ROOT / "apps_rg/runtime/exit/competencies_x3.py",
        REPO_ROOT / "apps_rg/runtime/shadow/competencies_l6.py",
    ]
    for path in overlay:
        text = path.read_text(encoding="utf-8")
        assert "agentic_core" not in text, path