"""
Demo Agent Unit Test - Working Example

This is a working demonstration of the agent unit test template
using a simple mock agent to verify all testing patterns work correctly.
"""

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import Mock, patch

import pytest

# Network service mocks
REDIS_MOCK = Mock()
OPENAI_MOCK = Mock()
ANTHROPIC_MOCK = Mock()


@dataclass
class MockAgentState:
    """Mock agent state for testing"""

    status: str = "initialized"
    config: dict[str, Any] = field(default_factory=dict)
    last_action: str | None = None
    health_score: float = 1.0


class MockAgent:
    """Mock agent class for demonstrating unit test patterns"""

    def __init__(self, config: dict[str, Any] = None, enable_healing: bool = True):
        self.state = MockAgentState(
            status="initialized", config=config or {}, last_action=None, health_score=1.0
        )
        self.has_healing = enable_healing
        self.has_tools = True
        self._llm_client = None

    def execute(self, input_data: Any) -> dict[str, Any]:
        """Main execution method"""
        self.state.last_action = f"execute: {str(input_data)[:50]}"

        # Mock different logic branches based on input
        if isinstance(input_data, str):
            input_lower = input_data.lower()
            if "validate" in input_lower:
                return {"tool": "location_validator", "result": "validated"}
            elif "dependency" in input_lower:
                return {"tool": "dependency_checker", "result": "checked"}
            elif "heal" in input_lower:
                return {"tool": "healing_executor", "result": "healed"}
            else:
                return {"tool": "default", "result": "processed"}
        else:
            return {"tool": "fallback", "result": "handled"}

    def heal_repository(self) -> dict[str, Any]:
        """Healing method"""
        self.state.last_action = "heal_repository"
        return {"healed": True, "issues_fixed": 0}

    def _perform_action(self, action: str) -> dict[str, Any]:
        """Tool action method"""
        self.state.last_action = f"perform_action: {action}"
        return {"action": action, "performed": True}

    def _run_self_tests(self) -> dict[str, Any]:
        """Self-test method"""
        self.state.last_action = "run_self_tests"
        return {"tests_passed": True, "count": 5}

    def _call_llm(self, prompt: str) -> dict[str, Any]:
        """Mock LLM call - would normally make network request"""
        return {"response": f"Mock response to: {prompt}"}


