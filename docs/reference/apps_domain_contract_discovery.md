# apps_* Domain Contract — Phase 0 Discovery Report

> **Status**: DRAFT — discovery complete, awaiting Phase 1 SR_APPROVAL.
> **Plan**: `.codex/plans/apps-domain-contract-fortknox-c4d8e2.md`
> **Date**: 2026-05-01
> **Scope**: Inventory all `apps_*` packages and identify the gaps required to
> make app-domain contracts authoritative-via-UWG/L4, runtime-resolved,
> Exit-consumed, and proven in E2E artifacts.

This report is the deliverable for **Phase 0** of the user's Fort Knox
app-domain contract objective. **No production code has been edited.**
Everything below is observational. Implementation begins only after the
user reviews this report and the companion plan.

---

## 1. apps_* package inventory

| App | Status | Entrypoint(s) | Has Policies | Has Thresholds | Has Agent Specs | Has Rubric (in `apps_eval/config/rubrics`) | Notes |
|---|---|---|---|---|---|---|---|
| `apps_eval` | active | `engines/base_eval_engine.py`, `integrations/eval_ingress_runner.py` | `eval_policies.yaml` | `eval_thresholds.yaml` | `agent_spec_config.py` | `rub_apps_eval_self_v1.yaml` | Self-eval rubric. Owns the rubric registry today. |
| `apps_exec` | active | `engines/base_exec_engine.py`, `integrations/exec_ingress_runner.py` | `exec_policies.yaml` | `exec_thresholds.yaml` | `agent_spec_config.py` | `rub_apps_exec_brief_v1.yaml` | Brief assembly engine. |
| `apps_lic` | active | `integrations/governed_lic_run.py`, 27 engine HOP files | `lic_policies.yaml` | `lic_thresholds.yaml` | `agent_specs.json`, `agent_spec_config.py` | `rub_apps_lic_outreach_v1.yaml` | Most config-heavy app. Validator rules, retry policy, voice profile, archetype indicators. |
| `apps_qna` | active | `builder/card_pack_builder.py`, `router/pack_loader.py` | **MISSING** | **MISSING** | `route_registry.yaml`, `build_config.py` | **none** | **Gap**: no domain-specific policies/thresholds/rubric. |
| `apps_research` | active | `engines/base_research_engine.py`, `integrations/governed_research_run.py` | `research_policies.yaml` | `research_thresholds.yaml` | `agent_spec_config.py` | `rub_apps_research_brief_v1.yaml` | Research brief generation. |
| `apps_rfp` | active | `engines/base_rfp_engine.py`, `integrations/governed_rfp_run.py` | `rfp_policies.yaml` | `rfp_thresholds.yaml` | `agent_spec_config.py` | `rub_apps_rfp_response_v1.yaml` | RFP response generation. |
| `apps_rg` | active | `__main__.py`, `bootstrap_runtime.py`, 52 engine files | `rg_policies.yaml` | `rg_thresholds.yaml` | `rg_agent_specs.json`, `agent_spec_config.py` | `rub_apps_rg_resume_generation_v1.yaml` | Resume generation. Most mature app: l3_dag.yaml, route_registry.yaml, hop_pipeline.py, spine_manifest.yaml. |
| `apps_underwriting_ai` | **stub** | `engines/hop_*` (5 files), `config/hop_pipeline.py` only | none | none | none | `rub_apps_underwriting_decisioning_v1.yaml` (rubric exists, app does not) | **Gap**: skeleton-only — `integrations/`, `outputs/`, `parsers/`, `tests/`, `types/`, `validators/` all empty. |
| `apps_shared` | platform | adapters, enforcement, proof harness | n/a | n/a | n/a | n/a | NOT an app — shared infrastructure (`proof/`, `enforcement/`, `data_adapters/`, `types/`). Does NOT receive a domain contract; provides the runtime/proof spine. |

**Total**: 8 apps + 1 platform module. **`apps_qna` and `apps_underwriting_ai`
require special handling** in Phase 2.

---

## 2. Per-app current state

For each app the following table summarizes current input/output/route/eval/L4/Exit/OTEL state.

