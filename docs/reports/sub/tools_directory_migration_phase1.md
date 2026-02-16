# Tools Directory Migration Phase 1 - Evidence

## Objective
Eliminate SSOT governance blind spot caused by tools/ by migrating all enforcement modules into agentic_core/L5_safety/enforcement/**, updating all references, and deleting tools/.

## Wave 1.1 - Baseline Inventory + Dependency Map

### Current State
- Git status (porcelain=v1):
```
?? docs/reports/plans/phase1_remediation_evidence.md
?? docs/reports/plans/phase2_evidence.md
?? docs/reports/plans/phase2_remediation_plan.md
?? docs/reports/plans/phase2_remediation_plan_redesigned.md
?? docs/reports/plans/phase2_retroactive_evidence.md
?? docs/reports/plans/phase2_wave1_retroactive_analysis.md
?? docs/reports/plans/phase2_wave1_retroactive_forensic.md
?? docs/reports/plans/phase2_wave1_static_analysis.md
?? phase2_violation_analysis.py
?? tests/apps_rg/scripts/test_engine.py
?? tests/apps_rg/scripts/test_input.py
?? tests/apps_rg/scripts/test_run_grand_unification_tests.py
?? tests/architecture/test_longpaths_bypass.py
```

- Current commit: ce624e6e2e35a2a41323621b32000e407cea5f2e

### Tools/ Directory Inventory
All Python files in tools/ with sizes:
```
C:\Git\Agentic-Workflow\tools\architectural\module_collision_guard.py:14688 bytes
C:\Git\Agentic-Workflow\tools\enforcement\phase_acceptance_guard.py:8905 bytes
C:\Git\Agentic-Workflow\tools\enforcement\pytest_config_guard.py:11801 bytes
C:\Git\Agentic-Workflow\tools\governance\agent_heal_audit.py:6675 bytes
C:\Git\Agentic-Workflow\tools\governance\artifacts_guard.py:4642 bytes
C:\Git\Agentic-Workflow\tools\governance\cache_guard.py:6579 bytes
C:\Git\Agentic-Workflow\tools\governance\docs_structure_guard.py:4880 bytes
C:\Git\Agentic-Workflow\tools\governance\logs_guard.py:7271 bytes
C:\Git\Agentic-Workflow\tools\security\credential_guard.py:4951 bytes
C:\Git\Agentic-Workflow\tools\tmp_ok\analyze_clusters_phase3.py:1058 bytes
C:\Git\Agentic-Workflow\tools\tmp_ok\analyze_exact_dupes.py:1131 bytes
C:\Git\Agentic-Workflow\tools\tmp_ok\callsite_ast_fuzzy_defs.py:7282 bytes
C:\Git\Agentic-Workflow\tools\tmp_ok\cluster_ast_fuzzy_defs.py:8483 bytes
C:\Git\Agentic-Workflow\tools\tmp_ok\derive_central_candidates.py:2287 bytes
C:\Git\Agentic-Workflow\tools\tmp_ok\scan_ast_fuzzy_defs.py:7009 bytes
```

### Tools Import References Found
```
C:\Git\Agentic-Workflow\tests\enforcement\test_phase_acceptance_guard.py:20:from tools.enforcement.phase_acceptance_guard import PhaseAcceptanceGuard
C:\Git\Agentic-Workflow\tests\enforcement\test_pytest_config_guard.py:18:from tools.enforcement.pytest_config_guard import PytestEnforcementGuard
C:\Git\Agentic-Workflow\tests\governance\test_agent_heal_audit.py:206:        from tools.governance.agent_heal_audit import AgentHealAuditScanner
```

### Migration Map (Target Files Only)
| Source Path | Destination Path | New Import Module |
|-------------|------------------|-------------------|
| tools/architectural/module_collision_guard.py | agentic_core/L5_safety/enforcement/module_collision_guard.py | agentic_core.L5_safety.enforcement.module_collision_guard |
| tools/governance/artifacts_guard.py | agentic_core/L5_safety/enforcement/governance/artifacts_guard.py | agentic_core.L5_safety.enforcement.governance.artifacts_guard |
| tools/governance/cache_guard.py | agentic_core/L5_safety/enforcement/governance/cache_guard.py | agentic_core.L5_safety.enforcement.governance.cache_guard |
| tools/governance/docs_structure_guard.py | agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py | agentic_core.L5_safety.enforcement.governance.docs_structure_guard |
| tools/governance/logs_guard.py | agentic_core/L5_safety/enforcement/governance/logs_guard.py | agentic_core.L5_safety.enforcement.governance.logs_guard |
| tools/security/credential_guard.py | agentic_core/L5_safety/enforcement/security/credential_guard.py | agentic_core.L5_safety.enforcement.security.credential_guard |
| tools/enforcement/phase_acceptance_guard.py | agentic_core/L5_safety/enforcement/phase_acceptance_guard.py | agentic_core.L5_safety.enforcement.phase_acceptance_guard |
| tools/enforcement/pytest_config_guard.py | agentic_core/L5_safety/enforcement/pytest_config_guard.py | agentic_core.L5_safety.enforcement.pytest_config_guard |
| tools/governance/agent_heal_audit.py | agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py | agentic_core.L5_safety.enforcement.governance.agent_heal_audit |

### Files Not in Scope
- tools/tmp_ok/* (temporary files - deleted with tools/)

## Wave 1.2 - Migration + Reference Updates

### Post-Migration Reference Search
```
C:\Git\Agentic-Workflow\.venv\Lib\site-packages\mcp\server\fastmcp\utilities\types.py:10:    """Helper class for returning images from tools."""
C:\Git\Agentic-Workflow\.venv\Lib\site-packages\mcp\server\fastmcp\utilities\types.py:58:    """Helper class for returning audio from tools."""
```
(Only .venv references remain - acceptable)

### Pytest Verification
```
======================================================================================================================================================== 153 passed in 20.32s =========================================================================================================================================================
```

## Wave 1.3 - Deletion + Final Proof

### Tools/ Directory Removal Proof
```
tools/ removed
```

### Zero References Proof
```
no tools references
```

### Full Verification
```
======================================================================================================================================================== 153 passed in 20.28s =========================================================================================================================================================
```

### Final Git Status
```
 M agentic_core/L5_safety/enforcement/__init__.py
 M tests/enforcement/test_phase_acceptance_guard.py
 M tests/enforcement/test_pytest_config_guard.py
 M tests/governance/test_agent_heal_audit.py
 D tools/architectural/module_collision_guard.py
 D tools/enforcement/phase_acceptance_guard.py
 D tools/enforcement/pytest_config_guard.py
 D tools/governance/agent_heal_audit.py
 D tools/governance/artifacts_guard.py
 D tools/governance/cache_guard.py
 D tools/governance/docs_structure_guard.py
 D tools/governance/logs_guard.py
 D tools/security/credential_guard.py
 D tools/tmp_ok/analyze_clusters_phase3.py
 D tools/tmp_ok/analyze_exact_dupes.py
 D tools/tmp_ok/callsite_ast_fuzzy_defs.py
 D tools/tmp_ok/cluster_ast_fuzzy_defs.py
 D tools/tmp_ok/derive_central_candidates.py
 D tools/tmp_ok/scan_ast_fuzzy_defs.py
?? agentic_core/L5_safety/enforcement/governance/
?? agentic_core/L5_safety/enforcement/module_collision_guard.py
?? agentic_core/L5_safety/enforcement/phase_acceptance_guard.py
?? agentic_core/L5_safety/enforcement/pytest_config_guard.py
?? agentic_core/L5_safety/enforcement/security/
?? docs/reports/sub/tools_directory_migration_phase1.md
```

## Final Commit Hash
[TO BE FILLED AFTER COMMIT]

## Changed Paths
[TO BE FILLED AFTER COMMIT]
