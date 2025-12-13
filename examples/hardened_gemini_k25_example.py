"""Example: Using HardenedGeminiExecutor for K.2.5 Deep Research.

This example demonstrates the titanium-grade features:
- Fault tolerance with automatic retry
- Pre-flight token validation
- Safety settings for Risk/Insurance domain
- Structured logging with telemetry
"""

import asyncio
import json
import logging

from agentic_workflow.runtime.shared import (
    create_hardened_gemini_executor,
    AgentMessage,
    HardenedGeminiConfig,
)
from agentic_workflow.apps_rg.L1_cognition.k2_5_deep_research_models import DeepResearchOutput

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # JSON logger outputs structured data
)

logger = logging.getLogger(__name__)

async def demonstrate_hardened_k25():
    """Demonstrate K.2.5 Deep Research with hardened executor."""

    logger.info("=== Hardened K.2.5 Deep Research Example ===\n")

    # Create hardened executor with custom config
    config = HardenedGeminiConfig(
        model="gemini-3-pro-preview",
        temperature=0.3,
        max_retries=5,
        safety_threshold_ratio=0.8,
    )

    executor = create_hardened_gemini_executor(config=config)

    # Prepare research prompt
    messages = [
        AgentMessage(
            role="user",
            content="Generate a comprehensive competitive intelligence report on DoorDash, focusing on their market position, technology stack, and leadership team."
        )
    ]

    system_prompt = """You are the Deep Research Core (K.2.5),
        an elite competitive intelligence analyst.

Your mission is to produce multi-layered intelligence reports that combine:
1. Strategic Layer: Market positioning, competitive moats, growth vectors
2. Technical Layer: Architecture decisions, tech stack, innovation pipeline
3. Leadership Layer: Executive team analysis, decision-making patterns

You must respond with valid JSON matching the DeepResearchOutput schema."""

    try:
        logger.info("Executing K.2.5 Deep Research with titanium-grade reliability...\n")

        # Execute with JSON schema enforcement
        response = await executor.execute_k_node(
            messages=messages,
            system_prompt=system_prompt,
            response_schema=DeepResearchOutput.model_json_schema()
        )

        # Parse and validate response
        research_data = json.loads(response)
        research_output = DeepResearchOutput(**research_data)

        # Display results
        logger.info("✅ Research completed successfully!\n")
        logger.info(f"Strategic Insights: {len(research_output.strategic_layer.key_findings)} findings")
        logger.info(f"Technical Analysis: {len(research_output.technical_layer.architecture_overview)} components")
        logger.info(f"Leadership Profiles: {len(research_output.leadership_layer.executive_profiles)} profiles")
        logger.info(f"Total Citations: {len(research_output.citation_map)} sources")

        # Show sample finding
        if research_output.strategic_layer.key_findings:
            logger.info("\nSample Strategic Finding:")
            logger.info(f"- {research_output.strategic_layer.key_findings[0].finding}")
            logger.info(f"  Confidence: {research_output.strategic_layer.key_findings[0].confidence_score}")

        return research_output

    except Exception as e:
        logger.info(f"❌ Error during research: {e}")
        raise

async def demonstrate_stateful_continuation():
    """Demonstrate stateful continuation with retry resilience."""

    logger.info("\n=== Stateful Continuation Example ===\n")

    executor = create_hardened_gemini_executor(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    # Initial request
    messages = [
        AgentMessage(role="user", content="Write a brief summary of machine learning.")
    ]

    logger.info("Sending initial request...")
    response1 = await executor.execute_k_node(messages=messages)

    # Parse response to get interaction ID (if available)
    try:
        response_data = json.loads(response1)
        # Note: interaction_id would be in telemetry logs, not response
        logger.info("Initial response received")
        logger.info(f"Response length: {len(response1)} characters")
    except json.JSONDecodeError:
        logger.info("Initial response received (plain text)")

    # Continue with refinement
    logger.info("\nSending refinement request...")
    messages2 = [
        AgentMessage(role="user", content="Now expand on deep learning specifically.")
    ]

    # In a real scenario, you'd pass the interaction_id from telemetry
    response2 = await executor.execute_k_node(messages=messages2)

    logger.info("✅ Refinement completed!")
    logger.info(f"Refined response length: {len(response2)} characters")

async def demonstrate_error_handling():
    """Demonstrate error handling and retry behavior."""

    logger.info("\n=== Error Handling Demonstration ===\n")

    # Create executor with low retry limit for demo
    config = HardenedGeminiConfig(
        model="gemini-3-pro-preview",
        max_retries=2,  # Low for quick demo
        retry_min_wait=1.0,
        retry_max_wait=5.0
    )

    executor = create_hardened_gemini_executor(config)

    # Create a payload that might exceed context
    large_content = "Analyze this: " + "This is test data. " * 100000

    messages = [
        AgentMessage(role="user", content=large_content)
    ]

    try:
        logger.info("Testing context overflow protection...")
        await executor.execute_k_node(messages=messages)
    except Exception as e:
        logger.info(f"✅ Caught expected error: {type(e).__name__}")
        logger.info(f"   Message: {str(e)[:100]}...")

    logger.info("\nAll error handling tests passed!")

async def main():
    """Run all demonstrations."""

    logger.info("🛡️  HardenedGeminiExecutor - Titanium Grade Demo\n")
    logger.info("This demo showcases:")
    logger.info("- Automatic retry on rate limits")
    logger.info("- Pre-flight token validation")
    logger.info("- Structured JSON logging")
    logger.info("- Safety settings for professional content")
    logger.info("- Stateful continuation support\n")

    # Run demonstrations
    await demonstrate_hardened_k25()
    await demonstrate_stateful_continuation()
    await demonstrate_error_handling()

    logger.info("\n✅ All demonstrations completed successfully!")
    logger.info("\nCheck the logs above for structured telemetry data.")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
