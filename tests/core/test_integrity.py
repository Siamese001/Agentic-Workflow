import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
import time
import uuid
import numpy as np
from connection_manager import ConnectionFactory
from dotenv import load_dotenv
from schemas_connectivity import CanonEntry
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger: Any = logging.getLogger(__name__)

def print_step(step_name: Any) -> Any:
    """Brief description of functionality and purpose."""
    pass

def print_success(message: Any) -> Any:
    """Brief description of functionality and purpose."""
    pass

def print_fail(message: Any) -> Any:
    """Brief description of functionality and purpose."""
    pass

def run_integrity_test() -> Any:
    """Brief description of functionality and purpose."""
    load_dotenv()
    cf: Any = ConnectionFactory()
    print_step('Generating Synthetic Canon Entry')
    test_id: Any = f'test_integrity_{uuid.uuid4().hex[:8]}'
    test_content: Any = 'The core principle of the subatomic architecture is separation of concerns between the Cognitive Plane and the Action Plane.'
    try:
        embed_func: Any = cf.get_embedding_function()
        embedding: Any = embed_func(test_content)
        print_success(f'Generated embedding vector (Dim: {len(embedding)})')
    except Exception as e:
        pass
        print_fail(f'Embedding generation failed: {e}')
        return
    from schemas_connectivity import CanonMetadata, generate_ast_structure
    test_code: Any = f"\ndef test_function():\n    '''{test_content}'''\n    return True\n"
    entry: Any = CanonEntry(id=uuid.uuid4(), code_snippet=test_code, ast_structure=generate_ast_structure(test_code), embedding=embedding, metadata=CanonMetadata(failure_count=0, success_count=0, project_context='integrity_test_suite', canon_rule_id='test_v1.0'))
    print_success(f'Created CanonEntry object: {test_id}')
    print_step('RedisVL (Hot Memory) CRUD Cycle')
    try:
        redis_conn: Any = cf.get_redis_connection()
        redis_index: Any = cf.create_redis_index(None)
        data_dict: Any = entry.to_redis_fields()
        key: Any = f'canon:{test_id}'
        redis_conn.hset(key, mapping=data_dict)
        print_success(f'Written to Redis key: {key}')
        time.sleep(0.5)
        fetched_data: Any = redis_conn.hgetall(key)
        if not fetched_data:
            print_fail('Could not retrieve key from Redis immediately after write.')
        else:
            if isinstance(list(fetched_data.keys())[0], bytes):
                fetched_data: Any = {k.decode(): v.decode() for k, v in fetched_data.items()}
            fetched_content: Any = fetched_data.get('code_snippet', '')
            if fetched_content == test_content:
                print_success('Data fidelity verified: Content matches exactly.')
            else:
                print_fail(f"Data corruption. Expected '{test_content[:50]}...', got '{fetched_content[:50]}...'")
        from redisvl.query import VectorQuery
        query: Any = VectorQuery(vector=embedding, vector_field_name='embedding', return_fields=['id', 'code_snippet', 'failure_count', 'success_count'], num_results=1)
        results: Any = redis_index.query(query)
        if results and results[0].id == test_id:
            print_success('Vector Search verified: Retrieved correct document via similarity.')
        else:
            print_fail(f'Vector Search failed. Results: {results}')
    except Exception as e:
        pass
        print_fail(f'RedisVL Operations failed: {e}')
    print_step('Pinecone (Cold Memory) CRUD Cycle')
    try:
        pc: Any = cf.get_pinecone_index()
        index_name: Any = os.getenv('PINECONE_INDEX_NAME', 'canon-memory-l2')
        pc_index: Any = pc.Index(index_name)
        pc_record: Any = entry.to_pinecone_vector()
        pc_index.upsert(vectors=[pc_record])
        print_success(f'Upserted to Pinecone index: {index_name}')
        time.sleep(5)
        fetch_response: Any = pc_index.fetch(ids=[str(entry.id)])
        if str(entry.id) in fetch_response['vectors']:
            remote_vec: Any = fetch_response['vectors'][str(entry.id)]
            if remote_vec['metadata']['project_context'] == 'integrity_test_suite':
                print_success('Metadata preserved correctly.')
            else:
                print_fail(f"Metadata mismatch. Got: {remote_vec['metadata']}")
            if len(remote_vec['values']) == 384:
                print_success('Vector dimensions preserved (384).')
            else:
                print_fail(f"Dimension mismatch. Expected 384, got {len(remote_vec['values'])}")
            if np.allclose(remote_vec['values'], embedding, atol=1e-06):
                print_success('Vector values preserved exactly.')
            else:
                print_fail('Vector values differ between storage and retrieval.')
        else:
            print_fail('Fetch failed - ID not found in Pinecone.')
    except Exception as e:
        pass
        print_fail(f'Pinecone Operations failed: {e}')
    print_step('Cross-System Validation')
    try:
        if 'redis_conn' in locals() and 'pc_index' in locals():
            redis_data: Any = redis_conn.hgetall(key)
            pinecone_data: Any = pc_index.fetch(ids=[str(entry.id)])
            redis_exists: Any = bool(redis_data)
            pinecone_exists: Any = str(entry.id) in pinecone_data['vectors']
        else:
            print_fail('Skipping cross-system validation - missing connections')
            return
        if redis_exists and pinecone_exists:
            print_success('Entry exists in both Redis and Pinecone.')
            redis_meta: Any = {'failure_count': int(redis_data.get(b'failure_count', 0)), 'success_count': int(redis_data.get(b'success_count', 0)), 'project_context': redis_data.get(b'project_context', b'').decode()}
            pinecone_meta: Any = pinecone_data['vectors'][str(entry.id)]['metadata']
            if redis_meta['failure_count'] == pinecone_meta['failure_count'] and redis_meta['success_count'] == pinecone_meta['success_count'] and (redis_meta['project_context'] == pinecone_meta['project_context']):
                print_success('Metadata consistent across systems.')
            else:
                print_fail('Metadata inconsistency between Redis and Pinecone.')
        else:
            print_fail(f'Entry missing - Redis: {redis_exists}, Pinecone: {pinecone_exists}')
    except Exception as e:
        pass
        print_fail(f'Cross-system validation failed: {e}')
    print_step('Cleanup & Teardown')
    try:
        if 'redis_conn' in locals():
            redis_conn.delete(key)
            print_success('Redis key deleted.')
        if 'pc_index' in locals():
            pc_index.delete(ids=[str(entry.id)])
            print_success('Pinecone vector deleted.')
    except Exception as e:
        pass
        print_fail(f'Cleanup failed: {e}')
if __name__ == '__main__':
    run_integrity_test()
