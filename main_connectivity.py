"""
Main Entry Point - Connectivity-Hardened Canon Validator

Boot sequence with explicit connectivity handshake between
RedisVL, Pinecone, and the embedding function.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import components
from connection_manager import ConnectionFactory
from etl_pipeline_connectivity import ETLPipeline, hydrate_cache
from agent_logic_connectivity import CanonValidator
from schemas_connectivity import generate_ast_structure, validate_ast_integrity


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
        print("\n" + "="*60)
        print("🔗 CONNECTIVITY HANDSHAKE")
        print("="*60)
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_status": "PASSED"
        }
        
        # Test RedisVL connection
        print("\n1️⃣ Testing RedisVL Connection...")
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
            
            print(f"   ✅ RedisVL connected successfully")
            print(f"   📊 Memory: {redis_info.get('used_memory_human', '0B')}")
            print(f"   💾 AOF: {aof_status}")
            
        except Exception as e:
            results["components"]["redis"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            print(f"   ❌ RedisVL connection failed: {e}")
        
        # Test Pinecone connection
        print("\n2️⃣ Testing Pinecone Connection...")
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
            
            print(f"   ✅ Pinecone connected successfully")
            print(f"   📋 Total indexes: {len(indexes.names())}")
            print(f"   🎯 Target index '{index_name}': {index_status}")
            
        except Exception as e:
            results["components"]["pinecone"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            print(f"   ❌ Pinecone connection failed: {e}")
        
        # Test embedding function
        print("\n3️⃣ Testing Embedding Function...")
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
            
            print(f"   ✅ Embedding function initialized")
            print(f"   🔧 Provider: {os.getenv('EMBEDDING_PROVIDER', 'unknown')}")
            print(f"   📐 Dimensions: {dims_status}")
            
        except Exception as e:
            results["components"]["embeddings"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            print(f"   ❌ Embedding function failed: {e}")
        
        # Test RedisVL index creation
        print("\n4️⃣ Testing RedisVL Index Creation...")
        try:
            redis_index = ConnectionFactory.create_redis_index(None)
            
            results["components"]["redis_index"] = {
                "status": "PASSED",
                "details": {
                    "index_name": redis_index.name,
                    "prefix": redis_index.prefix
                }
            }
            
            print(f"   ✅ RedisVL index created successfully")
            print(f"   📁 Index name: {redis_index.name}")
            print(f"   🔑 Key prefix: {redis_index.prefix}")
            
        except Exception as e:
            results["components"]["redis_index"] = {
                "status": "FAILED",
                "error": str(e)
            }
            results["overall_status"] = "FAILED"
            print(f"   ❌ RedisVL index creation failed: {e}")
        
        # Summary
        print("\n" + "="*60)
        status_color = "✅" if results["overall_status"] == "PASSED" else "❌"
        print(f"{status_color} CONNECTIVITY HANDSHAKE: {results['overall_status']}")
        print("="*60)
        
        return results


def run_agent_loop():
    """Run the main agent validation loop."""
    print("\n" + "="*60)
    print("🤖 AGENT VALIDATION LOOP")
    print("="*60)
    
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
        print(f"\n📝 Test Case {i}: {test['name']}")
        print("-" * 40)
        
        # Validate code
        result = validator.check_and_learn(
            test["code"],
            context={"test_case": test["name"]}
        )
        
        # Display results
        status_icon = "✅" if result["is_valid"] else "❌"
        print(f"{status_icon} Valid: {result['is_valid']}")
        print(f"📊 Confidence: {result['confidence']:.3f}")
        print(f"📍 Source: {result['source']}")
        print(f"💡 Recommendation: {result['recommendation']}")
        
        if result["matched_pattern"]:
            print(f"🎯 Matched pattern: {result['matched_pattern']}")
        
        # Update learning (mock success for valid code)
        if result["matched_pattern"]:
            validator.update_learning(
                result["matched_pattern"],
                result["is_valid"]
            )
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Show final stats
    print("\n" + "="*60)
    print("📈 FINAL STATISTICS")
    print("="*60)
    
    stats = validator.get_stats()
    
    print("\nRedis L1 Cache:")
    redis_stats = stats["redis_stats"]
    print(f"  💾 Memory used: {redis_stats.get('used_memory', 'N/A')}")
    print(f"  🔍 Cache hits: {redis_stats.get('keyspace_hits', 0)}")
    print(f"  ❌ Cache misses: {redis_stats.get('keyspace_misses', 0)}")
    
    print("\nPinecone L2 Cache:")
    pinecone_stats = stats["pinecone_stats"]
    print(f"  📊 Total vectors: {pinecone_stats.get('vector_count', 0)}")
    print(f"  📐 Dimensions: {pinecone_stats.get('dimension', 0)}")
    print(f"  📈 Index fullness: {pinecone_stats.get('index_fullness', 0):.2%}")
    
    print("\nThresholds:")
    thresholds = stats["thresholds"]
    print(f"  ⚠️  Failure threshold: {thresholds['failure_threshold']}")
    print(f"  ✅ Success threshold: {thresholds['success_threshold']}")


def main():
    """Main entry point with complete boot sequence."""
    print("\n" + "="*60)
    print("🚀 CONNECTIVITY-HARDENED CANON VALIDATOR")
    print("="*60)
    print("\nBoot sequence initiated...")
    
    # Step 1: Load environment
    print("\n📋 Step 1: Loading environment variables...")
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found. Using defaults.")
    
    env_vars = [
        "REDIS_URL", "PINECONE_API_KEY", "PINECONE_INDEX_NAME",
        "EMBEDDING_PROVIDER", "EMBEDDING_MODEL"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        status = "✅" if value != "NOT SET" else "⚠️"
        print(f"   {status} {var}: {value[:30]}..." if len(value) > 30 else f"   {status} {var}: {value}")
    
    # Step 2: Connectivity handshake
    handshake_results = SystemSanityCheck.run_connectivity_handshake()
    
    # Step 3: Check if we should proceed
    if handshake_results["overall_status"] != "PASSED":
        print("\n❌ CRITICAL: Connectivity handshake failed!")
        print("Please check the errors above and restart.")
        return 1
    
    # Step 4: Hydrate cache
    print("\n" + "="*60)
    print("💾 HYDRATING CACHE")
    print("="*60)
    
    if os.getenv("CACHE_WARMUP", "true").lower() == "true":
        print("\nWarming up cache with golden patterns...")
        etl = ETLPipeline()
        hydration_stats = etl.hydrate_cache()
        
        print(f"\n✅ Cache hydration complete:")
        print(f"   📥 Fetched from Pinecone: {hydration_stats['fetched_from_pinecone']}")
        print(f"   📤 Loaded to Redis: {hydration_stats['loaded_to_redis']}")
    else:
        print("\n⏭️  Cache warmup disabled by configuration")
    
    # Step 5: Run agent loop
    run_agent_loop()
    
    # Step 6: Final summary
    print("\n" + "="*60)
    print("🎉 SYSTEM READY")
    print("="*60)
    print("\nThe Connectivity-Hardened Canon Validator is ready!")
    print("\nKey features demonstrated:")
    print("  ✅ RedisVL for L1 semantic cache")
    print("  ✅ Pinecone for L2 long-term storage")
    print("  ✅ Explicit connectivity handshake")
    print("  ✅ AST-based structural validation")
    print("  ✅ Meta-learning with success/failure tracking")
    print("  ✅ Hybrid cache with automatic promotion")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
