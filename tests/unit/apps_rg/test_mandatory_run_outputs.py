from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.full_resume_review_bundle import write_review_index
from apps_rg.runtime.full_run_section_status import collect_full_run_section_status
from apps_rg.runtime.mandatory_run_outputs import (
    BCG_EXECUTIVE_OUTPUT_MD,
    MANDATORY_RUN_OUTPUT_JSON,
    MANDATORY_RUN_OUTPUT_MD,
    emit_mandatory_run_outputs,
)
from tools.apps_rg.render_run_summary import render


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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
    bcg = (run / BCG_EXECUTIVE_OUTPUT_MD).read_text(encoding="utf-8")
    mandatory = (run / MANDATORY_RUN_OUTPUT_MD).read_text(encoding="utf-8")
    assert "Executive Answer" in bcg
    assert "Evidence mapping failure" in bcg
    assert "Causal allocation" in bcg
    assert "Retry recoverability" in bcg
    assert "Required implementation plan" in bcg
    assert "Change the section enrichment step" in bcg
    assert "Causal allocation" in mandatory
    assert "Required implementation plan" in mandatory


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
    comp = next(row for row in payload["sections"] if row["section"] == "competencies")
    assert comp["status_bucket"] == "pre_run_blocked"
    assert "temperature" in comp["failure_classification"]
    assert payload["section_counts"]["total"] >= 1
    assert payload["rca_findings"]


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
    assert "final resume output gate failed" in bcg
    assert "Fix the P0 blocker sections named above" not in bcg
    assert "Fix the final resume output gates before treating the run as product-ready" in bcg


def test_review_index_points_to_mandatory_outputs(tmp_path: Path) -> None:
    run = tmp_path / "full_resume_review01"
    run.mkdir()
    (run / BCG_EXECUTIVE_OUTPUT_MD).write_text("# BCG\n", encoding="utf-8")
    (run / MANDATORY_RUN_OUTPUT_MD).write_text("# Ledger\n", encoding="utf-8")
    (run / MANDATORY_RUN_OUTPUT_JSON).write_text("{}\n", encoding="utf-8")

    index = write_review_index(run).read_text(encoding="utf-8")

    assert BCG_EXECUTIVE_OUTPUT_MD in index
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

    out = render(run)

    assert "## Mandatory BCG / Run-Ledger Outputs" in out
    assert "Evidence mapping failure" in out
    assert "Causal allocation" in out
    assert "Retry recoverability" in out
    assert "Required implementation plan" in out
    assert "Patch enrichment so visible terms require canonical source facts." in out
    assert "real LLM `1`" in out


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
