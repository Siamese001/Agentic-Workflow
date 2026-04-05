# Phase 3 Evidence: Decontamination + Wrapper Stabilization

## WAVE 3.1 — Scope lockdown + revert unrelated changes

### Current state capture:
- git rev-parse HEAD: bed74b7f3cfe997a212e8e63ee8d49f9bfc7b1e9
- git status --porcelain=v1:
 M agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
 M agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
?? artifacts/migration/phase2_commit_manifest.txt
?? artifacts/migration/phase3_evidence.md

### git --no-pager diff:
diff --git a/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py b/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
index 61da4dc84..c8400dc47 100644
--- a/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
+++ b/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
@@ -37,8 +37,6 @@ from data.sdks_mcps.client_wrappers import (
     create_vertex_client,
 )

-# guardian: allow-silent-swallower
-
 Logger = logging.getLogger(__name__)

 Provider = Literal["openai", "anthropic", "google"]
diff --git a/agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py b/agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
index 49aaf2dcb..90fa13d9f 100644
--- a/agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
+++ b/agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
@@ -29,9 +29,6 @@ from data.sdks_mcps.client_wrappers import (
     create_vertex_client,
 )

-# guardian: allow-silent-swallower
-# guardian: allow-magic-configuration
-
 Logger = logging.getLogger(__name__)

 # Import mixins for functionality

### Wrapper import test:
OK

### py_compile test:
SUCCESS

### Guardian import gate test:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

tests/guardian/test_no_direct_llm_sdk_imports.py::test_no_direct_llm_sdk_imports_in_agentic_core [32mPASSED[0m[32m [ 50%][0m
tests/guardian/test_no_direct_llm_sdk_imports.py::test_only_allowed_direct_imports_in_sdks_mcps [32mPASSED[0m[32m [100%][0m

============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================

=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 2
Passed: 2
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
1.03s call     tests/guardian/test_no_direct_llm_sdk_imports.py::test_no_direct_llm_sdk_imports_in_agentic_core
0.01s call     tests/guardian/test_no_direct_llm_sdk_imports.py::test_only_allowed_direct_imports_in_sdks_mcps

(4 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m2 passed[0m[32m in 1.08s[0m[32m ==============================[0m

### Unit contract tests:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 3 items / 1 error

=================================== ERRORS ====================================
[31m[1m_ ERROR collecting tests/unit/test_embedding_sovereign_agent_uses_wrappers.py _[0m
[1m[31mtests\unit\test_embedding_sovereign_agent_uses_wrappers.py[0m:11: in <module>
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mL2_execution[39;49;00m[04m[96m.[39;49;00m[04m[96mreasoning[39;49;00m[04m[96m.[39;49;00m[04m[96mEmbeddingSovereignAgent[39;49;00m[90m [39;49;00m[94mimport[39;49;00m EmbeddingSovereignAgent[90m[39;49;00m
[1m[31magentic_core\L2_execution\reasoning\EmbeddingSovereignAgent.py[0m:55: in <module>
    [0m[94mclass[39;49;00m[90m [39;49;00m[04m[92mEmbeddingSovereignAgent[39;49;00m(RedisCacheMixin, SovereignBaseAgent):[90m[39;49;00m
                                                   ^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mE   NameError: name 'SovereignBaseAgent' is not defined[0m
[36m[1m=========================== short test summary info ===========================[0m
[31mERROR[0m tests/unit/test_embedding_sovereign_agent_uses_wrappers.py - NameError: name 'SovereignBaseAgent' is not defined
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
[31m============================== [31m[1m1 error[0m[31m in 0.15s[0m[31m ===============================[0m

### Unit contract tests (AST import tests only):
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

tests/unit/test_sovereign_llm_gateway_uses_wrappers.py::test_no_direct_sdk_imports_in_sovereign_llm_gateway [32mPASSED[0m[32m [ 50%][0m
tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_no_direct_sdk_imports_in_embedding_sovereign_agent [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(6 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m2 passed[0m[32m in 0.14s[0m[32m ==============================[0m

### pre-commit run -a:
T0: Trailing Whitespace..................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing artifacts/evidence/phase11_isolated_branch_verification.md


### git --no-pager show --name-only --oneline -1 (BEFORE new commit):
bed74b7f3 Phase 2: Migrate agentic_core LLM SDK usage to client wrappers
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
apps_lic/engines/LicS2SupervisorAgent.py
artifacts/migration/phase1_guardian_output.txt
artifacts/migration/phase2_audit_regen_output.txt
artifacts/migration/phase2_guardian_full_output.txt
artifacts/migration/phase2_guardian_import_gate_output.txt
artifacts/migration/sdk_direct_import_audit.json
data/sdks_mcps/client_wrappers/__init__.py
data/sdks_mcps/client_wrappers/anthropic_client.py
data/sdks_mcps/client_wrappers/openai_client.py
docs/reports/plans/v15_p3_evidence.json
tests/guardian/test_no_direct_llm_sdk_imports.py
tests/unit/test_embedding_sovereign_agent_uses_wrappers.py
tests/unit/test_sovereign_llm_gateway_uses_wrappers.py

### git --no-pager diff --name-status HEAD (sanity):
M	agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
M	agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
M	artifacts/architecture/module_collision_baseline.json
M	artifacts/evidence/phase11_isolated_branch_verification.md
