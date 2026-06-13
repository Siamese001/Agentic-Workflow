# Hardened Embedding-Accelerated Meta-Learning Plan

This plan integrates embeddings throughout the L0-L6 agentic architecture with strict authority isolation, determinism contracts, local 4TB SSD storage, and formal invariants — treating the embedding layer with the same rigor as L2/L4.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## FORMAL EMBEDDING AUTHORITY CONSTRAINTS

Embeddings are **informational only**. They influence proposals; they never enforce.

```
EMBEDDING AUTHORITY INVARIANTS (Non-negotiable):
  I1. Embedding similarity may only generate ChangePackage deltas — never absolute values.
  I2. Embedding results may NEVER bypass L0/L5/L2 authority gates.
  I3. Embedding-derived changes must flow: Proposer → MetaLearningBus → L4 VersionStore → Merkle recompute.
  I4. Embedding-based anomaly detection cannot modify routing in the same execution cycle (time-shifted).
  I5. All embedding decisions must store: model_version, embedding_checksum, index_version_hash, top_k, similarity_cutoff.
  I6. DPO embedding spaces are namespace-isolated per domain + task_class + policy_version.
  I7. Embedding model change requires L4 Merkle root recomputation before use.
  I8. No embedding result may override L4 invariants or relax L5 safety constraints.
```

---

## CURRENT STATE ANALYSIS

### Existing Embedding Infrastructure
- **EmbeddingSovereignAgent** — Gemini/OpenAI gateway with Redis caching
- **EmbeddingMixin** — Unified agent-level embedding access
- **InMemoryVectorCache** — ChromaDB hot cache (RAM)
- **TieredVectorStore** — Hot-in-memory + warm-disk skeleton
- **SemanticCacheManager** — Redis + Pinecone dual-layer with PII sanitization
- **SovereignSemanticCache** — Mission-isolated semantic caching with AST features
- **PineconeSovereignAgent** — Cloud vector store with hybrid search

### Meta-Learning Pipeline (Actual Authority Model)
- **run_pipeline()** — Deterministic 9-step orchestrator; proposal_only=True by default
- **MetaLearningBus** — FIFO queue; sole conduit for change packages; no direct L4 mutation
- **ChangePackage** — Frozen dataclass; content-hash keyed; canonical_bytes() enforced
- **L4StateWriter** — Write-once, content-hash keyed via L4VersionStore
- **ReplayValidator** — Runs engine twice; raises DeterminismViolation on hash mismatch
- **ShadowEvaluator** — Fail-closed regression gate before activation
- **OscillationDetector** — Freeze-on-oscillation to prevent cascading drift

### Active Optimizers
- **l0_threshold_tuner** — Simple heuristic; escalation_rate → threshold delta
- **rag_optimizer** — Simple heuristic; retrieval_precision → top_k delta
- **healing_config_optimizer** — Aggregate-based threshold proposals
- **pattern_analysis_engine** — Statistical pattern detection on healing + drift
- **rlhf_optimizer** / **DefaultDeterministicRLHFOptimizer** — DPO → bounded threshold delta

---

## LOCAL SSD STORAGE (4TB)

### Partition Layout
| Partition | Size | Contents |
|---|---|---|
| FAISS indexes | 1TB | Healing + telemetry + DPO IVFPQ indexes |
| Embedding cache | 800GB | Pre-computed vectors (LZ4 compressed) |
| Raw source data | 400GB | Healing outcomes, telemetry, DPO pairs |
| L4 artifacts | 400GB | Versioned snapshots, Merkle witnesses |
| Working space | 400GB | Temp processing, logs |
| Reserve | 1TB | Future expansion |

### Simplified Storage Tiers (Collapsed from 6 → 3)
```
Tier 0: RAM    — InMemoryVectorCache (ChromaDB)  — hot patterns, <5ms
Tier 1: SSD    — FAISS IVFPQ + LZ4 cache        — warm patterns, <20ms
Tier 2: Cloud  — Pinecone                        — backup + collaboration, <200ms
```
**ChromaDB and TieredVectorStore are removed from the architecture.** FAISS on SSD replaces ChromaDB warm tier directly.

### Retention Lifecycle (Required)
| Data Type | Retention | Prune Strategy | Governance |
|---|---|---|---|
| Healing patterns |  | Drift-based pruning | L6 → L4 write |
| Telemetry embeddings |  | Rolling window eviction | L6 observe only |
| DPO embeddings | Permanent (versioned) | Immutable, version-pinned | L4 content-hash |
| Config embeddings | Versioned snapshot | Immutable | L4 content-hash |

---

## DETERMINISM CONTRACT

### Embedding Determinism Requirements
```
D1. FAISS IVFPQ training: fixed seed (seed=42), deterministic insertion order.
D2. All embedding vectors normalized before storage (unit L2 norm).
D3. Canonical sort before index persistence: sorted by (content_hash, vector_id).
D4. Index rebuild must produce identical nearest-neighbor sets (regression test required).
D5. Floating point: all similarity scores rounded to 6 decimal places before comparison.
D6. Async population: sequential chunked writes; no concurrent index mutation.
```

