# Phase 9 Evidence: Shadow Router Non-invasive Drift Detection

## Scope
Phase 9 implements a shadow router classifier that observes L0 routing decisions and produces shadow routing suggestions with drift scores, without affecting live traffic. The shadow classifier is strictly non-invasive and emits telemetry to L6 and optionally stores to L4.

## CODE_COMMIT
fc5c1e3d14a7a52bca1a84e513b91ec1e32cd667

EVIDENCE_COMMIT (40-hex): 376f0f52f9f48f500efeedbdfb03c227b35e16ff
SEALED_FROM (40-hex): 8f407269687c0d5c1b93a64decf6570b86f918e4

## EVIDENCE_COMMIT
16c01f6c04cec31a21b46e982d151ec866ca277d

## FILES_CHANGED_CODE
agentic_core/L0_routing/types/shadow_routing_types.py
agentic_core/L0_routing/engines/shadow_router_classifier.py
agentic_core/L0_routing/engines/shadow_routing_wiring.py
tests/unit_min_deps/test_shadow_router_classifier.py
tools/evidence/qwen_migration_phase9_shadow_router_runner.py

## INSPECTED_FILES
agentic_core/L0_routing/types/shadow_routing_types.py
agentic_core/L0_routing/engines/shadow_router_classifier.py
agentic_core/L0_routing/engines/shadow_routing_wiring.py
tests/unit_min_deps/test_shadow_router_classifier.py
tools/evidence/qwen_migration_phase9_shadow_router_runner.py

## Inline Evidence Output (verbatim)

```
=== PHASE 9 EVIDENCE: SHADOW ROUTER ===

TEST_SCOPE=TARGETED
TEST_TARGETS:
  [0]: ['python', '-m', 'pytest', '-q', 'tests/unit_min_deps/test_shadow_router_classifier.py']
SCOPE_JUSTIFICATION:
  - shadow_router_classifier.py added for non-invasive routing drift detection
  - shadow_routing_types.py defines contract for shadow routing decisions
  - shadow_routing_wiring.py wires classifier into L0 as read-only side-channel
PHASE_TOUCHED_FILES:
  agentic_core/L0_routing/types/shadow_routing_types.py
  agentic_core/L0_routing/engines/shadow_router_classifier.py
  agentic_core/L0_routing/engines/shadow_routing_wiring.py
  tests/unit_min_deps/test_shadow_router_classifier.py
  tools/evidence/qwen_migration_phase9_shadow_router_runner.py

git status --porcelain (before):


=== PYTEST TARGET [0] ===
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 8 items

tests/unit_min_deps/test_shadow_router_classifier.py::test_shadow_classifier_non_invasive PASSED [ 12%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_shadow_classifier_determinism PASSED [ 25%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_shadow_routing_wiring_non_invasive
-------------------------------- live log call --------------------------------
2026-02-23 14:50:35 [    INFO] agentic_core.L0_routing.engines.shadow_routing_wiring: Shadow routing telemetry emitted: trace=test-tr
ace-003, observed=human_escalation, shadow=human_escalation, drift=0.0                                                               PASSED                                                                   [ 37%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_shadow_feature_fingerprint_64hex PASSED [ 50%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_shadow_drift_detection PASSED [ 62%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_negative_control_shadow_route_application PASSED [ 75%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_shadow_re_run_determinism_lock PASSED [ 87%]
tests/unit_min_deps/test_shadow_router_classifier.py::test_global_wiring_function
-------------------------------- live log call --------------------------------
2026-02-23 14:50:35 [    INFO] agentic_core.L0_routing.engines.shadow_routing_wiring: Shadow routing telemetry emitted: trace=test-tr
ace-008, observed=route_recovery_budget_overflow, shadow=route_recovery_budget_overflow, drift=0.0                                   PASSED                                                                   [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 8 passed in 0.05s ==============================


=== PASS/FAIL/NEGATIVE CONTROL PROOFS ===
PASS SCENARIO:
  feature_fingerprint=b7859505e68089e2b1f657d840430b630e7014a674e3583f302dfd762d5b7414
OK: feature_fingerprint validated as 64-hex: b7859505e68089e2b1f657d840430b630e7014a674e3583f302dfd762d5b7414
  original_route_unchanged=True
  shadow_route_produced=True
OK: PASS scenario asserted

FAIL SCENARIO:
  observed_route=human_escalation
  shadow_route=standard_validation
  drift_score=0.3
  feature_fingerprint=c5e579e3cb8132ca67a6e6ddb9802ae4e3d3716061f4969f928ad18819343739
OK: feature_fingerprint validated as 64-hex: c5e579e3cb8132ca67a6e6ddb9802ae4e3d3716061f4969f928ad18819343739
  drift_detected=True
OK: FAIL scenario asserted

DETERMINISM RE-RUN LOCK:
  fingerprint_deterministic=True
  route_deterministic=True
  drift_score_deterministic=True
OK: Determinism re-run lock asserted

NEGATIVE CONTROL:
  original_route_unchanged=True
  shadow_route_different=True
  would_fail_if_applied=True
  OK: Shadow route application correctly prevented
OK: NEGATIVE CONTROL asserted
OK: All 1 required hash fields validated: ['feature_fingerprint']

git status --porcelain (final):



=== RUNNER PROOF CHECKLIST ===
- [x] TEST_SCOPE=TARGETED enforced
- [x] All pytest targets executed and passed
- [x] PASS scenario: shadow classifier produces deterministic output
- [x] FAIL scenario: drift detection for suboptimal routes
- [x] DETERMINISM: re-run lock proven with identical fingerprints
- [x] NEGATIVE CONTROL: shadow route application prevented
- [x] Per-hash 64-hex validation lines printed for all fields
- [x] Final git status clean

OK: All governance proofs asserted and passed
```

## Git Status
(clean)
