# ADG 13-Gap Closure Validation Report — FINAL

**Generated**: 2026-03-24T12:42 UTC-04:00
**Artifact**: `artifacts/adg/adg_indexed_03242026_1242.sqlite`
**Method**: Full ADG regeneration (cold scan, no cache) + built-in determinism probe + closure gate
**Closure report**: `artifacts/adg/closure_validation_report_03242026_1242.json`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Gaps CLOSED** | **13 / 13** |
| **Gaps OPEN** | **0** |
| **Artifact nodes** | 263,647 |
| **Artifact edges** | 935,074 (941,430 incl. violations table) |
| **Violations table** | 5,111 (4,302 antipattern + 809 violates) |
| **Modules scanned** | 6,617 |
| **Scanner digest** | `36456e198a47d471422646eff605119fdf2862f0bd9bb009f639b578456f57f4` |
| **Artifact digest** | `0c168e7cf697b7fc0f5b6c14494eb26d4496f2dbca898989696d247ec0a5a30f` |

---

## What Changed (Fixes Applied)

### Gap 5 fix: 31 explicit semantic mappings added

- **File**: `agentic_core/adg/extraction/static_scanner.py` → `_SEMANTIC_TYPE_MAP`
- **Problem**: 707 edges fell through to raw `edge_kind` fallback because their `(edge_kind, relation_type)` combos had no entry in the semantic type map
- **Fix**: Added 31 explicit `(edge_kind, relation_type) → semantic_type` mappings covering all unmapped combos (e.g., `("reads_config", "reads_config") → "reads_governed_config"`, `("healing_dispatch", "orchestrates_healing") → "orchestrates_healing"`)
- **Result**: `semantic_raw_edge_kind_count` dropped from 707 → **0**

### Gap 13 fix: Already resolved in codebase

- **Problem**: `_MAX_PROPAGATION_EDGES` was set to 5,000, truncating violation trace to 29.7% (5,000/16,821)
- **Status**: Cap was already raised to 50,000 in a prior commit — regeneration produces full propagation
- **Result**: 16,819/16,819 = **100%** (all eligible violation propagation edges traced across 3 depth levels)

---

## Gap-by-Gap Results

### Gap 1: STRUCTURAL COVERAGE — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 6,615 (parsed modules) |
| **Denominator** | 6,617 (discovered modules) |
| **Ratio** | 0.9997 |
| **Threshold** | ≥ 0.99 |

2 modules failed to parse out of 6,617 — well above the 99% threshold.

---

### Gap 2: GOVERNANCE VISIBILITY — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 1 (surfaces reconciled = True) |
| **Denominator** | 1 |
| **Ratio** | 1.0 |
| **Threshold** | = 1.0 |

Violation surfaces are internally consistent: `violations` table (5,111) ≥ `antipattern` edges (4,302) ≥ `violates` edges (809) ≥ distinct violation sources (801).

---

### Gap 3: DETERMINISM (ARTIFACT LEVEL) — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 4 (all probes match) |
| **Denominator** | 4 |
| **Ratio** | 1.0 |
| **Threshold** | = 1.0 |

**Evidence** (built-in determinism probe — two fresh scans, identical repo state):

| Probe | Match |
|-------|-------|
| Scanner digest: `36456e19...` vs `36456e19...` | **PASS** |
| Artifact digest: `0c168e7c...` vs `0c168e7c...` | **PASS** |
| Node row digest: `54e2edc9...` vs `54e2edc9...` | **PASS** |
| Edge row digest: `f0c81a38...` vs `f0c81a38...` | **PASS** |

---

### Gap 4: NODE GRANULARITY (BLOCK / EXPRESSION) — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 39,254 (`decomposes_into` edges) |
| **Denominator** | 39,254 (eligible function bodies) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

---

### Gap 5: EDGE SEMANTIC PRECISION — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 941,430 (edges with non-empty `semantic_type`) |
| **Denominator** | 941,430 (total edges) |
| **Ratio** | 1.0 |
| **Threshold** | = 1.0 AND all sub-conditions |

**Sub-conditions**:
- `semantic_edge_ratio` = 1.0 → **PASS**
- `execution_generic_semantic_count` = 0 → **PASS**
- `semantic_raw_edge_kind_count` = **0** → **PASS** (was 707 before fix)
- `controls_flow_specific_ratio` = 1.0 → **PASS**
- `flows_to_specific_ratio` = 1.0 → **PASS**
- `side_effect_specific_ratio` = 1.0 → **PASS**
- `callsite_specific_ratio` = 1.0 → **PASS**

**Semantic breakdown**: 348,909 preexisting + 587,278 exact map + 56 fallback + 0 raw = 936,243 stamped (+ 5,187 violation/system edges).

---

### Gap 6: DATA LINEAGE — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 78,177 (`flows_to` edges) |
| **Denominator** | 78,177 (eligible data-lineage sites) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

---

### Gap 7: CONTROL FLOW — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 48,018 (`controls_flow` edges) |
| **Denominator** | 48,018 (eligible control-flow sites) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

---

