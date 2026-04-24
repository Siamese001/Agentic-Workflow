# [3] ROUTE DECISION + SWITCHING — v12

> **Status:** Current doctrine. Supersedes `v11` (retained as historical reference).
> **Date:** 2026-04-24.
> **Companion:** `GAP_ANALYSIS_v11_vs_best_practices.md` (same folder).
> **Scope:** Dispatcher layer only. L3 orchestration, L2 execution, L5 safety-plane are named but
> owned elsewhere. Runtime HITL wiring is ADR-023 (`agentic_core/L5_safety/`), not this doc.

---

## 0. Contract (one-paragraph summary — read this first)

L0 is a **dispatcher, not an executor**. It consumes an approved `L1Plan` plus a query intent vector
and emits exactly one **Route Contract** (§2). The route contract decides which terminal
short-circuit (exact-cache, semantic-cache, fallback, HITL) or which downstream pipeline
(single grounded read, single action, parallel fan-out, evaluator-optimizer loop, managed
multi-step workflow) will do the actual work. L0 never retrieves, never reasons deeply, and never
calls a model — it only classifies, scores, and dispatches. Every dispatch is observable via the
**Route Telemetry Event** (§3) and every downstream failure has a **Fallback Chain** (§6).

---

## 1. Pedagogical Legend (preserved from v11)

```
🔵 Blue asks   = query_vec / intent vector
🟠 Orange knows = raw_text_vector / contextual_text_vector
🟢 Green maps  = knowledge_graph / entity_subgraph
[RET]          = Terminal early exit; bypasses L3, goes straight to [5] Exit Eval & Control
★              = New in v12 (not present in v11)
```

---

## 2. Route Contract Schema (★ W1 / G14)

Every dispatcher decision emits exactly one `RouteContract` record. This is the only artifact L0
produces — downstream layers consume it, trust it, and do not re-decide routing.

### 2.1 Required fields

| Field | Type | Notes |
|---|---|---|
| `contract_version` | string | Semver. Bumped on breaking field additions. Current: `1.0.0`. |
| `route_id` | enum | One of `R1A`, `R1B`, `R3_GROUNDED`, `R4_ACTION`, `R3R4_WORKFLOW`, `R5_FALLBACK`, `R-PAR`, `R-LOOP`, `R-HITL`, `R-CASC`. |
| `confidence` | float [0,1] | Classifier probability for the selected route. Calibrated per §4. |
| `reason_codes` | list[string] | Ordered machine-readable causes, e.g. `["high_freshness_required","action_bounded","cache_miss"]`. |
| `freshness_class` | enum | `REALTIME` (≤ 1 min), `FRESH` (≤ 1 h), `STABLE` (≤ 24 h), `ARCHIVAL` (no bound). Drives cache eligibility. |
| `cache_policy` | enum | `NO_CACHE`, `EXACT_ONLY`, `SEMANTIC_OK`, `CASCADE_CACHE_FIRST`. |
| `execution_form` | enum | `TERMINAL_SHORTCIRCUIT`, `SINGLE_STEP`, `PARALLEL_FANOUT`, `ITERATIVE_LOOP`, `MANAGED_WORKFLOW`, `HUMAN_GATED`. |
| `cost_tier` | enum ★ | `TIER_S` (small/cheap, e.g. Haiku-class), `TIER_M` (mid, Sonnet-class), `TIER_L` (large/frontier, Opus-class). See §5. |
| `fallback_chain` | list[RouteRef] ★ | Ordered list of alternate routes to try if the primary fails. See §6. |
| `slo` | object ★ | `{latency_budget_ms, token_budget_in, token_budget_out, cost_cap_usd}`. See §10. |
| `telemetry_keys` | list[string] ★ | Feature keys used by the classifier — persisted in the Telemetry Event (§3). |
| `tenant_scope` | object | `{tenant_id, region, acl_bounds}`. Populated from ingress pre-filter; downstream layers reject if missing. |
| `hmac_sig` | string | HMAC-SHA256 over the canonical JSON of all fields above, signed with the dispatcher key. Downstream layers MUST verify. |

