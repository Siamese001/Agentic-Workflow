---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\embedding-recommendation-proposal-integration-plan-5c8684.md'
original_relative_path: 'embedding-recommendation-proposal-integration-plan-5c8684.md'
source_sha256: 88026c317fc3c5035c38f2f93e54ebb88d7c20066b24516c1c1a6d5549508822
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan B: Embedding Recommendation and Proposal Integration

Recommendation owns authority isolation: wire Plan A's FAISS indexes into the meta-learning pipeline as informational-only signals that produce delta-only ChangePackages, pass ReplayValidator with NN-set equality, and never bypass L0/L5/L2 authority gates.

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


## SCOPE

- `MetaLearningEmbeddingService.find_similar_*` query methods
- `EmbeddingArtifact` construction and propagation
- Delta-only proposer logic: `EmbeddingAwareL0Proposer`, `EmbeddingAwareRAGProposer`, `EmbeddingEnhancedPatternAnalysisEngine`
- Telemetry anomaly signal path: L6 observe → L4 write → L0 consume at t+1
- DPO embedding integration with namespace isolation
- `ReplayValidator` extension for NN-set equality assertion
- Confidence handling: ranking signal only, never acceptance gate

---

## OUT OF SCOPE

- Index building, training, pruning, or versioning (Plan A)
- Any direct FAISS index mutation
- New storage layers

---

## DEPENDENCY ON PLAN A

Plan B depends on a **thin protocol adapter**, not the concrete `LocalFAISSStore` directly.
This enables offline testing, deterministic mock search for replay tests, and future backend swaps.

```python
# Location: system_learning/ports/embedding_search_provider.py

class EmbeddingSearchProvider(Protocol):
    """Read-only search interface. Plan B's sole dependency on Plan A's infrastructure.

    INVARIANT: Implementors may not expose train(), add(), prune(), or save().
    INVARIANT: search() enforces caller_namespace vs target index_id isolation (I9).
    """

    def open(self, index_id: str) -> tuple[Any, str, IndexBuildMetadata]:
        """Returns (index_handle, index_version_hash, build_metadata)."""
        ...

    def search(
        self,
        index_id: str,
        query_vector: list[float],
        top_k: int,
        cutoff: float,
        caller_namespace: str,          # Required for I9 enforcement
    ) -> list[tuple[str, str, float]]:
        """Returns [(content_hash, trace_id, score_round6)].
        Post-sorted: (score_round6 DESC, content_hash ASC) — deterministic.
        Raises CrossNamespaceViolation if caller_namespace incompatible with index_id.
        """
        ...
```

`LocalFAISSStore` (Plan A) implements `EmbeddingSearchProvider`.
For testing, `MockEmbeddingSearchProvider` implements it with fixed deterministic results.

Plan B must not call `train()`, `add()`, `prune()`, or `save()` — those are Plan A's exclusive domain.

---

## FORMAL AUTHORITY INVARIANTS

```
I1. Embedding similarity may only generate ChangePackage deltas — never absolute values.
I2. Embedding results may NEVER bypass L0/L5/L2 authority gates.
I3. All embedding-derived changes flow: Proposer → MetaLearningBus → L4VersionStore → Merkle recompute.
I4. Telemetry anomaly detection cannot modify routing in the same execution cycle (time-shifted to t+1).
I5. Every embedding-influenced ChangePackage carries an EmbeddingArtifact in its reason tuple.
I6. DPO embedding spaces are namespace-isolated per domain + task_class + policy_version.
I7. Cross-namespace queries are prohibited unless explicitly whitelisted in config_surfaces.py.
I8. Confidence score is a ranking signal only — it never gates approval.
I9. DPO namespace isolation applies at index_id level — cross-index search (e.g., querying
    healing_contexts from DPO logic) is prohibited unless the target index_id is in the whitelist.
    Detected by: EmbeddingSearchProvider.search() validates caller's declared namespace against target index_id.
```

---

## CORE TYPE: EmbeddingArtifact

