"""
Unit tests for HOP1 Hybrid Architecture.
Verifies LLM reasoning injection and hybrid decision-making.
"""

from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry

from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent


class MockLLM:
    """Mock LLM for testing hybrid reasoning."""

    def analyze(self, title, context):
        """Simulate intelligent override for 'Acting' roles."""
        if "acting" in title.lower():
            return {
                "archetype": "EXECUTIVE",
                "confidence": 0.85,
                "reasoning": "LLM recognized 'Acting' implies temporary high status",
                "key_indicators": ["Acting", "Lead"],
                "needs_manual_override": False,
            }
        return context  # No change


class TestHOP1Hybrid:
    def test_hybrid_override(self):
        """Test LLM override when heuristic confidence is low."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {"title": "Acting Lead", "name": "Test"})

        # Inject Mock LLM
        agent = HOP1ProfileAnalysisAgent(llm_client=MockLLM())

        # Force low confidence scenario by setting high threshold
        agent.config.profile_analysis_agent.manual_override_threshold = 0.8

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        traces = [t["type"] for t in registry.get_traces()]

        # Verify hybrid activation
        assert "REASONING_ACTIVATED" in traces
        assert "DECISION_OVERRIDE" in traces
        assert result["Archetype"] == "EXECUTIVE"  # Overridden by LLM
        assert result["confidence"] == 0.85
        assert result["needs_manual_override"] is False

    def test_heuristic_supremacy(self):
        """Test that clear titles skip LLM reasoning (efficiency)."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {"title": "CEO", "name": "Test"})

        # Inject Mock LLM (should not be called)
        agent = HOP1ProfileAnalysisAgent(llm_client=MockLLM())

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        traces = [t["type"] for t in registry.get_traces()]

        # Verify LLM was NOT activated (high confidence from heuristic)
        assert "REASONING_ACTIVATED" not in traces
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] == 0.95

    def test_graceful_degrade_no_llm(self):
        """Test agent functions in heuristic-only mode when LLM is None."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {"title": "Acting Lead", "name": "Test"})

        # No LLM client provided
        agent = HOP1ProfileAnalysisAgent(llm_client=None)

        # Force low confidence scenario
        agent.config.profile_analysis_agent.manual_override_threshold = 0.8

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        traces = [t["type"] for t in registry.get_traces()]

        # Verify LLM was NOT activated (no client available)
        assert "REASONING_ACTIVATED" not in traces
        # Should still complete successfully with heuristic result
        assert result["Archetype"] == "SENIOR_TA"  # Fallback from "lead" keyword
        assert result["needs_manual_override"] is True

    def test_llm_error_handling(self):
        """Test graceful handling of LLM errors."""

        class FailingLLM:
            def analyze(self, title, context):
                raise ValueError("LLM service unavailable")

        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {"title": "Acting Lead", "name": "Test"})

        agent = HOP1ProfileAnalysisAgent(llm_client=FailingLLM())
        agent.config.profile_analysis_agent.manual_override_threshold = 0.8

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        traces = [t["type"] for t in registry.get_traces()]

        # Verify error was traced
        assert "REASONING_ACTIVATED" in traces
        assert "REASONING_ERROR" in traces

        # Verify fallback to heuristic result
        assert result["Archetype"] == "SENIOR_TA"
        assert result["needs_manual_override"] is True

    def test_llm_lower_confidence_ignored(self):
        """Test that LLM result is ignored if confidence is lower than heuristic."""

        class WeakLLM:
            def analyze(self, title, context):
                return {
                    "archetype": "RECRUITER",
                    "confidence": 0.4,  # Lower than heuristic
                    "reasoning": "Weak LLM guess",
                    "key_indicators": [],
                    "needs_manual_override": True,
                }

        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        buffer.write_once("recipient_profile", {"title": "Unknown Title", "name": "Test"})

        agent = HOP1ProfileAnalysisAgent(llm_client=WeakLLM())
        agent.config.profile_analysis_agent.manual_override_threshold = 0.8

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        traces = [t["type"] for t in registry.get_traces()]

        # Verify LLM was activated but NOT used (confidence too low)
        assert "REASONING_ACTIVATED" in traces
        assert "DECISION_OVERRIDE" not in traces

        # Should keep heuristic result
        assert result["Archetype"] == agent.config.profile_analysis_agent.default_archetype
        assert result["confidence"] == agent.config.profile_analysis_agent.default_confidence
