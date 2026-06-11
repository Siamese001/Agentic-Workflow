---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\shadow-learning-bestpractice-gap-7b3e4c.md'
original_relative_path: '_archive\\2026-05\\shadow-learning-bestpractice-gap-7b3e4c.md'
source_sha256: fa989318b3fe93fc259ea5f6e816b411c24d2f32fe87e0e4cabf5435bbba22ab
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Shadow Learning & Meta-Learning Bus — Best-Practice Gap Plan

Status: Draft (no code changes yet)
Owner: Cursor Agent
Scope: §6 (L6 Shadow Evaluation → Future-Run Learning) of `docs/reference/_notes/agentic_process_mapping_v34.md`
ADG snapshot: most-recent `artifacts/adg/adg_indexed_*.sqlite`
Created: 2026-04-23

---

## 1. What v33 §6 Claims (SSOT to compare against)

Source lines: `docs/reference/_notes/agentic_process_mapping_v34.md:449-474`.

- **Four-stage pipeline** 6A INGEST → 6B EVALUATE → 6C RCA/SYNTH → 6D PROMOTE/UPDATE.
- **Invariants**:
  - *Eval must precede learning* (firewalled).
  - *No live patron impact*, future-run only.
  - *Floor staff propose only*; UWG is sole ink path.
  - *Observer posture* only during ingest (evidence reads, no mutation).
- **Bus U** pushes approved prompts, policies, baselines, rubrics, reason priors to next-run surfaces.
- **Human calibration** tunes grading, not runtime.

---

## 2. External Best Practices Reviewed (web-cited)

### Anthropic — *Demystifying evals for AI agents* (`anthropic.com/engineering/demystifying-evals-for-ai-agents`)
- **Three grader families**: code-based, model-based (LLM-as-judge), human. Combine; weight or gate per task.
- **Capability vs. regression evals** — capability suites start at low pass-rate (hill-climb); regression suites near 100%; capability graduates to regression once saturated.
- **Harness isolation** — every trial from clean env; no cross-trial state; beware infra flakiness masquerading as agent perf.
- **Grade the outcome, not the path** — rigid tool-sequence grading is brittle.
- **Partial credit** for multi-component tasks.
- **Per-dimension isolated LLM judges**; give LLM a way out (`Unknown`); calibrate against humans periodically.
- **Saturation watch** — reads transcripts regularly; revise eval when scores stop moving.
- **Eval-driven development** — write capability evals before features are built.
- **Open contribution** — domain experts author eval tasks; dedicated infra team owns harness.

### OpenAI — *Evaluate agent workflows* + *Trace grading* (`developers.openai.com/api/docs/guides/agent-evals`, `.../trace-grading`)
- **Trace-first** when debugging — inspect full end-to-end trace (model calls, tool calls, guardrails, handoffs).
- **Graders on traces**: structured criteria → scale → regression detection.
- **Graduate** from one-off trace grading to **repeatable datasets + eval runs** once "good" is defined.
- **Prompt optimizer** consumes dataset outcomes to auto-improve prompts → continuous-improvement flywheel.
- **Related surfaces** — batch evals vs external-model evals vs online feedback; pick per lifecycle stage.

### Google Cloud — *Methodical approach to agent evaluation* (`cloud.google.com/blog/.../a-methodical-approach-to-agent-evaluation`)
- **Purpose-driven pillars**: (1) final output quality, (2) trajectory / internal reasoning, (3) UX/safety, (4) tool-use ethics/cost.
- **Four method layers**: human (ground truth), LLM-as-judge (scaled approximation), programmatic/code-based (deterministic), **adversarial testing** (safety/robustness).
- **Data generation**: dueling-LLM synthesis, anonymized production traffic, human-in-the-loop curation.
- **Operationalize**: eval-in-CI as a quality gate; fail builds on threshold regression.
- **Production monitoring**: operational (latency/tokens), engagement (👍/👎), drift detection.
- **Virtuous feedback loop**: production failures → curated → added to golden → re-evaluated.

---

## 3. Current Repo State (inventory)

Modules already implemented (`system_learning/`):

