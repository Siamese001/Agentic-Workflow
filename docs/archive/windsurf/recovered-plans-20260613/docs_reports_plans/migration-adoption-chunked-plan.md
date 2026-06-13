# Migration Adoption Plan — Chunked with HITL Gates
## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Source: ADG Redis hot cache 03142026_0834

All counts from live Redis snapshot. Each chunk is scoped to what one agentic
session can safely execute. Every HITL gate is a hard stop — work does not
continue until the human approves the diff.

---

## Baseline (current Redis snapshot)

| Signal                     | Count  | Target     |
|----------------------------|--------|------------|
| uses_wall_clock            | 887    | ≤ 50       |
| patches_time               | 32     | ≥ 200      |
| invokes_getattr_dynamic    | 2,993  | ≤ 500      |
| agent_executes_agent       | 2      | ≥ 100      |
| applies_guardrail          | 68     | ≥ 500      |
| records_execution_trace    | 64     | ≥ 500      |
| snapshots_state            | 1      | ≥ 20       |
| observes_runtime_state     | 3      | ≥ 50       |
| dead_imports               | 4,416  | 0          |
| antipattern                | 1,533  | ≤ 200      |

---

## Chunk 1 — Clock migration: tests/ (24 wall_clock sites)
**Risk: LOW. Tests never run in production. FrozenClock is safe everywhere.**

### What I do
- Scan `tests/` for `datetime.now(` and `time.time(`
- Classify each: logging timestamp (safe to leave), determinism-critical (migrate)
- Replace determinism-critical sites with `get_clock().now()` / `get_clock().now_epoch()`
- Add `set_clock(FrozenClock(...))` / `reset_providers()` in affected test fixtures

### HITL-1 gate (hard stop)
> **You review the diff.** Confirm:
> - No test broke its assertion logic
> - Logging timestamps left as `datetime.now()` (acceptable)
> - Only determinism-critical sites migrated

### Expected ADG delta
- `patches_time` +~15, `uses_wall_clock` -~15

---

## Chunk 2 — Clock migration: ops_scripts/ (11 wall_clock sites)
**Risk: LOW-MEDIUM. Scripts run offline; no production semantics.**

### What I do
- Same classification as Chunk 1
- Scripts that do `datetime.now()` for file timestamps: leave alone
- Scripts that do `datetime.now()` for determinism digests / replay keys: migrate

### HITL-2 gate (hard stop)
> **You review the diff.** Confirm:
> - CI scripts still produce correct output
> - Only determinism-relevant sites migrated

### Expected ADG delta
- `patches_time` +~8, `uses_wall_clock` -~8

---

## Chunk 3 — TraceContext entry-point wiring: L3 orchestrators
**Risk: MEDIUM. Wraps entry points in run_frame() — zero change to logic.**

### Scope (from Redis: 10 L3 `uses_wall_clock` nodes)
- Identify the top-5 L3 orchestrators by fan-out (most downstream calls)
- Wrap their primary `run()` / `execute()` / `orchestrate()` method in `TraceContext.run_frame(run_id)`
- No changes to internal logic — purely additive wrapper

### What I do per orchestrator
```python
# Before
def run(self, run_id: str) -> Result:
    ...

# After
def run(self, run_id: str) -> Result:
    with TraceContext.run_frame(run_id):
        ...
```

### HITL-3 gate (hard stop, one orchestrator at a time)
> **You review each orchestrator diff individually.**
> Confirm: existing tests still pass, run_frame nesting correct.

### Expected ADG delta per orchestrator
- `records_execution_trace` +dispatch_count, `signs_execution_trace` +1

---

## Chunk 4 — RunStateAuthority adoption: one L3 orchestrator
**Risk: MEDIUM. Pass-through facade — zero semantic change. One orchestrator only.**

### What I do
- Pick the smallest L3 orchestrator (fewest `reads_runtime_state` dependencies)
- Replace direct `runtime_state.json` / dict reads with `rsa.read(key)`
- Replace direct state writes with `rsa.commit(key, value)`
- Add `rsa.snapshot("checkpoint")` at end of run

### HITL-4 gate (hard stop)
> **You run the orchestrator's existing test suite.**
> Confirm: all state reads/writes produce identical results.
> Confirm: `rsa.get_stats()` shows expected commit count.

### Expected ADG delta
- `observes_runtime_state` +~5, `snapshots_state` +1

---

## Chunk 5 — AgentDispatchRegistry: top-20 getattr_dynamic sites
**Risk: MEDIUM-HIGH. Requires caller/target identification per site.**

