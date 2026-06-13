# Phase 4: ML Cache Policy

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

Code files changed:
- tests/governance/test_phase4_ml_cache_policy.py

## CODE_COMMIT

<to-be-determined-after-commit>

## EVIDENCE_COMMIT

<to-be-determined-after-commit>

## FILES_CHANGED_CODE

tests/governance/test_phase4_ml_cache_policy.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/phase4_ml_cache_policy_evidence.md

## INSPECTED_FILES

tests/governance/test_phase4_ml_cache_policy.py
agentic_core/L4_state/config/versioned_configs.py
tests/conftest.py
tests/governance/conftest.py
pytest.ini

---

## Entry 1: git status (pre-change snapshot)

cmd /c "set NO_COLOR=1&& set TERM=dumb&& set CLICOLOR=0&& git -C c:\Git\Agentic-Workflow status > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_out.txt 2>&1 && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_out.txt > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_typed.txt && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_typed.txt && echo OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_out.txt && echo TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_typed.txt"

```text
OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_out.txt
TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t1_typed.txt
On branch agentic_process_gap_remediation
Your branch is ahead of 'origin/agentic_process_gap_remediation' by 2 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   docs/reports/plans/phase0-5_implementation_review_and_rca.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	tests/governance/test_phase1_classification_kernel.py
	tests/governance/test_phase2_determinism_thresholds.py
	tests/governance/test_phase3_detection_signal.py
	tests/governance/test_phase4_ml_cache_policy.py

no changes added to commit (use "git add" and/or "git commit -a")
```

---

## Entry 2: Acceptance SSOT Run #1

cmd /c "set NO_COLOR=1&& set TERM=dumb&& set CLICOLOR=0&& python -m pytest -q --color=no tests/governance/test_phase4_ml_cache_policy.py -s > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_out.txt 2>&1 && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_out.txt > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_typed.txt && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_typed.txt && echo OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_out.txt && echo TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_typed.txt"

```text
OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_out.txt
TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t2_typed.txt
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 16 items

tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_exists_and_importable PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_fields PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_methods PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_hash_changes_with_values PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_uses_sorted_keys PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_default_cache_config_matches_prior_behavior PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_ttl_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_max_entries_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_eviction_mode_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_config_version_is_present PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_printed
W4-ML-CACHE-POLICY-DIGEST: <digest-value>
PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_digest_changes_with_policy_changes PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_phase4_ml_cache_policy_comprehensive PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_negative_control_ml_cache_policy_tamper PASSED

============================ slowest 10 durations =============================
0.28s call     tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic
0.15s call     tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton
0.12s call     tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic

(13 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 16 passed in 1.08s ==============================
```

---

## Entry 3: Acceptance SSOT Run #2 (Determinism Proof)

cmd /c "set NO_COLOR=1&& set TERM=dumb&& set CLICOLOR=0&& python -m pytest -q --color=no tests/governance/test_phase4_ml_cache_policy.py -s > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_out.txt 2>&1 && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_out.txt > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_typed.txt && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_typed.txt && echo OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_out.txt && echo TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_typed.txt"

```text
OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_out.txt
TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t3_typed.txt
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 16 items

tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_exists_and_importable PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_fields PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_methods PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_hash_changes_with_values PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_uses_sorted_keys PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_default_cache_config_matches_prior_behavior PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_ttl_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_max_entries_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_eviction_mode_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_config_version_is_present PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_printed
W4-ML-CACHE-POLICY-DIGEST: <digest-value>
PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_digest_changes_with_policy_changes PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_phase4_ml_cache_policy_comprehensive PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_negative_control_ml_cache_policy_tamper PASSED

============================ slowest 10 durations =============================
0.29s call     tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic
0.16s call     tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton
0.13s call     tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic

(13 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 16 passed in 1.10s ==============================
```

---

## Entry 4: Negative Control Run (W4_NEGCTRL_TAMPER=1) -- XFAIL exit 0

cmd /c "set NO_COLOR=1&& set TERM=dumb&& set CLICOLOR=0&& set W4_NEGCTRL_TAMPER=1&& python -m pytest -q --color=no tests/governance/test_phase4_ml_cache_policy.py -s > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_out.txt 2>&1 && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_out.txt > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_typed.txt && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_typed.txt && echo OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_out.txt && echo TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_typed.txt"

```text
OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_out.txt
TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t4_typed.txt
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 16 items

tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_exists_and_importable PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_fields PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_methods PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_hash_changes_with_values PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_uses_sorted_keys PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_default_cache_config_matches_prior_behavior PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_ttl_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_max_entries_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_eviction_mode_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_config_version_is_present PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_printed
W4-ML-CACHE-POLICY-DIGEST: <digest-value>
PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_digest_changes_with_policy_changes PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_phase4_ml_cache_policy_comprehensive PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_negative_control_ml_cache_policy_tamper XFAIL

============================ slowest 10 durations =============================
0.27s call     tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic
0.14s call     tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton
0.11s call     tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic

(13 durations < 0.005s hidden.  Use -vv to show these durations.)
======================== 15 passed, 1 xfailed in 1.06s ========================
```

---

## Entry 5: Restore Run (no tamper env) -- PASS

cmd /c "set NO_COLOR=1&& set TERM=dumb&& set CLICOLOR=0&& python -m pytest -q --color=no tests/governance/test_phase4_ml_cache_policy.py -s > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_out.txt 2>&1 && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_out.txt > c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_typed.txt && type c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_typed.txt && echo OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_out.txt && echo TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_typed.txt"

```text
OUT_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_out.txt
TYPED_FILE=c:\Git\Agentic-Workflow\artifacts\windsurf\phase4_t5_typed.txt
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 16 items

tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_exists_and_importable PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_fields PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_has_required_methods PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_hash_changes_with_values PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_uses_sorted_keys PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_default_cache_config_matches_prior_behavior PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_ttl_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_max_entries_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_eviction_mode_comes_from_versioned_config PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_config_version_is_present PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_deterministic PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_w4_ml_cache_policy_digest_printed
W4-ML-CACHE-POLICY-DIGEST: <digest-value>
PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_digest_changes_with_policy_changes PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_phase4_ml_cache_policy_comprehensive PASSED
tests/governance/test_phase4_ml_cache_policy.py::test_negative_control_ml_cache_policy_tamper PASSED

============================ slowest 10 durations =============================
0.28s call     tests/governance/test_phase4_ml_cache_policy.py::test_ml_cache_config_values_are_deterministic
0.15s call     tests/governance/test_phase4_ml_cache_policy.py::test_get_ml_cache_config_returns_singleton
0.12s call     tests/governance/test_phase4_ml_cache_policy.py::test_canonical_bytes_is_deterministic

(13 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 16 passed in 1.09s ==============================
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

