# Hook Failure Outputs - Canonical Escalation Payload Hardening

## Date: 2026-02-24 04:01:00 UTC-05:00

## Context
Attempting to commit canonical escalation payload hardening with scope limited to:
- `agentic_core/L2_execution/scripts/remediation_dispatcher.py`
- `tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py`

## Hook Failure Output (verbatim)

```
git add agentic_core/L2_execution/scripts/remediation_dispatcher.py tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py && git commit -m "hardening: add canonical escalation payload with deterministic audit trail"
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

[BLOCK] Found 2 NEW anti-pattern landmine(s) (out of 1496 total):
  • magic_configuration: 2

[FAIL] healing_provider_adapters.py:79
   [magic_configuration] Magic configuration: Hardcoded max_tokens=2048 in function call
   Evidence: response = client.chat.completions.create(...
   [FIX] Externalize configuration value:

[FAIL] healing_provider_adapters.py:223
   [magic_configuration] Magic configuration: Hardcoded max_output_tokens=2048 in function call
   Evidence: generation_config=genai.types.GenerationConfig(...
   [FIX] Externalize configuration value:

[ACTION] Fix NEW violations or add '# guardian: allow-<pattern>' to whitelist.
         To update baseline with current violations: python ops_scripts/ci/check_anti_patterns.py --write-baseline
```

## Current Git Status

```bash
git status --porcelain
```

Output:
```
 M agentic_core/L2_execution/scripts/remediation_dispatcher.py
 M tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py
```

## Test Results (pytest)

```bash
python -m pytest -q -m unit_min_deps tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py
```

Output:
```
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 101 items / 81 deselected / 20 selected

tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_allowlisted_healer_with_flag_triggers_escalation PASSED                                                                                    [  5%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_failed_without_flag_does_not_escalate PASSED                                                                                               [ 10%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_non_allowlisted_check_id_does_not_escalate PASSED                                                                                          [ 15%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_escalation_context_is_deterministic PASSED                                                                                                 [ 20%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_escalation_context_hint_parsing PASSED                                                                                                     [ 25%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_escalation_context_defaults_on_missing_hint PASSED                                                                                         [ 30%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_escalation_context_extracts_healer_name_from_hint PASSED                                                                                   [ 35%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_tightened_allowlist_blocks_wrong_healer_name PASSED                                                                                        [ 40%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_authoritative_healer_identity_from_registry PASSED                                                                                         [ 45%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_end_to_end_wiring_reaches_adapter_invocation PASSED                                                                                        [ 50%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_strict_parsing_ignores_unknown_keys PASSED                                                                                                 [ 55%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_blast_radius_clamping PASSED                                                                                                               [ 60%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_longer_trace_id_generation PASSED                                                                                                          [ 65%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_escalation_note_contains_trace_id PASSED                                                                                                   [ 70%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_retry_count_forces_gemini_tier PASSED                                                                                                      [ 75%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestProductionEntrypointTierIntegration::test_successful_healer_does_not_trigger_escalation PASSED                                                                                       [ 80%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestCanonicalEscalationPayload::test_deterministic_payload_across_runs PASSED                                                                                                            [ 85%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestCanonicalEscalationPayload::test_negative_control_needs_llm_escalation_false PASSED                                                                                                  [ 90%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestCanonicalEscalationPayload::test_negative_control_allowlist_mismatch PASSED                                                                                                          [ 95%]
tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py::TestCanonicalEscalationPayload::test_payload_decision_reason_retry_threshold PASSED                                                                                                      [100%]

========================================================================================================================================================= slowest 10 durations =========================================================================================================================================================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
================================================================================================================================================== 20 passed, 81 deselected in 0.14s ==================================================================================================================================================
```

## Git Diff of Changes

```bash
git diff --cached --stat
```

Output:
```
 agentic_core/L2_execution/scripts/remediation_dispatcher.py |  77 +++++++++-
 tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py         | 156 +++++++++++++++++++++
 2 files changed, 232 insertions(+), 1 deletion(-)
```

## Analysis

### Problem
The hook failure is caused by pre-existing violations in `healing_provider_adapters.py` which is **outside the agreed scope** for this phase.

### Scope Compliance
✅ Only modified files within scope:
- `agentic_core/L2_execution/scripts/remediation_dispatcher.py`
- `tests/agentic_core/L2_execution/scripts/test_remediation_dispatcher.py`

### Test Compliance
✅ All tests passing: 20 passed, 81 deselected in 0.14s

### Hook Issue
❌ Failing on unrelated file: `healing_provider_adapters.py`
- Lines 79 and 223 have hardcoded configuration values
- These are pre-existing, not caused by current changes

### Required Resolution
The hook system needs to:
1. Not flag pre-existing violations as "NEW", or
2. Allow these specific patterns with guardian comments, or
3. Exclude the adapter file from this check

## Implementation Summary

The canonical escalation payload hardening is complete and tested:
- Added `EscalationDecisionReason` enum
- Added `CanonicalEscalationPayload` dataclass with deterministic serialization
- Updated `_tier_escalate` to generate and include payload in audit notes
- Added 4 comprehensive tests including determinism and negative controls
- All tests pass with 100% success rate

**Blocked by unrelated hook failures.**
