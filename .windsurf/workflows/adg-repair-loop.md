---
description: ADG-controlled repair loop - strictly graph-first, no full-suite runs until convergence
---

## ADG Repair Loop — Scoped Cluster Repair

This workflow enforces §ADG-1. Invoke with `/adg-repair-loop`.

### STEP 1: Load current cluster state
// turbo
```
python -c "import json; from pathlib import Path; f = Path('artifacts/adg_failure_clusters.json'); data = json.loads(f.read_text(encoding='utf-8')); clusters = data.get('top_clusters', []); print(f'Total clusters: {len(clusters)}'); [print(f\"  [{i}] {c.get('root_module','?')} tests={len(c.get('covering_tests',[]))} risk={c.get('risk_score',0)}\") for i, c in enumerate(clusters[:10])]"
```

### STEP 2: Run scoped tests for top cluster (identify actual failures)
// turbo
```
python -m pytest <CLUSTER_TEST_FILES> --tb=short -q --no-header
```
Replace `<CLUSTER_TEST_FILES>` with the covering_tests from cluster[0].

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

### STEP 5: Verify with scoped rerun
// turbo
```
python -m pytest <SAME_CLUSTER_TEST_IDS> --tb=short -q --no-header
```

Must see: `N passed` with 0 failures before moving to next cluster.

### STEP 6: Advance to next cluster

Repeat STEPS 1-5 for next unresolved cluster.

### STEP 7: Full convergence check (after ALL clusters green)
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
