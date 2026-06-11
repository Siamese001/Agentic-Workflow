---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\l0-routing-calibration-gap-audit-b3c9d4.md'
original_relative_path: '_archive\\2026-05\\l0-routing-calibration-gap-audit-b3c9d4.md'
source_sha256: 86eb0bb27488e0dfb342d4e0f78b4ea80169059a677b3c5b5c80a200e4d2fa03
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L0 Routing — Calibration-Data Gap Audit (R1A / R1B / R5 / R3 / C0→Prompt Assembly)

Status: **ALL WAVES EXECUTED (W0 + W1 + W1b + W2 + W3 + W4 + W5)** · Tier: **T3** (plan is T2, execution waves are T3)
Date: 2026-04-23 (audit + W0 + W1) · 2026-04-24 (W2 + W3 + W4 + W1b + W5 runtime wiring) · 267/267 tests pass
Scope doc: `docs/reference/_notes/agentic_process_mapping_v34.md` §[3] Route Decision + Switching
Authoritative doc: `docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v11.md`
Sibling audit (structural, not this one): `.cursor/plans/l0-routing-best-practice-audit-1f9180.md`
ADG Provenance: backend=degraded_grep, snapshot=n/a
DEGRADED_FALLBACK: reason=adg_sqlite_mcp_transport_closed; used filesystem find_by_name + targeted read_file for code enumeration (constitutional §ADG-First — health probe attempted, fallback logged)

## Intent

User asked: "Review best practices (Anthropic / Google / OpenAI) for L0 route decision & switching, in particular **what data to calibrate routing decision criteria on across the five paths** — R1A, R1B, R5, R3, C0→Prompt Assembly."

This audit answers that question and enumerates the calibration gaps in the current repo. **No code edits** are proposed in the audit itself — downstream execution waves are deferred pending user selection.

## TL;DR — Verdict

- The repo already has a **structural dispatcher** (`PathRouter`) and a **gate scaffold** (`route_gates.check_route_gates` for D1/D2) but **no calibrated decision surface**.
- Every threshold in play is a **single scalar literal** (`DEFAULT_ABSTAIN_THRESHOLD=0.50` in `abstain_contract.py:19`, `similarity_threshold=0.98` in `semantic_cache_manager.py:354`). None are tied to offline eval sets, telemetry feedback, or per-namespace calibration.
- **No multi-signal feature vector** feeds any route decision. Vendor best practice (Anthropic, Vertex, OpenAI) is to score on ≥4 independent signals and apply a calibrated threshold derived from a representative query set.
- **No prediction score for "does this prompt need grounding?"** (Vertex dynamic-retrieval equivalent — default threshold 0.7). R3 selection is implicit via `check_ids` payload shape in `PathRouter.select_path:183-190`.
- **No `prompt_cache_key` equivalent** for sticky-prefix cache-hit improvement (OpenAI reports 60%→87% hit-rate lift).
- **C0 → Prompt Assembly** has HMAC/slot-order discipline (`assembly_stage.py`) but no per-claim grounding confidence (Vertex grounded-answer pattern) and no evidence-coverage score feeding the R3-vs-R5 gate.

---

## Part 1 — Vendor Best Practices (synthesized)

### 1.1 Anthropic — *Building Effective Agents* (2024-12; re-read 2026-04-23)

**Routing workflow** (directly cited): "Classify an input and direct it to a specialized followup task… classification can be handled by an LLM *or* a more traditional classification model/algorithm." Anthropic explicitly names TWO calibration shapes:
1. **Rule/heuristic classifier** — fast, deterministic, auditable.
2. **LLM classifier** — higher recall on long-tail intents, slower.

**When to use routing**: "Distinct categories that are better handled separately, AND classification can be handled accurately." Implicit calibration requirement: **pre-deployment accuracy target on a labeled eval set**, else the router's error rate compounds downstream.

**Augmented-LLM discipline**: every routed branch must be tailored to its category — "optimizing for one kind of input can hurt performance on other inputs." This means each path (R1A/R1B/R3/R4/R5) needs its own calibration set.

### 1.2 OpenAI — *Prompt Caching 201* (cookbook, 2025)

