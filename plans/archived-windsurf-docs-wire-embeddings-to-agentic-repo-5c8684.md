---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\wire-embeddings-to-agentic-repo-5c8684.md'
original_relative_path: 'wire-embeddings-to-agentic-repo-5c8684.md'
source_sha256: 9026133ea4aaa2a3dd7e61c8b850326485f9ac14d94169fad0f2c7f618bf6e29
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wire Agentic Repo to Production Embedding Vectors (v4 — Zero-Loss Compliant)

Integrate the 1.14GB `text-embedding-3-large` seed pack into the agentic repo's highest-impact subsystems, with streaming-hash normalization, eps-guarded division, pack-hash-seeded spot-checks, z-score σ-floor, total kill-switch coverage, replay-mode RAG bypass, fallback telemetry containment, and psutil process-identity fork guard — fully aligned with L0–L6 zero-loss model.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Embedding Pack Reference
```
namespace:  healing_contexts
hash:       5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9
dims:       3072 × 100K vectors = 1.14 GB
model:      text-embedding-3-large
```

---

## Foundational Contract (applies to all phases)

**Embedding outputs are C0-INFORMATIONAL ONLY.**
```
MAY:  augment ChangePackage candidate context (C0)
MAY:  adjust optimizer candidate scoring (bounded, ≤ 0.3 weight)
MAY NOT: directly write L4 routing thresholds
MAY NOT: override L5 safety tiers
MAY NOT: alter allowed_tools[]
MAY NOT: contaminate curated seed packs with runtime data
```

**Kill-switch — total coverage:** `embedding_enabled: bool` in L4 governance.
- `EmbeddingServiceFactory` raises `EmbeddingDisabledError` on instantiation attempt when `false`
- Namespace writes blocked at factory level
- Telemetry signals suppressed (no drift signals from a disabled layer)
- All W1–W6 enter disabled path via single shared `EmbeddingServiceFactory.get_or_disabled()` call; no per-caller flag checks

**Telemetry-to-routing delay rule (explicit):**
```
Embedding telemetry signals MAY influence routing thresholds
ONLY via the Meta-Learning Bus commit cycle (L6 → L4 → L0 at t+1).
NEVER synchronously during execution.

Fallback telemetry MAY increase anomaly_score_weight
ONLY after Meta-Learning commit cycle — never during an active outage.
This prevents cascading instability when Pinecone is down.
```

