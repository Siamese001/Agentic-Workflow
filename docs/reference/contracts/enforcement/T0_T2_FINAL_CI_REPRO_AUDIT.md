# Tier 0–2 Final CI / Reproducibility Audit

**Result:** PASSED
**Audited at:** 2026-04-28 (UTC)
**Audit corpus:** `.github/workflows/tier*.yml` + `scripts/verify_tier*.py` +
`agentic_core/runtime/prove_requirements/tier*_runtime_proof_gate.py`.

This audit confirms every Tier 0–2 enforcement / runtime-proof / hardening
gate is wired into a corresponding GitHub Actions workflow, that each
workflow follows the repo's one-workflow-per-gate convention, and that no
workflow runs the full pytest suite, the proof harness, replay machinery,
or an OTEL exporter. Static-evidence enforcement only.

## Caveat

This audit does **not** claim full architecture proof, real replay
execution, real OTEL emission, or that all 150 Step 1 requirements are
enforced. It only validates the wiring and CI surface for the **54
selected requirements** (Tier 0: 17, Tier 1: 15, Tier 2: 22) and the
hardening test count (33).

## Verifier scripts (existence)

| Verifier | Exists |
|---|:---:|
| `scripts/verify_tier0_enforcement_gate.py` | ✅ |
| `scripts/verify_tier0_runtime_proof_gate.py` | ✅ |
| `scripts/verify_tier1_enforcement_gate.py` | ✅ |
| `scripts/verify_tier1_runtime_proof_gate.py` | ✅ |
| `scripts/verify_tier2_enforcement_gate.py` | ✅ |
| `scripts/verify_tier2_runtime_proof_gate.py` | ✅ |
| `scripts/verify_tier_gate_hardening.py` | ✅ |

## GitHub Actions workflows (existence + invariants)

For each workflow, the audit checks 11 invariants:

1. File exists.
2. Triggers on `pull_request` (any branch).
3. Triggers on `push` to `main` or `master`.
4. Uses Python `3.12`.
5. Runs the intended verifier command.
6. Runs no other tier verifier.
7. Does not run the full pytest suite (`pytest tests/`, `python -m pytest tests`).
8. Does not invoke the proof harness (`proof_harness`).
9. Does not invoke replay machinery (`replay_engine`).
10. Does not invoke an OTEL exporter (`otel_emitter`, `otel_harness`,
    `opentelemetry-exporter`, `OTEL_EXPORTER`).
11. For runtime/static-proof gates only: the verifier script invokes
    `tier_fixture_bootstrap.materialize()`.

| Workflow | All 11 invariants |
|---|:---:|
| `tier0-enforcement-gate.yml` | ✅ |
| `tier0-runtime-proof-gate.yml` | ✅ |
| `tier1-enforcement-gate.yml` | ✅ |
| `tier1-runtime-proof-gate.yml` | ✅ |
| `tier2-enforcement-gate.yml` | ✅ |
| `tier2-runtime-proof-gate.yml` | ✅ |
| `tier-gate-hardening.yml` | ✅ |

Per-workflow detail — including each boolean check and any forbidden
tokens found — is captured in the sidecar JSON
(`T0_T2_FINAL_CI_REPRO_AUDIT.json`).

## Local validation results (this audit run)

| Command | Result |
|---|---|
| `python scripts/verify_tier0_enforcement_gate.py` | **READY** |
| `python scripts/verify_tier0_runtime_proof_gate.py` | **READY** (Failed REQ_IDs: []) |
| `python scripts/verify_tier1_enforcement_gate.py` | **READY** |
| `python scripts/verify_tier1_runtime_proof_gate.py` | **READY** (Failed REQ_IDs: []) |
| `python scripts/verify_tier2_enforcement_gate.py` | **READY** |
| `python scripts/verify_tier2_runtime_proof_gate.py` | **READY** (Failed REQ_IDs: []) |
| `python scripts/verify_tier_gate_hardening.py` | **33 passed** |

## Confirmation

No full pytest run, no proof-harness invocation, no replay-machinery
execution, no OTEL exporter, no runtime behavior was executed during
this audit.
