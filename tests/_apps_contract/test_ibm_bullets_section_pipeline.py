"""Contract tests: ibm_bullets runs through ``python -m apps_rg --section ibm_bullets`` + canonical_dispatch only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
from apps_rg.runtime.sections.ibm_bullets_lane import build_mock_output, extract_ibm_employment
from apps_rg.runtime.validators.executive_summary_x2 import check_claim_ledger_claim_text_non_empty
from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates
import subprocess
import sys

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT as REPO,
    base_canonical_argv,
    contract_env,
    contract_live_pytestmark,
    run_lane_cli_once,
)

pytestmark = contract_live_pytestmark("ibm_bullets")


@pytest.fixture(scope="module")
def ibm_bullets_lane_run_dir() -> Path:
    """One live CLI run per module (was 8+ redundant subprocess invocations)."""
    return run_lane_cli_once("ibm_bullets", run_key="ibm_bullets_pipeline_module")


def test_canonical_cli_emits_required_ibm_bullets_artifacts(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    required = [
        "compiled_prompt.txt",
        "compiled_prompt_artifact.json",
        "provider_request.json",
        "provider_response.json",
        "l2_output.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "prompt_selection_trace.json",
        "l6_shadow_eval_package.json",
    ]
    for name in required:
        assert (rd / name).is_file(), f"missing {name} under {rd}"


def test_ibm_section_flag_alias():
    cmd = base_canonical_argv("ibm_bullets")
    sec_i = cmd.index("--section")
    cmd[sec_i : sec_i + 2] = ["--ibm-bullets"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=contract_env())
    assert r.returncode == 0, r.stderr


def test_canonical_dispatch_does_not_import_ibm_bullets_dispatch():
    path = REPO / "apps_rg" / "runtime" / "orchestration" / "canonical_dispatch.py"
    text = path.read_text(encoding="utf-8")
    assert "ibm_bullets_dispatch" not in text


def test_prompt_selection_trace_points_at_ibm_bullets_lane(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    trace = json.loads((rd / "prompt_selection_trace.json").read_text(encoding="utf-8"))
    assert trace.get("runtime_path") == "apps_rg.runtime.sections.ibm_bullets_lane"


def test_compiled_ibm_prompt_and_artifact_surface_allowed_fact_ids(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    compiled_txt = (rd / "compiled_prompt.txt").read_text(encoding="utf-8").lower()
    assert "allowed_source_fact_ids" in compiled_txt
    art = json.loads((rd / "compiled_prompt_artifact.json").read_text(encoding="utf-8"))
    ids = art.get("allowed_fact_ids")
    assert isinstance(ids, list)
    assert ids
    assert all(str(x).startswith("bul_ibm_") for x in ids)


def test_x2_contains_claim_text_gate_and_passes_on_mock(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    assert "x2_claim_ledger_claim_text_non_empty" in gate_ids
    g = next(g for g in x2["gates"] if g["gate_id"] == "x2_claim_ledger_claim_text_non_empty")
    assert g["pass"] is True


def test_x2_text_claim_coverage_integrity_gate_present_and_passes_on_mock(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    assert (rd / "text_claim_coverage.json").is_file()
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    assert "x2_text_claim_coverage_integrity" in gate_ids
    g = next(g for g in x2["gates"] if g["gate_id"] == "x2_text_claim_coverage_integrity")
    assert g["pass"] is True


def test_x2_ibm_only_fact_scope_present_and_passes_on_mock(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    g = next(g for g in x2["gates"] if g["gate_id"] == "x2_ibm_only_fact_scope")
    assert g["pass"] is True


def test_x2_no_taxonomy_label_prefix_gate_present_and_passes_on_mock(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in x2["gates"]}
    assert "x2_no_taxonomy_label_prefix_in_display_text" in gate_ids
    g = next(g for g in x2["gates"] if g["gate_id"] == "x2_no_taxonomy_label_prefix_in_display_text")
    assert g["pass"] is True


def test_x2_no_rewrite_intensity_model_gate_passes_on_mock_baseline():
    base = _ibm_x2_baseline()
    gates = run_ibm_bullets_x2_gates(
        bullets=base["bullets"],
        parsed_output=base["parsed_output"],
        claim_ledger=base["parsed_output"]["claim_ledger"],
        allowed_fact_ids=base["allowed_fact_ids"],
        jd_text=base["jd_text"],
        runtime_generation_status=base["runtime_generation_status"],
        x1d_judges=base["x1d_judges"],
    )
    g = next(x for x in gates if x.gate_id == "x2_ibm_no_rewrite_intensity_model")
    assert g.pass_ is True


def test_x2_no_rewrite_intensity_model_gate_fails_when_legacy_fields_present():
    base = _ibm_x2_baseline()
    parsed = dict(base["parsed_output"])
    parsed["rewrite_distribution"] = {"HEAVY": 0, "MODERATE": 3, "LIGHT_PROTECTED": 2, "total": 5}
    parsed["bullets"] = [dict(b) for b in parsed["bullets"]]
    parsed["bullets"][0]["rewrite_intensity"] = "MODERATE"
    gates = run_ibm_bullets_x2_gates(
        bullets=parsed["bullets"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=base["allowed_fact_ids"],
        jd_text=base["jd_text"],
        runtime_generation_status=base["runtime_generation_status"],
        x1d_judges=base["x1d_judges"],
    )
    g = next(x for x in gates if x.gate_id == "x2_ibm_no_rewrite_intensity_model")
    assert g.pass_ is False


@pytest.mark.parametrize(
    "ledger_row",
    [
        {"source_fact_ids": ["bul_ibm_001"]},
        {"claim_text": None, "source_fact_ids": ["bul_ibm_001"]},
        {"claim_text": "", "source_fact_ids": ["bul_ibm_001"]},
        {"claim_text": "   \t\n", "source_fact_ids": ["bul_ibm_001"]},
    ],
)
def test_check_claim_ledger_claim_text_non_empty_fail_closed(ledger_row: dict):
    ok, reason = check_claim_ledger_claim_text_non_empty([ledger_row])
    assert ok is False
    assert reason


def _ibm_x2_baseline():
    base, _path, _digest = load_lane_base_resume_json(repo_root=REPO)
    _hdr, facts, allowed = extract_ibm_employment(base)
    rp = {"selected_fact_plan": {"facts": facts}}
    parsed = build_mock_output(rp)
    judges = [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED"},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED"},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED"},
    ]
    return {
        "bullets": parsed["bullets"],
        "parsed_output": parsed,
        "allowed_fact_ids": allowed,
        "jd_text": "Enterprise platform leadership role.",
        "runtime_generation_status": "MOCKED",
        "provider_requested": "mock",
        "provider_attempted": "mock",
        "model_name": "mock",
        "raw_output": "{}",
        "x1d_judges": judges,
    }


def test_x2_claim_ledger_claim_text_gate_fails_on_whitespace_only_via_runner():
    base = _ibm_x2_baseline()
    ledger = [dict(r) for r in base["parsed_output"]["claim_ledger"]]
    ledger[0]["claim_text"] = "   "
    gates = run_ibm_bullets_x2_gates(
        claim_ledger=ledger,
        **{k: v for k, v in base.items() if k != "parsed_output"},
        parsed_output=base["parsed_output"],
    )
    g = next(x for x in gates if x.gate_id == "x2_claim_ledger_claim_text_non_empty")
    assert g.pass_ is False


def test_x2_ibm_only_fact_scope_fails_on_unify_fact_id():
    base = _ibm_x2_baseline()
    ledger = [dict(r) for r in base["parsed_output"]["claim_ledger"]]
    ledger[0] = dict(ledger[0])
    ledger[0]["source_fact_ids"] = list(ledger[0]["source_fact_ids"]) + ["bul_unify_001"]
    gates = run_ibm_bullets_x2_gates(
        bullets=base["bullets"],
        parsed_output=base["parsed_output"],
        claim_ledger=ledger,
        allowed_fact_ids=base["allowed_fact_ids"],
        jd_text=base["jd_text"],
        runtime_generation_status=base["runtime_generation_status"],
        provider_requested=base["provider_requested"],
        provider_attempted=base["provider_attempted"],
        model_name=base["model_name"],
        raw_output=base["raw_output"],
        x1d_judges=base["x1d_judges"],
    )
    g = next(x for x in gates if x.gate_id == "x2_ibm_only_fact_scope")
    assert g.pass_ is False


def test_x2_no_taxonomy_label_prefix_gate_fails_closed():
    base = _ibm_x2_baseline()
    bullets = [dict(b) for b in base["bullets"]]
    bullets[0] = dict(bullets[0])
    prefixed = "Cloud Modernization: Led migration from legacy on-prem environments."
    bullets[0]["bullet_text"] = prefixed
    ledger = [dict(r) for r in base["parsed_output"]["claim_ledger"]]
    ledger[0] = dict(ledger[0])
    ledger[0]["claim_text"] = prefixed
    parsed = dict(base["parsed_output"])
    parsed["bullets"] = bullets
    parsed["claim_ledger"] = ledger
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=base["allowed_fact_ids"],
        jd_text=base["jd_text"],
        runtime_generation_status=base["runtime_generation_status"],
        provider_requested=base["provider_requested"],
        provider_attempted=base["provider_attempted"],
        model_name=base["model_name"],
        raw_output=base["raw_output"],
        x1d_judges=base["x1d_judges"],
    )
    g = next(x for x in gates if x.gate_id == "x2_no_taxonomy_label_prefix_in_display_text")
    assert g.pass_ is False


def test_ibm_bullets_dispatch_module_has_no_argparse_cli():
    path = REPO / "apps_rg" / "runtime" / "dispatch" / "ibm_bullets_dispatch.py"
    text = path.read_text(encoding="utf-8")
    assert "argparse" not in text


def test_l6_shadow_handoff_follows_canonical_run(ibm_bullets_lane_run_dir: Path):
    rd = ibm_bullets_lane_run_dir
    l6 = json.loads((rd / "l6_shadow_eval_package.json").read_text(encoding="utf-8"))
    assert l6.get("section_id") == "ibm_bullets"
    assert l6.get("packet_type") == "L6_SHADOW_HANDOFF_PACKET"
    assert l6.get("observer_law_assertion")
    assert l6.get("future_run_only_assertion") is True
    assert l6.get("x3_summary", {}).get("x3_code")
    assert l6.get("claim_ledger_summary", {}).get("row_count", 0) >= 5
    cal = l6.get("foundation_proof_calibration") or {}
    assert cal.get("foundation_proof_model_id") == "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1"
    assert cal.get("treatment_profile") == "MODEL_POOL_CLAUDE_TOP_N_SELECTION"
    assert int(cal.get("bullet_count_observed") or 0) >= 5
    summ = l6.get("allowed_fact_ids_summary") or {}
    assert isinstance(summ.get("allowed_fact_ids_sorted"), list)
    assert summ["allowed_fact_ids_sorted"]
