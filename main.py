"""
Main Orchestration Script - Canon Validator System

Executes the complete L5 Meta-Learning workflow as specified
in the master prompt.
"""

import logging
import time

from agent_logic import CanonValidator
from db_manager import HybridDatabaseManager
from etl_pipeline import run_etl_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_system():
    """
    Initialize all system components.

    1. Connect to databases
    2. Run ETL pipeline to hydrate caches
    3. Initialize the Canon Validator
    """
    logger.info("=" * 50)
    logger.info("CANON VALIDATOR SYSTEM - L5 META-LEARNING")
    logger.info("=" * 50)

    # Initialize database manager
    logger.info("1. Connecting to databases...")
    db_manager = HybridDatabaseManager(
        redis_host="localhost",
        redis_port=6379,
        qdrant_host="localhost",
        qdrant_port=6333
    )

    # Run ETL pipeline
    logger.info("2. Running ETL pipeline...")
    etl_results = run_etl_pipeline(
        source_dir="./data/code_samples",
        create_samples=True,
        backfill=True,
        hydrate=True
    )

    logger.info(f"   ETL Results: {etl_results}")

    # Initialize Canon Validator
    logger.info("3. Initializing Canon Validator...")
    validator = CanonValidator()

    logger.info("System setup complete!")
    return validator, db_manager


def simulate_learning_loop(validator: CanonValidator, iterations: int = 3):
    """
    Simulate a learning loop to demonstrate meta-learning.

    The loop:
    1. Checks code against the Canon
    2. Mocks a failure
    3. Updates learning
    4. Checks again to see filtering
    """
    logger.info("\n" + "=" * 50)
    logger.info("SIMULATING LEARNING LOOP")
    logger.info("=" * 50)

    # Test code samples
    test_cases = [
        {
            "name": "Good Function",
            "code": """
def calculate_average(numbers):
    \"\"\"Calculate the average of a list of numbers.\"\"\"
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
""",
            "expected_outcome": "SUCCESS"
        },
        {
            "name": "Problematic Function",
            "code": """
def divide_by_zero(x):
    \"\"\"This will cause an error.\"\"\"
    return x / 0
""",
            "expected_outcome": "FAILURE"
        },
        {
            "name": "Async Pattern",
            "code": """
async def fetch_data(url):
    \"\"\"Fetch data asynchronously.\"\"\"
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
""",
            "expected_outcome": "SUCCESS"
        }
    ]

    for i, test_case in enumerate(test_cases[:iterations], 1):
        logger.info(f"\n--- Test Case {i}: {test_case['name']} ---")

        # Check code against Canon
        result = validator.check_and_learn(
            test_case["code"],
            context={
                "canon_rule_id": f"test_rule_{i}",
                "project_context": "demo_project"
            }
        )

        logger.info(f"Initial check result:")
        logger.info(f"  Valid: {result['is_valid']}")
        logger.info(f"  Source: {result['source']}")
        logger.info(f"  Confidence: {result['confidence']:.2f}")
        logger.info(f"  Recommendation: {result['recommendation']}")

        # Simulate execution outcome
        outcome = test_case["expected_outcome"]
        logger.info(f"\nSimulated execution outcome: {outcome}")

        # Update learning
        if result["matched_pattern"]:
            validator.update_learning(
                result["matched_pattern"],
                outcome,
                error_trace="DivisionByZeroError" if outcome == "FAILURE" else None
            )

            # Check again to see if learning took effect
            logger.info("\nChecking pattern after learning update...")
            patterns = validator.search_similar_patterns(
                test_case["code"], max_results=5)

            if patterns:
                top_pattern = patterns[0]
                logger.info(f"Top similar pattern:")
                logger.info(
                    f"  Success Rate: {top_pattern['success_rate']:.2%}")
                logger.info(f"  Successes: {top_pattern['success_count']}")
                logger.info(f"  Failures: {top_pattern['failure_count']}")

        time.sleep(1)  # Brief pause between tests


def demonstrate_meta_learning(validator: CanonValidator):
    """
    Demonstrate the meta-learning capabilities.
    """
    logger.info("\n" + "=" * 50)
    logger.info("META-LEARNING DEMONSTRATION")
    logger.info("=" * 50)

    # Show learning statistics
    stats = validator.get_learning_stats()
    logger.info("\nLearning Statistics:")
    logger.info(
        f"  Promotion Threshold: {stats['promotion_threshold']} successes")
    logger.info(f"  Failure Threshold: {stats['failure_threshold']} failures")

    # Show golden patterns in L1
    golden_patterns = validator.search_similar_patterns(
        "def example(): pass",
        max_results=10,
        include_failures=False
    )

    logger.info(f"\nFound {len(golden_patterns)} golden patterns in L1 cache:")
    for pattern in golden_patterns[:3]:
        logger.info(
            f"  - {pattern['id']}: {pattern['success_rate']:.2%} success rate")

    # Show how failures are filtered
    logger.info("\nDemonstrating failure filtering:")
    bad_code = "def broken():\n    return undefined_variable"

    result = validator.check_and_learn(
        bad_code,
        context={"canon_rule_id": "filter_test", "project_context": "demo"}
    )

    logger.info(f"Bad code validation result:")
    logger.info(f"  Valid: {result['is_valid']}")
    logger.info(f"  Matched: {result['matched_pattern'] is not None}")
    logger.info(f"  Source: {result['source']}")


def main():
    """Main execution flow."""
    try:
        # Setup system
        validator, db_manager = setup_system()

        # Run learning loop demonstration
        simulate_learning_loop(validator, iterations=3)

        # Demonstrate meta-learning features
        demonstrate_meta_learning(validator)

        # Final statistics
        logger.info("\n" + "=" * 50)
        logger.info("FINAL SYSTEM STATISTICS")
        logger.info("=" * 50)

        final_stats = validator.get_learning_stats()
        logger.info(f"\nRedis (L1) Stats:")
        if "redis_stats" in final_stats:
            redis_stats = final_stats["redis_stats"]
            logger.info(
                f"  Total patterns: {redis_stats.get('total_patterns', 0)}")
            logger.info(
                f"  Safe patterns: {redis_stats.get('safe_patterns', 0)}")
            logger.info(
                f"  Blocked patterns: {redis_stats.get('blocked_patterns', 0)}")

        logger.info(f"\nQdrant (L2) Stats:")
        if "qdrant_stats" in final_stats:
            qdrant_stats = final_stats["qdrant_stats"]
            logger.info(
                f"  Total vectors: {qdrant_stats.get('total_vectors', 0)}")
            logger.info(
                f"  Successes ingested: {qdrant_stats.get('successes_ingested', 0)}")
            logger.info(
                f"  Failures ingested: {qdrant_stats.get('failures_ingested', 0)}")

        logger.info("\n" + "=" * 50)
        logger.info("CANON VALIDATOR SYSTEM DEMO COMPLETE")
        logger.info("=" * 50)
        logger.info("\nThe system is now running and ready for production use!")
        logger.info("Key features demonstrated:")
        logger.info("  ✓ Hybrid semantic cache (L1 Redis + L2 Qdrant)")
        logger.info("  ✓ AST-based structural validation")
        logger.info("  ✓ Meta-learning with success/failure tracking")
        logger.info("  ✓ Automatic pattern promotion")
        logger.info("  ✓ Failure filtering")
        logger.info("  ✓ Real-time learning updates")

    except Exception as e:
    pass
pass


logger.error(f"System error: {e}")
        raise

    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

