# Meta-Learning Confidence Surface Audit — Parent Plan

**Plan ID:** `meta-learning-confidence-audit-b7c4e1`
**Status:** DRAFT (awaiting SR_APPROVAL)
**Tier:** T3 (cross-subsystem; touches L1/L2 + meta-learning pipeline)
**Date:** 2026-04-21
**Parent RCA:** `docs/reports/plans/rca-h5-system-learning-confidence-engine.md`
**Related plans:** `.windsurf/plans/routing-unification-qwen-abe735.md` (parent §9 marks this a non-goal), `.windsurf/plans/routing-followups-7a2c91.md` F3.4

---

## 1. Context

`@c:\Git\Agentic-Workflow\system_learning\confidence\engine.py:1-20` declares:

```python
CONFIDENCE_THRESHOLD = 0.8

class ConfidenceScore:
    """Placeholder confidence score type for test compatibility."""
    def __init__(self, value=0.0, level="LOW"):
        self.value = value
        self.level = level

def calculate_confidence():
    """Placeholder calculate confidence function for test compatibility."""
    return 0.0
```

The "Placeholder ... for test compatibility" docstrings suggest a shim surface, but grep confirms **2 production consumers**:

- `@c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py`
- `@c:\Git\Agentic-Workflow\system_learning\pipelines\pipeline_factory.py`

Combined with 4 other confidence surfaces enumerated in the H5 RCA, this is the **6th confidence surface** in the repo. Unlike consensus (H4), meta-learning is not a safety-validation concern — it's about **learning from past healing outcomes to improve future policy**.

---

## 2. Problem Statement

Three concerns that prompted this plan:

1. **"Placeholder" symbols have real production callers.** The docstring is misleading — `meta_learning_pipeline.py` and `pipeline_factory.py` actually import from this module. What they import, and whether those imports are load-bearing, needs ADG fan-in analysis.

2. **Unclear relationship with L2 `ConfidenceScorer`.** Is `system_learning/confidence/engine.ConfidenceScore` meant to be an alias? A different semantic type? A historical aggregate vs a real-time score? No ADR explains it.

3. **Constitutional §22 risk.** The H5 RCA identified this as the 6th confidence surface. Every additional surface increases the chance of silent divergence — different thresholds producing different tier decisions across different code paths.

---

## 3. Layering Invariants (Must Preserve)

- **L2 `ConfidenceScorer`** = runtime hot path; produces scores during a single heal attempt.
- **`system_learning/confidence/`** = offline/pipeline analysis; aggregates historical outcomes.
- **NO cross-layer import**: `agentic_core/L2_*` MUST NOT import from `system_learning/`.
- **NO L2 hot-path dependency on meta-learning**: heal decisions are never blocked on pipeline availability.

These invariants are why the parent routing-unification plan deferred this work — naive merge would violate them.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|-------------------|
| M1 | M1.1–M1.2 | ADG fan-in scan + consumer classification | 🟢 ~3k | TODO | For each symbol in `engine.py`, know: who imports it, are they load-bearing, are they test-only |
| M2 | M2.1–M2.3 | Decision: alias vs shim vs independent type | 🟡 ~4k | TODO | ADR written; decision recorded with explicit rationale |
| M3 | M3.1–M3.2 | Implement chosen approach (alias, shim, or rewrite) | 🟡 ~10k | TODO | Consumers migrated; placeholder docstrings removed; type semantics clearly documented |
| M4 | M4.1–M4.2 | Threshold + naming consolidation | 🟡 ~6k | TODO | `CONFIDENCE_THRESHOLD = 0.8` either routed through `path_constants` or documented as explicitly-distinct meta-learning constant |

**Total est: ~23k tokens.** Sequence: M1 → M2 → M3 → M4. Strictly sequential because each wave's output determines the next wave's scope.

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| M1.1 | Run `adg_edge_fanin` on `ConfidenceScore`, `CONFIDENCE_THRESHOLD`, `calculate_confidence` | ADG query (no code changes) | Must use ADG MCP (not grep) per constitutional §22 | 1k | TODO |
| M1.2 | Classify each consumer as: load-bearing / test-only / dead import | notebook-style evidence file in `docs/reports/plans/` | Some imports may be `TYPE_CHECKING`-only | 2k | TODO |
| M2.1 | Write decision ADR `docs/architecture/adr/ADR-NNN-meta-learning-confidence-boundary.md` | 1 new ADR | Must explain WHY 6 surfaces exist and which ones are legitimate | 2k | TODO |
| M2.2 | Decide: (a) alias L2 type, (b) keep as distinct meta-learning type, (c) delete placeholder entirely | ADR §2 | Author-gate decision; criterion: if consumers treat this as real-time score → alias; if aggregate → keep distinct | 1k | TODO |
| M2.3 | Record decision in the ADR with confidence score and alternatives rejected | ADR §3 | Per `author-gate-enforcement.md` | 1k | TODO |
| M3.1 | Implement chosen approach | `system_learning/confidence/engine.py` + 2 consumer files | Consumer-migration diff depends on M2.2 choice | 6k | TODO |
| M3.2 | Remove `"Placeholder ... for test compatibility"` docstrings; add real docs | same files | Naming + docstring hygiene | 4k | TODO |
| M4.1 | Decide threshold governance: SSOT in `path_constants` OR explicit meta-learning local constant | ADR §4 update | If aggregate-semantics confirmed, local constant is correct; else SSOT | 2k | TODO |
| M4.2 | Apply decision; add regression tests | `engine.py` + tests | Threshold drift detection | 4k | TODO |

