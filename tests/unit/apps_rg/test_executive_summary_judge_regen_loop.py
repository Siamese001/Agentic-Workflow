"""Tests for judge regen loop closure (plan d8f3a1)."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_judge_regen_loop import (
    extend_regen_thread_after_success,
    post_regen_x2_repair_eligible,
    preserve_judge_regen_claim_ledger_from_baseline,
    prepare_parsed_after_judge_regen,
    write_judge_regen_x2_snapshot,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    judge_regen_core_runner_enabled,
    judge_regeneration_enabled,
)
from apps_rg.runtime.sections.executive_summary_voice_repair import (
    strip_unsupported_source_sensitive_prose,
)


def test_judge_regen_defaults_on_without_env(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN", raising=False)
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    assert judge_regeneration_enabled() is True
    assert judge_regen_core_runner_enabled() is True


def test_post_regen_x2_repair_eligible_shape_gates_only() -> None:
    failed = [
        {"gate_id": "x2_exec_summary_meta_filler_zero", "pass": False},
        {"gate_id": "x2_source_sensitive_phrases_supported", "pass": False},
    ]
    assert post_regen_x2_repair_eligible(failed) is True
    assert post_regen_x2_repair_eligible(
        [{"gate_id": "x2_claim_ledger_orphan_zero", "pass": False}],
    ) is False


def test_strip_unsupported_source_sensitive_rewrites_environments() -> None:
    parsed = {
        "resume_display_text": (
            "Technology strategy executive operating in regulated environments "
            "with governance framework discipline."
        ),
        "claim_ledger": [],
    }
    facts = [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Governed agentic AI for regulated enterprise workflows.",
        },
    ]
    out, receipt = strip_unsupported_source_sensitive_prose(parsed, selected_facts=facts)
    text = out["resume_display_text"].lower()
    assert "regulated environments" not in text
    assert receipt.get("repaired") is True


def test_prepare_strips_meta_filler_opener() -> None:
    parsed = {
        "resume_display_text": (
            "Additionally, technology strategy executive aligning platform scale "
            "and innovation delivery across enterprise programs with measurable outcomes."
        ),
        "claim_ledger": [
            {
                "claim_text": "Technology strategy executive aligning platform scale.",
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
        "gap_notes": [],
    }
    facts = [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Governed agentic AI platform for regulated enterprise workflows.",
        },
    ]
    out, _receipt = prepare_parsed_after_judge_regen(
        parsed,
        allowed_fact_ids={"fact_engineering_platform_001"},
        plan_facts=facts,
    )
    assert "additionally" not in out["resume_display_text"].lower()


def test_preserve_ledger_restores_dropped_fact_ids() -> None:
    baseline = {
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_a"]},
            {"claim_text": "b", "source_fact_ids": ["fact_b"]},
        ],
    }
    regen = {
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_a"]},
        ],
    }
    out, receipt = preserve_judge_regen_claim_ledger_from_baseline(
        regen,
        baseline_parsed=baseline,
        allowed_fact_ids={"fact_a", "fact_b"},
    )
    assert receipt.get("repaired") is True
    assert "fact_b" in receipt.get("restored_fact_ids", [])
    assert len(out["claim_ledger"]) == 2


def test_write_judge_regen_x2_snapshot_writes_named_file(tmp_path) -> None:
    gates = [{"gate_id": "x2_exec_summary_sentence_count_6", "pass": True}]
    write_judge_regen_x2_snapshot(
        tmp_path,
        "x2_gate_outputs_pre_regen.json",
        gates,
        label="pre_regen",
    )
    path = tmp_path / "x2_gate_outputs_pre_regen.json"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "pre_regen" in body
    assert "x2_exec_summary_sentence_count_6" in body


def test_extend_regen_thread_assistant_only() -> None:
    msgs = [{"role": "system", "content": "sys"}, {"role": "user", "content": "u0"}]
    extended = extend_regen_thread_after_success(msgs, '{"resume_display_text":"x"}')
    assert len(extended) == len(msgs) + 1
    assert extended[-1]["role"] == "assistant"
