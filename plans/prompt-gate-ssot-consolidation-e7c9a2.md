---
plan_type: platform_core_change
slug: prompt-gate-ssot-consolidation-e7c9a2
status: In Progress
ai_summary: "Kill apps_rg prompt↔X1-X3 drift: single numeric SSOT, generated prompt prose, numeric-equality drift gate."
dod_exempt: false
supersedes: []
---

# Prompt ↔ X1–X3 SSOT Consolidation — Kill the Drift

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | |

## Context (SCQA)

- **Situation.** apps_rg section generation has been derailed repeatedly by **prompt drift**: the
  prompt tells the generator one thing (term count, sentence count, word budget, schema fields,
  grounding rule) while the X1/X2/X3 gates enforce another, so generation X3_BLOCKs on contradictions
  the operator never sees.
- **Complication (root cause, audited).** A per-section constraint value is authored in **3–6
  independent places** with **no programmatic binding**: (1) the prompt prose in `*_pa.py`
  `_legacy_i0`, (2) the template YAML `output_contract`/`validation_rules`, (3) the X2 validator
  constants, (4) `section_product_shape_ssot.py`, (5) hardcoded literals re-typed inside X2 validators,
  (6) the compiled R0 JSON schema. `section_product_shape_ssot.py` is a *partial* SSOT (it imports
  some constants and the prompt consumes it as one appended PRODUCT_SHAPE block) — but the prompt's
  **primary instructional body is hand-authored prose**, and the three existing drift audits check
  **regex presence + gate-ID sets, never numeric equality**. So a prompt that says "max 60 words" vs a
  gate that enforces 58 passes every current audit.
- **Question.** How do we make prompt and X1–X3 *structurally unable* to disagree?
- **Answer.** (1) One **numeric constraints SSOT** per section; (2) **generate** the prompt's
  constraint lines from it (don't hand-author); (3) **import** it in every X2 validator (no re-typed
  literals); (4) add a **numeric-equality drift gate** (parse the compiled prompt's stated numbers,
  assert `==` the X2 thresholds) to sit beside the existing gate-ID audit; (5) fix the **parity lies**
  (SSOT advertising gates a lane never emits; dead YAML templates). Plus W0: fix the live
  BLOCKS_GENERATION drifts already gating the AIG E2E.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W0 | P0 | Fix the **live BLOCKS_GENERATION drifts** gating the AIG E2E now | ~120k | ✅ Done | The 5 hard contradictions below resolved; lanes stop blocking on prompt↔gate disagreement. Commits: W0-A `04222155de`, W0-B `2c227fc44c`, W0-C `8b1f5cd733`, W0-D `1cf0ff1bf8`, W0-E `40385c5929`. Each stash-isolated → zero new test failures. |
| W1 | P1 | **Numeric constraints SSOT** — one module owns every per-section count/budget/schema | ~90k | ✅ Done | `section_product_shape_ssot.SECTION_CONSTRAINTS` (all 11 lanes) + `section_numeric_constraints()` accessor, composed entirely from canonical owner constants (exec/headline/competencies/narrative/bullets) — no re-typed numbers. Sync test `test_section_constraints_ssot` asserts each value == its owner + full lane coverage. Commit `09b5b80011`; W0-C test-regression fix `d791128d61`. Audit note: product_shape_ssot was already the aggregator (values agreed); W1 made it the single structured entry point for W3/W4. |
| W2 | P2 | **Collapse duplicated literals** — X2 validators + role_episode + ssot import the SSOT (no re-typed numbers) | ~70k | ⬜ Not Started | `grep` finds 0 re-typed constraint literals; the 6 NARRATIVE_MAX_WORDS copies → 1 |
| W3 | P3 | **Generate prompt prose from SSOT** — `_legacy_i0`/templates interpolate constants, not hand-author | ~110k | ⬜ Not Started | Prompt constraint lines are rendered from the SSOT; no hand-typed counts in prompts |
| W4 | P4 | **Numeric-equality drift gate** (CI) — assert compiled-prompt numbers == X2 thresholds | ~80k | ⬜ Not Started | New gate fails when a prompt number ≠ its gate threshold; wired into CI + the 3 existing audits |
| W5 | P5 | **Fix parity lies + dead templates** (insurtech/ey) | ~70k | ⬜ Not Started | SSOT advertises only emitted gates; dead YAML templates wired or retired |

## W0 — Live BLOCKS_GENERATION drifts (fix first; these are gating the AIG E2E)

| # | Lane | The contradiction | Prompt says | Gate enforces | Fix |
|---|---|---|---|---|---|
| **A** | unify/ibm **narrative** | required judge providers | policy `section_judge_policy` = `(gemini_pro,)` (recalibrated) | `x2_x1d_required_judges_present` reads `REQUIRED_JUDGE_PROVIDERS=[gemini,openai,anthropic]` (3) — `executive_summary_x2.py:384` | **The judge recalibration never propagated to `REQUIRED_JUDGE_PROVIDERS`.** Make it derive from `section_judge_policy.required_judge_providers` per lane (or drop `anthropic_claude`). |
| **B** | **competencies** | category count | R0 schema `competencies_pa.py:67-69` = **6**; `v2.yaml:76-78` = 6; `competencies_contract.yaml` = 6/`graph_10x6` | rigor/SSOT = **8/graph_8x8**; `x2_competencies_*category_count` HARD; forbidden regex `graph_10x6` | Finish the **6→8 migration**: R0 schema + v2.yaml + section-contract → 8 / graph_8x8. (Also surfaces as a live `assert_zero_drift` CI failure.) |
| **C** | **exec_summary** | claim_ledger row count | "3–6 rows; do NOT do one-per-sentence" — `executive_summary.generate_scratch_v1.yaml:107` | `x2_claim_ledger_row_count_matches_sentence_count` → rows **== 6** (one per sentence) — `executive_summary_x2.py:1358` | Reconcile: prompt → "exactly 6 rows, one per sentence" (or drop the row==sentence gate). |
| **D** | **exec_summary** | fact utilization | "do not force every allowed fact" | `x2_exec_summary_allowed_fact_utilization` fails if any non-credential fact uncited — `executive_summary_x2.py:1739` | Prompt → "cite every non-credential allowed fact" (or widen the waiver set). |
| **E** | **headline** | filler nouns + narrowing labels | I0 recommends stoplist words to reach 10 words; only 3 "Bad" examples shown | `xyz_literal_grounding` treats those as non-grounding (`headline_x2.py:98`); `NARROWING_IT_LABELS` HARD-fails a list the prompt never enumerates | Remove filler-noun advice; inject the full `NARROWING_IT_LABELS` blocklist into the headline prompt. |

