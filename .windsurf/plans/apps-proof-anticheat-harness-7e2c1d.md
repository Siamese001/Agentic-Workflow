# apps_* Anti-Cheat Proof Harness — Implementation Plan

- **Plan ID:** `apps-proof-anticheat-harness-7e2c1d`
- **Created:** 2026-04-26
- **Status:** Phase 1 (W0–W7) ✅ complete · Phase 2 (W8) ✅ complete · Phase 3 (W9–W13) in progress
- **Tier:** T3 (cross-layer, multi-app, verifier independence, real runtime invocation)
- **ADG Snapshot:** `artifacts/adg/adg_indexed_04252026_0843.sqlite` (346 MB, 84,920 nodes, 593,555 edges, 5,348 violations, 116,829 overlay violations, 70 tables, 32 views — all 17 required views present)
- **ADG Provenance:** backend=sqlite, snapshot=adg_indexed_04252026_0843.sqlite

## Goal (verbatim from user)

> Make it impossible for `apps_*` to "look like it ran" unless the repo produces runtime evidence that proves the app actually passed through the governed agentic path. Anti-cheat principle: a run passes only when (1) artifact exists, (2) OTEL trace confirms runtime path, (3) contract chain joins to trace, (4) independent verifier recomputes hashes — all four must agree.

## Phase 0 Outcome — What Already Exists

A substantial proof harness is already shipping at `apps_shared/proof/` (13 modules, ~150 KB, latest CI run `2026-04-27T02:00:31Z` PASS across all 8 apps). What it provides today:

| Capability | Status | Location |
|---|---|---|
| Real spine invocation U0 → L1 → L0 → C0 → PA → L3 → L2 → Exit → L6 | ✅ Real (NOT_IMPLEMENTED honestly when wiring missing) | `apps_shared/proof/scenario_base.py` |
| Real contracts: ValidatedRequest, L1PlanContract, RouteContract, PromptEnvelope, SealedArtifact, ExitDecision, FinalEvidenceContract | ✅ Real | same |
| Hash-chained `AppRunEvidencePacket` with `verify_packet_hash` | ✅ | `apps_shared/proof/proof_contracts.py` |
| W3 validators: trace tree, replay determinism, artifact inventory | ✅ | `apps_shared/proof/validators.py` |
| 13 negative controls (T1–T12 + extra), all caught | ✅ | `apps_shared/proof/negative_controls.py` |
| ADG bypass queries — all 12 required MVs | ✅ | `apps_shared/proof/adg_queries.py` |
| Write sovereignty validator | ✅ | `apps_shared/proof/write_sovereignty.py` |
| CI gate `--full` mode wired | ✅ | `ops_scripts/ci/check_apps_runtime_proof.py` |

**Gap that triggers this work:** L2 today uses a `deterministic_model` stub inside `scenario_base.run_l2()`. The 9 spans across all 8 apps are real spine spans, not synthetic — but they prove the spine, not the per-app code path. The user's anti-cheat principle requires real `apps_underwriting_ai/engines/decision_packet_assembler.py` (etc.) invocation, not a generic L2 stub.

## What Needs to Be Built / Wired

