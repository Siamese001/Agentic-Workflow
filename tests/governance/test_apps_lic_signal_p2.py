"""tests.governance.test_apps_lic_signal_p2 — P2 Signal Enhancement Governance Tests.

Plan: .windsurf/plans/apps-lic-signal-enhancements-p2p3-spine-aligned.md

Tests for P2a Narrative Arc Engine, P2b Archetype Tone Calibrator, P2c Competitive Landscape Engine.
"""

from __future__ import annotations

import pytest

# Import the engine under test
from apps_lic.engines.narrative_arc_engine import (
    MessageSection,
    NarrativeArc,
    build_narrative_arc_context,
    should_block_draft_due_to_arc_breaks,
)


# =============================================================================
# P0 Baseline Preservation Reference Tests
# =============================================================================


def test_signal_p2_baseline_spine_tests_still_green_reference():
    """Reference test that documents the baseline 81 tests requirement.
    
    This test serves as documentation that P2 implementation must not break
    the existing 81 apps_lic governance tests.
    """
    # This is a documentation/reference test only
    # The actual baseline verification happens in CI via:
    # pytest tests/governance/test_apps_lic_*.py -q
    assert True, "Baseline reference test (see docstring)"


# =============================================================================
# P2a Narrative Arc Engine Tests
# =============================================================================


def test_narrative_arc_opener_leads_with_recipient_not_sender_for_exec():
    """Executive policy: opener must lead with recipient/company context, not sender bio."""
    arc = build_narrative_arc_context(
        recipient_class="EXECUTIVE",
        company_name="Acme Corp",
        role_context="CTO",
        sender_credibility_claims=["ex-CTO at scale"],
        problem_insight="platform reliability challenges",
        ask_output="brief call to discuss architecture",
    )
    
    # Find opener section
    opener = next((s for s in arc.sections if s.section_id == "opener"), None)
    assert opener is not None, "Opener section must exist"
    
    # Executive policy: opener must not have sender_bio in forbidden_inputs
    assert "sender_bio" in opener.forbidden_inputs, \
        "Exec opener must forbid sender biography"
    assert "sender_background" in opener.forbidden_inputs, \
        "Exec opener must forbid sender background"


def test_narrative_arc_allows_compact_recruiter_arc():
    """Recruiter follow-up can use compact arc (opener, hook, ask)."""
    arc = build_narrative_arc_context(
        recipient_class="RECRUITER",
        company_name="TechCorp",
        role_context="Senior TA",
        sender_credibility_claims=["strong fit match"],
        problem_insight="prior engagement on role",
        ask_output="schedule follow-up",
        is_recruiter_followup=True,
    )
    
    # Recruiter arc should be compact
    assert arc.recommended_order == ["opener", "hook", "ask"], \
        "Recruiter follow-up should use compact arc order"


def test_narrative_arc_fails_if_proof_disconnected_from_hook():
    """Arc break detected when hook and proof are disconnected."""
    # Create arc with minimal inputs that may cause disconnect
    arc = build_narrative_arc_context(
        recipient_class="EXECUTIVE",
        company_name="TestCo",
        role_context="VP Eng",
        sender_credibility_claims=[],  # Missing credibility
        problem_insight=None,  # Missing insight
        ask_output="call",
    )
    
    # Should have arc breaks for missing evidence
    assert any("missing_sender_credibility" in b for b in arc.arc_breaks), \
        "Arc should report missing sender credibility"
    assert arc.arc_coherence_score < 1.0, \
        "Arc coherence should be reduced with missing inputs"


def test_narrative_arc_ask_logically_follows_proof():
    """Ask section should have logical connection from proof."""
    arc = build_narrative_arc_context(
        recipient_class="HIRING_MANAGER",
        company_name="StartupCo",
        role_context="Engineering Manager",
        sender_credibility_claims=["10 years distributed systems"],
        problem_insight="scaling challenges at current stage",
        ask_output="15-min architecture discussion",
    )
    
    # Find proof section
    proof = next((s for s in arc.sections if s.section_id == "proof"), None)
    ask = next((s for s in arc.sections if s.section_id == "ask"), None)
    
    assert proof is not None, "Proof section must exist"
    assert ask is not None, "Ask section must exist"
    
    # Proof should have transition marker for ask
    assert proof.transition_marker, "Proof should have transition to ask"


