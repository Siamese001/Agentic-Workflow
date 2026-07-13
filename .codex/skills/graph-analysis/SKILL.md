---
name: graph-analysis
description: Use this skill when answering dependency, import, consumer, reference, blast-radius, layer, dataflow, side-effect, or duplicate-symbol questions and when selecting graph-backed scope for a multi-file change.
metadata:
  owner: platform-team
  version: "2.0"
---

# Graph analysis

Use the ADG read path for structural relationships. Literal text search remains appropriate for
comments, TODOs, configuration strings, and non-structural text; it is not evidence for dependency or
blast-radius claims.

## Routing

| Question | Primary evidence |
|---|---|
| Imports, consumers, fan-in, fan-out, blast radius | ADG nodes plus incoming/outgoing edges |
| Layer membership or inversion | ADG layer views and violation views |
| Runtime dataflow, reads, writes, side effects | ADG semantic edges |
| Hotspots, chokepoints, refactor order | Materialized graph views and ranked artifacts |
| Exact comment, TODO, or configuration string | Literal search |
| Conceptual similarity | Vector search, with the semantic limitation stated |
| Runtime traces or observed execution | OTel/runtime evidence, not static ADG alone |

Read [tool_routing_decision_tree.md](tool_routing_decision_tree.md) before selecting a fallback.

## Workflow

1. Establish ADG snapshot and transport health. Record the snapshot or backend provenance.
2. Resolve the target file to both its module node and exported symbol nodes.
3. Query fan-in and fan-out for the module and relevant symbols; merge and deduplicate results.
4. For architectural or refactor work, inspect materialized views and semantic edges before raw edge
   tables. Read [graph_construction_standards.md](graph_construction_standards.md) for edge semantics.
5. Determine upstream, downstream, boundary, cycle, side-effect, and test impacts.
6. Declare the exact change scope and explain the graph path that brings each file into scope. Use
   [impact_analysis_template.md](impact_analysis_template.md) for T2/T3 work.
7. Re-query affected nodes after the edit and run graph-backed test selection.

## Module-to-symbol expansion

A module-level fan-in can miss callers that import a specific exported symbol. After resolving a file,
query the module node and every public symbol node relevant to the change. Skip symbol expansion only
when the file has no public API and record that reason.

## Failure handling

- Do not silently substitute grep for structural evidence.
- If the current ADG route is unavailable, stop graph-dependent edits or enter an explicitly named
  recovery/diagnostic path.
- State whether a result came from the canonical SQLite snapshot, a validated hot projection, or an
  explicit degraded diagnostic route.
- Treat extractor limitations as unresolved until a targeted counterexample proves them.

## Duplicate prevention

Before creating a new agent, orchestrator, registry, adapter, or utility:

1. Search symbols and name stems in ADG.
2. Compare behavioral edges, inputs, outputs, and side effects.
3. Check registries and factories.
4. Reuse or extend an existing implementation when the capability already exists.

Read [duplicate_prevention_protocol.md](duplicate_prevention_protocol.md) for the evidence format and
[scope_validation_checklist.md](scope_validation_checklist.md) before editing.

## Validation

```bash
python ops_scripts/ci/check_graph_layer_evidence.py
python ops_scripts/ci/run_contract_gates.py
```

Use [fail_closed_discipline.md](fail_closed_discipline.md) when parsing or transport health fails.
