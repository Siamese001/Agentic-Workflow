# ADG Import Orphans — Accurate Scan (P2)

- **Replaces**: `scan_lazy_import_gaps.py` 188-orphan figure (artifact of top-level-only AST filter)
- **Tool**: `tools/diag/scan_adg_import_orphans.py` — queries ADG SQLite directly
- **Date**: 2026-04-22
- **Snapshot**: `adg_indexed_04222026_1218.sqlite`

## Summary

| Metric | Count |
|---|---|
| Production modules scanned (`agentic_core/` + `apps_*/`, excluding `__init__`/`__main__`) | **2,615** |
| True zero-caller (ADG `imports` fan-in == 0) | **1,684** |
| Single-caller (fan-in == 1, one edge from orphan) | 248 |

## Layer distribution of modules scanned

| Layer | Count |
|---|---|
| L0 | 82 |
| L1 | 141 |
| L2 | 185 |
| L3 | 146 |
| L4 | 130 |
| L5 | 369 |
| L6 | 81 |
| apps_shared | 254 |
| apps_rg | 152 |
| apps_lic | 120 |
| apps_underwriting_ai | 62 |
| apps_eval | 45 |
| apps_exec | 44 |
| apps_research | 40 |
| apps_rfp | 40 |

## Caveat — not all "orphans" are dead code

ADG static analysis cannot see:

1. **Dynamic imports** via `importlib.import_module(name)` where `name` is a runtime string (e.g. `rag_sovereignty.py` whitelists module names like `escalation_router`, `timeshift_router` and likely loads them dynamically).
2. **Module-level side-effect registration** (e.g. decorator-based auto-registration that only runs when the module is imported by something else).
3. **CLI entry points** launched outside the Python import graph (`python -m <module>`).
4. **Tests-only** imports — my scan scope is production only; a test that imports a module won't show here.

## Verified example — `escalation_router.py`

- ADG nodes at path: 1 (the module only, no symbol nodes extracted → module has no top-level classes/functions either)
- `imports` fan-in: 0
- Grep result: only two non-archive references, both in `rag_sovereignty*.py` as **strings** in a module-name whitelist (not imports)

This is a **true orphan under static analysis** but could still be reachable via dynamic dispatch. Without a runtime trace correlation (see follow-up below), we can't distinguish true dead code from dynamic reachability.

## P0 expected-wiring — status after correction

The 16 assertions in `config/expected_wiring.yaml` all PASS. These assertions provide a **positive** signal (call site X must exist in AST subtree Y) that complements the ADG **negative** signal (zero-caller view). They remain the durable deliverable of this plan family — independent of the RC2 retraction.

## Remaining recommendations

### Completed (this plan family)

- ✅ **C1** — enroll three semcache adapters in `_APPROVED_ADAPTER_PATHS` + `_PROCESS_BOUNDARY_ADAPTERS` (`92cc8afac1`)
- ✅ **C3** — expected-wiring SSOT + AST gate (`3ccb8e5bf8`). Gate caught `SEMANTIC_CACHE_PROMOTE_ENABLED` doc gap on first run.
- ✅ **RC2 correction** — retracted incorrect claim that lazy imports are invisible (`6282117fe9`)
- ✅ **P2** — replace inaccurate scan with ADG-direct scan (this commit)

### Still open

- **C2 (was: lazy_imports edge kind)** — **CANCELLED**. ADG already captures lazy imports. Empirically verified.
- **Dynamic-import edge kind** — the real remaining gap. Extract `importlib.import_module(...)` calls, string-literal arguments, and `__import__` calls. Emit as `relation_type="dynamic_imports"` so views can distinguish static-orphan-but-dynamically-reachable from truly-dead. Proposed but not yet implemented.
- **C4 — fact-presence gate** — for runbooks marked `LIVE`, CI runs the declared probe + asserts declared stores non-empty after integration tests.
- **C5 — runtime↔static delta gate** — cross-reference `otel_mcp` runtime spans against `expected_wiring.yaml` call sites. A declared call with zero spans over the whole test run = dormant.
- **Triaging the 1,684 orphans** — likely 70-90% are explained by dynamic imports / registration patterns. The remaining subset is dead code that should either be deleted or have callers added.

## Commit chain

| Commit | Scope |
|---|---|
| `ef0f12cf9d` | semcache wired live (6-wave plan) |
| `92cc8afac1` | RCA + C1 enrollment + C3 expected-wiring gate |
| `3ccb8e5bf8` | P0 — 12 lazy-import wirings assertions; gate extended for ImportFrom |
| `6282117fe9` | P1 — RC2 retraction (lazy imports ARE captured by ADG) |
| this commit | P2 — ADG-direct orphan scan replaces inaccurate AST scan |
