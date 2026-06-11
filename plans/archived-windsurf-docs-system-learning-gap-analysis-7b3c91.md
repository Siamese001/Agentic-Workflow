---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\system-learning-gap-analysis-7b3c91.md'
original_relative_path: 'system-learning-gap-analysis-7b3c91.md'
source_sha256: b02e12eae16928cac4bc3cda27f18d9db75ac1646ca50dcc4926dc5c8143ed78
recovered_status: LOST_RECOVERED
last_commit: 'dd048e0b048'
last_commit_date: '2026-04-25 04:48:26 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# System Learning — Industry Gap Analysis (OpenAI / Anthropic / Google vs. v4 SSOT)

**Date**: 2026-04-24
**Scope**: Compare `docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v4.md`
(v4 SSOT, 44 lines, 6A→6D architecture) and the realized `system_learning/` implementation
(~35 subpackages, ~90 engines) against public state-of-the-art from
OpenAI Evals, Anthropic Constitutional-AI / RLAIF, and Google's "methodical agent evaluation",
plus Sakura's "deterministic replay primitives" and ArXiv 2505.17716 (LLM record & replay).
**Purpose**: identify gaps, then remediate in waves.

---

## 1. v4 SSOT — the architecture being measured

Phase 6 is Night-Shift / Board Meeting: runtime is walled off; learning informs **future** runs only.

| Phase | Steps (S*) | Intent |
|---|---|---|
| **6A INGEST** | S1A gather exhaust (telemetry, exits, traces, artifacts, HITL packets) / S1B normalize & preserve lineage / S1C **observer law** (read-only, no live mutation) | Turn raw run-time exhaust into replay-linkable evidence |
| **6B EVALUATE** | S2A outcome evals (completion, groundedness, citation) / S2B trajectory evals (tool order, retries, budget) / S2C governance regression (exact-match drift, schema drift, guardrail fails) / S2D human calibration (SME spot checks, grader calibration, scorer drift) | Score both *result* and *path*, with human anchor |
| **6C RCA / SYNTH** | S3A signal fusion (BUS P + BUS T, severity+drift, confidence bands) / S3B incident RCA (isolate fail chain, drift cluster map) / S3C rule drafting (prompts, policies, rubrics — **propose only**) | Synthesize proposals; floor staff may propose, never commit |
| **6D PROMOTE / UPDATE** | S4A gauntlet (shadow replay, regression packs, SME safety signoff) / S4B approve/reject (no silent promote, no partial bypass) / S4C **UWG master clerk** (sole ink path to L4) / S4D ledger proof (audit hashes, replay strictness, rollout receipts) | Only way state changes is through UWG; everything signed |

Invariants:
- EVAL **must precede** LEARNING (firewall against recursive degradation)
- No live patron impact, future visits only
- UWG = sole ink path
- Learning signals inform the next run; they do **not** rescue the completed one

---

## 2. Industry state-of-the-art (April 2026)

### 2.1 OpenAI (Evals + evaluation-best-practices)
- **Continuous evals gate deployments**: not a one-time check; every prompt/policy/model upgrade is re-graded against the registry.
- **Registry of eval templates**: programmatic + model-graded; HealthBench-style domain specialization.
- **Evals as the *only* real improvement lever** for LLM apps (acknowledged in official docs).
- Implication: evals are not optional instrumentation — they are the product's steering wheel.

### 2.2 Anthropic (Constitutional AI + RLAIF)
- **AI feedback substitutes for human labels at scale**: constitutional principles + self-critique loop produce preference data.
- **Preference model trained from AI feedback** becomes the reward signal (RL from AI Feedback).
- **Rubric-driven self-critique** is the key mechanism — every response is evaluated against an explicit constitution before training signal is derived.
- Implication: rubrics are first-class artifacts with versioning and calibration, not prompt-embedded strings.

### 2.3 Google Cloud (methodical agent evaluation)
4 pillars:
1. **Define purpose** — evals serve a product contract.
2. **Method mix**: deterministic assertions + LLM-judge + human — not a single modality.
3. **Golden dataset as quality gate** — even a small one; authors explicitly warn it should *not* be a blocker-to-start.
4. **Operationalize** — CI/CD integration, regression gates, dashboards. "Trajectory" = sequence of reasoning + tool calls, graded separately from outcome.

### 2.4 Sakura — 7 primitives of deterministic replay
1. Structured execution trace (typed span events)
2. Stable model + tool metadata (versioned, hashable)
3. Replay engine (indexed, query-able)
4. Deterministic stubs for LLMs and tools
5. Deterministic agent harness
6. Governance integration (audit, policy hooks)
7. Deterministic regression testing

