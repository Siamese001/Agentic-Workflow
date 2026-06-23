# ProceduralPattern:AppsGpuPolicyInvariant

- INVARIANT: apps_* GPU use is limited to transformer/BGE inference and explicitly opted-in large vector math; graph traversal, receipt assembly, JSON/file IO, and control-plane orchestration stay CPU.
- scope: apps_rg/cache/r1b_bge_embedding.py, apps_rg/cache/r1b_chroma_read_surface_projection.py, apps_research/engines/integration/chroma_research_store.py, apps_shared/enforcement/GlobalcacheStrategy.py.
- enforcement: tests/_apps_contract/test_w6_real_embeddings_and_ingestion.py; tests/unit/apps_rg/test_r1b_bge_embedding.py; tests/unit/apps_rg/test_section_evidence_w6c_chroma_projection.py; tests/unit/apps_shared/test_globalcache_gpu_policy.py.
- canonical_pattern: pass the resolved device into local SentenceTransformer/BGE loaders; batch parent+chunk R1B embeddings before Chroma upsert; require APPS_SHARED_VECTOR_GPU_ENABLED plus APPS_SHARED_VECTOR_GPU_MIN_ROWS before CUDA similarity search.
- violation_examples: moving C0.3 graph traversal onto GPU; using GPU for small generic apps_shared vector stores by default; assuming remote provider calls consume local GPU.
- discovered: 2026-06-23, validated: 2026-06-23.
