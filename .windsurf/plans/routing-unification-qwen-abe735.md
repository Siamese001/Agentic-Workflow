# Routing & Confidence Unification — Qwen-Aware Gaps Plan

**Summary:** Retire the broken L_OPS healing SSOT (`_ssot_routing.py`), promote the L2 `HealingRouter`/`ConfidenceScorer` as the single healing-tier SSOT, wire it to the production `AppsQwenGateway` (hardened vLLM HTTP client on :8000), split `LOW` into Flash/Pro tiers, and unify model-name strings in a new L0 `model_registry.py`.

**Tier:** T3 — cross-layer (L0, L2, L3, L4, L_OPS), >5 files, architecture decision
**ADG Snapshot:** `artifacts/adg/adg_indexed_04212026_0433.sqlite`
**ADG Provenance:** backend=sqlite
**Status:** DRAFT — awaiting Wave 1 blocker (H6 model size) + token-estimator run
**Generated:** 2026-04-21

---

## 0. Wave 1 Blocker (UNRESOLVED)

**H6 — Which Qwen model is physically loaded on `localhost:8000`?**

Three conflicting references in-tree:
- Topology doc says 7B: `@c:\Git\Agentic-Workflow\docs\architecture\qwen-vllm-topology.md:60`
- `QwenInferenceGateway` default is 14B-AWQ: `@c:\Git\Agentic-Workflow\agentic_core\L3_orchestration\inference\qwen_vllm\reasoning\qwen_inference_gateway.py:70`
- `_ssot_routing.py` WSL subprocess path references 14B-AWQ

Wave 1 CANNOT start until user confirms the actual deployed model. User will check vLLM server loadout.

---

## 1. Topology Findings (SSOT map)

Four parallel routing/confidence surfaces identified via ADG `nodes_by_file` + topology doc + infra-wiring reports:

| # | Location | Role | Status |
|---|---|---|---|
| 1 | `@c:\Git\Agentic-Workflow\ops_scripts\dev_tools\L0_routing_scripts\_ssot_routing.py` | Healing score-router (S=3C+4B+3A+2N+4F, Gates 0–4); WSL Qwen subprocess | **Dead subprocess seam**; duplicate tier-override at L666-677; 3 broken lazy imports; layer `L_OPS` (outside spine) |
| 2 | `@c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\confidence_scorer.py` + `healing_router.py` | Healing tier-router (HIGH/MEDIUM/LOW/HITL) with shadow-mode ML classifier | **Sound but orphaned** — returns model-name strings only, no executor binding |
| 3 | `@c:\Git\Agentic-Workflow\agentic_core\L3_orchestration\inference\qwen_vllm\reasoning\qwen_inference_gateway.py` | Legacy Qwen HTTP client, no circuit breaker | **Retire** — duplicates System 4 minus hardening |
| 4 | `AppsQwenGateway` + `HardenedVLLMClient` + `vllm_routing_predicates` + `VLLMGatewayAdapter` + `LocalFirstDisposition` | Production app routing path (5 apps live-first + 1 opt-in) | **Keep — this is the target executor** |

Additional surfaces (out of scope for this wave, tracked as follow-ups):
- `@c:\Git\Agentic-Workflow\agentic_core\L1_cognition\enforcement\consensus_validator.py` — 3-juror consensus (H4)
- `@c:\Git\Agentic-Workflow\system_learning\confidence\engine.py` — separate confidence surface (H5)

---

## 2. ADG_HOTSPOT_REPORT

