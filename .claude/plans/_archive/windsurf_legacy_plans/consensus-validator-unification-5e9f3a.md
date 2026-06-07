# Consensus Validator Unification — Parent Plan

**Plan ID:** `consensus-validator-unification-5e9f3a`
**Status:** DRAFT (awaiting SR_APPROVAL)
**Tier:** T3 (multi-layer; touches L1 cognition safety and L0 routing SSOT)
**Date:** 2026-04-21
**Parent RCA:** `docs/reports/plans/rca-h4-consensus-validator-juror-set.md`
**Related plans:** `.windsurf/plans/routing-unification-qwen-abe735.md` (parent §9 marks this a non-goal), `.windsurf/plans/routing-followups-7a2c91.md` F3.3

---

## 1. Context

`@c:\Git\Agentic-Workflow\agentic_core\L1_cognition\enforcement\consensus_validator.py` implements a consensus-voting layer for artifact safety validation using **3 jurors** (OpenAI, Anthropic, Gemini Pro) and a **hardcoded `MAJORITY_THRESHOLD = 0.66`** at line 188. This is a separate confidence-threshold surface from the routing SSOT established in `routing-unification-qwen-abe735.md` (Waves 1–6).

The routing-unification parent plan deliberately excluded this module from scope (§9 non-goals) because:

- Consensus validation and healing routing are **semantically distinct concerns**
- Jurors vote on artifact safety; the router picks a model for healing
- Naively merging them would couple safety-check policy to heal-dispatch policy, violating separation of concerns

This plan addresses the remaining question: **how should the consensus threshold and juror set be governed without compromising SoC?**

---

## 2. Problem Statement

Three observable issues remain after Wave 1 (model registry SSOT):

1. **`MAJORITY_THRESHOLD = 0.66`** is a magic number with no documented rationale in code. Its 0.66 value represents 2-of-3 majority voting — mathematically correct for the 3-juror default, but not SSOT-backed. If the juror set changes to 4 or 5, the threshold becomes wrong by construction.

2. **Juror set is hardcoded** at line 213: `[OPENAI_MODEL_ID, ANTHROPIC_MODEL_ID, GEMINI_PRO_MODEL_ID]`. Model IDs come from `model_registry.py` (Wave 1 ✅) but the **choice of which 3** to use is not governed.

3. **OTEL telemetry emission** from `_call_juror` does not participate in the unified `heal_router.v1` span hierarchy (ADR-025). Consensus votes are invisible to the routing analytics pipeline.

---

## 3. Decision Criteria

For any change in this plan, the following invariants must be preserved:

- **SoC preserved**: Consensus voting must NOT couple to `HealingRouter.route()`. Jurors are not healers.
- **Juror-set determinism**: Given a fixed juror list, `judge_artifact()` must produce identical results across runs (deterministic voting).
- **Backward-compat**: 14 existing consumers of `ConsensusEngine.judge_artifact()` must not break.
- **OTEL unification**: Consensus spans should emit under a `consensus.v1.*` hierarchy (NOT `heal_router.v1.*`) — parallel but independent.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|-------------------|
| C1 | C1.1–C1.3 | Move `MAJORITY_THRESHOLD` to `path_constants` SSOT + wire to juror count | 🟢 ~6k | TODO | Threshold is a function of juror count; hardcoded 0.66 deleted |
| C2 | C2.1–C2.2 | Formalize juror set as config + add `CONSENSUS_JURORS` constant | 🟡 ~8k | TODO | Juror set lives in `model_registry.py` with explicit selection rationale in an ADR |
| C3 | C3.1–C3.2 | OTEL span emission under `consensus.v1.*` hierarchy | 🟡 ~8k | TODO | Every `judge_artifact()` call emits a root span + per-juror child spans |
| C4 | C4.1 | ADR + migration guide | 🟢 ~3k | TODO | `docs/architecture/adr/ADR-NNN-consensus-validator-governance.md` |

**Total est: ~25k tokens.** Execution sequence: C1 → C2 → C3 → C4. C1–C2 can run in parallel with C3 (different files).

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| C1.1 | Add `consensus_majority_threshold(juror_count)` to `path_constants.py` | 1 file + test | Must return 0.66 for 3 jurors (backward-compat); strict majority formula for N jurors | 2k | TODO |
| C1.2 | Replace `MAJORITY_THRESHOLD = 0.66` with call to `path_constants.consensus_majority_threshold(len(self.providers))` | `consensus_validator.py` | Threshold becomes dynamic per juror count | 2k | TODO |
| C1.3 | Regression tests: 3-juror=0.66, 4-juror=0.75, 5-juror=0.6 | new `test_consensus_threshold.py` | Formula correctness | 2k | TODO |
| C2.1 | Add `CONSENSUS_JURORS: tuple[str, ...]` to `model_registry.py` | `model_registry.py` | Explicit registration; env-var override supported | 3k | TODO |
| C2.2 | Replace hardcoded juror list in `ConsensusEngine.__init__` with registry import | `consensus_validator.py` | Preserve `providers=` constructor override for caller customization | 5k | TODO |
| C3.1 | Add `L6_observability/consensus_otel.py` emitter (parallel to `heal_router_otel.py`) | 1 new file + 15-test suite | `consensus.v1.judge`, `consensus.v1.juror` span names; attributes: `juror_model`, `verdict`, `reason` | 5k | TODO |
| C3.2 | Wire emitter into `_call_juror` + `judge_artifact` | `consensus_validator.py` | Zero impact on existing callers (additive); error-safe | 3k | TODO |
| C4.1 | Write `ADR-NNN-consensus-validator-governance.md` | 1 new ADR | Document WHY consensus stays L1 and NOT merged with L2 healing; explain 3-juror default | 3k | TODO |

