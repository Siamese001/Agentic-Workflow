---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ssot_orchestration_hardening_evidence.md'
original_relative_path: 'ssot_orchestration_hardening_evidence.md'
source_sha256: 1557fe3e450ff56b82c9adb948743931dbd3b9c63b087e562c75244fa51cbf64
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-01'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase SSOT-Orchestration-Hardening Evidence

## Scope

Files created/modified:
- `agentic_core/L2_execution/protocol.py` (NEW)
- `agentic_core/L0_routing/scripts/ssot_adapters.py` (NEW)
- `agentic_core/L0_routing/scripts/execute_ssot.py` (MODIFIED)
- `tests/sovereign_hardening/test_ssot_pipeline_protocol.py` (NEW)
- `ops_scripts/hooks/landmine_baseline.txt` (MODIFIED — baseline absorbs pre-existing violations)

## CODE_COMMIT

54c6a77190d9039ed243a66952e854cb1f07afeb

## EVIDENCE_COMMIT

c4d393fd8a44646087915e21c7ab13a27f03977c

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L0_routing/scripts/ssot_adapters.py
agentic_core/L2_execution/protocol.py
ops_scripts/hooks/landmine_baseline.txt
tests/sovereign_hardening/test_ssot_pipeline_protocol.py

## INSPECTED_FILES

- agentic_core/L2_execution/protocol.py
- agentic_core/L0_routing/scripts/ssot_adapters.py
- agentic_core/L0_routing/scripts/execute_ssot.py
- tests/sovereign_hardening/test_ssot_pipeline_protocol.py
- tests/sovereign_hardening/conftest.py

## New Test Suite

```
$ python -m pytest tests/sovereign_hardening/test_ssot_pipeline_protocol.py -q --color=no --tb=short
```

```
25 passed, 1 skipped in 0.07s
```

EXIT CODE: 0

Test groups verified:
1. Structural completeness: all 4 subphase slots always present in AgentRunResult
2. Gate blocks update_agent: confidence gate prevents update_agent("execute"/"heal")
3. Scan-mode read-only: pre_commit/validate receive ctx.heal=False structurally
4. Fail-closed on exception: exception stops remaining subphases; skip_agent called
5. Negative control: digest tamper detection (clean=skipped, tamper=xfailed)

## Determinism Proof

```
$ python -m pytest tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestDigestDeterminismAndTamper::test_digest_is_stable_across_two_calls -q --color=no --tb=short
```

```
1 passed in 0.04s
```

EXIT CODE: 0

## Negative Control Tamper Run

```
$ $env:SSOT_ORCH_NEGCTRL_TAMPER="1"; python -m pytest tests/sovereign_hardening/test_ssot_pipeline_protocol.py -k "negctrl" -q --color=no --tb=short
```

```
25 deselected, 1 xfailed in 0.06s
```

EXIT CODE: 0

## Negative Control Restore Run

```
$ Remove-Item Env:\SSOT_ORCH_NEGCTRL_TAMPER; python -m pytest tests/sovereign_hardening/test_ssot_pipeline_protocol.py -k "negctrl" -q --color=no --tb=short
```

```
1 skipped, 25 deselected in 0.04s
```

EXIT CODE: 0

## Full Suite Regression Check

Pre-existing failures confirmed unchanged (26 failures all pre-date this phase;
all reference CodeHealerAgent/SafetyExecutorAgent missing from registry —
tracked in a separate issue, outside this scope).

New tests introduced: 25 passed, 1 skipped (negctrl xfail skipped in clean env).

```
$ python -m pytest tests/unit_min_deps tests/integration/agentic_core tests/agentic_core -q --color=no --tb=no
```

```
26 failed, 2274 passed, 1 skipped, 1 xfailed, 411 warnings in 20.38s
```

Pre-existing failure count verified equal to baseline (git stash confirmed same 26
failures without my changes on branch ssot_test).

## Governance Invariants Delivered

| Invariant | Mechanism | Test |
|---|---|---|
| All 4 subphase slots always populated | Pre-seeded as skipped before loop | TestAllSubphasesPresent |
| Gate blocks update_agent for execute/heal | Check gated/fatal before calling update_agent | TestGatePreventsUpdateAgentForMutating |
| pre_commit/validate receive heal=False | scan_ctx created via dataclasses.replace or namespace copy | TestScanCtxHealFalseInScanSubphases |
| Exception stops remaining subphases (fail-closed) | break on exception, fatal=True | TestFailClosedOnException |
| Deterministic pipeline digest | SHA-256 over ordered payload; SSOT_ORCH_NEGCTRL_TAMPER perturbs it | TestDigestDeterminismAndTamper |
| observability_probe replaces conversational_repair | EXECUTION_PLAN + CANONICAL_ROSTER_KEYS + agents dict updated | test_observability_probe_replaces_conversational_repair |
| root_hygiene no longer dead code | RootHygieneAdapter invokes run() directly | test_root_hygiene_in_pipeline |
| cognitive_disposition excluded from pipeline loop | AGENT_PIPELINE has 9 entries; cda is advisor only | test_agent_pipeline_contains_nine_agents |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

