# RCA — Why the ADG Did Not Surface 5,278+ Tech-Debt Items

**Date**: 2026-04-24
**Authored**: post-tech-debt-audit, after surfacing 663 dead imports, 13 dup file pairs, 75,645 module-load `_emit_*` calls, 121 stale `__all__` entries, 66 ImportError stubs
**Status**: RESOLVED — recommendations table at end

---

## Symptom

A simple repo-wide AST + filesystem audit (`tools/analysis/tech_debt_audit.py`) found:

| Pattern | Count | ADG visibility |
|---|---:|---|
| Truly dead imports (file does not exist) | **663** | ❌ Zero violations raised |
| Namespace-package imports (no `__init__.py`) | **4,650** | ❌ Zero violations raised |
| Hash-identical duplicate file pairs | **13** | ❌ ADG has no body fingerprint |
| Module-load `_emit_*(...)` "metadata theatre" calls | **75,645 calls in 1,203 files** | ❌ ADG ingests the calls but doesn't classify them as a smell |
| Stale `__all__` entries (export name not defined) | **121** | ❌ ADG creates a placeholder export edge instead of flagging |
| `try/except ImportError: class X: pass` stubs | **66** | ❌ Captured as ordinary class nodes; no antipattern |
| Backward-compat rename shim files | **8** | ❌ No detection |

Meanwhile, the ADG's `violations` table reports **4,970** issues, of which **4,967 are exception-handling antipatterns** (broad catch / log-and-swallow / silent-swallow / return-none-swallow). The remaining **3** are SC-1 structural conformance.

**The ADG is a high-resolution exception-handling debt scanner. It is largely silent on import / structural / duplication / metadata-call debt.**

---

## Root Causes

### 1. Import edges are never validated against disk

`@c:/Git/Agentic-Workflow/agentic_core/adg/extraction/visitors/core.py:1317-1335` — the `visit_ImportFrom` handler only inspects for **star imports** (`from X import *`). It does not call `importlib.util.find_spec(module)` or check whether the resolved file exists.

Downstream pipeline observation:

- `edges` table: 152,952 import edges, **0** with `dst_id IS NULL` (no unresolved-marker convention).
- `edges.dynamic_resolution` column **exists** in the schema but is **NULL/empty** for all 152,952 import edges (slot reserved, never populated).
- 33,489 import edges point at nodes whose `resolved_path` is empty — that is the closest thing to an "unresolved" signal but it never propagates to a violation.
- Probe of the `nodes` table: only **7 module nodes** in the snapshot have a `resolved_path` that does not exist on disk (4 of them are `agentic_core/interfaces/I*Protocol.py` files that have been missing all along — never noticed). The other ~656 dead-import targets in the source code don't even produce a module node — the import edge silently maps to *some* placeholder symbol.

> **Mechanism**: An `ImportFrom` node in user code never gets cross-referenced with the filesystem. The ADG trusts that whatever the source code claims to import, exists. The 663 truly dead imports thus silently pass through.

### 2. The CI ratchet `S4_unused_imports_ratchet` looks at the wrong relation

`@c:/Git/Agentic-Workflow/ops_scripts/ci/check_unused_imports_ratchet.py:42` — the gate header docstring says "edge_kind='dead_import'" but the actual SQL filter is `WHERE e.relation_type = 'unused_import'`. The two are different concepts:

- `unused_import` — the imported name is never referenced in the importing module (8,167 edges).
- `dead_import` (does NOT exist as a relation_type) — the imported module does not exist on disk.

Result: dead imports are completely outside the ratchet. The 663 dead-import sites accumulate without bound, and the gate's own docstring describes a behavior the gate does not implement.

### 3. ADG nodes have no body fingerprint

`PRAGMA table_info(nodes)` →  `id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path, precision_type, span_start, span_end, span_line, span_column, span_end_line, span_end_column, logical_sequence_id, control_path_id, temporal_order, type_surface, enclosing_symbol`

There is no `body_hash` / `content_sha` / `normalized_body_sha` column. P4 (duplicate file detection) is structurally impossible from current ADG data. Discovered by `tools/analysis/tech_debt_audit.py` only because that scanner computed SHA-1 over normalized file bodies directly.

