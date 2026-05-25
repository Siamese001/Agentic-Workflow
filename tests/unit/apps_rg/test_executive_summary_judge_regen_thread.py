"""W1.4 judge regen thread compaction contract."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_judge_regen_thread import (
    assert_judge_regen_thread_invariants,
    compact_judge_regen_messages,
)


def test_compact_drops_stacked_assistant_json_keeps_rubric_and_candidate() -> None:
    rubric = "JUDGE_RUBRIC frozen system content"
    candidate = "ORIGINAL_CANDIDATE resume_display_text under review"
    old_json = '{"resume_display_text":"old","claim_ledger":[]}'
    messages = [
        {"role": "system", "content": rubric},
        {"role": "user", "content": candidate},
        {"role": "assistant", "content": old_json},
        {"role": "user", "content": "critique dimension executive_signal"},
        {"role": "assistant", "content": old_json},
        {"role": "user", "content": "REGEN_DELTA fix synthesis"},
        {"role": "assistant", "content": '{"resume_display_text":"new","claim_ledger":[]}'},
    ]
    compacted, receipt = compact_judge_regen_messages(messages)
    assert receipt.get("compacted") is True
    assert receipt.get("removed_assistant_json_turns", 0) >= 1
    violations = assert_judge_regen_thread_invariants(
        messages,
        compacted,
        required_substrings=(rubric[:24], candidate[:24], "REGEN_DELTA"),
    )
    assert not violations
