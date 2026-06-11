---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\healer-output-system-learning-persistence-400f4c.md'
original_relative_path: 'healer-output-system-learning-persistence-400f4c.md'
source_sha256: 4353379a08423bd7eddda52751ca3da33387fc595851919f67d71ba1ab1cc34e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Healer Output → System Learning Persistence — Integrated Plan

Enable full cross-run system learning by persisting all healer output categories that currently
die at process end in `execute_ssot`, hardened against all 17 AST-identified gaps.

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


## § 0 — Governance Invariants (Non-Negotiable)

All waves below are bound by these invariants. Any implementation that violates them is invalid.

1. **Informational only.** All persisted artifacts are L4 state. No artifact may carry routing,
   safety, execution-tier, or authority-bearing fields.
2. **Forbidden authority fields.** Reject persistence payloads containing any of:
   `route_mode`, `execution_tier`, `safety_threshold`, `policy_override`, `capability_token`,
   `auth_token`, `tool_permissions`, `approval_decision`, `compliance_stamp`,
   `sandbox_envelope`, `mutation_authority`, `model_allowlist_override`,
   `direct_commit_instruction`.
3. **Post-commit phase only.** All writes must execute only in the post-commit telemetry /
   intake phase. Never during routing, policy enforcement, plan assembly, or same-run tier
   selection. Guard: `if phase != "POST_COMMIT_TELEMETRY": raise PersistencePhaseViolation(...)`.
4. **Deterministic serialization.** All JSON writes: `json.dumps(payload, sort_keys=True, separators=(",", ":"))`,
   UTF-8, no pretty-print, no unordered sets, no timestamps in keys.
5. **Schema version required.** Every persisted record family includes `"schema_version": <int>`
   as its first (sort-order) key.
6. **Validation helper.** Before every new write path, `validate_persistence_payload(payload)`
   must: require `schema_version`, canonicalize optional fields, reject forbidden authority
   fields, verify deterministic serializability, bound payload size.
7. **Cross-run sovereignty.** Artifacts may inform future proposal inputs only.
   ```
   Execution → Telemetry → Persistence → Evaluation → Proposal → Validation → Commit
   ```
   Forbidden: `Execution → Persistence → Direct Runtime Mutation`.
8. **No silent swallowers.** Every `except` block on a persistence path must emit
   `logger.warning(...)` with a structured event name and exception string. Bare `pass`
   is prohibited.
9. **No new authority-bearing subsystems.** If a new module is unavoidable it must live
   inside an approved persistence or typing surface only.

---

## § 1 — Problem Statement

`_fire_meta_learning_intake()` in `execute_ssot.py` (lines 120–383) runs at end of every
healing run but routes everything to `InMemoryHealingOutcomeIntakeStore` — destroyed at
process exit. Only FAISS vectors (`logs/faiss_store/healing_context_v1/`) and
`recent_failure_vectors` in `runtime_state.json` survive across runs. The meta-learning
feedback loop has no durable memory.

---

## § 2 — Full Gap Inventory (AST-Identified, 17 Gaps)

### Persistence Surface Matrix

| Artifact | Survives Restart | Durable Store | Schema Versioned | Gap IDs |
|---|---|---|---|---|
| `HealingOutcomeEvent` (per action) | ✗ | ✗ | N/A | GAP-1 |
| `HealingOutcomeStats` (aggregated) | ✗ | ✗ | N/A | GAP-1 |
| `HealingOutcomeIntakeRecord` | ✗ | ✗ | ✓ schema_version=1 | GAP-1, GAP-16 |
| `HealingOutcomeAggregateSnapshot` | Partial | Partial | ✗ | GAP-8, GAP-9 |
| `PatternAnalysisReport` | ✗ (stdout only) | ✗ | N/A | GAP-10 |
| `DriftSummary` | Partial (silent except) | Partial | ✗ | GAP-13 |
| `PolicyRecommendation` | Partial (silent except) | Partial | ✗ | GAP-13 |
| `RetrievalProfileProposal` | Partial (silent except) | Partial | ✗ | GAP-13 |
| `ThresholdAdjustmentProposal` | ✗ (return discarded) | ✗ | N/A | GAP-15 |
| `HealingSuccessRateStore` EMA | ✗ (in-memory singleton) | ✗ | ✗ | GAP-14 |
| FAISS vectors | ✓ | ✓ | Partial | GAP-3, GAP-4, GAP-5 |
| `recent_failure_vectors` | ✓ | ✓ | ✗ | GAP-6 |
| `embedding_metadata` / W-C-digest | ✗ (stdout only) | ✗ | N/A | GAP-11, GAP-12 |
| `run_pipeline()` proposals | ✗ (discarded) | ✗ | N/A | GAP-15 |

