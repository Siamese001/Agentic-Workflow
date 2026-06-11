---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\reranker-unification-inventory.md'
original_relative_path: 'reranker-unification-inventory.md'
source_sha256: 0bdbec1a0ff7b08c3e5f99e9b27d3e776c2c897c0369939c8078f9b1b2ede76e
recovered_status: LOST_RECOVERED
last_commit: 'dd048e0b048'
last_commit_date: '2026-04-25 04:48:26 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W1.2 — Reranker Unification Inventory & Retirement Matrix

**Plan**: `chromadb-best-in-class-agentic-embeddings-c4a1f8`
**Wave/Phase**: W1.2
**Date**: 2026-04-24
**Status**: Inventory complete — recommends ADR-046 amendment
**Relates-to**: ADR-046 Rerank Revival (Proposed)
**Tier**: T2 (analysis, no code changes)

---

## 1. Census

Repo currently contains **7 reranker-class modules** across 4 packages.

| # | Module | Size | Role | Live? | Caller depth |
|---|---|---:|---|:---:|---:|
| 1 | `agentic_core/knowledge/retrieval/senior_librarian_reranker.py` | small | Heuristic stage-1 (relevance × coverage × authority) | ✅ canonical | high — exported by `__init__.py`, used by stage-2 |
| 2 | `agentic_core/knowledge/retrieval/cross_encoder_reranker.py` | small | Two-stage wrapper (heuristic prune → BGE cross-encoder) | ✅ canonical | high — exported, factory target |
| 3 | `agentic_core/knowledge/retrieval/bge_reranker_adapter.py` | small | Lazy BGE adapter (`bge-reranker-v2-m3`) with singleton + fallback | ✅ canonical | medium — wrapped by #2 |
| 4 | `agentic_core/knowledge/retrieval/reranker_factory.py` | small | `get_reranker()` env-driven (`RERANKER` env var) | ✅ canonical | high — single entry point |
| 5 | `agentic_core/utils/workflow_engines/reranker.py` | medium | Workflow-engine local reranker | ⚠️ duplicate-suspect | unclear — pre-canonical-module era |
| 6 | `agentic_core/utils/workflow_engines/completeness_reranker.py` | large | Completeness-axis reranker (separate signal from relevance) | ⚠️ adjacent | high — referenced from `tools/eval/_build_smoke_manifest.py` |
| 7 | `agentic_core/L1_cognition/reasoning/reranking_engine.py` | medium | L1 wrapper engine | ⚠️ duplicate-suspect | unclear |
| 8 | `agentic_core/L1_cognition/reasoning/ml_decision_support/models/c0_reranker.py` | small | ML-decision-support C0 reranker | ⚠️ adjacent | low (debug tools only) |
| 9 | `agentic_core/L1_cognition/reasoning/ml_decision_support/models/advanced_c0_reranker.py` | large | Advanced C0 reranker | ⚠️ adjacent | low (debug tools only) |

