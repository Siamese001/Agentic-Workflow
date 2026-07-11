from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apps_rg.runtime.full_resume_review_bundle import write_review_index
from apps_rg.runtime.full_run_section_status import collect_full_run_section_status
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.mandatory_run_outputs import (
    BCG_EXECUTIVE_OUTPUT_MD,
    MANDATORY_OUTPUT_HARD_STOP_GATE_ID,
    MANDATORY_RUN_OUTPUT_JSON,
    MANDATORY_RUN_OUTPUT_MD,
    _bcg_forensics_truth_errors,
    _causal_allocation,
    _classify_failure,
    _result_summary,
    _top_rca_sections,
    build_mandatory_run_output,
    emit_mandatory_run_outputs,
    validate_mandatory_output_bundle,
)
from apps_rg.runtime.run_output_contract import (
    FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
    FINAL_RESUME_DOCX_RELPATH,
    FINAL_RESUME_OUTPUT_JSON,
    FINAL_RESUME_OUTPUT_TXT,
    L7_AUDIT_ABILITY_OUTPUT_MD,
    OUTPUT_BISECT_MD,
)
from apps_rg.runtime.section_failure_forensics import (
    E2E_SECTION_FORENSICS_GATE_ID,
    REQUIRED_RCA_FIELDS,
    SECTION_FAILURE_FORENSICS_DIR,
    emit_section_failure_forensics,
    validate_section_failure_rca,
)
from tools.apps_rg.render_run_summary import render

# apps-test-model: APP CONTRACT


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _pin_baseline(monkeypatch, tmp_path: Path, baseline: Path) -> None:
    mandatory = baseline / MANDATORY_RUN_OUTPUT_JSON
    contract = tmp_path / f"{baseline.name}_baseline.json"
    contract.write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.e2e_baseline.v1",
                "baseline_run_dir": str(baseline),
                "mandatory_output_sha256": hashlib.sha256(mandatory.read_bytes()).hexdigest(),
                "target_company": "Anthropic",
                "target_role": "Partnerships",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("APPS_RG_E2E_BASELINE_REF", str(contract))


def _valid_causal_allocation() -> dict:
    return {
        "dominant_cause": "Visible content was allowed before source lineage completed.",
        "retry_recoverability": "LOW",
        "retry_recoverability_reason": "Blind retry cannot repair missing source lineage.",
        "allocation": [
            {
                "domain": "Evidence substrate / graph lineage",
                "causal_role": "PRIMARY",
                "root_cause_link": "The failed graph gate named a category with missing source facts.",
                "work_share": "60%",
                "evidence_refs": ["x2_competencies_graph_granularity_gates"],
                "required_work": "Bind category output to source facts before display.",
            },
            {
                "domain": "Retry / repair policy",
                "causal_role": "LOW_RECOVERY",
                "root_cause_link": "More generations would use the same incomplete lineage contract.",
                "work_share": "40%",
                "evidence_refs": ["self_consistency_paths.json"],
                "required_work": "Use gate-aware lineage repair instead of blind retry.",
            },
        ],
    }


def test_section_failure_forensics_emits_independent_failure_rca(tmp_path: Path) -> None:
    run = tmp_path / "headline_failed"
    run.mkdir()
    (run / "headline_output.txt").write_text("AWS Migration Modernization Execution\n", encoding="utf-8")
    _write_json(
        run / "x3_disposition.json",
        {
            "x3_code": "X3_BLOCK",
            "product_quality_status": "FAIL",
            "runtime_generation_status": "REAL_LLM",
        },
    )
    _write_json(
        run / "x2_gate_outputs.json",
        {
            "gates": [
                {
                    "gate_id": "x2_headline_executive_abstraction_floor",
                    "pass": False,
                    "failure_reason": "missing executive abstraction",
                }
            ]
        },
    )
    _write_json(run / "selected_fact_plan.json", {"facts": [{"fact_id": "f1"}]})
    _write_json(run / "provider_request.json", {"provider_requested": "external_claude"})

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False, "fault": "headline"},
        section_id="headline",
    )

    gate = emitted["payload"]["section_failure_forensics"]
    assert gate["gate_id"] == E2E_SECTION_FORENSICS_GATE_ID
    assert gate["required"] is True
    assert gate["pass"] is False
    assert gate["failed_section_count"] == 1
    rca_path = run / SECTION_FAILURE_FORENSICS_DIR / "headline.json"
    md_path = run / SECTION_FAILURE_FORENSICS_DIR / "headline.md"
    assert rca_path.is_file()
    assert md_path.is_file()
    rca = json.loads(rca_path.read_text(encoding="utf-8"))
    assert all(field in rca for field in REQUIRED_RCA_FIELDS)
    assert rca["failure_type"] == "independent_failure"
    assert rca["failed_gate_ids"] == ["x2_headline_executive_abstraction_floor"]
    assert rca["final_materialized_output"]["present"] is True
    assert rca["baseline_confidence"] == "pinned_contract_invalid"
    gates_by_id = {row["gate_id"]: row for row in emitted["payload"]["mandatory_inline_output_gates"]}
    assert gates_by_id[E2E_SECTION_FORENSICS_GATE_ID]["pass"] is False
    assert "Section Failure Forensics" in (run / MANDATORY_RUN_OUTPUT_MD).read_text(encoding="utf-8")


def test_section_failure_forensics_emits_upstream_cascade_rca(tmp_path: Path) -> None:
    run = tmp_path / "cascade_failed"
    lane = run / "modular_r4" / "sections" / "headline"
    lane.mkdir(parents=True)
    _write_json(
        lane / "integrated_lane_pre_run_failure.json",
        {
            "blocker": "UPSTREAM_X3_BLOCK",
            "lane_exec_status": "executive_summary did not authorize",
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False, "fault": "cascade"},
    )

    rca = json.loads((run / SECTION_FAILURE_FORENSICS_DIR / "headline.json").read_text(encoding="utf-8"))
    assert rca["failure_type"] == "upstream_cascade"
    assert "upstream" in rca["why_it_failed_now"].lower()
    assert emitted["payload"]["section_failure_forensics"]["pass"] is False


def test_section_failure_forensics_marks_dirty_successful_baseline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline = tmp_path / "baseline_success"
    baseline_lane = baseline / "lanes" / "headline"
    baseline_lane.mkdir(parents=True)
    (baseline / "ingress_raw.json").write_text(
        json.dumps({"target_company": "Anthropic", "target_role": "Partnerships"}) + "\n",
        encoding="utf-8",
    )
    _write_json(
        baseline / MANDATORY_RUN_OUTPUT_JSON,
        {"result_summary": {"exit_status": "success", "outcome_authorized": True}},
    )
    _write_json(baseline / "worktree_status.json", {"worktree_dirty": True})
    _write_json(baseline / "agentic_core_spine_proof.json", {"git_commit": "c" * 40})
    (baseline_lane / "headline_output.txt").write_text("SVP AI Partnerships\n", encoding="utf-8")
    _write_json(baseline_lane / "x3_disposition.json", {"x3_code": "X3_ALLOW", "pass": True})
    _pin_baseline(monkeypatch, tmp_path, baseline)

    run = tmp_path / "current_failed"
    run.mkdir()
    (run / "ingress_raw.json").write_text(
        json.dumps({"target_company": "Anthropic", "target_role": "Partnerships"}) + "\n",
        encoding="utf-8",
    )
    (run / "headline_output.txt").write_text("AWS Migration Modernization Execution\n", encoding="utf-8")
    _write_json(run / "x3_disposition.json", {"x3_code": "X3_BLOCK", "pass": False})
    _write_json(
        run / "x2_gate_outputs.json",
        {"gates": [{"gate_id": "x2_headline_vendor_terms_proof_only", "pass": False}]},
    )
    _write_json(run / "agentic_core_spine_proof.json", {"git_commit": "d" * 40})

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
        section_id="headline",
    )

    rca = json.loads((run / SECTION_FAILURE_FORENSICS_DIR / "headline.json").read_text(encoding="utf-8"))
    assert rca["baseline_confidence"] == "dirty"
    assert "dirty" in rca["why_it_passed_before"].lower()
    assert rca["last_successful_output"]["present"] is True
    assert emitted["payload"]["section_failure_forensics"]["baseline_confidence"] == "dirty"


