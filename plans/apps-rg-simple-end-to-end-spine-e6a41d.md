---
plan_id: apps-rg-simple-end-to-end-spine-e6a41d
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/core_addition_author_gate/apps-rg-simple-end-to-end-spine-e6a41d.json"
dod_exempt: false
supersedes: []
---

# apps_rg_simple — Minimal Apps Research → Resume End-to-End Spine

Build an in-repository, serial-first reference runtime that starts with the governed `apps_research`
producer, validates its committed targeting-brief handoff, then preserves the essential `apps_rg`
stage contracts and produces a complete MVP reference resume without carrying the production app's
accumulated cache, calibration, repair-ladder, multi-ledger, and observability complexity.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-07-19
PORT_STATUS: NOT_STARTED_TARGET_ABSENT
SOURCE_INVENTORY_STATUS: PENDING_EXACT_SOURCE_INVENTORY
CORE_ADDITION_STATUS: REQUIRED_NOT_AUTHORIZED
MAX_ALLOWED_CLAIM: PLAN_ONLY

---

## Context (SCQA)

- **Situation** — The current end-to-end product path begins FRESH_PREFLIGHT → APPS_RESEARCH_U0 →
  APPS_RESEARCH_RUNTIME → APPS_RESEARCH_EXIT → HANDOFF_BUNDLE_COMMIT → APPS_RG_U0, then runs
  Apps RG U0 → L1 → L0 → C0/PA → L2 → gates/judges → X1/X2/X3 → UWG → L6 shadow over an
  11-lane resume DAG. That path now spans substantial preflight, cache, authority-ledger, retry,
  calibration, provider-panel, post-X3, Apps Eval, and terminal-closeout machinery.
- **Complication** — The requested outcome is a much smaller folder that demonstrates the complete
  logic, handoffs, runtime gates, judges, aggregation, and final resume outputs. Copying the existing
  runtime wholesale would preserve complexity rather than remove it; importing concrete
  `agentic_core` internals would also create a brittle second product path.
- **Question** — How do we build a runnable `apps_rg_simple` that requires the Apps Research producer
  and its gates, completes all resume sections, and preserves every essential authority boundary while
  remaining small enough to understand and maintain?
- **Answer** — Keep Apps Research as an external governed producer across a process/file boundary;
  validate its immutable v2 bundle and all producer gates before U0. Make `apps_rg_simple` a
  declarative app customization and L2 recipe that enters the public core spine. Core—not the app—runs
  U0/L1/L0, generic C0/PA interpreters, GateMesh/judge enforcement, the one root Exit/X3, UWG, and L6.
  Add only a generic profile-driven recipe-registration/composition seam to core; never add an
  `apps_rg_simple` literal or a local shadow spine.

### Objective

Create `apps_rg_simple/` under `C:\Git\Agentic-Workflow-FRESH` as a small, independently runnable
Apps RG reference-consumer package, plus an end-to-end proof sequence, that:

1. accepts a source resume, job description, target role/company, and research/runtime configuration;
2. in live proof, runs local fresh preflight and then the existing governed Apps Research CLI exactly
   once as a separate external producer and requires its fresh SearXNG-grounded generation,
   model-backed X2, exact six-gate
   GateMesh, canonical Exit, and atomic v2 bundle commit;
3. admits those immutable bytes through a local reference-only input validator, then enters the
   canonical core spine with an app-owned U0 package/profile set and serial 11-lane L2 recipe;
4. supplies section/aggregate evidence and rubric packets while generic core GateMesh/judge/Exit
   enforcement emits the one root X3 and core UWG alone commits authorized final resume outputs; and
5. supplies a meta-feedback profile while core L6 shadow analysis runs after the immutable core
   product-terminal seal and before non-authorizing `runtime_acceptance` closeout; it cannot modify
   the current resume or X3.

### Constraints

- Planning only in this turn; do not create the target folder or runtime files before approval.
- Repository and target are confirmed: `C:\Git\Agentic-Workflow-FRESH\apps_rg_simple`.
- Use repository-relative paths (`apps_rg_simple/**`) in code, plans, tests, and artifacts.
- The target is a **reference-only app customization on the canonical core spine**, not a
  production-authorizing replacement for `apps_rg` or `apps_research`.
- Production `apps_rg/**` and `apps_research/**` remain read-only. A narrowly generic
  `agentic_core/**` change is required and is blocked on the core-addition author gate.
- `apps_rg_simple` may call only the public canonical core entrypoint and public generic ports. It must
  not reimplement U0, L1, L0, C0, PA, GateMesh/judges, root Exit/X3, UWG/L4 admission, or
  L6.
- Core changes must be `GENERIC_READY`, driven by validated package/profile refs, and contain no app
  names, app-specific gates, thresholds, paths, or branches.
- Because every root `apps_*` Python package must be classified, add exactly one declarative
  `GovernedAppEntry` for `apps_rg_simple` whose canonical callable enters the public core spine. The
  row conveys registry conformance, not production authority, and may contain no dispatch logic.
- Do not import production `apps_rg` or `apps_research` Python modules into `apps_rg_simple`. Run the
  existing Apps Research product CLI only as a separate proof-sequence process and let the package
  consume only its committed file contract. If repository boundary policy rejects that integration,
  stop.
- The current v2 manifest hard-codes `consumer_app_id=apps_rg`. The simple validator must preserve
  those bytes, record `reference_runtime_consumer=apps_rg_simple` in a separate local receipt, and
  never claim a native or canonical Apps Research → `apps_rg_simple` authority chain.
- Live proof forbids a caller-authored targeting brief or reuse of an old authorized bundle. Replay may
  use a recorded v2 bundle but must remain `REPLAY_CONTRACT`. Direct briefs are diagnostic-only and
  cannot produce an E2E success claim.
- Run serially first. Concurrency is excluded until an 11/11 serial live run is stable.
- Source facts prove resume claims. JD and briefing text may target wording but never prove a claim.
- Unknown, malformed, missing, or stale required evidence is non-PASS.
- Only root `X3D_ALLOW_FINISH` may authorize a final-output commit through UWG.
- Apps Research may durably publish its upstream authority bundle before UWG; only final resume product
  writes are UWG-exclusive.
- Core L6 runs only after the immutable core product-terminal seal; it is read-only and future-run-only.

### Assumptions

- “All resume sections” means the current 11 generated lanes plus locked/pass-through identity,
  employment metadata, education, certifications, and other source-only content.
- Required human-facing outputs are structured JSON, readable Markdown/text, and DOCX.
- One generation model call per lane plus at most one bounded repair call is sufficient for the simple
  runtime. Self-consistency pools and multi-rung repair ladders are not required.
- Section judging and whole-resume judging are separate responsibilities. Certification requires a
  judge provider/model independent from the generation provider/model; replay tests may use fixtures.
- The existing 11-lane dependency order is retained even though execution is serial.
- Live upstream proof uses the current Apps Research product contract: SearXNG retrieval,
  `external_openai` generation, and a model-backed Gemini X2 judge. A provider substitution is a
  source-contract change, not an equivalent live proof under this plan.
- Only target company, target role, and JD enter Apps Research. Candidate resume contents never enter
  the research producer and never become research evidence.

### Tier and Touched Surfaces

Tier: **T3** — new package, multi-stage architecture, model execution, durable output boundary, and
cross-layer verification.

Planned edit scope after approval:

- `apps_rg_simple/**`
- `tests/unit/apps_rg_simple/**`
- `tests/integration/apps_rg_simple/**`
- `tests/e2e/apps_rg_simple/**`
- targeted generic core contract tests under `tests/runtime/**`
- `apps_shared/integrations/app_registry.py` for one declarative `apps_rg_simple` classification row
- focused app-registry conformance tests
- the minimal generic core recipe-registration/composition surface identified and approved in W0
- required customization/core-addition/migration/verification receipts
- this plan and its eventual run receipt/status updates

The root `pyproject.toml` already uses package discovery `include = ["apps_rg*", ...]`; no packaging
edit is expected. Profiles remain inside the app-owned runtime customization package and resolve
through the approved generic core seam. Any other root configuration change is a scope expansion that
must be declared before editing.

Read-only source evidence:

- `apps_rg/LEAN_CORE.md`
- `apps_rg/config/domain_contract/workflow_manifest.resume_sections.v1.yaml`
- `apps_rg/config/domain_contract/e2e_stage_graph.resume_generation.v1.yaml`
- `apps_rg/runtime/product_entry.py`
- `apps_rg/runtime/orchestration/canonical_dispatch.py`
- `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`
- `apps_rg/runtime/bindings/u0_package_ingest.py`
- `apps_rg/runtime/bindings/u0_binding.py`, `l1_binding.py`, `l0_binding.py`
- `apps_rg/runtime/section_execution_plan.py`
- `apps_rg/runtime/spine/section_c0_retrieve.py`
- `apps_rg/runtime/spine/governed_pa_compose.py`
- `apps_rg/runtime/spine/section_cli_runners.py`
- `apps_rg/runtime/section_l2_spine_receipt.py`
- `apps_rg/runtime/spine/exit_artifacts.py`
- `apps_rg/l2_recipe/modular_resume_generation.py`
- `apps_rg/runtime/internal/generated_lane_rollup.py`
- `apps_rg/runtime/aggregation/preflight.py`
- `apps_rg/runtime/aggregation/cross_section_x2.py`
- `apps_rg/runtime/internal/locked_copy_builder.py`
- `apps_rg/runtime/internal/final_resume_assembler.py`
- `apps_rg/runtime/assembly/final_resume_x2.py`
- `apps_rg/runtime/assembly/full_resume_text.py`
- `apps_rg/runtime/assembly/full_resume_llm_coherence.py`
- `apps_rg/runtime/final_resume_outputs.py`
- `apps_rg/runtime/product_output_policy.py`
- `apps_rg/runtime/package/apps_rg_full_resume_x3_eligibility.py`
- `apps_rg/runtime/post_x3_completion.py`
- `apps_rg/runtime/section_runtime_exhaust_lane_integration.py`
- `apps_rg/runtime/section_runtime_exhaust_spine_receipt.py`
- `apps_rg/runtime/spine/l6_shadow_eval_runner.py`
- `apps_rg/runtime/run_output_contract.py`
- `apps_research/__main__.py`
- `apps_research/AGENTS.md`
- `apps_research/spine_manifest.yaml`
- `apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml`
- `apps_research/config/domain_contract/provider_profile.company_brief.v1.yaml`
- `apps_research/config/domain_contract/retrieval_profile.company_brief.v1.yaml`
- `apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml`
- `apps_research/config/domain_contract/l2_execution_profile.company_brief.v1.yaml`
- `apps_research/config/domain_contract/required_exit_gates.company_brief.v1.yaml`
- `apps_research/config/domain_contract/exit_profile.company_brief.v1.yaml`
- `apps_research/engines/company_brief_engine.py`
- `apps_research/integrations/spine_handoff.py`
- `apps_research/integrations/governed_research_run.py`
- `apps_research/integrations/apps_rg_handoff.py`
- `apps_research/integrations/search_retrieval.py`
- `apps_research/reasoning/ResearchHopOrchestrator.py`
- `apps_research/config/hop_pipeline.py`
- `apps_research/types/apps_rg_targeting_brief_contract.py`
- `apps_rg/integrations/apps_research_bridge.py`
- `apps_rg/integrations/managed_research_delegation.py`
- `apps_rg/prerequisites/briefing_validator.py`
- `apps_rg/runtime/bindings/briefing_u0_signals.py`
- `config/certification/apps_research_rg_e2e_authority_contract.v1.json`
- `config/certification/schemas/apps_research_apps_rg_handoff.v2.schema.json`
- `.github/workflows/apps-research-rg-handoff-e2e.yml`
- `ops_scripts/ci/check_apps_research_rg_handoff_e2e.py`
- `ops_scripts/ci/check_apps_research_rg_e2e_contract_freeze.py`
- `ops_scripts/ci/check_apps_research_rg_e2e_traceability.py`
- `ops_scripts/ci/check_apps_research_rg_full_chain_e2e.py`
- `tests/unit/apps_research/test_apps_rg_handoff_canonical_exit.py`
- `tests/unit/apps_research/test_cli_apps_rg_targeting_brief.py`
- `tests/unit/apps_research/test_targeting_brief_grounding_failclosed.py`
- `tests/e2e/apps_rg/test_apps_research_handoff_runtime_gates.py`
- `tests/unit/apps_rg/test_apps_research_bridge_contract_gate.py`
- `tests/unit/apps_rg/test_apps_research_bridge_u0_handoff.py`
- `tests/unit/ops_scripts/ci/test_apps_research_rg_e2e_contract_freeze.py`
- `tests/unit/ops_scripts/ci/test_apps_research_rg_e2e_traceability.py`
- `apps_shared/integrations/app_registry.py`
- `ops_scripts/ci/check_app_registry_conformance.py`
- `tests/unit/ops_scripts/ci/test_check_app_registry_conformance.py`
- `agentic_core/AGENTS.md`
- `.codex/rules/apps-customization.md`
- `.codex/schemas/CoreAdditionAuthorGateReceipt.schema.json`
- `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`
- `agentic_core/runtime/l2_recipe_resolver.py`
- `agentic_core/runtime/contracts/runtime_customization_package.py`
- `agentic_core/runtime/profiles/profile_resolver.py`
- `agentic_core/runtime/c0/c0_package_driven_grounding.py`
- `agentic_core/prompt_governance/pa_package_driven_binding.py`
- `agentic_core/runtime/gates/gate_mesh.py`
- `agentic_core/runtime/judges/panel/panel_runner.py`
- `agentic_core/runtime/exit/exit_package_driven_binding.py`
- `agentic_core/runtime/uwg/universal_write_gate.py`
- `agentic_core/runtime/bindings/generic_l6_handoff_validator.py`

Deferred / forbidden edit scope:

- production `apps_rg/**`
- production `apps_eval/**` and `apps_research/**`
- app-specific branches/literals/adapters anywhere under `agentic_core/**`
- core-owned U0/L1/L0/C0/PA/GateMesh/judge/Exit/X3/UWG/L6 reimplementations under
  `apps_rg_simple/**`
- repository governance, CI, rules, hooks, or canonical production schemas
- existing production run artifacts

### Evidence Status

Observed source facts:

- The current core entrypoint sequences U0 intake, the U0→L1 bridge, L0 route gates, a typed
  preloaded-context C0 bypass, L2 recipe execution, and Exit V6 X1/X2/X3 receipts.
- Current section execution performs app-owned C0 evidence resolution and governed PA before each
  model call.
- The canonical generated-lane order is 11 lanes: competencies; Unify, IBM, InsurTech, and EY
  bullets; their four narratives; executive summary; headline.
- Current aggregation builds a lane rollup, merges locked copy, runs cross-section/final X2, invokes
  a whole-resume coherence judge, emits final outputs, then enters post-X3 UWG and L6 closeout.
- Current aggregation preflight additionally requires per-lane input-usage and source-fact-pool proof
  receipts, while current section authority seals L2 and Exit X1/X2/disposition/spine receipts.
- Current assembly includes locked early-career, education, certifications, candidate identity, and
  base role headers in addition to the 11 generated lanes.
- Current product completion actively requires JSON/text/DOCX outputs; DOCX is emitted through
  `final_resume_outputs.py` and the exporter under `ops_scripts/apps_rg/`.
- The authoritative upstream prefix is FRESH_PREFLIGHT → APPS_RESEARCH_U0 → APPS_RESEARCH_RUNTIME →
  APPS_RESEARCH_EXIT → HANDOFF_BUNDLE_COMMIT → APPS_RG_U0. A direct/manual brief is not equivalent.
