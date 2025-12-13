"""
Node Executor - Pipeline-based execution with schema validation, constraints, telemetry, and routing.

Implements a clean pipeline pattern:
1. Model Router selects appropriate LLM
2. Telemetry wraps execution for observability
3. Constraints inject governance into prompts
4. Schema validates and enforces output structure
"""

import logging
import time
import asyncio
import json
from typing import Dict, Any, Optional, Type, List, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ComputeTier(Enum):
    """Compute tiers for model selection."""
    TIER_1_REASONING = "TIER_1_REASONING"  # High intelligence, high cost
    TIER_2_BALANCED = "TIER_2_BALANCED"      # Good balance
    TIER_3_SPEED = "TIER_3_SPEED"           # Fast, cheap

@dataclass
class NodeExecutionContext:
    """Context object that flows through the execution pipeline."""
    node_id: str
    node_config: Dict[str, Any]
    input_data: Dict[str, Any]
    session_id: str = field(default="")

    # Runtime state
    telemetry_span: Optional[Any] = field(default=None)
    selected_model: Optional[str] = field(default=None)
    actual_cost_usd: float = field(default=0.0)
    execution_time_ms: float = field(default=0.0)

    # Results
    raw_output: Optional[str] = field(default=None)
    validated_output: Optional[BaseModel] = field(default=None)
    errors: List[str] = field(default_factory=list)

class SchemaEnforcement:
    """Handles Pydantic schema validation for node outputs."""

    def __init__(self, schema_registry: Dict[str, Type[BaseModel]]):
        """Initialize with schema registry.

        Args:
            schema_registry: Mapping from model names to Pydantic classes
        """
        self.schema_registry = schema_registry
        self.logger = logging.getLogger("SchemaEnforcement")

    def validate_output(
        self,
        context: NodeExecutionContext,
        raw_output: str
    ) -> BaseModel:
        """Validate raw output against schema.

        Args:
            context: Execution context
            raw_output: Raw LLM output

        Returns:
            Validated Pydantic model

        Raises:
            ValidationError: If output doesn't match schema
        """
        schema_config = context.node_config.get("schema_enforcement", {})

        if not schema_config.get("enabled", False):
            # No schema enforcement, return raw output
            class RawOutput(BaseModel):
                """TODO: Add docstring."""

                content: str = raw_output
            return RawOutput(content=raw_output)

        model_name = schema_config.get("pydantic_model")
        if not model_name:
            raise ValueError("Schema enforcement enabled but no pydantic_model specified")

        model_class = self.schema_registry.get(model_name)
        if not model_class:
            raise ValueError(f"Unknown Pydantic model: {model_name}")

        # Parse JSON if needed
        try:
            if raw_output.startswith("```json"):
                raw_output = raw_output.replace("```json", "").replace("```", "").strip()

            parsed_output = json.loads(raw_output) if isinstance(raw_output, str) else raw_output

        except json.JSONDecodeError as e:
            raise ValidationError(f"Output is not valid JSON: {e}")

        # Validate against Pydantic model
        max_retries = schema_config.get("validation_retries", 3)

        for attempt in range(max_retries):
            try:
                validated = model_class.model_validate(parsed_output)
                self.logger.info(f"Schema validation successful for {model_name}")
                return validated

            except ValidationError as e:
                if attempt == max_retries - 1:
                    raise ValidationError(f"Schema validation failed after {max_retries} attempts: {e}")

                self.logger.warning(f"Validation attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(0.1)  # Brief delay before retry

        raise ValidationError(f"Schema validation failed for {model_name}")

class CognitiveConstraints:
    """Handles negative constraints and governance policies."""

    def build_constraint_block(self, node_config: Dict[str, Any]) -> str:
        """Build governance barrier from constraints.

        Args:
            node_config: Node configuration

        Returns:
            Formatted constraint block string
        """
        constraints = node_config.get("negative_constraints", {})

        if not constraints:
            return ""

        constraint_block = "\n\n<GOVERNANCE_BARRIER>\n"
        constraint_block += "CRITICAL NEGATIVE CONSTRAINTS (VIOLATION = FAILURE):\n"

        category_descriptions = {
            "syntax_forbidden": "Syntax Rules:",
            "style_forbidden": "Style Rules:",
            "hallucination_guard": "Truthfulness Rules:",
            "content_forbidden": "Content Restrictions:"
        }

        for category, rules in constraints.items():
            if rules and isinstance(rules, list):
                constraint_block += f"\n{category_descriptions.get(category,
                    category.title() + ':')}\n"
                for rule in rules:
                    constraint_block += f"  - {rule}\n"

        constraint_block += "</GOVERNANCE_BARRIER>"

        return constraint_block

    def apply_constraints_to_prompt(
        self,
        base_prompt: str,
        node_config: Dict[str, Any]
    ) -> str:
        """Apply constraints to system prompt.

        Args:
            base_prompt: Base system prompt
            node_config: Node configuration

        Returns:
            Prompt with constraints appended
        """
        constraint_block = self.build_constraint_block(node_config)
        return base_prompt + constraint_block

