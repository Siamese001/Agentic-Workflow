"""Model router - Smart LLM selection based on task complexity.

This module optimizes cost and latency by dynamically selecting the appropriate
LLM based on task type, complexity, and budget constraints.
"""

import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ModelTier(str, Enum):
    """Model performance tiers."""

    FAST = "FAST"  # gpt-4o-mini, claude-3-haiku
    BALANCED = "BALANCED"  # gpt-4o, claude-3-5-sonnet
    REASONING = "REASONING"  # o1-preview, claude-3-opus


class TaskType(str, Enum):
    """Types of tasks that can be routed."""

    RESUME_FORMATTING = "RESUME_FORMATTING"
    MESSAGE_DRAFTING = "MESSAGE_DRAFTING"
    STRATEGIC_PLANNING = "STRATEGIC_PLANNING"
    CODE_GENERATION = "CODE_GENERATION"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    CONTENT_CREATION = "CONTENT_CREATION"
    TRANSLATION = "TRANSLATION"
    SUMMARIZATION = "SUMMARIZATION"
    QUESTION_ANSWERING = "QUESTION_ANSWERING"
    VALIDATION = "VALIDATION"


@dataclass
class ModelConfig:
    """configuration for a specific model."""

    provider: str  # openai, anthropic, etc.
    model_name: str
    tier: ModelTier
    max_tokens: int
    temperature: float
    cost_per_1k_tokens: float
    max_retries: int = 3
    timeout_seconds: int = 30


@dataclass
class TaskProfile:
    """Profile for a task type."""

    task_type: TaskType
    default_tier: ModelTier
    min_complexity: int = 1
    max_complexity: int = 10
    complexity_thresholds: dict[ModelTier, int] = field(default_factory=dict)
    config_overrides: dict[str, Any] = field(default_factory=dict)