```python
# Location: system_learning/types/embedding_artifact_types.py

@dataclass(frozen=True, slots=True)
class EmbeddingArtifact:
    """Replay-compatible wrapper for every embedding-influenced decision.

    Required on all ChangePackages produced by embedding-aware components.
    Without this, ReplayValidator cannot reconstruct the decision.
    """
    embedding_model_version: str       # e.g., "text-embedding-004-v1"
    embedding_checksum: str            # SHA-256 of query vector bytes
    index_id: str                      # e.g., "healing_contexts_v1"
    index_version_hash: str            # From IndexBuildMetadata
    top_k: int
    similarity_cutoff: float
    supporting_trace_ids: tuple[str, ...]  # Ordered: (score DESC, content_hash ASC)

    def canonical_bytes(self) -> bytes:
        """Deterministic serialization for replay hashing."""
        return json.dumps({
            "embedding_model_version": self.embedding_model_version,
            "embedding_checksum": self.embedding_checksum,
            "index_id": self.index_id,
            "index_version_hash": self.index_version_hash,
            "top_k": self.top_k,
            "similarity_cutoff": round(self.similarity_cutoff, 6),
            "supporting_trace_ids": list(self.supporting_trace_ids),
        }, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
```

---

## CORE SERVICE: MetaLearningEmbeddingService

```python
# Location: system_learning/engines/meta_learning_embedding_service.py

class MetaLearningEmbeddingService:
    """Informational-only embedding signal service.

    INVARIANT: Produces signals only. Never mutates state.
    INVARIANT: All outputs paired with EmbeddingArtifact for replay.
    INVARIANT: Degrades gracefully when index unavailable (returns None, None).
    """

    def __init__(self, search_provider: EmbeddingSearchProvider):  # protocol, not concrete
        self.search_provider = search_provider   # EmbeddingSearchProvider protocol
        self.embedder = EmbeddingSovereignAgent()
        self.hot_cache = InMemoryVectorCache()    # Tier 0 (existing)

    async def find_similar_healing_contexts(
        self,
        violation: dict,
        strategy: dict,
        *,
        top_k: int,
        similarity_cutoff: float,
    ) -> tuple[list[dict], EmbeddingArtifact] | tuple[None, None]:
        """Returns (contexts, artifact) or (None, None) on degradation."""
        ...

    async def find_similar_rag_contexts(
        self,
        query_metrics: dict,
        *,
        top_k: int,
        similarity_cutoff: float,
    ) -> tuple[list[dict], EmbeddingArtifact] | tuple[None, None]:
        ...

    async def emit_telemetry_anomaly_signal(
        self,
        events: list[dict],
        l4_writer: L4StateWriter,
        created_utc: int,
    ) -> str | None:
        """Writes anomaly signal to L4 only. Returns version_id.
        INVARIANT: No routing side-effects. L0 consumes at t+1, not now.
        """
        ...
```

---

## STAGED ROLLOUT

| Phase | Component | Validation Gate | Blast Radius |
|---|---|---|---|
| A | Telemetry anomaly signal (L6→L4 only) | Signal appears in L4; routing unchanged same cycle | L6 observe path only |
| B | `EmbeddingEnhancedPatternAnalysisEngine` | ReplayValidator passes; identical findings on double-run | PatternAnalysisEngine only |
| C | `EmbeddingAwareL0Proposer` + `EmbeddingAwareRAGProposer` | OscillationDetector armed; delta-only verified | L0 + RAG proposals |
| D | DPO embedding integration | Namespace isolation verified; immutable L4 archive confirmed | RLHFOptimizer input |
| E | Cross-layer transfer (whitelisted only) | Cross-namespace whitelist in `config_surfaces.py`; Merkle recompute | Full pipeline |

---

## KEY NEW COMPONENTS

### `EmbeddingEnhancedPatternAnalysisEngine`
```
Location: system_learning/engines/embedding_enhanced_pattern_analysis_engine.py
Extends: PatternAnalysisEngine (composition, not inheritance)
New behavior:
  - After statistical analysis, queries healing_contexts FAISS index
  - Adds EmbeddingFinding entries alongside existing PatternFinding entries
  - Falls back to base PatternAnalysisEngine if index unavailable
  - EmbeddingFinding carries EmbeddingArtifact for replay
INVARIANT: Does not replace statistical findings — augments only.
```

### `EmbeddingAwareL0Proposer`
```
Location: system_learning/engines/embedding_aware_l0_proposer.py
Implements: L0Proposer protocol
Behavior:
  - Calls find_similar_healing_contexts() for current escalation context
  - Extracts suggested_delta from similar contexts (weighted mean delta)
  - Passes delta through existing validate_surface_change() constraint
  - Returns ChangePackage with EmbeddingArtifact in reason tuple
  - If embedding service unavailable: delegates to existing l0_threshold_tuner
INVARIANT: Output is delta only. Existing constraint bounds unchanged.
```

