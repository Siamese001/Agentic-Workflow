# Plan — Fort Knox apps_* Domain Contract System (c4d8e2)

> **Status**: DRAFT — awaiting `SR_APPROVAL` before any Phase 1 edits.
> **Tier**: T3 (cross-layer architecture, all `apps_*`, multi-wave)
> **Discovery report**: `docs/reference/apps_domain_contract_discovery.md`
> **Goal**: Make every `apps_*` package declare its own domain-specific contract
> (input, output, rubric, thresholds, graders, retrieval, prompt, capability,
> route, fixtures, negative controls) and make those contracts authoritative
> via UWG/L4, runtime-resolved, Exit-consumed, and proven in E2E artifacts.

## Core invariants (from user spec, non-negotiable)

1. apps_* may author domain intent and app-local config.
2. apps_* may NOT become runtime authority.
3. L4 is the durable source of truth.
4. UWG is the only durable write path.
5. Exit consumes resolved app-specific rubric and threshold refs.
6. 99% proof harness proves the app-specific contract governed the run.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W0** | P0 | Discovery — inventory + gaps + reuse map | ~12k | None | **DONE** | Discovery report on disk; no edits. |
| **W1** | P1 | Shared `AppDomainContract` schema (records + digests + lookup helpers) | ~28k | L4_state/contracts/records.py is the canonical home | Todo | New records compile; deterministic_digest stable across runs; unit tests for each subcontract. |
| **W2** | P2.1, P2.2, P2.3 | Per-app `apps_<name>/config/domain_contract/*.yaml` for all 8 apps | ~42k | Seed from existing rubrics/thresholds/policies; apps_qna and apps_underwriting_ai handled specially | Todo | All 8 apps have the 13-file YAML set; schema-validation passes for each; identical-rubric anti-collision passes. |
| **W3** | P3.1, P3.2, P3.3 | UWG registration adapter (Exit-source pseudo-run); ALLOWED_OPERATIONS extension; CLI registrar | ~32k | Author-Gate decision needed for source_surface (see TODOs §8) | Todo | `register_app_domain_contracts.py --app all` produces UWGCommitReceipts for every app; direct-write attempts blocked with audit row. |
| **W4** | P4.1, P4.2, P4.3 | Runtime resolution: extend `RouteContract` + `V15RouteContract`; new `app_domain_resolver` at L0 dispatch; ingress runners stop direct YAML reads | ~38k | RouteContract extension is backward-compatible (defaults preserve current behavior) | Todo | Every L0 dispatch attaches app refs; static + runtime test prove no `apps_<name>/config/<...>.yaml` reads in hot path; replay determinism preserved. |
| **W5** | P5.1, P5.2, P5.3 | App-specific Exit evaluation: extend `ExitReviewPacket` and `X3CommitRequestPacket`; new `app_specific_evaluator`; per-dimension scoring with UNKNOWN fail-closed | ~36k | Generic V6 verdicts continue for non-app-bound runs | Todo | Exit X1/X2/X3 consume per-app rubric/threshold/grader; UNKNOWN never passes; minimums enforced (not just overall score). |
| **W6** | P6.1, P6.2 | OTEL + proof bundle: emit `app.*` attributes; extend proof bundle with all required app refs | ~22k | apps_shared/proof spine is reusable | Todo | OTEL spans carry all `app.*` keys; proof bundle JSON validates against new schema; replay receipt + no-bypass receipt include app contract refs. |
| **W7** | P7.1, P7.2, P7.3, P7.4 | Tests: schema, UWG/L4, runtime resolution, Exit, E2E proof (per-app golden + negative) | ~48k | Reuse `apps_shared/proof/scenarios.py`, `proof_runner.py` | Todo | Every test category from discovery §7 lands and passes; 8 apps × 2 golden + 2 negative = 32 E2E tests. |
| **W8** | P8 | Acceptance: full proof command set; verification doc; sign-off | ~14k | All prior waves DONE | Todo | All 13 acceptance bar items in user spec are TRUE; commands runnable; gaps disclosed. |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P0** | Discovery | `docs/reference/apps_domain_contract_discovery.md` (NEW), this plan (NEW) | None | ~12k | DONE |
| **P1** | Shared `AppDomainContract` schema | `agentic_core/L4_state/contracts/app_domain.py` (NEW), `app_domain_digests.py` (NEW), `app_domain_lookup.py` (NEW), `__init__.py` re-exports, unit tests | Schema bloat — 13 record types; need to keep digest computation deterministic; field count balance | ~28k | Todo |
| **P2.1** | Per-app YAMLs — manifest + task_classes for all 8 apps | `apps_<name>/config/domain_contract/{app_domain_manifest,task_classes}.yaml` × 8 | apps_qna and apps_underwriting_ai task_class ambiguity (TODO_FAILING_TEST) | ~10k | Todo |
| **P2.2** | Per-app YAMLs — input/output/rubric/threshold/grader for all 8 apps | `apps_<name>/config/domain_contract/{input_contract,output_schema,eval_rubrics,threshold_profiles,grader_roster}.yaml` × 8 | Migration of `apps_eval/config/rubrics/*.yaml` without breaking existing eval ingress | ~20k | Todo |
| **P2.3** | Per-app YAMLs — retrieval/prompt/capability/route/orchestration/fixtures/negative_controls | `apps_<name>/config/domain_contract/{retrieval_profiles,prompt_profiles,capability_profiles,route_profiles,orchestration_profiles,fixtures,negative_controls}.yaml` × 8 | apps_rg / apps_lic / apps_underwriting_ai also need orchestration_profiles (DAG/HOP). 2 fixtures + 2 negative controls minimum per app. | ~12k | Todo |
| **P3.1** | UWG ALLOWED_OPERATIONS + source-surface decision | `agentic_core/L4_state/uwg/durable_write_gateway.py` modification + Author-Gate packet for source_surface | **Author-Gate required** — extend NON_AUTHORIZED_SOURCES exemption vs. synthetic Exit run | ~10k | Todo |
| **P3.2** | Registration adapter (config YAML → CommitRequest+StateDiff) | `agentic_core/L4_state/uwg/app_domain_registration.py` (NEW) | Deterministic-digest stability across reruns; idempotent registration | ~14k | Todo |
| **P3.3** | CLI registrar + validator | `apps_shared/scripts/register_app_domain_contracts.py` (NEW), `validate_app_domain_contracts.py` (NEW) | Per-app vs all-apps; --dry-run mode | ~8k | Todo |
| **P4.1** | RouteContract + V15RouteContract extension | `agentic_core/L0_routing/c0_retrieval/route_contract.py`, `agentic_core/L0_routing/types/route_contract_v15.py` | Backward compatibility; field defaults; digest computation must remain stable | ~12k | Todo |
| **P4.2** | L0 app_domain_resolver | `agentic_core/L0_routing/app_domain_resolver.py` (NEW), composition wiring | (app_id, task_class) extraction from request; fail-closed when contract missing | ~14k | Todo |
| **P4.3** | Ingress runners stop direct YAML reads | `apps_<name>/integrations/*_ingress_runner.py` (8 apps) — replace direct YAML loads with RouteContract refs | Risk of regressing existing eval/exec/research/rfp/rg runs | ~12k | Todo |
| **P5.1** | ExitReviewPacket + X3CommitRequestPacket extension | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | Field set kept closed-vocabulary; digest stability | ~8k | Todo |
| **P5.2** | app_specific_evaluator | `agentic_core/L3_orchestration/exit_eval/v6/app_specific_evaluator.py` (NEW) | Deterministic vs LLM-judge dispatch; UNKNOWN fail-closed wiring; per-dimension minimums | ~16k | Todo |
| **P5.3** | Exit pipeline integration | `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` modification | X1/X2/X3 stage hooks; preserve V6 fall-through for non-app-bound runs | ~12k | Todo |
| **P6.1** | OTEL `app.*` attributes | `apps_shared/proof/otel_export.py`, span emit sites in L0/L2/Exit | Closed vocabulary for app.* keys; trace replay parity | ~10k | Todo |
| **P6.2** | Proof bundle extension | `apps_shared/proof/proof_runner.py`, `validators.py`, `write_sovereignty.py`, `negative_controls.py`, schema doc | All required proof fields land; replay/no-bypass receipts include app refs | ~12k | Todo |
| **P7.1** | Schema unit tests | `tests/_apps_contract/test_app_domain_contract_schema.py` (extend) | Anti-collision rule; UNKNOWN/NA semantics | ~10k | Todo |
| **P7.2** | UWG/L4 integration tests | `tests/_apps_contract/test_app_domain_uwg_registration.py` (NEW), `test_app_domain_l4_lookup.py` (NEW) | Direct-write attempt rejection; deprecated-status fail-closed | ~10k | Todo |
| **P7.3** | Runtime + Exit tests | `tests/_apps_contract/test_app_domain_runtime_resolution.py` (NEW), `test_app_domain_exit_evaluation.py` (NEW) | Per-app rubric resolution; UNKNOWN fail-closed | ~12k | Todo |
| **P7.4** | E2E proof tests | `tests/_apps_contract/test_app_domain_e2e_proof.py` (NEW) — parametrized | 8 apps × 2 fixtures + 8 × 2 negatives = 32 cases; OTEL replay parity; no-bypass scanner | ~16k | Todo |
| **P8** | Acceptance + sign-off | Verification commands runnable end-to-end; final report | All 13 acceptance bar items must be TRUE | ~14k | Todo |

