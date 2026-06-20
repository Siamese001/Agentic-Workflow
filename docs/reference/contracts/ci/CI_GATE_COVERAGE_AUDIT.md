# CI Gate Coverage Audit — Tier 0 / Tier 1 Workflows

Static audit. Confirms each of the five Tier 0 / Tier 1 gate workflows
exists on disk, shares the canonical trigger shape, pins Python 3.12,
runs only its intended verifier command, and never invokes full pytest,
the proof harness, replay machinery, or any OTEL exporter.

This audit is metadata-only. No workflow was executed, no replay
machinery was invoked, no OTEL exporter was run, no proof harness was
run, and no runtime behavior was exercised.

## Result: **PASSED** (5 / 5)

## Audit Invariants

| # | Invariant |
|---|---|
| 1 | Workflow file exists |
| 2 | Triggers on `pull_request` (all branches) |
| 3 | Triggers on `push` to `main` / `master` |
| 4 | `python-version` pinned to `"3.12"` |
| 5 | Runs only its intended verifier command |
| 6 | No full pytest invocation |
| 7 | No proof harness invocation |
| 8 | No replay machinery invocation |
| 9 | No OTEL exporter invocation |

## Per-Workflow Audit Table

| Workflow | Exists | PR | Push main/master | Py 3.12 | Intended Command | Full pytest? | Proof harness? | Replay? | OTEL exporter? | Result |
|---|:---:|:---:|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|
| `tier0-enforcement-gate.yml` | ✅ | ✅ | ✅ | ✅ | `python scripts/verify_tier0_enforcement_gate.py` | NO | NO | NO | NO | **PASSED** |
| `tier0-runtime-proof-gate.yml` | ✅ | ✅ | ✅ | ✅ | `python scripts/verify_tier0_runtime_proof_gate.py` | NO* | NO | NO | NO | **PASSED** |
| `tier1-enforcement-gate.yml` | ✅ | ✅ | ✅ | ✅ | `python scripts/verify_tier1_enforcement_gate.py` | NO | NO | NO | NO | **PASSED** |
| `tier1-runtime-proof-gate.yml` | ✅ | ✅ | ✅ | ✅ | `python scripts/verify_tier1_runtime_proof_gate.py` | NO* | NO | NO | NO | **PASSED** |
| `tier-gate-hardening.yml` | ✅ | ✅ | ✅ | ✅ | `python scripts/verify_tier_gate_hardening.py` | NO* | NO | NO | NO | **PASSED** |

\* The runtime-proof and hardening workflows install `pytest` only as a
dependency for a small, named set of targeted test files invoked by the
verifier script. Each verifier launches pytest against an explicit file
list (or single file), never the whole suite.

## Targeted Test Surface (informational)

| Workflow | Targeted test files (no full-suite collection) |
|---|---|
| `tier0-runtime-proof-gate.yml` | `tests/runtime/test_tier0_gate_schema_invariants.py`, `tests/runtime/test_tier0_l6_firewall_replay.py` |
| `tier1-runtime-proof-gate.yml` | `tests/runtime/test_tier1_runtime_proof_fixtures.py` (when present) |
| `tier-gate-hardening.yml` | `tests/runtime/test_tier_gate_fail_closed_hardening.py` |

## Trigger Shape (canonical for all 5)

```yaml
on:
  pull_request:
    branches: ["**"]
  push:
    branches: [main, master]
```

## Statement

This audit confirms the structural shape of each workflow. It does NOT
claim runtime proof, full-architecture proof, or replay execution. It
confirms only that the five workflows match the declared one-workflow-
per-gate pattern, pin Python 3.12, run a single bounded verifier
command, and do not invoke any forbidden surface (full pytest, proof
harness, replay machinery, OTEL exporter).
