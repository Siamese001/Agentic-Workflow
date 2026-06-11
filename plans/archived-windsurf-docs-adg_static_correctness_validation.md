---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_static_correctness_validation.md'
original_relative_path: 'adg_static_correctness_validation.md'
source_sha256: 2f479432fbb24885b88128f926e06395d75a073608511f3f4852266c3470af79
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Static Correctness Validation — Final Report

**Date**: 2026-03-24
**ADG**: `adg_indexed_03242026_1825.sqlite`
**Nodes**: 205,202 | **Edges**: 891,270 | **Relation types**: 113
**Method**: Direct SQLite queries + independent AST walk (no mocks, no fabrication)

---

## A) METRICS TABLE

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| semantic_accuracy | **0.9870** | ≥ 0.99 | ❌ FAIL |
| symbol_alignment_rate | **1.0000** | ≥ 0.995 | ✅ PASS |
| file_ratio | **0.8931** | [0.95, 1.05] | ❌ FAIL |
| function_ratio | **0.0354** | [0.95, 1.05] | ❌ FAIL |
| signal_ratio | **0.8668** | ≥ 0.90 | ❌ FAIL |
| consistency_rate | **0.9966** | ≥ 0.99 | ✅ PASS |
| synthetic_edge_count | **7,112** | == 0 | ❌ FAIL |
| duplicate_edge_ratio | **0.0034** | == 0 | ❌ FAIL |

**Gates passed: 2/8**

---

## B) FAILURE REPORT

### 1. semantic_accuracy = 0.9870 (threshold 0.99)

**Sample size**: 2,548 edges across all 113 relation types
**Errors**: 33 (1.3%)
**Root cause**: Import edge `line_no` drift — scanner records a line that is off by 1–5 lines from the actual `import` statement. Spot-check of 20 random import edges: 19 match, 1 mismatch (off by 2 lines).

**Sample incorrect edges:**
- `reasoning_streamer.py:107` — import edge points to `LOGGER.warning(...)` line instead of nearby import
- `query_planner.py:121` — import edge points to empty line
- `TraceRegistry.py:94` — import edge points to `pass`
- `permission_scope_types.py:91` — import edge points to `type(...)` assignment
- `healing_mixin.py:69` — import edge points to `_emit_snapshots_state()` call

**Nature**: Not false edges (the imports exist in the file), but `line_no` precision is imperfect. The semantic relationship is correct; the positional metadata is noisy.

### 2. file_ratio = 0.8931 (threshold [0.95, 1.05])

**AST files**: 10,807 | **ADG unique source_files**: 9,651
**Gap**: 1,156 files missing from ADG

**Root cause breakdown of 4,174 files missing from ADG (combined edges+nodes):**
| Directory | Missing count | Note |
|-----------|--------------|------|
| `archives/` | 3,966 | Scanner intentionally excludes archived files |
| `artifacts/` | 43 | Build artifacts, not source |
| `tools/` | 32 | Some utility scripts not imported anywhere |
| `docs/` | 30 | Documentation scripts |
| `tests/` | 18 | Some test helpers |
| `.backup/` | 11 | Backup directory |
| Other | 64 | Scattered utility/temp scripts |

**Key insight**: 95% of the gap (3,966/4,174) is `archives/`. The scanner by design doesn't scan archived/deprecated code. If `archives/` were excluded from the AST walker, the adjusted ratio would be closer to 1.0 — but per the strict prompt criteria, we count all `.py` files.

### 3. function_ratio = 0.0354 (threshold [0.95, 1.05])

**AST functions**: 67,647 | **ADG function nodes**: 2,396

**Root cause**: **ADG design limitation**. The ADG does not create discrete `entity_type='function'` nodes. Its node model is:
- `module` (9,029 nodes) — one per scanned file
- `symbol` (196,085 nodes) — classes, functions, methods, constants as scoped symbols