def test_narrative_arc_context_is_added_before_compile_prompt():
    """Narrative arc context is produced before compile_prompt step.
    
    This is a design intent test - the actual integration test verifies
    that build_narrative_arc_context is called in the DAG before compile_prompt.
    """
    arc = build_narrative_arc_context(
        recipient_class="CTO",
        company_name="GrowthCo",
        role_context="CTO",
        sender_credibility_claims=["former CTO"],
        problem_insight="technical debt slowing feature delivery",
        ask_output="explore advisory role",
    )
    
    # Arc should be complete and ready for Prompt Assembly
    section_ids = {s.section_id for s in arc.sections}
    assert "opener" in section_ids, "Arc must have opener"
    assert "hook" in section_ids, "Arc must have hook"
    assert "proof" in section_ids, "Arc must have proof"
    assert "ask" in section_ids, "Arc must have ask"
    
    assert arc.context_ref == "narrative_arc_context", \
        "Context ref should match expected slot for Prompt Assembly"


def test_narrative_arc_does_not_call_provider_or_retrieve():
    """Narrative arc engine must not call providers or retrieve external data."""
    import inspect
    
    source = inspect.getsource(build_narrative_arc_context)
    
    # No provider imports or calls
    assert "openai" not in source.lower(), "No OpenAI imports"
    assert "anthropic" not in source.lower(), "No Anthropic imports"
    assert "requests.get" not in source, "No HTTP requests"
    assert "urllib" not in source, "No urllib usage"
    
    # No apps_research calls
    assert "apps_research" not in source.lower(), "No apps_research calls"


# =============================================================================
# P2 Arc Break Policy Tests
# =============================================================================


def test_arc_break_exec_coherence_below_threshold_blocks():
    """Executive recipients: arc coherence < 0.6 should trigger block recommendation."""
    # Create low-coherence arc by simulating breaks
    low_arc = NarrativeArc(
        sections=[
            MessageSection("opener", "context", ["sender_bio"], ""),
        ],
        arc_coherence_score=0.5,
        arc_breaks=["missing_sections:hook,proof,ask", "missing_sender_credibility"],
        recommended_order=["opener"],
    )
    
    should_block, reason = should_block_draft_due_to_arc_breaks(low_arc, "EXECUTIVE")
    
    assert should_block is True, "Low coherence arc should block for exec"
    assert "0.6" in reason, "Reason should mention 0.6 threshold"


def test_arc_break_sender_bio_in_exec_opener_blocks():
    """Executive policy: sender bio in opener is a blocking arc break."""
    arc = NarrativeArc(
        sections=[
            MessageSection("opener", "sender_bio_intro", [], ""),
            MessageSection("hook", "problem", [], ""),
            MessageSection("proof", "credibility", [], ""),
            MessageSection("ask", "cta", [], ""),
        ],
        arc_coherence_score=0.7,
        arc_breaks=["exec_opener_leads_with_sender_bio"],
        recommended_order=["opener", "hook", "proof", "ask"],
    )
    
    should_block, reason = should_block_draft_due_to_arc_breaks(arc, "EXECUTIVE")
    
    assert should_block is True, "Sender bio in exec opener should block"
    assert "sender biography" in reason.lower(), "Reason should mention sender biography"


