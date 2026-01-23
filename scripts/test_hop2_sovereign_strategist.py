"""
MANDATORY Test Suite: HOP-2 Sovereign Strategist
100% Pass Requirement for Windsurf Execution.

Focus Areas:
- Seniority Escalation (K.3 Logic)
- Artifact ID Uniqueness & Traceability
- Logic Purity & Syntax Integrity
- Critical Input Validation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import MagicMock, patch
from apps_lic.engines.HOP2ResearchAgent import HOP2ResearchAgent
from apps_lic.shared.foundation.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.foundation.trace_registry import TraceRegistry


class TestHOP2SovereignStrategist:
    """
    MANDATORY: 100% Pass Requirement for Windsurf Execution.
    Focus: Seniority Escalation, Artifact ID Uniqueness, Logic Purity.
    """

    def test_wants_derivation_seniority_escalation(self):
        """
        Verify that C_LEVEL archetypes escalate research 'wants' to include
        strategic priorities and earnings signals.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once(
            "mission_input",
            {"contact_name": "Jane Doe", "company_id": "TechCorp", "recipient_id": "exec_001"},
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        # Verify 100% Pass: C-Level must trigger 3+ strategic wants
        assert result is not None, "hop2_research output missing"
        assert result["metadata"]["wants_count"] >= 3, "C_LEVEL should escalate to 3+ wants"
        
        # Verify strategic priorities are in trace logs
        traces = registry.get_traces()
        trace_str = str(traces)
        assert "starting_retrieval_planning" in trace_str, "Missing retrieval planning trace"

    def test_wants_derivation_mid_level_archetype(self):
        """
        Verify that non-C_LEVEL archetypes get baseline wants without escalation.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER"})
        buffer.write_once(
            "mission_input",
            {"contact_name": "John Smith", "company_id": "StartupCo", "recipient_id": "mgr_001"},
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        # Verify: Non-C_LEVEL should have baseline wants (1 primary anchor)
        assert result is not None
        assert result["metadata"]["wants_count"] >= 1, "Should have at least primary anchor"
        assert result["metadata"]["wants_count"] < 3, "MANAGER should not escalate to 3+ wants"

    def test_summarization_syntax_integrity(self):
        """
        Verify the fix for the nested loop syntax error in _summarize_for_archetype.
        Ensures the brief is correctly formatted with pipe delimiters.
        """
        agent = HOP2ResearchAgent()
        evidence_pack = [
            {"summary": "Expanding into APAC market", "source": "news", "artifact_id": "1"},
            {"summary": "Launched new AI platform", "source": "PR", "artifact_id": "2"},
            {"summary": "Q4 earnings beat expectations", "source": "earnings", "artifact_id": "3"},
        ]

        brief = agent._summarize_for_archetype(evidence_pack, "EXECUTIVE")

        # Verify 100% Pass: Formatting must include pipe delimiters and archetype prefix
        assert "Strategic Brief for EXECUTIVE:" in brief, "Missing archetype prefix"
        assert "|" in brief, "Missing pipe delimiter between summaries"
        assert "APAC market" in brief, "Missing first summary content"
        assert len(brief) <= 500, "Brief exceeds 500 char limit"

    def test_summarization_empty_evidence(self):
        """
        Verify graceful handling of empty evidence pack.
        """
        agent = HOP2ResearchAgent()
        brief = agent._summarize_for_archetype([], "C_LEVEL")
        
        assert brief == "No evidence available for strategic brief.", "Should return fallback message"

    def test_deterministic_artifact_id_traceability(self):
        """
        Verify that artifact IDs are deterministic based on source and multi-factor seed.
        Ensures audit trails correctly map back to specific sources.
        """
        agent = HOP2ResearchAgent()
        item = {
            "text": "Strategic Growth Plan for 2025",
            "source": "Internal",
            "company_id": "A",
            "tool": "V",
        }

        id1 = agent._generate_stable_id(item)
        id2 = agent._generate_stable_id(item)

        # Verify 100% Pass: IDs must be consistent and 12 chars long
        assert id1 == id2, "Artifact IDs must be deterministic"
        assert len(id1) == 12, "Artifact ID must be 12 characters"
        assert id1.isalnum(), "Artifact ID must be alphanumeric"

    def test_artifact_id_collision_avoidance(self):
        """
        Verify that similar items generate different artifact IDs.
        """
        agent = HOP2ResearchAgent()
        item1 = {
            "text": "Strategic Growth Plan",
            "source": "Internal",
            "company_id": "A",
            "tool": "V",
        }
        item2 = {
            "text": "Strategic Growth Plan",
            "source": "External",
            "company_id": "A",
            "tool": "V",
        }

        id1 = agent._generate_stable_id(item1)
        id2 = agent._generate_stable_id(item2)

        # Verify: Different sources should generate different IDs
        assert id1 != id2, "Different sources must generate unique artifact IDs"

    def test_critical_input_missing_halt(self):
        """
        Verify that HOP-2 raises a RuntimeError if HOP-1 analysis is absent.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"id": "123"})

        agent = HOP2ResearchAgent()
        # Verify 100% Pass: System must halt on critical context gap
        with pytest.raises(RuntimeError, match="Missing hop1_analysis"):
            agent.run_phase(buffer, registry)

    def test_c_level_missing_company_id_warning(self):
        """
        Verify that C_LEVEL missions without company_id trigger a warning trace.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once(
            "mission_input", {"contact_name": "Jane Doe", "recipient_id": "exec_001"}
        )  # Missing company_id

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        # Verify: Warning trace should be logged
        traces = registry.get_traces()
        warning_found = any(
            t.get("event_type") == "INPUT_WARNING" and "company_id" in str(t)
            for t in traces
        )
        assert warning_found, "Should log warning for C_LEVEL without company_id"

    def test_evidence_pack_structure(self):
        """
        Verify that evidence pack has correct structure with all required fields.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER"})
        buffer.write_once(
            "mission_input",
            {"contact_name": "Test User", "company_id": "TestCo", "recipient_id": "test_001"},
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        evidence_pack = result["evidence_pack"]

        # Verify: Each artifact has required fields
        assert len(evidence_pack) > 0, "Evidence pack should not be empty"
        for artifact in evidence_pack:
            assert "artifact_id" in artifact, "Missing artifact_id"
            assert "summary" in artifact, "Missing summary"
            assert "source" in artifact, "Missing source"
            assert "confidence" in artifact, "Missing confidence"
            assert len(artifact["artifact_id"]) == 12, "Artifact ID must be 12 chars"
            assert 0.0 <= artifact["confidence"] <= 1.0, "Confidence must be 0-1"

    def test_strategic_brief_generation(self):
        """
        Verify that strategic brief is generated and included in output.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "EXECUTIVE"})
        buffer.write_once(
            "mission_input",
            {"contact_name": "Test Exec", "company_id": "ExecCo", "recipient_id": "exec_002"},
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        
        # Verify: Strategic brief exists and has content
        assert "strategic_brief" in result, "Missing strategic_brief"
        assert len(result["strategic_brief"]) > 0, "Strategic brief should not be empty"
        assert "Strategic Brief for EXECUTIVE:" in result["strategic_brief"]

    def test_metadata_completeness(self):
        """
        Verify that metadata includes all required tracking fields.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once(
            "mission_input",
            {"contact_name": "CEO", "company_id": "BigCorp", "recipient_id": "ceo_001"},
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        metadata = result["metadata"]

        # Verify: Metadata has tracking fields
        assert "wants_count" in metadata, "Missing wants_count"
        assert "retrieval_count" in metadata, "Missing retrieval_count"
        assert metadata["wants_count"] > 0, "wants_count should be positive"
        assert metadata["retrieval_count"] > 0, "retrieval_count should be positive"

    def test_trace_registry_completeness(self):
        """
        Verify that all critical phases are traced.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER"})
        buffer.write_once(
            "mission_input",
            {"contact_name": "Manager", "company_id": "MgrCo", "recipient_id": "mgr_002"},
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        traces = registry.get_traces()
        trace_types = [t.get("event_type") for t in traces]

        # Verify: Critical trace events are present
        assert "AGENT_START" in trace_types, "Missing AGENT_START trace"
        assert "PHASE_STEP" in trace_types, "Missing PHASE_STEP trace"
        assert "RETRIEVAL_PLAN_COMPLETED" in trace_types, "Missing completion trace"
        assert "AGENT_END" in trace_types, "Missing AGENT_END trace"


def run_tests():
    """Execute test suite with detailed reporting."""
    print("=" * 80)
    print("HOP-2 SOVEREIGN STRATEGIST TEST SUITE")
    print("=" * 80)
    print()

    # Run pytest with verbose output
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--color=yes",
            "-W",
            "ignore::DeprecationWarning",
        ]
    )

    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED - 100% Pass Requirement Met")
        print("HOP-2 Sovereign Strategist is ready for deployment")
    else:
        print("❌ TEST FAILURES DETECTED")
        print("DO NOT DEPLOY until all tests pass")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
