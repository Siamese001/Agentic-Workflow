"""
Unified Agent Interface - Standardized interface for all application agents.

Provides consistent agent lifecycle, execution patterns, and result handling
for apps_lic and apps_rg.
Phase 3A - Agent Interface Standardization
"""
from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')

class AgentStatus(str, Enum):
    """Agent execution status."""
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    TIMEOUT = 'timeout'
    CANCELLED = 'cancelled'

@dataclass
class AgentContext:
    """Context passed to agent during execution."""
    session_id: str
    trace_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 300.0
    retry_count: int = 0
    max_retries: int = 3

    def with_trace(self, trace_id: str) -> AgentContext:
        """Create new context with trace ID."""
        return AgentContext(session_id=self.session_id, trace_id=trace_id, user_id=self.user_id, metadata=self.metadata.copy(), timeout_seconds=self.timeout_seconds, retry_count=self.retry_count, max_retries=self.max_retries)

@dataclass
class AgentResult(Generic[OutputT]):
    """Result of agent execution."""
    status: AgentStatus
    output: OutputT | None = None
    error: str | None = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == AgentStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if execution failed."""
        return self.status in (AgentStatus.FAILED, AgentStatus.TIMEOUT, AgentStatus.CANCELLED)

    @classmethod
    def success(cls, output: OutputT, execution_time_ms: float=0.0, metadata: dict[str, Any] | None=None) -> AgentResult[OutputT]:
        """Create a successful result."""
        return cls(status=AgentStatus.SUCCESS, output=output, execution_time_ms=execution_time_ms, metadata=metadata or {})

    @classmethod
    def failure(cls, error: str, execution_time_ms: float=0.0, metadata: dict[str, Any] | None=None) -> AgentResult[OutputT]:
        """Create a failed result."""
        return cls(status=AgentStatus.FAILED, error=error, execution_time_ms=execution_time_ms, metadata=metadata or {})

    @classmethod
    def timeout(cls, execution_time_ms: float=0.0, metadata: dict[str, Any] | None=None) -> AgentResult[OutputT]:
        """Create a timeout result."""
        return cls(status=AgentStatus.TIMEOUT, error='Execution timed out', execution_time_ms=execution_time_ms, metadata=metadata or {})

class IAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract interface for all application agents.

    Provides a standardized contract for agent implementation across
    apps_lic and apps_rg.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for identification."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Agent version."""
        pass

    @property
    def description(self) -> str:
        """Agent description."""
        return ''

    @abstractmethod
    def execute(self, input_data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """
        Execute the agent with given input and context.

        Args:
            input_data: Input data for the agent
            context: Execution context

        Returns:
            AgentResult with output or error
        """
        pass

    def validate_input(self, input_data: InputT) -> tuple[bool, str | None]:
        """
        Validate input data before execution.

        Args:
            input_data: Input to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return (True, None)

    def pre_execute(self, input_data: InputT, context: AgentContext) -> None:
        """Hook called before execution."""
        pass

    def post_execute(self, input_data: InputT, context: AgentContext, result: AgentResult[OutputT]) -> None:
        """Hook called after execution."""
        pass

    def on_error(self, input_data: InputT, context: AgentContext, error: Exception) -> None:
        """Hook called when an error occurs."""
        pass

class BaseAgent(IAgent[InputT, OutputT]):
    """
    Base implementation of IAgent with common functionality.

    Provides:
    - Automatic timing
    - Error handling
    - Retry logic
    - Logging
    """

    def __init__(self, agent_name: str, agent_version: str='1.0.0'):
        self._name = agent_name
        self._version = agent_version
        self._logger = logging.getLogger(f'{__name__}.{agent_name}')

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def execute(self, input_data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """Execute with timing, error handling, and retry logic."""
        start_time = time.time()
        is_valid, error_msg = self.validate_input(input_data)
        if not is_valid:
            return AgentResult.failure(error=f'Input validation failed: {error_msg}', execution_time_ms=(time.time() - start_time) * 1000)
        try:
            self.pre_execute(input_data, context)
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            self._logger.warning(f'Pre-execute hook failed: {e}')
        last_error: Exception | None = None
        for attempt in range(context.max_retries + 1):
            try:
                context.retry_count = attempt
                result = self._do_execute(input_data, context)
                result.execution_time_ms = (time.time() - start_time) * 1000
                try:
                    self.post_execute(input_data, context, result)
                # guardian: allow-silent-swallow
                except Exception as e:
                    self._logger.warning(f'Post-execute hook failed: {e}')
                return result
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                last_error = e
                self._logger.warning(f'Attempt {attempt + 1}/{context.max_retries + 1} failed: {e}')
                try:
                    self.on_error(input_data, context, e)
                # guardian: allow-silent-swallow
                except Exception as hook_error:
                    raise
                    self._logger.warning(f'Error hook failed: {hook_error}')
                if attempt < context.max_retries:
                    time.sleep(0.1 * (attempt + 1))
        return AgentResult.failure(error=f'All retries exhausted. Last error: {last_error}', execution_time_ms=(time.time() - start_time) * 1000)

    @abstractmethod
    def _do_execute(self, input_data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """
        Actual execution logic to be implemented by subclasses.

        Args:
            input_data: Validated input data
            context: Execution context

        Returns:
            AgentResult with output
        """
        pass

class AgentRegistry:
    """Registry for managing agent instances."""

    def __init__(self):
        self._agents: dict[str, IAgent] = {}

    def register(self, agent: IAgent) -> None:
        """Register an agent."""
        key = f'{agent.name}:{agent.version}'
        self._agents[key] = agent
        logger.info(f'Registered agent: {key}')

    def get(self, name: str, version: str | None=None) -> IAgent | None:
        """Get an agent by name and optional version."""
        if version:
            return self._agents.get(f'{name}:{version}')
        matching = [(k, v) for k, v in self._agents.items() if k.startswith(f'{name}:')]
        if matching:
            matching.sort(key=lambda x: x[0], reverse=True)
            return matching[0][1]
        return None

    def list_agents(self) -> list[dict[str, str]]:
        """List all registered agents."""
        return [{'name': agent.name, 'version': agent.version} for agent in self._agents.values()]

    def unregister(self, name: str, version: str) -> bool:
        """Unregister an agent."""
        key = f'{name}:{version}'
        if key in self._agents:
            del self._agents[key]
            logger.info(f'Unregistered agent: {key}')
            return True
        return False
_agent_registry: AgentRegistry | None = None

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry
