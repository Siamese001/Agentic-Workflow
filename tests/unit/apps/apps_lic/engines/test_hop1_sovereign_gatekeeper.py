"""
HOP-1 Sovereign Gatekeeper Test Suite.

MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
"""

import pytest
from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class TestHOP1SpecialistGatekeeper:
    """
    Sovereign Foundation Test Suite for HOP-1.
    MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
    """

    def test_k1_cxo_precedence_lock(self):
        """
        Verify K.1: Title 'Interim CEO' must bypass heuristics and force 1.0 confidence.
        Target: Zero tolerance for misclassification of high-value targets.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # 'CEO' is in the C_LEVEL keywords in agent_specs.json
        buffer.write_once(
            "mission_input",
            {"contact_title": "Interim CEO", "contact_about": "Strategic AI leadership"},
        )

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 1.0  # Force-multiplier per K1 rule
        assert result["cxo_precedence_triggered"] is True
        assert registry.count("CXO_PRECEDENCE_TRIGGERED") == 1

    def test_gate_2_failure_blocking(self):
        """
        Verify Gate 2: Mission must fail if the contact title is missing.
        Ensures the orchestrator stops before wasting downstream tokens.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"contact_name": "John Doe"})  # Missing title

        agent = HOP1ProfileAnalysisAgent()
        # V2AgentBase wraps exceptions in RuntimeError
        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)

        traces = [t["type"] for t in registry.get_traces()]
        assert "GATE_2_FAILED" in traces

    def test_heuristic_fallback_low_seniority(self):
        """
        Verify that standard titles fall back to heuristics correctly.
        'recruiter' keyword maps to RECRUITER archetype.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Use a title that contains 'recruiter' keyword
        buffer.write_once("mission_input", {"contact_title": "Technical Recruiter"})

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "RECRUITER"
        assert result["cxo_precedence_triggered"] is False

    def test_l3_slow_path_trigger(self):
        """
        Verify that low-confidence titles trigger the Reasoning trace.
        Unknown titles get default_confidence (0.5) < threshold (0.6).
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Use a title with no matching keywords - will get default confidence 0.5
        buffer.write_once("mission_input", {"contact_title": "Coordinator of Special Projects"})

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        traces = [t["type"] for t in registry.get_traces()]
        # Confidence for unknown titles is 0.5 (default_confidence)
        # threshold is 0.6 (manual_override_threshold)
        assert "REASONING_ACTIVATED" in traces

    def test_legacy_recipient_profile_support(self):
        """
        Verify backward compatibility with recipient_profile input format.
        CTO triggers CXO precedence with 1.0 confidence.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "recipient_profile",
            {
                "title": "CTO",  # Use exact CXO token
                "about": "Tech leadership",
                "name": "Jane Smith",
                "company": "TechCorp",
            },
        )

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 1.0  # CXO precedence forces 1.0
        assert result["cxo_precedence_triggered"] is True
        assert result["recipient_name"] == "Jane Smith"
        assert result["recipient_company"] == "TechCorp"

    def test_entrance_gates_recorded(self):
        """
        Verify that passed entrance gates are recorded in output.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"contact_title": "VP of Engineering"})

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert "entrance_gates_passed" in result
        assert "GATE_2_BLOCK" in result["entrance_gates_passed"]
        assert "GATE_4_ARCHETYPE" in result["entrance_gates_passed"]

    def test_metadata_title_captured(self):
        """
        Verify that metadata includes the original title.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"contact_title": "Director of Sales"})

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert "metadata" in result
        assert result["metadata"]["title"] == "Director of Sales"

    def test_cxo_precedence_absolute_lock(self):
        """
        PHASE 1 HARDENING: Verify that the CXO token 'CEO' forces 1.0 confidence and C_LEVEL archetype
        regardless of other noise in the 'about' section.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "mission_input",
            {
                "contact_title": "Interim Chief Executive Officer",
                "contact_about": "I used to be a coordinator but now I am the CEO.",
            },
        )

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 1.0
        assert result["cxo_precedence_triggered"] is True
        assert any(t["type"] == "CXO_PRECEDENCE_TRIGGERED" for t in registry.get_traces())

    def test_regex_boundary_false_positive_prevention(self):
        """
        PHASE 1 HARDENING: Verify that tokens like 'COO' do not trigger on words like 'Coordinator' or 'COOPERATIVE'.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "mission_input",
            {
                "contact_title": "Project Coordinator",
                "contact_about": "Expert in cooperative systems.",
            },
        )

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        # Should NOT be C_LEVEL if the token 'COO' was the only trigger attempt
        assert result["Archetype"] != "C_LEVEL"
        assert result["cxo_precedence_triggered"] is False

    def test_gate_2_empty_title_halt(self):
        """
        PHASE 1 HARDENING: Verify that a missing contact_title triggers a GATE_2_FAILED trace and raises ValueError.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"contact_about": "Just a bio."})

        agent = HOP1ProfileAnalysisAgent()
        with pytest.raises(RuntimeError):  # V2AgentBase wraps in RuntimeError
            agent.run_phase(buffer, registry)

        assert any(t["type"] == "GATE_2_FAILED" for t in registry.get_traces())

    def test_l3_slow_path_confidence_trigger(self):
        """
        PHASE 1 HARDENING: Verify that confidence scores below the threshold (0.6) trigger REASONING_ACTIVATED.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Unknown title should result in low confidence fallback
        buffer.write_once("mission_input", {"contact_title": "Grand Master of Magic"})

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        assert any(t["type"] == "REASONING_ACTIVATED" for t in registry.get_traces())

    def test_input_normalization_trace(self):
        """
        PHASE 1 HARDENING: Verify INPUT_NORMALIZED trace is emitted with title and about lengths.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "mission_input",
            {
                "contact_title": "  CEO  ",  # Whitespace should be stripped
                "contact_about": "  Leadership  ",
            },
        )

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        traces = registry.get_traces()
        norm_trace = next((t for t in traces if t["type"] == "INPUT_NORMALIZED"), None)
        assert norm_trace is not None
        # Trace data is stored under "details" key
        assert "details" in norm_trace
        assert "title_len" in norm_trace["details"]
        assert "about_len" in norm_trace["details"]
        assert norm_trace["details"]["title_len"] == 3  # "CEO" after strip

    def test_reasoning_not_required_trace(self):
        """
        PHASE 1 HARDENING: Verify REASONING_NOT_REQUIRED trace when confidence is high.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"contact_title": "CEO"})

        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)

        traces = registry.get_traces()
        # CXO precedence gives 1.0 confidence, so reasoning not required
        assert any(t["type"] == "REASONING_NOT_REQUIRED" for t in traces)

    def test_reasoning_skipped_trace(self):
        """
        PHASE 1 HARDENING: Verify REASONING_SKIPPED trace when LLM/COT disabled.
        MANDATORY: 100% Pass Requirement for Windsurf Execution.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"contact_title": "Unknown Title"})

        # Create agent without LLM (None by default)
        agent = HOP1ProfileAnalysisAgent(llm_client=None)
        # ReasoningToggles is frozen, so we can't modify it
        # By default, use_cot is False when llm is None
        agent.run_phase(buffer, registry)

        traces = registry.get_traces()
        # Low confidence but no LLM, so reasoning skipped
        assert any(t["type"] == "REASONING_SKIPPED" for t in traces)
