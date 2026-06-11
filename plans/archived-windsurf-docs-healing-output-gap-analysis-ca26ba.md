---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\healing-output-gap-analysis-ca26ba.md'
original_relative_path: 'healing-output-gap-analysis-ca26ba.md'
source_sha256: f62333d2520917269817e537b17de8f64dd9f72885b530530897a469806e0004
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Healing Output Persistence Gap Analysis — Full AST Review
**File:** `docs/reports/plans/healing-output-gap-analysis-ca26ba.md`
**Scope:** Complete AST trace of `_fire_meta_learning_intake` → `system_learning` pipeline
**Status:** Analysis only — no implementation. Awaiting confirmation before any code changes.

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


## Executive Summary

A full AST-level trace of `execute_ssot._fire_meta_learning_intake` (lines 120–383) through
all `system_learning` engines, types, stores, ports, and pipeline stages reveals **17 distinct
persistence gaps**. The four previously identified gaps (raw events, aggregated stats, success
rate store EMA, intake record versioning) are confirmed and classified below. Thirteen
additional gaps are newly identified.

Gaps are grouped by **severity**:

| Severity | Count | Description |
|---|---|---|
| **CRITICAL** | 5 | Data lost across process restarts, cross-run continuity broken |
| **HIGH** | 6 | Computed artifacts silently discarded, no recovery path |
| **MEDIUM** | 4 | Partial persistence, schema fragility, or silent swallow risk |
| **LOW** | 2 | Audit/traceability only, no functional loss |

---

## Data Flow Map: What Is Computed vs. What Is Persisted

```
execute_ssot._fire_meta_learning_intake()
│
├── [A] Aggregate HealingOutcomeEvents into HealingOutcomeAggregator
│     computes: per-(healer_id, tier, failure_type) success/failure counts + success_rate
│     persists: → InMemoryHealingOutcomeIntakeStore (process-local only)  ← GAP-1
│
├── [B] Build HealingOutcomeIntakeRecord via HealingOutcomeIntakeAdapter
│     computes: schema_version=1, created_utc=0 ← GAP-2, sorted snapshot, proposal
│     persists: → InMemoryHealingOutcomeIntakeStore (never survives process exit) ← GAP-1
│
├── [C] Produce failure_vector per healing action
│     computes: bge-m3 or hash-fallback embedding tuple
│     persists: → appended to _faiss_vectors list (only if non-None)
│
├── [D] FAISS cross-run persistence (healing_context_v1)
│     computes: merged prior + new vectors, FIFO-capped at 1000
│     persists: → logs/faiss_store/healing_context_v1/*.{index,meta,manifest} ← PARTIAL
│               GAPS: manifest integrity not validated before write ← GAP-3
│                     embedder_id = "hash-fallback" (not content-hash) ← GAP-4
│                     no atomic rename — partial write not protected ← GAP-5
│
├── [E] Update L4 state: recent_failure_vectors (novelty)
│     computes: merged list capped at 200
│     persists: → state_mgr.state["meta_learning"]["recent_failure_vectors"]
│               state_mgr.update_meta_learning writes to runtime_state.json ← OK
│               BUT: timestamp_utc=0 on every HealingOutcomeEvent ← GAP-2
│                    no schema_version on meta_learning sub-key ← GAP-6
│
└── [F] run_pipeline() via pipeline_factory.build_pipeline_deps()
      │
      ├── [F1] Step 8: healing_outcome_intake_adapter.build_record()
      │     computes: MOCK aggregator with hard-coded test_healer/test_failure ← GAP-7
      │     persists: → InMemoryHealingOutcomeIntakeStore inside run_pipeline
      │               (entirely separate store from [B], real events NOT forwarded) ← GAP-7
      │
      ├── [F2] Step 8.5: healing_config_optimizer.create_snapshot_from_intake()
      │     computes: HealingOutcomeAggregateSnapshot keyed by (healer_name, tier, failure_type)
      │     persists: → l4_writer.write_l4b_healing_snapshot() — only if l4_writer present
      │               BUT: build_pipeline_deps returns NoOpL4StateWriter ← GAP-8 (verify needed)
      │               HealingOutcomeAggregateSnapshot itself never written to JSONL ← GAP-9
      │
      ├── [F3] Step 8.6: PatternAnalysisEngine.analyze()
      │     computes: PatternAnalysisReport with cluster findings and pattern_digest
      │     persists: NOTHING — pattern_report is local variable, never persisted ← GAP-10
      │               W3-PATTERN-DIGEST printed to stdout only ← GAP-10
      │
      ├── [F4] Step 8.7: _retrieve_semantic_context()
      │     computes: embedding_metadata dict (topk_hashes, scores, artifact_hash, wc_digest)
      │     persists: NOTHING — informational only, no store ← GAP-11 (intentional, audit only)
      │               W-C-DETERMINISM-DIGEST printed to stdout only ← audit loss ← GAP-12
      │
      ├── [F5] Steps 8.8–8.10: Shadow drift → PolicyRecommendation → ProfileProposal
      │     computes: DriftSummary, PolicyRecommendation, RetrievalProfileProposal
      │     persists: → l4_writer.write_l4c_* (guarded by try/except, silently swallowed) ← GAP-13
      │               BUT only if _8_5_aggregate_snapshot is not None (GAP-7 cascade) ← GAP-13
      │               _shadow_telemetry_batch is module-global mutable list ← GAP-14
      │
      ├── [F6] Step 6b/6c: ResourcePrediction + RollbackRefinementDecision proposals
      │     computes: ChangePackage wrappers from injected bytes
      │     persists: → only if proposal_only=False AND version_store present (never in practice) ← GAP-15
      │               proposals returned as tuple but caller ignores return value ← GAP-15
      │
      └── [F7] HealingSuccessRateStore (DefaultOutcomeWriteBackHook)
            computes: EMA success rates per error_signature, export_state() snapshot
            persists: → ONLY in-memory (_default_store module singleton) ← GAP-16
                      export_state() exists but is NEVER called from any production path ← GAP-16
                      runtime_state.json["meta_learning"]["success_rates"] NOT populated ← GAP-16
```