## Author-Gate decisions anticipated (will surface at phase entry)

| Phase | Decision | Why |
|---|---|---|
| P3.1 | Source-surface for app-contract registration | UWG enforces `source_surface=="Exit"`. Two viable options: (a) carve out an `AppContractRegistrar` exemption in `NON_AUTHORIZED_SOURCES`, (b) route registration through a synthetic Exit pseudo-run with `disposition=COMMIT_REQUEST`. Trade-offs: (a) widens the authority model; (b) keeps invariant pure but adds boilerplate per registration. |
| P4.1 | RouteContract extension shape | Add new fields to existing `RouteContract` dataclass vs. compose via a new `AppContractRefs` sub-dataclass on RouteContract. |
| P4.3 | Migration strategy for ingress runners | Big-bang switch to L4 resolution vs. dual-read with feature-flag fallback. |
| P5.2 | Generic V6 vs app-specific Exit evaluation precedence | Replace V6 entirely vs. layer app-specific on top. |
| P7.4 | Replay determinism enforcement at proof gate | Hard-fail on digest mismatch vs. soft-warn during initial rollout. |

## ADG_GRAPH_LAYER_EVIDENCE

T3 plans require this section per constitutional §22 / `adg-graph-layer-enforcement.md`.

> **Note**: This plan is the **discovery + sequencing** plan. The deeper graph-layer
> evidence (materialized views, P-views, semantic edges across the L4/UWG/L0/Exit
> spine) will be embedded into each Wave's execution plan as it becomes active.
> The discovery report cites the concrete code paths read; full graph-layer
> evidence is gathered at Phase entry, not at plan-draft time.