### Replay Artifact (Required Per Decision)
Every embedding-influenced ChangePackage must carry:
```python
@dataclass(frozen=True, slots=True)
class EmbeddingArtifact:
    embedding_model_version: str   # e.g., "text-embedding-004-v1"
    embedding_checksum: str        # SHA-256 of query vector
    index_version_hash: str        # SHA-256 of FAISS index state
    top_k: int
    similarity_cutoff: float
    supporting_trace_ids: tuple[str, ...]  # IDs of top_k matched contexts
```
Without this, `replay_validate()` cannot reconstruct the decision.

---

## STAGED ROLLOUT (Not Simultaneous)

All five learning surfaces must be staged. No cross-layer activation until prior phase is validated.

| Phase | Component | Scope | Validation Gate |
|---|---|---|---|
| A | Telemetry embedding only | Observe + cluster events | Shadow eval; L6 write-only |
| B | Healing context embedding | Strategy recommendation | ReplayValidator passes |
| C | Proposer embedding (L0 + RAG) | Delta proposals via Bus | OscillationDetector armed |
| D | DPO embedding | Preference clustering | Namespace isolation verified |
| E | Cross-layer transfer | Pattern generalization | Full Merkle recompute |

---

## INTEGRATION OPPORTUNITIES (Priority-Ordered)

### High Impact

**1. Healing Strategy Recommendation (Phase B)**
- Embed `(violation_signature, environment_context, strategy)` triples
- FAISS Tier-1 search for top-5 similar historical cases
- Output: delta recommendation + confidence + supporting_trace_ids
- Authority path: `HealingConfigOptimizer → ChangePackage → MetaLearningBus → L4StateWriter`

**2. DPO Preference Clustering (Phase D)**
- Embed control and candidate outputs per DPO pair
- Namespace isolated: `dpo/{domain}/{task_class}/{policy_version}`
- Immutable archive in L4 (not SSD-only)
- Output: weighted preference signal fed to `DefaultDeterministicRLHFOptimizer`

**3. Telemetry Anomaly Semantic Clustering (Phase A)**
- Embed telemetry event payloads
- L6 observe-only: writes anomaly signal to L4 via `write_l4a_detection_signal()`
- L0 consumes signal at run t+1 — **no same-cycle routing mutation**

### Medium Impact

**4. L0/RAG Threshold Contextual Similarity (Phase C)**
- Embed current system context; find similar historical snapshots
- Output: proposed delta (not absolute value) with confidence
- Passes through: `L0Proposer.propose()` → existing constraint enforcement in `l0_threshold_tuner`

### Lower Impact (Deferred to Phase E)

**5. Cross-layer Pattern Transfer**
- Transfer healing patterns to inform RAG optimization
- Requires full cross-index semantic search — defer until A-D stable

---

## IMPLEMENTATION ARCHITECTURE

### Core Service
```python
class MetaLearningEmbeddingService:
    """Informational-only embedding service for meta-learning.

    INVARIANT: This service produces signals; it never mutates state.
    All outputs are EmbeddingArtifact-wrapped for replay compatibility.
    """

    def __init__(self, base_ssd_path: Path):
        self.embedder = EmbeddingSovereignAgent()   # existing
        self.hot_cache = InMemoryVectorCache()       # existing Tier 0
        self.faiss_store = LocalFAISSStore(base_ssd_path / "faiss_indexes")  # new Tier 1
        self.pinecone = PineconeSovereignAgent()     # existing Tier 2

    async def find_similar_healing_contexts(
        self, context: dict, top_k: int, similarity_cutoff: float
    ) -> tuple[list[dict], EmbeddingArtifact]:
        """Returns similar contexts AND replay artifact. Always paired."""
        ...

    async def emit_telemetry_anomaly_signal(
        self, events: list[dict], l4_writer: L4StateWriter, created_utc: int
    ) -> str:
        """Writes anomaly signal to L4 only. Returns version_id. No routing."""
        ...
```

### Embedding-Aware Proposer Contract
```python
class EmbeddingAwareL0Proposer:
    """L0 proposer with embedding guidance.

    INVARIANT: propose() returns delta only — never absolute threshold.
    INVARIANT: ChangePackage.reason includes EmbeddingArtifact fields.
    """

    def propose(self, snapshot, metrics, config, now_utc, history, cooldown, sample):
        similar, artifact = await self.embedding_service.find_similar_healing_contexts(...)

        # Compute delta from similar contexts — not absolute value
        suggested_delta = self._compute_delta_from_similar(similar, config)

        # Clamp through existing constraint enforcement (unchanged)
        validated = validate_surface_change(surface_name, current_value, current_value + suggested_delta)

        return ChangePackage(
            source="embedding_aware_l0_proposer",
            target="escalation_threshold",
            changes=json.dumps({"delta": suggested_delta}).encode(),
            confidence=artifact.similarity_cutoff,
            reason=(
                f"embedding_model={artifact.embedding_model_version}",
                f"index_hash={artifact.index_version_hash}",
                f"top_k={artifact.top_k}",
                *[f"trace={t}" for t in artifact.supporting_trace_ids],
            ),
            timestamp_utc=now_utc,
        )
```

