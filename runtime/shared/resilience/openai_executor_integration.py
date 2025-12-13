"""
Integration example for HardenedOpenAIExecutor with multi-provider fallback.

This file demonstrates how to:
1. Set up the OpenAI executor with proper hardening
2. Implement provider switching for redundancy
3. Use the executor with structured outputs
4. Monitor performance and costs
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, Type, Union
from enum import Enum

from .hardened_openai_executor import (
    HardenedOpenAIExecutor,
    HardeningConfig,
    Provider,
    create_hardened_executor,
    AgentMessage
)
from .titanium_research_core import TitaniumResearchOutput

logger = logging.getLogger(__name__)

class MultiProviderExecutor:
    """
    Multi-provider executor with automatic fallback.

    Provides seamless switching between providers (OpenAI, Gemini, etc.)
    with unified interface and comprehensive monitoring.
    """

    def __init__(self, config: HardeningConfig):
        """Initialize multi-provider executor.

        Args:
            config: Hardening configuration
        """
        self.config = config
        self.providers = {}
        self.primary_provider = None
        self.fallback_providers = []

        # Statistics
        self.stats = {
            "total_requests": 0,
            "primary_success": 0,
            "fallback_used": 0,
            "all_failed": 0,
            "provider_stats": {}
        }

        self.logger = logging.getLogger("MultiProviderExecutor")

    def register_provider(
        self,
        provider: Provider,
        is_primary: bool = False,
        **kwargs
    ) -> None:
        """Register a provider with the executor.

        Args:
            provider: Provider type
            is_primary: Whether this is the primary provider
            **kwargs: Provider-specific arguments
        """
        try:
            executor = create_hardened_executor(provider, self.config, **kwargs)
            self.providers[provider] = executor

            if is_primary:
                self.primary_provider = provider
            else:
                self.fallback_providers.append(provider)

            self.logger.info(f"Registered {provider.value} provider")

        except Exception as e:
            self.logger.error(f"Failed to register {provider.value}: {e}")
            raise

    async def execute_with_fallback(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str] = None,
        response_schema: Optional[Type] = None,
        temperature: float = 0.7
    ) -> Any:
        """Execute with automatic provider fallback.

        Args:
            messages: List of agent messages
            system_prompt: Optional system prompt
            response_schema: Optional response schema
            temperature: Sampling temperature

        Returns:
            Response from primary or fallback provider
        """
        self.stats["total_requests"] += 1

        # Try primary provider first
        if self.primary_provider:
            try:
                result = await self.providers[self.primary_provider].execute_k_node(
                    messages=messages,
                    system_prompt=system_prompt,
                    response_schema=response_schema,
                    temperature=temperature
                )

                self.stats["primary_success"] += 1
                self._update_provider_stats(self.primary_provider, True)

                return result

            except Exception as e:
                self.logger.warning(f"Primary provider {self.primary_provider.value} failed: {e}")
                self._update_provider_stats(self.primary_provider, False)

        # Try fallback providers
        for provider in self.fallback_providers:
            try:
                self.logger.info(f"Trying fallback provider: {provider.value}")
                result = await self.providers[provider].execute_k_node(
                    messages=messages,
                    system_prompt=system_prompt,
                    response_schema=response_schema,
                    temperature=temperature
                )

                self.stats["fallback_used"] += 1
                self._update_provider_stats(provider, True)

                self.logger.info(f"Fallback to {provider.value} successful")
                return result

            except Exception as e:
                self.logger.warning(f"Fallback provider {provider.value} failed: {e}")
                self._update_provider_stats(provider, False)
                continue

        # All providers failed
        self.stats["all_failed"] += 1
        raise RuntimeError("All providers failed to execute request")

    def _update_provider_stats(self, provider: Provider, success: bool) -> None:
        """Update provider-specific statistics.

        Args:
            provider: Provider that was used
            success: Whether the request was successful
        """
        if provider not in self.stats["provider_stats"]:
            self.stats["provider_stats"][provider] = {
                "requests": 0,
                "successes": 0,
                "failures": 0
            }

        stats = self.stats["provider_stats"][provider]
        stats["requests"] += 1

        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics across all providers."""
        total = self.stats["total_requests"]

        if total == 0:
            return self.stats

        stats = self.stats.copy()
        stats["primary_success_rate"] = (
            self.stats["primary_success"] / total
            if total > 0 else 0
        )
        stats["fallback_rate"] = (
            self.stats["fallback_used"] / total
            if total > 0 else 0
        )
        stats["total_failure_rate"] = (
            self.stats["all_failed"] / total
            if total > 0 else 0
        )

        # Add provider-specific stats
        for provider, provider_stats in self.stats["provider_stats"].items():
            if provider_stats["requests"] > 0:
                provider_stats["success_rate"] = (
                    provider_stats["successes"] / provider_stats["requests"]
                )

        return stats