| Area | Modules | State |
|---|---|---|
| Bus orchestrator | `engines/meta_learning_bus.py`, `meta_learning/meta_learning_bus.py`, `scripts/meta_learning_bridge.py`, `scripts/meta_learning_operator.py` | ADG-wired; content-addressed; fail-open. |
| Pipeline | `pipelines/meta_learning_pipeline.py` (1425 lines), `pipelines/pipeline_factory.py` | Proposal-only default; staged commit/activate via injected interfaces. |
| Trajectory eval (Component C) | `engines/trajectory_evaluation_engine.py` | 5 metrics (tool sel / args / retries / budget / policy). |
| Shadow posture | `engines/shadow_drift_analyzer.py`, `validators/shadow_replay_validator.py`, `validators/shadow_evaluator.py` | Drift signals informational-only; replay-based pre-activation regression guard. |
| Approval & gating | `engines/approval_gauntlet_engine.py`, `engines/retrieval_profile_activation_gate.py`, `engines/stage_barrier_enforcer.py`, `invariants/freeze_gate.py` | COMMANDANT sovereign approval + regression + safety gates. |
| State / write path | `engines/l4_state_writer.py` | Content-hash, idempotent; file/in-mem/no-op impls. |
| Rubrics & judges | `config/judges/rubrics.yaml`, `config/judges/budget.yaml` | 4 RAG dimensions + reference + pairwise + consensus; `eval_taxonomy: capability / regression`. |
| Golden dataset scaffold | `data/eval/golden/` (rag only), `data/eval/golden/README.md` | Schema + acceptance rules defined; ≥100 items/rubric target; κ ≥ 0.6. |
| Adapters into live run | `adapters/l1_meta_adapter.py`, `adapters/live_run_pipeline_adapter.py`, `adapters/system_learning_memory_bridge.py`, `runtime_hitl_consumer.py` | Bridge for inbound traces and outbound bus-U surfaces. |
| Runtime ADG ingest | `runtime_adg/l6_integration.py` + `otel_mcp` | Ingest telemetry → runtime ADG store. |

What is **present and matches v33**:
- 6A ingest (trace feature extractor + ADG bridge).
- 6B eval (trajectory engine + rubric bank + consensus judge + reference/pairwise).
- 6C synth (RCA cluster engine + rule_drafting).
- 6D promote (approval gauntlet + shadow replay validator + stage barrier + UWG route).
- Bus U surfaces: retrieval profiles, policy recommendations, rule proposals.
- "Observer posture" during ingest — meta_learning_bus invariants state additive-only, no mutation.

---

## 4. Gap Register (best practice → repo state)

Gaps are graded **P1 blocker / P2 important / P3 polish** for this workstream only (independent of the global P-band scorer).