### 2.2 Validity rules

- `cache_policy == NO_CACHE` ⟹ `execution_form != TERMINAL_SHORTCIRCUIT`.
- `execution_form == TERMINAL_SHORTCIRCUIT` ⟹ `route_id ∈ {R1A, R1B, R5_FALLBACK}`.
- `execution_form == HUMAN_GATED` ⟹ `route_id == R-HITL` AND `slo.latency_budget_ms` is waived.
- `confidence < surface_threshold` (see §4.2, default 0.72) ⟹ route MUST be a conservative
  fallback (`R3_GROUNDED` or `R5_FALLBACK`) — see §7 Cold-Start Safeguard.

### 2.3 Canonical JSON shape

```json
{
  "contract_version": "1.0.0",
  "route_id": "R3_GROUNDED",
  "confidence": 0.89,
  "reason_codes": ["support_target_required", "stable_freshness", "cache_miss"],
  "freshness_class": "STABLE",
  "cache_policy": "SEMANTIC_OK",
  "execution_form": "SINGLE_STEP",
  "cost_tier": "TIER_M",
  "fallback_chain": [
    {"route_id": "R3R4_WORKFLOW", "cost_tier": "TIER_L"},
    {"route_id": "R5_FALLBACK",  "cost_tier": "TIER_S"}
  ],
  "slo": {"latency_budget_ms": 4000, "token_budget_in": 8000, "token_budget_out": 1500, "cost_cap_usd": 0.05},
  "telemetry_keys": ["intent_class", "freshness_signal", "support_need", "tenant_quota_state"],
  "tenant_scope": {"tenant_id": "...", "region": "...", "acl_bounds": ["..."]},
  "hmac_sig": "..."
}
```

---

## 3. Route Telemetry Contract (★ W1 / G7)

Per Arthur.ai and Tian Pan's "Routing without observability" pitfall, every route decision MUST emit
a structured telemetry event to L6 observability. Without this, miscalibration is undetectable.

### 3.1 Required fields (RouteTelemetryEvent)

| Field | Source |
|---|---|
| `event_id`, `trace_id`, `span_id` | OTEL context |
| `route_id`, `confidence`, `reason_codes` | RouteContract |
| `classifier_features` | map[string,string|float] — the feature keys from `telemetry_keys` with their actual values |
| `classifier_model_id`, `classifier_version` | identity of the classifier (tiny model or rule set) used |
| `alternatives_considered` | list[{route_id, score}] — top-3 next-best routes and their scores |
| `calibration_bucket` | string — which calibration bucket this decision falls in (see §4) |
| `slo_snapshot` | RouteContract.slo copied |
| `tenant_scope_hash` | blake2b(tenant_scope) — avoids PII leak while preserving grouping |
| `timestamp_utc`, `dispatcher_pid`, `dispatcher_build_sha` | operational identity |

### 3.2 Downstream quality signal (linked event)

After the route executes, a second event `RouteOutcomeEvent` is emitted containing:

- `event_id_of_decision` (join key back to RouteTelemetryEvent)
- `outcome_status` ∈ `SUCCESS`, `DEGRADED`, `FALLBACK_TAKEN`, `FAILED`, `HITL_APPROVED`, `HITL_REJECTED`
- `observed_latency_ms`, `observed_tokens_in`, `observed_tokens_out`, `observed_cost_usd`
- `quality_signal` (optional; e.g. user feedback, eval rubric score, groundedness score)
- `fallback_depth` — 0 = primary succeeded, 1 = first fallback used, etc.

### 3.3 Analytics obligations

The L6 pipeline MUST expose, per (route_id × cost_tier × tenant_scope_hash):

