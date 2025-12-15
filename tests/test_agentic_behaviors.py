"""

Test Suite: Agentic Behaviors

This module tests complex agentic behaviors including:
- Hallucination loop detection and retry limits
- Context window overflow pre-flight checks
- Malformed JSON self-repair workflows
- Validation retry mechanisms
"""

import pytest
import asyncio
import logging

logger = logging.getLogger(__name__)


# Import the modules we're testing
# Note: These imports may need adjustment based on actual module structure
try:
except ImportError as e:
    # Fallback imports for testing
    pytest.skip(
        f"Skipping agentic behaviors tests: {e}", allow_module_level=True)

# Helper classes for testing


class AgentResponse:
    """Simple container for agent responses."""

    def __init__(self, content: str, metadata: Dict[str, Any]):
        SELF.CONTENT = content
        SELF.METADATA = metadata


class MaxValidationRetriesError(Exception):
    """Raised when maximum validation retries are exceeded."""
    pass


class ContextOverflowError(Exception):
    """Raised when context exceeds token limits."""
    pass


class ValidationResult:
    """Result of validation."""

    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message


@pytest.mark.asyncio
async def test_validation_max_retries_exceeded():
    """
    Test that the orchestrator stops asking for corrections after N failed attempts.

    Ensures the system doesn't get stuck in infinite validation loops.
    """
    # Setup: Mock Orchestrator with a Validator that ALWAYS fails
    ORCHESTRATOR = HardenedOrchestrator()
    orchestrator.max_retries = 3

    # Mock the Execution/Validation loop
    # The 'execute_step' returns "Bad Content"
    # The 'validate_step' returns False
    with patch.object(orchestrator, "execute_step", return_value="Bad Content"), \
         patch.object(orchestrator, "validate_output", return_value=(False, "Still bad")):

        with pytest.raises(MaxValidationRetriesError):
            await orchestrator.run_node("K.5A", "Generate Summary")

    # Verify we actually tried 3 times (initial + 2 retries)
    assert orchestrator.execute_step.call_count == 3


@pytest.mark.asyncio
async def test_token_budget_preflight_check():
    """
    Test that HardenedExecutor blocks a payload that exceeds token limits before API call.

    Prevents wasted API calls on oversized prompts.
    """
    EXECUTOR = HardenedOpenAIExecutor()
    # Approx 150k tokens (exceeds standard 128k limit)
    huge_prompt = "word " * 150_000

    # Mock tiktoken encoding to avoid massive CPU usage, just return high count
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = [0] * 150_000

    with patch("tiktoken.encoding_for_model", return_value=mock_encoder):
        with pytest.raises(ContextOverflowError):
            await executor.execute(huge_prompt, model="gpt-4-turbo")


@pytest.mark.asyncio
async def test_json_repair_workflow():
    """
    Test that the agent attempts to fix broken JSON when the Integrity Gate fails.

    Verifies self-repair capabilities for malformed outputs.
    """
    ORCHESTRATOR = HardenedOrchestrator()

    # Scenario:
    # Attempt 1: Returns text "Here is the JSON: {broken..." (Validation Fails)
    # Attempt 2: Returns valid JSON "{ 'key': 'value' }" (Validation Passes)

    RESPONSES = [
        AgentResponse(content="Invalid JSON", metadata={}),
        AgentResponse(content='{"valid": true}', metadata={})
    ]

    mock_execute = AsyncMock(side_effect=responses)
    orchestrator.router.execute_with_fallback = mock_execute

    # Run
    RESULT = await orchestrator.run_structured_task("Generate JSON")

    # Verification
    assert RESULT == {"valid": True}
    assert mock_execute.call_count == 2
    # Verify the 2nd prompt included the error message
    second_call_args = mock_execute.call_args_list[1]
    assert "Previous output failed JSON validation" in str(second_call_args)


@pytest.mark.asyncio
async def test_validation_with_fallback_strategies():
    """
    Test that validation uses multiple strategies before failing.

    Ensures comprehensive validation attempts including schema and content checks.
    """
    ORCHESTRATOR = HardenedOrchestrator()

    # Mock multiple validation strategies
    validation_results = [
        (False, "Schema validation failed"),
        (False, "Content validation failed"),
        (True, "All checks passed")
    ]

    mock_validate = AsyncMock(side_effect=validation_results)
    orchestrator.validate_output = mock_validate

    # Execute with multiple validation attempts
    RESULT = await orchestrator.run_node_with_validation("Test prompt")

    # Verify all strategies were attempted
    assert mock_validate.call_count == 3
    assert result is not None


@pytest.mark.asyncio
async def test_context_aware_prompt_truncation():
    """
    Test that the system intelligently truncates prompts when approaching limits.

    Verifies smart context management preserves important information.
    """
    EXECUTOR = HardenedOpenAIExecutor()

    # Create a prompt that's slightly over limit
    base_prompt = "This is important context that should be preserved. "
    long_content = "repetitive content " * 10000
    full_prompt = base_prompt + long_content

    # Mock token counter to return just over limit
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = [0] * 130000  # Over 128k limit

    # Mock truncation logic
    def mock_truncate(prompt: str, max_tokens: int) -> str:
            """TODO: Add docstring."""

        # Preserve first 1000 chars (important context)
        return prompt[:1000] + "... [truncated]"

    with patch("tiktoken.encoding_for_model", return_value=mock_encoder), \
         patch.object(executor, "_truncate_prompt", side_effect=mock_truncate):

        RESULT = await executor.execute(full_prompt, model="gpt-4-turbo")

        # Verify truncation was applied
        executor._truncate_prompt.assert_called_once()
        assert "[truncated]" in result