### Scope (from Redis: 951 edge keys, 98 in L_TEST, 23 in L5)
Start with L_TEST (98 sites) — safest because test failures are visible.

### What I do
- Use ADG to identify the top-20 `invokes_getattr_dynamic` sites in `tests/`
- For each: determine `caller`, `target_class`, `method`
- Replace `getattr(obj, method_name)(...)` with `registry.dispatch(caller=..., target_instance=obj, method=method_name)`
- Register `obj` via `registry.register_instance(name, obj)` at setup

### HITL-5 gate (hard stop, batches of 5)
> **You review each batch of 5 before I continue.**
> Confirm: dispatch semantics preserved, no silent failures introduced.

### Expected ADG delta per batch of 5
- `agent_executes_agent` +5, `invokes_getattr_dynamic` -5

---

## Chunk 6 — Guardrail expansion: top-10 L2 direct call sites
**Risk: MEDIUM. Adds check() before existing calls — fail-closed only in enforce mode.**

### Scope (from Redis: 10 L2 `uses_wall_clock` nodes = high-activity L2 modules)
- Identify top-10 L2 modules by `calls` fan-out
- Add `gate.check(operation, target)` at the top of their primary execution method
- Start with `strict_mode=False` (warn only — zero behaviour change)

### HITL-6 gate (hard stop)
> **You review the guardrail placement.**
> Confirm: `strict_mode=False` on all new sites (enforce only after separate approval).
> Confirm: no exception paths changed.

### Expected ADG delta
- `applies_guardrail` +~10

---

## Chunk 7 — Dead import burndown: tests/ (L_TEST first)
**Risk: LOW. F401 removals in test files have zero production impact.**

### What I do
- Run `ruff check --select F401 tests/ --fix`
- Review auto-fix diff for false positives (re-exports, `__all__` refs)
- Commit clean

### HITL-7 gate (hard stop)
> **You scan the diff for any removed import that looks like a re-export.**
> Confirm: full test suite still collects correctly after removal.

### Expected ADG delta
- `dead_imports` -~500 (L_TEST is the largest layer)

---

## Chunk 8 — Dead import burndown: ops_scripts/
**Risk: LOW. Same pattern as Chunk 7.**

### HITL-8 gate
> Same as HITL-7, scoped to ops_scripts/.

---

## Execution Order & Dependencies

```
Chunk 1 (tests clock)
    └── HITL-1
Chunk 2 (ops clock)
    └── HITL-2
Chunk 3 (trace wiring, orchestrator 1)
    └── HITL-3a
Chunk 3 (trace wiring, orchestrator 2)
    └── HITL-3b
Chunk 4 (RSA adoption)       ← depends on Chunk 3 complete
    └── HITL-4
Chunk 5 (dispatch, batch 1)
    └── HITL-5a
Chunk 5 (dispatch, batch 2)
    └── HITL-5b
Chunk 5 (dispatch, batch 3)  ← etc.
    └── HITL-5c
Chunk 6 (guardrail L2)       ← independent, can run anytime
    └── HITL-6
Chunk 7 (dead imports tests)
    └── HITL-7
Chunk 8 (dead imports ops)
    └── HITL-8
```

---

## What Each Chunk Moves

| Chunk | Signal moved                          | Sessions | HITL stops |
|-------|---------------------------------------|----------|------------|
| 1     | uses_wall_clock -15, patches_time +15 | 1        | 1          |
| 2     | uses_wall_clock -8, patches_time +8   | 1        | 1          |
| 3     | records_execution_trace +50/orch      | 1/orch   | 1/orch     |
| 4     | observes_runtime_state +5, snapshots +1| 1       | 1          |
| 5     | agent_executes_agent +5/batch         | 1/batch  | 1/batch    |
| 6     | applies_guardrail +10                 | 1        | 1          |
| 7     | dead_imports -500                     | 1        | 1          |
| 8     | dead_imports -300                     | 1        | 1          |

---

## What is NOT in scope for agentic execution (requires human decision)

- Migrating `uses_wall_clock` in `agentic_core/` core layers (L0–L6, 103 sites)
  → Each site needs classification: production timer, TTL, audit log, or determinism
- Migrating `invokes_getattr_dynamic` in L5 (23 sites)
  → Safety plane dynamic dispatch — requires domain knowledge of each hook
- Promoting any guardrail site from `strict_mode=False` to `strict_mode=True`
  → Behaviour change — human must sign off per module
- Migrating L_APP (46 wall_clock sites across 5 apps)
  → App-level semantics vary; needs per-app owner review

---
*Plan generated: 2026-03-14 | ADG snapshot: 03142026_0834*

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