- The Apps Research handoff GateMesh is exactly G5, G6, G7, G21, G24, and G26, all PASS. G6 must be
  model-backed; canonical producer publication requires exact `X3D_ALLOW_FINISH`.
- The producer stages and fsyncs its bundle, writes the commit marker last, and atomically renames the
  run directory. The consumer must recompute schema, identity, JD/brief/policy/blueprint hashes,
  artifact bytes, marker, Exit, freshness, and producer attestation before use.
- The current v2 schema names `apps_rg` as consumer. This plan can prove live producer execution and
  strict reference compatibility, but not native producer authority for `apps_rg_simple`.
- `python -m apps_research --target-company ... --target-role ... --jd ...` is the current standalone
  product entry that emits the producer-owned `briefing.md` beside the v2 bundle. Omitting JD takes a
  generic artifact path and is not an Apps RG targeting-handoff run.
- The active targeting route has SearXNG as its grounded retrieval provider with no Tavily fallback,
  `external_openai` / `gpt-5.4-mini-2026-03-17` as generation route, and `gemini_pro` /
  `gemini-3.1-pro-preview` as the separate handoff judge. X2 must be model-backed PASS at score
  ≥0.75; abstention, provider failure, and UNKNOWN are non-PASS.
- The current official source workflow is useful contract evidence but not fresh live verification:
  structural traceability currently reports `NOT_RUN` requirements, evidence mode does not alone
  enforce zero skips, and the full-chain certification test is deterministic/cassette-backed.
- Current production success also includes Apps Eval, state promotion, a fuller per-section L6
  runtime-exhaust/binding chain, and 13 mandatory operator artifacts. Those are explicit omissions in
  this reference plan, so full production parity is not an allowed claim.

Source-inventory baseline: the exact execution roots and known source families were read directly,
but the deterministic inventory manifest has not yet been generated. W0 must freeze those roots,
resolve exact import/reference sites, bind source hashes, and validate the inventory before broad
implementation. ADG is optional supplementary evidence and is not a prerequisite.

Directly observed target baseline on 2026-07-18:

- `Test-Path apps_rg_simple` returned `false`.
- `git ls-files -- apps_rg_simple` returned zero tracked files.
- `git ls-files --others --exclude-standard -- apps_rg_simple` returned zero untracked files.
- Only this planning artifact exists. Therefore **zero runtime functionality is currently ported**,
  no parity test can yet pass, and no replay/live/11-of-11 claim is valid.
- The target CoreAdditionAuthorGate receipt does not exist, and current
  `artifacts/governance/session_state.json.active_plan` names
  `apps-rg-c03-graph-health-embedding-closure-b8d4f1`, not this plan. The core-addition gate therefore
  cannot pass until an approved execution session activates this plan and materializes its exact
  receipt; this plan does not edit the pre-existing session-state file.

---

## Port Completeness Proof Contract

### What "core functionality" means in this plan

The proof scope is every product behavior execution-reachable across one complete current
Apps Research → Apps RG run: fresh preflight; Apps Research U0/runtime/retrieval/generation/gates/
model-backed X2/Exit/bundle commit; consumer admission; Apps RG U0/L1/L0; per-lane C0/PA/L2;
section gates, judges, and dispositions; all generated and locked resume content; aggregation and
whole-run review; root X3; UWG; final products; immutable core product-terminal seal; core L6; and
non-authorizing verification closeout. It does **not** mean
unrelated `agentic_core` modules that the current product route never invokes.

That execution-reachable set is not yet complete because the deterministic source inventory has not
been generated. Exact source reads below identify known families; W0 must expand and resolve the
entrypoint roots through source/import-aware discovery before the inventory may be called complete.

### Required versioned manifests

Implementation must create these source-controlled manifests and matching JSON Schemas:

```text
apps_rg_simple/config/source_inventory.v1.json
apps_rg_simple/config/port_coverage.v1.json
apps_rg_simple/config/omission_ledger.v1.json
apps_rg_simple/config/claim_ceiling.v1.json
apps_rg_simple/schemas/source_inventory.v1.schema.json
apps_rg_simple/schemas/port_coverage.v1.schema.json
apps_rg_simple/schemas/omission_ledger.v1.schema.json
apps_rg_simple/schemas/claim_ceiling.v1.schema.json
```

`source_inventory.v1.json` must bind the source revision, clean/dirty state, discovery roots and
commands, source/import discovery evidence, discovery errors, canonical inventory digest, and one
deterministic row per obligation. Optional ADG evidence may be recorded but is never required. Each
row must contain:

```text
source_item_id
kind                         # STAGE|CONTRACT|HANDOFF|LANE|GATE|JUDGE|ARTIFACT|CONFIG|TEST_FIXTURE
source_path
source_symbol_or_key
source_sha256
semantic_obligation
authority_class              # LAW|PRODUCT_CONTRACT|PROOF|ROUTING|OPTIONAL_COMPLEXITY
execution_owner              # PORTED_APP_TARGET|CHANGED_GENERIC_CORE|REUSED_CANONICAL_CORE|REQUIRED_EXTERNAL_PRODUCER|OMITTED
evidence_refs[]
```

An inventory is `COMPLETE` only when every root resolves, discovery has zero errors, every dependency
claim names its exact source/import evidence, and all bound source hashes match the recorded revision.

`port_coverage.v1.json` must have exactly one row for every `source_item_id`, using only:

- `IMPLEMENTED_APP_EQUIVALENT`
- `IMPLEMENTED_APP_SIMPLIFIED`
- `CHANGED_GENERIC_CORE_AUTHORIZED`
- `REUSED_CANONICAL_CORE_REQUIRED`
- `REUSED_EXTERNAL_REQUIRED`
- `OMITTED_DEFERRED`
- `OMITTED_NOT_APPLICABLE`

App-implemented rows require an app target owner, target references, preserved invariants, and
collected parity test node IDs. `IMPLEMENTED_APP_SIMPLIFIED` also requires one or more omission IDs
for every dropped mechanism. `CHANGED_GENERIC_CORE_AUTHORIZED` requires exact changed core paths,
author-receipt path/digest binding, genericity/no-app-literal evidence, focused tests, and existing-app
regressions. `REUSED_CANONICAL_CORE_REQUIRED` requires the unchanged canonical core owner, public-
entrypoint/runtime `producer_component` proof, core regression node IDs, and an enforced no-alias/
no-shadow statement. `REUSED_EXTERNAL_REQUIRED` means the read-only production Apps Research owner
still executes the behavior; it requires an exact producer command/contract, source owner, boundary
owner, required receipt/gate set, parity node IDs, and an enforced no-port statement. Omitted rows
require exactly one omission ID and no target owner. Missing, duplicate, unknown, or conflicting
dispositions fail closed.

Every `omission_ledger.v1.json` row must contain an ID, bound source item IDs, capability, reason
code, user-visible effect, risk, replacement/compensating control, forbidden claims, re-entry
condition, approval reference, and negative test node IDs. Grouping omissions only in prose is not
sufficient.

`claim_ceiling.v1.json` must mechanically prohibit claims that exceed the evidence. The verifier may
emit only these roll-up outcomes:

- `MVP_SCOPE_ACCOUNTED` — every certified source item is classified; app-implemented and authorized
  generic-core changes pass parity; unchanged canonical-core reuse has producer-component/regression
  proof; every required external producer obligation has replay evidence; every omission is ledgered;
  all boundary checks and Apps Research v2 admission pass; and an 11-lane replay receipt validates.
- `LIVE_REFERENCE_VERIFIED` — `MVP_SCOPE_ACCOUNTED` plus a fresh real-model run with independent
  Apps Research generation/judge identities, fresh committed producer bundle, local admission PASS,
  independent downstream resume generation/judge identities, 11/11 PASS, aggregate PASS, root X3D,
  UWG commit,
  and core L6 after the product-terminal seal but before runtime closeout.

It may additionally emit only these evidence-scoped facets:

- `CURRENT_SOURCE_ACCOUNTED` — deterministic source/import discovery and source-hash verification passed.
- `CANONICAL_CORE_SPINE_EXECUTED` — runtime producer-component proof attributes every retained core
  stage to the public core path with no app shadow implementation.

- `APPS_RESEARCH_V2_ADMISSION_PASS` — an exact producer v2 bundle and every bound byte/gate/Exit/
  marker/identity check passed the local reference-only admission contract.
- `APPS_RESEARCH_UPSTREAM_VERIFIED` — the same proof session freshly ran the real Apps Research
  producer with live retrieval/generation/judging and then passed v2 admission. It is not native
  consumer authority or full-chain certification.
- `ELEVEN_OF_ELEVEN` — all 11 unique required lanes have proof-class-consistent PASS records.
- `MODEL_BACKED_JUDGED` — live downstream section and aggregate judges are model-backed and provider
  independent; never emitted for replay.
- `REFERENCE_OUTPUT_COMMITTED` — exact core root X3D and verified core UWG commit bind the outputs.

It must never emit bare `FULL_PORT_COMPLETE`. Because this plan deliberately omits production
surfaces, even a green run is a reference-runtime result, not canonical production authorization.

### Exact no-claim rules

The following are always forbidden for this plan: `PRODUCTION_AUTHORITY`,
`FULL_APPS_RG_PARITY`, `APPS_RESEARCH_CHAIN_CERTIFIED`,
`L5_CERTIFIED`, `APPS_EVAL_BOUND`, `OTEL_L7_COMPLETE`, `BCG_OUTPUT_PARITY`,
`MULTI_PROVIDER_QUORUM`, `CACHE_PARITY`, `PATCH_RUN_PARITY`, and `CLOSED_LOOP_LEARNING`.

The following remain forbidden unless their named evidence passes:

- `CURRENT_SOURCE_ACCOUNTED` until deterministic source inventory and hash verification pass.
- `MVP_SCOPE_ACCOUNTED` until the recomputed port-completeness receipt passes.
- `LIVE_REFERENCE_VERIFIED` until the fresh live receipt passes.
- `APPS_RESEARCH_V2_ADMISSION_PASS` until the local admission receipt passes every required check.
- `APPS_RESEARCH_UPSTREAM_VERIFIED` until the proof binds a fresh producer process, real provider
  identities, exact producer artifacts, and local admission PASS in the same proof session.
- `CANONICAL_CORE_SPINE_EXECUTED` until public-entrypoint and producer-component verification proves
  core ownership of U0/L1/L0/C0/PA/GateMesh/judge/Exit/UWG/L6 with no app shadow path.
- `ELEVEN_OF_ELEVEN` if any lane is missing, duplicate, REVIEW, BLOCKED, or `NOT_RUN`.
- `MODEL_BACKED_JUDGED` for replay, stub, same-model, or unknown judge identity.
- `REFERENCE_OUTPUT_COMMITTED` unless exact X3D and a verified UWG commit receipt exist.

### Runtime acceptance receipt

Every terminal run must write root-level `runtime_acceptance.json` after core L6 and bind:

```text
producer_app_id=apps_rg_simple
producer_component=apps_rg_simple.proof.runtime_acceptance
receipt_class=NON_AUTHORIZING_VERIFICATION
runtime_classification=REFERENCE_ONLY
proof_class=REPLAY_CONTRACT|LIVE_REFERENCE
research_mode=RECORDED_REPLAY|FRESH_LIVE
research_required=true
producer_evidence_class=RECORDED_COMMITTED_BUNDLE|FRESH_CURRENT_SESSION
research_executed_in_current_session=false|true
research_parent_run_id/research_child_run_id
research_request_id/trace_root/tenant_id
research_manifest_producer_app_id=apps_research
research_manifest_consumer_app_id=apps_rg
reference_runtime_consumer=apps_rg_simple
native_v2_consumer_authority=false
research_u0_status
research_gate_ids/statuses
research_generation_provider/model
research_x2_provider/model/score/model_backed
research_exit_x3
research_bundle_manifest_ref/digest
research_commit_marker_ref/digest
research_brief_ref/digest
research_jd_digest
research_freshness_as_of/max_age_days
external_research_admission_ref/digest/status
source_inventory_digest
coverage_digest
omission_ledger_digest
claim_ceiling_digest
package_revision
core_addition_author_gate_ref/digest
core_addition_migration_receipt_ref/digest
u0_customization_receipt_ref/digest
core_spine_entrypoint
core_stage_producer_components{}
run_id/request_id
producer_stage_order_recorded[]
proof_session_stage_order_observed[]
lane_summary{expected,attempted,passed,review,blocked,not_run}
provider_and_judge_identity
judge_evidence_class=RECORDED_REPLAY|LIVE_MODEL_BACKED
independence_status
aggregate_gate_and_judge_status
root_x3
uwg_commit_ref/digest
product_terminal_receipt_ref/digest/sealed_before_l6=true
l6_ref/digest/current_run_mutated=false
artifact_bindings[]
product_terminal_status
runtime_closeout_status
claim_ceiling[]
```

Core seals the immutable product-terminal receipt first. Core L6 then consumes only that sealed
product-terminal evidence. The app proof verifier emits `runtime_acceptance.json` once after L6 completes
or records an explicit N/A/failure and binds both immutable digests; this receipt is non-authorizing
and cannot reopen product authority. A
replay/stub run uses `proof_class=REPLAY_CONTRACT` plus `judge_evidence_class=RECORDED_REPLAY`; it
cannot infer live-model or production authority from fixture shape.

### Recomputed proof receipt

Each verification run must write:

```text
artifacts/governance/verification_receipts/<ts>_apps_rg_simple_port_completeness.json
```

The receipt must bind repository/source revisions, deterministic source-inventory provenance, CoreAdditionAuthorGate,
generic-core migration/addition and U0 customization receipt digests, all four manifest digests,
inventory/disposition counts, unclassified/unapproved-omission counts, test collection/execution
counts, core genericity/no-app-literal/boundary/no-shadow results, runtime producer-component evidence,
the runtime-acceptance digest, known gaps, changed files, and final outcome. A report generated from
stale manifests or a wider core diff is invalid.

### Preliminary known source deltas

These are directly inspected families, not the final exhaustive inventory:

