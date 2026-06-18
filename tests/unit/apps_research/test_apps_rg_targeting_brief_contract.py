"""Validator tests for the AppsRgTargetingBrief route-specific contract."""

from __future__ import annotations

from apps_research.types.apps_rg_targeting_brief_contract import (
    BRIEFING_PROFILES,
    MAX_BULLETS,
    BriefStatus,
    blocked_targeting_brief,
    seal_targeting_brief,
    validate_targeting_brief_text,
)

_VALID_BRIEF = (
    "Acme Co (ACME) - SVP IT Strategy targeting brief\n"
    "| SVP IT Strategy | comp band | Reports to CIO (2026) |\n\n"
    "=== STRATEGIC MANDATE ===\n"
    "- Mid-cap insurer scaling distribution after carrier roll-ups\n"
    "- Role anchors platform consolidation across acquired books\n"
    "- 2025 cloud-core migration shifts spend to data services\n"
    "- Central tension: federated speed versus enterprise control\n\n"
    "=== LEADERSHIP ===\n"
    "- CEO drives acquisitive growth with disciplined integration\n"
    "- CIO mandate: unify policy systems onto one platform\n"
    "- CDO mandate: build governed shared data backbone\n\n"
    "=== TECH & AI PLATFORM ===\n"
    "- Mainframe-to-cloud core underway across business units\n"
    "- Integration debt from acquisitions slows new product launch\n"
    "- Peers investing in agentic underwriting assistance\n\n"
    "=== BUSINESS CONTEXT (JD alignment hooks) ===\n"
    "- Commercial lines: margin focus after rate hardening\n"
    "- Personal lines: retention pressure from direct carriers\n"
    "- Data priority: unify claims and policy for analytics\n"
    "- Culture: pragmatic, integration-heavy operating model\n\n"
    "=== EXEC SUMMARY FRAMING (not proof) ===\n"
    "- Deliver one platform that absorbs acquired books faster\n"
    "- Mirror CIO push for governed consolidation, not features\n"
    "- 12-month win: single rated quote path live in two units\n"
)


def test_valid_brief_passes() -> None:
    v = validate_targeting_brief_text(_VALID_BRIEF)
    assert v.valid, v.violations
    assert v.bullet_count <= MAX_BULLETS
    assert v.char_count <= BRIEFING_PROFILES["apps_rg"].max_total_chars
    assert v.section_count >= BRIEFING_PROFILES["apps_rg"].min_section_count


def test_seal_valid_brief() -> None:
    sealed = seal_targeting_brief(_VALID_BRIEF, company_name="Acme Co")
    assert sealed.is_sealed
    assert sealed.status is BriefStatus.SEALED
    assert sealed.company_brief_text


def test_apps_rg_profile_accepts_richer_frontier_brief() -> None:
    sections = []
    for i in range(7):
        sections.append(
            f"## Strategy Signal {i}\n"
            "- Verified company context complements the JD without repeating it.\n"
            "- Operating pressure shapes role positioning for the downstream lane.\n"
            "- Additional leadership, platform, and urgency signal remains targeting only.\n"
        )
    rich = _VALID_BRIEF + "\n\n" + "\n\n".join(sections)
    v = validate_targeting_brief_text(rich)
    assert v.valid, v.violations
    assert v.char_count > 2400
    assert v.char_count <= BRIEFING_PROFILES["apps_rg"].max_total_chars


def test_apps_lic_profile_keeps_compact_packet_budget() -> None:
    big = _VALID_BRIEF + ("\n## Outreach Signal\n" + "x" * 2500)
    v = validate_targeting_brief_text(big, profile="apps_lic")
    assert not v.valid
    assert any("char_count_over_max" in x for x in v.violations)


def test_rejects_too_many_bullets() -> None:
    extra = "\n".join(f"- net new verified fact number {i}" for i in range(55))
    text = "Co (C) - role brief\n| role | band | Reports to X (2026) |\n\n=== STRATEGIC MANDATE ===\n" + extra
    v = validate_targeting_brief_text(text)
    assert not v.valid
    assert any("too_many_bullets" in x for x in v.violations)