- **Hit rate** (cache routes): hits / (hits + misses)
- **Escalation rate** (R-CASC): % of primary-tier attempts that escalated
- **Fallback-depth distribution**
- **Calibration curve**: predicted confidence bucket vs. observed outcome_status == SUCCESS rate
- **SLO breach rate**: % observed_latency > latency_budget_ms

These feed §4 calibration and §10 budget tuning.

---

## 4. Calibration Discipline (★ W1 / G8)

### 4.1 Principle

Per Tian Pan: *"Any system that sets confidence thresholds by intuition will be miscalibrated."*
Thresholds in v12 are placeholders; the **real** thresholds are set per deployment from measured data.

### 4.2 Threshold SSOT (defaults — override per deployment)

| Parameter | Default | Meaning |
|---|---|---|
| `classifier_surface_threshold` | 0.72 | Minimum classifier confidence to dispatch the chosen route without a conservative fallback wrap. |
| `classifier_dominance_delta` | 0.12 | Gap between top and 2nd route needed to suppress alternatives from fallback_chain. |
| `r1b_semantic_match_threshold` | 0.88 | Cosine similarity above which R1B short-circuits (after hybrid-fusion + policy gates). |
| `r_casc_escalation_threshold` | 0.55 | R-CASC: executor self-reported confidence below this forces escalation to next tier. |
| `r_loop_quality_threshold` | 0.85 | R-LOOP: critic-agent quality score above this breaks the refinement loop early. |
| `cold_start_conservative_threshold` | 0.50 | Classifier confidence below this forces `R3_GROUNDED` or `R5_FALLBACK` regardless of the top pick. |

### 4.3 Calibration workflow (production obligation)

1. **Bucket decisions** into 10 confidence bins (0.0-0.1, ..., 0.9-1.0).
2. **Measure** observed success rate per bin, per (route_id, cost_tier) cell.
3. **Adjust** the thresholds above so that:
   - `surface_threshold` falls at the bin where observed success ≥ 0.90.
   - `r_casc_escalation_threshold` falls where escalated queries show quality uplift ≥ 10% vs. non-escalated at the same bin.
4. **Re-measure** tail distribution separately (Tian Pan: *"Your routing system's accuracy on typical queries doesn't predict its behavior on tail queries"*).
5. **Cadence:** weekly review; threshold changes are Author-Gate-worthy and land in the Author-Gate Decision Ledger.

### 4.4 Forbidden

- Setting a new threshold without an evaluation run against domain-labeled data.
- Using benchmark-suite confidence calibration as a substitute for domain calibration.
- Removing `confidence` or `classifier_features` from telemetry to "reduce noise".

---

## 5. Cost-Tier Cascade (★ W1 + W2 / G1, G2)

v11 treated L2 executors as uniform. v12 makes cost-tier a first-class field on the Route Contract,
and introduces **R-CASC** as a dedicated route for confidence-based escalation.

### 5.1 Three tiers

| Tier | Indicative class | Typical use |
|---|---|---|
| `TIER_S` | Haiku-class / 0.5B-8B local / fine-tuned | Classification, extraction, short factual lookups, semantic-cache match scoring |
| `TIER_M` | Sonnet-class / 20-70B | Grounded single-step synthesis, policy interpretation, most R3 traffic |
| `TIER_L` | Opus-class / frontier | Multi-hop reasoning, ambiguous edges, R3R4 managed workflows, R-LOOP critic |

Tier identity is declared by the executor, not by model name — this keeps v12 provider-neutral.

### 5.2 R-CASC — Confidence-Based Cascade Route

```
┌──────────────────────────────────────────────┐
│ R-CASC  CONFIDENCE CASCADE                ★  │
│ - Try TIER_S first                           │
│ - Executor self-reports confidence           │
│ - If confidence < r_casc_escalation_threshold│
│   escalate to TIER_M (then TIER_L)           │
│ - Each escalation emits a RouteOutcomeEvent  │
│   with outcome_status=DEGRADED +             │
│   fallback_depth++ so §3 analytics see it    │
│ - Early abstention: TIER_S may explicitly    │
│   emit "I don't know" → skip to TIER_M       │
│   (does not count against quality)           │
└──────────────────────────────────────────────┘
```