| Current source family | Planned disposition | Preserved or omitted behavior |
|-----------------------|---------------------|-------------------------------|
| Apps Research U0, fresh SearXNG retrieval, targeting-brief generation/seal, and live X2 | REUSED_EXTERNAL_REQUIRED | Run the existing read-only producer for live proof; do not port its internal retrieval, hop, provider, cache, or calibration machinery |
| Apps Research G5/G6/G7/G21/G24/G26 GateMesh and canonical Exit | REUSED_EXTERNAL_REQUIRED | Require the exact six PASS gates, model-backed G6, sealed workflow, X1/X2, runtime exhaust, and exact producer X3D |
| Atomic Apps Research v2 handoff publication | REUSED_EXTERNAL_REQUIRED | Require producer-owned staging/fsync/marker/atomic-rename semantics and verify all committed bytes |
| Native `apps_rg` v2 consumer authority | OMITTED_NOT_APPLICABLE | Current schema hard-codes `apps_rg`; never rewrite it or emit the native consumer receipt for `apps_rg_simple` |
| External research bundle admission | IMPLEMENTED_APP_SIMPLIFIED | Implement strict schema/identity/digest/gate/Exit/freshness checks as a local non-product receipt with `native_v2_consumer_authority=false` |
| App runtime customization package/profile graph | IMPLEMENTED_APP_SIMPLIFIED | App owns one frozen package/profile graph and omits the broader production profile graph |
| Root `apps_*` classification | IMPLEMENTED_APP_EQUIVALENT | Add one declarative shared `GovernedAppEntry` whose canonical callable enters the public core spine; it grants no production claim |
| Canonical core U0/L1/L0 contracts and route interpretation | REUSED_CANONICAL_CORE_REQUIRED | Core validates the app carrier/package and emits fail-closed plan/route/replay receipts; prove canonical producer components and regressions |
| Core L2 recipe resolver hard-coded built-in registration | CHANGED_GENERIC_CORE_AUTHORIZED | Refactor to generic validated recipe metadata/convention with no app literal and regression-equivalent current `apps_rg` resolution |
| Public core entrypoint plus generic C0/PA engines | REUSED_CANONICAL_CORE_REQUIRED | Reuse canonical entry, C0, and PA enforcement with profile-driven app inputs and producer-component proof |
| Missing public-spine composition link, if W0 proves one | CHANGED_GENERIC_CORE_AUTHORIZED | Add only the exact author-receipted generic GateMesh/judge/Exit/UWG/L6 link; no app-specific behavior |
| Eleven generated lanes and locked/source-only sections | IMPLEMENTED_APP_EQUIVALENT | Retain all generated lanes, candidate/role headers, early career, education, and certifications |
| Per-lane proof, sealed L2, and lane acceptance | IMPLEMENTED_APP_SIMPLIFIED | Retain proof/same-run/digest semantics as non-authorizing L2 records; remove app/per-lane Exit/X3 authority |
| Core section GateMesh and judge enforcement | REUSED_CANONICAL_CORE_REQUIRED | Reuse generic core engines with app data profiles; prove core producer components and live/replay evidence classes |
| Multi-provider section/final judge topology | OMITTED_DEFERRED | Use one generation route and one independent judge route; no quorum/failover parity |
| Same-run fingerprint, sealed section index, aggregation WARN/REVIEW policy | IMPLEMENTED_APP_SIMPLIFIED | Retain same-run sealing and fail-closed candidate policy; omit release modes and whole-resume graph machinery |
| Production aggregate ordering (judge before final/cross gates) | IMPLEMENTED_APP_SIMPLIFIED | App assembles the packet; canonical core intentionally runs deterministic aggregate gates before the aggregate judge |
| Core aggregate GateMesh/judge and one root Exit/X3 | REUSED_CANONICAL_CORE_REQUIRED | Reuse canonical enforcement and root authority; prove exact producer components and no app/per-lane X3 |
| Proposed JSON/Markdown/text/DOCX bytes and write profile | IMPLEMENTED_APP_SIMPLIFIED | App renders in memory only; no durable product write |
| Core UWG commit/state-diff contract | REUSED_CANONICAL_CORE_REQUIRED | Reuse core idempotent validation, atomic write, and hash receipt; omit production refresh/rollback orchestration |
| Core product-terminal and L6 consumer | REUSED_CANONICAL_CORE_REQUIRED | Reuse immutable product-terminal sealing and one non-authorizing post-product-terminal, pre-runtime-closeout L6 shadow from the app meta-feedback profile |
| Production per-section L6 v4/runtime-exhaust and Apps Eval binding chain | OMITTED_DEFERRED | Omit production per-lane v40/microstep/binding closure; retain only the reused core L6 shadow above |
| Apps Eval and post-X3 fact-vector/state promotion | OMITTED_DEFERRED | No evaluator binding or future-run state writeback in the MVP |
| Reference preflight and non-authorizing runtime closeout | IMPLEMENTED_APP_SIMPLIFIED | Implement readiness plus post-L6 proof receipt; reuse core product-terminal sealing and omit signed continuation/production stage-ledger seal |
| Thirteen mandatory production operator artifacts | OMITTED_DEFERRED | Define and verify a narrower reference terminal contract; no production mandatory-output parity |
| Parallel dispatch, caches, patch runs, advanced candidate pools/repair ladders | OMITTED_DEFERRED | Serial fresh run with at most one bounded repair |
| C0.3 SQLite/embedding/allocation/calibration, L5, OTel/L7, BCG RCA | OMITTED_DEFERRED | Preserve proof-bound facts and minimal timing only |

If certified W0 discovery finds another reachable item, it must be added and classified before any
claim may advance beyond `PLAN_ONLY`.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.3 | Core-addition authorization, boundary proof, deterministic inventory, frozen generic seam | ~16K | Author gate can be granted; exact source/import discovery is available | 🔲 TODO | Receipt exists; canonical-spine architecture is boundary-clean; inventory/port dispositions/claim ceilings are complete before broad code implementation |
| W1 | W1.1–W1.3 | Generic core registration/composition seam plus app U0 package, profiles, recipe metadata | ~30K | Exact minimal core surface is frozen in W0 | 🔲 TODO | Generic core has no app literals; existing apps remain unchanged; app package/profile graph validates and public core entry resolves the app recipe |
| W2 | W2.1–W2.4 | Required Apps Research upstream/admission then canonical core U0/L1/L0/C0/PA | ~40K | Live producer prerequisites are available; source facts have stable IDs | 🔲 TODO | Producer bundle passes every upstream gate; core—not app code—emits front-spine receipts and proof-bounded compiled inputs |
| W3 | W3.1–W3.3 | App serial L2 recipe plus generic core section GateMesh/judges and bounded repair | ~42K | Provider ports return strict JSON; recorded replay verdicts are available | 🔲 TODO | 11/11 lanes execute in order; each seals proof/L2 artifacts and core gate/judge receipts; lane acceptance is explicitly non-Exit |
| W4 | W4.1–W4.4 | Candidate aggregation then core aggregate review, one Exit/X3, UWG, outputs, L6 | ~38K | All required lanes are accepted for the proof class | 🔲 TODO | Candidate assembles; core review passes; core Exit emits one X3; core UWG alone writes products; core L6 is post-product-terminal, pre-runtime-closeout, and non-mutating |
| W5 | W5.1–W5.3 | Port accounting, upstream baseline, replay, fault, and fresh live proof | ~32K | SearXNG plus upstream research and downstream resume provider credentials are available | 🔲 TODO | Certified inventory is accounted; upstream and downstream negatives fail closed; replay proves scope; one fresh research→11-lane run proves the reference claim without exceeding its ceiling |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Obtain core-addition author receipt and confirm canonical-spine boundary | 🔲 TODO |
| W0.2 | Freeze and verify the exact source/import dependency map | 🔲 TODO |
| W0.3 | Freeze MVP contracts, omissions, and acceptance fixture | 🔲 TODO |
| W1.1 | Implement the generic profile-driven recipe/composition seam | 🔲 TODO |
| W1.2 | Create the carrier-only U0 package and app profile/schema graph | 🔲 TODO |
| W1.3 | Scaffold CLI, registry row, research admission, L2 recipe metadata, providers, and proof SSOTs | 🔲 TODO |
| W2.1 | Prove a required Apps Research producer bundle in replay/live modes | 🔲 TODO |
| W2.2 | Validate and admit the immutable v2 bundle without native consumer claims | 🔲 TODO |
| W2.3 | Enter canonical core U0, L1, and L0 | 🔲 TODO |
| W2.4 | Drive generic core C0 and PA from app profiles | 🔲 TODO |
| W3.1 | Implement serial 11-lane L2 execution | 🔲 TODO |
| W3.2 | Configure generic core section GateMesh enforcement | 🔲 TODO |
| W3.3 | Run proof-class-aware core judges, one bounded repair, and lane acceptance | 🔲 TODO |
| W4.1 | Assemble locked and generated resume content | 🔲 TODO |
| W4.2 | Run core aggregate checkout/gates/judge and one core Exit/X3 | 🔲 TODO |
| W4.3 | Commit final JSON/Markdown/DOCX only through core UWG | 🔲 TODO |
| W4.4 | Seal core product terminal, run core L6, then emit verification closeout | 🔲 TODO |
| W5.1 | Prove inventory/coverage schemas, units, gates, and negative paths | 🔲 TODO |
| W5.2 | Prove deterministic replay, artifact integrity, and `MVP_SCOPE_ACCOUNTED` | 🔲 TODO |
| W5.3 | Prove a fresh live Apps Research → 11-lane `LIVE_REFERENCE_VERIFIED` run and close out | 🔲 TODO |

---

## Architecture Decision

### Confirmed target: declarative reference app on the canonical core spine

The executable app is small because it owns only app policy, research ingress validation, provider
adapters, and the L2 resume recipe. It does **not** own the stage spine. A narrow generic core change
allows validated app recipe metadata/profile refs to register without any app-specific core literal;
the public core spine remains the sole U0→L6 authority.

```text
apps_rg_simple/
├── __init__.py
├── __main__.py
├── cli.py
├── README.md
├── config/domain_contract/
│   ├── runtime_customization_package.yaml
│   ├── ingress_contract.yaml
│   ├── field_map.yaml
│   ├── l0_route_profile.yaml
│   ├── c0_retrieval_profile.yaml
│   ├── prompt_profile.yaml
│   ├── exit_profile.yaml
│   ├── judge_rubric.yaml
│   ├── threshold_profile.yaml
│   ├── output_write_profile.yaml
│   ├── meta_feedback_profile.yaml
│   └── sections.yaml
├── templates/                 # one template per generated lane
├── rubrics/                   # one shared rubric shape + per-lane data
├── schemas/                   # ingress, section output, candidate resume, app receipts
├── examples/
├── research/                  # immutable v2 reader, admission gates, reference-only receipt
├── l2_recipe/
│   ├── registry.py            # app-owned metadata consumed by generic core resolver
│   ├── lane_runner.py         # serial recipe, no root authority
│   ├── section_packets.py     # C0/PA/gate/judge inputs for generic engines
│   └── candidate_assembly.py  # in-memory proposed resume only
├── providers/                 # app adapters implementing public core provider ports
├── rendering/                 # proposed bytes only; no durable product write
└── proof/                     # port/omission/claim verifiers

agentic_core/                  # exact paths frozen in W0 after author gate + source/import inventory
└── <generic profile-driven recipe/composition seam only>

apps_shared/integrations/app_registry.py
└── <one declarative apps_rg_simple GovernedAppEntry; no runtime branch>

tests/
├── unit/apps_rg_simple/
├── integration/apps_rg_simple/
└── e2e/apps_rg_simple/
```

Repository-native constraints:

- do not add a nested `pyproject.toml`, second dependency lock, second governance tree, or app-local
  test root;
- keep the package explicitly `REFERENCE_ONLY` in its README, CLI banner, and run manifest;
- keep its shared app-registry row declarative and reference-scoped; registry conformance cannot raise
  the product claim ceiling;
- require a producer-owned Apps Research bundle for every run eligible for replay/live E2E status;
- keep producer bytes immutable and expose only a local `external_research_admission` receipt;
- keep the app U0 contribution carrier-only: package ingress/field-map/profile refs for canonical core
  U0 to validate; no app U0 routing, retrieval, execution, judging, approval, or write;
- enter through `run_integrated_single_action_spine`; do not call core U0/L1/L0/C0/PA/GateMesh/
  judge/Exit/X3/UWG/L6 internals directly;
- let app L2 code build candidate outputs and evidence packets only. Generic core engines interpret
  C0/PA/gate/judge/Exit/write/meta-feedback profiles and remain the recorded producer components;
- require the CoreAdditionAuthorGateReceipt, exact source/import inventory, core boundary audit, structure gate,
  duplicate/registry proof, runtime producer-component proof, and no-shadow gate before implementation;
- treat `check_no_shadow_spine.py` as one signal, not sufficient proof by itself, because an import-free
  local reimplementation could evade its primary sequence detector.

### Rejected for this plan

1. **Copy current `apps_rg` wholesale** — fails the simplification objective and carries current
   product subtleties into the new folder.
2. **Reimplement U0/L1/L0/C0/PA/GateMesh/judges/Exit/X3/UWG/L6 under `apps_rg_simple`** — creates a
   forbidden semantic shadow spine and cannot be made canonical by labeling it `REFERENCE_ONLY`.
3. **Add an `apps_rg_simple` literal/branch to the current core registry** — creates app leakage.
   Registration must be generic, package/profile-driven, digest-bound, namespace-constrained, and
   covered by existing-app regression tests.
4. **Use the production `apps_rg` CLI behind a thin wrapper** — produces a smaller CLI, not a smaller
   runtime.
5. **Reimplement Apps Research inside `apps_rg_simple`** — duplicates an app-owned producer, risks
   drift, and obscures which research behaviors were ported versus externally reused.
6. **Treat a manual targeting brief as the Apps Research stage** — bypasses U0, grounded retrieval,
   model-backed X2, canonical Exit, atomic publication, and byte-level admission.
7. **Downgrade to fixtures/documentation only** — boundary-clean but fails the requested live
   model-to-final-resume outcome.

The target-path branch is resolved: `apps_rg_simple/` is repository-relative to
`C:\Git\Agentic-Workflow-FRESH`.

---

## Minimal Contract and Handoff Model

Apps Research remains a separate producer. The E2E proof harness runs local preflight, then the
producer, then admission and the simple consumer:

```powershell
python -m apps_rg_simple preflight --request <request_yaml> --proof-class <replay_or_live>
python -m apps_research --target-company <company> --target-role <role> --jd <jd_path>
python -m apps_rg_simple verify-research <producer_run_dir_or_briefing_md> --preflight-receipt <preflight_receipt>
python -m apps_rg_simple run --request <request_yaml> --preflight-receipt <preflight_receipt> --research-bundle <producer_run_dir_or_briefing_md>
```

The Apps Research command must exit 0 and print one exact
`artifact=<producer-owned briefing.md>` record. A live proof must bind all commands to one preflight
proof session and prove the bundle is fresh; replay may use a recorded immutable bundle.
`apps_rg_simple` never imports or rewrites producer code or bytes.

Before core U0, the local validator emits
`apps_rg_simple.external_research_admission.v1`, containing at minimum:

```text
authority_class=REFERENCE_ONLY
producer_authority_observed=true
native_v2_consumer_authority=false
producer_app_id=apps_research
producer_manifest_consumer_app_id=apps_rg
reference_runtime_consumer=apps_rg_simple
producer_run/request/trace/tenant identity
target_company/target_role/normalized_jd_digest/brief_digest
u0/gate_mesh/x1/x2/x3/runtime_exhaust statuses and refs
bundle_manifest/commit_marker/artifact digests
generation/judge provider-model identities and independence result
admission_status/reason_codes
```

It must not invoke the native Apps RG validator, emit
`apps_research_handoff_validation_receipt.json`, relabel the producer manifest consumer, or call this
stage canonical `APPS_RG_U0`. Producer X3D authorizes only the exact briefing bytes. The later core
root X3/UWG path separately controls final resume products.

App-owned L2 sub-artifacts use one small envelope; canonical stage receipts retain their core schemas
and `producer_component` values:

```json
{
  "schema_version": "apps_rg_simple.l2_artifact.v1",
  "run_id": "...",
  "request_id": "...",
  "stage": "L2_SECTION_CANDIDATE",
  "producer": "apps_rg_simple.l2_recipe.lane_runner",
  "consumer": "agentic_core.generic_gate_mesh",
  "status": "CANDIDATE_READY",
  "created_at_utc": "...",
  "input_refs": [{"path": "...", "sha256": "sha256:..."}],
  "output_refs": [{"path": "...", "sha256": "sha256:..."}],
  "reason_codes": [],
  "attempt": 1
}
```

Required rules:

- one local `run_id` and `request_id` across the app recipe, bound to the core runtime identity and one
  immutable preflight proof;
