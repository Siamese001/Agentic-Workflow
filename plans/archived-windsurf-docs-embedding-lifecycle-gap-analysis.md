---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\embedding-lifecycle-gap-analysis.md'
original_relative_path: 'embedding-lifecycle-gap-analysis.md'
source_sha256: 71f62a53d74ccff3cb8416f41011eb151f63bd5b405249446330306975801002
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Embedding Lifecycle Gap Analysis
**Reference doc:** `docs/technical/Embedding Lifecycle.md`
**Date:** 2026-03-04

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


## Stage-by-Stage Audit

| Stage | Layer | Status | Key Files |
|---|---|---|---|
| RAW SIGNAL | L2 | ✅ IMPLEMENTED | `state_mgr.state["healing_actions"]` |
| ENCODER | L2 | ⚠️ PARTIAL | `failure_signal_normalizer.py` |
| VECTOR | L1 | ⚠️ PARTIAL | `bmg_embedding_similarity.py` |
| MEMORY | L1 | ❌ NOT WIRED AT ROUTING TIME | `local_faiss_store.py`, `in_memory_vector_store.py` |
| ROUTING | L0 | ⚠️ PARTIAL | `SovereignDecisionEngine._route_decision()` |
| ORCHESTRATION | L3 | ✅ IMPLEMENTED | `execute_ssot.py` execution plan |
| PRE-COMMIT | L2.1 | ✅ IMPLEMENTED | agents |
| VALIDATION | L2.2 | ✅ IMPLEMENTED | `LocationValidatorAgent`, sovereignty tests |
| EXECUTION | L2.3 | ✅ IMPLEMENTED | healers |
| HEALING | L2.4 | ✅ IMPLEMENTED | `DependencyRepairAgent`, `ArchitectureGovernorAgent`, etc. |
| LEARNING LOOP | L4/L6 | ⚠️ PARTIAL | `HealingOutcomeEvent`, `_fire_meta_learning_intake` |
| SYSTEM LEARNING | CORE | ❌ NOT WIRED | `meta_learning_pipeline.py` |

---

## Gap 1 (CRITICAL) — MEMORY stage not wired at routing time

**What the doc says:**
> MEMORY [L1]: vector search against historical incidents returns top matches.
> ROUTING [L0]: uses retrieved metadata — violation types, healer used previously,
> patch applied previously, success/failure history, cluster statistics — to determine
> root cause + healer.

**What exists:**
- `LocalFAISSStore` (`system_learning/engines/local_faiss_store.py`) — real FAISS operations
  are `NotImplementedError` skeletons (Phase 2 placeholder).
- `InMemoryVectorStore` (`agentic_core/L4_state/memory/in_memory_vector_store.py`) —
  dev/testing only, O(N) naive cosine.
- `MetaLearningEmbeddingService` — can retrieve from Seed Embedding Packs (cosine on
  `embeddings.f32`), but requires an explicit embedder injection and pre-built seed packs.
- `_compute_novelty_score` in `SovereignDecisionEngine` — the ONLY embedding use at
  routing time. Computes N=0..3 novelty score from recent failure vectors but does
  NOT retrieve historical incident records or their metadata.

**What is missing:**
1. No code path in `SovereignDecisionEngine._route_decision()` queries a vector store
   before selecting a healer.
2. Retrieved metadata fields ("healer used previously", "patch applied previously",
   "success/failure history", "cluster statistics") are never surfaced at routing time.
3. The novelty score N feeds the gate logic but is a scalar — not a list of similar
   incidents with metadata.

**Files to change:**
- `agentic_core/L0_routing/scripts/execute_ssot.py` — `SovereignDecisionEngine`
- `system_learning/engines/local_faiss_store.py` — fill FAISS Phase 2 skeleton
- New: `agentic_core/L1_cognition/memory/healing_memory_retriever.py`

---

## Gap 2 (CRITICAL) — LEARNING LOOP vectors not persisted to disk

**What the doc says:**
> LEARNING LOOP [L4 storage | L6 telemetry]:
> VECTOR STORED: failure_vector
> METADATA STORED: failure summary, violation types, healer used, repair action,
> success/failure outcome, repo location/files touched, replay_key/routing_digest,
> confidence score, novelty flag/cluster id

**What exists:**
- `HealingOutcomeEvent` type has all required fields EXCEPT `cluster_id` and
  `files_touched` is always empty (never populated by any healer).