def test_section_failure_forensics_binds_output_and_revision_to_prior_run(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline = tmp_path / "baseline_success"
    baseline_lane = baseline / "modular_r4" / "sections" / "executive_summary" / "real" / "exec_summary_prior"
    baseline_lane.mkdir(parents=True)
    baseline_text = "Prior passing executive summary with complete evidence-backed sentences."
    baseline_output = baseline_lane / "resume_display_text.txt"
    baseline_output.write_text(baseline_text + "\n", encoding="utf-8")
    _write_json(
        baseline / "ingress_raw.json",
        {"target_company": "Anthropic", "target_role": "Partnerships"},
    )
    _write_json(
        baseline / "agentic_core_spine_proof.json",
        {
            "payload": {
                "git_commit": "a" * 40,
                "git_commit_subject": "Merge pull request #474 from example/prior-pass",
            }
        },
    )
    _write_json(
        baseline / MANDATORY_RUN_OUTPUT_JSON,
        {
            "result_summary": {"exit_status": "success", "outcome_authorized": True},
            "sections": [
                {
                    "section": "executive_summary",
                    "lane_dir": str(baseline_lane.relative_to(baseline)),
                    "display_txt_path": str(baseline_output),
                    "x3_code": "X3_ALLOW",
                    "x2_pass": "PASS",
                }
            ],
        },
    )
    _pin_baseline(monkeypatch, tmp_path, baseline)

    run = tmp_path / "current_failed"
    current_lane = run / "lanes" / "executive_summary"
    current_lane.mkdir(parents=True)
    current_output = current_lane / "resume_display_text.txt"
    current_output.write_text("Current fragmented output.\n", encoding="utf-8")
    _write_json(
        run / "ingress_raw.json",
        {"target_company": "Anthropic", "target_role": "Partnerships"},
    )
    _write_json(
        run / "agentic_core_spine_proof.json",
        {"payload": {"git_commit": "b" * 40, "git_commit_subject": "Current local commit"}},
    )
    section = {
        "section": "executive_summary",
        "lane_dir": str(current_lane),
        "display_txt_path": str(current_output),
        "x3_code": "X3_BLOCK",
        "x2_pass": "FAIL",
        "failed_gates": [{"gate_id": "x2_exec_summary_no_sentence_fragment", "pass": False}],
    }

    gate = emit_section_failure_forensics(
        run,
        repo_root=tmp_path,
        sections=[section],
        result={"exit_status": "error", "outcome_authorized": False},
    )

    assert gate["pass"] is False
    rca = json.loads(
        (run / SECTION_FAILURE_FORENSICS_DIR / "executive_summary.json").read_text(encoding="utf-8")
    )
    assert Path(rca["last_successful_output"]["path"]).resolve() == baseline_output.resolve()
    assert rca["last_successful_output"]["text"] == baseline_text
    assert rca["last_successful_output"]["sha256"] != rca["current_output"]["sha256"]
    assert rca["revision_comparison"]["baseline"]["git_commit"] == "a" * 40
    assert rca["revision_comparison"]["baseline"]["pr_number"] == 474
    assert rca["revision_comparison"]["current"]["git_commit"] == "b" * 40
    assert rca["comparison_complete"] is True
    validation_errors = validate_section_failure_rca(rca)
    assert any("CODE_CAUSE_NOT_ISOLATED" in error for error in validation_errors)


def test_mandatory_output_bundle_fails_each_missing_required_artifact(tmp_path: Path) -> None:
    run = tmp_path / "mandatory_bundle"
    run.mkdir()
    payload = {
        "result_summary": {"exit_status": "success", "outcome_authorized": True},
        "section_failure_forensics": {
            "required": False,
            "pass": True,
            "artifacts": [],
            "missing_or_incomplete": [],
        },
    }
    contents = {
        BCG_EXECUTIVE_OUTPUT_MD: (
            "# BCG Executive Output\n## Executive Answer\nOK\n"
            "## Board-Level Readout\nOK\n## Issue Tree\nOK\n## Evidence Map\nOK\n"
        ),
        OUTPUT_BISECT_MD: "# apps_rg Output Bisect\nNo failed-section bisect was required.\n",
        MANDATORY_RUN_OUTPUT_MD: "# apps_rg Mandatory Run Output\n## Section Lane Summary\nOK\n",
        L7_AUDIT_ABILITY_OUTPUT_MD: "## 3. L7 Audit Ability Output\nAudit evidence rendered.\n",
        MANDATORY_RUN_OUTPUT_JSON: json.dumps(payload),
    }
    for filename, body in contents.items():
        (run / filename).write_text(body, encoding="utf-8")

    assert validate_mandatory_output_bundle(run, payload)["pass"] is True
    for filename, body in contents.items():
        path = run / filename
        path.unlink()
        gate = validate_mandatory_output_bundle(run, payload)
        assert gate["gate_id"] == MANDATORY_OUTPUT_HARD_STOP_GATE_ID
        assert gate["pass"] is False
        assert any(filename in error for error in gate["errors"])
        path.write_text(body, encoding="utf-8")


def test_mandatory_output_bundle_rejects_empty_and_malformed_artifacts(tmp_path: Path) -> None:
    run = tmp_path / "malformed_bundle"
    run.mkdir()
    payload = {
        "result_summary": {"exit_status": "success", "outcome_authorized": True},
        "section_failure_forensics": {"required": False, "pass": True, "artifacts": []},
    }
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("", encoding="utf-8")
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# wrong ledger\n", encoding="utf-8")
    (run / L7_AUDIT_ABILITY_OUTPUT_MD).write_text("# wrong audit\n", encoding="utf-8")
    (run / MANDATORY_RUN_OUTPUT_JSON).write_text("{not-json", encoding="utf-8")

    gate = validate_mandatory_output_bundle(run, payload)

    assert gate["pass"] is False
    assert f"missing_or_empty:{BCG_EXECUTIVE_OUTPUT_MD}" in gate["errors"]
    assert any(error.startswith(f"missing_marker:{MANDATORY_RUN_OUTPUT_MD}") for error in gate["errors"])
    assert any(error.startswith(f"missing_marker:{L7_AUDIT_ABILITY_OUTPUT_MD}") for error in gate["errors"])
    assert f"malformed_json:{MANDATORY_RUN_OUTPUT_JSON}" in gate["errors"]


def test_emitter_writes_all_mandatory_outputs_and_embeds_hard_stop_gate(tmp_path: Path) -> None:
    run = tmp_path / "complete_bundle"
    run.mkdir()

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "success", "outcome_authorized": True},
        section_id="headline",
        emit_final_outputs=False,
    )

    assert emitted["mandatory_output_gate"]["pass"] is False
    for filename in (
        BCG_EXECUTIVE_OUTPUT_MD,
        OUTPUT_BISECT_MD,
        MANDATORY_RUN_OUTPUT_MD,
        L7_AUDIT_ABILITY_OUTPUT_MD,
        MANDATORY_RUN_OUTPUT_JSON,
    ):
        assert (run / filename).is_file()
        assert (run / filename).stat().st_size > 0
    persisted = json.loads((run / MANDATORY_RUN_OUTPUT_JSON).read_text(encoding="utf-8"))
    assert persisted["mandatory_output_hard_stop"]["pass"] is False


def test_mandatory_output_bundle_hard_stops_without_visible_underlying_root_cause(
    tmp_path: Path,
) -> None:
    run = tmp_path / "missing_root_cause_heading"
    run.mkdir()
    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
        section_id="executive_summary",
        emit_final_outputs=False,
    )
    bisect_path = run / OUTPUT_BISECT_MD
    bisect_path.write_text(
        bisect_path.read_text(encoding="utf-8").replace("### Underlying Root Cause", "### Cause Omitted"),
        encoding="utf-8",
    )

    gate = validate_mandatory_output_bundle(run, emitted["payload"])

    assert gate["pass"] is False
    assert f"missing_marker:{OUTPUT_BISECT_MD}:### Underlying Root Cause" in gate["errors"]


def test_mandatory_output_bundle_hard_stops_incomplete_section_comparison(tmp_path: Path) -> None:
    run = tmp_path / "incomplete_comparison_bundle"
    run.mkdir()
    payload = {
        "result_summary": {"exit_status": "error", "outcome_authorized": False},
        "section_failure_forensics": {
            "required": True,
            "pass": False,
            "artifacts": [],
            "missing_or_incomplete": [{"section_id": "executive_summary"}],
        },
    }
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text(
        "# BCG\n## Executive Answer\nX\n## Board-Level Readout\nX\n## Issue Tree\nX\n## Evidence Map\nX\n",
        encoding="utf-8",
    )
    (run / MANDATORY_RUN_OUTPUT_MD).write_text(
        "# apps_rg Mandatory Run Output\n## Section Lane Summary\nX\n",
        encoding="utf-8",
    )
    (run / L7_AUDIT_ABILITY_OUTPUT_MD).write_text(
        "## 3. L7 Audit Ability Output\nX\n",
        encoding="utf-8",
    )
    (run / MANDATORY_RUN_OUTPUT_JSON).write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    gate = validate_mandatory_output_bundle(run, payload)

    assert gate["pass"] is False
    assert E2E_SECTION_FORENSICS_GATE_ID in gate["errors"]
    assert "missing:section_failure_forensics_artifacts" in gate["errors"]


def test_emitter_marks_result_unauthorized_when_mandatory_output_is_invalid(
    monkeypatch,
    tmp_path: Path,
) -> None:
    run = tmp_path / "invalid_emitted_bundle"
    run.mkdir()

    def _emit_invalid_l7(root: Path) -> Path:
        path = root / L7_AUDIT_ABILITY_OUTPUT_MD
        path.write_text("# invalid L7 output\n", encoding="utf-8")
        return path

    monkeypatch.setattr(
        "apps_rg.runtime.mandatory_run_outputs.emit_l7_audit_ability_output",
        _emit_invalid_l7,
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "success", "outcome_authorized": True},
        section_id="headline",
        emit_final_outputs=False,
    )

    assert emitted["mandatory_output_gate"]["pass"] is False
    summary = emitted["payload"]["result_summary"]
    assert summary["exit_status"] == "error"
    assert summary["execution_status"] == "failed"
    assert summary["outcome_authorized"] is False
    assert summary["x3_disposition"] == ""
    assert summary["completion_status"] == "BLOCKED"
    assert summary["completion_fault"] == MANDATORY_OUTPUT_HARD_STOP_GATE_ID
    assert summary["fault"] == ""


