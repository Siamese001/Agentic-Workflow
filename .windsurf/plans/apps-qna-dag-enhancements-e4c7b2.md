# apps_qna — DAG Orchestration Enhancements (Routing + Paste-Set)

**Plan ID:** `apps-qna-dag-enhancements-e4c7b2`
**Owner:** apps_qna
**Status:** 🟡 Draft — W1 + W2 landed (W3-W5 pending)
**Created:** 2026-05-02
**Scope tier:** T3 (cross-layer — apps_qna router + spine_adapter + templates + tests)
**Intent:** Evolve `apps_qna` routing from BoW cosine + coarse paste buckets to best-in-class Anthropic/OpenAI 2025 patterns (semantic routing, handoffs with shared memory, retrieve-rerank, graded outcomes, semantic cache) for live ChatGPT 5.5-Thinking Q&A card selection.

## Background

Current DAG (see parent review 2026-05-02):

```
[apps_research + apps_rg + JD + interviewer YAML]
  → [Interview model, frozen]
  → [route_seeding]
      ├─ Thompson bandit (cold-start n=5)
      ├─ BGE-M3 / keyword cosine
      └─ hand-curated fallback
  → [CardPackBuilder] ← AppsQnaPasteBandit (buckets: 8/12/18/25)
  → [22 markdown cards] → ChatGPT 5.5-Thinking Project (runtime)
  → [card 22 Learnings] → bandit.update_outcome(asked ∧ landed)  # Bernoulli
```

**Gaps identified** (10, ranked by impact):

1. Live-triage `SemanticRouter` is stdlib BoW cosine; seeding uses BGE-M3 — two embedding surfaces.
2. No small-LLM intent-classifier fallback when bandit + embedding both abstain.
3. Paste-bandit buckets {8,12,18,25} collapse evidence across heterogeneous paste shapes.
4. No cross-encoder reranker on the 9-route ranking.
5. No semantic cache for repeated rehearsal questions (operator probes same shape 8× across sessions).
6. Panel interviews don't share posterior evidence across interviewers.
7. "Max-context ≤3 cards" rule in card 01 is prose, not model-asserted at runtime.
8. Outcome binding is binary `asked ∧ landed` — loses graded signal from card 22.
9. No eval harness measuring route-classifier paraphrase-robustness.
10. Flywheel → Notion writeback is one-directional; cross-interview learning loop unverified.

**Design anchors:**
- Anthropic — *Building Effective Agents* (routing → specialist; LLM-as-judge at 1-2%)
- Anthropic — *Building Effective AI Agents: Architecture Patterns* eBook
- OpenAI Agents SDK — handoffs with shared memory; mid-run model escalation
- Sealos 2025 blueprint — classifier → vector retrieve w/ rerank → tool executor DAG
- vCache (arXiv 2502.03771) — per-question semantic-cache thresholds beat global