**Determinism contract (all retrieval):**
- dtype: `float32` fixed, `casting="unsafe"` on matmul
- BLAS thread lock at process start: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`
- `blas_impl` fingerprint included in replay key
- Cosine scores rounded to 6 decimal places
- Sort: `(score_round6 DESC, content_hash ASC)` — identical to `LocalFAISSStore`
- Replay key = `sha256(embedder_id + vector_pack_hash + normalized_pack_hash + top_k + similarity_cutoff + blas_impl)`

**Namespace isolation + versioning (immutable):**
```
healing_contexts                         ← curated pack (read-only forever)
episodic_runtime_cache@<embedder_id>     ← TTL-based, versioned by embedder; pruned on upgrade
reasoning_contexts@<embedder_id>         ← offload-only, versioned; never merged into curated packs
```
On embedder upgrade: all `@<old_embedder_id>` namespaces auto-pruned.

**Memory ceiling strategy:**
- Single process: singleton memmap (W1)
- Multi-process/fork: pre-fork load before workers spawn (Gunicorn-style)
- Horizontal scale: shared read-only mmap segment OR dedicated embedding sidecar process
- **Fork guard** — identity stored as `(pid, psutil.Process().create_time())` pair; PID alone is insufficient (worker restart may reuse PID); both must match on every `get()` call

---

## W1 — Embedding Service Factory + Performance + Singleton

**New file:** `system_learning/engines/embedding_service_factory.py`
**Edit:** `system_learning/engines/meta_learning_embedding_service.py`
**Edit:** `system_learning/constraints/config_surfaces.py`

**What:**
1. **Kill-switch check first** — all retrieval methods return `None` immediately if `embedding_enabled=false`
2. **BLAS lock at module import** — `os.environ["OMP_NUM_THREADS"] = "1"`, `os.environ["MKL_NUM_THREADS"] = "1"`, `blas_impl = np.__config__.blas_opt_info.get("libraries", ["unknown"])[0]`
3. **Singleton** — `_INSTANCE: EmbeddingServiceFactory | None = None` with thread-safe `threading.Lock`; post-fork guard raises `RuntimeError` if PID changed after init
4. **numpy memmap + pre-normalized matrix:**
   ```python
   raw = np.memmap(path, dtype=np.float32, mode='r', shape=(N, D))
   eps = 1e-12
   norms = np.maximum(np.linalg.norm(raw, axis=1, keepdims=True), eps)  # eps-guard
   normalized = (raw / norms).astype(np.float32)   # stored in singleton, not on disk
   # Track zero-norm anomalies
   anomaly_count = int((norms < eps * 2).sum())
   emit_telemetry("embedding_row_norm_anomaly_count", anomaly_count)
   ```
5. **Streaming normalized_pack_hash** — avoids materializing a second 1.14GB bytes object:
   ```python
   hasher = hashlib.sha256()
   for chunk in np.nditer(normalized, flags=["external_loop"], order="C"):
       hasher.update(chunk.tobytes())
   normalized_pack_hash = hasher.hexdigest()
   ```
6. **Startup integrity check** — SHA-256 of `embeddings.f32` vs `manifest.matrix_hash`; emits `embedding_pack_integrity_ok=false` + raises if mismatch
7. **Deterministic spot-check** — seed derived from `vector_pack_hash`, never wall-clock or global `np.random` state:
   ```python
   seed = int(vector_pack_hash[:8], 16)
   rng = np.random.default_rng(seed)
   row_idx = rng.integers(0, N)
   ```
   `embedding_pack_integrity_ok` = startup check AND last spot-check both OK
7. **Cold-start** — pack missing → return `None`, emit L6 signal, never crash execution path
8. **Health probe** — `EmbeddingServiceFactory.is_healthy() -> bool`
10. **Replay key** — `sha256(embedder_id + vector_pack_hash + normalized_pack_hash + str(top_k) + str(round(cutoff,6)) + blas_impl)`

---

## W2 — Healing Pipeline Semantic Retrieval (Informational Only)

**Edit:** `system_learning/pipelines/meta_learning_pipeline.py`
**Edit:** `system_learning/engines/healing_config_optimizer.py`

**What:**
1. Check `embedding_enabled` kill-switch; skip entirely if false
2. After `PatternAnalysisEngine.analyze()`, call `factory.retrieve(query=failure_signature, k=top_k_cap)`
3. **Small-N guard** — if `statistical_sample_size < MIN_SAMPLE_THRESHOLD` (default 20, matching existing `min_observations`):
   ```python
   embedding_weight = 0.0   # embedding disabled under sparse telemetry
   ```
4. Otherwise weight-capped at ≤ 0.3:
   ```python
   final_score = (0.7 * statistical_score) + (min(0.3, embedding_influence_cap) * embedding_similarity_score)
   ```
5. `ChangePackage` carries `embedding_artifact_hash` as auditable metadata only — no executable path
6. All telemetry signals emitted **async** via Meta-Learning Bus; never synchronously alter thresholds

---

## W3 — L1 Episodic Memory Semantic Upgrade (Namespace-Versioned)

**Edit:** `agentic_core/L1_cognition/engines/episodic_manager.py`
**Edit:** `agentic_core/L1_cognition/engines/semantic_manager.py`

**What:**
1. Check `embedding_enabled` kill-switch; fall back to `_keyword_search` if false
2. Replace 384-dim zero stub with `EmbeddingServiceFactory` bridge
3. Evictions write to `episodic_runtime_cache@{embedder_id}` — never `healing_contexts`
4. `EmbeddingServiceFactory.write_episodic()` hard-rejects `namespace="healing_contexts"` with `ValueError`
5. **Embedder upgrade auto-prune** — on factory init, detect `embedder_id` change, prune all `episodic_runtime_cache@<old_id>` and `reasoning_contexts@<old_id>` namespaces
6. **Replay-safe TTL** — episodic retrieval disabled in `replay_mode=true`; TTL expressed as logical cycle count (L4 `episodic_ttl_cycles` int constraint), not wall-clock

---

## W4 — L4 Reasoning Memory Offload (No Silent Failure)

**Edit:** `agentic_core/L4_state/memory/reasoning_memory.py`

**What:**
1. Replace silent `ImportError` with:
   ```python
   except ImportError as e:
       emit_telemetry("reasoning_memory_offload_unavailable", {"error": str(e)})
       self.semantic_offload = False
   ```
2. On eviction: embed → store in `reasoning_contexts@{embedder_id}`; versioned namespace
3. Offload failure emits `reasoning_memory_health=0.0`; healthy emits `1.0`
4. `retrieve_relevant()` disabled in `replay_mode=true` (same as W3)

---

## W5 — Sovereign RAG Orchestrator Local Retrieval

**Edit:** `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py`

**What:**
1. Check `embedding_enabled`; skip local path if false
2. Local retrieve → z-score normalize scores with σ-floor:
   ```python
   sigma = max(scores.std(), 1e-9)   # division-by-zero guard when all scores identical
   local_norm = (scores - scores.mean()) / sigma
   ```
3. Alpha-weighted merge:
   ```python
   final = alpha * local_norm + (1 - alpha) * external_norm
   ```
   `alpha` from L4 `retrieval_alpha` (default 0.4, bounded [0.2, 0.6])
4. Deduplicate by `content_hash` (local wins on tie)
5. `backend_id` + `retrieval_backend_mode` stamped on every `RagDocument`
6. Cross-namespace blending disabled in fallback mode (`retrieval_backend_mode=FAIL_CLOSED` or `STRICT_EXTERNAL`)
7. **Replay-mode bypass** — if `replay_mode=true`, skip local retrieval entirely; transcript-driven only

---

## W6 — SemanticCacheManager Local Fallback (Visibly Degraded)

**Edit:** `agentic_core/L4_state/memory/semantic_cache_manager.py`

**What:**
1. Check `embedding_enabled`; skip fallback entirely if false
2. On Pinecone unavailable + `HIVE_MIND_STRICT_MODE=false`: activate local fallback
3. Fallback stamps on `ExecutionTrace`: `semantic_backend=LOCAL`, `fallback_reason=<exception_type>`
4. Fallback mode: `HIVE_MIND_MIN_CONFIDENCE × 1.1`, `top_k_cap × 0.8` (reduced), cross-namespace blending disabled
5. L6 emits `semantic_fallback_rate` async only — never synchronous routing change
6. Auto-deactivates on Pinecone health probe recovery

---

## L4 Governance Block (W1 prerequisite — `config_surfaces.py`)

```python
EMBEDDING_GOVERNANCE_BOOL: dict[str, bool] = {
    "embedding_enabled": True,   # kill-switch; only L4 may mutate
}
EMBEDDING_GOVERNANCE_POINTER: dict[str, PointerConstraint] = {
    "active_embedder_id": PointerConstraint(frozenset({"text-embedding-3-large", "text-embedding-3-small"})),
    "vector_pack_hash":   PointerConstraint(frozenset({PACK_HASH})),        # sealed at deploy
    "normalized_pack_hash": PointerConstraint(frozenset({NORM_HASH})),      # computed W1 init
    "retrieval_backend_mode": PointerConstraint(frozenset({
        "LOCAL_FIRST", "EXTERNAL_FIRST", "STRICT_EXTERNAL", "FAIL_CLOSED"
    })),
}
EMBEDDING_GOVERNANCE_FLOAT: dict[str, FloatConstraint] = {
    "similarity_cutoff":       FloatConstraint(0.5, 0.99, 0.05),
    "retrieval_alpha":         FloatConstraint(0.2, 0.6,  0.10),
    "embedding_influence_cap": FloatConstraint(0.05, 0.25, 0.05),  # anchored at 0.25; >0.25 degrades under correlated features
}
EMBEDDING_GOVERNANCE_INT: dict[str, IntConstraint] = {
    "top_k_cap":             IntConstraint(3, 20, 3),
    "episodic_ttl_cycles":   IntConstraint(1, 100, 10),   # logical time, not wall-clock
    "min_sample_threshold":  IntConstraint(5, 100, 5),
}
```
All keys added to `ALLOWED_SURFACES`. None in `FORBIDDEN_SURFACES`.

---

## L6 Telemetry Signals

All emitted **async via Meta-Learning Bus only** — zero synchronous routing side-effects:

| Signal | Type | Source | Routing impact |
|--------|------|--------|----------------|
| `embedding_pack_integrity_ok` | bool | W1 startup + spot-check | t+1 only |
| `embedding_row_norm_anomaly_count` | int | W1 pre-norm | t+1 only |
| `cosine_drift_pack_vs_query` | float | W1 per-retrieve | t+1 only |
| `top_k_stability_violation` | bool | W1 sort check | t+1 only |
| `retrieval_entropy_score` | float | W2 top-k diversity | t+1 only |
| `embedding_influence_actual` | float | W2 per-optimize cycle | t+1 only |
| `reasoning_memory_health` | float | W4 offload success | t+1 only |
| `semantic_fallback_rate` | float | W6 LOCAL/EXTERNAL ratio | t+1 only |

**Suppressed when `embedding_enabled=false`:** all signals above — no ghost drift from disabled layer.

---

## Implementation Order

| Phase | Files | New Hardening vs v3 |
|-------|-------|---------------------|
| **W1** | 2 new, 2 edit | Streaming hash (no 2×RAM), eps-guard + anomaly count, pack-hash-seeded rng spot-check, (pid+ctime) fork guard, total kill-switch via `get_or_disabled()` |
| **W2** | 2 edit | Telemetry suppressed when disabled; fallback telemetry delay rule explicit |
| **W3** | 2 edit | Replay-mode episodic retrieval disabled |
| **W4** | 1 edit | Replay-mode reasoning retrieval disabled |
| **W5** | 1 edit | σ-floor on z-score (1e-9), replay-mode local retrieval bypass |
| **W6** | 1 edit | Fallback telemetry MAY NOT increase anomaly_score_weight synchronously |

**Total:** ~720 lines across 7 files. Each phase independently testable and deployable. W1 is prerequisite for all others.

## Not In Scope
- No changes to existing builder/validator/artifact/replay logic
- No Pinecone migration
- `healing_contexts` pack is **read-only** at runtime; all writes go to versioned isolated namespaces

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