- the external producer child identity is immutable and explicitly bound to the local parent proof;
- producer bytes remain in the producer-owned directory; any local snapshot is immutable and
  digest-bound to that authority path;
- content digests, not timestamps, bind handoffs;
- no stage mutates an upstream artifact;
- core consumers validate schema, package/profile refs, producer identity, run identity, digest, and
  proof-class-appropriate PASS status before use;
- failures still emit a terminal receipt with exact reason codes;
- a retry creates a new attempt artifact and never overwrites attempt 1;
- the authoritative attempt is named explicitly before aggregation.

### Stage contract table

| Stage | Input | Output | Required authority / gate |
|------|-------|--------|---------------------------|
| REFERENCE_PREFLIGHT (app prerequisite) | `RunRequest` + config | `ReadinessReceipt` | Resume, JD, target, research bundle mode, source revision, and required provider readiness; no supplied-brief bypass or signed production-continuation claim |
| APPS_RESEARCH_U0 (external observed) | Company/role/JD | `apps_research_u0_receipt.json` | PASS, allowed/passed authority, raw/normalized digests, complete child identity |
| APPS_RESEARCH_RUNTIME (external observed) | Validated research request | Grounded brief + `runtime_exhaust_bundle.json` | Fresh nonempty SearXNG evidence, valid targeting-brief contract, provider receipts, no blocked/empty result |
| APPS_RESEARCH_EXIT (external observed) | Sealed brief + receipts | GateMesh/review/Exit receipts | Exact G5/G6/G7/G21/G24/G26 PASS; model-backed G6; no FAIL/UNKNOWN/WARN/missing; exact X3D |
| HANDOFF_BUNDLE_COMMIT (external observed) | Authorized producer artifacts | v2 manifest + commit marker | Required artifacts fsynced, manifest bytes/lengths/digests exact, marker last, atomic final directory, no exposed staging |
| EXTERNAL_RESEARCH_ADMISSION | Immutable producer run directory | `ExternalResearchAdmission` | Schema/identity/JD/brief/policy/blueprint/freshness/provider/gate/Exit/runtime/marker/artifact checks all PASS; native authority false |
| CORE U0 | Raw request + runtime customization package + admission | Core `ValidatedRequest` | Carrier-only schema/field-map/profile-ref/package-digest validation; targeting brief is data-only |
| CORE L1 | Core `ValidatedRequest` | Core plan contract | Fixed 11-lane recipe metadata, locked fields, dependencies, expected artifacts; no app L1 implementation |
| CORE L0 | Core plan + route profile | Core `RouteContract` | Generic interpreter selects one generation route and independent judge route; no app routing code |
| CORE C0 | Source facts + targeting inputs + retrieval profile | Core evidence contract | Generic coordinator enforces source-fact authority; JD/brief/research sources are `targeting_only` |
| CORE PA | Evidence + prompt profile + output schema | Core compiled-prompt artifact | Generic resolver enforces stable slots, no fabrication, source separation, and digest binding |
| APP L2 recipe | Core compiled inputs + app lane manifest/provider ports | Section candidates + proof/provider packets + assembled candidate | Serial 11-lane generation, strict JSON, bounded repair, no root authority or durable product write |
| CORE section GateMesh | Section candidate + evidence + app gate profile | `GateBundle` | Schema, product shape, proof coverage, fact existence, style, and dependency gates; UNKNOWN non-PASS |
| CORE section judge | Compact packet + rubric/threshold profile | `JudgeVerdict` | Live requires independent model-backed evidence; replay uses recorded replay evidence and cannot claim model-backed judging |
| APP lane acceptance | Core gate/judge results + attempt refs | `LaneAcceptanceRecord` | PASS/REVIEW/BLOCK for L2 aggregation only; explicitly not Exit, X3, or product authority |
| APP candidate aggregation | 11 accepted lane records + locked copy | Candidate resume + aggregate packet | Exactly 11 lanes, no stale/duplicate/missing input, locked-copy integrity; proposed bytes only |
| CORE aggregate GateMesh/judge | Candidate + claim ledger + app profiles | Aggregate gate/judge receipts | Completeness, chronology, identity, repeated metrics, proof coverage, coherence; proof-class-aware judge evidence |
| CORE Exit X1/X2/X3 | Sealed L2/runtime receipts + aggregate results | One core Exit review/disposition/runtime-exhaust chain | Core alone checks identity/completeness, aggregates X2, and emits exactly one root X3; UNKNOWN non-PASS |
| CORE UWG | Exit-authorized commit packet + proposed outputs + write profile | Core validation/commit receipt | Core alone admits allowlisted atomic final-product writes and verifies output hashes |
| CORE L6 shadow | Sealed product-terminal exhaust + meta-feedback profile | Core shadow report | Post-product-terminal, pre-runtime-closeout core consumer only; future-run proposals cannot mutate current run or rescue X3 |

Judge evidence classes are explicit:

- `LIVE_MODEL_BACKED` — real provider/model/attempt receipt, independence PASS; required for live lane,
  aggregate, and `LIVE_REFERENCE_VERIFIED` claims.
- `RECORDED_REPLAY` — digest-bound fixture/cassette verdict used only to prove contract flow. It may
  produce a proof-class-scoped `PASS` lane record and `MVP_SCOPE_ACCOUNTED`, but never
  `MODEL_BACKED_JUDGED`, live provider, or product-authority claims.

### Apps Research gate accounting

No Apps Research gate may disappear behind the phrase “external dependency.” The source inventory and
coverage matrix must separately account for:

1. **Configured research runtime gates** — G1 injection, G2 secret leakage, G3 PII, G4 unsafe
   instructions, G5 answer present, G6 relevance, G7 evidence, G8 citation integrity, and G10
   multi-step trajectory. G7/G8/G10 are required for this factual, cited, multi-step route. G9 cache
   semantic compatibility and G27/G28 commit safety/policy are N/A only with explicit reasons because
   cache is deferred and producer Exit uses `commit_requested=false`.
2. **Producer handoff GateMesh authority** — exactly G5, G6, G7, G21 output schema, G24 replay/digest
   eligibility, and G26 Exit eligibility, all PASS. G6 must bind a model-backed independent Gemini
   verdict at or above 0.75; deterministic semantics or bridge confidence cannot substitute.
3. **Admission gates** — U0 PASS; current identity; normalized JD and brief bytes; freshness ≤7 days;
   expected source-bound `external_openai` / `gpt-5.4-mini-2026-03-17` generation metadata; model-backed
   `gemini_pro` / `gemini-3.1-pro-preview` identity; provider independence; sealed
   workflow; X1 PASS; exact six-gate X2 PASS; exact X3D; runtime-exhaust linkage; committed marker;
   contained artifact paths; and every declared byte length/digest.

If the current producer bundle does not expose a separate receipt for a configured runtime gate, W0
must classify that item explicitly. The simple admission layer may re-evaluate a deterministic safety
gate as `IMPLEMENTED_APP_SIMPLIFIED`, but must not report it as a producer-executed authority receipt.

---

## Resume Section Manifest

Keep the current dependency semantics but execute serially:

| Order | Lane | Depends on | Required product shape |
|------:|------|------------|------------------------|
| 1 | `competencies` | — | Grounded categories/items with source-fact claim coverage |
| 2 | `unify_bullets` | — | Exact configured bullet count; one sentence each; unique proof facts |
| 3 | `ibm_bullets` | — | Exact configured bullet count; one sentence each; unique proof facts |
| 4 | `insurtech_bullets` | — | Exact configured bullet count; one sentence each; unique proof facts |
| 5 | `ey_bullets` | — | Exact configured bullet count; one sentence each; unique proof facts |
| 6 | `unify_narrative` | `unify_bullets` | One bounded narrative sentence derived from sealed bullets/facts |
| 7 | `ibm_narrative` | `ibm_bullets` | One bounded narrative sentence derived from sealed bullets/facts |
| 8 | `insurtech_narrative` | `insurtech_bullets` | One bounded narrative sentence derived from sealed bullets/facts |
| 9 | `ey_narrative` | `ey_bullets` | One bounded narrative sentence derived from sealed bullets/facts |
| 10 | `executive_summary` | lanes 1–9 | Evidence-fit summary with one claim-ledger row per sentence |
| 11 | `headline` | `executive_summary` + proof-bearing lanes | One-line final positioning within configured segment/length bounds |

Locked/pass-through content is copied byte-for-byte from the source resume and never sent to the
model for rewriting: identity/contact fields, employer names, titles, locations, dates, education,
certifications, and configured early-career/source-only blocks.

The final assembly contract must explicitly account for these non-generated sections/fields:

| Locked content | Required treatment |
|----------------|--------------------|
| Candidate header/contact | Source-only, byte-preserved where represented, excluded from model prompts |
| Employer/title/location/date role headers | Source-only structural fields joined to the matching generated role sections |
| `early_career` | Locked embedded section in canonical output order |
| `education` | Locked embedded section in canonical output order |
| `certifications` | Locked embedded section in canonical output order |

### Per-lane artifact contract

Each lane artifact set must contain:

```text
sections/<section_id>/
├── core_c0_evidence_ref.json
├── core_compiled_prompt_ref.json
├── section_input_usage_ledger.json
├── core_c0_proof_pool_ref.json
├── provider_request.json
├── provider_response.json
├── l2_execution_packet.json
├── sealed_l2_artifact.json
├── l2_recipe_receipt.json
├── l2_output.json
├── claim_ledger.json
├── core_gate_mesh_result.json
├── core_judge_verdict.json
├── lane_acceptance_record.json       # L2 aggregation only; not Exit/X3 authority
└── lane_manifest.json
```

The app owns the input-usage/provider/L2/candidate/claim/lane-acceptance artifacts. Canonical core owns
the C0 proof-pool, PA, GateMesh, and judge receipts; the section set contains their digest-bound refs
or canonical artifacts, never app aliases. Parity tests prove the full set shares same-run identity and
digests. The
source app's per-lane Exit/disposition machinery is explicitly `IMPLEMENTED_APP_SIMPLIFIED`: lane records
gate L2 aggregation only, while the single canonical core Exit after aggregate review owns root
X1/X2/X3 authority.

---

## Keep / Simplify / Defer Matrix

| Concern | Decision | Simple-runtime treatment |
|---------|----------|--------------------------|
| 11-lane DAG and dependency order | KEEP | One YAML manifest; serial executor |
| Locked resume sections and candidate/role headers | KEEP | Byte-preserved source-only fields plus canonical early-career, education, and certifications placement |
| U0 runtime package/profile authority | KEEP/SIMPLIFY | App owns one complete package/profile graph; canonical core U0 validates carrier/schema/field-map/digests |
| Product preflight continuation | SIMPLIFY | Local input/config/provider readiness receipt; no signed production continuation |
| L1 planning capsule and L0 route receipts | KEEP/SIMPLIFY | Core emits immutable plan/route/replay receipts from app profiles; omit ambiguity and advanced graph-policy registries |
| Canonical core spine | KEEP | Public core entrypoint is the only U0→Exit route; no app-owned stage orchestration |
| Generic recipe registration | EXTEND GENERIC CORE | Resolve validated app-owned recipe metadata/profile refs without app literals, arbitrary imports, or caller-supplied product callables |
| Core C0/PA interpretation | KEEP/SIMPLIFY | Generic core engines consume small retrieval/prompt profiles; no local C0/PA authority or second wrapper |
| Source-fact authority and claim ledger | KEEP | Minimal fact graph keyed by stable `source_fact_id` |
| C0 graph value | SIMPLIFY | Tag/employer/role adjacency over canonical JSON; no SQLite projection, embedding, allocation calibration, or sibling-frontier search |
| Prompt authority | KEEP | Generic core compiler consumes the app prompt profile and strict output schema |
| Provider execution | SIMPLIFY | One provider protocol, one live generation adapter, one replay adapter |
| Section input/proof-pool bindings | KEEP | App seals used-input/L2 bindings; canonical core C0 owns the eligible-source-fact proof pool and receipt |
| Sealed L2 and Exit handoff authority | SIMPLIFY | Preserve sealed L2→core Exit handoff and one root X1/X2/X3; replace source per-lane Exit with non-authorizing lane acceptance records |
| Section gates | SIMPLIFY | Generic core GateMesh consumes shared plus data-driven lane gate profiles |
| Section judges | KEEP | Generic core judge harness consumes compact packets/rubrics; live model-backed and replay-recorded evidence remain distinct |
| Same-run fingerprint, sealed index, WARN/REVIEW terminal policy | SIMPLIFY | Retain same-run sealing and fail-closed policy; no production release-mode/whole-graph machinery |
| Production aggregation ordering | SIMPLIFY | Deterministic aggregate gates run before the whole-resume judge; the changed order is explicit and tested |
| Aggregate judge | KEEP | Generic core judge harness runs a separate whole-resume rubric; live proof is model-backed |
| Repair | SIMPLIFY | At most one bounded repair attempt using deterministic/judge feedback; no pools or ladders |
| X1/X2/X3 | KEEP | Core Exit emits explicit receipts and exactly one root X3; the app never emits X3 |
| Final JSON/Markdown/text/DOCX products | KEEP | App returns proposed bytes; core UWG alone may commit final products after valid core Exit authorization |
| UWG | KEEP/SIMPLIFY | Core consumes an app write profile for idempotent allowlisted atomic commit/hash proof; omit production refresh/rollback orchestration |
| Minimal terminal closure | SIMPLIFY | Core product-terminal seal, then core L6, then app verification closeout; no production authorization state machine or stage-ledger seal |
| L6 shadow | KEEP | Post-product-terminal, pre-runtime-closeout core consumer uses app meta-feedback profile; future-run-only and non-authoritative |
| Per-section L6 v40/runtime-exhaust and Apps Eval binding chain | DEFER | No production per-lane v40 spans, microstep observations, closure, or evaluator-binding artifacts |
| Parallel dispatch | DEFER | Serial correctness first |
| R1A/R1B caches | DEFER | No cache in MVP |
| Apps Research producer execution | REUSE REQUIRED | Every replay/live E2E run requires a producer v2 bundle; live proof freshly runs the read-only product CLI with SearXNG/OpenAI/Gemini |
| Apps Research internal hops/retrieval/provider machinery | EXTERNAL, NOT PORTED | Prove it through producer receipts/source regressions; do not copy or import it into `apps_rg_simple` |
| Apps Research configured runtime gates | KEEP/SIMPLIFY | Account for G1-G10/G27/G28 individually; verify producer receipts where exposed and locally re-evaluate only explicitly simplified deterministic checks |
| Apps Research exact handoff GateMesh/Exit/atomic commit | KEEP | Require G5/G6/G7/G21/G24/G26 PASS, model-backed X2, exact X3D, and byte-valid COMMITTED bundle |
| Existing v2 bundle compatibility admission | SIMPLIFY | Local reference-only schema/identity/digest/artifact validator and `external_research_admission` receipt |
| Native Apps Research → Apps RG Simple consumer authority | NOT APPLICABLE | v2 is hard-coded to `apps_rg`; preserve source bytes, emit no native consumer receipt, and cap claims |
| Caller-authored/manual brief product ingress | FORBID | Diagnostic-only; never equivalent to Apps Research or eligible for replay/live success |
| Self-consistency candidate pools | DEFER | One generation plus one bounded repair maximum |
| Multi-provider judge panels/quorum/failover | DEFER | One independent section judge route and one aggregate judge route |
| Patch-run/reuse of accepted lanes | DEFER | Fresh run only |
| C0.3 SQLite traversal, whole-resume allocation, calibration W6–W9 | DEFER | Preserve fact IDs and proof binding only |
| L5 certification and product authority ledgers | DEFER | Reference-only output cannot become canonical product authority |
| Apps Eval | DEFER | No evaluator-bound grade, rescue, or authorization claim |
| Fact-vector writeback / `STATE_PROMOTION` | DEFER | No post-X3 future-run state promotion |
| OTel/L7 extended observability | DEFER | Small stage timing and attempt ledger only |
| Thirteen production operator outputs, BCG RCA, and mandatory-output authority | DEFER | One narrower reference `RUN_SUMMARY.md`, runtime receipt, and machine-readable run manifest |