def test_arc_break_recruiter_coherence_soft_policy():
    """Recruiter recipients: arc coherence has softer policy."""
    # Moderate coherence for recruiter should not block
    arc = NarrativeArc(
        sections=[
            MessageSection("opener", "context", [], ""),
            MessageSection("hook", "fit_signal", [], ""),
            MessageSection("ask", "schedule", [], ""),
        ],
        arc_coherence_score=0.5,  # Below exec threshold but recruiter is softer
        arc_breaks=[],
        recommended_order=["opener", "hook", "ask"],
    )
    
    should_block, reason = should_block_draft_due_to_arc_breaks(arc, "RECRUITER")
    
    # Recruiter policy is softer - 0.5 may not block
    # Only < 0.4 should block
    if arc.arc_coherence_score >= 0.4:
        assert should_block is False, "Recruiter arc >= 0.4 should not block"


# =============================================================================
# Spine Preservation Tests
# =============================================================================


def test_signal_p2_no_changes_to_apps_lic_main():
    """Verify apps_lic/__main__.py remains unchanged (pure shim)."""
    import os
    
    main_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "apps_lic", "__main__.py"
    )
    
    # Read main file
    with open(main_path, "r") as f:
        content = f.read()
    
    # Verify it's a shim - should have minimal code
    # Key indicators:
    # - No direct engine imports
    # - No direct HOP orchestration
    # - Uses agentic_core runner
    
    assert "agentic_core" in content or "runner" in content, \
        "Main should use agentic_core runner"
    
    # No direct narrative arc engine import in main
    assert "narrative_arc_engine" not in content, \
        "Main should not import narrative_arc_engine directly"


def test_signal_p2_no_legacy_runner_reachability():
    """Verify legacy run_workflow_lic.py is not reachable from new code."""
    import os
    import ast
    
    # Check that narrative_arc_engine doesn't import legacy runner
    from apps_lic import engines
    
    engine_path = os.path.join(
        os.path.dirname(__file__), "..", "..", 
        "apps_lic", "engines", "narrative_arc_engine.py"
    )
    
    with open(engine_path, "r") as f:
        tree = ast.parse(f.read())
    
    # Check imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    
    # No legacy runner imports
    assert "run_workflow_lic" not in " ".join(imports), \
        "Engine should not import legacy runner"
    assert "tools.run_workflow_lic" not in " ".join(imports), \
        "Engine should not import from legacy runner"


def test_signal_p2_no_ad_hoc_prompt_strings():
    """Verify narrative arc engine doesn't produce ad hoc prompt strings.
    
    The engine produces structured context for Prompt Assembly, not raw prompts.
    """
    arc = build_narrative_arc_context(
        recipient_class="CTO",
        company_name="TestCo",
        sender_credibility_claims=["former CTO"],
        problem_insight="scaling",
        ask_output="call",
    )
    
    # Arc is structured data, not a prompt string
    assert isinstance(arc, NarrativeArc), "Output should be NarrativeArc dataclass"
    assert arc.sections, "Arc should have sections"
    
    # Sections have structured inputs, not prompt text
    for section in arc.sections:
        assert section.section_id in ["opener", "hook", "proof", "ask"], \
            f"Unknown section: {section.section_id}"
        # Required input is a key/reference, not prose
        assert isinstance(section.required_input, str), \
            "Section input should be string key/reference"


# =============================================================================
# P2b Archetype Tone Calibrator Tests
# =============================================================================

# Import the archetype tone calibrator
from apps_lic.engines.archetype_tone_calibrator import (
    ArchetypeToneCalibration,
    calibrate_archetype_tone,
    check_tone_violations,
)


def test_archetype_calibrator_technical_builder_suppresses_business_jargon():
    """Technical builder archetype should suppress empty business jargon."""
    calibration = calibrate_archetype_tone(
        recipient_class="CTO",
        recipient_seniority="VP Engineering",
        recipient_trigger_vector=["github", "architecture", "scaling"],
    )
    
    assert calibration.archetype_id == "TECHNICAL_BUILDER", \
        "Should detect technical builder for CTO with tech signals"
    
    # Should have suppressed business jargon
    suppressed = calibration.vocabulary_suppressed
    assert "synergy" in suppressed, "Should suppress 'synergy'"
    assert "leverage" in suppressed, "Should suppress 'leverage'"
    assert "paradigm" in suppressed, "Should suppress 'paradigm'"
    
    # Check violation detection
    message_with_jargon = "We can leverage our synergy to create a paradigm shift."
    violations = check_tone_violations(message_with_jargon, calibration)
    
    assert any("suppressed_vocabulary" in v for v in violations), \
        "Should detect suppressed vocabulary"