### `EmbeddingAwareRAGProposer`
```
Location: system_learning/engines/embedding_aware_rag_proposer.py
Implements: RAGProposer protocol
Identical pattern to EmbeddingAwareL0Proposer, targeting retrieval_top_k.
```

### `ReplayValidator` Extension
```
Location: system_learning/validators/replay_validator.py (extend, not replace)
New: replay_validate_with_nn_set()
  - Runs engine twice
  - Compares ChangePackage hash (existing)
  - Additionally compares supporting_trace_ids tuple equality across runs  [NN-set equality]
  - Additionally compares artifact.index_version_hash equality across runs [R1]
  - Raises DeterminismViolation if NN sets differ OR index_version_hash differs
INVARIANT: This is an additive extension — existing replay_validate() unchanged.

R1. ReplayValidator must assert artifact.index_version_hash equality across both runs.
    Rationale: prevents silent index reload producing identical NN sets from a different index state.
```

### `assert_delta_only` Structural Guard
```python
# Location: system_learning/validators/delta_guard.py

class AbsoluteMutationViolation(RuntimeError):
    """Raised when a ChangePackage contains an absolute value instead of a delta."""

def assert_delta_only(change_package: ChangePackage) -> None:
    """Hard structural guard enforcing I1.

    Called by every embedding-aware proposer before returning.
    Raises AbsoluteMutationViolation — never swallowed.
    """
    try:
        parsed = json.loads(change_package.changes.decode("ascii"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise AbsoluteMutationViolation(f"ChangePackage.changes is not valid ASCII JSON: {e}") from e

    if "delta" not in parsed:
        raise AbsoluteMutationViolation(
            f"ChangePackage.changes must contain 'delta' key. Got keys: {sorted(parsed.keys())}"
        )
    if any(k in parsed for k in ("absolute_value", "new_value", "threshold")):
        raise AbsoluteMutationViolation(
            f"ChangePackage.changes must not contain absolute threshold keys. Got: {sorted(parsed.keys())}"
        )
```
Unit test requirement: `EmbeddingAwareL0Proposer` raises `AbsoluteMutationViolation`
if `suggested_delta` is replaced with an absolute threshold in any future refactor.

---

## CHANGEPACKAGE SHAPE WITH EMBEDDING

Embedding-aware proposers must produce this exact shape:

```python
ChangePackage(
    source="embedding_aware_l0_proposer",
    target="escalation_threshold",
    changes=json.dumps({
        "delta": suggested_delta,        # float — NEVER absolute value
        "current_value": current_value,  # for audit
    }).encode("ascii"),
    confidence=round(mean_similarity_score, 6),  # ranking signal only
    reason=(
        f"emb_model={artifact.embedding_model_version}",
        f"index_hash={artifact.index_version_hash}",
        f"top_k={artifact.top_k}",
        f"cutoff={artifact.similarity_cutoff}",
        f"artifact_hash={artifact.content_hash()}",
        *[f"trace={t}" for t in artifact.supporting_trace_ids],
    ),
    timestamp_utc=now_utc,
)
```

The existing `ChangePackage.canonical_bytes()` serializes `reason` — so the artifact is embedded in the replay hash automatically.

---

## DPO NAMESPACE ISOLATION

```python
class DPOEmbeddingNamespace:
    """Namespace key for DPO embedding isolation."""

    def __init__(self, domain: str, task_class: str, policy_version: str):
        self.namespace_id = f"dpo/{domain}/{task_class}/{policy_version}"

    def validate_cross_namespace_query(
        self, target_namespace: str, whitelist: frozenset[str]
    ) -> None:
        """Raises CrossNamespaceViolation if not whitelisted."""
        if target_namespace != self.namespace_id and target_namespace not in whitelist:
            raise CrossNamespaceViolation(
                f"Cross-namespace query from {self.namespace_id} "
                f"to {target_namespace} not whitelisted."
            )
```

DPO pairs are stored in L4 (immutable, content-hash keyed) in addition to SSD. SSD is a performance cache; L4 is the authority record.

---

## TELEMETRY ANOMALY SIGNAL PATH

