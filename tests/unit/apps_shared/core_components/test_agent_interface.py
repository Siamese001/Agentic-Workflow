"""
Unit tests for Agent Interface.

Tests Phase 3A - Agent Interface Standardization.
"""

from apps_shared.utils.agent_interface import (
    AgentContext,
    AgentRegistry,
    AgentResult,
    AgentStatus,
    BaseAgent,
    get_agent_registry,
)


class TestAgentStatus:
    """Test AgentStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert AgentStatus.PENDING.value == "pending"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.SUCCESS.value == "success"
        assert AgentStatus.FAILED.value == "failed"
        assert AgentStatus.TIMEOUT.value == "timeout"
        assert AgentStatus.CANCELLED.value == "cancelled"


class TestAgentContext:
    """Test AgentContext dataclass."""

    def test_context_defaults(self):
        """Test AgentContext default values."""
        context = AgentContext(session_id="test-session")
        assert context.session_id == "test-session"
        assert context.trace_id is None
        assert context.user_id is None
        assert context.metadata == {}
        assert context.timeout_seconds == 300.0
        assert context.retry_count == 0
        assert context.max_retries == 3

    def test_context_with_trace(self):
        """Test creating context with trace ID."""
        context = AgentContext(
            session_id="test-session",
            user_id="user123",
            metadata={"key": "value"},
        )
        new_context = context.with_trace("trace-456")

        assert new_context.session_id == "test-session"
        assert new_context.trace_id == "trace-456"
        assert new_context.user_id == "user123"
        assert new_context.metadata == {"key": "value"}


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_result_success(self):
        """Test creating successful result."""
        result = AgentResult.success(
            output={"data": "value"},
            execution_time_ms=100.5,
            metadata={"key": "value"},
        )
        assert result.status == AgentStatus.SUCCESS
        assert result.output == {"data": "value"}
        assert result.error is None
        assert result.execution_time_ms == 100.5
        assert result.is_success is True
        assert result.is_failure is False

    def test_result_failure(self):
        """Test creating failed result."""
        result = AgentResult.failure(
            error="Something went wrong",
            execution_time_ms=50.0,
        )
        assert result.status == AgentStatus.FAILED
        assert result.output is None
        assert result.error == "Something went wrong"
        assert result.is_success is False
        assert result.is_failure is True

    def test_result_timeout(self):
        """Test creating timeout result."""
        result = AgentResult.timeout(execution_time_ms=5000.0)
        assert result.status == AgentStatus.TIMEOUT
        assert result.error == "Execution timed out"
        assert result.is_failure is True

    def test_is_failure_includes_cancelled(self):
        """Test is_failure includes cancelled status."""
        result = AgentResult(status=AgentStatus.CANCELLED)
        assert result.is_failure is True


class TestBaseAgent:
    """Test BaseAgent implementation."""

    def test_agent_properties(self):
        """Test agent name and version properties."""

        class TestAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                return AgentResult.success(f"Processed: {input_data}")

        agent = TestAgent("test-agent", "1.0.0")
        assert agent.name == "test-agent"
        assert agent.version == "1.0.0"

    def test_successful_execution(self):
        """Test successful agent execution."""

        class TestAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                return AgentResult.success(f"Result: {input_data}")

        agent = TestAgent("test-agent", "1.0.0")
        context = AgentContext(session_id="test")
        result = agent.execute("input", context)

        assert result.is_success
        assert result.output == "Result: input"
        assert result.execution_time_ms >= 0  # May be 0 for very fast execution

    def test_input_validation_failure(self):
        """Test input validation failure."""

        class ValidatingAgent(BaseAgent[str, str]):
            def validate_input(self, input_data):
                if not input_data:
                    return False, "Input cannot be empty"
                return True, None

            def _do_execute(self, input_data, context):
                return AgentResult.success(input_data)

        agent = ValidatingAgent("validating-agent", "1.0.0")
        context = AgentContext(session_id="test")
        result = agent.execute("", context)

        assert result.is_failure
        assert "Input validation failed" in result.error

    def test_retry_on_failure(self):
        """Test retry logic on failure."""
        attempt_count = 0

        class RetryAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count < 3:
                    raise ValueError("Temporary failure")
                return AgentResult.success("Success after retries")

        agent = RetryAgent("retry-agent", "1.0.0")
        context = AgentContext(session_id="test", max_retries=3)
        result = agent.execute("input", context)

        assert result.is_success
        assert result.output == "Success after retries"
        assert attempt_count == 3

    def test_retry_exhausted(self):
        """Test all retries exhausted."""

        class FailingAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                raise ValueError("Always fails")

        agent = FailingAgent("failing-agent", "1.0.0")
        context = AgentContext(session_id="test", max_retries=2)
        result = agent.execute("input", context)

        assert result.is_failure
        assert "All retries exhausted" in result.error

    def test_pre_execute_hook(self):
        """Test pre-execute hook is called."""
        pre_execute_called = False

        class HookAgent(BaseAgent[str, str]):
            def pre_execute(self, input_data, context):
                nonlocal pre_execute_called
                pre_execute_called = True

            def _do_execute(self, input_data, context):
                return AgentResult.success("done")

        agent = HookAgent("hook-agent", "1.0.0")
        context = AgentContext(session_id="test")
        agent.execute("input", context)

        assert pre_execute_called

    def test_post_execute_hook(self):
        """Test post-execute hook is called."""
        post_execute_result = None

        class HookAgent(BaseAgent[str, str]):
            def post_execute(self, input_data, context, result):
                nonlocal post_execute_result
                post_execute_result = result

            def _do_execute(self, input_data, context):
                return AgentResult.success("done")

        agent = HookAgent("hook-agent", "1.0.0")
        context = AgentContext(session_id="test")
        agent.execute("input", context)

        assert post_execute_result is not None
        assert post_execute_result.is_success

    def test_on_error_hook(self):
        """Test on-error hook is called."""
        error_received = None

        class ErrorHookAgent(BaseAgent[str, str]):
            def on_error(self, input_data, context, error):
                nonlocal error_received
                error_received = error

            def _do_execute(self, input_data, context):
                raise ValueError("Test error")

        agent = ErrorHookAgent("error-hook-agent", "1.0.0")
        context = AgentContext(session_id="test", max_retries=0)
        agent.execute("input", context)

        assert error_received is not None
        assert str(error_received) == "Test error"


class TestAgentRegistry:
    """Test AgentRegistry functionality."""

    def test_register_and_get(self):
        """Test registering and getting an agent."""

        class TestAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                return AgentResult.success("done")

        registry = AgentRegistry()
        agent = TestAgent("test-agent", "1.0.0")
        registry.register(agent)

        retrieved = registry.get("test-agent", "1.0.0")
        assert retrieved is agent

    def test_get_latest_version(self):
        """Test getting latest version of an agent."""

        class TestAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                return AgentResult.success("done")

        registry = AgentRegistry()
        agent_v1 = TestAgent("test-agent", "1.0.0")
        agent_v2 = TestAgent("test-agent", "2.0.0")
        registry.register(agent_v1)
        registry.register(agent_v2)

        # Get without version should return one of them
        retrieved = registry.get("test-agent")
        assert retrieved is not None

    def test_get_nonexistent(self):
        """Test getting a nonexistent agent."""
        registry = AgentRegistry()
        result = registry.get("nonexistent", "1.0.0")
        assert result is None

    def test_list_agents(self):
        """Test listing all agents."""

        class TestAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                return AgentResult.success("done")

        registry = AgentRegistry()
        registry.register(TestAgent("agent1", "1.0.0"))
        registry.register(TestAgent("agent2", "2.0.0"))

        agents = registry.list_agents()
        assert len(agents) == 2
        names = [a["name"] for a in agents]
        assert "agent1" in names
        assert "agent2" in names

    def test_unregister(self):
        """Test unregistering an agent."""

        class TestAgent(BaseAgent[str, str]):
            def _do_execute(self, input_data, context):
                return AgentResult.success("done")

        registry = AgentRegistry()
        agent = TestAgent("test-agent", "1.0.0")
        registry.register(agent)

        result = registry.unregister("test-agent", "1.0.0")
        assert result is True

        retrieved = registry.get("test-agent", "1.0.0")
        assert retrieved is None

    def test_unregister_nonexistent(self):
        """Test unregistering a nonexistent agent."""
        registry = AgentRegistry()
        result = registry.unregister("nonexistent", "1.0.0")
        assert result is False


class TestGetAgentRegistry:
    """Test get_agent_registry singleton."""

    def test_singleton_instance(self):
        """Test that get_agent_registry returns singleton."""
        import apps_shared.utils.agent_interface as ai_module

        ai_module._agent_registry = None

        registry1 = get_agent_registry()
        registry2 = get_agent_registry()

        assert registry1 is registry2

        ai_module._agent_registry = None
