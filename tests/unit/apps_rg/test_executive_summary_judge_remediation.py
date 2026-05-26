"""Unit tests: judge remediation trigger and repair user message."""

from __future__ import annotations

from pathlib import Path

from agentic_core.L2_execution.regen.delta_shape_guard import estimate_token_count
from agentic_core.L2_execution.regen.prompt_lock import DEFAULT_MAX_DELTA_TOKENS
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    all_model_backed_judges_pass,
    any_model_backed_soft_fail,
    build_judge_remediation_prescriptive_delta_message,
    build_judge_remediation_user_message,
    collect_judge_remediation_delta_lines,
    evaluate_judge_remediation_trigger,
    retry_qwen_for_judge_remediation,
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


def test_trigger_not_skipped_when_two_pass_and_decisive_synthesis_failure() -> None:
    """Quorum skip must not suppress regen when a third judge flags decisive synthesis failure."""
    judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 0.95,
            "normalized_threshold": 0.8,
            "findings": [],
        },
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
            "findings": [],
        },
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "decisive_failure": True,
            "normalized_score": 0.4,
            "normalized_threshold": 0.8,
            "findings": ["synthesis lacks executive connective tissue"],
            "fail_reasons": [],
            "remediation_suggestions": [],
        },
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "decisive_synthesis_or_executive_signal"
    assert receipt.get("reason") != "two_or_more_judges_already_pass_skip_regen"


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
    assert "6 sentences" in msg.lower() or "claim_ledger" in msg.lower()


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


def _claude_soft_fail_with_dimension_verdicts() -> dict:
    judge = _soft_fail_judge(
        "anthropic_claude",
        findings=[
            "Sentences 2-5 read as a sequential achievement bullet stack rather than integrated narrative.",
        ],
        score=0.68,
    )
    judge["remediation_suggestions"] = [
        "Reframe the opening thesis to position the candidate as an enterprise-wide IT strategy leader.",
        "Replace the bullet-stack pattern (S2-S5) with connective narrative tying platform and governance.",
    ]
    judge["dimension_verdicts"] = {
        "executive_signal": {
            "pass": False,
            "severity": "major",
            "codes": ["bullet_stack", "narrow_opener"],
        },
        "synthesis_quality": {
            "pass": False,
            "severity": "major",
            "codes": ["sequential_achievement_stack", "thin_recap_s6"],
        },
        "ats_alignment_without_keyword_stuffing": {
            "pass": True,
            "severity": "minor",
            "codes": ["weak_domain_targeting"],
        },
    }
    return judge


def test_compact_regen_delta_fits_core_token_budget() -> None:
    lines = collect_judge_remediation_delta_lines(
        [_claude_soft_fail_with_dimension_verdicts()],
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert estimate_token_count(joined) <= DEFAULT_MAX_DELTA_TOKENS
    assert "executive_signal:" in joined
    assert "synthesis_quality:" in joined
    assert "ats_alignment_without_keyword_stuffing:" not in joined
    assert "enterprise-wide IT strategy leader" in joined
    assert "bullet-stack pattern" in joined


def test_all_soft_failed_judges_emit_untruncated_feedback() -> None:
    long_finding_a = (
        "Sentences 2-5 read as a sequential achievement bullet stack rather than integrated "
        "SVP-level strategic narrative with no connective tissue."
    )
    long_finding_b = (
        "Closing synthesis remains generic and does not project enterprise architecture "
        "or innovation incubation themes from allowed facts."
    )
    remed_a = (
        "Reframe the opening thesis to position the candidate as an enterprise-wide IT "
        "strategy and innovation leader, not solely an agentic AI platform builder."
    )
    remed_b = (
        "Strengthen S6 forward synthesis with specific strategic framing relevant to "
        "enterprise architecture and innovation incubation rather than generic outcomes."
    )
    judges = [
        {
            **_soft_fail_judge("anthropic_claude", findings=[long_finding_a], score=0.68),
            "remediation_suggestions": [remed_a],
            "dimension_verdicts": {
                "executive_signal": {"pass": False, "severity": "major", "codes": ["bullet_stack"]},
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["thin_S6"]},
            },
        },
        {
            **_soft_fail_judge("openai_chatgpt", findings=[long_finding_b], score=0.72),
            "remediation_suggestions": [remed_b],
            "dimension_verdicts": {
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["thin_recap"]},
            },
        },
    ]
    lines = collect_judge_remediation_delta_lines(
        judges,
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert long_finding_a in joined
    assert long_finding_b in joined
    assert remed_a in joined
    assert remed_b in joined
    assert "JUDGE_DELTA_SOURCE provider_key=anthropic_claude" in joined
    assert "JUDGE_DELTA_SOURCE provider_key=openai_chatgpt" in joined
    assert "anthropic_claude remediation:" in joined
    assert "openai_chatgpt remediation:" in joined


def test_retry_qwen_falls_back_when_core_runner_refuses(tmp_path: Path, monkeypatch) -> None:
    import json

    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_PRESCRIPTIVE_DELTA", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_LEGACY_BLOCK", "0")

    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps({"compilation_hash": "c1", "replay_key": "rk", "policy_hash": "p", "blueprint_hash": "b"}),
        encoding="utf-8",
    )
    parsed = {
        "resume_display_text": "Anchor text for judge regen fallback testing here.",
        "claim_ledger": [{"claim_text": "Led platform.", "source_fact_ids": ["f1"]}],
    }
    raw = json.dumps(parsed)

    def _refuse_core(**kwargs):
        return (
            "",
            {
                "accepted": False,
                "refusal": {"refusal_code": "delta_token_budget_exceeded"},
            },
            {},
            (),
        )

    class _Result:
        runtime_generation_status = "REAL_LLM"
        raw_model_output = json.dumps(
            {
                **parsed,
                "resume_display_text": "Revised anchor text for judge regen fallback testing here.",
            },
        )

        def to_dict(self) -> dict:
            return {"raw_model_output": self.raw_model_output}

    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_same_authority_regen_bridge.run_core_same_authority_regen",
        _refuse_core,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch.call_qwen_vllm",
        lambda *a, **k: _Result(),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_lane.normalize_executive_summary_llm_output",
        lambda parsed, _plan: parsed,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_lane.prune_exec_summary_claim_ledger_orphans",
        lambda parsed, _allowed: None,
    )

    new_raw, new_parsed, receipt = retry_qwen_for_judge_remediation(
        [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}],
        {"model": "qwen-test"},
        raw,
        parsed,
        x1d_judges=[_claude_soft_fail_with_dimension_verdicts()],
        trigger_receipt={"trigger_mode": "solitary_dimension_major_soft_fail"},
        selected_fact_plan={"facts": [{"fact_id": "f1"}]},
        allowed_fact_ids={"f1"},
        unused_fact_ids=[],
        artifact_dir=tmp_path,
        max_attempts=1,
    )
    assert receipt.get("core_runner_fallback") == "apps_rg.thread_append"
    assert receipt.get("accepted") is True
    assert receipt.get("output_changed") is True
    assert "Revised" in str(new_parsed.get("resume_display_text") or "")