### 4. `exports` edges silently absorb stale `__all__` entries

41,096 `exports` edges in the snapshot. **0** have `dst_id IS NULL`. The ADG's export-edge creator must be falling back to a placeholder when an `__all__` entry refers to a name that doesn't exist in the module. P7's 121 stale entries are thus invisible — they look like normal exports.

### 5. `_emit_*` call sites are ingested but never classified

The 75,645 module-load `_emit_*(...)` calls appear in the source ADTs as `ast.Call` nodes inside `ast.Module.body` (top level). The static scanner records them as part of the lifecycle-trace contract relations (e.g. `writes_through`, `authorize_and_execute`), which is technically correct: each call IS asserting one of those relations.

But there is no rule that says *"a relation asserted at module top level, before any function definition, is suspect"*. So the ADG records 75,645 "writes_through-at-import-time" claims as legitimate edges. The CI gates downstream then trust these edges as ground truth, magnifying the problem.

### 6. The violations registry is a closed enum

The `violations.category` column has only two values populated: `antipattern` (4,967) and `SC-1` (3). The `violation_class` column has `hygiene` (4,967) and `structural_conformance` (3). The schema clearly supports more categories — but nothing in the pipeline mints them.

There is no `dead_import`, `duplicate_module`, `module_load_action_call`, `stale_export`, `import_error_fallback_stub`, or `rename_shim` category in use.

### 7. `dynamic_resolution` flag is reserved but unused