---

## Wave 0 — Authorize Core Seam and Freeze Boundary/Source Contract

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: AUTHOR_GATE_BOUNDARY_AND_SOURCE_INVENTORY

**Authorization**: REQUIRED — after plan approval but before any implementation edit, produce and
validate `artifacts/governance/core_addition_author_gate/apps-rg-simple-end-to-end-spine-e6a41d.json`.
The receipt authorizes only a generic profile-driven core registration/composition seam; it does not
authorize app-specific core logic.

**Phases**:

- **W0.1** — Core author gate and canonical-spine boundary | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.2** — Freeze exact source/import and generic-seam map | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.3** — Freeze contracts, dispositions, omissions, and proof fixture | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Produce the CoreAdditionAuthorGateReceipt; bind the plan ID, proposed generic core behavior,
   candidate paths, no-app-literal invariant, tests, rollback, and receipt digest. Validate it before
   any core or app implementation file is created.
2. Confirm `apps_rg_simple/` is permitted as a root `apps_*` package only when it enters the public
   canonical core spine. Prohibit local U0/L1/L0/C0/PA/GateMesh/judge/Exit/X3/UWG/L6 implementations and record
   `REFERENCE_ONLY` product classification. Freeze the one declarative shared `GovernedAppEntry` and
   canonical callable shape required by app-registry conformance; reject any registry dispatch branch.
3. Map exact source symbols and import/reference sites reachable from Apps Research CLI/U0/governed
   run/company-brief engine/handoff publisher, the v2 consumer validator, the authority contract,
   Apps RG product/core entry, stage graph, section registry, rollup, assembler, post-X3,
   product-output, terminal-output, and L6 roots. Record direct/transitive import evidence,
   side-effect call sites, registry/factory checks, duplicate-symbol searches, and targeted tests.
   Optional ADG output may supplement but cannot gate this inventory.
4. Map the current public core entrypoint, L2 resolver, profile resolver, generic C0/PA engines,
   GateMesh, judge panel, Exit, UWG, product-terminal seal, and L6 consumer. Freeze the smallest generic seam
   needed for app-owned recipe metadata/profile refs, including namespace/path/digest protections.
5. Freeze the exact source revision and generate `source_inventory.v1.json`; resolve every seed,
   bind every source hash, and keep discovery errors explicit.
6. Freeze the required upstream stage prefix, producer artifact set, configured research gates, exact
   six-gate handoff GateMesh, provider-independence requirements, atomic commit contract, hard-coded
   consumer identity/claim ceiling, stage table, 11-lane manifest, locked fields/sections, section gate
   catalog, judge packets, aggregate checks, outputs, terminal contract, and live acceptance fixture.
7. Generate `port_coverage.v1.json` with exactly one disposition per source item. Every app-
   implemented semantic has one app owner and parity tests; every changed-core item binds the author
   receipt and generic regressions; every reused-core item binds canonical producer-component proof;
   every simplified/dropped mechanism binds one omission ID.
8. Generate `omission_ledger.v1.json` and `claim_ceiling.v1.json`. Classify all preliminary source
   deltas in this plan plus anything found by deterministic source discovery; do not silently collapse mandatory
   production stages into generic prose.

**Acceptance**:

- Target root is exactly `C:\Git\Agentic-Workflow-FRESH\apps_rg_simple` and all planned paths are
  repository-relative.
- The core-addition receipt exists, validates, matches `author_gate_receipt_ref`, and authorizes the
  exact frozen generic surface—nothing broader.
- Structure and boundary evidence permits a declarative app + app L2 recipe on the canonical core
  spine; no local shadow-stage module is planned.
- App-registry design has exactly one declarative classification row, points at the app's public
  core-entering callable, and is explicitly non-authorizing for product claims.
- Source/import inventory provenance names the exact commands, roots, references, and source hashes.
- No broad implementation file is created before authorization, boundary, and inventory checks pass.
- Source inventory status is `COMPLETE`, every discovery root resolves, and discovery error count is 0.
- Coverage count equals inventory count; unclassified, duplicate-disposition, and unknown-disposition
  counts are 0.
- The parity matrix has no ownerless/testless app implementation, unauthorized changed-core row, or
  reused-core row lacking producer-component/regression proof.
- Every Apps Research item is classified as required external, locally implemented admission,
  explicitly simplified, or omitted; no external behavior is described as “ported.”
- Boundary checks approve the Apps Research process/file contract, forbid sibling-app imports, and
  allow only the public core entrypoint/contracts/provider ports—not private core stage imports.
- The frozen core design is package/profile-driven, namespace-constrained, digest-bound, generic for
  any valid `apps_*`, and contains no app-specific names, gates, thresholds, or branches.
- Every simplified or omitted item has one complete omission record and mechanically enforced
  forbidden claims.
- W0 emits a baseline proof result of `MVP_SCOPE_ACCOUNTED=NO`; it cannot advance merely because the
  manifests exist.
- Any app-specific core edit, unapproved core path, or need for a second spine/registry stops and
  requires a revised author-gate receipt and plan.

---

## Wave 1 — Generic Core Seam and Declarative App Package

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: GENERIC_CORE_AND_U0_CONTRACTS

**Phases**:

- **W1.1** — Generic recipe/composition seam | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Carrier-only U0 package and profiles | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — CLI, registry row, research admission, L2 recipe/provider/proof SSOTs | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Refactor the core L2 resolver to a generic app-recipe protocol resolved from validated app identity
   and package/profile metadata. Enforce `apps_*` namespace containment, exact schema/digest, one
   metadata provider, and no arbitrary caller-supplied callable/import path. Preserve existing
   `apps_rg` behavior through generic convention/shape compatibility, not an app-name branch.
2. Reuse existing generic C0/PA/GateMesh/judge/Exit/UWG/L6 engines. If W0 proves a composition link is
   missing, add only the approved generic profile-driven link and bind it to the author receipt.
3. Create `apps_rg_simple/config/domain_contract/runtime_customization_package.yaml`, ingress schema,
   field map, route/retrieval/prompt/exit/judge/threshold/write/meta-feedback profiles, and exact
   digests. The app packages refs only; canonical core U0 validates and preserves them.
4. Create the root package with `preflight`, `run --preflight-receipt --research-bundle`,
   `verify-research`, `verify-run`, `verify-port`, and `render-summary`. `run` calls only the public
   core entrypoint; it does not call the resolver or stage internals directly.
5. Add the one shared `GovernedAppEntry` pointing at that public app callable. Keep routing target,
   capability token, and proof prefix unique; add no app-specific execution logic to `apps_shared`.
6. Define app-owned L2 recipe metadata, immutable section/candidate DTOs, external producer reference,
   and local reference-only research admission receipt. Persisted app types have JSON Schemas.
7. Implement one external v2 bundle reader/admission validator and one canonical JSON digest helper.
   Do not duplicate core handoff enforcement and do not emit the native Apps RG consumer receipt.
8. Put upstream stage order, expected producer schema hash/artifact set, research runtime and handoff
   gates, freshness, provider identities, stage/lane order, dependencies, downstream model routes,
   timeouts, token caps, output filenames, retry count, source inventory, port coverage, omission
   ledger, and claim ceiling in small versioned config files with matching schemas.
9. Implement adapters for public core generation/judge/replay ports; keep SDK code out of recipe,
   GateMesh, and profile interpretation.
10. Write the U0 customization receipt and generic-core migration/addition receipt with exact changed
   paths, digests, tests, and boundary classification.

**Acceptance**:

- Package installs in a clean virtual environment.
- `python -m apps_rg_simple --help` succeeds without provider credentials.
- The author-gate receipt is valid before core edits; core addition/migration and U0 customization
  receipts validate after implementation.
- Contract round-trip tests cover all app persisted types and core generic registry metadata.
- Handoff validation rejects schema, digest, run-id, stage, and producer mismatches.
- Research admission rejects a missing/legacy/stale/uncommitted/tampered/wrong-identity bundle, any
  non-PASS required gate, non-model-backed G6, non-X3D Exit, provider-identity mismatch, or a caller
  attempt to substitute raw briefing text.
- `verify-port` rejects stale source hashes, missing/duplicate inventory rows, missing/duplicate/unknown
  dispositions, incomplete omissions, and unsupported claims before any runtime proof is considered.
- Core AST/literal tests find no `apps_rg_simple` reference or new app-specific branch. Existing
  `apps_rg` recipe resolution and receipts remain regression-equivalent.
- App-registry conformance passes; the row points only at the public app callable, is unique, and adds
  no shared dispatch logic or product-authority claim.
- Malicious namespace/path/digest/multiple-provider metadata is rejected before import/execution.
- App AST/import checks find no sibling-app import and no private core U0/L1/L0/C0/PA/GateMesh/judge/
  Exit/X3/UWG/L6 import; the
  public core entrypoint and ports are allowed.
- Runtime receipts prove core producer components for U0/L1/L0/C0/PA/GateMesh/judge/Exit/UWG/L6.
- Repository structure, core boundary, genericity, duplicate, and fail-closed no-shadow-spine gates
  pass; no app-local U0/L1/L0/C0/PA/GateMesh/judge/Exit/X3/UWG/L6 implementation exists.

---

## Wave 2 — Required Apps Research Upstream and Canonical Core Front Spine

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: RESEARCH_TO_PRE_MODEL

**Phases**:

- **W2.1** — Required Apps Research producer proof | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Immutable v2 admission | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Canonical core U0/L1/L0 | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.4** — Profile-driven core C0/PA | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Local fresh preflight validates resume/JD/target/config/source revision, selects
   `RECORDED_REPLAY` or `FRESH_LIVE`, and rejects raw/manual briefing input. It emits a
   non-authorizing readiness receipt before downstream work. Live mode also rejects
   `--apps-e2e-dry-run`, `--dry-run`, active mock/synthetic research flags, missing credentials, and
   any command shape other than the frozen product CLI route.
2. Replay requires an immutable recorded producer run and can emit only replay proof. The live proof
   harness first runs `python -m apps_research --target-company ... --target-role ... --jd ...`, binds
   exit 0 and the exact `artifact=<briefing.md>` record, and then passes that fresh producer directory
   to `apps_rg_simple`. The source resume is never included in that producer command.
   Replay evaluates freshness against an immutable captured `as_of` clock; live evaluates against the
   current proof-session clock. Replay never implies current freshness.
3. Validate the producer U0 receipt, complete identity, target/JD/brief digests, freshness, expected
   artifact set, contained paths, byte lengths/hashes, staging/atomic-commit protocol, COMMITTED marker,
   targeting-brief contract, evidence/source register, provider metadata and independence.
4. Validate the configured research-gate accounting plus exact producer GateMesh G5/G6/G7/G21/G24/
   G26 PASS, model-backed X2 score ≥0.75, sealed workflow, X1/X2, exact X3D, and runtime-exhaust links.
   Emit the local `external_research_admission` input receipt without modifying or impersonating the
   native v2 consumer contract.
5. Build the app-owned U0 customization-package carrier with immutable resume/JD/admitted-brief/
   admission refs and the validated
   runtime customization package, then call the public canonical core entrypoint.
6. Core U0 validates ingress/schema/field map/profile refs/package digest and stamps runtime identity.
   Core L1 creates the fixed 11-lane plan and replay key. Core L0 interprets the route profile, selects
   one generation route plus one independent judge route, and emits fail-closed route receipts.
7. The generic core C0 coordinator consumes the retrieval profile, normalizes source-resume facts into
   stable IDs, selects bounded per-lane evidence, and marks JD/admitted brief/research sources
   `targeting_only`.
8. The generic core PA resolver consumes the prompt profile/template/schema and emits byte-stable
   compiled inputs bound to source facts, admission, package, route, and content digests.

**Acceptance**:

- Invalid/missing Apps Research evidence fails before core U0 and before any Apps RG Simple model call.
- Live proof observes fresh Apps Research U0/runtime/Exit/commit artifacts in order and no research
  stage is reused, skipped, duplicated, or marked `NOT_RUN`.
- Live proof records the sanitized producer argv/environment classification and rejects dry-run,
  mock, fixture, synthetic, or offline substitution as real provider evidence.
- Replay exercises the same admission checks but cannot emit live-research or model-backed-live claims.
- The source v2 identity remains `consumer_app_id=apps_rg`; the local receipt says
  `reference_runtime_consumer=apps_rg_simple` and `native_v2_consumer_authority=false`.
- Research configured gates and the exact six-gate GateMesh are individually accounted; no missing,
  FAIL, UNKNOWN, WARN, or unexplained N/A is accepted.
- No downstream resume generation or judge call occurs before core dispatches the registered L2 recipe;
  upstream Apps Research retrieval/generation/judging is expected and separately receipt-bound.
- Changing the frozen config/profile, plan, route, or replay key invalidates the downstream handoff.
- L1 and L0 are deterministic for fixed config and inputs; FAIL or UNKNOWN route readiness blocks.
- Core—not app code—produces U0/L1/L0/C0/PA receipts with canonical producer-component identities.
- No app-local U0/L1/L0/C0/PA/GateMesh/judge/Exit/X3/UWG/L6 implementation or direct stage call exists.
- Every generated claim must cite one or more existing source-fact IDs.
- Removing or changing a cited fact invalidates the downstream handoff.
- Prompt compilation is byte-stable under fixed inputs and cannot let JD/briefing/research sources
  become resume-claim proof.
- All 11 compiled prompts validate against their lane schemas and token budgets.

---

## Wave 3 — App Serial L2 Recipe and Core Section Enforcement

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: ELEVEN_LANES

**Phases**:

- **W3.1** — Core-resolved serial app L2 recipe | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Generic core section GateMesh | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — Proof-class-aware core judges, repair, lane acceptance | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. The public core entrypoint resolves the app-owned L2 recipe through the generic registry seam; the
   app CLI never supplies a product callable or invokes the resolver directly.
2. Execute the lane manifest in dependency order. A failed required dependency blocks its dependents
   with an explicit `NOT_RUN_DEPENDENCY_BLOCKED` receipt; it never disappears from the run ledger.
3. Before each provider call, the app seals `section_input_usage_ledger.json`, the L2 execution packet,
   and its input/config/route/research-admission digests; it binds, but does not seal or impersonate,
   canonical `core_c0_proof_pool_ref.json`. Record the admitted brief digest only as targeting context.
4. Use the app provider adapter through the public core port for one strict-JSON generation call per
   lane. Record provider, model, request digest, response
   digest, token counts, latency, finish reason, and parse status.
5. Submit the sealed candidate/evidence packet to generic core GateMesh. It runs shared gates (schema,
   non-empty
   display, claim coverage, source-fact existence, targeting-only
   discipline, provider receipt) plus the lane-specific product-shape gates.
6. Core invokes the compact section judge only after deterministic gates pass. Live mode requires
   `LIVE_MODEL_BACKED`; replay consumes a digest-bound `RECORDED_REPLAY` verdict. The packet contains
   display text, claim ledger, fact abstracts, gate summary, and rubric.
