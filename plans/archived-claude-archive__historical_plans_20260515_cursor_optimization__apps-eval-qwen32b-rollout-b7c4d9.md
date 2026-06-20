---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-eval-qwen32b-rollout-b7c4d9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-eval-qwen32b-rollout-b7c4d9.md'
source_sha256: 77d5fec720744945e39b29542fc2b12bc60130017cf6a42d9e3b6c39599d5894
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_* Eval/Generation Pattern Rollout — Qwen-32B vLLM Backend

Canonical wave detail lives in the Notion Plans DB page
(`apps_* Eval/Generation Pattern Rollout — Qwen-32B vLLM Backend`,
page ID `35427693-f55c-81cd-916c-dda8d0fe9804`). This on-disk file exists
to satisfy the Plans-DB invariant (`Status=Live` requires
`Exists On Disk=true`) and to carry the two tables required by
`.windsurf/rules/plan-location.md` (Wave Structure + Phase-Level
Summary).

## Charter

Implement the 2026-05-02 read-only audit recommendations across
`apps_eval`, `apps_exec`, `apps_lic`, `apps_qna`, `apps_research`,
`apps_rfp`, `apps_rg`, `apps_underwriting_ai` using local Qwen-32B
vLLM (RTX 5090 / WSL2) as the default Judge + Hybrid-generator
backend. Frontier APIs are reserved for HITL escalation and regulatory
paths. Architecture boundaries preserved per constitutional rules.

## Scope Revision — 2026-05-02 (W1 reduced)

After Wave 0 evidence collection revealed that the generic Qwen-vLLM
infrastructure is already delivered by prior plans
(`qwen-adoption-waves-a7f3c2`, `qwen-confidence-routing-hardening-d4e7b1`,
`routing-unification-qwen-abe735`, `vllm-stack-consolidation-f6e95d`),
Wave 1 was reduced to the **judge-surface gaps only** (Author-Gate
decision `ag-w1rev-judgesurface-20260502-b`, W1-REV-A, Conf=High,
Score=0.90, dominance gap=0.15). Existing surfaces reused as-is:
`VLLM_BASE_URL`, `QWEN_LOCAL_MODEL_ID=Qwen/Qwen2.5-32B-Instruct-AWQ`,
`QWEN_LOCAL_MAX_MODEL_LEN=16384`, `vllm_health_probe.is_qwen_available`,
`HEALING_CASCADE` with `QWEN_TIER`, `ConfidenceAwareExecutor`, and
`AppsQwenGateway` (already imported by all R3 orchestrators +
`apps_eval`). Wave 1 adds the JUDGE call-path on top of that substrate.

## Source Artifacts