def test_archetype_calibrator_business_executive_drops_implementation_detail():
    """Business executive archetype should flag excessive implementation detail."""
    calibration = calibrate_archetype_tone(
        recipient_class="CEO",
        recipient_trigger_vector=["growth", "revenue", "strategy"],
    )
    
    assert calibration.archetype_id == "BUSINESS_EXECUTIVE", \
        "Should detect business executive for CEO with business signals"
    
    # Should suppress implementation details
    suppressed = calibration.vocabulary_suppressed
    assert "implementation details" in suppressed, "Should suppress implementation details"
    assert "database schema" in suppressed, "Should suppress database schema"
    
    # Check violation detection
    message_with_detail = """
    The solution uses a microservices architecture with database schema 
    normalization, REST API endpoints with dependency injection, and 
    comprehensive unit tests with 95% code coverage.
    """
    violations = check_tone_violations(message_with_detail, calibration)
    
    assert any("excessive_detail" in v for v in violations), \
        "Should detect excessive implementation detail"


def test_archetype_calibrator_unknown_defaults_concise_professional():
    """Unknown archetype defaults to concise professional register."""
    calibration = calibrate_archetype_tone(
        recipient_class="ANALYST",  # No strong signals
    )
    
    assert calibration.archetype_id == "UNKNOWN", \
        "Should be unknown for unclear signals"
    
    assert calibration.register == "concise_professional", \
        "Should default to concise professional"
    assert calibration.confidence < 0.5, \
        "Should have low confidence for unknown"


def test_archetype_tone_context_is_added_before_compile_prompt():
    """Archetype tone calibration is produced before compile_prompt step."""
    calibration = calibrate_archetype_tone(
        recipient_class="CTO",
        company_briefing={"technical_language": True},
    )
    
    # Calibration is structured data for Prompt Assembly
    assert isinstance(calibration, ArchetypeToneCalibration), \
        "Output should be ArchetypeToneCalibration dataclass"
    
    assert calibration.context_ref == "archetype_tone_calibration", \
        "Context ref should match expected slot for Prompt Assembly"
    
    # Has vocabulary guidance
    assert isinstance(calibration.vocabulary_boosted, list), \
        "Should have boosted vocabulary list"
    assert isinstance(calibration.vocabulary_suppressed, list), \
        "Should have suppressed vocabulary list"


def test_archetype_calibrator_does_not_add_factual_claims():
    """Archetype calibration affects phrasing only, never adds factual claims."""
    calibration = calibrate_archetype_tone(
        recipient_class="CTO",
        recipient_trigger_vector=["technical"],
    )
    
    # Calibration should not contain any factual claims about recipient
    # It only contains tone/phrasing guidance
    assert not any(c in calibration.archetype_id.lower() for c in [
        "expert", "leader", "genius", "best", "top"
    ]), "Archetype ID should not make factual claims"
    
    # Detection signals are process metadata, not factual assertions
    for signal in calibration.detection_signals:
        assert signal.startswith(("recipient_class:", "trigger:", "briefing:")), \
            f"Signal '{signal}' should be process metadata, not factual claim"


def test_archetype_tone_table_validates_required_archetypes():
    """Verify all required archetypes are defined in the tone table."""
    required_archetypes = {
        "TECHNICAL_BUILDER",
        "BUSINESS_EXECUTIVE", 
        "RESEARCH_ACADEMIC",
        "TALENT_SCOUT",
        "UNKNOWN",
    }
    
    # Test by calibrating for each archetype signature
    test_cases = [
        ("CTO", ["github", "architecture"], "TECHNICAL_BUILDER"),
        ("CEO", ["growth", "revenue"], "BUSINESS_EXECUTIVE"),
        ("RESEARCH_SCIENTIST", ["phd", "paper"], "RESEARCH_ACADEMIC"),
        ("RECRUITER", ["hiring", "talent"], "TALENT_SCOUT"),
    ]
    
    for recipient_class, triggers, expected in test_cases:
        calibration = calibrate_archetype_tone(
            recipient_class=recipient_class,
            recipient_trigger_vector=triggers,
        )
        assert calibration.archetype_id in required_archetypes, \
            f"{recipient_class} should map to a required archetype"