### Gap Dependency Cascade

```
GAP-16 (no file-backed HealingOutcomeIntakeStore impl)
  └── GAP-1  (InMemoryStore used everywhere → records ephemeral)
        └── GAP-7  (run_pipeline Step 8 uses mock aggregator, not real records)
              ├── GAP-9  (aggregate snapshot never in JSONL)
              └── GAP-13 (L4C writes conditionally skipped; bare pass)
                    └── GAP-12 (shadow_telemetry_batch not cleared on cascade path)

GAP-2  (timestamp_utc=0 on every event / created_utc=0 on every record)
  └── corrupts all GAP-1 artifacts even after fix

GAP-14 (EMA store export never called)
  └── independent; MetaPriorProvider always returns 0.5

GAP-3, GAP-4, GAP-5 (FAISS write: non-deterministic ts, bad embedder_id, no atomic rename)
  └── independent; FAISS is the only currently-surviving cross-run artifact

GAP-8  (NoOpL4StateWriter injected by default)
  └── GAP-9, GAP-10 (no L4B/L4C writes reach disk)
        └── GAP-13 (silent pass compounds invisible loss)

GAP-15 (run_pipeline return value discarded)
  └── requires GAP-7 fix first to produce real proposals
```

### Critical Gap Details

**GAP-16 + GAP-1 (CRITICAL — root cause):**
`HealingOutcomeIntakeStore` protocol has exactly one concrete implementation:
`InMemoryHealingOutcomeIntakeStore`. No file-backed implementation exists anywhere.
Every `HealingOutcomeIntakeRecord` produced in production is garbage-collected at scope exit.
Fix: implement `JSONLBackedHealingOutcomeIntakeStore` (see Wave 3).

**GAP-2 (CRITICAL):**
`execute_ssot.py:238` — `timestamp_utc=0` hardcoded on every `HealingOutcomeEvent`.
`execute_ssot.py:252` — `created_utc=0` hardcoded on every `adapter.build_record()` call.
Temporal ordering, TTL eviction, and window-based aggregation are all broken.
Fix: inject `int(time.time())` at intake entry (Wave 0).

**GAP-7 (CRITICAL — most structurally dangerous):**
`meta_learning_pipeline.py:1228–1248` Step 8 constructs a brand-new `HealingOutcomeAggregator`
with hardcoded mock event (`healer_id="test_healer"`, `failure_type="test_failure"`,
`timestamp_utc=9999`). The real records passed via `healing_outcome_intake_adapter` are
**never read**. The optimizer runs on fabricated data.
Fix: Step 8 must call `adapter.store.get_records()` and skip if empty (Wave 3 + Wave 4).

**GAP-8 (HIGH):**
`build_pipeline_deps(repo_root=REPO_ROOT, healing_outcome_intake_adapter=adapter)` is called
with no `l4_state_writer` argument. `l4_state_writer=None` silently no-ops all
`write_l4b_healing_snapshot`, `write_l4c_shadow_drift`, `write_l4c_policy_recommendation`,
`write_l4c_retrieval_profile_proposal` calls. The entire L4 state layer is disabled silently.
Fix: inject `FileBackedL4StateWriter` in factory (Wave 4).

**GAP-13 (HIGH):**
All three L4C write helpers (`_analyze_shadow_drift_and_write`,
`_generate_policy_recommendation_and_write`, `_create_proposal_and_write`) use bare
`except Exception: pass` — completely silent, violating §0.8.
Fix: replace with `logger.warning(...)` (Wave 4).

