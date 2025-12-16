"""K.5A End-to-End Execution Example.

This example demonstrates the complete execution flow for K.5A bullet generation
with validation, feedback loop, and provenance rule enforcement.

This is the proof of concept that bridges the Configuration Layer and Execution Layer.
"""

import asyncio
import logging

# Import orchestration config
from .resume_orchestration_config import (
    K_NODE_REASONING_CONFIGS,
    GLOBAL_WORD_COUNTS,
    PROVENANCE_RULES,
    VALIDATION_GATES,
    FEEDBACK_LOOP_CONFIG,
    ADAPTIVE_TEMPERATURE_CONFIG,
)

# Import execution framework
from .execution_framework import (
    ValidationGateExecutor,
    ValidationStatus,
    ValidationResult,
)
from .feedback_loop import (
    FeedbackLoopOrchestrator,
    RegenerationResult,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

async def validate_k5a_output(
    output: K5AOutput,
    context: Dict[str, Any],
    validator: ValidationGateExecutor,
) -> ValidationResult:
    """Validate K.5A output against all constraints.

    Args:
        output: K.5A generation output
        context: Validation context
        validator: ValidationGateExecutor instance

    Returns:
        ValidationResult with pass/fail status
    """
    # Combine bullets into single content string for validation
    CONTENT = "\n".join(f"• {bullet}" for bullet in output.bullets)

    # Add output metadata to context
    context["word_counts"] = output.word_counts
    context["PROVENANCE"] = output.provenance

    # Execute all K.5A validation gates
    RESULTS = validator.execute_all_gates(
        execution_point="POST_K5A_GENERATION",
        CONTENT=CONTENT,
        k_node_id="K.5A",
        CONTEXT=context,
    )

    # Combine results
    all_passed = all(r.passed for r in RESULTS)
    all_failures = []
    for r in RESULTS:
        all_failures.extend(r.failures)

    if all_passed:
        return ValidationResult(
            STATUS=ValidationStatus.PASS,
            gate_id="K5A_COMBINED",
            execution_point="POST_K5A_GENERATION",
            SCORE=1.0,
        )
    else:
        # Find worst result
        WORST = min(RESULTS, key=lambda r: r.score)
        return ValidationResult(
            STATUS=WORST.status,
            gate_id="K5A_COMBINED",
            execution_point="POST_K5A_GENERATION",
            FAILURES=all_failures,
            ACTION=WORST.action,
            SCORE=WORST.score,
            MESSAGE=WORST.message,
        )

async def generate_k5a_bullets(
    context: Dict[str, Any],
    temperature: float,
    agent: K5A_GenerationAgent,
) -> K5AOutput:
    """Generate K.5A bullets.

    Args:
        context: Generation context
        temperature: Temperature for generation
        agent: K5A agent instance

    Returns:
        K5AOutput with bullets
    """
    # Update agent temperature
    agent.CONFIG.temperature = temperature

    # Execute generation
    output = await agent.execute(context)

    return output

async def execute_k5a_with_feedback(
    initial_context: Dict[str, Any],
    agent: K5A_GenerationAgent,
    validator: ValidationGateExecutor,
    orchestrator: FeedbackLoopOrchestrator,
) -> RegenerationResult:
    """Execute K.5A with feedback loop.

    Args:
        initial_context: Initial context
        agent: K5A agent
        validator: Validator
        orchestrator: Feedback loop orchestrator

    Returns:
        RegenerationResult with final bullets
    """
    # Define generator wrapper
    async def generator(context: Dict[str, Any], temperature: float) -> str:
        """TODO: Add docstring."""

        output = await generate_k5a_bullets(context, temperature, agent)
        # Store output in context for validation
        context["_k5a_output"] = output
        # Return as string for validation
        return "\n".join(f"• {bullet}" for bullet in output.bullets)

    # Define validator wrapper
    async def validator_func(content: str, context: Dict[str, Any]) -> ValidationResult:
        """Docstring."""
        output = context.get("_k5a_output")
        if not output:
            # Parse content back to output
            BULLETS = [line.strip("• ").strip()
                                  for line in content.split("\n") if line.strip()]
            output = K5AOutput(
                bullets=BULLETS,
                provenance=["S"] * len(BULLETS),
                word_counts=[len(b.split()) for b in BULLETS],
                metadata={},
            )

        return await validate_k5a_output(output, context, validator)

    # Execute with feedback loop
    result = await orchestrator.execute_with_feedback(
        GENERATOR=generator,
        VALIDATOR=validator_func,
        initial_context=initial_context,
        k_node_id="K.5A",
    )

    return result

async def main():
    """Main execution function - K.5A proof of concept."""

    LOGGER.info("=" * 80)
    LOGGER.info("K.5A END-TO-END EXECUTION - PROOF OF CONCEPT")
    LOGGER.info("=" * 80)

    # Step 1: Load configuration from orchestration config
    LOGGER.info(
        "\n[STEP 1] Loading configuration from resume_orchestration_config.py")

    k5_reasoning_config = K_NODE_REASONING_CONFIGS.get("K.5")
    if not k5_reasoning_config:
        LOGGER.error("K.5 reasoning config not found!")
        return

    LOGGER.info(
        f"✓ Loaded K.5 reasoning config: temp={k5_reasoning_config.temperature}")

    # Convert to ReasoningConfig
    reasoning_config = ReasoningConfig(
        temperature=k5_reasoning_config.temperature,
        rag_type=k5_reasoning_config.rag_type.value,
        rag_total_calls=k5_reasoning_config.rag_total_calls,
        rag_hops=k5_reasoning_config.rag_hops,
        self_consistency=k5_reasoning_config.self_consistency,
        tot_branches=k5_reasoning_config.tot_branches,
    )

    # Load provenance rule
    provenance_rule = PROVENANCE_RULES.get("K.5A")
    if not provenance_rule:
        LOGGER.error("K.5A provenance rule not found!")
        return

    LOGGER.info(f"✓ Loaded provenance rule: {provenance_rule.pattern}")

    # Load word count constraint
    word_count_constraint = GLOBAL_WORD_COUNTS.get("K.5A_unify_bullets")
    if not word_count_constraint:
        LOGGER.error("K.5A word count constraint not found!")
        return

    LOGGER.info(
        f"✓ Loaded word count constraint: "
        f"{word_count_constraint.min}-{word_count_constraint.max} words per bullet"
    )

    # Step 2: Initialize components
    LOGGER.info("\n[STEP 2] Initializing execution framework components")

    # Initialize K.5A agent
    agent = K5A_GenerationAgent(
        CONFIG=reasoning_config,
        provenance_rule=provenance_rule,
        word_count_min=word_count_constraint.min,
        word_count_max=word_count_constraint.max,
    )
    LOGGER.info("✓ K.5A agent initialized")

    # Initialize validator
    validator = ValidationGateExecutor(
        validation_gates=VALIDATION_GATES,
        word_count_constraints=GLOBAL_WORD_COUNTS,
    )
    LOGGER.info("✓ ValidationGateExecutor initialized")

    # Initialize feedback loop orchestrator
    orchestrator = FeedbackLoopOrchestrator(
        max_attempts=FEEDBACK_LOOP_CONFIG["max_attempts"],
        checkpoint_saving=FEEDBACK_LOOP_CONFIG["checkpoint_saving"],
        reversion_enabled=FEEDBACK_LOOP_CONFIG["reversion_capability"],
        adaptive_temperature_config=ADAPTIVE_TEMPERATURE_CONFIG,
    )
    LOGGER.info("✓ FeedbackLoopOrchestrator initialized")

    # Step 3: Prepare context
    LOGGER.info("\n[STEP 3] Preparing execution context")

    context = {
        "master_bullets": ["Led cross-functional team of 8 engineers to architect and deploy cloud-native ML platform serving 2M + daily predictions with 99.9 % uptime",
            "Designed and implemented real-time data pipeline processing 500GB daily using Apache Kafka and Spark, reducing latency by 60 %",
            "Built production recommendation system using collaborative filtering and deep learning, increasing user engagement by 35 %",
            "Established MLOps practices including CI/CD pipelines, automated testing, and model monitoring, reducing deployment time by 70 %",
            "Mentored 5 junior engineers on ML best practices, code review standards, and system design principles",
            "Optimized model inference performance through quantization and caching strategies, reducing costs by $200K annually",
            "Collaborated with product and business teams to define ML roadmap and prioritize high-impact features",
            "Implemented A/B testing framework for ML models, enabling data-driven decision making across 20 + experiments",
        ],
        "differentiators": [
            "machine learning",
            "cloud architecture",
            "real-time processing",
            "MLOps",
            "scalability",
        ],
        "job_description": """
        Senior ML Engineer - Unify Consulting

        We're looking for an experienced ML engineer to lead our AI initiatives.
        You'll architect scalable ML systems, mentor junior engineers, and drive
        technical excellence across our consulting practice.

        Required: Python, TensorFlow/PyTorch, cloud platforms (AWS/GCP), MLOps,
        distributed systems, real-time data processing.
        """,
    }

    LOGGER.info(
        f"✓ Context prepared with {len(context['master_bullets'])} master bullets")

    # Step 4: Execute with feedback loop
    LOGGER.info("\n[STEP 4] Executing K.5A generation with feedback loop")
    LOGGER.info(f"Max attempts: {FEEDBACK_LOOP_CONFIG['max_attempts']}")
    LOGGER.info(f"Initial temperature: {reasoning_config.temperature}")

    try:
        result = await execute_k5a_with_feedback(
            initial_context=context,
            agent=agent,
            validator=validator,
            orchestrator=orchestrator,
        )

        # Step 5: Display results
        LOGGER.info("\n[STEP 5] Results")
        LOGGER.info("=" * 80)

        if result.success:
            LOGGER.info("✅ K.5A GENERATION SUCCESSFUL")
            LOGGER.info(f"Attempts: {result.attempts}")
            LOGGER.info(f"Reverted: {result.reverted}")
            LOGGER.info(f"Final score: {result.final_validation.score:.2f}")

            # Parse bullets from final content
            BULLETS = [
                line.strip("• ").strip()
                for line in result.final_content.split("\n")
                if line.strip()
            ]

            LOGGER.info(f"\nGenerated {len(BULLETS)} bullets:")
            for i, bullet in enumerate(BULLETS, 1):
                word_count = len(bullet.split())
                LOGGER.info(f"\n{i}. {bullet}")
                LOGGER.info(f"   Words: {word_count}")

        elif result.reverted:
            LOGGER.warning("⚠️  K.5A GENERATION REVERTED TO BETTER ATTEMPT")
            LOGGER.info(f"Attempts: {result.attempts}")
            LOGGER.info(f"Final score: {result.final_validation.score:.2f}")

            BULLETS = [
                line.strip("• ").strip()
                for line in result.final_content.split("\n")
                if line.strip()
            ]

            LOGGER.info(
                f"\nReverted to {len(BULLETS)} bullets (best attempt):")
            for i, bullet in enumerate(BULLETS, 1):
                word_count = len(bullet.split())
                LOGGER.info(f"\n{i}. {bullet}")
                LOGGER.info(f"   Words: {word_count}")

        else:
            LOGGER.error("❌ K.5A GENERATION FAILED")
            LOGGER.error(f"Exhausted all {result.attempts} attempts")

            # Generate failure report
            failure_report = orchestrator.generate_failure_report(
                result, "K.5A")
            LOGGER.error(f"\n{failure_report}")

        # Display checkpoint history
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("CHECKPOINT HISTORY")
        LOGGER.info("=" * 80)

        for checkpoint in result.checkpoints:
            LOGGER.info(f"\nAttempt {checkpoint.attempt}:")
            LOGGER.info(f"  Temperature: {checkpoint.temperature:.2f}")
            LOGGER.info(f"  Score: {checkpoint.score:.2f}")
            LOGGER.info(f"  Failure Type: {checkpoint.failure_type.value if checkpoint.failure_type else 'N/A'}")
            LOGGER.info(
                f"  Status: {checkpoint.validation_result.status.value}")

            if hasattr(checkpoint.validation_result,
                'failures') and checkpoint.validation_result.failures:
                LOGGER.info(
                    f"  Failures: {len(checkpoint.validation_result.failures)}")
                for failure in checkpoint.validation_result.failures[:2]:
                    LOGGER.info(
                        f"    - {failure.rule_name}: {failure.message}")

    except Exception as e:
LOGGER.error(f"Execution failed with error: {e}", exc_info=True)

    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("K.5A PROOF OF CONCEPT COMPLETE")
    LOGGER.info("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

