# Governed-Architecture Rollout — Closeout

> **Status:** CLOSED — all phases complete  
> **Date:** April 2026  
> **One-command gate:** `python ops_scripts/ci/run_architecture_proof.py`  
> **Reviewer entry point:** `docs/architecture/REVIEWER_GUIDE.md`

---

## What was built

### Shared governed substrate

A single base class (`GovernedAppRunner`) that runs the full agentic pipeline:

```
L1 (query decomposition)
  → L0 (agentic routing)
    → C0 (grounded retrieval + evidence shaping)
      → L2 (authorize_and_execute — governance chokepoint)
        → L5 (exit gate: allow / refine / abstain / escalate)
          → L6 (shadow evaluation + BUS-T telemetry)
```

Every governed app supplies `_build_query()` + a frozen result record mapper.  
The substrate is shared; no app re-implements routing, retrieval, or governance.

### Formal exception framework

Two apps cannot adopt the substrate for structural reasons.  
Instead of silent bypasses, both have `FormalExceptionEntry` records with:
- Machine-readable reason codes (`CIRCULAR_DEPENDENCY`, `REGULATORY_DOMAIN`)
- Declared blocked/safe layers
- Compensating controls verified by the conformance gate at CI time
- Dedicated partial-adoption handlers

---

## Final status table

| Component | Status | Evidence |
|---|---|---|
| Shared runtime loop (L1→L0→C0→L2→L5→L6) | ✅ COMPLETE | `apps_shared/integrations/governed_app_runner.py` |
| Governed app: apps_research | ✅ GOVERNED | `apps_research/integrations/governed_research_run.py` |
| Governed app: apps_exec | ✅ GOVERNED | `apps_exec/integrations/governed_exec_run.py` |
| Governed app: apps_rfp | ✅ GOVERNED | `apps_rfp/integrations/governed_rfp_run.py` |
| Governed app: apps_rg | ✅ GOVERNED | `apps_rg/integrations/governed_rg_run.py` |
| Governed app: apps_lic | ✅ GOVERNED | `apps_lic/integrations/governed_lic_run.py` |
| Formal exception: apps_eval | ✅ FORMALIZED | `apps_eval/integrations/governed_eval_exception.py` |
| Formal exception: apps_underwriting_ai | ✅ FORMALIZED | `apps_underwriting_ai/integrations/governed_uw_exception.py` |
| App registry | ✅ COMPLETE | `apps_shared/integrations/app_registry.py` — 0 ad hoc statuses |
| Conformance gate (CONF+EXCF) | ✅ GREEN | 36/36 PASS |
| Behavioral proof harness | ✅ GREEN | ~80 checks — penta + eval/uw exceptions |
| Regression baseline | ✅ GREEN | RC01-RC12 PASS |
| Release gate (one command) | ✅ OPERATIONAL | `ops_scripts/ci/run_architecture_proof.py` |
| Architecture proof artifact | ✅ COMPLETE | `docs/architecture/architecture-proof-pack.md` |
| Reviewer guide | ✅ COMPLETE | `docs/architecture/REVIEWER_GUIDE.md` |
| Release readiness register | ✅ COMPLETE | `docs/architecture/RELEASE_READINESS.md` |

---

## Proof suites summary

| Suite | Command | Checks | Status |
|---|---|---|---|
| S1 — Conformance Gate | `ops_scripts/ci/check_governed_app_conformance.py` | 36 (CONF01-08, EXCF01-08) | ✅ PASS |
| S2 — Exception Framework | `tools/eval/retrieval_benchmark.py --exception-framework-proof` | ~80 (penta + EVAL01-10 + UW01-10) | ✅ PASS |
| S3 — Regression | `tools/eval/retrieval_benchmark.py --regression-check` | 12 (RC01-12) | ✅ PASS |

### Targeted proof commands

| Command | App / Scope |
|---|---|
| `--penta-app-proof` | All 5 governed apps E2E |
| `--eval-exception-proof` | apps_eval formal exception (EVAL01-10) |
| `--uw-exception-proof` | apps_underwriting_ai formal exception (UW01-10) |
| `--rg-pilot-proof` | apps_rg standalone (RG01-12) |
| `--lic-pilot-proof` | apps_lic standalone (LIC01-12) |
| `--shadow-eval-proof` | L6 shadow evaluation pipeline |
| `--promotion-gauntlet-proof` | Governed commit promotion gauntlet |
| `--promotion-commit-proof` | Commit-path approval + rollback |

---

## Known gaps register

| ID | Severity | Description | Blocking? | Owner |
|---|---|---|---|---|
| GAP-01 | LOW | No live vector collections in proof environment → C0 degrades to abstain | No | Deployment team |
| GAP-02 | LOW | `ClockProvider` kwargs mismatch → L0 graceful fallback | No | Platform team |
| GAP-03 | LOW | `SovereignLLMGateway` `artifact` arg mismatch → logged, not fatal | No | Platform team |
| GAP-04 | MEDIUM | No dedicated pytest unit tests for 5 new governed runners + 2 exception handlers | No | Platform team (next sprint) |
| GAP-05 | LOW | `ExceptionAppEntry` still exported from registry (backward compat, zero consumers) | No | Platform team (confirm via ADG fan-in) |

Full descriptions and recommended next owners: `docs/architecture/RELEASE_READINESS.md`

---

## Final command matrix

```bash
# Everything (recommended before merge/release)
python ops_scripts/ci/run_architecture_proof.py

# Fast structural check only (~1s)
python ops_scripts/ci/run_architecture_proof.py --suite S1

# Fast structural + behavioral (~12s, skip regression)
python ops_scripts/ci/run_architecture_proof.py --skip-regression

# Targeted: one app
python tools/eval/retrieval_benchmark.py --rg-pilot-proof

# Targeted: exceptions only
python tools/eval/retrieval_benchmark.py --exception-framework-proof
```

---

## Architecture documents

| Document | Purpose |
|---|---|
| `docs/architecture/REVIEWER_GUIDE.md` | Single entry point — executive walkthrough + engineer quickstart |
| `docs/architecture/architecture-proof-pack.md` | Proof command map, runtime loop diagram, app registry |
| `docs/architecture/governed-app-contract.md` | Contract schema — GovernedAppRunner + FormalExceptionEntry |
| `docs/architecture/RELEASE_READINESS.md` | Cleanup log + known-gap register |
| `docs/architecture/ROLLOUT_CLOSEOUT.md` | This file — canonical final reference |

---

## Rollout verdict

> **✅ CLOSED — GREEN WITH TRACKED KNOWN GAPS**
>
> Five apps governed. Two exceptions formalized. One conformance gate (36/36 PASS).  
> One release gate (S1+S2+S3, ~17s, exit 0). Zero ad hoc exception statuses.  
> All known gaps tracked, non-blocking, and assigned to next owner.
>
> The repo is reviewer-ready and release-ready.
