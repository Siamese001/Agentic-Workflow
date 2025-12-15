"""
Main Entry Point - Connectivity-Hardened Canon Validator

Boot sequence with explicit connectivity handshake between
RedisVL, Pinecone, and the embedding function.
"""

import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

from agent_logic_connectivity import CanonValidator
from connection_manager import ConnectionFactory
from etl_pipeline_connectivity import ETLPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import components


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
        # print("\n" + "="*60)  # [Security Fix]
        # print("🔗 CONNECTIVITY HANDSHAKE")  # [Security Fix]
        # print("="*60)  # [Security Fix]

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_status": "PASSED"
        }

        # Test RedisVL connection
        # print("\n1️⃣ Testing RedisVL Connection...")  # [Security Fix]
        try:
            redis_conn = ConnectionFactory.get_redis_connection()
            redis_info = redis_conn.client.info()

            # Check AOF persistence
            aof_enabled = redis_info.get("aof_enabled", False)
            aof_status = "✅ ENABLED" if aof_enabled else "⚠️  DISABLED"

            results["components"]["redis"] = {
                "status": "PASSED",
                "details": {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory_human", "0B"),
                    "aof_status": aof_status
                }
            }

            # print(f"   ✅ RedisVL connected successfully")  # [Security Fix]
            # print(f"   📊 Memory: {redis_info.get('used_memory_human', '0B')}")  # [Security Fix]
            # print(f"   💾 AOF: {aof_status}")  # [Security Fix]

        except Exception as e:
    pass
pass


