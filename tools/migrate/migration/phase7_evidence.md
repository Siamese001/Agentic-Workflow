# Phase 7 Evidence: Windows Pre-commit Unblock + Hook Convergence

## WAVE 7.1 — Reset to clean baseline

### git rev-parse HEAD:
387bb1ed2037ddbd46fdd8ae8457e4623561667f

### git status --porcelain=v1 (initial):
 M .pre-commit-config.yaml
?? artifacts/migration/phase7_evidence.md

### pre-commit run -a (iteration 1):
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Passed
T0: Enforce LF Line Endings..............................................Passed
T0: Check Merge Conflict Markers.........................................Passed
T1: Python Syntax Validation.............................................Passed
T2a: Ruff Lint & Auto-Fix................................................Passed
T2b: Ruff Format.........................................................Passed
T3a: Anti-Pattern Landmine Detection.....................................Failed
- hook id: check-anti-patterns
- exit code: 1

[BLOCK] Found 15 NEW anti-pattern landmine(s) (out of 5362 total):
  ò magic_configuration: 7
  ò silent_swallower: 8

[FAIL] SovereignLLMGateway.py:349
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as _p3_exc:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:312
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:172
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:294
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:304
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:193
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:249
   [magic_configuration] Magic configuration: Hardcoded max_depth=3
   Evidence: max_depth: int = 3,...
   [FIX] Externalize configuration value:

[FAIL] anthropic_client.py:431
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception:...
   [FIX] Add proper error handling:

[FAIL] anthropic_client.py:240
   [magic_configuration] Magic configuration: Hardcoded concurrent_limit=10
   Evidence: concurrent_limit: int = 10,...
   [FIX] Externalize configuration value:

[FAIL] anthropic_client.py:59
   [magic_configuration] Magic configuration: Hardcoded max_tries=7 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[FAIL] anthropic_client.py:59
   [magic_configuration] Magic configuration: Hardcoded max_value=60 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[FAIL] openai_client.py:343
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception:...
   [FIX] Add proper error handling:

[FAIL] openai_client.py:202
   [magic_configuration] Magic configuration: Hardcoded concurrent_limit=5
   Evidence: concurrent_limit: int = 5,...
   [FIX] Externalize configuration value:

[FAIL] openai_client.py:49
   [magic_configuration] Magic configuration: Hardcoded max_tries=5 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[FAIL] openai_client.py:49
   [magic_configuration] Magic configuration: Hardcoded max_value=60 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[ACTION] Fix NEW violations or add '# guardian: allow-<pattern>' to whitelist.
         To update baseline with current violations: python ops_scripts/ci/check_anti_patterns.py --write-baseline


### git status --porcelain=v1 (after pre-commit):
 M .pre-commit-config.yaml
?? artifacts/migration/phase7_evidence.md

### pytest unit test:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 3 items

tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_no_direct_sdk_imports_in_embedding_sovereign_agent [32mPASSED[0m[32m [ 33%][0m
tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_embedding_sovereign_agent_uses_wrapper_factories [32mPASSED[0m[32m [ 66%][0m
tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_embedding_sovereign_agent_no_direct_sdk_instantiation [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================
0.11s call     tests/unit/test_embedding_sovereign_agent_uses_wrappers.py::test_no_direct_sdk_imports_in_embedding_sovereign_agent

(8 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m3 passed[0m[32m in 0.14s[0m[32m ==============================[0m

### pytest guardian test:
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
1.05s call     tests/guardian/test_no_direct_llm_sdk_imports.py::test_no_direct_llm_sdk_imports_in_agentic_core
0.01s call     tests/guardian/test_no_direct_llm_sdk_imports.py::test_only_allowed_direct_imports_in_sdks_mcps

(4 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m2 passed[0m[32m in 1.10s[0m[32m ==============================[0m

### pre-commit run -a (iteration 2):
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Passed
T0: Enforce LF Line Endings..............................................Passed
T0: Check Merge Conflict Markers.........................................Passed
T1: Python Syntax Validation.............................................Passed
T2a: Ruff Lint & Auto-Fix................................................Passed
T2b: Ruff Format.........................................................Passed
T3a: Anti-Pattern Landmine Detection.....................................Failed
- hook id: check-anti-patterns
- exit code: 1

[BLOCK] Found 15 NEW anti-pattern landmine(s) (out of 5362 total):
  ò magic_configuration: 7
  ò silent_swallower: 8

[FAIL] SovereignLLMGateway.py:349
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as _p3_exc:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:312
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:172
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:294
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:304
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:193
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] EmbeddingSovereignAgent.py:249
   [magic_configuration] Magic configuration: Hardcoded max_depth=3
   Evidence: max_depth: int = 3,...
   [FIX] Externalize configuration value:

[FAIL] anthropic_client.py:431
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception:...
   [FIX] Add proper error handling:

[FAIL] anthropic_client.py:240
   [magic_configuration] Magic configuration: Hardcoded concurrent_limit=10
   Evidence: concurrent_limit: int = 10,...
   [FIX] Externalize configuration value:

[FAIL] anthropic_client.py:59
   [magic_configuration] Magic configuration: Hardcoded max_tries=7 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[FAIL] anthropic_client.py:59
   [magic_configuration] Magic configuration: Hardcoded max_value=60 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[FAIL] openai_client.py:343
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception:...
   [FIX] Add proper error handling:

[FAIL] openai_client.py:202
   [magic_configuration] Magic configuration: Hardcoded concurrent_limit=5
   Evidence: concurrent_limit: int = 5,...
   [FIX] Externalize configuration value:

[FAIL] openai_client.py:49
   [magic_configuration] Magic configuration: Hardcoded max_tries=5 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[FAIL] openai_client.py:49
   [magic_configuration] Magic configuration: Hardcoded max_value=60 in function call
   Evidence: @backoff.on_exception(...
   [FIX] Externalize configuration value:

[ACTION] Fix NEW violations or add '# guardian: allow-<pattern>' to whitelist.
         To update baseline with current violations: python ops_scripts/ci/check_anti_patterns.py --write-baseline


### git status --porcelain=v1 (final):
 M .pre-commit-config.yaml
?? artifacts/migration/phase7_evidence.md

### git --no-pager diff:
diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
index 98e2d3f2e..6105c0659 100644
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -35,6 +35,7 @@ repos:
         name: "T0: Trailing Whitespace"
       - id: end-of-file-fixer
         name: "T0: End-of-File Fixer"
+        exclude: ^artifacts/migration/
       - id: mixed-line-ending
         name: "T0: Enforce LF Line Endings"
         args: [--fix=lf]