### GAP-1 (P1) — Golden dataset coverage is partial
- **Best-practice**: Anthropic & Google require anchored golden sets per rubric; ≥100 items with ≥2 raters and κ ≥ 0.6 (repo's own README codifies this).
- **Evidence**: `data/eval/golden/` contains only `rag/` subtree; README declares `gov/` and `sec/` rubrics but dirs are missing. `system_learning/golden/` is an empty package.
- **Risk**: governance and security judges run uncalibrated → unreliable promotion decisions.

### GAP-2 (P1) — No capability-vs-regression CI quality-gate workflow
- **Best-practice**: OpenAI & Google — eval harness runs on every change; build fails on threshold regression.
- **Evidence**: `.github/workflows/` has 8 workflows (ADG, author-gate, config-sync, guardian, HITL, infra wiring, pytest SSOT, subprocess timeout). **No `eval-harness.yml`** that exercises `eval_taxonomy.capability` + `eval_taxonomy.regression` from `rubrics.yaml`.
- **Risk**: capability/regression taxonomy is declarative only; no enforcement surface.

### GAP-3 (P2) — Transcript-reading / saturation-watch loop is not codified
- **Best-practice**: Anthropic step 6–7 — regularly read transcripts; revise graders; monitor for saturation.
- **Evidence**: `data/judge_calibration/README.md` exists but no periodic procedure (workflow, cron, or operator script) enforces transcript sampling & regrade. No saturation-detection rule in rubrics.yaml.
- **Risk**: judges silently drift or saturate; rubric revisions become ad-hoc.

### GAP-4 (P2) — Adversarial testing layer is absent
- **Best-practice**: Google pillar 4 — adversarial/robustness suite against unexpected / malicious inputs.
- **Evidence**: `guardian-tests.yml` covers internal guardian enforcement; no explicit red-team / adversarial dataset under `data/eval/` nor an engine that mutates golden items into adversarial variants.
- **Risk**: safety assertions graded only on benign traffic.

### GAP-5 (P2) — No production-traffic virtuous loop ("curate-from-prod → golden")
- **Best-practice**: Google — anonymize production failures → add to golden → re-evaluate.
- **Evidence**: `runtime_adg/l6_integration.py` ingests telemetry into runtime ADG; no curation pipeline that emits candidate golden-dataset entries from ingested runs (with anonymization + human annotation queue).
- **Risk**: golden set becomes stale; drift detection cannot feed new eval tasks.

### GAP-6 (P2) — Dueling-LLM / synthetic dataset expansion
- **Best-practice**: Google — dueling LLMs to synthesize multi-turn conversational eval data.
- **Evidence**: no `tools/eval/synth_*` or pipeline that generates adversarial/edge conversations at scale.
- **Risk**: golden dataset growth rate is bottlenecked on human authorship.

### GAP-7 (P2) — Trace-grading UI / inspection surface
- **Best-practice**: OpenAI — trace browser first, dataset second; Anthropic — tooling to read transcripts regularly.
- **Evidence**: traces captured via OTel + runtime ADG, but no operator surface that lists traces by rubric score & lets a human sample/regrade. `otel_mcp` exposes `otel_trace` / `otel_healing_chain`, not a trace-grading review view.
- **Risk**: operators cannot cheaply verify grader fairness (Anthropic's explicit step 6).

### GAP-8 (P2) — "Bus U" rollout surfaces partial
- **Best-practice** (v33 §6D): bus U publishes Prompts, Policies, Baselines, Rubrics, Approved Reason Priors.
- **Evidence**: retrieval profiles, policy recommendations, rule proposals are wired; **no explicit rubric-update channel** (rubrics.yaml is edited manually) and **no reason-prior publication channel** surfaced in `adapters/`.
- **Risk**: rubric evolution and reason-prior delivery are out-of-band → weakens the closed loop.

### GAP-9 (P3) — Partial-credit / graded-trajectory scoring not exposed in rubrics bank
- **Best-practice**: Anthropic — partial credit on multi-component tasks; grade output not path.
- **Evidence**: `trajectory_evaluation_engine.py` scores 5 dimensions but `rubrics.yaml` exposes only single-scalar pass/warn thresholds; no partial-credit weighted composite documented.
- **Risk**: single-threshold gating blocks valid partial successes.

### GAP-10 (P3) — Determinism / isolation contract for eval harness trials
- **Best-practice**: Anthropic — clean-env trial isolation; avoid shared state.
- **Evidence**: `meta_learning_bus.py` is additive and content-addressed, but there is no documented "eval trial sandbox" invariant for capability/regression runs — e.g., no contract that `tests/eval/` fixtures start from a wiped artifacts dir.
- **Risk**: cross-trial state can inflate or deflate scores undetectably.

### GAP-11 (P3) — Capability-eval saturation telemetry
- **Best-practice**: Anthropic step 7 — monitor saturation; promote capability → regression when scores plateau.
- **Evidence**: `eval_taxonomy.capability` exists in rubrics.yaml with targets; no telemetry or script detects saturation and proposes promotion.
- **Risk**: graduation from capability to regression remains manual.

### GAP-12 (P3) — Prompt-optimizer integration (OpenAI surface) not wired
- **Best-practice**: OpenAI — prompt optimizer reads dataset outcomes to auto-tune prompts.
- **Evidence**: `engines/rule_drafting_engine.py` drafts rules but there is no prompt-specific optimizer fed by approved outcomes.
- **Risk**: prompts drift without automated proposal candidates; all tuning is rule-based.

---

## 5. Plan (no code yet — waves + phases)

ADG snapshot for validation work: latest `artifacts/adg/adg_indexed_*.sqlite` at execution time.

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1 — Close P1 Gaps** | W1.1, W1.2 | Golden-set coverage; CI quality gate | 18000 | rubrics.yaml is SSOT; workflow layout per `.github/workflows/`. | Todo | Gov+sec goldens ≥100 items each; `eval-harness.yml` blocks merges on capability-or-regression threshold breach. |
| **W2 — Close P2 Gaps (observer + curate)** | W2.1–W2.5 | Transcript sampling; adversarial layer; prod→golden curation; dueling-LLM synth; trace-grade review surface | 40000 | OTel + runtime ADG stable; no PII in prod traces (anonymizer required). | Todo | Weekly transcript sample + regrade automation exists; adversarial suite runs in W1 workflow; curation pipeline emits ≥N candidate items/week; synth generator produces reproducible dialog sets; trace-grade view surfaced via `otel_mcp` or a new `eval_mcp`. |
| **W3 — Close P2 Bus-U gap** | W3.1 | Rubric + reason-prior publication channel | 10000 | No breaking change to retrieval/profile flow. | Todo | Approved rubric updates flow via UWG like retrieval profiles; reason-prior bus hop documented in `agentic_process_mapping_v33.md` §6D. |
| **W4 — Close P3 Polish** | W4.1–W4.4 | Partial credit scoring; trial isolation contract; saturation telemetry; prompt-optimizer prototype | 22000 | W1+W2 landed. | Todo | Composite rubric scoring + weighted partial credit in rubrics.yaml; isolation invariant codified in `tests/eval/conftest.py`; saturation detector script emits promotion proposals to gauntlet; prompt optimizer prototype produces ≥1 accepted proposal. |
| **W5 — Doc + v33 Update** | W5.1 | Reflect closed gaps in §6 | 4000 | — | Todo | v33 §6 updated to cite capability/regression suites, transcript-sampling cadence, adversarial layer, curation loop, rubric + reason-prior bus-U channels. |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Golden set expansion — gov + sec | `data/eval/golden/gov/**`, `data/eval/golden/sec/**`, `config/judges/rubrics.yaml` additions | Human annotation throughput; κ≥0.6 gate | 10000 | Todo |
| W1.2 | Eval harness CI workflow | `.github/workflows/eval-harness.yml` (new), `tools/eval/run_capability_regression.py` (new), reuse of `ops_scripts/ci/check_judge_calibration.py` | Runtime cost in CI; caching | 8000 | Todo |
| W2.1 | Transcript sampling + regrade | `tools/eval/transcript_sampler.py` (new); cron / scheduled workflow | PII risk; sampling strategy | 8000 | Todo |
| W2.2 | Adversarial suite | `data/eval/adversarial/**`, `tools/eval/adversarial_generator.py` | Safety scope | 8000 | Todo |
| W2.3 | Prod→golden curation loop | `system_learning/adapters/golden_curation_adapter.py` (new), anonymizer | Anonymization quality | 8000 | Todo |
| W2.4 | Dueling-LLM synth | `tools/eval/dueling_llm_synth.py` (new) | Judge bias | 8000 | Todo |
| W2.5 | Trace-grade review surface | extend `tools/otel/otel_mcp_server.py` or new `tools/mcp/eval_mcp_server.py` | MCP serialization rule | 8000 | Todo |
| W3.1 | Bus-U rubric + reason-prior channel | `system_learning/adapters/rubric_publication_adapter.py` (new), `system_learning/adapters/reason_prior_adapter.py` (new) | UWG contract | 10000 | Todo |
| W4.1 | Partial-credit composite scoring | `config/judges/rubrics.yaml`, `agentic_core/evaluation/judges/consensus.py` | Weighting calibration | 6000 | Todo |
| W4.2 | Eval trial isolation contract | `tests/eval/conftest.py`, `docs/architecture/adr/ADR-NNN-eval-trial-isolation.md` | Cross-test fixture state | 6000 | Todo |
| W4.3 | Saturation detector | `tools/eval/saturation_detector.py` (new) + gauntlet hop | Signal volatility | 6000 | Todo |
| W4.4 | Prompt-optimizer prototype | `system_learning/engines/prompt_optimizer_engine.py` (new) | Safety of auto-proposals | 4000 | Todo |
| W5.1 | v33 §6 refresh | `docs/reference/_notes/agentic_process_mapping_v34.md` | Keep diagram intact | 4000 | Todo |

### Gap Register (cross-ref to §4)
- W1.1 closes **GAP-1**.
- W1.2 closes **GAP-2**; partial for **GAP-9, GAP-11**.
- W2.1 closes **GAP-3**.
- W2.2 closes **GAP-4**.
- W2.3 closes **GAP-5**.
- W2.4 closes **GAP-6**.
- W2.5 closes **GAP-7**.
- W3.1 closes **GAP-8**.
- W4.1 closes **GAP-9**.
- W4.2 closes **GAP-10**.
- W4.3 closes **GAP-11**.
- W4.4 closes **GAP-12**.
- W5.1 reflects all closures in v33 SSOT.

### Invariants preserved across all waves
1. Observer posture at 6A — no new mutation edges introduced.
2. UWG sole ink path — every new promotion channel routes via UWG.
3. Proposal-only defaults for pipeline (`proposal_only=True`).
4. Determinism digests + replay keys emitted for every new engine.
5. No PowerShell; all subprocess calls with `timeout=`.
6. No test skipping; any new tests are additive.

### Out of scope
- Runtime HITL (ADR-023 governs that — distinct from Author-Gate per AGENTS.md).
- Changing the four-stage semantics of §6.
- Introducing a graph-DB; ADG remains SQLite + overlay.

---

## 6. Evidence & Web Citations
- Anthropic — *Demystifying evals for AI agents*: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- OpenAI — *Evaluate agent workflows*: https://developers.openai.com/api/docs/guides/agent-evals
- OpenAI — *Trace grading*: https://developers.openai.com/api/docs/guides/trace-grading
- Google Cloud — *Methodical approach to agent evaluation*: https://cloud.google.com/blog/topics/developers-practitioners/a-methodical-approach-to-agent-evaluation
- Anthropic — *Bloom (auto behavioral evals)*: https://alignment.anthropic.com/2025/bloom-auto-evals/

Token estimator: **UNRESOLVED** — estimator not executed for this draft (question/plan task). Per constitutional §plan-location: UNRESOLVED is acceptable for T0/T1; this plan is T2 scoped, so token estimate is a **warning, not blocker**. Rerun `tools/utils/planning/token_estimator.py` before execution start.

---

## 7. Next Action

Await approval. On approval, execute W1.1 first (golden-set gov + sec) since every downstream wave depends on calibrated judges.

---

## 8. Wave F4 — Deferred-scope follow-up (added 2026-04-23)

Closes the two DEFERRED_SCOPE markers emitted during W5 and F3 summaries.
Token estimator: UNRESOLVED (T2 warning).

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **F4 — deferred closures** | F4.1, F4.2 | Annotation tooling + artifact signing | 16000 | Phases 1–3 landed; rubrics.yaml, runner, dueling_llm_synth in place. | Todo | F4.1: CLI accepts per-item rater labels, computes inter-rater κ, promotes pending→scored when κ≥0.6; F4.2: sovereign_default signs CompiledPromptArtifact so `verify_signatures=True` path works in real mode. |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| F4.1 | Human-annotation CLI + κ promotion gate | `tools/eval/annotate_golden.py` (new), `tools/eval/kappa_promotion_gate.py` (new), `tests/eval/test_kappa_promotion.py` (new) | Handling partial rater sets; Cohen's κ math for ordinal 1-5 scale; gold_score tie-break | 10000 | Todo |
| F4.2 | Sign CompiledPromptArtifact in sovereign_default | `tools/eval/_gateway_factories.py` (modify), `tests/eval/test_gateway_factories.py` (new) | HMAC payload contract matches `_compute_signature`; unsigned-vs-signed path kept clear | 6000 | Todo |

### Gap-back-reference

- F4.1 closes deferred item from §1-GAP closure of W1.1 — activates the κ≥0.6 gate defined in `data/eval/golden/README.md`.
- F4.2 closes deferred item from F3 — lets `sovereign_default` run against a gateway built with `verify_signatures=True` (hardening default in production).

### Invariants preserved
- κ promotion gate is additive — it never downgrades an already-scored item.
- Signing happens inside the factory; the synthesizer and runner stay gateway-agnostic.
- Mock-mode CI remains hermetic; signing requires the real gateway and its HMAC secret.
- No constitutional exceptions; subprocess discipline unchanged.