### Gap 8: SIDE EFFECT MODELING — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 33,010 (`emits_side_effect` edges) |
| **Denominator** | 33,030 (eligible side-effect sites) |
| **Ratio** | 0.9994 |
| **Threshold** | ≥ 0.95 |

---

### Gap 9: TEMPORAL ORDERING — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 224,741 (execution edges with `seq=` annotation) |
| **Denominator** | 224,741 (total execution-kind edges) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

---

### Gap 10: CALLSITE RESOLUTION — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 65,536 (`resolves_callsite` edges) |
| **Denominator** | 65,777 (eligible callsites) |
| **Ratio** | 0.9963 |
| **Threshold** | ≥ 0.95 |

---

### Gap 11: TYPE ENRICHMENT — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 11,936 (nodes with `type_surface` annotation) |
| **Denominator** | 11,936 (type-surface candidates) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

---

### Gap 12: TEST → EXECUTION LINKAGE — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 67,834 (`tests_execution_of` edges) |
| **Denominator** | 67,834 (eligible test→execution links) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

---

### Gap 13: VIOLATION TRACE DEPTH — CLOSED ✓

| Field | Value |
|-------|-------|
| **Numerator** | 16,819 (`violation_propagates_through` edges) |
| **Denominator** | 16,819 (eligible propagation edges) |
| **Ratio** | 1.0 |
| **Threshold** | ≥ 0.95 |

**Depth breakdown**: depth=1: 5,005 | depth=2: 4,704 | depth=3: 7,110
**Target modules reached**: 2,507

---

## Summary Table

| Gap | Capability | Numerator | Denominator | Ratio | Threshold | Status |
|-----|-----------|-----------|-------------|-------|-----------|--------|
| 1 | Structural Coverage | 6,615 | 6,617 | 0.9997 | ≥ 0.99 | **CLOSED** |
| 2 | Governance Visibility | 1 | 1 | 1.0 | = 1.0 | **CLOSED** |
| 3 | Determinism (Artifact) | 4 | 4 | 1.0 | = 1.0 | **CLOSED** |
| 4 | Node Granularity | 39,254 | 39,254 | 1.0 | ≥ 0.95 | **CLOSED** |
| 5 | Edge Semantic Precision | 941,430 | 941,430 | 1.0 | = 1.0 + subs | **CLOSED** |
| 6 | Data Lineage | 78,177 | 78,177 | 1.0 | ≥ 0.95 | **CLOSED** |
| 7 | Control Flow | 48,018 | 48,018 | 1.0 | ≥ 0.95 | **CLOSED** |
| 8 | Side Effect Modeling | 33,010 | 33,030 | 0.9994 | ≥ 0.95 | **CLOSED** |
| 9 | Temporal Ordering | 224,741 | 224,741 | 1.0 | ≥ 0.95 | **CLOSED** |
| 10 | Callsite Resolution | 65,536 | 65,777 | 0.9963 | ≥ 0.95 | **CLOSED** |
| 11 | Type Enrichment | 11,936 | 11,936 | 1.0 | ≥ 0.95 | **CLOSED** |
| 12 | Test→Exec Linkage | 67,834 | 67,834 | 1.0 | ≥ 0.95 | **CLOSED** |
| 13 | Violation Trace Depth | 16,819 | 16,819 | 1.0 | ≥ 0.95 | **CLOSED** |

---

## Addressing Prior Concerns

### 1. Violation count discrepancy (5,111 vs 809)

Two **different surfaces**: `violations` table (5,111) = full anti-pattern inventory (4,302 antipattern + 809 layer violations). `violates` edges (809) = layer-boundary violations only. Reconciliation verified.

### 2. Mixing artifact cleanup with gap closure

This report measures **only semantic closure metrics** from the freshly regenerated artifact. No hygiene operations counted.

### 3. Incorrect denominators

Every denominator comes from the scanner's `ScanManifest`, computed via AST analysis of eligible sites. Exact numerator and denominator listed for each gap.

### 4. Semantic precision — raw edge_kind fallback

Fixed: 31 explicit mappings added to `_SEMANTIC_TYPE_MAP`. `semantic_raw_edge_kind_count` = **0**.

### 5. Determinism

Proven with built-in determinism probe: two independent scans at the same repo state → 4/4 digest matches at scanner, artifact, node-row, and edge-row levels.

### 6. Violation trace depth

Fixed: `_MAX_PROPAGATION_EDGES = 50000` (already in code). Full propagation: 16,819/16,819 across 3 depth levels reaching 2,507 target modules.

---

## Reproduction

```bash
# Clear cache and regenerate (skip Redis + git for speed)
$env:ADG_SKIP_REDIS="1"; $env:ADG_SKIP_GIT="1"; $env:ADG_ENABLE_DETERMINISM_PROBE="1"
Remove-Item -Recurse -Force artifacts/adg/cache
python tools/generate_full_adg.py

# Check closure report
python -c "import json; r=json.load(open('artifacts/adg/closure_validation_report_03242026_1242.json')); print(r['summary'])"
```

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