(Numbering 1-9 because #1-#4 form the canonical 4-piece chain; #5-#9 are siblings or duplicates.)

## 2. Canonical Chain (per ADR-046)

```
caller
  ↓ get_reranker()
reranker_factory.py            (env: RERANKER=auto|heuristic|cross_encoder|none)
  ↓
SeniorLibrarianReranker        (#1 — stage 1, heuristic prune)
  ↓ pre_filter_top_k
CrossEncoderReranker           (#2 — orchestration)
  ↓
BgeRerankerAdapter             (#3 — bge-reranker-v2-m3 forward)
  → score: list[float] back up the chain
```

Stage 2 is **opt-in** via `RERANKER=cross_encoder`. Default is heuristic-only — matches ADR-046 §Latency budget mitigation.

## 3. Coverage Gaps — Where the Canonical Chain is NOT Used

| Call site | Reranker used | Should use |
|---|---|---|
| `agentic_core/L4_state/utils/client/chroma_client.py::query` | None | Optional `get_reranker()` post-step |
| `agentic_core/knowledge/engine/rag_orchestrator.py` | Direct heuristic call | `get_reranker()` |
| `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py` | Mixed — references at least 2 different rerankers | `get_reranker()` |
| `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` | Pluggable `RerankerFn` callable; never wired to factory by callers | Default to `get_reranker()` when caller passes None |
| `agentic_core/L1_cognition/reasoning/advanced_semantic_retriever.py` | Direct import of #6 + #1 | `get_reranker()` + completeness as secondary signal |

## 4. Retirement / Consolidation Recommendations

### Tier A — Retire (after ADG fan-in confirms zero callers)
- `agentic_core/utils/workflow_engines/reranker.py` (#5) — superseded by canonical chain
- `agentic_core/L1_cognition/reasoning/reranking_engine.py` (#7) — superseded; the L1 surface should call `get_reranker()` directly

### Tier B — Reposition as auxiliary signal (do NOT retire)
- `completeness_reranker.py` (#6) — emits a **different signal** (completeness ≠ relevance). Should become a **scorer** that feeds the canonical reranker's score-fusion weights, not a parallel reranker. Rename → `completeness_scorer.py`, expose `score(candidates, query) -> list[float]`.
- `advanced_c0_reranker.py` (#9) — ML-decision-support code path. Either retire (if low caller-depth confirms) or fold into the BGE adapter as a domain-tuned variant.

### Tier C — Net-new for ADR-046 §2 second backend
- `late_interaction_reranker.py` (un-archive from `archives/adg_dead_code/2026-04-23/apps_shared/utils/late_interaction_reranker_util.py`) — ColBERT-style late interaction. Lives alongside `bge_reranker_adapter.py` as a second backend (different compute profile, different latency band).

## 5. Proposed ADR-046 Amendment

Insert after the existing "Decision" §2:

> **2a. Single canonical entry point.** All retrieval call sites that need reranking SHALL invoke `agentic_core.knowledge.retrieval.reranker_factory.get_reranker()` and delegate to its return value. Direct construction of `SeniorLibrarianReranker`, `CrossEncoderReranker`, or any auxiliary reranker is permitted only inside the factory or its tests. CI gate `check_reranker_factory_use.py` enforces this for production paths.
>
> **2b. Auxiliary scorers vs. rerankers.** Modules that emit signals other than relevance (e.g. `completeness_scorer.py`) are **scorers**, not rerankers. They feed the rerank stage as additional features but do not own ordering. The taxonomy is: one **reranker** (orderer) per query, ≥0 **scorers** (feature emitters).
>
> **2c. Late-interaction backend slot.** ColBERT/late-interaction is reinstated as a **second backend** under the canonical chain (parallel to `BgeRerankerAdapter`). Selection is via `RERANKER=cross_encoder_late` and is opt-in. The cross-encoder backend remains the default when `RERANKER=cross_encoder`.

Add to "Risks":

> **R3 — Caller drift.** Existing call sites bypass the factory. Mitigation: ADG fan-in audit lands before this amendment is accepted; CI gate added in the same PR; callers migrated incrementally with a 1-release deprecation window on direct imports of `SeniorLibrarianReranker` / `CrossEncoderReranker`.

## 6. CI-Gate Sketch

`ops_scripts/ci/check_reranker_factory_use.py`:

- Walk production paths (exclude `tests/`, `tools/eval/`, `tools/debug/`, `archives/`).
- Block any direct `import` of `SeniorLibrarianReranker`, `CrossEncoderReranker`, `BgeRerankerAdapter` outside `agentic_core/knowledge/retrieval/`.
- Block construction (`SeniorLibrarianReranker(`, `CrossEncoderReranker(`) outside the factory module.
- Whitelist: `agentic_core/knowledge/retrieval/__init__.py`, `agentic_core/knowledge/retrieval/reranker_factory.py`, all test files matching `test_*reranker*.py`.

## 7. Dependency on Sibling Work

- ADR-045 wiring evidence audit (W1.1) — independent.
- ADG fan-in queries on each module — required pre-retirement (Tier A) per `agent-deletion-gate.md` constitutional rule. Use `adg_edge_fanin(tgt_id=<module_node>, relation_type="imports")`.

## 8. Acceptance

This inventory document is accepted when:
1. ADG fan-in run completes for #5, #7, #9. Zero-fan-in modules → schedule under `agent-deletion-gate.md` 90-day deprecation window.
2. ADR-046 amendment text accepted by maintainers.
3. CI gate `check_reranker_factory_use.py` lands in `ops_scripts/ci/`.

## 9. References

- ADR-046 Rerank Revival
- Plan `c0-context-assembly-best-practices-b7c3a1` (parent of ADR-046)
- `tests/unit/agentic_core/knowledge/retrieval/test_cross_encoder_reranker.py` (full chain coverage)
- `tools/eval/retrieval_abcd_harness.py` (env-driven A/B/C/D matrix already supports `RERANKER=none|heuristic|cross_encoder`)
- This plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