### 2.5 ArXiv 2505.17716 — Record & Replay for LLM agents
- Treats past successful trajectories as **cacheable experience**; replay reduces cost and variance.
- Agent "experience" is a retrievable asset alongside RAG corpus.

---

## 3. Implementation scan — `system_learning/` (current state)

Engines that clearly map to v4 phases (non-exhaustive):

| v4 Step | Realized module(s) |
|---|---|
| S1A/S1B ingest+normalize | `engines/telemetry_consumer.py`, `engines/historical_ingestion_orchestrator.py`, `engines/historical_backfill_engine.py`, `adapters/otel_telemetry_store_adapter.py`, `engines/prompt_execution_tracer.py` |
| S1C observer law | `engines/surface_isolation_validator.py`, `engines/stage_barrier_enforcer.py` |
| S2A outcome evals | `engines/outcome_evaluation_engine.py`, `engines/offline_healing_outcome_evaluator.py` |
| S2B trajectory evals | `engines/trajectory_evaluation_engine.py`, `engines/trace_feature_extractor.py` |
| S2C governance regression | `engines/g_gate_regression_checker.py`, `engines/prompt_drift_detector.py`, `engines/shadow_drift_analyzer.py` |
| S2D human calibration | `engines/human_calibration_engine.py`, `engines/hitl_decision_logger.py` |
| S3A signal fusion | `engines/signal_aggregator_engine.py`, `engines/signal_grouping_engine.py`, `engines/meta_learning_bus.py` |
| S3B incident RCA | `engines/rca_engine.py`, `engines/rca_cluster_engine.py`, `engines/pattern_analysis_engine.py` |
| S3C rule drafting | `engines/rule_drafting_engine.py`, `engines/l1_model_proposer.py`, `engines/l5_policy_proposer.py`, `engines/retrieval_profile_proposal.py`, `engines/rag_proposer.py` |
| S4A gauntlet | `engines/approval_gauntlet_engine.py`, `engines/gauntlet_gate.py`, `engines/deterministic_replay_engine.py`, `engines/replay_validator.py`, `engines/retrieval_profile_replay_check.py` |
| S4B approve/reject | `pipelines/approval_gate_impl.py`, `pipelines/approval_gates.py`, `engines/system_learning_admission_gate.py` |
| S4C UWG ink path | `engines/l4_state_writer.py`, `engines/l4_audit_reader.py`, `engines/l4_version_store.py` |
| S4D ledger proof | `engines/meta_learning_replay_binding.py`, `engines/meta_learning_state_digest.py`, `engines/faiss_startup_integrity.py` |

Peripheral/supporting: embedding corpus + retention (`embedding_*`), governance reward model (`governance_reward_model.py`), RLHF optimizer (`rlhf_optimizer.py`), confidence (`confidence/`), validators (`validators/`).

**Coverage at the engine level is deep.** The gaps are in assets, wiring, and lifecycle discipline — not in the presence of code.

---

## 4. GAP REGISTER

Graded Severity: **P1 (critical)**, **P2 (important)**, **P3 (nice-to-have)**. Each gap cites the industry source it is measured against and the realized code locus.

### G1 [P1] Empty golden dataset scaffold (Google §3)
- **Observed**: `system_learning/golden/` contains only an empty `__init__.py` (0 bytes); `data/eval/golden/` exists but content is not wired into the engine side.
- **Industry**: Google explicitly makes a golden dataset the *quality gate*. OpenAI registry is essentially a curated golden.
- **Impact**: Gauntlet (S4A) runs cannot prove "no regression" without a curated reference set; promotion gate (S4B) operates on thin evidence.
- **Fix surface**: populate `system_learning/golden/` with a loader + schema + small seed set; bind to `approval_gauntlet_engine` and `g_gate_regression_checker`.

### G2 [P1] Rubric versioning + calibration is not a first-class artifact (Anthropic §2.2)
- **Observed**: `config/judges/rubrics.yaml` and `trace_rubric.yaml` exist, but no engine-owned rubric-registry module with hash+version+calibration-score. `human_calibration_engine.py` exists but is not wired into a *rubric lifecycle*.
- **Industry**: Anthropic's CAI makes the constitution an explicit, version-controlled asset with calibration against human SMEs on a cadence.
- **Impact**: Rubric drift is invisible; judge scores can silently degrade.
- **Fix surface**: `system_learning/rubrics/` package + registry + `judge-calibration-cadence` workflow wiring (rule exists: `.windsurf/rules/judge-calibration-cadence.md`).