**Invariants:**

- Max cascade depth = 3 (S → M → L). No fourth hop.
- Each hop consumes its own `slo.latency_budget_ms` slice; if cumulative latency would exceed the
  overall SLO, the cascade truncates and falls through to `fallback_chain`.
- `quality_signal` in the outcome event distinguishes "escalation was worth it" (quality uplift ≥
  10%) from "escalation did not help" (used to retune `r_casc_escalation_threshold`).
- R-CASC is NOT for freshness / action / HITL routing — only for capability-matched compute.

### 5.3 When to prefer routing vs cascading

| Situation | Use |
|---|---|
| Intent category reliably predicts tier | **Routing** (R3 / R4 with fixed `cost_tier`) |
| Tier depends on query difficulty that is hard to pre-classify | **Cascading** (R-CASC) |
| Latency budget is tight | **Routing** — cascading adds accumulated latency per hop |
| Unknown / novel intent | **Routing to conservative tier** (§7 Cold-Start) — NOT cascading, because classifier is the weak link, not the executor |

---

## 6. Fallback Chain (★ W3 / G6)

v11 had R5 as a terminal abstain and no other fallback structure. v12 makes fallback a first-class
ordered list on every Route Contract (see §2.1 `fallback_chain`).

### 6.1 Rules

- **Every** non-terminal route MUST have a non-empty `fallback_chain`.
- Terminal cache routes (`R1A`, `R1B`) have `fallback_chain == []` on hit; on miss they are not
  "falling back" — the dispatcher re-decides from scratch.
- `R5_FALLBACK` is always the final entry in any non-empty chain (or the whole chain if nothing
  else is available).
- Fallback triggers: executor timeout, provider outage, SLO breach, explicit `FAILED` outcome,
  cascade exhaustion, HITL rejection with no retry allowed.
- Multi-provider fallback lives inside the chain: a chain like
  `[{R3, cost_tier=TIER_M, provider=A}, {R3, cost_tier=TIER_M, provider=B}, R5_FALLBACK]` is valid
  and recommended for tier-M traffic where provider-A has a history of rate-limit spikes.

### 6.2 Canonical chains (starting points — tune per deployment)

| Primary | Recommended chain |
|---|---|
| `R1B` (semantic cache) | `[R1A (revalidate), R3_GROUNDED, R5_FALLBACK]` |
| `R3_GROUNDED` | `[R3R4_WORKFLOW (TIER_L), R-CASC, R5_FALLBACK]` |
| `R4_ACTION` | `[R-HITL (if side-effect reversibility ambiguous), R5_FALLBACK]` |
| `R3R4_WORKFLOW` | `[R-LOOP (if partial progress), R5_FALLBACK]` |
| `R-CASC` | `[R3R4_WORKFLOW, R5_FALLBACK]` |
| `R-PAR` | `[R3_GROUNDED (serial mode), R5_FALLBACK]` |
| `R-LOOP` | `[R3_GROUNDED (best-partial draft), R5_FALLBACK]` |
| `R-HITL` | `[R5_FALLBACK]` (after rejection) |

---

## 7. Cold-Start Safeguard (★ W3 / G9)

When the classifier is not confident (`confidence < cold_start_conservative_threshold`), the
dispatcher MUST:

1. Override the top-pick route to `R3_GROUNDED` (grounded single-step) with `cost_tier = TIER_M`.
2. Tag the telemetry event with `reason_codes += ["cold_start_override"]`.
3. Append the original top pick as the first entry of `fallback_chain` (so it can be tried if the
   conservative route succeeds and wants to retry with confidence).
4. Flag the tenant_scope_hash + feature vector for offline review — new-intent-type emergence is a
   signal the classifier needs retraining.