def test_result_summary_preserves_x3_and_separates_completion_failure(tmp_path: Path) -> None:
    summary = _result_summary(
        {
            "exit_status": "error",
            "x3_disposition": "X3D",
            "completion_disposition": "X3D",
            "completion_status": "BLOCKED",
            "completion_fault": "L6_SHADOW_CLOSURE_FAILED",
        },
        tmp_path,
    )

    assert summary["x3_disposition"] == "X3D"
    assert summary["completion_disposition"] == "X3D"
    assert summary["completion_status"] == "BLOCKED"
    assert summary["completion_fault"] == "L6_SHADOW_CLOSURE_FAILED"
    assert summary["fault"] == ""


def test_incomplete_section_failure_forensics_is_hard_gate_defect() -> None:
    rca = {
        "section_id": "headline",
        "failure_type": "independent_failure",
        "failed_gate_ids": ["x2_headline_vendor_terms_proof_only"],
    }

    errors = validate_section_failure_rca(rca)

    assert "missing:current_output" in errors
    assert "missing:required_fix" in errors
    assert E2E_SECTION_FORENSICS_GATE_ID == "E2E_FAIL_WITHOUT_SECTION_FORENSICS"


def test_clean_pass_does_not_emit_fake_section_failure_forensics(tmp_path: Path) -> None:
    run = tmp_path / "clean_pass"
    run.mkdir()

    gate = emit_section_failure_forensics(
        run,
        repo_root=tmp_path,
        sections=[
            {
                "section": "headline",
                "status_bucket": "ran_real_llm",
                "x3_code": "X3_ALLOW",
                "failed_gates": [],
            }
        ],
        result={"exit_status": "success", "outcome_authorized": True},
    )

    assert gate["required"] is False
    assert gate["artifacts"] == []
    assert not (run / SECTION_FAILURE_FORENSICS_DIR).exists()


def test_bcg_forensics_truth_gate_requires_artifact_refs() -> None:
    doc = {
        "section_failure_forensics": {
            "required": True,
            "artifacts": [
                {
                    "section_id": "headline",
                    "json_path": "artifacts/apps_rg/runs/run1/section_failure_forensics/headline.json",
                    "md_path": "artifacts/apps_rg/runs/run1/section_failure_forensics/headline.md",
                    "complete": True,
                }
            ],
        },
    }

    errors = _bcg_forensics_truth_errors(
        doc,
        [{"section": "headline"}],
        [
            {
                "label": "Mandatory run ledger",
                "path": "@artifacts/apps_rg/runs/run1/APPS_RG_MANDATORY_RUN_OUTPUT.json",
            }
        ],
    )

    assert "bcg.forensics.missing_json_ref:headline" in errors
    assert "bcg.forensics.missing_md_ref:headline" in errors


def test_bcg_forensics_truth_gate_rejects_issue_tree_without_artifact() -> None:
    doc = {
        "section_failure_forensics": {
            "required": True,
            "artifacts": [
                {
                    "section_id": "executive_summary",
                    "json_path": "section_failure_forensics/executive_summary.json",
                    "md_path": "section_failure_forensics/executive_summary.md",
                    "complete": True,
                }
            ],
        },
    }

    errors = _bcg_forensics_truth_errors(
        doc,
        [{"section": "headline"}],
        [
            {
                "label": "Section forensic RCA: executive_summary",
                "path": (
                    "@section_failure_forensics/executive_summary.json; "
                    "@section_failure_forensics/executive_summary.md"
                ),
            }
        ],
    )

    assert "bcg.issue_tree.missing_forensic_artifact:headline" in errors


def test_emit_mandatory_outputs_for_failed_whole_run(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_failed01"
    lane = run / "lanes" / "competencies"
    lane.mkdir(parents=True)
    (lane / "competencies_display.txt").write_text(
        "Partner Applied AI Architecture: governed agentic systems architecture\n",
        encoding="utf-8",
    )
    _write_json(
        lane / "x3_disposition.json",
        {
            "x3_code": "X3_BLOCK",
            "product_quality_status": "FAIL",
            "runtime_generation_status": "REAL_LLM",
            "decisive_judge_failures": [],
            "soft_failed_judges": [],
            "blocked_judges": [],
            "mocked_judges": [],
            "model_backed_pass_provider_keys": ["openai_chatgpt"],
        },
    )
    _write_json(
        lane / "x2_gate_outputs.json",
        {
            "gates": [
                {
                    "gate_id": "x2_competencies_graph_granularity_gates",
                    "pass": False,
                    "failure_reason": "categories_missing_source_facts:['commercial']",
                }
            ]
        },
    )
    _write_json(
        lane / "x1d_llm_judge_outputs.json",
        {
            "judges": [
                {
                    "provider_name": "OpenAI ChatGPT",
                    "provider_key": "openai_chatgpt",
                    "model_name": "gpt-test",
                    "score": 4.4,
                    "threshold": 4.0,
                    "pass": True,
                    "provider_status": "MODEL_BACKED",
                }
            ]
        },
    )
    (lane / "l6_shadow_eval_package.json").write_text("{}\n", encoding="utf-8")

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False, "fault": "test fault"},
    )

    assert emitted["json_path"].is_file()
    assert (run / MANDATORY_RUN_OUTPUT_MD).is_file()
    assert (run / BCG_EXECUTIVE_OUTPUT_MD).is_file()
    payload = json.loads((run / MANDATORY_RUN_OUTPUT_JSON).read_text(encoding="utf-8"))
    comp = next(row for row in payload["sections"] if row["section"] == "competencies")
    assert comp["status_bucket"] == "ran_real_llm"
    assert comp["judges"][0]["provider"] == "OpenAI ChatGPT"
    assert comp["l6"]["file_count"] == 1
    assert payload["final_resume_output"]["required"] is True
    assert payload["final_resume_output"]["status"] == "FAIL"
    assert payload["section_lane_table"]
    assert payload["section_lane_table"][0]["order"] == 0
    assert payload["section_lane_table"][0]["section"] == "research_briefing_input"
    assert payload["section_lane_table"][0]["generation_status"] == "MISSING_BRIEFING"
    inline = payload["inline_required_output"]
    assert inline["schema_version"] == "apps_rg.inline_required_output.v1"
    assert inline["immutable_section_order"] == [
        "bcg",
        "section_lane_summary_table",
        "resume_docx_full_version_inline",
    ]
    assert inline["bcg"]["title"] == "BCG Executive Output - apps_rg Run"
    assert inline["bcg"]["section_order"] == [
        "executive_answer",
        "p0_p1_px_recommendations",
        "board_level_readout",
        "issue_tree",
        "recommended_next_move",
        "evidence_map",
    ]
    recommendation_rows = inline["bcg"]["p0_p1_px_recommendations"]["rows"]
    assert any(row["priority"] == "P0" for row in recommendation_rows)
    assert not any(
        row["recommendation"] == "Add dependency-token reporting for every PHASE1_NO_RUN_DIR lane."
        and "PHASE1_NO_RUN_DIR lanes:" not in row["evidence"]
        for row in recommendation_rows
    )
    gates_by_id = {gate["gate_id"]: gate for gate in payload["mandatory_inline_output_gates"]}
    assert gates_by_id["mandatory_inline_required_json_shape_locked"]["pass"] is True
    assert gates_by_id["mandatory_bcg_p0_p1_px_recommendations_locked"]["pass"] is False
    assert gates_by_id["mandatory_resume_docx_inline_json_present"]["pass"] is False
    assert (
        gates_by_id["mandatory_resume_docx_inline_json_present"]["observed_value"]["current_run_authorized"]
        is False
    )
    assert (run / FINAL_RESUME_ASSEMBLY_JSON_RELPATH).is_file()
    assert (run / FINAL_RESUME_OUTPUT_TXT).is_file()
    assert (run / FINAL_RESUME_DOCX_RELPATH).is_file()
    finding = payload["rca_findings"][0]
    assert finding["section"] == "competencies"
    assert finding["root_cause"].startswith("Visible content can be rendered")
    assert 3 <= len(finding["implementation_plan"]) <= 5
    assert all("rerun" not in item.lower() for item in finding["implementation_plan"][:-1])
    allocation = finding["causal_allocation"]
    assert allocation["retry_recoverability"] == "LOW"
    assert allocation["dominant_cause"]
    assert allocation["allocation"]
    assert all(row["root_cause_link"] != row["domain"] for row in allocation["allocation"])
    issue = next(row for row in inline["bcg"]["issue_tree"] if row["section"] == "competencies")
    issue_evidence = "\n".join(issue["evidence"])
    assert "forensics_json=" in issue_evidence
    assert "section_failure_forensics/competencies.json" in issue_evidence
    evidence_map = inline["bcg"]["evidence_map"]
    forensic_paths = "\n".join(row["path"] for row in evidence_map)
    assert "section_failure_forensics/competencies.json" in forensic_paths
    assert "section_failure_forensics/competencies.md" in forensic_paths
    bcg = (run / BCG_EXECUTIVE_OUTPUT_MD).read_text(encoding="utf-8")
    mandatory = (run / MANDATORY_RUN_OUTPUT_MD).read_text(encoding="utf-8")
    assert "BCG Executive Output - apps_rg Run" in bcg
    assert "P0/P1/PX Recommendations" in bcg
    assert "Evidence mapping failure" in bcg
    assert "Causal allocation" in bcg
    assert "Retry recoverability" in bcg
    assert "Required implementation plan" in bcg
    assert "Change the section enrichment step" in bcg
    assert "Section forensic RCA: competencies" in bcg
    assert "Section Lane Summary Table" in mandatory
    assert "Resume DOCX Full Version Inline" in mandatory
    assert "NO_AUTHORIZED_RESUME_OUTPUT" in mandatory
    assert "Causal allocation" in mandatory
    assert "Required implementation plan" in mandatory


