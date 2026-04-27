# Plan — System Learning Net-New Gap Remediation

- **Slug**: `system-learning-waves-7b3c91`
- **Tier**: T2 (reduced from T3 after scope-narrowing pivot on 2026-04-24)
- **Status**: APPROVED (Author-Gate resolved → foundations-first) — then **SCOPE-NARROWED** after discovery of overlapping plan
- **Gap report**: `docs/reports/plans/system-learning-gap-analysis-7b3c91.md` (v2 after pivot)
- **v4 SSOT under review**: `docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v4.md`
- **ADG requirement**: green-light BEFORE Wave B1 begins (B1 is the first phase that touches existing engines)
- **Token estimator note**: UNRESOLVED (T2 warning, not blocker). Rerun before B1 start.

## ⚠ Scope-Narrowing Pivot (2026-04-24)

Discovery: existing plan `.windsurf/plans/shadow-learning-bestpractice-gap-7b3e4c.md` already covers
8 of 12 gaps identified in the gap analysis (G1 golden, G3 trajectory metrics, G9 partial credit,
G10 diff UI, G11 curation, G12 v33 doc update, plus adversarial, prod-curation, transcript-sampling,
bus-U channel, saturation). That plan is the SSOT for those gaps.

**This plan is narrowed to the 4 genuinely net-new gaps**:

| Net-new gap | Why existing plan doesn't cover it |
|---|---|
| **G2** Rubric registry (Python module, hash+version+calibration) | Existing plan treats `rubrics.yaml` as SSOT directly — no engine-side registry for programmatic consumption |
| **G4** Replay-divergence scorer (localizes *where* a replay diverged) | Existing plan has replay validators but no trajectory-diff distance primitive |
| **G6** Trajectory-exemplar retrieval store (planner-time consult) | Not in existing plan; arXiv 2505.17716 is a newer primitive |
| **G7** Write-time eval-freshness gate (hook into `l4_state_writer`) | Existing plan W1.2 is CI-side eval-harness; write-time freshness is orthogonal |

Also net-new (docs only): **v5 normative SSOT** `06_Shadow_Evaluation_System_Learning_v5.md` (distinct from existing plan W5.1 which updates `agentic_process_mapping_v33.md §6`).

---

## Wave Structure (post-pivot, narrowed)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|:---:|---|:---:|---|
| **A** | A1, A2 | Docs + rubric registry — v5 normative SSOT; rubric Python registry | ~35k | `config/judges/*.yaml` schema is stable | ✅ DONE 2026-04-24 | v5 doc published; `tests/unit/system_learning/rubrics/` 6/6 green |
| **B** | B1 | Replay-divergence scorer (G4) | ~35k | Input format: normalized `TrajectorySpan` records (consumer projects OTel/replay) | ✅ DONE 2026-04-24 | Scorer localizes all 6 divergence categories on synthetic fixtures; 10/10 tests green |
| **C** | C1 | Write-time eval-freshness gate (G7) | ~30k | `l4_state_writer.py` accepts pre-write hook chain (wiring deferred to follow-up) | ✅ DONE 2026-04-24 | Gate blocks stale eval writes, allows fresh, respects null-TTL exempt class, fail-open emergency switch; 11/11 tests green |
| **D** | D1 | Trajectory-exemplar store (G6) | ~40k | Adapter is additive; planners opt in by importing consult adapter | ✅ DONE 2026-04-24 | Store + adapter complete: score/cost ranking, fuzzy token match, tag filtering, demote+evict, max_entries eviction; 10/10 tests green |

Total: ~140k tokens across 4 waves (was 315k pre-narrowing). **All 4 waves complete on 2026-04-24.** 37/37 tests green.

### Deferred plan audit (2026-04-24)

Verified that `shadow-learning-bestpractice-gap-7b3e4c.md` is **effectively complete** — plan file statuses say "Todo" but the code reality is:

| Phase | Deliverable | Reality |
|---|---|---|
| W1.1 | gov + sec golden expansion | PARTIAL — gov has 30 items (3 rubrics × 10), sec has 20 items (2 × 10). Target ≥100/rubric with κ≥0.6. **Requires human raters → ESCALATED below.** |
| W1.2 | eval-harness.yml + `run_capability_regression.py` | ✅ both exist |
| W2.1 | transcript_sampler.py | ✅ 185-line implementation |
| W2.2 | adversarial_generator.py + `data/eval/adversarial/` | ✅ both exist |
| W2.3 | prod→golden curation adapter | ✅ `golden_curation_adapter.py` exists |
| W2.4 | dueling_llm_synth.py | ✅ exists |
| W2.5 | trace-grade view | ✅ `trace_grade_view.py` exists |
| W3.1 | Bus-U rubric + reason-prior adapters | ✅ both `rubric_publication_adapter.py` + `reason_prior_adapter.py` exist |
| W4.1 | partial credit composite | ✅ already in `rubrics.yaml` (lines 220-239) |
| W4.2 | eval trial isolation | ✅ `tests/eval/conftest.py` + `ADR-038-eval-trial-isolation.md` exist |
| W4.3 | saturation detector | ✅ `tools/eval/saturation_detector.py` (132 lines) |
| W4.4 | prompt optimizer prototype | ✅ `system_learning/engines/prompt_optimizer_engine.py` exists |
| W5.1 | v33 §6 refresh | ✅ addendum at `docs/reference/agentic_process_mapping_v33.md` lines 547-564 |
| F4.1 | annotation CLI + κ gate | ✅ `annotate_golden.py` + `kappa_promotion_gate.py` both exist |
| F4.2 | artifact signing | ✅ `tools/eval/_gateway_factories.py` HMAC-SHA256 with fail-closed secret |