**GAP-14 (CRITICAL for MetaPriorProvider):**
`DefaultOutcomeWriteBackHook.on_outcome()` updates in-memory `_default_store` singleton.
`export_state()` exists but is **never called** from any production path. After restart,
all EMA priors revert to neutral 0.5. `MetaPriorProvider` has never returned a learned prior.
Fix: Wave 1.

**GAP-12 (MEDIUM):**
`_shadow_telemetry_batch` (module-global list) is cleared only inside
`_analyze_shadow_drift_and_write`, which is guarded by `_8_5_aggregate_snapshot is not None`.
On the GAP-7 cascade path (mock data), `_8_5_aggregate_snapshot` is always None → batch
accumulates across runs without clearing.
Fix: unconditional clear at `run_pipeline` exit (Wave 4).

**GAP-15 (MEDIUM):**
`_ml_run_pipeline(...)` return value (`tuple[ChangePackage, ...]`) is not captured.
Threshold proposals are silently dropped.
Fix: capture and append to `logs/proposals/threshold_proposals.jsonl` (Wave 4).

**GAP-3/GAP-5 (HIGH — FAISS integrity):**
- GAP-3: `built_at_utc=int(_time_faiss.time())` — wall-clock in manifest, breaks replay determinism.
- GAP-5: Three-file write (`*.index`, `*.meta`, `*.manifest`) is not atomic; partial write on
  crash passes `_faiss_disk_dir.exists()` check, then silently fails `load_from_disk` → prior
  vectors silently lost.
Fix: inject `built_at_utc` from `state_mgr`; use temp-dir + `os.replace()` atomic rename (Wave 3).

**GAP-4, GAP-6, GAP-9, GAP-10, GAP-11, GAP-17 (HIGH/MEDIUM/LOW):**
- GAP-4: `embedder_id="hash-fallback"` (source label, not content-addressed checksum).
- GAP-6: `meta_learning` sub-key in `runtime_state.json` has no `schema_version`.
- GAP-9: `HealingOutcomeAggregateSnapshot` never appended to `healing_contexts_corpus.jsonl`.
- GAP-10: `PatternAnalysisReport` result never persisted; engine re-clusters from scratch.
- GAP-11: `wc_determinism_digest` / `embedding_metadata` printed to stdout, never stored.
- GAP-17: `trace_id` and `run_id` in `HealingOutcomeIntakeRecord` always `None`.

---

## § 3 — Scope

### Files Modified

| File | Wave | Change |
|---|---|---|
| `agentic_core/L0_routing/scripts/execute_ssot.py` | 0,1,2,3,4 | `_fire_meta_learning_intake()` + `RuntimeStateManager.__init__()` |
| `system_learning/types/healing_outcome_intake_types.py` | 3 | add `canonical_bytes()` |
| `system_learning/engines/in_memory_healing_outcome_intake_store.py` | 3 | (reference only) |
| `system_learning/pipelines/meta_learning_pipeline.py` | 3,4 | fix Step 8 mock, fix GAP-12/GAP-13/GAP-15 |
| `system_learning/pipelines/pipeline_factory.py` | 4 | inject `FileBackedL4StateWriter` |

### New Files

| File | Wave | Purpose |
|---|---|---|
| `system_learning/engines/jsonl_healing_outcome_intake_store.py` | 3 | `JSONLBackedHealingOutcomeIntakeStore` (GAP-16 fix) |

### Persistence Layout (Post-Implementation)

```
runtime_state.json
  └── meta_learning.schema_version            ← Wave 0 (GAP-6)
  └── meta_learning.success_rate_store        ← Wave 1 (EMA rates + counts per error_sig)
  └── meta_learning.recent_failure_vectors    ← existing (routing novelty)
  └── meta_learning.last_pattern_digest       ← Wave 4 (GAP-10)

data/corpus/healing_contexts_corpus.jsonl     ← Wave 2 (raw events, JSONL append)
data/corpus/healing_intake_records.jsonl      ← Wave 3 (HealingOutcomeIntakeRecord, GAP-16)

data/golden_state/
  ├── faiss_indices/healing_context_v1/       ← existing (atomic rename hardened, Wave 3)
  └── healing_intakes/                        ← Wave 3 (content-addressed intake snapshots)
        ├── _index.json
        └── <sha[:2]>/<sha>.json

logs/l4_state/                                ← Wave 4 (L4B/L4C artifacts via FileBackedL4StateWriter)
logs/proposals/threshold_proposals.jsonl      ← Wave 4 (captured run_pipeline return, GAP-15)
logs/embedding_audit.jsonl                    ← Wave 4 (embedding_metadata per run, GAP-11)
```

