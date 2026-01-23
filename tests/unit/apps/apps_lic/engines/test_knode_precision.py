"""
K-Node Precision Test Suite.

Tests for Specialist Logic Integration (K.1 - K.7).
Requirement: 100% Pass Rate for Canon LIC Status.
"""
import pytest
from unittest.mock import MagicMock, patch
from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent
from apps_lic.engines.HOP5GenerationAgent import HOP5GenerationAgent
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class TestKNodePrecision:
    """Tests for Specialist Logic Integration (K.1 - K.7)."""

    def test_k1_cxo_precedence_ceo(self):
        """Verify K.1: Title 'CEO' forces C_LEVEL/1.0 confidence regardless of 'about' section."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {
            "title": "Acting CEO",
            "about": "N/A",
            "name": "John Doe",
            "company": "TestCorp"
        })
        
        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 1.0  # CXO precedence = 100% confidence
        
        # Verify trace was logged
        traces = registry.get_traces()
        cxo_traces = [t for t in traces if t["type"] == "CXO_PRECEDENCE_TRIGGERED"]
        assert len(cxo_traces) == 1
        assert cxo_traces[0]["details"]["token"] == "CEO"

    def test_k1_cxo_precedence_cto(self):
        """Verify K.1: Title 'CTO' forces C_LEVEL/1.0 confidence."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {
            "title": "CTO",  # Use exact CXO token
            "about": "Technical leader",
            "name": "Jane Smith",
            "company": "TechCorp"
        })
        
        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 1.0

    def test_k1_cxo_precedence_in_about(self):
        """Verify K.1: CXO token in 'about' section also triggers precedence."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {
            "title": "Executive",
            "about": "Former CEO of StartupX",
            "name": "Bob Johnson",
            "company": "NewCo"
        })
        
        agent = HOP1ProfileAnalysisAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 1.0

    def test_k5_cta_length_constraint_connection_req(self):
        """Verify K.5: CONNECTION_REQ CTAs are <= 5 words."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop4 = {"route": "CONNECTION_REQ", "constraints": {"char_limit": 300}}
        cta = agent._generate_k5_cta(hop4, registry)
        
        # Verify word count
        word_count = len(cta.split())
        assert word_count <= 5, f"CTA '{cta}' has {word_count} words, expected <= 5"
        
        # Verify no meeting request language
        assert "call" not in cta.lower()
        assert "meeting" not in cta.lower()
        assert "schedule" not in cta.lower()

    def test_k5_cta_length_constraint_inmail(self):
        """Verify K.5: INMAIL CTAs are <= 10 words."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop4 = {"route": "INMAIL", "constraints": {"char_limit": 500}}
        cta = agent._generate_k5_cta(hop4, registry)
        
        # Verify word count
        word_count = len(cta.split())
        assert word_count <= 10, f"CTA '{cta}' has {word_count} words, expected <= 10"

    def test_k7_signature_format(self):
        """Verify K.7: Signature must be exactly 4 lines (Immutability Gate)."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop1 = {"Archetype": "C_LEVEL", "recipient_company": "TestCorp"}
        body = "Test body content"
        cta = "Open to connecting?"
        
        message = agent._assemble_k7_message(body, cta, hop1, registry)
        
        # Verify signature is present and starts with "Regards,"
        assert "Regards," in message
        
        # Verify the trace logged 4 signature lines
        traces = registry.get_traces()
        k7_traces = [t for t in traces if t["type"] == "K7_MESSAGE_ASSEMBLED"]
        assert len(k7_traces) == 1
        assert k7_traces[0]["details"]["signature_lines"] == 4

    def test_k3_transition_phrase_c_level(self):
        """Verify K.3: C_LEVEL drafts include strategic research transition phrase."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop1 = {"Archetype": "C_LEVEL", "recipient_company": "Acme Corp"}
        hop2 = {"strategic_signals": ["AI initiative", "Cloud migration"]}
        hop3 = {"sender_grounding": {"products": ["Product A"]}}
        
        body = agent._generate_k3_body(hop1, hop2, hop3, registry)
        
        expected_phrase = "Two strategic insights I have gleaned from my research about Acme Corp:"
        assert expected_phrase in body

    def test_k3_transition_phrase_non_c_level(self):
        """Verify K.3: Non-C_LEVEL uses different transition phrase."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop1 = {"Archetype": "MANAGER", "recipient_company": "TechCo"}
        hop2 = {"strategic_signals": []}
        hop3 = {"sender_grounding": {"products": []}}
        
        body = agent._generate_k3_body(hop1, hop2, hop3, registry)
        
        # Should use the non-C_LEVEL transition
        assert "I noticed some interesting developments at TechCo:" in body
        assert "Two strategic insights" not in body

    def test_k5_trace_logging(self):
        """Verify K.5 generates proper trace with compliance info."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop4 = {"route": "CONNECTION_REQ", "constraints": {"char_limit": 300}}
        agent._generate_k5_cta(hop4, registry)
        
        traces = registry.get_traces()
        k5_traces = [t for t in traces if t["type"] == "K5_CTA_GENERATED"]
        
        assert len(k5_traces) == 1
        assert k5_traces[0]["details"]["route"] == "CONNECTION_REQ"
        assert k5_traces[0]["details"]["word_limit"] == 5
        assert k5_traces[0]["details"]["compliant"] is True

    def test_k7_trace_logging(self):
        """Verify K.7 generates proper trace with assembly info."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()
        
        hop1 = {"Archetype": "C_LEVEL", "recipient_company": "TestCorp"}
        agent._assemble_k7_message("Body text", "CTA text", hop1, registry)
        
        traces = registry.get_traces()
        k7_traces = [t for t in traces if t["type"] == "K7_MESSAGE_ASSEMBLED"]
        
        assert len(k7_traces) == 1
        assert k7_traces[0]["details"]["signature_lines"] == 4

    def test_full_k_node_integration(self):
        """Verify full K-Node integration through HOP5 generation."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        # Setup upstream data
        buffer.write_once("hop1_analysis", {
            "Archetype": "C_LEVEL",
            "confidence": 1.0,
            "recipient_title": "CEO",
            "recipient_company": "MegaCorp",
            "recipient_name": "Alice CEO"
        })
        buffer.write_once("hop2_research", {
            "signal_score": 0.9,
            "strategic_signals": ["Digital transformation", "AI adoption"]
        })
        buffer.write_once("hop3_sender_grounding", {
            "sender_grounding": {"products": ["Platform X", "Service Y"]}
        })
        buffer.write_once("hop4_routing", {
            "route": "CONNECTION_REQ",
            "constraints": {"char_limit": 300, "word_range": [50, 100]}
        })
        
        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop5_generation")
        
        # Verify output structure
        assert "selected_draft" in result
        assert "all_candidates" in result
        
        # Verify K.3 transition phrase in body
        draft_text = result["selected_draft"]["text"]
        assert "Two strategic insights I have gleaned from my research about MegaCorp:" in draft_text
        
        # Verify K.7 signature format
        assert "Regards," in draft_text
        
        # Verify traces
        trace_types = [t["type"] for t in registry.get_traces()]
        assert "K3_BODY_GENERATED" in trace_types
        assert "K5_CTA_GENERATED" in trace_types
        assert "K7_MESSAGE_ASSEMBLED" in trace_types
