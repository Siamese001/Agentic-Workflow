# Reviewer Guide — Governed Architecture

> **Start here.** This is the single entry point for anyone reviewing the governed architecture.  
> Read time: ~5 minutes.  
> One-command proof: `python ops_scripts/ci/run_architecture_proof.py`

---

## What was built

A **shared agentic substrate** for app packages that have adopted the governed runtime path.
Instead of each adopted app implementing its own routing, retrieval, and governance logic, the
governed entries reuse one pipeline:

```
L1 (intent decomposition) → L0 (routing) → C0 (grounded retrieval)
  → L2 (governed execution chokepoint) → L5 (exit gate) → L6 (shadow telemetry)
```

For governed entries, this is enforced structurally: the shared base class or canonical dispatch
entrypoint owns the pipeline, and app code supplies bounded app-specific mapping.

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

**Problem:** App packages can drift into separate routing, retrieval, and governance wiring unless
the shared substrate and exception model are checked continuously.

**Solution:**
1. Built `GovernedAppRunner` — a shared base class that runs the full L1→L0→C0→L2→L5→L6 pipeline.
2. Classified the current registry as three governed entries: `apps_exec`, `apps_research`, and `apps_rg`.
3. Formalized five exceptions: `apps_architect` (pending runner migration), `apps_eval` (circular
   dependency), `apps_lic` (canonical-dispatch product spine), `apps_qna` (pending runner migration),
   and `apps_underwriting_ai` (regulated domain). Each has reason codes, compensating controls, and
   gate-verifiable metadata.
4. One conformance gate (`check_governed_app_conformance.py`) enforces the schema at CI time.
5. One proof harness (`retrieval_benchmark.py`) verifies governed behavior and exception controls.
6. One release gate (`run_architecture_proof.py`) composes all checks into one command.

**Result:** Any reviewer can inspect the architecture and current gap list in one command.

---

## Engineer quickstart

```bash
# 1. Verify the whole governed architecture (fast — ~12s)
python ops_scripts/ci/run_architecture_proof.py --skip-regression

# 2. Full proof including regression baseline (~17s)
python ops_scripts/ci/run_architecture_proof.py

# 3. Structural checks only (fastest — ~1s)
python ops_scripts/ci/run_architecture_proof.py --suite S1

# 4. Behavioral checks only (governed apps + formal exceptions)
python ops_scripts/ci/run_architecture_proof.py --suite S2
```

To inspect individual apps:

```bash
# Per-app targeted proof
python tools/eval/retrieval_benchmark.py --rg-pilot-proof
python tools/eval/retrieval_benchmark.py --lic-pilot-proof
python tools/eval/retrieval_benchmark.py --eval-exception-proof
python tools/eval/retrieval_benchmark.py --uw-exception-proof

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

**Structural correctness (S1 — 52 checks):**
- Registry completeness is checked against `app_registry.py`.
- Governed apps: runner importable, subclass of `GovernedAppRunner`, versioned capability token.
- Exception apps: `FormalExceptionEntry` in registry (not ad hoc), valid reason code, blocked/safe
  layers declared, ≥2 compensating controls, partial adoption module importable, controls verified.

**Behavioral correctness (S2):**
- Each governed app runs both a **happy path** (grounded, proceed) and a **degraded path**
  (no vector store → abstain). The substrate handles degradation correctly.
- Exception app handlers instantiate without errors, emit telemetry, and pass CC checks.
- Zero ad hoc exception statuses remain in the registry.

**Regression baseline (S3 — 12 checks):**
- Evidence grounding thresholds, citation constants, and disposition logic match baseline.

---

## Current Validation Posture

The direct conformance-gate output is the source of truth for registry counts. A docs-refresh
validation run on this snapshot found the direct S1 conformance gate green:

```bash
python ops_scripts/ci/check_governed_app_conformance.py
```

Result: `PASS 52/52 checks pass`.

**Registry state:** 3 governed + 5 formal exceptions + 0 ad hoc, per `apps_shared/integrations/app_registry.py`.

Known documentation/tooling gap: the top-level `run_architecture_proof.py` runner may still print
stale summary prose for registry counts. Use the registry and direct conformance gate for the count
until that executable summary text is updated.

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