---

## Gap Catalogue

### GAP-1 (CRITICAL): `HealingOutcomeIntakeRecord` never durably persisted

**Location:** `execute_ssot.py:248–253`, `in_memory_healing_outcome_intake_store.py:1–44`

**What happens:** `_fire_meta_learning_intake` always instantiates a fresh
`InMemoryHealingOutcomeIntakeStore`. The `adapter.persist_record(record)` call at line 253
writes to this store's in-memory `_records` list. After `_fire_meta_learning_intake` returns,
the store goes out of scope and is garbage-collected. Every `HealingOutcomeIntakeRecord`
produced in production is lost at process exit.

**What is missing:** A `FileBackedHealingOutcomeIntakeStore` implementation (or equivalent
JSONL append-writer) that survives process restarts. The `HealingOutcomeIntakeStore` protocol
in `system_learning/ports/healing_outcome_intake_store.py` is defined but no file-backed
implementation exists anywhere in the codebase.

**Impact:** The entire meta-learning feedback loop has no durable intake record. Cross-run
learning is impossible for the aggregated stats path. The FAISS store is the only surviving
cross-run artifact (see GAP-3–GAP-5 for its own issues).

---

### GAP-2 (CRITICAL): `timestamp_utc=0` on all `HealingOutcomeEvent` objects

**Location:** `execute_ssot.py:238`, `healing_outcome_aggregator.py` (ingest path)

**What happens:** Every `HealingOutcomeEvent` ingested in `_fire_meta_learning_intake`
has `timestamp_utc=0` (hardcoded literal). The aggregator's `snapshot()` produces
`HealingOutcomeStats` records with no usable temporal information. Similarly, the
`HealingOutcomeIntakeRecord` is built with `created_utc=0` (line 252).

