# Architecture Proof Pack

> **Status:** Registry-aligned proof pack; run the command below for current green/fail state.
> **One-command gate:** `python ops_scripts/ci/run_architecture_proof.py`  
> **Contract:** `docs/architecture/governed-app-contract.md`  
> **Registry:** `apps_shared/integrations/app_registry.py`

---

## 1. Governed Runtime Loop

Governed entries run the shared substrate pipeline through a common governed entrypoint.
Formal exceptions are declared in the same registry with compensating controls.

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
- Governed entrypoint: L1, L0, C0, L2, L5, L6 control points reused across governed entries
- App subclass: `_build_query()` + record mapper — 2 methods per app

---

## 2. Governed Apps Registry

`apps_shared/integrations/app_registry.py` is the source of truth for current app classification.

| App | Runner Class | Capability Token | Proof Prefix | Status |
|---|---|---|---|---|
| `apps_research` | `GovernedResearchRun` | `apps_research.governed_e2e.v1` | APP | ✅ GOVERNED |
| `apps_exec` | `GovernedExecRun` | `apps_exec.governed_e2e.v1` | EXE | ✅ GOVERNED |
| `apps_rg` | `dispatch_apps_rg_run` | `apps_rg.canonical_dispatch.e2e.v1` | RG | ✅ GOVERNED |

Governed entries are expected to pass CONF01–CONF03 (runner importable, governed entrypoint shape, versioned token) plus their E2E proof path.

---

## 3. Formal Governed Exceptions

Five `apps_*` packages have formal exceptions from GovernedAppRunner or the generic governed substrate.
Each is formalized — not ad hoc.

| App | Reason Code | Blocked Layers | Safe Adoption | Compensating Controls | Handler |
|---|---|---|---|---|---|
| `apps_architect` | `PENDING_MIGRATION` | GovernedAppRunner | apps_shared.spine_emission, cert_fec_producer | CC-ARCH-01..02 | `GovernedArchitectException` |
| `apps_eval` | `CIRCULAR_DEPENDENCY` | L0,L1,C0,L2,L5,L6 | BUS_T_telemetry, conformance_metadata | CC-EVAL-01..04 | `GovernedEvalException` |
| `apps_lic` | `PENDING_MIGRATION` | GovernedAppRunner, GovernedLicRun | canonical_dispatch, agentic_core spine bindings | CC-LIC-01..02 | `GovernedLicException` |
| `apps_qna` | `PENDING_MIGRATION` | GovernedAppRunner | ValidatedRequest spine_handoff, runtime bindings | CC-QNA-01..02 | `GovernedQnaException` |
| `apps_underwriting_ai` | `REGULATORY_DOMAIN` | L0,L1,C0,L2,L5 | BUS_T_telemetry, conformance_metadata | CC-UW-01..04 | `GovernedUwException` |

**Why `apps_architect` is an exception:** the product scan is currently wrapped by `apps_shared.spine_emission.governed_run` and emits cert FEC evidence, but it does not expose a `GovernedAppRunner` subclass yet.

**Why `apps_eval` cannot be governed:** it IS the evaluation framework. Routing it through `GovernedAppRunner` (which calls `evaluate_and_emit` in L5) would create a circular evaluation-of-evaluator dependency. The `GovernedEvalException` handler emits BUS-T telemetry without calling `evaluate_and_emit`.

**Why `apps_lic` is an exception:** the product runtime uses the canonical-dispatch spine (`run_canonical_apps_lic_spine`) rather than `GovernedAppRunner`; the registry records the safe adopted layers and compensating controls.

**Why `apps_qna` is an exception:** build-time pack generation is wrapped in a `ValidatedRequest` spine handoff and the live runtime pack route exposes canonical runtime bindings, but no `GovernedAppRunner` subclass exists yet.

**Why `apps_underwriting_ai` cannot be governed:** underwriting decisions are legally-binding credit determinations. The generic evidence-retrieval substrate is inappropriate for a regulated decision domain. The app provides its own `CoreAdapter` + `CoreHandoffPayload` governance protocol (equivalent L2 guarantee) and `ObservabilityAdapter` (equivalent L6).

Formal exceptions are expected to pass EXCF01–EXCF08 (FormalExceptionEntry in registry, valid reason code, blocked/safe layers declared, >=2 compensating controls, review cadence, partial adoption module importable, compensating controls verified at gate time).

---

## 4. Proof Command Map

### One-command release gate
```bash
python ops_scripts/ci/run_architecture_proof.py
```

### Individual suites

| Suite ID | Command | Checks | What it validates |
|---|---|---|---|
| S1 | `python ops_scripts/ci/check_governed_app_conformance.py` | 52 (CONF01–CONF08, EXCF01–EXCF08) | Registry structure, runner imports, formal exception schema |
| S2 | `python tools/eval/retrieval_benchmark.py --exception-framework-proof` | governed apps + exception controls + no-adhoc | Behavioral proof for governed loop and exception controls |
| S3 | `python tools/eval/retrieval_benchmark.py --regression-check` | regression baseline | Evidence governance regression (grounding, coverage, telemetry) |

### Targeted proof commands

| Command | Checks | Scope |
|---|---|---|
| `--penta-app-proof` | legacy grouped proof | Historical grouped E2E path; prefer `--exception-framework-proof` for current registry status |
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

## 5. Gate Shape And Current Gaps

When the proof pack is green, the expected shape is:

```
Suite  Label                           Expected
─────  ──────────────────────────────  ────────────────────────────────────
S1     Conformance Gate                52/52 PASS (CONF01-08 + EXCF01-08)
S2     Exception Framework Proof       PASS
       ├─ governed_apps                PASS (registry-governed entries)
       ├─ eval_exception               10/10 PASS (EVAL01-EVAL10)
       ├─ lic_exception                PASS (CC-LIC controls)
       ├─ uw_exception                 10/10 PASS (UW01-UW10)
       └─ no_adhoc                     PASS (0 ad hoc exceptions)
S3     Regression Check                PASS
─────  ──────────────────────────────  ────────────────────────────────────
FINAL  Architecture Proof Pack         PASS
```

**Current docs-refresh S1 result:** PASS. The conformance gate reports 52/52 checks passing after registry rows,
runner imports, formal exception handlers, and the `apps_rg` canonical callable shape were aligned. Treat the
command output as authoritative for current status.

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
| architect exception handler | `apps_architect/integrations/governed_architect_exception.py` |
| eval exception handler | `apps_eval/integrations/governed_eval_exception.py` |
| lic exception handler | `apps_lic/integrations/governed_lic_exception.py` |
| qna exception handler | `apps_qna/integrations/governed_qna_exception.py` |
| uw exception handler | `apps_underwriting_ai/integrations/governed_uw_exception.py` |
