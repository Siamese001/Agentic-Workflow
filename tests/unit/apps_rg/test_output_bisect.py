from __future__ import annotations

import json
from pathlib import Path

import apps_rg.runtime.output_bisect as subject
from apps_rg.runtime.output_bisect import (
    build_section_output_bisect,
    render_output_bisect,
    validate_section_output_bisect,
)

# apps-test-model: APP CONTRACT


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_lane(
    lane: Path,
    *,
    passing: bool,
) -> None:
    lane.mkdir(parents=True)
    initial = (
        "Executive leader connects partner architecture with governed enterprise delivery."
        if passing
        else "Current first candidate with too many facts compressed into one sentence."
    )
    (lane / "raw_model_output.txt").write_text(
        json.dumps({"resume_display_text": initial}) + "\n",
        encoding="utf-8",
    )
    (lane / "resume_display_text.txt").write_text(initial + "\n", encoding="utf-8")
    _write_json(
        lane / "section_input_usage_ledger.json",
        {
            "input_refs": {
                "jd_text_hash": "jd-same",
                "briefing_hash": "brief-prior" if passing else "brief-current",
                "targeting_bundle_digest": "target-prior" if passing else "target-current",
                "graph_digest": "graph-prior" if passing else "graph-current",
                "selected_fact_plan_hash": "facts-prior" if passing else "facts-current",
            }
        },
    )
    _write_json(lane / "provider_request.json", {"request": "prior" if passing else "current"})
    if passing:
        _write_json(
            lane / "section_repair_ledger.json",
            {
                "authoritative_attempt_number": 1,
                "repairs": [
                    {
                        "seq": 1,
                        "kind": "deterministic_rewrite",
                        "operation": "repair_required_brushstroke_citation",
                        "reason": "ledger-only citation repair",
                        "replaced_l2": True,
                    }
                ],
            },
        )
        _write_json(
            lane / "x2_gate_outputs.json",
            {
                "gates": [
                    {"gate_id": "x2_exec_summary_no_sentence_fragment", "pass": True},
                    {"gate_id": "x2_exec_summary_cross_fact_conflation_zero", "pass": True},
                ]
            },
        )
        _write_json(
            lane / "x1d_llm_judge_outputs.json",
            {
                "judges": [
                    {
                        "judge_id": "gemini",
                        "provider_key": "gemini_pro",
                        "score": 5.0,
                        "threshold": 4.0,
                        "pass": True,
                        "provider_status": "MODEL_BACKED_PASS",
                        "input_hash": "candidate-prior",
                        "findings": ["clear and supported"],
                    },
                    {
                        "judge_id": "openai",
                        "provider_key": "openai_chatgpt",
                        "score": 4.5,
                        "threshold": 4.0,
                        "pass": True,
                        "provider_status": "MODEL_BACKED_PASS",
                        "input_hash": "candidate-prior",
                        "findings": ["strong executive signal"],
                    },
                ]
            },
        )
        _write_json(
            lane / "x3_disposition.json",
            {
                "x3_code": "X3_ALLOW",
                "pass": True,
                "final_summary_hash": "prior-final",
                "x1d_evaluator_mode": "MODEL_BACKED",
                "x2_failed_gates": [],
                "decisive_reason": "all gates and judges passed",
            },
        )
        return

    _write_json(
        lane / "synthesis_regen_receipt.json",
        {
            "triggered": True,
            "reject_reason": (
                "executive summary word count 167 exceeds maximum 150; "
                "cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence"
            ),
            "max_attempts": 2,
            "attempts": [
                {
                    "attempt": 1,
                    "call_id": "retry-1",
                    "candidate_digest": "1" * 64,
                    "reject_reason": (
                        "executive summary word count 167 exceeds maximum 150; "
                        "cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence"
                    ),
                    "regen_resume_word_count": 131,
                    "shape_failure_count": 1,
                    "monotonicity": {"accepted": True},
                },
                {
                    "attempt": 2,
                    "call_id": "retry-2",
                    "candidate_digest": "2" * 64,
                    "reject_reason": "cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence",
                    "regen_resume_word_count": 126,
                    "shape_failure_count": 1,
                    "monotonicity": {"accepted": True},
                },
            ],
            "accepted": False,
            "final_reject_reason": "cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence",
            "reverted_to_first_pass": True,
        },
    )
    _write_json(
        lane / "section_repair_ledger.json",
        {
            "authoritative_attempt_number": 1,
            "repairs": [
                {
                    "seq": 1,
                    "kind": "regen_llm",
                    "operation": "synthesis_regen",
                    "reason": "two retries retained fact conflation",
                    "replaced_l2": False,
                }
            ],
        },
    )
    _write_json(
        lane / "x2_gate_outputs.json",
        {
            "gates": [
                {
                    "gate_id": "x2_exec_summary_no_sentence_fragment",
                    "pass": False,
                    "failure_reason": "Sentence fragment detected",
                },
                {
                    "gate_id": "x2_exec_summary_cross_fact_conflation_zero",
                    "pass": False,
                    "failure_reason": "too many source facts in one sentence",
                },
            ]
        },
    )
    _write_json(lane / "x1d_llm_judge_outputs.json", {"judges": []})
    _write_json(
        lane / "x3_disposition.json",
        {
            "x3_code": "X3_BLOCK",
            "pass": False,
            "final_summary_hash": "current-final",
            "x1d_evaluator_mode": "NO_JUDGE_ROWS_EMITTED",
            "x2_failed_gates": [
                "x2_exec_summary_no_sentence_fragment",
                "x2_exec_summary_cross_fact_conflation_zero",
            ],
            "decisive_reason": "X2 deterministic gate failure",
        },
    )