class ModelRouter:
    """Routes tasks to appropriate models based on various factors."""

    def __init__(self, daily_budget: float = 5.0, budget_period_hours: int = 24):
        """Initialize model router.

        Args:
            daily_budget: Daily spend limit in USD
            budget_period_hours: Budget period in hours
        """
        self.daily_budget = daily_budget
        self.budget_period_hours = budget_period_hours

        # Model configurations
        self._models: dict[str, ModelConfig] = {}
        self._task_profiles: dict[TaskType, TaskProfile] = {}

        # Budget tracking
        self._budget_start = datetime.utcnow()
        self._current_spend = 0.0
        self._usage_history: list[dict[str, Any]] = []

        # Statistics
        self._stats = {
            "total_requests": 0,
            "requests_by_tier": {tier.value: 0 for tier in ModelTier},
            "requests_by_task": {task.value: 0 for task in TaskType},
            "fallbacks": 0,
            "budget_enforced": 0,
            "total_spend": 0.0,
        }

        # Initialize defaults
        self._initialize_defaults()

        logger.info(f"Initialized ModelRouter with budget ${daily_budget}/{budget_period_hours}h")

    def _initialize_defaults(self) -> None:
        """Initialize default model configurations and task profiles."""
        # Fast tier models
        self._models["gpt-4o-mini"] = ModelConfig(
            provider="openai",
            model_name="gpt-4o-mini",
            tier=ModelTier.FAST,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.00015,
        )

        self._models["claude-3-haiku"] = ModelConfig(
            provider="anthropic",
            model_name="claude-3-haiku-20240307",
            tier=ModelTier.FAST,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.00025,
        )

        # Balanced tier models
        self._models["gpt-4o"] = ModelConfig(
            provider="openai",
            model_name="gpt-4o",
            tier=ModelTier.BALANCED,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.005,
        )

        self._models["claude-3-5-sonnet"] = ModelConfig(
            provider="anthropic",
            model_name="claude-3-5-sonnet-20241022",
            tier=ModelTier.BALANCED,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.003,
        )

        # Reasoning tier models
        self._models["o1-preview"] = ModelConfig(
            provider="openai",
            model_name="o1-preview",
            tier=ModelTier.REASONING,
            max_tokens=32768,
            temperature=1.0,
            cost_per_1k_tokens=0.015,
        )

        self._models["claude-3-opus"] = ModelConfig(
            provider="anthropic",
            model_name="claude-3-opus-20240229",
            tier=ModelTier.REASONING,
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.015,
        )

        # Task profiles with complexity thresholds
        self._task_profiles[TaskType.RESUME_FORMATTING] = TaskProfile(
            task_type=TaskType.RESUME_FORMATTING,
            default_tier=ModelTier.FAST,
            complexity_thresholds={
                ModelTier.FAST: 3,
                ModelTier.BALANCED: 7,
                ModelTier.REASONING: 10,
            },
        )

        self._task_profiles[TaskType.MESSAGE_DRAFTING] = TaskProfile(
            task_type=TaskType.MESSAGE_DRAFTING,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={
                ModelTier.FAST: 2,
                ModelTier.BALANCED: 8,
                ModelTier.REASONING: 10,
            },
        )

        self._task_profiles[TaskType.STRATEGIC_PLANNING] = TaskProfile(
            task_type=TaskType.STRATEGIC_PLANNING,
            default_tier=ModelTier.REASONING,
            complexity_thresholds={
                ModelTier.FAST: 1,
                ModelTier.BALANCED: 5,
                ModelTier.REASONING: 8,
            },
        )

        self._task_profiles[TaskType.CODE_GENERATION] = TaskProfile(
            task_type=TaskType.CODE_GENERATION,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={
                ModelTier.FAST: 3,
                ModelTier.BALANCED: 7,
                ModelTier.REASONING: 10,
            },
        )

        self._task_profiles[TaskType.DATA_ANALYSIS] = TaskProfile(
            task_type=TaskType.DATA_ANALYSIS,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={
                ModelTier.FAST: 2,
                ModelTier.BALANCED: 6,
                ModelTier.REASONING: 9,
            },
        )

        self._task_profiles[TaskType.CONTENT_CREATION] = TaskProfile(
            task_type=TaskType.CONTENT_CREATION,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={
                ModelTier.FAST: 3,
                ModelTier.BALANCED: 7,
                ModelTier.REASONING: 10,
            },
        )

        self._task_profiles[TaskType.TRANSLATION] = TaskProfile(
            task_type=TaskType.TRANSLATION,
            default_tier=ModelTier.FAST,
            complexity_thresholds={
                ModelTier.FAST: 5,
                ModelTier.BALANCED: 8,
                ModelTier.REASONING: 10,
            },
        )

        self._task_profiles[TaskType.SUMMARIZATION] = TaskProfile(
            task_type=TaskType.SUMMARIZATION,
            default_tier=ModelTier.FAST,
            complexity_thresholds={
                ModelTier.FAST: 4,
                ModelTier.BALANCED: 8,
                ModelTier.REASONING: 10,
            },
        )

        self._task_profiles[TaskType.QUESTION_ANSWERING] = TaskProfile(
            task_type=TaskType.QUESTION_ANSWERING,
            default_tier=ModelTier.BALANCED,
            complexity_thresholds={
                ModelTier.FAST: 2,
                ModelTier.BALANCED: 6,
                ModelTier.REASONING: 9,
            },
        )

        self._task_profiles[TaskType.VALIDATION] = TaskProfile(
            task_type=TaskType.VALIDATION,
            default_tier=ModelTier.FAST,
            complexity_thresholds={
                ModelTier.FAST: 4,
                ModelTier.BALANCED: 8,
                ModelTier.REASONING: 10,
            },
        )

    def get_model_config(
        self, task_type: TaskType, complexity_score: int = 1, force_tier: ModelTier | None = None,
    ) -> dict[str, Any]:
        """Get model configuration for a task.

        Args:
            task_type: Type of task
            complexity_score: Task complexity (1-10)
            force_tier: Force specific tier

        Returns:
            Model configuration dictionary
        """
        # Get task profile
        profile = self._task_profiles.get(task_type)
        if not profile:
            raise ValueError(f"Unknown task type: {task_type}")

        # Determine tier
        if force_tier:
            tier = force_tier
        else:
            tier = self._determine_tier(profile, complexity_score)

        # Apply budget constraints
        tier = self._apply_budget_constraints(tier)

        # Select best model for tier
        model_config = self._select_model_for_tier(tier)

        # Build configuration
        config = {
            "provider": model_config.provider,
            "model": model_config.model_name,
            "tier": tier.value,
            "max_tokens": model_config.max_tokens,
            "temperature": model_config.temperature,
            "max_retries": model_config.max_retries,
            "timeout_seconds": model_config.timeout_seconds,
        }

        # Apply task-specific overrides
        config.update(profile.config_overrides)

        # Update stats
        self._stats["total_requests"] += 1
        self._stats["requests_by_tier"][tier.value] += 1
        self._stats["requests_by_task"][task_type.value] += 1

        return config

    def _determine_tier(self, profile: TaskProfile, complexity_score: int) -> ModelTier:
        """Determine model tier based on complexity.

        Args:
            profile: Task profile
            complexity_score: Complexity score

        Returns:
            Selected tier
        """
        thresholds = profile.complexity_thresholds

        # Check if complexity exceeds thresholds
        if complexity_score >= thresholds.get(ModelTier.REASONING, 10):
            return ModelTier.REASONING
        elif complexity_score >= thresholds.get(ModelTier.BALANCED, 7):
            return ModelTier.BALANCED
        else:
            return ModelTier.FAST

    def _apply_budget_constraints(self, tier: ModelTier) -> ModelTier:
        """Apply budget constraints to tier selection.

        Args:
            tier: Original tier selection

        Returns:
            Adjusted tier
        """
        # Check budget
        if self._is_budget_exceeded():
            # Force downgrade
            if tier == ModelTier.REASONING:
                self._stats["budget_enforced"] += 1
                return ModelTier.BALANCED
            elif tier == ModelTier.BALANCED:
                self._stats["budget_enforced"] += 1
                return ModelTier.FAST

        return tier

    def _select_model_for_tier(self, tier: ModelTier) -> ModelConfig:
        """Select the best model for a tier.

        Args:
            tier: Model tier

        Returns:
            Selected model configuration
        """
        # Get models for tier
        tier_models = [config for config in self._models.values() if config.tier == tier]

        if not tier_models:
            raise ValueError(f"No models available for tier: {tier}")

        # Select based on cost (cheapest first)
        return min(tier_models, key=lambda m: m.cost_per_1k_tokens)

    async def get_client(self, tier: ModelTier) -> "LLMClient":
        """Get LLM client for a tier with fallback.

        Args:
            tier: Model tier

        Returns:
            LLM client with fallback logic
        """
        model_config = self._select_model_for_tier(tier)

        # Create client with fallback wrapper
        return FallbackClient(model_config, self)

    def record_usage(
        self, model_name: str, input_tokens: int, output_tokens: int, cost: float,
    ) -> None:
        """Record model usage for budget tracking.

        Args:
            model_name: Model used
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost: Cost in USD
        """
        # Update spend
        self._current_spend += cost
        self._stats["total_spend"] += cost

        # Record usage
        usage = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
        }

        self._usage_history.append(usage)

        # Trim history
        if len(self._usage_history) > 1000:
            self._usage_history = self._usage_history[-1000:]

        # Check if need to reset budget period
        self._check_budget_period()

    def _is_budget_exceeded(self) -> bool:
        """Check if budget is exceeded.

        Returns:
            True if budget exceeded
        """
        return self._current_spend >= self.daily_budget

    def _check_budget_period(self) -> None:
        """Check and reset budget period if needed."""
        now = datetime.utcnow()
        elapsed = now - self._budget_start

        if elapsed >= timedelta(hours=self.budget_period_hours):
            # Reset budget
            self._budget_start = now
            self._current_spend = 0.0
            logger.info("Budget period reset")

    def get_stats(self) -> dict[str, Any]:
        """Get router statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()

        # Add budget info
        stats["budget_info"] = {
            "daily_budget": self.daily_budget,
            "current_spend": self._current_spend,
            "remaining": max(0, self.daily_budget - self._current_spend),
            "period_hours": self.budget_period_hours,
            "period_start": self._budget_start.isoformat(),
        }

        # Add model counts
        stats["available_models"] = {
            tier.value: len([m for m in self._models.values() if m.tier == tier])
            for tier in ModelTier
        }

        return stats

    def add_model(self, name: str, config: ModelConfig) -> None:
        """Add a new model configuration.

        Args:
            name: Model name
            config: Model configuration
        """
        self._models[name] = config
        logger.info(f"Added model {name} ({config.tier.value})")

    def add_task_profile(self, profile: TaskProfile) -> None:
        """Add a new task profile.

        Args:
            profile: Task profile
        """
        self._task_profiles[profile.task_type] = profile
        logger.info(f"Added task profile {profile.task_type.value}")


class FallbackClient:
    """LLM client with automatic fallback and retry logic."""

    def __init__(self, primary_config: ModelConfig, router: ModelRouter):
        """Initialize fallback client.

        Args:
            primary_config: Primary model configuration
            router: Model router instance
        """
        self.primary_config = primary_config
        self.router = router
        self._client_cache: dict[str, LLMClient] = {}

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text with fallback logic.

        Args:
            prompt: Generation prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        # Try primary model first
        try:
            client = await self._get_client(self.primary_config)
            result = await client.generate(prompt, **kwargs)

            # Record usage
            self._record_usage(client, prompt, result)

            return result

        except Exception as e:
            logger.warning(f"Primary model failed: {e}")

            # Try fallback to lower tier
            fallback_tier = self._get_fallback_tier(self.primary_config.tier)
            if fallback_tier:
                self.router._stats["fallbacks"] += 1

                try:
                    fallback_config = self.router._select_model_for_tier(fallback_tier)
                    client = await self._get_client(fallback_config)
                    result = await client.generate(prompt, **kwargs)

                    # Record usage
                    self._record_usage(client, prompt, result)

                    logger.info(f"Fallback to {fallback_config.model_name} succeeded")
                    return result

                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")

            # All attempts failed
            raise RuntimeError(f"All model attempts failed. Last error: {e}")

    async def _get_client(self, config: ModelConfig) -> "LLMClient":
        """Get or create LLM client.

        Args:
            config: Model configuration

        Returns:
            LLM client
        """
        cache_key = f"{config.provider}:{config.model_name}"

        if cache_key not in self._client_cache:
            # Create client based on provider
            if config.provider == "openai":
                client = OpenAIClient(config)
            elif config.provider == "anthropic":
                client = AnthropicClient(config)
            else:
                raise ValueError(f"Unknown provider: {config.provider}")

            self._client_cache[cache_key] = client

        return self._client_cache[cache_key]

    def _get_fallback_tier(self, current_tier: ModelTier) -> ModelTier | None:
        """Get fallback tier.

        Args:
            current_tier: Current tier

        Returns:
            Fallback tier or None
        """
        if current_tier == ModelTier.REASONING:
            return ModelTier.BALANCED
        elif current_tier == ModelTier.BALANCED:
            return ModelTier.FAST
        else:
            return None

    def _record_usage(self, client: "LLMClient", prompt: str, result: str) -> None:
        """Record usage for billing.

        Args:
            client: LLM client used
            prompt: Input prompt
            result: Generated result
        """
        # Estimate tokens (rough approximation)
        input_tokens = len(prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(result.split()) * 1.3

        # Calculate cost
        total_tokens = input_tokens + output_tokens
        cost = (total_tokens / 1000) * client.config.cost_per_1k_tokens

        # Record with router
        self.router.record_usage(
            client.config.model_name, int(input_tokens), int(output_tokens), cost,
        )


# Mock LLM client interfaces
class LLMClient(ABC):
    """Abstract base for LLM clients."""

    def __init__(self, config: ModelConfig):
        """Initialize client.

        Args:
            config: Model configuration
        """
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text.

        Args:
            prompt: Generation prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI client implementation."""

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Generation prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        # Mock implementation
        await asyncio.sleep(0.1)
        return f"OpenAI {self.config.model_name} response to: {prompt[:50]}..."


class AnthropicClient(LLMClient):
    """Anthropic client implementation."""

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic.

        Args:
            prompt: Generation prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        # Mock implementation
        await asyncio.sleep(0.1)
        return f"Anthropic {self.config.model_name} response to: {prompt[:50]}..."


# Global router
_model_router: ModelRouter | None = None
_router_lock = asyncio.Lock()


async def get_model_router() -> ModelRouter:
    """Get global model router instance.

    Returns:
        ModelRouter instance
    """
    global _model_router
    async with _router_lock:
        if _model_router is None:
            _model_router = ModelRouter()
    return _model_router


# Helper functions
async def route_and_generate(
    task_type: TaskType, prompt: str, complexity_score: int = 1, **kwargs,
) -> str:
    """Route task and generate response.

    Args:
        task_type: Type of task
        prompt: Generation prompt
        complexity_score: Task complexity
        **kwargs: Additional parameters

    Returns:
        Generated response
    """
    router = await get_model_router()

    # Get model configuration
    config = router.get_model_config(task_type, complexity_score)

    # Get client
    tier = ModelTier(config["tier"])
    client = await router.get_client(tier)

    # Generate
    return await client.generate(prompt, **kwargs)
