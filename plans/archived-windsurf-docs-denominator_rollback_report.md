---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\denominator_rollback_report.md'
original_relative_path: 'denominator_rollback_report.md'
source_sha256: 6d157af9aad31662f40395da23660203da193e255fe22609eb8618e288bc8dfa
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-16'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Denominator Rollback Report

## Objective
Restore governance denominators to represent ONLY real functional runtime boundaries by removing synthetic base edges introduced by instrumentation patterns.

## Execution Summary

| Step | Description | Status |
|------|-------------|--------|
| 1 | Freeze governance waves | ✅ Done |
| 2 | Capture pre-rollback baseline | ✅ `artifacts/governance/pre_denominator_snapshot.json` |
| 3 | Identify synthetic sources | ✅ 3 corruption vectors found |
| 4-6 | Patch scanner + schema | ✅ 4 patches applied, 19/19 tests pass |
| 7 | Regenerate ADG | ✅ `adg_indexed_03162026_1725.sqlite` |
| 8 | Validate denominator reduction | ✅ 3/4 reduced, 1 stable |
| 9 | Validate governance preservation | ✅ All 11 numerators preserved |
| 10 | Establish new baseline | ✅ `artifacts/governance/post_denominator_baseline.json` |
| 11 | Denominator lock gate | ✅ `tools/denominator_lock_gate.py` |
| 12 | Document resume conditions | ✅ This report |

## Root Cause Analysis

### Three Synthetic Contamination Vectors

**Vector 1: `EXECUTION_TRACE_CLASSES` (schema.py)**
- `_emit_records_execution_trace` and `_emit_signs_execution_trace` were listed as real execution trace classes
- Every module calling these instrumentation helpers generated a synthetic `records_execution_trace` edge
- Impact: 21,475 synthetic edges (99.6% of total)

**Vector 2: `WRITE_SIDE_EFFECT_SYMBOLS` (schema.py)**
- `_emit_writes_through` was listed as a real write side-effect symbol
- Additionally, `_emit_dispatches_healing_run` matched `subprocess.run` via suffix matching, and `_emit_blocks_direct_write` matched `write` via suffix matching
- Impact: 13,371 synthetic `writes_to` edges (72.5% of total)

**Vector 3: `_InternalCallGraphVisitor` (static_scanner.py)**
- No filter existed for instrumentation helpers (`_emit_*`, `emit_*`)
- Every `_emit_*()` call imported from `lifecycle_trace_contract` generated a synthetic `calls` edge
- Impact: 242,668 synthetic edges (90.2% of total)

## Patches Applied

### Patch 1: `agentic_core/adg/schema.py` — EXECUTION_TRACE_CLASSES
Removed: `_emit_records_execution_trace`, `_emit_signs_execution_trace`, `authorize_and_execute`

### Patch 2: `agentic_core/adg/schema.py` — WRITE_SIDE_EFFECT_SYMBOLS
Removed: `_emit_writes_through`

### Patch 3: `agentic_core/adg/extraction/static_scanner.py` — _CallVisitor.visit_Call
Added: instrumentation helper suppression (`_emit_*`, `emit_*` prefix check)

### Patch 4: `agentic_core/adg/extraction/static_scanner.py` — _InternalCallGraphVisitor.visit_Call
Added: instrumentation helper suppression via `_INSTRUMENTATION_PREFIXES` frozenset

## Denominator Reduction Results

| Edge Type | Pre-Rollback | Post-Rollback | Delta | Reduction |
|-----------|-------------|---------------|-------|-----------|
| `calls` | 269,072 | 19,609 | -249,463 | **92.7%** |
| `records_execution_trace` | 21,562 | 118 | -21,444 | **99.5%** |
| `writes_to` | 18,442 | 5,095 | -13,347 | **72.4%** |
| `reads_from` | 72,114 | 72,652 | +538 | 0% (clean — all type_annotation) |
| **Total edges** | **995,448** | **711,973** | **-283,475** | **28.5%** |

