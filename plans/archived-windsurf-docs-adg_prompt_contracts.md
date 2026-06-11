---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_prompt_contracts.md'
original_relative_path: 'adg_prompt_contracts.md'
source_sha256: 0113fa8a46e6186d74478cc0529253c119bc9c88e596a3708f3ce30e37730326
recovered_status: LOST_RECOVERED
last_commit: 'fd8afcb3494'
last_commit_date: '2026-04-11 11:10:04 -0400'
created_date: '2026-04-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Prompt Contracts — Runtime-Readiness Assessment
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: PromptEnvelope, PromptAssemblyStatus, EvidenceItem, EvidenceBundle, ContradictionFlag

---

## 1. Executive Summary

**Verdict: All existing PA contracts are runtime-ready for the C0→PA bridge without any required field additions.** Every field needed to carry C0 bridge metadata already exists:

- `EvidenceItem.cited_spans: list[str]` is the exact slot for `CitedSpan.span_id` values — currently empty in all ADG file adapters, designed for this use.
- `EvidenceItem.support_score: float` maps directly from `CitedSpan.relevance_score`.
- `PromptEnvelope.replay_metadata: dict[str, Any]` is an open dict that absorbs all C0 identity fields (`retrieval_id`, `request_id`, `evidence_hmac`, `abstain_hint`, `confidence_band`) without any schema change.
- `_assemble()` already builds `replay_metadata` from item fields and accepts `replay_extras` to inject any additional key-value pairs.
- `PromptAssemblyStatus` already carries `evidence_contract_status`, `assembly_result`, and `overflow_action` — every state that a C0 bridge handoff needs to audit.

**One conditional additive change** is identified but explicitly deferred: adding `"c0_span"` to the `SourceType` Literal in `contracts.py`. It is not blocking — the bridge can use `"json_report"` with `source_artifact="c0_retrieval:<retrieval_id>"` as a placeholder until differentiation is proven necessary.

---

## 2. Contract Field-by-Field Sufficiency Assessment

### 2.1 EvidenceItem — SUFFICIENT

| Field | Bridge use | Sufficiency |
|-------|-----------|-------------|
| `source_artifact` | `"c0_retrieval:<retrieval_id>"` or `source_ref` value | ✅ Sufficient |
| `source_type` | `"json_report"` (placeholder) or future `"c0_span"` | ✅ Sufficient without type extension |
| `snapshot_id` | Derived from `retrieval_id` or `source_ref` filename | ✅ Sufficient |
| `commit_sha` | Left `""` — not available from C0 | ✅ Sufficient (optional field) |
| `scanner_digest` | Left `""` — no scanner context in runtime retrieval | ✅ Sufficient (optional field) |
| `artifact_digest` | Left `""` — C0 does not hash artifact files | ✅ Sufficient (optional field) |
| `row_references` | `[span.chunk_hash]` — chunk hash as row identifier | ✅ Sufficient |
| `cited_spans` | `[span.span_id]` — the exact intended use | ✅ Sufficient, already designed for bridge |
| `support_score` | `span.relevance_score` — 1-to-1 | ✅ Sufficient |
| `coverage_score` | `contract.coverage_score` propagated to all spans | ✅ Sufficient |
| `is_derived` | Always `False` for C0 spans | ✅ Sufficient |
| `freshness` | ISO-8601 UTC at adapter call time | ✅ Sufficient |
| `data` | `{"text_snippet": ..., "source_ref": ..., "span_id": ...}` | ✅ Sufficient |

**No new fields required on `EvidenceItem`.**

---

### 2.2 EvidenceBundle — SUFFICIENT

| Field | Bridge use | Sufficiency |
|-------|-----------|-------------|
| `items` | Translated `EvidenceItem` objects from `CitedSpan` | ✅ Sufficient |
| `coverage_score` | Set by bridge merger to `contract.coverage_score` after shaping | ✅ Sufficient |
| `contradiction_status` | Computed by shaper; bridge merger may upgrade if adapter found contradictions | ✅ Sufficient |
| `contradictions` | Merged from shaper output + adapter pre-populated flags | ✅ Sufficient |
| `gaps` | Merged from shaper + adapter C0 gap strings | ✅ Sufficient |
| `freshness` | Max of all item freshness values (all identical for C0 spans) | ✅ Sufficient |
| `weak_support` | `coverage < 0.5`; bridge merger may override to True if median relevance < 0.5 | ✅ Sufficient |

**No new fields required on `EvidenceBundle`.** `confidence_band` goes into `PromptEnvelope.replay_metadata`, not here.

---

### 2.3 ContradictionFlag — SUFFICIENT

| Field | Bridge use | Sufficiency |
|-------|-----------|-------------|
| `field_name` | `"text_snippet"` for same-source-ref span conflicts | ✅ Sufficient |
| `source_a` / `source_b` | `"c0_span:<span_id>"` values | ✅ Sufficient |
| `value_a` / `value_b` | `chunk_hash` values | ✅ Sufficient |
| `severity` | `"minor"` for chunker inconsistency | ✅ Sufficient |
| `description` | Free text explanation | ✅ Sufficient |

