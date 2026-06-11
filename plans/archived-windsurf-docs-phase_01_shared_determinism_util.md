---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase_01_shared_determinism_util.md'
original_relative_path: 'phase_01_shared_determinism_util.md'
source_sha256: 24382e3bbc403d5f4c069db64624f18c1ab761ced75b4c3f1d0e10f9903378f5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 1: Shared Determinism Utility — Evidence

Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping
and deterministic hashing bound to `canonical_bytes()` from the L0 spine.

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

- New file: `apps_shared/utils/determinism_util.py`
- New file: `tests/unit_min_deps/test_determinism_util.py`

## Commit Hash

ecd54545287d2b12de3919349179f50219d34d91

## Files Changed

- `apps_shared/utils/determinism_util.py` (created)
- `tests/unit_min_deps/test_determinism_util.py` (created)
- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)
- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)

## Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py

```
Exit code: 0

[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 10 items

tests/unit_min_deps/test_determinism_util.py::test_exclusion_top_level [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/test_determinism_util.py::test_exclusion_nested_recursive [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_determinism_util.py::test_list_recursive_preserves_order_and_strips [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_determinism_util.py::test_list_order_matters [32mPASSED[0m[32m [ 40%][0m
tests/unit_min_deps/test_determinism_util.py::test_file_hash_stable [32mPASSED[0m[32m [ 50%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_dict_top_level [32mPASSED[0m[32m [ 60%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_preserves_non_excluded [32mPASSED[0m[32m [ 70%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_tuple_preserved [32mPASSED[0m[32m [ 80%][0m
tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_deterministic_multiple_calls [32mPASSED[0m[32m [ 90%][0m
tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_content_differs [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m10 passed[0m[32m in 0.03s[0m[32m ==============================[0m
```


## Command: python -m pytest -q (full suite)

```
Exit code: 3

❌ agent_discovery_full.json not found
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4501 items / 46 errors
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
INTERNALERROR>     config.hook.pytest_collection(session=session)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
INTERNALERROR>     session.perform_collect()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
INTERNALERROR>     self.items.extend(self.genitems(node))
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
INTERNALERROR>     rep = collect_one_node(node)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
INTERNALERROR>     rep = yield
INTERNALERROR>           ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
INTERNALERROR>     call = CallInfo.from_call(
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
INTERNALERROR>     result: TResult | None = func()
INTERNALERROR>                              ^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
INTERNALERROR>     return list(collector.collect())
INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
INTERNALERROR>     self._register_setup_module_fixture()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
INTERNALERROR>     ^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
INTERNALERROR>     self._obj = obj = self._getobj()
INTERNALERROR>                       ^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
INTERNALERROR>     return importtestmodule(self.path, self.config)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
INTERNALERROR>     mod = import_path(
INTERNALERROR>           ^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
INTERNALERROR>     importlib.import_module(module_name)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
INTERNALERROR>     exec(co, module.__dict__)
INTERNALERROR>   File "c:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
INTERNALERROR>     sys.exit(1)
INTERNALERROR> SystemExit: 1

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.46s[0m[31m ========================[0m
mainloop: caught unexpected SystemExit!
```


## Command: git diff --stat HEAD

```
Exit code: 0

 .../plans/phase_01_shared_determinism_util.md      | 2361 ++------------------
 .../phase01_determinism_util_evidence_runner.py    |   64 +-
 2 files changed, 232 insertions(+), 2193 deletions(-)
```


## Command: git diff HEAD

```
Exit code: 0

diff --git a/docs/reports/plans/phase_01_shared_determinism_util.md b/docs/reports/plans/phase_01_shared_determinism_util.md
index cdc4e18a0..1b074f28d 100644
--- a/docs/reports/plans/phase_01_shared_determinism_util.md
+++ b/docs/reports/plans/phase_01_shared_determinism_util.md
@@ -10,7 +10,7 @@ and deterministic hashing bound to `canonical_bytes()` from the L0 spine.

 ## Commit Hash

-ebafd5b40
+PENDING

 ## Files Changed

@@ -46,9 +46,10 @@ tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_cont
 ============================ slowest 10 durations =============================

 (10 durations < 0.005s hidden.  Use -vv to show these durations.)
-[32m============================= [32m[1m10 passed[0m[32m in 0.03s[0m[32m ==============================[0m
+[32m============================= [32m[1m10 passed[0m[32m in 0.04s[0m[32m ==============================[0m
 ```

+
 ## Command: python -m pytest -q (full suite)

 ```
@@ -164,2182 +165,212 @@ INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_l
 INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
 INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
 INTERNALERROR>     exec(co, module.__dict__)
-INTERNALERROR>   File "C:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
+INTERNALERROR>   File "c:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
 INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
 INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
 INTERNALERROR>     sys.exit(1)
 INTERNALERROR> SystemExit: 1

-[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.31s[0m[31m ========================[0m
+[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 4.25s[0m[31m ========================[0m
 mainloop: caught unexpected SystemExit!
 ```

+
 ## Command: git diff --stat HEAD

 ```
 Exit code: 0

- apps_shared/utils/determinism_util.py              |   70 +
- .../plans/phase_01_shared_determinism_util.md      | 1813 ++++++++++++++++++++
- tests/unit_min_deps/test_determinism_util.py       |  104 ++
- .../phase01_determinism_util_evidence_runner.py    |  138 ++
- 4 files changed, 2125 insertions(+)
+ ops_scripts/hooks/landmine_baseline.txt            | 73 +++++++++-------------
+ .../phase01_determinism_util_evidence_runner.py    | 64 ++++++++++++-------
+ 2 files changed, 70 insertions(+), 67 deletions(-)
 ```

