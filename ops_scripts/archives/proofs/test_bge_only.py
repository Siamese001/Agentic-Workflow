#!/usr/bin/env python
"""Quick test of BGE-only GPTCache implementation"""

import sys
import time

print('='*60)
print('BGE-ONLY GPTCACHE TEST')
print('='*60)

# Test 1: Import
print('\n[1] Testing imports...')
try:
    from agentic_core.L4_state.cache.gptcache_client import BGEEmbedding, GPTCacheClient
    print('   ✓ Imports successful')
except Exception as e:
    print(f'   ✗ Import failed: {e}')
    sys.exit(1)

# Test 2: BGE Embedding directly
print('\n[2] Testing BGE embedding...')
try:
    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

    start = time.time()
    embedding = bmg_embed_text("How do I configure Redis?")
    elapsed = time.time() - start

    if embedding:
        print(f'   ✓ BGE embedding works: {len(embedding)} dims in {elapsed*1000:.2f}ms')
    else:
        print('   ✗ BGE embedding returned None')
except Exception as e:
    print(f'   ✗ BGE embedding failed: {e}')
    import traceback
    traceback.print_exc()

# Test 3: BGEEmbedding wrapper
print('\n[3] Testing BGEEmbedding wrapper...')
try:
    bge = BGEEmbedding(model_name="BAAI/bge-m3")

    start = time.time()
    embedding = bge.to_embeddings("How do I configure Redis?")
    elapsed = time.time() - start

    if embedding and len(embedding) == 1024:
        print(f'   ✓ BGEEmbedding wrapper works: {len(embedding)} dims in {elapsed*1000:.2f}ms')
    else:
        print(f'   ✗ BGEEmbedding returned wrong dimensions: {len(embedding) if embedding else "None"}')
except Exception as e:
    print(f'   ✗ BGEEmbedding wrapper failed: {e}')
    import traceback
    traceback.print_exc()

# Test 4: GPTCache initialization (without OpenAI)
print('\n[4] Testing GPTCache initialization (BGE-only)...')
try:
    cache = GPTCacheClient(
        cache_dir="artifacts/gptcache_bge_test",
        similarity_threshold=0.95,
        embedding_provider="bge-m3",
        embedding_model="BAAI/bge-m3",
    )

    if cache._cache != "mock":
        print('   ✓ GPTCache initialized with BGE-only (not mock)')
        print(f'   ✓ Provider: {cache.embedding_provider}')
        print(f'   ✓ Model: {cache.embedding_model}')
    else:
        print('   ⚠ GPTCache using mock mode (gptcache may not be installed)')

except Exception as e:
    print(f'   ✗ GPTCache initialization failed: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*60)
print('BGE-ONLY TEST COMPLETE')
print('='*60)