**What is missing:** `int(time.time())` or an injected `now_utc` value must replace the
`0` literals in both the per-event construction (line 238) and the `adapter.build_record()`
call (line 252). Without real timestamps, cross-run temporal ordering, TTL eviction,
and any window-based aggregation are meaningless.

**Impact:** Even if GAP-1 is fixed, all persisted records will have `created_utc=0`, making
temporal queries and expiry logic impossible. Downstream optimizer window calculations are
corrupted.

---

### GAP-3 (CRITICAL): FAISS persist uses wall-clock `int(time.time())` — non-deterministic

**Location:** `execute_ssot.py:312`, `local_faiss_store.py:finalize_build`

**What happens:** `_faiss_writer.finalize_build(..., built_at_utc=int(_time_faiss.time()), ...)`
injects a wall-clock timestamp into the FAISS manifest. This violates the determinism
contract throughout the rest of the pipeline (all other timestamps are injected). On replay
or parallel runs, the manifest hash changes each execution, breaking any content-hash keyed
idempotency.

**What is missing:** `built_at_utc` must be passed in from `state_mgr` or derived from
`healing_actions` timestamps — not read from `time.time()` inside the function.

**Impact:** FAISS manifests are non-deterministic across runs. Replay validation of the
FAISS-backed retrieval path cannot be guaranteed.

---

### GAP-4 (HIGH): FAISS `embedder_id` conflates semantic meaning of content-hash

**Location:** `execute_ssot.py:315–316`

**What happens:**
```python
_vec_source_str = "bge-m3" if _is_bge else "hash-fallback"
_faiss_writer.persist_to_disk(_faiss_idx, _faiss_disk_dir, embedder_id=_vec_source_str, ...)
```
`embedder_id` is set to the human-readable source label (`"bge-m3"` or `"hash-fallback"`)
rather than a content-addressed model checksum. The `persist_to_disk` signature expects an
identifier for integrity verification of the embedding model, not a source tag.

**What is missing:** A stable, versioned `embedder_id` (e.g. `"BAAI/bge-m3-v1"` with a
checksum, or a frozen constant from `EmbeddingStorageLayout`) must be used. The
`_vec_source_str` should be written as a separate metadata field, not the primary `embedder_id`.

**Impact:** FAISS manifest integrity checks across runs with the same model will fail if the
env flag changes. Dimension-mismatch guard (line 290) will pass incorrectly when same
embedding size but different model is used.

---

### GAP-5 (HIGH): No atomic write protection for FAISS 3-file artifact

**Location:** `execute_ssot.py:317–322`, `local_faiss_store.py:persist_to_disk`

**What happens:** `persist_to_disk` writes three files (`*.index`, `*.meta`, `*.manifest`)
sequentially. If the process is interrupted between files (OOM, signal, crash), the artifact
directory contains a partially-written index that will pass the existence check on next run
(`_faiss_disk_dir.exists()` at line 282) but may fail `load_from_disk` with `ManifestIntegrityError`
— which is silently swallowed (line 294). The new run then starts fresh, losing prior vectors.

**What is missing:** Write to a temp directory, then `os.rename()` (atomic on POSIX, nearly
atomic on Windows with `os.replace()`). The temp-then-rename pattern must wrap the entire
3-file write.

**Impact:** Power-loss or OOM during FAISS write permanently loses all accumulated prior
vectors. Silent swallow at line 294 means this loss is never surfaced.

---

### GAP-6 (HIGH): `meta_learning` sub-key in `runtime_state.json` has no schema version

**Location:** `execute_ssot.py:340–344`, `state_mgr.update_meta_learning`

**What happens:** `state_mgr.update_meta_learning({"total_experiences": ..., "experience": ...})`
writes an unversioned dict into `runtime_state.json["meta_learning"]`. No `schema_version`
field is present, no migration path exists. The `recent_failure_vectors` list (line 338)
is stored as a raw list of lists with no type annotation or version marker.

