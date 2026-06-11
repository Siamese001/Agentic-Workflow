---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\qwen-confidence-routing-hardening-d4e7b1.md'
original_relative_path: '_archive\\2026-05\\qwen-confidence-routing-hardening-d4e7b1.md'
source_sha256: 4a2626745040452d42bbf2a24e55e4d196bed55ce39d9b284b4f9e188b639a95
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Qwen Confidence-Routing Hardening — Cursor Agent Fallback + Primary-Path Adoption

**Slug**: `qwen-confidence-routing-hardening-d4e7b1`
**Tier**: T3 (cross-layer L0/L2/L3, multi-file, architecture decision)
**ADG snapshot**: `artifacts/adg/adg_indexed_04252026_0843.sqlite`
**ADG Provenance**: backend=sqlite, snapshot=adg_indexed_04252026_0843.sqlite
**Created**: 2026-04-25
**Owner**: Cursor Agent (auto-execute approved per user "NO STOPPING 1M TOKENS")
**Status**: In progress

## Problem

Three prior waves (`routing-unification-qwen-abe735`, `qwen-adoption-waves-a7f3c2`, `vllm-stack-consolidation-f6e95d`) established:

- L0 SSOT (`model_registry.py`) with TIER_QWEN_LOCAL / TIER_GEMINI_FLASH / TIER_GEMINI_PRO
- L2 `HealingRouter` with confidence-driven tier selection
- L3 `QwenInferenceGateway` singleton
- 32B-AWQ live at `localhost:8000` (max_len 16384)

But the audit at `artifacts/qwen_adoption_audit_20260425.txt` reveals **8 hardening gaps**:

1. `HealingRouter.dispatch_to_executor` has **zero production call sites** — the unified executor seam exists but is unwired.
2. No automatic Qwen→Gemini fallback cascade — a failed Qwen call returns `success=False` and the caller is responsible for retry.
3. No vLLM health preflight — restart windows surface as 30s timeouts.
4. Apps use `AppsQwenGateway` directly for primary execution, **bypassing the confidence-tier routing decision entirely**. Confidence routing is currently *only active in the heal path*.
5. `max_model_len=16384` is a regression vs the 14B 32k context — callers assuming 32k will silently truncate.
6. `_dispatch_gemini` requires externally-provisioned gateway, returns `dry_plan=True` otherwise — LOW tier is non-functional out-of-box.
7. No success-rate telemetry for cost-demotion calibration.
8. Two `_run_async` paths to the same singleton from `LocalVLLMProvider` and `HealingRouter._dispatch_qwen`.

## Objective

Harden the confidence-routing model in L2 and beyond so:

- **MEDIUM tier** (Qwen) automatically falls through to Gemini Flash on Qwen unavailability.
- **LOW tier** (Gemini Flash/Pro) works without external gateway provisioning when a credentials env-var is present.
- **Apps** can opt into confidence-driven primary-path routing via a single `ConfidenceAwareExecutor` entry point.
- **Token budgets** reconcile with the active `max_model_len` (single SSOT in `model_registry.py`).
- **Observability**: every dispatch emits `tier_attempted` + `tier_used` + `fallback_reason` so cost-demotion is calibratable.

Zero breaking changes. All new behavior is additive or env-flag-gated.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| **W1** | W1.1, W1.2, W1.3 | vLLM health probe + Qwen→Flash cascade fallback | ~30k | Todo | `vllm_health_probe.py` exists with 5s TTL; `_dispatch_qwen` falls through to `_dispatch_gemini` Flash on failure; 8 unit tests pass |
| **W2** | W2.1, W2.2 | Token-budget SSOT reconciliation | ~15k | Todo | `MAX_MODEL_LEN` constant in `model_registry.py`; `vllm_token_budget_types` reads from SSOT; targeted compile + tests pass |
| **W3** | W3.1, W3.2, W3.3 | `ConfidenceAwareExecutor` for apps primary path | ~35k | Todo | New L2 module, env-flag-gated; 12 unit tests; one apps_* opt-in wired |
| **W4** | W4.1, W4.2, W4.3 | Test consolidation + ADG regen + commit/push | ~10k | Todo | All new tests green; ADG re-ingested; 4 commits pushed to origin/main |