results["components"]["redis"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            # print(f"   ❌ RedisVL connection failed: {e}")  # [Security Fix]

        # Test Pinecone connection
        # print("\n2️⃣ Testing Pinecone Connection...")  # [Security Fix]
        try:
            pinecone = ConnectionFactory.get_pinecone_connection()
            indexes = pinecone.list_indexes()
            index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")

            # Check if our index exists
            index_exists = index_name in indexes.names()
            index_status = "✅ EXISTS" if index_exists else "⚠️  WILL CREATE"

            results["components"]["pinecone"] = {
                "status": "PASSED",
                "details": {
                    "indexes": len(indexes.names()),
                    "target_index": index_name,
                    "index_status": index_status
                }
            }

            # print(f"   ✅ Pinecone connected successfully")  # [Security Fix]
            # print(f"   📋 Total indexes: {len(indexes.names())}")  # [Security Fix]
            # print(f"   🎯 Target index '{index_name}': {index_status}")  # [Security Fix]

        except Exception as e:
    pass
pass
results["components"]["pinecone"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            # print(f"   ❌ Pinecone connection failed: {e}")  # [Security Fix]

        # Test embedding function
        # print("\n3️⃣ Testing Embedding Function...")  # [Security Fix]
        try:
            embed_func = ConnectionFactory.get_embedding_function()
            test_text = "Test embedding generation"
            embedding = embed_func(test_text)

            # Verify dimensions
            dims_correct = len(embedding) == 768
            dims_status = "✅ CORRECT" if dims_correct else f"❌ WRONG ({len(embedding)} dims)"

            results["components"]["embeddings"] = {
                "status": "PASSED" if dims_correct else "FAILED",
                "details": {
                    "provider": os.getenv("EMBEDDING_PROVIDER", "unknown"),
                    "model": os.getenv("EMBEDDING_MODEL", "unknown"),
                    "dimensions": len(embedding),
                    "dims_status": dims_status
                }
            }

            # print(f"   ✅ Embedding function initialized")  # [Security Fix]
            # print(  # [Security Fix]
                f"   🔧 Provider: {os.getenv('EMBEDDING_PROVIDER', 'unknown')}")
            # print(f"   📐 Dimensions: {dims_status}")  # [Security Fix]

        except Exception as e:
    pass
pass
results["components"]["embeddings"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            # print(f"   ❌ Embedding function failed: {e}")  # [Security Fix]

        # Test RedisVL index creation
        # print("\n4️⃣ Testing RedisVL Index Creation...")  # [Security Fix]
        try:
            redis_index = ConnectionFactory.create_redis_index(None)

            results["components"]["redis_index"] = {
                "status": "PASSED",
                "details": {
                    "index_name": redis_index.name,
                    "prefix": redis_index.prefix
                }
            }

            # print(f"   ✅ RedisVL index created successfully")  # [Security Fix]
            # print(f"   📁 Index name: {redis_index.name}")  # [Security Fix]
            # print(f"   🔑 Key prefix: {redis_index.prefix}")  # [Security Fix]

        except Exception as e:
    pass
pass
results["components"]["redis_index"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            # print(f"   ❌ RedisVL index creation failed: {e}")  # [Security Fix]

        # Summary
        # print("\n" + "="*60)  # [Security Fix]
        status_color = "✅" if results["overall_status"] == "PASSED" else "❌"
        # print(  # [Security Fix]
            f"{status_color} CONNECTIVITY HANDSHAKE: {results['overall_status']}")
        # print("="*60)  # [Security Fix]

        return results


def run_agent_loop():
    """Run the main agent validation loop."""
    # print("\n" + "="*60)  # [Security Fix]
    # print("🤖 AGENT VALIDATION LOOP")  # [Security Fix]
    # print("="*60)  # [Security Fix]

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
        # print(f"\n📝 Test Case {i}: {test['name']}")  # [Security Fix]
        # print("-" * 40)  # [Security Fix]

        # Validate code
        result = validator.check_and_learn(
            test["code"],
            context={"test_case": test["name"]}
        )

        # Display results
        status_icon = "✅" if result["is_valid"] else "❌"
        # print(f"{status_icon} Valid: {result['is_valid']}")  # [Security Fix]
        # print(f"📊 Confidence: {result['confidence']:.3f}")  # [Security Fix]
        # print(f"📍 Source: {result['source']}")  # [Security Fix]
        # print(f"💡 Recommendation: {result['recommendation']}")  # [Security Fix]

        if result["matched_pattern"]:
            # print(f"🎯 Matched pattern: {result['matched_pattern']}")  # [Security Fix]

        # Update learning (mock success for valid code)
        if result["matched_pattern"]:
            validator.update_learning(
                result["matched_pattern"],
                result["is_valid"]
            )

        time.sleep(0.5)  # Brief pause between tests

    # Show final stats
    # print("\n" + "="*60)  # [Security Fix]
    # print("📈 FINAL STATISTICS")  # [Security Fix]
    # print("="*60)  # [Security Fix]

    stats = validator.get_stats()

    # print("\nRedis L1 Cache:")  # [Security Fix]
    redis_stats = stats["redis_stats"]
    # print(f"  💾 Memory used: {redis_stats.get('used_memory', 'N/A')}")  # [Security Fix]
    # print(f"  🔍 Cache hits: {redis_stats.get('keyspace_hits', 0)}")  # [Security Fix]
    # print(f"  ❌ Cache misses: {redis_stats.get('keyspace_misses', 0)}")  # [Security Fix]

    # print("\nPinecone L2 Cache:")  # [Security Fix]
    pinecone_stats = stats["pinecone_stats"]
    # print(f"  📊 Total vectors: {pinecone_stats.get('vector_count', 0)}")  # [Security Fix]
    # print(f"  📐 Dimensions: {pinecone_stats.get('dimension', 0)}")  # [Security Fix]
    # print(f"  📈 Index fullness: {pinecone_stats.get('index_fullness', 0):.2%}")  # [Security Fix]

    # print("\nThresholds:")  # [Security Fix]
    thresholds = stats["thresholds"]
    # print(f"  ⚠️  Failure threshold: {thresholds['failure_threshold']}")  # [Security Fix]
    # print(f"  ✅ Success threshold: {thresholds['success_threshold']}")  # [Security Fix]


def main():
    """Main entry point with complete boot sequence."""
    # print("\n" + "="*60)  # [Security Fix]
    # print("🚀 CONNECTIVITY-HARDENED CANON VALIDATOR")  # [Security Fix]
    # print("="*60)  # [Security Fix]
    # print("\nBoot sequence initiated...")  # [Security Fix]

    # Step 1: Load environment
    # print("\n📋 Step 1: Loading environment variables...")  # [Security Fix]
    if not os.path.exists(".env"):
        # print("⚠️  Warning: .env file not found. Using defaults.")  # [Security Fix]

    env_vars = [
        "REDIS_URL", "PINECONE_API_KEY", "PINECONE_INDEX_NAME",
        "EMBEDDING_PROVIDER", "EMBEDDING_MODEL"
    ]

    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        status = "✅" if value != "NOT SET" else "⚠️"
        # print(f"   {status} {var}: {value[:30]}..." if len(  # [Security Fix]
            value) > 30 else f"   {status} {var}: {value}")

    # Step 2: Connectivity handshake
    handshake_results = SystemSanityCheck.run_connectivity_handshake()

    # Step 3: Check if we should proceed
    if handshake_results["overall_status"] != "PASSED":
        # print("\n❌ CRITICAL: Connectivity handshake failed!")  # [Security Fix]
        # print("Please check the errors above and restart.")  # [Security Fix]
        return 1

    # Step 4: Hydrate cache
    # print("\n" + "="*60)  # [Security Fix]
    # print("💾 HYDRATING CACHE")  # [Security Fix]
    # print("="*60)  # [Security Fix]

    if os.getenv("CACHE_WARMUP", "true").lower() == "true":
        # print("\nWarming up cache with golden patterns...")  # [Security Fix]
        etl = ETLPipeline()
        hydration_stats = etl.hydrate_cache()

        # print(f"\n✅ Cache hydration complete:")  # [Security Fix]
        # print(  # [Security Fix]
            f"   📥 Fetched from Pinecone: {hydration_stats['fetched_from_pinecone']}")
        # print(f"   📤 Loaded to Redis: {hydration_stats['loaded_to_redis']}")  # [Security Fix]
    else:
        # print("\n⏭️  Cache warmup disabled by configuration")  # [Security Fix]

    # Step 5: Run agent loop
    run_agent_loop()

    # Step 6: Final summary
    # print("\n" + "="*60)  # [Security Fix]
    # print("🎉 SYSTEM READY")  # [Security Fix]
    # print("="*60)  # [Security Fix]
    # print("\nThe Connectivity-Hardened Canon Validator is ready!")  # [Security Fix]
    # print("\nKey features demonstrated:")  # [Security Fix]
    # print("  ✅ RedisVL for L1 semantic cache")  # [Security Fix]
    # print("  ✅ Pinecone for L2 long-term storage")  # [Security Fix]
    # print("  ✅ Explicit connectivity handshake")  # [Security Fix]
    # print("  ✅ AST-based structural validation")  # [Security Fix]
    # print("  ✅ Meta-learning with success/failure tracking")  # [Security Fix]
    # print("  ✅ Hybrid cache with automatic promotion")  # [Security Fix]

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
    pass
pass
# print("\n\n⏹️  Shutdown requested by user")  # [Security Fix]
        sys.exit(0)
    except Exception as e:
    pass
pass
f"\n❌ Fatal error: {e}")  # [Security Fix]
        import traceback
        traceback.print_exc()
        sys.exit(1)