### apps_eval
- **Input shape**: scorecard rows + judge model handles (`engines/_taxonomy.py` consumes `eval_policies.yaml`)
- **Output shape**: enterprise eval renderer + run_summary renderer
- **Route/orchestration**: `eval_ingress_runner.py` → engines → outputs
- **Eval metrics**: taxonomy-aware regression policy, capability vs regression class
- **L4/UWG integration**: **none** — reads `eval_policies.yaml` directly
- **Exit integration**: **none** — apps_eval IS the eval surface; not consumed by Exit
- **OTEL/proof**: `tests/_apps_contract/test_platform_contract.py` exists

### apps_exec
- **Input shape**: brief request → execution adapter
- **Output shape**: enterprise brief renderer
- **Route/orchestration**: `exec_ingress_runner.py` → `brief_assembly_engine.py`
- **Eval metrics**: rubric `rub_apps_exec_brief_v1.yaml` (decorative — not L4-resolved)
- **L4/UWG integration**: **none**
- **Exit integration**: generic V6 pipeline (not app-specific)
- **OTEL/proof**: standard pipeline OTEL only

### apps_lic
- **Input shape**: outreach campaign request, profile, voice profile
- **Output shape**: 27 HOP engines produce outreach messages
- **Route/orchestration**: `hop_pipeline.py` defines HOP1ProfileAnalysisAgent → HOP2ResearchAgent → HOP3SenderGroundingAgent → ...
- **Eval metrics**: `validator_rules.json`, `placeholder_detector_agent_config.py`, `subject_line_bandit_config.py`
- **L4/UWG integration**: **none** — config files read directly
- **Exit integration**: generic V6
- **OTEL/proof**: outreach-specific OTEL spans inside engines, but no app-specific contract refs

### apps_qna
- **Input shape**: question + namespace
- **Output shape**: answer pack
- **Route/orchestration**: `route_registry.yaml` (route ids), `pack_loader.py`
- **Eval metrics**: **NONE — biggest gap**. No rubric, no threshold, no fixtures.
- **L4/UWG integration**: **none**
- **Exit integration**: **none documented**
- **OTEL/proof**: minimal

### apps_research
- **Input shape**: research target → company brief request
- **Output shape**: research_renderer + enterprise_research_renderer
- **Route/orchestration**: `governed_research_run.py` → `company_brief_engine.py`
- **Eval metrics**: `rub_apps_research_brief_v1.yaml` (decorative)
- **L4/UWG integration**: **none**
- **Exit integration**: generic V6
- **OTEL/proof**: standard

### apps_rfp
- **Input shape**: RFP doc + KB
- **Output shape**: proposal_renderer + enterprise_rfp_renderer
- **Route/orchestration**: `governed_rfp_run.py` → `proposal_assembly_engine.py`
- **Eval metrics**: `rub_apps_rfp_response_v1.yaml` (decorative)
- **L4/UWG integration**: **none**
- **Exit integration**: generic V6
- **OTEL/proof**: standard

### apps_rg
- **Input shape**: profile + role + ATS keywords
- **Output shape**: 52 HOP engines produce resume artifact
- **Route/orchestration**: full L3 DAG (`l3_dag.yaml`), route_registry.yaml, hop_pipeline.py, spine_manifest.yaml — **most mature**
- **Eval metrics**: `rub_apps_rg_resume_generation_v1.yaml` (decorative)
- **L4/UWG integration**: bootstrap_runtime.py wires runtime, but app contract not L4-registered
- **Exit integration**: V6 pipeline; no app-specific rubric refs
- **OTEL/proof**: rich engine-level OTEL; no app contract refs

### apps_underwriting_ai
- **Input shape**: undefined (stub)
- **Output shape**: undefined (empty `outputs/`)
- **Route/orchestration**: `config/hop_pipeline.py` references 5 hop engines
- **Eval metrics**: rubric file exists but app does not
- **L4/UWG/Exit/OTEL**: **none**

---

## 3. Gaps by app (summary)