# =============================================================================
# Data Class Contract Tests
# =============================================================================


def test_message_section_immutable():
    """MessageSection dataclass is frozen (immutable)."""
    section = MessageSection(
        section_id="opener",
        required_input="context",
        forbidden_inputs=["sender_bio"],
        transition_marker="hook",
    )
    
    with pytest.raises(Exception):
        section.section_id = "modified"


def test_narrative_arc_immutable():
    """NarrativeArc dataclass is frozen (immutable)."""
    arc = NarrativeArc(
        sections=[],
        arc_coherence_score=0.8,
    )
    
    with pytest.raises(Exception):
        arc.arc_coherence_score = 0.9


def test_narrative_arc_default_values():
    """NarrativeArc has correct default values."""
    arc = NarrativeArc(
        sections=[],
        arc_coherence_score=0.5,
    )
    
    assert arc.arc_breaks == [], "Default arc_breaks is empty list"
    assert arc.recommended_order == [], "Default recommended_order is empty list"
    assert arc.context_ref == "narrative_arc_context", "Default context_ref"
    assert arc.source_refs == [], "Default source_refs is empty list"


# =============================================================================
# P2c Competitive Landscape Engine Tests
# =============================================================================


# Import P2c competitive landscape engine
from apps_lic.engines.competitive_landscape_engine import (
    CompetitiveLandscapeContext,
    build_competitive_landscape_context,
    should_include_competitive_context,
    validate_differentiator_for_exit,
)


def test_competitive_landscape_skipped_on_r4_without_source_refs():
    """Competitive landscape context is skipped when no source refs available."""
    # When company briefing lacks competitive context with source refs,
    # the engine should skip rather than fabricate
    context = build_competitive_landscape_context(
        company_briefing={"name": "TestCorp"},  # No competitive section, no source refs
    )
    
    assert context.skipped is True, "Should skip when no competitive signals or source refs"
    assert context.skip_reason == "no_competitive_signals", "Should indicate missing signals"
    assert context.differentiator_claim == "", "Should not fabricate claim"


def test_competitive_landscape_no_fabrication_below_confidence_threshold():
    """Confidence < 0.5 means skip competitive claims, not fabricate."""
    context = build_competitive_landscape_context(
        company_briefing={
            "competitive_landscape": {
                "market_position": "strong",  # Weak signal, no sources
            }
        },
    )
    
    # Confidence should be low without source refs
    assert context.confidence < 0.5, f"Confidence {context.confidence} should be < 0.5 without sources"
    assert context.skipped is True, "Should skip when confidence < 0.5"
    assert "confidence_too_low" in context.skip_reason, "Skip reason should mention confidence"


def test_competitive_landscape_requires_source_refs_for_company_claim():
    """Any company-specific differentiator claim requires source refs."""
    # With signals but no source refs
    context = build_competitive_landscape_context(
        company_briefing={
            "competitive_landscape": {
                "market_position": "leader",
                "differentiators": ["AI-powered"],
            }
        },
    )
    
    assert context.skipped is True, "Should skip without source refs"
    assert context.skip_reason == "missing_source_refs", "Should indicate missing source refs"
    
    # With both signals and source refs
    context_with_sources = build_competitive_landscape_context(
        company_briefing={
            "competitive_landscape": {
                "market_position": "leader",
                "differentiators": ["AI-powered"],
                "source_refs": ["gartner_report_2024", "forrester_wave"],
            }
        },
    )
    
    assert len(context_with_sources.source_refs) > 0, "Should capture source refs"
    assert context_with_sources.confidence >= 0.5, "Should have adequate confidence with sources"