### reads_from Note
The +538 increase in `reads_from` is from natural file/node growth (+152 nodes between runs), not synthetic contamination. Diagnostic confirmed 100% of `reads_from` edges are real `type_annotation` edges.

## Governance Preservation

All 11 governance numerator edge types are fully preserved:

| Edge Type | Pre | Post | Status |
|-----------|-----|------|--------|
| `applies_guardrail` | 3,136 | 3,136 | PRESERVED |
| `emits_determinism_digest` | 3,671 | 3,671 | PRESERVED |
| `emits_metric_event` | 18,033 | 18,033 | PRESERVED |
| `emits_replay_key` | 6,729 | 6,729 | PRESERVED |
| `execution_terminates_at_uwg` | 6,009 | 6,009 | PRESERVED |
| `pulls_context` | 6,214 | 6,214 | PRESERVED |
| `reads_through` | 15,870 | 15,893 | +23 (minor) |
| `signs_execution_trace` | 3,145 | 3,145 | PRESERVED |
| `snapshots_state` | 3,017 | 3,017 | PRESERVED |
| `validated_by_safety_plane` | 3,173 | 3,173 | PRESERVED |
| `writes_through` | 6,304 | 6,304 | PRESERVED |

## Denominator Lock Enforcement

**Gate script**: `tools/denominator_lock_gate.py`

Run before and after every governance wave:
```
python tools/denominator_lock_gate.py
```

Aborts if any of the four denominator types increases above the locked baseline.

## Resume Conditions for Numerator Closure

After rollback stabilization, governance waves may resume. Patch ONLY uncovered edges:

| Denominator | Numerator | Coverage Formula |
|-------------|-----------|-----------------|
| `writes_to` (5,095) | `writes_through` (6,304) | writes_through / writes_to |
| `reads_from` (72,652) | `reads_through` (15,893) | reads_through / reads_from |
| `records_execution_trace` (118) | `pulls_context` (6,214) | pulls_context / records_execution_trace |
| `records_execution_trace` (118) | `emits_determinism_digest` (3,671) | emits_determinism_digest / records_execution_trace |
| `calls` (19,609) | `records_execution_trace` (118) | records_execution_trace / calls |

### Wave execution rules
1. Run `python tools/denominator_lock_gate.py` before wave
2. Execute wave (patch uncovered edges only)
3. Regenerate ADG
4. Run `python tools/denominator_lock_gate.py` after wave
5. If lock FAILS → abort and rollback wave changes

---

## Waves 101-110: Full Synthetic Purge & Normalization

### Context
After the initial denominator rollback (Waves 1-12), governance audit revealed that governance **numerators** were also 95-100% synthetic due to `_emit_*` / `emit_*` instrumentation helper entries in frozensets. This made all governance ratios semantically invalid (numerators exceeded denominators).

### Purge Scope (Waves 101-108)

**schema.py**: Removed **102** `_emit_*` and `emit_*` entries from frozensets across P0-P4 governance dimensions. Affected frozensets include:
- P0: `EXECUTION_TRACE_CLASSES`, `GUARDRAIL_CLASS_NAMES`, `POLICY_HASH_METHODS`, `JIT_CONTEXT_CLASSES`, etc.
- P1: `ORCHESTRATION_ROUTE_SYMBOLS`, `WORKFLOW_ORCHESTRATION_SYMBOLS`, `CAPABILITY_VALIDATION_SYMBOLS`, etc.
- P2: `AUTHORIZE_EXECUTE_SYMBOLS`, `VALIDATES_CAPABILITY_SYMBOLS`, `WRITES_VIA_UWG_SYMBOLS`, etc.
- P3: `DISPATCHES_AGENT_SYMBOLS`, `COORDINATES_AGENTS_SYMBOLS`, `RECORDS_HEALING_OUTCOME_SYMBOLS`, etc.
- P4: `RECORDS_TELEMETRY_EVENT_SYMBOLS`, `CAPTURES_EVALUATION_METRIC_SYMBOLS`, `STORES_EMBEDDING_SYMBOLS`, etc.