---

## 6. Rollback Checkpoints

| After wave | Rollback trigger | Rollback action |
|------------|-----------------|-----------------|
| C1 | Any consumer of `judge_artifact()` regresses | Revert threshold change; keep formula as deprecated helper |
| C2 | Apps_* consumers pin specific juror IDs that change | Restore hardcoded default list; keep registry entry as opt-in |
| C3 | OTEL span volume causes performance regression in apps_* | Revert C3 commit; no telemetry backfill needed |
| C4 | N/A — ADR is documentation | — |

---

## 7. HITL Decisions Deferred to Execution

1. **C2.1** — Should `CONSENSUS_JURORS` be env-var overridable, or configuration-only? Decision criterion: if any deployment needs to swap jurors without redeploy, env-var; otherwise config-only.
2. **C3.1** — Should `consensus.v1.*` spans cross-link to `heal_router.v1.trace_id` when a heal triggers consensus? Likely **no** (SoC preserved) but decide at implementation.

---

## 8. Non-Goals (explicit)

- NOT merging `ConsensusEngine` into `HealingRouter`
- NOT changing the `OPENAI + ANTHROPIC + GEMINI_PRO` juror composition (default stays; plan only makes it overridable)
- NOT touching the critical-keyword heuristic at line 187 (`CRITICAL_KEYWORDS`)
- NOT adding streaming/async APIs — `judge_artifact` stays sync

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Layer | Fan-in | Archetype | Surfaces | Wave |
|------|------|-------|:------:|-----------|----------|------|
| 1 | `consensus_validator.ConsensusEngine.judge_artifact` | L1 | medium (14 consumers estimated) | SAFETY_GATEKEEPER | Security Surface | C1–C3 |
| 2 | `consensus_validator.MAJORITY_THRESHOLD` | L1 | 1 (self) | STATE_NODE | State Surface | C1 |
| 3 | `consensus_validator._call_juror` | L1 | 1 (self) | ORCHESTRATOR | Execution Surface, Security Surface | C3 |
| 4 | `path_constants.consensus_majority_threshold` (to be created) | L0 | 1 (`consensus_validator`) | CENTRAL_DEPENDENCY | none | C1 |
| 5 | `model_registry.CONSENSUS_JURORS` (to be created) | L0 | 1 (`consensus_validator`) | CENTRAL_DEPENDENCY | none | C2 |

Layer multipliers per `adg-canonical-invariants.md` §6: L1 ×1.0, L5-type safety-gatekeeper role elevates impact on Security Surface.

## ADG_GRAPH_LAYER_EVIDENCE

| MV / Semantic edge / P-view | Application in this plan |
|---|---|
| `mv_hotspot_centrality` | Expected to rank `ConsensusEngine.judge_artifact` as mid-centrality (14 consumers) — targeted fan-in query required during C1.1 execution |
| `mv_exemptions_near_critical_paths` | Verify consensus code sits on safety-critical paths before C3 telemetry changes |
| `mv_graph_reverse_dependency_hotspots` | Enumerate all 14 `judge_artifact` callers for backward-compat checklist |
| semantic edge `flows_to` | Trace how consensus verdicts propagate to caller decision logic (for OTEL span linkage) |
| semantic edge `emits_side_effect` | Identify current `_call_juror` logging/print emissions to migrate to OTEL spans in C3 |
| P-view `v_p1_mis_layered_infra` | Confirm `consensus_validator.py` stays in L1 (no migration to L2/L5) |

---

## 9. Constitutional Compliance Check

| Rule | Status |
|------|--------|
| §1 No PowerShell | N/A — plan document |
| §15 Precise exceptions | C3.2 must catch specific types in OTEL emission error handling |
| §16 Progress bar | N/A — juror voting is fixed-count, not a long loop |
| §17 Memory lifecycle | No new persistent memory entries required |
| §18 No hidden scope expansion | Explicitly bounded to consensus-governance; healer routing untouched |
| §22 ADG graph layer primary | Both mandatory sections present above |
| §23 ADG canonical invariants | Zero-Loss Propagation Pipeline respected — every proposed change has a node/edge/MV citation |

---

## 10. References

- RCA: `docs/reports/plans/rca-h4-consensus-validator-juror-set.md`
- Parent plan: `.windsurf/plans/routing-unification-qwen-abe735.md` §9 (non-goal confirmation)
- Precedent ADR pattern: `docs/architecture/adr/ADR-025-unified-heal-router-otel-schema.md`
- Constitutional rules: `.windsurf/rules/constitutional.md` §22, `.windsurf/rules/adg-canonical-invariants.md`
