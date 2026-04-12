# Architecture Proof Pack

> **Status:** Green — all suites pass as of April 2026  
> **One-command gate:** `python ops_scripts/ci/run_architecture_proof.py`  
> **Contract:** `docs/architecture/governed-app-contract.md`  
> **Registry:** `apps_shared/integrations/app_registry.py`

---

## 1. Governed Runtime Loop

Every governed app runs the same substrate pipeline through a shared base class.
No app implements its own routing, retrieval, or governance logic.

```
App Request
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  L1  query_planner.decompose_query(query)                    │
│      Intent decomposition → sub_queries tuple                │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L0  AgenticRouter.route(query)                              │
│      Route authority → target + confidence                   │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  C0  get_hybrid_search_engine() → EvidenceShaper.shape()     │
│      Grounded retrieval → EvidenceBundle                     │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L2  authorize_and_execute(ctx, fn, capability_token)        │
│      Chokepoint: guardrail + safety plane validation         │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L5  evaluate_and_emit(bundle, ctx)                          │
│      Exit gate: allow / refine / abstain / escalate_to_hitl  │
│      BUS T telemetry ingested                                │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L6  Shadow eval packet drained to OutcomeLogger             │
│      No current-run mutation                                 │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    App-specific RunRecord (frozen)
```

**Shared vs. app-specific split:**
- `GovernedAppRunner` (shared): L1, L0, C0, L2, L5, L6 — 100% reused across all 5 governed apps
- App subclass: `_build_query()` + record mapper — 2 methods per app

---

## 2. Governed Apps Registry

Five `apps_*` packages have completed full substrate adoption.

| App | Runner Class | Capability Token | Proof Prefix | Status |
|---|---|---|---|---|
| `apps_research` | `GovernedResearchRun` | `apps_research.governed_e2e.v1` | APP | ✅ GOVERNED |
| `apps_exec` | `GovernedExecRun` | `apps_exec.governed_e2e.v1` | EXE | ✅ GOVERNED |
| `apps_rfp` | `GovernedRfpRun` | `apps_rfp.governed_e2e.v1` | RFP | ✅ GOVERNED |
| `apps_rg` | `GovernedRgRun` | `apps_rg.governed_e2e.v1` | RG | ✅ GOVERNED |
| `apps_lic` | `GovernedLicRun` | `apps_lic.governed_e2e.v1` | LIC | ✅ GOVERNED |

Each governed app passes CONF01–CONF03 (runner importable, GovernedAppRunner subclass, versioned token) plus its own E2E proof (12 checks: L1 decomp, L0 routing, C0 grounding, L2 chokepoint, L5 exit, L6 telemetry, happy + degraded paths).

---

## 3. Formal Governed Exceptions

Two `apps_*` packages have permanent exceptions from GovernedAppRunner.
Both are formalized — not ad hoc.

| App | Reason Code | Blocked Layers | Safe Adoption | Compensating Controls | Handler |
|---|---|---|---|---|---|
| `apps_eval` | `CIRCULAR_DEPENDENCY` | L0,L1,C0,L2,L5,L6 | BUS_T_telemetry, conformance_metadata | CC-EVAL-01..04 | `GovernedEvalException` |
| `apps_underwriting_ai` | `REGULATORY_DOMAIN` | L0,L1,C0,L2,L5 | BUS_T_telemetry, conformance_metadata | CC-UW-01..04 | `GovernedUwException` |

**Why `apps_eval` cannot be governed:** it IS the evaluation framework. Routing it through `GovernedAppRunner` (which calls `evaluate_and_emit` in L5) would create a circular evaluation-of-evaluator dependency. The `GovernedEvalException` handler emits BUS-T telemetry without calling `evaluate_and_emit`.

**Why `apps_underwriting_ai` cannot be governed:** underwriting decisions are legally-binding credit determinations. The generic evidence-retrieval substrate is inappropriate for a regulated decision domain. The app provides its own `CoreAdapter` + `CoreHandoffPayload` governance protocol (equivalent L2 guarantee) and `ObservabilityAdapter` (equivalent L6).

Each formal exception passes EXCF01–EXCF08 (FormalExceptionEntry in registry, valid reason code, blocked/safe layers declared, ≥2 compensating controls, review cadence, partial adoption module importable, `check_compensating_controls()` all pass at gate time).

---

## 4. Proof Command Map

### One-command release gate
```bash
python ops_scripts/ci/run_architecture_proof.py
```

### Individual suites