- `_fire_meta_learning_intake` stores `failure_vector` ONLY in
  `state_mgr.state["meta_learning"]["recent_failure_vectors"]` — an **in-memory rolling
  window capped at 200 entries, lost on process exit**.
- `InMemoryHealingOutcomeIntakeStore.persist_record()` stores to memory, not disk.
- `LocalFAISSStore` and `local_embedding_population_service.py` exist but are NEVER
  called from `_fire_meta_learning_intake`.

**What is missing:**
1. No disk-persistence path from `_fire_meta_learning_intake` → `LocalFAISSStore`.
2. `files_touched: tuple[str, ...]` in `HealingOutcomeEvent` defaults to empty tuple;
   no healer populates it. The doc requires "repo location / files touched".
3. `cluster_id` not stored — `HealingOutcomeEvent` has `novelty_flag` (bool) but no
   `cluster_id` string as the doc specifies ("novelty flag / cluster id").
4. `failure_vector` is only produced when `BMG_EMBEDDINGS_ENABLED=true` (default: false),
   so the vector slot is `None` for every standard run.

**Files to change:**
- `system_learning/types/healing_outcome_types.py` — add `cluster_id` field
- `agentic_core/L0_routing/scripts/execute_ssot.py` — populate `files_touched` from
  healer action dicts; wire `_fire_meta_learning_intake` → `LocalFAISSStore.add_vectors()`
- `system_learning/engines/local_faiss_store.py` — implement disk persistence (Phase 2)

---

## Gap 3 (CRITICAL) — SYSTEM LEARNING pipeline not wired to live healing runs

**What the doc says:**
> SYSTEM LEARNING [CORE]: system analyzes historical healing events and telemetry.
> Uses vectors + incident metadata.
> Cluster failure patterns, identify recurring failure signatures,
> determine best healer per failure type, compute success rate per agent,
> detect recurring regressions.
> Insights improve routing and healing decision strategies.

**What exists:**
- `system_learning/pipelines/meta_learning_pipeline.py` — sophisticated pipeline with
  `run_pipeline()`, `PatternAnalysisEngine`, RLHF optimizer, policy proposals. ✅
- `HealingOutcomeAggregator` collects stats per (healer_id, tier, failure_type). ✅
- `HealingOutcomeIntakeAdapter.persist_record()` stores to `InMemoryHealingOutcomeIntakeStore`.

**What is missing:**
1. `run_pipeline()` is NEVER called from `execute_ssot.py` after a healing run. The
   pipeline requires `PipelineDependencies(audit_store, telemetry_store, config_provider)`
   which are not connected to live run state.
2. No bridge exists from `InMemoryHealingOutcomeIntakeStore` → `PipelineDependencies`.
3. `_retrieve_semantic_context()` inside `meta_learning_pipeline.py` (W2 stage) uses a
   **4-dimensional hash-based fake vector** (lines 713–719): "For W2, we use a simple
   hash-based approach since no embedder is available". This is not bge-m3 embedding.
4. `PatternAnalysisEngine` requires ≥10 historical embeddings and calls the legacy API
   path in `_analyze_historical_patterns()` when embeddings are disabled.

**Files to change:**
- `agentic_core/L0_routing/scripts/execute_ssot.py` — call `run_pipeline()` after heal
- `system_learning/pipelines/meta_learning_pipeline.py` — replace hash-based W2 vector
  with real bge-m3 call (guarded by kill-switch)
- New: `system_learning/adapters/live_run_pipeline_adapter.py` — bridges
  `InMemoryHealingOutcomeIntakeStore` → `PipelineDependencies`

---

## Gap 4 (SIGNIFICANT) — BMG_EMBEDDINGS_ENABLED defaults to false; entire ENCODER→VECTOR chain inactive

**What the doc says:**
> ENCODER [L2]: normalizes signal text; captures metadata separately.
> VECTOR [L1]: bge-m3 produces failure_vector from normalized text.

**What exists:**
- `normalize_failure_signal()` and `extract_failure_metadata()` are clean and correct. ✅
- `bmg_embed_text()` using BAAI/bge-m3 is implemented. ✅
- Both are gated behind `os.environ.get("BMG_EMBEDDINGS_ENABLED", "false")`.

**What is missing:**
1. When embeddings are off (default), `failure_vector` is always `None`, `novelty_flag`
   always `False`, and the ENCODER stage is never invoked. The lifecycle as documented
   requires a vector for every healing event stored in LEARNING LOOP.