def test_output_bisect_isolates_retry_failure_and_judges_not_reached(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline_run = tmp_path / "prior"
    current_run = tmp_path / "current"
    baseline_lane = baseline_run / "lane"
    current_lane = current_run / "lane"
    _write_lane(baseline_lane, passing=True)
    _write_lane(current_lane, passing=False)
    _write_json(baseline_run / "ingress_raw.json", {"manual_brief": "research/prior.md"})
    _write_json(current_run / "ingress_raw.json", {"manual_brief": "config/current.md"})
    _write_json(baseline_run / "u0_receipt.json", {"payload_digest": "u0-prior"})
    _write_json(current_run / "u0_receipt.json", {"payload_digest": "u0-current"})

    monkeypatch.setattr(
        subject,
        "_code_binding",
        lambda *args, **kwargs: {
            "role": args[-1],
            "file": args[-3],
            "symbol": args[-2],
            "baseline_symbol_hash": "a",
            "current_symbol_hash": "a",
            "changed_between_revisions": False,
            "status": "LATENT_PATH_PREEXISTED_BASELINE",
        },
    )

    doc = build_section_output_bisect(
        section_id="executive_summary",
        run_root=current_run,
        repo_root=tmp_path,
        current_lane=current_lane,
        baseline_run=baseline_run,
        baseline_lane=baseline_lane,
        baseline_revision={"git_commit": "a" * 40, "pr_number": 474},
        current_revision={"git_commit": "b" * 40},
    )

    assert doc["scope"] == "FULL_CAUSAL_BISECT"
    assert doc["first_observed_divergence"]["stage"] == "u0_ingress"
    assert doc["first_causally_relevant_divergence"]["stage"] == "retry_loop"
    assert (
        doc["underlying_root_cause"]["first_observed_divergence_root_cause"]["status"]
        == "NOT_CAUSALLY_ISOLATED"
    )
    assert (
        doc["underlying_root_cause"]["recovery_failure_root_cause"]["status"]
        == "ISOLATED"
    )
    retries = [
        row
        for row in doc["current_attempt_timeline"]
        if row["phase"] == "pre_judge_synthesis_retry"
    ]
    assert len(retries) == 2
    assert all(row["acceptance_scope"] == "MONOTONIC_IMPROVEMENT_ONLY" for row in retries)
    assert any(
        row["judge_result"] == "JUDGES_NOT_REACHED"
        for row in doc["current_attempt_timeline"]
    )
    assert any(row["judge"] == "gemini_pro" for row in doc["judge_matrix"])
    assert any(
        row["gate_id"] == "x2_exec_summary_no_sentence_fragment"
        and row["prior"] == "PASS"
        and row["current"] == "FAIL"
        for row in doc["gate_matrix"]
    )
    assert validate_section_output_bisect(doc) == []

    rendered = render_output_bisect([doc])
    assert "### Layperson RCA" in rendered
    assert "### Underlying Root Cause" in rendered
    assert "### Ingestion-To-Outcome Lineage" in rendered
    assert "MONOTONIC_IMPROVEMENT_ONLY" in rendered
    assert "JUDGES_NOT_REACHED" in rendered
    assert "PR #474 passed without a judge-driven retry" in rendered


def test_output_bisect_hard_stops_unisolated_code_cause() -> None:
    doc = {
        "schema_version": subject.OUTPUT_BISECT_SCHEMA_VERSION,
        "section_id": "executive_summary",
        "scope": "FULL_CAUSAL_BISECT",
        "first_observed_divergence": {"stage": "u0_ingress"},
        "first_causally_relevant_divergence": {"stage": "retry_loop"},
        "ingestion_to_outcome_lineage": [
            {"stage": "retry_loop", "classification": "CAUSAL"}
        ],
        "prior_attempt_timeline": [{"complete": True}],
        "current_attempt_timeline": [{"complete": True}],
        "gate_matrix": [{"gate_id": "g"}],
        "judge_matrix": [{"judge": "j"}],
        "code_bindings": [{"status": "CODE_CAUSE_NOT_ISOLATED"}],
        "code_cause_status": "CODE_CAUSE_NOT_ISOLATED",
        "underlying_root_cause": {
            "recovery_failure_root_cause": {
                "status": "EVIDENCE_GAP",
                "conclusion": "The code cause was not isolated.",
            }
        },
        "layperson_explanation": ["a" * 50, "b" * 50, "c" * 50],
    }

    assert "CODE_CAUSE_NOT_ISOLATED" in validate_section_output_bisect(doc)