Rationale: Tian Pan — *"The cost of unnecessarily routing to a mid-tier model is much lower than the
cost of a bad answer from a small model that should have been escalated."*

---

## 8. Loop Guard (★ W3 / G10)

Complements v11's "forward-only L3, no backward edges" invariant. Addresses the cross-route loop
pattern identified by Galileo (same node re-entered across multiple routes within one trace).

### 8.1 Detection

- Every RouteOutcomeEvent carries `trace_id`.
- L6 observability computes a rolling `agent_efficiency_score` per trace:
  `unique_productive_spans / total_spans`, where "productive" = span that emitted a new artifact or
  mutated state.
- Threshold: if `agent_efficiency_score < 0.4` across ≥ 5 spans within a single trace, the loop
  guard fires.

### 8.2 Response

- Dispatcher is notified via the L6→L0 feedback channel (advisory only — L0 stays stateless per
  request, but next-request routing for the same `user_session_id` biases toward
  `R-HITL` or `R5_FALLBACK`).
- A `LoopSuspected` event is logged and surfaced in the routing dashboard.
- If the same session trips the guard twice in a window, the dispatcher forces `R-HITL` on the
  next request in that session.

---

## 9. Single-Agent-First Principle & Handoff vs Agent-as-Tool (★ W4 / G11, G12)

### 9.1 Start with one agent

Per OpenAI and Anthropic: *"Start with one agent whenever you can. Add specialists only when they
materially improve capability isolation, policy isolation, prompt clarity, or trace legibility.
Splitting too early creates more prompts, more traces, and more approval surfaces without
necessarily making the workflow better."*

Applied to v12: prefer `R3_GROUNDED` (one bounded step) over `R3R4_WORKFLOW` (multi-step) unless
the task genuinely demands dependency tracking, branching, joins, or resumable state.
`R3R4_WORKFLOW` is reserved for cases where the A. Execution Shape Classification step (§14) says
the contract **changes** between steps.

### 9.2 Handoff vs agent-as-tool

| Pattern | Meaning | v12 route |
|---|---|---|
| **Handoff** (ownership transfer) | Specialist owns the final response. L0 hands the whole contract over. | `R3R4_WORKFLOW` step that re-enters L0 with a new sub-contract |
| **Agent-as-tool** (manager-calls-helper) | Manager agent calls the specialist as a bounded tool; manager synthesizes the final answer. | `R3_GROUNDED` or `R4_ACTION` with a bounded tool call inside |

Dispatchers MUST pick one. The Route Contract's `execution_form` encodes this: `MANAGED_WORKFLOW`
with re-entry = handoff; `SINGLE_STEP` with tool = agent-as-tool.

---

## 10. Route SLO & Budget (★ W3 / G15)

`slo` is a required field on every Route Contract (§2.1). The dispatcher seeds defaults; the L3 /
L2 layers enforce them.

### 10.1 Default budgets (tune per deployment)

| Route | latency_budget_ms | token_budget_in | token_budget_out | cost_cap_usd |
|---|---:|---:|---:|---:|
| `R1A` | 50 | 0 | 0 | 0.00 |
| `R1B` | 250 | 0 | 0 | 0.00 |
| `R3_GROUNDED` TIER_S | 2000 | 4000 | 800 | 0.01 |
| `R3_GROUNDED` TIER_M | 6000 | 12000 | 2000 | 0.08 |
| `R3_GROUNDED` TIER_L | 20000 | 32000 | 4000 | 0.60 |
| `R4_ACTION` | 10000 | 8000 | 1000 | 0.10 |
| `R3R4_WORKFLOW` | 60000 | 64000 | 8000 | 2.00 |
| `R-CASC` | sum-of-hops | sum-of-hops | sum-of-hops | sum-of-hops |
| `R-PAR` | max-of-shards | sum-of-shards | sum-of-shards | sum-of-shards |
| `R-LOOP` | iterations × per-iter | iterations × per-iter | iterations × per-iter | iterations × per-iter |
| `R-HITL` | waived | — | — | — |
| `R5_FALLBACK` | 500 | 0 | 200 | 0.00 |