class OpenAIExecutorIntegration:
    """
    Integration layer for OpenAI executor with specific use cases.

    Provides high-level methods for common tasks and ensures
    optimal usage of OpenAI's capabilities.
    """

    def __init__(self, executor: HardenedOpenAIExecutor):
        """Initialize with OpenAI executor.

        Args:
            executor: HardenedOpenAIExecutor instance
        """
        self.executor = executor
        self.logger = logging.getLogger("OpenAIIntegration")

    async def generate_structured_response(
        self,
        prompt: str,
        schema: Type,
        temperature: float = 0.3
    ) -> Any:
        """Generate a structured response using OpenAI's JSON mode.

        Args:
            prompt: Input prompt
            schema: Pydantic schema for response
            temperature: Sampling temperature

        Returns:
            Structured response matching schema
        """
        messages = [AgentMessage(role="user", content=prompt)]

        return await self.executor.execute_k_node(
            messages=messages,
            response_schema=schema,
            temperature=temperature
        )

    async def analyze_with_chain_of_thought(
        self,
        problem: str,
        context: Optional[str] = None
    ) -> str:
        """Generate analysis using chain of thought.

        Args:
            problem: Problem to analyze
            context: Optional context

        Returns:
            Detailed analysis
        """
        cot_prompt = f"""
        Think step by step to solve this problem.

        Problem: {problem}

        {f'Context: {context}' if context else ''}

        Provide a detailed analysis breaking down:
        1. Key components of the problem
        2. Relevant considerations
        3. Step-by-step reasoning
        4. Final conclusion

        Analysis:
        """

        messages = [AgentMessage(role="user", content=cot_prompt)]

        return await self.executor.execute_k_node(
            messages=messages,
            temperature=0.5
        )

    async def extract_entities(
        self,
        text: str,
        entity_types: List[str]
    ) -> Dict[str, List[str]]:
        """Extract entities from text.

        Args:
            text: Text to analyze
            entity_types: Types of entities to extract

        Returns:
            Dictionary of entity types and their values
        """
        from pydantic import BaseModel, Field

        class EntityExtraction(BaseModel):
            entities: Dict[str, List[str]] = Field(
                ...,
                description="Extracted entities by type"
            )

        prompt = f"""
        Extract the following entity types from the text:
        {', '.join(entity_types)}

        Text: {text}

        Return as JSON with entity types as keys and lists of extracted values.
        """

        result = await self.generate_structured_response(
            prompt=prompt,
            schema=EntityExtraction
        )

        return result.entities

    async def summarize_document(
        self,
        content: str,
        max_length: int = 200,
        style: str = "executive"
    ) -> str:
        """Summarize document with specified style.

        Args:
            content: Document content
            max_length: Maximum summary length
            style: Summary style (executive, technical, brief)

        Returns:
            Document summary
        """
        style_instructions = {
            "executive": "Focus on key business insights and recommendations",
            "technical": "Highlight technical details and implementation",
            "brief": "Provide the most important points in 3-4 sentences"
        }

        instruction = style_instructions.get(style, style_instructions["executive"])

        prompt = f"""
        Summarize the following document in {style} style.
        {instruction}

        Maximum length: {max_length} words

        Document:
        {content}

        Summary:
        """

        messages = [AgentMessage(role="user", content=prompt)]

        return await self.executor.execute_k_node(
            messages=messages,
            temperature=0.4
        )

    def get_usage_report(self) -> Dict[str, Any]:
        """Get detailed usage and cost report."""
        stats = self.executor.get_stats()

        # Add cost projections
        if stats["total_requests"] > 0:
            daily_projection = stats["total_cost_estimate"] * 24
            monthly_projection = stats["total_cost_estimate"] * 30

            stats["projections"] = {
                "daily_estimate": daily_projection,
                "monthly_estimate": monthly_projection
            }

        return stats

