---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\adg_prompt_assembly_integration_plan.md'
original_relative_path: 'adg_prompt_assembly_integration_plan.md'
source_sha256: 2fe3316a8f1810bcb03418455f2487ada6df58b1aa4ce44bbcb640c24d1ad84a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Prompt Assembly Integration Plan — Stage 1 Final Design
**Date:** 2026-04-11 | Status: DESIGN COMPLETE — Awaiting Stage 2 implementation approval

---

## 1. Executive Summary

This document is the final Stage 1 design package for the C0→PA bridge. All prior findings across 5 prompts are reconciled here into one coherent, consistent design. The bridge translates `C0EvidenceContract` (L3 runtime retrieval) into a bounded `PromptEnvelope` (tool-layer prompt assembly) without modifying any existing PA file except one minimal additive change to `_assemble()` that resolves the critical coverage-semantics risk.

**Firm decisions:**
1. **One new module required:** `agentic_core/L3_orchestration/adapters/c0_to_pa_adapter.py`
2. **One minimal additive change required:** `tools/adg/prompt_assembly/packets/builders.py` — add `pre_shaped_bundle` optional parameter to `_assemble()`
3. **Zero required changes** to `contracts.py`, `registry.py`, `evidence_shaper.py`, `token_budgeter.py`, `cli.py`, or `c0_evidence_contract_types.py`
4. **Default packet:** `executive_summary`; conditional: `graph_path_explanation`; no new families
5. **Architecture law preserved:** C0 retrieves only → adapter translates only → PA packages only

**Critical risk resolution:** Option B-modified (see §3.4) — add a single optional `pre_shaped_bundle` parameter to `_assemble()`. This is the smallest clean change that resolves the coverage-semantics risk without duplication, without contract churn, and without source-type aliasing hacks.

---

## 2. Current-State Analysis

### 2.1 What exists and is ready

| Component | Location | Status |
|-----------|----------|--------|
| `C0EvidenceContract` + `CitedSpan` | `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` | Complete, validated, HMAC-sealed |
| `EvidenceItem`, `EvidenceBundle`, `PromptEnvelope`, `PromptAssemblyStatus` | `tools/adg/prompt_assembly/contracts.py` | Complete, all fields sufficient |
| `shape_evidence()` shaping pipeline | `tools/adg/prompt_assembly/shaping/evidence_shaper.py` | Complete; all 6 steps apply to C0 items |
| `apply_budget()` token budgeter | `tools/adg/prompt_assembly/budgeting/token_budgeter.py` | Complete; handles C0 spans correctly |
| 8 `PacketTemplate` registrations | `tools/adg/prompt_assembly/packets/registry.py` | Complete; no template changes needed |
| 8 builder functions + `_assemble()` + `build_packet()` | `tools/adg/prompt_assembly/packets/builders.py` | Complete; one optional parameter addition needed |
| `artifacts/adg/packets/` directory | Confirmed present, empty | Ready for materialization |

### 2.2 What is missing

| Component | Status |
|-----------|--------|
| `c0_to_pa_adapter.py` | **Not yet written** — only required new module |
| `_assemble()` `pre_shaped_bundle` parameter | **Not yet added** — only required existing-file change |
| L3 orchestration dispatcher integration | **Out of scope for Stage 2** — adapter is the boundary |

### 2.3 Confirmed gaps in current design (low-severity, not blocking)

| Gap | Location | Notes |
|-----|----------|-------|
| `infrastructure_boundary` builder uses `source_type="sqlite"` but template expects `"infra_view"` | `builders.py` + `registry.py` | Pre-existing; not introduced by bridge; separate fix |
| `_SHARED_REFINE` mentions ADG regeneration — irrelevant for C0 bundles | `registry.py` | Not harmful; dispatcher can supplement via `task_block` |
| `"c0_span"` not in `SourceType` Literal | `contracts.py` | Deferred; `"json_report"` proxy works for initial bridge |

---

## 3. Critical Risk Resolution — `_assemble()` Coverage Semantics

### 3.1 The Problem (confirmed)

