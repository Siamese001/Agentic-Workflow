# apps_rg Simplification Audit — 2026-06-06

**Scope.** Identify simplifications that preserve every X2 gate, every X3 disposition rule, every fact-grounding invariant, and every judge contract. **No rigor or quality loss.** This audit names the structural cost drivers and the cheapest seam where complexity can collapse.

**Footprint baseline (measured).**

| Metric | Count |
|---|---|
| `apps_rg/**.py` files | 516 |
| `apps_rg/**.py` lines | 138,166 |
| `apps_rg/runtime/sections/*.py` | 87 |
| `apps_rg/runtime/sections/executive_summary_*.py` | 33 |
| `apps_rg/runtime/validators/*.py` | 30 |
| `apps_rg/runtime/bindings/*.py` | 27 |
| `apps_rg/runtime/c0*.py` (recursive) | 58 |
| `executive_summary_lane.py` | 4,009 lines |
| `executive_summary_x2.py` | 2,808 lines (54 `check_*`, 36 `add("x2_…")`) |
| `executive_summary_judge_remediation.py` | 1,861 lines |

That's a 138 KLOC payload to produce **6 resume sections**.

## Headline diagnosis

apps_rg is over-fit because a series of *correct local fixes* compounded into a *globally entangled pipeline*. The same idea keeps reappearing under new names ("repair", "coercer", "reconciler", "voice-repair", "finalize-coherence", "graph-only-display-authority-fallback", "anchor injection", "post-judge regen", "judge-remediation", "candidate-pool", "publish-disposition", "regen-delta-policy"). Each round of Author-Gate decisions added another interception point but never retired the prior one.

The bug class I just hit (a critical gate emitted only on the strategy lane while the convergence audit demanded it on every lane) is *symptomatic*, not exceptional — it is what happens when a 4 KLOC lane talks to a 2.8 KLOC validator through 4 different copies of `parsed`.

Below are 9 simplifications, ranked by **(rigor-loss risk)** × **(LOC removable)** × **(blast radius reduction)**. Every one is a no-quality-loss move because the underlying gate, judge, or invariant is preserved — only the plumbing collapses.

---

## SIMP-1 — Collapse the four-copy `parsed` pipeline (HIGHEST LEVERAGE)

**Evidence.** `executive_summary_lane.py` carries `parsed`, `parsed_for_x2`, `_pre_parsed`, plus shadow copies of `resume_display_text`, `claim_ledger`, and `x2` set/reset across at least 7 sites (lines 2199, 2234, 2247, 2266, 2320, 2355, 2476, 2497, 2919, 2981, 3018, 3097, 3235, 3418, 3476). Repairs run, then **composition rebuilds parsed**, then **finalize_coherence rebuilds it again**, then `enrich_parsed_for_x2` makes a fifth view for scoring. In the recent run, this is exactly why `parsed_output.json` was an empty stale snapshot while `resume_display_text.txt` was correct.

**Simplification.** A single `SectionResult` dataclass with `text`, `ledger`, `change_log`, `proof_pool`. Every repair takes a `SectionResult` and returns a `SectionResult`. X2 scores from one object. No re-derivation, no `enrich_parsed_for_x2`, no shadow copies.

**Rigor preserved.** Every X2 gate already takes `(resume_display_text, parsed_output, claim_ledger, …)`. Wrapping them in one struct doesn't change a single check.

**Estimated removal.** ~600–900 LOC in `executive_summary_lane.py` alone, plus the entire `enrich_parsed_for_x2` helper.

---

## SIMP-2 — Retire the seven-stage display-repair pipeline behind one ordered list

