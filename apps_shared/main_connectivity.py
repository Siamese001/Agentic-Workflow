"""
Main Entry Point - Connectivity-Hardened Canon Validator

Boot sequence with explicit connectivity handshake between
RedisVL, Pinecone, and the embedding function.
"""
from typing import Any, Optional, Protocol, Dict, List


import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

# Import components
from agent_logic_connectivity import CanonValidator
from connection_manager import ConnectionFactory
from etl_pipeline_connectivity import ETLPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemSanityCheck:
    """Comprehensive system health checker."""

    @staticmethod
    def run_connectivity_handshake() -> Dict[str, Any]:
        """
        Perform the connectivity handshake between all components.

        This is the critical step that ensures all APIs are properly
        wired up before the system starts.

        Returns:
            Dictionary with handshake results
        """
        # [Security Fix] Using logger instead of print for production logs
        logger.info("="*60)
        logger.info("🔗 CONNECTIVITY HANDSHAKE")
        logger.info("="*60)

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_status": "PASSED"
        }

        # Test RedisVL connection
        logger.info("1️⃣ Testing RedisVL Connection...")
        try:
            # Fix: ConnectionFactory.get_redis_connection() now returns the client directly
            redis_client = ConnectionFactory.get_redis_connection()
            redis_info = redis_client.info()  # This now works because redis_client is an object

            # Check AOF persistence
            aof_enabled = redis_info.get("aof_enabled", False)
            aof_status = "[OK] ENABLED" if aof_enabled else "[!]  DISABLED"

            results["components"]["redis"] = {
                "status": "PASSED",
                "details": {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory_human", "0B"),
                    "aof_status": aof_status
                }
            }

            logger.info("   [OK] RedisVL connected successfully")
            logger.info(f"   [STATS] Memory: {redis_info.get('used_memory_human', '0B')}")
            logger.info(f"   [SAVE] AOF: {aof_status}")

        except Exception as e:
            results["components"]["redis"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            logger.error(f"   [X] RedisVL connection failed: {e}")

        # Test Pinecone connection
        logger.info("2️⃣ Testing Pinecone Connection...")
        try:
            pc = ConnectionFactory.get_pinecone_client()
            index_list = pc.list_indexes()
            index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")

            # Check if our index exists
            index_exists = index_name in index_list
            index_status = "[OK] EXISTS" if index_exists else "[!]  WILL CREATE"

            results["components"]["pinecone"] = {
                "status": "PASSED",
                "details": {
                    "indexes": len(index_list.names()),
                    "target_index": index_name,
                    "index_status": index_status
                }
            }

            logger.info("   [OK] Pinecone connected successfully")
            logger.info(f"   [PLAN] Total indexes: {len(index_list.names())}")
            logger.info(f"   🎯 Target index '{index_name}': {index_status}")

        except Exception as e:
            results["components"]["pinecone"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            logger.error(f"   [X] Pinecone connection failed: {e}")

        # Test embedding function
        logger.info("3️⃣ Testing Embedding Function...")
        try:
            embed_func = ConnectionFactory.get_embedding_function()
            test_text = "Test embedding generation"
            embedding = embed_func(test_text)

            # Verify dimensions
            dims_correct = len(embedding) == 768
            dims_status = "[OK] CORRECT" if dims_correct else f"[X] WRONG ({len(embedding)} dims)"

            results["components"]["embeddings"] = {
                "status": "PASSED" if dims_correct else "FAILED",
                "details": {
                    "provider": os.getenv("EMBEDDING_PROVIDER", "unknown"),
                    "model": os.getenv("EMBEDDING_MODEL", "unknown"),
                    "dimensions": len(embedding),
                    "dims_status": dims_status
                }
            }

            logger.info("   [OK] Embedding function initialized")
            logger.info(f"   [+] Provider: {os.getenv('EMBEDDING_PROVIDER', 'unknown')}")
            logger.info(f"   📐 Dimensions: {dims_status}")

        except Exception as e:
            results["components"]["embeddings"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            logger.error(f"   [X] Embedding function failed: {e}")

        # Test RedisVL index creation
        logger.info("4️⃣ Testing RedisVL Index Creation...")
        try:
            redis_index = ConnectionFactory.create_redis_index(None)

            results["components"]["redis_index"] = {
                "status": "PASSED",
                "details": {
                    "index_name": redis_index.name,
                    "prefix": redis_index.prefix
                }
            }

            logger.info("   [OK] RedisVL index created successfully")
            logger.info(f"   📁 Index name: {redis_index.name}")
            logger.info(f"   🔑 Key prefix: {redis_index.prefix}")

        except Exception as e:
            results["components"]["redis_index"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            logger.error(f"   [X] RedisVL index creation failed: {e}")

        # Summary
        logger.info("="*60)
        status_color = "[OK]" if results["overall_status"] == "PASSED" else "[X]"
        logger.info(f"{status_color} CONNECTIVITY HANDSHAKE: {results['overall_status']}")
        logger.info("="*60)

        return results


def run_agent_loop():
    """Run the main agent validation loop."""
    logger.info("="*60)
    logger.info("🤖 AGENT VALIDATION LOOP")
    logger.info("="*60)

    # Initialize validator
    validator = CanonValidator()

    # Test cases
    test_cases = [
        {
            "name": "Valid Function",
            "code": """
def calculate_average(numbers):
    \"\"\"Calculate average of a list of numbers.\"\"\"
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
""",
            "expected": "valid"
        },
        {
            "name": "Syntax Error",
            "code": """
def broken_function():
    return undefined_variable
""",
            "expected": "invalid"
        },
        {
            "name": "New Pattern",
            "code": """
async def fetch_data(url):
    \"\"\"Fetch data asynchronously.\"\"\"
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
""",
            "expected": "new"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        logger.info(f"\n📝 Test Case {i}: {test['name']}")
        logger.info("-" * 40)

        # Validate code
        result = validator.check_and_learn(
            test["code"],
            context={"test_case": test["name"]}
        )

        # Display results
        status_icon = "[OK]" if result["is_valid"] else "[X]"
        logger.info(f"{status_icon} Valid: {result['is_valid']}")
        logger.info(f"[STATS] Confidence: {result['confidence']:.3f}")
        logger.info(f"📍 Source: {result['source']}")
        logger.info(f"💡 Recommendation: {result['recommendation']}")

        if result["matched_pattern"]:
            logger.info(f"🎯 Matched pattern: {result['matched_pattern']}")
            # Update learning (mock success for valid code)
            validator.update_learning(
                result["matched_pattern"],
                result["is_valid"]
            )

        time.sleep(0.5)

    # Show final stats
    logger.info("="*60)
    logger.info("📈 FINAL STATISTICS")
    logger.info("="*60)

    stats = validator.get_stats()

    logger.info("\nRedis L1 Cache:")
    redis_stats = stats["redis_stats"]
    logger.info(f"   [SAVE] Memory used: {redis_stats.get('used_memory', 'N/A')}")
    logger.info(f"   [SCAN] Cache hits: {redis_stats.get('keyspace_hits', 0)}")
    logger.info(f"   [X] Cache misses: {redis_stats.get('keyspace_misses', 0)}")

    logger.info("\nPinecone L2 Cache:")
    pinecone_stats = stats["pinecone_stats"]
    logger.info(f"   [STATS] Total vectors: {pinecone_stats.get('vector_count', 0)}")
    logger.info(f"   📐 Dimensions: {pinecone_stats.get('dimension', 0)}")
    logger.info(f"   📈 Index fullness: {pinecone_stats.get('index_fullness', 0):.2%}")

    logger.info("\nThresholds:")
    thresholds = stats["thresholds"]
    logger.info(f"   [!]  Failure threshold: {thresholds['failure_threshold']}")
    logger.info(f"   [OK] Success threshold: {thresholds['success_threshold']}")


def main():
    """Main entry point with complete boot sequence."""
    logger.info("="*60)
    logger.info("[START] CONNECTIVITY-HARDENED CANON VALIDATOR")
    logger.info("="*60)
    logger.info("Boot sequence initiated...")

    # Step 1: Load environment
    logger.info("[PLAN] Step 1: Loading environment variables...")
    if not os.path.exists(".env"):
        logger.warning("[!]  Warning: .env file not found. Using defaults.")

    env_vars = [
        "REDIS_URL", "PINECONE_API_KEY", "PINECONE_INDEX_NAME",
        "EMBEDDING_PROVIDER", "EMBEDDING_MODEL"
    ]

    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        status = "[OK]" if value != "NOT SET" else "[!]"
        display_val = f"{value[:30]}..." if len(value) > 30 else value
        logger.info(f"   {status} {var}: {display_val}")

    # Step 2: Connectivity handshake
    handshake_results = SystemSanityCheck.run_connectivity_handshake()

    # Step 3: Check if we should proceed
    if handshake_results["overall_status"] != "PASSED":
        logger.error("[X] CRITICAL: Connectivity handshake failed!")
        logger.error("Please check the errors above and restart.")
        return 1

    # Step 4: Hydrate cache
    logger.info("="*60)
    logger.info("[SAVE] HYDRATING CACHE")
    logger.info("="*60)

    if os.getenv("CACHE_WARMUP", "true").lower() == "true":
        logger.info("Warming up cache with golden patterns...")
        etl = ETLPipeline()
        hydration_stats = etl.hydrate_cache()

        logger.info("[OK] Cache hydration complete:")
        logger.info(f"   📥 Fetched from Pinecone: {hydration_stats['fetched_from_pinecone']}")
        logger.info(f"   📤 Loaded to Redis: {hydration_stats['loaded_to_redis']}")
    else:
        logger.info("⏭️  Cache warmup disabled by configuration")

    # Step 5: Run agent loop
    run_agent_loop()

    # Step 6: Final summary
    logger.info("="*60)
    logger.info("🎉 SYSTEM READY")
    logger.info("="*60)
    logger.info("The Connectivity-Hardened Canon Validator is ready!")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("⏹️  Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[X] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

