# FAISS to ChromaDB Migration Archive

## Overview
This directory contains the archived FAISS-related modules that were migrated to ChromaDB as part of the SVP Engineering consolidation initiative.

## Migration Date
March 29, 2026

## Rationale
- **Single source of truth**: ChromaDB is the canonical vector store (3.9GB populated, 6 collections)
- **Operational simplicity**: One vector DB instead of two
- **Dependency hygiene**: Remove redundant `faiss-cpu` dependency
- **Zero-regression**: All tests pass with ChromaDB-only implementation

## Files Archived

### Core Modules
- `faiss_store.py` - Original FAISS vector store implementation for Layer 3
- `local_faiss_store.py` - System learning FAISS integration

### CI/Scripts
- `check_faiss_persist_contract.py` - FAISS persistence validation
- `build_faiss_index.py` - FAISS index building utilities
- `verify_stack_runtime.py` - Stack verification (FAISS sections)

### Tests
- `test_layer_handoffs.py` - Layer handoff tests (FAISS references)

## Current Architecture (ChromaDB-Only)

```
Layer 2 (Semantic Cache): GPTCache → ChromaDB → BGE-M3
Layer 3 (Agentic RAG):   ChromaDB → 🟠 fact_vecs (3.9GB, 6 collections)
```

## Dependencies Removed
- `faiss-cpu` from requirements.txt
- `faiss-cpu` from pyproject.toml

## Verification
Run the following to confirm ChromaDB-only operation:
```bash
python ops_scripts/ci/full_activation_e2e_test.py
```

## Restoration
If FAISS needs to be restored, move these files back to their original locations and update `gptcache_client.py` to use `VectorBase("faiss", ...)` instead of `VectorBase("chromadb", ...)`.

## ADR Reference
See: `docs/architecture/adr/2026-03-29-chromadb-as-canonical-vector-store.md`
