# Apps Runtime Proof Harness — `apps-runtime-proof-harness-9d4c2a`

> Status: **W0..W6 COMPLETE (2026-04-26). 69/69 tests PASS, 96/96 negative controls caught, CI gate green. All deferred scope closed.**
> Source authority: `docs/reference/agentic_system_process_map_exec.md` and the
> §6 Source authority block of the originating prompt.
> ADG snapshot: `artifacts/adg/adg_indexed_04252026_0843.sqlite`.

## Objective

Make `apps_*` impossible to fake. Every `apps_*` run must emit a verifiable
`AppRunEvidencePacket` with real OTEL spans, real contracts, real gate verdicts,
deterministic replay, and ADG-backed bypass checks — all routed through the
governed runtime spine.

## Tier — T3 (architecture-spanning, multi-package, runtime-evidence)

## Reality Check (vs prompt's stale baseline)

The prompt declared per-app gap counts (e.g. `apps_eval: 13 trace + 11 contract
+ 34 write`). Actual filtered ADG state on snapshot
`adg_indexed_04252026_0843.sqlite`:

| Bypass class                | Total across 8 apps |
|-----------------------------|--------------------:|
| trace_replay_eval_gaps      | 131                 |
| replay_surface_gaps         | 160                 |
| task_contract_gaps (`gap_flag=1`) | 0             |
| write_sovereignty_paths (`is_direct_infra_write=1 AND NOT uwg_routed`) | 0 |
| v_p0_apps_direct_infra      | 0                   |
| mv_gateway_bypass_paths     | 0                   |
| v_p1_not_on_spine           | 0                   |
| v_p1_ad_hoc_imports         | 0                   |
| mv_capability_and_egress_gaps | 0                 |
| mv_prompt_assembly_wiring_gaps | 0                |
| mv_exit_disposition_coverage  | 0                 |
| v_p0_write_bypass_uwg        | 0                   |

The remaining real gap is **trace/replay/eval coverage**, not P0 bypasses. The
foundation must therefore (a) prove and lock the clean surfaces, and (b) close
trace/replay coverage by emitting span+replay receipts on every
`apps_*` ingress run.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0   | W0.1      | Discovery + plan SSOT | 1500 | ADG snapshot intact | DONE | Plan file present, ADG counts captured |
| W1   | W1.1, W1.2, W1.3, W1.4 | Foundation: contracts + ADG queries + bypass validator + CLI | 6000 | `app_ingress_runner.py` reusable as-is | DONE | `proof_runner --bypass-only` PASS (8/8 apps, P0=0 across all) |
| W2   | W2.1..W2.8 | Per-app scenarios — one real scenario per app, span recorder integrated | 18000 | Existing per-app `_ingress_runner.py` factories sufficient | DONE | `proof_runner --all` PASS — 8 packets hash-verified, 48 spans, 24 contracts, 19 gates |
| W3   | W3.1, W3.2, W3.3 | Trace + replay + artifact validators (deterministic re-run, hash check) | 8000 | Scenarios in W2 are deterministic | DONE | `proof_runner --validate` PASS — 8/8 trace + 8/8 replay + 8/8 inventory verdicts ok |
| W4   | W4.1, W4.2, W4.3 | Negative controls + write sovereignty + L6 firewall + 7 test files | 9000 | sandbox artifact writer is minimal new code | DONE | 12 negative controls × 8 apps = 96/96 catches; write sovereignty PASS; 55/55 pytest |
| W5   | W5.1      | Wire CI gate + writeback + Notion row | 1500 | None | DONE | `ops_scripts/ci/check_apps_runtime_proof.py` exits 0 end-to-end via subprocess |
| W6   | W6.1, W6.2, W6.3 | C0+PA+L2+ExitEval drivers; sandbox/UWG writer; optional OTEL SDK mirror | 19000 | scenarios are deterministic | DONE | 9 spans + 7 contracts per grounded scenario; exit_disposition=allow_finish; sandbox + uwg_pending artifacts on disk |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Discovery + plan | This file, `artifacts/runtime/apps_proof/_adg_*.json` | none | 1500 | DONE |
| W1.1 | Evidence contract types | `apps_shared/proof/proof_contracts.py` | hash determinism, span ordering invariants | 1500 | IN PROGRESS |
| W1.2 | App inventory from ADG | `apps_shared/proof/app_inventory.py` | column name drift across views | 1000 | IN PROGRESS |
| W1.3 | ADG bypass queries (12 views) | `apps_shared/proof/adg_queries.py` | filter predicates per view | 2000 | IN PROGRESS |
| W1.4 | Bypass validator + CLI smoke entrypoint | `apps_shared/proof/bypass_validator.py`, `proof_runner.py` | exit-code semantics | 1500 | IN PROGRESS |
| W2.1 | apps_eval scenario | `apps_shared/proof/scenarios/scenario_apps_eval.py` | L6-firewall (no policy mutation) | 2500 | TODO |
| W2.2 | apps_exec scenario | `apps_shared/proof/scenarios/scenario_apps_exec.py` | grounded brief, C0+Prompt Assembly required | 2500 | TODO |
| W2.3 | apps_lic scenario | `.../scenario_apps_lic.py` | egress+HITL gates, no external dispatch | 2500 | TODO |
| W2.4 | apps_research scenario | `.../scenario_apps_research.py` | citation-bound output | 2000 | TODO |
| W2.5 | apps_rfp scenario | `.../scenario_apps_rfp.py` | requirement parser contracts | 2000 | TODO |
| W2.6 | apps_rg scenario | `.../scenario_apps_rg.py` | hallucination detector emits gate verdict | 2500 | TODO |
| W2.7 | apps_underwriting_ai scenario | `.../scenario_apps_underwriting_ai.py` | recommendation-only or HITL routing | 2500 | TODO |
| W2.8 | apps_shared meta scenario | `.../scenario_apps_shared.py` | proof-of-shared-harness | 1500 | TODO |
| W3.1 | Trace validator | `apps_shared/proof/trace_validator.py` | required span sequence enforcement | 2500 | TODO |
| W3.2 | Replay validator | `apps_shared/proof/replay_validator.py` | normalized hash diff | 2500 | TODO |
| W3.3 | Artifact validator | `apps_shared/proof/artifact_validator.py` | content-hash check | 1500 | TODO |
| W4.1 | Negative controls (17) | `apps_shared/proof/negative_controls.py` + test file | tampering must produce hash mismatch | 3000 | TODO |
| W4.2 | Write sovereignty | `apps_shared/proof/sandbox_artifact_writer.py` | classify writes as SANDBOX_OUTPUT vs UWG | 2000 | TODO |
| W4.3 | Test suite (7 files) | `tests/apps_proof/*.py` | fixtures parameterized over 8 apps | 4000 | TODO |
| W5.1 | CI gate + writeback | `ops_scripts/ci/check_apps_runtime_proof.py`, Notion row | none | 1500 | TODO |

