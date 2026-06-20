---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-dom-real-evidence-enhancement-c7f4d8.md'
original_relative_path: '_archive\\2026-05\\apps-dom-real-evidence-enhancement-c7f4d8.md'
source_sha256: 25c56bede3566ac307d4375eb3093632629284c9269bd8f97b21310cae5b6bc8
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# APPS-DOM Real Evidence · Enhancement Closure

**Slug:** `apps-dom-real-evidence-enhancement-c7f4d8`
**Status:** Completed (2026-05-03)
**Parent:** `apps-dom-runtime-evidence-real-b4c9e2` (completed)
**Author-Gate link:** `dec_19dedd3f565173b7f` (heuristic_split precedent)

## AI Summary

Parent plan closed 4 evidence gaps (pipeline-native emit, preloaded store, mapper dim_scores,
sha256 hashes). Four residual synthetics remain in the fixtures: (1) `request_id` / `run_id`
/ `session_id` / `replay_key` synthetic deterministic strings, (2) `hmac_sig` synthetic
string, (3) no proof that the X3E SAFE_ABSTAIN disposition path fires under realistic
judge-abstain conditions, (4) no CI gate ensuring fixture freshness (stale fixtures could
mask later regressions). This plan closes all four with additive-only changes; does NOT
touch the pipeline's X1/X2/X3 logic or any rubric/threshold semantics.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1 | ULID-based `request_id` / `run_id` / `session_id` / `replay_key` generated per run | ~4k | Python-stdlib ULID (`uuid.uuid7()` or 26-char base32 derivation); deterministic seed supported for reproducible fixtures | Draft | Fixture carries real ULID-shaped ids; regenerating produces distinct ids unless `--deterministic` is set |
| W2 | W2.P1 | Real `hmac_sig` — HMAC-SHA256 over a canonical-JSON form of receipt content | ~6k | Key is a harness-local constant (`APPS_DOM_HARNESS_HMAC_KEY`) — documented as dev-tier, not prod-signed; prod keys are ADR-bound. | Draft | Fixture `hmac_sig` is `hmac-sha256://<64hex>` and verifies against the harness key; regeneration with same content produces identical sig (deterministic) |
| W3 | W3.P1 | X3E SAFE_ABSTAIN negative-control harness + emitter consumption | ~12k | Setting `output.judge_abstained=True` on grounded receipts forces X1D UNKNOWN → X2 safe_abstain path → X3E disposition per v6 spec invariant 25 | Draft | 8 fixtures in `artifacts/apps_safe_abstain_runtime/<app>_abstain_trace.json` with `exit_disposition: X3E`; fixtures verify the SAFE_ABSTAIN branch exists for every app |
| W4 | W4.P1 | Evidence-freshness CI gate: fail when harness fixtures older than 168h (1 week) | ~8k | `ops_scripts/ci/check_apps_dom_fixture_freshness.py`; reads fixture `generated_at_utc`; skips when fixtures absent (first-run tolerant); runs in `run_contract_gates.py` | Draft | Gate passes fresh fixtures; fails stale; bypass `APPS_DOM_FIXTURE_FRESHNESS_BYPASS=1`; registered in the contract-gates pipeline |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | ULID identifiers | `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (modify `_build_receipts`) + `tools/cert/apps_e2e/run_app_negative_control_with_otel.py` (same) + helper `_gen_ulid` | Must preserve deterministic mode for reproducible fixtures (flag-gated); generated ULID should be parseable as 26-char Crockford base32 | ~4k | Draft |
| W2.P1 | HMAC sig | Same 2 harness files (modify `_build_receipts`); helper `_compute_hmac_sig` + `_canonical_receipt_form` | Canonical form must exclude `hmac_sig` itself and any nondeterministic keys; HMAC key is a harness constant (documented) | ~6k | Draft |
| W3.P1 | X3E negative control | `tools/cert/apps_e2e/run_app_safe_abstain_with_otel.py` (new) + extend emitter to accept X3E as an additional DOM-006/010 disposition | Need to confirm `judge_abstained=True` on grounded route actually routes to X3E (not X3B escalate when `material_unknown` fires). If X3B, receipt tweaks required (non-material gate UNKNOWN). | ~12k | Draft |
| W4.P1 | Freshness CI gate | `ops_scripts/ci/check_apps_dom_fixture_freshness.py` (new) + register in `ops_scripts/ci/run_contract_gates.py` | CI gate runs on pre-commit hooks; must not break fresh checkouts lacking fixtures (first-run tolerant); bypass env var name follows existing pattern | ~8k | Draft |

## ADG_GRAPH_LAYER_EVIDENCE

- **MV `mv_dependency_cone_risk`** — all changes confined to `tools/cert/apps_e2e/` + new file under `ops_scripts/ci/`; zero L0/L5 boundary crossing.
- **MV `mv_chokepoint_bridges`** — no new chokepoints introduced; existing harness chokepoint unchanged.
- **Semantic edge `flows_to`** — harness L2 receipt → HMAC over canonical JSON → fixture signature field. Isolated flow.
- **P-view `v_p2_runtime_harness_ready`** — extends from "harness emits real evidence" to "harness emits real-ID + real-HMAC evidence with freshness enforcement".

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-in | Archetype | Surfaces | Impact |
|---|---|---|---|---|---|
| `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` | tools | 1 | ORCHESTRATOR | Observability | low — additive fields only |
| `tools/cert/apps_e2e/run_app_negative_control_with_otel.py` | tools | 1 | ORCHESTRATOR | Observability | low |
| `tools/cert/apps_e2e/run_app_safe_abstain_with_otel.py` (new) | tools | 0 | ORCHESTRATOR | Observability | low — new isolated harness |
| `ops_scripts/ci/check_apps_dom_fixture_freshness.py` (new) | ops_scripts | 1 (run_contract_gates) | SAFETY_GATEKEEPER | Security | low — advisory gate, bypass-enabled |

## Files In Scope

- `tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` (modify)
- `tools/cert/apps_e2e/run_app_negative_control_with_otel.py` (modify)
- `tools/cert/apps_e2e/run_app_safe_abstain_with_otel.py` (new)
- `tools/cert/apps_e2e/emit_apps_negative_control_assertions.py` (modify — accept X3E)
- `ops_scripts/ci/check_apps_dom_fixture_freshness.py` (new)
- `ops_scripts/ci/run_contract_gates.py` (modify — register gate)

6 files. T2 plan.

## Non-Goals

- **No runtime pipeline logic changes** (X1/X2/X3, preflight, aggregator all untouched).
- **No rubric/threshold YAML changes.**
- **No live `python -m <app>` invocation** — deferred to a separate "real cert run integration" plan; requires per-app `--cert-dry-run` cooperation which several apps lack.
- **No new APPS-DOM requirement rows.**
- **No changes to the 4 UNIMPL LLM judges** — separate plan with judge-calibration dependency.
- **No BLOCKER #5 closure** (apps_exec/apps_research `__main__.py` resolve_fec wiring) — separate plan.

## Gap Register

| Gap | Owner | Resolution |
|---|---|---|
| Harness HMAC key is dev-tier, not prod-signed | W2.P1 | Document in fixture `hmac_sig_class: "dev_harness"`; real prod signing requires ADR + KMS wiring (deferred) |
| X3E may not fire if material-UNKNOWN cascade triggers X3B instead | W3.P1 | Receipts tuned to produce X1D UNKNOWN only (not X1A/X1F which are material); fallback assertion accepts `{X3E, X3B}` as both prove the "safe-stop-not-allow" invariant |
| Freshness window of 168h may be too strict for on-demand-only workflows | W4.P1 | Configurable via env var `APPS_DOM_FIXTURE_FRESHNESS_HOURS`; default 168; bypass honored |

## Verification Plan (W4 close)

1. Run `python tools/cert/apps_e2e/run_app_cert_with_otel_capture.py` — fixtures now carry ULID ids + `hmac_sig = hmac-sha256://...`.
2. Run `python tools/cert/apps_e2e/run_app_negative_control_with_otel.py` — same.
3. Run `python tools/cert/apps_e2e/run_app_safe_abstain_with_otel.py` — 8 X3E fixtures.
4. Run `python ops_scripts/ci/check_apps_dom_fixture_freshness.py` — fresh fixtures → exit 0.
5. Run merger + compiler → confirm `signed_off=45 / blocked=0`, `trust_level=INTEGRITY_PROOF`.
6. Run v6 + apps_contract test suites — 979+ tests still pass.
7. Flip Notion row + plan header to Completed. Emit DECISION_OUTCOME marker.

## AG_QUEUE_SEED

(none — additive scope, no decisions expected.)