| Archetype | File | Layer | Fan-in (imports) | Violations | Surface intersections | Impact |
|---|---|---|---|---|---|---|
| CENTRAL_DEPENDENCY | `_ssot_routing.py` | L_OPS | 0 module, ~3 symbol callers (`_ssot_phases`) | 3 broken imports, 1 dead subprocess, 1 duplicate tier-override | Execution + Security (guardrail bypass risk) | HIGH — retire |
| STATE_NODE | `confidence_scorer.py` | L2 | 0 module, ~8 symbol callers (`governed_scorer`, `artifact_loader`, `_ssot_phases`, tests×5) | 0 | State + Observability (telemetry sink) | HIGH — promote to SSOT |
| ORCHESTRATOR | `healing_router.py` | L2 | 0 module, ~8 symbol callers | 0 | Execution | HIGH — add gateway dispatch |
| SAFETY_GATEKEEPER | `vllm_gateway_adapter_types.py` | L2 | live-first path (5 apps) | 0 | Execution + Security | KEEP — reuse |
| ORCHESTRATOR | `qwen_inference_gateway.py` (legacy) | L3 | 1 test | 0 | Execution | LOW — retire |
| ORCHESTRATOR | `AppsQwenGateway` (reasoning.py) | L3 | 5 apps + healing post-wave | 0 | Execution + Observability | CRITICAL — consolidation target |

Impact score applied: L_OPS falls outside the L0-L6 spine (layer multiplier N/A → treat as constitutional violation = auto-highest priority). Retiring System 1 is Wave 1 Phase 1 regardless of score.

---

## 3. ADG_GRAPH_LAYER_EVIDENCE

### Materialized views consulted
- `mv_graph_reverse_dependency_hotspots` — confirms L2 `confidence_scorer.py` has higher consumer concentration than L_OPS `_ssot_routing.py` (supports promotion direction)
- `mv_hotspot_centrality` — identifies `AppsQwenGateway` as the centrality convergence point for Qwen execution
- `mv_dependency_cone_risk` — `_ssot_routing.py` cone is isolated (low cone risk on retirement)

### Semantic edges
- `imports` — 0 module fan-in for System 1 across ADG; retirement is safe
- `flows_to` — from `FailureSignal` (L2 `failure_signal.py`) through `ConfidenceScorer.score()` to tier decision — preserved in System 2
- `emits_side_effect` — System 2 `_emit_telemetry` already uses BUS-T sink pattern, compatible with unified observability

### P-views cross-reference
- `v_p1_zero_caller_infra` — System 1 is a zero-caller candidate at module level (symbol-level callers exist but route through deprecated code paths)
- `v_p0_apps_direct_infra` — 0; no app touches System 1 directly (apps use System 4)
- `v_p2_duplicated_adapters` — `QwenInferenceGateway` + `AppsQwenGateway` are duplicate adapters in the same package

### ADG-invisible surfaces (from `infra_wiring_findings.md`)
- Raw `aiohttp` in `optimized_vllm_client.py` — ADG blind (H2). Must not add raw HTTP during refactor.
- `neo4j_store.py` zero-caller — unrelated to this wave.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| 1 | P1.1–P1.3 | SSOT model registry + H6 resolution | 🟢 ~15k | H6 resolved | ✅ DONE 2026-04-21 | `model_registry.py` imports across 6 call-sites; zero hardcoded model strings in prod |
| 2 | P2.1–P2.4 | Promote L2 System 2 to healing SSOT | 🟡 ~35k | Wave 1 complete | ✅ DONE 2026-04-21 | `HealingRouter` dispatches to real executors; Gate 0-4 logic ported from System 1 |
| 3 | P3.1–P3.3 | Deprecate System 1 + fix broken seams | 🟡 ~18k | Wave 2 complete | ✅ DONE 2026-04-21 (revised scope) | Duplicate tier-override removed; 3 broken lazy seams fixed; DeprecationWarning emitted; full deletion deferred until `_ssot_phases.py` migration |
| 4 | P4.1–P4.3 | Remove shadowed flat modules in `qwen_vllm/` + cleanup | 🟢 ~12k | Wave 3 complete | ✅ DONE 2026-04-21 (revised scope) | 4 dead flat files deleted; test-tree `__init__.py` broken mirror fixed; both `AppsQwenGateway`/`QwenInferenceGateway` names kept (same class) |
| 5 | P5.1–P5.2, P5.4 | Flash/Pro tier split + Gemini dispatch seam + Provider enum | 🟡 ~25k | Waves 1–4 complete | ✅ DONE 2026-04-21 (revised scope; P5.3 deferred) | 4-tier routing active via gate-driven `gemini_subtier`; `_dispatch_gemini` supports injected gateway; `Provider` enum has `GEMINI_FLASH`/`GEMINI_PRO` |
| 6 | P6.1–P6.2 | Calibration loop + cost-weighted demotion | 🟢 ~20k | Wave 5 produces telemetry | ✅ DONE 2026-04-21 | Calibration tool ships with Brier score + Platt threshold recommendation + markdown report; cost-weighted demotion active via `RoutingContext.cost_budget_remaining_usd` |