**What is missing:** A `schema_version` key (e.g. `"meta_learning_schema": 1`) must be
written alongside any `meta_learning` update. A validation helper analogous to the
`HealingOutcomeIntakeRecord.__post_init__` validator should guard this write.

**Impact:** Silent schema drift across deployments. Any future structural change to the
`meta_learning` sub-key will silently corrupt existing state without detection.

---

### GAP-7 (CRITICAL): `run_pipeline()` Step 8 uses a mock aggregator, not real healing data

**Location:** `meta_learning_pipeline.py:1228–1248`

**What happens:** Step 8 in `run_pipeline()` constructs a brand-new `HealingOutcomeAggregator`
with a hard-coded mock event (`healer_id="test_healer"`, `failure_type="test_failure"`,
`timestamp_utc=9999`). The real aggregator built in `_fire_meta_learning_intake` is passed as
`healing_outcome_intake_adapter` in `PipelineDependencies`, but inside `run_pipeline`, the
adapter's existing store is **not read** — instead, a new mock record is built and persisted
into a fresh `InMemoryHealingOutcomeIntakeStore` local to the adapter instance.

**What is missing:** `run_pipeline` Step 8 should check whether the injected adapter already
has persisted records (via `adapter.store.get_records()`) and use those. If none exist,
it should skip rather than inject mock data. The mock event is a testing artifact that should
never reach production code paths.

**Impact:** The `HealingConfigOptimizer` in Step 8.5 operates on synthetic mock data, not
real healing outcomes. All downstream threshold proposals are computed from fabricated inputs.
This is the most structurally dangerous gap: the optimizer is running but on garbage data.

---

### GAP-8 (HIGH): `build_pipeline_deps` wires `NoOpL4StateWriter` by default

**Location:** `system_learning/pipelines/pipeline_factory.py` (not read, but inferred from
`execute_ssot.py:368–371` — `build_pipeline_deps(repo_root=REPO_ROOT, healing_outcome_intake_adapter=adapter)`
with no `l4_state_writer` argument)

**What happens:** `l4_state_writer` is an optional field in `PipelineDependencies`
(default `None`). When `None`, Step 8.5 at line 1262–1273 guard-checks
`if deps.l4_state_writer is not None` and skips the `write_l4b_healing_snapshot` call.
If `pipeline_factory.build_pipeline_deps` does not inject a `FileBackedL4StateWriter`, all
L4A/L4B/L4C writes are silently no-oped.

**What is missing:** `build_pipeline_deps` must inject a `FileBackedL4StateWriter` pointing
to a stable directory (e.g. `REPO_ROOT / "logs" / "l4_state"`) in production invocations.
The factory must also expose a mechanism to verify which implementation was injected.

**Impact:** All `write_l4b_healing_snapshot`, `write_l4c_shadow_drift`,
`write_l4c_policy_recommendation`, and `write_l4c_retrieval_profile_proposal` calls are
no-ops in production. The entire L4 state layer is disabled silently.

---

### GAP-9 (HIGH): `HealingOutcomeAggregateSnapshot` never written to JSONL corpus

**Location:** `meta_learning_pipeline.py:1258–1259`

**What happens:** `aggregate_snapshot = deps.healing_config_optimizer.create_snapshot_from_intake(intake_record, ...)`
produces a `HealingOutcomeAggregateSnapshot` with deterministic canonical bytes
(`aggregate_snapshot.canonical_bytes()`). This is passed to `write_l4b_healing_snapshot`
(if the writer is present, see GAP-8), but is never appended to any JSONL corpus for
historical training.

**What is missing:** After the L4B write, `aggregate_snapshot.canonical_bytes()` (or a
JSON-serialized form) should be appended to a JSONL file under
`data/corpus/healing_contexts_corpus.jsonl` (which already exists in the repo). This would
feed `historical_ingestion_orchestrator.ingest_and_build_indexes_with_embedder` on next
index rebuild, closing the feedback loop.

