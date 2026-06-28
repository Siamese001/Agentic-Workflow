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

_PARTNER_JD = (
    "Lead AI architecture partnerships with cloud, GSI, and ISV partners. "
    "Drive co-sell solution design, partner enablement, enterprise deployment, "
    "governance, and technical close for applied AI adoption."
)

_PARTNERSHIP_TARGETING_BRIEF = (
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

_DIRECT_PARTNER_RESEARCH_NOTES = (
    "### company_basics\n"
    "Anthropic context establishes company DNA and operating model.\n"
    "### strategic_priorities\n"
    "Strategic priorities emphasize trusted enterprise AI, deployment maturity, and partner routes.\n"
    "### leadership_and_org\n"
    "Leadership pressure spans partnerships, platform, safety, revenue, and customer architecture.\n"
    "### recent_news_and_signals\n"
    "Recent moves include funding, valuation, and enterprise distribution signals.\n"
    "### financials_and_growth\n"
    "Latest funding and valuation signals supersede older financing context.\n"
    "### partner_ecosystem\n"
    "Partner ecosystem signals include cloud providers, GSI partners, ISV routes, and joint solution work.\n"
    "### commercial_motion\n"
    "Commercial motion includes co-sell execution, technical close, and ecosystem revenue expansion.\n"
    "### adoption_motion\n"
    "Adoption motion depends on enablement, reference patterns, governance, and measurable rollout.\n"
    "### tech_stack_and_tools\n"
    "AI, data, platform, architecture signals include reference architecture and evaluations.\n"
    "### regulatory_and_legal\n"
    "Governance, compliance, privacy, trust, security, and risk controls shape enterprise adoption.\n"
)

_ROLE_CONTEXT_ONLY_RESEARCH_NOTES = (
    "### company_basics\n"
    "Anthropic context establishes company DNA and operating model.\n"
    "### strategic_priorities\n"
    "Strategic priorities emphasize trusted enterprise AI and deployment maturity.\n"
    "### leadership_and_org\n"
    "Leadership and stakeholder map spans platform, product, and partnerships.\n"
    "### recent_news_and_signals\n"
    "Recent moves create urgency for deployment and ecosystem execution.\n"
    "### role_context\n"
    "Partner ecosystem, co-sell, commercial motion, and adoption motion are role-critical.\n"
    "### tech_stack_and_tools\n"
    "AI, data, platform, architecture signals include reference architecture and evaluations.\n"
    "### regulatory_and_legal\n"
    "Governance, compliance, privacy, trust, security, and risk controls shape enterprise adoption.\n"
)

_DIRECT_FAMILIES_BUT_NO_SOURCED_PARTNER_TERMS = (
    "### company_basics\n"
    "Anthropic context establishes company DNA and operating model.\n"
    "### strategic_priorities\n"
    "Strategic priorities emphasize trusted enterprise AI and deployment maturity.\n"
    "### leadership_and_org\n"
    "Leadership and stakeholder map spans platform and product teams.\n"
    "### recent_news_and_signals\n"
    "Recent moves create urgency for deployment.\n"
    "### partner_ecosystem\n"
    "The company works with external organizations.\n"
    "### commercial_motion\n"
    "The company sells to enterprises.\n"
    "### adoption_motion\n"
    "Customers deploy the product.\n"
    "### tech_stack_and_tools\n"
    "AI, data, platform, architecture signals include reference architecture and evaluations.\n"
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


def test_apps_lic_profile_keeps_compact_packet_budget() -> None:
    big = _VALID_BRIEF + ("\n## Outreach Signal\n" + "x" * 2500)
    v = validate_targeting_brief_text(big, profile="apps_lic")
    assert not v.valid
    assert any("char_count_over_max" in x for x in v.violations)


def test_rejects_dangerous_shapes() -> None:
    json_blob = validate_targeting_brief_text('{"company": "Acme", "brief": "x"}')
    assert not json_blob.valid
    assert "json_literal_present" in json_blob.violations

    fenced = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- fact one verified\n```json\n{}\n```\n")
    assert not fenced.valid
    assert "code_fence_present" in fenced.violations

    link = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- see https://example.com for detail\n")
    assert not link.valid
    assert "link_present" in link.violations

    cite = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- revenue grew (source: filing)\n")
    assert not cite.valid
    assert "citation_present" in cite.violations

    placeholder = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- [ROLE_TITLE] anchors the platform play\n")
    assert not placeholder.valid
    assert "bracket_placeholder_present" in placeholder.violations

    html = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- ratio improved by 5&#58; over peers\n")
    assert not html.valid
    assert "html_entity_present" in html.violations


def test_rejects_shape_limits_and_nested_content() -> None:
    extra = "\n".join(f"- net new verified fact number {i}" for i in range(55))
    too_many = validate_targeting_brief_text(
        "Co (C) - role brief\n| role | band | Reports to X (2026) |\n\n=== STRATEGIC MANDATE ===\n"
        + extra
    )
    assert not too_many.valid
    assert any("too_many_bullets" in x for x in too_many.violations)

    long_bullet = "- " + ("a" * 250)
    long_line = validate_targeting_brief_text(
        "Co (C) - role brief\n| role | band | Reports to X (2026) |\n\n=== STRATEGIC MANDATE ===\n"
        + long_bullet
    )
    assert not long_line.valid
    assert any("line_too_long" in x for x in long_line.violations)

    sub = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- top fact verified\n  - nested fact\n")
    assert not sub.valid
    assert "sub_bullet_present" in sub.violations

    table = validate_targeting_brief_text("=== STRATEGIC MANDATE ===\n- A | B | C table row here\n")
    assert not table.valid
    assert "table_pipe_present" in table.violations


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


def test_blocked_artifact_factory() -> None:
    art = blocked_targeting_brief(company_name="Acme", block_reason="no_sources", degraded=True)
    assert art.status is BriefStatus.DEGRADED
    assert not art.is_sealed
    assert art.block_reason == "no_sources"


def test_empty_and_invalid_briefs_do_not_seal() -> None:
    empty = seal_targeting_brief("", company_name="Acme")
    assert empty.status is BriefStatus.BLOCKED
    assert not empty.is_sealed

    invalid = seal_targeting_brief('{"json": true}', company_name="Acme")
    assert invalid.status is BriefStatus.REJECTED
    assert not invalid.is_sealed
    assert invalid.violations


def test_direct_partner_research_families_are_handoff_eligible() -> None:
    quality = assess_targeting_brief_semantics(
        _PARTNERSHIP_TARGETING_BRIEF,
        jd_text=_PARTNER_JD,
        research_notes=_DIRECT_PARTNER_RESEARCH_NOTES,
        profile="apps_rg",
    )

    assert quality.handoff_eligible, quality.as_dict()
    assert quality.missing_sections == ()
    assert "partnerships" in quality.evidence_intents
    assert "partner_ecosystem" in quality.source_families_present
    assert "commercial_motion" in quality.source_families_present
    assert "adoption_motion" in quality.source_families_present
    assert "regulatory_and_legal" in quality.source_families_present
    assert "tech_stack_signals" in quality.source_families_present
    assert "co-sell" in quality.signal_terms_present


def test_source_family_keys_survive_bounded_research_notes() -> None:
    bounded_notes = (
        "### company_basics\n"
        "Company DNA and operating model show leadership strategy urgency. "
        "Co-sell architecture product sales AI adoption and governance signals are sourced."
    )

    quality = assess_targeting_brief_semantics(
        _PARTNERSHIP_TARGETING_BRIEF,
        jd_text=_PARTNER_JD,
        research_notes=bounded_notes,
        source_family_keys=(
            "company_basics",
            "competitive_landscape",
            "leadership_and_org",
            "recent_news_and_signals",
            "financials_and_growth",
            "partner_ecosystem",
            "commercial_motion",
            "adoption_motion",
            "tech_stack_and_tools",
            "regulatory_and_legal",
        ),
        profile="apps_rg",
    )

    assert quality.handoff_eligible, quality.as_dict()
    assert quality.source_families_missing == ()


def test_role_context_no_longer_satisfies_partner_source_families() -> None:
    quality = assess_targeting_brief_semantics(
        _PARTNERSHIP_TARGETING_BRIEF,
        jd_text=_PARTNER_JD,
        research_notes=_ROLE_CONTEXT_ONLY_RESEARCH_NOTES,
        profile="apps_rg",
    )

    assert not quality.handoff_eligible
    assert "role_context" not in quality.source_families_present
    assert "partner_ecosystem" in quality.source_families_missing
    assert "commercial_motion" in quality.source_families_missing
    assert "adoption_motion" in quality.source_families_missing
    assert "missing_intent_evidence" in quality.reason


def test_jd_text_does_not_satisfy_partner_signal_terms() -> None:
    no_partner_signal_brief = _PARTNERSHIP_TARGETING_BRIEF.replace("Co-sell", "Distribution")
    no_partner_signal_brief = no_partner_signal_brief.replace("co-sell", "distribution")
    no_partner_signal_brief = no_partner_signal_brief.replace("GSI", "services")
    no_partner_signal_brief = no_partner_signal_brief.replace("ISV", "software")
    no_partner_signal_brief = no_partner_signal_brief.replace("enablement", "support")
    no_partner_signal_brief = no_partner_signal_brief.replace("technical close", "buyer confidence")

    quality = assess_targeting_brief_semantics(
        no_partner_signal_brief,
        jd_text=_PARTNER_JD,
        research_notes=_DIRECT_FAMILIES_BUT_NO_SOURCED_PARTNER_TERMS,
        profile="apps_rg",
    )

    assert not quality.handoff_eligible
    assert "co-sell" not in quality.signal_terms_present
    assert "missing_sourced_intent_signal" in quality.reason


def test_generic_intent_gate_blocks_missing_security_evidence() -> None:
    jd = "Security Architect responsible for privacy, compliance, risk, platform architecture, and governance."
    research_notes = (
        "### company_basics\n"
        "Acme context establishes company DNA and operating model.\n"
        "### strategic_priorities\n"
        "Strategy emphasizes enterprise growth and customer trust.\n"
        "### leadership_and_org\n"
        "Leadership stakeholders span product and engineering.\n"
        "### recent_news_and_signals\n"
        "Recent events create urgency for deployment.\n"
        "### role_context\n"
        "Security and compliance are role-critical but unsourced here.\n"
    )
    quality = assess_targeting_brief_semantics(
        _PARTNERSHIP_TARGETING_BRIEF,
        jd_text=jd,
        research_notes=research_notes,
        profile="apps_rg",
    )

    assert not quality.handoff_eligible
    assert "security_trust" in quality.evidence_intents
    assert "regulatory_and_legal" in quality.source_families_missing
    assert "missing_intent_evidence" in quality.reason


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
        research_notes=_DIRECT_PARTNER_RESEARCH_NOTES,
        profile="apps_rg",
    )
    assert not quality.handoff_eligible
    assert quality.missing_sections