Total: ~90k tokens.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | `vllm_health_probe.py` | new `agentic_core/L2_execution/healers/vllm_health_probe.py` | TTL cache; bounded HTTP timeout (1.5s); thread-safe | 8k | Todo |
| W1.2 | Cursor Agent fallback in `_dispatch_qwen` | patch `healing_router.py` `_dispatch_qwen` + new helper `_qwen_to_flash_fallback` | preserve existing public contract; structured `fallback_reason` field; opt-out env var `DISABLE_QWEN_FALLBACK` | 12k | Todo |
| W1.3 | Wave 1 unit tests | new `tests/unit/agentic_core/L2_execution/healers/test_qwen_cascade_fallback.py` | cover health-up/down × Qwen-success/fail × fallback-on/off matrix | 10k | Todo |
| W2.1 | `MAX_MODEL_LEN` SSOT | patch `model_registry.py` (add `MAX_MODEL_LEN`, env `VLLM_MAX_MODEL_LEN` default 16384) | additive; matches running 32B server | 4k | Todo |
| W2.2 | Token-budget audit | grep callers of `32768`/`vllm_token_budget_types`; patch hardcoded 32k → SSOT import | many caller sites; only patch where 32k is hardcoded as model_len; preserve other 32k semantics (e.g. cache size) | 11k | Todo |
| W3.1 | `confidence_aware_executor.py` | new `agentic_core/L2_execution/healers/confidence_aware_executor.py` | sync facade; reuses W1 cascade; HIGH=deterministic passthrough; opt-in via `USE_CONFIDENCE_AWARE_EXECUTOR=1` | 18k | Todo |
| W3.2 | Telemetry stamps | extend `RoutingDecision`/dispatch result with `tier_attempted`, `tier_used`, `fallback_reason` | additive fields on existing dataclass; default-empty | 6k | Todo |
| W3.3 | Wave 3 unit tests | new `tests/unit/agentic_core/L2_execution/healers/test_confidence_aware_executor.py` | HIGH/MEDIUM/LOW × success/fail × fallback paths; 12 tests | 11k | Todo |
| W4.1 | Run targeted pytest | `pytest tests/unit/agentic_core/L2_execution/healers/ -q` | must be 100% green | 2k | Todo |
| W4.2 | ADG regen + ingest | `python tools/generate_full_adg.py` + `adg_redis_ingest.py --force` | regen takes ~3 min; verify new modules visible | 3k | Todo |
| W4.3 | 4 commits + push | one commit per wave | preserves rollback granularity | 5k | Todo |

## Gap Register

| ID | Gap | Severity | Phase | Mitigation |
|---|---|---|---|---|
| G1 | `dispatch_to_executor` zero callers | HIGH | W3.1 | `ConfidenceAwareExecutor` exposes single entry point apps can adopt incrementally |
| G2 | No fallback cascade | HIGH | W1.2 | Qwen→Flash automatic with `fallback_reason="qwen_unavailable"` |
| G3 | No health preflight | MEDIUM | W1.1 | 5s TTL cached probe |
| G4 | Apps bypass confidence routing | HIGH | W3.1 | Opt-in env flag; non-breaking |
| G5 | max_model_len mismatch | MEDIUM | W2.1, W2.2 | SSOT in model_registry; audit hardcoded 32k |
| G6 | `_dispatch_gemini` non-functional | HIGH | W1.2 (partial) | Will document explicitly; full fix deferred to follow-up plan (gateway provisioning is its own scope) |
| G7 | No success-rate telemetry | LOW | W3.2 | `tier_attempted/tier_used/fallback_reason` makes calibration possible |
| G8 | Two `_run_async` shims | LOW | (deferred) | Note in code comment; consolidate in follow-up |

## ADG_HOTSPOT_REPORT

Ranked by impact = fan_in × layer_multiplier (L2 healing surfaces have 8-12 callers, ConfidenceScorer is a CENTRAL_DEPENDENCY).

| # | Target file | Layer | Fan-in | Multiplier | Surface | Archetype | Impact |
|---|---|---|---|---|---|---|---|
| 1 | `agentic_core/L2_execution/healers/healing_router.py` | L2 | high (5+ live + 7 apps potential) | 1.0 | Execution + Resilience | ORCHESTRATOR | HIGH — center of W1/W3 |
| 2 | `agentic_core/L2_execution/healers/confidence_scorer.py` | L2 | 8 (governed_scorer, artifact_loader, 5 tests) | 1.0 | Execution + State | CENTRAL_DEPENDENCY | HIGH — fed by ConfidenceScorer |
| 3 | `agentic_core/L0_routing/config/model_registry.py` | L0 | 19+ (apps + L1/L2/L3 + tests) | 2.0 (L0) | State | STATE_NODE | CRITICAL for W2 SSOT |
| 4 | `agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py` | L3 | 8 (L2 healer, evaluation judges, retrieval, ingestion) | 1.75 (L3) | Execution + Security | SAFETY_GATEKEEPER | HIGH — but read-only in this plan |
| 5 | `agentic_core/L2_execution/types/vllm_token_budget_types.py` | L2 | 4 (compose, retrieval, telemetry) | 1.0 | State | STATE_NODE | MEDIUM — W2 audit target |
| 6 | `agentic_core/L2_execution/enforcement/_provider_local_vllm.py` | L2 | 1 (SovereignLLMGateway) | 1.0 | Execution | ORCHESTRATOR | LOW — read-only this plan |

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized views consulted