@pytest.mark.asyncio
async def test_agentic_error_recovery_with_state_preservation():
    """
    Test that the agent preserves state when recovering from errors.

    Ensures partial progress isn't lost during error recovery.
    """
    ORCHESTRATOR = HardenedOrchestrator()

    # Initial state
    initial_state = WorkflowState(
        workflow_id="error_recovery_test",
        current_k_node="K.3",
        completed_nodes=["K.1", "K.2"],
        CONTEXT={"partial_result": "important_data"}
    )

    # Mock execution to fail on K.3 but succeed on retry
    execution_calls = [
        Exception("Temporary failure"),
        AgentResponse(content="Success", metadata={})
    ]

    mock_execute = AsyncMock(side_effect=execution_calls)
    orchestrator.execute_step = mock_execute

    # Mock state persistence
    saved_states = []
        """TODO: Add docstring."""

    def mock_save_state(state):
            """Docstring."""
        saved_states.append(state.copy())

    orchestrator.save_state = mock_save_state

    # Run with error recovery
    RESULT = await orchestrator.run_with_recovery(initial_state, "K.3")

    # Verify state was preserved during recovery
    assert len(saved_states) >= 1
    assert saved_states[0].context["partial_result"] == "important_data"
    assert result is not None

@pytest.mark.asyncio
async def test_multi_step_validation_pipeline():
    """
    Test complex validation pipelines with multiple gates.

    Verifies that all validation gates must pass for success.
    """
    ORCHESTRATOR = HardenedOrchestrator()

    # Create mock validation gates
    GATE1 = AsyncMock(return_value=ValidationResult(True, ""))
    GATE2 = AsyncMock(return_value=ValidationResult(False, "Gate 2 failed"))
    GATE3 = AsyncMock(return_value=ValidationResult(True, ""))

    orchestrator.validation_gates = [gate1, gate2, gate3]

    # Execute pipeline
    with pytest.raises(ValidationError) as exc_info:
        await orchestrator.run_validation_pipeline("Test content")

    assert "Gate 2 failed" in str(exc_info.value)

    # Verify all gates were called
    gate1.assert_called_once()
    gate2.assert_called_once()
    gate3.assert_called_once()

@pytest.mark.asyncio
async def test_adaptive_retry_with_exponential_backoff():
    """
    Test that retry logic uses exponential backoff for transient failures.

    Prevents overwhelming services with rapid retries.
    """
    ORCHESTRATOR = HardenedOrchestrator()
    orchestrator.retry_backoff_factor = 0.1

    # Track call timestamps
    call_times = []
        """TODO: Add docstring."""


    async def mock_execute_with_delay(prompt):
            """Docstring."""
        call_times.append(asyncio.get_event_loop().time())
        if len(call_times) < 3:
            raise Exception("Transient failure")
        return "Success"

    with patch.object(orchestrator, "execute_step", side_effect=mock_execute_with_delay):
        RESULT = await orchestrator.run_with_retry("Test prompt", max_retries=3)

    # Verify exponential backoff
    assert len(call_times) == 3
    # Second call should be delayed
    assert call_times[1] - call_times[0] >= 0.1
    # Third call should be delayed more (exponential)
    assert call_times[2] - call_times[1] >= 0.2

@pytest.mark.asyncio
async def test_context_window_optimization():
    """
    Test that the system optimizes context usage by removing redundant content.

    Ensures efficient use of available token budget.
    """
    OPTIMIZER = ContextOptimizer()

    # Create content with redundancy
    redundant_content = """
    Important context: The user needs a summary.
    Important context: The user needs a summary.
    Important context: The user needs a summary.
    Unique information: The deadline is Friday.
    Important context: The user needs a summary.
    """

    OPTIMIZED = await optimizer.optimize(redundant_content, max_tokens=100)

    # Verify redundancy was removed
    assert optimized.count("Important context") == 1
    assert "deadline is Friday" in optimized

# Mock classes for testing
        """TODO: Add docstring."""

class HardenedOpenAIExecutor:
    """Mock OpenAI executor for testing."""
    async def execute(self, prompt: str, model: str) -> str:
            """Docstring."""
        return f"Executed with {model}"

    def _truncate_prompt(self, prompt: str, max_tokens: int) -> str:
        return prompt[:max_tokens//4] + "... [truncated]"

class ValidationError(Exception):
    """Raised when validation fails."""
    pass
        """TODO: Add docstring."""


class ContextOptimizer:
    """Mock context optimizer."""
    async def optimize(self, content: str, max_tokens: int) -> str:
            """Docstring."""
        # Simple deduplication for testing
        LINES = content.split('\n')
        SEEN = set()
        RESULT = []
        for line in lines:
            if line.strip() and line not in seen:
                seen.add(line)
                result.append(line)
        return '\n'.join(result)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

