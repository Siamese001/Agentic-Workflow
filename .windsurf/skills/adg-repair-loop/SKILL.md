# ADG Repair Loop Skill

## When to invoke
Use this skill BEFORE making any code edit during a scoped repair session.
This skill enforces §ADG-1 from `.windsurf/rules/adg-repair-discipline.md`.

## Pre-Edit Gate — 4-Question Litmus

Before ANY edit, answer all four questions from ADG artifacts:

### Question 1: Which ADG cluster?
```
artifact: artifacts/adg_failure_clusters.json
action:   Read top_clusters[0..N], pick highest-priority unresolved cluster
answer:   cluster root_module path (e.g. agentic_core/L0_routing/scripts/execute_ssot.py)
```

### Question 2: What is the root module?
```
artifact: artifacts/adg_semantic_graph.json
action:   Trace edges: failing_test_node → IMPORT_EDGE → root_module_node
answer:   exact file path of the definition node (where the symbol is DEFINED, not used)
```

### Question 3: Which scoped tests?
```
artifact: artifacts/adg_test_surface_map.json
action:   Look up symbol_to_tests[root_module] → extract test file paths
answer:   explicit pytest IDs for the cluster only
```

### Question 4: Blast radius justification?
```
artifact: artifacts/adg_semantic_graph.json
action:   Find edge path: test_file → IMPORT_EDGE → intermediate → IMPORT_EDGE → root_module
answer:   full import chain showing why this file is in blast radius
```

## If any question cannot be answered

**STOP. Do not edit. Rebuild ADG artifacts first:**
```
python tools/adg_semantic_builder.py --rebuild
```

## Scoped Test Command Template

After each edit, run ONLY:
```
python -m pytest <test_id_1> <test_id_2> -xvs --tb=short
```

NOT:
```
python -m pytest tests/unit   # FORBIDDEN until §7.2 scoped convergence is declared and §7.3 blast-radius verified
```

## Convergence Check

After each cluster repair cycle, verify with:
```
python -m pytest <all_cluster_test_files> -q --tb=no
```

Only when output shows `X passed, 0 failed` for ALL clusters → declare scoped convergence (§7.2), then proceed to blast-radius verification and full suite per §7.3.