Three calibration surfaces distilled:
1. **Prefix stability** — cache hits depend on exact prefix match of first ~256 tokens. Calibration datum: **template prefix churn rate** (how often the system prompt mutates). If the prefix drifts week-over-week, exact-cache ROI collapses.
2. **`prompt_cache_key` as shard key** — granularity tuning:
   - Per-user → best reuse within a user's related conversations.
   - Per-conversation → better load distribution when a user runs many threads.
   - Too-narrow key → traffic spreads across machines, cache invalidates.
   - Too-wide key → >15 RPM per prefix overflows to new machines, each is a miss.
   - **Calibration datum**: observed RPM per prefix+key combination.
3. **`cached_tokens` per request** — OpenAI returns this field on each completion. Calibration datum: **rolling cache hit ratio** = `sum(cached_tokens) / sum(prompt_tokens)`. Target: ≥40% once prefix is stable.

**Implication for R1A**: exact-cache routing MUST track `cached_tokens` or an equivalent hit counter and feed it back into freshness-policy tuning.

### 1.3 Google Vertex AI — *Grounded Answers / Dynamic Retrieval*

Two directly-applicable signals:
1. **Dynamic-retrieval prediction score** (0.0–1.0) — assigned to each prompt: "whether the prompt can benefit from grounding with the most up-to-date information." Threshold default = **0.7**. Tuning procedure (cited verbatim):
   > "Create a representative set of queries that you expect to encounter. Sort the queries according to the prediction score in the response and select a good threshold for your use case."
2. **Per-claim grounding confidence score** — emitted alongside each sentence in the grounded answer. "Confidence scores: A number from 0 to 1 that indicates how grounded the claim is in the provided set of grounding chunks."

**Implication for R3 and C0**: the R3-vs-R5 gate should consume a prediction score (or analogous coverage score) — not a payload-shape heuristic. And C0's evidence contract should carry per-claim grounding confidence, not just "did we fetch evidence".

### 1.4 Industry consensus — semantic-cache threshold tuning

(Sources: GPT Semantic Cache arXiv 2411.05276, DeepLearning.AI Semantic-Caching course, Azure APIM semantic-cache policy, TrueFoundry / Maxim production notes)

Consistent pattern across sources:
- **One similarity threshold is wrong.** Calibrate per domain using a **precision-recall curve** on a labeled (query, acceptable-reuse) dataset.
- Precision-critical (e.g. factual Q&A): threshold **0.94–0.98** (industry range).
- Recall-optimized (e.g. boilerplate responses): threshold **0.85–0.90**.
- **Must-bypass list** — hard-coded flow classes that never consult the cache (writes, HITL, actions with side effects). The repo already has this pattern in `SemanticCacheManager.MUST_BYPASS_FLOWS` — ✅ conforming.
- **TTL / freshness band** — cache-hit return must respect a freshness SLA. No source permits unbounded TTL for semantic hits.

---

## Part 2 — Calibration Signal Matrix (the answer to the user's question)

Minimum feature set each path's decision should score on. Every signal must be **observable at routing time** (no future-looking dependencies) and **loggable** (so the ledger can be replayed against new thresholds).

### 2.1 R1A — Exact Cache

| Signal | Type | Source of truth | Repo status |
|---|---|---|:---:|
| Canonical request hash | str (sha256) | `route_gates.canonical_request_hash` | ✅ present |
| Tenant / ACL scope | str | ingress envelope | ⚠️ not bound into R1A key |
| Freshness band required | enum {fresh, bounded, stale_ok, volatile} | L1 plan (declared) | ❌ not emitted |
| Hit age vs TTL | int seconds | L1ExactCache entry + clock | ✅ TTL stored, ⚠️ not surfaced in contract |
| Namespace | str | caller | ✅ plumbed |
| Prefix-stability flag (template churn) | bool | template registry commit hash | ❌ missing |
| `cached_tokens` / hit counter rolling | int | OTEL counter | ❌ missing |