---

## 6. Rollback Checkpoints

| After wave | Rollback trigger | Rollback action |
|------------|-----------------|-----------------|
| M1 | N/A — read-only analysis | — |
| M2 | N/A — ADR only | — |
| M3 | Pipeline consumers regress (meta_learning_pipeline.py or pipeline_factory.py fail to import) | Revert M3 commit; keep ADR as future work |
| M4 | Threshold change breaks offline analysis | Revert M4 commit |

---

## 7. HITL Decisions Deferred to Execution

1. **M2.2 (author-gate)** — alias vs distinct vs delete. Will be a scored Author-Gate packet at execution time. Criteria: consumer fan-in classification from M1.
2. **M4.1 (author-gate)** — threshold SSOT vs local constant. Criteria: is `CONFIDENCE_THRESHOLD = 0.8` used as a tier boundary (SSOT candidate) or as a meta-learning aggregate cutoff (local constant)?

---

## 8. Non-Goals (explicit)

- NOT merging `system_learning/` into `agentic_core/L2_execution/healers/` — layer boundary preserved
- NOT adding a new cross-layer import seam — if M2.2 picks alias, use a duck-typed protocol, not direct import
- NOT changing the meta_learning_pipeline.py or pipeline_factory.py business logic — only their import lines
- NOT touching the other 5 confidence surfaces (`L2_execution.healers.confidence_scorer`, `_ssot_types`, `calibrate_thresholds`, `heal_classifier`, `consensus_validator`)

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Layer | Fan-in | Archetype | Surfaces | Wave |
|------|------|-------|:------:|-----------|----------|------|
| 1 | `system_learning.confidence.engine.ConfidenceScore` | L-meta | 2 confirmed (pipeline_factory, meta_learning_pipeline) | CENTRAL_DEPENDENCY | none (offline) | M1–M3 |
| 2 | `system_learning.confidence.engine.CONFIDENCE_THRESHOLD` | L-meta | TBD via M1.1 ADG query | STATE_NODE | none (offline) | M4 |
| 3 | `system_learning.confidence.engine.calculate_confidence` | L-meta | TBD via M1.1 ADG query | ORCHESTRATOR | none (offline) | M1–M3 |
| 4 | `agentic_core.L2_execution.healers.confidence_scorer.ConfidenceScore` | L2 | high | CENTRAL_DEPENDENCY | Execution Surface | comparison reference only |
| 5 | `system_learning.pipelines.meta_learning_pipeline` | L-meta | medium | ORCHESTRATOR | none (offline) | M3 |

Per `adg-canonical-invariants.md` §6: `system_learning/` is outside the L0–L6 layer gravity system. Layer multiplier N/A; impact is governance + SoC rather than routing criticality.

## ADG_GRAPH_LAYER_EVIDENCE

| MV / Semantic edge / P-view | Application in this plan |
|---|---|
| `mv_hotspot_centrality` | M1.1 — rank how central the 3 `engine.py` symbols are |
| `mv_graph_reverse_dependency_hotspots` | M1.1 — enumerate ALL fan-in for each symbol (not just the 2 grep matches) |
| `mv_dependency_cone_risk` | M3 — bound blast radius before migration |
| semantic edge `imports` | M1 — primary query primitive |
| semantic edge `flows_to` | M3 — trace how `ConfidenceScore` instances flow through pipelines |
| P-view `v_p3_isolated_experimental` | Expect some of the 3 symbols to land here (placeholder implies experimental) |
| P-view `v_p1_mis_layered_infra` | Detect if any L2 code illegally imports from `system_learning/` (invariant check) |

---

## 9. Constitutional Compliance Check

| Rule | Status |
|------|--------|
| §1 No PowerShell | N/A — plan document |
| §15 Precise exceptions | M3 implementation must catch specific types |
| §16 Progress bar | N/A — fixed-count symbol migration |
| §17 Memory lifecycle | Record M2.2 decision in memory graph as `ArchitectureDecision` after resolution |
| §18 No hidden scope expansion | Explicitly bounded to meta-learning-confidence scope; other 5 surfaces untouched |
| §22 ADG graph layer primary | Both mandatory sections present; M1 explicitly relies on ADG MCP |
| §23 ADG canonical invariants | Layer separation enforced via non-goals §8 |

---

## 10. References

- RCA: `docs/reports/plans/rca-h5-system-learning-confidence-engine.md`
- Parent plan: `.windsurf/plans/routing-unification-qwen-abe735.md` §9 (non-goal confirmation)
- Sibling plan: `.windsurf/plans/consensus-validator-unification-5e9f3a.md` (H4 — separate concern, similar pattern)
- Constitutional rules: `.windsurf/rules/constitutional.md` §22, `.windsurf/rules/adg-canonical-invariants.md`
