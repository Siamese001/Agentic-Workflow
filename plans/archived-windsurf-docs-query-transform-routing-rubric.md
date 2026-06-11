---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\query-transform-routing-rubric.md'
original_relative_path: 'query-transform-routing-rubric.md'
source_sha256: 0d34ff08de5fa72284db06acb3b63c4b93c30670030c801f2bc8904fb8e5a39d
recovered_status: LOST_RECOVERED
last_commit: 'dd048e0b048'
last_commit_date: '2026-04-25 04:48:26 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W3.2 — Query-Transform Routing Rubric

**Plan**: `chromadb-best-in-class-agentic-embeddings-c4a1f8`
**Wave/Phase**: W3.2
**Date**: 2026-04-24
**Status**: Rubric v1 — awaiting W5.1 golden-set validation
**Relates-to**: ADR-058 (query-transforms catalog)
**Tier**: T2 (spec, no code changes)

---

## 1. Purpose

ADR-058 defines **what** the five query transforms do (identity, multi-query, HyDE, step-back, decomposition, self-query) and **how** each one is invoked. This rubric answers: **given an incoming query, which transform fires?**

Per ADR-058 §9, at most one transform per query. The rubric is the arbiter.

## 2. Rubric Axes

Observable query features (no LLM needed to classify):

| Feature | Detector | Values |
|---|---|---|
| `length_tokens` | whitespace-tokenize | int |
| `has_conjunctions` | regex `\b(and|or|plus|also|as well as)\b` | bool |
| `has_metadata_cues` | regex on phrases: "in layer L\d", "in `<dir>`", "since 2026", "only `<artifact_type>`" | bool |
| `has_code_tokens` | regex on `[A-Z][a-zA-Z]+(\.py)?`, `snake_case`, `()` | bool |
| `has_question_word` | leading `what|why|how|when|where|who|which` | bool |
| `is_nl_question` | trailing `?` or leading question word | bool |
| `is_compound` | `has_conjunctions` AND clauses ≥ 2 around each conjunction | bool |
| `is_abstract_why` | leading `why`/`how come` | bool |
| `vocab_divergence_expected` | `is_nl_question` AND `has_code_tokens` | bool |

## 3. Decision Tree (v1, rule-based)

```
ROUTE(query):
  feats = extract_features(query)

  # Step 1: metadata-filtered path wins if unambiguous
  IF feats.has_metadata_cues:
      RETURN self_query
      # rationale: the operator has explicitly narrowed; honor it.
      # Transform also still runs semantic retrieval on the cleaned query.

  # Step 2: compound queries decompose
  IF feats.is_compound AND feats.length_tokens > 20:
      RETURN decomposition
      # rationale: single embedding dilutes when N clauses compete.

  # Step 3: "why/how come"-style abstractions step back
  IF feats.is_abstract_why:
      RETURN step_back
      # rationale: corpus rarely contains the question form; it contains
      # the underlying concept. Retrieve concept-level first.

  # Step 4: NL ⇄ code vocabulary gap → HyDE
  IF feats.vocab_divergence_expected:
      RETURN hyde
      # rationale: NL question embedded directly misses code-token-heavy
      # documents. HyDE generates a code-like hypothetical answer.

  # Step 5: short ambiguous NL queries — multi-query widens safely
  IF feats.is_nl_question AND feats.length_tokens <= 12:
      RETURN multi_query
      # rationale: few words → high paraphrase value.

  # Step 6: default
  RETURN identity
```

All decisions are **deterministic** — no LLM needed to route. The transforms themselves are what use the LLM.

## 4. Worked Examples

| Query | Feature matches | Route | Why |
|---|---|---|---|
| `how does the reranker factory pick the backend?` | `is_nl_question`, `has_code_tokens`, `vocab_divergence_expected` | **hyde** | NL ↔ code vocab |
| `find every guardian exemption in L5 since 2026-04-01` | `has_metadata_cues` (layer + date) | **self_query** | filter: `{layer:"L5", created_after:"2026-04-01"}` |
| `why do MCP calls hang and which server owns the race?` | `is_abstract_why`, `is_compound` | **step_back** (why wins over compound) | decomposition would miss the concept-level "hang race" context |
| `list all rerankers and describe each one's backend and list their callers` | `is_compound`, `length_tokens>20`, three `and` clauses | **decomposition** | 3 sub-queries |
| `what is CRAG?` | `is_nl_question`, `length_tokens<=12` | **multi_query** | short broad question |
| `agentic_core/knowledge/retrieval/reranker_factory.py` | none of the above | **identity** | exact filepath — embed as-is |
| `BGE_MULTI_HEAD env knob` | `has_code_tokens`, short | **identity** | code-token-heavy, no NL gap |

## 5. Conflict Resolution

When multiple features fire, the tree order above is authoritative. Rationale:

- **self_query > all**: metadata cues are explicit operator intent.
- **decomposition > hyde**: compound questions are multi-answer; HyDE generates one hypothetical which biases toward one clause.
- **step_back > decomposition**: `why` queries are concept-hungry even when compound; decomposing "why X fails and causes Y" loses the causal glue.
- **hyde > multi_query**: when NL/code vocab gap is real, paraphrasing in NL vocabulary does not close it.

## 6. Escape Hatches

- `QUERY_TRANSFORM=<name>` env var — operator override, bypasses the rubric.
- `query_transform` field on `RetrievalPlan` — programmatic override from a caller that knows better (e.g. a debug tool that always wants identity).
- Budget breach inside any transform → fallback to identity (per ADR-058 §8).

## 7. Telemetry

OTel span attributes emitted per query:

- `gen_ai.query.transform_route = <name>`         — which branch of the tree fired
- `gen_ai.query.transform_reason = <step_label>`  — which rule matched
- `gen_ai.query.features = "..."`                 — comma-separated feature flags
- `gen_ai.query.fallback = <bool>`                — true if budget-breach fallback to identity

Downstream: the evaluation dashboard (W5.1) plots recall/precision **per route**, which surfaces routes whose recall floor is slipping — the cue that the rubric needs adjustment.

## 8. Evolution Policy

- **v1 (this document)**: rule-based tree. Deterministic. Zero LLM cost to route.
- **v2 (deferred, pending W5.1 evidence)**: lightweight classifier (logistic regression over the same features + labeled outcomes from v1 telemetry).
- **v3 (deferred)**: agentic router per plan §G10 / W6.2 — an LLM picks the route conditioned on the whole conversation, not just the current query.

Advancement gate between versions: v1 → v2 requires 30 days of telemetry with per-route precision/recall delta; v2 → v3 requires v2 to not regress v1 floor by > 2 % on the golden set.

## 9. Backward Compatibility

Callers that don't opt into any transform keep current behaviour: `identity` is the default when the rubric is not invoked. `QUERY_TRANSFORM=identity` reproduces pre-ADR-058 behaviour. Rollback is a single env flip.

## 10. Open Questions (carried to W5.1)

1. Does the rubric's rule ordering hold on the actual golden set, or do we observe measurable wins from reordering step_back vs decomposition? Answered by W5.1 A/B.
2. What is the right budget per route? (Latency: 400 ms? 800 ms? Token: 500? 1000?) Tuned against W5.1 percentile data.
3. Should a second layer of rubric apply per **corpus** (code vs docs vs traces)? Hypothesis: docs benefit more from step-back, code more from HyDE. Tracked for W5.1.

## 11. References

- ADR-058 (Query Transforms Catalog)
- W3.1 acceptance gates per ADR-058 §Validation
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