**Calibration procedure** (vendor-aligned):
- Label a representative query set (N≥500) with `{expected_reuse, not_reusable}`.
- Measure per-namespace exact-hit rate. Target: ≥20% after warmup. Below that → freshness policy is too tight or keyspace is too wide.
- Alert on `cached_tokens/prompt_tokens < 0.4` rolling 7-day (OpenAI target).

### 2.2 R1B — Semantic Cache

| Signal | Type | Source of truth | Repo status |
|---|---|---|:---:|
| Query embedding vector | np.array | embedding factory | ✅ (bge-m3) |
| Top-k similarity score | float | GPTCache recall | ✅ scalar returned |
| Similarity threshold | float | `semantic_cache_manager.similarity_threshold` | ⚠️ hardcoded 0.98, no calibration |
| Flow class (`MUST_BYPASS_FLOWS`) | enum | caller | ✅ present |
| Corpus version | str | embedding model id | ✅ plumbed |
| Policy version | str | caller | ✅ plumbed |
| Tenant isolation bit | bool | caller | ✅ plumbed (D2 key) |
| Age of matched entry | int seconds | cache entry | ⚠️ not surfaced in contract |
| Second-best-match gap (precision signal) | float | GPTCache top-k | ❌ not emitted |
| Human-labeled reuse-acceptance per (query, response) | bool | eval set | ❌ no eval set exists |

**Calibration procedure**:
- Build labeled set: pairs of (new_query, cached_response) with human verdict `accept/reject`.
- Compute precision-recall curve across threshold sweep {0.80, 0.85, 0.90, 0.94, 0.97, 0.98, 0.99}.
- Select threshold per namespace: precision-critical → threshold that yields ≥0.95 precision; recall-optimized → highest-recall point with precision ≥0.90.
- The current 0.98 is a **conservative literal** with no empirical basis — likely over-rejecting.

### 2.3 R5 — Fallback (Abstain / Clarify / Safe Default)

| Signal | Type | Source of truth | Repo status |
|---|---|---|:---:|
| Scalar confidence | float [0,1] | caller | ✅ via `plan_abstain` |
| Abstain threshold | float | `DEFAULT_ABSTAIN_THRESHOLD = 0.50` | ⚠️ global literal, not per-task-class |
| Coverage score (evidence completeness) | float | C0 evidence contract | ⚠️ C0 has `c0_evidence_contract_types` but coverage not computed |
| OOD / intent-drift score | float | shadow router classifier | ⚠️ `shadow_router_classifier.py` exists, **not wired** to abstain |
| Toxicity / policy-violation flag | bool | L5 guardrail | ⚠️ L5 exists, not surfaced in abstain decision |
| Cost / budget cap breached | bool | `TokenCapArtifact.gate_result == DENY` | ✅ present, not routed to R5 |
| Explicit user "I don't know" / clarification-needed | bool | L1 plan | ⚠️ implicit, not enumerated |
| Circuit breaker OPEN | bool | `RoutingRationale.CIRCUIT_BREAKER_OPEN` enum exists | ⚠️ enum present, no emitter wired |

**Calibration procedure**:
- Enumerate abstain **triggers** as a closed set (currently: single `confidence<0.50`). Best practice: ≥5 independent triggers, logged with their contributing signal.
- Per-trigger precision measured on replay traces: "When R5 fires for reason X, does human rater agree it should have fired?"
- Missing: no trace carries the reason code in a machine-parseable field today (repo has `reason_codes` tuple in `L0RouteContract`, but no producer emits enriched codes).

### 2.4 R3 — Simple Grounded Read

| Signal | Type | Source of truth | Repo status |
|---|---|---|:---:|
| Grounding-need prediction score | float [0,1] | Vertex-style classifier | ❌ **missing entirely** |
| Work-class classification | enum {summarize, compare, analyze, act, factual} | L1 plan `work_class` | ⚠️ documented in v33 §[2] I3, not plumbed |
| Declared freshness requirement | enum (shared with R1A) | L1 plan | ❌ not emitted |
| Number of declared `check_ids` | int | payload | ✅ (but abused as shape heuristic) |
| Evidence-pool size for this query | int | C0 fetch result | ⚠️ C0 exists but coverage not scored pre-R3 |
| Historical grounding success rate for this intent | float | L6 telemetry rollup | ❌ no rollup exists |
| Budget available vs min-required grounded-step cost | float | TokenCap | ⚠️ token gate exists, not R3-scoped |