---

## § 4 — Wave 0 — Foundation Fixes (Timestamps + Schema Version)

**Fixes:** GAP-2, GAP-6

**In `_fire_meta_learning_intake`**, capture `now_utc` at function entry:
```python
import time as _time_intake
_now_utc_intake = int(_time_intake.time())
```

Replace all `timestamp_utc=0` (line 238) with `timestamp_utc=_now_utc_intake`.
Replace `created_utc=0` (line 252) with `created_utc=_now_utc_intake`.

Add `schema_version` to `state_mgr.update_meta_learning(...)` dict:
```python
state_mgr.update_meta_learning({
    "meta_learning_schema": 1,
    "total_experiences": store.count(),
    "experience": f"intake: {store.count()} healing records persisted",
})
```

**Tests:**
- `timestamp_utc` on ingested events equals injected `now_utc` (not 0)
- `created_utc` on `HealingOutcomeIntakeRecord` equals injected `now_utc`
- `meta_learning.meta_learning_schema == 1` in state after intake
- cold start with no prior meta_learning key does not crash

---

## § 5 — Wave 1 — Persist `HealingSuccessRateStore` EMA State

**Fixes:** GAP-14 (+ cross-run MetaPriorProvider activation)

**Target:** `runtime_state.json → meta_learning.success_rate_store`

**In `_fire_meta_learning_intake`**, after aggregator ingest loop:
```python
from system_learning.engines.healing_success_rate_store import get_default_store
_sr_store = get_default_store()
for action in healing_actions:
    sig = action.get("routing_digest") or f"{action.get('agent','unknown')}:{action.get('type','UNKNOWN')}"
    _sr_store.record_outcome(sig, action.get("outcome", "FAIL") == "SUCCESS")
state_mgr.state["meta_learning"]["success_rate_store"] = _sr_store.export_state()
```

**In `RuntimeStateManager.__init__`**, restore on startup:
```python
_sr_snapshot = _prior_meta.get("success_rate_store")
if _sr_snapshot:
    from system_learning.engines.healing_success_rate_store import get_default_store
    get_default_store().import_state(_sr_snapshot)
```

**Hardening:**
- Validate imported snapshot shape before `import_state()` (schema_version, rates/counts keys).
- On malformed state: fail-closed to neutral empty defaults, log warning, never crash.
- Persisted snapshot must not contain forbidden authority fields.

**Tests:**
- export → import roundtrip: `get_prior(sig)` identical before and after
- cold start (no `success_rate_store` key) → neutral prior 0.50, no crash
- malformed stored state → graceful fallback to neutral, warning emitted
- EMA accumulates correctly across 3-run simulated sequence
- repeated replay of identical sequence → identical priors (determinism)

---

## § 6 — Wave 2 — Persist Raw `HealingOutcomeEvent` Records to JSONL Corpus

**Fixes:** original gap #2 (raw events)

**Target:** `data/corpus/healing_contexts_corpus.jsonl`

**In `_fire_meta_learning_intake`**, append each event after aggregator loop:
```python
_corpus_path = REPO_ROOT / "data" / "corpus" / "healing_contexts_corpus.jsonl"
_new_lines = []
for action in healing_actions:
    _new_lines.append(json.dumps({
        "schema_version": 1,
        "content_hash": action.get("routing_digest", ""),
        "trace_id": action.get("trace_id", ""),
        "namespace": "healing_contexts",
        "created_utc": _now_utc_intake,
        "healer_id": action.get("agent", "unknown"),
        "tier": action.get("routing_tier", "L5"),
        "failure_type": action.get("type", "UNKNOWN"),
        "territory": action.get("territory", "unknown"),
        "outcome": action.get("outcome", "UNKNOWN"),
        "fix_summary": action.get("fix_summary", ""),
    }, separators=(",", ":"), sort_keys=True))
if _new_lines:
    try:
        with open(_corpus_path, "a", encoding="utf-8") as _f:
            _f.write("\n".join(_new_lines) + "\n")
    except Exception as _corpus_err:
        logging.warning("[MetaLearning] corpus write failed (non-fatal): %s", _corpus_err)
```

