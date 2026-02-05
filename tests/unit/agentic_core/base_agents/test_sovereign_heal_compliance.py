"""
test_sovereign_heal_compliance.py - Verify Interface Compliance.

Ensures SovereignBaseAgent and its subclasses satisfy the PreFlightValidator
requirements for the 'heal' method.
"""

from agentic_core.base_agents.sovereign_base_agent import SovereignBaseAgent


class TestSovereignHealCompliance:
    def test_base_agent_has_heal_method(self):
        """Verify the method exists on the base class."""
        agent = SovereignBaseAgent()
        assert hasattr(agent, "heal"), "SovereignBaseAgent missing 'heal' method"
        assert callable(agent.heal), "'heal' attribute is not callable"

    def test_heal_method_signature_compliance(self):
        """Verify the method accepts correct args and returns dict."""
        agent = SovereignBaseAgent()
        violation_mock = {"id": "V-101", "desc": "Test Violation"}

        # Should accept violation and kwargs
        result = agent.heal(violation_mock, extra_param=True)

        assert isinstance(result, dict), "heal() must return a dictionary"
        assert result["status"] == "skipped", "Default status should be 'skipped'"
        assert result["handler"] == "SovereignBaseAgent", "Handler should identify itself"
        assert result["violation_id"] == "V-101", "Should echo violation ID"

    def test_inheritance_propagation(self):
        """Verify subclasses inherit the default behavior."""

        class GenericWorkerAgent(SovereignBaseAgent):
            pass

        worker = GenericWorkerAgent()
        result = worker.heal({"id": "V-102"})

        assert result["status"] == "skipped"
        assert result["handler"] == "GenericWorkerAgent"  # Should identify subclass
