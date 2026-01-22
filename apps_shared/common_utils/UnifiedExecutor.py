"""Unified Executor - Shared execution module for all engines.

This module provides a unified execution system that both resume and outreach
engines can use, eliminating duplicate execution logic while maintaining
engine-specific optimizations.
"""

import asyncio
import json
import logging
import time
from datetime import datetime


logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RATE_LIMITED = "rate_limited"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ExecutionContext:
    """Context for execution operations."""

    engine_type: EngineType
    operation_id: str
    input_data: Any
    config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration(self) -> float | None:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class ExecutionResult:
    """Result of execution operation."""

    status: ExecutionStatus
    data: Any
    context: ExecutionContext
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "data": self.data,
            "operation_id": self.context.operation_id,
            "engine_type": self.context.engine_type.value,
            "duration": self.context.duration,
            "error": self.error,
            "metrics": self.metrics,
        }


class ExecutionStrategy(ABC):
    """Abstract base for execution strategies."""

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute the operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        pass

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get strategy name."""
        pass


class LLMExecutionStrategy(ExecutionStrategy):
    """Strategy for LLM-based execution."""

    def __init__(self, model_name: str = "default"):
        """Initialize LLM execution strategy.

        Args:
            model_name: Name of LLM model to use
        """
        self.model_name = model_name
        self.circuit_breaker = CircuitBreakerFactory.get_breaker(
            f"llm_{model_name}", failure_threshold=5, recovery_timeout=60
        )
        self.rate_limiter = get_rate_limiter("llm_calls", "10/minute")
        self.resource_manager = get_resource_manager()

    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute LLM operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()

        try:
            # Check rate limit
            if not self.rate_limiter.can_proceed():
                return ExecutionResult(
                    status=ExecutionStatus.RATE_LIMITED,
                    data=None,
                    context=context,
                    error="Rate limit exceeded",
                )

            # Execute with circuit breaker
            result = await self.circuit_breaker.call(self._execute_llm, context)

            # Update metrics
            metrics = {
                "llm_calls": 1,
                "tokens_used": self._estimate_tokens(context.input_data),
                "execution_time": time.time() - start_time,
            }

            return ExecutionResult(
                status=ExecutionStatus.COMPLETED, data=result, context=context, metrics=metrics
            )

        except CircuitOpenError:
            return ExecutionResult(
                status=ExecutionStatus.CIRCUIT_OPEN,
                data=None,
                context=context,
                error="Circuit breaker is open",
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, data=None, context=context, error=str(e)
            )

    async def _execute_llm(self, context: ExecutionContext) -> Any:
        """Execute actual LLM call.

        Args:
            context: Execution context

        Returns:
            LLM response
        """
        # Simulate LLM call
        await asyncio.sleep(0.5)

        # Process input based on engine type
        if context.engine_type == EngineType.RESUME:
            return self._process_resume_input(context.input_data)
        else:
            return self._process_outreach_input(context.input_data)

    def _process_resume_input(self, input_data: Any) -> str:
        """Process resume input.

        Args:
            input_data: Resume input

        Returns:
            Processed output
        """
        if isinstance(input_data, str):
            # Generate resume content
            return f"Generated resume content based on: {input_data[:100]}..."
        elif isinstance(input_data, dict):
            # Generate from structured data
            return f"Generated resume from {len(input_data)} sections"
        return "Generated resume content"

    def _process_outreach_input(self, input_data: Any) -> str:
        """Process outreach input.

        Args:
            input_data: Outreach input

        Returns:
            Processed output
        """
        if isinstance(input_data, str):
            # Generate outreach message
            return f"Generated outreach message for: {input_data[:100]}..."
        elif isinstance(input_data, dict):
            # Generate from structured data
            return f"Generated personalized message for {input_data.get('recipient', 'contact')}"
        return "Generated outreach message"

    def _estimate_tokens(self, input_data: Any) -> int:
        """Estimate token count.

        Args:
            input_data: Input data

        Returns:
            Estimated token count
        """
        text = json.dumps(input_data, default=str)
        return len(text.split()) * 1.3  # Rough estimate

    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return f"llm_{self.model_name}"


class APIExecutionStrategy(ExecutionStrategy):
    """Strategy for API-based execution."""

    def __init__(self, api_endpoint: str, timeout: float = 30.0):
        """Initialize API execution strategy.

        Args:
            api_endpoint: API endpoint URL
            timeout: Request timeout
        """
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.circuit_breaker = CircuitBreakerFactory.get_breaker(
            f"api_{api_endpoint}", failure_threshold=3, recovery_timeout=30
        )

    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute API operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()

        try:
            # Execute with circuit breaker
            result = await self.circuit_breaker.call(self._execute_api, context)

            metrics = {"api_calls": 1, "response_time": time.time() - start_time}

            return ExecutionResult(
                status=ExecutionStatus.COMPLETED, data=result, context=context, metrics=metrics
            )

        except CircuitOpenError:
            return ExecutionResult(
                status=ExecutionStatus.CIRCUIT_OPEN,
                data=None,
                context=context,
                error="API circuit breaker is open",
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, data=None, context=context, error=str(e)
            )

    async def _execute_api(self, context: ExecutionContext) -> Any:
        """Execute actual API call.

        Args:
            context: Execution context

        Returns:
            API response
        """
        # Simulate API call
        await asyncio.sleep(0.3)

        # Return mock response
        return {
            "status": "success",
            "data": f"API response for {context.engine_type.value}",
            "timestamp": datetime.now().isoformat(),
        }

    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return f"api_{self.api_endpoint}"


class BatchExecutionStrategy(ExecutionStrategy):
    """Strategy for batch execution."""

    def __init__(self, batch_size: int = 10, concurrency: int = 5):
        """Initialize batch execution strategy.

        Args:
            batch_size: Size of each batch
            concurrency: Maximum concurrent operations
        """
        self.batch_size = batch_size
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute batch operation.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()

        try:
            # Get input items
            items = (
                context.input_data if isinstance(context.input_data, list) else [context.input_data]
            )

            # Process in batches
            results = []
            for i in range(0, len(items), self.batch_size):
                batch = items[i : i + self.batch_size]
                batch_results = await asyncio.gather(
                    *[self._process_item(item, context) for item in batch], return_exceptions=True
                )
                results.extend(batch_results)

            metrics = {
                "items_processed": len(results),
                "batches_processed": len(range(0, len(items), self.batch_size)),
                "execution_time": time.time() - start_time,
            }

            return ExecutionResult(
                status=ExecutionStatus.COMPLETED, data=results, context=context, metrics=metrics
            )

        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, data=None, context=context, error=str(e)
            )

    async def _process_item(self, item: Any, context: ExecutionContext) -> Any:
        """Process a single item.

        Args:
            item: Item to process
            context: Execution context

        Returns:
            Processed item
        """
        async with self.semaphore:
            # Simulate processing
            await asyncio.sleep(0.1)

            if context.engine_type == EngineType.RESUME:
                return f"Processed resume item: {str(item)[:50]}"
            else:
                return f"Processed outreach item: {str(item)[:50]}"

    @property
    def strategy_name(self) -> str:
        """Get strategy name."""
        return f"batch_{self.batch_size}"


class UnifiedExecutor:
    """Unified executor for all engines."""

    def __init__(self):
        """Initialize the unified executor."""
        self.strategies = {
            "llm": LLMExecutionStrategy(),
            "api": APIExecutionStrategy("default"),
            "batch": BatchExecutionStrategy(),
        }

        # Statistics
        self._stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "strategy_usage": defaultdict(int),
        }

        logger.info("Initialized UnifiedExecutor")

    async def execute(
        self,
        input_data: Any,
        strategy: str,
        engine_type: EngineType,
        config: dict[str, Any] | None = None,
        operation_id: str | None = None,
    ) -> ExecutionResult:
        """Execute operation using specified strategy.

        Args:
            input_data: Input data
            strategy: Execution strategy
            engine_type: Type of engine
            config: Optional configuration
            operation_id: Optional operation ID

        Returns:
            Execution result
        """
        # Generate operation ID if not provided
        if not operation_id:
            operation_id = f"{engine_type.value}_{strategy}_{int(time.time())}"

        # Create execution context
        context = ExecutionContext(
            engine_type=engine_type,
            operation_id=operation_id,
            input_data=input_data,
            config=config or {},
            start_time=datetime.now(),
        )

        # Get strategy
        executor = self.strategies.get(strategy)
        if not executor:
            result = ExecutionResult(
                status=ExecutionStatus.FAILED,
                data=None,
                context=context,
                error=f"Unknown strategy: {strategy}",
            )
            return result

        # Update stats
        self._stats["total_executions"] += 1
        self._stats["strategy_usage"][strategy] += 1

        # Execute
        result = await executor.execute(context)
        context.end_time = datetime.now()

        # Update stats
        if result.status == ExecutionStatus.COMPLETED:
            self._stats["successful_executions"] += 1
        else:
            self._stats["failed_executions"] += 1

        return result

    def register_strategy(self, name: str, strategy: ExecutionStrategy) -> None:
        """Register a custom execution strategy.

        Args:
            name: Strategy name
            strategy: Execution strategy
        """
        self.strategies[name] = strategy
        logger.info(f"Registered custom strategy: {name}")

    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["total_executions"] > 0:
            stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
        else:
            stats["success_rate"] = 0.0
        return stats


class EngineExecutor:
    """Engine-specific executor with unified backend."""

    def __init__(self, engine_type: EngineType):
        """Initialize engine executor.

        Args:
            engine_type: Type of engine
        """
        self.engine_type = engine_type
        self.unified_executor = UnifiedExecutor()
        self.formatter = get_unified_formatter()
        self.shared_infra = get_shared_infrastructure()

        # Engine-specific configuration
        self.config = self._get_engine_config()

        logger.info(f"Initialized {engine_type.value} executor")

    async def generate_content(
        self, input_data: Any, content_type: str = "default", config: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """Generate content using unified executor.

        Args:
            input_data: Input data
            content_type: Type of content to generate
            config: Optional configuration

        Returns:
            Execution result
        """
        # Merge with engine config
        merged_config = {**self.config, **(config or {})}

        # Execute with LLM strategy
        result = await self.unified_executor.execute(
            input_data, "llm", self.engine_type, merged_config
        )

        # Format output if successful
        if result.status == ExecutionStatus.COMPLETED:
            format_type = self._get_format_type(content_type)
            formatted = self.formatter.format(
                result.data, format_type, self.engine_type, merged_config
            )
            result.data = formatted.data

        return result

    async def process_batch(
        self, items: list[Any], config: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """Process batch of items.

        Args:
            items: Items to process
            config: Optional configuration

        Returns:
            Execution result
        """
        return await self.unified_executor.execute(
            items, "batch", self.engine_type, config or self.config
        )

    def _get_engine_config(self) -> dict[str, Any]:
        """Get engine-specific configuration.

        Returns:
            Configuration dictionary
        """
        if self.engine_type == EngineType.RESUME:
            return {
                "max_length": 500,
                "ensure_metrics": True,
                "action_verbs": True,
                "format": "professional",
            }
        else:
            return {
                "max_length": 300,
                "personalization": True,
                "call_to_action": True,
                "format": "engaging",
            }

    def _get_format_type(self, content_type: str) -> str:
        """Get format type for content.

        Args:
            content_type: Content type

        Returns:
            Format type string
        """
        if self.engine_type == EngineType.RESUME:
            if content_type == "bullets":
                return "resume_bullet"
            elif content_type == "section":
                return "resume_section"
        else:
            if content_type == "message":
                return "outreach_message"
            elif content_type == "subject":
                return "outreach_subject"

        return "default"


# Global executor instances
_executors: dict[EngineType, EngineExecutor] = {}


def get_engine_executor(engine_type: EngineType) -> EngineExecutor:
    """Get engine executor instance.

    Args:
        engine_type: Type of engine

    Returns:
        EngineExecutor instance
    """
    if engine_type not in _executors:
        _executors[engine_type] = EngineExecutor(engine_type)
    return _executors[engine_type]


# Convenience functions
async def execute_resume_generation(
    input_data: Any, content_type: str = "default", config: dict[str, Any] | None = None
) -> ExecutionResult:
    """Execute resume generation.

    Args:
        input_data: Input data
        content_type: Type of content
        config: Optional configuration

    Returns:
        Execution result
    """
    executor = get_engine_executor(EngineType.RESUME)
    return await executor.generate_content(input_data, content_type, config)


async def execute_outreach_generation(
    input_data: Any, content_type: str = "message", config: dict[str, Any] | None = None
) -> ExecutionResult:
    """Execute outreach generation.

    Args:
        input_data: Input data
        content_type: Type of content
        config: Optional configuration

    Returns:
        Execution result
    """
    executor = get_engine_executor(EngineType.OUTREACH)
    return await executor.generate_content(input_data, content_type, config)