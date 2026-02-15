============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\amita\AppData\Local\Programs\Python\Python311\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.0, dash-3.3.0, hypothesis-6.148.7, langsmith-0.5.0, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 1 item

tests/guardian/test_ssot_alignment.py::TestSSOTAlignment::test_path_depth_limit
=== PHASE 3 MANDATORY: Path Depth Limit Check ===

  Files checked: 2247
  Maximum depth found: 6
  Depth violations: 82
FAILED

================================== FAILURES ===================================
___________________ TestSSOTAlignment.test_path_depth_limit ___________________

self = <guardian.test_ssot_alignment.TestSSOTAlignment object at 0x000001EF5E9F0B90>

    def test_path_depth_limit(self):
        """
        MANDATORY TEST 4: Assert that no file is nested deeper than 4 sub-directories.

        This prevents deep nesting complexity that makes navigation difficult.
        """
        print("\n=== PHASE 3 MANDATORY: Path Depth Limit Check ===")

        MAX_DEPTH = 4  # Maximum allowed nesting depth

        l4_approved = self.blueprint["L4_APPROVED_FOLDERS"]
        variable_depth = self.blueprint["VARIABLE_DEPTH_SUBFOLDERS"]

        depth_violations: list[dict[str, Any]] = []
        checked_files = 0
        max_depth_found = 0

        python_files = _get_all_python_files(self.EXCLUDED_DIRS)

        for file_path in python_files:
            checked_files += 1

            try:
                rel_path = file_path.relative_to(self.project_root)
            except ValueError:
                continue

            depth = len(rel_path.parts)
            max_depth_found = max(max_depth_found, depth)

            if depth > MAX_DEPTH:
                # Check if this path is in an L4-approved folder
                rel_path_str = str(rel_path).replace("\\", "/")

                is_approved = False
                for approved_folder in l4_approved:
                    if rel_path_str.startswith(approved_folder):
                        is_approved = True
                        break

                # Also check variable depth subfolders
                if not is_approved:
                    for var_folder in variable_depth:
                        if var_folder in rel_path.parts:
                            is_approved = True
                            break

                if not is_approved:
                    depth_violations.append(
                        {
                            "file": str(rel_path),
                            "depth": depth,
                            "max_allowed": MAX_DEPTH,
                        }
                    )

        # Report results
        print(f"\n  Files checked: {checked_files}")
        print(f"  Maximum depth found: {max_depth_found}")
        print(f"  Depth violations: {len(depth_violations)}")

        # Track as tech debt with threshold
        KNOWN_DEPTH_VIOLATIONS = 20  # Allow up to 20 known violations

        if depth_violations:
            if len(depth_violations) <= KNOWN_DEPTH_VIOLATIONS:
                print(
                    f"\n[TECH DEBT] {len(depth_violations)} depth violations (tracked, not blocking):"
                )
                for v in depth_violations[:10]:
                    print(f"  - {v['file']} (depth: {v['depth']})")
                if len(depth_violations) > 10:
                    print(f"  ... and {len(depth_violations) - 10} more")
            else:
                error_msg = f"PATH DEPTH VIOLATIONS EXCEED THRESHOLD ({len(depth_violations)} > {KNOWN_DEPTH_VIOLATIONS}):\n"
                for v in depth_violations[:15]:
                    error_msg += f"  [X] {v['file']} (depth: {v['depth']}, max: {MAX_DEPTH})\n"
>               raise AssertionError(error_msg)
E               AssertionError: PATH DEPTH VIOLATIONS EXCEED THRESHOLD (82 > 20):
E                 [X] tests\e2e\ops_scripts\maintenance\test_canon_key_removal.py (depth: 5, max: 4)
E                 [X] tests\e2e\ops_scripts\maintenance\test_cognitive_subset.py (depth: 5, max: 4)
E                 [X] tests\e2e\ops_scripts\maintenance\test_manifest_completion.py (depth: 5, max: 4)
E                 [X] tests\e2e\ops_scripts\maintenance\test_mro_refactor.py (depth: 5, max: 4)
E                 [X] tests\e2e\ops_scripts\maintenance\test_phase1_verification.py (depth: 5, max: 4)
E                 [X] tests\e2e\ops_scripts\maintenance\__init__.py (depth: 5, max: 4)
E                 [X] tests\integration\apps_lic\engines\test_hop_pipeline_integration.py (depth: 5, max: 4)
E                 [X] tests\integration\apps_lic\engines\__init__.py (depth: 5, max: 4)
E                 [X] tests\integration\apps_rg\engines\test_resume_generation_integration.py (depth: 5, max: 4)
E                 [X] tests\integration\apps_rg\engines\__init__.py (depth: 5, max: 4)
E                 [X] tests\unit\apps_lic\engines\test_accelerated_consolidation.py (depth: 5, max: 4)
E                 [X] tests\unit\apps_lic\engines\test_campaign_balance_agent.py (depth: 5, max: 4)
E                 [X] tests\unit\apps_lic\engines\test_deliverability_agent.py (depth: 5, max: 4)
E                 [X] tests\unit\apps_lic\engines\test_dispatch_outreach_tools_agent.py (depth: 5, max: 4)
E                 [X] tests\unit\apps_lic\engines\test_endgame_certification.py (depth: 5, max: 4)

tests\guardian\test_ssot_alignment.py:550: AssertionError

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
FAILED tests/guardian/test_ssot_alignment.py::TestSSOTAlignment::test_path_depth_limit
============================== 1 failed in 3.52s ==============================
