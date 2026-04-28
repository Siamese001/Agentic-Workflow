# Enforcement Baseline — Tier 0–2

**Baseline name:** `tier0-tier2-enforcement-baseline`
**Frozen at:** 2026-04-28 (UTC)

This document freezes the current Tier 0–2 enforcement state. The
machine-readable equivalent is `ENFORCEMENT_BASELINE_T0_T2.json`.

## Caveat (required wording)

> Tier 0–2 enforcement baseline means selected requirements are linked
> to machine-checkable metadata, static evidence consistency gates,
> fail-closed hardening, and CI workflows. It does not mean all 150
> requirements are enforced, and it does not claim real replay
> execution, real OTEL emission, or full production runtime proof.

## Scope

| Metric | Value |
|---|---:|
| Tier 0 row count | **17** |
| Tier 1 row count | **15** |
| Tier 2 row count | **22** |
| **Total selected rows protected by Tier 0–2** | **54** |
| Total Step 1 rows | 150 |
| Remaining Step 1 rows not yet tiered | **96** |

## Verifier scripts (7)

- `scripts/verify_tier0_enforcement_gate.py`
- `scripts/verify_tier0_runtime_proof_gate.py`
- `scripts/verify_tier1_enforcement_gate.py`
- `scripts/verify_tier1_runtime_proof_gate.py`
- `scripts/verify_tier2_enforcement_gate.py`
- `scripts/verify_tier2_runtime_proof_gate.py`
- `scripts/verify_tier_gate_hardening.py`

## CI workflows (7)

- `.github/workflows/tier0-enforcement-gate.yml`
- `.github/workflows/tier0-runtime-proof-gate.yml`
- `.github/workflows/tier1-enforcement-gate.yml`
- `.github/workflows/tier1-runtime-proof-gate.yml`
- `.github/workflows/tier2-enforcement-gate.yml`
- `.github/workflows/tier2-runtime-proof-gate.yml`
- `.github/workflows/tier-gate-hardening.yml`

All 7 workflows trigger on `pull_request` (any branch) and `push` to
`main`/`master`, use Python 3.12, run only their intended verifier, and
do not run the full pytest suite, the proof harness, replay machinery,
or any OTEL exporter. Runtime/static-proof verifier scripts call
`tier_fixture_bootstrap.materialize()` before evaluation. See
`T0_T2_FINAL_CI_REPRO_AUDIT.md` / `.json` for the per-workflow audit.

## Hardening test count

**33** fail-closed cases in
`tests/runtime/test_tier_gate_fail_closed_hardening.py`:

| Class | Cases |
|---|---:|
| `TestTier0EnforcementGateFailsClosed` | 4 |
| `TestTier1EnforcementGateFailsClosed` | 4 |
| `TestTier0RuntimeProofGateFailsClosed` | 5 |
| `TestTier1RuntimeProofGateFailsClosed` | 10 |
| `TestTier2RuntimeProofGateFailsClosed` | 10 |

## Latest relevant commit hashes

| Milestone | Commit |
|---|---|
| Tier 2 Batch A close | `d23fdd881a` |
| Tier 2 Batch B+C close | `72fc88261f` |
| Tier 2 Batch D+E close (Tier 2 metadata gate READY) | `f278bd02e1` |
| Tier 2 runtime-proof gate + CI + hardening | `c596c188f3` |

## Exact local commands

```
python scripts/verify_tier0_enforcement_gate.py
python scripts/verify_tier0_runtime_proof_gate.py
python scripts/verify_tier1_enforcement_gate.py
python scripts/verify_tier1_runtime_proof_gate.py
python scripts/verify_tier2_enforcement_gate.py
python scripts/verify_tier2_runtime_proof_gate.py
python scripts/verify_tier_gate_hardening.py
```

Expected: 6 gates **READY**, hardening **33 passed**.

## Roadmap

| Tier | Status | Notes |
|---|---|---|
| **Tier 0** | ✅ Frozen at this baseline | 17 rows, metadata + runtime-proof + CI + 4+5 hardening cases |
| **Tier 1** | ✅ Frozen at this baseline | 15 rows, metadata + runtime-proof + CI + 4+10 hardening cases |
| **Tier 2** | ✅ Frozen at this baseline | 22 rows, metadata + runtime-proof + CI + 10 hardening cases |
| **Tier 3** | 🔜 Next | Next selection wave from the remaining 96 Step 1 rows. Same pattern: metadata + static-evidence proof + CI + hardening. |
| **Tier 4** | 🔜 Pending | Subsequent selection wave; same pattern. |
| **Tier 5** | 🔜 Pending | Subsequent selection wave; same pattern. |
| **Tier 6** | 🔜 Pending | Subsequent selection wave; same pattern. |
| **Master all-requirements gate** | 🔜 Final | Aggregate gate covering all 150 Step 1 rows once Tiers 3–6 are closed; fail-closed if any tier is BLOCKED. |
