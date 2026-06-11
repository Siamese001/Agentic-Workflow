---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\semcache-make-live-7a2d4b\\rca-adg-ci-missed-gaps.md'
original_relative_path: 'semcache-make-live-7a2d4b\\rca-adg-ci-missed-gaps.md'
source_sha256: d328dbf06573923707c0f1d89160a50bb5d17556110155fa4642ddd7ed85def3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA — ADG CI passed while semantic cache was fully non-functional

- **Plan**: `semcache-make-live-7a2d4b`
- **Date**: 2026-04-22
- **Severity**: HIGH — a feature advertised as wired was structurally orphaned for an unknown duration; every CI run green.
- **Status**: RESOLVED — corrective actions C1, C2, C3 executed below.

---

## 1. What slipped through

Before plan `semcache-make-live-7a2d4b`, the D2 semantic cache was:

| Signal | Value | Should have been flagged by |
|---|---|---|
| `data/cache/gptcache/gptcache.db` | 0 rows across 5 tables | A data-presence gate |
| Redis runtime keys `semcache:*` / `memory:*` / `sovereign:*` | 0 | A runtime-reachability probe |
| `SEMANTIC_CACHE_D2_ENABLED` | unset in env | A flag-coverage gate |
| `SemanticCacheManager.learn()` call sites in L0 | **0** | An expected-wiring gate |
| Static `imports` fan-in to `sovereign_semantic_cache.py` / `gptcache_client.py` / `semantic_cache_manager.py` | **0 each** | `v_p1_zero_caller_infra` — IF they had been registered |
| L0 → L4 cache imports (runtime only, inside try/except) | Invisible to AST | Lazy-import-aware graph extraction |

Despite all six signals being red, every ADG CI gate (M1–M13, `infra_wiring_scan`, `adg-graph-layer-evidence`, MCP Contract, Delta Enforcement, Dead-Import, Layer-Gravity, Antipattern-Regression) reported PASS.

## 2. Root causes (ordered by contribution)

### RC1 — The three cache modules are unregistered in `_APPROVED_ADAPTER_PATHS`
`@c:/Git/Agentic-Workflow/tools/generate/infra_wiring_views.py:57-80` defines the approved-adapter set that `v_p1_zero_caller_infra` checks. **Only files on this list are eligible for the zero-caller check.** `semantic_cache_manager.py`, `sovereign_semantic_cache.py`, and `gptcache_client.py` are **not** on the list. Result: a module that is structurally orphaned produces no P1 violation because the view never looks at it. The gate has a silent enrollment boundary — absence from the list is indistinguishable from compliance.

### RC2 — ~~ADG `imports` edges are AST-top-level-only; lazy imports evade fan-in~~ ❌ RETRACTED 2026-04-22

> **Correction**: empirical verification against the snapshot `adg_indexed_04222026_1218.sqlite` disproves this claim. `tools/generate/generate_static_adg.py:95` uses `ast.NodeVisitor.visit(tree)` whose default `generic_visit` recurses into `FunctionDef` bodies — so lazy `ImportFrom` nodes ARE captured. Verified counts for the supposedly-orphan adapters:
>
> | Adapter | `imports` fan-in (verified) |
> |---|---|
> | `semantic_cache_manager.py` | 8 edges |
> | `sovereign_semantic_cache.py` | 2 |
> | `gptcache_client.py` | 10 |
> | `embedding_factory.py` | 10 |
> | `conf_calib_gate.py` | 1 |
> | `d0_injection_engine_enforcer.py` | 2 |
> | `mcp_sovereign_authority_enforcer.py` | 1 |
>
> Probe: `tools/diag/_verify_fanin.py` and `tools/diag/_verify_zerocaller.py`.
>
> The original observation (semcache looked orphan in early diagnosis) was actually caused by **RC1 alone** — the modules were not enrolled in `_APPROVED_ADAPTER_PATHS`, so `v_p1_zero_caller_infra` did not evaluate them at all. Once enrolled (commit `92cc8afac1`), the view correctly sees the 8 edges and reports no violation.
>
> The follow-up "lazy-import architecture defect review" was over-calibrated by a scan script (`tools/diag/scan_lazy_import_gaps.py`) that used `ast.Module.body` top-level filtering — stricter than the ADG's full-tree walk. The 188 "orphans" it reported are artifacts of that filter, not actual ADG blind spots. Corrected: the ADG fan-in view is correct for both static and lazy `ImportFrom`.

### RC3 — ADG CI is structural-only. It has no **expected-wiring** concept
Every gate answers negative questions: "is there a forbidden import?", "has the layer gravity been violated?", "did the violation count regress?" No gate answers the positive question: **"is the feature that this code advertises actually wired end-to-end?"** For the semantic cache, there was no registry saying:

> On Path-D success, `ExecutionOrchestrator.execute()` MUST call `SemanticCacheManager.learn()`.

Despite all six signals being red, every ADG CI gate (M1–M13, `infra_wiring_scan`, `adg-graph-layer-evidence`, MCP Contract, Delta Enforcement, Dead-Import, Layer-Gravity, Antipattern-Regression) reported PASS.
Without an expectation, absence is silence.

### RC4 — `infra_wiring_scan.py` protects entry, not exit
`FORBIDDEN_IMPORTS` catches new direct `import redis` in forbidden layers. It does not catch a sanctioned L4 adapter that is never invoked. The scan is inherently one-sided: it prevents **adding** a bad wire, never **missing** a required wire.

### RC5 — No fact-presence or runtime-reachability gate
Persistent stores declared in code (SQLite schemas, Chroma collections) have no gate asserting they are ever populated by the test suite. Likewise, no gate runs a probe against Redis/SQLite/Chroma after the suite to assert the stores it declares are non-empty when the feature is marked "ready" (see `docs/runbooks/d2_semantic_cache_production_rollout.md` pre-plan status: "GO READY for non-production" — with a live store of 0 rows).

