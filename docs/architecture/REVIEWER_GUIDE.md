# Reviewer Guide — Governed Architecture

> **Start here.** This is the single entry point for anyone reviewing the governed architecture.  
> Read time: ~5 minutes.  
> One-command proof: `python ops_scripts/ci/run_architecture_proof.py`

---

## What was built

A **shared agentic substrate** that every application-layer app (`apps_*`) runs through.  
Instead of each app implementing its own routing, retrieval, and governance logic, they all
reuse one pipeline:

```
L1 (intent decomposition) → L0 (routing) → C0 (grounded retrieval)
  → L2 (governed execution chokepoint) → L5 (exit gate) → L6 (shadow telemetry)
```

This is enforced structurally — the shared base class `GovernedAppRunner` owns the pipeline,
app subclasses supply only `_build_query()` and a record mapper.

Apps that structurally cannot adopt this pattern have **formal governed exceptions** — not
ad hoc bypasses — with reason codes, compensating controls, and annual review cadence.

---

## Reading order

| Step | Read | Purpose |
|---|---|---|
| 1 | This file | Orientation and reviewer journey |
| 2 | `docs/architecture/architecture-proof-pack.md` | Proof command map, app registry, gap list |
| 3 | `python ops_scripts/ci/run_architecture_proof.py` | Run the proofs yourself |
| 4 | `docs/architecture/governed-app-contract.md` | Contract schema detail (optional deep-dive) |
| 5 | `docs/architecture/ROLLOUT_CLOSEOUT.md` | Final status + known gaps |

---

## Executive walkthrough (2-minute version)

**Problem:** Seven `apps_*` packages — each with its own routing, retrieval, and governance wiring.
No shared substrate, no structural enforcement, no provable behavioral guarantees.

**Solution:**
1. Built `GovernedAppRunner` — a shared base class that runs the full L1→L0→C0→L2→L5→L6 pipeline.
2. Migrated five apps onto it: `apps_research`, `apps_exec`, `apps_rfp`, `apps_rg`, `apps_lic`.
3. Two apps have structural exceptions (`apps_eval`: circular dependency; `apps_underwriting_ai`:
   regulated domain). Both are formalized with reason codes, compensating controls, and gate-verified.
4. One conformance gate (`check_governed_app_conformance.py`) enforces the schema at CI time.
5. One proof harness (`retrieval_benchmark.py`) verifies the live behavior of all 7 apps.
6. One release gate (`run_architecture_proof.py`) composes all checks into one command.

**Result:** Any reviewer can confirm the architecture is sound in one command.

---

## Engineer quickstart

```bash
# 1. Verify the whole governed architecture (fast — ~12s)
python ops_scripts/ci/run_architecture_proof.py --skip-regression

# 2. Full proof including regression baseline (~17s)
python ops_scripts/ci/run_architecture_proof.py

# 3. Structural checks only (fastest — ~1s)
python ops_scripts/ci/run_architecture_proof.py --suite S1

# 4. Behavioral checks only (penta-app + exceptions)
python ops_scripts/ci/run_architecture_proof.py --suite S2
```

To inspect individual apps:

```bash
# Per-app targeted proof
python tools/eval/retrieval_benchmark.py --rg-pilot-proof
python tools/eval/retrieval_benchmark.py --lic-pilot-proof
python tools/eval/retrieval_benchmark.py --eval-exception-proof
python tools/eval/retrieval_benchmark.py --uw-exception-proof

# Full penta-app E2E
python tools/eval/retrieval_benchmark.py --penta-app-proof

# Exception framework only
python tools/eval/retrieval_benchmark.py --exception-framework-proof
```

To inspect the registry directly:

```bash
python -c "from apps_shared.integrations.app_registry import APP_REGISTRY; \
  [print(k, v.status) for k, v in APP_REGISTRY.items()]"
```

---

## What to look for when reviewing

**Structural correctness (S1 — 36 checks):**
- Every `apps_*` package is registered in `app_registry.py`.
- Governed apps: runner importable, subclass of `GovernedAppRunner`, versioned capability token.
- Exception apps: `FormalExceptionEntry` in registry (not ad hoc), valid reason code, blocked/safe
  layers declared, ≥2 compensating controls, partial adoption module importable, controls verified.

**Behavioral correctness (S2 — ~80 checks):**
- Each governed app runs both a **happy path** (grounded, proceed) and a **degraded path**
  (no vector store → abstain). The substrate handles degradation correctly.
- Exception app handlers instantiate without errors, emit telemetry, and pass CC checks.
- Zero ad hoc exception statuses remain in the registry.

**Regression baseline (S3 — 12 checks):**
- Evidence grounding thresholds, citation constants, and disposition logic match baseline.

---

## Current green state

```
S1  Conformance Gate        PASS  36/36 checks
S2  Exception Framework     PASS  ~80 checks (penta + eval + uw + no-adhoc)
S3  Regression Check        PASS  RC01-RC12
```

**Registry state:** 5 governed + 2 formal exceptions + 0 ad hoc.

---

## Known non-blocking gaps

| Gap | Status |
|---|---|
| C0 raw=0 in degraded path (no live ChromaDB) | Expected — abstain is the correct governed response |
| `ClockProvider` kwargs mismatch in test harness | Expected — L0 graceful fallback path tested |
| No live vector collections in proof environment | Expected — proof validates both paths explicitly |

Full gap list with severity and recommended next owner: `docs/architecture/RELEASE_READINESS.md`

---

## Key files

| File | Role |
|---|---|
| `apps_shared/integrations/governed_app_runner.py` | Shared base class — the governed pipeline |
| `apps_shared/integrations/app_registry.py` | Single source of truth for all app classifications |
| `ops_scripts/ci/check_governed_app_conformance.py` | Structural conformance gate (CONF + EXCF) |
| `ops_scripts/ci/run_architecture_proof.py` | One-command release gate |
| `tools/eval/retrieval_benchmark.py` | All behavioral proof suites |
| `docs/architecture/architecture-proof-pack.md` | Full proof command map and gap maps |
| `docs/architecture/governed-app-contract.md` | FormalExceptionEntry schema detail |
| `docs/architecture/ROLLOUT_CLOSEOUT.md` | Final rollout status and known-gap register |