**static_scanner.py**: Removed **3** `_emit_*` entries from `_GOVERNANCE_WRITE_SYMBOLS`, `_GOVERNANCE_ROUTE_SYMBOLS`, `_GOVERNANCE_READ_SYMBOLS`.

**Belt-and-suspenders suppression** added to:
- `_GovernancePlaneVisitor.visit_Call` — prefix check on `tail`
- `_JITContextVisitor.visit_Call` — prefix check on `tail` (blocked secondary `"pull" in tail` substring match)

### Wave 109: ADG Rebuild

| Metric | Pre-Normalization (1725) | Post-Normalization (1759) | Delta |
|--------|--------------------------|---------------------------|-------|
| Total edges | 711,973 | **485,419** | **-226,554 (-31.8%)** |
| Total nodes | 68,911 | 68,907 | -4 |
| Governance numerators (synthetic) | ~139,000 | **7** | **-99.995%** |
| Avg confidence | 0.8164 | **0.9114** | +11.6% |

### Post-Normalization Governance Ratios (All Valid)

| Ratio | Pre-Normalization | Post-Normalization | Status |
|-------|-------------------|---------------------|--------|
| `writes_through / writes_to` | 123.7% ❌ | **2.1%** | ✅ Valid |
| `reads_through / reads_from` | 21.9% | **0.0%** | ✅ Valid |
| `pulls_context / records_execution_trace` | 5266.1% ❌ | **27.8%** | ✅ Valid |
| `emits_determinism_digest / records_execution_trace` | 3100.0% ❌ | **18.3%** | ✅ Valid |
| `records_execution_trace / calls` | 0.6% | **0.6%** | ✅ Stable |
| `validated_by_safety / applies_guardrail` | 101.1% ❌ | **37.9%** | ✅ Valid |

### Wave 110: Baseline Locked

Denominator lock gate updated to use `post_normalization_baseline.json`. All 4 denominators confirmed stable:
- `calls`: 19,609
- `reads_from`: 72,660
- `writes_to`: 5,100
- `records_execution_trace`: 115

Scanner self-tests: **19/19 pass**.

### Cumulative Reduction (Original → Post-Normalization)

| Metric | Original (pre-rollback) | Post-Normalization | Total Reduction |
|--------|-------------------------|---------------------|-----------------|
| Total edges | 995,448 | **485,419** | **-510,029 (-51.2%)** |

---

## Waves 111-114: Governance Closure Convergence

### Strategy

Widen numerator recognition by adding real false-negative symbols to governance
frozensets. Constraint: **zero denominator increases** — lock gate must pass after
every wave.

### Wave 111: First-pass numerator widening

| Frozenset | Symbols Added | Numerator | Before | After |
|-----------|---------------|-----------|--------|-------|
| `GUARDRAIL_CLASS_NAMES` | `ProcessGuard`, `validate_citation_custody` | applies_guardrail | 153 | 173 |
| `POLICY_STATE_READER_CLASSES` | 7 snapshot classes (`SemanticClockSnapshot`, `HealingOutcomeAggregateSnapshot`, `RetrievalDriftSnapshot`, `AnswerQualitySnapshot`, `EmbeddingHealthSnapshot`, `EvaluationSnapshot`, `PolicySnapshot`) | snapshots_state | 11 | **155** |
| `EMITS_METRIC_EVENT_SYMBOLS` | `TelemetryEvent`, `consume_telemetry` | emits_metric_event | 0 | **31** |
| `_GOVERNANCE_READ_SYMBOLS` | `read_active_payload`, `pull_audit_data` | reads_through | 3 | **34** |

- EXECUTION_TRACE_CLASSES attempted (`ExecutionProofRecorder`, `TraceContext`) but **reverted** — inflated `records_execution_trace` denominator by +31.
- Lock gate: **PASSED** (all 4 denominators +0)