| Concern | Affected apps | Severity |
|---|---|---|
| No `AppDomainContract` schema anywhere in repo | all | **P1** |
| Per-app rubric YAMLs live in `apps_eval/config/rubrics/` not in each app's own `config/domain_contract/` | 7 apps | **P1** |
| No L4 records for AppDomainContract / Rubric / Threshold / Grader / Retrieval / Prompt / Capability / Route / Fixture / NegativeControl | all | **P1** |
| No UWG admission path for app contracts (current `ALLOWED_OPERATIONS` excludes app-contract registration) | all | **P1** |
| No L4 lookup API for `(app_id, task_class) → contract_record` | all | **P1** |
| `RouteContract` lacks `app_id`, `task_class`, `rubric_ref`, `threshold_ref`, `grader_ref`, `capability_profile_ref`, `prompt_profile_ref`, `retrieval_profile_ref`, `domain_contract_ref` | all | **P1** |
| `ExitReviewPacket` and X3CommitRequestPacket lack app-specific refs | all | **P1** |
| Exit X1/X2/X3 evaluators use generic V6 verdicts; no per-app rubric/threshold consumption | all | **P1** |
| OTEL spans do not emit `app.id` / `app.task_class` / `app.*_ref` attributes | all | **P1** |
| `apps_shared/proof/proof_runner.py` proof bundles do not include app contract refs / digests | all | **P1** |
| `apps_qna` has no policies, thresholds, rubric, or fixtures | qna | **P2** (separate from contract system) |
| `apps_underwriting_ai` is a stub — no engines, no configs | underwriting_ai | **P2** |
| Configuration loaded via direct YAML reads at runtime (e.g., `_taxonomy.py`, app spec configs) — bypass-prone | all | **P1** |
| No tests proving "app cannot write directly to L4" beyond the generic UWG anti-bypass tests | all | **P1** |
| Negative controls exist in `apps_shared/proof/negative_controls.py` but are not bound to per-app contract violations | all | **P2** |

---

## 4. Existing code to reuse (do NOT reinvent)

This is the **most important section**. The repo already provides the spine.
Phase 1+ MUST extend, not replace.

### L4 / UWG / Exit spine — reuse as-is