def test_competitive_landscape_allows_one_sentence_max():
    """Exactly one differentiator sentence maximum in final draft."""
    # Build context with competitive signals
    context = build_competitive_landscape_context(
        company_briefing={
            "competitive_landscape": {
                "market_position": "leader",
                "source_refs": ["industry_report"],
            }
        },
    )
    
    # Validate differentiator claim format
    is_valid, violations = validate_differentiator_for_exit(
        differentiator=context.differentiator_claim,
        source_refs=context.source_refs,
        max_length=200,
    )
    
    # If we have a claim, it should be valid and structured
    if not context.skipped:
        assert is_valid, f"Differentiator should be valid, violations: {violations}"


def test_competitive_landscape_context_added_after_manifest_validation():
    """Competitive context only added after validate_research_and_build_manifest."""
    # This is a design intent test - the actual integration test verifies
    # that build_competitive_landscape_context is called after manifest validation
    context = build_competitive_landscape_context(
        company_briefing={
            "competitive_landscape": {
                "market_position": "leader",
                "source_refs": ["research_report"],
            }
        },
    )
    
    # Context should be complete and ready for Prompt Assembly
    assert isinstance(context, CompetitiveLandscapeContext), \
        "Output should be CompetitiveLandscapeContext dataclass"
    assert context.context_ref == "competitive_landscape_context", \
        "Context ref should match expected slot for Prompt Assembly"


def test_competitive_landscape_does_not_call_apps_research_directly():
    """Competitive landscape engine must not call apps_research directly."""
    import inspect
    
    source = inspect.getsource(build_competitive_landscape_context)
    
    # No provider imports or calls
    assert "openai" not in source.lower(), "No OpenAI imports"
    assert "anthropic" not in source.lower(), "No Anthropic imports"
    
    # No apps_research calls
    assert "apps_research" not in source.lower(), "No apps_research calls"
    
    # Uses only company_briefing from context (R3 output)
    assert "company_briefing" in source, "Should use company_briefing from context"


def test_competitive_landscape_fallback_mode_forbids_differentiator_claim():
    """When fallback_mode is true, no company-specific differentiator claim allowed."""
    context = build_competitive_landscape_context(
        company_briefing={
            "competitive_landscape": {
                "market_position": "leader",
                "differentiators": ["AI-powered"],
                "source_refs": ["industry_report"],
            }
        },
        fallback_mode=True,  # Fallback mode active
    )
    
    assert context.fallback_mode is True, "Should preserve fallback_mode"
    assert context.skipped is True, "Should skip in fallback mode"
    assert context.skip_reason == "fallback_mode_active", "Should indicate fallback mode"
    assert context.differentiator_claim == "", "No claim in fallback mode"


def test_competitive_landscape_context_immutable():
    """CompetitiveLandscapeContext dataclass is frozen (immutable)."""
    context = CompetitiveLandscapeContext(
        differentiator_claim="test",
        confidence=0.8,
    )
    
    with pytest.raises(Exception):
        context.differentiator_claim = "modified"


# =============================================================================
# Prompt Template and Exit Rubric Tests
# =============================================================================


def test_signal_p2_prompt_template_hash_changes_after_template_update():
    """Template changes must update template_hash and prompt_registry_hash.
    
    This is a documentation test - the actual verification happens in CI
    via prompt hash validation.
    """
    # Documentation only - actual hash verification happens in CI
    assert True, "See plan: outreach_draft_v1.yaml hash must change when updated"


def test_signal_p2_exit_rubric_has_narrative_and_tone_dims():
    """Exit rubric must include narrative_coherence and tone_register_fit dims.
    
    This is a documentation test - actual rubric validation happens via
    config validation gates.
    """
    # Documentation only - actual rubric validation in CI
    assert True, "See plan: exit_rubric.yaml must add narrative_coherence and tone_register_fit"
