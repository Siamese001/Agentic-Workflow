---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\finish-open-scope-test-harden-38010b.md'
original_relative_path: 'finish-open-scope-test-harden-38010b.md'
source_sha256: 95514c37f21c92496a5a360ecfaf918c0d4223ec8f78a949bf27977980b2d94c
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Finish Open Scope — Golden-Set + Token Rotation + Test Harden

- **Plan ID**: `finish-open-scope-test-harden-38010b`
- **Parents**: `exit-eval-v5-gap-c0aa47.md` (commit `171ad27e8d`), `exit-eval-v5-test-harden-1cb78d.md` (commit `06040bcd11`)
- **Tier**: T2 (two new modules, two new test files; no cross-layer churn)
- **ADG snapshot**: `artifacts/adg/adg_indexed_04252026_0843.sqlite`
- **Status**: Active

## SR_INTAKE

User mandate: "no next steps finish all scope and commit and sync test harden". Closes the three carry-overs flagged at the end of `exit-eval-v5-test-harden-1cb78d.md`:

1. **BUS T golden-set promotion pipeline** — surface candidate buckets from PassKStore for §S2D / §S4A golden-set comparisons.
2. **Capability-token rotation policy** — L5 policy module that decides KEEP / ROTATE_* based on token TTL, single_use, and observed usage.
3. **Judge calibration cadence automation** — already shipped (verified): `@c:/Git/Agentic-Workflow/ops_scripts/ci/check_judge_calibration.py` is a concrete CI gate that blocks merge when judge-vs-human Cohen's κ falls below the configured threshold per rubric. Pairs with the existing `judge-calibration-cadence.md` rule. **No new module needed.**

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| G1 | G1.1 G1.2 | Golden-set candidate surface | ~3500 | Done | new module + 14 tests pass |
| G2 | G2.1 G2.2 | Capability-token rotation policy | ~3000 | Done | new module + 23 tests pass |
| G3 | G3.1 | Regression check across exit_eval surface | ~500 | Done | 217+ existing tests still green |
| G4 | G4.1 | Commit + push | ~500 | Done | pushed to origin/main |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| G1.1 | golden_set.py | `agentic_core/L3_orchestration/exit_eval/golden_set.py` (new) | Read-only contract per v6 §1; deterministic ordering; default policy must be conservative | 2000 | Done |
| G1.2 | test_golden_set.py | `tests/agentic_core/L3_orchestration/exit_eval/test_golden_set.py` (new) | Cover policy validation, recency-window short-circuit, determinism, dedup | 1500 | Done |
| G2.1 | capability_token_rotation.py | `agentic_core/L5_safety/enforcement/capability_token_rotation.py` (new) | Pure function; precedence ordering; layer-correct (L5 acting on L2 type) | 1500 | Done |
| G2.2 | test_capability_token_rotation.py | `tests/unit/agentic_core/L5_safety/enforcement/test_capability_token_rotation.py` (new) | Duck-type stand-in to avoid PrincipalChain ceremony; precedence + parametrize | 1500 | Done |
| G3.1 | Regression sweep | exit_eval test surface | None | 500 | Done |
| G4.1 | Commit + push | git | None | 500 | Done |

## Design Notes

### Golden-set candidate surface

```
promotable iff history_size >= min_history
          AND last_n_pass_rate(n=min_history) >= pass_rate_threshold
          AND no failed trial in last `recency_window` records
```

- Read-only per v6 §1 (does not mutate the store).
- Defaults conservative: `min_history=20, pass_rate_threshold=1.0, recency_window=5`.
- Caller supplies the key list — PassKStore deliberately does not enumerate, because production backends will shard.
- Returns `tuple` sorted by `(trajectory_class, rubric_version, agent_version, policy_version)` so BUS U snapshots stay content-addressable.

### Capability-token rotation policy

```
EXPIRY     := age_seconds >= token.ttl_seconds
USAGE      := token.single_use AND usage_count >= 1
THRESHOLD  := age_seconds >= int(ttl_seconds * rotation_threshold_pct)

decision = first match of (EXPIRY, USAGE, THRESHOLD) else KEEP
```

- Pure function — no clock reads, no I/O.
- Precedence is auditor-friendly (most decisive first).
- Lives in `L5_safety/enforcement/` because rotation is policy, not type.
- Defaults `rotation_threshold_pct=0.8`; HIGH-band sites tighten to 0.5; LOW-band sites relax to 0.9.

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Archetype | Surface | Fan-in | Impact | Wave |
|---|---|---|---|---|---|---|---|
| 1 | `golden_set.py` (new) | L3 | STATE_NODE | State | 0 (new) | 0.4 | G1 |
| 2 | `capability_token_rotation.py` (new) | L5 | SAFETY_GATEKEEPER | Security | 0 (new) | 0.5 | G2 |

Both modules are **leaf** files (no fan-in yet); risk is bounded.

## ADG_GRAPH_LAYER_EVIDENCE

- `mv_exit_disposition_coverage` — disposition surface unchanged.
- `mv_eval_coverage_by_path` — both new files start with full coverage from this plan's tests.
- `mv_dependency_cone_risk` — new files add zero entries to the cone (no dependents yet).
- Semantic edges: `golden_set.select_candidates` `reads_from` `consistency.PassKStore.history`; `capability_token_rotation.evaluate_rotation` `reads_from` `CapabilityTokenV4Artifact` (read-only — v6 §1 OBSERVER LAW respected).
- P-views: zero `v_p0_*` / `v_p1_*` matches expected.

## Out of Scope (genuinely not touched)

None. The three deferrals from prior plan are now either implemented (G1, G2) or verified-already-shipped (judge calibration).