2. No fallback embedding strategy for the MEMORY stage when bge-m3 unavailable — the
   novelty score falls back to a `[BMG-GPU]` string heuristic, not a structured fallback.
3. The env var is undocumented in code; no config surface or `RetrievalProfile` field
   controls it — it's a raw `os.environ` check.

**Files to change:**
- `agentic_core/L0_routing/scripts/execute_ssot.py` — expose `BMG_EMBEDDINGS_ENABLED`
  through `RetrievalProfile` or a config surface, not raw env var
- Consider making a lightweight hash-based fallback vector so `failure_vector` is never
  `None` (16-dim hash vector when bge-m3 unavailable)

---

## Gap 5 (SIGNIFICANT) — W2 semantic retrieval uses fake 4D hash vectors

**Location:** `system_learning/pipelines/meta_learning_pipeline.py` lines 709–719

**What the doc says:**
> VECTOR [L1]: Embedding Model (bge-m3) produces failure_vector = [v1..vN].
> embedding model rarely changes; knowledge grows via incident memory.

**What exists:**
```python
# For W2, we use a simple hash-based approach since no embedder is available
query_hash = hashlib.sha256(failure_signature.encode()).hexdigest()
query_vector = []
for i in range(0, 8, 2):
    val = int(query_hash[i : i + 2], 16) / 255.0
    query_vector.append(val)
```
A 4-dimensional [0,1] vector derived from a SHA-256 hash. This is not semantic.

**What is missing:**
- W2 retrieval must call `bmg_embed_text(failure_signature)` (guarded by kill-switch)
  to produce a real ~1024-dim bge-m3 vector, not a 4D hash.
- The `MetaLearningEmbeddingService` already has the right interface but requires an
  explicit `Embedder` injection that is never wired.

**Files to change:**
- `system_learning/pipelines/meta_learning_pipeline.py` — replace lines 709–719 with
  guarded `bmg_embed_text()` call; wire `MetaLearningEmbeddingService` with bge-m3
  embedder injection

---

## Gap 6 (SIGNIFICANT) — `files_touched` never populated

**What the doc says:**
> METADATA STORED: repo location / files touched

**What exists:**
- `HealingOutcomeEvent.files_touched: tuple[str, ...] = field(default_factory=tuple)` ✅
- `_fire_meta_learning_intake` creates `HealingOutcomeEvent(...)` but never passes
  `files_touched`. It remains an empty tuple for every event.

**What is missing:**
- Healers need to record which files they mutate into the `healing_action` dict
  under a `files_touched` key, which `_fire_meta_learning_intake` can then forward.

**Files to change:**
- `agentic_core/L0_routing/scripts/execute_ssot.py` — extract `files_touched` from
  `action.get("files_touched", [])` when building `HealingOutcomeEvent`
- Each healer agent should populate `files_touched` in its returned action dict

---

## Gap 7 (MINOR) — `cluster_id` not stored in `HealingOutcomeEvent`

**What the doc says:**
> METADATA STORED: novelty flag / cluster id

**What exists:**
- `HealingOutcomeEvent.novelty_flag: bool` ✅
- No `cluster_id` field.

**What is missing:**
- Add `cluster_id: str | None = None` to `HealingOutcomeEvent`.
- `PatternAnalysisEngine` produces cluster labels — these should flow back as
  `cluster_id` on subsequent events that match a known cluster.

**Files to change:**
- `system_learning/types/healing_outcome_types.py`

---

## Gap 8 (MINOR) — ENCODER missing raw stack trace and test failure text

**What the doc says:**
> ENCODER captures: parse stack trace, extract error signature,
> collect repo + execution context, normalize signal text.

**What exists:**
- `normalize_failure_signal()` uses: `failure_type`, `routing_gate`, `agent`, `fix_summary`.
- Missing: raw exception stack trace text, test failure output, the specific file path
  that triggered the failure.

**What is missing:**
- Enriching the normalized text with `error_message` / `stack_trace` fields from the
  action dict (when present) would give bge-m3 more semantic signal to work with.

**Files to change:**
- `agentic_core/L2_execution/healers/failure_signal_normalizer.py`

---

## Implementation Plan

### Phase A — Learning Loop Persistence (prerequisite for all other phases)
**Rationale:** Without persistent cross-run vector storage, MEMORY and SYSTEM LEARNING
cannot function. This unblocks everything downstream.