### 10.2 Enforcement points

- L3 orchestrator refuses to spawn a node whose remaining budget is already exhausted.
- L2 executor emits a `SLOBreach` event and returns early with the best-partial artifact (never
  blocks forever).
- Per-tenant daily cost caps live in L5 policy plane, not in this contract.

---

## 11. R1B Callout (★ W4 / G13)

R1B Semantic Cache is a **hallucination amplifier** if policy gates are bypassed — a single bad
entry can serve many similar queries. v11's R1B diagram (`R1B Semantic Cache.md`) already has
`R1B.3 POLICY: VALIDATION & SHAPE` and `R1B.4` short-circuit emit — v12 hoists this concern to
the top level:

> **v12 invariant:** R1B.3 hybrid-fusion + policy gates are STRUCTURAL, not optional. A dispatcher
> configuration that disables R1B.3 is invalid and MUST be rejected at config-load.

---

## 12. Route Switch Diagram (updated from v11)

```
 ┌──────────────────────────────────────────────┐                               ┌────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │                               │ L4 STATE / ARCHIVE                 │
 │ - Ingress: L1Plan + 🔵 query_vec             │                               │ - Universal Persistence Boundary   │
 │ - Pre-filter: tenant / ACL / region bounds   │                               │ - Cache Stores (Exact/Sem.)        │
 │ - Enforce expiry / freshness requirements    │                               │ - Canonical raw chunks 🟠          │
 │ - Fast Fail: Reject invalid scope early      │                               │ - Dense vector / sparse index 🟠   │
 │ - Score: cacheable / grounded / action /     │                               │ - Knowledge graph & entities 🟢    │
 │   multi-hop / freshness / support / parallel │                               │ - Canonical source lineage         │
 │   / iterative / high-stakes                  │                               │ - Version manifests / schema       │
 │ - Calibrated thresholds (§4)              ★  │                               │ - No direct write path exists      │
 │ - Emit RouteContract (§2) + telemetry (§3)★  │                               └──────────────────┬─────────────────┘
 └──────────────────────┬───────────────────────┘                                                  │
                        │                                                                          │
                        ▼                                                                          │
 ┌──────────────────────────────────────────────┐                                                  │
 │ L0 ROUTE DECISION SWITCH                     │                                                  │
 │ The dispatcher selects ONE terminal or       │                                                  │
 │ orchestrated path based on the contract.     │                                                  │
 │ Cold-start override (§7) may rewrite the  ★  │                                                  │
 │ top pick to a conservative route.            │                                                  │
 └─┬────────────────────────────────────────────┘                                                  │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1A EXACT CACHE                        │◄──────────────────────────────────────────────────┤
   │  │ - Perfect keyed reuse, zero infer.     │                                                   │
   │  │ - Bypass deep pipeline entirely        ├─► [RET] ──► To [5] EXIT EVAL & CONTROL            │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1B SEMANTIC CACHE                     │◄──────────────────────────────────────────────────┤
   │  │ - Hybrid fusion + POLICY GATES ★       │                                                   │
   │  │   (structural, see §11)                │                                                   │
   │  │ - Terminal short-circuit route         ├─► [RET] ──► To [5] EXIT EVAL & CONTROL            │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R5 FALLBACK                            │                                                   │
   │  │ - Safest bound outcome                 │                                                   │
   │  │ - Abstain/clarify, always last entry   ├─► [RET] ──► To [5] EXIT EVAL & CONTROL            │
   │  │   in every fallback_chain              │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R-HITL  HUMAN-GATED ACTION          ★  │                                                   │
   │  │ - For high-stakes / irreversible /     │                                                   │
   │  │   sensitive-data mutations             │                                                   │
   │  │ - Suspends until approver signs off    │                                                   │
   │  │ - Runtime impl: ADR-023 (L5 exit ctrl) ├─► [RET approved] ──► To [5]                       │
   │  │ - execution_form = HUMAN_GATED         ├─► [RET rejected] ──► R5_FALLBACK                  │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R3 SIMPLE GROUNDED READ                │                                                   │
   │  │ - Factual/policy claims require backing│                                                   │
   │  │ - Single-pass grounding, bypasses L3   │                                                   │
   │  │ - cost_tier selected per §5            │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ C0 CONTEXT ENGINE (Ref Desk)           │◄──────────────[ Read ]────────────────────────────┤
   │  │ - C0.1 Plan → C0.6 Rewrite within      │                                                   │
   │  │   route budget (unchanged from v11)    │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      │ [Evidence Contract]                                                    │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ PROMPT ASSEMBLY (unchanged from v11)   │◄──────────────[ Load ]────────────────────────────┘
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 Execute Single Grounded Step ]──────► [RET] ──► To [5]
   │
   │  ┌────────────────────────────────────────┐
   ├──► R4 SINGLE ACTION                       │
   │  │ - Dispatch external action payload     │
   │  │ - If reversibility ambiguous →         │
   │  │   fallback_chain[0] = R-HITL         ★ │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │             [ L2 Execute Single Step ]─────────► [RET] ──► To [5]
   │
   │  ┌────────────────────────────────────────┐
   ├──► R-PAR  PARALLEL FAN-OUT             ★  │
   │  │ Two variants (Anthropic taxonomy):     │
   │  │  (a) SECTIONING: split task into       │
   │  │      independent subtasks, aggregate   │
   │  │  (b) VOTING: N replicas, aggregate by  │
   │  │      majority / threshold              │
   │  │ Use cases:                             │
   │  │  - guardrail fan-out (Anthropic §Par)  │
   │  │  - multi-aspect eval                   │
   │  │  - multi-perspective review            │
   │  │ SLO = max-of-shards latency,           │
   │  │       sum-of-shards cost               │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 Execute N Parallel Steps ──► Aggregator ]──► [RET] ──► To [5]
   │
   │  ┌────────────────────────────────────────┐
   ├──► R-LOOP  EVALUATOR-OPTIMIZER         ★  │
   │  │ Generator → Critic → Refiner cycle     │
   │  │ Exit conditions (whichever first):     │
   │  │  - critic quality ≥                    │
   │  │    r_loop_quality_threshold (§4.2)     │
   │  │  - max_iterations reached (default 3)  │
   │  │  - SLO budget exhausted                │
   │  │ Different from R-CASC:                 │
   │  │  - R-CASC escalates on confidence      │
   │  │  - R-LOOP refines on quality           │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L3 LoopAgent ──► L2 per iteration ]──► [RET] ──► To [5]
   │
   │  ┌────────────────────────────────────────┐
   ├──► R-CASC  CONFIDENCE CASCADE          ★  │
   │  │ TIER_S → TIER_M → TIER_L               │
   │  │ (See §5.2)                             │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 TIER_S ] ──[low conf]──► [ L2 TIER_M ] ──► ...
   │
   │  ┌────────────────────────────────────────┐
   └──► R3R4 MANAGED WORKFLOW                  │
      │ - Multi-hop RAG or workflow action     │
      │ - L3 orchestration required            │
      │ - Only when contract changes between   │
      │   steps (§9.1 single-agent-first)   ★  │
      └───────────────────┬────────────────────┘
                          │
                          ▼
           [ L3 DAG RUNNER → L2 per node → merge → exit ]
             (diagram identical to v11 §A..§D — unchanged)
```

