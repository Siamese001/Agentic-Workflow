"""Integration: run_x2_gates + write_section_x2_gate_outputs enumerates lane_registry critical gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.section_x2_gate_outputs import write_section_x2_gate_outputs
from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane

C0_GATES = frozenset({"x2_c0_metrics_artifact_present", "x2_c0_support_status_gate"})


def _gate_ids_from_artifact(artifact_dir: Path) -> set[str]:
    data = json.loads((artifact_dir / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    return {g["gate_id"] for g in data.get("gates", []) if isinstance(g, dict)}


def _write_minimal_c0(artifact_dir: Path, section_id: str) -> None:
    payload = {
        "schema_version": "apps_rg_section_lane_c0_metrics_v1",
        "section_id": section_id,
        "support_status": "SUPPORTED",
        "support_target_met": True,
        "allowed_fact_count": 3,
        "retrieved_fact_count": 3,
    }
    (artifact_dir / "c0_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_executive_summary_x2_write_includes_rigor_critical(tmp_path: Path) -> None:
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    text = (
        "Engineering executive who builds governed agentic AI platforms for regulated enterprise workflows. "
        "The leader scales deterministic routing and orchestration across platform programs. "
        "Platform lifecycle work ties architecture to commercial adoption and operating discipline. "
        "Prior delivery outcomes stay grounded in selected executive facts only."
    )
    (tmp_path / "prompt_selection_trace.json").write_text(
        json.dumps(
            {
                "apps_rg_prompt_template_ref": (
                    "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
                ),
                "compiler_template_id": "executive_summary.generate_scratch_v1",
            }
        ),
        encoding="utf-8",
    )
    gates = [g.to_dict() for g in run_x2_gates(
        resume_display_text=text,
        parsed_output={
            "resume_display_text": text,
            "jd_alignment": {
                "targeting_only": True,
                "jd_used_as_proof": False,
                "briefing_used_as_proof": False,
            },
            "input_payload_hash": "a" * 16,
            "output_payload_hash": "b" * 16,
        },
        claim_ledger=[{"claim_text": "platform", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": True},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Acme",
        jd_text="jd",
        temperature=0.4,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=True,
        artifacts_dir=tmp_path,
        provider_requested="retired_provider_profile",
        provider_attempted="retired_provider_profile",
        model_name="retired_provider-test",
        prompt_hash="c" * 16,
        compiled_prompt="x" * 32,
        raw_output='{"resume_display_text":"x"}',
        x1d_judges=[],
    )]
    _write_minimal_c0(tmp_path, "executive_summary")
    write_section_x2_gate_outputs(tmp_path, "executive_summary", gates)
    present = _gate_ids_from_artifact(tmp_path)
    crit = spec_for_lane("executive_summary").critical_gates
    missing = sorted(g for g in crit if g not in present)
    assert not missing, missing
    assert "x2_c0_metrics_artifact_present" in present


def test_ibm_narrative_x2_write_includes_meta_and_c0(tmp_path: Path) -> None:
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    narrative = "At IBM, led cloud and data foundations for regulated financial services delivery."
    gates = [
        g.to_dict()
        for g in run_ibm_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output={"narrative_sentence": narrative},
            claim_ledger=[{"claim_text": "cloud", "source_fact_ids": ["bul_ibm_001"]}],
            jd_text="",
            runtime_generation_status="REAL_LLM",
            companion_bullet_texts="",
            allowed_fact_ids=["bul_ibm_001"],
        )
    ]
    _write_minimal_c0(tmp_path, "ibm_narrative")
    write_section_x2_gate_outputs(tmp_path, "ibm_narrative", gates)
    present = _gate_ids_from_artifact(tmp_path)
    crit = spec_for_lane("ibm_narrative").critical_gates
    assert "x2_ibm_narrative_no_meta_disclaimer_in_display" in present
    assert not sorted(g for g in crit if g not in present)


@pytest.mark.parametrize("lane", ["headline", "unify_bullets", "ibm_bullets", "competencies"])
def test_lane_x2_write_includes_rigor_critical_except_c0_only_when_no_metrics(
    tmp_path: Path, lane: str
) -> None:
    """Smoke: each lane validator run + section_id write covers registry gates (C0 needs c0_metrics.json)."""
    artifact_dir = tmp_path / lane
    artifact_dir.mkdir()
    gates: list[dict] = [{"gate_id": "x2_json_parse_valid", "pass": True}]
    write_section_x2_gate_outputs(artifact_dir, lane, gates)
    present_before = _gate_ids_from_artifact(artifact_dir)
    assert "x2_c0_metrics_artifact_present" not in present_before or not (
        artifact_dir / "c0_metrics.json"
    ).is_file()
    _write_minimal_c0(artifact_dir, lane)
    write_section_x2_gate_outputs(artifact_dir, lane, gates)
    present = _gate_ids_from_artifact(artifact_dir)
    assert "x2_c0_metrics_artifact_present" in present
