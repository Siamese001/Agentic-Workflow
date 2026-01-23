"""
HOP-2 Sovereign Strategist Test Suite (v2.5).

MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
"""

import pytest
from unittest.mock import MagicMock
from apps_lic.engines.HOP2ResearchAgent import HOP2ResearchAgent
from apps_lic.shared.foundation.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.foundation.trace_registry import TraceRegistry


class TestHOP2SovereignStrategist:
    """
    Sovereign Strategist Test Suite for v2.5.
    MANDATORY: 100% PASS REQUIREMENT.
    """

    def test_k3_wants_derivation_cxo_precedence(self):
        """
        Verify K.3: C-Level targets must trigger strategic milestone and news 'wants'.
        Ensures high-seniority drafts are backed by business intelligence.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once("mission_input", {"company_id": "AcmeCorp", "contact_name": "Jane Doe"})

        agent = HOP2ResearchAgent(memory_store=MagicMock())
        agent.run_phase(buffer, registry)

        # Verify 100% Pass: C-Level wants must be derived correctly.
        result = buffer.read("hop2_research")
        assert result["metadata"]["wants_count"] >= 3
        # Verify milestones trace is present
        traces = str(registry.get_traces())
        assert "RETRIEVAL_PLAN_COMPLETED" in traces

    def test_stable_artifact_id_consistency(self):
        """
        Verify Artifact IDs are deterministic and multi-factored.
        Ensures audit trails correctly map back to specific sources.
        """
        agent = HOP2ResearchAgent(memory_store=None)
        item1 = {"text": "Strategic AI Growth", "source": "url_1", "company_id": "ABC"}
        item2 = {"text": "Strategic AI Growth", "source": "url_1", "company_id": "ABC"}

        id1 = agent._generate_stable_id(item1)
        id2 = agent._generate_stable_id(item2)

        # Verify 100% Pass: Same inputs must produce same ID.
        assert id1 == id2
        assert len(id1) == 12

    def test_summarization_syntax_fix(self):
        """
        Verify the fix for the nested loop syntax error in _summarize_for_archetype.
        Ensures strategic brief generation does not crash.
        """
        agent = HOP2ResearchAgent(memory_store=None)
        evidence = [{"summary": "fact 1"}, {"summary": "fact 2"}]

        # This previously failed with 'summaries is not iterable'
        brief = agent._summarize_for_archetype(evidence, "EXECUTIVE")

        # Verify 100% Pass: Brief must contain the summaries.
        assert "fact 1" in brief
        assert "Strategic Brief" in brief

    def test_sovereign_data_missing_halt(self):
        """
        Verify that HOP-2 raises a RuntimeError if HOP-1 analysis is missing.
        Prevents research from running on unclassified profiles.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # hop1_analysis is intentionally missing
        buffer.write_once("mission_input", {"id": "123"})

        agent = HOP2ResearchAgent(memory_store=None)
        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)

        # Verify 100% Pass: DATA_ERROR must be logged.
        assert any(t["type"] == "DATA_ERROR" for t in registry.get_traces())

    def test_trace_registry_observability(self):
        """
        Verify that the Retrieval Plan start and completion are logged.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "RECRUITER"})
        buffer.write_once("mission_input", {"company_id": "Acme", "contact_name": "Bob"})

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        traces = [t["type"] for t in registry.get_traces()]
        assert "RETRIEVAL_PLAN_COMPLETED" in traces

    def test_evidence_pack_structure(self):
        """
        Verify that evidence pack contains required fields.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "SENIOR_TA"})
        buffer.write_once("mission_input", {"company_id": "TestCorp", "contact_name": "Alice"})

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        assert "evidence_pack" in result
        assert "strategic_brief" in result
        assert "metadata" in result

        # Check evidence item structure
        if result["evidence_pack"]:
            evidence = result["evidence_pack"][0]
            assert "artifact_id" in evidence
            assert "summary" in evidence
            assert "source" in evidence
            assert "confidence" in evidence

    def test_strategic_brief_generation(self):
        """
        Verify that strategic brief is generated based on evidence.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once("mission_input", {"company_id": "BigCorp", "contact_name": "CEO John"})

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        assert result["strategic_brief"] is not None
        assert len(result["strategic_brief"]) > 0
        # Brief should mention the archetype
        assert "C_LEVEL" in result["strategic_brief"]

    def test_non_c_level_wants_count(self):
        """
        Verify that non-C-Level archetypes get fewer wants.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "RECRUITER"})
        buffer.write_once(
            "mission_input", {"company_id": "SmallCo", "contact_name": "Recruiter Jane"}
        )

        agent = HOP2ResearchAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop2_research")
        # Non-C-Level should have only 1 want (profile highlights)
        assert result["metadata"]["wants_count"] == 1