**Constitutional alignment:** §22 (graph-layer evidence), §29 (closed-loop router markers paired with ledger writes), §34 (retrieval budgets), ADR-050 (intelligence-ledger family — `apps_qna_pack_lifecycle`).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Collapse BoW router → unified BGE-M3 path | ~6k | `spine_adapter.classify_section_topic` remains stable; no new dep | **Done (2026-05-02)** | `SemanticRouter.route` and `route_seeding.rank_routes_by_signal` share one embedding surface; all existing tests green; paraphrase pair ("tell me about a time you led architecture" vs "walk me through an architecture decision") lands on same primary route |
| W2 | W2.1, W2.2, W2.3 | Cross-encoder reranker + graded outcome binding | ~12k | `BAAI/bge-reranker-v2-m3` available via spine (`agentic_core.knowledge.retrieval.bge_reranker_adapter`); additive `update_graded` on spine `BetaPosterior` + `NamespaceBandit`, additive `score` kwarg on domain `update_outcome` | **Done (2026-05-02)** | Reranker pass logged as feature in `apps_qna_pack_lifecycle` (`event_kind=rerank_pass`, `mode=cross_encoder\|bi_encoder_passthrough`, `rerank_delta`); `update_outcome(score: float)` accepts 0..1 grade, emits §29 `event=graded_outcome` marker + `route_outcome_graded`/`paste_outcome_graded` ledger rows; Bernoulli path preserved for back-compat; Thompson posterior reflects graded evidence via `alpha += score; beta += (1-score)` |
| W3 | W3.1, W3.2 | Panel-shared namespaces + small-LLM intent-classifier fallback | ~10k | Haiku 4.5 / GPT-5-mini gated by env flag (off by default); panel hash stable across rebuilds | Pending | 3-interviewer panel accumulates shared posterior while per-interviewer specificity preserved; LLM fallback emits `ROUTER_DECISION: layer=L0 router=apps_qna_intent_llm …`; ledger row written |
| W4 | W4.1, W4.2 | Finer paste-budget bucketing + rehearsal semantic cache | ~9k | Bucket function derives from `(panel_size, technical_depth)`; cache writes to pack_lifecycle ledger only, no new store | Pending | Paste-bandit uses `(panel_size, depth) → budget_bucket` fn with ≤8 buckets; `rehearsal_cache` detects same-shape questions across builds; warm-start signal feeds both bandits |
| W5 | W5.1, W5.2 | Route-purity runtime self-check + paraphrase-robustness eval | ~7k | ChatGPT 5.5-Thinking respects appended self-check directive; card 22 grep post-rehearsal extracts assertion | Pending | Card 01 answer-shape tail emits `route=N, cards_loaded=[X,Y]` assertion; `tests/eval_route_robustness.py` perturbs card-21 questions and reports route-stability metric; card 22 Learnings parses the self-check line |

**Total est. tokens:** ~44k across 5 waves, 11 phases.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Unify router on BGE-M3 | `apps_qna/router/semantic_router.py`, `apps_qna/scripts/run_qna.py`, `apps_qna/tests/test_semantic_router.py` | BoW cosine misses paraphrases; two embedding surfaces | ~3k | **Done** |
| W1.2 | Route-registry descriptor parity | `apps_qna/router/semantic_router.py`, `apps_qna/router/route_seeding.py` | `_route_corpus` (BoW) vs `_build_route_descriptor` (NL) drift | ~3k | **Done** |
| W2.1 | Cross-encoder reranker adapter | new `apps_qna/router/reranker.py` | Bi-encoder ceiling on 9-route ranking | ~5k | **Done** |
| W2.2 | Graded outcome binding | `agentic_core/L0_routing/reasoning/namespace_bandit.py` (additive `update_graded`), `apps_qna/router/route_bandit.py`, `apps_qna/router/paste_bandit.py` | Bernoulli collapses 1-5 rehearsal grade; Thompson gradient starved | ~4k | **Done** |
| W2.3 | Reranker wiring in route_seeding | `apps_qna/router/route_seeding.py` (`rerank=True` default, env-gated), new `apps_qna/tests/test_w2_reranker_and_graded.py` | Rerank delta not captured as ledger feature | ~3k | **Done** |
| W3.1 | Panel-shared namespace hashing | `apps_qna/router/route_bandit.py` | 3-interviewer panels don't pool evidence | ~4k | Pending |
| W3.2 | Small-LLM intent-classifier fallback | new `apps_qna/integrations/intent_classifier.py`, `apps_qna/router/route_seeding.py` | Static `_FALLBACK_ROUTE_ORDER` when bandit + embedding abstain | ~6k | Pending |
| W4.1 | Dynamic paste-budget buckets | `apps_qna/router/paste_bandit.py` | Coarse {8,12,18,25} merges heterogeneous paste shapes | ~4k | Pending |
| W4.2 | Rehearsal semantic cache | new `apps_qna/integrations/rehearsal_cache.py`, `apps_qna/integrations/flywheel.py` | Operator rehearses same question 8× with no warm-start signal | ~5k | Pending |
| W5.1 | Route-purity runtime self-check | `apps_qna/templates/01_routing_manifest.md.j2`, `apps_qna/templates/22_learnings.md.j2` | ChatGPT drifts from ≤3-card rule; no model-side assertion | ~3k | Pending |
| W5.2 | Paraphrase-robustness eval harness | new `apps_qna/tests/test_eval_route_robustness.py`, `apps_qna/SLO.md` | No measurement of classifier stability across paraphrases | ~4k | Pending |

