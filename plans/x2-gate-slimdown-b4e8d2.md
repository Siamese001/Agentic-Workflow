---
plan_type: platform_core_change
slug: x2-gate-slimdown-b4e8d2
status: In Progress
ai_summary: "Slim apps_rg X2 hard-gate surface for the Claude-base era without weakening grounding/safety."
dod_exempt: false
supersedes: []
---

# X2 Gate Slim-Down — Claude Sonnet 4.6 Base Recalibration

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | |

## Context (SCQA)

- **Situation.** apps_rg runs ~370 X2 deterministic gates across 17 validator files
  (executive_summary 81, competencies 43, ibm/headline/unify bullets ~35 each). The hard-FAIL
  surface ballooned during the **Qwen-vLLM era**, when the base generator was high-variance and
  produced frequent stylistic/robotic failure modes that needed deterministic guards.
- **Complication.** The base generator is now **Claude Sonnet 4.6** (Qwen removed, PR#256) plus a
  cross-provider X1D proof judge (recalibration `e558409f60`). A large subset of the gates are
  **STYLE/prose-hygiene** hedges that a strong model rarely trips — they now mostly add
  **false-block risk + maintenance burden**. A handful are **REDUNDANT** (the same check
  parameterized N ways, e.g. per-employer leakage). But the **majority are model-INDEPENDENT
  CORRECTNESS invariants** (grounding, anti-leakage, anti-fabrication, metric fidelity,
  schema/count, REAL_LLM) that a better writer does **not** make safe — and a fluent model
  produces *more* convincing hallucinations, so those gates are arguably more load-bearing now.
- **Question.** Which gates can be slimmed without weakening the proof contract, and how do we
  prove the slim-down is safe?
- **Answer.** A conservative, evidence-gated triage: **DEMOTE** adversarially-verified STYLE gates
  to WARN (record-don't-block), **MERGE** exact-duplicate REDUNDANT gates, **RETIRE** stale
  process gates — while keeping **every** CORRECTNESS gate a hard FAIL. Demotion is reversible and
  telemetered; style gates are retired only after live evidence shows they never fire.

> ⛔ **Hard invariant (constitutional): never demote a CORRECTNESS gate to make a bad output pass.**
> Only gates that survive adversarial refutation (CONFIRM) are eligible. Uncertain → KEEP_FAIL.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0 | Exhaustive per-gate triage (classify + adversarial verify) | ~250k | All 17 validator files reachable | 🔄 In Progress | Every gate tagged; STYLE/REDUNDANT/STALE candidates each CONFIRM/OVERRULE |
| W1 | P1 | `x2_severity` soften helper + `STYLE_WARN_GATE_IDS` SSOT + apply at lane sites + telemetry | ~60k | WARN mechanism (`pass=real OR warn_only`) | ⬜ Not Started | Demoted gates record `[WARN_ONLY] would_fail:` and never block X3 |
| W2 | P2 | Merge CONFIRMED-REDUNDANT clusters (e.g. cross-employer leakage 3→1) | ~50k | Merge targets verified exact-duplicate | ⬜ Not Started | One parameterized gate replaces the cluster; coverage unchanged |
| W3 | P3 | Test: unit + negative (fabrication still blocks) + positive (style no longer blocks) + lane run | ~80k | apps_rg test surface green at baseline for touched lanes | ⬜ Not Started | Correctness gates still FAIL; style gates WARN; lane tests green; smoke run exits 0 |
| W4 | P4 | Evidence-gated retirement (after N runs, retire style gates that never fired) | ~30k | Telemetry accrues over runs | ⬜ Not Started | Retire only gates with 0 real fires over N runs; logged |

### Phase-Level Summary
| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0 | Triage | all `*_x2.py` + `competencies_rigor.py` + `role_episode_lane.py` | exhaustiveness; not mis-tagging correctness as style | ~250k | 🔄 |
| P1 | Soften + telemetry | new `validators/x2_severity.py`; 8 lane-execution sites | uniform across 7 `X2GateResult` shapes | ~60k | ⬜ |
| P2 | Merge redundant | leakage gates + duplicate source-supported gates | proving exact-duplicate before merge | ~50k | ⬜ |
| P3 | Test | `tests/unit/apps_rg/**`, one live lane run | negative/positive proofs; no regression | ~80k | ⬜ |
| P4 | Retire-with-evidence | the demoted set | requires accrued telemetry | ~30k | ⬜ |

## Architecture

- **WARN mechanism (existing).** A gate becomes WARN by computing `passed = (real_pass or warn_only)`
  and stashing the real verdict in `failure_reason`. The X3 aggregator
  (`executive_summary_x3.py:132`) blocks only on `pass == False`, so a WARN gate never blocks.
- **Uniform soften wrapper (new SSOT).** `apps_rg/runtime/validators/x2_severity.py`:
  - `STYLE_WARN_GATE_IDS: frozenset[str]` — the **single** list of demoted gate ids (verified W0).
  - `WARN_ONLY_MARKER = "[WARN_ONLY] would_fail:"`.
  - `soften_warn_only(results)` — for any result whose `gate_id ∈ STYLE_WARN_GATE_IDS` and
    `pass_ is False`, return `replace(r, pass_=True, failure_reason=f"{WARN_ONLY_MARKER} {r.failure_reason}")`.
    Works across all 7 `X2GateResult` dataclasses (shared `gate_id/pass_/failure_reason` fields).
  - `warn_only_fires(results)` — telemetry extractor: which demoted gates *would have* failed.
- **Apply sites (8).** Wrap each lane's gate assembly:
  `[g.to_dict() for g in soften_warn_only(run_<lane>_x2_gates(...))]`.
- **Telemetry.** The `[WARN_ONLY] would_fail:` marker in the per-run X2 gate-results artifact **is**
  the telemetry — grep-able evidence of whether a demoted gate ever actually fires. No new artifact.
- **Reversibility.** Remove a gate id from `STYLE_WARN_GATE_IDS` → it is a hard FAIL again.

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| 1 | Every X2 gate triaged CORRECTNESS\|STYLE\|REDUNDANT\|STALE with adversarial verdict | W0 triage table committed |
| 2 | `x2_severity.soften_warn_only` flips only `STYLE_WARN_GATE_IDS` failures to WARN | unit test |
| 3 | **Negative proof:** a CORRECTNESS violation (fabricated/leaked/wrong-count) still yields X3 BLOCK | unit test feeding a bad output |
| 4 | **Positive proof:** a demoted STYLE violation no longer blocks; records `[WARN_ONLY] would_fail:` | unit test feeding a style violation |
| 5 | Touched-lane X2 unit tests green vs baseline (no new failures attributable to this change) | `pytest` diff (stash-isolation) |
| 6 | Smoke run: `python -m apps_rg --section unify_bullets ...` exits 0 (or same disposition as baseline) | live lane run |
| 7 | No CORRECTNESS gate appears in `STYLE_WARN_GATE_IDS` | grep audit of the set vs triage |

### Verification vs Deferral
| Verified now | Deferred (W4) |
|---|---|
| Demotion mechanism + negative/positive proofs + lane test | Retiring style gates that never fire (needs accrued telemetry) |

## Safety Invariants
- CORRECTNESS gates never demoted. Uncertain → KEEP_FAIL.
- All demotions reversible via the single `STYLE_WARN_GATE_IDS` set.
- Nothing silently dropped — demoted gates still record their real verdict (telemetry).
- REDUNDANT merges must be proven exact-duplicate (coverage unchanged) before landing.

## W0 Triage Output (workflow `x2-gate-triage`, 86 agents)

**Totals (518 gates classified):** 447 CORRECTNESS · 61 STYLE · 5 REDUNDANT · 5 STALE.
Adversarial verification CONFIRMED only **4 demote + 3 real merges** and **OVERRULED 51** proposed
changes (skeptic kept them hard-FAIL). 0 confirmed retire. **86% of gates are model-independent
CORRECTNESS** — confirming the density is mostly load-bearing, not Qwen-variance bloat.

### Confirmed DEMOTE → WARN (4) — IMPLEMENTED (W1)
| gate | lanes affected | note |
|---|---|---|
| `x2_no_em_dash` | competencies, headline, ibm/unify bullets, ibm/unify narrative | em-dash formatting; cosmetic |
| `x2_no_first_person` | same 6 lanes | third-person convention; cosmetic |
| `x2_narrative_base_prose_ngram_overlap` | unify/ibm narrative | soft anti-hydration; HARD structural gate stays FAIL |
| `x2_ibm_narrative_forbidden_opener` | (declared-only — no emission) | harmless no-op; future-proofed |

### Confirmed MERGE (3, exact-duplicate) — VERIFIED, DEFERRED to W2
| canonical (kept) | absorbs (remove) | proof | why deferred |
|---|---|---|---|
| `x2_headline_svp_engineering_seniority_required` | `x2_headline_seniority_floor_met` | both emit from the SAME `check_headline_seniority_floor` result (identical pass/observed/reason) | removal needs paired edit of `test_remaining_resume_rigor_finish.py:100` |
| `x2_unify_narrative_exactly_one_sentence` | `x2_unify_narrative_exactly_one_sentence_mechanical` | mechanical-registration duplicate of the canonical sentence-count gate | needs SSOT-declaration + test coordination |
| `x2_structured_term_primary_facts` | `x2_competency_term_primary_fact_present` | both assert a term declares a primary `source_fact_id` | cross-file (validators vs diagnostics) — CORRECTNESS, needs coverage proof before removal |

> Merges are coverage-affecting (they delete a registration), so each is gated on a paired
> coverage proof + test update — deliberately separated from the zero-risk severity demotion.
> The 2 empty-`absorbs` "clusters" the synthesis emitted (`x2_generic_filler_zero`,
> `x2_no_five_bullet_roll_up_tone`) had no merge target and are NOT actioned.

### Implementation (W1) — landed
- `apps_rg/runtime/validators/x2_severity.py` — `STYLE_WARN_GATE_IDS` SSOT + `soften_warn_only` + `warn_only_fires` telemetry.
- `soften_warn_only(x2)` applied at the 6 lane gate-assembly sites that emit the demoted gates.
- Proof: `tests/unit/apps_rg/test_x2_severity.py` (7 passed) + stash-isolation diff = **0 new failures** across the touched surface (51 failures all pre-existing baseline).