**Tests:**
- identical normalized action dict → byte-identical JSONL line (determinism)
- each appended line is parseable JSON
- mocked `open()` failure does not propagate out of intake function
- corpus lines parseable by `HistoricalIngestionOrchestrator`
- `created_utc` matches injected `now_utc` (not 0)

---

## § 7 — Wave 3 — Durable `HealingOutcomeIntakeRecord` Persistence

**Fixes:** GAP-16, GAP-1, GAP-7, GAP-5 (FAISS atomic write)

### 7A — `JSONLBackedHealingOutcomeIntakeStore`

New file: `system_learning/engines/jsonl_healing_outcome_intake_store.py`

```python
class JSONLBackedHealingOutcomeIntakeStore(HealingOutcomeIntakeStore):
    def __init__(self, path: Path) -> None: ...
    def write(self, record: HealingOutcomeIntakeRecord) -> None:
        # validate_persistence_payload(record)
        # json.dumps(dataclasses.asdict(record), sort_keys=True, separators=(",",":"))
        # append line; structured warning on failure
    def get_records(self) -> list[HealingOutcomeIntakeRecord]: ...
    def read_records(self, since_utc: int = 0) -> list[HealingOutcomeIntakeRecord]: ...
    def count(self) -> int: ...
    def validate(self) -> None: ...  # checks schema_version on all lines
```

Wire in `_fire_meta_learning_intake`:
```python
_intake_jsonl = REPO_ROOT / "data" / "corpus" / "healing_intake_records.jsonl"
store = JSONLBackedHealingOutcomeIntakeStore(_intake_jsonl)
```

### 7B — `canonical_bytes()` on `HealingOutcomeIntakeRecord`

In `system_learning/types/healing_outcome_intake_types.py`:
```python
def canonical_bytes(self) -> bytes:
    import json, dataclasses
    return json.dumps(dataclasses.asdict(self), separators=(",", ":"), sort_keys=True).encode("utf-8")
```

### 7C — Content-addressed file-backed store (Wave 3 extension)

In `_fire_meta_learning_intake`, additionally write to content-addressed store:
```python
from system_learning.stores.version_store import FileBackedVersionStore
_intake_dir = REPO_ROOT / "data" / "golden_state" / "healing_intakes"
_file_store = FileBackedVersionStore(_intake_dir)
_file_store.commit_change_package(record)  # idempotent; re-runs don't duplicate
```

### 7D — Fix `run_pipeline` Step 8 mock (GAP-7)

In `meta_learning_pipeline.py` Step 8: replace mock aggregator construction with:
```python
_existing_records = (
    deps.healing_outcome_intake_adapter.store.get_records()
    if deps.healing_outcome_intake_adapter is not None
    else []
)
if not _existing_records:
    # No real records — skip optimizer step rather than inject mock data
    _8_5_aggregate_snapshot = None
else:
    intake_record = _existing_records[-1]  # most recent
    _8_5_aggregate_snapshot = deps.healing_config_optimizer.create_snapshot_from_intake(...)
```

### 7E — FAISS atomic write hardening (GAP-5)

Wrap `persist_to_disk` in `execute_ssot.py` with temp-dir + `os.replace()`:
```python
import tempfile, shutil
_tmp_dir = _faiss_base / f"_tmp_{_faiss_idx}"
# write to _tmp_dir, then os.replace(_tmp_dir, _faiss_disk_dir) atomically
```

Also: replace `built_at_utc=int(_time_faiss.time())` with `built_at_utc=_now_utc_intake` (GAP-3).
Replace `embedder_id=_vec_source_str` with a stable versioned constant from
`EmbeddingStorageLayout` or a frozen module-level `_EMBEDDER_ID_BGE = "BAAI/bge-m3-v1"` /
`_EMBEDDER_ID_FALLBACK = "hash-fallback-v1"` (GAP-4).