| Asset | Path | Role in new system |
|---|---|---|
| `DurableWriteGateway` | `agentic_core/L4_state/uwg/durable_write_gateway.py` | THE write authority. Add `app_domain_contract_register` to `ALLOWED_OPERATIONS`; submit registrations as `CommitRequest`+`StateDiff` from a new "Exit" registration adapter (per UWG's `source_surface == "Exit"` rule, since Exit is the only authorized source). |
| `L4_CONTRACT_SCHEMA_VERSION` constant + record dataclass pattern | `agentic_core/L4_state/contracts/records.py` | Add `AppDomainContractRecord`, `EvalRubricRecord`, `ThresholdProfileRecord`, `GraderRosterRecord`, `RetrievalProfileRecord`, `PromptProfileRecord`, `CapabilityProfileRecord`, `RouteProfileRecord`, `FixtureRecord`, `NegativeControlRecord`, `InputContractRecord`, `OutputSchemaRecord` here. Use `stamp_digest`, `compute_deterministic_digest`. |
| `lookup.py` lookup APIs | `agentic_core/L4_state/contracts/lookup.py` | Extend with `get_app_domain_contract(app_id, task_class)` and family. |
| `audit_ledger.AuditLedger` | `agentic_core/L4_state/audit/audit_ledger.py` | Already wires through UWG commit/blocked paths. Free benefit. |
| `RouteContract` (C0 input) | `agentic_core/L0_routing/c0_retrieval/route_contract.py` | **Extend** with `app_id`, `task_class`, `domain_contract_ref`, `rubric_ref`, `threshold_profile_ref`, `grader_roster_ref`, `retrieval_profile_ref`, `prompt_profile_ref`, `capability_profile_ref`. Keep existing fields (max_k, max_hops, allowed_sources, etc.) — they map onto retrieval profile. |
| `V15RouteContract` (richer schema) | `agentic_core/L0_routing/types/route_contract_v15.py` | Add `app_id`, `task_class`, `domain_contract_ref` to `signatures` block + add new closed-vocabulary fields. |
| `ExitReviewPacket` | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | **Extend** with all app-specific refs. Pipeline at `pipeline.py` already routes to `process_commit_request`. |
| `X3CommitRequestPacket` | same file | Already carries `route_contract` dict; just bind app refs and digest. |
| `process_commit_request` orchestrator | `agentic_core/L3_orchestration/exit_eval/v6/uwg.py` | Already runs U1..U5. Adapt the registration-via-UWG path to use this pattern. |
| `RouteReasonCode` closed vocab | `agentic_core/L0_routing/types/routing_artifact_types.py` | Use the same "closed vocabulary + reason codes" pattern for new `AppContractReasonCode`. |

### Per-app rubric YAMLs — migrate, do not duplicate

`apps_eval/config/rubrics/` already contains per-app rubrics:
- `rub_apps_eval_self_v1.yaml`
- `rub_apps_exec_brief_v1.yaml`
- `rub_apps_lic_outreach_v1.yaml`
- `rub_apps_research_brief_v1.yaml`
- `rub_apps_rfp_response_v1.yaml`
- `rub_apps_rg_resume_generation_v1.yaml`
- `rub_apps_underwriting_decisioning_v1.yaml`

**Phase 2 strategy**: leave originals in place during transition; new authoritative
copies live under `apps_<name>/config/domain_contract/eval_rubrics.yaml`. Phase 3
registration drains the new locations into L4. Original files are deprecated
in a later wave.

### Proof harness — extend, do not rewrite

| Asset | Path | Role |
|---|---|---|
| `proof_runner.py` | `apps_shared/proof/proof_runner.py` | Add app contract section to the bundle. |
| `validators.py` | `apps_shared/proof/validators.py` | Add `validate_app_domain_contract_resolution` validator. |
| `negative_controls.py` | `apps_shared/proof/negative_controls.py` | Wire per-app negative controls from `apps_<name>/config/domain_contract/negative_controls.yaml` into existing harness. |
| `write_sovereignty.py` | `apps_shared/proof/write_sovereignty.py` | Already proves "no direct L4 writes from apps_*"; extend assertion to cover app-contract registration path. |
| `otel_export.py` | `apps_shared/proof/otel_export.py` | Add `app.*` attribute extraction. |

### Configuration loader patterns — reuse

| Asset | Path | Pattern to adopt |
|---|---|---|
| `routing_thresholds.py` | `agentic_core/runtime/config/routing_thresholds.py` | YAML loader with namespace overrides + env override + cached singleton + back-compat literal defaults. **Use the same shape** for the registration-time loader that reads `apps_<name>/config/domain_contract/*.yaml` and produces StateDiffs. |
| `_taxonomy.py` | `apps_eval/engines/_taxonomy.py` | Existing direct-YAML reader; serves as the **anti-pattern** to migrate AWAY from after Phase 3 registration is live. |

---

## 5. Files to create

### Schema (shared)

Per the user's Phase 1 directive ("Use the existing repo style. Do not invent
a parallel architecture if one already exists."), the shared schema lives in
the established L4 contracts module:

- `agentic_core/L4_state/contracts/app_domain.py` (NEW)
  - `AppDomainContractRecord` dataclass
  - `InputContractRecord`
  - `OutputSchemaRecord`
  - `EvalRubricRecord`
  - `ThresholdProfileRecord`
  - `GraderRosterRecord`
  - `RetrievalProfileRecord`
  - `PromptProfileRecord`
  - `CapabilityProfileRecord`
  - `RouteProfileRecord`
  - `OrchestrationProfileRecord`
  - `FixtureRecord`
  - `NegativeControlRecord`

- `agentic_core/L4_state/contracts/app_domain_lookup.py` (NEW) — read-only
  resolver `(app_id, task_class) → contract refs`. Sibling to existing
  `lookup.py`.

- `agentic_core/L4_state/contracts/app_domain_digests.py` (NEW) — deterministic
  digest computation per subcontract. Reuses `digests.compute_deterministic_digest`.

### Registration adapter

- `agentic_core/L4_state/uwg/app_domain_registration.py` (NEW) — converts
  validated `apps_<name>/config/domain_contract/*.yaml` into `CommitRequest`
  with `state_diffs=[StateDiff(operation_type="app_domain_contract_register", ...)]`.
  Calls `DurableWriteGateway.commit()`. Source surface = `"Exit"` per UWG rule.
- `ALLOWED_OPERATIONS` extension in `durable_write_gateway.py` to include
  `"app_domain_contract_register"`.

### Runtime resolver

- `agentic_core/L0_routing/app_domain_resolver.py` (NEW) — at L0 dispatch
  time, resolve `(app_id, task_class)` to contract refs and inject into
  `RouteContract` + `V15RouteContract`. Fail closed when no record exists.

### Exit evaluator extension

- `agentic_core/L3_orchestration/exit_eval/v6/app_specific_evaluator.py` (NEW)
  — pulls `rubric_ref`/`threshold_profile_ref`/`grader_roster_ref` from L4 via
  the resolver, runs per-dimension scoring, attaches results to
  `ExitReviewPacket.app_specific_eval`. Hooks into the X1/X2/X3 stages.

### CLI / harness

- `apps_shared/scripts/register_app_domain_contracts.py` (NEW) — CLI entrypoint:
  `python -m apps_shared.scripts.register_app_domain_contracts --app <name>|all`
- `apps_shared/scripts/validate_app_domain_contracts.py` (NEW) — schema
  validation only (no UWG submission).
- `tools/proof/run_app_domain_e2e.py` (NEW under `tools/proof/`) — golden +
  negative E2E runner per app.

### Per-app config (Phase 2 deliverable per user spec)

For each of the 8 apps (`eval`, `exec`, `lic`, `qna`, `research`, `rfp`, `rg`,
`underwriting_ai`):

```
apps_<name>/config/domain_contract/
├── app_domain_manifest.yaml
├── task_classes.yaml
├── input_contract.yaml
├── output_schema.yaml
├── eval_rubrics.yaml             # seeded from apps_eval/config/rubrics/<rub>.yaml
├── threshold_profiles.yaml       # seeded from apps_<name>/config/<name>_thresholds.yaml
├── grader_roster.yaml
├── retrieval_profiles.yaml
├── prompt_profiles.yaml
├── capability_profiles.yaml
├── route_profiles.yaml
├── orchestration_profiles.yaml   # apps_rg, apps_lic, apps_underwriting_ai (DAG/HOP apps)
├── fixtures.yaml                 # >=2 golden fixtures
└── negative_controls.yaml        # >=2 negative controls
```

**Total per-app new files**: ~13 YAMLs × 8 apps = **~104 new YAML files**.

### Tests

- `tests/_apps_contract/test_app_domain_contract_schema.py` (extend existing)
- `tests/_apps_contract/test_app_domain_uwg_registration.py` (new)
- `tests/_apps_contract/test_app_domain_l4_lookup.py` (new)
- `tests/_apps_contract/test_app_domain_runtime_resolution.py` (new)
- `tests/_apps_contract/test_app_domain_exit_evaluation.py` (new)
- `tests/_apps_contract/test_app_domain_e2e_proof.py` (new)
- Per-app fixture/negative-control parametrized tests — discovered from YAML.

---

## 6. Files to modify

| File | Change |
|---|---|
| `agentic_core/L4_state/uwg/durable_write_gateway.py` | Extend `ALLOWED_OPERATIONS` with `app_domain_contract_register` and related ops. |
| `agentic_core/L4_state/contracts/__init__.py` | Re-export new app_domain records. |
| `agentic_core/L4_state/contracts/lookup.py` | Add app-domain lookup helpers OR keep separate in `app_domain_lookup.py`. |
| `agentic_core/L0_routing/c0_retrieval/route_contract.py` | Add app-specific ref fields. |
| `agentic_core/L0_routing/types/route_contract_v15.py` | Add app-specific fields to V15. |
| `agentic_core/L3_orchestration/exit_eval/v6/types.py` | Add app-specific refs to `ExitReviewPacket` and `X3CommitRequestPacket`. |
| `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` | Wire `app_specific_evaluator` into X1/X2/X3 stages. |
| `apps_shared/proof/proof_runner.py` | Add app contract section to bundle. |
| `apps_shared/proof/validators.py` | Add app-domain validators. |
| `apps_shared/proof/otel_export.py` | Emit `app.*` attributes. |
| `apps_shared/proof/write_sovereignty.py` | Cover registration-path bypass attempts. |
| `apps_<name>/integrations/*_ingress_runner.py` (per app) | Stop reading `apps_<name>/config/<...>.yaml` directly at runtime; instead consume L4 resolver output passed via `RouteContract`. |

---

## 7. Tests to add

| Category | Test name | Asserts |
|---|---|---|
| Schema | `test_valid_contract_passes` | All required fields present, digest stable. |
| Schema | `test_missing_input_contract_fails_closed` | KeyError or validation error. |
| Schema | `test_missing_rubric_fails_closed` | Same. |
| Schema | `test_missing_threshold_profile_fails_closed` | Same. |
| Schema | `test_missing_grader_roster_fails_closed` | Same. |
| Schema | `test_duplicate_task_class_fails` | Per-app, one task_class only once. |
| Schema | `test_identical_rubric_across_apps_requires_shared_base_ref` | Anti-collision rule. |
| Schema | `test_unknown_dimension_never_passes` | UNKNOWN → fail closed. |
| Schema | `test_not_applicable_requires_reason` | NA dimensions need a reason field. |
| UWG/L4 | `test_apps_cannot_write_l4_directly` | `reject_direct_write` called for every apps_* surface. |
| UWG/L4 | `test_app_contract_registers_via_uwg` | Registration produces `UWGCommitReceipt`. |
| UWG/L4 | `test_l4_record_has_deterministic_digest` | `record.deterministic_digest != ""`. |
| UWG/L4 | `test_l4_lookup_returns_active_contract` | `get_app_domain_contract("apps_rg", "resume_generation")` returns the record. |
| UWG/L4 | `test_deprecated_app_contract_fails_closed` | Status=deprecated → resolver refuses. |
| Runtime | `test_apps_rg_resolves_apps_rg_rubric_from_l4` | RouteContract.rubric_ref points to L4 record, not local YAML. |
| Runtime | `test_apps_lic_resolves_apps_lic_rubric_from_l4` | Same for lic. |
| Runtime | `test_runtime_does_not_read_app_yaml_after_registration` | Static check: no `yaml.safe_load(apps_<name>/config/...)` call sites in hot path after Phase 4. |
| Runtime | `test_route_contract_contains_app_specific_refs` | RouteContract has all refs after L0 dispatch. |
| Runtime | `test_exit_review_packet_contains_app_specific_refs` | ExitReviewPacket carries them through to UWG handoff. |
| Exit | `test_apps_rg_unsupported_resume_claim_fails` | Negative control fixture trips `factual_grounding` dimension. |
| Exit | `test_apps_rg_missing_required_section_fails` | Output schema violation → X3 disposition `DENY`. |
| Exit | `test_apps_lic_fake_personalization_fails` | Negative control. |
| Exit | `test_apps_lic_sensitive_targeting_fails` | Negative control. |
| Exit | `test_apps_lic_channel_length_violation_fails` | Output schema constraint. |
| Exit | `test_unknown_required_dimension_never_passes` | UNKNOWN → fail-closed at Exit. |
| E2E | `test_<app>_golden_path_emits_full_proof_bundle` | Per app × 2 fixtures = 16 tests. |
| E2E | `test_<app>_negative_control_fails_for_expected_reason` | Per app × 2 controls = 16 tests. |
| E2E | `test_otel_spans_include_app_specific_contract_refs` | Spans carry `app.id`, `app.task_class`, etc. |
| E2E | `test_replay_resolves_same_l4_contract_digest` | Replay determinism. |
| E2E | `test_no_bypass_scanner_clean` | Static + runtime scanner. |

---

## 8. Ambiguity → TODO_FAILING_TEST (to encode, not silently skip)

The user's spec mandates: "Any ambiguity that must be encoded as
TODO_FAILING_TEST, not silently skipped."

| Ambiguity | TODO_FAILING_TEST owner |
|---|---|
| **`apps_qna` task_class definition**: this app produces card packs / paste-sets, but its eval surface is partially owned by W4 NamespaceBandit + Wilson CI in the apps_qna pack lifecycle ledger. Is the "task_class" `qna_pack_build`, `qna_route_select`, or both? | `tests/_apps_contract/test_apps_qna_task_class_resolution.py::test_TODO_qna_task_class_canonical` |
| **`apps_underwriting_ai` is a stub**. Should Phase 2 author a contract for a non-existent app? Recommendation: minimal manifest + 1 task_class + 1 fixture + 1 negative control + `status=draft`. Full implementation deferred. | `tests/_apps_contract/test_apps_underwriting_ai_stub_disposition.py::test_TODO_underwriting_ai_status_draft` |
| **Source-surface for app-contract registration**: UWG enforces `source_surface == "Exit"`. App-contract registration is a build-time event, not a runtime Exit event. Two options: (a) extend `NON_AUTHORIZED_SOURCES` exemption for a dedicated `"AppContractRegistrar"` surface; (b) route registration through a synthetic Exit pseudo-run. **Author-Gate decision required at Phase 3 entry**. | `tests/_apps_contract/test_app_contract_registration_authority.py::test_TODO_registration_source_surface` |
| **L4 versioning for app contracts**: when `app_version` increments, do older versions stay queryable? UWG already supports `version_insert`; need to define the active-version selection rule (latest-by-policy_hash? explicit alias_swap?). | `tests/_apps_contract/test_app_contract_versioning.py::test_TODO_active_version_selection` |
| **`apps_eval` self-eval circularity**: apps_eval evaluates other apps and itself. Does its rubric resolve from L4 like other apps, or does it bootstrap from disk? | `tests/_apps_contract/test_apps_eval_self_eval_resolution.py::test_TODO_self_eval_bootstrap` |
| **Backward-compat with `apps_eval/config/rubrics/`**: during the transition window (Phases 2–4), both locations may exist. Drift detection? | `tests/_apps_contract/test_rubric_dual_location_drift.py::test_TODO_no_drift_during_migration` |
| **Capability profile vs. existing `apps_shared/enforcement/*Strategy.py`**: enforcement strategies (CircuitBreakerStrategy, AdaptiveRetrievalGateStrategy, etc.) already constrain L2 behavior. Does CapabilityProfileContract supersede them or compose with them? | `tests/_apps_contract/test_capability_profile_vs_enforcement_strategy.py::test_TODO_layered_authority` |
| **Grader roster for deterministic-only rubrics**: `apps_qna` may have purely deterministic graders. Does the schema force a non-empty `llm_judge_graders[]`? Recommendation: allow empty if `deterministic_graders[]` non-empty. | `tests/_apps_contract/test_grader_roster_minima.py::test_TODO_deterministic_only_allowed` |

---

## 9. Provenance

- ADG snapshot consulted: latest under `artifacts/adg/adg_indexed_*.sqlite` (via `code_search` tool, which uses ADG MCP under the hood for dependency questions).
- Code paths read directly: `agentic_core/L4_state/uwg/durable_write_gateway.py`, `agentic_core/L4_state/contracts/records.py` (excerpt), `agentic_core/L0_routing/c0_retrieval/route_contract.py`, `agentic_core/L0_routing/types/route_contract_v15.py`, `agentic_core/L3_orchestration/exit_eval/v6/{uwg,pipeline,types}.py`, `agentic_core/L0_routing/reasoning/route_gates.py`, `agentic_core/L0_routing/composition_root.py`, `agentic_core/L0_routing/c0_retrieval/dispatcher.py`, `agentic_core/runtime/config/routing_thresholds.py`, `apps_eval/engines/_taxonomy.py`, `apps_shared/types/integration_layer_types.py`.
- Per-app inventories: `list_dir` on every `apps_*` directory and their `config/` subdirectories.
- Rubric YAML inventory: `apps_eval/config/rubrics/`.

This report is read-only output. **Zero production code has been edited
during Phase 0.**

---

## Next action (gated)

Phase 1 begins only when the user reviews this report + the companion plan
(`.codex/plans/apps-domain-contract-fortknox-c4d8e2.md`) and emits
`SR_APPROVAL: APPROVED` (or requests scope/sequencing changes).
