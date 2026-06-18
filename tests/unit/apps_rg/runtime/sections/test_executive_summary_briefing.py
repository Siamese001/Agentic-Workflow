from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_briefing import (
    briefing_signal_bonus,
    extract_briefing_signal_packet,
)


def test_briefing_signal_bonus_depends_on_bundle_content_not_target_briefing() -> None:
    briefing = (
        "## Strategy\n"
        "- Strategy and mandate framing.\n\n"
        "## Operating Model\n"
        "- Decision rights and governance.\n\n"
        "## Leadership\n"
        "- CEO and CIO stakeholder map.\n"
    )
    packet = extract_briefing_signal_packet(briefing)
    target_blob = f"SVP\n{briefing}"

    aligned_bundle = "bundle strategy operating model governance"
    unrelated_bundle = "bundle claim text without the theme keywords"

    aligned_score = briefing_signal_bonus(
        packet,
        bundle_blob=aligned_bundle,
        target_blob=target_blob,
    )
    unrelated_score = briefing_signal_bonus(
        packet,
        bundle_blob=unrelated_bundle,
        target_blob=target_blob,
    )

    assert aligned_score > unrelated_score
    assert unrelated_score == 0.0
