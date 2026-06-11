---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_scanner_integrity_audit.md'
original_relative_path: 'adg_scanner_integrity_audit.md'
source_sha256: fbca18505b34ef47eb7959c62c2df6b0b3b22d2dbaa99655e5148a99430754ed
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Scanner Integrity Audit Report

**Date:** 2026-03-24
**ADG:** `adg_indexed_03242026_1352.sqlite` -- 941,972 edges, 9,015 nodes
**Audit script:** `tools/adg_scanner_audit.py`
**Raw output:** `tools/adg_scanner_audit_output.txt`

---

## A) METRICS TABLE

| Metric                        | Value        | Pass/Fail |
|-------------------------------|-------------|-----------|
| `synthetic_edge_ratio`        | **0.056146** (52,888 / 941,972) | **FAIL** -- 5.6% synthetic, not labeled/excluded |
| `semantic_digest_sensitivity` | **SENSITIVE** | **PASS** -- structural vs full digest differ |
| `symbol_alignment_rate`       | **0.999950** (20 fragmented / 398,188) | **PASS** -- >= 0.99 |
| `duplicate_edge_ratio`        | **0.320138** (301,561 excess / 941,972) | **FAIL** -- 32% duplicates |
| `denominator_accuracy`        | **PARTIAL** -- see findings | **WARN** -- denominators shifted vs locked baseline |
| `ast_location_rate`           | **0.914983** (861,888 / 941,972 have line > 1) | **WARN** -- 8.5% have line 0 or 1 |
| `semantic_accuracy`           | **1.000000** (10/10 flows_to AST-verified) | **PASS** |
| `self_generated_edge_ratio`   | **0.000115** (108 / 941,972) | **PASS** -- negligible |

---

## B) ROOT CAUSE FINDINGS

### B1. `_P1608HardeningVisitor` emits 100% synthetic edges (CRITICAL)

**Location:** `agentic_core/adg/extraction/static_scanner.py` lines 640-814

**Mechanism:** Every edge is emitted in `__init__()` with hardcoded `line_no=1` and hardcoded `symbol=<relation_type_name>`. The visitor has no `visit_Call`, `visit_FunctionDef`, or any AST-inspecting method. Its `visit()` override just calls `super().visit(node)` which is a no-op since no visit methods are defined.

**Evidence:**
- 12 relation types are emitted per module, unconditionally
- All 52,888 synthetic edges have `line_no=1` and `symbol == relation_type`
- 6 types are 100% synthetic: `mutation_signature`, `parent_snapshot_hash`, `gates_promotion`, `links_to_execution_trace`, `detects_regression`, `records_validation_outcome`
- Test-file edges (8 types for files matching `test_` or `tests/`) are also 100% synthetic -- they don't inspect AST for actual test functions

**Impact:** 52,888 edges (5.6% of ADG) have zero AST provenance.

**Gap contamination:** `dispatches_execution_plan` -- 6,622 of 6,625 total edges (99.95%) are P1608 synthetic. Only 3 are from real AST-backed P1OrchestrationGovernanceVisitor. This directly inflates the `dispatches_execution_plan` gap closure numerator.

### B2. Massive duplicate edge generation (HIGH)

**Location:** Multiple visitors emitting edges for the same (src, dst, relation, kind) tuple.

**Evidence:**
- 113,176 duplicate groups
- 301,561 excess duplicate edges (32% of total)
- Worst case: `reads_from/type_annotation` -- 380 duplicate edges for a single (src, dst) pair
- `emits_side_effect/execution` -- up to 206 duplicates per pair
- `controls_flow/execution` -- up to 145 duplicates per pair

**Root cause:** The `_ExecutionSemanticVisitor` walks all statements in every function and emits edges per-occurrence. If a function calls `list.append()` 380 times targeting the same symbol node, 380 identical edges are produced. No deduplication pass exists.

**Impact:** 301,561 edges (32%) are pure duplicates. The actual unique edge count is approximately 640,411 not 941,972.

### B3. Denominator drift from locked baseline (MEDIUM)

**Evidence (current vs locked baseline from memory):**

| Denominator | Locked Baseline | Current | Delta |
|---|---|---|---|
| `writes_to` | 5,102 | 5,612 | +510 (+10.0%) |
| `reads_from` | 72,660 | 77,084 | +4,424 (+6.1%) |
| `records_execution_trace` | 115 | 331 | +216 (+187.8%) |
| `calls` | 19,609 | 20,622 | +1,013 (+5.2%) |
| `applies_guardrail` | 173 | 173 | +0 (stable) |

`records_execution_trace` has nearly tripled from locked baseline (115 -> 331). This requires investigation -- either new modules genuinely using execution trace classes, or denominator contamination re-introduced.

### B4. ~76% of edges lack span enrichment (LOW)

**Evidence:**
- `semantic_type`: 100% populated (OK)
- `source_span_line`: 35.2% populated (non-zero)
- `source_span_column`: 23.9% populated
- `target_span_line/column`: 23.9% populated
- `dynamic_resolution`: 23.9% populated