# Example usage
async def main():
    """Example of OpenAI executor integration usage."""

    # Initialize hardening config
    config = HardeningConfig(
        max_retries=3,
        timeout_seconds=30.0,
        circuit_breaker_threshold=5
    )

    # Create OpenAI executor
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.info("Error: OPENAI_API_KEY environment variable not set")
        return

    executor = create_openai_executor(
        api_key=api_key,
        model="gpt-4o",
        hardening_config=config
    )

    # Create integration layer
    integration = OpenAIExecutorIntegration(executor)

    # Example 1: Structured response
    logger.info("\n=== Structured Response Example ===")
    prompt = "Analyze the financial performance of a tech company with $100M revenue"

    try:
        result = await integration.generate_structured_response(
            prompt=prompt,
            schema=TitaniumResearchOutput
        )
        logger.info(f"Confidence: {result.confidence_score}")
        logger.info(f"Findings: {len(result.verified_findings)}")
    except Exception as e:
        logger.info(f"Error: {e}")

    # Example 2: Entity extraction
    logger.info("\n=== Entity Extraction Example ===")
    text = "Apple Inc. announced Q4 2024 revenue of $94.9B, led by Tim Cook."
    entities = await integration.extract_entities(
        text=text,
        entity_types=["companies", "people", "amounts", "dates"]
    )

    for entity_type, values in entities.items():
        logger.info(f"{entity_type}: {values}")

    # Example 3: Multi-provider fallback
    logger.info("\n=== Multi-Provider Example ===")
    multi = MultiProviderExecutor(config)

    # Register OpenAI as primary
    multi.register_provider(
        Provider.OPENAI,
        is_primary=True,
        api_key=api_key,
        model="gpt-4o"
    )

    # Register Gemini as fallback (if available)
    # multi.register_provider(
    #     Provider.GOOGLE,
    #     is_primary=False,
    #     api_key=os.getenv("GOOGLE_API_KEY")
    # )

    # Execute with fallback
    messages = [AgentMessage(role="user", content="What is the meaning of life?")]

    try:
        response = await multi.execute_with_fallback(messages)
        logger.info(f"Response: {response[:100]}...")
    except Exception as e:
        logger.info(f"All providers failed: {e}")

    # Get comprehensive stats
    stats = multi.get_comprehensive_stats()
    logger.info(f"\n=== Multi-Provider Stats ===")
    logger.info(f"Total Requests: {stats['total_requests']}")
    logger.info(f"Primary Success Rate: {stats['primary_success_rate']:.2%}")
    logger.info(f"Fallback Rate: {stats['fallback_rate']:.2%}")

    # Get usage report
    usage = integration.get_usage_report()
    logger.info(f"\n=== Usage Report ===")
    logger.info(f"Total Cost: ${usage['total_cost_estimate']:.4f}")
    logger.info(f"Avg Tokens/Request: {usage['avg_tokens_per_request']:.0f}")

    if "projections" in usage:
        logger.info(f"Monthly Projection: ${usage['projections']['monthly_estimate']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