### G3 [P1] Trajectory evaluation metrics are narrow (Google §2.3 + v4 S2B)
- **Observed**: `trajectory_evaluation_engine.py` exists (17KB) but from v4 text only lists: tool order/choice, retry thrash, budget/latency.
- **Industry**: Google trajectory rubric additionally covers *plan fidelity*, *unnecessary-step ratio*, *backtrack count*, *tool-call success rate per tool type*, *cost-per-outcome*. Sakura adds *replay divergence score*.
- **Impact**: Partial trajectory vision → false-pass on bad paths that happen to produce correct outcomes.
- **Fix surface**: extend `trajectory_evaluation_engine` metric vocabulary; add per-tool span feature extraction in `trace_feature_extractor`.

### G4 [P1] No explicit replay-divergence regression primitive (Sakura §2.4 primitive 7)
- **Observed**: `deterministic_replay_engine.py` + `replay_validator.py` + `g_gate_regression_checker.py` exist, but no module computes a normalized *trajectory-diff distance* between replay and baseline beyond exact-match.
- **Industry**: Sakura mandates a deterministic regression harness that reports *where* the run diverged and *why* (tool args changed, model metadata changed, stub miss).
- **Impact**: Regression signal is binary ("exact-match failed") rather than localized ("tool X arg 'threshold' changed 0.7→0.9 at span 34").
- **Fix surface**: new `engines/trajectory_divergence_scorer.py` + wire into gauntlet.

### G5 [P2] RLAIF loop is half-closed (Anthropic §2.2)
- **Observed**: `rlhf_optimizer.py` + `governance_reward_model.py` + `l1_model_proposer.py` + `l5_policy_proposer.py` exist. Not clear from tree there is a **preference-pair producer** driven by the constitution (rubrics) that feeds the reward model.
- **Industry**: CAI pipeline = (response, critique, revision) × constitution → preference pair → reward model → RL. Missing step is the critique→pair producer.
- **Impact**: Reward model likely trains on heuristic signals rather than constitutionally-derived AI preferences; self-improvement loop runs at half speed.
- **Fix surface**: `engines/constitutional_preference_producer.py` that consumes (trace, rubric, constitution) → emits (preferred, dispreferred, reason) pairs into the reward model.

### G6 [P2] Experience-reuse layer missing (ArXiv 2505.17716)
- **Observed**: `retrieval_case_embedder.py` + `enhanced_rag_retrieval_cache.py` + `seed_embedding_pack_builder.py` exist. No clear "successful trajectory → retrievable exemplar" cache exposed to L0/L1 at *plan time*.
- **Industry**: Record-and-replay literature treats past trajectories as a *retrieval corpus* consulted before planning, cutting cost 30-60%.
- **Impact**: Every run re-derives plans from zero; no compound learning at the planning layer.
- **Fix surface**: `engines/trajectory_exemplar_store.py` + L0/L1 consult adapter.

### G7 [P2] Continuous-eval gating is not enforced at write time (OpenAI §2.1 + v4 S4B)
- **Observed**: `pipelines/approval_gate_impl.py` and `system_learning_admission_gate.py` exist, and `.windsurf/rules/evaluation-promotion-gate.md` encodes the invariant. What's unclear is whether every prompt/policy/config change routed through UWG is blocked on a fresh eval pass.
- **Industry**: OpenAI best-practices: every deployment is a re-graded deployment. No stale-eval promotions.
- **Impact**: Possible silent promotions if eval staleness is not checked.
- **Fix surface**: add `eval_freshness_gate.py` tied to `l4_state_writer.py` — writes blocked if last-eval-age > TTL per change class.

### G8 [P2] Human-calibration cadence watchdog not implemented in code (rule §judge-calibration-cadence)
- **Observed**: Rule file exists. `human_calibration_engine.py` exists. No budget watchdog + alerting layer that *blocks* judge use when calibration is stale.
- **Industry**: Both CAI and Google insist on bounded human-anchor cadence.
- **Fix surface**: `engines/judge_calibration_watchdog.py` + integration with L6 observability.

### G9 [P3] Signal fusion weights are not learned (v4 S3A)
- **Observed**: `signal_aggregator_engine.py` + `signal_grouping_engine.py` exist. Likely static weights.
- **Industry**: Google + OpenAI converge on *learned* aggregation (meta-judge), or at least periodically-refit heuristics.
- **Fix surface**: add weight-refit job in `meta_learning_pipeline`.

### G10 [P3] No standardized trajectory-diff UI artifact (Google §4 operationalize)
- **Observed**: Diffs live in logs + JSONL; no rendered report.
- **Industry**: Modern eval harnesses (DeepEval, Vertex AI Eval) ship an HTML diff viewer as a first-class deliverable.
- **Fix surface**: small renderer under `system_learning/output/`.

