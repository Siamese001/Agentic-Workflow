# ADR-064 — Agentic Retrieval Router: Intent-Driven Strategy Selection

**Status**: Accepted (implemented)
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/L0_routing/`, `agentic_core/L1_cognition/reasoning/`, `agentic_core/knowledge/engine/rag_orchestrator.py`, `config/retrieval/`
**Plan**: `.claude/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W6.2
**Relates-to**: ADR-046, ADR-055, ADR-056, ADR-057, ADR-058, ADR-060, ADR-061, ADR-062, ADR-063 — this is the **integration ADR** that ties them together at query time.

**Current-state note (2026-06-15):** Implemented by `agentic_core/L1_cognition/reasoning/retrieval_router.py`, including intent classes, strategy plans, query-transform/reranker/reflective/dim-tier/hydration routing, override hints, and closed-loop tests.

---

## Context

After ADRs 045–063 land, the retrieval surface offers **dozens of independently-tunable knobs**:

| Axis | Values |
|---|---|
| `RERANKER` | `none`, `heuristic`, `cross_encoder`, `cross_encoder_late` |
| `QUERY_TRANSFORM` | `identity`, `multi_query`, `hyde`, `step_back`, `decomposition`, `self_query` |
| `RETRIEVAL_REFLECTIVE` | `0`, `1` |
| `dim_tier` | `hot-interactive`, `warm-analytics`, `cold-batch`, `tiny-prefilter` |
| `collections` | `code_chunks`, `docs`, `tests_guardrails`, `traces`, `incidents_rca`, ... |
| `hydration_mode` | `none`, `parent`, `sentence_window` |
| `latency_budget_ms` | tier-dependent |

Without a router, callers either:
- Hardcode a permutation that worked once and ages poorly, or
- Expose every knob upward and force the agent to pick — moving the choice problem one layer up without solving it.

ADR-058 §W3.2 routing rubric covers **query transforms only**. This ADR generalizes that rubric across all axes — the agentic router.

The router is also the **calibration sink**: ADR-061's nightly evals and ADR-062's drift telemetry feed back here as routing-weight updates. Without a router there is no place for that feedback to land.

## Decision

Adopt a **two-tier agentic router** at the L0/L1 boundary that maps each query to a `RetrievalPlan` (existing dataclass, extended) using deterministic rules first and learned weights second.

### Normative Requirements

1. **Router contract** — new module `agentic_core/L1_cognition/reasoning/retrieval_router.py`:

   ```python
   class RetrievalRouter:
       def route(
           self,
           query: str,
           caller_hints: RouterHints,        # SLO, allowed_tiers, allowed_collections
           telemetry_snapshot: TelemetrySnapshot,  # latest weights from ADR-061/062
       ) -> RetrievalPlan: ...
   ```

   `RetrievalPlan` (already exists in `agentic_core/knowledge/retrieval/retrieval_plan.py`) gains fields:
   - `query_transform: str`       (slug from ADR-058 catalog)
   - `reranker_mode: str`         (slug from ADR-046 factory)
   - `reflective: bool`           (ADR-060)
   - `dim_tier: str`              (ADR-057)
   - `collections: list[str]`     (which corpora to query)
   - `hydration_mode: str`        (ADR-063)
   - `latency_budget_ms: int`
   - `route_reason: str`          (telemetry; which rule fired)

2. **Tier 1 — deterministic intent classifier** (no LLM):

   The classifier extracts the same observable features documented in ADR-058 §W3.2 (length, conjunctions, metadata cues, code tokens, question words). Maps to one of N **intent classes**:

   | Intent class | Heuristic |
   |---|---|
   | `code_concept` | code tokens + NL question |
   | `code_locator` | filepath-like / `module.symbol` only |
   | `prose_factual` | NL question, ≤ 12 tokens, no compound |
   | `prose_compound` | conjunctions + length > 20 |
   | `prose_abstract_why` | leads with `why`/`how come` |
   | `metadata_filter` | layer/date/artifact_type cues |
   | `trace_lookup` | mentions trace id / span / agent class |
   | `incident_recall` | mentions RCA / incident / outage |
   | `unknown` | none of the above |

3. **Tier 2 — class-to-plan mapping** with telemetry-weighted defaults:

   | Intent class | collections | query_transform | reranker | reflective | dim_tier | hydration |
   |---|---|---|---|:-:|---|---|
   | `code_concept` | `code_chunks` + `docs` | `hyde` | `cross_encoder_late` | `1` | hot | none |
   | `code_locator` | `code_chunks` | `identity` | `cross_encoder` | `0` | hot | none |
   | `prose_factual` | `docs` + `incidents_rca` | `multi_query` | `cross_encoder` | `0` | hot | parent |
   | `prose_compound` | `docs` + `code_chunks` | `decomposition` | `cross_encoder` | `1` | hot | parent |
   | `prose_abstract_why` | `docs` + `incidents_rca` | `step_back` | `cross_encoder` | `1` | hot | parent |
   | `metadata_filter` | as filter dictates | `self_query` | `cross_encoder` | `0` | hot | parent |
   | `trace_lookup` | `traces` | `identity` | `heuristic` | `0` | warm | parent |
   | `incident_recall` | `incidents_rca` + `docs` | `step_back` | `cross_encoder` | `1` | hot | parent |
   | `unknown` | `code_chunks` + `docs` | `identity` | `cross_encoder` | `0` | hot | none |

   These are **defaults**. Telemetry weights (per §6) modulate them.

4. **Caller hints override** — `RouterHints` carries `slo: "interactive"|"background"|"batch"` and optional `allowed_tiers`/`allowed_collections`. The router applies hints **after** mapping and **before** budget enforcement; it never widens beyond the hint.

