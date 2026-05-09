# BGE-M3 Model Configuration

> Deferred scope item 3. Status: Documented. Date: 2026-05-07.

## Current State

- Model: BGE-M3 via sentence-transformers (BAAI/bge-m3)
- Embedding dim: 1024
- Normalized: True (L2)
- Used by: D2 semantic cache, C0 dense retrieval, vector_db MCP

## Configuration

```python
# agentic_core/L4_state/utils/memory/semantic_cache_manager.py
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
```

## Swap Procedure (when needed)

1. Update EMBEDDING_MODEL_NAME to new model
2. Update EMBEDDING_DIM to match new model output
3. Clear existing D2 cache: delete artifacts/gptcache/
4. Re-index: next runs will populate cache with new embeddings
5. Run test suite: pytest tests/unit/agentic_core/L4_state/

## Candidates for Future Swap

| Model | Dim | Notes |
|-------|-----|-------|
| BGE-M3 (current) | 1024 | Multilingual, good all-around |
| BGE-large-en-v1.5 | 1024 | English-only, slightly better on MTEB |
| E5-mistral-7b-instruct | 4096 | Higher quality, larger dim, slower |
| Stella-base-en-v2 | 768 | Smaller, faster, good for latency-sensitive |
