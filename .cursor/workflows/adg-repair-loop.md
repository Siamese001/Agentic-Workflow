---
description: ADG-controlled repair loop - strictly graph-first, no full-suite runs until convergence
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

## ADG Repair Loop — Scoped Cluster Repair

This workflow enforces §ADG-1. Invoke with `/adg-repair-loop`.

### STEP 0: Verify ADG Redis cache is hot and fresh
// turbo
```
python tools/adg/adg_stale_guard.py --json
```

- `"is_stale": false` + ingest_time present → cache is HOT and FRESH → continue
- `"is_stale": true` → run `/adg-redis-refresh` (STEP 2+3) before continuing
- Exit 1 (Redis unavailable) → start Redis: `redis-server` then run `/adg-redis-refresh`

### STEP 1: Load current cluster state
// turbo
```
python -c "import json; from pathlib import Path; f = Path('artifacts/adg_failure_clusters.json'); data = json.loads(f.read_text(encoding='utf-8')); clusters = data.get('top_clusters', []); print(f'Total clusters: {len(clusters)}'); [print(f\"  [{i}] {c.get('root_module','?')} tests={len(c.get('covering_tests',[]))} risk={c.get('risk_score',0)}\") for i, c in enumerate(clusters[:10])]"
```

### STEP 2: Select scoped tests via ADG (Accelerator #5) and run them

**PRIMARY source (post-P7):** when refactoring a file that appears in the top-20 of
`artifacts/adg/adg_refactor_accelerator_<ts>.json`, use the pre-computed
`candidates[i].impacted_tests` field directly — it is the same ADG-derived result
as `adg_test_selector.py` but already materialized in the per-run zip. See
`rules/adg-p7-analyst-artifacts.md` for the full routing table.

**Fallback** (file not in top-20, or no current P7 artifact): use `adg_test_selector.py`
— never manually expand test paths:
// turbo
```
python tools/adg/adg_test_selector.py --from-diff
```

This emits exact `pytest` nodeids derived from ADG `covers` edges for all files changed since HEAD. Copy the emitted command and run it:
// turbo
```
python -m pytest <EMITTED_NODEIDS> --tb=short -q --no-header
```

If the cluster root module is known (from STEP 1), target it directly:
```
python tools/adg/adg_test_selector.py <root_module_file>
```

**STOP HERE** — Read actual failure messages before editing anything.

### STEP 3: Answer 4-question litmus gate (MANDATORY before any edit)

Answer all four before proceeding:

1. **Cluster ID:** `<root_module from cluster>`
2. **Root definition node:** `<file:line where failing symbol is DEFINED>`
3. **Scoped tests:** `<explicit pytest IDs only>`
4. **Blast radius path:** `<test → import → root_module edge chain>`

If any answer is missing → rebuild ADG: `python tools/adg_semantic_builder.py --rebuild`

### STEP 4: Apply minimal fix to ROOT MODULE only

- Edit only the root definition node file
- Fix the definition, not the call sites
- No changes to test files unless the test itself has a missing import that is the root cause

### STEP 5: Refresh ADG Redis after fix, then verify staleness and type-check blast radius
// turbo
```
python tools/adg/adg_redis_ingest.py
```

Staleness guard auto-skips if sqlite is unchanged. If `generate_full_adg.py` was run as part of the fix, use `--force` instead.

**After ingest — run incremental type check over the blast radius (Accelerator #4):**
```
python tools/adg/adg_type_check.py --from-diff
```

Fix any type errors before moving to STEP 6.

### STEP 6: Verify with scoped rerun
// turbo
```
python -m pytest <SAME_CLUSTER_TEST_IDS> --tb=short -q --no-header
```

Must see: `N passed` with 0 failures before moving to next cluster.

### STEP 7: Advance to next cluster

Repeat STEPS 1-6 for next unresolved cluster.

### STEP 8: Full convergence check (after ALL clusters green)
// turbo
```
python -m pytest <ALL_CLUSTER_SCOPED_TESTS> --tb=no -q --no-header
```

Only when 0 failures → declare scoped convergence (§7.2) → proceed to blast-radius verification (§7.3 cond. 2) → then full suite (§7.3 cond. 3).

---

## Full suite validation (ONCE, after §7.2 convergence and blast-radius verified)

```
python -m pytest tests/unit --tb=short -q --no-header
```

This is the ONLY allowed `pytest tests/unit` invocation. Run exactly once after §7.3 conditions 1–2 are satisfied.

---

## Forbidden actions during scoped repair

- `pytest tests/unit` — full suite before convergence
- Editing files not in blast radius of current cluster
- Fixing call sites instead of definition nodes
- Grep-based triage without ADG artifact backing

---

## P0 remediation — fail-closed by design (no auto-fix)

When `python tools/generate_full_adg.py` halts with `P0 two-pass runner BLOCKED`,
the pipeline emits `artifacts/adg/issues/p0_remediation_wave_plan_<ts>.md`.

**The plan is the remediation path. There is no auto-burndown script.**

Rationale (RCA 2026-04-24, see `tools/archive/phase3_orphan_w6/README.md`):

- Every P0 class (`infra_wiring`, `write_sovereignty`, `capability_egress`,
  `critical_path_integrity`, `authority_boundary`, `dynamic_exec`) requires a
  design decision a mechanical rewriter cannot make.
- Historical false-positive rate on mechanical burndown of swallow-class
  defects: ~87% against doctrinally-valid best-effort patterns
  (`docs/reports/plans/p1-guardian-burndown-final-04202026.md`).
- Auto-fix would violate constitutional §6 (Author-Gate), §8 (guardian
  exemptions), §23 (ADG canonical invariants — "fix the graph, not your
  analysis").

### P0 remediation loop

1. Read the wave plan. P0 is fail-closed, so there is exactly one file.
2. For the top-ranked item: consult ADG (`adg_edge_fanin`, `adg_nodes_by_file`,
   `mv_*` views) to understand the design constraint being violated.
3. Apply the targeted fix — adapter routing, layer relocation, chokepoint
   alignment, or (rare) guardian exemption with Author-Gate justification.
4. Rerun `python tools/generate_full_adg.py`. The regen either confirms the
   fix or surfaces the next P0.
5. Repeat. P0 budget is always 0 — no ratchet, no ceiling.

### Do NOT

- Wire the archived `phase3_auto_remediation.py` back in. It is permanently
  retired.
- Hand-assign P-bands on deferred items. Use `DEFERRED_SCOPE:` markers and let
  `tools/priority/deferred_scope_scorer.py` compute P1..P5.
- Demote a P0 gate to reporting-only without Author-Gate approval.