---

## 13. Route Selection Decision Order (normative)

When multiple routes look viable, the dispatcher applies this **fixed order**. First match wins.

1. **Pre-filter fails** (tenant/ACL/region/expiry) → reject with `R5_FALLBACK` + `reason_codes=["ingress_reject"]`.
2. **Classifier confidence < cold_start_conservative_threshold** → §7 Cold-Start Safeguard.
3. **Exact cache hit** (key match, freshness satisfied) → `R1A`.
4. **Semantic cache hit** (after R1B.1→R1B.3 gates) → `R1B`.
5. **High-stakes / irreversible action detected** (ACL flag, side-effect classifier, user-opt-in) → `R-HITL`.
6. **Action request with bounded reversibility** → `R4_ACTION`.
7. **Multi-aspect task benefiting from parallelism** (classifier flag: independent_subtasks ≥ 2) → `R-PAR`.
8. **Qualitative-refinement task** (classifier flag: generator_critic_refiner_applicable) → `R-LOOP`.
9. **Single-step grounded claim** (support target present, single-pass C0 sufficient) → `R3_GROUNDED`.
10. **Ambiguous tier / confidence-varying difficulty** (single-step-but-hard-to-pre-classify) → `R-CASC`.
11. **Otherwise** — multi-hop, cross-step contract change, DAG required → `R3R4_WORKFLOW`.
12. **No viable route** → `R5_FALLBACK`.