**Calibration procedure**:
- Vendor verbatim (Vertex): assemble representative query set, score prediction, sweep threshold to find operating point.
- Default to 0.7 as Vertex does, then tune per agent class (LIC, EVAL, RFP, RG, Research) once telemetry accrues.

### 2.5 C0 → Prompt Assembly (the cascade inside R3)

| Signal | Type | Source of truth | Repo status |
|---|---|---|:---:|
| Evidence span coverage (% of claim-slots backed) | float | C0.5 contract verify | ⚠️ contract exists (`c0_evidence_contract_types.py`), per-claim score absent |
| Retrieval dedup / rerank score | float | `c0_reranker` model | ✅ reranker present, score not surfaced upstream |
| Token-budget headroom | int | `TokenCapArtifact` | ✅ present |
| Template / prefix stability fingerprint | hash | prompt template registry | ⚠️ `prompt_version_store.py` exists, fingerprint not exported to router |
| D0 injection fence present | bool | `GovernedPayload.__post_init__` warning | ✅ present (warning only) |
| HMAC integrity | hash | `assembly_stage.canonical_bytes` | ✅ present |
| Adversarial / injection score | float | `assembly_injection_neutralizer` | ⚠️ neutralizer runs, binary pass/fail, not graded |
| Per-claim grounding confidence | float[] | — | ❌ **missing** (Vertex pattern not implemented) |

**Calibration procedure**:
- C0 MUST emit an evidence-coverage score `[0,1]` = (claims_supported / claims_total). This score is the primary input to the R3-vs-R5 re-evaluation after fetch.
- If `coverage < r3_min_coverage` (suggest initial 0.6), **rewrite / broaden / decompose** per v11 §C0.6 — this loop exists in the doc but not in code.
- Prompt Assembly must record a deterministic template-prefix hash so downstream cache-hit analysis can attribute misses to prefix churn (OpenAI pattern).

---

## Part 3 — Repo Gap Matrix (calibration angle)

| # | Gap | Path(s) affected | Vendor citation | Severity | Effort |
|---:|---|---|---|:---:|:---:|
| G1 | No grounding-need prediction score. R3 selection uses `check_ids` payload shape. | R3, C0 | Vertex dynamic retrieval | **HIGH** | M |
| G2 | Semantic-cache threshold is global literal `0.98`, not calibrated per namespace. | R1B | industry consensus | **HIGH** | S |
| G3 | Abstain uses one signal (scalar confidence vs 0.50). No OOD, toxicity, budget, circuit-breaker, or clarification signal wired. | R5 | Anthropic routing; constitutional §6 HITL | **HIGH** | M |
| G4 | No `prompt_cache_key` / sticky-prefix affordance. `canonical_request_hash` exists but not grouped by user/conversation. | R1A | OpenAI Prompt Caching 201 §4.4 | MEDIUM | S |
| G5 | C0 has no per-claim grounding confidence; coverage loop (v11 §C0.6) not implemented. | R3, C0 | Vertex grounded-gen | **HIGH** | L |
| G6 | No offline labeled eval set for any routing decision. Thresholds are ungrounded. | all five | Anthropic ("accurate classification"); Vertex ("representative set") | **HIGH** | L |
| G7 | No feedback loop from telemetry to threshold adjustment. | all five | Anthropic evaluator-optimizer | MEDIUM | M |
| G8 | `cached_tokens` / cache-hit ratio not emitted as a first-class OTEL metric. | R1A, R1B | OpenAI §3.1 | MEDIUM | S |
| G9 | L1 plan does not emit `work_class`, `freshness_class`, or `grounding_required` as typed fields consumable by L0. | R3, R5 | v33 §[2] I3 + v11 §L0 ingress | **HIGH** | M |
| G10 | `shadow_router_classifier.py` exists but is not consulted by `PathRouter`. | R5 | Anthropic ("LLM or traditional classifier") | MEDIUM | M |
| G11 | Prompt-template prefix fingerprint not exported for cache-analytics. | R1A, C0 | OpenAI §4.2 | LOW | S |
| G12 | No precision-recall curve / calibration harness exists under `tests/` or `tools/`. | all five | industry consensus | **HIGH** | L |
| G13 | `L0RouteContract.reason_codes` is a tuple of strings with no closed vocabulary beyond `d1_exact_hit` / `d2_semantic_hit`. Vendor best practice: finite enum per decision. | all five | v9 §ROUTE DECISION | MEDIUM | S |