1. **A1** — Add `cluster_id: str | None` to `HealingOutcomeEvent`
   (`system_learning/types/healing_outcome_types.py`)
2. **A2** — Populate `files_touched` from `action.get("files_touched", [])` in
   `_fire_meta_learning_intake` (`execute_ssot.py`)
3. **A3** — Implement FAISS disk-persistence in `LocalFAISSStore`:
   - `begin_build` → real `faiss.IndexFlatIP` when FAISS available, memory fallback otherwise
   - `finalize_build` → write `.faiss` + `.meta.json` to `EmbeddingStorageLayout` paths
4. **A4** — Wire `_fire_meta_learning_intake` → `LocalFAISSStore.add_vectors()`:
   - After building `HealingOutcomeEvent`, if `failure_vector` is not None, call
     `local_faiss_store.add_vectors(index_id="healing_contexts", vectors=[...], metadatas=[...])`
5. **A5** — Produce a lightweight **fallback vector** when bge-m3 disabled:
   - 16-dim normalized hash vector from `normalize_failure_signal()` output
   - Ensures `failure_vector` is never `None` regardless of embedding kill-switch
   - Stored with a `vector_source: "bge-m3" | "hash-fallback"` metadata field

#### HARDENINGS — Phase A

**1) Fail-Closed Guards**
- Every persisted artifact set MUST consist of exactly three files: `<index.faiss>`,
  `<meta.json>`, `<manifest.json>`. Writing fewer files is a hard-fail; partial writes
  are not committed to the index directory.
- On load: verify `manifest.json` contains `schema_version`, `sha256_index`,
  `sha256_meta_canonical`, `embedder_id`, `model_version`, `dims`, `vector_count`.
  Any hash mismatch or missing field → raise `ManifestIntegrityError`; no best-effort
  fallback, no silent ignore.
- All metadata JSON is canonical before hashing: `json.dumps(sort_keys=True,
  separators=(",",":"), ensure_ascii=True)`. Truncation of string fields follows a
  single deterministic rule: first N bytes, UTF-8 safe. This rule is in one function
  only, called from all write paths.

**2) Determinism Hooks**
- `LocalFAISSStore.finalize_build()` MUST print exactly once per call:
  `W-A-DETERMINISM-DIGEST: <hex64>` where the digest binds:
  `embedder_id | model_version | dims | vector_count | sha256(index_bytes) |
  sha256(meta_canonical_bytes) | sha256(manifest_bytes)`.
- Replay rule: if `BMG_EMBEDDINGS_ENABLED=false`, the stored `failure_vector` MUST
  be the hash-fallback vector (A5); the transcript must supply it. Silent recomputation
  on reload is forbidden — recomputed vectors must be flagged `vector_source="recomputed"`
  and trigger a WARNING log.

**3) Negative Controls (exit-0)**
- `W_A_NEGCTRL_TAMPER=1`: flip one byte in `manifest.json` before load → test MUST
  `pytest.mark.xfail(strict=True)` and exit 0.
- Restore run (env unset, original manifest): MUST pass with `W-A-DETERMINISM-DIGEST`
  printed and digest identical across two back-to-back invocations.

**4) CI/AST Gates**
- AST rule: ban any `faiss.write_index` / `faiss.read_index` call that does not appear
  inside `LocalFAISSStore` methods. Any call outside that class → CI HARD FAIL.
- AST rule: ban any `open(...).read()` or `Path.read_bytes()` on a `.faiss` file that
  is not preceded (in the same function scope) by a call to the manifest verification
  function.

**5) Acceptance Criteria (SSOT)**
```
python -m pytest tests/system_learning/test_phase_a_learning_loop.py -q --color=no
```
Must collectively verify: (a) passes, (b) `W-A-DETERMINISM-DIGEST` printed exactly
once, (c) two consecutive runs produce the identical digest, (d) `W_A_NEGCTRL_TAMPER=1`
causes `xfail` with exit code 0, (e) restore run (no tamper) passes.

---

### Phase B — Memory Search at Routing Time
**Rationale:** Connects the stored vectors to `SovereignDecisionEngine` so routing
uses historical incident metadata as the doc specifies.

6. **B1** — Create `agentic_core/L1_cognition/memory/healing_memory_retriever.py`:
   - `retrieve_similar_incidents(signal_text, top_k=5)` → queries `LocalFAISSStore`
   - Returns list of `SimilarIncident(healer_id, success_rate, patch_summary, cluster_id)`