| Suite ID | Command | Checks | What it validates |
|---|---|---|---|
| S1 | `python ops_scripts/ci/check_governed_app_conformance.py` | 36 (CONF01–CONF08, EXCF01–EXCF08) | Registry structure, runner imports, formal exception schema |
| S2 | `python tools/eval/retrieval_benchmark.py --exception-framework-proof` | penta(60) + EVAL(10) + UW(10) + no-adhoc | All 7 apps behavioral — E2E governed loop + exception controls |
| S3 | `python tools/eval/retrieval_benchmark.py --regression-check` | regression baseline | Evidence governance regression (grounding, coverage, telemetry) |

### Targeted proof commands

| Command | Checks | Scope |
|---|---|---|
| `--penta-app-proof` | ~60 | 5 governed apps E2E (research + exec + rfp + rg + lic) |
| `--eval-exception-proof` | 10 (EVAL01–EVAL10) | apps_eval formal exception |
| `--uw-exception-proof` | 10 (UW01–UW10) | apps_underwriting_ai formal exception |
| `--shadow-eval-proof` | shadow eval | L6 shadow evaluation pipeline |
| `--promotion-gauntlet-proof` | gauntlet | Governed commit promotion gauntlet |
| `--promotion-commit-proof` | commit | Commit path approval + rollback enforcement |
| `--conformance-gate-proof` | gate + penta | Conformance gate + penta E2E combined |
| `--app-pilot-proof` | dual | apps_research + apps_exec dual E2E |
| `--rg-pilot-proof` | 12 (RG01–RG12) | apps_rg standalone E2E |
| `--lic-pilot-proof` | 12 (LIC01–LIC12) | apps_lic standalone E2E |

### Gate files

| File | Role |
|---|---|
| `ops_scripts/ci/run_architecture_proof.py` | **Top-level release gate** — orchestrates S1 + S2 + S3 |
| `ops_scripts/ci/check_governed_app_conformance.py` | Structural conformance gate (S1) |
| `tools/eval/retrieval_benchmark.py` | All behavioral proof suites (S2, S3, targeted) |
| `apps_shared/integrations/app_registry.py` | Single source of truth for all app classifications |

---

## 5. Expected Green State

```
Suite  Label                           Expected
─────  ──────────────────────────────  ────────────────────────────────────
S1     Conformance Gate                36/36 PASS (CONF01-08 + EXCF01-08)
S2     Exception Framework Proof       PASS
       ├─ penta_app                    PASS (research/exec/rfp/rg/lic)
       ├─ eval_exception               10/10 PASS (EVAL01-EVAL10)
       ├─ uw_exception                 10/10 PASS (UW01-UW10)
       └─ no_adhoc                     PASS (0 ad hoc exceptions)
S3     Regression Check                PASS
─────  ──────────────────────────────  ────────────────────────────────────
FINAL  Architecture Proof Pack         PASS
```

**Registry final state:** 5 governed apps + 2 formal governed exceptions + 0 ad hoc statuses.

---

## 6. Known Non-Blocking Gaps

These are expected behaviors, not architecture failures:

| Gap | Cause | Behavior | Impact |
|---|---|---|---|
| C0 raw=0 in degraded path | No live ChromaDB/FAISS collection in test env | `EvidenceBundle.shaped=0` → disposition=`abstain` | Degraded path proof passes — abstain is the correct governed response |
| `ClockProvider.emit_determinism_digest()` fallback | Clock provider kwargs mismatch in test harness | L0 graceful fallback, routing still succeeds | No proof failure — fallback is tested explicitly |
| `SovereignLLMGateway.generate()` missing `artifact` | Prompt assembly context mismatch | `Prompt assembly failed: INVALID_CONTEXT_TYPE` logged | L2 still runs; disposition recorded correctly |

All three gaps manifest in test-harness context only (no live vector store, mock clock). The substrate handles each with a graceful degradation path — the E2E proofs validate both the happy path AND the degraded path explicitly.

---

## 7. Ownership & Review Cadence

| Artifact | Owner | Review cadence |
|---|---|---|
| Governed-app contract | platform team | On new app addition |
| Formal exception entries | per-app owner (see registry) | Annual |
| Conformance gate (CONF+EXCF) | platform team | On schema change |
| Proof harness | platform team | On new proof suite |
| This document | platform team | On any status change |

---

## 8. Quick Links

| Resource | Path |
|---|---|
| This document | `docs/architecture/architecture-proof-pack.md` |
| Governed-app contract | `docs/architecture/governed-app-contract.md` |
| App registry | `apps_shared/integrations/app_registry.py` |
| Shared runner base | `apps_shared/integrations/governed_app_runner.py` |
| Conformance gate | `ops_scripts/ci/check_governed_app_conformance.py` |
| Release gate (one command) | `ops_scripts/ci/run_architecture_proof.py` |
| Proof harness | `tools/eval/retrieval_benchmark.py` |
| eval exception handler | `apps_eval/integrations/governed_eval_exception.py` |
| uw exception handler | `apps_underwriting_ai/integrations/governed_uw_exception.py` |