`_assemble()` in `builders.py` line 57:
```python
bundle = shape_evidence(all_items, must_use_sources=template.must_use_sources)
```

`template.must_use_sources` for `executive_summary` = `["snapshot", "burndown", "closure_report", "ratchet"]`.

C0 `EvidenceItem` objects have `source_type="json_report"` (or any C0-compatible type). None match the executive_summary must-use list. Result: `_compute_coverage()` returns `0.0` → `bundle.coverage_score = 0.0` → `_assemble()` computes `evidence_contract_status = "empty"` → `assembly_result = "fail"`. This is **incorrect** when `C0EvidenceContract.coverage_score >= 0.30`.

### 3.2 Three Options Evaluated

**Option A: Adapter-side `source_type` aliasing**

The adapter sets `source_type` values to match the packet's `must_use_sources` strings (e.g., `source_type="json_report"` for one item to satisfy `"closure_report"` or similar by proximity).

- **Problem:** This is a semantic lie. `source_type` is a typed Literal. Setting `"json_report"` when the source is a C0 retrieval span misleads the shaper's coverage computation. The coverage score produced would be `1/4` or `2/4` — not the C0's actual `coverage_score`. It also means different C0 items get different `source_type` values purely to satisfy the coverage check, which creates items with inconsistent semantics in the bundle.
- **Verdict: REJECTED** — semantic aliasing produces incorrect coverage values and creates misleading item metadata.

**Option B: Bridge calls `shape_evidence()` directly, builds `PromptEnvelope` manually**

The adapter calls `shape_evidence(items, must_use_sources=[])` directly, gets a bundle, merges it, then builds `PromptEnvelope` with the same field structure as `_assemble()`.

- **Problem:** This duplicates `_assemble()`'s assembly logic (token estimation, budget application, status construction, abstain augmentation, refine augmentation, `replay` dict construction, `PromptAssemblyStatus` population). That is ~85 lines of logic that must be kept in sync with `_assemble()` manually. Any change to `_assemble()` creates a silent divergence.
- **Verdict: REJECTED** — creates a maintenance shadow implementation that diverges silently.

**Option C (RECOMMENDED): Add `pre_shaped_bundle` optional parameter to `_assemble()`**

Add one optional parameter:
```python
def _assemble(
    template: PacketTemplate,
    must_items: list[EvidenceItem],
    opt_items: list[EvidenceItem],
    task_block: str,
    replay_extras: dict[str, Any] | None = None,
    pre_shaped_bundle: EvidenceBundle | None = None,   # ← NEW optional parameter
) -> PromptEnvelope:
```

When `pre_shaped_bundle` is not `None`, skip the `shape_evidence()` call and use the supplied bundle directly:
```python
if pre_shaped_bundle is not None:
    bundle = pre_shaped_bundle
else:
    bundle = shape_evidence(all_items, must_use_sources=template.must_use_sources)
```

This is the **only change to an existing file**. All 8 builder functions are unaffected (they never pass `pre_shaped_bundle`). `build_packet()` is unaffected. The C0 adapter calls `shape_evidence(items, must_use_sources=[])` directly, applies the bridge merger (coverage override, gap merge, confidence_band), and passes the merged bundle to `_assemble()` as `pre_shaped_bundle`. `_assemble()` then runs budgeting, status construction, and envelope assembly on the correct, C0-semantically-correct bundle.

**Why this is correct:**
- Zero duplication: all assembly logic stays in `_assemble()`
- Zero semantic aliasing: `source_type` values remain honest C0 labels
- Zero contract churn: `EvidenceBundle` contract unchanged; `_assemble()` signature is additive
- Backward compatible: all 8 existing builders pass `pre_shaped_bundle=None` implicitly
- Clean separation: adapter owns shaping + merging; `_assemble()` owns budgeting + assembling
- Smallest possible change: 2 lines added to `_assemble()` in `builders.py`

**Verdict: RECOMMENDED.**

### 3.3 The `must_use_sources=[]` Call for C0 Shaping

