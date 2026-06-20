---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\judge-surface-harmonization-b9d3a7.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\judge-surface-harmonization-b9d3a7.md'
source_sha256: 99a6a3a4fdee3bf3edd6a3acd0d5cd9f57bdbe07b35e38dd707f195c609daffd
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Judge Surface Harmonization — Legacy RAG vs Structured Rubric

- **Slug**: `judge-surface-harmonization-b9d3a7`
- **Tier**: T3 (cross-layer architectural consolidation)
- **Status**: Todo — backlog
- **Parent**: `llm-as-judge-hardening-anthropic-e7b1a4` (ADR-031 §Compatibility explicitly defers this)

## Context

The hardening plan ENH5 landed its work on `agentic_core/evaluation/judges/llm_judge.py` — a RAG-style 4-dimension judge (faithfulness, answer_relevancy, context_precision, groundedness). A parallel, more mature structured judge system lives in the same package:

- `agentic_core/evaluation/judges/llm_judges.py` — `judge_gov_001`, `judge_gov_003`, `judge_sec_001` (async, rubric-driven)
- `agentic_core/evaluation/judges/orchestrator.py` — `JudgeOrchestrator` with rubric engine, evidence assembler, verdict store
- `agentic_core/evaluation/judges/types.py` — `JudgeVerdict`, `JudgeReport`, `RubricDefinition`, `ScoringCriterion`, `EvidenceBundle`
- `agentic_core/evaluation/judges/rubrics.json` — declarative rubric bank
- `agentic_core/evaluation/judges/provider_registry.py`, `verdict_store.py`

And a third surface lives outside the package:

- `system_learning/confidence/llm_judge.py` — confidence-engine judge

Three surfaces, three rubric formats, three verdict shapes. ADR-031 explicitly called this out:

> *"Existing structured-judge system (`llm_judges.py`, `orchestrator.py`, `types.py`) is untouched by this ADR; the hardening applies to the RAG-style `llm_judge.py` harness. A follow-up plan will harmonise the two surfaces."*

This plan is that follow-up.

## Goal

Reduce the three parallel judge surfaces to **one unified judge architecture**, preserving both the structured per-rubric P0-ish feature set and the newly hardened Anthropic-aligned per-dim RAG evaluation.

## Scope

| In Scope | Out of Scope |
|---|---|
| Unified `JudgeProvider` → `JudgeVerdict` pipeline covering both RAG and governance rubrics | New rubric authoring |
| Single `rubrics.yaml` SSOT (replacing both the old `rubrics.json` and the new `config/judges/rubrics.yaml`) | Trajectory / full-run evals (that is ENH4 MoE + future) |
| Unified scorecard aggregating pointwise, pairwise, reference-based, consensus, and per-rubric verdicts | Removing any backward-compat public symbols in one step |
| Deprecation path for `system_learning/confidence/llm_judge.py` → consumes unified judges | |
| `JudgeScore` (RAG shape) and `JudgeVerdict` (structured shape) converge into one type with both a pointwise and rubric view | |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH6.1 | ADG audit + surface map + consumer inventory | 3000 | Todo | `docs/reports/plans/judge-surfaces-audit.md` with consumer → surface matrix |
| W2 | ENH6.2 | Design unified type + rubric SSOT | 4000 | Todo | ADR draft with `JudgeResult` superset type + migration mapping; rubrics.yaml v2 schema |
| W3 | ENH6.3 | Implement unified judge API adapters (keep existing imports working) | 3000 | Todo | Both old and new API paths hit the unified backend; tests pass on both import roots |
| W4 | ENH6.4 | Migrate `system_learning/confidence/llm_judge.py` to unified API | 2000 | Todo | Confidence engine consumes unified judge; deprecation warning on old path |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH6.1 | Surface audit | `agentic_core/evaluation/judges/**`, `system_learning/confidence/**` | Three verdict shapes, three rubric formats | 3000 | Todo |
| ENH6.2 | Unified type + SSOT | `agentic_core/evaluation/judges/types.py`, `config/judges/rubrics.yaml` | Type convergence must preserve immutability + digest stability | 4000 | Todo |
| ENH6.3 | Adapters | `agentic_core/evaluation/judges/` | Backward compat across ~6 public symbols | 3000 | Todo |
| ENH6.4 | Confidence-engine migration | `system_learning/confidence/` | Downstream meta-learning ties | 2000 | Todo |

## Dependencies

- **ENH5 follow-ups** (`llm-judge-hardening-followups-f2c8e1`) — should land first so migrations migrate to the hardened surface.
- **ADR-031** — defines the RAG-side contract this plan unifies.
- **ADR-028** (eval-sl publisher boundary) — unified pipeline must preserve the L5 → L6 evidence publication boundary.

## Design Decisions for Author-Gate (W2)

1. **Primary type**: keep `JudgeVerdict` (one-dimension-per-verdict) as canonical; wrap pointwise 4-dim `JudgeScore` as a fixed-shape multi-verdict. Alternative: introduce a new `JudgeResult` superset.
2. **Rubric format**: YAML (ENH5's `rubrics.yaml`) vs JSON (existing `rubrics.json`). Recommendation: YAML with JSON-importable schema; retain json loader for back-compat.
3. **Async vs sync**: structured judges are async (`async def judge`), hardened RAG judges are sync (`def score`). Unify under async; provide `asyncio.run`-wrapped sync shim for existing sync consumers.
4. **Rubric-ID vs dimension-name**: structured uses `GOV-001`, RAG uses `faithfulness`. Proposal: namespaced rubric_id (`rag.faithfulness`, `governance.gov_001`).

## Non-Goals

- Removing any existing public symbol in one landing; migrations run with deprecation warnings for at least one release cycle.
- Rewriting rubric content; only format/type harmonization.

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH6.1)

- MVs: `mv_hotspot_centrality`, `mv_graph_chokepoint_bridges`
- Semantic edges: `calls`, `flows_to`
- P-views: L5 safety P-views; L1 cognition P-views (for confidence-engine consumer)