**Tests (Wave 3):**
- `JSONLBackedHealingOutcomeIntakeStore`: write → read roundtrip, `read_records(since_utc=t)` filters correctly
- `validate()` raises on malformed line
- duplicate commit of identical `canonical_bytes()` yields one logical identity
- `_index.json` valid after write; `healing_intakes/` auto-created
- run_pipeline Step 8 skips optimizer when adapter has no records (no mock data path reachable)
- run_pipeline Step 8 uses real record when adapter has records
- FAISS: partial-write simulation → `os.replace()` restores clean prior state
- FAISS: `built_at_utc` equals injected value (not wall-clock)
- FAISS: `embedder_id` is versioned constant, not runtime source tag

---

## § 8 — Wave 4 — Cross-Run Reload + L4 State + Pipeline Outputs

**Fixes:** GAP-8, GAP-9, GAP-10, GAP-11, GAP-12, GAP-13, GAP-15, GAP-17, original gap #4

### 8A — Cross-run aggregate reload into optimizer

In `_fire_meta_learning_intake`, before building current-run snapshot:
```python
_prior_stats: dict[tuple, tuple[int, int]] = {}
_idx_path = _intake_dir / "_index.json"
if _idx_path.exists():
    _idx = json.loads(_idx_path.read_text())
    for _vid in sorted(_idx.keys())[-50:]:  # bounded, deterministic order
        try:
            _raw = _file_store.get(_vid)
            if _raw:
                _rec = json.loads(_raw.decode())
                for s in _rec.get("snapshot", []):
                    k = (s["healer_id"], s["tier"], s["failure_type"])
                    sc, fc = _prior_stats.get(k, (0, 0))
                    _prior_stats[k] = (sc + s["success_count"], fc + s["failure_count"])
        except Exception as _prior_err:
            logging.warning("[MetaLearning] skipping malformed prior record: %s", _prior_err)

for (hid, tier, ftype), (sc, fc) in sorted(_prior_stats.items()):
    for _ in range(sc):
        aggregator.ingest(HealingOutcomeEvent(healer_id=hid, tier=tier, failure_type=ftype,
                                              success=True, timestamp_utc=_now_utc_intake))
    for _ in range(fc):
        aggregator.ingest(HealingOutcomeEvent(healer_id=hid, tier=tier, failure_type=ftype,
                                              success=False, timestamp_utc=_now_utc_intake))
```

### 8B — Inject `FileBackedL4StateWriter` (GAP-8)

In `pipeline_factory.build_pipeline_deps`:
```python
from system_learning.engines.l4_state_writer import FileBackedL4StateWriter
_l4_dir = repo_root / "logs" / "l4_state"
_l4_dir.mkdir(parents=True, exist_ok=True)
l4_state_writer = FileBackedL4StateWriter(base_dir=_l4_dir)
```

### 8C — Fix silent `pass` in L4C write guards (GAP-13)

In all three helpers in `meta_learning_pipeline.py`:
```python
except Exception as _l4_err:
    logger.warning("[MetaLearning] L4C write failed: %s", _l4_err)
```

### 8D — Persist `PatternAnalysisReport` digest (GAP-10)

After `pattern_report` is produced in `run_pipeline`:
```python
if pattern_report is not None and hasattr(pattern_report, "pattern_digest"):
    state_mgr_ref = deps.state_mgr_ref if hasattr(deps, "state_mgr_ref") else None
    if state_mgr_ref is not None:
        state_mgr_ref.state.setdefault("meta_learning", {})["last_pattern_digest"] = pattern_report.pattern_digest
```
Append full `pattern_report` JSON to `data/corpus/pattern_analysis_history.jsonl`.

### 8E — Capture and persist proposals (GAP-15)

In `_fire_meta_learning_intake`:
```python
_proposals = _ml_run_pipeline(now_utc=_now_utc, ...)
if _proposals:
    _prop_path = REPO_ROOT / "logs" / "proposals" / "threshold_proposals.jsonl"
    _prop_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(_prop_path, "a", encoding="utf-8") as _pf:
            for _p in _proposals:
                _pf.write(json.dumps({"schema_version": 1, "created_utc": _now_utc,
                    "proposal": str(_p)}, sort_keys=True, separators=(",", ":")) + "\n")
    except Exception as _prop_err:
        logging.warning("[MetaLearning] proposal write failed: %s", _prop_err)
logging.info("[MetaLearning] %d threshold proposals generated.", len(_proposals) if _proposals else 0)
```