```
Execution cycle t:
  L6 embed telemetry events → FAISS cluster → anomaly score computed
  L6 calls l4_writer.write_l4a_detection_signal(payload_bytes, ...)
  L6 returns. DONE. No routing effect.

Execution cycle t+1:
  run_pipeline() reads L4 detection signal via audit_store
  PatternAnalysisEngine sees detection_signal_bytes
  EmbeddingEnhancedPatternAnalysisEngine augments findings
  Proposers generate delta proposals if warranted
  MetaLearningBus enqueues proposals
  L0 routing optionally adjusts at activation
```

This is the mandatory time-shift enforced by I4.

---

## GRACEFUL DEGRADATION CONTRACT

```python
# If embedding service unavailable at any point:
# 1. Log warning (no exception raised)
# 2. Return (None, None) from find_similar_*
# 3. Proposer falls back to existing heuristic engine
# 4. ChangePackage.source = "heuristic_l0_proposer" (not embedding-aware)
# 5. Pipeline continues unaffected

# This ensures: index build issues in Plan A never block Plan B pipeline correctness.
```

---

## WHAT DOES NOT CHANGE

| Component | Status |
|---|---|
| `run_pipeline()` | Unchanged — proposers are injected via `PipelineDependencies` |
| `MetaLearningBus` | Unchanged — FIFO queue; embedding-aware packages are valid ChangePackages |
| `ChangePackage` | Unchanged schema — artifact travels in existing `reason: tuple[str, ...]` |
| `replay_validate()` | Unchanged — extended variant is additive |
| `ShadowEvaluator` | Unchanged — regression gate applies to all proposals equally |
| `OscillationDetector` | Unchanged — embedding-induced oscillation caught here automatically |
| `L4StateWriter` / `L4VersionStore` | Unchanged — all writes go through existing protocol |
| All L5 safety constraints | Unchanged and non-bypassable |
| `l0_threshold_tuner` | Unchanged — used as fallback when embedding unavailable |
| `rag_optimizer` | Unchanged — used as fallback when embedding unavailable |
| `config_surfaces.py` | Extended only: add cross-namespace whitelist entry for Phase E |

---

## ACCEPTANCE CRITERIA

1. **Replay determinism (NN-set + index hash)**: Same inputs → same `supporting_trace_ids` + same `artifact.index_version_hash` + same `EmbeddingArtifact.content_hash()` across two runs via `replay_validate_with_nn_set()`. [R1]
2. **Delta-only structural guard**: `assert_delta_only()` is called by all embedding-aware proposers; unit test confirms `AbsoluteMutationViolation` is raised when absolute key present.
3. **Time-shift enforcement**: Integration test asserts that telemetry anomaly signal written at cycle t produces no routing change at cycle t; change is observable only at cycle t+1.
4. **Graceful degradation**: With `EmbeddingSearchProvider` returning empty results, pipeline produces identical output to heuristic-only baseline (negative-control test).
5. **Authority gate compliance**: No embedding-derived ChangePackage bypasses `ShadowEvaluator` or `OscillationDetector` (existing tests still pass).
6. **Namespace isolation (namespace + index_id)**: Cross-namespace DPO query without whitelist raises `CrossNamespaceViolation`; cross-index query (e.g., DPO querying healing_contexts) raises `CrossNamespaceViolation`. [I9]
7. **Negative-control**: Removing embedding guidance produces a measurable difference in proposal confidence values — proving the feature is used, not just wired.
8. **Mock testability**: `MockEmbeddingSearchProvider` produces identical results to `LocalFAISSStore` for fixed corpus; replay tests pass against mock without SSD dependency.

---

## IMPLEMENTATION PHASES

| Week | Deliverable |
|---|---|
| 1 | `EmbeddingArtifact` type + `EmbeddingSearchProvider` protocol + `assert_delta_only` guard + `MetaLearningEmbeddingService` skeleton |
| 2 | Phase A: Telemetry anomaly signal path (L6→L4, time-shifted) |
| 3 | Phase B: `EmbeddingEnhancedPatternAnalysisEngine` + ReplayValidator extension |
| 4 | Phase C: `EmbeddingAwareL0Proposer` + `EmbeddingAwareRAGProposer` + fallback wiring |
| 5 | Phase D: DPO namespace isolation + L4 immutable archive |
| 6 | Phase E: Cross-namespace whitelist + Merkle recompute + full acceptance suite |

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