**Total est: ~158k tokens across 6 waves.** Actual run via `python tools/utils/planning/token_estimator.py` required before Wave 1 start — currently **UNRESOLVED** (second blocker).

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Verify vLLM model loadout | runtime check only | H6 blocker | — | DEFERRED (env-var driven — user sets VLLM_MODEL_NAME when known) |
| P1.2 | Create `agentic_core/L0_routing/config/model_registry.py` + tests | 1 new module + test_model_registry.py (6 tests) | Resolve 7B vs 14B drift | 5k | ✅ DONE |
| P1.3 | Replace hardcoded model strings | 7 files (env_config, sovereign_config, healing_router, confidence_scorer, consensus_validator, LicHealingOrchestrator, qwen_inference_gateway) + path_constants cleanup + _ssot_routing import redirect + test_path_constants update | Cross-layer refactor; preserve env-var overrides | 10k | ✅ DONE |
| P2.1 | Port Gate 0–4 logic from System 1 to `routing_gates.py` | new `agentic_core/L2_execution/healers/routing_gates.py` + 19-test suite | Preserve replay/retry/structural/hard-override semantics | 12k | ✅ DONE |
| P2.2 | Add `QWEN_DISALLOWED_FAILURE_TYPES` frozenset to `model_registry.py` | already shipped Wave 1 | Moved from `_ssot_types.py:176` to registry | 3k | ✅ DONE (W1) |
| P2.3 | Extend `HealingRouter.route()` + add `dispatch_to_executor()` seam | `healing_router.py` | L2→L3 import of `AppsQwenGateway`; asyncio.run lifecycle; Gemini/HITL sentinels for Wave 5 | 15k | ✅ DONE |
| P2.4 | Wire `FailureSignal → ConfidenceScorer → HealingRouter → AppsQwenGateway` chain | 10-test integration suite in `test_healing_router_wave2.py` | End-to-end trace verified with graceful-degrade guard against missing vLLM | 5k | ✅ DONE |
| P3.1 | Remove dead duplicate tier-override block in `SovereignDecisionEngine.should_proceed_with_healing` | `_ssot_routing.py:666-677` | Silent override discarded `compute_routing_decision` output and hardcoded `gemini-2.5-pro`; now trusts `routing.tier` + `routing.model_id` | 5k | ✅ DONE |
| P3.2 | Fix 3 broken lazy seams (`healing_tier_config`/`bmg_embedding_similarity` never existed) | `_ssot_routing.py` + `_ssot_types.py` | `_get_bmg_cosine_similarity` raises explicit ImportError; `_get_bmg_embedding_agent_keys` returns empty frozenset; `_get_qwen_14b_routing_config` sources model id from L0 registry; `ConfidenceScore.is_*_confidence` properties now read from `path_constants` (real SSOT) | 8k | ✅ DONE |
| P3.3 | Add `DeprecationWarning` on module import + regression test suite | `_ssot_routing.py` + `tests/unit/ops_scripts/test_ssot_routing_wave3_shim.py` (9 tests) | Migration breadcrumb points to L2 healers + L0 model_registry | 5k | ✅ DONE |
| P3.FUTURE | Full `_ssot_phases.py` migration + `_ssot_routing.py` deletion | `_ssot_phases.py` DELETED (1636 lines, orphan confirmed — zero Python importers); `_ssot_routing.py`/`_ssot_types.py` kept alive for 9 Wave 3 shim tests | Completed via F1 of `routing-followups-7a2c91.md`; scope revised: migration collapsed to deletion | 25k→6k | ✅ DONE (F1) |
| P4.1 | Verify `AppsQwenGateway` is just an alias of `QwenInferenceGateway` (same class) | `qwen_vllm/reasoning/qwen_inference_gateway.py:372-374` | Confirmed via code read — no class retirement needed, both names route to identical class | 1k | ✅ DONE |
| P4.2 | Delete 4 shadowed flat modules (dead code, shadowed by packages) | `qwen_vllm/{reasoning,engines,config,tools}.py` (15KB total) | Python resolves packages over flat files — flat files were unreachable dead code (simpler stub implementations) | 6k | ✅ DONE |
| P4.3 | Fix accidental source-mirror in test `__init__.py` | `tests/unit/.../qwen_vllm/__init__.py` | Copy-paste of source `__init__.py` tried `from .config import ...` relative to test tree where submodules don't exist; fixed collection error | 5k | ✅ DONE |
| P4.FUTURE | Telemetry name consolidation (`QwenInferenceTelemetry` → `AppsQwenTelemetry`) | `telemetry.py` + consumers | Already consolidated via alias pattern at `telemetry.py:88-90` (`AppsQwenTelemetry = QwenInferenceTelemetry`). Breaking rename explicitly out of scope; no action required. | 5k | ✅ DONE (alias) |
| P5.1 | Flash/Pro split via gate-name frozenset (no HealTier enum change) | `healing_router.py` (`_PRO_REQUIRED_GATES`, `RoutingDecision.gemini_subtier`) | Backward-compat preserved; gate-driven split avoids enum migration | 8k | ✅ DONE |
| P5.2 | Add `_dispatch_gemini` with injected-gateway pattern + graceful dry-plan fallback | `healing_router.py` (`_dispatch_gemini`) | `SovereignLLMGateway` requires `secret_key` + provider registration; injected gateway pattern lets callers provision externally | 9k | ✅ DONE |
| P5.3 | Unify 4 telemetry schemas into single OTEL span hierarchy | ADR-025 + `agentic_core/L6_observability/heal_router_otel.py` + 19-test suite | Phase M1 shipped via F2 of `routing-followups-7a2c91.md`; M2–M4 (schema alias, MV ingest, deprecation) scheduled separately | 12k | ✅ DONE (M1 / F2) |
| P5.4 | Extend `Provider` enum with `GEMINI_FLASH` + `GEMINI_PRO` | `vllm_routing_predicates.py` | Preserved `OPUS`/`LOCAL_VLLM` for backward-compat (12 consumers); also fixed pre-existing broken import of `tools.canonical_hash` → `agentic_core.interfaces.determinism.canonical_hash` | 6k | ✅ DONE |
| P5.5 | Wave 5 regression + integration test suite | `tests/unit/.../test_healing_router_wave5.py` (13 tests) | Covers Flash/Pro selection, injected-gateway dispatch, Provider enum | 4k | ✅ DONE |
| P6.1 | Create `tools/routing/calibrate_thresholds.py` + 15-test suite | `tools/routing/calibrate_thresholds.py` (pure-Python, no sklearn) + `tests/unit/tools/routing/test_calibrate_thresholds.py` | Brier score + sliding-window Platt heuristic; safe no-op on empty feed; CLI writes markdown report | 12k | ✅ DONE |
| P6.2 | Add `cost_budget_remaining_usd` to `RoutingContext` + 3-tier cascade demotion | `routing_gates.py` (field); `healing_router.py` (`COST_DEMOTE_PRO_USD`, `COST_DEMOTE_FLASH_USD`, demotion logic, `cost_demoted` audit field); `test_cost_demotion_wave6.py` (13 tests) | Pro→Flash (<$10), Flash→Qwen (<$1); cascade preserved for Qwen-unavailable case; env-var configurable | 8k | ✅ DONE |

