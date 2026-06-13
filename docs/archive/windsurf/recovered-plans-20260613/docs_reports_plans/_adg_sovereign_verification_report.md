================================================================================
AST-BASED DEPENDENCY GRAPH VERIFICATION
SOVEREIGN_TERRITORIES Elimination Analysis
================================================================================

Constitutional Compliance: §3.4 (AST PRIMARY), §3.5 (NO GREP), §3.6 (FAIL CLOSED)

⚠️  PARSE ERRORS (Fail-Closed): 189 files
These files could not be analyzed. Manual review required:
  - .healing_backups\location_violations\agentic_core_L3_orchestration_reasoning_DagRuntimeInspectorAgent.py
  - .healing_backups\location_violations\agentic_core_L3_orchestration_reasoning_DagRuntimeInspectorAgent_1.py
  - .healing_backups\location_violations\agentic_core_L3_orchestration_reasoning_DagRuntimeInspectorAgent_2.py
  - .healing_backups\location_violations\agentic_core_L5_safety_reasoning_SignatureVerifierAgent.py
  - .healing_backups\location_violations\agentic_core_L5_safety_reasoning_SignatureVerifierAgent_1.py
  - .healing_backups\location_violations\agentic_core_L5_safety_reasoning_SignatureVerifierAgent_2.py
  - .healing_backups\location_violations\agentic_core_L5_safety_reasoning_TokenBudgetInspectorAgent.py
  - .healing_backups\location_violations\agentic_core_L5_safety_reasoning_TokenBudgetInspectorAgent_1.py
  - .healing_backups\location_violations\agentic_core_L5_safety_reasoning_TokenBudgetInspectorAgent_2.py
  - .healing_backups\location_violations\agent_registry.py
  ... and 179 more

DEFINITION LAYER: 8 files
  Imports: 10
  Usages: 24
  Status: ✅ EXPECTED (these files define/derive the constant)
  Files:
    - agentic_core\L5_safety\config\structure_blueprint\__init__.py
    - agentic_core\L5_safety\config\structure_blueprint\_constants.py
    - agentic_core\L5_safety\config\structure_blueprint\_verify.py
    - agentic_core\L5_safety\config\structure_blueprint\derived.py
    - agentic_core\L5_safety\config\structure_blueprint\ssot.py
    ... and 3 more

PRODUCTION CODE: 0 files
  Imports: 0
  Usages: 0
  Status: ✅ CLEAN (zero imports/usages)

TESTS: 8 files
  Imports: 18
  Usages: 45
  Status: ℹ️  INFORMATIONAL (tests may reference for validation)

ARCHIVED: 16 files
  Imports: 20
  Usages: 41
  Status: ✅ IGNORED (archived code)

================================================================================
DEPENDENCY GRAPH SUMMARY (§3.7)
================================================================================
Total Active Files: 16
Total Imports: 28
Total Usages: 69

VERDICT: ✅ 100% COMPLETE
  Zero production imports
  Zero production usages
  All references are in definition layer or tests (expected)
## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