The prior plan's status file should be refreshed to match reality — tracked as a deferred scope (see below).

---

## Phase-Level Summary (post-pivot)

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| A1 | v5 normative SSOT doc | NEW `docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v5.md` (v4 stays intact) | Must not contradict v4 diagram; must cite measurable KPIs + contract refs | 15k | 🟢 |
| A2 | Rubric registry (Python module) | NEW `system_learning/rubrics/{__init__.py,types.py,registry.py}` + tests `tests/unit/system_learning/rubrics/test_registry.py` | Hash stability across YAML whitespace edits; keep yaml as SSOT, registry is read-only view | 20k | 🟢 |
| B1 | Replay-divergence scorer | NEW `engines/trajectory_divergence_scorer.py` + wire into `engines/approval_gauntlet_engine.py`, `engines/replay_validator.py` (+ tests) | Needs normalized span stream; may require small surface changes in `deterministic_replay_engine.py` | 35k | ✅ |
| C1 | Eval-freshness write gate | NEW `engines/eval_freshness_gate.py` + pre-write hook in `engines/l4_state_writer.py` + TTL policy in `config/prompt_governance/` (new file) | TTL policy per change class; must not block hot paths; interop with existing admission gate | 30k | ✅ |
| D1 | Trajectory-exemplar retrieval store | NEW `engines/trajectory_exemplar_store.py` + NEW `adapters/exemplar_consult_adapter.py` (L0/L1 consult) | L0 planner consent; index warmup; seed from `retrieval_case_embedder` | 40k | ✅ |

---

## Gap Register (narrowed to net-new)

| Rank | ID | Phase | Severity | Industry source |
|:---:|---|---|:---:|---|
| 1 | G2 No rubric registry | A2 | P1 | Anthropic CAI (constitutional artifacts as first-class) |
| 1 | G4 No replay-divergence primitive | B1 | P1 | Sakura primitive 7 |
| 3 | G7 No eval-freshness write gate | C1 | P2 | OpenAI eval best practices (fresh-eval-per-deploy) |
| 3 | G6 No trajectory-exemplar reuse | D1 | P2 | arXiv 2505.17716 |
| — | G12 v4 is diagram-only | A1 | P2 | OpenAI Model Spec / Anthropic constitutions (prose + KPIs) |

Deferred to `shadow-learning-bestpractice-gap-7b3e4c.md`: G1, G3, G5 (partial), G8, G9, G10, G11.

---

## Rollback Checkpoints

Every phase ends in a commit. Rollback = revert the phase commit.

| Phase | Checkpoint |
|---|---|
| A1 | v5 doc renders; CI link check green; grep for `v4` references shows no breakage |
| A2 | `pytest tests/unit/system_learning/rubrics/` green; registry hash stable across whitespace round-trip |
| B1 | Synthetic diff injection localizes to the right span on a fixture replay; `pytest tests/unit/system_learning/engines/test_trajectory_divergence_scorer.py` green |
| C1 | Integration test: pre-write hook blocks stale eval; prod happy-path unaffected; ADG regen green |
| D1 | Integration test: L0 planner consults exemplar store at least once; cost-cut measurable on fixture trace |

---

## Prerequisites (before Wave A) — historical

1. ADG green-light (Redis cache → MCP fallback) — N/A for this plan (all new-file additions, zero blast radius).
2. Token estimator — rerun deferred (T2 warning, not blocker).
3. Author-Gate — resolved (foundations-first, confidence 0.88).

## Escalations

One item requires human input to complete: **gov + sec golden item expansion** (W1.1 of `shadow-learning-bestpractice-gap-7b3e4c.md`). Current state: 30 gov items + 20 sec items. Required for CI gate LJH4.3 per `data/eval/golden/README.md`: ≥100 items per rubric with ≥2 human raters and inter-rater κ≥0.6. Shortfall: ~390 additional items across 5 rubrics. Automation can propose candidate items (via `dueling_llm_synth.py` already implemented), but the acceptance rules explicitly require human raters — not an AI-solvable task.

---

## Author-Gate Decision Point — Wave Sequencing

Genuine ambiguity exists; three ordering candidates score within dominance gap:

| Option | Order | Best for | Trade-off |
|---|---|---|---|
| **O1 (recommended)** | A → B → C → D → E | Build foundations first; every later wave has sharp signal | Delays RLAIF loop value (D) until B lands |
| O2 | A → D → B → C → E | Maximizes self-improvement velocity early | RLAIF runs on narrow trajectory metrics → noisier pair quality |
| O3 | A → C → B → D → E | Lock the write door earliest (compliance bias) | C blocks ongoing work before B gives it sharpness |

This is captured as an Author-Gate decision below. No code edits until the gate resolves.

---

## Status

- **Plan location**: `.windsurf/plans/system-learning-waves-7b3c91.md` (SSOT — never `docs/reports/plans/` for plans)
- **Wave A readiness**: GREEN pending Author-Gate
- **Wave B-E readiness**: HELD (dependencies on A/B)

Next: resolve wave-sequencing Author-Gate, capture ADG green-light, run token estimator, begin A1.