**Impact:** Historical aggregate snapshots cannot be replayed for embedding index rebuild.
The FAISS index can only be populated from live vectors (GAP-1 cascade), not from
reconstructed historical windows.

---

### GAP-10 (HIGH): `PatternAnalysisReport` from W3 is never persisted

**Location:** `meta_learning_pipeline.py:1297–1303`

**What happens:** `pattern_report = _analyze_historical_patterns(deps, _8_5_aggregate_snapshot, ...)`
returns a `PatternAnalysisReport` with `findings`, `pattern_digest`, and cluster metadata.
The digest is printed to stdout (`print(f"W3-PATTERN-DIGEST: ...")`). The `pattern_report`
object is only passed forward to `_retrieve_semantic_context()` (Step 8.7) for informational
context enrichment. It is never written to any store, file, or L4 state slot.

**What is missing:**
1. Write `pattern_report` to an L4C slot (a new `write_l4c_pattern_report` method) or
   append to a JSONL file (`data/corpus/pattern_analysis_history.jsonl`).
2. Persist the `pattern_digest` to `runtime_state.json["meta_learning"]["last_pattern_digest"]`
   for cross-run novelty comparison.

**Impact:** Pattern findings are ephemeral. The pattern analysis engine has no memory of
prior runs. Each run re-clusters from scratch, defeating the purpose of historical pattern
detection. Repeated failure motifs cannot be tracked across runs.

---

### GAP-11 (MEDIUM): Semantic retrieval `wc_determinism_digest` printed but not persisted

**Location:** `meta_learning_pipeline.py:664–665`, `_retrieve_semantic_context` return dict

**What happens:** `W-C-DETERMINISM-DIGEST` is printed to stdout. The returned
`embedding_metadata` dict (containing `wc_determinism_digest`, `embedding_artifact_hash`,
`topk_hashes`) is only used to attach `embedding_context_hash` to `threshold_proposal`
(line 1389). The full `embedding_metadata` dict is never written to any store.

**What is missing:** `embedding_metadata` should be written to an audit log (e.g.
`logs/embedding_audit.jsonl`) appended per-run with `created_utc`. This provides a
replay-verifiable record of which vectors influenced which proposals.

**Impact:** C0 informational context that influenced threshold proposals is not
auditable after the fact. `wc_determinism_digest` verification is only possible if stdout
logs are preserved (not guaranteed).

---

### GAP-12 (MEDIUM): Module-global `_shadow_telemetry_batch` is not process-safe

**Location:** `meta_learning_pipeline.py:88`, `_accumulate_shadow_telemetry`,
`_analyze_shadow_drift_and_write`

**What happens:** `_shadow_telemetry_batch: list[dict[str, Any]] = []` is a module-level
mutable list. `GAP-015` (line 925 in `run_pipeline`) clears it at pipeline entry, which
prevents _same-call_ contamination. However:
1. If `run_pipeline` is called concurrently (e.g. ThreadPoolExecutor in `execute_ssot`),
   two threads will race on `_shadow_telemetry_batch.append()` and `.clear()`.