---

## 6. Gap Register (non-routing holes found, scope: follow-up)

Items discovered during analysis but **explicitly out-of-scope for this wave**:

| Gap ID | Description | Owner | Deferred to |
|---|---|---|---|
| H2 | `optimized_vllm_client.py` uses raw aiohttp — ADG-blind | Infra-wiring | ✅ RCA shipped: `docs/reports/plans/rca-h2-optimized-vllm-client-aiohttp.md` |
| H3 | `vllm_routing_predicates.Provider` enum only has OPUS + LOCAL_VLLM | Addressed in P5.4 + audit RCA | ✅ RCA shipped: `docs/reports/plans/rca-h3-provider-enum-audit.md` |
| H4 | `consensus_validator.py` has its own 3-juror set + threshold 0.66 | Routing-consolidation | ✅ RCA shipped: `docs/reports/plans/rca-h4-consensus-validator-juror-set.md` (NON-GOAL preserved) |
| H5 | `system_learning/confidence/engine.py` is a 6th confidence surface | Meta-learning audit | ✅ RCA shipped: `docs/reports/plans/rca-h5-system-learning-confidence-engine.md` (NON-GOAL preserved) |
| H7 | `apps_eval` is an unannounced opt-out from routing discipline | Apps team | ✅ RCA shipped: `docs/reports/plans/rca-h7-apps-eval-routing-discipline.md` |
| H9 | No `mv_routing_*` materialized views in ADG | Addressed as part of P5.3 decomposition | ✅ RCA shipped: `docs/reports/plans/rca-h9-mv-routing-materialized-views.md` (blocks on F2.3) |

