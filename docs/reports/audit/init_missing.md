============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\amita\AppData\Local\Programs\Python\Python311\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.0, dash-3.3.0, hypothesis-6.148.7, langsmith-0.5.0, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 1 item

tests/guardian/test_import_safety.py::TestNuclearImportSweep::test_init_completeness
=== PHASE 2 MANDATORY: __init__.py Completeness Check ===

  Directories checked: 85
  Missing __init__.py: 32
FAILED

================================== FAILURES ===================================
________________ TestNuclearImportSweep.test_init_completeness ________________

self = <guardian.test_import_safety.TestNuclearImportSweep object at 0x000001B569FE03D0>

    def test_init_completeness(self):
        """
        MANDATORY TEST 4: Verify that every directory with .py files
        contains an __init__.py file.

        Missing __init__.py can cause import failures in certain contexts.
        """
        print("\n=== PHASE 2 MANDATORY: __init__.py Completeness Check ===")

        missing_init: list[str] = []
        checked_dirs = 0

        for directory in self.SOURCE_DIRECTORIES:
            dir_path = PROJECT_ROOT / directory
            if not dir_path.exists():
                continue

            for root, dirs, files in os.walk(dir_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]

                root_path = Path(root)

                # Check if this directory has Python files
                py_files = [f for f in files if f.endswith(".py") and f != "__init__.py"]

                if py_files:
                    checked_dirs += 1

                    # Check for __init__.py
                    init_file = root_path / "__init__.py"
                    if not init_file.exists():
                        rel_path = root_path.relative_to(PROJECT_ROOT)
                        missing_init.append(str(rel_path))

        # Report results
        print(f"\n  Directories checked: {checked_dirs}")
        print(f"  Missing __init__.py: {len(missing_init)}")

        # Track as tech debt with threshold
        KNOWN_MISSING_INIT = 20  # Allow up to 20 known missing __init__.py

        if missing_init:
            if len(missing_init) <= KNOWN_MISSING_INIT:
                print(f"\n[TECH DEBT] {len(missing_init)} directories missing __init__.py:")
                for path in missing_init[:10]:
                    print(f"  - {path}")
                if len(missing_init) > 10:
                    print(f"  ... and {len(missing_init) - 10} more")
            else:
                error_msg = f"MISSING __init__.py EXCEEDS THRESHOLD ({len(missing_init)} > {KNOWN_MISSING_INIT}):\n"
                for path in missing_init[:15]:
                    error_msg += f"  [X] {path}/\n"
>               raise AssertionError(error_msg)
E               AssertionError: MISSING __init__.py EXCEEDS THRESHOLD (32 > 20):
E                 [X] apps_rg\core/
E                 [X] apps_rg\engines\generation/
E                 [X] apps_rg\engines\quality/
E                 [X] apps_rg\engines\refinement/
E                 [X] apps_rg\engines\retrieval/
E                 [X] apps_rg\validation/
E                 [X] apps_lic\domain/
E                 [X] apps_lic\logic_nodes/
E                 [X] apps_lic\scripts/
E                 [X] apps_lic\tools/
E                 [X] agentic_core\base_agents/
E                 [X] agentic_core\L0_maintenance/
E                 [X] agentic_core\L0_maintenance\boot/
E                 [X] agentic_core\L0_maintenance\scripts/
E                 [X] agentic_core\L0_maintenance\scripts\ci/

tests\guardian\test_import_safety.py:977: AssertionError

============================================================
GUARDIAN REPORT GENERATED
============================================================
Report saved to: C:\Git\Agentic-Workflow\guardian_report.txt
Status: FAIL
Failed Tests: 1
============================================================
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 0
Failed: 1
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
=========================== short test summary info ===========================
FAILED tests/guardian/test_import_safety.py::TestNuclearImportSweep::test_init_completeness
============================== 1 failed in 2.55s ==============================
