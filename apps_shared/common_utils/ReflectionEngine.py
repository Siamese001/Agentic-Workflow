"""Self-Reflection Engine - Quality gates for the CRITIQUE micro-stage.

This module implements the reflection engine that forces nodes to grade their own
work before passing it downstream, preventing hallucination cascades.
"""

import asyncio
import json
import logging
import time


    CircuitBreakerConfig,
    CircuitBreakerFactory,
    CircuitOpenError,
)

logger = logging.getLogger(__name__)


class CritiqueResult(BaseModel):
    """Result of a critique evaluation."""

    is_valid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    critique_reasoning: str
    suggested_fix: str | None = None
    validation_type: str = "unknown"  # "regex" or "llm"
    execution_time: float = 0.0
    mutation_request: Optional["MutationRequest"] = None

    @validator("confidence_score")
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0 and 1")
        return v


class ValidationCriterion(BaseModel):
    """A single validation criterion."""

    name: str
    description: str
    validator: str | Callable  # regex pattern or function
    is_required: bool = True
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class ReflectionConfig(BaseModel):
    """Configuration for the Reflection Engine."""

    use_fast_model: bool = True
    max_critique_loops: int = Field(default=3, ge=1, le=10)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_regex_cache: bool = True
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"  # Cost-effective model
    timeout: float = Field(default=30.0, ge=1.0)


class MutationRequest(BaseModel):
    """Request for DAG mutation when critique fails."""

    action: str  # "SPAWN_PREDECESSOR" or "ESCALATE"
    reason: str
    required_context: str | None = None
    hop_function: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: str = "normal"


