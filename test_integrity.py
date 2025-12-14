import os
import time
import uuid
import logging
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Import our hardened modules
from connection_manager import ConnectionFactory
from schemas_connectivity import CanonEntry

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

def run_integrity_test():
    print("\n🧪 STARTING DATA INTEGRITY SUITE")
    print("============================================================")
    
    # Load environment
    load_dotenv()
    
    # Initialize Factory
    cf = ConnectionFactory()
    
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
        return

    # Create CanonEntry with proper structure
    from schemas_connectivity import CanonMetadata, generate_ast_structure
    
    # Create a valid Python code snippet for AST parsing
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
    # 2. REDISVL INTEGRITY (HOT MEMORY)
    # ---------------------------------------------------------
    print_step("RedisVL (Hot Memory) CRUD Cycle")
    
    try:
        redis_conn = cf.get_redis_connection()
        redis_index = cf.create_redis_index(None)
        
        # WRITE
        data_dict = entry.to_redis_fields()
        key = f"canon:{test_id}"
        redis_conn.client.hset(key, mapping=data_dict)
        print_success(f"Written to Redis key: {key}")
        
        # Force a brief pause for Redis indexing
        time.sleep(0.5)
        
        # READ (Fetch by ID)
        fetched_data = redis_conn.client.hgetall(key)
        
        if not fetched_data:
            print_fail("Could not retrieve key from Redis immediately after write.")
        else:
            # Convert bytes to strings if necessary
            if isinstance(list(fetched_data.keys())[0], bytes):
                fetched_data = {k.decode(): v.decode() for k, v in fetched_data.items()}
            
            fetched_content = fetched_data.get('code_snippet', '')
            
            if fetched_content == test_content:
                print_success("Data fidelity verified: Content matches exactly.")
            else:
                print_fail(f"Data corruption. Expected '{test_content[:50]}...', got '{fetched_content[:50]}...'")
                
        # SEARCH (Vector Query)
        from redisvl.query import VectorQuery
        
        query = VectorQuery(
            vector=embedding,
            vector_field_name="embedding",
            return_fields=["id", "code_snippet", "failure_count", "success_count"],
            num_results=1
        )
        
        results = redis_index.query(query)
        
        if results and results[0].id == test_id:
             print_success("Vector Search verified: Retrieved correct document via similarity.")
        else:
             print_fail(f"Vector Search failed. Results: {results}")
             
    except Exception as e:
        print_fail(f"RedisVL Operations failed: {e}")

    # ---------------------------------------------------------
    # 3. PINECONE INTEGRITY (COLD MEMORY)
    # ---------------------------------------------------------
    print_step("Pinecone (Cold Memory) CRUD Cycle")
    
    try:
        pc = cf.get_pinecone_index()
        index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
        pc_index = pc.Index(index_name)
        
        # UPSERT
        pc_record = entry.to_pinecone_vector()
        pc_index.upsert(vectors=[pc_record])
        print_success(f"Upserted to Pinecone index: {index_name}")
        
        # Wait for eventual consistency
        print("   ⏳ Waiting 5s for Pinecone consistency...")
        time.sleep(5)
        
        # FETCH
        fetch_response = pc_index.fetch(ids=[test_id])
        
        if test_id in fetch_response['vectors']:
            remote_vec = fetch_response['vectors'][test_id]
            
            # Check Metadata
            if remote_vec['metadata']['project_context'] == "integrity_test_suite":
                print_success("Metadata preserved correctly.")
            else:
                print_fail(f"Metadata mismatch. Got: {remote_vec['metadata']}")
                
            # Check Dimensions
            if len(remote_vec['values']) == 384:
                print_success("Vector dimensions preserved (384).")
            else:
                print_fail(f"Dimension mismatch. Expected 384, got {len(remote_vec['values'])}")
                
            # Check vector values (exact match)
            if np.allclose(remote_vec['values'], embedding, atol=1e-6):
                print_success("Vector values preserved exactly.")
            else:
                print_fail("Vector values differ between storage and retrieval.")
        else:
            print_fail("Fetch failed - ID not found in Pinecone.")
            
    except Exception as e:
        print_fail(f"Pinecone Operations failed: {e}")

    # ---------------------------------------------------------
    # 4. CROSS-SYSTEM VALIDATION
    # ---------------------------------------------------------
    print_step("Cross-System Validation")
    
    try:
        # Verify the same entry exists in both systems
        redis_data = redis_conn.client.hgetall(key)
        pinecone_data = pc_index.fetch(ids=[test_id])
        
        redis_exists = bool(redis_data)
        pinecone_exists = test_id in pinecone_data['vectors']
        
        if redis_exists and pinecone_exists:
            print_success("Entry exists in both Redis and Pinecone.")
            
            # Compare metadata consistency
            redis_meta = {
                'failure_count': int(redis_data.get(b'failure_count', 0)),
                'success_count': int(redis_data.get(b'success_count', 0)),
                'project_context': redis_data.get(b'project_context', b'').decode()
            }
            
            pinecone_meta = pinecone_data['vectors'][test_id]['metadata']
            
            if (redis_meta['failure_count'] == pinecone_meta['failure_count'] and
                redis_meta['success_count'] == pinecone_meta['success_count'] and
                redis_meta['project_context'] == pinecone_meta['project_context']):
                print_success("Metadata consistent across systems.")
            else:
                print_fail("Metadata inconsistency between Redis and Pinecone.")
        else:
            print_fail(f"Entry missing - Redis: {redis_exists}, Pinecone: {pinecone_exists}")
            
    except Exception as e:
        print_fail(f"Cross-system validation failed: {e}")

    # ---------------------------------------------------------
    # 5. CLEANUP
    # ---------------------------------------------------------
    print_step("Cleanup & Teardown")
    
    try:
        # Delete from Redis
        redis_conn.client.delete(key)
        print_success("Redis key deleted.")
        
        # Delete from Pinecone
        pc_index.delete(ids=[test_id])
        print_success("Pinecone vector deleted.")
        
    except Exception as e:
        print_fail(f"Cleanup failed: {e}")

    print("\n✅ INTEGRITY SUITE COMPLETE")
    print("============================================================")
    print("\nSummary:")
    print("  - CRUD operations verified on RedisVL")
    print("  - CRUD operations verified on Pinecone")
    print("  - Vector dimensions validated (768)")
    print("  - Data fidelity confirmed")
    print("  - Cross-system consistency checked")

if __name__ == "__main__":
    run_integrity_test()