## Gap Register

| Gap | Severity | Mitigation Wave |
|-----|----------|-----------------|
| BoW vs BGE-M3 surface drift | Med | W1 |
| No reranker (bi-encoder ceiling) | Med | W2.1 |
| Bernoulli loses graded signal | Med | W2.2 |
| Panel evidence siloed per-interviewer | Low-Med | W3.1 |
| No LLM fallback when both signals abstain | Low-Med | W3.2 |
| Coarse paste buckets | Low | W4.1 |
| No semantic cache for rehearsal | Med | W4.2 |
| Prose-only max-context rule | Low | W5.1 |
| No paraphrase-robustness eval | Med | W5.2 |

## ADG_HOTSPOT_REPORT

| File | Layer | Archetype | Fan-in | Fan-out | Surface | Impact |
|------|-------|-----------|--------|---------|---------|--------|
| `apps_qna/router/route_bandit.py` | apps_qna (app) | ORCHESTRATOR | 3 (seeding, flywheel, tests) | 4 (spine_bandit, spine_adapter, registry, uuid) | Execution + Observability | High — §29 paired emission |
| `apps_qna/router/paste_bandit.py` | apps_qna (app) | ORCHESTRATOR | 2 (builder, tests) | 3 (spine_bandit, spine_adapter) | Execution + Observability | High |
| `apps_qna/router/route_seeding.py` | apps_qna (app) | CENTRAL_DEPENDENCY | 4 (from_research_brief, builder, tests, flywheel) | 3 (spine_adapter, route_bandit, types) | Execution | High |
| `apps_qna/router/semantic_router.py` | apps_qna (app) | STATE_NODE | 2 (cli, tests) | 1 (route_registry) | Execution | Med — BoW-only |
| `apps_qna/integrations/spine_adapter.py` | apps_qna ↔ spine | CENTRAL_DEPENDENCY | 6+ (all router + builder) | spine primitives | Execution + State + Observability | Critical — shared embedding surface |

*Note: `apps_qna` sits above L0_routing as an app-layer consumer of spine primitives. Layer-multiplier heuristics from constitutional §23 apply to spine edges, not to apps_qna itself — impact ranking here reflects app-internal fan-in × graph-edge density.*

## ADG_GRAPH_LAYER_EVIDENCE

**Materialized views consulted (to be re-run before W1 kickoff):**

1. `mv_graph_reverse_dependency_hotspots` — confirm `spine_adapter.classify_section_topic` fan-in count before unifying router path (W1)
2. `mv_graph_chokepoint_bridges` — identify `route_bandit` ↔ `namespace_bandit` bridge edges; ensure W2.2 graded-outcome change doesn't break spine contract
3. `mv_hotspot_centrality` — rank `route_seeding` vs `route_bandit` vs `paste_bandit` by centrality to prioritize W-ordering

**Semantic edges required:**

- `flows_to` — from `route_seeding.seed_likely_questions_from_research` → `LikelyQuestionGroup` emission → `CardPackBuilder.build` (validates W2.3 reranker wiring surface)
- `emits_side_effect` — on `emit_pack_lifecycle_event` calls in both bandits (W2.2 must preserve §29 paired emission invariant)
- `reads_from` / `writes_to` — on `pack_lifecycle` ledger reads in W4.2 `rehearsal_cache` (confirm no write-read cycle within a single build)
- `resolves_callsite` — `classify_section_topic` callsites in `route_seeding` and (new) `semantic_router` (W1 parity check)
- `controls_flow` — cold-start threshold branch in `route_bandit.choose_routes_for_signal` (W3.1 must preserve)

**P-view cross-references:**