| # | Gap | User-spec item |
|---|---|---|
| 1 | `tools/apps_proof/` CLI namespace does not exist | "Create or extend `tools/apps_proof/run_app_proof.py`" |
| 2 | `--fixture <path>`, `--require-otel`, `--require-replay`, `--require-adg` flags | exact CLI surface |
| 3 | Independent verifier separate from runner (current is in-process) | "A separate verifier must read the trace export and artifacts and recompute" |
| 4 | `proof_verdict.json` (separate from `evidence_packet.json`) | "proof_verdict.json must include proof_manifest_hash, verifier_version, …" |
| 5 | Per-app real driver hook in L2 (instead of generic deterministic stub) | "actually passed through the governed agentic path" |
| 6 | ADG before/after snapshot diff per run | adg_before.json, adg_after.json, adg_delta.json |
| 7 | `apps_proof_matrix.{md,json}` cross-app verdict | explicit deliverable D |
| 8 | `tests/apps_proof/` test suite | explicit deliverable E |
| 9 | Sabotage cases T13–T21 (the 9 user-listed cases) | TEST SABOTAGE CASES section |
| 10 | ADG inspector handles `NO_FILE_COLUMN` views (5 P0/P1/P2 views use non-standard column) | inspector contract |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W0** | W0.1 | Phase 0 Discovery — ADG baseline + plan + sabotage map | ~6k | Existing harness inventoried, no edits | ✅ DONE | `artifacts/apps_proof/{adg_apps_baseline.{md,json},implementation_plan.md}` written; canonical plan written |
| **W1** | W1.1–W1.3 | `tools/apps_proof/` CLI shim layer | ~12k | Delegate to existing `apps_shared.proof`; expose user's exact CLI surface | TODO | `python -m tools.apps_proof.run_app_proof --app apps_underwriting_ai --fixture …` runs end-to-end; existing CI still green |
| **W2** | W2.1–W2.3 | Real `apps_underwriting_ai` L2 driver | ~16k | New `apps_shared/proof/runtime_drivers/` package; opt-in via `--driver real` flag | TODO | L2 invokes `decision_packet_assembler.py` for real, captures real OTEL, sealed artifact carries real evidence_register reference |
| **W3** | W3.1–W3.2 | Independent verifier + `proof_verdict.json` | ~10k | Reads on-disk artifacts only; recomputes ALL hashes; never trusts in-memory state | TODO | `python -m tools.apps_proof.verify_app_proof --proof-dir …` produces `proof_verdict.json` with `final_status: PASS`, recomputed hashes match |
| **W4** | W4.1–W4.2 | Sabotage cases T13–T21 (9 user-listed) | ~8k | Map onto existing 13; add missing 4–6 | TODO | Each sabotage case fails the verifier with the user's expected reason code (e.g., FAIL_UWG_BYPASS) |
| **W5** | W5.1–W5.2 | ADG before/after diff + `--require-adg` | ~10k | Snapshot ADG before invocation, re-query touched files after, fail if P0 worsens | TODO | `adg_delta.json` shows zero P0 worsening on touched paths; verifier rejects worsened runs |
| **W6** | W6.1 | `apps_proof_matrix.{md,json}` builder | ~6k | Aggregates all per-app `proof_verdict.json` | TODO | Matrix shows PASS/FAIL per app with failure reasons |
| **W7** | W7.1–W7.7 | `tests/apps_proof/` suite (7 test files) | ~14k | Pure verifier tests, no harness invocation | TODO | All 7 test files pass against the W4 sabotage corpus |
| **W8** | W8.1–W8.6 | Extend real drivers to apps_rfp, apps_research, apps_exec, apps_lic (with privacy/egress), apps_rg (read-only), apps_shared substrate | ~36k | Phase 2; one driver per wave; reuse W2 framework | TODO | Each new app's `proof_verdict.json` PASS; matrix all green |

**Phase 1 = W0–W7 for `apps_underwriting_ai` + `apps_eval` + `apps_shared` substrate**. Phase 2 = W8.

### Phase 3 — Hardening & Coverage Expansion (W9–W13)

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **W9** | W9.1 | Dedupe contract files (cosmetic) — driver-written artifacts re-emitted with `<kind>_<digest8>.json` suffix | ~3k | TODO | No file is written twice for the same logical contract; only the canonical filename remains |
| **W10** | W10.1–W10.4 | Per-app unsupported-claim invariants in verifier (currently only apps_underwriting_ai is checked) | ~6k | TODO | apps_rfp claim ↔ capability_evidence; apps_research claim ↔ credibility_scores; apps_exec claim ↔ evidence_source; apps_lic claim ↔ approval_packet |
| **W11** | W11.1–W11.5 | Per-app sabotage cases T22-T30 — apps-specific tampers | ~6k | TODO | T22 (delete capability_evidence_map), T23 (mutate egress verdict), T24 (mutate research credibility), T25 (mutate recommendation flag), T26 (delete substrate import) |
| **W12** | W12.1 | Real ADG delta with regen guard — currently same-snapshot, no genuine delta | ~5k | DEFERRED | Optional: invoke `tools/generate_full_adg.py --quick` post-run; compare to pre-snapshot |
| **W13** | W13.1 | CI integration — nightly full chain on PR | ~4k | DEFERRED | Document CI invocation; integration deferred until W9–W11 stabilize |