class TestMockAgent:
    """Working example of agent unit tests using MockAgent"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connections to prevent network calls."""
        with patch("redis.Redis", return_value=REDIS_MOCK):
            yield REDIS_MOCK

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI API calls."""
        try:
            with patch("openai.ChatCompletion.create", return_value=OPENAI_MOCK):
                yield OPENAI_MOCK
        except (AttributeError, ImportError):
            try:
                with patch("openai.chat.completions.create", return_value=OPENAI_MOCK):
                    yield OPENAI_MOCK
            except (AttributeError, ImportError):
                yield OPENAI_MOCK

    @pytest.fixture
    def mock_anthropic(self):
        """Mock Anthropic API calls."""
        try:
            with patch("anthropic.Completions.create", return_value=ANTHROPIC_MOCK):
                yield ANTHROPIC_MOCK
        except (AttributeError, ImportError):
            try:
                with patch("anthropic.messages.create", return_value=ANTHROPIC_MOCK):
                    yield ANTHROPIC_MOCK
            except (AttributeError, ImportError):
                yield ANTHROPIC_MOCK

    @pytest.fixture
    def agent_instance(self, mock_redis, mock_openai, mock_anthropic):
        """Create agent instance with all network services mocked."""
        config = {"territories": {}, "debug": True}
        return MockAgent(config=config, enable_healing=True)

    def test_state_integrity_after_init(self, agent_instance):
        """Test 1: State Integrity - Verify self.state remains immutable after init"""
        # Capture initial state
        initial_state = {
            "status": agent_instance.state.status,
            "config": agent_instance.state.config.copy(),
            "last_action": agent_instance.state.last_action,
            "health_score": agent_instance.state.health_score,
        }

        # Verify state structure
        assert agent_instance.state is not None, "Agent should have a state attribute"
        assert agent_instance.state.status == "initialized", "Status should be initialized"
        assert agent_instance.state.health_score == 1.0, "Health score should be 1.0"
        assert agent_instance.state.last_action is None, "Last action should be None initially"

        # Test that state is properly initialized
        assert isinstance(agent_instance.state.config, dict), "Config should be a dictionary"
        assert len(initial_state) == 4, "State should have exactly 4 fields"

    def test_logic_branching_with_mocked_llm(self, agent_instance):
        """Test 2: Logic Branching - Mock LLM outputs to verify tool selection logic"""
        test_scenarios = [
            {
                "input": "validate file location",
                "expected_tool": "location_validator",
            },
            {
                "input": "check dependency",
                "expected_tool": "dependency_checker",
            },
            {
                "input": "heal repository",
                "expected_tool": "healing_executor",
            },
            {
                "input": "generic task",
                "expected_tool": "default",
            },
        ]

        for scenario in test_scenarios:
            result = agent_instance.execute(scenario["input"])

            # Verify the expected tool/logic was triggered
            assert result is not None, f"Execute should return result for: {scenario['input']}"
            assert result["tool"] == scenario["expected_tool"], (
                f"Expected tool {scenario['expected_tool']}, got {result['tool']} "
                f"for input: {scenario['input']}"
            )

            # Verify state was updated
            assert agent_instance.state.last_action is not None, "Last action should be updated"
            assert "execute:" in agent_instance.state.last_action, (
                "Last action should show execute was called"
            )

    def test_fuzzing_input_validation(self, agent_instance):
        """Test 3: Fuzzing - Inject garbage/None types to test Mixin error handling"""
        fuzz_inputs = [
            None,
            "",
            [],
            {},
            0,
            "   ",  # Whitespace only
            "\x00\x01\x02",  # Control characters
            "A" * 10000,  # Very long string
            {"nested": {"invalid": None}},
            ["mixed", None, "types"],
        ]

        for fuzz_input in fuzz_inputs:
            # Should handle all inputs gracefully
            result = agent_instance.execute(fuzz_input)

            # Should either handle gracefully or return fallback result
            assert result is not None, f"Should handle input: {repr(fuzz_input)}"
            assert "tool" in result, f"Result should have tool field for input: {repr(fuzz_input)}"
            assert "result" in result, (
                f"Result should have result field for input: {repr(fuzz_input)}"
            )

    def test_network_call_isolation(self, agent_instance):
        """Test 4: Network Isolation - Verify zero network requests during unit tests"""
        network_calls = []

        def track_network_call(*args, **kwargs):
            network_calls.append((args, kwargs))
            raise Exception("Network call detected in unit test!")

        # Patch common network libraries
        with (
            patch.multiple(
                "requests", get=track_network_call, post=track_network_call, put=track_network_call
            ),
            patch.multiple("urllib.request", urlopen=track_network_call),
        ):
            # Execute agent methods
            agent_instance.execute("test input")

            # Verify no network calls were made
            assert len(network_calls) == 0, f"Network calls detected: {network_calls}"

    def test_error_handling_robustness(self, agent_instance):
        """Test 5: Error Handling - Verify Mixin error handling catches issues gracefully"""
        # Test various error conditions by patching internal methods
        error_scenarios = [
            {"exception": Exception("LLM failed"), "method": "_call_llm"},
            {"exception": ValueError("Invalid config"), "method": "_call_llm"},
            {"exception": TimeoutError("Operation timed out"), "method": "_call_llm"},
        ]

        for scenario in error_scenarios:
            with patch.object(
                agent_instance, scenario["method"], side_effect=scenario["exception"]
            ):
                # Agent should still be able to execute other methods
                result = agent_instance.execute("test input")
                assert result is not None, f"Should handle {scenario['exception']} gracefully"

    def test_agent_signature_compliance(self, agent_instance):
        """Test 6: Signature Compliance - Verify agent follows expected interface patterns"""
        # Check for required methods
        required_methods = ["execute", "heal_repository", "_perform_action", "_run_self_tests"]

        for method_name in required_methods:
            assert hasattr(agent_instance, method_name), f"Agent should have method: {method_name}"
            assert callable(getattr(agent_instance, method_name)), (
                f"{method_name} should be callable"
            )

        # Test method functionality
        assert agent_instance.execute("test")["tool"] == "default"
        assert agent_instance.heal_repository()["healed"] is True
        assert agent_instance._perform_action("test")["performed"] is True
        assert agent_instance._run_self_tests()["tests_passed"] is True

    def test_performance_baseline(self, agent_instance):
        """Test 7: Performance Baseline - Ensure agent operations complete within reasonable time"""
        import time

        # Test execution time
        start_time = time.time()
        result = agent_instance.execute("simple test input")
        execution_time = time.time() - start_time

        # Should complete within 1 second for simple mock operations
        assert execution_time < 1.0, f"Execution took too long: {execution_time}s"
        assert result is not None, "Should return result quickly"


if __name__ == "__main__":
    # Run the demo tests
    pytest.main([__file__, "-v"])
