# Local Vector Store Evaluation and Implementation Plan

This document evaluates replacing Pinecone with a fully local embedding+index stack for the Agentic-Workflow repository, focusing on cost savings while maintaining retrieval behavior contracts.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## PHASE 1 DISCOVERY FINDINGS

### Current Pinecone Architecture
The repository has extensive Pinecone integration across multiple layers:

**Core Components:**
- `PineconeVectorMixin` - Ultra-hardened mixin with Redis caching, graceful degradation
- `PineconeSovereignAgent` - Sovereign gateway for all Pinecone operations
- `SemanticCacheManager` - Dual-layer cache (Redis + Pinecone) with PII sanitization
- `EmbeddingSovereignAgent` - Unified embedding gateway (Gemini + OpenAI)

**Configuration:**
- Default index: `canon-sovereign-territory` (configurable via `PINECONE_INDEX_NAME`)
- Default dimension: 1536 (configurable via `EMBEDDING_DIMENSION`)
- Cloud: AWS us-east-1 (configurable)
- Feature flags: `USE_PINECONE`, `USE_REDIS_CACHE`, `GRACEFUL_DEGRADATION`

**Retrieval Patterns:**
- Hybrid search (dense + sparse) with RRF fusion
- Namespace isolation by architectural layers
- Metadata filtering (file_path, territory, type)
- Top-k retrieval with configurable broadness (5-50 results)
- Similarity thresholds (0.75-0.98 default)

**Current Usage:**
- L1 Cognition: Memory embedding and semantic search
- L4 State: Long-term memory storage and territory bootstrapping
- RAG Pipeline: Document indexing and retrieval
- Healing Systems: Violation pattern matching

### Corpus Size Analysis
Based on `data/processed/` and agent discovery:
- Agent discovery: ~2,358 bytes (small metadata file)
- Semantic cache: Contains processed chunks for embedding
- Estimated corpus: ~10K-50K code chunks (based on agent count and file structure)
- Growth rate: Low-moderate (mature codebase)

## RECOMMENDATION: HYBRID APPROACH

**Decision: HYBRID (Local Primary + Pinecone Fallback)**

**Rationale:**
1. **Cost Optimization**: Local index eliminates recurring Pinecone costs
2. **Privacy**: All embeddings remain on-premise
3. **Reliability**: Local operation continues if Pinecone unavailable
4. **Future-Proofing**: Easy migration path if local proves insufficient

**Embedding Model Selection:**
- **Primary**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, CPU-optimized)
- **Fallback**: `text-embedding-3-small` (1536-dim, existing OpenAI integration)

**Estimated Index Size:**
- 50K chunks × 384 dims × 4 bytes = ~76MB base index
- Metadata (SQLite): ~10-20MB
- Total: ~100MB (well within 4TB SSD budget)

## PHASE 2 IMPLEMENTATION PLAN

### Wave 1: Backend Interface + Config
1. Create `VectorIndexBackend` protocol with methods:
   - `upsert(chunks: list[ChunkRecord])`
   - `query(query_text: str, top_k: int, filters: dict) -> list[ChunkHit]`
   - `delete(ids: list[str])`
   - `stats()`

2. Add config toggles:
   - `VECTOR_BACKEND = "local" | "pinecone"`
   - `EMBEDDER_ID = "minilm" | "openai-small"`
   - `INDEX_PATH = "./data/vector_index"`

3. Ensure callers use only interface, no direct imports

### Wave 2: Local Index Implementation
1. **Vector Store**: FAISS IVF index with persistence
   - Index file: `./data/vector_index/faiss.index`
   - Metadata: SQLite database with schema:
     ```sql
     CREATE TABLE chunks (
         chunk_id TEXT PRIMARY KEY,
         doc_id TEXT,
         source_path TEXT,
         start_offset INTEGER,
         end_offset INTEGER,
         text_hash TEXT,
         content TEXT,
         territory TEXT,
         namespace TEXT
     )
     ```

2. **Incremental Indexing**:
   - Skip re-embed if `text_hash` unchanged
   - Stable vector IDs via content hash
   - Batch upserts (100 chunks per batch)

3. **Filter Support**:
   - Exact match on metadata fields
   - Territory/namespace filtering
   - File path filtering

### Wave 3: Embedding Provider
1. **Local Embedder**:
   ```python
   class LocalEmbedder:
       def __init__(self, model_name="all-MiniLM-L6-v2"):
           self.model = SentenceTransformer(model_name)
           self.dimension = self.model.get_sentence_embedding_dimension()

       def embed(self, texts: list[str]) -> list[list[float]]:
           return self.model.encode(texts, batch_size=32, normalize_embeddings=True)
   ```

2. **Determinism**:
   - Fixed random seed
   - Explicit dtype (float32)
   - Normalized embeddings (unit length)
   - Batch size configurable

### Wave 4: Integration Points
1. **Update PineconeVectorMixin**:
   - Add backend selection logic
   - Preserve existing method signatures
   - Maintain Redis caching layer

2. **Update SemanticCacheManager**:
   - Add local index option
   - Preserve promotion logic
   - Keep PII sanitization

3. **Update RAG Orchestrator**:
   - Add local embedder option
   - Preserve hybrid search capabilities

## ACCEPTANCE CRITERIA

1. ✅ Repo-grounded recommendation with explicit references
2. ✅ Local backend builds index from existing corpus
3. ✅ Query equivalence (same top-k shape, metadata preserved)
4. ✅ Backend switching via config only
5. ✅ Unit tests cover backend selection and incremental indexing
6. ✅ Pinecone backend remains import-safe when unavailable
7. ✅ No scope creep (only retrieval backend changes)

## TESTING STRATEGY

1. **Unit Tests**:
   - Backend selection logic
   - Embedding dimension validation
   - Incremental indexing (hash-based skip)
   - Query shape equivalence

2. **Integration Tests**:
   - End-to-end retrieval with local backend
   - Config switching between backends
   - Performance benchmarks (local vs Pinecone)

3. **Performance Targets**:
   - Index build: < for 50K chunks
   - Query latency: <100ms for top-15
   - Memory usage: <500MB during operation

## RISKS AND MITIGATIONS

1. **Performance Risk**: Local search slower than Pinecone
   - Mitigation: FAISS IVF indexing, batch operations

2. **Compatibility Risk**: Embedding dimension mismatch
   - Mitigation: Config validation, automatic dimension detection

3. **Data Migration Risk**: Existing Pinecone data loss
   - Mitigation: Migration script, backup procedures

4. **Memory Risk**: Large index memory usage
   - Mitigation: FAISS memory mapping, chunked loading

## NEXT STEPS

1. Implement backend interface and config
2. Create local FAISS + SQLite implementation
3. Add local sentence-transformers embedder
4. Update existing mixins to use backend interface
5. Create migration script from Pinecone
6. Add comprehensive tests
7. Performance benchmarking and optimization

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

