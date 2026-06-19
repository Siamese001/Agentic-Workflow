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


def test_briefing_signal_packet_captures_partner_and_adoption_motion() -> None:
    briefing = (
        "## Company DNA & Operating Model\n"
        "- Partner-led motion scales through GSI co-sell and ISV ecosystems.\n\n"
        "## Partnership / Ecosystem Motion\n"
        "- Joint solution development and technical close are the bottlenecks.\n\n"
        "## Recent Events & Urgency\n"
        "- Pilot-to-production adoption remains the operating pressure.\n"
    )
    packet = extract_briefing_signal_packet(briefing)
    assert packet["theme_counts"]["commercial_motion"] >= 1
    assert packet["theme_counts"]["partner_ecosystem"] >= 1
    assert packet["theme_counts"]["adoption_motion"] >= 1
    assert packet["dominant_themes"][0] in {"commercial_motion", "partner_ecosystem", "adoption_motion"}