### G11 [P3] Golden-curation adapter is a stub relative to ingest volume
- **Observed**: `adapters/golden_curation_adapter.py` is 3.8KB — a thin surface relative to `system_learning_memory_bridge.py` at 67KB.
- **Industry**: Curation is a whole engineering discipline (active learning, disagreement sampling).
- **Fix surface**: expand curation to at least disagreement-based sampling.

### G12 [P2] SSOT doc (v4 44 lines) is a diagram-only artifact
- **Observed**: Industry SSOTs (e.g., OpenAI Model Spec, Anthropic's constitutions, Google's agent eval pillars) pair diagrams with explicit *normative* prose, measurable KPIs, and contract references.
- **Industry**: Fowler / OpenAI / Anthropic all maintain normative prose + SLOs for the same architecture they diagram.
- **Fix surface**: `06_Shadow_Evaluation_System_Learning_v5.md` with normative prose, KPI table, contract refs — leaving v4 diagram intact.

---

## 5. Prioritization — scoring

Formula: `impact = severity_weight × surface_coverage × reversibility_bonus`
(P1=3, P2=2, P3=1; surface_coverage = {narrow:1, medium:2, broad:3}; reversibility_bonus = {code-only:1.0, code+data:0.9, code+data+migration:0.8})

| ID | Title | Severity | Surface | Rev. | Score | Rank |
|---|---|:---:|:---:|:---:|:---:|:---:|
| G1 | Golden dataset scaffold | P1 | broad (3) | 0.9 | 8.1 | 1 |
| G3 | Trajectory metrics widening | P1 | medium (2) | 1.0 | 6.0 | 2 |
| G4 | Replay divergence scorer | P1 | medium (2) | 1.0 | 6.0 | 2 |
| G2 | Rubric registry + calibration | P1 | medium (2) | 0.9 | 5.4 | 4 |
| G7 | Eval-freshness promote gate | P2 | broad (3) | 0.9 | 5.4 | 4 |
| G5 | Constitutional preference producer | P2 | medium (2) | 0.9 | 3.6 | 6 |
| G12 | v5 normative SSOT | P2 | narrow (1) | 1.0 | 2.0 | — |
| G6 | Trajectory-exemplar store | P2 | medium (2) | 0.9 | 3.6 | 6 |
| G8 | Calibration watchdog | P2 | narrow (1) | 1.0 | 2.0 | — |
| G9 | Learned fusion weights | P3 | narrow (1) | 1.0 | 1.0 | — |
| G10 | Trajectory-diff UI | P3 | narrow (1) | 1.0 | 1.0 | — |
| G11 | Curation adapter expansion | P3 | medium (2) | 1.0 | 2.0 | — |

---

## 6. Suggested wave structure (hand-off to plan)

- **Wave A — foundations (P1 that unblock everything else)**: G1 golden scaffold → G2 rubric registry → G12 v5 normative SSOT (tiny, docs-only; lands with A).
- **Wave B — evaluator depth (P1 metric + divergence)**: G3 trajectory metrics → G4 replay-divergence scorer.
- **Wave C — promotion discipline (P1/P2 write-path)**: G7 eval-freshness gate → G8 calibration watchdog.
- **Wave D — learning loop (P2)**: G5 constitutional preference producer → G6 trajectory-exemplar store.
- **Wave E — polish (P3)**: G9 fusion weights → G10 diff UI → G11 curation depth.

Rationale: A is infrastructural; B adds signal sharpness; C closes the write door; D lights the learning flywheel; E polishes.

Alternate orderings considered and rejected:
- Starting with D (RLAIF loop) is attractive but fires on a weak golden (G1) → false signals.
- Starting with C (promote gate) first would block ongoing work before B gives it sharpness.

---

## 7. Source references

- v4 SSOT: `docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v4.md`
- OpenAI Evals: https://github.com/openai/evals ; Evaluation best practices: platform.openai.com/docs/guides/evaluation-best-practices
- Anthropic CAI/RLAIF: https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback ; arXiv:2212.08073
- Google methodical agent eval: https://cloud.google.com/blog/topics/developers-practitioners/a-methodical-approach-to-agent-evaluation
- Sakura deterministic replay: https://www.sakurasky.com/blog/missing-primitives-for-trustworthy-ai-part-8/
- Record & Replay for LLM agents: https://arxiv.org/abs/2505.17716
- Local rules referenced: `.windsurf/rules/evaluation-promotion-gate.md`, `.windsurf/rules/judge-calibration-cadence.md`

---

## 8. Next step

Hand off to plan file: `.windsurf/plans/system-learning-waves-7b3c91.md` with wave queue, token budgets, and per-wave success criteria. Author-Gate required on wave sequencing because (a) Wave A vs. Wave D first is a genuine architectural tradeoff and (b) Wave C could be pulled forward if compliance pressure exists.
