---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\high-wave1-p1-zero-a13f7c.md'
original_relative_path: 'high-wave1-p1-zero-a13f7c.md'
source_sha256: 179af1b8da5af351f81b7acd0d9df9723cf200972d1725c711a0e9c3a09aace2
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-19'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# High Wave 1 — Finish P0 and Drive P1 to Zero

Close the remaining P0 hygiene debt and execute a focused Wave 1 sequence to reduce P1 (HIGH anti-pattern net) from `632` to `0` with verifiable ADG evidence.

---

## Baseline Evidence

- ADG health: `sqlite=healthy`, `redis=healthy`, snapshot `04182026_2015`
- Source: `artifacts/adg/adg_burndown_table.json`
- Current state: `P0_layer_violations=5`, `P1_anti_patterns=632`, `P2_anti_patterns=2242`
- P1 kind breakdown (net):
  - `log_and_swallow=384`
  - `return_none_swallow=160`
  - `broad_exception_catch=53`
  - `silent_exception_swallow=35`

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| Wave 0 | 0.1, 0.2 | Finish P0 closure and stabilize gates | 9K 🟢 | SC-1 remains audit so reporting completes | 🔲 TODO | `P0_layer_violations=0` and full ADG/report pipeline runs |
| Wave 1A | 1.1, 1.2 | Eliminate `broad_exception_catch` + `silent_exception_swallow` (P1) | 14K 🟢 | Remaining P1 broad/silent are code-fixable (non-guardian) | 🔲 TODO | P1 broad/silent net becomes `0` |
| Wave 1B | 1.3, 1.4 | Eliminate `return_none_swallow` (P1) | 16K 🟢 | Return-path contracts can be tightened without regressions | 🔲 TODO | P1 return-none net becomes `0` |
| Wave 1C | 1.5, 1.6 | Eliminate `log_and_swallow` and lock ratchet | 22K 🟢 | Logging-only catches can be converted to precise handling/escalation | 🔲 TODO | `P1_anti_patterns=0` and ratchet ceiling updated to `0` |

**Total: ~61K tokens, all GREEN per estimator budget envelope (hard max 262K, safe cap 223K).**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| 0.1 | Close residual P0 violations | Files contributing to 5 hygiene P0 findings | P0 blocks release posture; mixed ownership | 5K | 🔲 TODO |
| 0.2 | Run ADG end-to-end with fresh burndown | `tools/generate/*`, `artifacts/adg/*` outputs | Historical stale burndown risk when blocked early | 4K | 🔲 TODO |
| 1.1 | Remove P1 broad catches | Top P1 files from ADG high-severity list | Overly broad handlers mask actionable failures | 7K | 🔲 TODO |
| 1.2 | Remove P1 silent swallows | Silent swallow hotspots in prod paths | Silent failure paths require behavior-safe rewrites | 7K | 🔲 TODO |
| 1.3 | Remove P1 return-none swallows | Return-none hotspots in runtime paths | Contract changes may require callsite hardening | 8K | 🔲 TODO |
| 1.4 | Verify no regressions after return-path hardening | Narrow targeted tests by changed modules | Risk of behavior drift | 8K | 🔲 TODO |
| 1.5 | Remove P1 log-and-swallow | Highest-volume P1 category files | Needs precise exceptions and explicit propagation | 12K | 🔲 TODO |
| 1.6 | Final ratchet lock to zero | `artifacts/adg/p1_ratchet.json` + ADG regen | Must avoid post-fix rebound | 10K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: P0 is not yet clean (`5`)**
- Must be reduced to zero before declaring Wave 1 complete.
- If unresolved, high-confidence production readiness remains blocked.

**GAP-2: SC-1 structural conformance still reports `54` violations**
- Keep SC-1 in audit posture during burndown execution so reporting/ratchet writes are not skipped.
- Track separately from P1 scope; do not mix success criteria.

**GAP-3: P1 largest bucket is `log_and_swallow` (`384 net`)**
- Dominates remaining work and likely spans multiple ownership domains.
- Requires tranche-based execution and strict verification checkpoints.

---

## Execution Plan

### Phase 0 — P0 Completion and Baseline Integrity
**Scope**: Eliminate remaining P0 hygiene findings and produce a fresh baseline artifact set.

**Commands**:
```bash
python tools/generate_full_adg.py
```

**Acceptance**:
- `artifacts/adg/adg_burndown_table.json` shows `P0_layer_violations=0`.
- ADG pipeline reaches report + ratchet write stage (no stale baseline).

### Phase 1 — High Wave 1 (P1 to 0)
**Scope**: Execute in three tranches ordered by smallest-to-largest risk cluster.

**Tranche order**:
1. `broad_exception_catch` (53) + `silent_exception_swallow` (35)
2. `return_none_swallow` (160)
3. `log_and_swallow` (384)

**Commands (per tranche loop)**:
```bash
python -m py_compile <changed_python_files>
python tools/generate_full_adg.py
```

**Acceptance**:
- After each tranche, P1 net decreases monotonically.
- No new P0 introduced.
- Final tranche yields `P1_anti_patterns=0`.

### Phase 2 — Ratchet and Governance Lock
**Scope**: Freeze achieved zero and prevent regressions.

**Commands**:
```bash
python tools/generate_full_adg.py
```

**Acceptance**:
- `artifacts/adg/p1_ratchet.json` set to ceiling `0`.
- Regeneration validates zero without rebound.

---

## Rules

- No test skipping, no broad `except Exception` additions, no guardian expansion to hide debt.
- Keep edits scoped to high-severity anti-pattern removal and required behavior-preserving hardening.
- Validate each tranche with syntax checks and ADG regeneration before moving forward.

---

## Success Criteria

- [ ] `P0_layer_violations=0`
- [ ] `P1_anti_patterns=0`
- [ ] `p1_ratchet.json` ceiling locked at `0`
- [ ] Fresh burndown and ratchet artifacts written in the latest ADG run
- [ ] No regressions introduced in targeted validation runs

---

## Rollback Strategy

1. If a tranche increases P1/P0, stop and revert only that tranche’s edits.
2. Re-run ADG to confirm return to previous known-good metrics.
3. Resume with smaller file batches and narrower exception scopes.
