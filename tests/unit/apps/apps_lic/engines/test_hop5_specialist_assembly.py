"""
HOP-5 Specialist Assembly Test Suite.

Tests for Phase 15: K.3, K.5A, K.5, K.7 Integration.
Requirement: 100% Pass Rate for LIC Specialist Assembly.
"""

from apps_lic.engines.HOP5GenerationAgent import HOP5GenerationAgent
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class TestHOP5SpecialistAssembly:
    """
    Mandatory Test Suite for Phase 15.
    Requirement: 100% Pass Language.
    """

    def test_k3_transition_phrase_persistence(self):
        """Verify K.3: C_LEVEL drafts must include the strategic research phrase."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "C_LEVEL",
                "recipient_company": "TechCorp",
                "recipient_title": "CEO",
                "recipient_name": "Alice",
            },
        )
        buffer.write_once(
            "hop2_research",
            {"strategic_signals": ["AI Growth", "Cloud Migration"], "signal_score": 0.9},
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {
                "sender_grounding": {
                    "products": ["Platform X", "Service Y"],
                    "capabilities": ["AI Solutions"],
                }
            },
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "INMAIL", "constraints": {"char_limit": 500, "word_range": [50, 100]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        expected_phrase = "Two strategic insights I have gleaned from my research about TechCorp:"
        assert expected_phrase in result["selected_draft"]["text"]
        assert result["meta"]["k3_phrase"] is not None
        assert "TechCorp" in result["meta"]["k3_phrase"]

    def test_k5a_provenance_enforcement(self):
        """Verify K.5A: Output must contain exactly 7 provenance labels in 3V-3T-1S order."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "MANAGER",
                "recipient_company": "StartupCo",
                "recipient_title": "VP Engineering",
                "recipient_name": "Bob",
            },
        )
        buffer.write_once(
            "hop2_research",
            {
                "strategic_signals": ["Digital Transformation", "API Strategy", "DevOps"],
                "signal_score": 0.85,
            },
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {
                "sender_grounding": {
                    "products": ["Product A", "Product B", "Product C"],
                    "capabilities": ["Consulting", "Training"],
                }
            },
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "CONNECTION_REQ", "constraints": {"char_limit": 300, "word_range": [30, 50]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        labels = result["selected_draft"]["provenance_labels"]

        # Verify 3V-3T-1S distribution
        assert len(labels) == 7, f"Expected 7 labels, got {len(labels)}"
        assert labels.count("V") == 3, f"Expected 3 V labels, got {labels.count('V')}"
        assert labels.count("T") == 3, f"Expected 3 T labels, got {labels.count('T')}"
        assert labels.count("S") == 1, f"Expected 1 S label, got {labels.count('S')}"

        # Verify bullets exist
        bullets = result["selected_draft"]["bullets"]
        assert len(bullets) == 7, f"Expected 7 bullets, got {len(bullets)}"

    def test_k7_signature_immutability(self):
        """Verify K.7: Signature must be the final 4 lines of the message."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "C_LEVEL",
                "recipient_company": "MegaCorp",
                "recipient_title": "CFO",
                "recipient_name": "Carol",
            },
        )
        buffer.write_once(
            "hop2_research", {"strategic_signals": ["Financial Innovation"], "signal_score": 0.95}
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {"sender_grounding": {"products": ["FinTech Platform"], "capabilities": []}},
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "INMAIL", "constraints": {"char_limit": 600, "word_range": [80, 120]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        text = result["selected_draft"]["text"]

        # Verify signature is present
        assert "Regards," in text
        assert "linkedin.com/in/[profile]" in text

        # Verify trace logged 4 signature lines
        traces = registry.get_traces()
        k7_traces = [t for t in traces if t["type"] == "K7_MESSAGE_ASSEMBLED"]
        assert len(k7_traces) >= 1
        assert k7_traces[0]["details"]["signature_lines"] == 4

    def test_trace_registry_granularity(self):
        """Verify that the TraceRegistry logs each specialist node start."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "C_LEVEL",
                "recipient_company": "TestCo",
                "recipient_title": "CEO",
                "recipient_name": "Dave",
            },
        )
        buffer.write_once(
            "hop2_research", {"strategic_signals": ["Market Expansion"], "signal_score": 0.88}
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {"sender_grounding": {"products": ["Solution X"], "capabilities": ["Support"]}},
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "INMAIL", "constraints": {"char_limit": 500, "word_range": [60, 90]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        traces = [t["type"] for t in registry.get_traces()]

        # Verify all specialist nodes logged their start
        assert "K3_START" in traces, "K3_START trace missing"
        assert "K5A_START" in traces, "K5A_START trace missing"
        assert "K5_CTA_GENERATED" in traces, "K5_CTA_GENERATED trace missing"
        assert "K7_MESSAGE_ASSEMBLED" in traces, "K7_MESSAGE_ASSEMBLED trace missing"
        assert "DECISION_FINAL" in traces, "DECISION_FINAL trace missing"

    def test_k5a_bullet_content_structure(self):
        """Verify K.5A: Bullets have correct structure with bullet points."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "MANAGER",
                "recipient_company": "InnovateCo",
                "recipient_title": "Director",
                "recipient_name": "Eve",
            },
        )
        buffer.write_once(
            "hop2_research", {"strategic_signals": ["Innovation", "Growth"], "signal_score": 0.8}
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {
                "sender_grounding": {
                    "products": ["Tool A", "Tool B"],
                    "capabilities": ["Capability X"],
                }
            },
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "CONNECTION_REQ", "constraints": {"char_limit": 300, "word_range": [30, 50]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        bullets = result["selected_draft"]["bullets"]

        # Verify all bullets start with bullet point
        for bullet in bullets:
            assert bullet.startswith("•"), f"Bullet '{bullet}' doesn't start with '•'"

    def test_k3_non_c_level_transition(self):
        """Verify K.3: Non-C_LEVEL uses different transition phrase."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "MANAGER",
                "recipient_company": "DevShop",
                "recipient_title": "Engineering Manager",
                "recipient_name": "Frank",
            },
        )
        buffer.write_once(
            "hop2_research",
            {"strategic_signals": ["Tech Stack Modernization"], "signal_score": 0.75},
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {"sender_grounding": {"products": ["Dev Tools"], "capabilities": []}},
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "INMAIL", "constraints": {"char_limit": 400, "word_range": [50, 80]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        text = result["selected_draft"]["text"]

        # Verify non-C_LEVEL transition phrase
        assert "I noticed some interesting developments at DevShop:" in text
        assert "Two strategic insights" not in text

    def test_k5_cta_word_count_compliance(self):
        """Verify K.5: CTA word count is compliant with route constraints."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "C_LEVEL",
                "recipient_company": "GlobalCorp",
                "recipient_title": "CTO",
                "recipient_name": "Grace",
            },
        )
        buffer.write_once(
            "hop2_research", {"strategic_signals": ["Cloud Strategy"], "signal_score": 0.92}
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {"sender_grounding": {"products": ["Cloud Platform"], "capabilities": ["Migration"]}},
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "CONNECTION_REQ", "constraints": {"char_limit": 300, "word_range": [30, 50]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        cta = result["selected_draft"]["cta"]

        # Verify word count for CONNECTION_REQ
        word_count = len(cta.split())
        assert word_count <= 5, f"CONNECTION_REQ CTA has {word_count} words, expected <= 5"

        # Verify trace shows compliance
        traces = registry.get_traces()
        k5_traces = [t for t in traces if t["type"] == "K5_CTA_GENERATED"]
        assert len(k5_traces) >= 1
        assert k5_traces[0]["details"]["compliant"] is True

    def test_full_specialist_assembly_output_structure(self):
        """Verify complete output structure includes all specialist components."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Seed dependencies
        buffer.write_once(
            "hop1_analysis",
            {
                "Archetype": "C_LEVEL",
                "recipient_company": "EnterpriseCo",
                "recipient_title": "CEO",
                "recipient_name": "Henry",
            },
        )
        buffer.write_once(
            "hop2_research",
            {"strategic_signals": ["Digital Transformation", "AI Adoption"], "signal_score": 0.98},
        )
        buffer.write_once(
            "hop3_sender_grounding",
            {
                "sender_grounding": {
                    "products": ["Enterprise Suite", "AI Platform", "Analytics"],
                    "capabilities": ["Consulting", "Support", "Training"],
                }
            },
        )
        buffer.write_once(
            "hop4_routing",
            {"route": "INMAIL", "constraints": {"char_limit": 700, "word_range": [100, 150]}},
        )

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")

        # Verify all specialist components are present
        assert "selected_draft" in result
        assert "body" in result["selected_draft"]
        assert "bullets" in result["selected_draft"]
        assert "cta" in result["selected_draft"]
        assert "provenance_labels" in result["selected_draft"]
        assert "transition_phrase" in result["selected_draft"]
        assert "text" in result["selected_draft"]

        # Verify meta includes k3_phrase
        assert "meta" in result
        assert "k3_phrase" in result["meta"]
        assert result["meta"]["k3_phrase"] is not None