**Evidence.** A single section run executes, in order:
1. `coerce_resume_display_sentence_count_band`
2. `reconcile_claim_ledger_to_sentence_count`
3. `attach_composition_to_parsed`
4. `apply_exec_summary_display_authority_repairs` (which itself wraps `strip_credential_dump`, `strip_target_company_tailoring`, `repair_orphan_row_with_unused_required_fact` (today's add), `_exec_summary_shape_ok`, `build_graph_only_executive_summary_from_facts`)
5. `finalize_executive_summary_coherence` (wraps `voice_repair`, `gap_excuses`, `materialization`)
6. orphan-citation stripping at lines 2330–2348
7. `apply_exec_summary_display_authority_repairs` again inside the regen loop

Each stage can mutate text + ledger; ordering is implicit; failures cascade silently when one stage's mutation breaks the next stage's pre-condition (today's case).

**Simplification.** Replace with one explicit list:

```python
REPAIR_PIPELINE = [
    strip_credential_dump_sentences,
    strip_target_company_tailoring_sentences,
    coerce_sentence_count_to_target,
    repair_orphan_rows_with_unused_required_facts,
    voice_repair,
    gap_excuses,
    reconcile_ledger_to_sentences,  # ALWAYS LAST — invariant
]
def run_repairs(result: SectionResult) -> SectionResult:
    for step in REPAIR_PIPELINE:
        result = step(result)
    return result
```

Each step receives and returns `SectionResult`. Add a single invariant assertion at the end (`len(rows) == len(sentences)`, `every row has source_fact_ids OR is empty-claim`). The convergence-audit gate I just unblocked becomes redundant — the invariant is enforced at the seam, not via a missing-gate audit.

**Rigor preserved.** Same steps run in the same order with the same logic; only the dispatch is collapsed.

**Estimated removal.** ~400–600 LOC of glue.

---

## SIMP-3 — Delete the `strategy_lane`-only gate carve-outs

**Evidence.** `executive_summary_x2.py` has `if strategy_lane:` blocks at lines 2150, 2541, and (until today) 2173. The two gates I just unconditionally enabled (`x2_claim_ledger_row_count_matches_sentence_count`, `x2_claim_field_maps_to_display_sentence`) were *always* listed in `section_product_shape_ssot.proof_gate_ids` — meaning the conditional emission was a structural bug, not a feature. The convergence audit existed *to detect this bug class*, not to be a routine block.

**Simplification.** Audit every `if strategy_lane:` branch; for each gate inside, decide once:
- Is it lane-agnostic logic? → emit unconditionally (already proven safe for the 2 I touched).
- Is it strategy-specific? → keep the carve-out **and** remove from `proof_gate_ids` so the convergence audit doesn't demand it.

This eliminates a recurring class of deterministic blockers and removes the need for the convergence-audit's "missing rigor critical gate" branch.

**Rigor preserved.** Strengthens it — every gate in the spec runs on every applicable lane.

**Estimated removal.** ~150 LOC of conditionals + the `apply_rigor_convergence_to_x2_payload` BLOCK-injection branch.

---

## SIMP-4 — Fold the 33 `executive_summary_*.py` modules into ≤8

**Evidence.** Twelve of the 33 are <250 lines, one (`executive_summary_judge_regen_thread.py`) is 98 lines. They're 33 separate import surfaces for one section. Many are a single function or a 3-class policy module. Examples worth merging today:
- `executive_summary_judge_regen_loop.py` (439) + `executive_summary_judge_regen_thread.py` (98) + `executive_summary_judge_remediation.py` (1861) + `executive_summary_qwen_regen_dispatch.py` (292) + `executive_summary_regen_observability.py` (419) + `executive_summary_regen_delta_policy.py` (844) + `executive_summary_regen_incremental.py` (235) + `executive_summary_same_authority_regen_bridge.py` (293) → one `executive_summary_regen.py`. **8 files → 1.** Same code, no extra imports, no tangled re-export graph.
- `executive_summary_publish_disposition.py` + `executive_summary_targeting_publish.py` + `executive_summary_lane_done_policy.py` + `executive_summary_operator_disposition.py` → one `executive_summary_publish.py`. **4 files → 1.**
- `executive_summary_briefing.py` + `executive_summary_targeting_context.py` + `executive_summary_targeting_cap.py` → one `executive_summary_targeting.py`. **3 files → 1.**

**Rigor preserved.** No code change — only mechanical merge + import rewrite.

**Estimated removal.** Net file count: 33 → ≤8. Net LOC: roughly unchanged, but the dependency graph collapses by ~70%.

---

## SIMP-5 — Replace the 4-mode generation status with a 2-mode model

**Evidence.** `RUNTIME_GENERATION_STATUS` carries 4 values across the codebase: `REAL_LLM`, `MOCKED`, `OFFLINE_CONTRACT_STUB_RUNTIME_STATUS`, `SIDECAR/PLUMBING_ONLY`. 67 files branch on these. The best-of-N harness had to grow a `runtime_generation_status == REAL_LLM` guard because the other three were silently treated as passes by some callers and blocks by others.

**Simplification.** Two states only:
- `REAL_LLM` → eligible for X3_ALLOW
- `NOT_LIVE` → never eligible; X3 always BLOCK or REVIEW_PLUMBING

Everything else (mock/sidecar/offline-contract) collapses into `NOT_LIVE` with a `not_live_reason` field. The test surface that needs the contract stub keeps using it; the runtime path stops branching on three look-alike flags.

**Rigor preserved.** Tightens it — eliminates the failure mode where a mock path was scored as if it were live.

**Estimated removal.** ~200 LOC of branch logic.

---

## SIMP-6 — Make X2 emission table-driven

**Evidence.** `executive_summary_x2.py` has 36 hand-rolled `add("x2_…", ok, observed, expected, reason)` calls; each is six lines of boilerplate. 54 separate `check_*` functions. Same pattern repeats in every other validator (`ibm_bullets_x2`: 6 adds, `unify_narrative_x2`: 11, etc.). The lane spec already lists which gates apply to which surface in `section_product_shape_ssot.py` — but the validator doesn't read it.

**Simplification.** A `GATE_REGISTRY: dict[str, GateFn]` keyed by gate id; each lane declares the gate ids it needs (already in `section_product_shape_ssot`); `run_x2_gates` iterates the spec and calls registered checks. New gates: 1 function + 1 spec line. No more `add(...)` boilerplate. The strategy-lane carve-out (SIMP-3) becomes a per-lane spec entry instead of an `if` in code.

**Rigor preserved.** Identical gate logic; the spec becomes the SSOT it already claims to be.

**Estimated removal.** ~600 LOC across the 6 large validator files.

---

## SIMP-7 — Drop or archive the `runtime_proofs/.../real|mock|sidecar` directory split

**Evidence.** Single-section runs write to `runtime_proofs/<section>/real/<section>_<timestamp>/` — but every artifact under `mock/` or `sidecar/` is by construction *not* certifying. The harness already filters by `runtime_generation_status`. Maintaining three sibling trees forces every reader (the best-of-N harness, receipt collectors, the assembler, the certification report) to know the layout.

**Simplification.** Flat layout: `runtime_proofs/<section>/<timestamp>/`. A single `run_manifest.json` records `runtime_generation_status`. Readers filter by that field, not by directory.

**Rigor preserved.** The status is already the source of truth; the directory was a hint, not an invariant.

**Estimated removal.** ~150 LOC of layout logic in `runtime_proof_layout.py` and dependents.

---

## SIMP-8 — Replace the best-of-N harness with `--attempts N` on the section runner

**Evidence.** `ops_scripts/apps_rg/best_of_n_section_harness.py` is a wrapper that subprocesses the section runner, parses stdout, and re-scans timestamped artifact dirs. Most of its bugs (parser regex, MOCKED detection, dir lookup, list-vs-dict gate format) come from that boundary. The lane already has a regen loop internally.

**Simplification.** Add `--attempts N --accept review|allow` to `python -m apps_rg`. The lane returns the first accepting attempt's artifact dir; the harness collapses to a 30-line driver that runs once per section. No subprocess parsing, no re-scanning.

**Rigor preserved.** Same N attempts, same acceptance criterion, same artifacts written. Just no IPC-shaped duplication.

**Estimated removal.** Whole `best_of_n_section_harness.py` (~250 LOC) plus its bug-fix history.

---

## SIMP-9 — Move the cross-section guards to a small shared module

**Evidence.** `bullet_quality_floor_x2.py`, `bullet_ngram_overlap_x2.py`, `bullet_line_discipline_x2.py`, `narrative_quality_x2.py`, `narrative_mechanical_x2.py`, `headline_quality_x2.py`, `competencies_quality_x2.py` all implement near-identical helpers (seniority detection, n-gram overlap, generic-consulting phrase lists, JD-only phrase detection). Today these live as siblings; the deferred-scope cross-section helpers were intentionally not extracted because "do not over-refactor."

**Simplification.** Now is the time. One `apps_rg/runtime/validators/_signal_helpers.py` with: `score_seniority_floor`, `score_technical_specificity_floor`, `detect_generic_consulting`, `ngram_overlap`, `detect_jd_only_phrase`, `detect_e0_leakage`, `detect_base_archive_hydration`. Each lane validator imports only what it needs.

**Rigor preserved.** Same checks; one definition each. Removes drift risk where one lane's seniority list grew "owned"/"headed" while another didn't.

**Estimated removal.** ~400 LOC of duplication.

---

## Update 2026-06-06 17:30 — Variance-class triage applied

Re-evaluated against the variance-class mental model:

> SC fixes generation variance. More judges fix evaluation variance. Harder criteria fix low standards. Deterministic gates fix mechanical rules. Upstream fixes fix missing evidence.

Applied the model to the actual block-causes per section and identified compute being spent on the wrong technique:

| Section | Block class | Was using | Cut applied |
|---|---|---|---|
| competencies | mechanical (family coverage) | SC=10 + 4 attempts | SC=4, attempts=2 — anchor injection does the work |
| unify_bullets | none (pinned A1) | SC=15 + 4 attempts | SC=4, attempts=2 |
| ibm_bullets | mechanical (metric drop) + judge variance | SC=12 + 4 attempts | SC=4, attempts=2 — plan-fact metric injection (in tree) does the work |
| executive_summary | mechanical (5 blockers, all deterministic-guard-addressable) | SC=5 + 4 attempts | SC unchanged (5 already low), attempts=2 |
| narratives | upstream missing | 4 attempts each | early-exit on `BLOCKED_UPSTREAM_NOT_FINALIZED` |
| headline | upstream evidence missing (`fact_engineering_platform_001` not in FEC) | 4 attempts | skip until data-wave promotes the fact |

**SIMP-10** (new): Cap SC samples for mechanical-dominated lanes at 4. X2 still scores the selector-picked candidate identically (zero rigor loss); LLM time drops ~75% for those lanes. Implemented in `apps_rg/runtime/reasoning/section_reasoning_intensity.py`.

**SIMP-11** (new): Loop break on `BLOCKED_UPSTREAM_NOT_FINALIZED`. Upstream-evidence-missing is not a retry-class problem; retrying just pays preflight repeatedly. Implemented in `apps_rg/__main__.py`.

**SIMP-12** (new): Headline `fact_engineering_platform_001` FEC promotion is the only path to clear `x2_headline_xyz_literal_grounding`. Validator/lane workarounds were tried and reverted (broke 4 sibling FEC gates). This is the canonical example of "upstream fixes fix missing evidence" — no SC, no judges, no deterministic guard solves it.

Estimated wall-clock: 45 min sweep → ~10 min sweep, same X2 gates, same X3 disposition rules, same judges, no quality loss.

## What I'm NOT recommending (and why)

- **Rewriting the X2 contract.** It's the reason rigor holds. Don't touch.
- **Removing the convergence audit.** Keep it — but make it report-only after SIMP-3 lands, since SIMP-3 makes its current BLOCK pathway redundant. After 90 days with zero injections, retire it.
- **Removing `agentic_core` plumbing.** Out of scope per project rules and not the cost driver.
- **Removing the judge panel.** It's lean already (1.9 KLOC for 3 providers, transport, and decisive aggregation).
- **Touching `augmented_skills_graph_sqlite.py`** (2,114). Big but stable; not on the hot path that hurts daily.

---

## Suggested order of execution

| Wave | Items | Risk | Days |
|---|---|---|---|
| W1 | SIMP-1, SIMP-2 | Medium | 3–5 |
| W2 | SIMP-3, SIMP-6 | Low | 2–3 |
| W3 | SIMP-4, SIMP-9 | Low (mechanical) | 2 |
| W4 | SIMP-5, SIMP-7, SIMP-8 | Low | 2 |

**Total estimated reduction:** ~2,500–3,500 LOC, 33 → ≤8 exec_summary modules, 87 → ~50 section files, 4 → 2 generation modes, 0 lost gates.

## Definition of done (per simplification)

1. `python -m compileall apps_rg -q` exit 0
2. Targeted X2 contract suites for every section pass with the same gate-id set as before
3. Stash-parity check on the 19 known pre-existing failures shows no new entrants
4. One end-to-end live `qwen_vllm` resume run reproduces the same X3 disposition shape the prior run produced (gate-by-gate diff at most 0)
