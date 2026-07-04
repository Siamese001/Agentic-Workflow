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

Five apps currently cannot adopt the generic substrate directly.
Instead of silent bypasses, they have `FormalExceptionEntry` records with:
- Machine-readable reason codes (`CIRCULAR_DEPENDENCY`, `REGULATORY_DOMAIN`, `PENDING_MIGRATION`)
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
| Governed app: apps_rg | ✅ GOVERNED | `agentic_core/runtime/entry/apps_rg_dispatch.py` |
| Formal exception: apps_architect | ✅ FORMALIZED | `apps_architect/integrations/governed_architect_exception.py` |
| Formal exception: apps_eval | ✅ FORMALIZED | `apps_eval/integrations/governed_eval_exception.py` |
| Formal exception: apps_lic | ✅ FORMALIZED | `apps_lic/integrations/governed_lic_exception.py` |
| Formal exception: apps_qna | ✅ FORMALIZED | `apps_qna/integrations/governed_qna_exception.py` |
| Formal exception: apps_underwriting_ai | ✅ FORMALIZED | `apps_underwriting_ai/integrations/governed_uw_exception.py` |
| App registry | ✅ COMPLETE | `apps_shared/integrations/app_registry.py` — 0 ad hoc statuses |
| Conformance gate (CONF+EXCF) | ✅ GREEN | 52/52 PASS |
| Behavioral proof harness | ✅ GREEN | Governed apps + formal exception controls |
| Regression baseline | ✅ GREEN | RC01-RC12 PASS |
| Release gate (one command) | ✅ OPERATIONAL | `ops_scripts/ci/run_architecture_proof.py` |
| Architecture proof artifact | ✅ COMPLETE | `docs/architecture/architecture-proof-pack.md` |
| Reviewer guide | ✅ COMPLETE | `docs/architecture/REVIEWER_GUIDE.md` |
| Release readiness register | ✅ COMPLETE | `docs/architecture/RELEASE_READINESS.md` |

---

## Proof suites summary

| Suite | Command | Checks | Status |
|---|---|---|---|
| S1 — Conformance Gate | `ops_scripts/ci/check_governed_app_conformance.py` | 52 (CONF01-08, EXCF01-08) | ✅ PASS |
| S2 — Exception Framework | `tools/eval/retrieval_benchmark.py --exception-framework-proof` | Governed apps + exception controls | ✅ PASS |
| S3 — Regression | `tools/eval/retrieval_benchmark.py --regression-check` | 12 (RC01-12) | ✅ PASS |

### Targeted proof commands

| Command | App / Scope |
|---|---|
| `--penta-app-proof` | Historical grouped proof; prefer `--exception-framework-proof` for current registry status |
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
| GAP-04 | MEDIUM | Keep proof-runner summary prose aligned with current registry counts | No | Platform team |
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
> Three apps governed. Five exceptions formalized. One conformance gate (52/52 PASS).
> One release gate composes S1+S2+S3. Zero ad hoc exception statuses.
> All known gaps tracked, non-blocking, and assigned to next owner.
>
> The registry evidence is reviewer-ready; release decisions remain gated by current command output.
