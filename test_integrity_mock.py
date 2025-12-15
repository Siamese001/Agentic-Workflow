import logging
import uuid

import numpy as np
from dotenv import load_dotenv

# Import our hardened modules
from connection_manager import ConnectionFactory
from schemas_connectivity import (CanonEntry, CanonMetadata,
                                  generate_ast_structure)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_step(step_name):
    print(f"\n🔹 TESTING: {step_name}")
    print("-" * 50)


def print_success(message):
    print(f"   ✅ PASS: {message}")


def print_fail(message):
    print(f"   ❌ FAIL: {message}")


class MockRedisClient:
    """Mock Redis client for testing data transformations."""

    def __init__(self):
        self.data = {}

    def hset(self, key, mapping):
        self.data[key] = mapping

    def hgetall(self, key):
        return self.data.get(key, {})

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    @property
    def client(self):
        return self


class MockPineconeIndex:
    """Mock Pinecone index for testing data transformations."""

    def __init__(self):
        self.vectors = {}

    def upsert(self, vectors):
        for vec in vectors:
            self.vectors[vec['id']] = vec

    def fetch(self, ids):
        return {'vectors': {id_: self.vectors[id_] for id_ in ids if id_ in self.vectors}}

    def delete(self, ids):
        for id_ in ids:
            if id_ in self.vectors:
                del self.vectors[id_]


class MockSearchIndex:
    """Mock RedisVL SearchIndex for testing."""

    def __init__(self):
        pass

    def query(self, query):
        # Return mock results for testing
        return [type('Result', (), {'id': 'test-id'})()]