Provisional graph-layer evidence anchors (to expand at W1+ entry):

- `mv_graph_chokepoint_bridges` — likely flags `agentic_core/L4_state/uwg/durable_write_gateway.py` and `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` as bridges; this plan's blast radius MUST honor those chokepoints.
- `mv_hotspot_centrality` — used at W4/W5 entry to identify which `apps_<name>/integrations/*_ingress_runner.py` files have the highest fan-in (most caller risk on migration).
- `v_p0_apps_direct_infra` — pre-flight check at W3 to enumerate any current direct-L4 writes from `apps_*` to migrate before registration goes live.
- `v_p0_write_bypass_uwg` — same pre-flight + post-condition at W3 close (count must remain at zero).
- `flows_to` semantic edges — at W5 entry, traces from L0 RouteContract construction through Exit eval, confirming the new app refs propagate end-to-end.
- `emits_side_effect` — at W6 entry, audits OTEL emission sites to ensure all app.* attributes appear at the right spans.

## ADG_HOTSPOT_REPORT (preliminary — refined per-Wave)

| Hotspot | Layer | Archetype | Surface(s) | Fan-in (preliminary) | Notes |
|---|---|---|---|---|---|
| `agentic_core/L4_state/uwg/durable_write_gateway.py` | L4 | SAFETY_GATEKEEPER | Write, Security, Observability | high | THE write authority; W3 modification must preserve all existing invariants. |
| `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` | L3 | ORCHESTRATOR | Execution, Write | high | X1/X2/X3 dispatcher; W5 hook point. |
| `agentic_core/L4_state/contracts/records.py` | L4 | CENTRAL_DEPENDENCY | State | very high | All L4 records live here; W1 extension blast radius. |
| `agentic_core/L0_routing/c0_retrieval/route_contract.py` | L0 | CENTRAL_DEPENDENCY | Execution | high | RouteContract consumed by C0/Prompt/L2/Exit; W4 extension. |
| `apps_shared/proof/proof_runner.py` | apps_shared | ORCHESTRATOR | Observability | medium | Proof bundle builder; W6 extension. |

Full layer-criticality multipliers per `adg-canonical-invariants.md` §6 will be applied at each Wave entry.

## Gap Register