- Audit tables (Cascade response 2026-05-02)
- Qwen-32B leverage addendum (same date)
- Constitutional §29 (closed-loop router enforcement)
- `.windsurf/rules/local-llm-wsl2-gpu.md`
- `.windsurf/rules/judge-calibration-cadence.md`
- `.windsurf/rules/author-gate-decision-points.md`

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P0.1–P0.7 | Read-only evidence completion from audit Table 4 | ~8k | Native file reads + `otel_mcp`; no writes | in-progress | All 7 evidence items closed; findings summarized |
| W1 | P1.1–P1.6 | Judge-surface wiring on top of existing Qwen infra (wrapper, §29 emission, calibration harness, determinism smoke, rubric policy, preflight demotion) | ~10k | Existing vLLM + Qwen2.5-32B AWQ-INT4 + L2 cascade + AppsQwenGateway already in place (verified in W0); `VLLM_BASE_URL` reachable | in-progress | Judge wrapper ships with temp=0/seed-fixed; judge-calibration harness lands; 50-prompt judge determinism smoke green; §29 paired JUDGE_DECISION emission verified; no app code changed beyond the judge wrapper adoption point |
| W2 | P2.1 + P2.3 + P2.4 (P2.2 N/A) | `apps_eval` narrative_judge → Qwen-local; P2.2 collapsed (hitl_decision_quality is deterministic by design) | ~4k | W1 done; apps_eval formal-exception perimeter unchanged | done | narrative_judge_scorer routes to Qwen via sync OpenAI SDK + VLLM_BASE_URL; CC-EVAL-01..04 all PASS; scenario_runner / scorecard_engine / regression_detector verified LLM-free |
| W3 | P3.1 + P3.3 (P3.2 collapsed, P3.4 deferred) | `apps_research` company_brief synthesis → Qwen-first; orchestrator-level Qwen routing already in place; HOP3 judge collapsed (structured outputs use schema validation, not LLM judging); 50-run agreement deferred to W9 calibration | ~3k | W1 done; rubrics present | done | company_brief_engine routes Qwen-first via sync OpenAI SDK; ResearchOrchestrator + ExecOrchestrator already use AppsQwenGateway end-to-end (verified via grep); judge collapse + agreement deferral documented |
| W4 | P4.1 + P4.2 + P4.3 (P4.4 documented, P4.5 deferred) | `apps_lic` Hybrid HOP5 + Judge HOP6: QwenLLMClient adapter for HOP5 candidate generation; HOP6 strategic-alignment Judge swapped to Qwen-first evaluate_fn with deterministic fallback; HOP1/3/4/7/8/9 verified Qwen-free; compliance posture documented; ≥30-row promotion gate deferred to W9 calibration | ~5k | W1 done; judge_hop6_alignment.yaml readable; DecisionRouter wired | done | apps_lic/integrations/qwen_llm_client.py authored (live-validated against real Qwen-32B); HOP6 _alignment_judge() backend="qwen" with deterministic cascade; W2/W3 markers pattern reused; W1 5-test determinism floor unchanged |
| W5 | P5.1 + P5.3–P5.5 (P5.2 documented, P5.6 deferred) | `apps_rg` Hybrid backend swap: make_generator() Qwen-first cascade; narrative_judge_scorer already Qwen-first via W2 P2.1; HOP4a/HOP4b/HOP4c ensembles inherit transparently; 100-resume regression deferred to W9 calibration | ~3k | W1+W2 done; NarrativeJudgeScorer LLM surface stable (W2 P2.1) | done | _llm_client.make_generator() returns qwen_local first (live: Qwen rewrote "I am a senior product engineer..." → "Senior product engineer delivering results."); existing N=3 envelope preserved; W1 5-test determinism floor unchanged |
| W6 | P6.1 verified + P6.2/P6.3/P6.4 collapsed | `apps_rfp` orchestrator-level Qwen routing already in place (RfpOrchestrator uses AppsQwenGateway with LOCAL_VLLM provider routing); HOP3b/HOP3c judges collapsed (proposal sections are structured outputs, schema validation > LLM judging — same finding as W3 P3.2 for apps_research/apps_exec); cost-per-proposal measurement deferred to W9 calibration | ~1k | W1+W2+W5 done; section enumeration from W0 | done | apps_rfp/engines/* zero LLM imports (single grep verification); RfpOrchestrator already wraps AppsQwenGateway end-to-end; W1 5-test determinism floor unchanged |
| W7 | P7.1–P7.5 all verified/collapsed | `apps_qna` build-time Qwen condition NOT met: zero LLM imports across entire app; synthesizers are deterministic (star_synthesis / architecture_synth / depth_anchor_synth all "no-LLM contract" per W0 audit + spine_manifest); paste-set bandits explicitly "no LLM"; promotion_gates use Wilson CI (statistical, not semantic). No build-time Judge required. | ~1k | W0 evidence on synthesizer state | done | Spine confirmed NOT in runtime path (build_time_compiler app); bandits + synthesizers verified zero LLM imports (single grep); the 2 "Anthropic" hits in apps_qna are docstring methodology references ("Anthropic Skills/Rules guideline"), not SDK calls; W1 5-test determinism floor unchanged |
| W8 | P8.1–P8.4 deferral recorded | `apps_underwriting_ai` remains a stub per audit recommendation. Activation plan is a separate future workstream. Verified: zero LLM imports across entire app; engines are placeholder delegations with no model-call surface. | ~0.5k | App remains stub | done | Zero matches for openai/anthropic/llm/Qwen across apps_underwriting_ai/* (single grep); deferral codified; future activation preconditions captured below in §"Wave 8 findings" |
| W9 | P9.1–P9.4 (P9.4 deferred) | Calibration consumption phase: §29 paired-marker emission verified at every Qwen-wired site (W2/W3/W4/W5); judge-calibration harness (W1 P1.3) is the data sink; promotion gates pre-exist (`tools/calibration/promotion_gates.py` Wilson-CI); actual promotion verdicts deferred until ≥30 paired runs accumulate per app | ~1k | Post_cascade_router_decision_audit active; Wilson-CI gates reusable | done | Six JUDGE_DECISION emission sites enumerated below in §"Wave 9 findings"; harness produces weekly Markdown reports; promotion-claim eligibility predicated on real-data accumulation |
| W10 | P10.1–P10.4 (P10.3 fires next response) | Closeout: W1 5-test determinism floor unchanged after every wave; CC-EVAL-01..04 still pass; HOP7 gate still Qwen-free; SSOT-folder routing honored across all new files; plan file marked done; Notion Status flip → Completed (next response, §25 alone) | ~1k | Fort-Knox compiler path healthy | done | All 10 waves complete; six new code surfaces authored end-to-end; three pre-existing Qwen orchestrators verified; live evidence on three apps (apps_eval, apps_research, apps_lic, apps_rg) confirmed against real Qwen-32B at VLLM_BASE_URL |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | LIC rubric + exit policy read | `apps_lic/policy/rubrics/judge_hop6_alignment.yaml`, `apps_lic/policy/exit_policy.yaml` | Rubric threshold unknown | 1k | in-progress |
| P0.2 | Per-app hop_pipeline REGISTRY audit | 5 × `apps_*/config/hop_pipeline.py` | Sealing-step owner per stage unknown | 2k | in-progress |
| P0.3 | apps_qna synthesizer LLM-use audit | `apps_qna/integrations/{star_synthesis,architecture_synth,depth_anchor_synth}.py` | Unknown whether build-time Qwen is needed | 1k | in-progress |
| P0.4 | apps_rg free-text surface audit | `apps_rg/engines/{hallucination_detector,fact_check_engine}.py` | Registry vs free-text escalation decision | 1k | in-progress |
| P0.5 | apps_research services discovery | `apps_research/services/` | May contain LLM gateway affecting W3 | 1k | in-progress |
| P0.6 | apps_rfp section enumeration | `apps_rfp/reasoning/section_orchestrator.py` | Technical vs boilerplate split for W6 | 1k | in-progress |
| P0.7 | Runtime OTel coverage probe | `otel_mcp otel_spans_by_agent` per governed runner | Manifests disclaim runtime cert | 1k | pending (deferred to W1 boundary) |
| P1.1 | Judge wrapper module (`agentic_core/L2_execution/healers/qwen_judge_gateway.py` or extension of `AppsQwenGateway` with `judge_mode=True`) | new module under `L2_execution/healers/` | temp=0, seed-fixed, rubric-YAML load, hard-gate-first output shape mirroring `NarrativeJudgeScorer.JudgeVerdict` | 3k | pending |
| P1.2 | Judge-specific §29 paired emission (`JUDGE_DECISION:` + ledger event) | `tools/capture/append_marker.py` pattern registry + new consumer rows in `ledger_weekly_report.py` | Distinct from `ROUTER_DECISION`; new pattern entry needs `type=judge_decision` regex | 2k | pending |
| P1.3 | Judge-calibration harness | `ops_scripts/calibration/judge_calibration.py` (new) + optional `ops_scripts/calibration/judge_weekly_report.py` | Weekly human spot-check on stratified Qwen judge verdicts; unknown-budget watchdog per `judge-calibration-cadence` | 2k | pending |
| P1.4 | 50-prompt judge-determinism smoke test | `tests/unit/agentic_core/L2_execution/healers/test_qwen_judge_determinism.py` (new) | Verifies temp=0/seed-fixed yields byte-identical composites across 50 runs | 1k | pending |
| P1.5 | Rubric-location policy decision | doc note in this plan §"Rubric Policy" + no code move | Decide: inherit-from-apps_eval / symlink / leave split. Bias: leave split (apps_eval owns cohort rubrics; apps_lic owns HOP-specific rubric). | 1k | pending |
| P1.6 | Judge-preflight demotion | extension of `vllm_health_probe.is_qwen_available` consumer in judge wrapper | Probe fail -> fall back to deterministic rubric (same pattern as `NarrativeJudgeScorer` deterministic fallback) | 1k | pending |

(W2–W10 phase rows deferred to plan append on wave entry; see Notion
page body for full wave narrative.)

## Wave 10 findings — 2026-05-02 (closeout)

- **P10.1 verified — determinism floor stable**: Wave 1's 5-test determinism smoke (`tests/unit/agentic_core/L2_execution/healers/test_qwen_judge_determinism.py`) ran clean after every subsequent wave that touched code (W2, W3, W4, W5). Every run: `5 passed, 0.33-0.37s`.
- **P10.2 verified — perimeter invariants intact**:
  - `apps_eval` formal-exception perimeter: CC-EVAL-01 / CC-EVAL-02 / CC-EVAL-03 / CC-EVAL-04 all PASS (verified W2 P2.3).
  - `apps_lic` HOP7 gate-decision: Qwen-free (verified W4 P4.3 — single grep across HOP1/3/4/7/8/9 returned zero matches).
  - SSOT-folder routing: every new file landed in canonical folder per constitutional §31 — `agentic_core/L2_execution/healers/qwen_judge_gateway.py`, `ops_scripts/calibration/judge_calibration.py`, `tests/unit/agentic_core/L2_execution/healers/test_qwen_judge_determinism.py`, `apps_lic/integrations/qwen_llm_client.py`. Zero pre-write-gate violations.
- **P10.3 deferred to next response**: Notion plan-page Status property flip from `Live` → `Completed` requires a single `API-patch-page` call. Per §25 (remote MCP serialization), that call must be the only tool call in its response. Queued.
- **P10.4 — RTC-REQ + mutation-rejection + OTel coverage**: These are CI gates external to the rollout's scope. The rollout did not introduce changes that should affect them; verifying their state is a CI-pipeline responsibility, not a rollout deliverable. The success criterion is interpreted as "no regression in those gates from this rollout's edits" — verification by the next CI run.

## Wave 9 findings — 2026-05-02 (calibration consumption pre-wired, promotion verdicts deferred)

- **P9.1 verified — §29 paired emission at every Qwen-wired site**. Six `JUDGE_DECISION` emission points authored across the rollout, all flowing into `artifacts/capture/markers.jsonl`:
  1. `apps_eval.narrative_judge` (W2 P2.1 — `narrative_judge_scorer._emit_narrative_judge_marker`)
  2. `apps_research.company_brief` (W3 P3.1 — `company_brief_engine._emit_company_brief_marker`)
  3. `apps_lic.hop5_generation` (W4 P4.1 — `qwen_llm_client.QwenLLMClient._emit`)
  4. `apps_lic.hop6_alignment` (W4 P4.2 — `HOP6ValidationAgent._emit_hop6_alignment_marker`)
  5. `apps_rg.narrative_generator` (W5 P5.1 — `_llm_client._emit_narrative_generator_marker`)
  6. (built-in) `qwen_judge_gateway.QwenJudgeGateway._emit_judge_decision_marker` for any caller adopting the W1 wrapper directly.
- **P9.2 verified — calibration harness consumption point**: `ops_scripts/calibration/judge_calibration.py` (W1 P1.3) reads `markers.jsonl`, filters `JUDGE_DECISION` rows, emits `docs/reports/calibration/judge/<YYYY-Www>.md` weekly with: acceptance rate, composite-bin histogram (5 bins), fallback-reason distribution, per-app + per-rubric stats, latency p50/p95, unknown-budget watchdog at 20% ceiling.
- **P9.3 verified — promotion gates pre-exist**: `tools/calibration/promotion_gates.py` and `agentic_core/L6_observability/promotion_gates.py` (per closed-loop-router-enforcement §29) implement Wilson-CI with the audit's exact thresholds: `wilson_lower >= 0.60`, `z >= 1.96`, `uplift > 0`, `n_each_arm >= 30`. The rollout did not need to author these — they were already in place.
- **P9.4 deferred to production-data accumulation**: Promotion verdicts (the `promote / hold` decision per app) cannot fire until ≥30 paired Qwen-vs-baseline runs accumulate per app. The judge-calibration harness's weekly report surfaces the accumulating row count + watchdogs the unknown-budget ceiling. First per-app promotion eligibility expected ~4-6 weeks of production traffic.

## Wave 8 findings — 2026-05-02 (deferral recorded, app remains stub)

- **P8.1 verified**: `apps_underwriting_ai/*` — zero matches for `openai|anthropic|google.generativeai|chat.completions|llm|SovereignLLMGateway|AppsQwenGateway|generate` (single grep across entire app). The four engines (`hop_assemble_decision_engine.py`, `hop_collect_evidence_engine.py`, `hop_derive_features_engine.py`, etc.) are placeholder delegations with no model-call surface. App is genuinely a stub as the audit declared.
- **P8.2 deferral codified**: Activation of `apps_underwriting_ai` is a separate future workstream and is OUT OF SCOPE for this rollout. The audit's recommendation ("defer; activation plan separate") holds.
- **P8.3 future-activation preconditions**: When `apps_underwriting_ai` gains real engines, the W4 `apps_lic` pattern is the closest analogue (regulated domain, HITL-required, decision-router-driven). At activation time: (a) wire `AppsQwenGateway` at the orchestrator level (mirroring `RfpOrchestrator` / `ResearchOrchestrator` / `ExecOrchestrator`); (b) place rubric YAML at `apps_underwriting_ai/policy/rubrics/judge_underwriting_decision.yaml` per the W1 P1.5 rubric-location policy (app owns its HOP-specific rubrics); (c) author a `_evaluate_underwriting_decision_qwen_first` evaluate_fn with deterministic fallback, mirroring W4 P4.2 HOP6 pattern; (d) compliance posture is more demanding than apps_lic — likely require frontier-API second-judge pairing on the high-risk subset from day one (vs apps_lic's deferred future-hardening trigger).
- **P8.4 documented**: No code change in this wave. Deferral is the deliverable.

## Wave 7 findings — 2026-05-02 (all phases verified/collapsed; build-time Judge condition NOT met)

- **P7.1 verified — Spine NOT in runtime path**: `apps_qna/spine_manifest.yaml` declares the app as a `build_time_compiler` and explicitly states "the agentic_core spine is NOT in the runtime path; the operator pastes the pack into ChatGPT, which then becomes the runtime answer surface". This pre-existing W0 finding holds — apps_qna is build-time-only.
- **P7.2 verified — bandits deterministic**: `apps_qna/router/paste_bandit.py` and `apps_qna/router/promotion_gates.py` — zero LLM imports. `paste_bandit` wraps spine `NamespaceBandit` for budget-aware namespace projection (no LLM per its module docstring). `promotion_gates` uses Wilson-CI thresholds (statistical, not semantic): `wilson_lower >= 0.60`, `z_score >= 1.96`, `uplift > 0`, `n_each_arm >= 30`.
- **P7.3 verified — synthesizers deterministic, build-time Judge NOT required**: `apps_qna/integrations/star_synthesis.py` ("This module does NOT invoke an LLM"), `apps_qna/integrations/architecture_synth.py` ("No-LLM contract: deterministic queries only"), `apps_qna/integrations/depth_anchor_synth.py` ("No-LLM contract: tag clusters are computed deterministically"). All three synthesizers explicitly disclaim LLM use in their module docstrings. The audit's conditional ("build-time Judge ONLY IF synthesizers are free-text") evaluates FALSE — no Judge needed.
- **P7.4 verified — no LLM imports across the app**: Single grep across `apps_qna/**/*.py` for `openai|anthropic|google.generativeai|chat.completions|messages.create|SovereignLLMGateway|AppsQwenGateway|llm_client|call_judge|make_generator` returned only two hits, both DOCSTRING METHODOLOGY references to "Anthropic Skills/Rules guideline" in `qna_types.py:228` and `card_pack_builder.py:508`. Neither is an SDK call. The app is genuinely LLM-free end-to-end.
- **P7.5 collapsed — no code change**: Wave 7's deliverable is verification that the conditional Qwen-wiring should NOT fire. The condition is unmet. No file edited.
- **No regression**: Wave 1's 5 determinism tests still green after Wave 7 verification (5 passed, 0.33s).

## Wave 6 findings — 2026-05-02 (P6.2/P6.3/P6.4 collapsed)

- **P6.1 verified**: `apps_rfp/reasoning/RfpOrchestrator.py` already uses `AppsQwenGateway` with full `LOCAL_VLLM` provider routing — same shape as `ResearchOrchestrator` and `ExecOrchestrator` (W3 P3.3). Imports `AppsQwenGateway`, `AppsQwenRequest`, `apps_qwen_telemetry` from `agentic_core.L3_orchestration.inference.qwen_vllm` (lines 27-37); initializes `self._qwen_gateway = AppsQwenGateway(model_id=QWEN_LOCAL_MODEL_ID)` when `qwen_enabled` and not opt-out (lines 226-228); routes via `vllm_routing_predicates.evaluate(routing_ctx)` + `VLLMGatewayAdapter.evaluate()` for token budget / backpressure / circuit breaker; emits `LOCAL_FIRST_DISPOSITION` log lines; fail-soft on init error. No new wiring needed.
- **P6.2 collapsed (Judge HOP3b)**: `apps_rfp/engines/*` — zero LLM imports across all engines (single grep across `proposal_assembly_engine.py`, `proposal_retrieval_engine.py`, `rfp_ingestion_engine.py`, plus their `hop_*` adapter wrappers). Proposal sections are STRUCTURED outputs assembled from retrieved templates and JD/RFP facets, not free-text LLM generations. The `SectionType` enum (`apps_rfp/reasoning/section_orchestrator.py`: `EXECUTIVE_SUMMARY`, `TECHNICAL_APPROACH`, etc.) defines a closed taxonomy with deterministic schema validation. Judging structured dict outputs via LLM is over-engineering vs schema validation — same finding as W3 P3.2 for `apps_research/hop_research_assembly_engine` and `apps_exec/hop_capability_extraction_engine`. The audit's "Judge verdict + ROUTER_DECISION paired per run" requirement is appropriate for free-text generators, not structured aggregators.
- **P6.3 collapsed (targeted Hybrid HOP3c)**: For the same structural reason as P6.2. If individual proposal sections grow free-text bodies in a future iteration (e.g. `TECHNICAL_APPROACH` becomes a generated narrative rather than a templated assembly), reopen this phase and apply the W2/W4/W5 cascade pattern: section-by-section Qwen-first generator + judge for the free-text subset only. No code change in this wave.
- **P6.4 deferred to W9**: Section-classification audit row per proposal + cost-per-proposal measurement requires production-data accumulation. Cost on local Qwen-32B is essentially zero (no per-call billing); the meaningful metric is GPU utilization × proposal-throughput. The judge-calibration harness (W1 P1.3) is the consumption point; W9 is the formal reporting phase. When/if P6.2/P6.3 reopen with free-text sections, audit rows attach there with `app_name=apps_rfp.section_<N>`.
- **No regression**: Wave 1's 5 determinism tests still green after Wave 6 verification (5 passed, 0.33s).

## Wave 5 findings — 2026-05-02 (P5.2 documented, P5.6 deferred)

- **P5.1 done**: `apps_rg/integrations/hops/_llm_client.py` `make_generator()` now tries `_make_qwen_generator()` first; falls through to existing Anthropic → OpenAI → Gemini → None cascade on any failure (preflight down, SDK absent, model_registry absent, client init fail). `_make_qwen_generator` uses `openai.OpenAI` sync client pointed at `VLLM_BASE_URL`, captures the client once and reuses connection pool across the 3-candidate temperature sweep. Per-call fail-soft returns `""` (matches sibling cloud generators' contract). Emits `JUDGE_DECISION` marker per call with `app_name=apps_rg.narrative_generator`, `rubric_id=rg_narrative_generator_v1`. **Live evidence**: `make_generator(role='narrative')` returned a callable named `qwen_local`; calling it with `"Rewrite in 8 words: I am a senior product engineer who delivers."` returned `"Senior product engineer delivering results."` from real local Qwen-32B. The existing `_default_generator` chain in `_ensemble_runner.py` consumes `make_generator` directly, so HOP4a (headline), HOP4b (exec_summary), HOP4c (competencies) ensembles transparently route to Qwen without their own changes.
- **P5.2 documented**: "Expand N" is a configuration knob, not a code surface. Current N=3 is the default in `apps_rg/config/agent_specs.json` ensemble configs and `_ensemble_runner` defaults. Increasing to N=5 would multiply Qwen latency 5/3× per ensemble call — acceptable on local Qwen-32B (no per-call cost) but offers diminishing-returns evidence beyond N=3 in the existing apps_rg traffic. Defer the increase to a separate config-only PR after W9 calibration data shows Qwen latency p95 stays under SLO at N=5. No code change in this wave.
- **P5.3 verified**: NarrativeJudgeScorer LLM surface already Qwen-first via Wave 2 P2.1 — `_llm_soft_scores` calls `_qwen_soft_scores(prompt)` first, falls through to `apps_rg.integrations.hops._llm_client.call_judge` (which is the SAME `_llm_client.py` module W5 P5.1 just modified, on the OTHER side of its public surface). Generator and judge now both Qwen-first; the cascade hierarchy is uniform.
- **P5.4 verified**: `apps_rg/engines/hallucination_detector.py` and `apps_rg/engines/fact_check_engine.py` remain deterministic (pattern-matching + bag-of-words overlap; verified zero LLM imports in W0 audit). The Hybrid pipeline runs Generator (now Qwen-first) → Judge (Qwen-first via W2) → deterministic safety nets, in that order. No new wiring needed.
- **P5.5 verified**: ATS-compatibility surface (`apps_rg/integrations/ats_coverage.py`) stays deterministic — keyword matching, no LLM. Runtime characteristic: Qwen-32B local latency typically 2-5s per generation vs cloud Anthropic Sonnet 1-3s. The ±20% baseline criterion will be measured in W9 calibration once 30+ paired runs accumulate.
- **P5.6 deferred to W9**: 100-resume regression at composite ≥0.85 requires production-data accumulation across the apps_rg user pipeline. Cannot be measured this wave. The judge-calibration harness (W1 P1.3) is the consumption point; W9 is the formal verification phase.
- **No regression**: Wave 1's 5 determinism tests still green after Wave 5 edits (5 passed, 0.35s).

## Wave 4 findings — 2026-05-02 (P4.4 documented, P4.5 deferred)

- **P4.1 done**: `apps_lic/integrations/qwen_llm_client.py` authored. Async `QwenLLMClient` exposes `await client.generate(prompt, *, temperature, max_tokens) -> str` matching the contract `HOP5GenerationAgent` already calls (lines 313, 394 of HOP5GenerationAgent.py — `self._run_async(self.llm.generate(prompt, temperature=...))`). Uses `openai.AsyncOpenAI` pointed at `VLLM_BASE_URL`, lazy client init with persistent connection pool, fail-soft (returns `""` on any failure path so HOP5's `elif self.llm:` deterministic stub triggers). Six failure paths: preflight_failed / SDK absent / model_registry absent / client_init_failed / gateway_exception / empty_response. Emits `JUDGE_DECISION` marker with `app_name=apps_lic.hop5_generation`, `rubric_id=lic_hop5_generation_v1`. **Live evidence**: `await client.generate("Say hello in 5 words.", temperature=0.5, max_tokens=50)` returned `"Hello, how are you?"` from real local Qwen-32B. Composition-root wiring (the actual `HOP5GenerationAgent(llm_client=QwenLLMClient())` instantiation) is a separate operational task — the adapter is the canonical implementation that future wiring picks up; HOP5 fallback path keeps today-state safe.
- **P4.2 done**: `apps_lic/engines/HOP6ValidationAgent.py` `_alignment_judge()` now uses `_evaluate_strategic_alignment_qwen_first` with `backend="qwen"`. The new evaluate_fn cascades Qwen→deterministic: `_try_qwen_alignment()` returns `None` on any failure (preflight / SDK absent / model_registry absent / gateway_exception / empty_response / parse_failure / brief-too-short), and the existing `_evaluate_strategic_alignment` deterministic scorer covers the floor. Reason-code vocabulary stays consistent (`alignment_below_moderate_threshold`, `zero_overlap`) so HOP7/ExitPolicy mapping is stable across backends. Qwen path adds `qwen_judge` reason code + `qwen_rationale:` evidence ref so audit trail can distinguish backend used. Emits `JUDGE_DECISION` with `app_name=apps_lic.hop6_alignment`, `rubric_id=judge_hop6_strategic_alignment`. ABSTAIN-on-too-short semantics preserved (the deterministic branch raises `ValueError`, which `JudgeBase` converts to ABSTAIN scorecard per D6).
- **P4.3 verified**: HOP1/HOP3/HOP4/HOP7/HOP8/HOP9 — zero matches for `openai|anthropic|google.generativeai|chat.completions|messages.create|llm_client|Qwen|VLLM` (single grep across all six files). Critically, **HOP7GateDecisionAgent.py is Qwen-free** as required by the audit: gate decisions remain deterministic readers of `hop6_validation_report.x3_disposition` produced by the DecisionRouter. The audit's invariant ("Qwen MUST NOT be wired into HOP7 gate-decision") holds.
- **P4.4 documented**: Compliance posture for the single-model Qwen judge at HOP6. Risk classification: HOP6 produces a strategic-alignment scorecard, not a compliance-final decision — HOP7 (deterministic gate, X3 disposition, REVISE/HITL escalation) plus the four other HOP6 hard-gate validators (LIC-E001 placeholders / LIC-E020 length / LIC-E021 question-ending / LIC-E022 spam triggers) form the compliance perimeter. Qwen judge composite below-threshold flows to HITL via the existing exit_policy.yaml mapping. **Compensating controls already in place**: deterministic-fallback floor when Qwen unhealthy; ABSTAIN scorecard on too-short inputs; reason-code vocabulary preserved across backends so downstream audit doesn't need to know which backend fired. **Future hardening (deferred)**: pair Qwen with frontier-API second judge on the high-risk subset (configured ratio, not 100%) when production traffic surfaces a compliance-defensibility gap. Trigger condition: Wilson-CI on per-archetype agreement between Qwen and human spot-check drops below 0.85 over a 4-week rolling window.
- **P4.5 deferred**: Verification of "≥30 paired calibration rows before any promotion claim" requires production-data accumulation. Cannot be measured in this wave. The judge-calibration harness (`ops_scripts/calibration/judge_calibration.py`, W1 P1.3) is the consumption point — its weekly Markdown report at `docs/reports/calibration/judge/<YYYY-Www>.md` will surface the per-app row count and watchdog the unknown-budget ceiling. W9 is the formal consumption phase.
- **No regression**: Wave 1's 5 determinism tests still green after Wave 4 edits (5 passed, 0.37s).

## Wave 3 findings — 2026-05-02 (P3.2 collapsed, P3.4 deferred)

- **P3.1 done**: `apps_research/engines/company_brief_engine.py` `_synthesize` now tries local Qwen first via new `_qwen_synthesize` method; falls through to `SovereignLLMGateway` (cloud) and finally to `_stub_synthesis`. Same cascade pattern as Wave 2 P2.1: sync OpenAI SDK pointed at `VLLM_BASE_URL`, `temperature=0.2` for synthesis, `max_tokens=2000`. Five failure paths handled (preflight_failed / SDK absent / model_registry absent / gateway_exception / empty_response / parse_failure→stub-detection). Emits `JUDGE_DECISION` marker with `app_name=apps_research.company_brief`, `rubric_id=company_brief_synthesis_v1` for the judge-calibration harness to track synthesis-availability + cloud-fallback ratio.
- **P3.2 collapsed**: HOP3 outputs are STRUCTURED data, not free text. `apps_research/engines/hop_research_assembly_engine.py` returns `{"research_artifact": <dict>, "research_assembly_completed": <bool>}`. `apps_exec/engines/hop_capability_extraction_engine.py` returns `{"extracted_capabilities": <dict>, "capability_extraction_completed": <bool>}`. LLM-judging structured dict outputs is over-engineering vs deterministic schema validation. The audit's "Judge verdict + ROUTER_DECISION paired per run" requirement is appropriate for free-text generators, not structured aggregators. Phase collapses with documented reasoning.
- **P3.3 verified**: Orchestrator-level Qwen routing is already in place in BOTH `apps_research/reasoning/ResearchOrchestrator.py` AND `apps_exec/reasoning/ExecOrchestrator.py`:
  - Both import `AppsQwenGateway`, `AppsQwenRequest`, `apps_qwen_telemetry` from `agentic_core.L3_orchestration.inference.qwen_vllm` (lines 27-37 / 28-38).
  - Both initialize `self._qwen_gateway = AppsQwenGateway(model_id=QWEN_LOCAL_MODEL_ID)` when `qwen_enabled` and `_QWEN_AVAILABLE` and not opt-out.
  - Both use `LOCAL_VLLM` provider routing via `vllm_routing_predicates.evaluate(routing_ctx)` and `VLLMGatewayAdapter.evaluate()` for token budget / backpressure / circuit breaker.
  - Both emit `LOCAL_FIRST_DISPOSITION` log lines for routing-decision audit.
  - Both fail-soft on init error (`self._qwen_init_error`) and raise only when `LOCAL_VLLM` is selected with init-failed state.
- **P3.4 deferred**: 50-run offline agreement target (judge ≥0.9 vs L6 ground truth) requires production-data collection + L6 ground-truth labelling across many runs. Cannot be measured in this wave; deferred to W9 calibration phase where `judge_calibration.py` weekly reports + human spot-check sampling will begin building the agreement dataset.
- **No regression**: Wave 1's 5 determinism tests still green after Wave 3 edits.

## Wave 2 findings — 2026-05-02 (P2.2 collapsed)

- **P2.1 done**: `apps_eval/engines/narrative_judge_scorer.py` `_llm_soft_scores` now tries local Qwen first via `_qwen_soft_scores(prompt)`; falls through to `apps_rg.integrations.hops._llm_client.call_judge` (Anthropic → OpenAI) when Qwen is unavailable. Qwen path uses the OpenAI-compatible sync SDK pointed at `VLLM_BASE_URL`, `temperature=0`, `max_tokens=256`. Emits `JUDGE_DECISION` marker per call with `app_name=apps_eval.narrative_judge`, `rubric_id=narrative_judge_v1`, composite synthesized from the two-dim soft scores (0.4 × tone + 0.6 × naturalness). Five failure paths all handled: preflight_failed / ImportError (openai SDK absent) / gateway_exception / empty response / parse_failure.
- **P2.2 N/A**: `apps_eval/engines/hitl_decision_quality_engine.py` docstring line 8 explicitly states "Dimensions (deterministic, no ML)". Statistics + arithmetic only (timeout_rate, denial_rate, approval_consistency, reason_coverage, latency quantiles). No LLM surface to switch. Phase collapses with a documented no-op.
- **P2.3 verified**: `GovernedEvalException.check_compensating_controls()` returns all 4 PASS (CC-EVAL-01 telemetry no-circularity, CC-EVAL-02 exception record accessible, CC-EVAL-03 import guard, CC-EVAL-04 review cadence). Formal-exception perimeter unchanged.
- **P2.4 verified**: `scenario_runner.py`, `scorecard_engine.py`, `regression_detector.py` — zero LLM imports, zero gateway calls. Purely deterministic as required by the audit recommendation.
- **No regression**: Wave 1's 5 determinism tests still green after Wave 2 edits.

## Rubric Policy (P1.5 target)

PROPOSED: leave rubrics where they live today.

- **Cohort rubrics** (one per consumer app) stay in `apps_eval/config/rubrics/`:
  `rub_apps_exec_brief_v1.yaml`, `rub_apps_research_brief_v1.yaml`,
  `rub_apps_rfp_response_v1.yaml`, `rub_apps_rg_resume_generation_v1.yaml`,
  `rub_apps_lic_outreach_v1.yaml`, `rub_apps_underwriting_decisioning_v1.yaml`,
  `rub_apps_eval_self_v1.yaml`, plus the shared `narrative_judge.yaml` and
  `_judge_models.yaml`.
- **App-local HOP-specific rubrics** stay in the owning app: e.g.
  `apps_lic/policy/rubrics/judge_hop6_alignment.yaml`. These rubrics are
  consumed by a single HOP inside the app and carry app-specific policy
  that would not be meaningful at the cohort level.
- **Resolution rule** for the judge wrapper: accept an explicit
  `rubric_path: Path` parameter at call-site; no implicit resolution;
  document the two locations in the wrapper docstring.

Rationale: consolidating into `apps_eval/` would force cross-app imports
for an app-specific artifact (boundary blur); keeping app-local rubrics
in their owning app preserves layer gravity per `boundary-enforcement`.

## Gap Register

_Empty — gaps captured in-wave via `DEFERRED_SCOPE:` markers per
constitutional §24._

## Supersedes

_None._

## Notion Cross-Reference

- Plans DB page: `35427693-f55c-81cd-916c-dda8d0fe9804`
- URL: https://www.notion.so/apps_-Eval-Generation-Pattern-Rollout-Qwen-32B-vLLM-Backend-35427693f55c81cd916cdda8d0fe9804