Phase 3 immediate scope: W9–W11 (dedup, per-app verifier, per-app sabotage). W12 and W13 are stamped DEFERRED — they require either ADG regen orchestration (W12, ~5–10 min runtime) or repo-CI infra changes (W13). Captured as NEXT_STEP markers.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|
| W0.1 | ADG baseline + plan | `_adg_inspect.py` (throwaway), `artifacts/apps_proof/{baseline,plan}.{md,json}`, `.windsurf/plans/...` | 5 P-views report `NO_FILE_COLUMN` — need column name discovery in W5 | 6k | DONE |
| W1.1 | `tools/apps_proof/__init__.py` + `run_app_proof.py` | 2 new files | Map `--fixture/--require-*` flags onto existing `--apps/--full/--bypass-only` | 4k | TODO |
| W1.2 | `tools/apps_proof/verify_app_proof.py` skeleton | 1 new file | Initially proxies to existing in-process verifier; W3 makes it independent | 4k | TODO |
| W1.3 | `tools/apps_proof/adg_app_inspector.py` | 1 new file | Extract logic from `_adg_inspect.py`, harden `NO_FILE_COLUMN` cases | 4k | TODO |
| W2.1 | `apps_shared/proof/runtime_drivers/__init__.py` + base protocol | 2 new files | Define `AppRuntimeDriver` Protocol with `invoke(envelope, ctx) -> SealedArtifact`; backward-compat with current stub | 4k | TODO |
| W2.2 | `apps_shared/proof/runtime_drivers/apps_underwriting_ai_driver.py` | 1 new file | Wire `decision_packet_assembler.assemble_decision_packet(...)`; supply borrower fixture; capture real OTEL via `tools.otel.otel_bootstrap` | 8k | TODO |
| W2.3 | Hook driver into `scenario_base.run_l2()` | edit 1 file | Opt-in via `ScenarioSpec.runtime_driver` field; default = current stub | 4k | TODO |
| W3.1 | Independent verifier — hash recomputation | edit `verify_app_proof.py` | Reads only on-disk artifacts; recomputes packet_hash, contract_digests, sealed_artifact_hash; fails on any mismatch | 6k | TODO |
| W3.2 | `proof_verdict.json` schema + writer | edit `verify_app_proof.py` | proof_manifest_hash = hash(stable_json({…})); passed_checks/failed_checks lists; verifier_version stamping | 4k | TODO |
| W4.1 | Sabotage T13–T21 mutators | extend `apps_shared/proof/negative_controls.py` | Need new mutators: unsupported_claim_injection, provider_fallback_without_recertification, fake_proof_verdict | 4k | TODO |
| W4.2 | Map T13–T21 to user-spec FAIL reason codes | extend `negative_controls.py` | Match user's exact strings: FAIL_MISSING_C0_CONTRACT, FAIL_REPLAY_ROUTE_MISMATCH, etc. | 4k | TODO |
| W5.1 | `--require-adg` ADG snapshot diff | new `apps_shared/proof/adg_diff.py` | Re-query touched files post-run; produce delta JSON | 6k | TODO |
| W5.2 | Verifier ADG no-worsening assertion | edit `verify_app_proof.py` | Fail if any touched-file P0 increased | 4k | TODO |
| W6.1 | `tools/apps_proof/build_proof_matrix.py` | 1 new file | Aggregates `artifacts/apps_proof/<app>/<run_id>/proof_verdict.json` files | 6k | TODO |
| W7.1–7.7 | Seven `tests/apps_proof/test_*.py` files | 7 new test files | Tests verifier behavior, not runtime; uses W4 sabotage corpus as fixtures | 14k | TODO |
| W8.1 | apps_rfp driver | new file in runtime_drivers/ | invoke `apps_rfp/engines/proposal_assembly_engine.py` | 6k | TODO |
| W8.2 | apps_research driver | same | invoke `apps_research/engines/research_assembly_engine.py` | 6k | TODO |
| W8.3 | apps_exec driver | same | invoke `apps_exec/engines/brief_assembly_engine.py` | 6k | TODO |
| W8.4 | apps_lic driver + privacy/egress | same + `apps_shared/proof/privacy_validator.py` | invoke `apps_lic/engines/control_plane.py` with egress=BLOCKED gate | 8k | TODO |
| W8.5 | apps_rg read-only driver | same | invoke `apps_rg/engines/base_rg_engine.py` with mutate=False; assert no writes | 6k | TODO |
| W8.6 | apps_shared substrate proof | new file | shared_runtime_spine_report, shared_contract_schema_report, shared_trace_helpers_report, shared_replay_helpers_report | 4k | TODO |

