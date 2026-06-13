# Dep Graph DB + __all__ Shims + CI Gate — Hardening Pass

## Scope

Re-hardening of items 2-4 (dep_graph_db, __all__ shims, CI regression gate).
Identified and fixed 9 bugs found during deep audit.

## CODE_COMMIT

ea655ba19bb1e21d98cd6c10ce8e7fc3c3c2d3b6

## EVIDENCE_COMMIT

4cbdefed71c1bb33aa24cf20455a091304c09cc9

## FILES_CHANGED_CODE

agentic_core/prompt_governance/core/__init__.py
agentic_core/runtime/config/__init__.py
agentic_core/runtime/engine/__init__.py
agentic_core/runtime/types/__init__.py
tests/governance/test_dep_graph_regression.py
tools/dep_graph_db.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/dep_graph_db_hardening_evidence.md

## INSPECTED_FILES

tools/dep_graph_db.py
tests/governance/test_dep_graph_regression.py
agentic_core/prompt_governance/core/__init__.py
agentic_core/prompt_governance/optimization/__init__.py
agentic_core/runtime/config/__init__.py
agentic_core/runtime/engine/__init__.py
agentic_core/runtime/types/__init__.py
agentic_core/runtime/utils/__init__.py
agentic_core/utils/__init__.py

## BugsFixed

### dep_graph_db.py (4 bugs)

Bug 1: _build_graph return type annotation said tuple[DiGraph, dict[str,str]] but returns 3-tuple.
  Fixed: tuple[nx.DiGraph, dict[str, str], list]

Bug 2: blast_radius() caught nx.NodeNotFound but nx.ancestors on reversed view raises
  NetworkXError (not NodeNotFound) for unknown nodes. Caused unhandled exception.
  Fixed: explicit `if module not in self._g: return set()` guard before ancestors call.

Bug 3: direct_dependents() and direct_dependencies() called predecessors()/successors()
  on unknown nodes — raises NetworkXError via KeyError chain, not caught.
  Fixed: `if module not in self._g: return []` guard on both methods.

Bug 4: all_paths() caught nx.NetworkXNoPath which all_simple_paths() never raises
  (it returns an empty generator instead). Unknown nodes caused unhandled NetworkXError.
  Fixed: explicit node-existence guard + catch only nx.NodeNotFound.

### __all__ shims (5 inaccuracies)

Bug 5: runtime/engine/__init__.py — listed extract_entity_code, generate_import_fix,
  get_movable_entities which do NOT exist as top-level names in ast_relocator.py
  (only AstRelocator is top-level). Fixed: removed non-existent names.

Bug 6: runtime/config/__init__.py — listed EXCELLENT_MIN, GOOD_MIN, HIGH_MIN,
  MARGINAL_MIN, MAX_HALLUCINATION_RISK, MAX_REPETITION_RATIO, MIN_AUTHORITY which are
  not exported by signal_quality_config.py. Actual exports: QualityThresholds,
  SignalAssessment, SignalQuality, get_signal_enhancer, signal_enhancer.
  Fixed: replaced with accurate names from AST audit.

Bug 7: runtime/types/__init__.py — missing create_semantic_cache, semantic_cache
  (from cache_entry_types), create_claim_scorer (from claim_type_types),
  get_global_cost_governor, track_api_call (from cost_governor_types).
  Fixed: added all missing accurate names.

Bug 8: prompt_governance/core/__init__.py — listed validate_input, validate_output
  (not in governance_hub.py), render, render_tagentic (not in sovereign_prompt_renderer.py),
  get_template_schema, list_available_templates (not exported).
  Fixed: removed all non-existent names.

Bug 9 (CI gate): test_no_new_pinecone_nodes used baseline of 6 but actual measured
  pinecone_nodes() count is 4. Fixed: baseline corrected to 4.
  Also: previous test_pinecone_importer_count_not_growing was a pure duplicate of
  test_pinecone_importer_count_within_budget (identical assertion). Replaced with
  distinct test_no_new_pinecone_nodes (direct Pinecone node count gate).

## DeepProbeResults

20 correctness probes run against the fixed dep_graph_db API:

  OK: blast_radius unknown module -> empty set
  OK: direct_dependents unknown -> []
  OK: direct_dependencies unknown -> []
  OK: all_paths unknown -> []
  OK: blast_radius PSA -> 90 modules (includes execution_agents)
  OK: dependencies execution_agents -> contains PSA
  OK: shortest_path -> ['agentic_core.interfaces.execution_agents', 'agentic_core.L2_execution.reasoning.PineconeSovereignAgent']
  OK: shortest_path to unknown -> []
  OK: all_paths -> 1 paths found
  OK: pinecone_nodes = 4
  OK: pinecone_importers = 92
  OK: cycles = 13, all valid lists
  OK: layer_violations = 100
  OK: orphans = 725, none are __init__
  OK: file_for/module_for_file round-trip
  OK: subgraph_for_layer L2_execution = 184 nodes
  OK: fan_in_top[0] = ('agentic_core.base_agents.SovereignBaseAgent', 131)
  OK: stats dict has all 8 required keys
  OK: pinecone_import_paths = 9 entries
  OK: unreachable_from execution_agents = 2018 modules

## AllShimsAccurate

Post-fix AST audit of all 7 __all__ shims vs source modules:

  OK agentic_core/utils/__init__.py: all 5 exports verified
  OK agentic_core/prompt_governance/core/__init__.py: all 10 exports verified
  OK agentic_core/prompt_governance/optimization/__init__.py: all 5 exports verified
  OK agentic_core/runtime/config/__init__.py: all 9 exports verified
  OK agentic_core/runtime/engine/__init__.py: all 1 exports verified
  OK agentic_core/runtime/types/__init__.py: all 21 exports verified
  OK agentic_core/runtime/utils/__init__.py: all 1 exports verified

## CIGateRun

$ python -m pytest -q --color=no tests/governance/test_dep_graph_regression.py -v
5 passed in 0.15s

  test_cycle_count_within_budget          PASSED (13 <= 13)
  test_layer_inversion_count_within_budget PASSED (100 <= 100)
  test_pinecone_importer_count_within_budget PASSED (92 <= 92)
  test_no_new_pinecone_nodes              PASSED (4 <= 4)
  test_no_unshimmed_star_imports_in_inits PASSED (0 violations)

## FullPytestRun

$ python -m pytest -q --color=no
6554 passed, 83 skipped, 7 xfailed in 83.73s (0:01:23)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