## ADG_GRAPH_LAYER_EVIDENCE

This plan uses the ADG graph layer as the primary driver — not raw `edges`/
`violations` counts. Materialized views and P-views consulted:

1. **`mv_trace_replay_eval_gaps`** (columns `node_id, file, layer, has_trace,
   has_replay_link, has_eval, gap_type`) — primary driver of which app surfaces
   need span emission. 131 unresolved across the 8 apps.
2. **`mv_replay_surface_gaps`** (`node_id, file, layer, mutation_count,
   replay_link_count, gap_flag`) — drives W3.2 replay validator scope. 160
   unresolved.
3. **`mv_write_sovereignty_paths`** (`writer_file, write_symbol, is_uwg_routed,
   is_direct_infra_write, severity`) — drives W4.2; baseline already 0 when
   filtered to `is_direct_infra_write=1 AND NOT is_uwg_routed`.
4. **`mv_task_contract_gaps`** (`node_id, file, layer, action_edge_count,
   schema_or_policy_count, contract_impl_count, gap_flag`) — drives W1.4
   contract verifier; baseline 0 when `gap_flag=1`.
5. **`mv_exit_disposition_coverage`** (`node_id, file, layer,
   outgoing_terminal_count, is_terminal_covered, gap_type`) — drives the
   exit-disposition span requirement; baseline already 0 unresolved.
6. **`mv_capability_and_egress_gaps`** (`provider_invoke_count,
   capability_route_count, egress_gate_count`) — drives apps_lic egress proof.

P-views consulted:
- `v_p0_apps_direct_infra` — must remain 0 across W2 scenarios.
- `v_p0_write_bypass_uwg` — must remain 0 across W4.2.
- `v_p1_not_on_spine`, `v_p1_ad_hoc_imports` — adapter spine compliance.

Semantic edges used in scenario validators (W2/W3):
- `flows_to` for U0→L1→L0→C0→PromptAssembly→L2→Exit chain validation.
- `writes_to` + `emits_side_effect` for sandbox vs UWG classification (W4.2).
- `resolves_callsite` for span↔contract digest binding.
- `controls_flow` for L3 step dispatch verification.

ADG Provenance: backend=sqlite, snapshot=adg_indexed_04252026_0843.sqlite

## Mode Separation (constitutional §19)

- W0 = analyze (DONE)
- W1 = edit foundation only (no apps_* surface modifications)
- W2 = edit per-app scenario stubs (compose existing ingress_runners)
- W3, W4 = edit validators + tests (no production code changes)
- W5 = edit CI wiring

## Bypass / Decisions

- No author-gate triggered: architecture is fixed by existing
  `app_ingress_runner.py` + `scripts/proof/*.py` precedent.
- No agent deletion.
- No archives imports.
- Subprocess wrappers will use `subprocess.run(argv, shell=False, timeout=...)`.

## Out of Scope (next-step candidates)

- Closing the 131+160 trace/replay gap structurally (i.e. instrumenting every
  app surface with OTEL spans and replay-link metadata) — this plan emits
  PROOF that the gaps exist; closing them is a follow-up wave.
- Modifying `governed_app_runner` to inject the recorder — current plan uses
  `LocalSpanRecorder` from `scripts/proof/run_end_to_end_runtime_proof.py`.
