# Shim and Stub __all__ Inventory — Fix All Invalid Entries

## Scope

AST-based scan of all 380 files with `__all__` definitions across
`agentic_core`, `apps_lic`, `apps_rg`, `apps_shared`, `system_learning`,
`ops_scripts`, `tools`, `tests`. Identified and fixed all 23 genuinely
invalid entries (the original scanner count of 69 included 46 false
positives from `try/except` import blocks and annotated assignments).

## CODE_COMMIT

4792a4422c3cfe743eb5bdbf0cc49ade913b261f

## EVIDENCE_COMMIT

550f80b1786febc3af94f8be1832a4c685615971

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/function_tool.py
agentic_core/L0_routing/types/routing_artifact_types.py
agentic_core/L1_cognition/__init__.py
agentic_core/L2_execution/tools/file_io_impl.py
agentic_core/L4_state/__init__.py
agentic_core/L4_state/utils/__init__.py
agentic_core/L4_state/utils/rag_enhancement_util.py
agentic_core/L5_safety/runners/__init__.py
agentic_core/L5_safety/validators/__init__.py
agentic_core/prompt_governance/core/__init__.py
agentic_core/prompt_governance/optimization/__init__.py
agentic_core/runtime/config/__init__.py
agentic_core/runtime/engine/__init__.py
agentic_core/runtime/exceptions/workflow_exceptions.py
agentic_core/runtime/types/__init__.py
agentic_core/runtime/utils/__init__.py
agentic_core/utils/__init__.py
apps_lic/utils/mixins_util.py
apps_shared/utils/__init__.py
system_learning/engines/seed_embedding_pack_builder.py
tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports.py
tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports_impl.py
ops_scripts/hooks/landmine_baseline.txt

## FILES_CHANGED_EVIDENCE

docs/reports/plans/shim_inventory_evidence.md

## INSPECTED_FILES

agentic_core/L0_routing/scripts/function_tool.py
agentic_core/L0_routing/types/routing_artifact_types.py
agentic_core/L1_cognition/__init__.py
agentic_core/L2_execution/tools/file_io_impl.py
agentic_core/L4_state/__init__.py
agentic_core/L4_state/utils/__init__.py
agentic_core/L4_state/utils/rag_enhancement_util.py
agentic_core/L5_safety/config/structure_blueprint/__init__.py
agentic_core/L5_safety/runners/__init__.py
agentic_core/L5_safety/validators/__init__.py
agentic_core/prompt_governance/core/__init__.py
agentic_core/prompt_governance/optimization/__init__.py
agentic_core/runtime/config/__init__.py
agentic_core/runtime/engine/__init__.py
agentic_core/runtime/exceptions/workflow_exceptions.py
agentic_core/runtime/types/__init__.py
agentic_core/runtime/utils/__init__.py
agentic_core/utils/__init__.py
apps_lic/utils/mixins_util.py
apps_shared/utils/__init__.py
system_learning/engines/seed_embedding_pack_builder.py
tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports.py
tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports_impl.py

## AST Inventory Scan

$ python -c "... (scanner — see _shim_inventory_raw.txt for full output) ..."
TOTAL_FILES_WITH_ALL=380
INVALID_FILES=0
ALL_CLEAN: 0 invalid __all__ entries remaining

## Fix Classification

Pattern A — Star-import __init__.py (explicit imports added):
  agentic_core/prompt_governance/core/__init__.py
  agentic_core/prompt_governance/optimization/__init__.py
  agentic_core/runtime/config/__init__.py
  agentic_core/runtime/engine/__init__.py
  agentic_core/runtime/types/__init__.py
  agentic_core/runtime/utils/__init__.py
  agentic_core/utils/__init__.py

Pattern B — Phantom __all__ (names never existed, removed):
  agentic_core/L1_cognition/__init__.py (14 phantom names removed, 4 real ActionRequest types kept)
  agentic_core/L4_state/__init__.py (11 phantom names removed, entire __all__ dropped)
  system_learning/engines/seed_embedding_pack_builder.py (SeedEmbeddingPackBuilder removed)
  agentic_core/L0_routing/scripts/function_tool.py (BaseTool removed, base.py missing)
  apps_shared/utils/__init__.py (StateManager, VectorMemoryStore, CircuitBreaker removed)

Pattern C — Case mismatch (corrected):
  agentic_core/L4_state/utils/rag_enhancement_util.py (SelfRAGProcessor->SelfRagProcessor, KGContext->KgContext)
  agentic_core/L2_execution/tools/file_io_impl.py (FileIO->FileIo)
  agentic_core/runtime/exceptions/workflow_exceptions.py (APIError->ApiError)

Pattern D — Typo alias (removed):
  agentic_core/L0_routing/types/routing_artifact_types.py (RoutDecisionArtifact removed)

Pattern E — Empty __init__.py, imports added:
  agentic_core/L5_safety/runners/__init__.py (arch_governor_runner module import added)
  agentic_core/L4_state/utils/__init__.py (complexity + layer_gravity imports added)
  apps_lic/utils/mixins_util.py (SubatomicTestingMixin, MCPHardenedMixin, HealerMixin imports added)

Pattern F — Intentionally lazy shim, __all__ removed:
  agentic_core/L5_safety/validators/__init__.py (__all__ removed, lazy per docstring)

Pattern G — Illegal __all__ = ["*"] (removed):
  tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports.py
  tests/guardian/data_prompt_governance/tests_modularity_test_layer_imports_impl.py

Pattern H — __getattr__ lazy loader (VALID, no fix needed):
  agentic_core/L5_safety/config/structure_blueprint/__init__.py

## Full Test Suite

$ python -m pytest -q --color=no
6554 passed, 83 skipped, 7 xfailed in 92.84s
EXIT CODE: 0

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