class CognitiveTelemetry:
    """Handles telemetry and observability for cognitive operations."""

    def __init__(self, provider: str = "langsmith", config: Optional[Dict] = None):
        """Initialize telemetry provider.

        Args:
            provider: Telemetry provider (langsmith, custom, etc.)
            config: Telemetry configuration
        """
        self.provider = provider
        self.config = config or {}
        self.logger = logging.getLogger("CognitiveTelemetry")

        # Initialize tracer based on provider
        self.tracer = self._initialize_tracer()

    def _initialize_tracer(self):
        """Initialize the appropriate tracer."""
        if self.provider == "langsmith":
            try:
                from langsmith import Client
                return Client()
            except ImportError:
                self.logger.warning("LangSmith not available, using mock tracer")
                return MockTracer()
        else:
            return MockTracer()

    def start_span(self, context: NodeExecutionContext):
        """Start a telemetry span for the node.

        Args:
            context: Execution context
        """
        span_name = f"node_{context.node_id}"
        context.telemetry_span = self.tracer.start_span(span_name)

        # Apply tagging rules
        tagging_rules = self.config.get("span_tagging_rules", {})

        if "k_node" in tagging_rules:
            context.telemetry_span.set_tag("k_node", context.node_id)

        if "session_id" in tagging_rules:
            context.telemetry_span.set_tag("session_id", context.session_id)

        if "model_version" in tagging_rules:
            context.telemetry_span.set_tag("model_version", context.selected_model)

    def end_span(self, context: NodeExecutionContext, metrics: Dict[str, Any]):
        """End telemetry span with metrics.

        Args:
            context: Execution context
            metrics: Execution metrics
        """
        if not context.telemetry_span:
            return

        # Track configured metrics
        metrics_to_track = self.config.get("metrics_to_track", [])

        for metric in metrics_to_track:
            if metric in metrics:
                context.telemetry_span.set_metric(metric, metrics[metric])

        context.telemetry_span.finish()

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        # Pricing per 1M tokens (simplified)
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
        }

        model_pricing = pricing.get(model, pricing["gpt-4o"])

        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

        return input_cost + output_cost

class ModelRouter:
    """Handles dynamic model routing based on compute tier and cost optimization."""

    def __init__(self):
        """Initialize model router."""
        self.model_configs = {
            ComputeTier.TIER_1_REASONING: {
                "primary": "claude-3-5-sonnet-20241022",
                "fallback": "gpt-4o",
                "temperature": 0.7,
                "timeout_ms": 60000
            },
            ComputeTier.TIER_2_BALANCED: {
                "primary": "gpt-4o",
                "fallback": "claude-3-5-sonnet-20241022",
                "temperature": 0.5,
                "timeout_ms": 30000
            },
            ComputeTier.TIER_3_SPEED: {
                "primary": "gpt-4o-mini",
                "fallback": "claude-3-haiku-20240307",
                "temperature": 0.1,
                "timeout_ms": 15000
            }
        }

        self.logger = logging.getLogger("ModelRouter")

    def select_model(self, context: NodeExecutionContext) -> str:
        """# SQL removed: Select appropriate model based on infrastructure config.

        Args:
            context: Execution context

        Returns:
            Selected model name
        """
        infra_config = context.node_config.get("infrastructure_config", {})

        # Use explicit model if specified
        if "primary_model" in infra_config:
            context.selected_model = infra_config["primary_model"]
            return context.selected_model

        # Use compute tier to determine model
        tier_str = infra_config.get("compute_tier", "TIER_2_BALANCED")

        try:
            tier = ComputeTier(tier_str)
            model_config = self.model_configs[tier]
            context.selected_model = model_config["primary"]
            return context.selected_model

        except (ValueError, KeyError):
            self.logger.warning(f"Invalid tier {tier_str}, using default")
            context.selected_model = "gpt-4o"
            return context.selected_model

    def get_model_config(self, model: str) -> Dict[str, Any]:
        """Get configuration for a specific model.

        Args:
            model: Model name

        Returns:
            Model configuration
        """
        for tier_config in self.model_configs.values():
            if tier_config["primary"] == model:
                return tier_config

        # Default config
        return {
            "temperature": 0.7,
            "timeout_ms": 30000,
            "fallback": "gpt-4o"
        }

