# ADR-075 — Split Runtime Telemetry from Static ADG Edge Declarations

**Status:** Accepted (skeleton implemented; migration tracked separately)
**Date:** 2026-04-30
**Deciders:** apps_* owners, ADG layer owner
**Source plan:** `.codex/plans/apps-svp-plus-hardening-7c4e3a.md` (W4.2)
**Related:** ADR-050 (intelligence ledger family), constitutional §22 (graph-layer primary driver)

**Current-state note (2026-06-15):** Runtime trace, RAG semconv, ADG ingest primitives, `runtime_telemetry_decorators.py`, and the decorator unit tests exist. The broad `_emit_*` call-site migration is successor-plan scope outside this skeleton ADR.

---

## Context

The platform has 2,482 `emits_side_effect` ADG edges across `apps_*` (per the
04292026_1606 ADG snapshot). These edges are produced by the AST walker
scanning calls to `_emit_*` functions in
`agentic_core.runtime.contracts.lifecycle_trace_contract` — e.g.:

```python
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_emits_side_effect,
)

def write_decision_to_ledger(...):
    _emit_emits_side_effect("decision_packet_write")
    # ... actual write
```

The AST walker treats every call site of `_emit_emits_side_effect` as a static
ADG edge declaration. The runtime simultaneously emits an OTEL span using the
same function call. **The same line of code carries two responsibilities** —
static ADG edge declaration AND runtime telemetry emission.

### Problems

1. **Refactoring risk.** Moving telemetry to async batching, OTEL exporters,
   structured logging, or a different observability stack would require
   touching every one of the 2,482 sites because the static-edge declaration
   is fused to the runtime emit.

2. **Coverage gaps surface as edge gaps.** A function that should emit
   `emits_side_effect` but doesn't (because the dev forgot the `_emit_*` call)
   produces no ADG edge. There's no way to declare "this function is supposed
   to emit X" without producing the runtime emission too.

3. **Test isolation pain.** Unit tests of side-effect functions either
   (a) emit telemetry, polluting test telemetry; (b) monkey-patch `_emit_*`
   per test, brittle; (c) skip the assertion entirely.

4. **No introspection.** Given a function reference, there is no way to ask
   "what side effects does this function declare?" without re-parsing the
   source. Static intent is invisible to the runtime.

## Decision

Introduce a **declarative decorator** in
`agentic_core/runtime/contracts/runtime_telemetry_decorators.py`:

```python
@emits_side_effect("decision_packet_write")
def write_decision_to_ledger(...):
    # ... actual write
```

The decorator:

- **Is statically introspectable** — the AST walker can read the decorator
  argument to produce an ADG edge WITHOUT any runtime call to `_emit_*`. The
  edge declaration is the decorator argument, period.
- **Stores intent on the function object** —
  `func.__adg_side_effects__ = ("decision_packet_write",)`. Any code with a
  reference to the function can ask what it declares.
- **Wraps with runtime emission** by default — the decorator returns a
  wrapper that calls the existing OTEL emit functions. Same runtime behavior
  as today.
- **Allows runtime suppression for tests** — `EMITS_SUPPRESS=1` env var
  short-circuits the wrapper to no-op runtime emission while preserving
  the static declaration. Closes the test-isolation gap.

### Layered separation (this is the point)

| Concern | Where it lives | When it runs |
|---|---|---|
| Static declaration ("this function emits X") | Decorator argument | At parse / AST scan |
| Runtime emission ("emit OTEL span Y") | Wrapper body | At call time |
| Test-mode suppression | Env var read in wrapper | At call time |

The AST walker reads the decorator argument directly — no runtime call
needed for static-edge production.

## Consequences

### Positive
- **2,482 sites become editable as a unit.** Telemetry stack swap = update
  the wrapper; no site-by-site rewrite.
- **Static intent is queryable at runtime** via `__adg_side_effects__`.
- **Test isolation** via `EMITS_SUPPRESS=1` (no monkey-patch).
- **Coverage gap detection** — the AST walker can flag functions that
  *should* declare side effects (per heuristics) but don't carry the
  decorator.

