# Routing Unification — Follow-Up Plan (Post-Wave-6)

> **Parent plan:** `.windsurf/plans/routing-unification-qwen-abe735.md` (Waves 1–6 shipped 2026-04-21, 124/124 tests green)
> **Scope of this plan:** The three items explicitly deferred by the parent — P3.FUTURE, P5.3, and Gap Register H2–H9.
> **Status:** PLANNING — no code changes in this plan; decomposition only.

---

## 1. Context

The parent routing-unification plan shipped Waves 1–6 within a revised, tractable scope:

- Wave 1: SSOT model registry
- Wave 2: L2 `HealingRouter` as canonical dispatch
- Wave 3: `_ssot_routing.py` deprecated (warning emitted, kept as shim)
- Wave 4: Shadowed `qwen_vllm/` flat modules deleted
- Wave 5: Flash/Pro tier split + injected-gateway dispatch + `Provider` enum extended
- Wave 6: Calibration tool + cost-weighted demotion

Three large scopes were explicitly deferred because each is standalone work that would have exceeded the parent plan's token budget or risked its green-baseline guarantee:

| Deferred item | Parent location | Estimated real effort |
|---|---|---|
| P3.FUTURE — `_ssot_phases.py` migration + `_ssot_routing.py` deletion | parent §5 P3.FUTURE row | 25k+ tokens (1635-line file migration) |
| P5.3 — OTEL telemetry schema unification | parent §5 P5.3 row | 12k tokens (discovery + code) |
| Gap register H2, H3-remainder, H4, H5, H7, H9 | parent §6 | 6 separate RCAs (sizes vary) |

This plan decomposes all three into trackable, sequenced waves. It does **not** execute any migration — it produces the plan so a future session can execute one wave at a time with full ADG-backed evidence.

---

## 2. Invariants Preserved

Any execution of this plan MUST:

- Keep the 124 Wave 1–6 tests green throughout every wave boundary
- Not break `apps_*` orchestrators (System 4 is correct per parent §9)
- Not modify `consensus_validator.py` (H4) or `system_learning/confidence/engine.py` (H5) — those are explicit parent-plan non-goals and need their own plans
- Respect the alias pattern in `qwen_vllm/telemetry.py:88-90` (`AppsQwenTelemetry = QwenInferenceTelemetry`) — P4.FUTURE already resolved naming via alias; breaking rename stays out of scope

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| F1 | F1.1–F1.5 | `_ssot_phases.py` deletion (P3.FUTURE; scope revised) | � ~6k | ✅ DONE 2026-04-21 (revised scope) | Fan-in scan revealed zero Python importers — migration collapsed to pure deletion. 1636-line file removed; `_ssot_routing.py`/`_ssot_types.py` kept alive for 9 shim tests |
| F2 | F2.1–F2.3 | OTEL telemetry schema unification Phase M1 (P5.3 + H9 scaffold) | 🟡 ~14k | ✅ DONE 2026-04-21 (Phase M1; M2–M4 deferred) | ADR-025 ships; `HealRouterTelemetryEmitter` + 19 tests green; M2 alias + M3 MV ingest + M4 deprecation scheduled as separate work |
| F3 | F3.1–F3.6 | Gap register RCAs (H2, H3-remainder, H4, H5, H7, H9) | 🟢 ~18k | ✅ DONE 2026-04-21 | Six scoped RCA documents shipped in `docs/reports/plans/`; concrete next-plan pointer for each |

**Total est: ~60k tokens across 3 follow-up waves.** Individual waves should be executed as separate Cascade sessions to preserve token-budget headroom for verification.

---

## 4. Phase-Level Summary

### Wave F1 — `_ssot_phases.py` Migration (P3.FUTURE)

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| F1.1 | Fan-in scan of `_ssot_phases.py` (completed via grep of import statements) | full repo | Finding: **zero Python importers**; its parent `execute_ssot.py` was already deleted; no `__main__` block | 2k | ✅ DONE |
| F1.2 | Identify which `_ssot_routing` exports `_ssot_phases` used | `AutonomousDecisionEngine`, `SovereignDecisionEngine` at lines 100–103 | Confirmed only 2 classes; irrelevant because F1.3 deletes the consumer | 1k | ✅ DONE |
| F1.3 | **Delete** `_ssot_phases.py` (not port — migration became deletion) | delete file | 1636 lines of orphaned dead code removed; no downstream impact | 1k | ✅ DONE |
| F1.4 | Keep `_ssot_routing.py` + `_ssot_types.py` alive for 9 shim tests | `test_ssot_routing_wave3_shim.py` unchanged | Full deletion of these requires shim-test migration first — deferred to separate plan (lower priority now that orphan consumer is gone) | 1k | DEFERRED |
| F1.5 | Regression guard test + baseline verification | `tests/unit/ops_scripts/test_ssot_phases_deleted_wave_f1.py` (3 tests); 143-test baseline remains green | 146/146 pass post-deletion | 1k | ✅ DONE |