The `edges` table has a `dynamic_resolution` column. This is the perfect slot for marking imports inside `try/except ImportError` blocks (which is exactly P2's pattern). The column is **empty for all 152,952 import edges**. The W2 ImportError-stub pattern is invisible because the static scanner doesn't distinguish "import that is wrapped in defensive `try`" from "import that is not".

### 8. The `t_infra_importers` table doesn't expose import resolution status

`PRAGMA t_infra_importers` only carries (importer, importee) tuples — no resolution metadata. So even if a downstream materialized view wanted to filter for "imports that don't resolve", the upstream table cannot answer.

---

## Why this matters

The mixin work (W3) succeeded because we used **AST + filesystem checks outside the ADG**. The ADG itself would have happily told us all those imports were healthy. This means:

- Plans that follow constitutional §22 ("ADG graph layer is primary for refactoring") get a confident answer that **silently underrepresents** the scope of the cleanup.
- The "ADG wins conflicts" doctrine (§23) is undermined when the ADG simply doesn't have the data — the conflict resolution favors the side with less information.
- We're working with **a structural map that is missing one structural axis** (resolution / fingerprint / classification of module-level metadata).

---

## Proposed Enhancements

### Immediate (extraction-stage upgrades) — fix on next ADG regen

| ID | Enhancement | Effort | Detects |
|---|---|---|---|
| **A1** | In `visit_ImportFrom` and `visit_Import`, call `module_path_status(dotted)` (logic from `tech_debt_audit.py`) and write `dynamic_resolution` ∈ `{"resolved", "namespace_pkg", "missing"}` | small (1 file) | P3a, P3b |
| **A2** | Detect `try` ancestor when emitting an import edge; flag edges whose enclosing `Try` has an `ImportError`/`ModuleNotFoundError` handler. Set `edge_kind='import_error_guarded'` | small (1 visitor) | P2 |
| **A3** | Add a `body_hash TEXT` column to `nodes` (entity_type=`module`); populate with SHA-1 of normalized body (strip docstrings + comments + `_emit_*` no-ops) at extraction time. Index it. | medium (schema migration + extractor) | P4 |
| **A4** | Validate `__all__` entries at extraction time: for each name listed, walk the module AST + import set and confirm presence. Emit `relation_type='unresolved_export'` for misses | small (1 visitor) | P7 |
| **A5** | Tag any `ast.Expr` that is an `ast.Call` to a function whose name matches `_emit_*` and whose enclosing scope is `ast.Module` (not a function/method) with a new edge attribute `module_load_assertion=True` | medium | P5 |

### Violation-pipeline upgrades — promote signals to gated debt

| ID | New category | Promotion from | Severity |
|---|---|---|---|
| **B1** | `dead_import` | `imports` edges with `dynamic_resolution='missing'` | HIGH |
| **B2** | `namespace_pkg_import` | `imports` edges with `dynamic_resolution='namespace_pkg'` | LOW (advisory) |
| **B3** | `import_error_fallback_stub` | classes whose only ancestor scope is an `ImportError` handler AND whose body is `Pass` or `len(body) ≤ 2` | MEDIUM |
| **B4** | `module_duplicate` | sets of `nodes` sharing `body_hash` | HIGH (CRITICAL if both are imported live) |
| **B5** | `stale_all_export` | `unresolved_export` edges | MEDIUM |
| **B6** | `module_load_action_call` | edges with `module_load_assertion=True` whose `relation_type` is in the runtime-action set (`writes_through`, `authorize_and_execute`, `emits_metric_event`, ...) | LOW initially; HIGH once policy decision is made |
| **B7** | `rename_shim_module` | modules whose docstring matches a regex of compat-marker phrases AND whose body has only `class X(<canonical>): pass` re-exports | LOW |

### CI-gate upgrades — turn detections into ratchets

| ID | New gate | Ratchet target |
|---|---|---|
| **C1** | `S5_dead_imports_ratchet` (mirror of S4 but for `dead_import`) | 663 → 0 over N waves |
| **C2** | `S6_module_duplicate` (binary fail on any new dup pair) | block-on-add |
| **C3** | `S7_stale_all_export` | 121 → 0 |
| **C4** | `S8_import_error_fallback_stub` | 66 → 0 (matches W2 of mixin plan) |
| **C5** | `S9_namespace_pkg_import` (advisory only — no hard fail) | trend-only ratchet |
| **C6** | Fix `S4_unused_imports_ratchet` docstring drift (delete the misleading "edge_kind='dead_import'" mention OR implement what it claims) | doc fix |

### Materialized-view upgrades

| ID | New view | Purpose |
|---|---|---|
| **D1** | `mv_dead_import_hotspots` | Rank files by `count(dead_import edges)`, joined with `mv_hotspot_centrality` so layer × fan-in × resolution-failure is a single column |
| **D2** | `mv_duplicate_module_clusters` | Group `nodes` by `body_hash`; surface cluster size and per-cluster fan-in delta (which copy is more imported = the canonical) |
| **D3** | `mv_module_load_action_calls` | Fan-out by file of `module_load_assertion=True` edges; powers the P5 sweep wave |

---

## Recommendation Sequence

| Phase | Items | Risk | Notes |
|---|---|---|---|
| **R1** | A1, A2, A4, B1, B5, C1, C3, C6 | low | Extraction-stage signal additions + first two new ratchets. No schema migration required for B1/B5; they reuse existing columns by widening the `category` enum semantically. |
| **R2** | A3, B4, C2, D1, D2 | medium | Adds `body_hash` column to `nodes` — schema migration. Provides duplicate-module detection. |
| **R3** | A5, B6, B3, C4, D3 | medium | Promotes 75,645 module-load action calls into a tracked debt category. Should be paired with an architectural decision per the tech-debt findings note. |
| **R4** | B2, B7, C5 | low | Advisory-only signals. Useful for trend-watching, not gating. |

---

## References

- **Tech-debt findings**: `docs/reports/plans/tech_debt_findings.md`
- **Tech-debt JSON evidence**: `docs/reports/plans/tech_debt_audit.json`
- **Probe script**: `tools/analysis/_adg_rca_probe.py`
- **Audit script**: `tools/analysis/tech_debt_audit.py`
- **Constitutional rules cited**: §22 (graph-layer primary), §23 (canonical invariants)
- **ADG snapshot at probe time**: `artifacts/adg/adg_indexed_04242026_1935.sqlite`
- **Existing import gate (broken docstring)**: `ops_scripts/ci/check_unused_imports_ratchet.py:4`
- **Import visitor (no resolution check)**: `agentic_core/adg/extraction/visitors/core.py:1317-1335`