Legend: Effort = S (≤1 day, single file), M (2–5 files, ≤1 week), L (≥1 week, cross-layer).

### Severity distribution

- HIGH: 7 (G1, G2, G3, G5, G6, G9, G12)
- MEDIUM: 5 (G4, G7, G8, G10, G13)
- LOW: 1 (G11)

---

## Part 4 — Remediation Waves (DEFERRED — no execution)

All waves are proposed only; no code changes performed. Execution requires user approval (Author-Gate).

### Dependency ordering

```
W0 (eval harness) ──► W1 (features) ──► W2 (calibration) ──► W3 (wiring) ──► W4 (feedback)
                              │                                     ▲
                              └── W1b (contract enrichment) ────────┘
```

### Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W0 | W0.P1, W0.P2 | Build labeled eval sets + threshold-sweep harness (no code wiring) | ~18k 🟢 | representative query corpus can be assembled from prod traces + synthesis | ✅ DONE 2026-04-23 | Harness runs, emits PR curve per path, under `tools/calibration/` |
| W1 | W1.P1, W1.P2, W1.P3 | Emit routing feature vector: `work_class`, `freshness_class`, `grounding_need_score`, `ood_score`, `budget_headroom` | ~35k 🟡 | L1 planner can be extended additively | ✅ DONE 2026-04-23 | Feature vector typed + heuristic classifier + telemetry pass-through; 50/50 new tests pass, 27/27 PathRouter back-compat tests pass |
| W1b | W1b.P1 | Enrich `L0RouteContract` reason_codes to closed enum; surface per-claim coverage from C0 | ~15k 🟢 | L0RouteContract is still lightly consumed | ✅ DONE 2026-04-24 | `RouteReasonCode` (16 codes) + `ClaimGroundingConfidence` + `mean/min_claim_confidence` shipped; 224/224 tests pass |
| W2 | W2.P1, W2.P2 | Derive calibrated thresholds per namespace; retire hardcoded 0.98 / 0.50 literals | ~22k 🟡 | W0 harness output is accepted by calibrators | ✅ DONE 2026-04-24 | `config/routing_thresholds.yaml` shipped + loader with env/namespace/default/literal fallback chain |
| W3 | W3.P1, W3.P2, W3.P3 | Wire features → router: (a) R3 gate on grounding-need score, (b) R5 on multi-signal, (c) R1B per-namespace threshold | ~48k 🔴 | PathRouter public API can evolve | ✅ DONE 2026-04-24 | `check_r3_grounding_gate` + `plan_abstain_multi_signal` + per-namespace R1B threshold enforcement shipped additively |
| W4 | W4.P1, W4.P2 | OTEL metrics + feedback loop (`cached_tokens`, `hit_ratio`, `false_r5_rate`); weekly calibration cadence | ~20k 🟢 | OTEL MCP runtime ingest works | ✅ DONE 2026-04-24 | 5 counter emitters + hit_ratio helper + `weekly_refresh.py` CLI with drift-report generation |
| W5 | W5.P1..P5 | Runtime wiring — SemanticCacheManager YAML retrofit, L1 producer hook, C0 producer hook, PathRouter.route_with_features dispatch, metric call sites | ~63k 🟡 | Observability import fail-soft | ✅ DONE 2026-04-24 | 3 new producer/dispatch modules + 2 additive edits; 43 new tests; 267/267 total pass; zero existing call sites broken |