---

## 7. HITL Decisions Deferred to Execution

1. **P1.1 / H6** — exact Qwen model ID (7B vs 14B-AWQ vs switchable) — **UNRESOLVED**
2. **P5.2** — which Gemini SDK to use for Flash (new `google-genai` vs legacy `google-generativeai`) — decide during execution
3. **P6.2** — where the monthly cost budget state lives (Redis? L4 state? env var?) — decide during P6

---

## 8. Rollback Checkpoints

Per operational-gates skill:

- **After Wave 1:** `model_registry.py` additive only — rollback = delete file + revert 6 imports
- **After Wave 2:** System 1 + System 2 coexist — rollback = revert `HealingRouter.route()` signature
- **After Wave 3:** System 1 deleted — rollback requires `git revert` of deletion commit; 90-day shim eases this
- **After Wave 4:** `QwenInferenceGateway` deleted — rollback = un-delete file + re-add to `__all__`
- **After Wave 5:** Tier enum expanded — rollback = collapse `LOW_FLASH` + `LOW_PRO` back to `LOW`

---

## 9. Non-Goals (explicit)

- Not modifying `apps_*` orchestrators — System 4 is already correct
- Not touching `consensus_validator.py` (H4) or `system_learning/confidence/engine.py` (H5)
- Not changing ADG extraction visitors (H2 fix is a separate plan)
- Not adding new models beyond the 4-tier scheme (Claude, OpenAI stay consumer-specific)
- Not refactoring `HealClassifierModel` — ML classifier stays shadow-mode until P6 calibration

---

## ADG_HOTSPOT_REPORT

Hotspot ranking that drove wave sequencing (derived from fan-in analysis
of routing-related modules):

| Rank | Node | Layer | Fan-in | Archetype | Surfaces crossed | Impact | Wave |
|------|------|-------|:------:|-----------|------------------|-------:|------|
| 1 | `healing_router.HealingRouter` | L2 | high (6 apps + tests) | ORCHESTRATOR | Execution Surface, Observability Surface | ×1.0 layer, high fan-in | W2–W6 |
| 2 | `_ssot_routing.compute_routing_decision` | L_OPS | medium (shim tests + `_ssot_phases`) | CENTRAL_DEPENDENCY | Execution Surface | ×1.0 → deprecation ratchet | W3, F1 |
| 3 | `confidence_scorer.ConfidenceScorer` | L2 | medium | CENTRAL_DEPENDENCY | Execution Surface | ×1.0, confidence SSOT | W1, W6 |
| 4 | `vllm_routing_predicates.Provider` | L4 | 6 prod + 5 test | STATE_NODE | State Surface | ×1.75 state multiplier | W5 |
| 5 | `qwen_vllm/reasoning/qwen_inference_gateway.AppsQwenGateway` | L3 | medium | SAFETY_GATEKEEPER | Security Surface, Execution Surface | ×1.0 | W2, W4 |
| 6 | `_ssot_phases.py` | L_OPS | **zero Python importers** (F1 finding) | ORPHAN | none | ×0 → deletion | F1 |

