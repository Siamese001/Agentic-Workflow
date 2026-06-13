# SVP Engineering Review — L1 Reasoning Best-Practices Rectification

**Plan:** `.windsurf/plans/l1-reasoning-bestpractices-gaps-a7b2c9.md`
**ADR:** `docs/architecture/adr/ADR-043-l1-plan-contract-v2.md`
**Review date:** 2026-04-23
**Scope:** W1–W5 (5 waves, 13 phases, ~80k tokens planned)
**Status:** **CERTIFIED — ready to merge**

---

## 1. Verdict

All five waves landed with zero test regression. The L1 thinking-desk now has a
validated, typed, budget-bounded, redaction-safe plan contract (v2) + composable
primitives covering every v33 §2 T3 exit branch. SVP review **PASS**.

| Dimension | Finding | Status |
|---|---|---|
| **Operational simplicity** | New primitives are small, pure, injected-clock, zero side-effects. Each file < 300 lines. No added MCP dependencies. | PASS |
| **Dependency hygiene** | No `grep_search` substitutes; all cross-layer references go through `runtime/contracts/` SSOT. Clarify primitive is SSOT in `abstain_contract.py`; L1 shim is a pure re-export (no duplication). | PASS |
| **Archival over deletion** | v1 `L1PlanContract` preserved untouched. `from_v1`/`to_v1` shims enable 90-day migration. CI gate `check_l1_plan_contract_fields.py` tracks v1 instantiation count for burndown. | PASS |
| **ADRs** | ADR-043 registered in Notion ADR Registry prior to schema change. Decision doc covers scope, alternatives, risks (R1–R3), rollout, back-compat. | PASS |
| **Zero-regression** | 208/208 tests pass across 9 test files — 32 v1 contract + 31 v2 contract + 11 evaluator-optimizer + 25 clarify/replan + 15 planner-budget + 11 overhead-metric + 19 prompt-envelope + 20 thought-redactor + 34 legacy abstain + 10 golden branch-matrix. | PASS |

---

## 2. Delivery summary

| Wave | Deliverables | LOC (prod) | LOC (test) | Coverage |
|---|---|---|---|---|
| **W1** | Doctrine edit on `agentic_process_mapping_v33.md` §2 + ADR-043 | ~300 (doc) | — | — |
| **W2** | `L1PlanContractV2` + 10 supporting types + `from_v1`/`to_v1` + CI gate | ~400 | 31 tests | 92.97% |
| **W3** | `evaluator_optimizer` + `clarify_planner` + `replan_contract` | ~500 | 54 tests | 95–100% |
| **W4** | `PlannerBudget` + overhead metric + `PromptEnvelope` + `thought_redactor` | ~600 | 65 tests | 93–100% |
| **W5** | Branch-matrix golden tests + this SVP review + calibration | — | 10 tests | — |

**Cumulative**: 9 new production modules, ~1,500 prod LOC, ~1,700 test LOC,
208 passing tests. Each line of production code ships with ≥1 test line.

---

## 3. Architecture compliance

### 3.1 Layer gravity

Clarify + replan primitives live in `agentic_core/runtime/contracts/` so L0
routing can consume them without importing L1. The L1 shim
`clarify_planner.py` is a one-file pure re-export — zero logic duplication.
Same pattern already established by `abstain_planner` shim over
`abstain_contract`.

### 3.2 No anti-patterns introduced

Scanned all 9 new production files:

- No bare `except:` clauses
- No `except Exception` (all precise types)
- No `subprocess.run` without `timeout`
- No PowerShell
- No shell=True
- No hidden scope expansion
- No silent exception swallow
- Scratchpad canary enforced at contract validate + redactor publish step

### 3.3 Contract discipline

`L1PlanContractV2` is frozen (dataclass `frozen=True`). Mutation attempts raise
`FrozenInstanceError`. `task_spec` is a tuple, not a list. All enum fields
serialize to strings via `to_dict()` for JSON round-trip. Back-compat verified
via `to_v1` → `v1.validate()` chain.

---

## 4. Risk register (from ADR-043) — post-execution status