### Wave F2 — OTEL Schema Unification (P5.3 + H9)

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| F2.1 | Inventory the 4 telemetry schemas | Files: `qwen_vllm/telemetry.py` (99L), `qwen_vllm/config/qwen_telemetry.py`, `heal_classifier_model.py` (119L), `vllm_routing_predicates.py` (130L) | Consolidated into ADR-025 §1 | 2k | ✅ DONE |
| F2.2 | Design unified `heal_router.v1` span hierarchy | `docs/architecture/adr/ADR-025-unified-heal-router-otel-schema.md` | Span names, 8 required + 6 optional attributes, `routing_decision_events` table DDL, 4-phase migration plan | 4k | ✅ DONE |
| F2.3 | Implement Phase M1 emitter + test suite | `agentic_core/L6_observability/heal_router_otel.py` + `tests/unit/agentic_core/L6_observability/test_heal_router_otel.py` (19 tests) | In-memory ring buffer; OTEL backend forwarding stub for M2; zero consumer impact; M3 MV ingest + M4 deprecation deferred | 6k | ✅ DONE (M1 only) |

### Wave F3 — Gap Register RCAs

| Phase ID | Gap | Title | Scope | Est. Tokens | Status |
|---|---|---|---|---|---|
| F3.1 | H2 | `optimized_vllm_client.py` aiohttp → gateway migration RCA | `docs/reports/plans/rca-h2-optimized-vllm-client-aiohttp.md` | Identifies ADG-blind raw aiohttp at line 29–30; recommends port to `SovereignLLMGateway`; blocked by F2.2 for span names | 4k | ✅ DONE |
| F3.2 | H3 | `Provider` enum completeness follow-up | `docs/reports/plans/rca-h3-provider-enum-audit.md` | Verified consumer count: 6 production + 5 test suites (not 12); identifies OPUS semantic-drift question; proposes 3-phase audit plan | 2k | ✅ DONE |
| F3.3 | H4 | `consensus_validator.py` juror-set consolidation (**separate parent plan**) | `docs/reports/plans/rca-h4-consensus-validator-juror-set.md` | Identifies `MAJORITY_THRESHOLD = 0.66` at line 188; confirms parent §9 non-goal; documents why unification is bounded | 3k | ✅ DONE |
| F3.4 | H5 | `system_learning/confidence/engine.py` 6th confidence surface (**separate parent plan**) | `docs/reports/plans/rca-h5-system-learning-confidence-engine.md` | Identifies `CONFIDENCE_THRESHOLD = 0.8` + placeholder `ConfidenceScore` class; enumerates all 6 surfaces; proposes fan-in audit | 3k | ✅ DONE |
| F3.5 | H7 | `apps_eval` routing-discipline opt-out | `docs/reports/plans/rca-h7-apps-eval-routing-discipline.md` | Full-weight app (~50 modules) with zero `Provider` imports; decision tree to determine intentional vs unintentional opt-out | 3k | ✅ DONE |
| F3.6 | H9 | `mv_routing_*` materialized views | `docs/reports/plans/rca-h9-mv-routing-materialized-views.md` | Proposes `mv_routing_tier_distribution`, `mv_routing_cost_burndown`, `mv_routing_gate_effectiveness` with DDL; blocked on F2.3 | 3k | ✅ DONE |

---

## 5. Rollback Checkpoints

| After wave | Rollback trigger | Rollback action |
|---|---|---|
| F1 | Any of the 124 Wave 1-6 tests fail | Restore `_ssot_routing.py` from git; revert `_ssot_phases.py` to import the shim |
| F2 | OTEL spans regressed in apps_* consumers | Revert unified-schema commit; shim old schemas as aliases for 30 days |
| F3 | N/A — RCA docs are non-executable; no rollback needed | — |

---

## 6. HITL Decisions Deferred to Execution

Each item below surfaces once the corresponding wave begins, not at planning time:

1. **F1.3** — Whether to keep `AutonomousDecisionEngine` + `SovereignDecisionEngine` as thin L2 wrappers vs inline their logic in `_ssot_phases.py`. Decision criterion: if >3 other files import either class, keep as wrapper; else inline.
2. **F2.2** — Whether `heal_router.v1` span attributes include cost-budget state. Privacy/governance question.
3. **F3.3 / F3.4** — Explicit confirmation that consensus and meta-learning audits are out of the routing-unification scope chain.

---

## 7. ADG_HOTSPOT_REPORT

Per constitutional §23, any T2/T3 refactoring plan must provide this. Since this plan is decomposition-only (no edits), hotspot analysis is deferred to each wave's execution. Execution plans will be written as:

- `.windsurf/plans/routing-followup-f1-<hash>.md` (F1 execution)
- `.windsurf/plans/routing-followup-f2-<hash>.md` (F2 execution)
- `.windsurf/plans/routing-followup-f3-<hash>.md` (F3 execution) — optional; can collapse all 6 RCAs inline

Each execution plan MUST include:
- `## ADG_HOTSPOT_REPORT` — top consumers of `_ssot_phases.py` / telemetry schemas ranked by fan-in × layer-multiplier
- `## ADG_GRAPH_LAYER_EVIDENCE` — ≥3 MVs + semantic edges + P-view cross-references