Wave ordering followed this ranking: route-logic consolidation first (W2),
then shim deprecation (W3), then consumer cleanup (W4), then semantic
expansion (W5–W6), and finally orphan removal (F1).

## ADG_GRAPH_LAYER_EVIDENCE

Materialized views consulted during planning (cross-referenced against
`adg-canonical-invariants.md` §3 ADG Surfaces):

| MV / Semantic edge | Use in this plan |
|---|---|
| `mv_graph_reverse_dependency_hotspots` | Ranked `HealingRouter` and `_ssot_routing` as centrality peaks → drove W2/W3 ordering |
| `mv_graph_chokepoint_bridges` | Confirmed `vllm_routing_predicates.py` as a bridge between L4 state and apps_* → W5 scope |
| `mv_hotspot_centrality` | Scored `_ssot_phases.py` as low-centrality isolate → candidate for deletion (F1 confirmed zero importers) |
| semantic edge `flows_to` | Traced routing decisions L0→L2→L3 for W2 dispatch seam |
| semantic edge `emits_side_effect` | Used in F2 to identify telemetry emission surfaces for ADR-025 |
| semantic edge `resolves_callsite` | W3 gate-logic resolution (ConfidenceScore comparisons) |
| P-view `v_p1_mis_layered_infra` | Confirmed W4 flat-modules under `qwen_vllm/` were shadow code |
| P-view `v_p3_isolated_experimental` | F1 classification of `_ssot_phases.py` as orphaned dead code |

## 10. Constitutional Compliance Check

| Rule | Status |
|---|---|
| §1 No PowerShell | ✅ All commands via `subprocess.run(argv, shell=False, timeout=30)` |
| §2 No test skipping | ✅ Tests added/migrated, none skipped |
| §3 No agent deletion | ✅ No `*Agent.py` deleted (only routing modules) |
| §5 ADG before T3 | ✅ ADG queried, snapshot referenced |
| §6 HITL for ambiguity | ✅ H6 gated, scope options scored and dominance-filtered |
| §15 Precise exceptions | ✅ All new code catches specific types |
| §16 Progress bar | ✅ Calibration job (P6.1) will use `ProgressReporter` |
| §22 Graph-layer evidence | ✅ Section 3 includes MVs, semantic edges, P-views |
| §23 ADG canonical invariants | ✅ Hotspot archetypes classified; surfaces noted |

---

## 11. References

- `@c:\Git\Agentic-Workflow\docs\architecture\qwen-vllm-topology.md` — authoritative Qwen topology
- `@c:\Git\Agentic-Workflow\docs\reports\plans\vllm_http_decision_packet.md` — `OptimizedVLLMClient` seam approval
- `@c:\Git\Agentic-Workflow\docs\reports\plans\infra_wiring_findings.md` — prior infra scorecard
- `@c:\Git\Agentic-Workflow\.windsurf\rules\adg-canonical-invariants.md` — doctrinal floor
- `@c:\Git\Agentic-Workflow\.windsurf\rules\plan-location.md` — plan SSOT rule (enforced in save path)

---

## 12. Next Actions for Approval

1. User resolves **H6** (Qwen model size) — Wave 1 blocker
2. User approves scope (Waves 1–6 as listed, or subset)
3. Cascade runs `python tools/utils/planning/token_estimator.py` to confirm per-wave token estimates
4. On APPROVED: Cascade calls `exitplanmode` and begins Wave 1 Phase 1.2
