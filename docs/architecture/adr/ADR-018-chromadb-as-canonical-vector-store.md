# ADR-018: ChromaDB as Canonical Vector Store

**Date:** 2026-03-29  
**Status:** Accepted  
**Deciders:** SVP Engineering (Constitutional Rule #11)  
**Related:** Agentic Retrieval Models v17, Layer 2/3 Architecture

## Context

The system previously had dual vector store backends:
- **FAISS** (`faiss-cpu`) - Originally used for Layer 3 RAG vector search
- **ChromaDB** (`chromadb`) - Used for persistent vector storage with metadata

This created:
1. **Dependency bloat** - Two vector libraries with overlapping functionality
2. **Operational complexity** - Two indexing paths, two sync points
3. **Confusion** - Unclear which was canonical for Layer 3

ChromaDB was already fully populated (3.9 GB, 6 collections) and serving as the production vector store.

## Decision

**ChromaDB is now the single canonical vector store** for both Layer 2 (Semantic Cache) and Layer 3 (Agentic RAG).

### Changes Made

1. **Code:**
   - `gptcache_client.py`: Switched from `VectorBase("faiss", ...)` to `VectorBase("chromadb", ...)`
   - Layer 2 GPTCache now uses ChromaDB backend (was FAISS)
   - Layer 3 already used ChromaDB (no change)

2. **Dependencies:**
   - Removed `faiss-cpu>=1.7.4` from `pyproject.toml`

3. **Documentation:**
   - Updated `Agentic Retrieval Models v17.md` to reference ChromaDB exclusively
   - Replaced all `FAISS/Chroma` references with `ChromaDB`

4. **Archival:**
   - Moved FAISS modules to `tools/archive/faiss_migration/`:
     - `agentic_core/L4_state/memory/faiss_store.py`
     - `system_learning/engines/local_faiss_store.py`
     - `ops_scripts/ci/check_faiss_persist_contract.py`
     - `ops_scripts/ci/build_faiss_index.py`
   - Created migration README with restoration instructions

## Rationale

### Operational Simplicity (SVP Principle A)
- One vector DB to maintain, monitor, and optimize
- Single indexing pipeline for all embeddings
- Reduced cognitive load for operators

### Dependency Hygiene (SVP Principle B)
- Eliminated redundant `faiss-cpu` dependency
- Faster `pip install` times
- Fewer version conflict risks

### Archival Over Deletion (SVP Principle C)
- FAISS modules preserved in `tools/archive/faiss_migration/`
- Git history intact
- Restoration path documented if needed

### Single Source of Truth
- ChromaDB already populated with production corpus (3.9 GB)
- No data migration required
- Consistent with Layer 3 existing implementation

## Consequences

### Positive
- ✅ Reduced dependency count by 1
- ✅ Simplified vector store architecture
- ✅ Zero data migration (ChromaDB already populated)
- ✅ Consistent backend for Layer 2 + Layer 3

### Negative
- ⚠️ FAISS-specific optimizations lost (if any existed)
- ⚠️ Teams familiar with FAISS need to learn ChromaDB API

### Neutral
- ChromaDB supports ANN search, metadata filtering, and persistence (feature parity)
- Performance characteristics similar for our use case (BGE-M3 embeddings, Top-K retrieval)

## Validation

### Zero-Regression Test
Run full e2e test suite to confirm ChromaDB-only operation:
```bash
python ops_scripts/ci/full_activation_e2e_test.py
```

Expected: All Layer 2 + Layer 3 tests pass with ChromaDB backend.

### Rollback Plan
If issues arise:
1. Restore FAISS modules from `tools/archive/faiss_migration/`
2. Re-add `faiss-cpu>=1.7.4` to `pyproject.toml`
3. Revert `gptcache_client.py` to `VectorBase("faiss", ...)`

## References
- Constitutional Rule #11: SVP Engineering Persona
- `tools/archive/faiss_migration/README.md` - Migration details
- `Agentic Retrieval Models v17.md` - Updated spec
- `.windsurfrules` - SVP Engineering principles