7. If deterministic output or the judge blocks a repairable content defect, allow exactly one app
   provider repair
   call. Missing proof, route/config errors, and dependency failures are not repairable.
8. Re-run core GateMesh and judge on the repaired output. Select the authoritative attempt and emit
   a PASS/REVIEW/BLOCK `LaneAcceptanceRecord` for L2 aggregation. It is not Exit, X3, UWG, or product
   authority.

**Acceptance**:

- The ledger has exactly 11 unique lane rows in the canonical order.
- Every attempted lane has a complete artifact set and every non-attempted lane has an explicit
  blocker receipt.
- Aggregation rejects a lane missing either proof ledger, sealed L2 artifact, core GateMesh receipt,
  core judge receipt, or lane acceptance, even when display text exists.
- A lane whose research-admission or brief digest differs from core U0 is blocked; a lane treating
  research/JD content as candidate evidence fails its proof gate.
- Judges never run on deterministic-gate failure and never modify artifacts.
- Judge transport error, timeout, invalid JSON, or UNKNOWN is non-PASS.
- Repair count is 0 or 1; attempt 1 remains immutable.
- Replay reaches 11 proof-class-scoped PASS lane records with `RECORDED_REPLAY`; it cannot emit
  `MODEL_BACKED_JUDGED`. Live lane PASS requires `LIVE_MODEL_BACKED` and provider independence.
- No per-lane Exit/X3 artifact exists, and runtime producer-component proof attributes section gates
  and judges to generic core engines.

---

## Wave 4 — Candidate Aggregation and Core Exit/UWG/L6

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: PRODUCT_OUTPUT

**Phases**:

- **W4.1** — Assemble proposed locked/generated content | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Core aggregate review and one core Exit/X3 | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — Core UWG product commit | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.4** — Core L6 shadow and closeout | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. App candidate checkout requires one PASS external-research admission, immutable producer
   bundle/marker/brief digests, 11 proof-class-consistent PASS lane acceptance records, proof ledgers,
   matching identities, one same-run fingerprint/sealed section index, and intact locked-copy hashes.
2. Within L2, assemble a proposed structured resume from candidate/role headers, locked early-career/education/
   certifications content, and the 11 authoritative outputs. No model call occurs during deterministic
   merge; the app writes no final product file.
3. Submit the aggregate packet to generic core GateMesh for completeness, chronology, identity preservation, duplicate metrics,
   cross-section proof coverage, narrative/bullet consistency, style, and output schema.
   WARN/REVIEW is terminal non-PASS unless an explicit simple policy resolves it before the judge.
4. Core runs one independent whole-resume coherence judge after aggregate deterministic gates pass. This
   gate-before-judge order intentionally differs from the current production assembler and is bound
   as `IMPLEMENTED_APP_SIMPLIFIED`; live/replay judge evidence classes remain distinct.
5. Hand sealed L2 and aggregate receipts to core Exit. Core alone performs root X1/X2 and emits exactly
   one X3. Preserve `X3A_DENY_REROUTE`, `X3B_ESCALATE_HITL`,
   `X3C_COMMIT_REQUEST_TO_UWG`, `X3D_ALLOW_FINISH`, and `X3E_SAFE_ABSTAIN`; only exact X3D is the
   reference product success code. The upstream producer X3D is separately namespaced and
   authorizes only its briefing bytes; it is never counted as the simple resume root X3.
6. App renderers deterministically return an in-memory candidate bundle for `final_resume.json`,
   `FINAL_RESUME_OUTPUT.md`, `FINAL_RESUME_OUTPUT.txt`, and `outputs/resume.docx`; verify content parity
   before durable output authorization. Renderers cannot alter semantic content.
7. The approved generic core post-Exit path—not app code—constructs the commit packet and invokes core
   UWG using the app write profile. Core UWG validates the reference output root, atomically writes,
   re-hashes bytes, and emits validation/commit receipts. Production rollback and refresh remain omitted.
8. Core seals the minimal immutable `core_product_terminal_receipt.json`, binding the producer and admission
   identities/digests. Record `native_v2_consumer_authority=false`; record Apps Eval, production
   operator outputs, per-section L6 v40 binding, and state promotion as omitted/not run.
9. After core seals the product-terminal receipt—following core UWG when applicable—core L6 consumes sealed runtime exhaust
   plus the app meta-feedback profile and emits shadow patterns/recommendations. It cannot edit prompts,
   gates, outputs, X3, or UWG receipts.
10. Emit `runtime_acceptance.json` only after L6 completes or records an explicit non-success N/A/
    failure. Bind the earlier immutable product-terminal receipt and L6 result; never reopen terminal
    product authority.

**Acceptance**:

- One missing/blocked lane prevents aggregate PASS.
- Aggregate judge cannot override a deterministic gate failure.
- Exactly one root X3 exists and its producer component is core; no lane/app X3 artifact exists.
- Producer X3D, bundle commit, and local admission are present and immutable but cannot authorize or
  rescue the downstream resume root X3.
- A non-X3D run produces no committed final resume.
- All durable final-resume product writes originate from core UWG; producer-owned research authority
  artifacts are the explicit pre-UWG exception.
- JSON/Markdown/text/DOCX render the same section content and pass digest/content parity tests.
- The terminal receipt cannot claim production pipeline/product authority, Apps Eval, state promotion,
  production operator-output parity, or the production per-lane L6 closure chain.
- The immutable product-terminal receipt is sealed before core L6. L6 artifacts are timestamped after
  that boundary, contain no mutation path, and the later runtime-acceptance closeout binds both digests.
- Runtime producer-component verification attributes aggregate enforcement, Exit/X3, UWG, and L6 to
  canonical core surfaces; the app supplies only profiles, packets, candidate bytes, and provider ports.

---

## Wave 5 — Verification and Fresh Live Proof

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: CLOSEOUT

**Phases**:

- **W5.1** — Unit, schema, and negative proof | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Deterministic replay integration | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** — Fresh live research-to-resume run and closeout | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Verification ladder**:

First run the active Apps Research → Apps RG source-contract baseline. These commands prove the
current structural/fixture contract only; they do not by themselves prove fresh live providers:

```powershell
python scripts/governance/codex_readiness.py --json
python ops_scripts/ci/check_apps_research_rg_e2e_contract_freeze.py
python -m unittest tests.unit.ops_scripts.ci.test_apps_research_rg_e2e_contract_freeze -v
python ops_scripts/ci/check_apps_research_rg_handoff_e2e.py
python ops_scripts/ci/check_apps_research_rg_e2e_traceability.py --mode structural
python ops_scripts/ci/check_apps_research_rg_full_chain_e2e.py
python ops_scripts/ci/check_apps_research_rg_e2e_traceability.py --mode evidence
python -m pytest tests/unit/apps_research/test_apps_rg_targeting_brief_contract.py tests/unit/apps_research/test_targeting_brief_grounding_failclosed.py tests/unit/apps_research/test_research_brief_uwg_writer.py -q --tb=short -p no:cacheprovider
python -m pytest tests/governance/test_core_addition_receipt_schema.py tests/governance/test_core_addition_negative_controls.py tests/unit/governance_scripts/test_pre_write_gate_core_guard.py -q --tb=short
$env:CORE_ADDITION_CHANGED_PATHS = @('<each exact W0-authorized core path>') -join [IO.Path]::PathSeparator
python ops_scripts/ci/check_agentic_core_addition.py
$coreGateExit = $LASTEXITCODE
Remove-Item Env:CORE_ADDITION_CHANGED_PATHS -ErrorAction SilentlyContinue
if ($coreGateExit -ne 0) { exit $coreGateExit }
python ops_scripts/ci/check_agentic_core_static_boundary.py --strict
python ops_scripts/ci/check_no_app_specific_literals_in_core.py --strict
python -m pytest tests/governance/test_agentic_core_static_boundary.py tests/governance/test_no_app_specific_literals_in_core.py -q --tb=short
python -m pytest tests/unit/agentic_core/runtime/contracts/test_runtime_customization_package.py tests/_apps_contract/test_apps_rg_u0_package_ingest.py tests/_apps_contract/test_apps_rg_effective_output_contract_resolves_from_u0_package.py -q --tb=short
python -m pytest tests/unit/agentic_core/runtime/test_l2_recipe_resolver.py tests/unit/apps_rg/test_l2_recipe_registry.py tests/_apps_contract/test_apps_rg_core_resolves_l2_recipe.py tests/_apps_contract/test_apps_rg_missing_recipe_fails_closed.py tests/_apps_contract/test_apps_rg_cannot_inject_l2_callable.py tests/_apps_contract/test_apps_rg_l2_steps_only_via_core_recipe.py tests/unit/apps_rg/test_single_action_spine_entrypoint.py -q --tb=short
python -m pytest tests/unit/agentic_core/runtime/entrypoints/test_integrated_single_action_spine_run.py tests/_apps_contract/test_apps_rg_r4_manifest_l2_fault_consistency.py tests/_core_contract/test_spine_u0_through_exit_gates.py -q --tb=short
python ops_scripts/ci/check_app_registry_conformance.py
python -m pytest tests/unit/ops_scripts/ci/test_check_app_registry_conformance.py -q --tb=short
python tools/governance/boundary_receipt_validator.py
python ops_scripts/ci/check_governance_receipts.py --strict
python -m pytest tests/unit/apps_rg_simple tests/integration/apps_rg_simple -q --tb=short
python -m pytest tests/e2e/apps_rg_simple/test_replay_full_run.py -q --tb=short
python -m pytest tests/unit/apps_rg tests/apps_rg tests/evals/apps_rg tests/e2e/apps_rg tests/unit/tools/apps_rg -q --tb=short
python ops_scripts/ci/check_structure_policy.py --verbose
$env:NO_SHADOW_SPINE_FAIL_CLOSED='1'
python ops_scripts/ci/check_no_shadow_spine.py
$shadowExit = $LASTEXITCODE
Remove-Item Env:NO_SHADOW_SPINE_FAIL_CLOSED -ErrorAction SilentlyContinue
if ($shadowExit -ne 0) { exit $shadowExit }
python ops_scripts/ci/check_apps_test_model.py
python ops_scripts/ci/check_test_integrity.py
python -m apps_rg_simple preflight --request apps_rg_simple/examples/reference_run.yaml --proof-class replay
python -m apps_rg_simple verify-research <recorded_producer_run_dir> --proof-class replay --preflight-receipt <replay_preflight_receipt>
python -m apps_rg_simple run --request apps_rg_simple/examples/reference_run.yaml --preflight-receipt <replay_preflight_receipt> --research-bundle <recorded_producer_run_dir> --provider replay
python -m apps_rg_simple verify-run artifacts/apps_rg_simple/runs/<run_id>
python -m apps_rg_simple verify-port --require-current-source --runtime-receipt artifacts/apps_rg_simple/runs/<run_id>/runtime_acceptance.json
python -m apps_rg_simple render-summary artifacts/apps_rg_simple/runs/<run_id>
```

Before the CoreAddition scanner runs, `artifacts/governance/session_state.json.active_plan` must name
this plan and match its five author-gate frontmatter fields. `CORE_ADDITION_CHANGED_PATHS` must list
every exact W0-authorized core path, including untracked paths the git-diff scan cannot see.

W0 must also capture `python ops_scripts/ci/check_apps_runtime_package_contracts.py --strict` as a
known repository-wide baseline. It is currently red because scanner expectations and existing package
filenames/`profile_refs` have drifted. Do not call it a clean target gate or repair governance under
this plan. The new app instead needs plan-owned package-ingest, digest, reference-resolution,
typed-negative, and core-U0 flow-through tests; making the repo-wide scanner blocking requires a
separately approved governance repair.

Then run one fresh upstream-and-downstream live proof session with SearXNG, OpenAI, Gemini, and the
downstream resume generation/judge configuration available. The producer directory must come from the first
command in this same session; a previous authorized bundle is not accepted as live proof:

```powershell
python -m apps_rg_simple preflight --request apps_rg_simple/examples/live_reference_run.yaml --proof-class live
python -m apps_research --target-company <company> --target-role <role> --jd <jd_path>
python -m apps_rg_simple verify-research <fresh_producer_run_dir> --proof-class live --require-fresh --preflight-receipt <live_preflight_receipt>
python -m apps_rg_simple run --request apps_rg_simple/examples/live_reference_run.yaml --preflight-receipt <live_preflight_receipt> --research-bundle <fresh_producer_run_dir> --artifact-root artifacts/apps_rg_simple/runs
python -m apps_rg_simple verify-run artifacts/apps_rg_simple/runs/<live_run_id> --require-live --require-11-of-11
python -m apps_rg_simple verify-port --require-current-source --require-live --runtime-receipt artifacts/apps_rg_simple/runs/<live_run_id>/runtime_acceptance.json
python scripts/governance/verify_codex_run_receipt.py <codex_run_receipt.json>
```

Required fault tests:

- missing resume/JD/target/research bundle/provider readiness and malformed source resume;
- caller-authored/manual brief bypass, live reuse of an old bundle, or research stage omitted,
  reordered, duplicated, skipped, or marked `NOT_RUN`;
- `--dry-run`, `--apps-e2e-dry-run`, mock/synthetic/offline producer mode, fake sidecar, or fixture
  provider evidence presented as live;
- SearXNG readiness failure, zero/empty research evidence, stale evidence, unsupported source claims,
  invalid targeting format, blocked/weak producer output, or missing producer artifact;
- missing/failed producer U0, incomplete identity, wrong parent/request/trace/tenant/company/role/JD,
  wrong generation provider/model, or resume contents leaked into the research request;
- missing/FAIL/UNKNOWN/WARN research runtime gate, unexplained N/A, missing or non-model-backed X2,
  judge score below 0.75, same-provider generation/judging, or serialization retry exhaustion;
- missing/extra/non-PASS G5/G6/G7/G21/G24/G26, invalid sealed workflow/X1/X2/runtime exhaust, or
  producer Exit other than exact X3D;
- legacy-v1-only handoff, missing COMMITTED marker, surviving/exposed staging directory, escaped
  artifact path, missing artifact, or tampered manifest/marker/brief/JD/Exit/receipt/artifact bytes;
- local admission missing, non-PASS, identity/digest-mismatched, falsely native-authoritative, or
  replay evidence claiming fresh live research;
- missing/invalid/mismatched CoreAdditionAuthorGate receipt, or a core changed path outside its exact
  authorized set;
- any app name/literal/branch, resume-specific gate/threshold/path, or duplicate registry introduced
  under `agentic_core/**`;
- arbitrary recipe import/callable injection, namespace escape, path escape, digest mismatch,
  duplicate metadata provider, or unvalidated recipe metadata;
- app CLI invocation of the L2 resolver/private core stages instead of the public spine entrypoint;
- any app-local U0/L1/L0/C0/PA/GateMesh/judge/Exit/X3/UWG/L6 authority implementation or
  producer-component claim;
- existing `apps_rg` recipe resolution or public-entrypoint receipt shape changing under the generic
  seam;
- missing/orphan/duplicate/misclassified `apps_rg_simple` shared registry row, a registry target that
  bypasses the public core entrypoint, or registry status presented as production authority;