### Negative
- **Migration is non-trivial.** 2,482 call sites need to convert
  `_emit_emits_side_effect("X")` (inside the function body) to
  `@emits_side_effect("X")` (on the function definition). This is mechanical
  for direct cases but requires manual review where:
  - The emit is conditional (`if x: _emit_*(...)`).
  - The emit is not at the top of the function.
  - The emit kind depends on a runtime parameter.

  These cases keep the inline pattern; only the unconditional, top-of-function,
  static-kind pattern migrates.

- **AST walker requires update.** The walker currently reads call sites; it
  must additionally read decorators with the new shape and emit edges from
  the decorator arguments. (Same edge kind in the ADG; only the source-of-
  truth changes.)

### Neutral
- **Performance.** Decorator overhead is one function-call per decorated call.
  Negligible vs. an OTEL span.

## Migration Plan (successor scope)

This ADR ships the **decorator + tests + AST-walker contract spec**. The
mechanical migration of all 2,482 sites is intentionally owned by a separate
successor plan so it can get its own Author-Gate decision and per-app rollout
evidence.

Phases for the migration (to be tracked in
`apps-telemetry-adg-split-rollout-<6hex>` plan when authored):

1. **Phase 1 — Inventory.** ADG-driven census of all `_emit_*` call sites,
   grouped by static / conditional / dynamic.
2. **Phase 2 — AST walker dual-read.** Walker reads BOTH inline `_emit_*`
   calls AND the new `@emits_side_effect` decorator; produces edges from
   either source. Live with both during migration.
3. **Phase 3 — Migrate static cases per app** (apps_eval first as the
   smallest, lowest-risk surface). Per-app PR. CI gate confirms ADG edge
   count is preserved (zero regression).
4. **Phase 4 — Audit conditional cases.** For non-static `_emit_*` calls,
   document why they must remain inline in the source; ADD a decorator
   carrying `dynamic=True` so the static edge is declared even when the
   runtime call is conditional.
5. **Phase 5 — Walker dropouts.** Once all sites migrated, walker stops
   reading inline `_emit_*` calls. Inline pattern remains valid for
   genuinely-dynamic emits but they MUST also carry the decorator.

## Author-Gate

**Triggering Author-Gate decision** when migration starts:
`type=architecture_choice, repo_area=apps_*+agentic_core/runtime`. Bands to
surface:
- Big-bang vs. per-app migration
- Walker dual-read vs. atomic switchover
- Decorator-only vs. decorator+inline (allowed both)

Not at this ADR — those decisions live in the migration plan.

## Skeleton (this PR)

| File | Purpose |
|---|---|
| `agentic_core/runtime/contracts/runtime_telemetry_decorators.py` | The decorator + introspection helpers |
| `tests/unit/runtime/contracts/test_runtime_telemetry_decorators.py` | Decorator behavior + introspection contract |
| `docs/architecture/adr/ADR-075-split-runtime-telemetry-from-adg-edges.md` | This file |

The skeleton is **production-ready**. It lands as a new SUPPLEMENTAL way to
declare emits — existing inline `_emit_*` calls keep working unchanged.
Migration itself is a separate plan with its own Author-Gate.

## Constitutional Tie-In

- §22 (graph-layer primary driver) — the AST walker continues to read
  edges into the same `mv_*` views; only the SOURCE of the edge changes.
- §28 (SQLite-direct fallback) — unchanged.
- §29 (closed-loop router evidence) — unaffected; routers do not use this
  decorator. They use `tools.ledgers.hook_helpers.emit_ledger_event`.

## Out of Scope

- Migrating `_emit_*` callers to the decorator — separate plan.
- Updating the AST walker — separate plan, after ADR is accepted.
- Replacing OTEL with another backend — explicitly out of scope; the
  decorator is OTEL-stack-agnostic but the wrapper currently uses OTEL.