Only the `_ExecutionSemanticVisitor` populates span fields. All other visitors emit edges with span fields defaulting to 0. This is not a correctness issue but reduces the value of span data for consumers.

### B5. Line-1 / Line-0 edges (MEDIUM)

**Evidence:**
- 56,625 edges at `line_no=1` (6.0%) -- nearly all are P1608 synthetic + some legitimate `imports`
- 23,459 edges at `line_no=0` (2.5%) -- `violation_propagates_through` (16,837) and `belongs_to_layer` (6,622)

Breakdown of line_no=1 excluding legitimate imports (3,698):
- **52,888 are P1608 synthetic** (identified in B1)
- **39 are dead_imports/violates/covers** (legitimate scanner outputs for module-level constructs)

---

## C) IMPACT ON 13-GAP CLAIM

### Original 13 Gaps (P0-P4 coverage dimensions)

| # | Gap / Edge Type | Verdict | Evidence |
|---|---|---|---|
| 1 | `records_execution_trace` | **VALID** | 331 edges from AST-backed `_GovernancePlaneVisitor` matching `EXECUTION_TRACE_CLASSES`. Denominator drifted but edges are real. |
| 2 | `applies_guardrail` | **VALID** | 173 edges, denominator stable. All from AST-backed visitors matching `GUARDRAIL_CLASS_NAMES`. |
| 3 | `reads_policy_state` | **VALID** | AST-backed via `_GovernancePlaneVisitor`. |
| 4 | `emits_replay_key` | **VALID** | AST-backed via governance visitor. |
| 5 | `emits_determinism_digest` | **VALID** | AST-backed via governance visitor. |
| 6 | `signs_execution_trace` | **VALID** | AST-backed via governance visitor. |
| 7 | `snapshots_state` | **VALID** | AST-backed via governance visitor. |
| 8 | `routes_to_agent` | **VALID** | AST-backed via `_P1OrchestrationGovernanceVisitor`. |
| 9 | `orchestrates_workflow` | **VALID** | AST-backed via P1 visitor. |
| 10 | `dispatches_execution_plan` | **INVALID (INFLATED)** | 6,622/6,625 edges (99.95%) are P1608 synthetic. Only 3 edges are real AST-backed. Gap closure claim is false. |
| 11 | `validates_agent_capability` | **VALID** | AST-backed via P1 visitor. |
| 12 | `checks_agent_registry` | **VALID** | AST-backed via P1 visitor. |
| 13 | P2/P3/P4 batch-wired edges | **PARTIALLY VALID** | Edges exist via batch-wired `_emit_*` calls in source files. These ARE in the AST (real function calls at module level), so they are structurally AST-derived. However, they represent instrumentation signals, not organic code structure. The scanner's `_CallVisitor` and `_GovernancePlaneVisitor` explicitly suppress `_emit_*` calls, so these only appear if gap-plane visitors' frozensets include `_emit_*` symbols. Coverage is instrumentation-complete, not organically-complete. |

**Summary: 11/13 VALID, 1/13 INVALID, 1/13 PARTIALLY VALID**

---

## D) FINAL VERDICT (STRICT)

### **"ADG SCANNER INFLATES METRICS -- PARTIAL CLOSURE ONLY"**

**Justification:**

1. **5.6% of all edges are 100% synthetic** (zero AST backing) from `_P1608HardeningVisitor`. This visitor injects edges in `__init__()` without inspecting any AST node. These edges are not labeled as synthetic and are not excluded from metrics.

2. **32% of all edges are duplicates** (301,561 excess). No deduplication pass exists. This inflates edge counts by ~47% over unique edges.

3. **`dispatches_execution_plan` gap is INVALID** -- 99.95% of its edges are P1608 synthetic. The gap closure claim for this dimension is false.

4. **Denominator drift** -- `records_execution_trace` nearly tripled from locked baseline without documented justification.

5. **P2/P3/P4 batch-wired coverage is instrumentation-complete, not organically-complete** -- edges come from `_emit_*()` calls injected into 3,011 modules, not from organic code patterns.

**What IS trustworthy:**
- Core structural edges (`calls`, `imports`, `reads_from`, `writes_to`, `exports`) are AST-backed with real line numbers
- Semantic enrichment edges (`flows_to`, `controls_flow`, `emits_side_effect`) are 100% AST-backed with verified accuracy
- Symbol identity is consistent (99.995% alignment)
- Determinism digest is sensitive to semantic field changes
- Scanner self-instrumentation is negligible (0.01%)
- 11 of 13 gap dimensions have legitimate AST-backed edges

**Required remediation:**
1. Label or exclude `_P1608HardeningVisitor` edges from gap closure metrics
2. Add edge deduplication pass (or deduplicate at query time)
3. Investigate `records_execution_trace` denominator drift
4. Document that P2/P3/P4 coverage is instrumentation-based, not organic

---

*Audit completed 2026-03-24. All findings are falsifiable and reproducible via `tools/adg_scanner_audit.py`.*

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