2. The batch is cleared even on pipeline failure (`GAP-015` runs before the freeze gate
   check — but `_shadow_telemetry_batch.clear()` at line 149 is inside
   `_analyze_shadow_drift_and_write`, which is only called if `_8_5_aggregate_snapshot is not None`
   (i.e. not called on GAP-7 cascade path). If `_8_5_aggregate_snapshot` is None, the
   batch accumulates across runs without being cleared.

**What is missing:** `_shadow_telemetry_batch` must be cleared unconditionally at the end
of `run_pipeline` regardless of the `_8_5_aggregate_snapshot` guard. For thread safety,
use a local variable pattern or lock.

**Impact:** Cross-run shadow telemetry contamination. Drift analysis for run N may include
telemetry from run N-1 (if run N-1 had no aggregate snapshot, see GAP-7).

---

### GAP-13 (HIGH): `write_l4c_*` calls are inside bare `try/except: pass` — silent loss

**Location:** `meta_learning_pipeline.py:137–146`, `183–192`, `224–234`
(all three `_analyze_shadow_drift_and_write`, `_generate_policy_recommendation_and_write`,
`_create_proposal_and_write` helper functions)

**What happens:** Every L4C write is wrapped in:
```python
except Exception:
    # L4 write failure should not break pipeline
    pass
```
This is a **completely silent swallow** — no logging, no telemetry, no counter increment.
If the `FileBackedL4StateWriter` fails (disk full, permissions, serialization error),
the failure is invisible.

**What is missing:** The `except` block must at minimum call `logger.warning(...)` with
the exception and a structured event name. Silent pass is forbidden by the
`OutcomeWriteBackHook` contract ("MUST emit structured telemetry on failure (never fully
silent)") and by the constitutional rules (§1.5 exception path verification).

**Impact:** L4C persistence failures are undetectable in production. DriftSummary,
PolicyRecommendation, and RetrievalProfileProposal can be silently lost with no observable
signal.

---

### GAP-14 (MEDIUM): `HealingSuccessRateStore` EMA state never written to `runtime_state.json`

**Location:** `healing_success_rate_store.py:112–118`, `outcome_write_back_hook.py:89`

**What happens:** `DefaultOutcomeWriteBackHook.on_outcome()` calls
`self._store.record_outcome(healing_input.error_signature, success)` which updates the
in-memory `_default_store` singleton. `export_state()` returns a full
`{"rates": ..., "counts": ..., "owner_pid": ...}` snapshot. However:
1. `export_state()` is **never called** from any production code path.
2. `runtime_state.json` has no `meta_learning.success_rates` or `meta_learning.ema_state`
   key populated by any call.
3. The `MetaPriorProvider` seam reads from the in-memory store only; after process restart,
   all learned priors revert to `_NEUTRAL_PRIOR = 0.5`.

**What is missing:** A post-commit telemetry phase hook must call
`store.export_state()` and write the result to
`runtime_state.json["meta_learning"]["success_rate_ema"]`. The write must use the
`RuntimeStateManager` (not direct file I/O) and must be gated to the post-commit phase
only (governance constraint).

**Impact:** All EMA-learned success rate priors are ephemeral. Cross-run meta-learning via
`MetaPriorProvider` is impossible. The system always routes with neutral 0.5 priors
regardless of historical outcomes.

---

### GAP-15 (MEDIUM): `run_pipeline()` return value is silently discarded by `_fire_meta_learning_intake`

**Location:** `execute_ssot.py:372–378`

**What happens:**
```python
_ml_run_pipeline(
    now_utc=_now_utc, window_start_utc=_window_start_utc, window_end_utc=_now_utc,
    cfg=_ml_cfg, deps=_ml_deps,
)
```
`run_pipeline` returns `tuple[Any, ...]` of validated `ChangePackage` proposals. The return
value is not captured. In `proposal_only=True` mode (the default), these proposals represent
the system's self-assessment of needed threshold changes — but they are immediately discarded.

**What is missing:**
1. Capture the return value: `_proposals = _ml_run_pipeline(...)`.
2. Serialize and append proposals to `logs/proposals/threshold_proposals.jsonl` (or similar)
   with `now_utc` and a run correlation ID.
3. At minimum, log the count: `logging.info("[MetaLearning] %d threshold proposals generated.", len(_proposals))`.

**Impact:** Threshold adjustment proposals computed from healing outcomes are silently dropped.
The optimizer runs but produces no observable artifact. There is no mechanism to review,
approve, or activate proposals from prior runs.

---

### GAP-16 (CRITICAL): No durable store for `HealingOutcomeIntakeStore` — missing implementation

**Location:** `system_learning/ports/healing_outcome_intake_store.py` (protocol),
`system_learning/engines/in_memory_healing_outcome_intake_store.py` (only implementation)

**What happens:** The `HealingOutcomeIntakeStore` protocol has exactly one concrete
implementation: `InMemoryHealingOutcomeIntakeStore`. A search of the entire `system_learning`
directory confirms no `FileBackedHealingOutcomeIntakeStore`, `JSONLHealingOutcomeIntakeStore`,
or equivalent exists. The `historical_ingestion_orchestrator` writes
`healing_contexts.jsonl` to `raw_staging_dir`, but this is populated only from
`healing_source: list[dict]` passed by the caller — it has no connection to
`HealingOutcomeIntakeRecord` objects.

**What is missing:** A `JSONLBackedHealingOutcomeIntakeStore` that:
1. Accepts a file path (`data/corpus/healing_intake_records.jsonl`).
2. Appends each `HealingOutcomeIntakeRecord` as a JSON line (deterministic field ordering,
   `schema_version` as first key).
3. Provides `read_records(since_utc: int) -> list[HealingOutcomeIntakeRecord]` for
   historical replay.
4. Is injected in `_fire_meta_learning_intake` instead of `InMemoryHealingOutcomeIntakeStore`.

**Impact:** Same as GAP-1 — all intake records are ephemeral. This is the root cause that
makes all other intake-record-dependent gaps (GAP-7, GAP-9) cascade.

---

### GAP-17 (LOW): `trace_id` and `run_id` fields on `HealingOutcomeIntakeRecord` are never populated

**Location:** `healing_outcome_intake_types.py:22–23`, `execute_ssot.py:252`

**What happens:** `adapter.build_record(aggregator=aggregator, created_utc=0, source="execute_ssot")`
does not pass `run_id` or `trace_id`. Both fields default to `None`. `run_id` is defined
as the cross-run correlation identifier but is never sourced from `state_mgr`.

**What is missing:** `state_mgr` should expose a `run_id` (e.g. a UUID set at invocation
start and stored in `runtime_state.json`). This should be passed as `run_id=state_mgr.run_id`
in `build_record()`.

**Impact:** Cross-run correlation between intake records and FAISS vectors is impossible.
The `routing_digest` stored in `_faiss_metas` (line 224) cannot be linked back to the
intake record that produced the corresponding vectors.

---

## Persistence Surface Matrix

| Artifact | Type | Survives Restart | Durable Store | Schema Versioned | Notes |
|---|---|---|---|---|---|
| `HealingOutcomeEvent` (per action) | In-memory | ✗ | ✗ | N/A | Lost at scope exit |
| `HealingOutcomeStats` (aggregated) | In-memory | ✗ | ✗ | N/A | GAP-1 |
| `HealingOutcomeIntakeRecord` | In-memory | ✗ | ✗ | ✓ (schema_version=1) | GAP-1, GAP-16 |
| `HealingOutcomeAggregateSnapshot` | L4B (optional) | Partial | Partial | ✗ | GAP-8, GAP-9 |
| `PatternAnalysisReport` | stdout only | ✗ | ✗ | N/A | GAP-10 |
| `DriftSummary` | L4C (silent except) | Partial | Partial | ✗ | GAP-13 |
| `PolicyRecommendation` | L4C (silent except) | Partial | Partial | ✗ | GAP-13 |
| `RetrievalProfileProposal` | L4C (silent except) | Partial | Partial | ✗ | GAP-13 |
| `ThresholdAdjustmentProposal` | Return value discarded | ✗ | ✗ | N/A | GAP-15 |
| `HealingSuccessRateStore` EMA | In-memory singleton | ✗ | ✗ | ✗ | GAP-14 |
| FAISS vectors | Disk (logs/faiss_store) | ✓ | ✓ | Partial | GAP-3, GAP-4, GAP-5 |
| `recent_failure_vectors` | runtime_state.json | ✓ | ✓ | ✗ | GAP-6 |
| `embedding_metadata` / W-C-digest | stdout only | ✗ | ✗ | N/A | GAP-11, GAP-12 |
| `run_pipeline()` proposals | Discarded | ✗ | ✗ | N/A | GAP-15 |

---

## Dependency Graph: Gap Cascade Order

```
GAP-16 (no file-backed store impl)
  └── GAP-1 (InMemory used everywhere)
        └── GAP-7 (run_pipeline uses mock data)
              ├── GAP-9 (aggregate snapshot never in JSONL)
              └── GAP-13 (L4C writes conditionally skipped)
                    └── GAP-12 (shadow telemetry batch not cleared)

GAP-2 (timestamp=0)
  └── corrupts GAP-1 artifacts even if fixed

GAP-14 (EMA store not persisted)
  └── independent of GAP-1; requires separate fix

GAP-3, GAP-4, GAP-5 (FAISS write issues)
  └── independent; FAISS is the only currently-surviving cross-run artifact

GAP-8 (NoOpL4StateWriter)
  └── GAP-9, GAP-10 (no L4B/L4C writes)
        └── GAP-13 (silent except compounds this)

GAP-15 (proposals discarded)
  └── requires GAP-7 fix first to be meaningful
```

---

## Recommended Fix Priority Order

1. **GAP-16** → Implement `JSONLBackedHealingOutcomeIntakeStore` (unblocks GAP-1)
2. **GAP-1** → Wire file-backed store in `_fire_meta_learning_intake`
3. **GAP-2** → Replace `timestamp_utc=0` and `created_utc=0` with real timestamps
4. **GAP-7** → Fix `run_pipeline` Step 8 to use real records, not mock data
5. **GAP-8** → Inject `FileBackedL4StateWriter` in `build_pipeline_deps`
6. **GAP-14** → Add EMA export hook to post-commit telemetry phase
7. **GAP-13** → Replace silent `pass` with `logger.warning` in all L4C write guards
8. **GAP-5** → Add atomic rename pattern to FAISS persist
9. **GAP-10** → Persist `PatternAnalysisReport` to L4C or JSONL
10. **GAP-15** → Capture and persist proposal return value
11. **GAP-3** → Replace wall-clock timestamp in FAISS finalize_build
12. **GAP-12** → Unconditional clear of `_shadow_telemetry_batch` at pipeline exit
13. **GAP-6** → Add `schema_version` to `meta_learning` sub-key writes
14. **GAP-9** → Append aggregate snapshots to `healing_contexts_corpus.jsonl`
15. **GAP-4** → Fix FAISS `embedder_id` to use stable versioned checksum
16. **GAP-11** → Write `embedding_metadata` to audit JSONL
17. **GAP-17** → Populate `run_id` and `trace_id` from `state_mgr`

---

## Governance Constraints for All Fixes

The following constraints from the existing hardening overlay apply to every fix above:

1. **Post-commit phase only** — all persistence writes must occur in the post-commit
   telemetry phase, not during routing or healing execution.
2. **No authority-bearing fields** — persisted artifacts must not contain
   `HEALING_CONFIDENCE_X/Y`, tier routing weights, or any field that directly mutates
   routing behaviour.
3. **Deterministic serialization** — all JSON writes must use `sort_keys=True`,
   `separators=(",", ":")`. No `datetime.now()` or `uuid4()` without an injected seed.
4. **Schema version required** — every new store file format must include
   `"schema_version": <int>` as its first key.
5. **Validation helper** — each new store implementation must expose a
   `validate()` method that checks schema_version and required fields before accepting a write.
6. **Cross-run sovereignty** — no fix may allow a run to retroactively mutate records
   from a prior run. Append-only JSONL is the correct pattern.
7. **No silent swallowers** — every `except` block introduced by a fix must call
   `logger.warning` with a structured event name and exception string.

---

*Generated by AST trace of execute_ssot._fire_meta_learning_intake, meta_learning_pipeline.run_pipeline,
healing_outcome_aggregator, healing_outcome_intake_adapter, healing_success_rate_store,
in_memory_healing_outcome_intake_store, l4_state_writer, outcome_write_back_hook,
pattern_analysis_engine, live_run_pipeline_adapter.*

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