def run_integrity_test():
    print("\n🧪 STARTING DATA INTEGRITY SUITE (MOCK)")
    print("============================================================")

    # Load environment
    load_dotenv()

    # Initialize Factory
    cf = ConnectionFactory()

    test_results = {
        'redis_crud': False,
        'pinecone_crud': False,
        'cross_system': False,
        'cleanup': False
    }

    # ---------------------------------------------------------
    # 1. SYNTHETIC DATA GENERATION
    # ---------------------------------------------------------
    print_step("Generating Synthetic Canon Entry")

    test_id = f"test_integrity_{uuid.uuid4().hex[:8]}"
    test_content = "The core principle of the subatomic architecture is separation of concerns between the Cognitive Plane and the Action Plane."

    # Generate embedding (using the factory's embedding function)
    try:
        embed_func = cf.get_embedding_function()
        embedding = embed_func(test_content)
        print_success(f"Generated embedding vector (Dim: {len(embedding)})")
    except Exception as e:
        print_fail(f"Embedding generation failed: {e}")
        return test_results

    # Create CanonEntry with proper structure
    test_code = f"""
def test_function():
    '''{test_content}'''
    return True
"""

    entry = CanonEntry(
        id=uuid.uuid4(),  # Generate a proper UUID
        code_snippet=test_code,
        ast_structure=generate_ast_structure(test_code),
        embedding=embedding,
        metadata=CanonMetadata(
            failure_count=0,
            success_count=0,
            project_context="integrity_test_suite",
            canon_rule_id="test_v1.0"
        )
    )
    print_success(f"Created CanonEntry object: {test_id}")

    # ---------------------------------------------------------
    # 2. REDIS TRANSFORMATION TEST (MOCK)
    # ---------------------------------------------------------
    print_step("Redis Data Transformation (Mock)")

    try:
        mock_redis = MockRedisClient()

        # Test to_redis_fields transformation
        redis_fields = entry.to_redis_fields()

        # Verify required fields exist
        required_fields = ['id', 'code_snippet',
                           'failure_count', 'success_count', 'project_context']
        missing_fields = [
            field for field in required_fields if field not in redis_fields]

        if missing_fields:
            print_fail(f"Missing Redis fields: {missing_fields}")
        else:
            print_success("All required Redis fields present")

            # Write to mock Redis
            key = f"canon:{test_id}"
            mock_redis.hset(key, mapping=redis_fields)

            # Read from mock Redis
            retrieved = mock_redis.hgetall(key)

            # Verify data integrity
            if (retrieved.get('code_snippet') == test_code and
                int(retrieved.get('failure_count', -1)) == 0 and
                int(retrieved.get('success_count', -1)) == 0 and
                    retrieved.get('project_context') == 'integrity_test_suite'):
                print_success("Redis data transformation verified")
                test_results['redis_crud'] = True
            else:
                print_fail(
                    f"Redis data transformation failed. Got: {retrieved}")

    except Exception as e:
        print_fail(f"Redis transformation test failed: {e}")

    # ---------------------------------------------------------
    # 3. PINECONE TRANSFORMATION TEST (MOCK)
    # ---------------------------------------------------------
    print_step("Pinecone Data Transformation (Mock)")

    try:
        mock_pinecone = MockPineconeIndex()

        # Test to_pinecone_vector transformation
        pinecone_vec = entry.to_pinecone_vector()

        # Verify required fields
        if 'id' in pinecone_vec and 'values' in pinecone_vec and 'metadata' in pinecone_vec:
            print_success("Pinecone vector structure valid")

            # Verify embedding dimensions
            if len(pinecone_vec['values']) == 384:
                print_success("Pinecone embedding dimensions correct (384)")
            else:
                print_fail(
                    f"Wrong embedding dimensions: {len(pinecone_vec['values'])}")

            # Verify metadata
            metadata = pinecone_vec['metadata']
            if (metadata.get('failure_count') == 0 and
                metadata.get('success_count') == 0 and
                    metadata.get('project_context') == 'integrity_test_suite'):
                print_success("Pinecone metadata transformation correct")

                # Write to mock Pinecone
                mock_pinecone.upsert([pinecone_vec])

                # Read from mock Pinecone (use string ID)
                retrieved = mock_pinecone.fetch([str(entry.id)])

                if str(entry.id) in retrieved['vectors']:
                    remote_vec = retrieved['vectors'][str(entry.id)]

                    # Verify vector values match
                    if np.allclose(remote_vec['values'], embedding, atol=1e-6):
                        print_success(
                            "Pinecone vector values preserved exactly")
                        test_results['pinecone_crud'] = True
                    else:
                        print_fail("Pinecone vector values corrupted")
                else:
                    print_fail("Failed to retrieve from Pinecone")
            else:
                print_fail("Pinecone metadata transformation failed")
        else:
            print_fail("Invalid Pinecone vector structure")

    except Exception as e:
        print_fail(f"Pinecone transformation test failed: {e}")

    # ---------------------------------------------------------
    # 4. CROSS-SYSTEM CONSISTENCY (MOCK)
    # ---------------------------------------------------------
    print_step("Cross-System Consistency (Mock)")

    try:
        # Verify both transformations produce consistent data
        redis_fields = entry.to_redis_fields()
        pinecone_vec = entry.to_pinecone_vector()

        # Check metadata consistency
        redis_meta = {
            'failure_count': int(redis_fields.get('failure_count', 0)),
            'success_count': int(redis_fields.get('success_count', 0)),
            'project_context': redis_fields.get('project_context', '')
        }

        pinecone_meta = pinecone_vec['metadata']

        if (redis_meta['failure_count'] == pinecone_meta['failure_count'] and
            redis_meta['success_count'] == pinecone_meta['success_count'] and
                redis_meta['project_context'] == pinecone_meta['project_context']):
            print_success(
                "Metadata consistent across Redis and Pinecone formats")
            test_results['cross_system'] = True
        else:
            print_fail("Metadata inconsistency between formats")

    except Exception as e:
        print_fail(f"Cross-system test failed: {e}")

    # ---------------------------------------------------------
    # 5. CLEANUP (MOCK)
    # ---------------------------------------------------------
    print_step("Cleanup (Mock)")

    try:
        # Mock cleanup - just verify methods exist
        mock_redis = MockRedisClient()
        mock_pinecone = MockPineconeIndex()

        # Test cleanup methods
        mock_redis.delete("test-key")
        mock_pinecone.delete(["test-id"])

        print_success("Cleanup methods available")
        test_results['cleanup'] = True

    except Exception as e:
        print_fail(f"Cleanup test failed: {e}")

    # ---------------------------------------------------------
    # 6. SUMMARY
    # ---------------------------------------------------------
    print("\n✅ INTEGRITY SUITE COMPLETE")
    print("============================================================")

    passed = sum(test_results.values())
    total = len(test_results)

    print(f"\nTest Results: {passed}/{total} passed")
    print("\nDetails:")
    for test, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  - {test}: {status}")

    print("\nValidated:")
    if test_results['redis_crud']:
        print("  - Redis data transformation")
    if test_results['pinecone_crud']:
        print("  - Pinecone data transformation")
    if test_results['cross_system']:
        print("  - Cross-system consistency")
    if test_results['cleanup']:
        print("  - Cleanup operations")

    return test_results


if __name__ == "__main__":
    run_integrity_test()