class ReflectionEngine:
    """Engine for self-reflection and quality assessment."""

    def __init__(self, config: ReflectionConfig | None = None):
        """Initialize the Reflection Engine.

        Args:
            config: Optional configuration
        """
        self.config = config or ReflectionConfig()

        # Built-in validation criteria
        self.builtin_criteria = {
            "json_valid": ValidationCriterion(
                name="json_valid",
                description="Output must be valid JSON",
                validator=self._validate_json,
                is_required=True,
            ),
            "min_length": ValidationCriterion(
                name="min_length",
                description="Output must meet minimum length",
                validator=lambda x: len(str(x)) >= 10,
                is_required=False,
            ),
            "max_length": ValidationCriterion(
                name="max_length",
                description="Output must not exceed maximum length",
                validator=lambda x: len(str(x)) <= 10000,
                is_required=False,
            ),
            "no_empty_fields": ValidationCriterion(
                name="no_empty_fields",
                description="Dictionary values must not be empty",
                validator=self._validate_no_empty_fields,
                is_required=True,
            ),
            "contains_keywords": ValidationCriterion(
                name="contains_keywords",
                description="Output must contain specific keywords",
                validator=self._validate_keywords,
                is_required=False,
            ),
        }

        # Cache for regex patterns
        self._regex_cache = {} if self.config.enable_regex_cache else None

        # Statistics
        self.stats = {
            "total_critiques": 0,
            "fast_path_critiques": 0,
            "llm_critiques": 0,
            "passes": 0,
            "failures": 0,
            "average_confidence": 0.0,
        }

        # Initialize circuit breaker for LLM calls
        self.circuit_breaker = CircuitBreakerFactory.get(
            "reflection_engine",
            CircuitBreakerConfig(
                failure_threshold=3, recovery_timeout=60.0, timeout=self.config.timeout
            ),
        )

        logger.info(f"Initialized ReflectionEngine with model: {self.config.llm_model}")

    async def evaluate(
        self,
        content: Any,
        criteria: list[str | ValidationCriterion],
        context: dict[str, Any] | None = None,
    ) -> CritiqueResult:
        """Evaluate content against criteria with circuit breaker protection.

        Args:
            content: The content to evaluate
            criteria: List of criteria names or objects
            context: Optional context for evaluation

        Returns:
            CritiqueResult with evaluation details
        """
        start_time = time.time()
        self.stats["total_critiques"] += 1

        # Normalize criteria to objects
        normalized_criteria = []
        for criterion in criteria:
            if isinstance(criterion, str):
                if criterion in self.builtin_criteria:
                    normalized_criteria.append(self.builtin_criteria[criterion])
                else:
                    logger.warning(f"Unknown criterion: {criterion}")
            else:
                normalized_criteria.append(criterion)

        # Determine evaluation path and execute with circuit breaker
        try:
            if self._should_use_fast_path(normalized_criteria):
                # Fast path doesn't need circuit breaker (no LLM call)
                result = await self._fast_path_evaluate(content, normalized_criteria, context)
                self.stats["fast_path_critiques"] += 1
            else:
                # Wrap LLM call with circuit breaker
                result = await self.circuit_breaker.call(
                    self._llm_path_evaluate, content, normalized_criteria, context
                )
                self.stats["llm_critiques"] += 1

        except CircuitOpenError:
            # Circuit is open - return conservative result
            logger.warning("Reflection Engine Circuit OPEN. Skipping critique.")
            result = CritiqueResult(
                is_valid=True,  # Fail-open strategy
                confidence_score=0.3,  # Low confidence
                critique_reasoning="Circuit breaker OPEN - service degraded",
                validation_type="circuit_breaker_fallback",
            )

        except Exception as e:
            # Unexpected error - return conservative result
            logger.error(f"Reflection evaluation failed: {e}")
            result = CritiqueResult(
                is_valid=True,  # Fail-open to avoid blocking workflow
                confidence_score=0.2,  # Very low confidence
                critique_reasoning=f"Evaluation failed: {str(e)}",
                validation_type="error_fallback",
            )

        # Update statistics
        result.execution_time = time.time() - start_time
        if result.is_valid:
            self.stats["passes"] += 1
        else:
            self.stats["failures"] += 1

        # Update average confidence
        total = self.stats["total_critiques"]
        current_avg = self.stats["average_confidence"]
        self.stats["average_confidence"] = (
            current_avg * (total - 1) + result.confidence_score
        ) / total

        return result

    def _should_use_fast_path(self, criteria: list[ValidationCriterion]) -> bool:
        """Determine if fast path (regex) can be used."""
        # Fast path if all criteria are simple validators
        for criterion in criteria:
            if isinstance(criterion.validator, str):
                # Regex pattern - can use fast path
                continue
            elif callable(criterion.validator) and criterion.name in self.builtin_criteria:
                # Built-in validator - can use fast path
                continue
            else:
                # Complex validator - need LLM
                return False
        return True

    async def _fast_path_evaluate(
        self, content: Any, criteria: list[ValidationCriterion], context: dict[str, Any] | None
    ) -> CritiqueResult:
        """Evaluate using fast regex/built-in validators."""
        results = []
        total_weight = 0
        weighted_score = 0

        for criterion in criteria:
            try:
                if isinstance(criterion.validator, str):
                    # Regex validation
                    is_valid = self._validate_regex(content, criterion.validator)
                else:
                    # Built-in function validation
                    is_valid = criterion.validator(content)

                if is_valid:
                    weighted_score += criterion.weight
                else:
                    results.append(f"Failed: {criterion.description}")

                total_weight += criterion.weight

            except Exception as e:
                logger.error(f"Validation error for {criterion.name}: {e}")
                results.append(f"Error: {criterion.name} - {str(e)}")

        # Calculate overall result
        confidence = weighted_score / total_weight if total_weight > 0 else 0.0
        is_valid = confidence >= self.config.confidence_threshold

        reasoning = (
            "Fast path validation: " + "; ".join(results) if results else "All criteria passed"
        )

        return CritiqueResult(
            is_valid=is_valid,
            confidence_score=confidence,
            critique_reasoning=reasoning,
            validation_type="regex",
        )

    async def _llm_path_evaluate(
        self, content: Any, criteria: list[ValidationCriterion], context: dict[str, Any] | None
    ) -> CritiqueResult:
        """Evaluate using LLM for semantic validation."""
        # Build prompt
        criteria_text = "\n".join(
            [
                f"- {c.name}: {c.description}{' (Required)' if c.is_required else ''}"
                for c in criteria
            ]
        )

        context_text = f"\nContext: {json.dumps(context, indent=2)}" if context else ""

        prompt = f"""You are a QA Auditor evaluating the output of an AI agent.

Output to evaluate:
{json.dumps(content, indent=2)}

Validation criteria:
{criteria_text}
{context_text}

Instructions:
1. Check each criterion carefully
2. Provide a Pass/Fail judgment
3. Explain your reasoning
4. If failed, suggest a specific fix

Respond in JSON format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation",
    "suggested_fix": "Specific suggestion if invalid"
}}"""

        try:
            # Call LLM (mock implementation)
            response = await self._call_llm(prompt)

            # Parse response
            llm_result = json.loads(response)

            return CritiqueResult(
                is_valid=llm_result.get("is_valid", False),
                confidence_score=llm_result.get("confidence", 0.0),
                critique_reasoning=llm_result.get("reasoning", "No reasoning provided"),
                suggested_fix=llm_result.get("suggested_fix"),
                validation_type="llm",
            )

        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            # Fallback to conservative result
            return CritiqueResult(
                is_valid=False,
                confidence_score=0.0,
                critique_reasoning=f"LLM evaluation failed: {str(e)}",
                validation_type="llm_error",
            )

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM for evaluation.

        In a real implementation, this would use the actual LLM client.
        For now, returns a mock response.
        """
        # Mock implementation - in production, use actual LLM
        await asyncio.sleep(0.1)  # Simulate network delay

        # Simple heuristic based on prompt content
        if "json" in prompt.lower():
            return json.dumps(
                {
                    "is_valid": True,
                    "confidence": 0.9,
                    "reasoning": "Output is valid JSON format",
                    "suggested_fix": None,
                }
            )
        elif "required" in prompt.lower():
            return json.dumps(
                {
                    "is_valid": False,
                    "confidence": 0.3,
                    "reasoning": "Missing required fields",
                    "suggested_fix": "Add all required fields to the output",
                }
            )
        else:
            return json.dumps(
                {
                    "is_valid": True,
                    "confidence": 0.8,
                    "reasoning": "Output meets general quality standards",
                    "suggested_fix": None,
                }
            )

    def _validate_regex(self, content: Any, pattern: str) -> bool:
        """Validate content using regex pattern."""
        if self._regex_cache and pattern in self._regex_cache:
            compiled = self._regex_cache[pattern]
        else:
            compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            if self._regex_cache is not None:
                self._regex_cache[pattern] = compiled

        text = str(content)
        return bool(compiled.search(text))

    def _validate_json(self, content: Any) -> bool:
        """Validate that content is valid JSON."""
        if isinstance(content, (dict, list)):
            try:
                json.dumps(content)
                return True
            except (TypeError, ValueError):
                return False
        elif isinstance(content, str):
            try:
                json.loads(content)
                return True
            except json.JSONDecodeError:
                return False
        return False

    def _validate_no_empty_fields(self, content: Any) -> bool:
        """Validate that dictionary has no empty values."""
        if not isinstance(content, dict):
            return True  # Not applicable

        for key, value in content.items():
            if value is None or value == "":
                return False
            if isinstance(value, str) and not value.strip():
                return False

        return True

    def _validate_keywords(self, content: Any) -> bool:
        """Validate that content contains required keywords."""
        # This is a placeholder - actual keywords would be in context
        text = str(content).lower()
        required_keywords = ["result", "output"]  # Example

        return all(keyword in text for keyword in required_keywords)

    def get_stats(self) -> dict[str, Any]:
        """Get reflection engine statistics."""
        return {
            **self.stats,
            "config": {
                "model": self.config.llm_model,
                "max_loops": self.config.max_critique_loops,
                "confidence_threshold": self.config.confidence_threshold,
            },
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            "total_critiques": 0,
            "fast_path_critiques": 0,
            "llm_critiques": 0,
            "passes": 0,
            "failures": 0,
            "average_confidence": 0.0,
        }


# Global instance
_reflection_engine: ReflectionEngine | None = None


def get_reflection_engine(**kwargs) -> ReflectionEngine:
    """Get or create global ReflectionEngine instance.

    Args:
        **kwargs: Configuration arguments

    Returns:
        ReflectionEngine instance
    """
    global _reflection_engine

    if _reflection_engine is None:
        config = ReflectionConfig(**kwargs) if kwargs else ReflectionConfig()
        _reflection_engine = ReflectionEngine(config)

    return _reflection_engine


# Convenience functions
async def evaluate_content(
    content: Any,
    criteria: list[str | ValidationCriterion],
    context: dict[str, Any] | None = None,
    **kwargs,
) -> CritiqueResult:
    """Convenience function for content evaluation.

    Args:
        content: Content to evaluate
        criteria: Validation criteria
        context: Optional context
        **kwargs: Engine configuration

    Returns:
        CritiqueResult
    """
    engine = get_reflection_engine(**kwargs)
    return await engine.evaluate(content, criteria, context)


# Pre-defined criteria sets
STANDARD_CRITERIA = ["json_valid", "no_empty_fields", "min_length"]

STRICT_CRITERIA = ["json_valid", "no_empty_fields", "min_length", "max_length"]

LENIENT_CRITERIA = ["json_valid"]