def test_blocked_run_does_not_inline_stale_final_resume_text(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_partnership_blocked"
    run.mkdir()
    stale_resume = (
        "SVP Engineering | Governed Distributed Infrastructure | "
        "Databricks Lakehouse Retrieval Architecture | Alliance Co-Sell Partner Growth"
    )
    (run / FINAL_RESUME_OUTPUT_TXT).write_text(stale_resume + "\n", encoding="utf-8")
    _write_json(
        run / FINAL_RESUME_OUTPUT_JSON,
        {
            "schema_version": "apps_rg.final_resume_output.v1",
            "required": True,
            "status": "FAIL",
            "failed_gate_ids": ["final_resume_no_gap_markers"],
            "final_resume_json": {
                "relpath": FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
                "exists": True,
                "bytes": 100,
                "sha256": "spine",
            },
            "rendered_resume_text": {
                "relpath": FINAL_RESUME_OUTPUT_TXT,
                "exists": True,
                "bytes": len(stale_resume),
                "sha256": "resume",
            },
            "resume_docx": {
                "relpath": FINAL_RESUME_DOCX_RELPATH,
                "exists": True,
                "bytes": 100,
                "sha256": "docx",
            },
        },
    )

    doc = build_mandatory_run_output(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    inline_resume = doc["inline_required_output"]["resume_docx_full_version_inline"]
    assert inline_resume["text"].startswith("NO_AUTHORIZED_RESUME_OUTPUT")
    assert "source_of_truth=current_e2e_run_artifacts_only" in inline_resume["text"]
    assert "final_resume_no_gap_markers" in inline_resume["text"]
    assert "Databricks Lakehouse" not in inline_resume["text"]
    gates_by_id = {gate["gate_id"]: gate for gate in doc["mandatory_inline_output_gates"]}
    assert gates_by_id["mandatory_resume_docx_inline_json_present"]["pass"] is False
    assert (
        gates_by_id["mandatory_resume_docx_inline_json_present"]["observed_value"]["current_run_authorized"]
        is False
    )


def test_clean_pass_bcg_surfaces_l6_hardening_without_failure_forensics(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_partnership_clean"
    for lane_name in GENERATED_LANES:
        lane = run / "lanes" / lane_name
        lane.mkdir(parents=True)
        (lane / "command_output.txt").write_text(f"{lane_name} authorized output\n", encoding="utf-8")
        if lane_name == "headline":
            (lane / "l6_shadow_eval_package.json").write_text("{}\n", encoding="utf-8")
        _write_json(
            lane / "x3_disposition.json",
            {
                "x3_code": "X3_ALLOW",
                "product_quality_status": "PASS",
                "runtime_generation_status": "REAL_LLM",
            },
        )
        _write_json(lane / "x2_gate_outputs.json", {"gates": []})
    final_resume_text = "Authorized resume output."
    (run / FINAL_RESUME_OUTPUT_TXT).write_text(final_resume_text, encoding="utf-8")
    (run / FINAL_RESUME_ASSEMBLY_JSON_RELPATH).parent.mkdir(parents=True, exist_ok=True)
    (run / FINAL_RESUME_ASSEMBLY_JSON_RELPATH).write_text('{"status":"PASS"}\n', encoding="utf-8")
    assembly_dir = run / "modular_r4" / "final_resume_assembly"
    _write_json(
        assembly_dir / "final_resume_x2_gate_outputs.json",
        {"gates": [{"gate_id": "x2_final_resume", "pass": True}]},
    )
    _write_json(
        assembly_dir / "full_resume_llm_coherence_review.json",
        {
            "full_resume_coherence_pass": True,
            "aggregation_method": "unit_fixture",
            "judge_verdicts": [
                {
                    "judge_id": "openai",
                    "provider_name": "OpenAI",
                    "model_name": "gpt-test",
                    "score": 4.8,
                    "threshold": 4.0,
                    "pass": True,
                    "provider_status": "MODEL_BACKED",
                }
            ],
        },
    )
    (run / FINAL_RESUME_DOCX_RELPATH).parent.mkdir(parents=True, exist_ok=True)
    (run / FINAL_RESUME_DOCX_RELPATH).write_text("docx-bytes", encoding="utf-8")
    _write_json(
        run / FINAL_RESUME_OUTPUT_JSON,
        {
            "schema_version": "apps_rg.final_resume_output.v1",
            "required": True,
            "status": "PASS",
            "failed_gate_ids": [],
            "gates": [],
            "final_resume_json": {
                "relpath": FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
                "exists": True,
                "bytes": 18,
                "sha256": "spine",
            },
            "rendered_resume_text": {
                "relpath": FINAL_RESUME_OUTPUT_TXT,
                "exists": True,
                "bytes": len(final_resume_text),
                "sha256": "resume",
            },
            "resume_docx": {
                "relpath": FINAL_RESUME_DOCX_RELPATH,
                "exists": True,
                "bytes": 10,
                "sha256": "docx",
            },
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "success", "outcome_authorized": True},
        emit_final_outputs=False,
    )

    payload = emitted["payload"]
    assert payload["section_failure_forensics"]["required"] is False
    assert not (run / SECTION_FAILURE_FORENSICS_DIR).exists()
    recommendations = payload["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"]
    assert any(
        row["priority"] == "PX"
        and row["recommendation"]
        == "Review L6 shadow observations as future-run hardening inputs, not product blockers."
        and "headline: future_run_advisory_only" in row["evidence"]
        for row in recommendations
    )
    evidence_map_text = "\n".join(
        row["path"] for row in payload["inline_required_output"]["bcg"]["evidence_map"]
    )
    assert "section_failure_forensics" not in evidence_map_text
    gates_by_id = {gate["gate_id"]: gate for gate in payload["mandatory_inline_output_gates"]}
    assert gates_by_id["mandatory_bcg_p0_p1_px_recommendations_locked"]["pass"] is True


def test_failed_lane_table_hydrates_provider_proof_from_current_run(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_partnership_provider_proof"
    lane = run / "lanes" / "unify_bullets"
    lane.mkdir(parents=True)
    (lane / "unify_bullets_output.txt").write_text("generated but blocked\n", encoding="utf-8")
    _write_json(
        lane / "provider_request.json",
        {
            "provider_requested": "external_claude",
            "provider_attempted": True,
            "model": "claude-sonnet-5",
        },
    )
    _write_json(
        lane / "l2_output.json",
        {
            "section_id": "unify_bullets",
            "runtime_generation_status": "REAL_LLM",
        },
    )
    _write_json(
        lane / "x3_disposition.json",
        {
            "x3_code": "X3_BLOCK",
            "product_quality_status": "FAIL",
            "runtime_generation_status": "REAL_LLM",
        },
    )
    _write_json(
        lane / "x2_gate_outputs.json",
        {
            "gates": [
                {
                    "gate_id": "x2_unify_metric_source_required",
                    "pass": False,
                    "failure_reason": "missing metric source",
                }
            ]
        },
    )
    _write_json(
        run / "modular_r4" / "section_provider_calls.json",
        {
            "schema_version": "apps_rg.section_provider_calls.phase1.v2",
            "records": [
                {
                    "section_lane": "unify_bullets",
                    "provider_call_attempted": False,
                    "provider_profile": "external_claude_section_lane",
                    "model_id": "",
                    "candidate_index": 1,
                    "generation_status": "MISSING_LANE_RUN",
                }
            ],
        },
    )

    doc = build_mandatory_run_output(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    row = next(row for row in doc["section_lane_table"] if row["section"] == "unify_bullets")
    assert row["provider_call_attempted"] is True
    assert row["primary_provider"] == "external_claude"
    assert row["primary_model_observed"] == "claude-sonnet-5"
    assert row["generation_status"] == "REAL_LLM"
    recommendations = doc["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"]
    assert not any(
        "Capture provider attempts" in str(row.get("recommendation") or "") for row in recommendations
    )


def test_full_run_section_status_loads_lane_judges(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_judges01"
    lane = run / "lanes" / "headline"
    lane.mkdir(parents=True)
    (lane / "headline_output.txt").write_text("SVP Engineering\n", encoding="utf-8")
    _write_json(
        lane / "x3_disposition.json",
        {
            "x3_code": "X3_ALLOW",
            "product_quality_status": "PASS",
            "runtime_generation_status": "REAL_LLM",
        },
    )
    _write_json(lane / "x2_gate_outputs.json", {"gates": []})
    _write_json(
        lane / "x1d_llm_judge_outputs.json",
        {
            "judges": [
                {
                    "provider_name": "Gemini",
                    "model_name": "gemini-test",
                    "score": 5.0,
                    "threshold": 4.0,
                    "pass": True,
                    "provider_status": "MODEL_BACKED",
                }
            ]
        },
    )

    rows = collect_full_run_section_status(run, repo_root=tmp_path)
    headline = next(row for row in rows if row.lane == "headline")
    assert "Gemini" in headline.judge_summary
    assert headline.judge_details[0]["model_name"] == "gemini-test"


def test_mandatory_outputs_collect_modular_r4_sections(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_custom_run"
    _write_json(
        run / "modular_r4" / "phase1_lane_inventory.json",
        {
            "lane_argv_targeting": {
                "target_company": "Anthropic",
                "target_title": "Manager of Applied AI Architecture, Partnerships",
                "briefing_source": "RUN_SPECIFIC",
                "briefing_digest": "brief-digest-123",
                "briefing_ref_used": "tests/fixtures/apps_rg/brief_anthropic_partnerships_2026.json",
                "briefing_text": json.dumps(
                    {
                        "target_company": "Anthropic",
                        "target_role": "Manager of Applied AI Architecture, Partnerships",
                        "source": "RUN_SPECIFIC",
                        "briefing_text": "Partner-enabled enterprise AI adoption briefing.",
                    }
                ),
            }
        },
    )
    _write_json(
        run / "ingress_raw.json",
        {
            "auto_research_internal": True,
            "manual_brief": "tests/fixtures/apps_rg/brief_anthropic_partnerships_2026.json",
        },
    )
    _write_json(run / "spine_run_manifest.json", {"research_delegation_executed": False})
    lane = run / "modular_r4" / "sections" / "competencies"
    lane.mkdir(parents=True, exist_ok=True)
    _write_json(
        lane / "integrated_lane_pre_run_failure.json",
        {
            "blocker": "EXECUTED_X3A",
            "lane_exec_status": (
                "L2_EXECUTION_ERROR:PoolSelectorUnavailableError:"
                "competencies selector unavailable: no parsed candidate paths; "
                "first failure: External provider HTTP 400: `temperature` is deprecated for this model."
            ),
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    payload = emitted["payload"]
    briefing = payload["section_lane_table"][0]
    assert briefing["order"] == 0
    assert briefing["section"] == "research_briefing_input"
    assert briefing["provider_call_attempted"] is False
    assert briefing["research_source_class"] == "STATIC_MANUAL_BRIEF"
    assert briefing["primary_provider"] == "STATIC_MANUAL_BRIEF"
    assert briefing["primary_model_observed"] == "NOT_OBSERVED"
    assert briefing["generation_status"] == "P0_STATIC_MANUAL_BRIEF_USED"
    assert "NOT_OBSERVED" in briefing["x2"]
    assert "missing_apps_research_envelope" in briefing["x2"]
    assert briefing["x3"] == "FAIL"
    assert "auto_research_internal=True" in briefing["past_fail_blocker"]
    assert "research_delegation_executed=False" in briefing["past_fail_blocker"]
    assert "brief-digest-123" in briefing["past_fail_blocker"]
    assert "briefing_text_chars=" in briefing["past_fail_blocker"]
    assert payload["section_lane_table"][1]["section"] == "competencies"
    assert payload["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"][0]["priority"] == "P0"
    assert (
        payload["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"][0]["recommendation"]
        == "Fail closed when auto_research_internal=True but apps_research delegation does not execute."
    )
    comp = next(row for row in payload["sections"] if row["section"] == "competencies")
    assert comp["status_bucket"] == "pre_run_blocked"
    assert "temperature" in comp["failure_classification"]
    assert payload["section_counts"]["total"] >= 1
    assert payload["rca_findings"]


def test_mandatory_outputs_rca_classifies_selector_timeout(tmp_path: Path) -> None:
    run = tmp_path / "selector_timeout_run"
    lane = run / "modular_r4" / "sections" / "competencies"
    lane.mkdir(parents=True, exist_ok=True)
    _write_json(
        lane / "integrated_lane_pre_run_failure.json",
        {
            "blocker": "EXECUTED_X3A",
            "lane_exec_status": (
                "dispatch_error:L2_EXECUTION_ERROR:PoolSelectorUnavailableError:"
                "competencies selector unavailable: Anthropic pool selector selector_timeout "
                "after 90.141s (budget 90.0s): TimeoutError: The read operation timed out"
            ),
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    payload = emitted["payload"]
    comp = next(row for row in payload["sections"] if row["section"] == "competencies")
    assert comp["failure_classification"].startswith("Provider selector timeout:")

    finding = next(row for row in payload["rca_findings"] if row["section"] == "competencies")
    assert "live provider call" in finding["root_cause"]
    assert "dependency graph" not in finding["root_cause"]
    allocation = finding["causal_allocation"]
    assert allocation["dominant_cause"].startswith("The competencies selector provider request")
    domains = [row["domain"] for row in allocation["allocation"]]
    assert "Provider selector budget" in domains


def test_mandatory_row0_reports_apps_research_provider_when_handoff_missing(tmp_path: Path) -> None:
    run = tmp_path / "delegated_research_missing_handoff"
    run.mkdir()
    brief = tmp_path / "delegated_briefing.txt"
    brief.write_text("Fresh delegated briefing text.", encoding="utf-8")
    _write_json(
        run / "ingress_raw.json",
        {
            "auto_research_internal": True,
            "manual_brief": str(brief),
            "research_via": "apps_research",
        },
    )
    _write_json(run / "spine_run_manifest.json", {"research_delegation_executed": True})

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    briefing = emitted["payload"]["section_lane_table"][0]
    assert briefing["research_source_class"] == "FRESH_APPS_RESEARCH"
    assert briefing["primary_provider"] == "external_openai"
    assert briefing["primary_model_observed"] == "gpt-5.4-mini-2026-03-17"
    assert briefing["x2"] == "NOT_OBSERVED; blocker=missing_apps_research_envelope"
    assert briefing["x3"] == "NOT_OBSERVED; blocker=missing_apps_research_envelope"


def test_mandatory_row0_surfaces_apps_research_source_class_and_x2_x3(tmp_path: Path) -> None:
    run = tmp_path / "authorized_research_handoff"
    run.mkdir()
    brief = tmp_path / "briefing.md"
    jd = tmp_path / "jd.txt"
    brief_text = "Fresh apps_research handoff briefing for Anthropic partnerships."
    jd_text = "Manager of Applied AI Architecture, Partnerships at Anthropic."
    brief.write_text(brief_text, encoding="utf-8")
    jd.write_text(jd_text, encoding="utf-8")
    brief_sha = hashlib.sha256(brief_text.encode("utf-8")).hexdigest()
    jd_sha = hashlib.sha256(jd_text.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)
    _write_json(
        tmp_path / "apps_research_briefing_envelope.json",
        {
            "schema_version": "apps_research.apps_rg_briefing_envelope.v1",
            "producer_app": "apps_research",
            "consumer_app": "apps_rg",
            "run_id": "research-run-row0",
            "target_company": "Anthropic",
            "target_role": "Manager Applied AI Architecture Partnerships",
            "generated_at_utc": now.isoformat(),
            "expires_at_utc": (now + timedelta(days=7)).isoformat(),
            "dry_run": False,
            "stub_detected": False,
            "is_stale": False,
            "handoff_eligible": True,
            "generation_provider": "external_openai",
            "generation_model": "gpt-5.4-mini-2026-03-17",
            "provider_call_attempted": True,
            "brief_sha256": brief_sha,
            "jd_sha256": jd_sha,
            "apps_research_x1_x3_authorization": {
                "schema_version": "apps_research.apps_rg_handoff_x1_x3_authorization.v1",
                "run_id": "research-run-row0",
                "brief_sha256": brief_sha,
                "jd_sha256": jd_sha,
                "x1": {"gate_id": "X1_TARGETING_BRIEF_CONTRACT", "status": "PASS"},
                "x2": {
                    "gate_id": "X2_RESEARCH_SEMANTIC_GATE",
                    "status": "PASS",
                    "score": 0.94,
                    "threshold": 0.75,
                    "judge_name": "gemini_pro",
                    "judge_provider": "gemini_pro",
                    "judge_model": "gemini-3.1-pro-preview",
                    "model_backed": True,
                    "provider_status": "MODEL_BACKED_PASS",
                },
                "x3": {
                    "gate_id": "X3_HANDOFF_AUTHORIZATION",
                    "status": "PASS",
                    "disposition": "ALLOW",
                },
            },
        },
    )
    _write_json(
        run / "ingress_raw.json",
        {
            "auto_research_internal": True,
            "manual_brief": str(brief),
            "job_description_ref": str(jd),
        },
    )
    _write_json(run / "spine_run_manifest.json", {"research_delegation_executed": True})

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    briefing = emitted["payload"]["section_lane_table"][0]
    assert briefing["section"] == "research_briefing_input"
    assert briefing["provider_call_attempted"] is True
    assert briefing["research_source_class"] == "FRESH_APPS_RESEARCH"
    assert briefing["primary_provider"] == "external_openai"
    assert briefing["primary_model_observed"] == "gpt-5.4-mini-2026-03-17"
    assert briefing["x2"] == "PASS; 0.94; judge=gemini-3.1-pro-preview"
    assert briefing["x3"] == "ALLOW; X1=PASS"
    assert all(
        gate["pass"]
        for gate in emitted["payload"]["mandatory_inline_output_gates"]
        if gate["gate_id"] == "mandatory_apps_research_row0_x1_x2_x3_gates_locked"
    )
    mandatory = (run / MANDATORY_RUN_OUTPUT_MD).read_text(encoding="utf-8")
    assert "Research source class" in mandatory
    assert "FRESH_APPS_RESEARCH" in mandatory
    assert "ALLOW; X1=PASS" in mandatory
    recommendations = emitted["payload"]["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"]
    recommendation_text = "\n".join(row["recommendation"] for row in recommendations)
    assert "Add research source class to the locked BCG and lane table." not in recommendation_text
    assert "Compare latest run to prior passing research wiring" not in recommendation_text


def test_bcg_recommendations_are_evidence_backed_for_fresh_research_blocked_lanes(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_fresh_blocked_lanes"
    brief = tmp_path / "delegated_briefing.txt"
    brief.write_text("Fresh delegated briefing text.", encoding="utf-8")
    _write_json(
        run / "modular_r4" / "phase1_lane_inventory.json",
        {
            "lane_argv_targeting": {
                "target_company": "Anthropic",
                "target_title": "Manager of Applied AI Architecture, Partnerships",
                "briefing_source": "RUN_SPECIFIC",
                "briefing_digest": "brief-digest-fresh",
                "briefing_ref_used": str(brief),
                "briefing_text": "Fresh delegated briefing text.",
            }
        },
    )
    _write_json(run / "ingress_raw.json", {"auto_research_internal": True, "manual_brief": str(brief)})
    _write_json(run / "spine_run_manifest.json", {"research_delegation_executed": True})

    for lane_name in GENERATED_LANES:
        lane = run / "modular_r4" / "sections" / lane_name
        lane.mkdir(parents=True, exist_ok=True)
        blocked = lane_name in {"insurtech_bullets", "headline"}
        if lane_name != "insurtech_bullets":
            display_name = {
                "headline": "headline_output.txt",
                "executive_summary": "resume_display_text.txt",
                "competencies": "competencies_display.txt",
            }.get(lane_name, f"{lane_name}_output.txt")
            (lane / display_name).write_text(f"{lane_name} output\n", encoding="utf-8")
        _write_json(
            lane / "x3_disposition.json",
            {
                "x3_code": "X3_BLOCK" if blocked else "X3_ALLOW",
                "product_quality_status": "FAIL" if lane_name == "insurtech_bullets" else "PASS",
                "runtime_generation_status": "REAL_LLM",
                "decisive_judge_failures": ["gemini_pro"] if blocked else [],
            },
        )
        _write_json(
            lane / "x2_gate_outputs.json",
            {
                "gates": [
                    {
                        "gate_id": "x2_insurtech_bullets_bullet_count_3",
                        "pass": False,
                        "failure_reason": "expected exactly 3 bullets",
                    }
                ]
                if lane_name == "insurtech_bullets"
                else []
            },
        )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    payload = emitted["payload"]
    recommendations = payload["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"]
    recommendation_text = "\n".join(row["recommendation"] for row in recommendations)
    evidence_text = "\n".join(row["evidence"] for row in recommendations)
    next_moves = payload["inline_required_output"]["bcg"]["recommended_next_move"]
    gates_by_id = {gate["gate_id"]: gate for gate in payload["mandatory_inline_output_gates"]}

    assert any(
        row["priority"] == "P0"
        and row["recommendation"] == "Fix X3-blocked generated lanes before authorizing the final resume."
        and row["evidence"] == "insurtech_bullets, headline"
        for row in recommendations
    )
    assert "Add dependency-token reporting for every PHASE1_NO_RUN_DIR lane." not in recommendation_text
    assert "Add research source class to the locked BCG and lane table." not in recommendation_text
    assert "Compare latest run to prior passing research wiring" not in recommendation_text
    assert "PHASE1_NO_RUN_DIR" not in evidence_text
    assert "insurtech_bullets, headline" in next_moves[0]
    assert gates_by_id["mandatory_bcg_p0_p1_px_recommendations_locked"]["pass"] is False


def test_bcg_surfaces_final_aggregation_x2_failure_as_p0(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_final_aggregation_blocked"
    (run / "modular_r4" / "sections").mkdir(parents=True)
    for lane_name in GENERATED_LANES:
        lane = run / "modular_r4" / "sections" / lane_name
        lane.mkdir(parents=True, exist_ok=True)
        _write_json(
            lane / "x3_disposition.json",
            {
                "x3_code": "X3_ALLOW",
                "product_quality_status": "PASS",
                "runtime_generation_status": "REAL_LLM",
            },
        )
        _write_json(lane / "x2_gate_outputs.json", {"gates": []})
    asm = run / "modular_r4" / "final_resume_assembly"
    asm.mkdir(parents=True)
    (asm / "final_resume.json").write_text('{"sections":[]}\n', encoding="utf-8")
    _write_json(
        asm / "final_resume_x2_gate_outputs.json",
        {
            "gates": [
                {
                    "gate_id": "x2_full_resume_llm_coherence_aggregation",
                    "pass": False,
                    "failure_reason": "deterministic_blocker",
                    "observed_value": {"blockers": ["judge_quorum_insufficient:model_backed=0 required=2"]},
                }
            ]
        },
    )
    _write_json(
        asm / "full_resume_llm_coherence_review.json",
        {
            "full_resume_coherence_pass": False,
            "decisive_reason": "deterministic_blocker",
            "blockers": ["judge_quorum_insufficient:model_backed=0 required=2"],
            "model_backed_pass_count": 0,
            "model_backed_total": 0,
            "quorum_required": 2,
        },
    )
    _write_json(
        asm / "x1d_full_resume_judge_outputs.json",
        {
            "judges": [
                {
                    "judge_id": "x1d_gemini_pro_full_resume_coherence",
                    "provider_name": "Google Gemini 3.1 Pro Preview",
                    "provider_key": "gemini_pro",
                    "model_name": "gemini-3.1-pro-preview",
                    "provider_status": "BLOCKED_PROVIDER_ERROR",
                    "pass": False,
                    "threshold": 0.8,
                }
            ],
            "aggregation": {
                "full_resume_coherence_pass": False,
                "aggregation_method": "quorum_majority_model_backed",
                "model_backed_pass_count": 0,
                "model_backed_total": 0,
            },
        },
    )
    _write_json(
        run / FINAL_RESUME_OUTPUT_JSON,
        {
            "schema_version": "apps_rg.final_resume_output.v1",
            "required": True,
            "status": "PASS",
            "failed_gate_ids": [],
            "final_resume_json": {"relpath": FINAL_RESUME_ASSEMBLY_JSON_RELPATH, "exists": True, "bytes": 12},
            "rendered_resume_text": {"relpath": FINAL_RESUME_OUTPUT_TXT, "exists": True, "bytes": 64},
            "resume_docx": {"relpath": FINAL_RESUME_DOCX_RELPATH, "exists": True, "bytes": 64},
            "gates": [],
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    payload = emitted["payload"]
    final_section = next(
        section for section in payload["sections"] if section["section"] == "final_resume_aggregation"
    )
    final_rca = next(
        finding for finding in payload["rca_findings"] if finding["section"] == "final_resume_aggregation"
    )
    recommendations = payload["inline_required_output"]["bcg"]["p0_p1_px_recommendations"]["rows"]
    issue_tree = payload["inline_required_output"]["bcg"]["issue_tree"]
    board = payload["inline_required_output"]["bcg"]["board_level_readout"]["rows"]
    gates_by_id = {gate["gate_id"]: gate for gate in payload["mandatory_inline_output_gates"]}

    assert final_section["x2_pass"] == "FAIL"
    assert "provider quorum" in final_section["failure_classification"].lower()
    assert [gate["gate_id"] for gate in final_section["failed_gates"]] == [
        "x2_full_resume_llm_coherence_aggregation"
    ]
    assert "full-resume coherence judge panel" in final_rca["root_cause"]
    assert "required-lane authorization ledger" not in final_rca["root_cause"]
    assert "Provider artifact persistence" in {
        row["domain"] for row in final_rca["causal_allocation"]["allocation"]
    }
    assert any(
        "long-path" in item or "long-path" in item.lower() for item in final_rca["implementation_plan"]
    )
    assert any(
        row["priority"] == "P0"
        and row["recommendation"] == "Fix final_resume_aggregation before authorizing the final resume."
        and "x2_full_resume_llm_coherence_aggregation" in row["evidence"]
        for row in recommendations
    )
    assert any(row["section"] == "final_resume_aggregation" for row in issue_tree)
    assert "final_resume_aggregation" in next(
        row["answer"] for row in board if row["question"] == "Primary blocker"
    )
    assert "x3_blocked=final_resume_aggregation" in next(
        gate["observed_value"]["blockers"]
        for gate in payload["mandatory_inline_output_gates"]
        if gate["gate_id"] == "mandatory_resume_text_inline_present"
    )
    assert gates_by_id["mandatory_bcg_p0_p1_px_recommendations_locked"]["pass"] is False

    summary = render(run)
    assert "Final resume aggregation failed gates: `x2_full_resume_llm_coherence_aggregation`" in summary


def test_bcg_classifies_final_aggregation_upstream_certification_failure(tmp_path: Path) -> None:
    run = tmp_path / "anthropic_final_aggregation_exec_summary_review_only"
    (run / "modular_r4" / "sections").mkdir(parents=True)
    for lane_name in GENERATED_LANES:
        lane = run / "modular_r4" / "sections" / lane_name
        lane.mkdir(parents=True, exist_ok=True)
        is_exec = lane_name == "executive_summary"
        _write_json(
            lane / "x3_disposition.json",
            {
                "x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL" if is_exec else "X3_ALLOW",
                "product_quality_status": "PASS",
                "runtime_generation_status": "REAL_LLM",
                "publish_disposition": "judge_certification_required" if is_exec else "product_authorized",
                "x1d_certified": False if is_exec else True,
                "blocking_judge_ids": ["gemini_pro"] if is_exec else [],
                "soft_failed_judges": ["gemini_pro"] if is_exec else [],
                "model_backed_pass_provider_keys": ["openai_chatgpt"] if is_exec else ["gemini_pro"],
            },
        )
        _write_json(lane / "x2_gate_outputs.json", {"gates": []})
        display_name = "resume_display_text.txt" if is_exec else f"{lane_name}_output.txt"
        (lane / display_name).write_text(f"{lane_name} output\n", encoding="utf-8")

    asm = run / "modular_r4" / "final_resume_assembly"
    asm.mkdir(parents=True)
    (asm / "final_resume.json").write_text('{"sections":[]}\n', encoding="utf-8")
    _write_json(
        asm / "final_resume_x2_gate_outputs.json",
        {
            "gates": [
                {
                    "gate_id": "x2_generated_sections_from_latest_successful_real",
                    "pass": False,
                    "failure_reason": "section_resolution_not_accepted",
                    "observed_value": "executive_summary resolution not accepted: modular_r4_explicit_run_dir; publish_disposition=judge_certification_required; blocking_judge_ids=gemini_pro",
                }
            ]
        },
    )
    _write_json(
        asm / "full_resume_llm_coherence_review.json",
        {
            "full_resume_coherence_pass": True,
            "model_backed_pass_count": 2,
            "quorum_required": 2,
        },
    )
    _write_json(
        asm / "x1d_full_resume_judge_outputs.json",
        {
            "judges": [
                {
                    "provider_name": "Google Gemini 3.1 Pro Preview",
                    "provider_key": "gemini_pro",
                    "model_name": "gemini-3.1-pro-preview",
                    "provider_status": "MODEL_BACKED_PASS",
                    "score": 5,
                    "threshold": 4,
                    "pass": True,
                },
                {
                    "provider_name": "OpenAI ChatGPT",
                    "provider_key": "openai_chatgpt",
                    "model_name": "gpt-5.5",
                    "provider_status": "MODEL_BACKED_PASS",
                    "score": 4.4,
                    "threshold": 4,
                    "pass": True,
                },
            ],
            "aggregation": {
                "full_resume_coherence_pass": True,
                "model_backed_pass_count": 2,
                "model_backed_total": 2,
            },
        },
    )
    _write_json(
        run / FINAL_RESUME_OUTPUT_JSON,
        {
            "schema_version": "apps_rg.final_resume_output.v1",
            "required": True,
            "status": "PASS",
            "failed_gate_ids": [],
            "final_resume_json": {"relpath": FINAL_RESUME_ASSEMBLY_JSON_RELPATH, "exists": True, "bytes": 12},
            "rendered_resume_text": {"relpath": FINAL_RESUME_OUTPUT_TXT, "exists": True, "bytes": 64},
            "resume_docx": {"relpath": FINAL_RESUME_DOCX_RELPATH, "exists": True, "bytes": 64},
            "gates": [],
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={"exit_status": "error", "outcome_authorized": False},
    )

    payload = emitted["payload"]
    final_section = next(
        section for section in payload["sections"] if section["section"] == "final_resume_aggregation"
    )
    final_rca = next(
        finding for finding in payload["rca_findings"] if finding["section"] == "final_resume_aggregation"
    )

    assert "upstream certification" in final_section["failure_classification"].lower()
    assert "provider quorum" not in final_section["failure_classification"].lower()
    assert "review-only" in final_rca["root_cause"]
    assert "Section certification / X3 authority" in {
        row["domain"] for row in final_rca["causal_allocation"]["allocation"]
    }
    assert any("judge-certification soft fail" in item for item in final_rca["implementation_plan"])


def test_mandatory_result_summary_prefers_patch_pass_over_prior_terminal_fault(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_patch_pass"
    run.mkdir()
    _write_json(
        run / "terminal_ret_packet.json",
        {
            "payload": {
                "l2_fault": "L2_EXECUTION_ERROR:old failed wrapper",
                "x3_disposition": "X3A",
                "run_id": "old-run",
            }
        },
    )

    emitted = emit_mandatory_run_outputs(
        run,
        repo_root=tmp_path,
        result={
            "decisive_status": "PASS",
            "all_lanes_authorized": True,
            "exit_code": 0,
        },
    )

    summary = emitted["payload"]["result_summary"]
    assert summary["exit_status"] == "success"
    assert summary["execution_status"] == "completed"
    assert summary["outcome_authorized"] is True
    assert summary["x3_disposition"] == "X3_ALLOW"
    assert summary["fault"] == ""
    assert summary["decisive_status"] == "PASS"
    bcg = (run / BCG_EXECUTIVE_OUTPUT_MD).read_text(encoding="utf-8")
    assert "BCG Executive Output - apps_rg Run" in bcg
    assert "P0/P1/PX Recommendations" in bcg
    assert "Keep final resume product gate failed while generated-section gap markers exist." in bcg
    assert "Resolve P0:" in bcg


def test_review_index_points_to_mandatory_outputs(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_review01"
    run.mkdir()
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("# BCG\n", encoding="utf-8")
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# Ledger\n", encoding="utf-8")
    (run / MANDATORY_RUN_OUTPUT_JSON).write_text("{}\n", encoding="utf-8")

    index = write_review_index(run).read_text(encoding="utf-8")

    assert BCG_EXECUTIVE_OUTPUT_MD in index
    assert OUTPUT_BISECT_MD in index
    assert MANDATORY_RUN_OUTPUT_MD in index
    assert MANDATORY_RUN_OUTPUT_JSON in index


def test_render_run_summary_surfaces_mandatory_output_status(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_render01"
    run.mkdir()
    _write_json(
        run / MANDATORY_RUN_OUTPUT_JSON,
        {
            "result_summary": {"exit_status": "error", "outcome_authorized": False},
            "section_counts": {
                "total": 1,
                "ran_real_llm": 1,
                "allowed": 0,
                "blocked": 1,
                "pre_run_blocked": 0,
                "not_run": 0,
            },
            "rca_findings": [
                {
                    "section": "competencies",
                    "classification": "Evidence mapping failure",
                    "root_cause": "Visible content rendered without complete source lineage.",
                    "evidence": "x2_graph",
                    "implementation_plan": [
                        "List every visible term missing source lineage.",
                        "Patch enrichment so visible terms require canonical source facts.",
                        "Block display rendering when lineage coverage is incomplete.",
                    ],
                    "causal_allocation": _valid_causal_allocation(),
                }
            ],
        },
    )
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# Ledger\n", encoding="utf-8")
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("# BCG\n", encoding="utf-8")
    (run / OUTPUT_BISECT_MD).write_text(
        "# apps_rg Output Bisect\n### Layperson RCA\nRetry evidence.\n",
        encoding="utf-8",
    )

    out = render(run)

    assert "## Mandatory Outputs (1/2/3/4)" in out
    assert "## Locked Output Bisect" in out
    assert "Evidence mapping failure" in out
    assert "Causal allocation" in out
    assert "Retry recoverability" in out
    assert "Required implementation plan" in out
    assert "Patch enrichment so visible terms require canonical source facts." in out
    assert "real LLM `1`" in out
    assert "## Locked BCG Output" in out
    assert "## Locked Section Lane Summary Table" in out
    assert "## Resume DOCX Full Version Inline" in out


def test_render_run_summary_can_render_without_backfilling_l7(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = tmp_path / "non_mutating_render"
    run.mkdir()
    monkeypatch.setattr(
        "tools.apps_rg.render_run_summary.emit_l7_audit_ability_output",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not backfill")),
    )

    out = render(run, emit_missing_l7=False)

    assert "apps_rg Run Summary" in out
    assert not (run / L7_AUDIT_ABILITY_OUTPUT_MD).exists()


def test_render_run_summary_uses_locked_resume_inline_not_raw_final_resume(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_render_locked_inline"
    run.mkdir()
    stale_resume = "SVP Engineering | Databricks Lakehouse Retrieval Architecture"
    (run / FINAL_RESUME_OUTPUT_TXT).write_text(stale_resume + "\n", encoding="utf-8")
    _write_json(
        run / MANDATORY_RUN_OUTPUT_JSON,
        {
            "result_summary": {"exit_status": "error", "outcome_authorized": False},
            "section_counts": {
                "total": 1,
                "ran_real_llm": 1,
                "allowed": 0,
                "blocked": 1,
                "pre_run_blocked": 0,
                "not_run": 0,
            },
            "section_lane_table": [],
            "final_resume_output": {
                "status": "FAIL",
                "failed_gate_ids": ["final_resume_no_gap_markers"],
                "final_resume_json": {
                    "relpath": FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
                    "exists": True,
                    "bytes": 10,
                },
                "rendered_resume_text": {
                    "relpath": FINAL_RESUME_OUTPUT_TXT,
                    "exists": True,
                    "bytes": len(stale_resume),
                },
                "resume_docx": {
                    "relpath": FINAL_RESUME_DOCX_RELPATH,
                    "exists": True,
                    "bytes": 10,
                },
            },
            "mandatory_inline_output_gates": [
                {"gate_id": "mandatory_resume_text_inline_present", "pass": False},
                {"gate_id": "mandatory_final_resume_json_present", "pass": False},
                {"gate_id": "mandatory_resume_docx_present", "pass": False},
            ],
            "inline_required_output": {
                "resume_docx_full_version_inline": {
                    "title": "Resume DOCX Full Version Inline",
                    "source": "No authorized resume text emitted; current E2E run only.",
                    "text": "NO_AUTHORIZED_RESUME_OUTPUT\nsource_of_truth=current_e2e_run_artifacts_only",
                }
            },
            "rca_findings": [],
        },
    )
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# Ledger\n", encoding="utf-8")
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("# BCG\n", encoding="utf-8")

    out = render(run)

    assert "NO_AUTHORIZED_RESUME_OUTPUT" in out
    assert "EXISTS_UNAUTHORIZED" in out
    assert stale_resume not in out


def test_render_run_summary_rejects_one_line_rca_action_as_format_gap(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_render_old_rca01"
    run.mkdir()
    _write_json(
        run / MANDATORY_RUN_OUTPUT_JSON,
        {
            "result_summary": {"exit_status": "error", "outcome_authorized": False},
            "section_counts": {
                "total": 1,
                "ran_real_llm": 1,
                "allowed": 0,
                "blocked": 1,
                "pre_run_blocked": 0,
                "not_run": 0,
            },
            "rca_findings": [
                {
                    "section": "competencies",
                    "classification": "Evidence mapping failure",
                    "evidence": "x2_graph",
                    "action": "Rerun the section.",
                }
            ],
        },
    )
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# Ledger\n", encoding="utf-8")
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("# BCG\n", encoding="utf-8")

    out = render(run)

    assert "RCA format gap" in out
    assert "missing 3-5 root-cause implementation bullets" in out
    assert "missing causal allocation" in out


def test_render_run_summary_rejects_root_cause_plan_without_causal_allocation(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_render_no_allocation01"
    run.mkdir()
    _write_json(
        run / MANDATORY_RUN_OUTPUT_JSON,
        {
            "result_summary": {"exit_status": "error", "outcome_authorized": False},
            "section_counts": {
                "total": 1,
                "ran_real_llm": 1,
                "allowed": 0,
                "blocked": 1,
                "pre_run_blocked": 0,
                "not_run": 0,
            },
            "rca_findings": [
                {
                    "section": "competencies",
                    "classification": "Evidence mapping failure",
                    "root_cause": "Visible content rendered without complete source lineage.",
                    "evidence": "x2_graph",
                    "implementation_plan": [
                        "List every visible term missing source lineage.",
                        "Patch enrichment so visible terms require canonical source facts.",
                        "Block display rendering when lineage coverage is incomplete.",
                    ],
                }
            ],
        },
    )
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# Ledger\n", encoding="utf-8")
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("# BCG\n", encoding="utf-8")

    out = render(run)

    assert "missing causal allocation with concrete root-cause-linked rows" in out


def test_exec_summary_evidence_mapping_rca_uses_exec_summary_density_language() -> None:
    allocation = _causal_allocation(
        {
            "section": "executive_summary",
            "failure_classification": "Evidence mapping failure",
            "failed_gates": [
                "x2_exec_summary_paragraph_max_words",
                "x2_exec_summary_no_mechanism_inventory",
                "x2_exec_summary_cross_fact_conflation_zero",
            ],
            "x2_gate_details": [
                {
                    "gate_id": "x2_exec_summary_cross_fact_conflation_zero",
                    "failure_reason": "cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence",
                }
            ],
        }
    )

    assert "executive summary" in allocation["dominant_cause"].lower()
    assert "competency surface" not in allocation["dominant_cause"].lower()
    assert any(
        "x2_exec_summary_cross_fact_conflation_zero" in row["evidence_refs"]
        for row in allocation["allocation"]
    )


def test_exec_summary_deterministic_gate_rca_names_synthesis_contract() -> None:
    failed_gates = [
        {
            "gate_id": "x2_exec_summary_allowed_fact_utilization",
            "failure_reason": "uncovered_required_brushstrokes=['reb_unify_platform_commercialization_leadership']",
            "observed_value": "uncovered_required_brushstrokes=['reb_unify_platform_commercialization_leadership']",
        },
        {
            "gate_id": "x2_executive_summary_synthesis_quality",
            "failure_reason": "robotic_transition_stack:3_in_s2_s5_matched=through that,building on that,that operating foundation",
            "observed_value": "robotic_transition_stack:3_in_s2_s5_matched=through that,building on that,that operating foundation",
        },
        {
            "gate_id": "x2_exec_summary_robotic_transition_stack_zero",
            "failure_reason": "robotic_transition_stack:3_in_s2_s5_matched=through that,building on that,that operating foundation",
            "observed_value": "robotic_transition_stack:3_in_s2_s5_matched=through that,building on that,that operating foundation",
        },
    ]

    classification = _classify_failure("executive_summary", failed_gates, {})
    allocation = _causal_allocation(
        {
            "section": "executive_summary",
            "failure_classification": classification,
            "failed_gates": failed_gates,
            "x2_gate_details": failed_gates,
        }
    )

    assert "Executive summary synthesis contract failure" in classification
    assert "repair path" in allocation["dominant_cause"]
    assert allocation["retry_recoverability"] == "MEDIUM"
    assert any(
        row["domain"] == "Composition-plan brushstroke coverage"
        and "x2_exec_summary_allowed_fact_utilization" in row["evidence_refs"]
        for row in allocation["allocation"]
    )
    assert "failed gate evidence has not been allocated" not in allocation["dominant_cause"]


def test_x1d_decisive_judge_failure_rca_surfaces_without_failed_x2_gates() -> None:
    judges = [
        {
            "provider": "Google Gemini 3.1 Pro Preview",
            "provider_key": "gemini_pro",
            "model": "gemini-3.1-pro-preview",
            "score": 0.0,
            "threshold": 4.0,
            "pass": False,
            "provider_status": "MODEL_BACKED_FAIL",
            "decisive_failure": True,
            "findings": [
                "The narrative claims experience with insurance operations, but the cited source fact only supports regulatory analytics.",
                "The claim ledger fails to cite reb_ey_insurance_core_modernization to support the insurance claim.",
            ],
            "dimension_verdicts": {
                "factual_support": {
                    "pass": False,
                    "severity": "major",
                    "codes": ["unsupported_claim", "missing_citation"],
                }
            },
        }
    ]

    classification = _classify_failure(
        "ey_narrative",
        [],
        {},
        x3_code="X3_BLOCK",
        judges=judges,
    )
    section = {
        "section": "ey_narrative",
        "status_bucket": "ran_real_llm",
        "x3_code": "X3_BLOCK",
        "failed_gates": [],
        "failure_classification": classification,
        "judges": judges,
        "judge_issue_summary": {"decisive_judge_failures": ["gemini_pro"]},
    }
    findings = _top_rca_sections([section])
    allocation = findings[0]["causal_allocation"]

    assert "X1D decisive judge failure" in classification
    assert findings[0]["section"] == "ey_narrative"
    assert "insurance operations" in findings[0]["evidence"]
    assert "claim-ledger" in findings[0]["root_cause"]
    assert allocation["retry_recoverability"] == "LOW_UNTIL_LEDGER_FIX"
    assert any(row["domain"] == "Claim ledger normalization" for row in allocation["allocation"])


def test_headline_vendor_display_gate_rca_names_positioning_contract() -> None:
    failed_gates = [
        {
            "gate_id": "x2_headline_executive_abstraction_floor",
            "failure_reason": "Each headline segment must express executive scope.",
            "observed_value": {
                "segments_missing_executive_abstraction": ["AWS Migration Modernization Execution"]
            },
        },
        {
            "gate_id": "x2_headline_vendor_terms_proof_only",
            "failure_reason": "Vendor/product terms may support proof, but display segments require an executive abstraction.",
            "observed_value": {
                "vendor_terms_without_executive_abstraction": ["AWS Migration Modernization Execution"]
            },
        },
    ]

    classification = _classify_failure("headline", failed_gates, {})
    allocation = _causal_allocation(
        {
            "section": "headline",
            "failure_classification": classification,
            "failed_gates": failed_gates,
        }
    )

    assert "Headline executive positioning contract failure" in classification
    assert "vendor-specific migration phrase" in allocation["dominant_cause"]
    assert allocation["retry_recoverability"] == "HIGH_AFTER_NORMALIZATION_FIX"
    assert any(
        row["domain"] == "Headline normalization / display policy"
        and "x2_headline_vendor_terms_proof_only" in row["evidence_refs"]
        for row in allocation["allocation"]
    )
