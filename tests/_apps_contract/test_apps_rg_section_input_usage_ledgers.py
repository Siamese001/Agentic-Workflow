"""Contract tests: ``section_input_usage_ledger.json`` + input-authority gates for apps_rg sections."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests._apps_contract.contract_harness_paths import harness_run
from tests._apps_contract.lane_cli_common import (
    REPO_ROOT as REPO,
    artifact_dir_from_stdout,
    contract_artifact_dir,
    qwen_live_available,
    run_lane_cli,
)

pytestmark = pytest.mark.skipif(
    not qwen_live_available(),
    reason="section input usage ledger CLI tests require live qwen_vllm",
)

SECTION_IDS = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)


def _section_kwargs(section_id: str) -> dict[str, str]:
    if section_id != "executive_summary":
        return {}
    return {
        "target_company": "CI-Probe-Co",
        "target_role": "Software Engineer",
        "jd": str(REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"),
        "manual_brief": str(REPO / "apps_rg" / "config" / "default_targeting_briefing.txt"),
    }


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_section_cli_emits_input_usage_ledger_and_prompt_authority(section_id: str) -> None:
    art = contract_artifact_dir(section_id)
    rel = art.relative_to(REPO).as_posix()
    r = run_lane_cli(section_id, artifact_dir=rel, timeout_s=600, **_section_kwargs(section_id))
    assert r.returncode == 0, f"stderr={r.stderr!r} stdout={r.stdout!r}"
    rd = artifact_dir_from_stdout(r)
    led_path = rd / "section_input_usage_ledger.json"
    assert led_path.is_file(), f"missing {led_path}"
    doc = json.loads(led_path.read_text(encoding="utf-8"))
    assert doc.get("schema") == "section_input_usage_ledger_v1"
    assert doc.get("section_id") == section_id
    led_blob = json.dumps(doc, ensure_ascii=False).lower()
    assert "jd as proof" not in led_blob
    assert "briefing as proof" not in led_blob

    assert doc.get("proof_source") in ("broad_skills_ledger", "srfs", "base_resume_fallback")
    assert doc.get("proof_pool_digest")
    assert doc.get("non_proof_inputs") == ["jd_title_company", "briefing"]
    claim_support = doc.get("claim_support_inputs") or []
    assert claim_support
    assert "jd_title_company" not in claim_support
    assert "briefing" not in claim_support

    ia = doc.get("input_authority")
    assert isinstance(ia, dict)
    if doc.get("proof_source") == "broad_skills_ledger":
        assert doc.get("broad_skills_ledger_present") is True
        assert doc.get("base_resume_fallback_used") is False
        assert ia.get("broad_skills_ledger") == "CLAIM_EVIDENCE"
        assert ia.get("base_resume") == "BASE_RESUME_SOURCE"
    elif doc.get("proof_source") == "srfs":
        assert doc.get("srfs_present") is True
        assert ia.get("selected_role_fact_set") == "CLAIM_EVIDENCE"
        assert ia.get("base_resume") == "BASE_RESUME_SOURCE"
    else:
        assert doc.get("base_resume_fallback_used") is True
        assert ia.get("base_resume") == "CLAIM_EVIDENCE_FALLBACK"
    assert ia.get("selected_fact_plan") == "CLAIM_EVIDENCE_AFTER_SELECTION"
    assert ia.get("jd_text") == "TARGETING_INPUT"
    assert ia.get("briefing_research") == "CONTEXT_INPUT"
    assert ia.get("target_title") == "POSITIONING_INPUT"
    assert ia.get("target_company") == "POSITIONING_INPUT"

    riu = doc.get("required_input_usage")
    assert isinstance(riu, dict)
    assert riu.get("jd_text", {}).get("authority") == "TARGETING_INPUT"
    assert riu.get("jd_text", {}).get("required") is True
    assert riu.get("briefing_research", {}).get("authority") == "CONTEXT_INPUT"
    assert riu.get("target_title", {}).get("authority") == "POSITIONING_INPUT"
    assert riu.get("target_company", {}).get("authority") == "POSITIONING_INPUT"
    if doc.get("proof_source") == "broad_skills_ledger":
        assert riu.get("base_resume", {}).get("authority") == "BASE_RESUME_SOURCE"
    elif doc.get("proof_source") == "base_resume_fallback":
        assert riu.get("base_resume", {}).get("authority") == "CLAIM_EVIDENCE"
    else:
        assert riu.get("base_resume", {}).get("authority") in ("BASE_RESUME_SOURCE", "CLAIM_EVIDENCE")

    eb = doc.get("evidence_boundary")
    assert isinstance(eb, dict)
    assert eb.get("non_evidence_inputs_used_as_claim_evidence") is not True
    assert eb.get("non_evidence_inputs_in_source_fact_ids") is not True

    for name in (
        "canonical_claim_ledger_v2.json",
        "text_claim_coverage.json",
        "parsed_output.json",
        "compiled_prompt.txt",
    ):
        assert (rd / name).is_file(), f"missing {name} under {rd}"

    compiled = (rd / "compiled_prompt.txt").read_text(encoding="utf-8")
    cl = compiled.lower()
    assert "INPUT_AUTHORITY" in compiled
    assert "BASE_RESUME_SELECTED_FACTS" in compiled or "ALLOWED_SOURCE_FACT_IDS" in compiled
    assert "TARGETING_INPUT" in compiled or "CLAIM_EVIDENCE" in compiled or "CLAIM SUPPORT POOL" in compiled
    assert "jd as proof" not in cl
    assert "briefing as proof" not in cl


def test_x3_blocks_when_evidence_boundary_flags_non_evidence_as_claim_evidence() -> None:
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    bad_ledger = {
        "schema": "section_input_usage_ledger_v1",
        "section_id": "executive_summary",
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": True,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {},
    }
    x3 = aggregate_x3(
        resume_display_text="x",
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x1d_judges=[],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=bad_ledger,
    )
    assert x3.x3_code == "X3_BLOCK"


def test_append_input_usage_x2_missing_ledger_fails() -> None:
    from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult
    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    gates: list[X2GateResult] = []
    ad = harness_run("_contract_test_nonexistent_run")
    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=ad,
        allowed_fact_ids={"bul_unify_001"},
        claim_ledger=[{"claim_text": "Led cloud migration.", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"overall_pass": True, "sentences": []},
    )
    present = [g.to_dict() for g in gates if g.to_dict().get("gate_id") == "x2_section_input_usage_ledger_present"]
    assert present and not present[0].get("pass")


def test_l6_learning_record_refs_section_input_usage_ledger(tmp_path: Path) -> None:
    from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record

    ad = tmp_path / "run"
    ad.mkdir(parents=True)
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_BLOCK", "proof_eligible": False}),
        encoding="utf-8",
    )
    (ad / "x2_gate_outputs.json").write_text(json.dumps({"gates": []}), encoding="utf-8")
    (ad / "x1d_llm_judge_outputs.json").write_text(json.dumps({"judges": []}), encoding="utf-8")
    (ad / "section_input_usage_ledger.json").write_text(
        json.dumps({"schema": "section_input_usage_ledger_v1"}),
        encoding="utf-8",
    )
    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="headline",
        lane_key="headline",
    )
    ref = (rec.get("input_refs") or {}).get("section_input_usage_ledger_ref")
    assert isinstance(ref, str) and ref.endswith("section_input_usage_ledger.json")