7. **B2** — Inject `HealingMemoryRetriever` into `SovereignDecisionEngine.__init__`
   (optional, guarded — null object pattern when unavailable)
8. **B3** — In `_route_decision()`: before selecting tier, call retriever and check:
   - If top-k all succeeded with a specific healer → boost deterministic confidence
   - If top-k all failed with a specific healer → apply failure_prior penalty
   - If novelty N=3 and no matches → escalate to higher tier regardless of confidence
   - Retriever output is **advisory only** — cannot override L5 policy gates

#### HARDENINGS — Phase B

**1) Fail-Closed Guards**
- C0 informational-only is a hard contract: retrieval outputs populate `advisory_context`
  only. They MUST NOT set `tier`, `tool`, `policy`, any allowlist entry, or any
  threshold. This is not a convention — it is enforced at runtime.
- Add a `SovereigntyError` raise in `_route_decision()`: if any code path consumes an
  embedding-derived field to select or override a routing tier, raise immediately.
- Bounded context: `retrieve_similar_incidents()` enforces `max_k` (default 5, hard
  ceiling 20), `max_chars` per field (256), deterministic truncation via the same
  canonical truncation function from Phase A. All secret/key patterns are redacted
  (regex allowlist) before the result is returned to the caller.

**2) Determinism Hooks**
- Top-k ordering is deterministic: primary sort by score descending; tie-break by
  `(content_hash ASC, trace_id ASC)`. No wall-clock, no random seed.
- `retrieve_similar_incidents()` MUST print exactly once per call:
  `W-B-DETERMINISM-DIGEST: <hex64>` binding:
  `query_normalized | top_k_ids (sorted) | scores_round6 | store_manifest_hash`.

**3) Negative Controls (exit-0)**
- `W_B_NEGCTRL_TAMPER=1`: inject a test shim that attempts to copy
  `advisory_context["top_score"]` into the tier selection variable. Test MUST
  `pytest.mark.xfail(strict=True)` on the `SovereigntyError` and exit 0.
- Restore run (no shim): advisory path executes without `SovereigntyError`; digest
  is printed and identical across two runs.

**4) CI/AST Gates**
- AST rule: ban any reference to embedding-derived field names (`top_score`,
  `pattern_boost`, `retrieval_score`, `advisory_context` sub-fields) inside the
  tier selection code path of `_route_decision()`. CI HARD FAIL on violation.
- AST rule: all retrieval result consumption MUST pass through a single adapter
  function (e.g. `_apply_advisory_context()`). Direct field access on retrieval
  results elsewhere → CI HARD FAIL.

**5) Acceptance Criteria (SSOT)**
```
python -m pytest tests/agentic_core/L1_cognition/test_phase_b_memory_routing.py -q --color=no
```
Must collectively verify: (a) passes, (b) `W-B-DETERMINISM-DIGEST` printed exactly
once, (c) two consecutive runs produce the identical digest, (d) `W_B_NEGCTRL_TAMPER=1`
causes `xfail` with exit code 0, (e) restore run passes.

---

### Phase C — System Learning Pipeline Integration
**Rationale:** Connects the offline batch pipeline to live run data.

9. **C1** — Create `system_learning/adapters/live_run_pipeline_adapter.py`:
   - Bridges `InMemoryHealingOutcomeIntakeStore` → `TelemetryStore` protocol
   - Allows `run_pipeline()` to consume the in-memory store from a heal run
10. **C2** — After `_fire_meta_learning_intake()` completes, call `run_pipeline()` with
    a minimal `PipelineDependencies` (audit from L4 state, telemetry from adapter)
    — in `proposal_only=True` mode (no mutations)
11. **C3** — Replace hash-based W2 vector in `_retrieve_semantic_context()` with
    guarded `bmg_embed_text()` call; inject `bmg_embed_text` as the `Embedder`
    into `MetaLearningEmbeddingService`

#### HARDENINGS — Phase C

**1) Fail-Closed Guards**
- `proposal_only=True` is the immutable default. Activation (Stage B) requires
  explicit dual-injection proof: two independent approval objects carrying different
  `approver_id` values. Providing one or zero approvals → `ActivationAuthorizationError`
  hard-fail; no partial activation.
