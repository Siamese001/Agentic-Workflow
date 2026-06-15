from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_regen_support import (
    DEFAULT_STEP_ORDER,
    PROMPT_LOCK_GENERIC,
    JudgeDirectedRegenPlan,
    JudgeDirectedRegenStep,
    PromptMessages,
    compute_system_prefix_hash,
    format_regen_delta_user_turn,
    sha256_hex,
)


def test_format_regen_delta_user_turn_filters_blank_lines_and_preserves_lock() -> None:
    rendered = format_regen_delta_user_turn(
        (
            " tighten S2 to evidence-backed mechanism ",
            "",
            "keep S4 metric unchanged",
        )
    )

    assert rendered.startswith("REGEN_DELTA_v1\n")
    assert PROMPT_LOCK_GENERIC in rendered
    assert "tighten S2 to evidence-backed mechanism" in rendered
    assert "keep S4 metric unchanged" in rendered
    assert "  tighten" not in rendered


def test_judge_directed_regen_plan_serializes_stable_step_order() -> None:
    plan = JudgeDirectedRegenPlan()

    assert plan.steps == DEFAULT_STEP_ORDER
    assert plan.as_dict() == {
        "schema": "judge_directed_regen_plan_v1",
        "steps": [step.value for step in DEFAULT_STEP_ORDER],
        "require_x2_pass_before_rescore": True,
        "allow_x2_repair": True,
    }
    assert DEFAULT_STEP_ORDER[0] is JudgeDirectedRegenStep.EVALUATE_TRIGGER
    assert DEFAULT_STEP_ORDER[-1] is JudgeDirectedRegenStep.EMIT_RECEIPTS


def test_prompt_messages_flattens_structured_slots_before_user_turn() -> None:
    messages = PromptMessages(
        slot_map={
            "S0": "system",
            "I0": "instructions",
            "D0": "data",
            "USER": "fallback user",
            "U0": "bounded delta",
        },
        ordered_slots=("D0", "S0", "I0", "U0"),
        exemplars=(("bad", "good"),),
        metadata={"run_id": "r1"},
    )

    assert messages.system_text(separator="|") == "data|system|instructions"
    assert messages.user_text() == "bounded delta"
    assert messages.to_flat() == ("data\n\nsystem\n\ninstructions", "bounded delta")
    assert messages.as_dict()["exemplars"] == [["bad", "good"]]


def test_system_prefix_hash_ignores_trailing_whitespace_only() -> None:
    assert compute_system_prefix_hash("system\n") == sha256_hex("system")
    assert compute_system_prefix_hash(" system") != sha256_hex("system")