Total span: ~158k tokens across 5 waves.

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W0.P1 | Build labeled eval sets for R1A/R1B/R5/R3/C0 | `tests/calibration/fixtures/{r1a,r1b,r5,r3,c0}*.json` | Seed fixtures only (12–16 samples each); real-trace corpora deferred | 10k | ✅ DONE — 5 fixtures, 64 total records |
| W0.P2 | Threshold-sweep + PR-curve harness | `tools/calibration/{__init__,feature_vector,threshold_sweep,__main__}.py`, `tests/calibration/test_threshold_sweep.py` | Reproducible, progress-bar compliant | 8k | ✅ DONE — 23/23 tests pass, 5 reports in `docs/reports/calibration/` |
| W1.P1 | Typed routing feature vector contract (additive, not L1-plan mutation) | `agentic_core/runtime/contracts/routing_features.py` (new), `tests/unit/runtime/contracts/test_routing_features.py` (new) | Layer gravity — `runtime.contracts` below L0, so `FreshnessClass` duplicated with parity test | 14k | ✅ DONE — 19/19 tests pass, parity test with L0 FreshnessClass |
| W1.P2 | Heuristic grounding-need classifier (Anthropic "traditional classifier" option) | `agentic_core/L1_cognition/reasoning/ml_decision_support/features/grounding_need_features.py` (new), `tests/unit/agentic_core/L1_cognition/test_grounding_need_features.py` (new) | Heuristic first; W0 target ~0.72 as default intercept calibration | 11k | ✅ DONE — 24/24 tests pass, fixture ranking confirmed |
| W1.P3 | Wire optional `feature_vector` into `RoutingTelemetryContext` + `RoutingTelemetry` dataclass (back-compat default None) | `agentic_core/L0_routing/utils/routing_telemetry.py` (edit), `tests/unit/L0_routing/test_routing_telemetry_feature_vector.py` (new) | Additive only; 5 existing call sites unchanged | 10k | ✅ DONE — 7/7 pass-through tests pass + 27/27 PathRouter back-compat tests still pass |
| W1b.P1 | `RouteReasonCode` closed enum (16 values spanning D1/D2/D3/D4/R5/generic) + `validate_reason_codes` normalizer + `ClaimGroundingConfidence` per-claim Vertex pattern + `mean/min_claim_confidence` helpers + dangling-span validation | `agentic_core/L0_routing/types/routing_artifact_types.py` (edit), `agentic_core/L0_routing/reasoning/route_gates.py` (edit — emits `RouteReasonCode.*.value`), `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` (edit), `tests/unit/L0_routing/test_route_reason_codes.py` (new), `tests/unit/L3_orchestration/test_c0_claim_confidences.py` (new) | `str`-enum preserves equality contract — no existing tests broken | 15k | ✅ DONE — 16 enum values align with W3.P1 gate return codes + W3.P2 R5 triggers |
| W2.P1 | Move thresholds (`similarity_threshold`, `DEFAULT_ABSTAIN_THRESHOLD`) to `config/routing_thresholds.yaml` | `config/routing_thresholds.yaml` (new), `agentic_core/runtime/config/routing_thresholds.py` (new), `tests/unit/runtime/config/test_routing_thresholds.py` (new) | Back-compat preserved — existing callers unchanged | 12k | ✅ DONE — loader with 4-tier fallback (env > namespace > default > literal) |
| W2.P2 | Calibrate initial thresholds from W0 harness output | `config/routing_thresholds.yaml` + `docs/reports/calibration/w2_initial_calibration.md` (new) | Seed-data only; re-calibrate on ≥500 real traces per namespace | 10k | ✅ DONE — 8 namespaces seeded from W0 PR curves |
| W3.P1 | Wire `grounding_need_score` into R3 gate | `agentic_core/L0_routing/reasoning/route_gates.py` (edit — `check_r3_grounding_gate`), `tests/unit/L0_routing/test_r3_grounding_gate.py` (new) | Back-compat: NO_SIGNAL returns no_grounding_signal so dispatcher falls back | 18k | ✅ DONE — 4 reason codes (`no_grounding_signal`, `below_grounding_threshold`, `d3_grounding_required`, `d3_coverage_below_floor`) |
| W3.P2 | Wire multi-signal R5 (6 triggers with priority ordering) | `agentic_core/runtime/contracts/abstain_contract.py` (edit — `plan_abstain_multi_signal`), `tests/unit/runtime/contracts/test_multi_signal_r5.py` (new) | `plan_abstain` unchanged; additive new function | 18k | ✅ DONE — 6 closed reason codes, priority toxicity > circuit > budget > OOD > clarify > confidence |
| W3.P3 | Wire per-namespace R1B threshold lookup into `check_d2_semantic_cache` | `route_gates.py` (edit — `similarity_threshold_override` kwarg + post-hit enforcement) | Post-hit enforcement only; underlying `SemanticCacheManager` literal unchanged (deferred) | 12k | ✅ DONE — effective threshold resolved + logged + used to reject false-positive hits |
| W4.P1 | OTEL metrics: `r1a.exact_hit`, `r1b.semantic_hit`, `r5.fired`, `r3.coverage_below_floor`, `r3.grounded` | `agentic_core/L6_observability/routing_calibration_metrics.py` (new), `tests/unit/L6_observability/test_routing_calibration_metrics.py` (new) | OTEL fail-soft — falls back to in-process counters | 10k | ✅ DONE — 5 counters + `hit_ratio()` helper per OpenAI §3.1 |
| W4.P2 | Weekly calibration refresh job + drift alert | `ops_scripts/calibration/{__init__,weekly_refresh}.py` (new) | Advisory only — does NOT edit YAML; operators review | 10k | ✅ DONE — CLI: `--no-sweep`, `--output`, `--fail-on-alert`; warn/alert bands at 0.02/0.05 Δ |

