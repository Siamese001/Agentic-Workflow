# ADR-046 — Rerank Revival: Cross-Encoder on C0.4

**Status**: Accepted (implemented; amended 2026-04-24 - factory + scorer + late-interaction backend slot)
**Date**: 2026-04-23 (amended 2026-04-24)
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/knowledge/retrieval/senior_librarian_reranker.py`, `agentic_core/knowledge/retrieval/hybrid_recall_stage.py`, `agentic_core/knowledge/retrieval/evidence_contract_builder.py`, new `agentic_core/knowledge/retrieval/cross_encoder_reranker.py`
**Plan**: `.codex/plans/c0-context-assembly-best-practices-b7c3a1.md` (W2)

**Current-state note (2026-06-15):** Implemented by `agentic_core/knowledge/retrieval/reranker_factory.py`, `senior_librarian_reranker.py`, `cross_encoder_reranker.py`, and `bge_reranker_adapter.py`, with reranker factory/cross-encoder tests.

---

## Context

Anthropic's published retrieval numbers assume a two-stage funnel: recall
broadly (~150 candidates) and rerank with a cross-encoder or late-interaction
model down to ~20 before generation. Rerank is the second-largest published
quality lift (after Contextual Retrieval).

Current repo state:

- `agentic_core/knowledge/retrieval/senior_librarian_reranker.py` is present
  but shallow (5.5 KB, heuristic).
- `apps_shared/utils/late_interaction_reranker_util.py` was moved to
  `archives/adg_dead_code/2026-04-23/` — a previously-extant late-interaction
  implementation is now out of the active graph.
- `agentic_core/L1_cognition/reasoning/ml_decision_support/models/c0_reranker.py`
  and `advanced_c0_reranker.py` exist; their integration into the live C0.4
  flow has not been verified and should be audited before revival.

Result: the 150→20 funnel is not meaningfully in effect. We recall broadly
but then hand the prompt assembler a weakly-ordered candidate set.

## Decision

Restore a genuine cross-encoder / late-interaction reranker as the canonical
C0.4 rerank stage.

Normative requirements:

1. A new module `agentic_core/knowledge/retrieval/cross_encoder_reranker.py`
   implements a cross-encoder scoring API (e.g. a BGE-reranker family model
   or equivalent). It replaces the scoring core of
   `senior_librarian_reranker.py`; the "senior librarian" name continues as
   the orchestration class but delegates scoring to the cross-encoder.
2. The archived `late_interaction_reranker_util.py` is reviewed; if its
   core scoring path is sound, it is un-archived into
   `agentic_core/knowledge/retrieval/late_interaction_reranker.py` as a
   second backend (not a competitor — different compute profile).
3. `HybridRecallStage` is parameterized: `recall_k` default **150**,
   `rerank_k` default **20**. Both configurable via `RetrievalPlan`.
4. Rerank emits a score distribution alongside the top-K so the evidence
   contract can propagate calibrated confidence into C0.5.
5. Latency budget: P95 rerank stage ≤ **250 ms** for `recall_k = 150` on the
   calibration corpus. Breach triggers fallback to the heuristic reranker
   with a telemetry event, not a silent downgrade.
6. `replay_key` and `policy_hash` propagate across rerank just as they do
   across recall (`hybrid_recall_stage.py` pattern).

### Amendment (2026-04-24) — Single Factory, Scorer Taxonomy, Late-Interaction Slot

The W1.2 reranker-unification inventory (`docs/reports/plans/reranker-unification-inventory.md`)
found seven reranker-class modules across four packages; only four form the
canonical chain (`reranker_factory` → `SeniorLibrarianReranker` → `CrossEncoderReranker` →
`BgeRerankerAdapter`). Three additional normative requirements are added:

**2a. Single canonical entry point.** All retrieval call sites that need
reranking SHALL invoke
`agentic_core.knowledge.retrieval.reranker_factory.get_reranker()` and
delegate to its return value. Direct construction of
`SeniorLibrarianReranker`, `CrossEncoderReranker`, or any auxiliary
reranker is permitted only inside the factory or its tests. CI gate
`ops_scripts/ci/check_reranker_factory_use.py` enforces this for production
paths. Whitelist: `agentic_core/knowledge/retrieval/__init__.py`,
`agentic_core/knowledge/retrieval/reranker_factory.py`, and any test file
matching `test_*reranker*.py`.

**2b. Auxiliary scorers vs. rerankers.** Modules that emit signals other
than relevance (e.g. `completeness_reranker.py` → renamed
`completeness_scorer.py`) are **scorers**, not rerankers. They feed the
rerank stage as additional features but do not own ordering. The taxonomy
is: one **reranker** (orderer) per query, ≥0 **scorers** (feature emitters).
Tier-A retirement candidates from W1.2 inventory:
- `agentic_core/utils/workflow_engines/reranker.py` — superseded by the canonical chain
- `agentic_core/L1_cognition/reasoning/reranking_engine.py` — superseded by `get_reranker()`

Both retired only after `adg_edge_fanin` confirms zero callers, per the
constitutional 90-day deprecation window.

**2c. Late-interaction backend slot.** ColBERT-style late-interaction is
reinstated as a **second backend** under the canonical chain (parallel to
`BgeRerankerAdapter`, not in series with it). Selection via
`RERANKER=cross_encoder_late`; `cross_encoder` (single backend, BGE) remains
the default opt-in. The late-interaction backend lives at
`agentic_core/knowledge/retrieval/late_interaction_reranker.py` after
un-archive from `archives/adg_dead_code/2026-04-23/apps_shared/utils/late_interaction_reranker_util.py`,
subject to the anti-pattern-author-gate scan called out in the original §Risks.

**Coordination with ADR-056.** Once ADR-056 (BGE-M3 multi-head) lands, the
`cross_encoder_late` backend can consume the ColBERT head from the same
forward pass that produces the dense vectors — eliminating the separate
late-interaction model load. The slot defined here is the integration point.

## Non-Goals

- Training a custom reranker. Off-the-shelf model, possibly domain-tuned
  later.
- Replacing dense or sparse recall. Rerank sits strictly downstream.
- GPU provisioning strategy — rerank runs CPU-first; GPU acceleration is a
  separate operational concern.

## Consequences

**Positive**

- Restores the second-largest published quality lift in the retrieval
  literature.
- Enables Anthropic's documented 150→20 funnel instead of the current
  shallow top-K.
- Confidence distribution fed to C0.5 improves support-score calibration
  and abstain behaviour.

**Negative / costs**

- Adds a model dependency and cold-start cost. Mitigated by `DeferredLoader`
  pattern already used by vector_db and otel_mcp.
- Slight memory footprint increase on the serving host.

**Risks**

- Reranker model drift vs. embedding model. Tracked as a retrieval-drift
  eval axis in W6.1.
- Revived late-interaction code may carry anti-patterns from pre-archive
  era. Pre-revival: run `adg_violations` on the file and apply
  anti-pattern-author-gate if any new violations would land.
- **(Amendment R3) Caller drift.** Existing call sites bypass the factory.
  Mitigation: ADG fan-in audit lands before §2a CI gate is enforced;
  callers migrated incrementally with a 1-release deprecation window on
  direct imports of `SeniorLibrarianReranker` / `CrossEncoderReranker`.

## Alternatives Considered

1. **Keep heuristic reranker.** Concedes the documented quality lift.
2. **Use the LLM itself as reranker (LLM-as-judge over candidates).** Higher
   latency and cost for comparable or worse quality at recall_k = 150.
3. **Colbert-style late-interaction only.** Valid, but the off-the-shelf
   cross-encoder is simpler to wire first; late-interaction is kept as a
   second backend per §2 above.

## References

- Anthropic, *Contextual Retrieval in AI Systems*, §Rerank, 2024-09
- Google Cloud, *Building your own RAG — semantic ranking API*, 2024
- In-repo: `agentic_core/knowledge/retrieval/senior_librarian_reranker.py`
- In-repo archive: `archives/adg_dead_code/2026-04-23/apps_shared/utils/late_interaction_reranker_util.py`
- Plan: `.codex/plans/c0-context-assembly-best-practices-b7c3a1.md`