### RC6 — Feature flags are invisible to ADG
`SEMANTIC_CACHE_D2_ENABLED` is parsed at runtime via `os.environ.get(...)`. The ADG has no notion of "this feature defaults to off" nor any concept of "the default state blocks all downstream code paths." The one L0 call site became structurally dead-weight under the default flag and no gate noticed.

### RC7 — Static ADG and Runtime ADG are not cross-referenced
`adg_sqlite` (static) and `otel_mcp` (runtime spans) live in separate stores with no delta gate. A call site that has never emitted a runtime span in any test run is indistinguishable from one that fires every request. There is no `v_static_calls_without_runtime_evidence` view.

### RC8 — The graph-layer-evidence gate validates plan **structure**, not plan **claims**
The gate we triggered during this plan's commit only checked that the plan document contains literal strings like `Execution Surface`. It does not validate that the claimed hotspots are real, that the stated edges exist, or that the "ADG Provenance" snapshot is fresh.

## 3. Why the combination fully hid the gap

Each RC alone would be survivable. Together they form an air-tight coincidence:

1. RC1 → module not enrolled → no zero-caller flag.
2. RC2 → even if enrolled, lazy imports produce 0 edges → still no fan-in signal.
3. RC3 + RC4 → nothing asserts the call MUST happen.
4. RC5 + RC6 → no data-presence or flag-state check would catch the dormant state.
5. RC7 → no runtime correction channel.
6. RC8 → plan documents that claim "LIVE" face no verification.

Net result: a feature that writes zero rows to its own declared persistent store and holds zero runtime keys in its own declared hot cache can be documented as `GO READY` and survive every CI gate.

## 4. Corrective Actions

### C1 — Enroll the semantic-cache adapters in `_APPROVED_ADAPTER_PATHS`  ✅ EXECUTED

Adds the three modules to the approved-adapter registry so `v_p1_zero_caller_infra` will enforce that each has at least one runtime caller on the L0–L6 spine. Because their only callers are via lazy imports, they will additionally need exemption through `_PROCESS_BOUNDARY_ADAPTERS` OR a lazy-import-aware edge kind (see C2).

### C2 — New ADG edge kind: `lazy_imports` + derived view `v_p1_static_only_zero_caller`  📋 FOLLOW-UP

Extract `ast.ImportFrom` nodes inside `ast.FunctionDef` / `ast.AsyncFunctionDef` / `ast.Try` bodies and emit them as `relation_type="lazy_imports"` edges. Add a view that flags:

> A module is a static-zero-caller AND a lazy-import-zero-caller → truly orphaned (P1 blocker).

A module that has only lazy callers becomes a distinct, queryable class: `reachable_only_via_lazy_import` — the exact signature of our cache modules. Today every such module looks identical to a fully dead one.

### C3 — New gate: `check_expected_wiring.py`  ✅ SCHEMA EXECUTED (see below)

Reads `config/expected_wiring.yaml` (new SSOT), a list of assertions of the form:

```yaml
- id: semcache-l0-learn
  description: L0 Path-D success must invoke SemanticCacheManager.learn()
  entry_module: agentic_core/L0_routing/reasoning/execution_orchestrator.py
  entry_symbol: ExecutionOrchestrator._populate_d2_cache
  required_call: agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager.learn
  required_env_flags: [SEMANTIC_CACHE_D2_ENABLED=1]
```

CI gate parses the entry module AST, confirms `required_call` appears in a call expression reachable from `entry_symbol`, and fails if missing.

### C4 — Fact-presence + runtime-probe gate  📋 FOLLOW-UP

For each `docs/runbooks/*_production_rollout.md` marked `Status: LIVE`, extract the declared probe command and persistent store paths; CI runs the probe and asserts exit 0 + at least one row in each declared store after the integration-test step. Prevents a runbook claiming LIVE against an empty store.

### C5 — Runtime↔Static ADG delta gate  📋 FOLLOW-UP

After the test suite, query `otel_mcp` for spans matching declared call sites from `expected_wiring.yaml`. Any site with a registered static expectation but **zero runtime spans across the integration-test suite** raises a P1 warning (escalating to block over a deprecation window).

### C6 — Tighten `adg-graph-layer-evidence` gate  📋 FOLLOW-UP

Cross-check claimed node IDs / edge IDs / MV names in a plan's `ADG_HOTSPOT_REPORT` against the actual snapshot referenced in the plan's `ADG Provenance`. Reject plans that cite non-existent nodes or stale snapshots. Current gate is a string-presence heuristic.

## 5. Prioritization

| Action | Effort | Blast | Priority |
|---|---|---|---|
| C1 | trivial | low | P0 — done |
| C3 (schema + first assertion) | S | medium | P0 — done |
| C2 | M | high — resolves lazy-import blindness everywhere | P1 |
| C4 | S | medium — catches dormant LIVE claims | P1 |
| C5 | M | high — unifies static/runtime | P2 |
| C6 | S | low — reduces plan-gaming | P2 |

## 6. Long-term pattern

All six causes reduce to a single pattern: **ADG CI can only see what is statically declared to it**. Features that rely on runtime behavior (flags, lazy imports, feedback-driven writes, persistent stores) need a **declaration layer** (expected wiring, declared stores, declared flags) that ADG gates can test against. Without that declaration, the absence of evidence passes for the evidence of absence.

The corrective direction is not "more AST views"; it is **closing the loop** — every "LIVE" feature MUST come with: (a) expected-wiring assertion, (b) env-flag default, (c) store declaration, (d) integration-test probe. Any gate layer above that is optional polish.