- `v_p0_*` — no P0 defects expected in apps_qna routers (confirm pre-W1)
- `v_p1_*` — check for P1s in `spine_adapter` that would block W2.1 reranker wiring
- `v_p2_*` — existing `log_and_swallow` / `broad_exception_catch` at `route_seeding.py:196-198` (already present — not introduced by this plan; W3.2 must match the same guarded-except pattern)
- `v_p3_*` — doc/style items only; address incidentally

## Constitutional §29 Paired-Emission Matrix

Every new router touchpoint must emit `ROUTER_DECISION:` marker + `emit_pack_lifecycle_event` in the same code path. Waves affecting this contract:

| Wave | Router name | layer | event_kind |
|------|-------------|-------|------------|
| W2.2 | `apps_qna_route_bandit` (graded) | L0 | `route_outcome_graded` |
| W2.2 | `apps_qna_paste_bandit` (graded) | L0 | `paste_outcome_graded` |
| W3.2 | `apps_qna_intent_llm` | L0 | `route_select_llm_fallback` |
| W4.2 | `apps_qna_rehearsal_cache` | L6 | `cache_hit` / `cache_miss` |

All must be captured by `post_cascade_router_decision_audit.py`.

## Out of Scope (explicit)

- No runtime LLM call into ChatGPT — pack remains paste-into-Project workflow.
- No governance plane (UWG / L5 / Author-Gate at runtime) — offline builder stays offline.
- No new database / persistent store — all writes land in existing `apps_qna_pack_lifecycle` ledger + `pack_manifest.json`.
- No changes to the 22-card structure, filename convention, or the 6 linter invariants (LINT-1..6) — all card shape is preserved; only routing/ranking surfaces change.
- No API keys or network calls at build time unless W3.2 LLM fallback is explicitly enabled via env flag.

## Dependencies + Prerequisites

- ADG snapshot refresh (`/adg-redis-refresh`) before W1 kickoff.
- Verify `BAAI/bge-reranker-v2-m3` availability in spine vector_db path before W2.1.
- Confirm `NamespaceBandit.update` accepts fractional success weights before W2.2 (if not, W2.2 includes a thin shim).
- All waves assume `apps_qna_pack_lifecycle` ledger remains registered and functional (ADR-050).

## Rollback Posture

Each wave is a **net-add** by design:

- W1 keeps old `SemanticRouter` class signature; internal implementation swap.
- W2.1 new file; W2.2 additive signature (existing Bernoulli path preserved).
- W3.2 new file, env-gated.
- W4.2 new file; no changes to existing `pack_lifecycle` schema (new `event_kind` values only).
- W5.1 append-only to template; W5.2 new test file.

Rollback = revert the wave's commits; no schema migration, no data loss.

## Acceptance for Plan Close

- All 11 phases complete, green.
- `pytest apps_qna/` green.
- `python -m apps_qna lint <pack>` exits 0 on all existing canaries.
- Paraphrase-robustness metric (W5.2) reports ≥ 0.80 route-stability across 20-question perturbation sample.
- `post_cascade_router_decision_audit.py` shows zero §29 emission violations across all new router touchpoints.
- Notion row for this plan updated to 🔵 Completed with on-disk commit SHA referenced.

## References

- Parent review (this session, 2026-05-02) — 10-gap assessment of current DAG
- `apps_qna/README.md` — 22-card anatomy + Rules/Skills metadata
- `apps_qna/TECHNICAL_SPEC.md` — types, builder, linter contract
- `apps_qna/spine_manifest.yaml` — `build_time_compiler` route claim
- `agentic_core/L0_routing/reasoning/namespace_bandit.py` — spine bandit primitive
- ADR-050 — intelligence-ledger family
- Constitutional rules §22, §23, §29, §34
- Anthropic — *Building Effective Agents* (2025)
- OpenAI Agents SDK guide (2025) — handoffs, multi-model runs
- Sealos 2025 AI-application blueprint
- vCache (arXiv 2502.03771v4) — verified semantic prompt caching
