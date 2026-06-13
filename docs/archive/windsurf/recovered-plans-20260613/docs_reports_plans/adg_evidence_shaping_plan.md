# ADG Evidence Shaping Plan — C0→PA Bridge
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: evidence shaping handoff from translated `C0EvidenceContract` through `EvidenceBundle` to `PromptEnvelope`

---

## 1. Executive Summary

The existing `evidence_shaper.py` (`shape_evidence()`) is structurally correct for the bridge use case but was designed around **ADG file-sourced** evidence: SQLite rows, JSON report fields, ratchet JSON. The C0 bridge introduces **runtime-retrieved text spans** as the evidence unit. The shaper pipeline (dedupe → normalize → reconcile → contradiction-retain → coverage/gap) applies to C0-sourced items with **three design extensions**:

1. **Freshness handling** must be explicit and timestamp-anchored to the retrieval moment — not to file modification time.
2. **Confidence banding** must propagate `relevance_score` (from `CitedSpan`) into `support_score` per item and drive a band classification on the bundle.
3. **Reconciliation scope** is narrower for C0 spans (no SQLite vs. report count cross-check) but contradiction-retain still applies across spans that reference the same `source_ref` with conflicting `text_snippet` values.

No changes to the shaper's public API (`shape_evidence(items, must_use_sources)`) are required. All extensions are achievable via the adapter's construction of `EvidenceItem` fields before the shaper receives them.

---

## 2. Shaping Pipeline — Full Design

### 2.1 Pre-shaping: Adapter responsibilities

The `c0_to_pa_adapter` (to be built) must fully populate `EvidenceItem` fields **before** calling `shape_evidence()`. The shaper must receive clean items — it does not peek inside `C0EvidenceContract`.

**Required adapter outputs per span:**

| `EvidenceItem` field | Adapter responsibility |
|---------------------|----------------------|
| `source_artifact` | `"c0_retrieval:<retrieval_id>"` or `source_ref` value |
| `source_type` | Classified from `source_ref` pattern; default `"json_report"` if unclassifiable; `"c0_span"` if `SourceType` is extended |
| `snapshot_id` | Extracted from `source_ref` filename or `retrieval_id` |
| `row_references` | `[span.chunk_hash]` |
| `cited_spans` | `[span.span_id]` |
| `support_score` | `span.relevance_score` (1-to-1) |
| `coverage_score` | `contract.coverage_score` (same value for all spans from one contract) |
| `is_derived` | `False` (C0 spans are canonical retrieval) |
| `freshness` | ISO-8601 UTC timestamp at adapter call time |
| `data` | `{"text_snippet": span.text_snippet, "source_ref": span.source_ref, "span_id": span.span_id}` |

**Abstain gate (before shaper):** If `contract.abstain_hint is True`, the adapter must NOT call `shape_evidence()`. Instead it must return a pre-populated `EvidenceBundle` with:
```
coverage_score = contract.coverage_score
weak_support = True
gaps = ["abstain_hint:c0_coverage_below_threshold"]
items = []
```
This preserves the architecture law: `abstain_hint` is a C0 decision, not a shaper heuristic.

---

### 2.2 Step 1: Dedupe

**Existing implementation:** `_dedupe_items()` deduplicates on `(source_artifact, source_type, row_references)`.

**Behaviour for C0 spans:**
- Each `CitedSpan` gets a unique `row_references = [chunk_hash]`
- Two spans from the same retrieval run with the same `chunk_hash` (chunker produced duplicates) → deduplicated correctly
- Two spans from the same document but different chunks → different `chunk_hash` → kept as distinct items
- Two spans from different `source_ref` values → different `source_artifact` → always kept

**No change required.** Dedup key naturally handles span-level granularity.

---

### 2.3 Step 2: Normalize

**Existing implementation:** `_normalize_fields()` applies `_FIELD_ALIASES` to keys inside `EvidenceItem.data`.

**Behaviour for C0 spans:**
The `data` dict from C0 spans uses: `text_snippet`, `source_ref`, `span_id`. None of these are in `_FIELD_ALIASES`. They pass through unchanged — which is correct; these are native C0 fields, not ADG report fields.

**No change required.** Normalization is additive and alias-only; unknown fields pass through.

**Design note:** If in future the C0 layer begins producing structured evidence with ADG-like fields (e.g., `filepath`, `lineno`), the adapter should pre-normalize those before passing to the shaper, so the shaper's alias map fires correctly.

---

### 2.4 Step 3 & 4: Reconcile + Contradiction Retain