1. **`mv_graph_reverse_dependency_hotspots`** — confirms `healing_router.py` and `model_registry.py` as the leverage centers.
2. **`mv_hotspot_centrality`** — `model_registry` is the centrality peak for model-id constants (19+ fan-in).
3. **`mv_dependency_cone_risk`** — touching `model_registry` propagates to every layer; W2 keeps it strictly additive (new constant only).
4. **`mv_path_criticality_rollup`** — confirms the heal-path L2→L3 hop already exists; W1 adds a *fallback edge* L2→L2 (HealingRouter._dispatch_qwen → HealingRouter._dispatch_gemini), no new layer crossing.

### Semantic edges exercised

| Edge | Use in this plan |
|---|---|
| `imports` | All cross-module fan-in counts above |
| `flows_to` | `RoutingDecision` → `_dispatch_qwen` → (W1) `_dispatch_gemini` on failure → caller |
| `resolves_callsite` | `get_qwen_inference_gateway` resolved via local import in W1.2 (preserves L2→L3 gravity) |
| `reads_from` | W2 callers read `MAX_MODEL_LEN` from L0 registry (SSOT compliance) |
| `writes_to` | None — strictly additive |
| `emits_side_effect` | W3.2 telemetry stamps emit through existing `_get_default_heal_router_emitter` |

### P-view cross-references

* **`v_p0_apps_direct_infra`** — W1/W3 do NOT introduce new app→infra direct edges. Apps adopting `ConfidenceAwareExecutor` (W3) replace `AppsQwenGateway` import with L2 import (improves layering).
* **`v_p1_mis_layered_infra`** — `ConfidenceAwareExecutor` (L2) → `QwenInferenceGateway` (L3) via local import — same pattern as `_dispatch_qwen` (verified legal in routing-unification plan §6).
* **`v_p2_duplicated_adapters`** — `ConfidenceAwareExecutor` is NOT a duplicate of `HealingRouter`; it is a primary-path facade that *delegates to* `HealingRouter._dispatch_qwen`/`_dispatch_gemini` after assembling a synthetic `RoutingDecision`.
* **`v_p3_isolated_experimental`** — W3 gates new behavior behind env flag; default OFF.

## Rollback

Per operational-gates skill — one commit per wave.

- **W1**: `git revert <sha>` removes health probe + cascade. `_dispatch_qwen` returns to pre-fallback behavior (manual retry).
- **W2**: revert removes `MAX_MODEL_LEN`; affected callers fall back to their inline 32k assumption (regression to current state).
- **W3**: revert removes `ConfidenceAwareExecutor`; apps that opted-in via env flag silently disable (env flag matches no module).
- **W4**: ADG regen is idempotent; commit/push are reversible.

## Constitutional Compliance

| Rule | Status |
|---|---|
| §1 No PowerShell | ✅ All cmds via `subprocess.run(argv, shell=False)` |
| §2 No test skipping | ✅ Adds 20+ new tests; none skipped |
| §3 No agent deletion | ✅ No `*Agent.py` modified |
| §5 ADG before T3 | ✅ Snapshot referenced; audit script in `tools/analysis/` |
| §14 Subprocess timeout | ✅ All HTTP calls have explicit timeout |
| §15 Precise exceptions | ✅ All new code catches specific types; guardian comments only on telemetry best-effort |
| §22 Graph-layer evidence | ✅ Section above |
| §23 ADG canonical invariants | ✅ Hotspot archetypes; surfaces noted; layer multipliers applied |
| §25 MCP serialization | ✅ Direct SQLite reads; no parallel MCP dispatches |

## Non-Goals

- Not consolidating `_run_async` (G8) — defer to a follow-up.
- Not fully implementing `_dispatch_gemini` provisioning (G6) — only documented; LOW-tier real call requires Gemini API key wiring which is its own plan.
- Not modifying any `apps_*` orchestrator in this plan — W3 only adds the new executor; opt-in adoption is a follow-up.
- Not changing `QWEN_DISALLOWED_FAILURE_TYPES` (safety invariant).
- Not modifying ADG extraction visitors.

## References

- `.cursor/plans/routing-unification-qwen-abe735.md` (parent — completed)
- `.cursor/plans/qwen-adoption-waves-a7f3c2.md` (sibling — completed)
- `.cursor/plans/vllm-stack-consolidation-f6e95d.md` (sibling — completed)
- `artifacts/qwen_adoption_audit_20260425.txt` (audit evidence for this plan)
- `docs/architecture/qwen-vllm-topology.md`