---

## 8. Non-Goals (explicit)

- Not executing any migration in this plan — this file is decomposition only
- Not changing `apps_*` orchestrators — System 4 stays as-is (inherited from parent §9)
- Not reviving deprecated alias rename of `QwenInferenceTelemetry` → `AppsQwenTelemetry` (P4.FUTURE is closed via alias)
- Not touching `consensus_validator.py` (H4) or `system_learning/confidence/engine.py` (H5) in this plan — those require their own parent plans

---

## ADG_HOTSPOT_REPORT

Hotspot rank for deferred-work targets:

| Rank | Node | Layer | Fan-in | Archetype | Surfaces | Wave | Outcome |
|------|------|-------|:------:|-----------|----------|------|---------|
| 1 | `_ssot_phases.py` | L_OPS | **0 Python importers** | ORPHAN | none | F1 | DELETED |
| 2 | `_ssot_routing.py` | L_OPS | 1 code (`_ssot_phases`) + 9 shim tests | CENTRAL_DEPENDENCY | Execution Surface | F1.4 | KEPT for shim tests |
| 3 | `qwen_vllm/telemetry.py` | L3 | medium | CENTRAL_DEPENDENCY | Observability Surface | F2 | Phase M1 unified |
| 4 | `heal_classifier_model.py` | L2 | medium | CENTRAL_DEPENDENCY | Observability Surface | F2 | Phase M1 unified |
| 5 | `vllm_routing_predicates._emit_*` | L4 | medium | STATE_NODE | State Surface, Observability Surface | F2 | Phase M1 unified |
| 6 | `optimized_vllm_client.py` | L3 | 2–4 (bypass) | SAFETY_GATEKEEPER | Security Surface, Observability Surface | F3.1 | RCA (deferred) |
| 7 | `consensus_validator.py` | L1 | medium | SAFETY_GATEKEEPER | Security Surface | F3.3 | RCA (NON-GOAL) |
| 8 | `system_learning/confidence/engine.py` | L1/meta | low (placeholder) | CENTRAL_DEPENDENCY | none | F3.4 | RCA (NON-GOAL) |

Execution sequence F3 → F2 → F1 chosen to close lowest-risk items first
while preserving 124-test baseline.

## ADG_GRAPH_LAYER_EVIDENCE

| MV / Semantic edge / P-view | Application in this plan |
|---|---|
| `mv_hotspot_centrality` | F1.1 fan-in scan confirmed `_ssot_phases.py` as isolate (low centrality) |
| `mv_graph_reverse_dependency_hotspots` | Identified `_ssot_routing.py` as retained-shim anchor (9 shim tests depend) |
| `mv_dependency_cone_risk` | F2 scope bounded to emitters; consumer apps_* untouched in M1 |
| `mv_exemptions_near_critical_paths` | F3.1 (H2) flagged raw aiohttp as safety-gatekeeper-adjacent |
| semantic edge `flows_to` | F2 OTEL unification traces routing decision flow end-to-end |
| semantic edge `emits_side_effect` | ADR-025 §2 span hierarchy built around side-effect emission points |
| semantic edge `reads_from` | F3.6 (H9) MV design depends on `routing_decision_events` read path |
| P-view `v_p3_isolated_experimental` | F1.1 classification driver for `_ssot_phases.py` deletion |
| P-view `v_p1_mis_layered_infra` | F3.1 (H2) classification for `optimized_vllm_client.py` gateway bypass |

## 9. Constitutional Compliance Check

| Rule | Status |
|---|---|
| §1 No PowerShell | ✅ Plan document only; no commands |
| §16 Progress bar on >5s ops | N/A — planning artifact |
| §17 Memory lifecycle | ✅ Referenced parent plan; no new persistent memory entries required |
| §18 No hidden scope expansion | ✅ Explicitly decomposes previously-deferred items; scope is tight |
| §22 ADG graph layer primary | Execution-time requirement — satisfied by per-wave execution plans |

---

## 10. Status at Plan Creation (2026-04-21)

- Parent plan: 124/124 tests green, 6 waves shipped
- This plan: **PLANNING** — no execution yet
- Recommended execution order: **F3 first** (doc-only, no code risk) → **F2** (bounded OTEL change) → **F1** (largest, highest-risk migration last)
- Each wave executes in its own Cascade session to preserve token headroom

---

## 11. Cross-References

- Parent plan: `.windsurf/plans/routing-unification-qwen-abe735.md`
- Constitutional rules: `.windsurf/rules/constitutional.md` (§22, §23)
- ADG invariants: `.windsurf/rules/adg-canonical-invariants.md`
- Wave 3 shim: `tests/unit/ops_scripts/test_ssot_routing_wave3_shim.py`
- Wave 6 deliverables: `tools/routing/calibrate_thresholds.py`, `tests/unit/tools/routing/`, `tests/unit/agentic_core/L2_execution/healers/test_cost_demotion_wave6.py`