When the adapter calls `shape_evidence(items, must_use_sources=[])`:
- `_dedupe_items()` — works on `(source_artifact, source_type, chunk_hash)` — correct
- `_normalize_fields()` — C0 fields pass through unchanged — correct
- `_reconcile_counts()` — no ADG count fields in C0 items — zero new flags — correct
- `_compute_coverage()` — `must_use_sources=[]` → returns `1.0` — **this value is overridden by bridge merger**
- `_identify_gaps()` — `must_use_sources=[]` → zero file-source gaps — bridge merger injects C0-specific gaps
- `bundle.weak_support` = `(1.0 < 0.5)` = `False` — **bridge merger overrides if needed**

**Bridge merger responsibilities (after `shape_evidence()` returns, before `_assemble()` call):**
1. `bundle.coverage_score = contract.coverage_score` (override shaper's 1.0)
2. `bundle.weak_support = True` if `contract.coverage_score < 0.5` or `median(relevance_scores) < 0.5`
3. Merge adapter-detected `ContradictionFlag` objects into `bundle.contradictions`
4. Update `bundle.contradiction_status` from merged flags
5. Inject C0-specific gap strings into `bundle.gaps`
6. Compute `confidence_band` from bundle state

---

## 4. Final Runtime Integration Flow

```
─────────────────────────────────────────────────────────────────────────
STEP 1: L3 Orchestration Dispatcher
─────────────────────────────────────────────────────────────────────────
  Input:  (request_context: str, packet_type: str | None)
  Action: Invoke C0 retrieval engine
  Output: C0EvidenceContract (validated, HMAC-sealed)

─────────────────────────────────────────────────────────────────────────
STEP 2: Adapter Gate (c0_to_pa_adapter.py)
─────────────────────────────────────────────────────────────────────────
  Input:  C0EvidenceContract
  Action:
    [A] Validate required fields (retrieval_id, request_id, evidence_hmac, coverage_score, cited_spans)
        → If any missing: raise ContractValidationError, do not proceed
    [B] abstain_hint gate:
        → If abstain_hint=True or coverage_score < 0.30 or all spans < 0.10 relevance
        → Return (None, abstain_bundle, replay_extras) immediately
    [C] Prune spans: discard relevance_score < 0.30; cap at packet-type max
    [D] Sort spans: relevance_score DESC; apply source diversity cap (max 3 per source_ref)
    [E] Translate: CitedSpan → EvidenceItem (support_score, freshness, data, cited_spans, row_references)
    [F] Detect same-source-ref contradictions → pre-populate ContradictionFlag list
    [G] Truncate text_snippet to 512 chars (word-boundary)
  Output: list[EvidenceItem], ContradictionFlag[], gap_strings[]

─────────────────────────────────────────────────────────────────────────
STEP 3: shape_evidence() — Direct call from adapter
─────────────────────────────────────────────────────────────────────────
  Input:  items=list[EvidenceItem], must_use_sources=[]
  Action: Dedupe, normalize, reconcile (no ADG fields → zero new flags), coverage=1.0, freshness=max
  Output: EvidenceBundle (raw — coverage_score=1.0, weak_support=False, no C0 gaps yet)

─────────────────────────────────────────────────────────────────────────
STEP 4: Bridge Merger (inside adapter)
─────────────────────────────────────────────────────────────────────────
  Input:  EvidenceBundle (raw), ContradictionFlag[], gap_strings[], C0EvidenceContract
  Action:
    [A] bundle.coverage_score = contract.coverage_score  (override shaper's 1.0)
    [B] bundle.weak_support = True if coverage < 0.5 or median(relevance) < 0.5
    [C] bundle.contradictions = dedup(shaper_flags + adapter_flags)
    [D] bundle.contradiction_status = max_severity(bundle.contradictions)
    [E] bundle.gaps = shaper_gaps + adapter_c0_gaps
    [F] confidence_band = derive(coverage, weak_support, contradiction_status)
  Output: EvidenceBundle (C0-enriched), replay_extras dict

─────────────────────────────────────────────────────────────────────────
STEP 5: Packet Selection (L3 Dispatcher)
─────────────────────────────────────────────────────────────────────────
  Input:  request_context, confidence_band, from_node, to_node
  Rules:
    abstain_hint=True or confidence_band="ABSTAIN" → NO PACKET → stop
    from_node + to_node explicit + coverage >= 0.50  → graph_path_explanation
    all other cases                                   → executive_summary (default)
  Output: packet_type str

─────────────────────────────────────────────────────────────────────────
STEP 6: _assemble() — PA integration point
─────────────────────────────────────────────────────────────────────────
  Input:
    template = get_template(packet_type)
    must_items = bundle.items                  (C0 EvidenceItem list)
    opt_items = []
    task_block = <request-specific description, ≤ 200 tokens>
    replay_extras = {
        retrieval_id, request_id, evidence_hmac,
        coverage_score, abstain_hint, confidence_band,
        snapshot_id (if available),
        [from_node, to_node] for graph_path_explanation
    }
    pre_shaped_bundle = bundle                 (C0-enriched bundle — skips internal shaping)
  Action: budget → status → envelope assembly
  Output: PromptEnvelope (sealed)

─────────────────────────────────────────────────────────────────────────
STEP 7: Pre-emission Quality Gate (L3 Dispatcher)
─────────────────────────────────────────────────────────────────────────
  Check: assembly_result == "fail"       → do not emit, do not write to disk
  Check: evidence_hmac missing           → do not emit, log bridge error
  Check: empty must_use_evidence + pass  → downgrade to fail, log anomaly
  Pass:  assembly_result in (pass,partial) → proceed to emit

─────────────────────────────────────────────────────────────────────────
STEP 8: Emit to L2 + Optional Artifact Materialization
─────────────────────────────────────────────────────────────────────────
  Action: Return PromptEnvelope to L2 dispatcher
  Optional: envelope.to_json(indent=2) →
            artifacts/adg/packets/<packet_type>_<packet_id>.json
            (only when assembly_result in ("pass", "partial"))
```

### 4.1 L2 Receive Contract

L2 receives `PromptEnvelope` by value. L2 must:
- Verify `assembly_status.assembly_result != "fail"` before consuming evidence
- Consume blocks in canonical order (1–10)
- Read `replay_metadata["abstain_hint"]` — if `True`, abstain from acting
- Read `replay_metadata["confidence_band"]` — route confidence-dependent logic accordingly
- Read `replay_metadata["evidence_hmac"]` — use for audit trail
- Never mutate `replay_metadata`
- Never trigger write operations except via UWG

---

## 5. File-by-File Stage 2 Implementation Plan

### 5.1 Required Changes

#### File 1: `tools/adg/prompt_assembly/packets/builders.py`
- **Change type:** Additive — one optional parameter to `_assemble()`
- **Why:** Resolves critical coverage-semantics risk. Without this, C0 bundles with valid coverage are incorrectly failed by `shape_evidence(must_use_sources=template.must_use_sources)`.
- **Required:** YES
- **Scope:** 2 lines added to `_assemble()` signature and body. No other function touched.
- **Change:**
  ```python
  # Signature: add optional parameter (after replay_extras)
  pre_shaped_bundle: EvidenceBundle | None = None,

  # Body: replace unconditional shape_evidence() call
  if pre_shaped_bundle is not None:
      bundle = pre_shaped_bundle
  else:
      bundle = shape_evidence(all_items, must_use_sources=template.must_use_sources)
  ```
- **Test coverage:** Unit test `test__assemble_with_pre_shaped_bundle()` verifying that when `pre_shaped_bundle` is supplied, `shape_evidence()` is not called and the bundle's fields are used directly.
- **Backward compatibility:** All 8 existing builder functions call `_assemble()` without `pre_shaped_bundle` — they continue to use the existing `shape_evidence()` path unchanged. Zero regression risk.

#### File 2: `agentic_core/L3_orchestration/adapters/c0_to_pa_adapter.py` (NEW)
- **Change type:** New module
- **Why:** The bridge translation layer. Implements the adapter gate, span translation, bridge merger, and relay_extras construction.
- **Required:** YES
- **Scope:** ~150–200 lines. One module, no cross-layer imports except `c0_evidence_contract_types` (L3) and `contracts.py` / `evidence_shaper.py` (tool layer).
- **Public API:**
  ```python
  def translate_contract(
      contract: C0EvidenceContract,
      packet_type: str,
  ) -> tuple[EvidenceBundle | None, dict[str, Any]]:
      """
      Returns (bundle, replay_extras).
      bundle is None when abstain gate fires.
      replay_extras always contains retrieval_id, request_id, evidence_hmac,
      coverage_score, abstain_hint, confidence_band.
      """
  ```
- **Internal functions:**
  - `_validate_contract(contract)` → raises `ContractValidationError` if required fields missing
  - `_prune_and_sort_spans(spans, packet_type)` → applies relevance cap + source diversity cap + span count cap
  - `_translate_span(span, retrieval_id, timestamp)` → CitedSpan → EvidenceItem
  - `_detect_contradictions(items)` → list[ContradictionFlag]
  - `_bridge_merge(raw_bundle, adapter_flags, adapter_gaps, contract)` → EvidenceBundle (enriched)
  - `_compute_confidence_band(coverage, weak_support, contradiction_status)` → str
- **Test coverage:** See §6.1

### 5.2 Optional / Deferred Changes

#### File 3: `tools/adg/prompt_assembly/contracts.py`
- **Change type:** Additive — extend `SourceType` Literal with `"c0_span"`
- **Required:** NO — deferred
- **When:** After first bridge implementation iteration if source differentiation is proven necessary
- **Impact:** Zero — additive type extension, all existing code continues to work

#### File 4: `tools/adg/prompt_assembly/retrieval/adapters.py`
- **Change type:** Bug fix — `fetch_infra_wiring_views()` should set `source_type="infra_view"`
- **Required:** NO — pre-existing defect, separate PR
- **Impact:** Fixes spurious partial coverage on `infrastructure_boundary` packets

#### File 5: `tools/adg/prompt_assembly/budgeting/token_budgeter.py`
- **Change type:** Additive — `_severity_key()` to recognise `data["relevance_score"]` for C0 items
- **Required:** NO — deferred
- **When:** If trim order for C0 spans proves incorrect in practice (adapter pre-sort is the primary guarantee)

---

## 6. Test Strategy

### 6.1 Unit Tests for `c0_to_pa_adapter.py`

| Test | Scenario | Expected |
|------|----------|----------|
| `test_translate_abstain_hint_true` | `C0EvidenceContract(abstain_hint=True)` | Returns `(None, replay_extras)` immediately; no items translated |
| `test_translate_coverage_below_threshold` | `coverage_score=0.20` | Returns `(None, replay_extras)`; abstain gate fires |
| `test_translate_empty_spans` | `cited_spans=()` | Returns `(None, replay_extras)` |
| `test_translate_all_spans_below_minimum` | All `relevance_score < 0.10` | Returns `(None, replay_extras)` |
| `test_translate_valid_contract` | Valid contract, 5 spans | Returns `(EvidenceBundle, replay_extras)` with correct field mapping |
| `test_span_to_evidence_item_fields` | Single span | `support_score == relevance_score`, `cited_spans == [span_id]`, `row_references == [chunk_hash]` |
| `test_snippet_truncation` | `text_snippet` length > 512 | Truncated at word boundary; gap injected; `"..."` appended |
| `test_span_pruning_by_relevance` | 5 spans, 2 below 0.30 | 2 pruned; gap strings emitted |
| `test_source_diversity_cap` | 5 spans from same `source_ref` | Max 3 retained |
| `test_bridge_merger_coverage_override` | Raw bundle has `coverage_score=1.0` | Merger sets to `contract.coverage_score` |
| `test_bridge_merger_weak_support` | `coverage_score=0.40` | `weak_support=True` |
| `test_bridge_merger_contradiction_merge` | Adapter flags + shaper flags | Merged deduplicated list; severity aggregation correct |
| `test_confidence_band_high` | `coverage=0.90`, no weak_support | `"HIGH"` |
| `test_confidence_band_low` | `coverage=0.35`, weak_support=True | `"LOW"` |
| `test_confidence_band_abstain` | `coverage=0.25` | `"ABSTAIN"` |
| `test_replay_extras_keys` | Valid contract | All 6 C0 extras present; no collision with standard replay keys |
| `test_hmac_preserved` | Valid contract | `replay_extras["evidence_hmac"] == contract.evidence_hmac` |
| `test_retrieval_id_preserved` | Valid contract | `replay_extras["retrieval_id"] == contract.retrieval_id` |

### 6.2 Unit Tests for `builders.py` `_assemble()` change

| Test | Scenario | Expected |
|------|----------|----------|
| `test__assemble_without_pre_shaped` | Call without `pre_shaped_bundle` | `shape_evidence()` called; existing behavior unchanged |
| `test__assemble_with_pre_shaped` | Call with `pre_shaped_bundle` | `shape_evidence()` NOT called; pre-shaped bundle used directly |
| `test__assemble_pre_shaped_coverage_propagates` | Pre-shaped bundle with `coverage_score=0.65` | `evidence_contract_status="partial"` (not `"empty"`) |
| `test__assemble_pre_shaped_fail_on_empty` | Pre-shaped bundle with `coverage_score=0.0`, `items=[]` | `assembly_result="fail"` |
| `test_existing_builders_unaffected` | All 8 builder functions | Each produces identical output to pre-change baseline |

### 6.3 Integration Tests

| Test | Scope | Expected |
|------|-------|----------|
| `test_c0_bridge_executive_summary_pass` | Valid C0 contract (coverage=0.85) → adapter → `_assemble(executive_summary)` | `assembly_result="pass"`, `evidence_hmac` in `replay_metadata` |
| `test_c0_bridge_executive_summary_partial` | Valid C0 contract (coverage=0.50) → adapter → `_assemble()` | `assembly_result="partial"`, `weak_support=True` in status |
| `test_c0_bridge_abstain_no_packet` | C0 contract with `abstain_hint=True` | No `PromptEnvelope` returned; abstain signal propagated |
| `test_c0_bridge_graph_path` | C0 contract + from_node/to_node → `graph_path_explanation` | `replay_metadata` contains `from_node`, `to_node` |
| `test_c0_bridge_token_budget_trim` | C0 contract with 20 spans, max-length snippets → `executive_summary` | `overflow_action="narrow"`, ≤15 spans in final `must_use_evidence` |
| `test_c0_bridge_disk_write_on_pass` | `assembly_result="pass"` | File written to `artifacts/adg/packets/` |
| `test_c0_bridge_no_disk_write_on_fail` | `assembly_result="fail"` | No file written |

### 6.4 Regression Tests

| Test | Purpose |
|------|---------|
| Run all 8 existing builder functions with their current parameters | Confirm zero output change from `_assemble()` parameter addition |
| `test_executive_summary_adg_file_path` | `build_executive_summary()` still produces correct output when called normally |
| `test_shape_evidence_must_use_sources_unchanged` | `shape_evidence()` with `must_use_sources=template.must_use_sources` still computes correct coverage for ADG-file items |

### 6.5 CI Gate Implications

| Gate | Action |
|------|--------|
| Existing `check_query_progress_bar.py` | If adapter has loops >10 items, `ProgressReporter` must be used |
| `check_no_archives_imports.py` | Adapter must import only from `agentic_core/` and `tools/adg/` |
| Layer boundary gate (E6) | Adapter is in `L3_orchestration/adapters/` — importing from `tools/adg/` is permitted only if L3→tool layer is an allowed cross-layer dependency. **Verify against E6 gate before committing.** |
| `check_terminal_cleanup.py` | Adapter must not leave open subprocess calls |
| `run_contract_gates.py` | Run full contract gate suite after committing |
| Future: `evidence_hmac_presence_gate` | New gate on `artifacts/adg/packets/` directory — Stage 3 |

---

## 7. Acceptance Criteria

All must pass before Stage 2 is considered complete.

### 7.1 Contract Preservation

- [ ] All 8 existing builder functions produce byte-identical output to pre-change baseline (no `_assemble()` regression)
- [ ] `EvidenceItem`, `EvidenceBundle`, `PromptEnvelope`, `PromptAssemblyStatus` contracts unchanged
- [ ] `shape_evidence()` public API unchanged — adapter calls it with `must_use_sources=[]`, which is a valid invocation
- [ ] `C0EvidenceContract` and `CitedSpan` contracts unchanged

### 7.2 Abstain Correctness

- [ ] `abstain_hint=True` in `C0EvidenceContract` → no `PromptEnvelope` emitted → no disk write → abstain signal returned to caller
- [ ] `coverage_score < 0.30` → same behavior as `abstain_hint=True`
- [ ] `abstain_hint=True` in `replay_metadata` of any emitted partial packet is preserved verbatim
- [ ] Adapter abstain gate fires **before** `shape_evidence()` or `_assemble()` are called

### 7.3 Runtime Packet Selection Correctness

- [ ] Default packet type is `executive_summary` when no explicit path context exists
- [ ] `graph_path_explanation` only selected when `from_node`, `to_node` non-empty AND `coverage >= 0.50`
- [ ] No ADG-file-first packet type is selected for C0-only evidence in standard operation
- [ ] `confidence_band` is correctly computed and placed in `replay_metadata`

### 7.4 Token Boundedness

- [ ] `text_snippet` in all `EvidenceItem.data` values ≤ 512 chars after adapter processing
- [ ] `executive_summary` packets contain ≤ 15 spans in `must_use_evidence`
- [ ] `graph_path_explanation` packets contain ≤ 20 spans in `must_use_evidence`
- [ ] `task_block` token count ≤ 200 (dispatcher enforced — documented contract)
- [ ] All emitted packets have `token_budget_status in ("within_budget", "trimmed", "split")`

### 7.5 Replay Metadata Preservation

- [ ] `evidence_hmac` from `C0EvidenceContract` appears unchanged in `PromptEnvelope.replay_metadata`
- [ ] `retrieval_id` appears unchanged in `replay_metadata`
- [ ] `request_id` appears unchanged in `replay_metadata`
- [ ] `coverage_score` in `replay_metadata` equals `C0EvidenceContract.coverage_score` (not shaper's computed value)
- [ ] `replay_metadata` key names do not collide with standard replay keys (`snapshot_ids`, `commit_shas`, `artifact_digests`, `source_artifacts`)

### 7.6 No Prompt Scatter Regression

- [ ] `_SHARED_POLICY`, `_SHARED_ABSTAIN`, `_SHARED_REFINE` remain defined once each, referenced by all 8 templates
- [ ] No new per-builder inline policy text introduced
- [ ] No new packet template added to `TEMPLATES` dict

### 7.7 No Unsafe Artifact Writes

- [ ] `artifacts/adg/packets/` is written ONLY when `assembly_result in ("pass", "partial")`
- [ ] No file written when `assembly_result == "fail"`
- [ ] No file written when adapter abstain gate fires

---

## 8. Risks and Mitigations — Final Register

| Risk | Severity | Status | Mitigation |
|------|---------|--------|-----------|
| `_assemble()` coverage-semantics failure | **HIGH** | **RESOLVED by Option C** | `pre_shaped_bundle` parameter bypasses internal `shape_evidence()` call |
| Layer boundary violation: L3 adapter importing from tool layer | **HIGH** | **Must verify** | Check E6 gate before committing; if L3→tool is disallowed, adapter moves to `tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py` instead |
| `replay.update(replay_extras)` key collision | MEDIUM | **Confirmed safe** | No collision between C0 extras and existing `replay` dict keys |
| `abstain_hint` bypassed by misconfigured dispatcher | HIGH | **Design** | Adapter gate fires before `_assemble()`; `replay_metadata["abstain_hint"]` is the downstream signal |
| `evidence_hmac` recomputed or dropped | **HIGH** | **Structurally prevented** | `EvidenceBundle` has no HMAC field; only `replay_metadata` carries it; `replay.update()` preserves it |
| Adapter places duplicate spans due to missing dedup | MEDIUM | **Shaper handles** | `_dedupe_items()` deduplicates on `(source_artifact, source_type, chunk_hash)`; C0 spans with same `chunk_hash` are deduplicated correctly |
| `text_snippet` inflation in large C0 spans | MEDIUM | **Adapter gate** | 512-char truncation at word boundary in adapter; gap string emitted |
| All 8 existing builders regress from `_assemble()` change | LOW | **Backward safe** | `pre_shaped_bundle=None` default preserves existing code path exactly |
| `overflow_action="split"` causes incomplete follow-on | MEDIUM | **Documented** | Treat as `"partial"` in initial implementation; no part-2 follow-on attempted |
| `infrastructure_boundary` source_type mismatch | LOW | **Pre-existing** | Not introduced by bridge; separate fix in own PR |

---

## 9. Explicit Assumptions and Uncertainties

| Item | Status |
|------|--------|
| L3→tool layer cross-import is permitted by E6 gate | **MUST VERIFY** — highest uncertainty; determines adapter file location |
| `_assemble()` `pre_shaped_bundle` parameter addition is a backward-compatible additive change | **Confirmed by design** — all 8 callers pass no new arguments |
| `apply_budget()` trim order is end-of-list (lowest index last) | **Confirmed from implementation** |
| `shape_evidence(items, must_use_sources=[])` is a valid invocation — no assertion or validation on `must_use_sources` | **Confirmed from implementation** — no type check on this parameter |
| `C0EvidenceContract.cited_spans` is `tuple[CitedSpan, ...]` (immutable, ordered) | **Confirmed from contract file** |
| `CitedSpan.chunk_hash` is stable and unique within one retrieval pass | **Confirmed from HMAC computation logic in `c0_evidence_contract_types.py`** |
| L3 dispatcher exists and owns packet type selection | **Architectural assumption** — dispatcher not in scope for Stage 2 |
| `artifacts/adg/packets/` is writable by the process | **Confirmed** — directory exists, currently empty |
| No existing test asserts that `shape_evidence()` is always called inside `_assemble()` | **Inferred** — no test files scanned; must verify before committing `pre_shaped_bundle` change |
| `_SHARED_POLICY` rule 7 `"C0 retrieves only; prompt assembly packages only"` covers the bridge adapter implicitly | **Confirmed** — adapter translates only, does not retrieve or package |

---

## 10. Stage 1 Package Inventory

All 9 Stage 1 design artifacts:

| Artifact | Path | Focus |
|----------|------|-------|
| ADG Prompt Assembly Inventory | `docs/reports/plans/adg_prompt_assembly_inventory.md` | Current-state discovery of PA package |
| ADG Result Consumers Map | `docs/reports/plans/adg_result_consumers.md` | ADG consumer families and artifact consumption |
| ADG Prompt Scatter Findings | `docs/reports/plans/adg_prompt_scatter_findings.md` | Prompt scatter analysis and architectural gap |
| ADG Evidence Contract | `docs/reports/plans/adg_evidence_contract.md` | Field-by-field C0→PA mapping matrix |
| ADG Evidence Shaping Plan | `docs/reports/plans/adg_evidence_shaping_plan.md` | Shaping pipeline design for C0 spans |
| ADG Prompt Contracts | `docs/reports/plans/adg_prompt_contracts.md` | Contract sufficiency assessment |
| ADG Prompt Templates | `docs/reports/plans/adg_prompt_templates.md` | Packet-by-packet runtime-readiness review |
| ADG Packet Registry Plan | `docs/reports/plans/adg_packet_registry_plan.md` | Registry and builder entrypoint design |
| ADG Token Budgeting Rules | `docs/reports/plans/adg_token_budgeting_rules.md` | C0-specific token constraints |
| ADG Packet Overflow Policy | `docs/reports/plans/adg_packet_overflow_policy.md` | Overflow actions, abstain semantics, gates |
| ADG Prompt Packet Families | `docs/reports/plans/adg_prompt_packet_families.md` | Applicability matrix and selection policy |
| **ADG Prompt Assembly Integration Plan** | **`docs/reports/plans/adg_prompt_assembly_integration_plan.md`** | **This document — final Stage 1 package** |
