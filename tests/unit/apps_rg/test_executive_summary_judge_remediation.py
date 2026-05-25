"""Unit tests: judge remediation trigger and repair user message."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    all_model_backed_judges_pass,
    any_model_backed_soft_fail,
    build_judge_remediation_prescriptive_delta_message,
    build_judge_remediation_user_message,
    evaluate_judge_remediation_trigger,
    rerun_soft_failed_judges,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import judge_regen_max_attempts


def _soft_fail_judge(provider_key: str, *, findings: list[str], score: float = 0.5) -> dict:
    return {
        "provider_key": provider_key,
        "provider_name": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "decisive_failure": False,
        "normalized_score": score,
        "normalized_threshold": 0.8,
        "findings": findings,
        "fail_reasons": [],
        "remediation_suggestions": [],
    }


def test_trigger_quorum_two_judges_shared_synthesis_tag() -> None:
    judges = [
        _soft_fail_judge("anthropic_claude", findings=["bullet-stack synthesis lacks weave"]),
        _soft_fail_judge("openai_gpt", findings=["paragraph reads as stacked bullets"]),
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 0.95,
            "normalized_threshold": 0.8,
        },
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "quorum_soft_fail"


def test_trigger_solitary_severe_soft_fail() -> None:
    judges = [
        _soft_fail_judge(
            "anthropic_claude",
            findings=[
                "Summary reads as stacked bullets; poor ATS alignment to enterprise architecture and IT strategy",
            ],
            score=0.7,
        ),
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 1.0,
            "normalized_threshold": 0.8,
        },
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 0.82,
            "normalized_threshold": 0.8,
        },
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "solitary_severe_soft_fail"


def test_trigger_skipped_when_x2_not_passed() -> None:
    ok, receipt = evaluate_judge_remediation_trigger(
        [], runtime_generation_status="REAL_LLM", x2_passed=False
    )
    assert ok is False
    assert receipt.get("reason") == "requires_real_llm_and_x2_pass"


def test_judge_regen_max_attempts_default_one(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_MAX_ATTEMPTS", raising=False)
    assert judge_regen_max_attempts() == 1


def test_all_model_backed_judges_pass_helpers() -> None:
    passing = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
        },
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
        },
    ]
    assert all_model_backed_judges_pass(passing) is True
    assert any_model_backed_soft_fail(passing) is False
    mixed = [
        *passing,
        _soft_fail_judge("anthropic_claude", findings=["weak synthesis"]),
    ]
    assert all_model_backed_judges_pass(mixed) is False
    assert any_model_backed_soft_fail(mixed) is True


def test_judge_remediation_user_message_includes_x2_floor() -> None:
    msg = build_judge_remediation_user_message(
        x1d_judges=[_soft_fail_judge("anthropic_claude", findings=["weak synthesis"])],
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=110,
        prior_ledger_rows=6,
    )
    assert "X2_FLOOR" in msg
    assert "110" in msg
    assert "6" in msg


def test_prescriptive_delta_locks_compile_core_runner_splits_anchor() -> None:
    from agentic_core.L2_execution.regen.prompt_lock import PROMPT_LOCK_GENERIC

    msg = build_judge_remediation_prescriptive_delta_message(
        x1d_judges=[_soft_fail_judge("anthropic_claude", findings=["weak synthesis"])],
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_resume_display_text="Sentence one. Sentence two.",
        prior_word_count=42,
        prior_ledger_rows=6,
    )
    assert "REGEN_DELTA_v1" in msg
    assert PROMPT_LOCK_GENERIC.split(".")[0] in msg
    assert "ANCHOR_DRAFT" not in msg
    assert "Sentence one. Sentence two." not in msg
    assert "synthesis" in msg.lower() or "weak" in msg.lower()
    assert "SYNTHESIS_SHAPE" not in msg
    assert "X2_PHRASE_GUARDS" not in msg


def test_remediation_user_message_lists_unused_facts_when_evidence_dim_fails() -> None:
    judge = _soft_fail_judge("anthropic_claude", findings=["underused facts"])
    judge["dimension_verdicts"] = {
        "evidence_utilization": {"pass": False, "severity": "major", "codes": ["underused_facts"]},
    }
    msg = build_judge_remediation_user_message(
        x1d_judges=[judge],
        unused_fact_ids=["fact_003", "fact_004"],
        allowed_fact_count=8,
    )
    assert "EVIDENCE_WEAVE" in msg or "fact_003" in msg
    assert "exactly 6 sentences" in msg.lower()


def test_remediation_user_message_legacy_block_includes_x2_phrase_guards(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_LEGACY_BLOCK", "1")
    msg = build_judge_remediation_user_message(
        x1d_judges=[_soft_fail_judge("anthropic_claude", findings=["weak synthesis"])],
        unused_fact_ids=[],
        allowed_fact_count=8,
    )
    assert "X2_PHRASE_GUARDS" in msg


def test_rerun_soft_failed_judges_uses_post_x2_packet_when_x2_gates_provided(
    tmp_path: Path,
    monkeypatch,
) -> None:
    captured: dict[str, str] = {}

    def _fake_run_llm_judges(**kwargs):
        captured["judge_packet_ref"] = str(kwargs.get("judge_packet_ref") or "")
        return []

    monkeypatch.setattr(
        "apps_rg.runtime.judges.executive_summary_x1d.run_llm_judges",
        _fake_run_llm_judges,
    )
    prior = [
        _soft_fail_judge("anthropic_claude", findings=["weak synthesis"]),
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        },
    ]
    rerun_soft_failed_judges(
        resume_display_text="Six sentence summary here for testing.",
        claim_ledger=[],
        judge_packet={"allowed_fact_ids": ["f1"]},
        judge_packet_ref=str(tmp_path / "executive_summary_judge_packet.json"),
        compiled_prompt=None,
        artifact_dir=tmp_path,
        judge_keys=["anthropic_claude", "gemini_pro"],
        judge_mode="mocked",
        prior_judges=prior,
        x2_gates=[{"gate_id": "x2_shape", "pass": True}],
        allowed_fact_packet=[{"fact_id": "f1", "claim_text": "Led platform work."}],
        allowed_fact_ids={"f1"},
        target_title="SVP",
        target_company="Acme",
        jd_text="jd",
        briefing_text="brief",
        parsed_output={"resume_display_text": "text", "claim_ledger": []},
    )
    assert captured["judge_packet_ref"].endswith("executive_summary_judge_packet_post_x2.json")
    assert (tmp_path / "executive_summary_judge_packet_post_x2.json").is_file()


def test_rerun_soft_failed_expands_to_full_panel_when_packet_hash_drifts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    captured: dict[str, list[str]] = {}

    def _fake_run_llm_judges(**kwargs):
        captured["judge_keys"] = list(kwargs.get("judge_keys") or [])
        return []

    monkeypatch.setattr(
        "apps_rg.runtime.judges.executive_summary_x1d.run_llm_judges",
        _fake_run_llm_judges,
    )
    prior = [
        _soft_fail_judge("anthropic_claude", findings=["weak synthesis"]),
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "judge_packet_hash": "old_hash_11111111",
            "input_hash": "old_hash_11111111",
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        },
    ]
    rerun_soft_failed_judges(
        resume_display_text="Six sentence summary here for testing.",
        claim_ledger=[],
        judge_packet={"allowed_fact_ids": ["f1"]},
        judge_packet_ref=str(tmp_path / "executive_summary_judge_packet.json"),
        compiled_prompt=None,
        artifact_dir=tmp_path,
        judge_keys=["anthropic_claude", "gemini_pro", "openai_chatgpt"],
        judge_mode="mocked",
        prior_judges=prior,
        x2_gates=[{"gate_id": "x2_shape", "pass": True}],
        allowed_fact_packet=[{"fact_id": "f1", "claim_text": "Led platform work."}],
        allowed_fact_ids={"f1"},
        target_title="SVP",
        target_company="Acme",
        jd_text="jd",
        briefing_text="brief",
        parsed_output={"resume_display_text": "text", "claim_ledger": []},
    )
    assert captured["judge_keys"] == ["anthropic_claude", "gemini_pro", "openai_chatgpt"]