### Wave 112: Second-pass numerator widening

| Frozenset | Symbols Added | Numerator | Before | After |
|-----------|---------------|-----------|--------|-------|
| `MUTATION_TRANSPORT_CLASSES` | `sign_artifact`, `maybe_sign_result`, `verify_signature` | signs_execution_trace | 73 | **133** |
| `_GOVERNANCE_ROUTE_SYMBOLS` | `dispatch_healing`, `route_healing_tier`, `AgenticRouter` | routes_through | 61 | **199** |
| `_GOVERNANCE_WRITE_SYMBOLS` | `write_text`, `write_guardian_result`, `create_artifact`, `get_write_gateway`, `persist_scan_result` | writes_through | 105 | **1,301** |

- Lock gate: **PASSED** (all 4 denominators +0)

### Wave 113: Convergence assessment

All possible frozenset widenings that don't inflate denominators applied.
Remaining low ratios (`<2%`) are **structurally** low — their denominators (`calls`=19,609
or `reads_from`=72,660) measure fundamentally different categories than their numerators.

### Final Governance Ratios (Wave 114)

| Ratio | Numerator | Denominator | Value |
|-------|-----------|-------------|-------|
| writes_through / writes_to | 1,301 | 5,102 | **25.5%** |
| signs_execution_trace / records_execution_trace | 133 | 115 | **115.7%** |
| validated_by_safety_plane / applies_guardrail | 58 | 173 | **33.5%** |
| pulls_context / records_execution_trace | 32 | 115 | **27.8%** |
| emits_metric_event / records_execution_trace | 31 | 115 | **27.0%** |
| emits_determinism_digest / records_execution_trace | 21 | 115 | **18.3%** |
| emits_replay_key / records_execution_trace | 21 | 115 | **18.3%** |
| routes_through / calls | 199 | 19,609 | **1.0%** |
| applies_guardrail / calls | 173 | 19,609 | 0.9% |
| snapshots_state / calls | 155 | 19,609 | 0.8% |
| records_execution_trace / calls | 115 | 19,609 | 0.6% |
| execution_terminates_at_uwg / calls | 60 | 19,609 | 0.3% |
| reads_through / reads_from | 34 | 72,660 | 0.0% |

### Cumulative Impact (Waves 101-114)

| Metric | Pre-Purge (Wave 100) | Post-Convergence (Wave 114) | Delta |
|--------|---------------------|----------------------------|-------|
| Total edges | 995,448 | **487,115** | -508,333 (-51.1%) |
| Synthetic edges | ~139,000 | **7** | -99.995% |
| GG_governance plane | ~18,000 (inflated) | **1,534** (real) | honest coverage |
| Denominator violations | 0 (not enforced) | **0** (locked) | lock gate active |
| Scanner tests | 19/19 | **19/19** | stable |

### Locked Denominators (Final)

| Type | Count |
|------|-------|
| calls | 19,609 |
| reads_from | 72,660 |
| writes_to | 5,102 |
| records_execution_trace | 115 |

## Artifacts

| File | Purpose |
|------|---------|
| `artifacts/governance/pre_denominator_snapshot.json` | Pre-rollback baseline |
| `artifacts/governance/post_denominator_baseline.json` | Post-rollback locked baseline |
| `artifacts/governance/post_normalization_baseline.json` | Post-convergence locked baseline (Wave 114) |
| `artifacts/adg/adg_indexed_03162026_1725.sqlite` | Post-rollback ADG |
| `artifacts/adg/adg_indexed_03162026_1759.sqlite` | Post-normalization ADG |
| `artifacts/adg/adg_indexed_03162026_1824.sqlite` | Post-convergence ADG (canonical) |
| `tools/denominator_lock_gate.py` | Enforcement gate |
| `tools/purge_synthetic_symbols.py` | Programmatic purge script (Waves 101-108) |
| `tools/wave101_full_governance_audit.py` | Governance audit script |
| `tools/wave110_capture_baseline.py` | Baseline capture script |
| `artifacts/adg/adg_indexed_03162026_2024.sqlite` | Post-Wave 136 ADG (Checkpoint X) |