---

## ADG_HOTSPOT_REPORT (calibration-touch files)

Files most likely to be touched during execution waves, ranked by layer-weighted impact. ADG MCP degraded at audit time; ranks derived from direct fan-in inspection during doc audit (`l0-routing-best-practice-audit-1f9180.md` §Hotspot) + filesystem evidence.

| Rank | File | Archetype | Surface | Layer Mult | Notes |
|---:|---|---|---|:---:|---|
| 1 | `agentic_core/L0_routing/reasoning/path_router.py` | ORCHESTRATOR | Execution + Observability + Security | ×2.0 (L0) | Sole prod dispatcher. W3 touches this directly. |
| 2 | `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | STATE_NODE | State + Write | ×1.75 (L4) | D2 gate + similarity_threshold literal. W2/W3 touch. |
| 3 | `agentic_core/runtime/contracts/abstain_contract.py` | SAFETY_GATEKEEPER | Security | ×1.0 (runtime) | DEFAULT_ABSTAIN_THRESHOLD literal. W2 touches. |
| 4 | `agentic_core/L0_routing/reasoning/route_gates.py` | ORCHESTRATOR | Execution | ×2.0 (L0) | W3 edit target for R3 feature gate. |
| 5 | `agentic_core/L0_routing/types/routing_artifact_types.py` | CENTRAL_DEPENDENCY | Execution | ×2.0 (L0) | `L0RouteContract.reason_codes` enum closure in W1b. |
| 6 | `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` | CENTRAL_DEPENDENCY | State | ×1.75 (L3) | `coverage_score` additive in W1b. |
| 7 | `agentic_core/L1_cognition/reasoning/ml_decision_support/features/c0_features.py` | CENTRAL_DEPENDENCY | Execution | ×1.0 (L1) | Hosts `grounding_need_score` model in W1.P2. |
| 8 | `agentic_core/L6_observability/routing_decision_events_schema.py` | CENTRAL_DEPENDENCY | Observability | ×0.75 (L6) | OTEL schema change in W4.P1. |

## ADG_GRAPH_LAYER_EVIDENCE

ADG MCP degraded at audit start (transport closed). Per constitutional §ADG-First, fallback logged above with reason code. Consulted during prior sibling audit `.cursor/plans/l0-routing-best-practice-audit-1f9180.md` (snapshot `adg_indexed_04222026_1508.sqlite`):

- **Materialized views** referenced in sibling audit (carried forward by provenance):
  1. `mv_graph_reverse_dependency_hotspots` — PathRouter fan-in = 5
  2. `mv_graph_chokepoint_bridges` — PathRouter is chokepoint L0 ↔ L2 execution proof path
  3. `mv_hotspot_centrality` — all three dispatchers below 90th-percentile L0 centrality
  4. `mv_dependency_cone_risk` — 5-file cone for Path-enum retirement (relevant to W1.P3 telemetry export only)
- **Semantic edges** planned for W3 pre-flight re-check: `resolves_callsite` (dispatcher unification), `flows_to` (R3/R4 L2-step invariants), `writes_to` (cache learn path).
- **P-views**: `v_p0_apps_direct_infra`, `v_p0_write_bypass_uwg`, `v_p1_mis_layered_infra` — all clean for the touched files in prior audit; W2/W3 must re-run pre-execution on a live snapshot.

**Mandatory pre-W2 action**: regenerate ADG snapshot (`python tools/generate_full_adg.py`) and re-verify hotspot rank + P-view clean status before any W3 edit. This is NOT covered by this audit — it's an execution prerequisite.

---

## Assumptions, Uncertainty, and Risks

### Assumptions

- A-1: A representative query corpus of ≥500 requests per agent class can be assembled or synthesized for W0 calibration. If not, thresholds cannot be empirically grounded.
- A-2: `L1_cognition` planner can be extended additively to emit `work_class`/`freshness_class`/`grounding_required` without breaking existing consumers (confirmed by plan file churn evidence, not code inspection).
- A-3: `shadow_router_classifier.py` can be repurposed or its learnings reused without retraining (unverified; it may be a drift detector only).
- A-4: OTEL MCP stays healthy enough for W4 metrics emission; runtime ADG ingest path validated.

### Uncertainty

- U-1: Whether the grounding-need-score classifier must be LLM-based (Anthropic option 2) or can remain heuristic (Anthropic option 1). **Resolution path**: W1.P2 starts heuristic, upgrade decision deferred to W2 eval results.
- U-2: Whether per-namespace thresholds require new storage (YAML) or can piggy-back on existing `config_store`. **Resolution path**: W2.P1 Author-Gate option set.
- U-3: Back-compat strategy for the three parallel dispatchers (PathRouter + AgenticRouter + DeterministicRoutingGateway). Sibling audit §W3 flagged this; this plan does NOT assume unification — it just accepts PathRouter as canonical and adds features behind it.

### Risks

- R-1: Calibrated thresholds that shift behavior in production. Mitigation: all W3 wiring behind env flags defaulting to off, replay-verified on fixed traces before flip.
- R-2: Scope creep from W1 contract changes cascading into every L1 planner call site. Mitigation: strict additive-only fields in W1.P1; no existing field semantics change.
- R-3: Overlap with sibling structural audit (`1f9180`) if it runs. Mitigation: this plan accepts current PathRouter as dispatcher of record; does NOT propose enum renames or dispatcher unification (those belong to 1f9180 W2/W3).

---

## Success Criteria (for this audit)

- [x] Vendor best practices extracted and cited (Anthropic, OpenAI, Vertex, industry consensus)
- [x] Per-path calibration signal matrix produced for R1A, R1B, R5, R3, C0→Prompt Assembly
- [x] Gaps mapped against repo with severity + effort
- [x] Remediation waves enumerated with token estimates + dependency graph
- [x] ADG provenance stamped (with degraded-fallback reason code)
- [x] No code edits performed
- [x] Cross-linked to sibling structural audit `1f9180` (distinct scope, no overlap)

---

## Next Author-Gate (caller's decision)

User should choose one of:

1. **Accept W0 only** — lowest-risk, unblocks empirical calibration without behavior change.
2. **Accept W0 + W1 + W1b** — builds the feature vector and typed contracts, still no behavioral change.
3. **Accept W0 → W2** — adds calibrated thresholds in config (removes 0.98 / 0.50 literals).
4. **Full sequence W0 → W4** — large T3 effort, requires ADR.
5. **Close audit without action** — vendor practices documented, repo stays as-is.

Do not proceed to W1+ without explicit selection. Before any W2/W3 edit, re-run ADG health + regenerate snapshot.