### Local FAISS Population Pipeline
```python
class LocalEmbeddingPopulationService:
    """SSD-optimized batch embedding population. Read-only source access."""

    BATCH_SIZE = 5000          # Optimal for SSD sequential I/O
    MAX_WORKERS = 8            # Match available CPU cores
    FAISS_SEED = 42            # Fixed for determinism (D1)
    FAISS_NLIST = 2048         # IVF cells
    FAISS_M = 64               # PQ subquantizers
    FAISS_NBITS = 8            # Bits per subquantizer
    COMPRESSION = "lz4"        # SSD storage compression

    async def populate(self, source_path: Path, index_type: str):
        """Populate FAISS index from source. Deterministic insertion order."""
        files = sorted(source_path.glob("*.json"))  # Sorted = deterministic (D3)

        for chunk in self._chunked(files, self.BATCH_SIZE):
            texts = self._extract_texts(chunk)
            embeddings = await self.embedder.get_embeddings_batch(texts)
            normalized = [self._l2_normalize(e) for e in embeddings]  # D2

            await self.faiss_store.add(normalized, metadata=chunk, index=index_type)

        # Rebuild index with fixed seed
        self.faiss_store.train(index_type, seed=self.FAISS_SEED)  # D1
        self.faiss_store.save_with_hash(index_type)               # For I5
```

---

## SSD STORAGE REQUIREMENTS

| Item | Estimated Size | Notes |
|---|---|---|
| Healing context embeddings | ~200GB | 1M contexts × 768-dim × 4B |
| Telemetry event embeddings | ~150GB | 5M events × 384-dim × 4B (30-day window) |
| DPO pair embeddings | ~50GB | 100K pairs × 768-dim × 4B |
| FAISS IVFPQ indexes | ~600GB | Healing + telemetry + DPO |
| L4 versioned artifacts | ~200GB | Snapshots + Merkle witnesses |
| Working space | ~400GB | Batch processing temp |
| **Total** | **~1.6TB** | Well within 4TB capacity |

---

## PERFORMANCE TARGETS

| Operation | Target | Mechanism |
|---|---|---|
| FAISS Tier-1 search | <20ms / 1M vectors | IVFPQ + SSD sequential |
| Hot cache lookup | <5ms | InMemoryVectorCache |
| Batch embedding | >1000 texts/sec | BatchEmbeddingService (existing) |
| Index rebuild | < | LZ4-compressed offline rebuild |
| Pinecone fallback | <200ms | Cloud backup only |

---

## MISSING PIECES (Must Be Built)

| New Component | Layer | Purpose |
|---|---|---|
| `EmbeddingArtifact` (frozen dataclass) | system_learning/types | Replay compatibility wrapper |
| `LocalFAISSStore` | system_learning/engines | SSD-backed FAISS IVFPQ with seed + hash |
| `LocalEmbeddingPopulationService` | system_learning/engines | Deterministic batch population |
| `MetaLearningEmbeddingService` | system_learning/engines | Informational signal service |
| `EmbeddingEnhancedPatternAnalysisEngine` | system_learning/engines | Extends PatternAnalysisEngine |
| `EmbeddingAwareL0Proposer` | system_learning/engines | Delta-only proposer |
| `EmbeddingAwareRAGProposer` | system_learning/engines | Delta-only proposer |
| Retention/pruning cron | ops_scripts | SSD lifecycle enforcement |
| Index rebuild regression test | tests/unit_min_deps | Verifies D4 (identical NN sets) |

---

## WHAT DOES NOT CHANGE

- `run_pipeline()` — unchanged orchestration
- `MetaLearningBus` — unchanged FIFO conduit
- `ChangePackage` — unchanged schema (confidence + reason fields carry artifact)
- `ReplayValidator` — unchanged; embedding-aware proposers must pass it
- `ShadowEvaluator` — unchanged regression gate
- `OscillationDetector` — unchanged; embedding-induced oscillation is detected here
- `L4StateWriter` / `L4VersionStore` — unchanged; all embedding writes go through here
- All L5 safety constraints — unchanged and non-bypassable

---

## PHASED IMPLEMENTATION SCHEDULE

| Week | Phase | Deliverables |
|---|---|---|
| 1 | Infrastructure | `LocalFAISSStore`, SSD partitions, `EmbeddingArtifact` type |
| 2 | Population | `LocalEmbeddingPopulationService`, historical data ingestion |
| 3–4 | Phase A | Telemetry embedding + L6→L4 anomaly signal path |
| 5–6 | Phase B | Healing strategy embedding + `EmbeddingEnhancedPatternAnalysisEngine` |
| 7–8 | Phase C | `EmbeddingAwareL0Proposer` + `EmbeddingAwareRAGProposer` |
| 9–10 | Phase D | DPO embedding + namespace isolation + immutable L4 archive |
| 11–12 | Phase E | Cross-layer transfer + full Merkle recompute + production hardening |

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