**Existing implementation:** `_reconcile_counts()` cross-checks `db_node_count` (from `sqlite` items) against `modules_total` (from `json_report` items). It also checks `reconciliation.nodes_match` / `edges_match` inside provenance report items.

**Behaviour for C0 spans:**
- C0 items have `source_type` in `{"sqlite", "json_report", "c0_span"}` (none will carry `db_node_count` or `modules_total` in their `data`)
- `_reconcile_counts()` will find no matching items → produces zero `ContradictionFlag` objects
- This is correct: there is nothing to reconcile structurally in a pure C0 bundle

**C0-specific contradiction scenario (new, not in existing reconciler):**

When two `CitedSpan` objects reference the **same `source_ref`** but provide conflicting `text_snippet` values — this indicates chunker inconsistency or retrieval ordering instability. The adapter (not the shaper) is responsible for detecting this before calling `shape_evidence()`:

```
For each (source_ref, chunk_hash) pair in cited_spans:
  If same source_ref appears twice with different chunk_hashes:
    → Both spans are kept (contradiction-retain principle)
    → Adapter emits a ContradictionFlag:
        field_name = "text_snippet"
        source_a = "c0_span:<span_id_1>"
        value_a = <chunk_hash_1>
        source_b = "c0_span:<span_id_2>"
        value_b = <chunk_hash_2>
        severity = "minor"
        description = "Same source_ref returned different chunks in one retrieval pass"
    → Flag is pre-populated in EvidenceItem before shaper runs
```

The shaper's contradiction detection (`_reconcile_counts`) is then augmented by pre-existing flags from the adapter. The shaper's `contradictions` list will contain any flags already attached if the adapter passes them through a pre-populated `EvidenceBundle` — **but** the current `shape_evidence()` signature accepts `list[EvidenceItem]`, not a pre-existing bundle.

**Recommended design resolution:** The adapter pre-populates a `ContradictionFlag` list and passes it to a thin wrapper that merges adapter-detected contradictions with shaper-detected contradictions before building the final `EvidenceBundle`. No change to shaper API needed.

---

### 2.5 Step 5: Coverage Score

**Existing implementation:** `_compute_coverage(items, must_use_sources)` counts how many must-use source type strings are present in the item set.

**Behaviour for C0 spans:**

The `must_use_sources` list is defined per packet type in `PacketRegistry`. For example, `executive_summary` requires `["snapshot", "burndown", "closure_report", "ratchet"]`. None of these will be present in a C0-derived `EvidenceBundle` — they are ADG file artifacts, not runtime retrieval spans.

**This is the most significant shaper gap for the C0 bridge.** Two design options:

**Option A (preferred — no shaper change):** The `must_use_sources` parameter passed to `shape_evidence()` for C0-bridged items should be `[]` (empty) or a C0-specific list (e.g., `["c0_span"]`). Coverage is then computed purely from span presence, and the adapter sets `coverage_score` directly from `C0EvidenceContract.coverage_score` (which C0 already computed correctly). The shaper's `_compute_coverage()` returns `1.0` when `must_use_sources=[]`, and the adapter's pre-set `EvidenceBundle.coverage_score` is used as the authoritative value.

**Option B (shaper change):** Extend `shape_evidence()` to accept an `override_coverage_score: float | None = None` parameter and use it when provided. This is a minimal additive change but still a contract change.

**Recommended:** Option A. The adapter pre-sets `EvidenceBundle.coverage_score = contract.coverage_score` before returning. The `must_use_sources` check is only relevant when assembling ADG-file packets, not runtime span bundles.

---

### 2.6 Gap List

**Existing implementation:** `_identify_gaps(items, must_use_sources)` returns `["missing_must_use_source:<src>"]` strings for each absent required source.

**Behaviour for C0 spans with Option A above:** `must_use_sources=[]` → zero gaps from file-source check.

**C0-specific gap signals** the adapter should inject into `gaps` before calling the shaper:

| Gap condition | Gap string |
|--------------|-----------|
| `abstain_hint=True` | `"abstain_hint:c0_coverage_below_threshold"` |
| `coverage_score < 0.30` | `"coverage_below_abstain_threshold:0.30"` |
| `coverage_score < 0.50` and `coverage_score >= 0.30` | `"coverage_below_weak_threshold:0.50"` |
| `cited_spans` is empty | `"no_spans_retrieved"` |
| Any span has `relevance_score < 0.30` | `"low_relevance_span:<span_id>"` |

These strings are injected into the `items` wrapper (by pre-populating a synthetic gap `EvidenceItem` with `source_type="json_report"` and `data={"gaps": [...]}`) **or** by having the bridge wrapper merge adapter gaps with shaper gaps in the final `EvidenceBundle`.