## ADG_HOTSPOT_REPORT

Hotspot ranking for files this plan will touch. Impact = `violations × (1 + log10(1 + fan_in)) × layer_multiplier`. Source: ADG snapshot + Phase 0 baseline.

| File | Layer | Layer mult | Violations | Overlay | Archetype | Surfaces | Impact | Wave touch |
|---|---|---:|---:|---:|---|---|---:|---|
| `apps_shared/proof/scenario_base.py` | L_APP | 1.0 | low (proof code) | n/a | ORCHESTRATOR | Execution, Observability | medium | W2.3 (1 edit) |
| `apps_shared/proof/proof_runner.py` | L_APP | 1.0 | low | n/a | ORCHESTRATOR | Execution, Observability | medium | W1 (delegate via tools shim, no edit) |
| `apps_shared/proof/negative_controls.py` | L_APP | 1.0 | low | n/a | SAFETY_GATEKEEPER | Security, Observability | medium | W4 (extend) |
| `apps_underwriting_ai/engines/decision_packet_assembler.py` | L_APP | 1.0 | 0 (clean) | unknown | STATE_NODE | Write, State | low | W2.2 (read-only invoke) |
| `apps_lic/engines/control_plane.py` | L_APP | 1.0 | medium | high | ORCHESTRATOR | Security, Execution | HIGH | W8.4 (no edit; carefully invoked with egress gate) |
| `apps_rg/engines/base_rg_engine.py` | L_APP | 1.0 | high | very high | CENTRAL_DEPENDENCY | Execution, State | HIGH | W8.5 (read-only invocation only; no edit) |
| `apps_shared/config/pipeline_constants_config.py` | L_APP | 1.0 | medium | high | CENTRAL_DEPENDENCY | State | HIGH | NO-GO (read-only, never edited by this plan) |

`apps_underwriting_ai` has the **lowest debt** of any vertical app in the baseline (75 nodes, **6 violations, 5 overlay violations**) — this validates the user's prior signal that it should be the first proof app.

## ADG_GRAPH_LAYER_EVIDENCE

The plan is driven by the following materialized views and P-views (all confirmed present in the snapshot):

**Materialized views (used to drive wave selection and risk):**
1. `mv_high_fan_in_out_with_defects` — apps_underwriting_ai = 73 hits, apps_rg = 163 (highest), apps_shared = 164 → confirms `apps_rg` and `apps_shared` are CENTRAL_DEPENDENCY archetype
2. `mv_debt_concentration_hotspots` — apps_underwriting_ai = 6 (lowest of the verticals); apps_rg = 41 → first-proof-app selection validated
3. `mv_hidden_writes_overlay` — apps_rg = 82 (highest), apps_shared = 50, apps_lic = 12, apps_underwriting_ai = 4 → write-sovereignty risk concentrated in rg/shared/lic; W8.4 and W8.5 must enforce no-write
4. `mv_trace_replay_eval_gaps` — apps_underwriting_ai = 6 (lowest), apps_rg = 30 (highest), apps_shared = 38 → trace coverage gaps concentrate in rg/shared (Phase 2)
5. `mv_module_load_action_calls_overlay` — apps_rg = 110 (extreme), apps_shared = 101, apps_lic = 39, apps_underwriting_ai = 0 → confirms apps_underwriting_ai has clean module-load path; perfect first-proof candidate
6. `mv_provider_surface_sprawl` — apps_lic = 1, apps_research = 1, apps_rg = 1, apps_shared = 2, others = 0 → provider fallback risk surface; W4 sabotage T13 (provider fallback without recertification) must catch this for these apps

**Semantic edges in scope:**
- `flows_to` — used by W3 verifier to confirm contract chain joins to spans
- `writes_to` / `emits_side_effect` — used by W5 ADG diff to detect any new write surface introduced by a run
- `resolves_callsite` — used by W2 driver to confirm L2 invocation actually reaches `decision_packet_assembler.assemble_decision_packet`
- `controls_flow` — used by W3 to verify gate verdicts gate the right span branches

**P-view cross-references** (5 of 5 P-views report `NO_FILE_COLUMN` — column-name discovery deferred to W5.1):
- `v_p0_apps_direct_infra` — must inspect schema and surface column name in W1.3 inspector hardening
- `v_p0_write_bypass_uwg` — same; cross-checks `mv_hidden_writes_overlay` rows for confirmation
- `v_p0_provider_bypass` — same; cross-checks `mv_provider_surface_sprawl`
- `v_p1_raw_http_outside_seam` — same
- `v_p2_duplicated_adapters` — same