## W1 — The Numeric Constraints SSOT (the architectural fix)

Create `apps_rg/runtime/sections/section_constraints.py` (or promote `section_product_shape_ssot.py`)
as the **single owner** of every per-section numeric/schema constraint:

```
SECTION_CONSTRAINTS = {
  "competencies": {category_count: 8, terms_min: 2, terms_max: 6, generic_min_graph_terms: 3,
                   term_schema: [text, source_fact_ids, graph_skill_node_ids], labels: [...8...]},
  "executive_summary": {sentences: 6, max_words: 140, max_words_per_sentence: 45,
                        claim_ledger_rows: 6, ...},
  "unify_narrative": {max_words: 58, max_chars: 360, sentences: 1, ...},
  "headline": {word_min: 10, word_max: 13, max_chars: 140, segments: 4, ...},
  "unify_bullets": {count: 6, sc_paths: 2, ...}, ... }
```

- **X2 validators import their thresholds from here** (no `EXEC_SUMMARY_MIN_SENTENCES=6` re-declared in
  the validator; it lives in the SSOT and the validator imports it).
- **The prompt assembly reads here** (W3).
- **The required judge roster derives from `section_judge_policy`** (resolves W0-A permanently).

## W2 — Collapse duplicated literals (audited list)

| Constant | Canonical home (keep) | Re-typed copies to delete (import instead) |
|---|---|---|
| `NARRATIVE_MAX_WORDS=58` / `MAX_CHARS=360` | SSOT | `role_episode_lane.py:55-56`, `unify_narrative_x2.py:483` (hardcoded `<=58 and <=360`) |
| `MIN_ITEMS_PER_CATEGORY=2,MAX=6` | `competencies_rigor.py:13-20` | `competency_capability_evidence.py:375` (fallback `2,6`) |
| `HEADLINE_WORD_MIN/MAX=10/13` | SSOT | `headline_x2.py:581,755` (hardcoded `10<=wc<=13`) |
| `qwen_paths` | `employment_bullet_pool.SC_PATH_COUNT_BY_LANE` (=4… or 2 post-cut) | `unify_bullet_tailor_v1.yaml:103` (15), `ibm_bullet_tailor_v1.yaml:131` (12) — stale |

## W4 — The numeric-equality drift gate (prevents recurrence)

The three existing audits (`section_prompt_drift_audit` = regex presence; `section_prompt_judge_alignment`
= prompt↔judge dimensions; `section_x2_x1d_contract` = gate-ID set ⊆ runtime) do **not** compare
*values*. Add `check_prompt_gate_numeric_parity.py`:
- Compile each lane's prompt; parse the stated numbers (sentence/term/bullet count, word/char budgets).
- Assert each `==` the corresponding `SECTION_CONSTRAINTS` value (which the X2 validator also imports).
- Fail CI on any mismatch. This is the gate that makes drift *impossible to ship*.

## W5 — Parity lies + dead templates
- `section_product_shape_ssot._role_bullets_shape` advertises `x2_*_bullet_single_thought`,
  `x2_no_first_person`, `x2_no_em_dash` (`:521-535`) that `role_episode_lane._x2_gates` never emits →
  emit them or drop them.
- insurtech/ey `*_bullets_tailor_v1.yaml` / `*_narrative_v1.yaml` templates are **never loaded**
  (`role_episode_lane.py:289-311` hardcodes the prompt) yet the artifact claims the template ref →
  load the YAML or retire it + stop referencing it.

## Definition of Done
| # | Criterion | Verification |
|---|---|---|
| 1 | The 5 W0 contradictions resolved | per-lane re-run: the named gate passes; no prompt↔gate contradiction |
| 2 | Every numeric constraint has exactly one definition | grep audit: 0 re-typed literals |
| 3 | Prompt constraint lines are generated from the SSOT | inspect compiled prompt; numbers trace to SSOT |
| 4 | Numeric-equality drift gate green across all lanes | `check_prompt_gate_numeric_parity.py` passes; fails on injected mismatch |
| 5 | SSOT advertises only emitted gates; no dead template refs | parity test + artifact ref check |
| 6 | AIG E2E: lanes no longer X3_BLOCK on prompt↔gate disagreement | full E2E re-run vs baseline |

## Safety / Invariants
- Never weaken a gate to "match" a prompt — reconcile toward the *correct* requirement (usually the gate),
  then regenerate the prompt line from the SSOT.
- W0 fixes are reconciliations (prompt↔gate agreement), not grounding weakenings.
- The numeric-equality gate is the durable guarantee — without it, drift returns.
