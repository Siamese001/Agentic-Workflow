"""Validator tests for the AppsRgTargetingBrief route-specific contract."""

from __future__ import annotations

from apps_research.types.apps_rg_targeting_brief_contract import (
    BRIEFING_PROFILES,
    MAX_BULLETS,
    BriefStatus,
    assess_targeting_brief_semantics,
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


_PARTNER_JD = (
    "Lead AI architecture partnerships with cloud, GSI, and ISV partners. "
    "Drive co-sell solution design, partner enablement, enterprise deployment, "
    "governance, and technical close for applied AI adoption."
)

_SEARXNG_RESEARCH_NOTES = (
    "### overview\n"
    "Anthropic is scaling enterprise Claude adoption through product, safety, and platform motion.\n"
    "### strategic_priorities\n"
    "Strategic priorities emphasize trusted enterprise AI, deployment maturity, and partner routes.\n"
    "### leadership\n"
    "Leadership pressure spans partnerships, platform, safety, revenue, and customer architecture.\n"
    "### recent_moves\n"
    "Recent moves point to urgent enterprise distribution and deployment-readiness work.\n"
    "### partner_ecosystem\n"
    "Partner ecosystem signals include cloud providers, GSI partners, ISV routes, and joint solution work.\n"
    "### commercial_motion\n"
    "Commercial motion includes co-sell execution, technical close, and ecosystem revenue expansion.\n"
    "### adoption_motion\n"
    "Adoption motion depends on enablement, reference patterns, governance, and measurable rollout.\n"
    "### tech_stack_signals\n"
    "Tech stack signals include AI platform architecture, data controls, integration, and evaluation loops.\n"
)

_TAVILY_STYLE_TARGETING_BRIEF = (
    "Anthropic - Manager of Applied AI Architecture, Partnerships targeting brief\n\n"
    "## JD Complement\n"
    "- Company DNA points to safe frontier AI deployment through partner-led enterprise adoption.\n"
    "- The role complements platform architecture, partner enablement, and technical close pressure.\n\n"
    "## Company DNA & Operating Model\n"
    "- Company DNA blends frontier model research with enterprise product and safety operating discipline.\n"
    "- Operating model signals tight coordination across partnerships, product, platform, and field teams.\n\n"
    "## Company Strategy & Operating Pressure\n"
    "- Strategy pressure centers on scaling trusted Claude deployments through commercial ecosystems.\n"
    "- Enterprise urgency favors repeatable governance, implementation patterns, and adoption measurement.\n\n"
    "## Leadership & Stakeholder Map\n"
    "- Leadership stakeholders need partner architects who translate roadmap into credible customer motions.\n"
    "- Stakeholder map spans partnerships, platform, revenue, safety, and customer architecture leaders.\n\n"
    "## AI, Data, Platform, Architecture Signals\n"
    "- AI platform signal favors integration patterns, data controls, evaluation loops, and secure rollout.\n"
    "- Architecture signal points to reusable reference designs for enterprise deployment readiness.\n\n"
    "## Partnership / Ecosystem Motion\n"
    "- Co-sell motion depends on cloud, GSI, and ISV alignment around joint solution design.\n"
    "- Partner ecosystem revenue needs enablement, technical close discipline, and partner-led proof paths.\n\n"
    "## Recent Events & Urgency\n"
    "- Recent events increase urgency for enterprise-grade operating models and deployment playbooks.\n"
    "- Urgency supports positioning around safe adoption, partner activation, and scalable architecture.\n\n"
    "## apps_rg Positioning Themes\n"
    "- Positioning should connect platform architecture, partner-led delivery, and executive trust.\n"
    "- Themes remain targeting context only and cannot become proof for candidate achievement claims.\n\n"
    "## apps_lic Outreach Angles\n"
    "- Outreach can emphasize ecosystem revenue, partner enablement, and AI adoption motion.\n"
    "- Outreach should mirror strategy pressure without copying job description responsibilities.\n\n"
    "## Do Not Use As Proof\n"
    "- This briefing is targeting context only and must not support candidate achievement claims.\n"
)

_SEARXNG_STYLE_TARGETING_BRIEF = (
    "Anthropic (private) - Manager of Applied AI Architecture, Partnerships briefing packet\n\n"
    "## JD Complement\n"
    "- Company DNA frames the role as a bridge between applied AI architecture and partner adoption.\n"
    "- The packet should bias toward ecosystem motion, enterprise deployment, and governance readiness.\n\n"
    "## Company DNA & Operating Model\n"
    "- Company DNA combines frontier AI product execution with safety, reliability, and enterprise trust.\n"
    "- Operating model pressure rewards leaders who can make partner delivery repeatable and measurable.\n\n"
    "## Company Strategy & Operating Pressure\n"
    "- Strategy pressure is to turn Claude demand into durable enterprise deployments through partners.\n"
    "- Commercial scale depends on lowering deployment friction while preserving safety and data controls.\n\n"
    "## Leadership & Stakeholder Map\n"
    "- Leadership stakeholders likely span partnerships, product, revenue, platform, and solutions teams.\n"
    "- Stakeholder map calls for translation across executive priorities and field architecture realities.\n\n"
    "## AI, Data, Platform, Architecture Signals\n"
    "- AI platform signal includes reference architecture, integration patterns, evaluations, and governance.\n"
    "- Data and architecture signals should foreground secure deployment paths and customer-ready controls.\n\n"
    "## Partnership / Ecosystem Motion\n"
    "- Co-sell execution with cloud, GSI, and ISV partners is the critical route-to-market signal.\n"
    "- Partner-led solution design and enablement create the technical close path for ecosystem revenue.\n\n"
    "## Recent Events & Urgency\n"
    "- Recent events point to intensified enterprise AI adoption and partner distribution urgency.\n"
    "- Urgency favors candidates who can make deployment playbooks concrete across partner channels.\n\n"
    "## apps_rg Positioning Themes\n"
    "- Positioning themes should tie AI architecture, partner scale, adoption governance, and trust.\n"
    "- Use this only to choose emphasis; it is not evidence for resume proof bullets.\n\n"
    "## apps_lic Outreach Angles\n"
    "- Outreach can lead with partner ecosystem revenue, architecture enablement, and co-sell maturity.\n"
    "- The angle should sound like business context, not a restatement of the job description.\n\n"
    "## Do Not Use As Proof\n"
    "- This briefing is targeting context only and must not support candidate achievement claims.\n"
)


def test_searxng_targeting_brief_quality_matches_tavily_style_packet() -> None:
    tavily_quality = assess_targeting_brief_semantics(
        _TAVILY_STYLE_TARGETING_BRIEF,
        jd_text=_PARTNER_JD,
        research_notes=_SEARXNG_RESEARCH_NOTES,
        profile="apps_rg",
    )
    searxng_quality = assess_targeting_brief_semantics(
        _SEARXNG_STYLE_TARGETING_BRIEF,
        jd_text=_PARTNER_JD,
        research_notes=_SEARXNG_RESEARCH_NOTES,
        profile="apps_rg",
    )

    assert tavily_quality.handoff_eligible, tavily_quality.as_dict()
    assert searxng_quality.handoff_eligible, searxng_quality.as_dict()
    assert searxng_quality.missing_sections == ()
    assert "partner_ecosystem" in searxng_quality.source_families_present
    assert "co-sell" in searxng_quality.signal_terms_present
    assert searxng_quality.score >= tavily_quality.score - 0.05


def test_generic_company_brief_is_not_quality_equivalent_to_targeting_packet() -> None:
    generic = (
        "# Anthropic Company Brief\n\n"
        "## Overview\n"
        "- Anthropic builds AI products for enterprises.\n\n"
        "## Recent News\n"
        "- The company announced several business updates.\n"
    )
    quality = assess_targeting_brief_semantics(
        generic,
        jd_text=_PARTNER_JD,
        research_notes=_SEARXNG_RESEARCH_NOTES,
        profile="apps_rg",
    )
    assert not quality.handoff_eligible
    assert quality.missing_sections


def test_searxng_source_family_aliases_satisfy_apps_rg_quality_gate() -> None:
    searxng_family_notes = (
        "### company_basics\n"
        "Anthropic context establishes company DNA and operating model.\n"
        "### competitive_landscape\n"
        "Strategic priorities and commercial motion center on partner-led enterprise scale.\n"
        "### leadership_and_org\n"
        "Leadership and stakeholder map spans platform, product, and partnerships.\n"
        "### recent_news_and_signals\n"
        "Recent moves create urgency for deployment and ecosystem execution.\n"
        "### role_context\n"
        "Partner ecosystem, co-sell, commercial motion, and adoption motion are role-critical.\n"
        "### tech_stack_and_tools\n"
        "AI, data, platform, architecture signals include reference architecture and evaluations.\n"
    )

    quality = assess_targeting_brief_semantics(
        _SEARXNG_STYLE_TARGETING_BRIEF,
        jd_text=_PARTNER_JD,
        research_notes=searxng_family_notes,
        profile="apps_rg",
    )

    assert quality.handoff_eligible, quality.as_dict()
    assert "overview" in quality.source_families_present
    assert "partner_ecosystem" in quality.source_families_present
    assert "tech_stack_signals" in quality.source_families_present