- the known repository-wide runtime-package scanner drift presented as a clean app-specific proof;
- missing source fact and claim-ledger orphan;
- generation timeout, invalid JSON, truncated response, and provider error;
- deterministic gate failure and judge timeout/UNKNOWN;
- narrative dependency blocked;
- one missing, duplicate, stale, or digest-mismatched lane at aggregation;
- aggregate judge fail;
- non-X3D UWG request, path traversal, interrupted write, and hash mismatch;
- L6 invoked before the core product-terminal boundary or attempting current-run mutation;
- missing or duplicate source inventory item;
- unknown, missing, or duplicate coverage disposition;
- stale source revision/hash or unresolved source/import evidence marked `COMPLETE`;
- app-implemented item without target owner, preserved invariant, or parity test;
- changed-core item without exact author-receipt path binding, genericity proof, or existing-app
  regression;
- reused-core item without canonical producer-component evidence, core regression, or no-alias proof;
- simplified/omitted item without a bound omission and forbidden-claim entry;
- unaccounted target Python/config/schema file;
- required parity node ID missing from collection, skipped, xfailed, or deselected;
- replay/stub receipt claiming live or model-backed proof;
- same provider/model serving generation and certification judging;
- tampered inventory, coverage, omission, claim-ceiling, or runtime-receipt digest; and
- a `REFERENCE_ONLY` run claiming canonical/production authorization.

Every changed app-owned test file must declare the appropriate apps testing-model bucket. Use `LAW`
for authority/proof/write-sovereignty tests, `APP CONTRACT` for CLI/schema/output contracts, and
`SPINE BINDING` for stage/handoff/one-route tests.

**Acceptance**:

- Unit/contract/integration/e2e suites collect and execute with zero failures and no skipped MVP tests.
- The official upstream source-contract chain is retained as a baseline. Its structural/fixture
  `NOT_RUN` rows are enumerated and classified as non-execution evidence; they do not fail the
  baseline solely by existing and cannot satisfy any plan proof obligation.
- A separate plan-owned required-node/proof manifest has zero failed, skipped, xfailed, deselected, or
  `NOT_RUN` requirements. Live proof has no required upstream stage or downstream lane `NOT_RUN`.
- The bound current-source regression suite passes, or any source failure blocks parity with an RCA;
  historical `_apps_contract` archaeology is not substituted for the active source gate.
- Core-addition receipt, changed-path, static-boundary, no-app-literal, structure, no-shadow, runtime
  customization, resolver, and public-entrypoint gates all pass. Runtime producer-component tests
  prove the canonical core—not app aliases—emitted U0/L1/L0/C0/PA/GateMesh/judge/Exit/UWG/L6.
- Existing `apps_rg` recipe resolution and public-entrypoint behavior remain regression-equivalent;
  the new seam accepts only digest-bound, namespace-contained, schema-valid recipe metadata.
- Certified source inventory is current, coverage count equals inventory count, and unclassified,
  duplicate, unknown, ownerless, testless, and unapproved-omission counts are all 0.
- Every required parity node ID is collected, executed, and passed; no required node is skipped,
  xfailed, or deselected.
- No target Python/config/schema file is absent from the coverage/accounting manifest.
- Replay E2E validates a recorded producer bundle through every admission gate and runs all 11 lanes;
  zero research requirement or resume lane is unaccounted or `NOT_RUN`.
- Replay proof emits `MVP_SCOPE_ACCOUNTED` and a valid recomputed verification receipt; it cannot emit
  a live or production claim.
- Replay binds `producer_evidence_class=RECORDED_COMMITTED_BUNDLE`,
  `research_executed_in_current_session=false`, and `judge_evidence_class=RECORDED_REPLAY`; it cannot
  emit `MODEL_BACKED_JUDGED` or `APPS_RESEARCH_UPSTREAM_VERIFIED`.
- Live E2E records a fresh Apps Research child run, SearXNG evidence, real OpenAI generation, real
  model-backed Gemini X2, exact six-gate PASS, producer X3D, committed byte-valid bundle, local
  admission PASS, real downstream resume provider/model IDs and judge attempts, 11/11 terminal PASS lanes,
  aggregate deterministic PASS, aggregate judge PASS, root `X3D_ALLOW_FINISH`, UWG commit PASS,
  final outputs, and L6 shadow completion.
- The live receipt emits `APPS_RESEARCH_UPSTREAM_VERIFIED` and `LIVE_REFERENCE_VERIFIED`, while still
  recording `native_v2_consumer_authority=false` and forbidding `APPS_RESEARCH_CHAIN_CERTIFIED`.
- Live binds `producer_evidence_class=FRESH_CURRENT_SESSION`,
  `research_executed_in_current_session=true`, `judge_evidence_class=LIVE_MODEL_BACKED`, provider
  attempt receipts, and `independence_status=PASS` for section and aggregate judges.
- Fresh live proof emits `LIVE_REFERENCE_VERIFIED`, never `FULL_PORT_COMPLETE`, and reports every
  deliberate omission and resulting claim ceiling in both JSON and human-readable status output.
- The substantial execution emits a JSON Codex run receipt whose validator passes and whose changed-
  path, gate-result, blocker, and artifact-digest fields agree with the port-completeness receipt.
- If credentials or live providers are unavailable, deterministic proof may pass but the plan remains
  incomplete; do not label fixture evidence live reference verification.
- Final diff is limited to `apps_rg_simple/**`, the three approved centralized app-test roots, the
  one declarative `apps_shared/integrations/app_registry.py` row and focused conformance tests, the
  exact W0-authorized generic `agentic_core/**` paths and focused core tests, and the declared
  customization/core-addition/migration/verification receipts plus this plan update.

---

## Artifact Layout

The external producer remains authoritative at
`artifacts/apps_research/runs/<producer_run_id>/`. Admission requires this committed set:

```text
job_description.raw.txt
job_description.normalized.txt
apps_research_u0_receipt.json
apps_research_gate_mesh_result.json
sealed_workflow_package.json
exit_review_packet.json
exit_disposition_receipt.json
runtime_exhaust_bundle.json
company_brief.json
briefing.md
run_metadata.json
apps_research_apps_rg_handoff_v2.json
bundle_commit_manifest.json
```

The native Apps RG consumer receipt is intentionally absent from simple authority. Its presence in a
source bundle may be validated as source evidence but cannot be copied, renamed, or reissued as an
`apps_rg_simple` receipt.

Every proof session creates preflight before current-session admission. Live then launches the
producer; replay validates a producer run committed before the current proof session:

```text
artifacts/apps_rg_simple/proof_sessions/<proof_id>/
├── preflight_readiness.json
├── producer_command_observation.json      # live only; argv/exit/artifact path, no secrets
├── producer_bundle_binding.json
└── proof_session_manifest.json
```

Each fresh run owns one immutable directory:

```text
artifacts/apps_rg_simple/runs/<run_id>/
├── request/
├── research/
│   ├── proof_session.json
│   ├── producer_bundle_ref.json
│   ├── producer_artifact_index.json
│   ├── external_research_admission.json
│   └── admitted_briefing.snapshot.md       # targeting-only immutable input, never authority
├── receipts/
│   ├── preflight_readiness.json
│   ├── core_u0_receipt.json
│   ├── core_l1_plan_receipt.json
│   ├── core_l0_route_receipt.json
│   ├── core_c0_pa_receipt_index.json
│   ├── core_stage_handoffs.jsonl
│   └── producer_component_report.json
├── sections/<section_id>/...
├── aggregate/
│   ├── same_run_fingerprint.json
│   ├── sealed_section_index.json
│   ├── assembled_resume.candidate.json
│   ├── core_gate_mesh_result.json
│   └── core_judge_verdict.json
├── core_exit/
│   ├── x1_checkout.json
│   ├── x2_aggregation.json
│   ├── exit_review_packet.json
│   └── x3_disposition.json
├── core_uwg/
│   ├── commit_request.json
│   ├── validation_receipt.json
│   └── commit_receipt.json
├── outputs/                              # durable bytes written only by core UWG
│   ├── final_resume.json
│   ├── FINAL_RESUME_OUTPUT.md
│   ├── FINAL_RESUME_OUTPUT.txt
│   └── resume.docx
├── core_product_terminal_receipt.json   # core-sealed after UWG, before L6
├── core_l6/
│   ├── shadow_report.json
│   └── future_run_recommendations.md
├── runtime_acceptance.json              # non-authorizing app proof closeout, after L6
├── run_manifest.json
└── RUN_SUMMARY.md
```

Directory placement does not confer authority. Every core-owned artifact above must carry a canonical
core `producer_component`; the app may persist only its preflight/admission/L2/candidate/proof
artifacts and references to core outputs. Copying a core result into an app-shaped alias is a failure.

Failed runs keep the same layout where applicable and preserve the exact closeout order:
`core_product_terminal_receipt.json` → core L6 result/N/A/failure → `runtime_acceptance.json` →
`RUN_SUMMARY.md`. They must not backfill missing product artifacts after Exit.

Port proof is recomputed outside any one run and binds one runtime receipt:

```text
artifacts/apps_rg_simple/port_proof/<proof_id>/
├── source_inventory.snapshot.json
├── port_coverage.snapshot.json
├── omission_ledger.snapshot.json
├── claim_ceiling.snapshot.json
├── parity_test_results.json
├── upstream_source_baseline.json
├── external_research_admission.ref.json
├── runtime_acceptance.ref.json
└── PORT_STATUS.md

artifacts/governance/verification_receipts/
└── <ts>_apps_rg_simple_port_completeness.json
```

---

## Out Of Scope

- Replacing, deleting, or refactoring production `apps_rg`.
- Replacing, deleting, refactoring, or locally reimplementing production `apps_research` internals.
- Any `agentic_core` change outside the W0-frozen, author-receipted generic recipe-registration/
  composition seam; any app-specific core literal, adapter, branch, gate, threshold, path, or schema.
- Any `apps_shared/**` change beyond the one declarative app-registry row and its focused conformance
  test; shared dispatch logic remains out of scope.
- Changing the v2 producer schema/identity to name `apps_rg_simple`, emitting a native Apps RG
  consumer receipt, or claiming production release/certification authority.
- Production parity beyond the required external Apps Research producer, strict bundle admission, and
  downstream reference semantics retained by this plan.
- Caches, semantic reuse, Redis, SQLite graph projection, embeddings, or vector retrieval.
- Parallel lane dispatch or throughput optimization.
- Patch-run/resume-from-partial-run behavior.
- Full self-consistency pools, reselection ladders, multi-pass executive-summary regeneration, or
  model-specific recovery branches.
- Multi-provider judge quorum, failover economics, and calibration/human-evaluation programs.
- L5 certification, Apps Eval binding, fact-vector/state promotion, production product-eligibility
  and stage ledgers, per-section L6 v40/microstep/evaluator-binding closure, OTel/L7, dashboards, or
  BCG RCA.
- Parity with the 13-file production operator-output/mandatory-output authority contract.
- Changing the source resume, source facts, or JD. The briefing is freshly generated upstream and its
  exact bytes become immutable after producer commit.
- Adding `apps_rg_simple/**` to canonical production workflow triggers, dependency SSOT, stage-ledger
  authority, or release certification.
- Publication, branch merge, or push.

---

## Tools Needed During Execution

- `rg --files` / exact source, import, reference, and literal search — files, symbols, schemas, gate
  IDs, fixtures, consumers, and duplicate candidates; results are checked against source and tests.
- `adg_sqlite` MCP — optional supplementary graph evidence only; absence or unhealthy status does not block execution.
- `pytest` — unit, contract, integration, negative, replay, and live-run artifact verification.
- `ruff` — import, unused-symbol, and formatting checks.
- Provider SDKs behind package-owned ports — live generation and independent judging.
- `python-docx` or another single deterministic renderer — DOCX output from committed JSON only.
- JSON Schema validator — persisted contract and artifact verification.

---

## Missing Information / Required Decisions

1. **Core-addition authorization** — plan approval is not the author receipt. The exact generic core
   seam and changed paths must be frozen from exact source/import/test evidence, then separately
   authorized by a valid `CoreAdditionAuthorGateReceipt` before implementation.
2. **Exact generic seam** — current source registers only the existing Apps RG recipe. W0 must prove
   whether generic recipe resolution alone is sufficient or whether the public spine also needs a
   narrowly generic composition link for GateMesh/judge/UWG/L6. Wider changes require re-planning.
3. **Live providers** — the downstream package is provider-neutral, but W5 live proof needs one
   `apps_rg_simple` downstream resume-generation route and one independent downstream judge route,
   plus a ready SearXNG service, OpenAI
   generation credentials, and Google/Gemini judge credentials for the required upstream run.

---

## Risks / Stop Conditions

- **STOP** if the core-addition author receipt is absent, invalid, stale, or does not exactly bind the
  changed core paths and generic behavior.
- **STOP and re-plan** if structure, boundary, or fail-closed no-shadow-spine validation rejects the
  declarative app plus canonical-core design.
- **STOP and re-plan** if the required core change is wider than the W0-frozen generic seam, adds any
  app-specific literal/branch/threshold/path, or cannot preserve existing Apps RG behavior.
- **STOP and re-plan** if root app-registry conformance cannot be satisfied with one declarative
  `GovernedAppEntry` pointing at the public app callable, or if shared dispatch logic is required.
- **STOP** if any retained core stage lacks public-entrypoint/runtime `producer_component` proof or an
  app alias/shadow path appears to have emitted a core-owned artifact.
- **STOP and re-plan** if any production `apps_research/**` or `apps_rg/**` edit/import becomes
  necessary, or if process/file integration fails repository boundary policy.
- **STOP and re-plan** if the desired outcome is a production replacement rather than a
  reference-only runtime.
- **STOP** if deterministic source discovery is incomplete, any source item is unclassified, any implemented
  item lacks an owner/parity test, or any omission lacks an enforced claim ceiling.
- **STOP and regenerate proof manifests** if the bound source revision/hash or frozen discovery roots change.
- **STOP and re-plan** if Apps Eval, state promotion, the production per-section L6 binding chain, or
  production mandatory operator outputs become required rather than documented omissions.
- Fail closed if source facts lack stable IDs or cannot support a requested claim.
- Fail closed before core U0 on absent/stale/legacy/uncommitted/tampered producer artifacts, wrong
  identity/JD/target/freshness, any missing or non-PASS research gate, non-model-backed X2, provider
  mismatch, invalid runtime-exhaust linkage, or producer Exit other than exact X3D.
- Fail closed if live proof reuses a previously authorized producer bundle or substitutes a manual
  brief; only replay may use recorded producer artifacts.
- Fail closed if the local admission receipt claims native v2 consumer authority, rewrites
  `consumer_app_id=apps_rg`, or emits the native Apps RG consumer receipt.
- Fail closed if JD/briefing content appears as proof authority.
- Fail closed if the downstream generation route and reference-proof judge are not provider/model
  independent in a live reference proof.
- Fail closed on any missing required lane, receipt, digest, deterministic gate, or judge result.
- Fail closed if more than one root X3 is emitted or a lane disposition is treated as root authority.
- Fail closed if a non-UWG component performs a durable final-resume product write. Producer-owned
  Apps Research authority artifacts and immutable admitted inputs are not final resume products.
- Fail closed if L6 runs before the core product-terminal boundary or influences the current X3/UWG
  result.
- Do not weaken gates, judge thresholds, or proof rules merely to obtain 11/11.
- Do not use `FULL_PORT_COMPLETE`, `FULL_APPS_RG_PARITY`, `APPS_RESEARCH_CHAIN_CERTIFIED`, or
  production-authority wording under this plan, even when every retained MVP obligation passes.
- Replay-only evidence may reach `MVP_SCOPE_ACCOUNTED`, but plan completion and
  `LIVE_REFERENCE_VERIFIED` remain blocked until one fresh current-session upstream-and-downstream
  live reference proof passes.