### 8F — Populate `run_id` / `trace_id` (GAP-17)

Pass `run_id=getattr(state_mgr, "run_id", None)` in `adapter.build_record(...)`.

### 8G — Unconditional `_shadow_telemetry_batch` clear (GAP-12)

At the end of `run_pipeline` (final `finally` block or after all steps):
```python
global _shadow_telemetry_batch
_shadow_telemetry_batch = []
```

**Tests (Wave 4):**
- Prior merge sums `success_count`/`failure_count` correctly per composite key
- 50-record cap enforced (FIFO, oldest dropped)
- Empty prior index → aggregator starts fresh, no crash
- After 20 simulated single-event runs: merged snapshot `total_count >= 20` → optimizer fires
- `FileBackedL4StateWriter` is the injected implementation (not None) in `build_pipeline_deps`
- L4C write failure logs warning (not silent)
- `_shadow_telemetry_batch` is empty at `run_pipeline` exit regardless of aggregate_snapshot presence
- `run_pipeline` return value captured; proposals appended to JSONL
- `pattern_digest` written to `runtime_state.json["meta_learning"]["last_pattern_digest"]`
- `run_id` / `trace_id` on `HealingOutcomeIntakeRecord` match `state_mgr.run_id`

---

## § 9 — Test Requirements (Full Matrix)

### Mandatory across all waves

**Determinism:**
- repeated canonicalization of identical input → identical bytes
- repeated reload/merge over identical persisted history → identical aggregate snapshot
- repeated simulated runs over identical history → identical optimizer inputs
- `embedding_metadata` / W-C-digest reproducible on replay

**Corruption / Recovery:**
- malformed `success_rate_store` in `runtime_state.json`
- malformed `_index.json`
- truncated intake blob
- invalid JSONL corpus line
- partial FAISS write (simulate interrupt mid-write)

**Sovereignty:**
- payload containing any forbidden authority field is rejected by `validate_persistence_payload`
- persistence hook cannot execute outside `POST_COMMIT_TELEMETRY` phase
- persisted artifacts cannot directly mutate routing, safety, or execution state

**Boundary:**
- empty `healing_actions` → no writes attempted, no crash
- missing `routing_digest`, `trace_id`, `territory`, `tier`
- unknown tier / failure type / outcome
- duplicate records committed twice → one logical identity
- oversized summary content → normalized/truncated

**Branch coverage per §1.2:**
- every changed guard (GAP-7 skip path, GAP-13 except path, GAP-5 atomic rename, GAP-12 clear)
  must have success, divergence, negative, and exception tests

---

## § 10 — Acceptance Criteria

- `python -m pytest -q --color=no` exits 0
- `runtime_state.json` contains `meta_learning.success_rate_store` after simulated run
- `runtime_state.json["meta_learning"]["meta_learning_schema"] == 1`
- `data/corpus/healing_contexts_corpus.jsonl` grows by N lines per run (N = len(healing_actions))
- `data/corpus/healing_intake_records.jsonl` contains at least one record per run with `schema_version`
- `data/golden_state/healing_intakes/_index.json` exists and is non-empty after run
- `MetaPriorProvider.get_prior()` returns non-neutral value after importing stored state
- `HealingConfigOptimizer.propose_threshold_adjustments()` fires at least one adjustment given 20+ merged events
- `run_pipeline` Step 8 does not execute mock aggregator path in production
- `logs/proposals/threshold_proposals.jsonl` contains entries after run with healing actions
- All persisted record families include `schema_version`
- All persistence artifacts free of forbidden authority fields
- Replay of identical persisted inputs → identical merged aggregate outputs
- No direct runtime mutation path introduced from persistence into live routing/safety/execution

---

*Integrated from: healer-output-system-learning-persistence-400f4c.md (four-wave implementation plan +
hardening overlay) and healing-output-gap-analysis-ca26ba.md (17-gap AST review).*

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

