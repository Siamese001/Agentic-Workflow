# Dep Graph DB + __all__ Shims + CI Regression Gate

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Items 2-4 from ranking table:
- Item 2: NetworkX+SQLite persistent import graph (tools/dep_graph_db.py)
- Item 3: __all__ shims for 7 star-import __init__.py files
- Item 3 (CI): governance regression gate (tests/governance/test_dep_graph_regression.py)

## CODE_COMMIT

cbb949571cec5012f6588c14f463de79775ce283

## EVIDENCE_COMMIT

8d073ce49fad14753a6d3269c54e75901fc87552

## FILES_CHANGED_CODE

artifacts/dep_graph.sqlite
tests/governance/test_dep_graph_regression.py
tools/dep_graph_db.py
agentic_core/prompt_governance/core/__init__.py
agentic_core/prompt_governance/optimization/__init__.py
agentic_core/runtime/config/__init__.py
agentic_core/runtime/engine/__init__.py
agentic_core/runtime/types/__init__.py
agentic_core/runtime/utils/__init__.py
agentic_core/utils/__init__.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/dep_graph_db_evidence.md

## INSPECTED_FILES

ops_scripts/general/dep_graph_scan.py
tools/dep_graph_db.py
tests/governance/test_dep_graph_regression.py
agentic_core/prompt_governance/core/__init__.py
agentic_core/prompt_governance/optimization/__init__.py
agentic_core/runtime/config/__init__.py
agentic_core/runtime/engine/__init__.py
agentic_core/runtime/types/__init__.py
agentic_core/runtime/utils/__init__.py
agentic_core/utils/__init__.py

## GraphBuild

$ python tools/dep_graph_db.py --build
Graph built and saved to: C:\Git\Agentic-Workflow\artifacts\dep_graph.sqlite
  nodes=2109  edges=2100
  orphans=725  cycles=13
  layer_violations=100
  pinecone_importers=92

## GraphStats

$ python tools/dep_graph_db.py --stats
  total_nodes: 2109
  total_edges: 2100
  total_unique_modules: 1919
  orphan_count: 725
  cycle_count: 13
  layer_violation_count: 100
  pinecone_importer_count: 92
  syntax_error_count: 0

## PineconeNodes

$ python tools/dep_graph_db.py --pinecone
Pinecone importers (transitive): 92
  agentic_core.L2_execution.reasoning.PineconeSovereignAgent
  agentic_core.L4_state.reasoning.PineconeSovereignAgent
  agentic_core.mixins.pinecone_vector_mixin
  agentic_core.L2_execution.enforcement.pinecone_mcp_client

Primary infection vector: agentic_core.interfaces.execution_agents
  exports PineconeSovereignAgent -> pulled by memory_embedder -> 80+ downstream modules

Blast radius of PineconeSovereignAgent: 90 modules
Transitive importers: 92 (includes 4 Pinecone nodes themselves)

## CIGateRun

$ python -m pytest -q --color=no tests/governance/test_dep_graph_regression.py
5 passed in 0.16s

Gates:
  test_cycle_count_within_budget          PASSED (13 <= 13)
  test_layer_inversion_count_within_budget PASSED (100 <= 100)
  test_pinecone_importer_count_within_budget PASSED (92 <= 92)
  test_pinecone_importer_count_not_growing PASSED (92 <= 92)
  test_no_unshimmed_star_imports_in_inits PASSED (0 violations)

## StarImportShimsFix

Files fixed (7):
  agentic_core/prompt_governance/core/__init__.py       - 17 exports declared
  agentic_core/prompt_governance/optimization/__init__.py - 5 exports declared
  agentic_core/runtime/config/__init__.py               - 11 exports declared
  agentic_core/runtime/engine/__init__.py               - 4 exports declared
  agentic_core/runtime/types/__init__.py                - 17 exports declared
  agentic_core/runtime/utils/__init__.py                - 1 export declared + try/except guard for missing runtime_bootstrapper
  agentic_core/utils/__init__.py                        - 5 exports declared

## FullPytestRun

$ python -m pytest -q --color=no
6554 passed, 83 skipped, 7 xfailed in 100.17s (0:01:40)

## PineconeDeprecationPathfinding

Key insight from graph queries:
  The 92 Pinecone importers are primarily reachable via ONE choke point:
    agentic_core.interfaces.execution_agents
  Removing PineconeSovereignAgent from __all__ in that file will cut the
  transitive reach from 92 to ~6 in a single edit (Phase 1.3 of deprecation plan).
  The blast_radius() query confirms safe deletion order:
    1. Remove from interfaces/execution_agents.py __all__ (Phase 1.3)
    2. Fix sovereign_memory_store.py (Phase 1.1)
    3. Fix SubAtomicRegistryAgent.py (Phase 1.2)
    4. Remove pinecone_vector_mixin.py (Phase 2)
    5. Delete PineconeSovereignAgent.py (Phase 3)

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