| Gap | Owner Phase | Mitigation |
|---|---|---|
| `apps_qna` task_class undefined | P2.1 (TODO_FAILING_TEST) | Surface as Author-Gate at P2.1 entry. |
| `apps_underwriting_ai` is a stub | P2.1 (TODO_FAILING_TEST) | Author minimal `status=draft` contract; full implementation deferred. |
| Source-surface for registration | P3.1 (Author-Gate) | Decide: exempt-list expansion vs synthetic Exit run. |
| Versioning (active-version selection) | P3.2 (TODO_FAILING_TEST) | Default: latest by policy_hash; optional explicit alias_swap. |
| Self-eval circularity for `apps_eval` | P5.2 (TODO_FAILING_TEST) | Bootstrap rule: apps_eval rubric loads from L4 like others; chicken-and-egg solved by registration ordering (apps_eval first). |
| Rubric dual-location during migration | P2.2 (TODO_FAILING_TEST) | Drift detector test; deprecation timeline = 1 wave after P3.3. |
| Capability profile vs `apps_shared/enforcement/*Strategy.py` | P5.2 (TODO_FAILING_TEST) | Compose: capability profile defines allowlist; strategies enforce dynamics. |
| Grader roster minima for deterministic-only apps | P1 (TODO_FAILING_TEST) | Allow empty `llm_judge_graders[]` if `deterministic_graders[]` non-empty. |

## Acceptance Bar (final P8)

All 13 must be TRUE — verbatim from user spec:

- [ ] Every apps_* has a domain contract.
- [ ] Every active task_class has input contract, output schema, rubric, threshold profile, grader roster, retrieval profile, prompt profile, capability profile, fixture, and negative control.
- [ ] Domain contracts are registered into L4 through UWG.
- [ ] Runtime resolves app-specific contracts from L4, not directly from app YAML.
- [ ] Exit consumes app-specific rubric and thresholds.
- [ ] X3 disposition references app-specific eval results.
- [ ] L6 receives app-specific evaluation refs in runtime exhaust.
- [ ] OTEL spans include app-specific contract refs and digests.
- [ ] E2E proof bundle shows the app contract governed runtime behavior.
- [ ] Negative controls fail for expected app-specific reasons.
- [ ] Direct app-to-L4 writes are impossible and tested.
- [ ] Missing app-specific rubric or threshold fails closed.
- [ ] UNKNOWN required app-specific eval dimension never passes.

## Proof commands (final, will be runnable at P8)

```powershell
# Validate (no UWG submission)
python -m apps_shared.scripts.validate_app_domain_contracts --app all

# Register through UWG into L4
python -m apps_shared.scripts.register_app_domain_contracts --app all

# Per-app golden path
python -m tools.proof.run_app_domain_e2e --app apps_rg --case golden
python -m tools.proof.run_app_domain_e2e --app apps_lic --case golden
# ... for every apps_*

# All apps × all cases
python -m tools.proof.run_app_domain_e2e --app all --case all

# Verify OTEL spans carry app refs
python -m tools.proof.verify_otel_app_refs --bundle artifacts/proof/<run-id>.json

# No-bypass scanner
python -m tools.proof.scan_no_direct_l4_writes --apps all

# Full test suite
pytest tests/_apps_contract/ -v
```

## Sequencing rules

1. **No code edits before SR_APPROVAL** on this plan.
2. Each Wave begins with its own SR_PLAN packet (refined from this plan).
3. Each Wave ends with SR_VERIFY: tests green + commit + WRITEBACK to Notion.
4. Phases within a Wave run sequentially unless explicitly parallel-safe.
5. Author-Gate decisions surface at Phase entry, never mid-Phase.
6. Every commit on this plan's branch carries `plan-ref=apps-domain-contract-fortknox-c4d8e2`.
7. Phase 0 (this) is closed once the user approves; all later Phases require their own SR cycle.

## Notes on tier classification and discipline

- **Tier**: T3 (cross-layer, cross-app, multi-Wave).
- **Constitutional rule binding**: §22 (graph-layer evidence), §23 (ADG canonical invariants), §28 (no grep for deps), §29 (router emission for any new router-class decisions — likely none here, but P5.2 should verify), §31 (SSOT folder routing for new files).
- **Author-Gate triggers**: see "Author-Gate decisions anticipated" above.
- **Plan location**: `.cursor/plans/apps-domain-contract-fortknox-c4d8e2.md` — repo SSOT per `plan-location.md`.
- **Discovery report location**: `docs/reference/apps_domain_contract_discovery.md` — the user explicitly requested this path in §8 of the spec.