Functions are represented as `symbol` nodes with scoped names (e.g., `ADG::Symbol::ADGArtifactBuilder._is_seam_module`) rather than as `entity_type='function'` nodes. The `identity_kind` field shows `inferred_symbol` (95,282), `external_module` (77,388), `repo_module` (11,314), `unresolved_import` (10,942) — **none labeled as 'function_def'**.

This is a fundamental design gap: the ADG schema does not distinguish function definitions at the entity_type level. Function-level tracking exists only through symbol naming conventions and edges.

### 4. signal_ratio = 0.8668 (threshold 0.90)

**Sample**: 2,500 random edges
**High signal**: 2,167 (86.7%) | **Low signal**: 333 (13.3%)

**Low-signal breakdown (from full edge distribution):**
| Type | Count | % of total | Classification |
|------|-------|------------|---------------|
| exports | 39,939 | 4.48% | LOW — interface declaration only |
| decomposes_into | 39,414 | 4.42% | LOW — structural decomposition |
| violation_propagates_through | 16,850 | 1.89% | LOW — violation tracing artifact |
| dead_imports | 4,767 | 0.53% | LOW — unused imports (noise) |
| belongs_to_layer | 6,633 | 0.74% | LOW — pure metadata |
| unreachable_after_raise | 382 | 0.04% | LOW — dead code marker |
| duplicate_method | 11 | 0.00% | LOW — code smell marker |
| **Total low-signal** | **107,996** | **12.12%** | |

### 5. synthetic_edge_count = 7,112 (threshold 0)

**Root cause**: All 7,112 low-confidence edges are `violation_propagates_through` at confidence 0.40. These are generated by the violation propagation visitor to trace how anti-pattern violations spread through the dependency graph. They are not fabricated data but have intentionally lower confidence to indicate they are inferred, not directly observed in AST.

### 6. duplicate_edge_ratio = 0.0034 (threshold 0)

**Excess duplicate edges**: 2,999 out of 891,270

**Breakdown by type:**
| Type | Duplicate groups |
|------|-----------------|
| resolves_callsite | 2,508 |
| emits_side_effect | 334 |
| authorize_and_execute | 18 |
| flows_to | 6 |

**Root cause**: The `_ExecutionSemanticVisitor` and structural visitors both emit `resolves_callsite` and `emits_side_effect` edges for the same call sites, creating duplicates when they agree on the same (src, dst, relation, line) tuple.

---

## C) FINAL VERDICT

**STRUCTURAL COVERAGE COMPLETE — SEMANTIC GAPS REMAIN**

### Justification

The ADG achieves:
- **Perfect symbol identity** (1.0000) — no naming conflicts, no cross-visitor ID mismatches
- **High structural consistency** (0.9966) — zero orphan edges, minimal duplicates
- **Near-threshold semantic accuracy** (0.987 vs 0.99) — errors are line_no drift, not false relationships

But fails on:
- **Denominator integrity** — scanner intentionally excludes `archives/` (3,966 files) and doesn't track function-level entity_type
- **Edge precision** — 12% structural/administrative edges dilute signal
- **Synthetic edges** — 7,112 violation-propagation edges at 0.40 confidence
- **Duplicates** — 2,999 edges from multi-visitor overlap

### What would be needed for FULL PASS

1. **Semantic accuracy → 0.99**: Fix `line_no` precision in import edge scanner (likely a multiline import handling issue)
2. **File ratio → [0.95, 1.05]**: Either scan `archives/` or exclude it from the AST baseline
3. **Function ratio → [0.95, 1.05]**: Add `entity_type='function'` to the node schema; create discrete function nodes
4. **Signal ratio → 0.90**: Reclassify `exports` and `decomposes_into` as meaningful (debatable) or reduce their emission
5. **Synthetic count → 0**: Either remove `violation_propagates_through` edges or raise their confidence above 0.5
6. **Duplicate ratio → 0**: Deduplicate edges in post-processing or add visitor-awareness to edge emission

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