def test_rejects_long_bullet() -> None:
    long_bullet = "- " + ("a" * 250)
    text = "Co (C) - role brief\n| role | band | Reports to X (2026) |\n\n=== STRATEGIC MANDATE ===\n" + long_bullet
    v = validate_targeting_brief_text(text)
    assert not v.valid
    assert any("line_too_long" in x for x in v.violations)


def test_rejects_json() -> None:
    v = validate_targeting_brief_text('{"company": "Acme", "brief": "x"}')
    assert not v.valid
    assert "json_literal_present" in v.violations


def test_rejects_code_fence() -> None:
    text = "=== STRATEGIC MANDATE ===\n- fact one verified\n```json\n{}\n```\n"
    v = validate_targeting_brief_text(text)
    assert not v.valid
    assert "code_fence_present" in v.violations


def test_rejects_links_and_citations() -> None:
    link = validate_targeting_brief_text(
        "=== STRATEGIC MANDATE ===\n- see https://example.com for detail\n"
    )
    assert not link.valid
    assert "link_present" in link.violations
    cite = validate_targeting_brief_text(
        "=== STRATEGIC MANDATE ===\n- revenue grew (source: 10-K filing)\n"
    )
    assert not cite.valid
    assert "citation_present" in cite.violations


def test_rejects_bracket_placeholder() -> None:
    v = validate_targeting_brief_text(
        "=== STRATEGIC MANDATE ===\n- [ROLE_TITLE] anchors the platform play\n"
    )
    assert not v.valid
    assert "bracket_placeholder_present" in v.violations


def test_rejects_html_entity() -> None:
    v = validate_targeting_brief_text(
        "=== STRATEGIC MANDATE ===\n- ratio improved by 5&#58; over peers\n"
    )
    assert not v.valid
    assert "html_entity_present" in v.violations


def test_allows_custom_additive_headers() -> None:
    v = validate_targeting_brief_text(
        "## Strategy Signal\n- one verified company fact here\n\n"
        "## Leadership Signal\n- one verified leader fact here\n\n"
        "## Platform Signal\n- one verified platform fact here\n\n"
        "## Outreach Signal\n- one verified outreach angle here\n"
    )
    assert v.valid, v.violations


def test_allows_operating_model_and_forward_view_additive_headers() -> None:
    v = validate_targeting_brief_text(
        "## Operating Model\n- one verified company fact here\n\n"
        "## Forward View\n- one verified forward-looking company fact here\n\n"
        "## Decision Rights\n- one verified operating pressure fact here\n\n"
        "## Leadership Signal\n- one verified leader fact here\n"
    )
    assert v.valid, v.violations


def test_rejects_sub_bullet_and_table() -> None:
    sub = validate_targeting_brief_text(
        "=== STRATEGIC MANDATE ===\n- top fact verified\n  - nested fact\n"
    )
    assert not sub.valid
    assert "sub_bullet_present" in sub.violations
    tbl = validate_targeting_brief_text(
        "=== STRATEGIC MANDATE ===\n- A | B | C table row here\n"
    )
    assert not tbl.valid
    assert "table_pipe_present" in tbl.violations


def test_rejects_jd_restatement_in_bullet() -> None:
    jd = "Lead enterprise data platform strategy for the insurance division."
    text = (
        "Co (C) - role brief\n| role | band | Reports to X (2026) |\n\n"
        "=== STRATEGIC MANDATE ===\n"
        "- lead enterprise data platform strategy is the mandate\n"
    )
    v = validate_targeting_brief_text(text, jd_text=jd)
    assert not v.valid
    assert "jd_restatement_in_bullet" in v.violations


def test_empty_brief_blocks() -> None:
    sealed = seal_targeting_brief("", company_name="Acme")
    assert sealed.status is BriefStatus.BLOCKED
    assert not sealed.is_sealed


def test_invalid_brief_rejected_not_sealed() -> None:
    sealed = seal_targeting_brief('{"json": true}', company_name="Acme")
    assert sealed.status is BriefStatus.REJECTED
    assert not sealed.is_sealed
    assert sealed.violations


def test_blocked_artifact_factory() -> None:
    art = blocked_targeting_brief(company_name="Acme", block_reason="no_sources", degraded=True)
    assert art.status is BriefStatus.DEGRADED
    assert not art.is_sealed
    assert art.block_reason == "no_sources"