class MockTracer:
    """Mock tracer for when telemetry provider is not available."""

    def start_span(self, name: str):
        """TODO: Add docstring."""

        return MockSpan()

        """TODO: Add docstring."""

    def finish(self):
        pass

class MockSpan:
    """Mock span for telemetry."""
        """TODO: Add docstring."""


    def set_tag(self, key: str, value: str):
        """TODO: Add docstring."""

        pass

        """TODO: Add docstring."""

    def set_metric(self, key: str, value: Union[int, float]):
        pass

    def finish(self):
        pass

class NodeExecutor:
    """Main executor that composes all pipeline components."""

    def __init__(
        self,
        schema_registry: Dict[str, Type[BaseModel]],
        telemetry_config: Optional[Dict] = None
    ):
        """Initialize the node executor.

        Args:
            schema_registry: Registry of Pydantic models
            telemetry_config: Telemetry configuration
        """
        self.schema_enforcement = SchemaEnforcement(schema_registry)
        self.constraints = CognitiveConstraints()
        self.telemetry = CognitiveTelemetry(
            provider=telemetry_config.get("provider", "mock") if telemetry_config else "mock",
            config=telemetry_config
        )
        self.router = ModelRouter()

        self.logger = logging.getLogger("NodeExecutor")

    async def execute_node(self, context: NodeExecutionContext) -> NodeExecutionContext:
        """Execute a node through the full pipeline.

        Args:
            context: Execution context

        Returns:
            Updated context with results
        """
        start_time = time.time()

        try:
            # 1. Model Selection
            selected_model = self.router.select_model(context)
            self.logger.info(f"Selected model: {selected_model}")

            # 2. Start Telemetry
            self.telemetry.start_span(context)

            # 3. Build Prompt with Constraints
            base_prompt = context.node_config.get("system_prompt", "")
            constrained_prompt = self.constraints.apply_constraints_to_prompt(
                base_prompt,
                context.node_config
            )

            # 4. Execute LLM (mock implementation)
            raw_output = await self._execute_llm(context, constrained_prompt)
            context.raw_output = raw_output

            # 5. Validate Output
            validated_output = self.schema_enforcement.validate_output(context, raw_output)
            context.validated_output = validated_output

            # 6. Calculate Metrics
            context.execution_time_ms = (time.time() - start_time) * 1000

            metrics = {
                "latency_ms": context.execution_time_ms,
                "model": selected_model,
                "cost_usd": context.actual_cost_usd
            }

            # 7. End Telemetry
            self.telemetry.end_span(context, metrics)

            self.logger.info(f"Node {context.node_id} executed successfully")

        except Exception as e:
            context.errors.append(str(e))
            self.logger.error(f"Node {context.node_id} failed: {e}")

            # Still end telemetry with error metrics
            if context.telemetry_span:
                self.telemetry.end_span(context, {"error": str(e)})

        return context

    async def _execute_llm(self, context: NodeExecutionContext, prompt: str) -> str:
        """Execute the LLM (mock implementation).

        Args:
            context: Execution context
            prompt: System prompt

        Returns:
            Raw LLM output
        """
        # This would be replaced with actual LLM client
        # For now, return mock output based on node type

        if context.node_id == "K.6_most_recent_experience":
            return json.dumps({
                "intro_sentence": "Led strategic initiatives that drove measurable business growth through innovative solutions and cross-functional collaboration.",
                "bullets": [
                    "Orchestrated a digital transformation initiative that increased operational efficiency by 35% through automation.",
                    "Spearheaded the development of a customer analytics platform, resulting in a 25% improvement in retention rates.",
                    "Managed a cross-functional team of 12 to deliver a cloud migration project 2 months ahead of schedule.",
                    "Implemented a data-driven decision framework that reduced costs by $2M annually through optimization.",
                    "Led the integration of AI technologies into core products, enhancing user engagement by 40%.",
                    "Drove strategic partnerships with key technology vendors, expanding market reach by 30%.",
                    "Mentored junior developers and established best practices that improved team productivity by 50%."
                ]
            })

        return '{"content": "Mock output for testing"}'

# Factory function
def create_node_executor(
    schema_registry: Optional[Dict[str, Type[BaseModel]]] = None,
    telemetry_config: Optional[Dict] = None
) -> NodeExecutor:
    """Create a configured node executor.

    Args:
        schema_registry: Optional schema registry
        telemetry_config: Optional telemetry configuration

    Returns:
        NodeExecutor instance
    """
    if schema_registry is None:
        schema_registry = {}

    return NodeExecutor(schema_registry, telemetry_config)