5. **Latency budget enforcement** — final plan's `latency_budget_ms` is the minimum of the SLO budget and the sum of stage budgets implied by the chosen knobs. If the implied sum exceeds the SLO budget, the router downgrades in this fixed priority order until fit:
   1. Drop reflective loop (reflective: 1 → 0).
   2. Downgrade reranker (`cross_encoder_late` → `cross_encoder` → `heuristic`).
   3. Downgrade dim_tier (`hot` → `warm`).
   4. Drop query transform to `identity`.
   5. Refuse with `RouteUnsatisfiableError` — caller decides whether to expand budget or accept identity-baseline.

   Each downgrade emits a `route_downgraded` OTel event.

6. **Learned weights** — `config/retrieval/router_weights.yaml` (new) holds per-(intent_class, knob) success rates derived from ADR-061's golden-set runs and ADR-062's drift signals:

   ```yaml
   intent_classes:
     code_concept:
       transforms:
         hyde: 0.42       # win rate vs identity on golden set
         step_back: 0.18
         identity: 0.0
       rerankers:
         cross_encoder_late: 0.31
         cross_encoder: 0.22
   ```

   The router selects the highest-weighted knob value within feasibility constraints. Updated weekly by `tools/eval/cron_retrieval_eval.py --update-router-weights` (the cron job from W5.2 gains this side-effect).

7. **Shadow mode + A/B** — `ROUTER_SHADOW=1` runs the router in parallel with the current hardcoded path; the chosen plan is recorded but the hardcoded plan executes. Allows risk-free observation before flipping. `ROUTER_AB=<bucket>` deterministically buckets queries by `query_hash mod 100` for A/B comparison without per-query randomness.

8. **Override** — `RetrievalRouterOverride` dataclass on the call site forces a specific plan, bypassing classification (debug, evaluation, deliberate stress-tests). Always logged.

### Non-Goals

- Replacing the ADR-058 §W3.2 transform-routing rubric. ADR-064 generalizes it; the rubric remains the authoritative description for the transforms axis specifically.
- Replacing the L0 prompt-classifier. That handles **prompt tier** (T0/T1/T2/T3) for the broader Codex harness. ADR-064 handles **retrieval intent** for queries entering the retriever. Different concerns; both deterministic.
- ML training a router. Tier 1 is rules; Tier 2 is YAML-encoded statistics. Genuine learned routing is a separate ADR if/when telemetry justifies it.
- Cross-corpus join planning. Each plan queries N collections in parallel; result fusion is ADR-056's RRF / late-interaction work. Router does not plan joins.

## Consequences

**Positive**
- Single integration point. All other ADRs in the plan compose through it; they don't have to leak knobs to the agent layer.
- Agent code shrinks: `rag_orchestrator.query(query, slo="interactive")` replaces multi-line knob plumbing.
- Telemetry → routing weights closes the eval-drives-behavior loop without manual tuning.
- Shadow + A/B let us land the router without committing to its decisions.

**Negative / costs**
- One more module on the hot path; ~1–3 ms classification latency. Negligible vs retrieval cost.
- `router_weights.yaml` adds a config surface. Mitigated by cron-driven regeneration (no human tuning).
- Downgrade ladder is opinionated. Operator can override per-call; default remains the safe path.

**Risks**
- **R1 — Misrouted queries silently underperform.** Mitigation: shadow mode for first 30 days; A/B comparison ≥ 1000 queries; rollback flag `ROUTER_DISABLE=1`.
- **R2 — Telemetry-driven weights amplify selection bias.** Mitigation: ε-greedy: 5 % of queries always pick a non-default knob to keep counterfactual data flowing; documented in `router_weights.yaml` as `epsilon: 0.05`.
- **R3 — `RouteUnsatisfiableError` surfaces too aggressively.** Mitigation: degrade to identity baseline emits an event but never errors unless `caller_hints.fail_on_unsatisfiable=True`.

## Validation

- `pytest tests/unit/agentic_core/L1_cognition/reasoning/test_retrieval_router.py` — intent classification, downgrade ladder, hint enforcement, override path.
- `pytest tests/integration/test_router_shadow_mode.py` — shadow plan recorded, hardcoded path still executes, no behavior change.
- W5.1 acceptance gate (per ADR-061): `ROUTER=on` Recall@20 ≥ baseline + 3 % across all intent classes after 30 days of shadow + A/B.

Rollback: `ROUTER_DISABLE=1`. Orchestrator falls back to the hardcoded path. Router module stays on disk; it is a no-op when disabled.

## Alternatives Considered

1. **Expose all knobs to the calling agent.** Today's posture; complexity grows linearly per knob. Rejected.
2. **Pure LLM router.** Cost and latency; non-determinism in a hot path that should be reproducible. Reserved for a future ADR if Tier 2's YAML stops fitting.
3. **Use the existing query_router (`agentic_core/L1_cognition/reasoning/query_router.py`).** That module exists for multi-query fusion's collection-selection step; ADR-064 generalizes its responsibility. Implementation may inherit/extend it; semantics expand.
4. **Fold routing into the orchestrator.** Couples concerns; orchestrator should consume a `RetrievalPlan`, not produce one.

## References

- ADR-058 — Query transforms catalog (the rubric this generalizes)
- ADR-061 — Golden set + RAGAS (telemetry source)
- ADR-062 — RAG OTel + drift (drift inputs to weight updates)
- LlamaIndex `RouterQueryEngine` (2023+)
- Anthropic, *How we built our agent* (2024) — Tier-1 deterministic + Tier-2 learned routing pattern
- In-repo: `agentic_core/L1_cognition/reasoning/query_router.py`, `agentic_core/knowledge/retrieval/retrieval_plan.py`
- Parent plan: `.claude/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