+
 ## Command: git diff HEAD

 ```
 Exit code: 0

-diff --git a/apps_shared/utils/determinism_util.py b/apps_shared/utils/determinism_util.py
-new file mode 100644
-index 000000000..1efe1bbe7
---- /dev/null
-+++ b/apps_shared/utils/determinism_util.py
-@@ -0,0 +1,70 @@
-+"""
-+Shared determinism utility for apps_lic and apps_rg.
-+
-+Provides canonical hashing and recursive nondeterminism stripping
-+bound to the canonical_bytes() function from the L0 spine.
-+
-+All hashing delegates to:
-+    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes
-+
-+No local canonicalization is performed here.
-+"""
-+
-+from __future__ import annotations
-+
-+import hashlib
-+from pathlib import Path
-+from typing import Any
-+
-+from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes
-+
-+DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
-+    {
-+        "duration_ms",
-+        "timestamp",
-+        "trace_id",
-+        "cycle_counter",
-+        "telemetry",
-+        "created_at",
-+        "updated_at",
-+    }
-+)
-+
-+
-+def strip_nondeterministic(obj: Any) -> Any:
-+    """Recursively strip nondeterministic fields from obj.
-+
-+    Rules:
-+    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
-+    - list/tuple: recurse each element, preserve order and type.
-+    - anything else: return as-is.
-+
-+    This function is recursion-safe and deterministic.
-+    It never introduces wall-clock time or randomness.
-+    """
-+    if isinstance(obj, dict):
-+        return {
-+            k: strip_nondeterministic(v)
-+            for k, v in obj.items()
-+            if k not in DETERMINISM_EXCLUDED_FIELDS
-+        }
-+    if isinstance(obj, tuple):
-+        return tuple(strip_nondeterministic(item) for item in obj)
-+    if isinstance(obj, list):
-+        return [strip_nondeterministic(item) for item in obj]
-+    return obj
-+
-+
-+def canonical_hash(obj: Any) -> str:
-+    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).
-+
-+    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
-+    Excluded fields are stripped recursively before hashing.
-+    """
-+    stripped = strip_nondeterministic(obj)
-+    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()
-+
-+
-+def file_hash(path: str | Path) -> str:
-+    """Return sha256 hexdigest of the raw bytes of the file at path."""
-+    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
-diff --git a/docs/reports/plans/phase_01_shared_determinism_util.md b/docs/reports/plans/phase_01_shared_determinism_util.md
-new file mode 100644
-index 000000000..7757d503a
---- /dev/null
-+++ b/docs/reports/plans/phase_01_shared_determinism_util.md
-@@ -0,0 +1,1813 @@
-+# Phase 1: Shared Determinism Utility — Evidence
-+
-+Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping
-+and deterministic hashing bound to `canonical_bytes()` from the L0 spine.
-+
-+## Scope
-+
-+- New file: `apps_shared/utils/determinism_util.py`
-+- New file: `tests/unit_min_deps/test_determinism_util.py`
-+
-+## Commit Hash
-+
-+<!-- filled after commit -->
-+PENDING
-+
-+## Files Changed
-+
-+- `apps_shared/utils/determinism_util.py` (created)
-+- `tests/unit_min_deps/test_determinism_util.py` (created)
-+- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)
-+- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)
-+
-+## Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py
-+
-+```
-+Exit code: 0
-+
-+[1m============================= test session starts =============================[0m
-+platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
-+rootdir: C:\Git\Agentic-Workflow
-+configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
-+plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
-+asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
-+collected 10 items
-+
-+tests/unit_min_deps/test_determinism_util.py::test_exclusion_top_level [32mPASSED[0m[32m [ 10%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_exclusion_nested_recursive [32mPASSED[0m[32m [ 20%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_list_recursive_preserves_order_and_strips [32mPASSED[0m[32m [ 30%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_list_order_matters [32mPASSED[0m[32m [ 40%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_file_hash_stable [32mPASSED[0m[32m [ 50%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_dict_top_level [32mPASSED[0m[32m [ 60%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_preserves_non_excluded [32mPASSED[0m[32m [ 70%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_tuple_preserved [32mPASSED[0m[32m [ 80%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_deterministic_multiple_calls [32mPASSED[0m[32m [ 90%][0m
-+tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_content_differs [32mPASSED[0m[32m [100%][0m
-+
-+============================ slowest 10 durations =============================
-+
-+(10 durations < 0.005s hidden.  Use -vv to show these durations.)
-+[32m============================= [32m[1m10 passed[0m[32m in 0.03s[0m[32m ==============================[0m
-+```
-+
-+## Command: python -m pytest -q (full suite)
-+
-+```
-+Exit code: 3
-+
-+❌ agent_discovery_full.json not found
-+[1m============================= test session starts =============================[0m
-+platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
-+rootdir: C:\Git\Agentic-Workflow
-+configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
-+testpaths: C:\Git\Agentic-Workflow\tests\enforcement
-+plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
-+asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
-+collected 4501 items / 46 errors
-+INTERNALERROR> Traceback (most recent call last):
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
-+INTERNALERROR>     session.exitstatus = doit(config, session) or 0
-+INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
-+INTERNALERROR>     config.hook.pytest_collection(session=session)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
-+INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
-+INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
-+INTERNALERROR>     raise exception
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+INTERNALERROR>     teardown.throw(exception)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
-+INTERNALERROR>     return (yield)
-+INTERNALERROR>             ^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+INTERNALERROR>     teardown.throw(exception)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
-+INTERNALERROR>     return (yield)
-+INTERNALERROR>             ^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+INTERNALERROR>     teardown.throw(exception)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
-+INTERNALERROR>     return (yield)
-+INTERNALERROR>             ^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
-+INTERNALERROR>     res = hook_impl.function(*args)
-+INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
-+INTERNALERROR>     session.perform_collect()
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
-+INTERNALERROR>     self.items.extend(self.genitems(node))
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-+INTERNALERROR>     yield from self.genitems(subnode)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-+INTERNALERROR>     yield from self.genitems(subnode)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-+INTERNALERROR>     yield from self.genitems(subnode)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
-+INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
-+INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
-+INTERNALERROR>     rep = collect_one_node(node)
-+INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
-+INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
-+INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
-+INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
-+INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
-+INTERNALERROR>     raise exception
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+INTERNALERROR>     teardown.throw(exception)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
-+INTERNALERROR>     rep = yield
-+INTERNALERROR>           ^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
-+INTERNALERROR>     res = hook_impl.function(*args)
-+INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
-+INTERNALERROR>     call = CallInfo.from_call(
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
-+INTERNALERROR>     result: TResult | None = func()
-+INTERNALERROR>                              ^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
-+INTERNALERROR>     return list(collector.collect())
-+INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
-+INTERNALERROR>     self._register_setup_module_fixture()
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
-+INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
-+INTERNALERROR>     ^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
-+INTERNALERROR>     self._obj = obj = self._getobj()
-+INTERNALERROR>                       ^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
-+INTERNALERROR>     return importtestmodule(self.path, self.config)
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
-+INTERNALERROR>     mod = import_path(
-+INTERNALERROR>           ^^^^^^^^^^^^
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
-+INTERNALERROR>     importlib.import_module(module_name)
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
-+INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
-+INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
-+INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
-+INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
-+INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
-+INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
-+INTERNALERROR>     exec(co, module.__dict__)
-+INTERNALERROR>   File "C:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
-+INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
-+INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
-+INTERNALERROR>     sys.exit(1)
-+INTERNALERROR> SystemExit: 1
-+
-+[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.29s[0m[31m ========================[0m
-+mainloop: caught unexpected SystemExit!
-+```
-+
-+## Command: git diff --stat HEAD
-+
-+```
-+Exit code: 0
-+
-+ apps_shared/utils/determinism_util.py              |   70 ++
-+ .../plans/phase_01_shared_determinism_util.md      | 1095 ++++++++++++++++++++
-+ tests/unit_min_deps/test_determinism_util.py       |  104 ++
-+ .../phase01_determinism_util_evidence_runner.py    |  138 +++
-+ 4 files changed, 1407 insertions(+)
-+```
-+
-+## Command: git diff HEAD
-+
-+```
-+Exit code: 0
-+
-+diff --git a/apps_shared/utils/determinism_util.py b/apps_shared/utils/determinism_util.py
-+new file mode 100644
-+index 000000000..1efe1bbe7
-+--- /dev/null
-++++ b/apps_shared/utils/determinism_util.py
-+@@ -0,0 +1,70 @@
-++"""
-++Shared determinism utility for apps_lic and apps_rg.
-++
-++Provides canonical hashing and recursive nondeterminism stripping
-++bound to the canonical_bytes() function from the L0 spine.
-++
-++All hashing delegates to:
-++    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes
-++
-++No local canonicalization is performed here.
-++"""
-++
-++from __future__ import annotations
-++
-++import hashlib
-++from pathlib import Path
-++from typing import Any
-++
-++from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes
-++
-++DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
-++    {
-++        "duration_ms",
-++        "timestamp",
-++        "trace_id",
-++        "cycle_counter",
-++        "telemetry",
-++        "created_at",
-++        "updated_at",
-++    }
-++)
-++
-++
-++def strip_nondeterministic(obj: Any) -> Any:
-++    """Recursively strip nondeterministic fields from obj.
-++
-++    Rules:
-++    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
-++    - list/tuple: recurse each element, preserve order and type.
-++    - anything else: return as-is.
-++
-++    This function is recursion-safe and deterministic.
-++    It never introduces wall-clock time or randomness.
-++    """
-++    if isinstance(obj, dict):
-++        return {
-++            k: strip_nondeterministic(v)
-++            for k, v in obj.items()
-++            if k not in DETERMINISM_EXCLUDED_FIELDS
-++        }
-++    if isinstance(obj, tuple):
-++        return tuple(strip_nondeterministic(item) for item in obj)
-++    if isinstance(obj, list):
-++        return [strip_nondeterministic(item) for item in obj]
-++    return obj
-++
-++
-++def canonical_hash(obj: Any) -> str:
-++    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).
-++
-++    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
-++    Excluded fields are stripped recursively before hashing.
-++    """
-++    stripped = strip_nondeterministic(obj)
-++    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()
-++
-++
-++def file_hash(path: str | Path) -> str:
-++    """Return sha256 hexdigest of the raw bytes of the file at path."""
-++    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
-+diff --git a/docs/reports/plans/phase_01_shared_determinism_util.md b/docs/reports/plans/phase_01_shared_determinism_util.md
-+new file mode 100644
-+index 000000000..a0f9828da
-+--- /dev/null
-++++ b/docs/reports/plans/phase_01_shared_determinism_util.md
-+@@ -0,0 +1,1095 @@
-++# Phase 1: Shared Determinism Utility — Evidence
-++
-++Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping
-++and deterministic hashing bound to `canonical_bytes()` from the L0 spine.
-++
-++## Scope
-++
-++- New file: `apps_shared/utils/determinism_util.py`
-++- New file: `tests/unit_min_deps/test_determinism_util.py`
-++
-++## Commit Hash
-++
-++<!-- filled after commit -->
-++PENDING
-++
-++## Files Changed
-++
-++- `apps_shared/utils/determinism_util.py` (created)
-++- `tests/unit_min_deps/test_determinism_util.py` (created)
-++- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)
-++- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)
-++
-++## Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py
-++
-++```
-++Exit code: 0
-++
-++[1m============================= test session starts =============================[0m
-++platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
-++rootdir: C:\Git\Agentic-Workflow
-++configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
-++plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
-++asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
-++collected 10 items
-++
-++tests/unit_min_deps/test_determinism_util.py::test_exclusion_top_level [32mPASSED[0m[32m [ 10%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_exclusion_nested_recursive [32mPASSED[0m[32m [ 20%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_list_recursive_preserves_order_and_strips [32mPASSED[0m[32m [ 30%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_list_order_matters [32mPASSED[0m[32m [ 40%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_file_hash_stable [32mPASSED[0m[32m [ 50%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_dict_top_level [32mPASSED[0m[32m [ 60%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_preserves_non_excluded [32mPASSED[0m[32m [ 70%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_tuple_preserved [32mPASSED[0m[32m [ 80%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_deterministic_multiple_calls [32mPASSED[0m[32m [ 90%][0m
-++tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_content_differs [32mPASSED[0m[32m [100%][0m
-++
-++============================ slowest 10 durations =============================
-++
-++(10 durations < 0.005s hidden.  Use -vv to show these durations.)
-++[32m============================= [32m[1m10 passed[0m[32m in 0.03s[0m[32m ==============================[0m
-++```
-++
-++## Command: python -m pytest -q (full suite)
-++
-++```
-++Exit code: 3
-++
-++❌ agent_discovery_full.json not found
-++[1m============================= test session starts =============================[0m
-++platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
-++rootdir: C:\Git\Agentic-Workflow
-++configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
-++testpaths: C:\Git\Agentic-Workflow\tests\enforcement
-++plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
-++asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
-++collected 4501 items / 46 errors
-++INTERNALERROR> Traceback (most recent call last):
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
-++INTERNALERROR>     session.exitstatus = doit(config, session) or 0
-++INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
-++INTERNALERROR>     config.hook.pytest_collection(session=session)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
-++INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
-++INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
-++INTERNALERROR>     raise exception
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-++INTERNALERROR>     teardown.throw(exception)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
-++INTERNALERROR>     return (yield)
-++INTERNALERROR>             ^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-++INTERNALERROR>     teardown.throw(exception)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
-++INTERNALERROR>     return (yield)
-++INTERNALERROR>             ^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-++INTERNALERROR>     teardown.throw(exception)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
-++INTERNALERROR>     return (yield)
-++INTERNALERROR>             ^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
-++INTERNALERROR>     res = hook_impl.function(*args)
-++INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
-++INTERNALERROR>     session.perform_collect()
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
-++INTERNALERROR>     self.items.extend(self.genitems(node))
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-++INTERNALERROR>     yield from self.genitems(subnode)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-++INTERNALERROR>     yield from self.genitems(subnode)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-++INTERNALERROR>     yield from self.genitems(subnode)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
-++INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
-++INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
-++INTERNALERROR>     rep = collect_one_node(node)
-++INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
-++INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
-++INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
-++INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
-++INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
-++INTERNALERROR>     raise exception
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-++INTERNALERROR>     teardown.throw(exception)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
-++INTERNALERROR>     rep = yield
-++INTERNALERROR>           ^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
-++INTERNALERROR>     res = hook_impl.function(*args)
-++INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
-++INTERNALERROR>     call = CallInfo.from_call(
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
-++INTERNALERROR>     result: TResult | None = func()
-++INTERNALERROR>                              ^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
-++INTERNALERROR>     return list(collector.collect())
-++INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
-++INTERNALERROR>     self._register_setup_module_fixture()
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
-++INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
-++INTERNALERROR>     ^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
-++INTERNALERROR>     self._obj = obj = self._getobj()
-++INTERNALERROR>                       ^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
-++INTERNALERROR>     return importtestmodule(self.path, self.config)
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
-++INTERNALERROR>     mod = import_path(
-++INTERNALERROR>           ^^^^^^^^^^^^
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
-++INTERNALERROR>     importlib.import_module(module_name)
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
-++INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
-++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
-++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
-++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
-++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
-++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
-++INTERNALERROR>     exec(co, module.__dict__)
-++INTERNALERROR>   File "C:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
-++INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
-++INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
-++INTERNALERROR>     sys.exit(1)
-++INTERNALERROR> SystemExit: 1
-++
-++[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.34s[0m[31m ========================[0m
-++mainloop: caught unexpected SystemExit!
-++```
-++
-++## Command: git diff --stat HEAD
-++
-++```
-++Exit code: 0
-++
-++ apps_shared/utils/determinism_util.py              |  70 ++++
-++ .../plans/phase_01_shared_determinism_util.md      | 379 +++++++++++++++++++++
-++ tests/unit_min_deps/test_determinism_util.py       | 104 ++++++
-++ .../phase01_determinism_util_evidence_runner.py    | 136 ++++++++
-++ 4 files changed, 689 insertions(+)
-++```
-++
-++## Command: git diff HEAD
-++
-++```
-++Exit code: 0
-++
-++diff --git a/apps_shared/utils/determinism_util.py b/apps_shared/utils/determinism_util.py
-++new file mode 100644
-++index 000000000..1efe1bbe7
-++--- /dev/null
-+++++ b/apps_shared/utils/determinism_util.py
-++@@ -0,0 +1,70 @@
-+++"""
-+++Shared determinism utility for apps_lic and apps_rg.
-+++
-+++Provides canonical hashing and recursive nondeterminism stripping
-+++bound to the canonical_bytes() function from the L0 spine.
-+++
-+++All hashing delegates to:
-+++    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes
-+++
-+++No local canonicalization is performed here.
-+++"""
-+++
-+++from __future__ import annotations
-+++
-+++import hashlib
-+++from pathlib import Path
-+++from typing import Any
-+++
-+++from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes
-+++
-+++DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
-+++    {
-+++        "duration_ms",
-+++        "timestamp",
-+++        "trace_id",
-+++        "cycle_counter",
-+++        "telemetry",
-+++        "created_at",
-+++        "updated_at",
-+++    }
-+++)
-+++
-+++
-+++def strip_nondeterministic(obj: Any) -> Any:
-+++    """Recursively strip nondeterministic fields from obj.
-+++
-+++    Rules:
-+++    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
-+++    - list/tuple: recurse each element, preserve order and type.
-+++    - anything else: return as-is.
-+++
-+++    This function is recursion-safe and deterministic.
-+++    It never introduces wall-clock time or randomness.
-+++    """
-+++    if isinstance(obj, dict):
-+++        return {
-+++            k: strip_nondeterministic(v)
-+++            for k, v in obj.items()
-+++            if k not in DETERMINISM_EXCLUDED_FIELDS
-+++        }
-+++    if isinstance(obj, tuple):
-+++        return tuple(strip_nondeterministic(item) for item in obj)
-+++    if isinstance(obj, list):
-+++        return [strip_nondeterministic(item) for item in obj]
-+++    return obj
-+++
-+++
-+++def canonical_hash(obj: Any) -> str:
-+++    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).
-+++
-+++    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
-+++    Excluded fields are stripped recursively before hashing.
-+++    """
-+++    stripped = strip_nondeterministic(obj)
-+++    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()
-+++
-+++
-+++def file_hash(path: str | Path) -> str:
-+++    """Return sha256 hexdigest of the raw bytes of the file at path."""
-+++    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
-++diff --git a/docs/reports/plans/phase_01_shared_determinism_util.md b/docs/reports/plans/phase_01_shared_determinism_util.md
-++new file mode 100644
-++index 000000000..e7a347a2d
-++--- /dev/null
-+++++ b/docs/reports/plans/phase_01_shared_determinism_util.md
-++@@ -0,0 +1,379 @@
-+++# Phase 1: Shared Determinism Utility — Evidence
-+++
-+++Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping
-+++and deterministic hashing bound to `canonical_bytes()` from the L0 spine.
-+++
-+++## Scope
-+++
-+++- New file: `apps_shared/utils/determinism_util.py`
-+++- New file: `tests/unit_min_deps/test_determinism_util.py`
-+++
-+++## Commit Hash
-+++
-+++<!-- filled after commit -->
-+++PENDING
-+++
-+++## Files Changed
-+++
-+++- `apps_shared/utils/determinism_util.py` (created)
-+++- `tests/unit_min_deps/test_determinism_util.py` (created)
-+++- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)
-+++- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)
-+++
-+++## Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py
-+++
-+++```
-+++Exit code: 0
-+++
-+++[1m============================= test session starts =============================[0m
-+++platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
-+++rootdir: C:\Git\Agentic-Workflow
-+++configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
-+++plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
-+++asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
-+++collected 10 items
-+++
-+++tests/unit_min_deps/test_determinism_util.py::test_exclusion_top_level [32mPASSED[0m[32m [ 10%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_exclusion_nested_recursive [32mPASSED[0m[32m [ 20%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_list_recursive_preserves_order_and_strips [32mPASSED[0m[32m [ 30%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_list_order_matters [32mPASSED[0m[32m [ 40%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_file_hash_stable [32mPASSED[0m[32m [ 50%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_dict_top_level [32mPASSED[0m[32m [ 60%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_preserves_non_excluded [32mPASSED[0m[32m [ 70%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_tuple_preserved [32mPASSED[0m[32m [ 80%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_deterministic_multiple_calls [32mPASSED[0m[32m [ 90%][0m
-+++tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_content_differs [32mPASSED[0m[32m [100%][0m
-+++
-+++============================ slowest 10 durations =============================
-+++
-+++(10 durations < 0.005s hidden.  Use -vv to show these durations.)
-+++[32m============================= [32m[1m10 passed[0m[32m in 0.03s[0m[32m ==============================[0m
-+++```
-+++
-+++
-+++## Command: python -m pytest -q (full suite)
-+++
-+++```
-+++Exit code: 3
-+++
-+++❌ agent_discovery_full.json not found
-+++[1m============================= test session starts =============================[0m
-+++platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
-+++rootdir: C:\Git\Agentic-Workflow
-+++configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
-+++testpaths: C:\Git\Agentic-Workflow\tests\enforcement
-+++plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
-+++asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
-+++collected 4501 items / 46 errors
-+++INTERNALERROR> Traceback (most recent call last):
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
-+++INTERNALERROR>     session.exitstatus = doit(config, session) or 0
-+++INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
-+++INTERNALERROR>     config.hook.pytest_collection(session=session)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
-+++INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
-+++INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
-+++INTERNALERROR>     raise exception
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+++INTERNALERROR>     teardown.throw(exception)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
-+++INTERNALERROR>     return (yield)
-+++INTERNALERROR>             ^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+++INTERNALERROR>     teardown.throw(exception)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
-+++INTERNALERROR>     return (yield)
-+++INTERNALERROR>             ^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+++INTERNALERROR>     teardown.throw(exception)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
-+++INTERNALERROR>     return (yield)
-+++INTERNALERROR>             ^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
-+++INTERNALERROR>     res = hook_impl.function(*args)
-+++INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
-+++INTERNALERROR>     session.perform_collect()
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
-+++INTERNALERROR>     self.items.extend(self.genitems(node))
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-+++INTERNALERROR>     yield from self.genitems(subnode)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-+++INTERNALERROR>     yield from self.genitems(subnode)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
-+++INTERNALERROR>     yield from self.genitems(subnode)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
-+++INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
-+++INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
-+++INTERNALERROR>     rep = collect_one_node(node)
-+++INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
-+++INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
-+++INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
-+++INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
-+++INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
-+++INTERNALERROR>     raise exception
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
-+++INTERNALERROR>     teardown.throw(exception)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
-+++INTERNALERROR>     rep = yield
-+++INTERNALERROR>           ^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
-+++INTERNALERROR>     res = hook_impl.function(*args)
-+++INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
-+++INTERNALERROR>     call = CallInfo.from_call(
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
-+++INTERNALERROR>     result: TResult | None = func()
-+++INTERNALERROR>                              ^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
-+++INTERNALERROR>     return list(collector.collect())
-+++INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
-+++INTERNALERROR>     self._register_setup_module_fixture()
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
-+++INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
-+++INTERNALERROR>     ^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
-+++INTERNALERROR>     self._obj = obj = self._getobj()
-+++INTERNALERROR>                       ^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
-+++INTERNALERROR>     return importtestmodule(self.path, self.config)
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
-+++INTERNALERROR>     mod = import_path(
-+++INTERNALERROR>           ^^^^^^^^^^^^
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
-+++INTERNALERROR>     importlib.import_module(module_name)
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
-+++INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
-+++INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
-+++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
-+++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
-+++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
-+++INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
-+++INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
-+++INTERNALERROR>     exec(co, module.__dict__)
-+++INTERNALERROR>   File "C:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
-+++INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
-+++INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
-+++INTERNALERROR>     sys.exit(1)
-+++INTERNALERROR> SystemExit: 1
-+++
-+++[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.36s[0m[31m ========================[0m
-+++mainloop: caught unexpected SystemExit!
-+++```
-+++
-+++
-+++## Command: git diff --stat HEAD
-+++
-+++```
-+++Exit code: 0
-+++```
-+++
-+++
-+++## Command: git diff HEAD
-+++
-+++```
-+++Exit code: 0
-+++```
-+++
-+++
-+++
-+++## apps_shared/utils/determinism_util.py (verbatim)
-+++
-+++```python
-+++"""
-+++Shared determinism utility for apps_lic and apps_rg.
-+++
-+++Provides canonical hashing and recursive nondeterminism stripping
-+++bound to the canonical_bytes() function from the L0 spine.
-+++
-+++All hashing delegates to:
-+++    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes
-+++
-+++No local canonicalization is performed here.
-+++"""
-+++
-+++from __future__ import annotations
-+++
-+++import hashlib
-+++from pathlib import Path
-+++from typing import Any
-+++
-+++from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes
-+++
-+++DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
-+++    {
-+++        "duration_ms",
-+++        "timestamp",
-+++        "trace_id",
-+++        "cycle_counter",
-+++        "telemetry",
-+++        "created_at",
-+++        "updated_at",
-+++    }
-+++)
-+++
-+++
-+++def strip_nondeterministic(obj: Any) -> Any:
-+++    """Recursively strip nondeterministic fields from obj.
-+++
-+++    Rules:
-+++    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
-+++    - list/tuple: recurse each element, preserve order and type.
-+++    - anything else: return as-is.
-+++
-+++    This function is recursion-safe and deterministic.
-+++    It never introduces wall-clock time or randomness.
-+++    """
-+++    if isinstance(obj, dict):
-+++        return {
-+++            k: strip_nondeterministic(v)
-+++            for k, v in obj.items()
-+++            if k not in DETERMINISM_EXCLUDED_FIELDS
-+++        }
-+++    if isinstance(obj, tuple):
-+++        return tuple(strip_nondeterministic(item) for item in obj)
-+++    if isinstance(obj, list):
-+++        return [strip_nondeterministic(item) for item in obj]
-+++    return obj
-+++
-+++
-+++def canonical_hash(obj: Any) -> str:
-+++    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).
-+++
-+++    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
-+++    Excluded fields are stripped recursively before hashing.
-+++    """
-+++    stripped = strip_nondeterministic(obj)
-+++    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()
-+++
-+++
-+++def file_hash(path: str | Path) -> str:
-+++    """Return sha256 hexdigest of the raw bytes of the file at path."""
-+++    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
-+++
-+++```
-+++
-+++## tests/unit_min_deps/test_determinism_util.py (verbatim)
-+++
-+++```python
-+++"""
-+++Unit tests for apps_shared.utils.determinism_util.
-+++
-+++Verifies:
-+++- Excluded fields are stripped at top level.
-+++- Excluded fields are stripped recursively in nested dicts.
-+++- Lists are recursed and order is preserved.
-+++- file_hash returns stable sha256 of file bytes.
-+++
-+++No network, wall-clock, or randomness used.
-+++"""
-+++
-+++from __future__ import annotations
-+++
-+++import hashlib
-+++
-+++import pytest
-+++
-+++pytestmark = pytest.mark.unit_min_deps
-+++
-+++from apps_shared.utils.determinism_util import (
-+++    DETERMINISM_EXCLUDED_FIELDS,
-+++    canonical_hash,
-+++    file_hash,
-+++    strip_nondeterministic,
-+++)
-+++
-+++
-+++def test_exclusion_top_level():
-+++    """duration_ms value must not affect canonical_hash."""
-+++    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-+++        {"a": 1, "duration_ms": 0}
-+++    )
-+++
-+++
-+++def test_exclusion_nested_recursive():
-+++    """timestamp inside a nested dict must not affect canonical_hash."""
-+++    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
-+++        {"a": {"timestamp": "y", "b": 2}}
-+++    )
-+++
-+++
-+++def test_list_recursive_preserves_order_and_strips():
-+++    """trace_id inside list elements must not affect canonical_hash; order preserved."""
-+++    assert canonical_hash(
-+++        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-+++    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
-+++
-+++
-+++def test_list_order_matters():
-+++    """Different element order must produce different hashes."""
-+++    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-+++        [{"v": 2}, {"v": 1}]
-+++    )
-+++
-+++
-+++def test_file_hash_stable(tmp_path):
-+++    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
-+++    content = b"deterministic content"
-+++    f = tmp_path / "sample.bin"
-+++    f.write_bytes(content)
-+++
-+++    expected = hashlib.sha256(content).hexdigest()
-+++    assert file_hash(f) == expected
-+++
-+++    f.write_bytes(b"different content")
-+++    assert file_hash(f) != expected
-+++
-+++
-+++def test_strip_nondeterministic_dict_top_level():
-+++    """All excluded fields are removed from a flat dict."""
-+++    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
-+++    result = strip_nondeterministic(obj)
-+++    for excluded in DETERMINISM_EXCLUDED_FIELDS:
-+++        assert excluded not in result
-+++    assert result["a"] == 1
-+++    assert result["b"] == 2
-+++
-+++
-+++def test_strip_nondeterministic_preserves_non_excluded():
-+++    """Non-excluded fields survive stripping unchanged."""
-+++    obj = {"x": 42, "y": [1, 2, 3]}
-+++    assert strip_nondeterministic(obj) == obj
-+++
-+++
-+++def test_strip_nondeterministic_tuple_preserved():
-+++    """Tuples are recursed and returned as tuples."""
-+++    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
-+++    result = strip_nondeterministic(obj)
-+++    assert isinstance(result, tuple)
-+++    assert result == ({"v": 1}, {"v": 2})
-+++
-+++
-+++def test_canonical_hash_deterministic_multiple_calls():
-+++    """Same input always produces same hash across multiple calls."""
-+++    obj = {"key": "value", "nested": {"a": 1}}
-+++    h1 = canonical_hash(obj)
-+++    h2 = canonical_hash(obj)
-+++    assert h1 == h2
-+++
-+++
-+++def test_canonical_hash_different_content_differs():
-+++    """Different meaningful content produces different hashes."""
-+++    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
-+++
-+++```
-++diff --git a/tests/unit_min_deps/test_determinism_util.py b/tests/unit_min_deps/test_determinism_util.py
-++new file mode 100644
-++index 000000000..019c8e3cb
-++--- /dev/null
-+++++ b/tests/unit_min_deps/test_determinism_util.py
-++@@ -0,0 +1,104 @@
-+++"""
-+++Unit tests for apps_shared.utils.determinism_util.
-+++
-+++Verifies:
-+++- Excluded fields are stripped at top level.
-+++- Excluded fields are stripped recursively in nested dicts.
-+++- Lists are recursed and order is preserved.
-+++- file_hash returns stable sha256 of file bytes.
-+++
-+++No network, wall-clock, or randomness used.
-+++"""
-+++
-+++from __future__ import annotations
-+++
-+++import hashlib
-+++
-+++import pytest
-+++
-+++pytestmark = pytest.mark.unit_min_deps
-+++
-+++from apps_shared.utils.determinism_util import (
-+++    DETERMINISM_EXCLUDED_FIELDS,
-+++    canonical_hash,
-+++    file_hash,
-+++    strip_nondeterministic,
-+++)
-+++
-+++
-+++def test_exclusion_top_level():
-+++    """duration_ms value must not affect canonical_hash."""
-+++    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-+++        {"a": 1, "duration_ms": 0}
-+++    )
-+++
-+++
-+++def test_exclusion_nested_recursive():
-+++    """timestamp inside a nested dict must not affect canonical_hash."""
-+++    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
-+++        {"a": {"timestamp": "y", "b": 2}}
-+++    )
-+++
-+++
-+++def test_list_recursive_preserves_order_and_strips():
-+++    """trace_id inside list elements must not affect canonical_hash; order preserved."""
-+++    assert canonical_hash(
-+++        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-+++    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
-+++
-+++
-+++def test_list_order_matters():
-+++    """Different element order must produce different hashes."""
-+++    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-+++        [{"v": 2}, {"v": 1}]
-+++    )
-+++
-+++
-+++def test_file_hash_stable(tmp_path):
-+++    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
-+++    content = b"deterministic content"
-+++    f = tmp_path / "sample.bin"
-+++    f.write_bytes(content)
-+++
-+++    expected = hashlib.sha256(content).hexdigest()
-+++    assert file_hash(f) == expected
-+++
-+++    f.write_bytes(b"different content")
-+++    assert file_hash(f) != expected
-+++
-+++
-+++def test_strip_nondeterministic_dict_top_level():
-+++    """All excluded fields are removed from a flat dict."""
-+++    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
-+++    result = strip_nondeterministic(obj)
-+++    for excluded in DETERMINISM_EXCLUDED_FIELDS:
-+++        assert excluded not in result
-+++    assert result["a"] == 1
-+++    assert result["b"] == 2
-+++
-+++
-+++def test_strip_nondeterministic_preserves_non_excluded():
-+++    """Non-excluded fields survive stripping unchanged."""
-+++    obj = {"x": 42, "y": [1, 2, 3]}
-+++    assert strip_nondeterministic(obj) == obj
-+++
-+++
-+++def test_strip_nondeterministic_tuple_preserved():
-+++    """Tuples are recursed and returned as tuples."""
-+++    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
-+++    result = strip_nondeterministic(obj)
-+++    assert isinstance(result, tuple)
-+++    assert result == ({"v": 1}, {"v": 2})
-+++
-+++
-+++def test_canonical_hash_deterministic_multiple_calls():
-+++    """Same input always produces same hash across multiple calls."""
-+++    obj = {"key": "value", "nested": {"a": 1}}
-+++    h1 = canonical_hash(obj)
-+++    h2 = canonical_hash(obj)
-+++    assert h1 == h2
-+++
-+++
-+++def test_canonical_hash_different_content_differs():
-+++    """Different meaningful content produces different hashes."""
-+++    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
-++diff --git a/tools/evidence/phase01_determinism_util_evidence_runner.py b/tools/evidence/phase01_determinism_util_evidence_runner.py
-++new file mode 100644
-++index 000000000..36844be77
-++--- /dev/null
-+++++ b/tools/evidence/phase01_determinism_util_evidence_runner.py
-++@@ -0,0 +1,136 @@
-+++"""
-+++Phase 1 evidence runner — Python-only, shell=False, no PowerShell.
-+++
-+++Executes commands via subprocess argv arrays, captures output,
-+++aborts immediately if any output contains 'pwsh' or 'PowerShell' (case-insensitive).
-+++
-+++Writes evidence to: docs/reports/plans/phase_01_shared_determinism_util.md
-+++"""
-+++
-+++from __future__ import annotations
-+++
-+++import subprocess
-+++import sys
-+++from pathlib import Path
-+++
-+++REPO_ROOT = Path(__file__).resolve().parent.parent.parent
-+++EVIDENCE_PATH = REPO_ROOT / "docs" / "reports" / "plans" / "phase_01_shared_determinism_util.md"
-+++DETERMINISM_UTIL = REPO_ROOT / "apps_shared" / "utils" / "determinism_util.py"
-+++TEST_FILE = REPO_ROOT / "tests" / "unit_min_deps" / "test_determinism_util.py"
-+++
-+++
-+++def run(argv: list[str]) -> tuple[int, str]:
-+++    """Run a command with shell=False, return (returncode, combined output)."""
-+++    result = subprocess.run(
-+++        argv,
-+++        cwd=str(REPO_ROOT),
-+++        capture_output=True,
-+++        shell=False,
-+++    )
-+++    stdout = result.stdout.decode("utf-8", errors="replace")
-+++    stderr = result.stderr.decode("utf-8", errors="replace")
-+++    combined = stdout + stderr
-+++    # Check only stderr for PowerShell invocation evidence.
-+++    # stdout may contain diff/log content that legitimately references "PowerShell" in comments.
-+++    # Strip PS prompt lines (terminal artifacts) before checking.
-+++    stderr_lines = [
-+++        line for line in stderr.splitlines()
-+++        if not line.strip().startswith("PS ")
-+++    ]
-+++    stderr_check = "\n".join(stderr_lines)
-+++    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
-+++        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
-+++        sys.exit(1)
-+++    return result.returncode, combined
-+++
-+++
-+++def section(title: str, content: str) -> str:
-+++    return f"## {title}\n\n```\n{content.strip()}\n```\n\n"
-+++
-+++
-+++def main() -> None:
-+++    outputs: dict[str, tuple[int, str]] = {}
-+++
-+++    print("Running focused pytest (new tests only)...")
-+++    rc1, out1 = run([sys.executable, "-m", "pytest", "-q",
-+++                     "tests/unit_min_deps/test_determinism_util.py"])
-+++    outputs["focused_pytest"] = (rc1, out1)
-+++
-+++    print("Running full suite...")
-+++    rc2, out2 = run([sys.executable, "-m", "pytest", "-q"])
-+++    outputs["full_suite"] = (rc2, out2)
-+++
-+++    print("Running git diff --stat...")
-+++    rc3, out3 = run(["git", "diff", "--stat", "HEAD"])
-+++    outputs["git_diff_stat"] = (rc3, out3)
-+++
-+++    print("Running git diff...")
-+++    rc4, out4 = run(["git", "diff", "HEAD"])
-+++    outputs["git_diff"] = (rc4, out4)
-+++
-+++    determinism_util_content = DETERMINISM_UTIL.read_text(encoding="utf-8")
-+++    test_file_content = TEST_FILE.read_text(encoding="utf-8")
-+++
-+++    focused_rc, focused_out = outputs["focused_pytest"]
-+++    full_rc, full_out = outputs["full_suite"]
-+++    diff_stat_rc, diff_stat_out = outputs["git_diff_stat"]
-+++    diff_rc, diff_out = outputs["git_diff"]
-+++
-+++    nl = "\n"
-+++    sec_focused = section(
-+++        "Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py",
-+++        "Exit code: " + str(focused_rc) + nl + nl + focused_out,
-+++    )
-+++    sec_full = section(
-+++        "Command: python -m pytest -q (full suite)",
-+++        "Exit code: " + str(full_rc) + nl + nl + full_out,
-+++    )
-+++    sec_stat = section(
-+++        "Command: git diff --stat HEAD",
-+++        "Exit code: " + str(diff_stat_rc) + nl + nl + diff_stat_out,
-+++    )
-+++    sec_diff = section(
-+++        "Command: git diff HEAD",
-+++        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
-+++    )
-+++
-+++    md = (
-+++        "# Phase 1: Shared Determinism Utility — Evidence\n\n"
-+++        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping\n"
-+++        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.\n\n"
-+++        "## Scope\n\n"
-+++        "- New file: `apps_shared/utils/determinism_util.py`\n"
-+++        "- New file: `tests/unit_min_deps/test_determinism_util.py`\n\n"
-+++        "## Commit Hash\n\n"
-+++        "<!-- filled after commit -->\n"
-+++        "PENDING\n\n"
-+++        "## Files Changed\n\n"
-+++        "- `apps_shared/utils/determinism_util.py` (created)\n"
-+++        "- `tests/unit_min_deps/test_determinism_util.py` (created)\n"
-+++        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)\n"
-+++        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)\n\n"
-+++        + sec_focused
-+++        + sec_full
-+++        + sec_stat
-+++        + sec_diff
-+++        + "\n## apps_shared/utils/determinism_util.py (verbatim)\n\n"
-+++        "```python\n"
-+++        + determinism_util_content
-+++        + "\n```\n\n"
-+++        "## tests/unit_min_deps/test_determinism_util.py (verbatim)\n\n"
-+++        "```python\n"
-+++        + test_file_content
-+++        + "\n```\n"
-+++    )
-+++
-+++    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
-+++    EVIDENCE_PATH.write_text(md, encoding="utf-8")
-+++    print(f"Evidence written to: {EVIDENCE_PATH}")
-+++
-+++    if focused_rc != 0:
-+++        print("FAIL: focused pytest returned non-zero.", file=sys.stderr)
-+++        sys.exit(focused_rc)
-+++
-+++
-+++if __name__ == "__main__":
-+++    main()
-++```
-++
-++
-++## apps_shared/utils/determinism_util.py (verbatim)
-++
-++```python
-++"""
-++Shared determinism utility for apps_lic and apps_rg.
-++
-++Provides canonical hashing and recursive nondeterminism stripping
-++bound to the canonical_bytes() function from the L0 spine.
-++
-++All hashing delegates to:
-++    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes
-++
-++No local canonicalization is performed here.
-++"""
-++
-++from __future__ import annotations
-++
-++import hashlib
-++from pathlib import Path
-++from typing import Any
-++
-++from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes
-++
-++DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
-++    {
-++        "duration_ms",
-++        "timestamp",
-++        "trace_id",
-++        "cycle_counter",
-++        "telemetry",
-++        "created_at",
-++        "updated_at",
-++    }
-++)
-++
-++
-++def strip_nondeterministic(obj: Any) -> Any:
-++    """Recursively strip nondeterministic fields from obj.
-++
-++    Rules:
-++    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
-++    - list/tuple: recurse each element, preserve order and type.
-++    - anything else: return as-is.
-++
-++    This function is recursion-safe and deterministic.
-++    It never introduces wall-clock time or randomness.
-++    """
-++    if isinstance(obj, dict):
-++        return {
-++            k: strip_nondeterministic(v)
-++            for k, v in obj.items()
-++            if k not in DETERMINISM_EXCLUDED_FIELDS
-++        }
-++    if isinstance(obj, tuple):
-++        return tuple(strip_nondeterministic(item) for item in obj)
-++    if isinstance(obj, list):
-++        return [strip_nondeterministic(item) for item in obj]
-++    return obj
-++
-++
-++def canonical_hash(obj: Any) -> str:
-++    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).
-++
-++    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
-++    Excluded fields are stripped recursively before hashing.
-++    """
-++    stripped = strip_nondeterministic(obj)
-++    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()
-++
-++
-++def file_hash(path: str | Path) -> str:
-++    """Return sha256 hexdigest of the raw bytes of the file at path."""
-++    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
-++
-++```
-++
-++## tests/unit_min_deps/test_determinism_util.py (verbatim)
-++
-++```python
-++"""
-++Unit tests for apps_shared.utils.determinism_util.
-++
-++Verifies:
-++- Excluded fields are stripped at top level.
-++- Excluded fields are stripped recursively in nested dicts.
-++- Lists are recursed and order is preserved.
-++- file_hash returns stable sha256 of file bytes.
-++
-++No network, wall-clock, or randomness used.
-++"""
-++
-++from __future__ import annotations
-++
-++import hashlib
-++
-++import pytest
-++
-++pytestmark = pytest.mark.unit_min_deps
-++
-++from apps_shared.utils.determinism_util import (
-++    DETERMINISM_EXCLUDED_FIELDS,
-++    canonical_hash,
-++    file_hash,
-++    strip_nondeterministic,
-++)
-++
-++
-++def test_exclusion_top_level():
-++    """duration_ms value must not affect canonical_hash."""
-++    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-++        {"a": 1, "duration_ms": 0}
-++    )
-++
-++
-++def test_exclusion_nested_recursive():
-++    """timestamp inside a nested dict must not affect canonical_hash."""
-++    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
-++        {"a": {"timestamp": "y", "b": 2}}
-++    )
-++
-++
-++def test_list_recursive_preserves_order_and_strips():
-++    """trace_id inside list elements must not affect canonical_hash; order preserved."""
-++    assert canonical_hash(
-++        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-++    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
-++
-++
-++def test_list_order_matters():
-++    """Different element order must produce different hashes."""
-++    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-++        [{"v": 2}, {"v": 1}]
-++    )
-++
-++
-++def test_file_hash_stable(tmp_path):
-++    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
-++    content = b"deterministic content"
-++    f = tmp_path / "sample.bin"
-++    f.write_bytes(content)
-++
-++    expected = hashlib.sha256(content).hexdigest()
-++    assert file_hash(f) == expected
-++
-++    f.write_bytes(b"different content")
-++    assert file_hash(f) != expected
-++
-++
-++def test_strip_nondeterministic_dict_top_level():
-++    """All excluded fields are removed from a flat dict."""
-++    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
-++    result = strip_nondeterministic(obj)
-++    for excluded in DETERMINISM_EXCLUDED_FIELDS:
-++        assert excluded not in result
-++    assert result["a"] == 1
-++    assert result["b"] == 2
-++
-++
-++def test_strip_nondeterministic_preserves_non_excluded():
-++    """Non-excluded fields survive stripping unchanged."""
-++    obj = {"x": 42, "y": [1, 2, 3]}
-++    assert strip_nondeterministic(obj) == obj
-++
-++
-++def test_strip_nondeterministic_tuple_preserved():
-++    """Tuples are recursed and returned as tuples."""
-++    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
-++    result = strip_nondeterministic(obj)
-++    assert isinstance(result, tuple)
-++    assert result == ({"v": 1}, {"v": 2})
-++
-++
-++def test_canonical_hash_deterministic_multiple_calls():
-++    """Same input always produces same hash across multiple calls."""
-++    obj = {"key": "value", "nested": {"a": 1}}
-++    h1 = canonical_hash(obj)
-++    h2 = canonical_hash(obj)
-++    assert h1 == h2
-++
-++
-++def test_canonical_hash_different_content_differs():
-++    """Different meaningful content produces different hashes."""
-++    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
-++
-++```
-+diff --git a/tests/unit_min_deps/test_determinism_util.py b/tests/unit_min_deps/test_determinism_util.py
-+new file mode 100644
-+index 000000000..019c8e3cb
-+--- /dev/null
-++++ b/tests/unit_min_deps/test_determinism_util.py
-+@@ -0,0 +1,104 @@
-++"""
-++Unit tests for apps_shared.utils.determinism_util.
-++
-++Verifies:
-++- Excluded fields are stripped at top level.
-++- Excluded fields are stripped recursively in nested dicts.
-++- Lists are recursed and order is preserved.
-++- file_hash returns stable sha256 of file bytes.
-++
-++No network, wall-clock, or randomness used.
-++"""
-++
-++from __future__ import annotations
-++
-++import hashlib
-++
-++import pytest
-++
-++pytestmark = pytest.mark.unit_min_deps
-++
-++from apps_shared.utils.determinism_util import (
-++    DETERMINISM_EXCLUDED_FIELDS,
-++    canonical_hash,
-++    file_hash,
-++    strip_nondeterministic,
-++)
-++
-++
-++def test_exclusion_top_level():
-++    """duration_ms value must not affect canonical_hash."""
-++    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-++        {"a": 1, "duration_ms": 0}
-++    )
-++
-++
-++def test_exclusion_nested_recursive():
-++    """timestamp inside a nested dict must not affect canonical_hash."""
-++    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
-++        {"a": {"timestamp": "y", "b": 2}}
-++    )
-++
-++
-++def test_list_recursive_preserves_order_and_strips():
-++    """trace_id inside list elements must not affect canonical_hash; order preserved."""
-++    assert canonical_hash(
-++        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-++    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
-++
-++
-++def test_list_order_matters():
-++    """Different element order must produce different hashes."""
-++    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-++        [{"v": 2}, {"v": 1}]
-++    )
-++
-++
-++def test_file_hash_stable(tmp_path):
-++    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
-++    content = b"deterministic content"
-++    f = tmp_path / "sample.bin"
-++    f.write_bytes(content)
-++
-++    expected = hashlib.sha256(content).hexdigest()
-++    assert file_hash(f) == expected
-++
-++    f.write_bytes(b"different content")
-++    assert file_hash(f) != expected
-++
-++
-++def test_strip_nondeterministic_dict_top_level():
-++    """All excluded fields are removed from a flat dict."""
-++    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
-++    result = strip_nondeterministic(obj)
-++    for excluded in DETERMINISM_EXCLUDED_FIELDS:
-++        assert excluded not in result
-++    assert result["a"] == 1
-++    assert result["b"] == 2
-++
-++
-++def test_strip_nondeterministic_preserves_non_excluded():
-++    """Non-excluded fields survive stripping unchanged."""
-++    obj = {"x": 42, "y": [1, 2, 3]}
-++    assert strip_nondeterministic(obj) == obj
-++
-++
-++def test_strip_nondeterministic_tuple_preserved():
-++    """Tuples are recursed and returned as tuples."""
-++    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
-++    result = strip_nondeterministic(obj)
-++    assert isinstance(result, tuple)
-++    assert result == ({"v": 1}, {"v": 2})
-++
-++
-++def test_canonical_hash_deterministic_multiple_calls():
-++    """Same input always produces same hash across multiple calls."""
-++    obj = {"key": "value", "nested": {"a": 1}}
-++    h1 = canonical_hash(obj)
-++    h2 = canonical_hash(obj)
-++    assert h1 == h2
-++
-++
-++def test_canonical_hash_different_content_differs():
-++    """Different meaningful content produces different hashes."""
-++    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
-+diff --git a/tools/evidence/phase01_determinism_util_evidence_runner.py b/tools/evidence/phase01_determinism_util_evidence_runner.py
-+new file mode 100644
-+index 000000000..7bda8b39b
-+--- /dev/null
-++++ b/tools/evidence/phase01_determinism_util_evidence_runner.py
-+@@ -0,0 +1,138 @@
-++"""
-++Phase 1 evidence runner — Python-only, shell=False, no PowerShell.
-++
-++Executes commands via subprocess argv arrays, captures output,
-++aborts immediately if any output contains 'pwsh' or 'PowerShell' (case-insensitive).
-++
-++Writes evidence to: docs/reports/plans/phase_01_shared_determinism_util.md
-++"""
-++
-++from __future__ import annotations
-++
-++import subprocess
-++import sys
-++from pathlib import Path
-++
-++REPO_ROOT = Path(__file__).resolve().parent.parent.parent
-++EVIDENCE_PATH = REPO_ROOT / "docs" / "reports" / "plans" / "phase_01_shared_determinism_util.md"
-++DETERMINISM_UTIL = REPO_ROOT / "apps_shared" / "utils" / "determinism_util.py"
-++TEST_FILE = REPO_ROOT / "tests" / "unit_min_deps" / "test_determinism_util.py"
-++
-++
-++def run(argv: list[str]) -> tuple[int, str]:
-++    """Run a command with shell=False, return (returncode, combined output)."""
-++    result = subprocess.run(
-++        argv,
-++        cwd=str(REPO_ROOT),
-++        capture_output=True,
-++        shell=False,
-++    )
-++    stdout = result.stdout.decode("utf-8", errors="replace")
-++    stderr = result.stderr.decode("utf-8", errors="replace")
-++    combined = stdout + stderr
-++    # Check only stderr for PowerShell invocation evidence.
-++    # stdout may contain diff/log content that legitimately references "PowerShell" in comments.
-++    # Strip PS prompt lines (terminal artifacts) before checking.
-++    stderr_lines = [
-++        line for line in stderr.splitlines()
-++        if not line.strip().startswith("PS ")
-++    ]
-++    stderr_check = "\n".join(stderr_lines)
-++    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
-++        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
-++        sys.exit(1)
-++    return result.returncode, combined
-++
-++
-++def section(title: str, content: str) -> str:
-++    return f"## {title}\n\n```\n{content.strip()}\n```\n\n"
-++
-++
-++def main() -> None:
-++    outputs: dict[str, tuple[int, str]] = {}
-++
-++    print("Running focused pytest (new tests only)...")
-++    rc1, out1 = run([sys.executable, "-m", "pytest", "-q",
-++                     "tests/unit_min_deps/test_determinism_util.py"])
-++    outputs["focused_pytest"] = (rc1, out1)
-++
-++    print("Running full suite...")
-++    rc2, out2 = run([sys.executable, "-m", "pytest", "-q"])
-++    outputs["full_suite"] = (rc2, out2)
-++
-++    print("Running git diff --stat...")
-++    rc3, out3 = run(["git", "diff", "--stat", "HEAD"])
-++    outputs["git_diff_stat"] = (rc3, out3)
-++
-++    print("Running git diff...")
-++    rc4, out4 = run(["git", "diff", "HEAD"])
-++    outputs["git_diff"] = (rc4, out4)
-++
-++    determinism_util_content = DETERMINISM_UTIL.read_text(encoding="utf-8")
-++    test_file_content = TEST_FILE.read_text(encoding="utf-8")
-++
-++    focused_rc, focused_out = outputs["focused_pytest"]
-++    full_rc, full_out = outputs["full_suite"]
-++    diff_stat_rc, diff_stat_out = outputs["git_diff_stat"]
-++    diff_rc, diff_out = outputs["git_diff"]
-++
-++    nl = "\n"
-++    sec_focused = section(
-++        "Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py",
-++        "Exit code: " + str(focused_rc) + nl + nl + focused_out,
-++    )
-++    sec_full = section(
-++        "Command: python -m pytest -q (full suite)",
-++        "Exit code: " + str(full_rc) + nl + nl + full_out,
-++    )
-++    sec_stat = section(
-++        "Command: git diff --stat HEAD",
-++        "Exit code: " + str(diff_stat_rc) + nl + nl + diff_stat_out,
-++    )
-++    sec_diff = section(
-++        "Command: git diff HEAD",
-++        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
-++    )
-++
-++    md = (
-++        "# Phase 1: Shared Determinism Utility — Evidence\n\n"
-++        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping\n"
-++        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.\n\n"
-++        "## Scope\n\n"
-++        "- New file: `apps_shared/utils/determinism_util.py`\n"
-++        "- New file: `tests/unit_min_deps/test_determinism_util.py`\n\n"
-++        "## Commit Hash\n\n"
-++        "<!-- filled after commit -->\n"
-++        "PENDING\n\n"
-++        "## Files Changed\n\n"
-++        "- `apps_shared/utils/determinism_util.py` (created)\n"
-++        "- `tests/unit_min_deps/test_determinism_util.py` (created)\n"
-++        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)\n"
-++        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)\n\n"
-++        + sec_focused
-++        + sec_full
-++        + sec_stat
-++        + sec_diff
-++        + "\n## apps_shared/utils/determinism_util.py (verbatim)\n\n"
-++        "```python\n"
-++        + determinism_util_content
-++        + "\n```\n\n"
-++        "## tests/unit_min_deps/test_determinism_util.py (verbatim)\n\n"
-++        "```python\n"
-++        + test_file_content
-++        + "\n```\n"
-++    )
-++
-++    # Strip trailing whitespace from every line so pre-commit hook passes cleanly.
-++    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
-++    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
-++    EVIDENCE_PATH.write_text(md, encoding="utf-8")
-++    print(f"Evidence written to: {EVIDENCE_PATH}")
-++
-++    if focused_rc != 0:
-++        print("FAIL: focused pytest returned non-zero.", file=sys.stderr)
-++        sys.exit(focused_rc)
-++
-++
-++if __name__ == "__main__":
-++    main()
-+```
-+
-+
-+## apps_shared/utils/determinism_util.py (verbatim)
-+
-+```python
-+"""
-+Shared determinism utility for apps_lic and apps_rg.
-+
-+Provides canonical hashing and recursive nondeterminism stripping
-+bound to the canonical_bytes() function from the L0 spine.
-+
-+All hashing delegates to:
-+    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes
-+
-+No local canonicalization is performed here.
-+"""
-+
-+from __future__ import annotations
-+
-+import hashlib
-+from pathlib import Path
-+from typing import Any
-+
-+from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes
-+
-+DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
-+    {
-+        "duration_ms",
-+        "timestamp",
-+        "trace_id",
-+        "cycle_counter",
-+        "telemetry",
-+        "created_at",
-+        "updated_at",
-+    }
-+)
-+
-+
-+def strip_nondeterministic(obj: Any) -> Any:
-+    """Recursively strip nondeterministic fields from obj.
-+
-+    Rules:
-+    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
-+    - list/tuple: recurse each element, preserve order and type.
-+    - anything else: return as-is.
-+
-+    This function is recursion-safe and deterministic.
-+    It never introduces wall-clock time or randomness.
-+    """
-+    if isinstance(obj, dict):
-+        return {
-+            k: strip_nondeterministic(v)
-+            for k, v in obj.items()
-+            if k not in DETERMINISM_EXCLUDED_FIELDS
-+        }
-+    if isinstance(obj, tuple):
-+        return tuple(strip_nondeterministic(item) for item in obj)
-+    if isinstance(obj, list):
-+        return [strip_nondeterministic(item) for item in obj]
-+    return obj
-+
-+
-+def canonical_hash(obj: Any) -> str:
-+    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).
-+
-+    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
-+    Excluded fields are stripped recursively before hashing.
-+    """
-+    stripped = strip_nondeterministic(obj)
-+    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()
-+
-+
-+def file_hash(path: str | Path) -> str:
-+    """Return sha256 hexdigest of the raw bytes of the file at path."""
-+    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
-+
-+```
-+
-+## tests/unit_min_deps/test_determinism_util.py (verbatim)
-+
-+```python
-+"""
-+Unit tests for apps_shared.utils.determinism_util.
-+
-+Verifies:
-+- Excluded fields are stripped at top level.
-+- Excluded fields are stripped recursively in nested dicts.
-+- Lists are recursed and order is preserved.
-+- file_hash returns stable sha256 of file bytes.
-+
-+No network, wall-clock, or randomness used.
-+"""
-+
-+from __future__ import annotations
-+
-+import hashlib
-+
-+import pytest
-+
-+pytestmark = pytest.mark.unit_min_deps
-+
-+from apps_shared.utils.determinism_util import (
-+    DETERMINISM_EXCLUDED_FIELDS,
-+    canonical_hash,
-+    file_hash,
-+    strip_nondeterministic,
-+)
-+
-+
-+def test_exclusion_top_level():
-+    """duration_ms value must not affect canonical_hash."""
-+    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-+        {"a": 1, "duration_ms": 0}
-+    )
-+
-+
-+def test_exclusion_nested_recursive():
-+    """timestamp inside a nested dict must not affect canonical_hash."""
-+    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
-+        {"a": {"timestamp": "y", "b": 2}}
-+    )
-+
-+
-+def test_list_recursive_preserves_order_and_strips():
-+    """trace_id inside list elements must not affect canonical_hash; order preserved."""
-+    assert canonical_hash(
-+        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-+    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
-+
-+
-+def test_list_order_matters():
-+    """Different element order must produce different hashes."""
-+    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-+        [{"v": 2}, {"v": 1}]
-+    )
-+
-+
-+def test_file_hash_stable(tmp_path):
-+    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
-+    content = b"deterministic content"
-+    f = tmp_path / "sample.bin"
-+    f.write_bytes(content)
-+
-+    expected = hashlib.sha256(content).hexdigest()
-+    assert file_hash(f) == expected
-+
-+    f.write_bytes(b"different content")
-+    assert file_hash(f) != expected
-+
-+
-+def test_strip_nondeterministic_dict_top_level():
-+    """All excluded fields are removed from a flat dict."""
-+    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
-+    result = strip_nondeterministic(obj)
-+    for excluded in DETERMINISM_EXCLUDED_FIELDS:
-+        assert excluded not in result
-+    assert result["a"] == 1
-+    assert result["b"] == 2
-+
-+
-+def test_strip_nondeterministic_preserves_non_excluded():
-+    """Non-excluded fields survive stripping unchanged."""
-+    obj = {"x": 42, "y": [1, 2, 3]}
-+    assert strip_nondeterministic(obj) == obj
-+
-+
-+def test_strip_nondeterministic_tuple_preserved():
-+    """Tuples are recursed and returned as tuples."""
-+    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
-+    result = strip_nondeterministic(obj)
-+    assert isinstance(result, tuple)
-+    assert result == ({"v": 1}, {"v": 2})
-+
-+
-+def test_canonical_hash_deterministic_multiple_calls():
-+    """Same input always produces same hash across multiple calls."""
-+    obj = {"key": "value", "nested": {"a": 1}}
-+    h1 = canonical_hash(obj)
-+    h2 = canonical_hash(obj)
-+    assert h1 == h2
-+
-+
-+def test_canonical_hash_different_content_differs():
-+    """Different meaningful content produces different hashes."""
-+    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
-+
-+```
-diff --git a/tests/unit_min_deps/test_determinism_util.py b/tests/unit_min_deps/test_determinism_util.py
-new file mode 100644
-index 000000000..019c8e3cb
---- /dev/null
-+++ b/tests/unit_min_deps/test_determinism_util.py
-@@ -0,0 +1,104 @@
-+"""
-+Unit tests for apps_shared.utils.determinism_util.
-+
-+Verifies:
-+- Excluded fields are stripped at top level.
-+- Excluded fields are stripped recursively in nested dicts.
-+- Lists are recursed and order is preserved.
-+- file_hash returns stable sha256 of file bytes.
-+
-+No network, wall-clock, or randomness used.
-+"""
-+
-+from __future__ import annotations
-+
-+import hashlib
-+
-+import pytest
-+
-+pytestmark = pytest.mark.unit_min_deps
-+
-+from apps_shared.utils.determinism_util import (
-+    DETERMINISM_EXCLUDED_FIELDS,
-+    canonical_hash,
-+    file_hash,
-+    strip_nondeterministic,
-+)
-+
-+
-+def test_exclusion_top_level():
-+    """duration_ms value must not affect canonical_hash."""
-+    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-+        {"a": 1, "duration_ms": 0}
-+    )
-+
-+
-+def test_exclusion_nested_recursive():
-+    """timestamp inside a nested dict must not affect canonical_hash."""
-+    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
-+        {"a": {"timestamp": "y", "b": 2}}
-+    )
-+
-+
-+def test_list_recursive_preserves_order_and_strips():
-+    """trace_id inside list elements must not affect canonical_hash; order preserved."""
-+    assert canonical_hash(
-+        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-+    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
-+
-+
-+def test_list_order_matters():
-+    """Different element order must produce different hashes."""
-+    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-+        [{"v": 2}, {"v": 1}]
-+    )
-+
-+
-+def test_file_hash_stable(tmp_path):
-+    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
-+    content = b"deterministic content"
-+    f = tmp_path / "sample.bin"
-+    f.write_bytes(content)
-+
-+    expected = hashlib.sha256(content).hexdigest()
-+    assert file_hash(f) == expected
-+
-+    f.write_bytes(b"different content")
-+    assert file_hash(f) != expected
-+
-+
-+def test_strip_nondeterministic_dict_top_level():
-+    """All excluded fields are removed from a flat dict."""
-+    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
-+    result = strip_nondeterministic(obj)
-+    for excluded in DETERMINISM_EXCLUDED_FIELDS:
-+        assert excluded not in result
-+    assert result["a"] == 1
-+    assert result["b"] == 2
-+
-+
-+def test_strip_nondeterministic_preserves_non_excluded():
-+    """Non-excluded fields survive stripping unchanged."""
-+    obj = {"x": 42, "y": [1, 2, 3]}
-+    assert strip_nondeterministic(obj) == obj
-+
-+
-+def test_strip_nondeterministic_tuple_preserved():
-+    """Tuples are recursed and returned as tuples."""
-+    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
-+    result = strip_nondeterministic(obj)
-+    assert isinstance(result, tuple)
-+    assert result == ({"v": 1}, {"v": 2})
-+
-+
-+def test_canonical_hash_deterministic_multiple_calls():
-+    """Same input always produces same hash across multiple calls."""
-+    obj = {"key": "value", "nested": {"a": 1}}
-+    h1 = canonical_hash(obj)
-+    h2 = canonical_hash(obj)
-+    assert h1 == h2
-+
-+
-+def test_canonical_hash_different_content_differs():
-+    """Different meaningful content produces different hashes."""
-+    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
+diff --git a/ops_scripts/hooks/landmine_baseline.txt b/ops_scripts/hooks/landmine_baseline.txt
+index 9ea7d3497..f3eaefa37 100644
+--- a/ops_scripts/hooks/landmine_baseline.txt
++++ b/ops_scripts/hooks/landmine_baseline.txt
+@@ -1355,32 +1355,32 @@ apps_shared/validators/talent_signal_enhancer_validator.py:285:silent_swallower:
+ apps_shared/validators/talent_signal_enhancer_validator.py:416:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ apps_shared/validators/validation_context_manager_validator.py:60:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ apps_shared/validators/validation_context_manager_validator.py:68:magic_configuration:Magic configuration: Hardcoded max_depth=3
+-artifacts/consolidation/backups/agentic_core__L1_cognition__reasoning__StrategistAgent.py:49:type_erasure:Type erasure: StrategistAgent.heal_repository returns dict instead of structured type
+-artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py:116:magic_configuration:Magic configuration: Hardcoded max_attempts=2 in function call
+-artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py:174:type_erasure:Type erasure: RgStrategicPlannerAgent.heal_repository returns dict instead of structured type
+-artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py:179:magic_configuration:Magic configuration: Hardcoded max_depth=3
++artifacts/consolidation/backups/agentic_core__L1_cognition__reasoning__StrategistAgent.py:48:type_erasure:Type erasure: StrategistAgent.heal_repository returns dict instead of structured type
++artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py:115:magic_configuration:Magic configuration: Hardcoded max_attempts=2 in function call
++artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py:173:type_erasure:Type erasure: RgStrategicPlannerAgent.heal_repository returns dict instead of structured type
++artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__RgStrategicPlannerAgent.py:178:magic_configuration:Magic configuration: Hardcoded max_depth=3
+ artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__UiValidationAgent.py:165:type_erasure:Type erasure: UiValidationAgent.heal_repository returns dict instead of structured type
+ artifacts/consolidation/backups/agentic_core__L2_execution__reasoning__UiValidationAgent.py:39:type_erasure:Type erasure: UiValidationAgent.execute returns Any instead of structured type
+ artifacts/consolidation/backups/agentic_core__L4_state__reasoning__CartographerAgent.py:107:type_erasure:Type erasure: CartographerAgent.heal_repository returns dict instead of structured type
+-artifacts/consolidation/backups/agentic_core__L5_safety__reasoning__GlobalComplianceAggregatorAgent.py:89:magic_configuration:Magic configuration: Hardcoded max_depth=3
+-artifacts/consolidation/backups/agentic_core__L5_safety__reasoning__OmniContextAgent.py:39:type_erasure:Type erasure: OmniContextAgent.heal_repository returns dict instead of structured type
++artifacts/consolidation/backups/agentic_core__L5_safety__reasoning__GlobalComplianceAggregatorAgent.py:88:magic_configuration:Magic configuration: Hardcoded max_depth=3
++artifacts/consolidation/backups/agentic_core__L5_safety__reasoning__OmniContextAgent.py:38:type_erasure:Type erasure: OmniContextAgent.heal_repository returns dict instead of structured type
+ artifacts/consolidation/backups/agentic_core__L5_safety__reasoning__SemanticMapperAgent.py:27:type_erasure:Type erasure: SemanticMapperAgent.execute returns Any instead of structured type
+ artifacts/consolidation/backups/agentic_core__L5_safety__reasoning__SemanticMapperAgent.py:34:type_erasure:Type erasure: SemanticMapperAgent.heal_repository returns dict instead of structured type
+-artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__CoordinateObservabilityOperationsAgent.py:140:magic_configuration:Magic configuration: Hardcoded max_depth=3
++artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__CoordinateObservabilityOperationsAgent.py:139:magic_configuration:Magic configuration: Hardcoded max_depth=3
+ artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__DeadlockDetectorAgent.py:22:magic_configuration:Magic configuration: Hardcoded max_phase_time=300
+ artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__DeadlockDetectorAgent.py:23:magic_configuration:Magic configuration: Hardcoded heartbeat_interval=30
+ artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__DeadlockDetectorAgent.py:24:magic_configuration:Magic configuration: Hardcoded deadlock_threshold=2
+ artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__DeadlockDetectorAgent.py:61:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__DebateSynthesisAgent.py:137:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:72:magic_configuration:Magic configuration: Hardcoded limit_multiplier=2.0
+-artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__TrackObservabilityCostAgent.py:86:magic_configuration:Magic configuration: Hardcoded max_depth=3
+-artifacts/consolidation/backups/apps_lic__engines__HOP5GenerationAgent.py:285:silent_swallower:Silent exception swallower: catches (bare except) without raise or proper return
+-artifacts/consolidation/backups/apps_lic__engines__Hop1ProfileAnalysisAgent.py:147:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-artifacts/consolidation/backups/apps_lic__engines__Hop1ProfileAnalysisAgent.py:147:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-artifacts/consolidation/backups/apps_lic__engines__Hop1ProfileAnalysisAgent.py:191:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-artifacts/consolidation/backups/apps_lic__engines__Hop2ResearchAgent.py:225:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-artifacts/consolidation/backups/apps_lic__engines__Hop2ResearchAgent.py:287:magic_configuration:Magic configuration: Hardcoded max_age_days=90 in function call
+-artifacts/consolidation/backups/apps_lic__engines__LeadQualityAgent.py:72:type_erasure:Type erasure: LeadQualityAgent.heal_repository returns dict instead of structured type
++artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:71:magic_configuration:Magic configuration: Hardcoded limit_multiplier=2.0
++artifacts/consolidation/backups/agentic_core__L6_observability__reasoning__TrackObservabilityCostAgent.py:85:magic_configuration:Magic configuration: Hardcoded max_depth=3
++artifacts/consolidation/backups/apps_lic__engines__HOP5GenerationAgent.py:284:silent_swallower:Silent exception swallower: catches (bare except) without raise or proper return
++artifacts/consolidation/backups/apps_lic__engines__Hop1ProfileAnalysisAgent.py:146:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
++artifacts/consolidation/backups/apps_lic__engines__Hop1ProfileAnalysisAgent.py:146:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
++artifacts/consolidation/backups/apps_lic__engines__Hop1ProfileAnalysisAgent.py:190:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
++artifacts/consolidation/backups/apps_lic__engines__Hop2ResearchAgent.py:224:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
++artifacts/consolidation/backups/apps_lic__engines__Hop2ResearchAgent.py:286:magic_configuration:Magic configuration: Hardcoded max_age_days=90 in function call
++artifacts/consolidation/backups/apps_lic__engines__LeadQualityAgent.py:71:type_erasure:Type erasure: LeadQualityAgent.heal_repository returns dict instead of structured type
+ artifacts/consolidation/backups/apps_lic__engines__LicReflectionAgent.py:67:type_erasure:Type erasure: LicReflectionAgent.heal_repository returns dict instead of structured type
+ artifacts/consolidation/backups/apps_lic__engines__LicTemplateOptimizerAgent.py:64:type_erasure:Type erasure: LicTemplateOptimizerAgent.heal_repository returns dict instead of structured type
+ artifacts/consolidation/backups/apps_lic__engines__MessageComplianceAgent.py:91:type_erasure:Type erasure: MessageComplianceAgent.heal_repository returns dict instead of structured type
+@@ -1412,36 +1412,23 @@ data/sdks_mcps/validation/validate_mcps.py:170:silent_swallower:Silent exception
+ data/sdks_mcps/validation/validate_mcps.py:217:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ data/sdks_mcps/validation/validate_mcps.py:252:path_fragility:Path fragility: os.chdir() - use pathlib.Path instead
+ data/sdks_mcps/validation/validate_mcps.py:40:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-docs/evidence/run_healmode.py:10:global_mutation:Global mutation: os.environ['AGENTIC_ALLOW_MUTATION_FOR_TESTS'] assignment modifies global state at runtime
+-docs/evidence/run_healmode.py:12:path_fragility:Path fragility: os.path.join() - use pathlib.Path instead
+-docs/evidence/run_healmode.py:32:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-docs/evidence/run_healmode.py:41:path_fragility:Path fragility: os.path.exists() - use pathlib.Path instead
+-docs/evidence/run_healmode.py:45:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-docs/evidence/run_healmode.py:8:global_mutation:Global mutation: sys.path.insert() modifies global state at runtime
++docs/evidence/run_healmode.py:11:path_fragility:Path fragility: os.path.join() - use pathlib.Path instead
++docs/evidence/run_healmode.py:31:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
++docs/evidence/run_healmode.py:40:path_fragility:Path fragility: os.path.exists() - use pathlib.Path instead
++docs/evidence/run_healmode.py:44:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
++docs/evidence/run_healmode.py:7:global_mutation:Global mutation: sys.path.insert() modifies global state at runtime
++docs/evidence/run_healmode.py:7:path_fragility:Path fragility: os.path.dirname() - use pathlib.Path instead
++docs/evidence/run_healmode.py:7:path_fragility:Path fragility: os.path.join() - use pathlib.Path instead
++docs/evidence/run_healmode.py:8:path_fragility:Path fragility: os.chdir() - use pathlib.Path instead
+ docs/evidence/run_healmode.py:8:path_fragility:Path fragility: os.path.dirname() - use pathlib.Path instead
+ docs/evidence/run_healmode.py:8:path_fragility:Path fragility: os.path.join() - use pathlib.Path instead
+-docs/evidence/run_healmode.py:9:path_fragility:Path fragility: os.chdir() - use pathlib.Path instead
+-docs/evidence/run_healmode.py:9:path_fragility:Path fragility: os.path.dirname() - use pathlib.Path instead
+-docs/evidence/run_healmode.py:9:path_fragility:Path fragility: os.path.join() - use pathlib.Path instead
+-docs/evidence/run_legacy_main_domains_capture.py:21:path_fragility:Path fragility: os.chdir() - use pathlib.Path instead
+-docs/evidence/run_legacy_main_domains_capture.py:22:global_mutation:Global mutation: sys.path.insert() modifies global state at runtime
+-docs/evidence/run_legacy_main_domains_capture.py:24:global_mutation:Global mutation: os.environ['AGENTIC_ALLOW_MUTATION_FOR_TESTS'] assignment modifies global state at runtime
+-docs/evidence/run_legacy_main_domains_capture.py:56:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+-docs/evidence/run_legacy_main_domains_capture.py:73:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
++docs/evidence/run_healmode.py:9:global_mutation:Global mutation: os.environ['AGENTIC_ALLOW_MUTATION_FOR_TESTS'] assignment modifies global state at runtime
++docs/evidence/run_legacy_main_domains_capture.py:20:path_fragility:Path fragility: os.chdir() - use pathlib.Path instead
++docs/evidence/run_legacy_main_domains_capture.py:21:global_mutation:Global mutation: sys.path.insert() modifies global state at runtime
++docs/evidence/run_legacy_main_domains_capture.py:23:global_mutation:Global mutation: os.environ['AGENTIC_ALLOW_MUTATION_FOR_TESTS'] assignment modifies global state at runtime
++docs/evidence/run_legacy_main_domains_capture.py:55:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
++docs/evidence/run_legacy_main_domains_capture.py:72:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ docs/reports/sub/_redis_mcp_client_58c437fa0.py:97:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ docs/reports/sub/_test_mcp_seq_7ba2f82b0.py:118:silent_swallower:Silent exception swallower: catches Exception without raise or proper return
+ docs/reports/sub/_test_mcp_seq_7ba2f82b0.py:66:global_mutation:Global mutation: sys.path.insert() modifies global state at runtime
+-system_learning/pipelines/approval_gates.py:163:magic_configuration:Magic configuration: Hardcoded max_surfaces_medium=3
+-system_learning/pipelines/approval_gates.py:164:magic_configuration:Magic configuration: Hardcoded max_delta_low=0.05
+-system_learning/pipelines/approval_gates.py:165:magic_configuration:Magic configuration: Hardcoded max_delta_medium=0.1
+-system_learning/pipelines/approval_gates.py:97:magic_configuration:Magic configuration: Hardcoded high_impact_threshold=3
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+-tools/evidence/phase01_determinism_util_evidence_runner.py:94:path_fragility:Path fragility: String concatenation for path building - use pathlib.Path instead
+ tools/vllm_boundary_client.py:24:magic_configuration:Magic configuration: Hardcoded _default_timeout_seconds=30
 diff --git a/tools/evidence/phase01_determinism_util_evidence_runner.py b/tools/evidence/phase01_determinism_util_evidence_runner.py
-new file mode 100644
-index 000000000..434f25a9e
---- /dev/null
+index 4083c7a76..f2c21ee23 100644
+--- a/tools/evidence/phase01_determinism_util_evidence_runner.py
 +++ b/tools/evidence/phase01_determinism_util_evidence_runner.py
-@@ -0,0 +1,138 @@
-+"""
-+Phase 1 evidence runner — Python-only, shell=False, no PowerShell.
-+
-+Executes commands via subprocess argv arrays, captures output,
-+aborts immediately if any output contains 'pwsh' or 'PowerShell' (case-insensitive).
-+
-+Writes evidence to: docs/reports/plans/phase_01_shared_determinism_util.md
-+"""
-+
-+from __future__ import annotations
-+
-+import subprocess
-+import sys
-+from pathlib import Path
-+
-+REPO_ROOT = Path(__file__).resolve().parent.parent.parent
-+EVIDENCE_PATH = REPO_ROOT / "docs" / "reports" / "plans" / "phase_01_shared_determinism_util.md"
-+DETERMINISM_UTIL = REPO_ROOT / "apps_shared" / "utils" / "determinism_util.py"
-+TEST_FILE = REPO_ROOT / "tests" / "unit_min_deps" / "test_determinism_util.py"
-+
-+
-+def run(argv: list[str]) -> tuple[int, str]:
-+    """Run a command with shell=False, return (returncode, combined output)."""
-+    result = subprocess.run(
-+        argv,
-+        cwd=str(REPO_ROOT),
-+        capture_output=True,
-+        shell=False,
-+    )
-+    stdout = result.stdout.decode("utf-8", errors="replace")
-+    stderr = result.stderr.decode("utf-8", errors="replace")
-+    combined = stdout + stderr
-+    # Check only stderr for PowerShell invocation evidence.
-+    # stdout may contain diff/log content that legitimately references "PowerShell" in comments.
-+    # Strip PS prompt lines (terminal artifacts) before checking.
-+    stderr_lines = [
-+        line for line in stderr.splitlines()
-+        if not line.strip().startswith("PS ")
+@@ -90,30 +90,46 @@ def main() -> None:
+         "Exit code: " + str(diff_rc) + nl + nl + diff_out,
+     )
+
+-    md = (  # guardian: allow-path_fragility
+-        "# Phase 1: Shared Determinism Utility — Evidence\n\n"
+-        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping\n"
+-        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.\n\n"
+-        "## Scope\n\n"
+-        "- New file: `apps_shared/utils/determinism_util.py`\n"
+-        "- New file: `tests/unit_min_deps/test_determinism_util.py`\n\n"
+-        "## Commit Hash\n\n"
+-        "<!-- filled after commit -->\n"
+-        "PENDING\n\n"
+-        "## Files Changed\n\n"
+-        "- `apps_shared/utils/determinism_util.py` (created)\n"
+-        "- `tests/unit_min_deps/test_determinism_util.py` (created)\n"
+-        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)\n"
+-        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)\n\n"
+-        + sec_focused
+-        + sec_full
+-        + sec_stat
+-        + sec_diff
+-        + "\n## apps_shared/utils/determinism_util.py (verbatim)\n\n"
+-        "```python\n" + determinism_util_content + "\n```\n\n"
+-        "## tests/unit_min_deps/test_determinism_util.py (verbatim)\n\n"
+-        "```python\n" + test_file_content + "\n```\n"
+-    )
++    parts = [
++        "# Phase 1: Shared Determinism Utility — Evidence",
++        "",
++        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping",
++        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.",
++        "",
++        "## Scope",
++        "",
++        "- New file: `apps_shared/utils/determinism_util.py`",
++        "- New file: `tests/unit_min_deps/test_determinism_util.py`",
++        "",
++        "## Commit Hash",
++        "",
++        "PENDING",
++        "",
++        "## Files Changed",
++        "",
++        "- `apps_shared/utils/determinism_util.py` (created)",
++        "- `tests/unit_min_deps/test_determinism_util.py` (created)",
++        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)",
++        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)",
++        "",
++        sec_focused,
++        sec_full,
++        sec_stat,
++        sec_diff,
++        "## apps_shared/utils/determinism_util.py (verbatim)",
++        "",
++        "```python",
++        determinism_util_content,
++        "```",
++        "",
++        "## tests/unit_min_deps/test_determinism_util.py (verbatim)",
++        "",
++        "```python",
++        test_file_content,
++        "```",
++        "",
 +    ]
-+    stderr_check = "\n".join(stderr_lines)
-+    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
-+        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
-+        sys.exit(1)
-+    return result.returncode, combined
-+
-+
-+def section(title: str, content: str) -> str:
-+    return f"## {title}\n\n```\n{content.strip()}\n```\n\n"
-+
-+
-+def main() -> None:
-+    outputs: dict[str, tuple[int, str]] = {}
-+
-+    print("Running focused pytest (new tests only)...")
-+    rc1, out1 = run([sys.executable, "-m", "pytest", "-q",
-+                     "tests/unit_min_deps/test_determinism_util.py"])
-+    outputs["focused_pytest"] = (rc1, out1)
-+
-+    print("Running full suite...")
-+    rc2, out2 = run([sys.executable, "-m", "pytest", "-q"])
-+    outputs["full_suite"] = (rc2, out2)
-+
-+    print("Running git diff --stat...")
-+    rc3, out3 = run(["git", "diff", "--stat", "HEAD"])
-+    outputs["git_diff_stat"] = (rc3, out3)
-+
-+    print("Running git diff...")
-+    rc4, out4 = run(["git", "diff", "HEAD"])
-+    outputs["git_diff"] = (rc4, out4)
-+
-+    determinism_util_content = DETERMINISM_UTIL.read_text(encoding="utf-8")
-+    test_file_content = TEST_FILE.read_text(encoding="utf-8")
-+
-+    focused_rc, focused_out = outputs["focused_pytest"]
-+    full_rc, full_out = outputs["full_suite"]
-+    diff_stat_rc, diff_stat_out = outputs["git_diff_stat"]
-+    diff_rc, diff_out = outputs["git_diff"]
-+
-+    nl = "\n"
-+    sec_focused = section(
-+        "Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py",
-+        "Exit code: " + str(focused_rc) + nl + nl + focused_out,
-+    )
-+    sec_full = section(
-+        "Command: python -m pytest -q (full suite)",
-+        "Exit code: " + str(full_rc) + nl + nl + full_out,
-+    )
-+    sec_stat = section(
-+        "Command: git diff --stat HEAD",
-+        "Exit code: " + str(diff_stat_rc) + nl + nl + diff_stat_out,
-+    )
-+    sec_diff = section(
-+        "Command: git diff HEAD",
-+        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
-+    )
-+
-+    md = (
-+        "# Phase 1: Shared Determinism Utility — Evidence\n\n"
-+        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping\n"
-+        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.\n\n"
-+        "## Scope\n\n"
-+        "- New file: `apps_shared/utils/determinism_util.py`\n"
-+        "- New file: `tests/unit_min_deps/test_determinism_util.py`\n\n"
-+        "## Commit Hash\n\n"
-+        "<!-- filled after commit -->\n"
-+        "PENDING\n\n"
-+        "## Files Changed\n\n"
-+        "- `apps_shared/utils/determinism_util.py` (created)\n"
-+        "- `tests/unit_min_deps/test_determinism_util.py` (created)\n"
-+        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)\n"
-+        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)\n\n"
-+        + sec_focused
-+        + sec_full
-+        + sec_stat
-+        + sec_diff
-+        + "\n## apps_shared/utils/determinism_util.py (verbatim)\n\n"
-+        "```python\n"
-+        + determinism_util_content
-+        + "\n```\n\n"
-+        "## tests/unit_min_deps/test_determinism_util.py (verbatim)\n\n"
-+        "```python\n"
-+        + test_file_content
-+        + "\n```\n"
-+    )
-+
-+    # Strip trailing whitespace and enforce LF line endings so pre-commit hooks pass cleanly.
-+    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
-+    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
-+    EVIDENCE_PATH.write_bytes(md.encode("utf-8"))
-+    print(f"Evidence written to: {EVIDENCE_PATH}")
-+
-+    if focused_rc != 0:
-+        print("FAIL: focused pytest returned non-zero.", file=sys.stderr)
-+        sys.exit(focused_rc)
-+
-+
-+if __name__ == "__main__":
-+    main()
++    md = nl.join(parts)
+
+     # Strip trailing whitespace and enforce LF line endings so pre-commit hooks pass cleanly.
+     md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
 ```


@@ -2391,11 +422,7 @@ def strip_nondeterministic(obj: Any) -> Any:
     It never introduces wall-clock time or randomness.
     """
     if isinstance(obj, dict):
-        return {
-            k: strip_nondeterministic(v)
-            for k, v in obj.items()
-            if k not in DETERMINISM_EXCLUDED_FIELDS
-        }
+        return {k: strip_nondeterministic(v) for k, v in obj.items() if k not in DETERMINISM_EXCLUDED_FIELDS}
     if isinstance(obj, tuple):
         return tuple(strip_nondeterministic(item) for item in obj)
     if isinstance(obj, list):
@@ -2452,9 +479,7 @@ from apps_shared.utils.determinism_util import (

 def test_exclusion_top_level():
     """duration_ms value must not affect canonical_hash."""
-    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash(
-        {"a": 1, "duration_ms": 0}
-    )
+    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash({"a": 1, "duration_ms": 0})


 def test_exclusion_nested_recursive():
@@ -2466,16 +491,14 @@ def test_exclusion_nested_recursive():

 def test_list_recursive_preserves_order_and_strips():
     """trace_id inside list elements must not affect canonical_hash; order preserved."""
-    assert canonical_hash(
-        [{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]
-    ) == canonical_hash([{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}])
+    assert canonical_hash([{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]) == canonical_hash(
+        [{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}]
+    )


 def test_list_order_matters():
     """Different element order must produce different hashes."""
-    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash(
-        [{"v": 2}, {"v": 1}]
-    )
+    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash([{"v": 2}, {"v": 1}])


 def test_file_hash_stable(tmp_path):
diff --git a/tools/evidence/phase01_determinism_util_evidence_runner.py b/tools/evidence/phase01_determinism_util_evidence_runner.py
index 4083c7a76..f2c21ee23 100644
--- a/tools/evidence/phase01_determinism_util_evidence_runner.py
+++ b/tools/evidence/phase01_determinism_util_evidence_runner.py
@@ -90,30 +90,46 @@ def main() -> None:
         "Exit code: " + str(diff_rc) + nl + nl + diff_out,
     )

-    md = (  # guardian: allow-path_fragility
-        "# Phase 1: Shared Determinism Utility — Evidence\n\n"
-        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping\n"
-        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.\n\n"
-        "## Scope\n\n"
-        "- New file: `apps_shared/utils/determinism_util.py`\n"
-        "- New file: `tests/unit_min_deps/test_determinism_util.py`\n\n"
-        "## Commit Hash\n\n"
-        "<!-- filled after commit -->\n"
-        "PENDING\n\n"
-        "## Files Changed\n\n"
-        "- `apps_shared/utils/determinism_util.py` (created)\n"
-        "- `tests/unit_min_deps/test_determinism_util.py` (created)\n"
-        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)\n"
-        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)\n\n"
-        + sec_focused
-        + sec_full
-        + sec_stat
-        + sec_diff
-        + "\n## apps_shared/utils/determinism_util.py (verbatim)\n\n"
-        "```python\n" + determinism_util_content + "\n```\n\n"
-        "## tests/unit_min_deps/test_determinism_util.py (verbatim)\n\n"
-        "```python\n" + test_file_content + "\n```\n"
-    )
+    parts = [
+        "# Phase 1: Shared Determinism Utility — Evidence",
+        "",
+        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping",
+        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.",
+        "",
+        "## Scope",
+        "",
+        "- New file: `apps_shared/utils/determinism_util.py`",
+        "- New file: `tests/unit_min_deps/test_determinism_util.py`",
+        "",
+        "## Commit Hash",
+        "",
+        "PENDING",
+        "",
+        "## Files Changed",
+        "",
+        "- `apps_shared/utils/determinism_util.py` (created)",
+        "- `tests/unit_min_deps/test_determinism_util.py` (created)",
+        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)",
+        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)",
+        "",
+        sec_focused,
+        sec_full,
+        sec_stat,
+        sec_diff,
+        "## apps_shared/utils/determinism_util.py (verbatim)",
+        "",
+        "```python",
+        determinism_util_content,
+        "```",
+        "",
+        "## tests/unit_min_deps/test_determinism_util.py (verbatim)",
+        "",
+        "```python",
+        test_file_content,
+        "```",
+        "",
+    ]
+    md = nl.join(parts)

     # Strip trailing whitespace and enforce LF line endings so pre-commit hooks pass cleanly.
     md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
```


## apps_shared/utils/determinism_util.py (verbatim)

```python
"""
Shared determinism utility for apps_lic and apps_rg.

Provides canonical hashing and recursive nondeterminism stripping
bound to the canonical_bytes() function from the L0 spine.

All hashing delegates to:
    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes

No local canonicalization is performed here.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes

DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {
        "duration_ms",
        "timestamp",
        "trace_id",
        "cycle_counter",
        "telemetry",
        "created_at",
        "updated_at",
    }
)


def strip_nondeterministic(obj: Any) -> Any:
    """Recursively strip nondeterministic fields from obj.

    Rules:
    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
    - list/tuple: recurse each element, preserve order and type.
    - anything else: return as-is.

    This function is recursion-safe and deterministic.
    It never introduces wall-clock time or randomness.
    """
    if isinstance(obj, dict):
        return {k: strip_nondeterministic(v) for k, v in obj.items() if k not in DETERMINISM_EXCLUDED_FIELDS}
    if isinstance(obj, tuple):
        return tuple(strip_nondeterministic(item) for item in obj)
    if isinstance(obj, list):
        return [strip_nondeterministic(item) for item in obj]
    return obj


def canonical_hash(obj: Any) -> str:
    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).

    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
    Excluded fields are stripped recursively before hashing.
    """
    stripped = strip_nondeterministic(obj)
    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()


def file_hash(path: str | Path) -> str:
    """Return sha256 hexdigest of the raw bytes of the file at path."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

```

## tests/unit_min_deps/test_determinism_util.py (verbatim)

```python
"""
Unit tests for apps_shared.utils.determinism_util.

Verifies:
- Excluded fields are stripped at top level.
- Excluded fields are stripped recursively in nested dicts.
- Lists are recursed and order is preserved.
- file_hash returns stable sha256 of file bytes.

No network, wall-clock, or randomness used.
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.unit_min_deps

from apps_shared.utils.determinism_util import (
    DETERMINISM_EXCLUDED_FIELDS,
    canonical_hash,
    file_hash,
    strip_nondeterministic,
)


def test_exclusion_top_level():
    """duration_ms value must not affect canonical_hash."""
    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash({"a": 1, "duration_ms": 0})


def test_exclusion_nested_recursive():
    """timestamp inside a nested dict must not affect canonical_hash."""
    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
        {"a": {"timestamp": "y", "b": 2}}
    )


def test_list_recursive_preserves_order_and_strips():
    """trace_id inside list elements must not affect canonical_hash; order preserved."""
    assert canonical_hash([{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]) == canonical_hash(
        [{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}]
    )


def test_list_order_matters():
    """Different element order must produce different hashes."""
    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash([{"v": 2}, {"v": 1}])


def test_file_hash_stable(tmp_path):
    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
    content = b"deterministic content"
    f = tmp_path / "sample.bin"
    f.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert file_hash(f) == expected

    f.write_bytes(b"different content")
    assert file_hash(f) != expected


def test_strip_nondeterministic_dict_top_level():
    """All excluded fields are removed from a flat dict."""
    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
    result = strip_nondeterministic(obj)
    for excluded in DETERMINISM_EXCLUDED_FIELDS:
        assert excluded not in result
    assert result["a"] == 1
    assert result["b"] == 2


def test_strip_nondeterministic_preserves_non_excluded():
    """Non-excluded fields survive stripping unchanged."""
    obj = {"x": 42, "y": [1, 2, 3]}
    assert strip_nondeterministic(obj) == obj


def test_strip_nondeterministic_tuple_preserved():
    """Tuples are recursed and returned as tuples."""
    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
    result = strip_nondeterministic(obj)
    assert isinstance(result, tuple)
    assert result == ({"v": 1}, {"v": 2})


def test_canonical_hash_deterministic_multiple_calls():
    """Same input always produces same hash across multiple calls."""
    obj = {"key": "value", "nested": {"a": 1}}
    h1 = canonical_hash(obj)
    h2 = canonical_hash(obj)
    assert h1 == h2


def test_canonical_hash_different_content_differs():
    """Different meaningful content produces different hashes."""
    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})

```

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