**No new fields required on `ContradictionFlag`.**

---

### 2.4 PromptEnvelope — SUFFICIENT

| Field | Bridge use | Sufficiency |
|-------|-----------|-------------|
| `packet_type` | Unchanged — selected by bridge dispatcher | ✅ Sufficient |
| `packet_id` | Auto-generated from type + `replay_metadata` — deterministic | ✅ Sufficient |
| `schema_version` | `"1.0.0"` unchanged | ✅ Sufficient |
| `system_block` | From `PacketTemplate` — unchanged | ✅ Sufficient |
| `policy_block` | `_SHARED_POLICY` — unchanged | ✅ Sufficient |
| `task_block` | Supplied by bridge dispatcher (L3 orchestration context) | ✅ Sufficient |
| `must_use_evidence` | C0-sourced `EvidenceItem.to_dict()` after budget trimming | ✅ Sufficient |
| `optional_evidence` | Empty for pure C0 bundles unless ADG file evidence is also included | ✅ Sufficient |
| `contradiction_flags` | `[c.to_dict() for c in bundle.contradictions]` — unchanged path | ✅ Sufficient |
| `abstain_instructions` | Template `abstain_instructions`; augmented by `_assemble()` if `coverage < 0.3` | ✅ Sufficient |
| `refine_instructions` | Template `refine_instructions`; augmented by `_assemble()` budget note | ✅ Sufficient |
| `output_schema` | From `PacketTemplate.output_schema` — unchanged | ✅ Sufficient |
| `replay_metadata` | Open `dict` — absorbs `retrieval_id`, `request_id`, `evidence_hmac`, `coverage_score`, `abstain_hint`, `confidence_band` via `replay_extras` | ✅ Sufficient |
| `assembly_status` | `PromptAssemblyStatus` instance — populated by `_assemble()` | ✅ Sufficient |

**No new fields required on `PromptEnvelope`.** The `replay_extras` parameter in `_assemble()` is the correct injection point for all C0 identity metadata.

---

### 2.5 PromptAssemblyStatus — SUFFICIENT

| Field | Bridge use | Sufficiency |
|-------|-----------|-------------|
| `packet_type` | Unchanged | ✅ Sufficient |
| `packet_id` | Set from `PromptEnvelope.packet_id` after envelope is built | ✅ Sufficient |
| `input_artifacts` | List of `source_ref` values from C0 spans | ✅ Sufficient |
| `evidence_contract_status` | `"complete"` (≥0.8) / `"partial"` (≥0.3) / `"empty"` (<0.3) derived from `coverage_score` | ✅ Sufficient; thresholds match C0 abstain logic |
| `contradiction_status` | From `bundle.contradiction_status` | ✅ Sufficient |
| `token_budget_status` | From `BudgetResult.budget_status` | ✅ Sufficient |
| `overflow_action` | From `BudgetResult.overflow_action` | ✅ Sufficient |
| `assembly_result` | `"fail"` when `abstain_hint=True` (coverage_status `"empty"` path) | ✅ Sufficient — existing logic already maps empty → fail |
| `replay_metadata` | Carries `retrieval_id`, `request_id`, `evidence_hmac`, `confidence_band` | ✅ Sufficient — open dict |
| `assembly_timestamp` | Auto ISO-8601 UTC at construction | ✅ Sufficient |

**No new fields required on `PromptAssemblyStatus`.**

---

### 2.6 SourceType Literal — CONDITIONAL ADDITIVE

**Current values:** `"sqlite"`, `"json_report"`, `"graph_db"`, `"infra_view"`, `"ratchet"`, `"structural"`

**Bridge need:** The adapter uses `"json_report"` with `source_artifact="c0_retrieval:<retrieval_id>"` as the interim `source_type` for C0 spans. This works because:
- The shaper's `_compute_coverage()` classifies items by `source_type` string
- `"json_report"` will match the `json_report` coverage bucket
- `_dedupe_items()` deduplicates on `(source_artifact, source_type, row_references)` — the `source_artifact` value distinguishes C0 items from ADG file items

**When `"c0_span"` becomes necessary:** Only if shaping logic needs to *explicitly branch* on C0 vs. ADG-file items. The current shaper does not branch — it treats all items uniformly. If a future shaper extension needs C0-specific logic, adding `"c0_span"` is a one-line additive change to the `Literal` type alias.

**Decision: DEFER.** Do not add `"c0_span"` now. Re-evaluate after first bridge implementation iteration.

---

### 2.7 `_assemble()` Helper — RUNTIME-READY AS-IS

The shared `_assemble()` function in `builders.py` is the convergence point. For C0 bridge use:

| `_assemble()` input | Bridge supply |
|--------------------|--------------|
| `template` | Selected from registry by bridge dispatcher via `get_template(packet_type)` |
| `must_items` | C0 `EvidenceItem` list from adapter (all canonical — `is_derived=False`) |
| `opt_items` | Empty list `[]` for pure C0 bundles |
| `task_block` | Supplied by L3 orchestration context (the current request's task description) |
| `replay_extras` | `{"retrieval_id": ..., "request_id": ..., "evidence_hmac": ..., "coverage_score": ..., "abstain_hint": ..., "confidence_band": ...}` |

**No changes to `_assemble()` required.** The `replay_extras` dict injection already handles all C0 identity metadata.

---

### 2.8 Evidence Contract Status Threshold — ALIGNED

`_assemble()` line 90–95 computes `evidence_status`:
```python
if bundle.coverage_score >= 0.8:    evidence_status = "complete"
elif bundle.coverage_score > 0.0:   evidence_status = "partial"
else:                               evidence_status = "empty"
```

`C0EvidenceContract` abstain threshold is `0.30`. When `coverage_score < 0.30`, C0 sets `abstain_hint=True`. The bridge adapter converts this to an empty bundle (`items=[]`, `coverage_score = contract.coverage_score`). The shaper then sees `coverage_score < 0.3` → `_assemble()` augments `abstain_instructions` with the gap list → `assembly_result = "fail"`.

**Alignment confirmed:** C0 abstain → empty bundle → `_assemble()` fail path → `abstain_instructions` augmented → `assembly_result="fail"`. No threshold mismatch.

---

### 2.9 Token Budget — SUFFICIENT

`TokenBudget` fields:

| Field | Value (default) | Bridge impact |
|-------|----------------|--------------|
| `total` | 6,000 (default) / 4,000–8,000 per type | Unchanged |
| `system_policy` | 800 | Unchanged |
| `task` | 400 | Unchanged |
| `must_use_evidence` | 4,000 | C0 text spans go here; may be larger than ADG rows |
| `optional_evidence` | 800 | Empty for pure C0 bundles |
| `contradiction_meta` | 400 | Unchanged |

**Risk:** C0 `text_snippet` values may be substantially larger than ADG SQLite rows. The budgeter handles this correctly via `apply_budget()` — trimming strategies (summarize → narrow → abstain) apply uniformly. The adapter should truncate `text_snippet` to ≤512 chars before placing in `data` to prevent unexpected budget exhaustion.

**No changes to `TokenBudget` required.**

---

### 2.10 Canonical Block Ordering — CONFIRMED SUFFICIENT

The 10-block canonical order:

| # | Block | Bridge impact |
|---|-------|--------------|
| 1 | `system_block` | Template-sourced; unchanged |
| 2 | `policy_block` | `_SHARED_POLICY`; unchanged |
| 3 | `task_block` | L3 dispatcher supplies; unchanged |
| 4 | `must_use_evidence` | C0 spans land here (canonical retrieval = must-use) |
| 5 | `optional_evidence` | Empty for pure C0 bundles; may carry ADG file evidence in hybrid mode |
| 6 | `contradiction_flags` | Merged adapter + shaper contradictions; **never hidden** |
| 7 | `abstain_instructions` | Augmented with gap list when `coverage < 0.3` |
| 8 | `refine_instructions` | Augmented with budget overflow note |
| 9 | `output_schema` | Template-sourced; unchanged |
| 10 | `replay_metadata` | Extended with C0 identity fields via `replay_extras` |

**Order is canonical, enforced by `PromptEnvelope` field layout, and sufficient for the bridge.** No reordering needed.

---

## 3. Minimal Additive Changes Required

**Count: ZERO required changes.** One conditional deferred change.

| Change | Status | When |
|--------|--------|------|
| Add `"c0_span"` to `SourceType` Literal | **DEFERRED** — not blocking | After first bridge iteration proves differentiation needed |
| Add `"c0_span"` handling to `_compute_coverage()` | **DEFERRED** — not blocking | Conditional on above |
| Add `relevance_score` stratification to `token_budgeter.py` | **DEFERRED** — not blocking | Only if trim-order for C0 spans proves incorrect in practice |

---

## 4. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `_assemble()` `replay_extras` parameter correctly merges into `replay` dict before `PromptEnvelope` is built | **Confirmed** — line 85–86 of `builders.py`: `if replay_extras: replay.update(replay_extras)` |
| `evidence_contract_status` threshold `0.8` for "complete" vs `0.30` C0 abstain threshold are non-conflicting | **Confirmed** — different decision points in different contracts |
| `PromptEnvelope.packet_id` is deterministic for the same `(packet_type, replay_metadata)` | **Confirmed** — SHA-256[:16] of `json.dumps({"packet_type": ..., "replay": replay_metadata}, sort_keys=True)` |
| `"guardian: allow-broad-exception"` in `cli.py` is already approved | **Confirmed** — guardian comment present at line 153 |
| No existing field name in `replay_metadata` will collide with C0 identity fields (`retrieval_id`, `request_id`, etc.) | **Confirmed** — current `replay` dict keys are `snapshot_ids`, `commit_shas`, `artifact_digests`, `source_artifacts` |