---

## Gap Register

**GAP-1: Corrected canonical-core boundary is not yet certified**

- The target is now confirmed inside the governed repository, so structure and one-spine rules apply
  to the new root `apps_*` package.
- The earlier app-local-spine shape was invalid. The corrected design makes the app declarative,
  routes through the public core entrypoint, and leaves U0/L1/L0/C0/PA/GateMesh/judge/Exit/UWG/L6
  ownership in core.
- Resolution: W0.1 validates this exact design and stops rather than adding an exemption or restoring
  any local shadow stage.

**GAP-2: Deterministic source inventory not yet generated**

- Exact source reads identified the principal entrypoints and contract families, but the versioned
  root/reference/hash inventory is not yet materialized.
- Resolution: W0.2 completes source/import-aware discovery and verifies every root. ADG may add
  supplementary graph context but is neither required nor a stop condition.

**GAP-3: Canonical core execution versus production product authority**

- The runtime is planned to execute the canonical core spine, but its app profiles, product outputs,
  omissions, and external Apps Research admission remain `REFERENCE_ONLY`; using core does not make it
  the current production Apps RG authority chain.
- Resolution: producer-component proof may unlock `CANONICAL_CORE_SPINE_EXECUTED`; only the narrower
  reference claims may follow. Production release/certification registration remains separate scope.

**GAP-4: DOCX implementation differs while the product contract remains mandatory**

- Current source actively emits DOCX through
  `apps_rg/runtime/final_resume_outputs.py::emit_final_resume_product_outputs`, which invokes
  `ops_scripts/apps_rg/export_final_resume_docx.py::export`; product eligibility requires verified
  `outputs/resume.docx` by default.
- Resolution: the app owns one deterministic in-memory DOCX renderer from the core-reviewed candidate
  and tests semantic/content parity; only core UWG persists those proposed bytes. It does not copy the
  production exporter.

**GAP-5: Port implementation has not started**

- The target directory is absent and tracked/untracked target-file counts are both zero.
- Resolution: keep `PORT_STATUS=NOT_STARTED_TARGET_ABSENT` and `MAX_ALLOWED_CLAIM=PLAN_ONLY` until
  approved execution creates code and the recomputed proof receipt advances the status.

**GAP-6: Current production E2E includes deliberately omitted mandatory stages/artifacts**

- Current production success includes Apps Eval, state promotion, product/terminal authority, the
  fuller per-section L6 closure/binding chain, and 13 mandatory operator artifacts.
- Resolution: bind each family to the omission ledger and exact forbidden claims. A green simple run
  may prove `MVP_SCOPE_ACCOUNTED` or `LIVE_REFERENCE_VERIFIED`; it may never claim full production
  E2E parity under this plan.

**GAP-7: Current v2 producer identity does not authorize `apps_rg_simple` as native consumer**

- `apps_research.apps_rg_handoff.v2` hard-codes `consumer_app_id=apps_rg`, and its consumer receipt is
  namespaced to Apps RG.
- Resolution: preserve the source manifest byte-for-byte; emit only
  `apps_rg_simple.external_research_admission.v1` with `native_v2_consumer_authority=false`. Native
  authority requires a separate approved producer/schema/consumer change outside this plan.

**GAP-8: Existing source-chain checks are not fresh live end-to-end certification**

- The currently inspected structural traceability result contains 29 `NOT_RUN` requirements;
  evidence-mode PASS is JUnit/group-derived and does not itself reject `skipped > 0`; the full-chain
  certification test is a deterministic receipt/ledger cassette. Current CLI/bridge tests use mocks or
  fake records/sidecars in important paths.
- Resolution: W5 retains and labels those checks as baseline-only, explicitly classifies their known
  `NOT_RUN` rows as non-execution evidence, and separately requires zero skip/xfail/deselect/`NOT_RUN`
  in the plan-owned required-node manifest. A fresh SearXNG/OpenAI/Gemini producer run plus live
  11-lane reference run is required for `LIVE_REFERENCE_VERIFIED`.

**GAP-9: Canonical CI/dependency authority does not cover the new package**

- The mandatory shared `APP_REGISTRY` classification row is in scope and does not itself add workflow
  or dependency authority. Existing workflow triggers and dependency SSOT do not include
  `apps_rg_simple/**`; a green local suite cannot be described as canonical CI certification.
- Resolution: record this as a forbidden claim and out-of-scope production-governance change. If
  canonical CI registration is later required, stop and approve a separate governance plan.

**GAP-10: Some configured Apps Research runtime gates may not have separate producer receipts**

- The source profile names G1-G10/G27/G28, while the canonical handoff Exit uses the exact six-gate
  G5/G6/G7/G21/G24/G26 GateMesh.
- Resolution: W0 maps each configured gate to an actual runtime receipt or classifies it explicitly.
  A locally repeated deterministic gate is `IMPLEMENTED_APP_SIMPLIFIED`, never evidence that the producer
  executed an otherwise absent authority receipt.

**GAP-11: Generic core recipe/composition seam is not implemented or authorized**

- The current L2 resolver lazily registers the existing Apps RG recipe; no validated generic metadata
  path for `apps_rg_simple` exists yet, and the exact additional public-spine composition work is
  unresolved until source/import-aware discovery is complete.
- Resolution: W0 freezes the smallest generic, reusable, no-app-literal seam and authorizes exact
  paths. W1 proves namespace/digest/schema controls plus unchanged existing Apps RG resolution. Until
  then `CORE_ADDITION_STATUS=REQUIRED_NOT_AUTHORIZED` and no runnable claim is valid.

**GAP-12: Repository-wide runtime-package scanner has a known red baseline**

- `check_apps_runtime_package_contracts.py --strict` currently expects one canonical filename and a
  top-level `refs` map, while existing packages use mixed filenames and Apps RG uses `profile_refs`.
  It is not a clean app-specific gate today.
- Resolution: W0 records the exact baseline without claiming PASS. Plan-owned Apps RG Simple package-
  ingest/digest/ref-resolution/typed-negative/core-U0 tests are blocking. Repairing or narrowing the
  repository-wide scanner is a separate governance plan; no green claim may silently ignore its
  baseline status.

---

## Definition of Done

DoD-1: The repository-native package installs and exposes `preflight`,
`run --preflight-receipt --research-bundle`, `verify-research`, `verify-run`, `verify-port`, and
`render-summary`.

- Evidence: clean-environment install plus `python -m apps_rg_simple --help` exits 0.
- Status: TODO

DoD-2: App-owned preflight, external-research admission, L2 packets, lane acceptance, candidate, and
proof receipts are typed; each observed Apps Research U0/runtime/Exit/commit boundary is bound; and
the external bundle passes reference-only admission before core U0.

- Evidence: schema/round-trip/tamper contract suite; all stage artifacts validate.
- Status: TODO

DoD-3: Canonical core U0/L1/L0/C0/PA are deterministic, fail closed, carry canonical core producer
components, and make no downstream model call before core dispatches the app L2 recipe; upstream Apps
Research retrieval/generation/judging is separately receipt-bound.

- Evidence: call-count assertions, golden digests, and negative-input tests.
- Status: TODO

DoD-4: The serial manifest executes exactly 11 unique generated lanes in dependency order.

- Evidence: replay E2E lane ledger equals the canonical lane tuple; zero missing/extra/`NOT_RUN`.
- Status: TODO

DoD-5: Every lane produces app-owned used-input/L2 bindings to a canonical core C0 proof-pool receipt,
a sealed L2 handoff, proof-bound output, core GateMesh and core judge receipts, and one non-authorizing lane acceptance record. Live evidence
is independent and model-backed; replay evidence is explicitly `RECORDED_REPLAY`. No per-lane Exit or
X3 artifact exists.

- Evidence: per-lane artifact verifier over all 11 directories.
- Status: TODO

DoD-6: Candidate/role headers plus locked early-career, education, and certifications content are
byte-preserved and never rewritten by a model.

- Evidence: before/after hashes and provider-payload exclusion tests.
- Status: TODO

DoD-7: App L2 aggregation requires 11 proof-class-consistent PASS lane records and proposes one
candidate; core runs cross-section/final GateMesh and aggregate judge enforcement, then core Exit
emits exactly one root X3.

- Evidence: positive E2E plus missing/duplicate/stale/gate-fail/judge-fail negative matrix.
- Status: TODO

DoD-8: Only the core root X3D reaches core UWG, and only core UWG commits final resume product outputs
atomically; the app has no product-write path.

- Evidence: write-sovereignty test, path-escape test, interruption test, and commit receipt hashes.
- Status: TODO

DoD-9: Final JSON, Markdown, text, and DOCX contain the same 11 generated lanes plus all required
locked/source-only resume sections and headers.

- Evidence: renderer parity test and human-readable artifact inspection.
- Status: TODO

DoD-10: Core seals the immutable product-terminal receipt, then core L6 runs the one simplified shadow
and cannot mutate the current run. Non-authorizing `runtime_acceptance.json` is emitted afterward and
binds both digests; production per-lane v40/microstep/Apps Eval bindings remain explicitly omitted.

- Evidence: ordering/timestamp/digest tests and mutation-attempt rejection.
- Status: TODO

DoD-11: The active upstream source-contract baselines pass as labeled baseline evidence, with every
known structural/fixture `NOT_RUN` row explicitly classified and excluded from execution claims. The
separate plan-owned required-node manifest and deterministic suite have zero failed, skipped, xfailed,
deselected, or `NOT_RUN` requirements.

- Evidence: the W5 source command chain plus
  `python -m pytest tests/unit/apps_rg_simple tests/integration/apps_rg_simple tests/e2e/apps_rg_simple/test_replay_full_run.py -q`, with explicit collection/JUnit accounting.
- Status: TODO

DoD-12: A fresh live proof first completes Apps Research with real SearXNG retrieval, OpenAI
generation, model-backed Gemini X2, exact GateMesh PASS, producer X3D and committed bundle; it then
completes 11/11 with real downstream resume generation and independent judge receipts, aggregate PASS, root
X3D, core UWG commit, final outputs, and core L6 shadow artifacts.

- Evidence: fresh run directory plus `verify-run --require-live --require-11-of-11` exit 0.
- Status: TODO

DoD-13: No production `apps_research/**` or `apps_rg/**` file changes; the only core changes are the
exact author-receipted generic paths frozen in W0. The app imports no sibling app or private core
stage and passes repository structure, boundary, genericity, and fail-closed no-shadow-spine checks.

- Evidence: `git diff --name-only` contains only the declared app/test paths, one shared app-registry
  row/focused conformance test, exact W0-authorized generic core paths/focused tests, and declared
  receipts/plan update; core-addition, static-boundary, no-app-literal, registry, structure, and
  `NO_SHADOW_SPINE_FAIL_CLOSED=1 check_no_shadow_spine.py` gates exit 0.
- Status: TODO

DoD-14: README explains the reference-runtime boundary, mandatory Apps Research producer, SearXNG/
OpenAI/Gemini prerequisites, ordered live proof commands, replay-only recorded bundle mode, no manual-brief
fallback, inputs, outputs, stage map, failure semantics, and differences from production Apps RG.

- Evidence: documentation review plus copy/paste smoke command.
- Status: TODO

DoD-15: A current deterministic source inventory accounts for every execution-reachable obligation from
the frozen Apps Research producer, handoff publisher/validator/authority-contract, and Apps RG
product-entry roots.

- Evidence: source inventory verifier reports `COMPLETE`, discovery errors 0, matching source hashes,
  and exact root/import/reference/test provenance. Optional ADG evidence is non-blocking.
- Status: TODO

DoD-16: Every source item has exactly one valid disposition. App-implemented items have app owners and
passing parity tests; changed generic-core items have exact author-receipted paths and generic/core
regressions; unchanged canonical-core reuse has producer-component and no-alias proof; externally
reused Apps Research items have source/boundary owners, required receipts/tests, and explicit no-port
status; every simplified or omitted mechanism has a complete omission record.

- Evidence: coverage verifier reports inventory count = coverage count, with unclassified,
  duplicate/unknown, ownerless, testless, and unapproved-omission counts all 0.
- Status: TODO

DoD-17: Completeness-specific negative controls reject stale/tampered inventory, missing accounting,
test deselection, replay-as-live, same-model judging, and reference-as-production claims.

- Evidence: named negative test matrix plus collected/executed/passed node-ID receipt; no required
  test is skipped, xfailed, or deselected.
- Status: TODO

DoD-18: The recomputed port receipt truthfully separates app-implemented equivalent/simplified
functionality, author-receipted generic-core changes, unchanged canonical-core reuse, required-but-
not-ported Apps Research functionality, and omitted production functionality.

- Evidence: replay result is `CANONICAL_CORE_SPINE_EXECUTED` plus `MVP_SCOPE_ACCOUNTED`; fresh live
  result adds `APPS_RESEARCH_UPSTREAM_VERIFIED` plus `LIVE_REFERENCE_VERIFIED`; `PORT_STATUS.md` and JSON show
  exact counts and rows for all five owner classes—app implemented, changed generic core, reused
  canonical core, externally reused, and omitted—plus every forbidden claim; no output contains
  `FULL_PORT_COMPLETE` or production-authority wording.
- Status: TODO

DoD-19: Replay observes reference preflight → validation of a previously committed producer stage
ledger/bundle → strict admission → canonical core U0 and never claims current producer execution.
Live observes reference preflight → fresh Apps Research U0/runtime/Exit/commit in the same proof
session → strict admission → canonical core U0, with no direct-brief/reuse bypass.

- Evidence: separate recorded-producer and observed-proof-session stage arrays bind Apps Research U0/
  runtime/Exit/commit and local admission; the source v2 identity remains `consumer_app_id=apps_rg`, local admission records
  `native_v2_consumer_authority=false`, and all omission/reuse negative tests pass.
- Status: TODO

DoD-20: The generic core seam has a valid CoreAdditionAuthorGate receipt, contains no app literal or
arbitrary import/callable path, accepts only namespace-contained/schema-valid/digest-bound recipe
metadata, and preserves existing Apps RG resolver/public-entrypoint behavior.

- Evidence: author-receipt schema/negative tests, changed-path core-addition scanner, AST/literal and
  boundary gates, malicious metadata matrix, existing Apps RG resolver regression, and runtime
  producer-component proof all pass.
- Status: TODO

DoD-21: The new root package has exactly one declarative shared `GovernedAppEntry` whose canonical
callable enters the public core spine; registry conformance adds no shared dispatch behavior and does
not raise the `REFERENCE_ONLY` claim ceiling.

- Evidence: app-registry conformance command and focused tests pass; runtime proof traces the registry
  target to the public core entrypoint; AST/diff checks find only the approved row.
- Status: TODO

---

## Scope Expansion Authorization

Any discovery requiring edits to production `apps_research/**` or `apps_rg/**`, changes to the v2
producer/consumer schema, `apps_shared/**` beyond the one approved declarative registry row,
`agentic_core` outside the exact W0-authorized generic seam, any app-specific core behavior, canonical
CI/dependency authority, governance, publication, cache, parallelism, or production-certification
edits is a material expansion. Stop, show the evidence, and obtain a revised plan approval (and, for
core, a revised author receipt) before changing those surfaces.

Executing the existing `python -m apps_research` CLI and reading/verifying its committed file contract
remain mandatory in-scope proof steps; they do not authorize mutation of the producer.

---

## Supersedes

_None — net-new plan. It does not supersede the production lane/aggregation gap plan or the archived
lean-core migration plan._
