# apps_rg Engine Consolidation Candidates (W5 audit-only)

Snapshot: `adg_indexed_04292026_1606.sqlite`
Engine files scanned: **47**

## How candidates were ranked

- For every engine file, the import-target set was extracted from the static ADG (`relation_type='imports'`).
- For every pair of engines, Jaccard similarity of their import-target sets was computed.
- Pairs with Jaccard ≥ 0.50 are surfaced as candidates: they share at least half of their downstream dependencies and so likely share most of their cross-cutting concerns.
- This is a structural similarity proxy. It does NOT imply behavioral equivalence; before any actual consolidation, behavioral parity must be verified by reading both engines.

## Candidate pairs (Jaccard ≥ 0.50)

| Rank | Jaccard | Engine A | Engine B | Shared deps | A fan-out | B fan-out |
|---:|---:|---|---|---:|---:|---:|
| 1 | 1.00 | `weight_adjustment_engine.py` | `writing_quality_engine.py` | 2 | 2 | 2 |
| 2 | 1.00 | `user_preferences_engine.py` | `writing_quality_engine.py` | 2 | 2 | 2 |
| 3 | 1.00 | `user_preferences_engine.py` | `weight_adjustment_engine.py` | 2 | 2 | 2 |
| 4 | 1.00 | `template_optimizer_engine.py` | `writing_quality_engine.py` | 2 | 2 | 2 |
| 5 | 1.00 | `template_optimizer_engine.py` | `weight_adjustment_engine.py` | 2 | 2 | 2 |
| 6 | 1.00 | `template_optimizer_engine.py` | `user_preferences_engine.py` | 2 | 2 | 2 |
| 7 | 1.00 | `strategic_planning_engine.py` | `writing_quality_engine.py` | 2 | 2 | 2 |
| 8 | 1.00 | `strategic_planning_engine.py` | `weight_adjustment_engine.py` | 2 | 2 | 2 |
| 9 | 1.00 | `strategic_planning_engine.py` | `user_preferences_engine.py` | 2 | 2 | 2 |
| 10 | 1.00 | `strategic_planning_engine.py` | `template_optimizer_engine.py` | 2 | 2 | 2 |
| 11 | 1.00 | `skill_score_normalizer.py` | `writing_quality_engine.py` | 2 | 2 | 2 |
| 12 | 1.00 | `skill_score_normalizer.py` | `weight_adjustment_engine.py` | 2 | 2 | 2 |
| 13 | 1.00 | `skill_score_normalizer.py` | `user_preferences_engine.py` | 2 | 2 | 2 |
| 14 | 1.00 | `skill_score_normalizer.py` | `template_optimizer_engine.py` | 2 | 2 | 2 |
| 15 | 1.00 | `skill_score_normalizer.py` | `strategic_planning_engine.py` | 2 | 2 | 2 |
| 16 | 1.00 | `skill_ordering_engine.py` | `writing_quality_engine.py` | 2 | 2 | 2 |
| 17 | 1.00 | `skill_ordering_engine.py` | `weight_adjustment_engine.py` | 2 | 2 | 2 |
| 18 | 1.00 | `skill_ordering_engine.py` | `user_preferences_engine.py` | 2 | 2 | 2 |
| 19 | 1.00 | `skill_ordering_engine.py` | `template_optimizer_engine.py` | 2 | 2 | 2 |
| 20 | 1.00 | `skill_ordering_engine.py` | `strategic_planning_engine.py` | 2 | 2 | 2 |

## Top fan-out engine files (complexity proxy)

| Rank | File | Fan-out | Fan-in |
|---:|---|---:|---:|
| 1 | `apps_rg/engines/resume_orchestrator_engine.py` | 11 | 3 |
| 2 | `apps_rg/engines/base_rg_engine.py` | 5 | 44 |
| 3 | `apps_rg/engines/rg_spine_adapter.py` | 4 | 0 |
| 4 | `apps_rg/engines/clerk_extraction_engine.py` | 3 | 1 |
| 5 | `apps_rg/engines/hardened_gemini_executor.py` | 3 | 1 |
| 6 | `apps_rg/engines/void_compliance_engine.py` | 3 | 1 |
| 7 | `apps_rg/engines/achievement_prioritizer_engine.py` | 2 | 0 |
| 8 | `apps_rg/engines/ats_compatibility_engine.py` | 2 | 1 |
| 9 | `apps_rg/engines/bullet_generation_task.py` | 2 | 0 |
| 10 | `apps_rg/engines/cognition_relevance_engine.py` | 2 | 0 |
| 11 | `apps_rg/engines/competency_item.py` | 2 | 0 |
| 12 | `apps_rg/engines/contact_safety_engine.py` | 2 | 0 |
| 13 | `apps_rg/engines/content_optimizer_engine.py` | 2 | 4 |
| 14 | `apps_rg/engines/data_enrichment_engine.py` | 2 | 1 |
| 15 | `apps_rg/engines/dispatch_tools_engine.py` | 2 | 0 |

## Recommendation

This audit-only report identifies the following consolidation-candidate pairs, ranked by import-set similarity. Each pair is a hypothesis — not a directive. Before merging, perform Author-Gate decision per `anti-pattern-author-gate.md`:

1. **`weight_adjustment_engine.py` ↔ `writing_quality_engine.py`** (Jaccard 1.00, 2 shared deps).
2. **`user_preferences_engine.py` ↔ `writing_quality_engine.py`** (Jaccard 1.00, 2 shared deps).
3. **`user_preferences_engine.py` ↔ `weight_adjustment_engine.py`** (Jaccard 1.00, 2 shared deps).
4. **`template_optimizer_engine.py` ↔ `writing_quality_engine.py`** (Jaccard 1.00, 2 shared deps).
5. **`template_optimizer_engine.py` ↔ `weight_adjustment_engine.py`** (Jaccard 1.00, 2 shared deps).

Each candidate consolidation is a separate refactor-class decision. Following constitutional §6, none of the above should be executed silently. Open an ADR per pair, capture the parity-verification evidence, and route through the `architecture_choice` Author-Gate.

## Out of scope for this report

- Behavioral parity verification (requires reading both engine bodies + their tests)
- Actual file deletions or merges (that's a real refactor — needs Author-Gate)
- Ranking by runtime invocation frequency (would require otel_mcp runtime-ADG queries)
- Test-suite impact estimation (would require ADG-test-triage-gate)
