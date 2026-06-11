---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-dom-runtime-harness-followup-f2a7b3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-dom-runtime-harness-followup-f2a7b3.md'
source_sha256: 76f638f69c260a9fd104958d9b64b9c336981c982bfb9d9931f20022819d837c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# APPS-DOM Runtime Harness · Follow-Up

**Slug:** `apps-dom-runtime-harness-followup-f2a7b3`
**Status:** Draft
**Parent:** `apps-runtime-domain-enforcement-a7e9d4` (W5-W8 runtime portion)
**Blocks:** Parent plan Definition of Done (trust_level=FAILED until 7 runtime APPS-DOM rows sign off)

## AI Summary

The parent plan's W5-W8 runtime portion is blocked on real Exit-pipeline OTEL evidence for 7 APPS-DOM rows. The W3.P1 config-checking portion + W3.P2 negative-control simulator + W4.P1 policy resolution + W4-followup FEC producers have all landed. Compiler now emits 36 SIGNED_OFF / 9 BLOCKED of 45 total rows; the 9 BLOCKED are all APPS-DOM rows that require live runtime traces the static emitters cannot produce. This plan ships the runtime harness that actually invokes the Exit pipeline per app, captures the OTEL trace, writes it to `artifacts/apps_otel_traces/<app>_cert_trace.json`, and extends the W3.P1 emitter to consume those fixtures.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1 | Runtime harness — invoke Exit pipeline per app + capture OTEL | ~18k | `apps_shared/cert/exit_eval_hook.maybe_invoke_exit_eval` already exists; cert_route_registry flag controls invocation | Draft | 8 trace fixtures on disk with 13 required fields each |
| W2 | W2.P1 | Extend W3.P1 emitter to consume OTEL fixtures | ~10k | Emitter checks in `_check_evaluator_invoked`, `_check_exit_packet_bound`, `_check_x1_consumes_domain`, `_check_x2_aggregate`, `_check_otel_fields_complete`, `_check_l2_artifact_evaluable` | Draft | DOM-002/003/004/005/009/012 flip to PASS |
| W3 | W3.P1 | DOM-006 real runtime negative control | ~12k | Invoke harness with synthesized bad output per app; capture X3=DENY from OTEL | Draft | DOM-006 flips to PASS (replaces simulator proof) |
| W4 | W4.P1 | Verification + compiler run | ~3k | All 12 APPS-DOM rows SIGNED_OFF; trust_level flips to EVIDENCE_PROOF or higher | Draft | compiler signed_off=45 / blocked=0 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Runtime harness | `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (new), `tools/cert/apps_e2e/otel_capture_fixtures/*.json` (generated outputs) | Requires each app's `__main__.py` to reach `maybe_invoke_exit_eval`; apps_exec + apps_research have BLOCKER #5 deferred. Harness may need to invoke at a lower level (direct `run_exit_eval` call against synthetic L2 receipts) if __main__ integration is incomplete. | ~18k | Draft |
| W2.P1 | OTEL-fixture emitter consumption | `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py` (modify) | Change each of 6 OTEL-dependent checker functions to accept `artifacts/apps_otel_traces/<app>_cert_trace.json` as PASS evidence when fixture exists + carries all 13 Phase 2 §9 fields | ~10k | Draft |
| W3.P1 | Real runtime negative-control | `tools/cert/apps_e2e/run_app_negative_control_with_otel.py` (new), fixtures under `artifacts/apps_negative_controls_runtime/<app>_<archetype>_trace.json` | Replaces DOM-006 simulator proof with real X3=DENY captured from Exit invocation on synthesized bad input | ~12k | Draft |
| W4.P1 | Verification + trust_level flip | Run compiler + confirm signed_off=45 / blocked=0 / trust_level≥EVIDENCE_PROOF | `certification/apps_e2e_requirements_source.json` governance for trust_level rules | ~3k | Draft |

## ADG_GRAPH_LAYER_EVIDENCE

- **MV `mv_dependency_cone_risk`** — confirms `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` has bounded downstream cone (L3 only; no L0/L5 crossing)
- **MV `mv_chokepoint_bridges`** — `exit_eval_hook.maybe_invoke_exit_eval` is the chokepoint between cert routes and Exit; no new chokepoints added
- **Semantic edge `flows_to`** — L2 sealed receipt → Exit pipeline → OTEL emit → fixture write (new) → emitter read (new)
- **P-view `v_p2_runtime_harness_ready`** (to auto-discover post-landing) — 0/8 apps currently; target 8/8

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Surfaces | Impact |
|---|---|---|---|---|---|
| `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` | L3 | high (~12) | CENTRAL_DEPENDENCY | Execution, Observability | medium — adds span attrs, no behavior change |
| `apps_shared/cert/exit_eval_hook.py` | apps_shared | 8 | CENTRAL_DEPENDENCY | Execution | low — caller-side only |
| `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py` | tools | 1 (compiler) | ORCHESTRATOR | Observability | low — additive OTEL fixture path |

## Files In Scope

- `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (new)
- `tools/cert/apps_e2e/run_app_negative_control_with_otel.py` (new)
- `tools/cert/apps_e2e/emit_apps_domain_enforcement_assertions.py` (modify — 6 checker functions)
- `artifacts/apps_otel_traces/<app>_cert_trace.json` × 8 (generated; not source)
- `artifacts/apps_negative_controls_runtime/<app>_<archetype>_trace.json` × 24 (generated; not source)

## Non-Goals

- No v6 pipeline logic changes — only span-attr additions if Phase 2 §9 fields missing
- No changes to the 5 already-shipped FEC producers or to DOM-007/008/010 (already SIGNED_OFF)
- No bypass of compiler trust_level rules

## Gap Register

| Gap | Owner | Resolution |
|---|---|---|
| apps_exec + apps_research __main__ BLOCKER #5 (no resolve_fec call at runtime) | W1.P1 | Invoke Exit at a lower level (direct `run_exit_eval(l2_receipt)`) via harness, bypassing __main__; OR defer those 2 apps' runtime rows until BLOCKER #5 lands |
| 13 required OTEL fields per Phase 2 §9 — exact list | W2.P1 | Read plan parent's Phase 2 §9 list; map each field to span attr name |
| DOM-006 dual-proof policy | W3.P1 | Keep simulator proof as fallback; promote to PASS via real runtime proof when available |

## Verification Plan (W4.P1)

1. Run `python tools/cert/apps_e2e/run_app_cert_with_otel_capture.py --all-apps`
2. Confirm 8 trace fixtures on disk under `artifacts/apps_otel_traces/`
3. Re-run W3.P1 emitter; confirm DOM-002/003/004/005/009/012 flip to PASS
4. Run `python tools/cert/apps_e2e/run_app_negative_control_with_otel.py --all-apps`
5. Re-run W3.P2 emitter; confirm DOM-006 flips to PASS
6. Run merger + compiler; confirm signed_off=45 / blocked=0 / trust_level≥EVIDENCE_PROOF
7. Update parent plan Notion row to Completed

## AG_QUEUE_SEED

```
AG_QUEUE_SEED: plan=apps-dom-runtime-harness-followup-f2a7b3 id=AG-W1-harness-scope depends_on= title=Invoke Exit at __main__ level (requires BLOCKER #5 closure) vs direct run_exit_eval (bypass) — which scope?
```