**Recommended:** Adapter accumulates gap strings. After `shape_evidence()` returns a bundle, the bridge merges adapter gaps into `bundle.gaps`. No shaper change.

---

### 2.7 Weak Support Flag

**Existing implementation:** `weak_support = coverage < 0.5` (line 259 in `evidence_shaper.py`).

**Behaviour for C0 spans:**
- `EvidenceBundle.coverage_score` is set from `C0EvidenceContract.coverage_score` by the adapter
- The shaper computes `weak_support = coverage < 0.5`
- If `C0EvidenceContract.coverage_score = 0.45` → `weak_support=True` — correct
- If `C0EvidenceContract.coverage_score = 0.85` → `weak_support=False` — correct

**No change required.** The threshold applies uniformly to both ADG-file and C0-span bundles.

**Additional weak-support signal from span scores:**

If the median `relevance_score` across all `CitedSpan` objects is below 0.5, the adapter should set `weak_support=True` regardless of the aggregate `coverage_score`. This is a C0-specific enrichment that the shaper cannot compute (it does not inspect `support_score` in its `weak_support` calculation).

**Design:** Adapter computes `median_relevance = median([s.relevance_score for s in contract.cited_spans])`. If `median_relevance < 0.50`, override `bundle.weak_support = True` post-shaping.

---

### 2.8 Freshness / Timestamp Handling

**Existing implementation:** `freshness = max(item.freshness for item in deduped if item.freshness)`. Uses lexicographic max of ISO-8601 strings — correct for UTC timestamps.

**Behaviour for C0 spans:**
- All spans from one `C0EvidenceContract` are retrieved at the same time (one retrieval pass)
- The adapter sets `item.freshness = ISO-8601 UTC at adapter call time` for all spans
- The shaper's `max()` call returns that single value — correct