The `NO_FILE_COLUMN` finding for the 5 P-views is itself an ADG signal — the inspector in W1.3 must discover their actual schema (likely `node_id` or `module` instead of `file`) and surface it, otherwise we leak P0 risk.

## High-Risk Files — NO-GO List (per user spec)

These files are **read-only** for this plan. Touching them requires Author-Gate:

- `apps_shared/config/pipeline_constants_config.py`
- `apps_rg/engines/base_rg_engine.py`
- `apps_eval/engines/scenario_runner.py`
- `apps_shared/reasoning/BaseDispatchAgent.py`
- `apps_shared/enforcement/ProvenancetrackerStrategy.py`
- `apps_lic/engines/control_plane.py`
- `apps_underwriting_ai/engines/underwriting_engine.py`
- `apps_underwriting_ai/engines/decision_packet_assembler.py` *(invoked, never edited)*
- `apps_underwriting_ai/engines/evidence_register_engine.py` *(invoked, never edited)*
- `apps_underwriting_ai/integrations/retrieval_adapter.py` *(invoked, never edited)*

## Files To Modify / Create (per wave)

| Wave | New files | Edited files | Read-only invoked |
|---|---|---|---|
| W1 | `tools/apps_proof/__init__.py`, `run_app_proof.py`, `verify_app_proof.py`, `adg_app_inspector.py` | none | `apps_shared/proof/proof_runner.py` |
| W2 | `apps_shared/proof/runtime_drivers/__init__.py`, `apps_underwriting_ai_driver.py`, `fixtures/apps_underwriting_ai/golden_borrower_package.json` | `apps_shared/proof/scenario_base.py` (run_l2 hook) | `apps_underwriting_ai/engines/decision_packet_assembler.py` |
| W3 | (verifier extension) | `tools/apps_proof/verify_app_proof.py` | `apps_shared/proof/proof_contracts.py` |
| W4 | (sabotage extension) | `apps_shared/proof/negative_controls.py` | none |
| W5 | `apps_shared/proof/adg_diff.py` | `tools/apps_proof/run_app_proof.py`, `verify_app_proof.py` | ADG snapshots |
| W6 | `tools/apps_proof/build_proof_matrix.py` | none | per-app proof_verdict.json |
| W7 | 7 × `tests/apps_proof/test_*.py` | none | sabotage corpus |
| W8 | 6 × runtime_drivers/*, fixtures | (none required in apps_*) | each app's primary engine |

## Tests To Add

`tests/apps_proof/test_no_static_fake_proof.py` — every artifact in a passing run must contain `run_id` AND `trace_id`; rejects hand-written files
`tests/apps_proof/test_trace_contract_join.py` — every contract `emitted_by_span_id` must resolve to an actual span with matching `trace_id`
`tests/apps_proof/test_replay_required.py` — `replay_comparison.json` must exist and prove byte-equal canonical contracts
`tests/apps_proof/test_exit_required.py` — final output cannot exist without `ExitDisposition`
`tests/apps_proof/test_l6_post_exit_only.py` — every L6 record's timestamp must be ≥ `runtime_boundary_ts`
`tests/apps_proof/test_adg_no_worsening.py` — `adg_delta.json` must show zero P0 worsening
`tests/apps_proof/test_app_specific_required_artifacts.py` — each app has a per-spec required-artifacts list (e.g. `evidence_register.json` for apps_underwriting_ai)

## Anti-Cheat Sabotage Cases (W4 mapping)

| User case # | Existing T# | Action |
|:---:|:---:|---|
| 1. remove C0 evidence contract | T3 (`inventory_file_deleted`) | Re-target to delete `FinalEvidenceContract*.json` only |
| 2. remove one OTEL span from L2 E3 | T3 variant | Add T13 specifically targeting L2 spans |
| 3. change route_digest between replay runs | T9 (`contract_content_mutation`) | Add T14 specifically targeting `RouteContract.route_digest` |
| 4. add final output without ExitDisposition | (none) | Add T15 — delete `ExitDecision_*.json` |
| 5. add L6 record timestamp before ExitDisposition | (none) | Add T16 — mutate L6 span `started_at` to before `runtime_boundary_ts` |
| 6. proposed durable write without UWG receipt | (none) | Add T17 — inject fake `SovereignWriteRequest_*.json` without `uwg_receipt_*` |
| 7. add unsupported claim to underwriting decision packet | (none) | Add T18 — mutate `decision_packet.json` to add a claim absent from `evidence_register.json` |
| 8. add provider fallback without recertification | (none) | Add T19 — add `provider_fallback_*.json` to artifacts without matching `recertification_*.json` |
| 9. fake proof_verdict PASS without trace links | (none) | Add T20 — write `proof_verdict.json` with `final_status: PASS` but no `trace_id` reference, verifier must reject on `proof_manifest_hash` recompute |

## Commands (Phase 1 acceptance)

```pwsh
# Phase 0 (DONE)
python _adg_inspect.py
# → artifacts/apps_proof/adg_apps_baseline.{md,json}

# W1 — CLI shim layer
python -m tools.apps_proof.adg_app_inspector --adg artifacts/adg/adg_indexed_04252026_0843.sqlite --apps-glob "apps_*" --out artifacts/apps_proof/adg_apps_baseline.json

python -m tools.apps_proof.run_app_proof --app apps_underwriting_ai --fixture fixtures/apps_underwriting_ai/golden_borrower_package.json --proof-root artifacts/apps_proof --require-otel --require-replay --require-adg

python -m tools.apps_proof.verify_app_proof --proof-dir artifacts/apps_proof/apps_underwriting_ai/<run_id>

# W7 — tests
python -m pytest tests/apps_proof -q
```

## Risks

- **R1 — `decision_packet_assembler` requires real upstream evidence_register**: in W2.2, the driver must construct or load a fixture `EvidenceRegister`. Fix: ship `fixtures/apps_underwriting_ai/golden_borrower_package.json` with a pre-validated evidence_register payload.
- **R2 — OTEL bootstrap may not be initialized in proof harness context**: existing `tools/otel/otel_bootstrap.py` is used by `scripts/proof/`. W2.2 must explicitly call `init_otel_runtime(...)` before driving the L2 invocation. Fail loudly if absent.
- **R3 — ADG snapshot diff (W5) requires re-running `tools/generate_full_adg.py` post-run**: that's expensive (~5–10 min). Mitigation: W5 runs incremental query against latest snapshot only, not a regen. If incremental ≠ regen, document in proof_verdict.
- **R4 — Existing `--apps` flag conflict with new `--app` (singular)**: W1.1 supports both: `--app X` (single, with `--fixture`) AND `--apps X Y Z` (multi-batch).
- **R5 — `apps_underwriting_ai` "L_UNKNOWN classification risk"**: user mentioned this from prior review. W2.2 must set `risk_class = "HIGH_IMPACT"` explicitly via the driver, not `L_UNKNOWN`. ADG taxonomy regen is out of scope for this plan.

## Completion Criteria

The plan is complete when:

1. ✅ `tools/apps_proof/run_app_proof.py --app apps_underwriting_ai --fixture …` exits 0
2. ✅ `tools/apps_proof/verify_app_proof.py` produces `proof_verdict.json` with `final_status: PASS` and recomputed hashes match
3. ✅ All 9 sabotage cases (T13–T21) cause the verifier to FAIL with the user-spec reason codes
4. ✅ `tests/apps_proof/` 7-file suite passes
5. ✅ Existing `ops_scripts/ci/check_apps_runtime_proof.py --mode full` still PASSes (no regression)
6. ✅ `apps_proof_matrix.{md,json}` produced for `apps_underwriting_ai` + `apps_eval` + `apps_shared`
7. ✅ Phase 1 user sign-off before Phase 2 (W8) begins

## Out of Scope (deferred to Phase 2 / future)

- Real-app drivers for `apps_rfp`, `apps_research`, `apps_exec`, `apps_lic`, `apps_rg`, `apps_shared` substrate (W8)
- ADG taxonomy regen to resolve `apps_underwriting_ai` L_UNKNOWN
- Streaming OTEL export to a remote collector (current is file-based)
- Network egress validator beyond ADG-static checks (would require runtime mock)

## Plan SSOT

This file is the canonical plan. The user-requested deliverable
`artifacts/apps_proof/implementation_plan.md` exists as a thin pointer to
this canonical SSOT (per `.windsurf/rules/plan-location.md`).
