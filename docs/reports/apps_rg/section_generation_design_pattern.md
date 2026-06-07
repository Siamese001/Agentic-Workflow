# apps_rg Section Generation Design Pattern (variance-class triage)

> **Mental model.** SC paths fix generation variance. Deterministic rules fix known required content. LLM judges select among valid candidates. Retries fix repairable failures only. Retries do not fix missing upstream evidence.

This is the pattern every section lane in `apps_rg/runtime/sections/` should follow. SC paths above ~4 are wasted compute when the dominant failure is anything other than generation variance.

## The pattern

```
SOURCE FACTS
   |
   v
DETERMINISTIC BULLET PLAN
   - required anchors
   - locked metrics
   - role tags
   - forbidden claims
   - max bullet count
   |
   v
SMALL SC GENERATION
   - IBM bullets       : SC=3-4
   - Unify bullets     : SC=4 (angle-diverse)
   - Competencies      : SC=1-2 (or fully deterministic render)
   - Executive summary : SC=5
   - Narratives        : SC=4-6
   - Headline          : SC=1 (T0_LOCKED)
   |
   v
DETERMINISTIC FILTERS / REPAIRS
   - metric preserved?
   - banned phrase?
   - length within bounds?
   - duplicate?
   - missing required anchor?
   - evidence available?
   - orphan ledger row? (repair with unused required fact)
   |
   v
LLM JUDGE
   - score valid candidates
   - select top N
   - explain failure reason internally
   |
   v
X2 AGGREGATION
   - combine hard checks + judge score
   - select candidate set
   |
   v
EXIT (X3)
   - pass / repair / block / abstain
```

## Per-section dominant risk and the right tool

| Section | Dominant risk | Best control | SC value |
|---|---|---|---|
| **IBM bullets** | Dropping or mutating hard metrics | Deterministic metric/anchor injection | Low (3-4) |
| **Unify bullets** | Becoming vague, generic, over-claimed, or not agentic enough | Judge for specificity, credibility, role fit | Medium-low (4) |
| **Competencies** | Missing required anchored terms | Deterministic inclusion rules | Very low (1-2) |
| **Executive summary** | Sentence count, claim coverage, fact utilization | Deterministic guards + small SC | Low-medium (5) |
| **Narratives** | Story shape, flow, positioning | SC + judge actually matter here | Higher (4-6) |
| **Headline** | T0_LOCKED canonical phrasing | Deterministic + bundle binding | None (1) |

## SC vs. LLM judge — when to use which

| Self-consistency paths | LLM-as-judge |
|---|---|
| Creates multiple candidate bullets | Scores/ranks candidate bullets |
| Useful when wording/angle is uncertain | Useful when quality criteria are complex |
| Fixes generator randomness | Fixes selection uncertainty |
| Should be small when anchors are deterministic | Should be strict when facts/metrics matter |
| Bad use: 15 paraphrases of same metric bullet | Good use: reject metric drift or vague fluff |
| Belongs in L2 generation | Belongs in Exit/X1/X2 evaluation |

> **Key invariant.** SC creates options. Judge decides whether any option deserves to live.

## Per-section mental model

```
IBM bullets        : "Do not lose the facts."
Unify bullets      : "Do not lose the differentiation."
Competencies       : "Do not lose the required anchors."
Narratives         : "Find the best story."
Executive summary  : "Hit the structural shape AND every required fact."
Headline           : "Match the locked canonical phrasing."
```

Which means:

```
IBM        = deterministic anchors first, judge second, SC small
Unify      = deterministic anchors + angle diversity, judge heavier, SC small-medium
Competencies = deterministic render, minimal SC
Narratives = SC and judge actually matter
Exec sum   = deterministic guards (sentence count coercer, orphan-row repair) + SC=5
Headline   = T0_LOCKED, no SC
```

## Retry logic (failure-class based)

| Failure class | Retry helps? | Correct action |
|---|---:|---|
| JSON malformed | Yes | Local repair |
| Weak phrasing | Maybe | Regenerate small set |
| Judge tie | Maybe | Add 2 more SC paths |
| Metric dropped | Sometimes | Repair with locked anchor (deterministic) |
| Sentence count off-by-one | No (mechanical) | Deterministic coercer |
| Orphan ledger row | No (mechanical) | Deterministic orphan-row repair |
| Missing upstream evidence | **No** | Block / skip / wait for upstream |
| Dependency not finalized | **No** | Early exit |
| Headline fact not in FEC | **No** | Data wave (FEC promotion) |
| Final evidence contract not passable | **No** | Surface the contract failure |

```python
# implemented in apps_rg/__main__.py best-of-N loop
if failure_class in {
    "BLOCKED_UPSTREAM_NOT_FINALIZED",
    "UPSTREAM_EVIDENCE_MISSING",
    "REQUIRED_DEPENDENCY_EMPTY",
    "FINAL_EVIDENCE_CONTRACT_NOT_PASSABLE",
}:
    break
```

## Default settings (current)