**Recommended adapter rule:** Set `freshness` on all `EvidenceItem` objects to the **same** ISO-8601 timestamp (the adapter's invocation time), not to per-span wall clock. This preserves the semantics that all spans from one contract are co-temporal.

**Stale retrieval detection (future CI implication):** If the `retrieval_id` timestamp in `replay_metadata` diverges from the ADG `snapshot_id` by more than a configurable threshold, the packet should be flagged as potentially stale. This is not a shaper responsibility — it belongs in the E21 audit or a staleness gate.

---

### 2.9 Support Score (per-item confidence)

**Existing implementation:** `EvidenceItem.support_score: float = 1.0` (default). No current adapter sets it to anything other than `1.0` (ADG file adapters do not have a per-row quality signal).

**C0 bridge — key semantic difference:** `CitedSpan.relevance_score` is a per-span retrieval quality signal from the hybrid search engine. It maps directly to `support_score`.

**Design:**
- `support_score = span.relevance_score` (set by adapter — already in mapping matrix)
- The token budgeter's `_severity_key()` stratification function inspects `item.get("severity")` and `item.get("data", {}).get("severity")`. For C0 spans, `data` contains no `severity` field. The budgeter will fall through to `"low"` — meaning C0 spans are treated as equal-priority for trimming unless stratification is adjusted.

**Recommended design:** The adapter places `"relevance_score": span.relevance_score` in `data` in addition to the `support_score` field. The `token_budgeter.py` can be updated (future, minimal change) to recognise `data.get("relevance_score")` as a stratification key for C0 spans. **This is not required for the bridge to function** — it only affects trim order when the budget is exceeded.

---

### 2.10 Confidence Band

**No existing implementation** — `EvidenceBundle` and `EvidenceItem` have no confidence band field. This is a **gap in the current contracts** for the C0 bridge use case.

**Design:**

A confidence band classifies the aggregate evidence quality into a discrete tier:

| Band | Condition | Meaning |
|------|-----------|---------|
| `HIGH` | `coverage_score >= 0.8` AND `weak_support=False` AND no major contradictions | Strong evidence — proceed normally |
| `MEDIUM` | `coverage_score >= 0.5` AND no major contradictions | Adequate evidence — proceed with caution flag |
| `LOW` | `coverage_score >= 0.3` AND (`weak_support=True` OR minor contradictions) | Weak evidence — proceed only if refine path is present |
| `ABSTAIN` | `coverage_score < 0.3` OR `abstain_hint=True` OR major contradictions | Insufficient — emit ABSTAIN packet |

**Where to compute it:** The bridge wrapper (the adapter or a thin post-shaper step) computes the band from `EvidenceBundle` fields after `shape_evidence()` returns. The band is placed in `PromptEnvelope.replay_metadata["confidence_band"]`.

**Why not in `EvidenceBundle`:** Adding a `confidence_band` field to `EvidenceBundle` would be a contract change. Placing it in `replay_metadata` (a free `dict`) requires no contract change and preserves it for audit and replay.

**Token budgeter integration:** The `apply_budget()` function does not consume confidence band. The band is a downstream signal for L2 (and for the E21 audit) — not a token allocation input.

---

## 3. Shaping Pipeline Summary Table

| Step | Existing function | Behaviour with C0 spans | Change required? |
|------|-----------------|------------------------|-----------------|
| Abstain gate | Not in shaper | Adapter checks `abstain_hint` before calling shaper | Adapter only |
| Dedupe | `_dedupe_items()` | Works on `(source_artifact, source_type, chunk_hash)` | None |
| Normalize | `_normalize_fields()` | C0 fields pass through unchanged | None |
| Reconcile | `_reconcile_counts()` | No SQLite/report count fields in C0 items → zero flags | None |
| Contradiction retain | `_reconcile_counts()` | Same-source-ref multi-span contradiction detected by adapter, not shaper | Adapter pre-populates flags; bridge merges |
| Coverage score | `_compute_coverage()` | `must_use_sources=[]` for C0 path; adapter pre-sets `coverage_score` | None (adapter controls input) |
| Gap list | `_identify_gaps()` | Adapter injects C0-specific gap strings post-shaping | Bridge merger step |
| Weak support | `bundle.weak_support` | `coverage < 0.5` threshold applies; adapter overrides if `median_relevance < 0.5` | Adapter post-shaping override |
| Freshness | `max(item.freshness)` | All spans share same timestamp; max is correct | None |
| Support score | `item.support_score` | Set to `span.relevance_score` by adapter | None (adapter sets it) |
| Confidence band | Not implemented | Bridge wrapper derives band from bundle fields; places in `replay_metadata` | Bridge wrapper only |

---

## 4. Evidence Shaping Handoff — Sequence

```
C0EvidenceContract (validated, HMAC sealed)
    │
    ▼
[Adapter: c0_to_pa_adapter.py]
    ├── Check abstain_hint → if True, return pre-populated empty EvidenceBundle
    ├── For each CitedSpan → construct EvidenceItem (support_score, freshness, data)
    ├── Detect same-source-ref contradictions → pre-populate ContradictionFlag list
    ├── Accumulate gap strings from coverage_score / relevance thresholds
    │
    ▼
EvidenceItem list  (ready for shaper)
    │
    ▼
[shape_evidence(items, must_use_sources=[])]
    ├── Step 1: Dedupe on (source_artifact, source_type, chunk_hash)
    ├── Step 2: Normalize field aliases in data dicts
    ├── Step 3-4: Reconcile counts → no ADG items → zero new ContradictionFlags
    ├── Step 5: Coverage = 1.0 (no must_use_sources to check)
    ├── Freshness = max of identical timestamps
    └── weak_support = (adapter-set coverage_score < 0.5)
    │
    ▼
EvidenceBundle (raw from shaper)
    │
    ▼
[Bridge merger step — in adapter after shape_evidence()]
    ├── Set bundle.coverage_score = contract.coverage_score (override shaper's 1.0)
    ├── Merge adapter ContradictionFlags into bundle.contradictions
    ├── Merge adapter gap strings into bundle.gaps
    ├── If median_relevance < 0.5 → override bundle.weak_support = True
    ├── Compute confidence_band from (coverage_score, weak_support, contradiction_status)
    │
    ▼
EvidenceBundle (shaped, C0-enriched)
    │
    ▼
[build_packet(packet_type, bundle, task_block, replay_metadata)]
    ├── Load PacketTemplate from registry
    ├── Split items into must_use_evidence / optional_evidence
    ├── apply_budget(must_use, optional, fixed_tokens, budget)
    ├── Populate PromptEnvelope (10 blocks)
    ├── Set replay_metadata = {retrieval_id, request_id, evidence_hmac, coverage_score,
    │                         abstain_hint, snapshot_id, assembly_timestamp, confidence_band}
    └── Set assembly_status = PromptAssemblyStatus(...)
    │
    ▼
PromptEnvelope (sealed, ready for L2 dispatch)
```

---

## 5. Ownership Boundary Enforcement at Each Step

| Step | Owner | What is forbidden |
|------|-------|------------------|
| Abstain check | Adapter (C0 boundary) | PA must not override `abstain_hint` |
| `EvidenceItem` construction | Adapter | Must not query ADG SQLite or JSON files |
| `shape_evidence()` call | Adapter invokes shaper | Shaper must not read `C0EvidenceContract` directly |
| Coverage override | Bridge merger (adapter-side) | Must not inflate `coverage_score` above `contract.coverage_score` |
| Contradiction merge | Bridge merger | Must not drop any `ContradictionFlag` from adapter or shaper |
| `build_packet()` call | Bridge dispatcher (L3 orchestration) | Must not call with `abstain_hint=True` contract |
| `replay_metadata` population | `build_packet()` / bridge | Must include `evidence_hmac` unchanged; must not recompute it |
| `PromptEnvelope` write to disk | L3 dispatcher (not PA) | PA returns envelope; L3 decides whether to persist it |

---

## 6. Minimum Future Implementation Change Set (shaping-specific)

| Item | Location | Type | Priority |
|------|----------|------|---------|
| `c0_to_pa_adapter.py` | `agentic_core/L3_orchestration/adapters/` | New module | **Required** |
| `SourceType` extension with `"c0_span"` | `tools/adg/prompt_assembly/contracts.py` | Additive Literal change | Optional (defer) |
| Bridge merger step (post-shaper, pre-builder) | Within `c0_to_pa_adapter.py` | Part of adapter | **Required** |
| `"relevance_score"` stratification in `token_budgeter.py` | `tools/adg/prompt_assembly/budgeting/token_budgeter.py` | Minor additive change | Optional (defer) |
| Confidence band derivation | Within `c0_to_pa_adapter.py` (bridge merger step) | No contract change | **Required** |
| E21 gate upgrade (violation_count → CI hard-block) | `ops_scripts/ci/adg_gates/gate_p0_authority.py` | Gate logic addition | Future (CI phase) |
| `evidence_hmac` presence gate | New gate in `ops_scripts/ci/adg_gates/` | New gate module | Future (CI phase) |

**Zero changes to existing files:** `evidence_shaper.py`, `contracts.py` (unless `SourceType` extended), `packets/registry.py`, `packets/builders.py`, `budgeting/token_budgeter.py`, `retrieval/adapters.py`.

---

## 7. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|---------|-----------|
| `shape_evidence()` `coverage_score` of `1.0` (from `must_use_sources=[]`) overwrites bridge merger's correct value | HIGH | Bridge merger must set `bundle.coverage_score` **after** `shape_evidence()` returns, not before |
| Adapter merges `ContradictionFlag` from shaper + adapter without dedup → duplicate flags | MEDIUM | Bridge merger deduplicates flags on `(field_name, source_a, source_b)` before assigning |
| `abstain_hint` check happens inside `build_packet()` rather than at adapter boundary | HIGH | The adapter must be the exclusive abstain gate; `build_packet()` should also check `bundle.weak_support and bundle.gaps` but must not be the first gate |
| Span `relevance_score = 0.0` → `support_score = 0.0` → budgeter treats item as lowest priority → gets trimmed first | LOW — correct behaviour | Document that zero-relevance spans will be trimmed before higher-relevance spans; no mitigation needed |
| C0 spans with `text_snippet` that are very long inflate token budget silently | MEDIUM | Adapter should truncate `text_snippet` to a maximum length (e.g., 512 chars) before placing in `data`; log truncation as a gap string |
| Two-phase C0 retrieval (multiple contracts per request) → multiple bundles merged before PA | MEDIUM — not in current C0 contract design | Out of scope for this bridge; a future `C0EvidenceBatch` contract would handle this |

---

## 8. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `shape_evidence()` public API (`items, must_use_sources`) will not change | **Assumed stable** — no changes planned |
| `token_budgeter.apply_budget()` will receive `EvidenceItem.to_dict()` serialized items, not raw `EvidenceItem` objects | **Confirmed** — `builders.py` serializes via `to_dict()` before calling budgeter |
| Median relevance score threshold of `0.50` for `weak_support` override | **Design choice** — aligns with shaper's existing `coverage < 0.5` threshold |
| `"c0_span"` `SourceType` value is deferred — bridge uses `"json_report"` with `source_artifact="c0_retrieval"` | **Recommended default** — no type change required for initial implementation |
| Confidence band thresholds (`0.8 / 0.5 / 0.3`) align with existing `_SHARED_REFINE` text (`coverage_score < 0.3`) and `_ABSTAIN_COVERAGE_THRESHOLD = 0.30` | **Confirmed alignment** — thresholds derived from existing constants |
| L3 orchestration dispatcher exists and owns the call sequence (C0 → adapter → PA → L2) | **Architectural assumption** — the dispatcher module is not in scope for this design |
| Two distinct `C0EvidenceContract` instances in one request (e.g., multi-turn retrieval) are not a current concern | **Out of scope** — single contract per request assumed |
