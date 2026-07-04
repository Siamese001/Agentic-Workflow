from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apps_rg.runtime.full_resume_review_bundle import write_review_index
from apps_rg.runtime.full_run_section_status import collect_full_run_section_status
from apps_rg.runtime.mandatory_run_outputs import (
    BCG_EXECUTIVE_OUTPUT_MD,
    MANDATORY_RUN_OUTPUT_JSON,
    MANDATORY_RUN_OUTPUT_MD,
    build_mandatory_run_output,
    emit_mandatory_run_outputs,
)
from apps_rg.runtime.run_output_contract import (
    FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
    FINAL_RESUME_DOCX_RELPATH,
    FINAL_RESUME_OUTPUT_JSON,
    FINAL_RESUME_OUTPUT_TXT,
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
    assert {"P0", "P1", "PX"}.issubset(
        {row["priority"] for row in inline["bcg"]["p0_p1_px_recommendations"]["rows"]}
    )
    gates_by_id = {gate["gate_id"]: gate for gate in payload["mandatory_inline_output_gates"]}
    assert gates_by_id["mandatory_inline_required_json_shape_locked"]["pass"] is True
    assert gates_by_id["mandatory_resume_docx_inline_json_present"]["pass"] is False
    assert gates_by_id["mandatory_resume_docx_inline_json_present"]["observed_value"][
        "current_run_authorized"
    ] is False
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
    bcg = (run / BCG_EXECUTIVE_OUTPUT_MD).read_text(encoding="utf-8")
    mandatory = (run / MANDATORY_RUN_OUTPUT_MD).read_text(encoding="utf-8")
    assert "BCG Executive Output - apps_rg Run" in bcg
    assert "P0/P1/PX Recommendations" in bcg
    assert "Evidence mapping failure" in bcg
    assert "Causal allocation" in bcg
    assert "Retry recoverability" in bcg
    assert "Required implementation plan" in bcg
    assert "Change the section enrichment step" in bcg
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
    assert gates_by_id["mandatory_resume_docx_inline_json_present"]["observed_value"][
        "current_run_authorized"
    ] is False


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
        "Capture provider attempts" in str(row.get("recommendation") or "")
        for row in recommendations
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
                "briefing_ref_used": "apps_rg/config/targeting/brief_anthropic_partnerships_2026.json",
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
            "manual_brief": "apps_rg/config/targeting/brief_anthropic_partnerships_2026.json",
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
    assert briefing["primary_provider"] == "STATIC_MANUAL_BRIEF"
    assert briefing["primary_model_observed"] == "NOT_OBSERVED"
    assert briefing["generation_status"] == "P0_STATIC_MANUAL_BRIEF_USED"
    assert briefing["x3"] == "FAIL"
    assert "handoff_observed=False" in briefing["apps_research_x1_x2_x3_gates"]
    assert "handoff_valid=False" in briefing["apps_research_x1_x2_x3_gates"]
    assert "missing_apps_research_envelope" in briefing["apps_research_x1_x2_x3_gates"]
    assert "X1=NOT_OBSERVED" in briefing["apps_research_x1_x2_x3_gates"]
    assert "X2=NOT_OBSERVED" in briefing["apps_research_x1_x2_x3_gates"]
    assert "X3=NOT_OBSERVED/NOT_OBSERVED" in briefing["apps_research_x1_x2_x3_gates"]
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


def test_mandatory_row0_surfaces_apps_research_x1_x2_x3_gates(tmp_path: Path) -> None:
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
                    "judge_model": "gpt-5.4-mini",
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
    assert briefing["primary_provider"] == "apps_research"
    assert briefing["x2"] == "PASS"
    assert briefing["x3"] == "ALLOW"
    assert "handoff_observed=True" in briefing["apps_research_x1_x2_x3_gates"]
    assert "handoff_valid=True" in briefing["apps_research_x1_x2_x3_gates"]
    assert "X1=PASS" in briefing["apps_research_x1_x2_x3_gates"]
    assert "X2=PASS score=0.94 judge_model=gpt-5.4-mini" in briefing["apps_research_x1_x2_x3_gates"]
    assert "X3=PASS/ALLOW" in briefing["apps_research_x1_x2_x3_gates"]
    assert all(
        gate["pass"]
        for gate in emitted["payload"]["mandatory_inline_output_gates"]
        if gate["gate_id"] == "mandatory_apps_research_row0_x1_x2_x3_gates_locked"
    )
    mandatory = (run / MANDATORY_RUN_OUTPUT_MD).read_text(encoding="utf-8")
    assert "apps_research X1/X2/X3 gates" in mandatory
    assert "X1=PASS" in mandatory


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
    assert "Fix P0 gates before rerun" in bcg


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
    assert "## Locked BCG Output" in out
    assert "## Locked Section Lane Summary Table" in out
    assert "## Resume DOCX Full Version Inline" in out


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