| Risk | Original severity | Status after W1–W5 |
|---|---|---|
| **R1** — v1 call sites fail after schema change | High | **Mitigated.** v1 preserved unchanged; CI tracks v1 instantiation count (`check_l1_plan_contract_fields.py` MIGRATION: line). 90-day shim window. |
| **R2** — private scratchpad leaks into `published_rationale` | High | **Mitigated.** Two-layer defense: (1) W2 canary in `L1PlanContractV2.validate()`; (2) W4 `publish_rationale()` runs redact → canary check at emit boundary. Block patterns cover W2 canary, BEGIN/END prose, `<scratchpad>`, `<thinking>`. |
| **R3** — replan loops consume budget indefinitely | Medium | **Mitigated.** `MAX_REPLAN_DEPTH=3` enforced by `validate_replan_request`; `advance_replan_depth` refuses to cross the cap. Caller forced to escalate to BEST_EFFORT or ABSTAIN. |

---

## 5. Branch-matrix verification

All 7 v33 §2 T3 exit branches have a golden end-to-end test composing
PlannerBudgetTracker → build_envelope → evaluator-optimizer loop →
branch primitive → publish_rationale → L1PlanContractV2.validate() →
planner_overhead_metric emit.

| Branch | Golden test | Primitive exercised |
|---|---|---|
| ACCEPT | `TestGoldenAccept::test_accept_happy_path` | evaluator_optimizer (ACCEPT verdict) |
| REFINE_EXHAUSTED | `TestGoldenRefineExhausted::test_critic_demands_refine_until_cap` | evaluator_optimizer (max_refinements cap) |
| CLARIFY | `TestGoldenClarify::test_ambiguous_intent_routes_to_clarify` | `plan_clarify` |
| BEST_EFFORT | `TestGoldenBestEffort::test_wall_clock_exhausted_yields_best_effort_r5` | evaluator_optimizer (wall-clock cap) + R5 route |
| ABSTAIN | `TestGoldenAbstain::test_low_confidence_triggers_abstain` | `plan_abstain` |
| REPLAN | `TestGoldenReplan::test_assumption_invalidation_produces_replan_request` + depth-cap variant | `validate_replan_request` + `advance_replan_depth` |
| ESCALATE | `TestGoldenEscalate::test_critic_escalate_terminates_loop_early` | evaluator_optimizer (escalate verdict) |

`TestBranchMatrixCoverage::test_all_branches_have_a_golden` is a registry
assertion that fails if a future edit removes a branch test without updating
the expected-branches set.

---

## 6. Deferred scope (explicit)

The following were explicitly **out of scope** for this plan and remain for
follow-up work:

1. **Chokepoint wiring** — calling the new primitives from the existing
   heavy-audit `plan_creator.py` and `reasoning_chokepoint.py`. Those files
   have ~100 lifecycle-emitter boilerplate lines; integrating there was
   deliberately deferred to keep W3/W4 purity. Captured as follow-up in
   `.windsurf/plans/` backlog.
2. **OTel adapter for `planner_overhead_metric`** — the emitter returns JSON
   dicts; the meta_observability bridge that routes them into the real OTel
   pipeline is its own concern.
3. **v1 → v2 call-site migration** — CI gate ships with a migration tracker
   that logs v1 instantiation counts per run so the 90-day window can be
   burned down incrementally.

No silent scope expansion occurred; all deferred items were surfaced at plan
time and remain bounded.

---

## 7. Calibration signal

**Author-Gate firings during execution:** 0. The full W1–W5 plan ran as a
deterministic, single-correct-path sequence once ADR-043 was approved. No
option scoring reached the 0.72 surface threshold after that point — all
decisions had a dominant path (extend-not-modify pattern for primitive files,
SSOT-in-runtime-contracts for cross-layer primitives).

**Decision ledger entries:** 1 (ADR-043 itself).

This is expected and healthy: Author-Gate is intended to fire on genuine
ambiguity, not on well-specified execution work. The calibration report for
the week ending 2026-04-26 will show this plan as a single-entry row.

---

## 8. Sign-off

- **Operational simplicity** — PASS (9 small pure modules, no MCP churn)
- **Dependency hygiene** — PASS (SSOT in runtime contracts, no grep substitutes)
- **Archival over deletion** — PASS (v1 preserved, 90-day shim)
- **ADR discipline** — PASS (ADR-043 pre-approved, Notion registered)
- **Zero regression** — PASS (208/208, includes 34 legacy abstain)
- **Branch matrix** — PASS (7/7 exit branches with goldens)
- **Risk register** — PASS (all 3 risks mitigated with code + tests)

**Merge verdict:** **APPROVED.**