| Section | SC paths | `--attempts` default | Notes |
|---|---:|---:|---|
| Competencies | 2 | 1-2 | Mostly deterministic (anchor injection + Pass-0 family coverage) |
| IBM bullets | 4 | 2 | Plan-fact metric injection + gated-FinOps demotion deterministic |
| Unify bullets | 4 | 2 | Angle-diverse paths preferred over volume |
| Executive summary | 5 | 2 | All known mechanical blockers covered by deterministic guards in tree |
| Narratives | 4 | 2 | Real prose uncertainty — SC genuinely helps |
| Headline | 1 (T0_LOCKED) | 0 if upstream blocked | Skip when FEC missing |

Set in `apps_rg/runtime/reasoning/section_reasoning_intensity.py`. The variance-class taxonomy is documented inline at the top of that file as well.

## Adaptive SC (future)

Today's SC count is fixed per lane. The next refinement is adaptive:

```
start with SC=4 (or per-lane floor)
judge candidates
if hard pass AND top candidate's score margin >= threshold:
    stop
else if failure is repairable:
    add 2 more SC paths OR run deterministic repair once
else:
    block / skip / surface dependency failure
```

This requires hooking into the lane's regen loop to consume judge confidence. Deferred. Captured in [`simplification_audit_20260606.md`](simplification_audit_20260606.md) as SIMP-13 (future).

## Bullet judging: deterministic validator + 1 composite judge + optional adjudicator

Bullet sections (`ibm_bullets`, `unify_bullets`) no longer run a 3-judge panel on every run. The pattern is:

1. **Deterministic hard validator (X2 gates)** — mechanical correctness (metric preserved, single thought, bundle id present, n-gram overlap, etc.). A hard X2 failure rejects the candidate; retries/SC cannot fix it.
2. **ONE batched composite LLM judge** (`anthropic_claude` by default) — selects among valid candidates and grades the merged output.
3. **Code-based X2 aggregation** (`apps_rg/runtime/judges/bullet_x2_aggregation.py`) — deterministic accept decision combining hard gates + composite judge:
   - any hard X2 fail -> `REJECT_X2_HARD_FAILURE`
   - judge decisive failure / below `pass_threshold` (0.72) -> `REJECT_JUDGE_DECISIVE`
   - accept, but margin below `margin_threshold` (0.05) -> `ACCEPT_BORDERLINE_ADJUDICATE`
   - otherwise -> `ACCEPT`
4. **Optional triggered adjudicator** (`apps_rg/runtime/judges/bullet_adjudicator.py`) — escalates to the full 3-provider panel ONLY when a borderline condition fires. It is a **second opinion, not a regeneration**; panel rows are appended to the X1D set that X3 then aggregates (more judges can only make X3 stricter, never weaker).

Implemented adjudicator triggers (all use data already on the composite judge row + X2 result):

| Trigger | Condition |
|---|---|
| `JUDGE_CONFIDENCE_LOW` | composite normalized_score within `±band` of its threshold (borderline) |
| `X2_PASS_JUDGE_RISK` | all hard X2 gates pass, but the judge flagged decisive_failure / soft-fail / non-empty findings |
| `METRIC_BULLET_BORDERLINE` (IBM only) | a high-value metric bullet is present AND the judge is borderline |

**Deferred:** `TOP_TWO_WITHIN_MARGIN`. The Claude pool selector currently emits only the winning score per slot (no runner-up), so a real candidate-to-candidate margin cannot be computed without changing the selector output schema. Documented here as a future refinement.

Lane wiring: IBM bullets lane runs the trigger/aggregation after X2 (so failed-gate ids are known), conditionally invokes the panel, and writes `bullet_adjudication.json` + `bullet_x2_aggregation.json` evidence.

## Deterministic validator coverage audit (2026-06-06)

Cross-referenced the orchestration-redesign prompt's per-section `deterministic_validator.checks` (~60 named checks) against existing X2 gate ids. Coverage is essentially complete. **3 named checks have no single dedicated gate; all are covered by composition** (decision: document, do not add new gates — zero blast radius, no re-pin):

| section | prompt check | coverage |
|---|---|---|
| `unify_bullets` | `no_unsupported_agentic_or_platform_claim` | `x2_unify_flat_skill_only_graph_packet_forbidden` + `x2_unify_source_fact_or_graph_lineage_required` (note: unlike IBM's `x2_no_agentic_inflation`, "agentic" IS supported for the Unify platform role; the real risk is *unsupported* claims, which the lineage+packet gates already block) |
| `ibm_narrative` | `graph_skill_node_ids_required` | WARN proxy `x2_narrative_upstream_graph_proof_required` (upstream bullet gate carries the graph-skill requirement) |
| `executive_summary` | `seniority_preserved` | `x2_target_title_inflation_zero` + `x2_unsupported_claim_zero` (no-new-proof gates prevent demotion below upstream-bound seniority) |

The competencies category count is locked at **6** (`MIN_CATEGORY_COUNT == MAX_CATEGORY_COUNT == 6`); the prompt's "8" was illustrative and was not adopted (would break pinned competencies fixtures).

## What this replaces

The previous mental model was: **"every bullet section has high creative uncertainty, brute-force SC will solve it."** That model produced SC=15 / 12 / 10 for the bullet pools and a 45-minute end-to-end resume runtime, while the dominant failures (metric drop, missing anchor, sentence count, orphan row, upstream missing) were not generation-variance failures at all. The new model produces ~10-minute end-to-end runtime with **identical X2 gates, identical X3 disposition rules, and identical judges** — zero rigor loss.