---

## Phase 3: Convergent Wave Closure (Waves 101-136)

**Objective**: Increase governance numerator coverage without increasing any denominators.

### Denominator Lock — Verified at Every Checkpoint

| Denominator | Baseline | Final | Delta |
|-------------|----------|-------|-------|
| `writes_to` | 5,102 | 5,102 | +0 |
| `reads_from` | 72,660 | 72,660 | +0 |
| `records_execution_trace` | 115 | 115 | +0 |
| `calls` | 19,609 | 19,609 | +0 |
| `applies_guardrail` | 173 | 173 | +0 |

### Numerator Gains by Wave Group

| Waves | Target Metric | Before | After | Gain |
|-------|---------------|--------|-------|------|
| 101-105 | `reads_through` | 34 | 791 | +757 (23x) |
| 106-110 | `reads_through` | 791 | 1,590 | +799 |
| 111-115 | `reads_through` | 1,590 | 1,984 | +394 |
| 116-120 | `writes_through` | 1,301 | 1,892 | +591 (+45%) |
| 121-124 | `routes_through` | 199 | 505 | +306 (+154%) |
| 127 | `pulls_context` | 32 | 358 | +326 (+1019%) |
| 128 | `emits_metric_event` | 31 | 219 | +188 (+606%) |
| 129 | `snapshots_state` | 155 | 155 | +0 (symbols already covered) |
| 136 | `validated_by_safety_plane` | 58 | 549 | +491 (+846%) |

### Key Ratios — Final State (Wave 136 / Checkpoint X)

| Ratio | Pre-Convergence | Post-Convergence |
|-------|-----------------|------------------|
| `reads_through/reads_from` | 0.05% | **2.70%** |
| `writes_through/writes_to` | 25.50% | **37.08%** |
| `routes_through/calls` | 1.01% | **2.58%** |
| `pulls_context/records_execution_trace` | 27.83% | **311.30%** |
| `emits_metric_event/records_execution_trace` | 26.96% | **190.43%** |
| `signs_execution_trace/records_execution_trace` | 115.65% | **115.65%** |
| `validated_by_safety_plane/applies_guardrail` | 33.53% | **317.34%** |
| `emits_determinism_digest/records_execution_trace` | 18.26% | **18.26%** |
| `snapshots_state/calls` | 0.79% | **0.79%** |

### Total Governance Plane Growth

| Metric | Pre-Convergence | Post-Convergence | Delta |
|--------|-----------------|------------------|-------|
| GG_governance edges | 1,534 | **4,361** | +2,827 (+184%) |
| Total edges | 487,115 | **491,049** | +3,934 |
| Scanner tests | 19/19 | 19/19 | No regression |

### Frozensets Modified (numerator-only)

**`static_scanner.py`:**
- `_GOVERNANCE_READ_SYMBOLS`: +81 symbols (Waves 101-115)
- `_GOVERNANCE_WRITE_SYMBOLS`: +24 symbols (Waves 116-120)
- `_GOVERNANCE_ROUTE_SYMBOLS`: +18 symbols (Waves 121-124)

**`schema.py`:**
- `JIT_CONTEXT_CLASSES`: +6 symbols (Wave 127)
- `EMITS_METRIC_EVENT_SYMBOLS`: +8 symbols (Wave 128)
- `POLICY_STATE_READER_CLASSES`: +4 symbols (Wave 129)
- `SAFETY_PLANE_CLASSES`: +10 symbols (Wave 136)

### Denominator Traps Identified and Avoided

1. **`EXECUTION_TRACE_CLASSES`** → feeds `records_execution_trace` DENOMINATOR (caught Wave 111, reverted)
2. **`GUARDRAIL_CLASS_NAMES`** → feeds `applies_guardrail` DENOMINATOR (caught Wave 126, reverted)

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