---

## 14. Execution Shape Classification (L3 entry — unchanged semantics from v11)

Preserved from v11 §A..§D. Only annotation is that the decision now reads
`RouteContract.execution_form` as its authoritative input rather than re-deciding from the L1 plan.
Diagrams in v11 §A..§D remain valid; see `v11` for the ASCII.

---

## 15. Deferred for Code Layer (not in this doc)

The following are doctrinal in v12 but require implementation work in `agentic_core/L0_routing/`.
Each is a DEFERRED_SCOPE item — track in Wave/Phase Convergence DB, not here:

- Route Contract Python dataclass + HMAC sign/verify helpers.
- Telemetry event emitter wired to L6 (OTEL spans).
- Calibration report generator (weekly, feeds §4 thresholds).
- Loop Guard feedback channel (L6 → L0).
- Default fallback chains as config (YAML under `config/routing/`).
- Classifier surface with cold-start override logic.

These are tracked against this reference doc, not created blindly — the reference IS the contract
the code must satisfy.

---

## 16. Changelog vs v11

| Section | Change | Source gap |
|---|---|---|
| §2 Route Contract Schema | NEW — normative 14-field schema with HMAC and validity rules | G14 |
| §3 Route Telemetry Contract | NEW — RouteTelemetryEvent + RouteOutcomeEvent + analytics obligations | G7 |
| §4 Calibration Discipline | NEW — threshold SSOT + calibration workflow + forbidden patterns | G8 |
| §5 Cost-Tier Cascade + R-CASC | NEW route + cost_tier field | G1, G2 |
| §6 Fallback Chain | NEW — every non-terminal route has ordered chain; R5 always last | G6 |
| §7 Cold-Start Safeguard | NEW — conservative override on low classifier confidence | G9 |
| §8 Loop Guard | NEW — cross-trace efficiency signal + session-level HITL bias | G10 |
| §9 Single-Agent-First + Handoff-vs-Tool | NEW principle section | G11, G12 |
| §10 Route SLO & Budget | NEW — budgets as contract field, per-route defaults table | G15 |
| §11 R1B Callout | NEW — hallucination-amplifier risk hoisted to top level | G13 |
| §12 Diagram | UPDATED — R-HITL, R-PAR, R-LOOP, R-CASC added; ★ markers on new elements | multiple |
| §13 Route Selection Decision Order | NEW — fixed normative order, first match wins | synthesis |
| §14 Execution Shape Classification | Preserved from v11 §A..§D | — |

v11 sections preserved unchanged: pedagogical legend, R1A/R1B/R5/R3/R4/R3R4 core semantics, C0
Context Engine, Prompt Assembly, L3 orchestration (DAG runner, state ledger, context bus, policy
engine, step contract, readiness control, graph state update, completion/exit).
