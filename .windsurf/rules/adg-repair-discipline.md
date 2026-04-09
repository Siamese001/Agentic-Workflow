---
trigger: model_decision
---
# ADG Repair Discipline — Constitutional Rule §ADG-1

## HARD GATES — NEVER BYPASS

### §ADG-1.1 No Edit Without ADG Provenance

Before making ANY code edit during a repair session, you MUST answer all four:

1. **Which ADG cluster?** — cluster ID from `artifacts/adg_failure_clusters.json`
2. **What is the root module?** — canonical definition node from the dependency chain
3. **Which scoped tests?** — specific test IDs from `artifacts/adg_test_surface_map.json`
4. **Why is this file in the blast radius?** — edge path from semantic graph

If you cannot answer all four, the edit is **FORBIDDEN**.

### §ADG-1.2 No Full-Suite Run Before Convergence

`pytest tests/unit` is **FORBIDDEN** during scoped repair loops.

Only allowed test invocations:
```
pytest <cluster_scoped_test_files> -q    # scoped to current cluster
pytest <single_test_id> -xvs             # verifying a single fix
```

Full suite (`pytest tests/unit`) is ONLY allowed after ALL clusters are green AND scoped convergence (§7.2) is declared. See §7.3 for repair run completion conditions.

### §ADG-1.3 Fix Root Modules, Not Call Sites

When a symbol is undefined in N files:
- **FORBIDDEN**: patch each of the N call sites
- **REQUIRED**: fix the single root definition node identified by ADG dependency chain

### §ADG-1.4 No Text-Search Debugging — ADG MCP MANDATORY

**FORBIDDEN** patterns:
- `grep_search` / `find_by_name` for dependencies, imports, call-sites, or class/def discovery
- Hunting literal strings to satisfy source-text assertion tests without ADG justification
- Patching test files to fix `import pytest` or similar without tracing the dependency chain
- Using text search as fallback when ADG MCP returns an error

**REQUIRED**: Use ADG MCP tools exclusively for all dependency analysis:

| Query Need | Required MCP Tool |
|------------|-------------------|
| Trace import chain | `mcp0_adg_edge_fanout` with `relation_type=imports` |
| Find who calls a function | `mcp0_adg_edge_fanin` |
| Locate symbol definition | `mcp0_adg_node` |
| List files in a layer | `mcp0_adg_nodes_by_layer` |
| Find nodes in a file | `mcp0_adg_nodes_by_file` |

**If ADG MCP is broken:** STOP. Run `/mcp-failure-rca`. Fix the MCP. Do NOT fall back to grep.

The correct escalation when `mcp0_adg_*` fails:
```
python ops_scripts/ci/mcp_health_monitor.py --probe
Remove-Item -Recurse -Force tools/adg/core/__pycache__
# Restart ADG MCP server in Windsurf IDE
```

---

## TEST FAILURE TRIAGE (REQUIRED before repair loop)

Before entering the ADG-controlled repair loop, classify the failure using the 5-check decision tree in `docs/technical/TEST_FAILURE_decision_tree.md`:

1. Should this module exist in the architecture? → `production_bug_fix`
2. Is the import path wrong? → `stale_reference_fix`
3. Is an error supposed to happen here? → `production_bug_fix`
4. Is the test too strict about wording? → `broken_test_fix` (semantic equivalence MUST be preserved)
5. Did the architecture contract legitimately change? → `policy_regression_fix` or `production_bug_fix`; if NO → **BLOCKED** (fake module anti-pattern)

Record the repair class in the `ADG_REPAIR_LITMUS` evidence section before making any edit.

---

## ADG-CONTROLLED REPAIR LOOP

Each repair iteration MUST follow this exact sequence:

```
STEP 1: Read artifacts/adg_failure_clusters.json
        → Identify highest-priority unresolved cluster

STEP 2: Read artifacts/adg_semantic_graph.json
        → Trace dependency chain: failing_test → import_edges → root_module

STEP 3: Read artifacts/adg_test_surface_map.json
        → Extract scoped test IDs covering root module

STEP 4: Run SCOPED tests only:
        pytest <scoped_test_ids> -q
        → Observe actual failure messages

STEP 5: Fix ROOT MODULE only (definition node, not call sites)
        → Apply minimal change

STEP 6: Rerun SCOPED tests:
        pytest <scoped_test_ids> -q
        → Verify cluster is green

STEP 7: Mark cluster complete → load next cluster → repeat from STEP 1

After ALL clusters are green → verify scoped convergence (§7.2) → then proceed to
blast-radius verification and full suite per §7.3 repair run completion conditions.
```

---

## MANDATORY PRE-CONDITION (Constitutional — no bypass)

**BEFORE making ANY code edit during a repair session:**

1. **Answer all 4 litmus questions**:
   - Which ADG cluster? (cluster ID from `artifacts/adg_failure_clusters.json`)
   - What is the root module? (canonical definition node from dependency chain)
   - Which scoped tests? (specific test IDs from `artifacts/adg_test_surface_map.json`)
   - Why is this file in the blast radius? (edge path from semantic graph)

2. **Write answers to**: Evidence section titled `## ADG_REPAIR_LITMUS`

**Format required**:
```
## ADG_REPAIR_LITMUS
Cluster: <cluster_id>
Root module: <path/to/definition/file.py>
Scoped tests: <test_id_1>, <test_id_2>, ...
Blast radius: <edge_path: test → import → module>
```

**IF you cannot answer all 4 questions → STOP. The edit is FORBIDDEN.**

Only after `ADG_REPAIR_LITMUS` section is written may you make the edit.

## LITMUS TEST

Every edit must pass this check before being made:

| Question | Required Answer |
|---|---|
| Which ADG cluster? | Cluster ID (e.g. `agentic_core/L0_routing/scripts/execute_ssot.py`) |
| Root module? | Exact file path of definition node |
| Scoped tests? | Explicit test IDs, not test directories |
| Blast radius justification? | Edge path: `test → import → module` |

---

## REPAIR SCOPE GATE

| Stage | Allowed pytest scope |
|---|---|
| Scoped repair (any cluster) | `pytest <cluster_tests_only>` |
| Single-fix verification | `pytest <single_test_id> -xvs` |
| Scoped convergence check (§7.2) | `pytest <all_cluster_test_files>` |
| Blast-radius verification (§7.3 cond. 2) | `pytest <adg_reachable_dependents>` |
| Full suite (§7.3 cond. 3) | `pytest tests/unit` — ONLY after §7.2 and blast-radius are green |

---

## AUDIT TRAIL DISCIPLINE

Every repair iteration MUST record:
- **Timestamp**: ISO8601 timestamp of each edit
- **Edit location**: File path and line numbers changed
- **Rationale**: Which cluster/repair class this addresses
- **Test verification**: Scoped test run results
- **ADG snapshot**: Used for dependency tracing

Audit trail MUST be included in evidence files under `docs/reports/plans/`.
Missing audit trail = gate failure.