- Freeze discipline: during live execution (while `run_pipeline()` is in-flight),
  policy/threshold/tooling mutations are prohibited. Only "append-only proposal
  persistence" is allowed. Any attempt to mutate an active config surface mid-wave →
  hard-fail.
- Kill-switch discipline: when `BMG_EMBEDDINGS_ENABLED=false`, vectors stored with
  `vector_source="hash-fallback"` MUST NOT be consumed by novelty or cluster logic as
  if they were real semantic embeddings. Any such consumption → raise
  `VectorSourceMismatchError`. The kill-switch state is explicit, tagged, and logged.

**2) Determinism Hooks**
- `run_pipeline()` MUST print exactly once per call:
  `W-C-DETERMINISM-DIGEST: <hex64>` binding:
  `pipeline_inputs_snapshot_hash | proposal_outputs_hash | embedder_metadata |
  store_manifest_hash`.
- All generated proposals are serialized in stable key order (canonical JSON) before
  hashing. Proposal ordering within a batch is deterministic (sorted by proposal type,
  then by content hash).

**3) Negative Controls (exit-0)**
- `W_C_NEGCTRL_TAMPER=1`: invoke activation path with only one approval object →
  test MUST `pytest.mark.xfail(strict=True)` on `ActivationAuthorizationError` and
  exit 0.
- Restore run: provide two distinct approval objects → activation succeeds (or is
  staged as proposal); digest is printed and identical across two runs.

**4) CI/AST Gates**
- AST rule: ban any direct config write from `live_run_pipeline_adapter.py` or any
  path reachable from it except into the designated append-only proposals store.
  CI HARD FAIL on any other write target.
- AST rule: ban embedding provider instantiation (e.g. `SentenceTransformer(...)`,
  `bmg_embed_text` import) outside `EmbeddingServiceFactory` or
  `bmg_embedding_similarity.py`. Enforces the factory boundary already present in
  the repo. CI HARD FAIL on violation.

**5) Acceptance Criteria (SSOT)**
```
python -m pytest tests/system_learning/test_phase_c_pipeline_integration.py -q --color=no
```
Must collectively verify: (a) passes, (b) `W-C-DETERMINISM-DIGEST` printed exactly
once, (c) two consecutive runs produce the identical digest, (d) `W_C_NEGCTRL_TAMPER=1`
causes `xfail` with exit code 0, (e) restore run passes.

---

### Phase D — Encoder Enrichment
**Rationale:** More semantic signal → better bge-m3 vectors → better recall.

12. **D1** — Enrich `normalize_failure_signal()` to include `error_message` /
    `stack_trace` fields (first 200 chars) when present in the action dict
13. **D2** — Expose `BMG_EMBEDDINGS_ENABLED` through `RetrievalProfile` config
    surface instead of raw `os.environ` check

---

## Summary: Gaps by Priority

| # | Gap | Severity | Phase |
|---|-----|----------|-------|
| 1 | MEMORY→ROUTING feedback loop missing | CRITICAL | B |
| 2 | Vectors not persisted cross-run | CRITICAL | A |
| 3 | SYSTEM LEARNING not wired to live runs | CRITICAL | C |
| 4 | BMG_EMBEDDINGS_ENABLED off by default; no fallback vector | SIGNIFICANT | A5, D2 |
| 5 | W2 uses fake 4D hash vectors, not bge-m3 | SIGNIFICANT | C3 |
| 6 | `files_touched` never populated | SIGNIFICANT | A2 |
| 7 | `cluster_id` not in `HealingOutcomeEvent` | MINOR | A1 |
| 8 | ENCODER missing stack trace / file path text | MINOR | D1 |

**Stages fully implemented (no gap):**
RAW SIGNAL, ORCHESTRATION, PRE-COMMIT, VALIDATION, EXECUTION, HEALING

---

## Global Governance Addendum

- Every phase defines exactly ONE acceptance pytest command (listed in its SSOT block
  above). That command is the sole arbiter of phase completion.
- Every phase MUST demonstrate: determinism proof (two identical digests across
  back-to-back runs) + negative control (`xfail strict=True`, exit 0) + restore PASS.
- No silent fallbacks anywhere. Every kill-switch transition MUST be: explicit (a
  tagged log line at WARNING or above), fail-closed (default to off/safe), and covered
  by a negative-control test that verifies the hard-fail path.
- Digest format for all phases: `sha256(canonical_utf8_string)`, lowercase hex, 64
  chars. The digest string printed to stdout is the sole replay verification token.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

